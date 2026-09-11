# -*- coding: utf-8 -*-
"""
FastAPI REST API Server cho Hệ thống Định lượng & Machine Learning VN30
Cung cấp các RESTful endpoints phục vụ Web Frontend (Vue 3), Mobile App và Bot cảnh báo.

Các cải tiến so với phiên bản cũ:
- asyncio.Lock bảo vệ STATE writes (fix race condition)
- run_in_executor cho blocking I/O calls (fix event loop block)
- Structured logging thay vì print()
- POST /refresh dùng BackgroundTasks (không timeout)
- Xóa importlib.reload, xóa duplicate mount /assets
- Health check đầy đủ thông tin hệ thống
- Feature computation caching (skip nếu không có nến mới)
- Startup time tracking
"""
import os
import logging
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd
import uvicorn

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import (
    VN30_TICKERS, SERVER_CONFIG, AUTO_REFRESH_CONFIG,
    MARKET_SCHEDULE_CONFIG, get_market_trading_status,
    get_vietnam_now, VIETNAM_TZ, get_today_date
)
from data_loader import DataLoader
from feature_engineering import add_technical_features
from ml_engine import StockPredictor
from quant_analyzer import QuantAnalyzer

# ==================== STRUCTURED LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("vn30-api")

# ==================== THREAD POOL CHO BLOCKING I/O ====================
# Dùng riêng cho các tác vụ nặng: gọi API vnstock, đọc/ghi CSV, tính toán ML
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="refresh-worker")

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="VN30 Quant & AI Intelligence API",
    description="Hệ thống API Phân tích Định lượng Đa nhân tố và Dự đoán Học máy rổ VN30",
    version="3.0.0"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=SERVER_CONFIG.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== RATE LIMITING ====================
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    HAS_RATE_LIMITER = True
    logger.info("Rate limiter khởi tạo thành công (200 req/phút/IP).")
except ImportError:
    HAS_RATE_LIMITER = False
    logger.warning("slowapi chưa cài đặt – bỏ qua rate limiting. Cài: pip install slowapi")

# ==================== NO-CACHE MIDDLEWARE ====================
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    """Middleware chống cache cho toàn bộ endpoint API."""
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ==================== STATE & LOCK ====================
STATE = {
    "data_loader": None,
    "predictor": None,
    "analyzer": None,
    "market_summary": {},
    "stock_analyses": [],
    "processed_stocks": {},
    "vnindex_df": None,
    "last_updated": None,
    "is_updating": False,
    "refresh_batch_index": 0,   # Vị trí batch hiện tại trong staggered refresh (0-based)
    "startup_time": None,        # Thời gian server khởi động (để tính uptime)
}

# asyncio.Lock bảo vệ tất cả các writes vào STATE
# Đảm bảo không có 2 goroutine đồng thời ghi/đọc dữ liệu chưa hoàn chỉnh
_STATE_LOCK = asyncio.Lock()


# ==================== FEATURE CACHING HELPER ====================
def _get_or_compute_features(ticker: str, raw_df: pd.DataFrame, vn_raw: pd.DataFrame | None) -> pd.DataFrame:
    """
    Tính toán feature chỉ khi có nến mới hơn cache hiện tại.
    Nếu dữ liệu giống hệt → trả về cached features để tránh tính lại ~1000 nến mỗi lần.
    """
    existing = STATE["processed_stocks"].get(ticker)
    if existing is not None and not existing.empty:
        last_existing = existing["time"].max()
        last_raw = raw_df["time"].max()
        if last_existing >= last_raw:
            # Không có nến mới hơn → dùng lại features đã tính
            return existing
    return add_technical_features(raw_df, vnindex_df=vn_raw)


# ==================== SYNC BLOCKING FUNCTIONS (chạy trong ThreadPool) ====================

