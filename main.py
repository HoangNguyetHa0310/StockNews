# -*- coding: utf-8 -*-
"""
Chương trình chính: Hệ thống Phân tích Định lượng & Dự đoán Machine Learning VN30
Khởi chạy:
    python main.py                  # Chạy phân tích toàn bộ VN30 (dùng cache thông minh)
    python main.py --force-update   # Buộc tải mới dữ liệu từ vnstock
    python main.py --ticker FPT     # Phân tích chi tiết một mã cụ thể
    python main.py --test-run       # Chạy thử nhanh kiểm tra luồng hoạt động
"""
import sys
import argparse
from datetime import datetime
import pandas as pd
from pathlib import Path

from config import VN30_TICKERS, MARKET_INDICES, REPORTS_DIR
from data_loader import DataLoader
from feature_engineering import add_technical_features
from ml_engine import StockPredictor
from quant_analyzer import QuantAnalyzer
from report_generator import ReportGenerator


def parse_arguments():
    parser = argparse.ArgumentParser(description="Hệ thống Dự đoán & Phân tích Định lượng VN30")
    parser.add_argument("--force-update", action="store_true", help="Bắt buộc tải lại dữ liệu mới nhất từ sàn")
    parser.add_argument("--ticker", type=str, default=None, help="Chỉ phân tích chuyên sâu 1 mã (vd: FPT, HPG)")
    parser.add_argument("--retrain", action="store_true", help="Bắt buộc huấn luyện lại mô hình Machine Learning")
    parser.add_argument("--test-run", action="store_true", help="Chế độ chạy thử nghiệm nhanh với 5 mã")
    return parser.parse_args()


def print_banner():
    banner = """
========================================================================================
   VN30 QUANTITATIVE & MACHINE LEARNING STOCK PREDICTOR SYSTEM
   Tích hợp Phân tích Đa nhân tố + Thuật toán Gradient Boosting (LightGBM/RF)
========================================================================================
"""
    print(banner)


