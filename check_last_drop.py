# -*- coding: utf-8 -*-
"""
Đọc file vn30_drawdown_events.csv (đã xuất từ vn30_drawdown_analysis.py)
để xem: với mỗi mã, đáy (trough) gần nhất là ngày nào, đã bao nhiêu phiên
trôi qua kể từ đó, và so sánh với khoảng cách trung bình lịch sử.

CHỈ mang tính tham khảo thống kê mô tả — KHÔNG phải dự đoán chắc chắn.
"""

import pandas as pd

TICKERS_OF_INTEREST = ["FPT", "CTG", "VCB"]  # VCB không nằm trong top20 thanh khoản
                                              # nên có thể không có trong file events

df = pd.read_csv("vn30_drawdown_events.csv", parse_dates=["peak_date", "trough_date"])

today = pd.Timestamp.now().normalize()

for ticker in TICKERS_OF_INTEREST:
    sub = df[df["ticker"] == ticker].sort_values("trough_date")
    if sub.empty:
        print(f"\n{ticker}: không có trong dữ liệu đã phân tích "
              f"(có thể do không nằm trong top 20 thanh khoản, hoặc chưa từng "
              f"giảm >= ngưỡng 10% theo tiêu chí quét).")
        continue

    last = sub.iloc[-1]
    days_since_last_trough = (today - last["trough_date"]).days
    avg_gap = sub["days_since_prev_trough"].dropna().mean()
    std_gap = sub["days_since_prev_trough"].dropna().std()

    print(f"\n===== {ticker} =====")
    print(f"Số đợt giảm mạnh (>=10%) đã ghi nhận: {len(sub)}")
    print(f"Đáy gần nhất: {last['trough_date'].date()} (mức giảm {last['drop_pct']}%)")
    print(f"Số ngày lịch (không phải phiên) đã trôi qua kể từ đáy gần nhất: {days_since_last_trough}")
    print(f"Khoảng cách trung bình giữa các đợt (số phiên giao dịch): {avg_gap:.1f}")
    print(f"Độ lệch chuẩn khoảng cách: {std_gap:.1f}  <- nếu số này gần bằng hoặc lớn hơn "
          f"trung bình, nghĩa là KHÔNG có chu kỳ đều đặn, chỉ là ngẫu nhiên")