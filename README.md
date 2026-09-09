# VN30 Quantitative & AI Intelligence Platform (FastAPI + Vue 3)

Hệ thống Phân tích Định lượng (Quantitative Multi-Factor) kết hợp Học máy (Machine Learning - LightGBM) dành riêng cho thị trường chứng khoán Việt Nam (rổ VN30 và chỉ số VN-INDEX), được thiết kế theo kiến trúc **API-First (Headless Backend + Vue 3 SPA)** sẵn sàng tái sử dụng cho Web chuyên nghiệp, Mobile App (iOS/Android) và Bot cảnh báo.

---

## 🏛️ Kiến Trúc Hệ Thống (API-First Architecture)

```
                       ┌────────────────────────────────────────┐
                       │           CLIENT CONSUMERS             │
                       └────────────────────────────────────────┘
                                    │      │      │
            ┌───────────────────────┘      │      └──────────────────────┐
            ▼                              ▼                             ▼
    ┌───────────────┐              ┌───────────────┐             ┌───────────────┐
    │  Vue 3 Web    │              │  Mobile App   │             │ Telegram Bot  │
    │  (Vite + TV)  │              │ (Flutter/RN)  │             │  (Alert Bot)  │
    └───────────────┘              └───────────────┘             └───────────────┘
            │                              │                             │
            └───────────────────────┬──────┴─────────────────────────────┘
                                    │ RESTful JSON APIs
                                    ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                FASTAPI REST BACKEND (Port 8000)               │
       │  • /api/market/overview     • /api/vn30/leaderboard           │
       │  • /api/stocks/{code}/chart • /api/stocks/{code}/analysis     │
       └───────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                 QUANT & AI PREDICTIVE ENGINE                  │
       │  • LightGBM / GBDT Classifier (TimeSeriesSplit Validation)    │
       │  • 25+ Technical Indicators (RSI, MACD, BB, ATR, OBV, MFI)    │
       │  • Multi-Factor Quant Scoring (Trend, Momentum, Volume, AI)   │
       │  • Smart Local Caching & Incremental Update (vnstock API)     │
       └───────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Cấu Hình Hệ Thống (File `config.py`)

Bạn có thể dễ dàng tùy chỉnh mọi thông số tại [`config.py`](file:///D:/ProjectPy/config.py):
* **`AUTO_REFRESH_CONFIG`**:
  * `enabled`: `True` / `False` (Bật / tắt tự động làm mới ngầm).
  * `interval_seconds`: `60` (Thời gian tự động làm mới theo giây. Mặc định 60 giây = 1 phút).
  * `fetch_new_bars`: `True` (Tự động quét nến phiên mới nhất nếu sàn đang giao dịch).
* **`MARKET_SCHEDULE_CONFIG` (Cơ chế giảm tải theo giờ sàn HOSE & Tin tức 24/7)**:
  * `trading_start_time`: `"09:00"` (Mở phiên sáng ATO).
  * `lunch_start_time`: `"11:30"` - `lunch_end_time`: `"13:00"` (Nghỉ trưa, tạm dừng quét API).
  * `trading_end_time`: `"15:00"` (Đóng phiên chiều ATC).
  * `enable_time_filter`: `True` (Bật bộ lọc giờ: **Chỉ quét nến cổ phiếu từ 09:00 - 15:00 Thứ 2 - Thứ 6**. Ngoài giờ hoặc cuối tuần tự động chuyển sang chế độ tiết kiệm tài nguyên, giữ nguyên dữ liệu chốt phiên trong RAM/Cache, không gọi ra API ngoài để tránh rate-limit).
  * `news_always_realtime`: `True` (**Tin tức tài chính & Báo cáo đánh giá rủi ro luôn cập nhật 24/7** theo thời gian thực).
* **`VN30_TICKERS`**: Danh sách 30 cổ phiếu thuộc rổ chỉ số VN30 (có thể thêm/bớt mã tùy ý).
* **`QUANT_WEIGHTS`**: Tỷ trọng chấm điểm đa nhân tố: Xu hướng (30%), Động lượng (25%), Dòng tiền (25%), Dự báo AI (20%).
* **`SIGNAL_THRESHOLDS`**: Các ngưỡng phân loại khuyến nghị `MUA MẠNH`, `MUA`, `THEO DÕI`, `BÁN`.

```
D:\ProjectPy\
├── api_server.py             # Máy chủ FastAPI REST API (tích hợp phục vụ Vue 3)
├── config.py                 # Cấu hình danh sách mã, tham số kỹ thuật, trọng số, CORS
├── data_loader.py            # Tải dữ liệu vnstock, cache CSV cục bộ chống rate-limit
├── feature_engineering.py    # Tính toán 25+ chỉ báo định lượng, dòng tiền và nhãn ML T+3
├── ml_engine.py              # Huấn luyện mô hình LightGBM với TimeSeriesSplit & dự đoán
├── quant_analyzer.py         # Bộ chấm điểm đa nhân tố (0-100), tính Target & Stoploss
├── report_generator.py       # Xuất báo cáo Excel (.xlsx) và HTML Dashboard độc lập
├── main.py                   # Điểm chạy chế độ Terminal CLI truyền thống
├── data_cache/               # Dữ liệu nến lịch sử lưu dạng CSV (cập nhật gia tăng)
├── saved_models/             # Mô hình Machine Learning lưu trữ dạng .pkl
├── reports/                  # Chứa file Excel VN30_Quant_AI_Report.xlsx
└── frontend/                 # Ứng dụng Web Vue 3 chuyên nghiệp
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── dist/                 # Bản build tĩnh production của Vue 3
    └── src/
        ├── App.vue           # Layout điều phối chính
        ├── main.js
        ├── style.css         # TailwindCSS
        ├── api.js            # Client kết nối REST API FastAPI
        └── components/
            ├── Navbar.vue          # Header & chỉ số VN-INDEX thời gian thực
            ├── MarketOverview.vue  # 4 Thẻ tổng quan chỉ số & độ rộng thị trường
            ├── Leaderboard.vue     # Bảng 30 mã VN30 (Tìm kiếm, lọc Mua/Bán, sắp xếp)
            └── StockModal.vue      # Chi tiết phân tích + Biểu đồ nến TradingView
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Chạy Nhanh Nhất (Chỉ Cần 1 Lệnh Duy Nhất)

