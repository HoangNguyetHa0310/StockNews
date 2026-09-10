# -*- coding: utf-8 -*-
"""
Module nạp và cache dữ liệu thị trường thông minh từ vnstock
Tự động lưu trữ cục bộ, cập nhật dữ liệu mới (incremental), và xử lý chống rate-limit.
"""
import time
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from vnstock.api.quote import Quote
from config import (
    DATA_DIR, VN30_TICKERS, MARKET_INDICES,
    DEFAULT_START_DATE, TODAY_DATE, API_CONFIG,
    get_vietnam_now
)


class DataLoader:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.source = API_CONFIG["source"]
        self.sleep_seconds = API_CONFIG["sleep_between_calls"]
        self.max_retries = API_CONFIG["max_retries"]
        self.retry_wait = API_CONFIG["retry_wait"]

    def _get_cache_path(self, ticker: str) -> Path:
        return self.data_dir / f"{ticker.upper()}.csv"

    def fetch_from_api(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Gọi API vnstock để tải dữ liệu lịch sử của 1 mã, tự động retry nếu gặp lỗi rate-limit.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                q = Quote(symbol=ticker.upper(), source=self.source)
                df = q.history(start=start_date, end=end_date, interval='1D')
                if df is not None and not df.empty:
                    df = df.copy()
                    # Chuẩn hóa cột
                    df.columns = [c.lower().strip() for c in df.columns]
                    if 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'])
                        df = df.sort_values('time').reset_index(drop=True)
                    # Ép kiểu dữ liệu số
                    num_cols = ['open', 'high', 'low', 'close', 'volume']
                    for col in num_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    return df
                return pd.DataFrame()
            except BaseException as e:
                err_msg = str(e)
                is_rate_limit = any(k in err_msg for k in ["Rate limit", "rate limit", "429", "GIỚI HẠN API"])
                if is_rate_limit or isinstance(e, SystemExit):
                    print(f"  [Cảnh báo] {ticker}: Chạm giới hạn API rate-limit. Chờ {self.retry_wait}s (lần {attempt}/{self.max_retries})...")
                    time.sleep(self.retry_wait)
                else:
                    print(f"  [Lỗi] Không thể tải {ticker}: {err_msg}")
                    if attempt < self.max_retries:
                        time.sleep(self.sleep_seconds)
                    else:
                        return pd.DataFrame()
        return pd.DataFrame()

    def get_ticker_data(self, ticker: str, start_date: str = DEFAULT_START_DATE,
                        end_date: str = None, force_update: bool = False) -> pd.DataFrame:
        """
        Lấy dữ liệu cổ phiếu: ưu tiên từ cache, tự động tải bù phiên mới nếu cần.
        """
        ticker = ticker.upper()
        cache_file = self._get_cache_path(ticker)
        if end_date is None:
            end_date = get_vietnam_now().strftime("%Y-%m-%d")

        if cache_file.exists() and not force_update:
            try:
                cached_df = pd.read_csv(cache_file, parse_dates=['time'])
                if not cached_df.empty:
                    # Chế độ tiết kiệm tải / Ngoài giờ giao dịch: dùng trực tiếp cache không gọi mạng
                    return cached_df.sort_values('time').reset_index(drop=True)
            except Exception as e:
                print(f"  [Cảnh báo] Lỗi đọc cache {ticker}: {e}, sẽ thử tải mới...")

        # Nếu có cache và yêu cầu force_update=True: cập nhật bổ sung (incremental)
        if cache_file.exists():
            try:
                cached_df = pd.read_csv(cache_file, parse_dates=['time'])
                if not cached_df.empty:
                    cached_df = cached_df.sort_values('time').reset_index(drop=True)
                    last_cached_date = cached_df['time'].max().strftime("%Y-%m-%d")
                    last_dt = datetime.strptime(last_cached_date, "%Y-%m-%d")
                    today_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    if (today_dt - last_dt).days <= 0:
                        return cached_df
                    
                    next_day = (last_dt + timedelta(days=1)).strftime("%Y-%m-%d")
                    if next_day <= end_date:
                        print(f"[{ticker}] Cập nhật bổ sung nến mới từ {next_day} đến {end_date}...")
                        new_df = self.fetch_from_api(ticker, start_date=next_day, end_date=end_date)
                        if new_df is not None and not new_df.empty:
                            # Cơ chế phòng vệ toàn vẹn dữ liệu: phát hiện và chặn nến nhảy giá dị thường (>35%)
                            last_price = cached_df['close'].iloc[-1]
                            new_price = new_df['close'].iloc[0]
                            if last_price > 0 and abs(new_price / last_price - 1.0) > 0.35:
                                print(f"  [Cảnh báo an toàn] {ticker}: Nến mới ({new_price}) lệch > 35% so với giá nến cũ ({last_price}). Giữ nguyên cache an toàn.")
                                return cached_df

                            combined = pd.concat([cached_df, new_df]).drop_duplicates(subset=['time']).sort_values('time').reset_index(drop=True)
                            combined.to_csv(cache_file, index=False)
                            time.sleep(self.sleep_seconds)
                            return combined
                    return cached_df
            except Exception as e:
                print(f"  [Cảnh báo] Lỗi đồng bộ bổ sung {ticker}: {e}")

        # Tải mới toàn bộ
        print(f"[{ticker}] Tải mới dữ liệu từ {start_date} đến {end_date}...")
        df = self.fetch_from_api(ticker, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            df.to_csv(cache_file, index=False)
            time.sleep(self.sleep_seconds)
        return df

    def get_market_data(self, index_symbol: str = "VNINDEX", start_date: str = DEFAULT_START_DATE,
                        end_date: str = None, force_update: bool = False) -> pd.DataFrame:
        """
        Lấy dữ liệu chỉ số thị trường (VNINDEX hoặc VN30).
        """
        if end_date is None:
            end_date = get_vietnam_now().strftime("%Y-%m-%d")
        return self.get_ticker_data(index_symbol, start_date=start_date, end_date=end_date, force_update=force_update)

    def load_all_vn30(self, force_update: bool = False) -> dict[str, pd.DataFrame]:
        """
        Tải và nạp dữ liệu cho toàn bộ 30 cổ phiếu VN30 và chỉ số VN-Index.
        Trả về dictionary: { 'VNINDEX': df, 'FPT': df, ... }
        """
        all_data = {}
        
        # 1. Tải chỉ số thị trường trước
        for idx_symbol in MARKET_INDICES:
            print(f"\n>>> Đang chuẩn bị dữ liệu chỉ số: {idx_symbol}")
            df = self.get_market_data(idx_symbol, force_update=force_update)
            if df is not None and not df.empty:
                all_data[idx_symbol] = df
            else:
                print(f"  [!] Không thể lấy dữ liệu cho chỉ số {idx_symbol}")

        # 2. Tải 30 mã VN30
        total = len(VN30_TICKERS)
        print(f"\n>>> Đang nạp dữ liệu cho {total} cổ phiếu rổ VN30...")
        for i, ticker in enumerate(VN30_TICKERS, start=1):
            print(f"[{i}/{total}] Đang xử lý {ticker}...")
            df = self.get_ticker_data(ticker, force_update=force_update)
            if df is not None and not df.empty:
                all_data[ticker] = df
            else:
                print(f"  [!] Cảnh báo: Mã {ticker} không có dữ liệu.")

        print(f"\n>>> Hoàn thành nạp dữ liệu! Đã tải thành công {len(all_data)} mã/chỉ số.")
        return all_data


if __name__ == "__main__":
    loader = DataLoader()
    print("Kiểm tra nạp mã FPT...")
    fpt_df = loader.get_ticker_data("FPT")
    if not fpt_df.empty:
        print(f"FPT data shape: {fpt_df.shape}")
        print(fpt_df.tail(3))
    else:
        print("Không tải được FPT.")