def _sync_initialize_engine():
    """Khởi động và nạp dữ liệu ban đầu vào bộ nhớ RAM."""
    if STATE["data_loader"] is None:
        STATE["data_loader"] = DataLoader()
        STATE["predictor"] = StockPredictor()
        STATE["analyzer"] = QuantAnalyzer()

    # Nạp mô hình ML đã lưu; nếu không có → train mới trong background
    model_loaded = STATE["predictor"].load_model()
    if not model_loaded:
        logger.warning("Không tìm thấy model pkl đã lưu. Sẽ train mới sau khi nạp dữ liệu xong.")

    _sync_refresh_calculations()

    # Nếu chưa có model → train sau khi đã có dữ liệu
    if not model_loaded and STATE["processed_stocks"]:
        logger.info("Bắt đầu train ML model lần đầu (cross-sectional VN30)...")
        try:
            metrics = STATE["predictor"].train_model(STATE["processed_stocks"])
            logger.info(f"Train ML xong: AUC={metrics.get('mean_auc', 0):.3f}, Acc={metrics.get('mean_accuracy', 0):.3f}")
        except Exception as e:
            logger.error(f"Lỗi train ML: {e}")


def _sync_refresh_calculations(force_update_api: bool = False):
    """
    Tính toán lại toàn bộ VN30 (dùng lần đầu startup).
    Không dùng importlib.reload – QuantAnalyzer đã stable trong STATE.
    """
    loader = STATE["data_loader"]
    analyzer = STATE["analyzer"]      # Dùng instance đã có, không reload module
    predictor = STATE["predictor"]

    # 1. Nạp VN-INDEX
    vn_raw = loader.get_market_data("VNINDEX", force_update=force_update_api)
    if vn_raw is not None and not vn_raw.empty:
        STATE["vnindex_df"] = add_technical_features(vn_raw)

    # 2. Xử lý các mã có trong cache
    cache_files = list(loader.data_dir.glob("*.csv"))
    tickers_to_load = {f.stem.upper() for f in cache_files if f.stem.upper() not in ["VNINDEX", "VN30"]}

    if not tickers_to_load:
        tickers_to_load = {"FPT", "HPG", "TCB", "MWG", "VCB"}

    processed = {}
    analyses = []
    vn_raw_ref = STATE.get("vnindex_df")

    for t in sorted(tickers_to_load):
        raw_df = loader.get_ticker_data(t, force_update=force_update_api)
        if raw_df is not None and len(raw_df) >= 30:
            feat_df = _get_or_compute_features(t, raw_df, vn_raw_ref)
            processed[t] = feat_df
            ml_res = predictor.predict_latest(t, feat_df)
            analysis = analyzer.analyze_ticker(t, feat_df, ml_res)
            if analysis:
                analyses.append(analysis)

    market_summary = analyzer.analyze_market_regime(STATE["vnindex_df"], analyses)
    analyses.sort(key=lambda x: x.get("total_score", 0), reverse=True)

    STATE["processed_stocks"] = processed
    STATE["stock_analyses"] = analyses
    STATE["market_summary"] = market_summary
    STATE["last_updated"] = get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Full refresh xong: {len(analyses)} mã | last_updated={STATE['last_updated']}")


def _sync_refresh_batch(tickers_batch: list, force_update_api: bool = False):
    """
    Cập nhật một batch nhỏ (5 mã) – chạy trong ThreadPool, không block event loop.
    Staggered refresh: 5 mã/3 phút → sau 6 chu kỳ (~18 phút) toàn bộ VN30 được làm mới.
    """
    loader = STATE["data_loader"]
    predictor = STATE["predictor"]
    analyzer = STATE["analyzer"]
    vn_raw = STATE.get("vnindex_df")

    new_analyses = list(STATE["stock_analyses"])
    new_processed = dict(STATE["processed_stocks"])

    for t in tickers_batch:
        try:
            raw_df = loader.get_ticker_data(t, force_update=force_update_api)
            if raw_df is not None and len(raw_df) >= 30:
                feat_df = _get_or_compute_features(t, raw_df, vn_raw)
                new_processed[t] = feat_df
                ml_res = predictor.predict_latest(t, feat_df)
                analysis = analyzer.analyze_ticker(t, feat_df, ml_res)
                if analysis:
                    new_analyses = [a for a in new_analyses if a["ticker"] != t]
                    new_analyses.append(analysis)
        except Exception as e:
            logger.warning(f"[Batch Refresh] Lỗi cập nhật {t}: {e}")

    new_analyses.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    market_summary = analyzer.analyze_market_regime(vn_raw, new_analyses)

    STATE["processed_stocks"] = new_processed
    STATE["stock_analyses"] = new_analyses
    STATE["market_summary"] = market_summary
    STATE["last_updated"] = get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== ASYNC WRAPPERS (chạy blocking code trong ThreadPool) ====================