def run_pipeline(force_update: bool = False, target_ticker: str = None, retrain: bool = False, is_test: bool = False):
    print_banner()

    data_loader = DataLoader()
    predictor = StockPredictor()
    analyzer = QuantAnalyzer()
    reporter = ReportGenerator()

    # Xác định danh sách mã cần chạy
    if target_ticker:
        tickers = [target_ticker.upper()]
    elif is_test:
        tickers = ["FPT", "HPG", "TCB", "MWG", "VCB"]
        print(f"[*] Chế độ kiểm thử nhanh: quét {len(tickers)} mã: {tickers}")
    else:
        tickers = VN30_TICKERS
        print(f"[*] Quét toàn bộ danh sách {len(tickers)} mã rổ VN30...")

    # 1. Tải và xử lý dữ liệu chỉ số VN-INDEX
    print("\n[Bước 1/5] Đang nạp dữ liệu chỉ số thị trường VN-INDEX...")
    vnindex_raw = data_loader.get_market_data("VNINDEX", force_update=force_update)
    if vnindex_raw is None or vnindex_raw.empty:
        print("  [Cảnh báo] Không thể lấy dữ liệu VN-INDEX, hệ thống sẽ tiếp tục ở chế độ độc lập.")
        vnindex_feat = None
    else:
        vnindex_feat = add_technical_features(vnindex_raw)
        print(f"  -> Dữ liệu VN-INDEX: {len(vnindex_raw)} phiên (từ {vnindex_raw['time'].min().date()} đến {vnindex_raw['time'].max().date()})")

    # 2. Tải và tính toán các đặc trưng kỹ thuật cho từng mã
    print(f"\n[Bước 2/5] Đang nạp và tính toán 25+ chỉ báo kỹ thuật cho các mã...")
    processed_stocks = {}
    for i, t in enumerate(tickers, start=1):
        print(f"  ({i}/{len(tickers)}) Đang xử lý {t}...", end="\r")
        raw_df = data_loader.get_ticker_data(t, force_update=force_update)
        if raw_df is not None and len(raw_df) >= 35:
            feat_df = add_technical_features(raw_df, vnindex_df=vnindex_raw)
            processed_stocks[t] = feat_df
        else:
            print(f"\n  [!] Mã {t} không đủ dữ liệu (cần ít nhất 35 phiên).")
    print(f"\n  -> Hoàn tất xử lý đặc trưng cho {len(processed_stocks)} mã.")

    if not processed_stocks:
        print("[Lỗi] Không có cổ phiếu nào được xử lý thành công. Vui lòng kiểm tra lại kết nối.")
        return

    # 3. Huấn luyện hoặc nạp mô hình Machine Learning
    print("\n[Bước 3/5] Khởi động Machine Learning Predictive Engine...")
    model_loaded = False
    if not retrain:
        model_loaded = predictor.load_model()
        if model_loaded:
            print("  -> Đã nạp thành công mô hình đã lưu sẵn trước đó.")
    
    if not model_loaded:
        print("  -> Đang huấn luyện mô hình Machine Learning mới với TimeSeriesSplit...")
        predictor.train_model(processed_stocks, target_col="target_up_t3")

    # 4. Dự đoán và phân tích định lượng
    print("\n[Bước 4/5] Chạy suy luận xác suất ML và bộ chấm điểm Quant Multi-Factor...")
    stock_analyses = []
    for ticker, df in processed_stocks.items():
        ml_res = predictor.predict_latest(ticker, df)
        analysis = analyzer.analyze_ticker(ticker, df, ml_res)
        if analysis:
            stock_analyses.append(analysis)

    # Đánh giá thị trường chung
    market_summary = analyzer.analyze_market_regime(vnindex_feat, stock_analyses)

    # Sắp xếp theo điểm Quant tổng
    stock_analyses = sorted(stock_analyses, key=lambda x: x.get("total_score", 0), reverse=True)

    # 5. In bảng kết quả tổng hợp ra Console
    print("\n" + "=" * 95)
    print(f"{'HẠNG':<5} {'MÃ':<6} {'GIÁ':<9} {'THAY ĐỔI':<10} {'RSI':<6} {'VOL/MA20':<9} {'AI P(TĂNG)':<12} {'ĐIỂM':<7} {'KHUYẾN NGHỊ':<16} {'MỤC TIÊU 1':<10}")
    print("-" * 95)
    for rank, s in enumerate(stock_analyses, start=1):
        chg_str = f"{s['change_pct']:+.2f}%"
        prob_str = f"{s['ml_prob_up']:.1f}%"
        score_str = f"{s['total_score']:.1f}"
        print(f"{rank:<5} {s['ticker']:<6} {s['close']:<9.2f} {chg_str:<10} {s['rsi']:<6.1f} {s['vol_vs_ma20']:<9.2f} {prob_str:<12} {score_str:<7} {s['signal']:<16} {s['target_1']:<10.2f}")
    print("=" * 95)

    # In tóm tắt thị trường
    if market_summary:
        print(f"\n[Tổng Quan Thị Trường VN-INDEX]:")
        print(f"  - Điểm số: {market_summary.get('vnindex_close')} ({market_summary.get('vnindex_change_pct'):+.2f}%)")
        print(f"  - Trạng thái: {market_summary.get('market_sentiment')}")
        print(f"  - Phân bổ tín hiệu: {market_summary.get('buy_count')} Mua | {market_summary.get('hold_count')} Theo dõi | {market_summary.get('sell_count')} Bán")

    # 6. Xuất báo cáo Excel & HTML Dashboard
    print("\n[Bước 5/5] Đang xuất báo cáo chi tiết...")
    excel_path = reporter.export_excel(market_summary, stock_analyses)
    html_path = reporter.export_html_dashboard(market_summary, stock_analyses)

    print("\n>>> HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH THÀNH CÔNG! <<<")
    print(f"[*] Báo cáo Excel: {excel_path}")
    print(f"[*] Báo cáo HTML Dashboard: {html_path}")
    print(f"[*] Gợi ý: Bạn có thể mở trực tiếp file '{html_path.name}' trong trình duyệt để xem dashboard tương tác!")


if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(
        force_update=args.force_update,
        target_ticker=args.ticker,
        retrain=args.retrain,
        is_test=args.test_run
    )
