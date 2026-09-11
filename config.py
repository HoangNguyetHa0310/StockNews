# -*- coding: utf-8 -*-
"""
Cấu hình hệ thống Phân tích Định lượng & Dự đoán Machine Learning VN30
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import os

# ==================== TỰ ĐỘNG ĐỌC BIẾN MÔI TRƯỜNG & VNSTOCK API KEY ====================
def _load_env_file():
    """Tự động đọc file .env nếu có mà không cần cài thêm thư viện phụ thuộc."""
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# Kích hoạt VNSTOCK API Key nếu có
VNSTOCK_KEY = os.environ.get("VNSTOCK_API_KEY", "")
if VNSTOCK_KEY:
    try:
        from vnstock.core import setup_api_key
        setup_api_key(VNSTOCK_KEY)
        print("[VNSTOCK] Đã thiết lập API Key thành công (Nâng cấp hạn mức dữ liệu)")
    except Exception as e:
        print(f"[VNSTOCK] Lưu ý khi nạp API Key: {e}")

# ==================== MÚI GIỜ HỆ THỐNG ====================
# Chuẩn hóa múi giờ Việt Nam (UTC+7 / Asia/Ho_Chi_Minh) cho toàn bộ backend,
# đảm bảo hoạt động chính xác cả khi chạy local và khi deploy trên Cloud (Render, Docker, VPS chạy múi giờ UTC).
VIETNAM_TZ = timezone(timedelta(hours=7))

def get_vietnam_now() -> datetime:
    """Lấy thời gian hiện tại chuẩn theo múi giờ Việt Nam (UTC+7)."""
    return datetime.now(VIETNAM_TZ)

# ==================== ĐƯỜNG DẪN HỆ THỐNG ====================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_cache"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "saved_models"

# Đảm bảo các thư mục luôn tồn tại
for d in [DATA_DIR, REPORTS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==================== DANH SÁCH MÃ CHỨNG KHOÁN ====================
# Chỉ số thị trường chung
MARKET_INDICES = ["VNINDEX", "VN30"]

# 30 cổ phiếu rổ VN30 (có thể tùy chỉnh hoặc mở rộng thêm)
VN30_TICKERS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

# ==================== THỜI GIAN DỮ LIỆU ====================
# Ngày bắt đầu lấy dữ liệu lịch sử (khuyến nghị >= 2-3 năm để mô hình học các chu kỳ)
DEFAULT_START_DATE = "2021-01-01"

def get_today_date() -> str:
    """Lấy ngày hôm nay theo giờ Việt Nam (UTC+7) – luôn chính xác dù server chạy lâu không restart."""
    return get_vietnam_now().strftime("%Y-%m-%d")

# Giữ lại TODAY_DATE cho backward compatibility với các file khác import nó
# nhưng các hàm mới nên dùng get_today_date() thay vì hằng số này.
TODAY_DATE = get_today_date()


# ==================== THÔNG SỐ CHỈ BÁO KỸ THUẬT ====================
INDICATOR_PARAMS = {
    "sma_periods": [10, 20, 50, 200],
    "ema_periods": [9, 21],
    "rsi_period": 14,
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "bollinger": {"period": 20, "std_dev": 2.0},
    "atr_period": 14,
    "stochastic": {"k_period": 14, "d_period": 3},
    "volume_sma": 20,
    "mfi_period": 14,
}

# ==================== THAM SỐ MACHINE LEARNING ====================
ML_CONFIG = {
    # Số phiên dự phóng tương lai (T+3 phù hợp chu kỳ giao dịch T+2.5 tại VN)
    "prediction_horizon": 3,
    # Ngưỡng lợi nhuận tối thiểu để coi là TĂNG (ví dụ > 1.0% sau T+3)
    "return_threshold": 0.010,
    # Tỷ lệ dữ liệu test và số split cho TimeSeriesSplit
    "cv_splits": 5,
    # Thuật toán ưu tiên: 'lightgbm' hoặc 'random_forest'
    "model_type": "lightgbm",
    "random_state": 42
}

# ==================== TRỌNG SỐ BỘ CHẤM ĐIỂM QUANT (0 - 100) ====================
QUANT_WEIGHTS = {
    "trend": 0.30,       # Điểm xu hướng (MA, EMA, Supertrend)
    "momentum": 0.25,    # Điểm động lượng (RSI, MACD, Stochastic)
    "money_flow": 0.25,  # Điểm dòng tiền (Volume vs MA20, OBV, MFI)
    "ml_prediction": 0.20 # Điểm xác suất tăng giá từ Machine Learning
}

# Ngưỡng phân loại khuyến nghị
SIGNAL_THRESHOLDS = {
    "STRONG_BUY": 75,   # Điểm >= 75: Mua mạnh
    "BUY": 60,          # Điểm 60 - 74: Mua
    "HOLD": 45,         # Điểm 45 - 59: Theo dõi / Nắm giữ
    "SELL": 30,         # Điểm 30 - 44: Bán
    "STRONG_SELL": 0    # Điểm < 30: Bán mạnh / Thoát vị thế
}

# ==================== CẤU HÌNH API & CACHE ====================
API_CONFIG = {
    "source": "VCI",
    "sleep_between_calls": 2.0,   # Giây nghỉ giữa các request (2s an toàn cho guest 20 req/phút, 0.5s nếu có API key 60 req/phút)
    "max_retries": 5,
    "retry_wait": 30
}

# ==================== CẤU HÌNH FASTAPI SERVER ====================
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "cors_origins": ["*"]       # Cho phép Vue 3 kết nối từ localhost hoặc IP mạng LAN
}

# ==================== CẤU HÌNH TỰ ĐỘNG CẬP NHẬT NGẦM (AUTO REFRESH) ====================
AUTO_REFRESH_CONFIG = {
    "enabled": True,             # Bật/tắt tự động làm mới ngầm
    "interval_seconds": 180,     # Thời gian tự động làm mới (180s = 3 phút; giảm áp lực rate-limit)
    "fetch_new_bars": True,      # Tự động tải nến phiên mới nhất nếu thị trường đang mở cửa
    "batch_size": 5              # Số mã cổ phiếu quét mỗi chu kỳ (30 mã / 5 = 6 chu kỳ để hoàn tất toàn bộ)
}

# ==================== CẤU HÌNH KHUNG GIỜ GIAO DỊCH CHỨNG KHOÁN (MARKET SCHEDULE) ====================
# Giảm tải hệ thống: Chỉ quét nến cổ phiếu trong giờ giao dịch (09:00 - 15:00, Thứ 2 - Thứ 6)
# Tin tức & Đánh giá rủi ro luôn cập nhật 24/7 thời gian thực
MARKET_SCHEDULE_CONFIG = {
    "trading_start_time": "09:00",   # Bắt đầu phiên sáng (ATO)
    "lunch_start_time": "11:30",     # Bắt đầu nghỉ trưa
    "lunch_end_time": "13:00",       # Bắt đầu phiên chiều
    "trading_end_time": "15:15",     # Kéo dài đến 15:15 để nạp trọn vẹn kết quả khớp lệnh chốt phiên ATC
    "enable_time_filter": True,      # Bật cơ chế lọc theo giờ (True: chỉ lấy giá cổ phiếu 9h-15h15)
    "news_always_realtime": True     # Tin tức & Rủi ro luôn cập nhật 24/7
}


def get_market_trading_status(now: datetime = None) -> dict:
    """
    Kiểm tra trạng thái thị trường chứng khoán Việt Nam (HOSE/VN30).
    Luôn quy đổi chuẩn xác về múi giờ Việt Nam (UTC+7 / Asia/Ho_Chi_Minh).
    Trả về: { is_trading: bool, session_name: str, can_fetch_stocks: bool, detail: str, current_time: str }
    """
    if now is None:
        now = get_vietnam_now()
    elif now.tzinfo is not None:
        # Nếu có múi giờ (ví dụ UTC từ Cloud server), chuyển đổi chính xác sang giờ Việt Nam
        now = now.astimezone(VIETNAM_TZ)
    else:
        # Naive datetime: giả định theo giờ Việt Nam
        now = now.replace(tzinfo=VIETNAM_TZ)

    if not MARKET_SCHEDULE_CONFIG.get("enable_time_filter", True):
        return {
            "is_trading": True,
            "session_name": "Chế độ mô phỏng liên tục",
            "can_fetch_stocks": True,
            "detail": "Bỏ qua bộ lọc giờ (Chạy 24/7)",
            "current_time": now.strftime("%H:%M:%S")
        }

    # Thứ 2 = 0, Chủ Nhật = 6
    weekday = now.weekday()
    if weekday in [5, 6]:
        return {
            "is_trading": False,
            "session_name": "Đóng cửa (Cuối tuần)",
            "can_fetch_stocks": False,
            "detail": "Thị trường đóng cửa thứ Bảy & Chủ Nhật. Sử dụng dữ liệu chốt phiên gần nhất.",
            "current_time": now.strftime("%H:%M:%S")
        }

    current_time_str = now.strftime("%H:%M")
    start_t = MARKET_SCHEDULE_CONFIG.get("trading_start_time", "09:00")
    lunch_start_t = MARKET_SCHEDULE_CONFIG.get("lunch_start_time", "11:30")
    lunch_end_t = MARKET_SCHEDULE_CONFIG.get("lunch_end_time", "13:00")
    end_t = MARKET_SCHEDULE_CONFIG.get("trading_end_time", "15:00")

    if start_t <= current_time_str < lunch_start_t:
        return {
            "is_trading": True,
            "session_name": "Phiên Sáng (Đang giao dịch)",
            "can_fetch_stocks": True,
            "detail": f"Khớp lệnh liên tục ({start_t} - {lunch_start_t})",
            "current_time": now.strftime("%H:%M:%S")
        }
    elif lunch_start_t <= current_time_str < lunch_end_t:
        return {
            "is_trading": False,
            "session_name": "Tạm nghỉ trưa",
            "can_fetch_stocks": False,
            "detail": f"Thị trường nghỉ trưa ({lunch_start_t} - {lunch_end_t}). Bảo lưu giá phiên sáng.",
            "current_time": now.strftime("%H:%M:%S")
        }
    elif lunch_end_t <= current_time_str <= end_t:
        return {
            "is_trading": True,
            "session_name": "Phiên Chiều (Đang giao dịch)",
            "can_fetch_stocks": True,
            "detail": f"Khớp lệnh liên tục & ATC ({lunch_end_t} - {end_t})",
            "current_time": now.strftime("%H:%M:%S")
        }
    else:
        return {
            "is_trading": False,
            "session_name": "Đã đóng phiên",
            "can_fetch_stocks": False,
            "detail": f"Ngoài giờ giao dịch ({end_t} - {start_t} hôm sau). Sử dụng dữ liệu chốt phiên.",
            "current_time": now.strftime("%H:%M:%S")
        }