async def _async_refresh_batch(tickers_batch: list, force_update_api: bool = False):
    """Wrapper async cho _sync_refresh_batch – không block event loop."""
    loop = asyncio.get_event_loop()
    async with _STATE_LOCK:
        await loop.run_in_executor(_executor, _sync_refresh_batch, tickers_batch, force_update_api)


async def _async_full_refresh(force_update_api: bool = False):
    """Wrapper async cho _sync_refresh_calculations – dùng bởi POST /api/market/refresh."""
    loop = asyncio.get_event_loop()
    async with _STATE_LOCK:
        await loop.run_in_executor(_executor, _sync_refresh_calculations, force_update_api)


# ==================== BACKGROUND WORKERS ====================

async def auto_refresh_worker():
    """
    Staggered Batch Auto-Refresh Worker:
    - Mỗi chu kỳ (3 phút) quét 1 batch nhỏ (5 mã) chạy trong ThreadPool.
    - Event loop không bị block → request API vẫn phản hồi bình thường trong lúc refresh.
    - Sau 6 chu kỳ (~18 phút), toàn bộ 30 mã VN30 được làm mới 1 vòng.
    """
    batch_size = AUTO_REFRESH_CONFIG.get("batch_size", 5)
    all_tickers = sorted(VN30_TICKERS)

    while True:
        interval = AUTO_REFRESH_CONFIG.get("interval_seconds", 180)
        await asyncio.sleep(interval)

        if not AUTO_REFRESH_CONFIG.get("enabled", True):
            continue

        try:
            market_status = get_market_trading_status()
            can_fetch = market_status.get("can_fetch_stocks", False) and AUTO_REFRESH_CONFIG.get("fetch_new_bars", True)

            batch_idx = STATE["refresh_batch_index"]
            start = batch_idx * batch_size
            current_batch = all_tickers[start: start + batch_size]

            if not current_batch:
                # Reset vòng + cập nhật VNINDEX trong ThreadPool
                STATE["refresh_batch_index"] = 0
                loader = STATE["data_loader"]
                loop = asyncio.get_event_loop()
                vn_raw = await loop.run_in_executor(
                    _executor, loader.get_market_data, "VNINDEX", None, None, can_fetch
                )
                if vn_raw is not None and not vn_raw.empty:
                    feat = await loop.run_in_executor(_executor, add_technical_features, vn_raw)
                    STATE["vnindex_df"] = feat
                logger.info("↺ Reset vòng quét VN30 + cập nhật VNINDEX.")
                continue

            if can_fetch:
                batch_label = f"Batch {batch_idx + 1}/{len(all_tickers)//batch_size} ({', '.join(current_batch)})"
                logger.info(f"[Auto-Refresh] 🟢 {market_status['session_name']} | {batch_label}")
                await _async_refresh_batch(current_batch, force_update_api=True)
            else:
                logger.info(f"[Auto-Refresh] ⏸ {market_status['session_name']}: {market_status['detail']}")

            # Tiến sang batch tiếp theo
            next_start = start + batch_size
            STATE["refresh_batch_index"] = 0 if next_start >= len(all_tickers) else batch_idx + 1
            logger.info(f"[Auto-Refresh] Hoàn tất chu kỳ | last_updated={STATE['last_updated']}")

        except Exception as e:
            logger.error(f"[Auto-Refresh Worker] Lỗi: {e}", exc_info=True)


async def keep_alive_worker():
    """
    Keep-Alive Worker – Ngăn Render.com spin-down sau 15 phút idle:
    Tự ping /health mỗi 10 phút để giữ server luôn awake.
    """
    import httpx
    await asyncio.sleep(60)  # Chờ server khởi động hoàn tất
    while True:
        await asyncio.sleep(600)  # 10 phút
        try:
            port = int(os.environ.get("PORT", 8000))
            async with httpx.AsyncClient() as client:
                r = await client.get(f"http://localhost:{port}/health", timeout=10)
                logger.info(f"[Keep-Alive] Ping ✓ ({r.status_code}) lúc {get_vietnam_now().strftime('%H:%M:%S')}")
        except Exception as e:
            logger.warning(f"[Keep-Alive] Ping thất bại: {e}")


