# -*- coding: utf-8 -*-
"""
FastAPI REST API Server cho Hệ thống Định lượng & Machine Learning VN30
Cung cấp các RESTful endpoints phục vụ Web Frontend (Vue 3), Mobile App và Bot cảnh báo.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import asyncio
from config import (
    VN30_TICKERS, SERVER_CONFIG, AUTO_REFRESH_CONFIG,
    MARKET_SCHEDULE_CONFIG, get_market_trading_status,
    get_vietnam_now, VIETNAM_TZ
)
from data_loader import DataLoader
from feature_engineering import add_technical_features
from ml_engine import StockPredictor
from quant_analyzer import QuantAnalyzer

app = FastAPI(
    title="VN30 Quant & AI Intelligence API",
    description="Hệ thống API Phân tích Định lượng Đa nhân tố và Dự đoán Học máy rổ VN30",
    version="2.5.0"
)

# Cấu hình CORS mở rộng cho Vue.js và Mobile Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=SERVER_CONFIG.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quản lý bộ nhớ đệm State trong RAM để API phản hồi tức thì dưới 10ms
STATE = {
    "data_loader": None,
    "predictor": None,
    "analyzer": None,
    "market_summary": {},
    "stock_analyses": [],
    "processed_stocks": {},
    "vnindex_df": None,
    "last_updated": None,
    "is_updating": False
}


def initialize_engine():
    """Khởi động và nạp dữ liệu ban đầu vào bộ nhớ RAM."""
    if STATE["data_loader"] is None:
        STATE["data_loader"] = DataLoader()
        STATE["predictor"] = StockPredictor()
        STATE["analyzer"] = QuantAnalyzer()
        # Nạp mô hình ML đã lưu
        STATE["predictor"].load_model()

    _refresh_calculations()


def _refresh_calculations(force_update_api: bool = False):
    """Tính toán lại các chỉ số và dự đoán cho các mã đã nạp."""
    loader = STATE["data_loader"]
    predictor = STATE["predictor"]
    analyzer = STATE["analyzer"]

    # 1. Nạp VN-INDEX
    vn_raw = loader.get_market_data("VNINDEX", force_update=force_update_api)
    if vn_raw is not None and not vn_raw.empty:
        STATE["vnindex_df"] = add_technical_features(vn_raw)

    # 2. Xử lý các mã có trong cache (hoặc quét VN30)
    # Lấy danh sách các file trong cache
    cache_files = list(loader.data_dir.glob("*.csv"))
    tickers_to_load = set()
    for f in cache_files:
        stem = f.stem.upper()
        if stem not in ["VNINDEX", "VN30"]:
            tickers_to_load.add(stem)

    # Nếu chưa có mã nào trong cache, mặc định nạp 5 mã cơ bản
    if not tickers_to_load:
        tickers_to_load = {"FPT", "HPG", "TCB", "MWG", "VCB"}

    processed = {}
    analyses = []

    for t in sorted(list(tickers_to_load)):
        raw_df = loader.get_ticker_data(t, force_update=force_update_api)
        if raw_df is not None and len(raw_df) >= 30:
            feat_df = add_technical_features(raw_df, vnindex_df=vn_raw)
            processed[t] = feat_df
            
            ml_res = predictor.predict_latest(t, feat_df)
            analysis = analyzer.analyze_ticker(t, feat_df, ml_res)
            if analysis:
                analyses.append(analysis)

    # Đánh giá thị trường chung
    market_summary = analyzer.analyze_market_regime(STATE["vnindex_df"], analyses)

    # Sắp xếp theo điểm Quant
    analyses.sort(key=lambda x: x.get("total_score", 0), reverse=True)

    STATE["processed_stocks"] = processed
    STATE["stock_analyses"] = analyses
    STATE["market_summary"] = market_summary
    STATE["last_updated"] = get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")


async def auto_refresh_worker():
    """
    Luồng worker chạy ngầm định kỳ tự động làm mới dữ liệu:
    - Cổ phiếu VN30: Chỉ tải nến mới từ API trong giờ giao dịch (09:00 - 15:00, Thứ 2 - Thứ 6).
    - Ngoài giờ giao dịch: Tạm dừng quét API, giữ nguyên dữ liệu chốt phiên để chống quá tải & tránh rate-limit.
    - Tin tức & Đánh giá rủi ro: Luôn cập nhật liên tục 24/7 theo thời gian thực.
    """
    while True:
        interval = AUTO_REFRESH_CONFIG.get("interval_seconds", 60)
        await asyncio.sleep(interval)
        if AUTO_REFRESH_CONFIG.get("enabled", True):
            try:
                # Kiểm tra trạng thái phiên giao dịch chứng khoán
                market_status = get_market_trading_status()
                can_fetch_stocks = market_status.get("can_fetch_stocks", False) and AUTO_REFRESH_CONFIG.get("fetch_new_bars", True)

                if can_fetch_stocks:
                    print(f"\n[Auto-Refresh Worker] 🟢 Đang trong phiên ({market_status['session_name']}). Đang quét nến cổ phiếu mới từ API...")
                    _refresh_calculations(force_update_api=True)
                else:
                    print(f"\n[Auto-Refresh Worker] ⏸️ {market_status['session_name']}: {market_status['detail']}")
                    print("[Auto-Refresh Worker] 🛡️ Chế độ tiết kiệm tài nguyên: Giữ nguyên dữ liệu chốt phiên, không gọi API ngoài.")
                    _refresh_calculations(force_update_api=False)

                print(f"[Auto-Refresh Worker] 🌐 Tin tức & Đánh giá rủi ro: Cập nhật thời gian thực 24/7.")
                print(f"[Auto-Refresh Worker] Hoàn tất chu kỳ lúc {STATE['last_updated']}.")
            except Exception as e:
                print(f"[Auto-Refresh Worker Lỗi]: {e}")


@app.on_event("startup")
async def on_startup():
    print("[FastAPI] Khởi tạo các module Quant và nạp dữ liệu...")
    initialize_engine()
    if AUTO_REFRESH_CONFIG.get("enabled", True):
        asyncio.create_task(auto_refresh_worker())
        print(f"[FastAPI] Đã kích hoạt Auto-Refresh ngầm mỗi {AUTO_REFRESH_CONFIG.get('interval_seconds', 60)} giây (Cấu hình tại config.py).")
    print("[FastAPI] Hệ thống API đã sẵn sàng phục vụ!")


# ==================== PHỤC VỤ GIAO DIỆN VUE 3 ====================
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

@app.api_route("/", methods=["GET", "HEAD"], tags=["Giao diện & Thông tin"])
def get_root():
    """Truy cập giao diện Web Vue 3 (nếu đã build) hoặc thông tin hệ thống."""
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return {
        "system": "VN30 Quant & AI Intelligence API",
        "version": "2.5.0",
        "status": "online",
        "last_updated": STATE["last_updated"],
        "docs_url": "/docs"
    }


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Hệ thống"])
def health_check():
    """Endpoint kiểm tra sức khỏe hệ thống (Health Check) hỗ trợ cả GET và HEAD cho UptimeRobot."""
    return {"status": "ok", "message": "Server is healthy and running"}


@app.get("/api/market/overview", tags=["Thị trường"])
def get_market_overview():
    """Lấy thông tin tổng quan chỉ số VN-INDEX, trạng thái thị trường và độ rộng."""
    if not STATE["market_summary"]:
        _refresh_calculations()

    summary = dict(STATE["market_summary"])
    summary["last_updated"] = STATE["last_updated"]
    summary["auto_refresh"] = AUTO_REFRESH_CONFIG
    summary["market_schedule"] = get_market_trading_status()
    return {
        "status": "success",
        "data": summary
    }


@app.get("/api/market/recommendation-report", tags=["Báo cáo khuyến nghị & Lý do VN30"])
def get_market_recommendation_report():
    """
    Báo cáo tổng hợp phân bổ khuyến nghị Mua/Chờ/Bán theo tỷ lệ %
    và giải trình chi tiết lý do từng cổ phiếu VN30 nên mua/bán/giữ,
    tin tức tác động và động lực tăng giá.
    """
    if not STATE["stock_analyses"]:
        _refresh_calculations()

    market_summary = STATE.get("market_summary", {})
    all_stocks = STATE.get("stock_analyses", [])

    buy_stocks = [s for s in all_stocks if "MUA" in s.get("signal", "")]
    sell_stocks = [s for s in all_stocks if "BÁN" in s.get("signal", "")]
    hold_stocks = [s for s in all_stocks if s not in buy_stocks and s not in sell_stocks]

    total = len(all_stocks) or 1
    allocation = {
        "buy": {
            "label": "Nên Mua",
            "count": len(buy_stocks),
            "percentage": round((len(buy_stocks) / total) * 100.0, 1),
            "tickers": [s["ticker"] for s in buy_stocks]
        },
        "hold": {
            "label": "Chờ / Nắm Giữ",
            "count": len(hold_stocks),
            "percentage": round((len(hold_stocks) / total) * 100.0, 1),
            "tickers": [s["ticker"] for s in hold_stocks]
        },
        "sell": {
            "label": "Nên Bán / Hạ Tỷ Trọng",
            "count": len(sell_stocks),
            "percentage": round((len(sell_stocks) / total) * 100.0, 1),
            "tickers": [s["ticker"] for s in sell_stocks]
        }
    }

    return {
        "status": "success",
        "data": {
            "market_sentiment": market_summary.get("market_sentiment", "Thận Trọng / Tích Lũy Chờ Xu Hướng Mới"),
            "regime_explanation": market_summary.get("regime_explanation", ""),
            "vnindex_close": market_summary.get("vnindex_close"),
            "vnindex_change_pct": market_summary.get("vnindex_change_pct"),
            "total_stocks": total,
            "allocation": allocation,
            "all_stocks": all_stocks,
            "buy_stocks": buy_stocks,
            "hold_stocks": hold_stocks,
            "sell_stocks": sell_stocks,
            "last_updated": STATE["last_updated"]
        }
    }


@app.post("/api/market/refresh", tags=["Thị trường"])
def post_refresh_market():
    """Kích hoạt làm mới và tính toán lại dữ liệu từ cache."""
    _refresh_calculations(force_update_api=False)
    return {
        "status": "success",
        "message": "Đã làm mới và tính toán lại dữ liệu thành công",
        "last_updated": STATE["last_updated"]
    }


@app.get("/api/config/auto-refresh", tags=["Cấu hình"])
def get_auto_refresh_config():
    """Lấy thông số chu kỳ tự động làm mới ngầm được định nghĩa trong config.py."""
    return {
        "status": "success",
        "data": AUTO_REFRESH_CONFIG,
        "market_schedule": get_market_trading_status(),
        "schedule_config": MARKET_SCHEDULE_CONFIG,
        "last_updated": STATE["last_updated"]
    }


@app.get("/api/vn30/leaderboard", tags=["Bảng xếp hạng VN30"])
def get_vn30_leaderboard(
    signal: Optional[str] = Query(None, description="Lọc theo tín hiệu: BUY, SELL, HOLD"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo mã cổ phiếu (ví dụ: FPT)"),
    sort_by: str = Query("total_score", description="Trường sắp xếp: total_score, ml_prob_up, change_pct, rsi"),
    order: str = Query("desc", description="Thứ tự: desc hoặc asc")
):
    """
    Lấy danh sách bảng xếp hạng cổ phiếu VN30 theo điểm Định lượng và AI.
    Hỗ trợ tìm kiếm, lọc theo tín hiệu và sắp xếp động.
    """
    if not STATE["stock_analyses"]:
        _refresh_calculations()

    results = list(STATE["stock_analyses"])

    # Lọc theo tìm kiếm mã
    if search:
        s_upper = search.strip().upper()
        results = [s for s in results if s_upper in s["ticker"]]

    # Lọc theo tín hiệu
    if signal:
        sig_upper = signal.strip().upper()
        if sig_upper == "BUY":
            results = [s for s in results if "MUA" in s.get("signal", "")]
        elif sig_upper == "SELL":
            results = [s for s in results if "BÁN" in s.get("signal", "")]
        elif sig_upper == "HOLD":
            results = [s for s in results if "QUAN SÁT" in s.get("signal", "") or "THEO DÕI" in s.get("signal", "")]

    # Sắp xếp
    reverse = (order.lower() == "desc")
    if sort_by in ["total_score", "ml_prob_up", "change_pct", "rsi", "close", "vol_vs_ma20"]:
        results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "signal":
        def get_signal_rank(sig):
            s = str(sig or "").upper()
            if "MUA MẠNH" in s: return 6
            if "MUA" in s: return 5
            if "QUAN SÁT" in s: return 4
            if "THEO DÕI" in s: return 3
            if "BÁN MẠNH" in s: return 1
            if "BÁN" in s: return 2
            return 3.5
        results.sort(key=lambda x: (get_signal_rank(x.get("signal")), x.get("total_score", 0)), reverse=reverse)

    return {
        "status": "success",
        "count": len(results),
        "data": results,
        "last_updated": STATE["last_updated"]
    }


@app.get("/api/stocks/{ticker}/analysis", tags=["Chi tiết cổ phiếu"])
def get_stock_analysis(ticker: str):
    """Lấy chi tiết phân tích định lượng, ML, vùng mua, Target và Stoploss cho 1 mã."""
    ticker = ticker.upper()
    analyses = STATE["stock_analyses"]
    for s in analyses:
        if s["ticker"] == ticker:
            return {"status": "success", "data": s}

    # Nếu chưa có trong danh sách phân tích sẵn, tính toán trực tiếp
    loader = STATE["data_loader"]
    df = loader.get_ticker_data(ticker)
    if df is None or len(df) < 30:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy dữ liệu cho mã {ticker}")

    feat_df = add_technical_features(df, vnindex_df=STATE.get("vnindex_df"))
    ml_res = STATE["predictor"].predict_latest(ticker, feat_df)
    analysis = STATE["analyzer"].analyze_ticker(ticker, feat_df, ml_res)

    return {"status": "success", "data": analysis}


@app.get("/api/stocks/{ticker}/candles", tags=["Biểu đồ nến"])
def get_stock_candles(ticker: str, limit: int = Query(150, description="Số phiên nến lịch sử")):
    """
    Trả về dữ liệu chuỗi nến lịch sử chuẩn hóa theo định dạng TradingView Lightweight Charts.
    Format mỗi nến: { time: 'YYYY-MM-DD', open: float, high: float, low: float, close: float, volume: int }
    """
    ticker = ticker.upper()
    df = None
    if ticker in STATE["processed_stocks"]:
        df = STATE["processed_stocks"][ticker]
    elif ticker == "VNINDEX" and STATE.get("vnindex_df") is not None:
        df = STATE["vnindex_df"]
    else:
        df = STATE["data_loader"].get_ticker_data(ticker)

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"Không có dữ liệu nến cho {ticker}")

    sub = df.tail(limit).copy()
    candles = []
    for _, row in sub.iterrows():
        t_str = row['time'].strftime("%Y-%m-%d") if hasattr(row['time'], 'strftime') else str(row['time'])[:10]
        candles.append({
            "time": t_str,
            "open": round(float(row['open']), 2),
            "high": round(float(row['high']), 2),
            "low": round(float(row['low']), 2),
            "close": round(float(row['close']), 2),
            "volume": int(row['volume'])
        })

    return {
        "status": "success",
        "ticker": ticker,
        "count": len(candles),
        "data": candles
    }


from news_service import NewsService
from market_flow_service import MarketFlowService

NEWS_SERVICE = NewsService()
MARKET_FLOW_SERVICE = MarketFlowService()


# ==================== ENDPOINTS GIAO DỊCH KHỐI NGOẠI & TRONG NƯỚC ====================

@app.get("/api/market/trading-flow", tags=["Giao dịch Khối ngoại & Trong nước"])
def get_market_trading_flow(period: str = Query("today", description="Chu kỳ: today (hôm nay), 1_week (1 tuần qua), 1_month (1 tháng qua)")):
    """
    Báo cáo tổng khối lượng giao dịch mua & bán (triệu cổ phiếu)
    của nhà đầu tư nước ngoài (khối ngoại) và nhà đầu tư trong nước (khối nội) rổ VN30.
    Hỗ trợ xem theo: Hôm nay (today), 1 tuần qua (1_week), 1 tháng qua (1_month).
    """
    if period not in ["today", "1_week", "1_month"]:
        period = "today"
    return MARKET_FLOW_SERVICE.get_trading_flow(period=period)


# ==================== ENDPOINTS TIN TỨC & RỦI RO ====================

@app.get("/api/news/feed", tags=["Tin Tức Tài Chính"])
def get_news_feed(
    region: Optional[str] = Query(None, description="Lọc theo khu vực: domestic (trong nước), international (quốc tế)"),
    asset: Optional[str] = Query(None, description="Lọc theo loại tài sản: stocks, gold, btc, politics, macro"),
    search: Optional[str] = Query(None, description="Tìm kiếm từ khóa tin tức")
):
    """Lấy danh sách tin tức tài chính thị trường mới nhất trong nước và quốc tế."""
    items = NEWS_SERVICE.get_market_news(region=region, asset=asset, search=search)
    return {
        "status": "success",
        "count": len(items),
        "data": items,
        "last_updated": get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/news/risk-assessment", tags=["Đánh Giá Rủi Ro"])
def get_news_risk_assessment():
    """Lấy báo cáo phân tích và đánh giá rủi ro thị trường từ các biến số tin tức vĩ mô/địa chính trị."""
    report = NEWS_SERVICE.get_risk_assessment_report()
    return {
        "status": "success",
        "data": report
    }


# ==================== PHỤC VỤ GIAO DIỆN TĨNH VUE 3 (ALL-IN-ONE SPA) ====================
FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_spa(full_path: str):
        # Tránh can thiệp các API endpoint nếu bị gọi sai path
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint không tồn tại")

        # Nếu yêu cầu file tĩnh cụ thể có sẵn trong thư mục dist (như favicon.ico, logo...)
        target_file = FRONTEND_DIST / full_path
        if full_path and target_file.exists() and target_file.is_file():
            return FileResponse(target_file)

        # Mặc định trả về index.html cho các route phía Vue SPA
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Giao diện chưa được build.")


if __name__ == "__main__":
    host = os.environ.get("HOST", SERVER_CONFIG.get("host", "0.0.0.0"))
    port = int(os.environ.get("PORT", SERVER_CONFIG.get("port", 8000)))
    print(f"[*] Khởi động máy chủ tại http://{host}:{port}")
    uvicorn.run("api_server:app", host=host, port=port, reload=False)