Backend FastAPI đã được cấu hình tự động tích hợp phục vụ bản build của Vue 3:

```powershell
python api_server.py
```

Mở trình duyệt truy cập:
* **Giao diện Web Vue 3:** [http://localhost:8000](http://localhost:8000)
* **Tài liệu API Swagger UI tương tác:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Cách 2: Chạy Chế Độ Phát Triển Frontend (Hot-Reload)

Nếu bạn muốn chỉnh sửa giao diện Vue 3 và xem thay đổi ngay lập tức:

1. **Terminal 1 (Chạy Backend API):**
   ```powershell
   python api_server.py
   ```

2. **Terminal 2 (Chạy Frontend Dev Server):**
   ```powershell
   cd frontend
   npm run dev
   ```
   Mở trình duyệt tại [http://localhost:5173](http://localhost:5173). Mọi thay đổi trong mã nguồn Vue sẽ tự động cập nhật tức thì (HMR).

3. **Khi cần đóng gói lại bản build:**
   ```powershell
   cd frontend
   npm run build
   ```

---

### Cách 3: Chạy Quét Bằng Dòng Lệnh & Xuất Excel (CLI Mode)

Nếu bạn chỉ muốn xuất nhanh file báo cáo Excel mà không cần mở web:

```powershell
# Chạy phân tích toàn bộ 30 mã VN30:
python main.py

# Chạy kiểm thử nhanh 5 mã:
python main.py --test-run

# Phân tích chuyên sâu 1 mã cụ thể (ví dụ FPT, HPG):
python main.py --ticker FPT
```
File Excel xuất ra tại: `D:\ProjectPy\reports\VN30_Quant_AI_Report.xlsx`.

---

## 🔌 Danh Sách REST Endpoints (Dành cho Mobile App & Bot)

Khi phát triển Mobile App (Flutter / React Native) hoặc Bot Telegram, bạn chỉ cần gọi các Endpoint chuẩn sau:

| Phương thức | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/api/market/overview` | Lấy điểm số VN-INDEX, % thay đổi, trạng thái thị trường và phân bổ số lượng Mua/Chờ/Bán. |
| `GET` | `/api/vn30/leaderboard` | Lấy bảng xếp hạng 30 mã. Hỗ trợ query: `?signal=BUY`, `?search=FPT`, `?sort_by=total_score`. |
| `GET` | `/api/stocks/{ticker}/analysis` | Lấy phân tích chi tiết 1 mã: Điểm xu hướng, động lượng, dòng tiền, xác suất AI, Vùng mua, Target, Stoploss. |
| `GET` | `/api/stocks/{ticker}/candles` | Lấy chuỗi nến lịch sử `[ { time, open, high, low, close, volume } ]` để vẽ biểu đồ nến TradingView. |
| `GET` | `/api/news/feed` | Dòng chảy tin tức tài chính trong nước & quốc tế tác động tới Cổ phiếu, Vàng, BTC, Địa chính trị. |
| `GET` | `/api/news/risk-assessment` | Báo cáo phân tích và lượng hóa chỉ số rủi ro tin tức vĩ mô (Asset Impact Matrix & Hedging Strategy). |
| `POST`| `/api/market/refresh` | Kích hoạt tải dữ liệu mới nhất từ sàn trong background. |


---

## 📈 Cách Đọc Tín Hiệu & Quản Trị Rủi Ro

* **MUA MẠNH (Strong Buy):** Điểm Quant >= 75 & Xác suất AI T+3 >= 52% & Xu hướng kỹ thuật đồng thuận.
* **MUA (Buy):** Điểm Quant 60 - 74 & Xác suất AI T+3 >= 45%.
* **THEO DÕI (Chờ AI đồng thuận):** Điểm kỹ thuật cao nhưng mô hình AI dự báo thị trường chung đang có rủi ro ngắn hạn -> Khuyên nhà đầu tư kiên nhẫn quan sát, chờ điểm bùng nổ.
* **QUAN SÁT / NẮM GIỮ (Hold):** Điểm 45 - 59, cổ phiếu đang trong vùng tích lũy/giằng co.
* **BÁN / HẠ TỶ TRỌNG (Sell):** Điểm < 45 hoặc AI cảnh báo xác suất giảm cao.
* **BÁN MẠNH (Strong Sell):** Điểm < 30 hoặc gãy các đường hỗ trợ quan trọng.
* **Tỷ Lệ Risk/Reward:** Hệ thống luôn tự động đặt mức **Mục Tiêu (Target)** và **Cắt Lỗ (Stoploss)** theo độ biến động thực tế ATR, đảm bảo tỷ lệ Lời/Lỗ tối thiểu từ 1:1.5 trở lên.