# ==================== STARTUP ====================

@app.on_event("startup")
async def on_startup():
    STATE["startup_time"] = get_vietnam_now()
    logger.info("=== VN30 Quant & AI Intelligence API v3.0.0 đang khởi động ===")

    # Chạy initialization nặng trong ThreadPool (không block event loop)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _sync_initialize_engine)

    if AUTO_REFRESH_CONFIG.get("enabled", True):
        asyncio.create_task(auto_refresh_worker())
        asyncio.create_task(keep_alive_worker())
        logger.info(
            f"Auto-Refresh Staggered Batch: mỗi {AUTO_REFRESH_CONFIG.get('interval_seconds', 180)}s, "
            f"batch={AUTO_REFRESH_CONFIG.get('batch_size', 5)} mã."
        )
        logger.info("Keep-Alive Worker: ping mỗi 10 phút – ngăn Render.com spin-down.")

    logger.info("=== Hệ thống API sẵn sàng phục vụ! ===")


# ==================== STATIC FILES (1 lần duy nhất) ====================
FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# ==================== ROOT & HEALTH ====================

@app.api_route("/", methods=["GET", "HEAD"], tags=["Giao diện"])
def get_root():
    """Truy cập giao diện Web Vue 3 hoặc thông tin hệ thống."""
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": "VN30 Quant & AI Intelligence API",
        "version": "3.0.0",
        "status": "online",
        "last_updated": STATE["last_updated"],
        "docs_url": "/docs"
    }


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Hệ thống"])
def health_check():
    """Health check đầy đủ thông tin hệ thống – hỗ trợ UptimeRobot và Render.com."""
    startup = STATE.get("startup_time")
    uptime_s = int((get_vietnam_now() - startup).total_seconds()) if startup else 0
    predictor = STATE.get("predictor")
    return {
        "status": "ok",
        "version": "3.0.0",
        "stocks_loaded": len(STATE.get("stock_analyses", [])),
        "model_ready": predictor is not None and predictor.model is not None,
        "last_updated": STATE.get("last_updated"),
        "uptime_seconds": uptime_s,
        "market_status": get_market_trading_status().get("session_name", "Unknown"),
        "batch_index": STATE.get("refresh_batch_index", 0),
    }


# ==================== MARKET ENDPOINTS ====================

@app.get("/api/market/overview", tags=["Thị trường"])
def get_market_overview():
    """Lấy thông tin tổng quan chỉ số VN-INDEX, trạng thái thị trường và độ rộng."""
    summary = dict(STATE.get("market_summary", {}))
    summary["last_updated"] = STATE.get("last_updated")
    summary["auto_refresh"] = AUTO_REFRESH_CONFIG
    summary["market_schedule"] = get_market_trading_status()
    return {"status": "success", "data": summary}


@app.get("/api/market/recommendation-report", tags=["Báo cáo khuyến nghị & Lý do VN30"])
def get_market_recommendation_report():
    """Báo cáo phân bổ khuyến nghị Mua/Chờ/Bán và giải trình lý do từng cổ phiếu VN30."""
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
            "last_updated": STATE.get("last_updated")
        }
    }


@app.post("/api/market/refresh", tags=["Thị trường"])
async def post_refresh_market(
    background_tasks: BackgroundTasks,
    force_api: bool = Query(True, description="Lấy nến Realtime mới nhất từ API")
):
    """
    Kích hoạt làm mới dữ liệu trong background (không block, không timeout).
    Trả về ngay lập tức; dữ liệu được cập nhật sau 10-60 giây tuỳ tải.
    """
    if STATE.get("is_updating"):
        return {
            "status": "already_updating",
            "message": "Đang có refresh đang chạy, vui lòng chờ...",
            "last_updated": STATE.get("last_updated")
        }

    async def _bg_refresh():
        STATE["is_updating"] = True
        try:
            await _async_full_refresh(force_update_api=force_api)
        finally:
            STATE["is_updating"] = False

    background_tasks.add_task(_bg_refresh)
    return {
        "status": "accepted",
        "message": "Đã nhận lệnh làm mới. Dữ liệu sẽ cập nhật trong vài giây.",
        "last_updated": STATE.get("last_updated")
    }


