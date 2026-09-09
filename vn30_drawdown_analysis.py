# -*- coding: utf-8 -*-
"""
THỐNG KÊ CHU KỲ GIẢM GIÁ MẠNH (DRAWDOWN) CHO CÁC MÃ VN30
==========================================================
Cài đặt trước khi chạy (trên Colab hoặc máy local):
    pip install vnstock openpyxl

Ý tưởng:
- Tải dữ liệu giá đóng cửa lịch sử (theo ngày) của TẤT CẢ các mã trong VN30
  (không lọc theo thanh khoản nữa — quét toàn bộ để không bỏ sót mã nào).
- Với mỗi mã, tìm các đợt "giảm mạnh": từ 1 đỉnh cục bộ (local peak) giảm
  xuống 1 đáy cục bộ (local trough) với mức giảm >= ngưỡng (mặc định 10%).
- Đo khoảng cách (số ngày giao dịch) giữa các đợt giảm liên tiếp.
- Đo mức % hồi phục sau đáy (từ đáy tăng lên bao nhiêu % trong N ngày sau đó).
- Xuất KẾT QUẢ RA 1 FILE EXCEL (.xlsx) duy nhất, gồm 3 sheet:
    - Giai_thich: giải thích từng cột và các lưu ý quan trọng (đọc sheet này trước)
    - Tom_tat_theo_ma: mỗi mã 1 dòng, các số liệu trung bình
    - Chi_tiet_su_kien: liệt kê từng đợt giảm cụ thể của tất cả các mã

LƯU Ý QUAN TRỌNG:
- Đây là thống kê MÔ TẢ (descriptive) dựa trên dữ liệu quá khứ, KHÔNG phải quy luật
  vật lý học và KHÔNG đảm bảo lặp lại trong tương lai.
- Không dùng kết quả này như tín hiệu giao dịch chắc chắn. Thị trường chứng khoán
  không có "chu kỳ cố định" theo đúng nghĩa toán học.
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# ============ 1. CẤU HÌNH ============

# Danh sách mã VN30 (bạn có thể sửa lại danh sách 20 mã thanh khoản cao nhất
# tùy theo thời điểm thực tế, vì thứ hạng thanh khoản thay đổi theo thời gian)
VN30_TICKERS = [
    "ACB", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG", "MBB",
    "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB", "TCB",
    "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

START_DATE = "2022-01-01"   # có thể chỉnh khoảng thời gian dài hơn/ngắn hơn
END_DATE = datetime.now().strftime("%Y-%m-%d")

DROP_THRESHOLD = 0.10        # ngưỡng coi là "giảm mạnh" = 10%
RECOVERY_WINDOW_DAYS = 20    # số phiên sau đáy để đo mức hồi phục
MIN_SWING_SEPARATION = 5     # số phiên tối thiểu giữa 2 đỉnh/đáy để tránh nhiễu

# Tài khoản "khách" (guest) của vnstock giới hạn 20 request/phút.
# Ta chủ động nghỉ giữa mỗi lần gọi để không bao giờ chạm giới hạn,
# và tự động retry (chờ rồi gọi lại) nếu vẫn bị chặn.
SLEEP_BETWEEN_CALLS = 8       # giây nghỉ giữa mỗi mã (an toàn hơn nhiều so với 20/phút,
                              # vì mỗi lần gọi history() có thể tốn hơn 1 request nội bộ)
MAX_RETRIES = 8
RETRY_WAIT_SECONDS = 45

# ============ 2. HÀM LẤY DỮ LIỆU (dùng vnstock) ============

def _fetch_one_ticker(ticker, start_date, end_date):
    """
    Tải dữ liệu 1 mã, tự động retry nếu bị rate-limit (vnstock ném lỗi
    dạng chuỗi/exception chứa 'Rate limit' hoặc tương tự khi vượt 20 req/phút).
    """
    from vnstock import Vnstock

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            stock = Vnstock().stock(symbol=ticker, source='VCI')
            df = stock.quote.history(start=start_date, end=end_date, interval='1D')
            return df
        except BaseException as e:
            # Bắt BaseException (không chỉ Exception) vì vnstock có thể raise
            # SystemExit hoặc một lớp lỗi tùy biến không kế thừa Exception chuẩn
            # khi bị rate-limit, khiến except Exception thông thường bỏ lọt.
            msg = str(e)
            is_rate_limit = any(k in msg for k in
                                 ["Rate limit", "rate limit", "429", "GIỚI HẠN API"])
            if is_rate_limit or isinstance(e, SystemExit):
                print(f"  -> Bị rate-limit khi tải {ticker}, chờ {RETRY_WAIT_SECONDS}s rồi thử lại "
                      f"(lần {attempt}/{MAX_RETRIES})...")
                time.sleep(RETRY_WAIT_SECONDS)
                continue
            else:
                print(f"Lỗi khi tải {ticker}: {e}")
                return None
    print(f"Bỏ qua {ticker} sau {MAX_RETRIES} lần thử vẫn bị rate-limit.")
    return None


def get_all_tickers_data(tickers, start_date, end_date):
    """
    Tải dữ liệu cho TẤT CẢ các mã trong danh sách (không lọc top 20 theo
    thanh khoản nữa — quét toàn bộ để không bỏ sót mã nào, kể cả VCB).
    Chủ động nghỉ giữa các lần gọi để tránh vượt giới hạn request/phút
    của tài khoản khách (guest).
    """
    price_data = {}

    for idx, ticker in enumerate(tickers, start=1):
        try:
            df = _fetch_one_ticker(ticker, start_date, end_date)
        except BaseException as e:
            print(f"  -> Vẫn lỗi ngoài dự kiến với {ticker}, bỏ qua mã này: {e}")
            df = None
        if df is not None and not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time').reset_index(drop=True)
            price_data[ticker] = df
            print(f"Đã tải {ticker}: {len(df)} phiên  ({idx}/{len(tickers)})")

        # Nghỉ giữa các lần gọi (trừ lần cuối cùng) để tránh chạm rate limit
        if idx < len(tickers):
            time.sleep(SLEEP_BETWEEN_CALLS)

    return price_data


# ============ 3. HÀM TÌM ĐỈNH/ĐÁY & CHU KỲ GIẢM ============

def find_drawdown_cycles(df, drop_threshold=DROP_THRESHOLD,
                          recovery_window=RECOVERY_WINDOW_DAYS,
                          min_sep=MIN_SWING_SEPARATION):
    """
    Quét chuỗi giá đóng cửa, tìm các đợt giảm từ đỉnh cục bộ xuống đáy cục bộ
    có biên độ >= drop_threshold. Trả về DataFrame liệt kê từng đợt giảm với:
    - ngày đỉnh, ngày đáy, số phiên kéo dài, % giảm
    - % hồi phục trong recovery_window phiên sau đáy
    - số phiên tính từ đáy của đợt giảm trước đó (khoảng cách giữa 2 chu kỳ)
    """
    close = df['close'].values
    dates = df['time'].values
    n = len(close)

    # Tìm chuỗi các đỉnh/đáy cục bộ đơn giản bằng cách theo dõi max/min chạy
    events = []
    peak_idx = 0
    peak_val = close[0]

    i = 1
    while i < n:
        if close[i] > peak_val:
            peak_val = close[i]
            peak_idx = i
        else:
            drop_pct = (peak_val - close[i]) / peak_val
            if drop_pct >= drop_threshold:
                # tìm đáy thực sự trong đoạn tiếp theo trước khi giá vượt lại đỉnh cũ
                trough_idx = i
                trough_val = close[i]
                j = i + 1
                while j < n and close[j] < peak_val:
                    if close[j] < trough_val:
                        trough_val = close[j]
                        trough_idx = j
                    j += 1

                recov_end = min(trough_idx + recovery_window, n - 1)
                recovery_pct = (close[recov_end] - trough_val) / trough_val

                events.append({
                    "Mã": None,  # sẽ gán ticker ở bước gộp sau
                    "Ngày_đỉnh": pd.Timestamp(dates[peak_idx]),
                    "Ngày_đáy": pd.Timestamp(dates[trough_idx]),
                    "Số_phiên_đỉnh_đến_đáy": trough_idx - peak_idx,
                    "Phần_trăm_giảm": round(-drop_pct * 100, 2),
                    "Phần_trăm_hồi_phục_sau_đáy": round(recovery_pct * 100, 2),
                    "_trough_idx": trough_idx,
                })

                # reset: bắt đầu tìm đỉnh mới từ sau đáy
                peak_idx = trough_idx
                peak_val = trough_val
                i = trough_idx + min_sep
                continue
        i += 1

    events_df = pd.DataFrame(events)
    if not events_df.empty:
        # khoảng cách (số phiên) giữa đáy của chu kỳ này và đáy của chu kỳ trước
        events_df["Số_phiên_kể_từ_đợt_giảm_trước"] = events_df["_trough_idx"].diff()
    return events_df


# ============ 4. HÀM TỔNG HỢP THỐNG KÊ NHIỀU MÃ ============

def summarize_all(price_data_dict, **kwargs):
    all_events = []
    per_ticker_summary = []

    for ticker, df in price_data_dict.items():
        ev = find_drawdown_cycles(df, **kwargs)
        if ev.empty:
            continue
        ev["Mã"] = ticker
        all_events.append(ev)

        per_ticker_summary.append({
            "Mã": ticker,
            "Số_đợt_giảm_mạnh": len(ev),
            "TB_số_ngày_giữa_2_đợt_giảm": round(ev["Số_phiên_kể_từ_đợt_giảm_trước"].dropna().mean(), 1)
                if ev["Số_phiên_kể_từ_đợt_giảm_trước"].notna().any() else np.nan,
            "TB_phần_trăm_giảm": round(ev["Phần_trăm_giảm"].mean(), 2),
            "TB_phần_trăm_hồi_phục": round(ev["Phần_trăm_hồi_phục_sau_đáy"].mean(), 2),
        })

    if all_events:
        all_events_df = pd.concat(all_events, ignore_index=True)
        # sắp xếp lại cột cho dễ đọc, bỏ cột nội bộ _trough_idx
        col_order = ["Mã", "Ngày_đỉnh", "Ngày_đáy", "Số_phiên_đỉnh_đến_đáy",
                     "Phần_trăm_giảm", "Phần_trăm_hồi_phục_sau_đáy",
                     "Số_phiên_kể_từ_đợt_giảm_trước"]
        all_events_df = all_events_df[col_order]
    else:
        all_events_df = pd.DataFrame()

    summary_df = pd.DataFrame(per_ticker_summary).sort_values(
        "TB_số_ngày_giữa_2_đợt_giảm"
    )
    return all_events_df, summary_df


# ============ 5. CHẠY CHƯƠNG TRÌNH ============

if __name__ == "__main__":
    print(f"Đang tải dữ liệu cho toàn bộ {len(VN30_TICKERS)} mã VN30 (không lọc theo thanh khoản)...")
    price_data = get_all_tickers_data(VN30_TICKERS, START_DATE, END_DATE)
    print(f"\nĐã tải thành công {len(price_data)}/{len(VN30_TICKERS)} mã.")

    print("\nĐang phân tích các đợt giảm mạnh (>= {:.0f}%) cho từng mã...".format(DROP_THRESHOLD*100))
    all_events_df, summary_df = summarize_all(price_data)

    print("\n===== TÓM TẮT THEO TỪNG MÃ =====")
    print(summary_df.to_string(index=False))

    if not all_events_df.empty:
        print("\n===== THỐNG KÊ TỔNG HỢP TOÀN BỘ NHÓM =====")
        tb_ngay = round(all_events_df["Số_phiên_kể_từ_đợt_giảm_trước"].dropna().mean(), 1)
        tv_ngay = round(all_events_df["Số_phiên_kể_từ_đợt_giảm_trước"].dropna().median(), 1)
        tb_giam = round(all_events_df["Phần_trăm_giảm"].mean(), 2)
        tb_hoiphuc = round(all_events_df["Phần_trăm_hồi_phục_sau_đáy"].mean(), 2)
        print("Trung bình số ngày giữa 2 đợt giảm mạnh (toàn nhóm):", tb_ngay)
        print("Trung vị số ngày giữa 2 đợt giảm mạnh (toàn nhóm):", tv_ngay)
        print("Trung bình % giảm mỗi đợt:", tb_giam, "%")
        print("Trung bình % hồi phục sau đáy ({} phiên):".format(RECOVERY_WINDOW_DAYS), tb_hoiphuc, "%")

        # ---- Sheet giải thích, để người đọc không rành Excel/thống kê vẫn hiểu ----
        giai_thich = pd.DataFrame({
            "Cột / Mục": [
                "Mã",
                "Ngày_đỉnh",
                "Ngày_đáy",
                "Số_phiên_đỉnh_đến_đáy",
                "Phần_trăm_giảm",
                "Phần_trăm_hồi_phục_sau_đáy",
                "Số_phiên_kể_từ_đợt_giảm_trước",
                "",
                "Số_đợt_giảm_mạnh",
                "TB_số_ngày_giữa_2_đợt_giảm",
                "TB_phần_trăm_giảm",
                "TB_phần_trăm_hồi_phục",
            ],
            "Ý nghĩa": [
                "Mã cổ phiếu",
                "Ngày giá đạt đỉnh (cao nhất) trước khi bắt đầu giảm",
                "Ngày giá chạm đáy (thấp nhất) của đợt giảm đó",
                "Số phiên giao dịch từ lúc đỉnh đến lúc chạm đáy (đợt giảm kéo dài bao lâu)",
                "Mức giảm giá từ đỉnh xuống đáy, tính theo % (số âm)",
                f"Giá đã hồi phục bao nhiêu % so với đáy, tính trong {RECOVERY_WINDOW_DAYS} phiên sau đáy",
                "Khoảng cách (số phiên giao dịch) từ đáy của đợt giảm TRƯỚC đó đến đáy của đợt này — "
                "đây là con số dùng để ước tính 'chu kỳ'",
                "",
                "Tổng số đợt giảm mạnh (>= 10%) mà mã này từng có trong giai đoạn quét",
                "Trung bình khoảng cách (số phiên) giữa các đợt giảm liên tiếp của mã này. "
                "CHÚ Ý: chỉ là trung bình quá khứ, không phải chu kỳ chắc chắn lặp lại",
                "Trung bình mức giảm (%) của các đợt giảm mạnh ở mã này",
                f"Trung bình mức hồi phục (%) sau đáy, đo trong {RECOVERY_WINDOW_DAYS} phiên",
            ]
        })
        luu_y = pd.DataFrame({
            "Lưu ý quan trọng khi đọc số liệu": [
                "1. Đây là thống kê MÔ TẢ dựa trên dữ liệu quá khứ (từ {} đến nay), KHÔNG phải quy luật "
                "toán học và KHÔNG đảm bảo lặp lại trong tương lai.".format(START_DATE),
                "2. Với mỗi mã, hãy so sánh 'TB_số_ngày_giữa_2_đợt_giảm' với độ lệch chuẩn thực tế của các "
                "khoảng cách trong sheet Chi_tiet_su_kien — nếu các khoảng cách chênh lệch nhau rất nhiều "
                "(ví dụ có lần cách 40 ngày, có lần cách 300 ngày) thì KHÔNG có 'chu kỳ' đều đặn.",
                "3. Ngưỡng coi là 'giảm mạnh' hiện đặt là 10% (đổi được trong biến DROP_THRESHOLD của code).",
                "4. 'Số phiên' là số ngày giao dịch thực tế (không tính thứ 7, Chủ nhật, ngày nghỉ lễ), "
                "khác với số ngày lịch bình thường.",
                "5. Không nên dùng bảng này để xác định thời điểm mua/bán chắc chắn — chỉ nên dùng để "
                "tham khảo mức độ biến động lịch sử của từng mã.",
            ]
        })

        # ---- Xuất ra 1 file Excel duy nhất, nhiều sheet, có định dạng ----
        output_file = "VN30_thong_ke_giam_gia.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            giai_thich.to_excel(writer, sheet_name="Giai_thich", index=False)
            luu_y.to_excel(writer, sheet_name="Giai_thich", index=False,
                            startrow=len(giai_thich) + 3)
            summary_df.to_excel(writer, sheet_name="Tom_tat_theo_ma", index=False)
            all_events_df.to_excel(writer, sheet_name="Chi_tiet_su_kien", index=False)

        # ---- Định dạng cho dễ đọc: bôi đậm header, tự co giãn độ rộng cột ----
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        wb = pd.ExcelFile(output_file).book if False else None  # (giữ chỗ, không dùng)
        import openpyxl
        wb = openpyxl.load_workbook(output_file)
        header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        header_font = Font(bold=True)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Bôi đậm + tô màu hàng đầu tiên (header)
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            # Tự co giãn độ rộng cột theo nội dung dài nhất
            for col_cells in ws.columns:
                max_len = max((len(str(c.value)) for c in col_cells if c.value is not None), default=10)
                col_letter = get_column_letter(col_cells[0].column)
                ws.column_dimensions[col_letter].width = min(max_len + 4, 60)
            ws.freeze_panes = "A2"  # đóng băng hàng tiêu đề khi cuộn

        wb.save(output_file)

        print(f"\nĐã lưu kết quả vào file Excel: {output_file}")
        print("File có 3 sheet: 'Giai_thich' (đọc sheet này trước), "
              "'Tom_tat_theo_ma' (tổng hợp mỗi mã 1 dòng), "
              "'Chi_tiet_su_kien' (từng đợt giảm cụ thể).")
    else:
        print("Không tìm thấy đợt giảm nào đạt ngưỡng đã đặt.")