@app.get("/api/config/auto-refresh", tags=["Cấu hình"])
def get_auto_refresh_config():
    """Lấy thông số chu kỳ tự động làm mới ngầm."""
    return {
        "status": "success",
        "data": AUTO_REFRESH_CONFIG,
        "market_schedule": get_market_trading_status(),
        "schedule_config": MARKET_SCHEDULE_CONFIG,
        "last_updated": STATE.get("last_updated")
    }


# ==================== VN30 LEADERBOARD ====================

@app.get("/api/vn30/leaderboard", tags=["Bảng xếp hạng VN30"])
def get_vn30_leaderboard(
    signal: Optional[str] = Query(None, description="Lọc theo tín hiệu: BUY, SELL, HOLD"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo mã cổ phiếu (ví dụ: FPT)"),
    sort_by: str = Query("total_score", description="Trường sắp xếp: total_score, ml_prob_up, change_pct, rsi"),
    order: str = Query("desc", description="Thứ tự: desc hoặc asc")
):
    """Lấy danh sách bảng xếp hạng VN30 theo điểm Định lượng và AI."""
    results = list(STATE.get("stock_analyses", []))

    if search:
        s_upper = search.strip().upper()
        results = [s for s in results if s_upper in s["ticker"]]

    if signal:
        sig_upper = signal.strip().upper()
        if sig_upper == "BUY":
            results = [s for s in results if "MUA" in s.get("signal", "")]
        elif sig_upper == "SELL":
            results = [s for s in results if "BÁN" in s.get("signal", "")]
        elif sig_upper == "HOLD":
            results = [s for s in results if "QUAN SÁT" in s.get("signal", "") or "THEO DÕI" in s.get("signal", "")]

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
        "last_updated": STATE.get("last_updated")
    }


# ==================== STOCK ENDPOINTS ====================

@app.get("/api/stocks/{ticker}/analysis", tags=["Chi tiết cổ phiếu"])
def get_stock_analysis(ticker: str):
    """Lấy chi tiết phân tích định lượng, ML, vùng mua, Target và Stoploss cho 1 mã."""
    ticker = ticker.upper()
    for s in STATE.get("stock_analyses", []):
        if s["ticker"] == ticker:
            return {"status": "success", "data": s}

    loader = STATE.get("data_loader")
    if not loader:
        raise HTTPException(status_code=503, detail="Server đang khởi động, vui lòng thử lại sau")

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
    Trả về dữ liệu nến lịch sử chuẩn TradingView Lightweight Charts.
    Format: { time, open, high, low, close, volume }
    """
    ticker = ticker.upper()
    df = None
    if ticker in STATE.get("processed_stocks", {}):
        df = STATE["processed_stocks"][ticker]
    elif ticker == "VNINDEX" and STATE.get("vnindex_df") is not None:
        df = STATE["vnindex_df"]
    else:
        loader = STATE.get("data_loader")
        if loader:
            df = loader.get_ticker_data(ticker)

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


@app.get("/api/stocks/{ticker}/price", tags=["Giá Realtime"])
def get_stock_price(ticker: str):
    """
    Lấy giá close mới nhất từ RAM cache (< 1ms, không gọi API bên ngoài).
    Dùng để poll giá realtime mà không tiêu tốn rate-limit vnstock.
    """
    ticker = ticker.upper()
    df = None
    if ticker in STATE.get("processed_stocks", {}):
        df = STATE["processed_stocks"][ticker]
    elif ticker == "VNINDEX" and STATE.get("vnindex_df") is not None:
        df = STATE["vnindex_df"]

    if df is None or df.empty:
        for s in STATE.get("stock_analyses", []):
            if s["ticker"] == ticker:
                return {
                    "status": "success",
                    "ticker": ticker,
                    "close": s.get("close"),
                    "change_pct": s.get("change_pct"),
                    "last_updated": STATE.get("last_updated")
                }
        raise HTTPException(status_code=404, detail=f"Không có dữ liệu giá cho {ticker}")

    last = df.iloc[-1]
    close = round(float(last.get("close", 0)), 2)
    open_ = round(float(last.get("open", close)), 2)
    high = round(float(last.get("high", close)), 2)
    low = round(float(last.get("low", close)), 2)
    volume = int(last.get("volume", 0))
    change_pct = round((close - open_) / open_ * 100, 2) if open_ > 0 else 0.0
    time_str = last["time"].strftime("%Y-%m-%d") if hasattr(last["time"], "strftime") else str(last["time"])[:10]

    return {
        "status": "success",
        "ticker": ticker,
        "date": time_str,
        "close": close,
        "open": open_,
        "high": high,
        "low": low,
        "volume": volume,
        "change_pct": change_pct,
        "last_updated": STATE.get("last_updated")
    }


# ==================== NEWS & FLOW ENDPOINTS ====================

from news_service import NewsService
from market_flow_service import MarketFlowService

NEWS_SERVICE = NewsService()
MARKET_FLOW_SERVICE = MarketFlowService()


@app.get("/api/market/trading-flow", tags=["Giao dịch Khối ngoại & Trong nước"])
def get_market_trading_flow(
    period: str = Query("today", description="Chu kỳ: today, 1_week, 1_month")
):
    """
    Báo cáo ước tính khối lượng giao dịch Khối Ngoại & Khối Nội rổ VN30.
    Lưu ý: Dữ liệu dòng tiền là ước tính tính toán dựa trên tỷ trọng lịch sử,
    không phải dữ liệu khớp lệnh thực tế từ sàn giao dịch.
    """
    if period not in ["today", "1_week", "1_month"]:
        period = "today"
    result = MARKET_FLOW_SERVICE.get_trading_flow(period=period)
    # Thêm disclaimer rõ ràng
    result["data_note"] = "Ước tính dựa trên tỷ trọng lịch sử khối ngoại. Không phải dữ liệu khớp lệnh thực tế."
    return result


@app.get("/api/news/feed", tags=["Tin Tức Tài Chính"])
def get_news_feed(
    region: Optional[str] = Query(None),
    asset: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Lấy tin tức tài chính thị trường mới nhất trong nước và quốc tế."""
    try:
        items = NEWS_SERVICE.get_market_news(region=region, asset=asset, search=search)
        return {
            "status": "success",
            "count": len(items),
            "data": items,
            "last_updated": get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Lỗi /api/news/feed: {e}")
        fallback_items = NEWS_SERVICE._get_fallback_news()
        return {
            "status": "success",
            "count": len(fallback_items),
            "data": fallback_items,
            "last_updated": get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")
        }


@app.get("/api/news/risk-assessment", tags=["Đánh Giá Rủi Ro"])
def get_news_risk_assessment():
    """Báo cáo đánh giá rủi ro thị trường từ biến số tin tức vĩ mô/địa chính trị."""
    try:
        report = NEWS_SERVICE.get_risk_assessment_report(state=STATE, flow_service=MARKET_FLOW_SERVICE)
        return {"status": "success", "data": report}
    except Exception as e:
        logger.error(f"Lỗi /api/news/risk-assessment: {e}")
        fallback_report = NEWS_SERVICE.get_risk_assessment_report(state=None, flow_service=None)
        return {"status": "success", "data": fallback_report}


@app.get("/api/news/hot-movers", tags=["Cổ Phiếu Tăng Nóng & Giải Mã"])
def get_hot_movers():
    """Danh sách cổ phiếu tăng nóng trong phiên và giải mã nguyên nhân."""
    try:
        movers = NEWS_SERVICE.get_hot_movers(state=STATE)
        return {"status": "success", "count": len(movers), "data": movers}
    except Exception as e:
        logger.error(f"Lỗi /api/news/hot-movers: {e}")
        fallback_movers = NEWS_SERVICE.get_hot_movers(state=None)
        return {"status": "success", "count": len(fallback_movers), "data": fallback_movers}


# ==================== SPA FALLBACK ====================

if FRONTEND_DIST.exists():
    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint không tồn tại")

        target_file = FRONTEND_DIST / full_path
        if full_path and target_file.exists() and target_file.is_file():
            return FileResponse(target_file)

        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Giao diện chưa được build.")


# ==================== MAIN ====================

if __name__ == "__main__":
    host = os.environ.get("HOST", SERVER_CONFIG.get("host", "0.0.0.0"))
    port = int(os.environ.get("PORT", SERVER_CONFIG.get("port", 8000)))
    logger.info(f"Khởi động máy chủ tại http://{host}:{port}")
    uvicorn.run("api_server:app", host=host, port=port, reload=False)
