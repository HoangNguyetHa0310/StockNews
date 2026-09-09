# -*- coding: utf-8 -*-
"""
Module Xuất Báo Cáo Chuyên Nghiệp
1. Xuất file Excel (.xlsx) đa tầng với định dạng tô màu điều kiện (Conditional Formatting).
2. Xuất Interactive HTML Dashboard hiện đại (Dark Theme, TradingView/Bloomberg style)
   tích hợp biểu đồ, tìm kiếm, lọc và bảng xếp hạng tương tác mở trực tiếp trên trình duyệt.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from config import REPORTS_DIR


class ReportGenerator:
    def __init__(self, reports_dir: Path = REPORTS_DIR):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def export_excel(self, market_summary: dict, stock_analyses: list[dict], filename: str = "VN30_Quant_AI_Report.xlsx") -> Path:
        """
        Xuất báo cáo Excel chuyên nghiệp nhiều sheet với định dạng màu sắc đẹp mắt.
        """
        file_path = self.reports_dir / filename
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        # Style colors
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        
        buy_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        buy_font = Font(name="Calibri", size=11, bold=True, color="166534")
        
        strong_buy_fill = PatternFill(start_color="86EFAC", end_color="86EFAC", fill_type="solid")
        strong_buy_font = Font(name="Calibri", size=11, bold=True, color="14532D")

        sell_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        sell_font = Font(name="Calibri", size=11, bold=True, color="991B1B")

        hold_fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
        hold_font = Font(name="Calibri", size=11, bold=True, color="854D0E")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # ---------------- SHEET 1: TỔNG QUAN THỊ TRƯỜNG ----------------
        ws1 = wb.create_sheet(title="Tong_Quan_Thi_Truong")
        ws1.views.sheetView[0].showGridLines = True
        
        # Tiêu đề
        ws1.merge_cells("A1:F1")
        ws1["A1"] = "BÁO CÁO PHÂN TÍCH ĐỊNH LƯỢNG & DỰ ĐOÁN THỊ TRƯỜNG VN30"
        ws1["A1"].font = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
        ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws1.row_dimensions[1].height = 35

        ws1["A2"] = f"Thời gian thực hiện: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws1["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

        market_rows = [
            ("Chỉ số VN-INDEX", market_summary.get("vnindex_close", "N/A")),
            ("Biến động phiên gần nhất", f"{market_summary.get('vnindex_change_pct', 0):+.2f}%"),
            ("Khối lượng giao dịch VN-INDEX", f"{market_summary.get('vnindex_volume', 0):,}".replace(",", ".")),
            ("Trạng thái thị trường", market_summary.get("market_sentiment", "N/A")),
            ("Tổng số mã VN30 phân tích", market_summary.get("total_stocks_analyzed", 0)),
            ("Số mã cho tín hiệu MUA / MUA MẠNH", f"{market_summary.get('buy_count', 0)} ({market_summary.get('pct_buy', 0)}%)"),
            ("Số mã trạng thái THEO DÕI", market_summary.get("hold_count", 0)),
            ("Số mã cho tín hiệu BÁN / HẠ TỶ TRỌNG", market_summary.get("sell_count", 0)),
        ]

        ws1.cell(row=4, column=1, value="CHỈ SỐ & ĐỘ RỘNG THỊ TRƯỜNG").font = Font(name="Calibri", size=12, bold=True, color="1E293B")
        for r_idx, (k, v) in enumerate(market_rows, start=5):
            c1 = ws1.cell(row=r_idx, column=1, value=k)
            c2 = ws1.cell(row=r_idx, column=2, value=v)
            c1.font = Font(name="Calibri", size=11, bold=True, color="334155")
            c2.font = Font(name="Calibri", size=11, color="0F172A")
            c1.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
            c1.border = thin_border
            c2.border = thin_border

        sorted_stocks = sorted(stock_analyses, key=lambda x: x.get("total_score", 0), reverse=True)
        top_picks = sorted_stocks[:5]

        ws1.cell(row=15, column=1, value="TOP CỔ PHIẾU TIỀM NĂNG NHẤT (ĐIỂM ĐỊNH LƯỢNG & AI CAO NHẤT)").font = Font(name="Calibri", size=12, bold=True, color="15803D")
        top_headers = ["Mã CK", "Giá", "Thay đổi", "Điểm Quant", "Xác suất tăng (AI)", "Khuyến nghị", "Mục tiêu 1", "Dừng lỗ"]
        for c_idx, h in enumerate(top_headers, start=1):
            cell = ws1.cell(row=16, column=c_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        for r_idx, s in enumerate(top_picks, start=17):
            ws1.cell(row=r_idx, column=1, value=s.get("ticker")).alignment = Alignment(horizontal="center")
            ws1.cell(row=r_idx, column=2, value=s.get("close")).number_format = "#,##0.00"
            ws1.cell(row=r_idx, column=3, value=f"{s.get('change_pct', 0):+.2f}%").alignment = Alignment(horizontal="center")
            ws1.cell(row=r_idx, column=4, value=s.get("total_score")).alignment = Alignment(horizontal="center")
            ws1.cell(row=r_idx, column=5, value=f"{s.get('ml_prob_up', 0):.1f}%").alignment = Alignment(horizontal="center")
            
            sig_cell = ws1.cell(row=r_idx, column=6, value=s.get("signal"))
            sig_cell.alignment = Alignment(horizontal="center")
            sig = s.get("signal", "")
            if "MUA MẠNH" in sig:
                sig_cell.fill = strong_buy_fill
                sig_cell.font = strong_buy_font
            elif "MUA" in sig:
                sig_cell.fill = buy_fill
                sig_cell.font = buy_font
            elif "BÁN" in sig:
                sig_cell.fill = sell_fill
                sig_cell.font = sell_font
            else:
                sig_cell.fill = hold_fill
                sig_cell.font = hold_font

            ws1.cell(row=r_idx, column=7, value=s.get("target_1")).number_format = "#,##0.00"
            ws1.cell(row=r_idx, column=8, value=s.get("stoploss")).number_format = "#,##0.00"

            for c_i in range(1, 9):
                ws1.cell(row=r_idx, column=c_i).border = thin_border

        # ---------------- SHEET 2: BẢNG XẾP HẠNG VN30 ----------------
        ws2 = wb.create_sheet(title="Bang_Xep_Hang_VN30")
        ws2.views.sheetView[0].showGridLines = True

        headers_s2 = [
            "Hạng", "Mã CK", "Giá Đóng Cửa", "Thay Đổi %", "Khối Lượng", "Vol/MA20",
            "RSI (14)", "MACD", "Điểm Xu Hướng", "Điểm Động Lượng", "Điểm Dòng Tiền",
            "Xác Suất Tăng AI", "ĐIỂM QUANT TỔNG", "KHUYẾN NGHỊ", "Vùng Mua Gợi Ý",
            "Giá Dừng Lỗ", "Mục Tiêu 1", "Mục Tiêu 2", "Tỷ Lệ R:R"
        ]

        for col_num, h_text in enumerate(headers_s2, start=1):
            cell = ws2.cell(row=1, column=col_num, value=h_text)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws2.row_dimensions[1].height = 28

        for rank, s in enumerate(sorted_stocks, start=1):
            row_idx = rank + 1
            ws2.cell(row=row_idx, column=1, value=rank).alignment = Alignment(horizontal="center")
            ws2.cell(row=row_idx, column=2, value=s.get("ticker")).font = Font(bold=True)
            ws2.cell(row=row_idx, column=2).alignment = Alignment(horizontal="center")
            ws2.cell(row=row_idx, column=3, value=s.get("close")).number_format = "#,##0.00"
            
            chg_cell = ws2.cell(row=row_idx, column=4, value=s.get("change_pct") / 100.0)
            chg_cell.number_format = "+0.00%;-0.00%;0.00%"
            chg_cell.alignment = Alignment(horizontal="right")
            if s.get("change_pct", 0) > 0:
                chg_cell.font = Font(color="16A34A", bold=True)
            elif s.get("change_pct", 0) < 0:
                chg_cell.font = Font(color="DC2626", bold=True)

            ws2.cell(row=row_idx, column=5, value=s.get("volume")).number_format = "#,##0"
            ws2.cell(row=row_idx, column=6, value=s.get("vol_vs_ma20")).number_format = "0.00"
            ws2.cell(row=row_idx, column=7, value=s.get("rsi")).number_format = "0.0"
            ws2.cell(row=row_idx, column=8, value=s.get("macd_status")).alignment = Alignment(horizontal="center")
            
            ws2.cell(row=row_idx, column=9, value=s.get("trend_score")).number_format = "0.0"
            ws2.cell(row=row_idx, column=10, value=s.get("momentum_score")).number_format = "0.0"
            ws2.cell(row=row_idx, column=11, value=s.get("flow_score")).number_format = "0.0"
            
            prob_cell = ws2.cell(row=row_idx, column=12, value=s.get("ml_prob_up") / 100.0)
            prob_cell.number_format = "0.0%"
            prob_cell.alignment = Alignment(horizontal="center")

            total_cell = ws2.cell(row=row_idx, column=13, value=s.get("total_score"))
            total_cell.font = Font(bold=True)
            total_cell.alignment = Alignment(horizontal="center")
            total_cell.number_format = "0.0"

            sig_cell = ws2.cell(row=row_idx, column=14, value=s.get("signal"))
            sig_cell.alignment = Alignment(horizontal="center")
            sig = s.get("signal", "")
            if "MUA MẠNH" in sig:
                sig_cell.fill = strong_buy_fill
                sig_cell.font = strong_buy_font
            elif "MUA" in sig:
                sig_cell.fill = buy_fill
                sig_cell.font = buy_font
            elif "BÁN" in sig:
                sig_cell.fill = sell_fill
                sig_cell.font = sell_font
            else:
                sig_cell.fill = hold_fill
                sig_cell.font = hold_font

            ws2.cell(row=row_idx, column=15, value=s.get("entry_range")).alignment = Alignment(horizontal="center")
            ws2.cell(row=row_idx, column=16, value=s.get("stoploss")).number_format = "#,##0.00"
            ws2.cell(row=row_idx, column=17, value=s.get("target_1")).number_format = "#,##0.00"
            ws2.cell(row=row_idx, column=18, value=s.get("target_2")).number_format = "#,##0.00"
            ws2.cell(row=row_idx, column=19, value=s.get("risk_reward_ratio")).number_format = "0.00"

            for c_i in range(1, 20):
                ws2.cell(row=row_idx, column=c_i).border = thin_border

        for ws in [ws1, ws2]:
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

        wb.save(file_path)
        print(f"[Báo Cáo] Đã xuất thành công file Excel: {file_path}")
        return file_path

    def export_html_dashboard(self, market_summary: dict, stock_analyses: list[dict], filename: str = "dashboard.html") -> Path:
        """
        Xuất Dashboard tương tác dạng HTML hiện đại (Dark Theme),
        tích hợp tìm kiếm, lọc theo khuyến nghị, bảng xếp hạng và biểu đồ trực quan.
        """
        file_path = self.reports_dir / filename
        sorted_stocks = sorted(stock_analyses, key=lambda x: x.get("total_score", 0), reverse=True)
        stocks_json = json.dumps(sorted_stocks, ensure_ascii=False)
        market_json = json.dumps(market_summary, ensure_ascii=False)
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Sử dụng template text tĩnh với placeholder để tránh xung đột cú pháp giữa Python f-string và JavaScript
        raw_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VN30 Quant & AI Intelligence Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        slate: {
                            850: '#151f32',
                            950: '#0b1120',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .font-mono {
            font-family: 'JetBrains Mono', monospace;
        }
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased selection:bg-cyan-500 selection:text-white">

    <!-- Header / Navbar -->
    <nav class="border-b border-slate-800/80 bg-slate-900/70 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <i data-lucide="trending-up" class="w-6 h-6 text-slate-950 stroke-[2.5]"></i>
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                        VN30 QUANT & AI PREDICTOR
                        <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">PRO V2.5</span>
                    </h1>
                    <p class="text-xs text-slate-400">Hệ thống Phân tích Định lượng & Học máy Dự báo Xu hướng T+3</p>
                </div>
            </div>

            <!-- Market Pill -->
            <div class="flex items-center gap-4">
                <div class="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
                    <span class="text-slate-400">VN-INDEX:</span>
                    <span class="font-mono font-bold text-white" id="nav-vn-close">--</span>
                    <span class="font-mono font-bold" id="nav-vn-change">--</span>
                </div>
                <div class="text-xs text-slate-400 font-mono hidden md:block">
                    Cập nhật: <span class="text-slate-200">__DATE_STR__</span>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- Market Overview Section -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Card 1: VN-INDEX -->
            <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-xl relative overflow-hidden">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Chỉ Số VN-INDEX</p>
                        <h3 class="text-2xl font-bold font-mono text-white mt-1" id="m-close">--</h3>
                        <p class="text-xs font-mono font-semibold mt-1" id="m-change">--</p>
                    </div>
                    <div class="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        <i data-lucide="bar-chart-2" class="w-5 h-5"></i>
                    </div>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                    <span>Thanh khoản phiên:</span>
                    <span class="font-mono text-slate-200" id="m-vol">--</span>
                </div>
            </div>

            <!-- Card 2: Market Sentiment -->
            <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-xl relative overflow-hidden">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Trạng Thái Thị Trường</p>
                        <h3 class="text-base font-bold text-white mt-1.5" id="m-sentiment">--</h3>
                        <p class="text-xs text-slate-400 mt-1">Dựa trên phân tích xu hướng</p>
                    </div>
                    <div class="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <i data-lucide="compass" class="w-5 h-5"></i>
                    </div>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                    <span>Độ rộng rổ VN30:</span>
                    <span class="font-mono font-bold text-emerald-400" id="m-pct-buy">--% Mua</span>
                </div>
            </div>

            <!-- Card 3: Tín hiệu Mua / Bán -->
            <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-xl relative overflow-hidden">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Phân Bổ Khuyến Nghị</p>
                        <div class="flex items-center gap-3 mt-2">
                            <span class="text-emerald-400 font-bold font-mono text-xl" id="m-buy-count">0 Mua</span>
                            <span class="text-slate-600">|</span>
                            <span class="text-amber-400 font-bold font-mono text-xl" id="m-hold-count">0 Chờ</span>
                            <span class="text-slate-600">|</span>
                            <span class="text-rose-400 font-bold font-mono text-xl" id="m-sell-count">0 Bán</span>
                        </div>
                    </div>
                    <div class="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        <i data-lucide="pie-chart" class="w-5 h-5"></i>
                    </div>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-800/60">
                    <!-- Progress Bar -->
                    <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden flex" id="breadth-bar">
                        <div class="bg-emerald-500 h-full" style="width: 50%"></div>
                        <div class="bg-amber-500 h-full" style="width: 30%"></div>
                        <div class="bg-rose-500 h-full" style="width: 20%"></div>
                    </div>
                </div>
            </div>

            <!-- Card 4: Top Pick AI -->
            <div class="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/40 to-slate-900/80 border border-cyan-500/30 shadow-xl relative overflow-hidden">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-1">
                            <i data-lucide="zap" class="w-3.5 h-3.5"></i> Cổ Phiếu Dẫn Đầu AI
                        </p>
                        <h3 class="text-2xl font-bold font-mono text-white mt-1" id="top-ticker">--</h3>
                        <p class="text-xs text-slate-300 font-mono mt-0.5" id="top-detail">--</p>
                    </div>
                    <div class="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 font-mono font-bold text-xs border border-emerald-500/40" id="top-score">
                        -- ĐIỂM
                    </div>
                </div>
                <div class="mt-4 pt-3 border-t border-cyan-500/20 flex items-center justify-between text-xs text-slate-400">
                    <span>Xác suất tăng T+3:</span>
                    <span class="font-mono font-bold text-cyan-300" id="top-prob">--%</span>
                </div>
            </div>
        </section>

        <!-- Filter & Search Toolbar -->
        <section class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80">
            <!-- Signal Filter Tabs -->
            <div class="flex flex-wrap gap-2" id="filter-tabs">
                <button onclick="setFilter('ALL')" class="filter-btn active px-3.5 py-1.5 rounded-xl text-xs font-bold transition bg-cyan-500 text-slate-950" data-filter="ALL">
                    Tất cả (30)
                </button>
                <button onclick="setFilter('BUY')" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-semibold transition bg-slate-800 text-slate-300 hover:bg-slate-700" data-filter="BUY">
                    Tín hiệu MUA / MUA MẠNH
                </button>
                <button onclick="setFilter('HOLD')" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-semibold transition bg-slate-800 text-slate-300 hover:bg-slate-700" data-filter="HOLD">
                    Nắm giữ / Theo dõi
                </button>
                <button onclick="setFilter('SELL')" class="filter-btn px-3.5 py-1.5 rounded-xl text-xs font-semibold transition bg-slate-800 text-slate-300 hover:bg-slate-700" data-filter="SELL">
                    Cảnh báo BÁN
                </button>
            </div>

            <!-- Search Input -->
            <div class="relative w-full md:w-72">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2"></i>
                <input type="text" id="search-input" onkeyup="filterStocks()" placeholder="Tìm theo mã (ví dụ: FPT, HPG)..." 
                       class="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition font-mono">
            </div>
        </section>

        <!-- Stock Leaderboard Table -->
        <section class="bg-slate-900/80 rounded-2xl border border-slate-800/80 shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-slate-800/80 flex justify-between items-center">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        BẢNG XẾP HẠNG TÍN HIỆU 30 CỔ PHIẾU VN30
                    </h2>
                    <p class="text-xs text-slate-400 mt-0.5">Sắp xếp theo Điểm Định Lượng & Xác suất Tăng Machine Learning</p>
                </div>
                <div class="text-xs font-mono text-slate-400">
                    Hiển thị: <span id="visible-count" class="text-white font-bold">30</span> mã
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-950/80 text-slate-400 font-semibold border-b border-slate-800 text-[11px] uppercase tracking-wider">
                        <tr>
                            <th class="py-3.5 px-4 text-center">Hạng</th>
                            <th class="py-3.5 px-4">Mã CK</th>
                            <th class="py-3.5 px-4 text-right">Giá Đóng Cửa</th>
                            <th class="py-3.5 px-4 text-right">Biến Động</th>
                            <th class="py-3.5 px-4 text-center">RSI (14)</th>
                            <th class="py-3.5 px-4 text-center">Vol/MA20</th>
                            <th class="py-3.5 px-4 text-center">Xác Suất Tăng AI (T+3)</th>
                            <th class="py-3.5 px-4 text-center">Điểm Quant (100)</th>
                            <th class="py-3.5 px-4 text-center">Khuyến Nghị</th>
                            <th class="py-3.5 px-4 text-center">Vùng Mua Gợi Ý</th>
                            <th class="py-3.5 px-4 text-right">Dừng Lỗ</th>
                            <th class="py-3.5 px-4 text-right">Mục Tiêu 1</th>
                        </tr>
                    </thead>
                    <tbody id="stock-tbody" class="divide-y divide-slate-800/60 font-mono">
                        <!-- Render qua JS -->
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Methodological Explanation -->
        <section class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
            <div class="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/60 text-xs text-slate-400 space-y-2">
                <div class="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                    <i data-lucide="cpu" class="w-4 h-4 text-cyan-400"></i> Thuật Toán Machine Learning
                </div>
                <p>Mô hình LightGBM / GBDT phân loại chuỗi thời gian (TimeSeriesSplit) dự đoán xác suất giá cổ phiếu tăng trên 1.0% trong T+3 phiên, tận dụng mối tương quan phi tuyến của 25 chỉ báo kỹ thuật.</p>
            </div>
            <div class="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/60 text-xs text-slate-400 space-y-2">
                <div class="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                    <i data-lucide="sliders" class="w-4 h-4 text-emerald-400"></i> Hệ Thống Điểm Đa Nhân Tố
                </div>
                <p>Điểm Quant (0-100) tổng hợp 4 trụ cột: Xu hướng (30%), Động lượng RSI/MACD (25%), Dòng tiền OBV/MFI (25%) và Dự phóng AI (20%) giúp triệt tiêu tín hiệu giả.</p>
            </div>
            <div class="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/60 text-xs text-slate-400 space-y-2">
                <div class="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                    <i data-lucide="shield-alert" class="w-4 h-4 text-amber-400"></i> Quản Trị Rủi Ro Chặt Chẽ
                </div>
                <p>Mỗi mã đều được tự động tính toán mức Dừng lỗ (Stoploss) và Mục tiêu (Target) dựa trên độ biến động thực tế ATR, luôn đảm bảo tỷ lệ Risk/Reward tối thiểu 1:1.5.</p>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500 font-mono mt-12">
        <p>Hệ thống hỗ trợ ra quyết định đầu tư định lượng VN30 &bull; Dữ liệu nguồn từ Vnstock API</p>
        <p class="mt-1 text-[11px] text-slate-600">Lưu ý: Kết quả mang tính chất tham khảo phân tích kỹ thuật & toán học xác suất, không phải lời mời chào đầu tư ủy thác.</p>
    </footer>

    <!-- Logic Script -->
    <script>
        const STOCKS_DATA = __STOCKS_JSON__;
        const MARKET_DATA = __MARKET_JSON__;
        let currentFilter = 'ALL';

        function initDashboard() {
            lucide.createIcons();

            if (MARKET_DATA) {
                const close = MARKET_DATA.vnindex_close ? MARKET_DATA.vnindex_close.toLocaleString('vi-VN', {minimumFractionDigits: 2}) : '--';
                const chg = MARKET_DATA.vnindex_change_pct ? (MARKET_DATA.vnindex_change_pct > 0 ? '+' : '') + MARKET_DATA.vnindex_change_pct.toFixed(2) + '%' : '--';
                const chgClass = (MARKET_DATA.vnindex_change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400';

                document.getElementById('nav-vn-close').innerText = close;
                document.getElementById('nav-vn-change').innerText = chg;
                document.getElementById('nav-vn-change').className = 'font-mono font-bold ' + chgClass;

                document.getElementById('m-close').innerText = close;
                document.getElementById('m-change').innerText = chg;
                document.getElementById('m-change').className = 'text-xs font-mono font-semibold mt-1 ' + chgClass;
                
                document.getElementById('m-vol').innerText = MARKET_DATA.vnindex_volume ? MARKET_DATA.vnindex_volume.toLocaleString('vi-VN') : '--';
                document.getElementById('m-sentiment').innerText = MARKET_DATA.market_sentiment || '--';
                document.getElementById('m-pct-buy').innerText = (MARKET_DATA.pct_buy || 0) + '% Mua';

                document.getElementById('m-buy-count').innerText = (MARKET_DATA.buy_count || 0) + ' Mua';
                document.getElementById('m-hold-count').innerText = (MARKET_DATA.hold_count || 0) + ' Chờ';
                document.getElementById('m-sell-count').innerText = (MARKET_DATA.sell_count || 0) + ' Bán';

                const total = MARKET_DATA.total_stocks_analyzed || 30;
                const buyW = ((MARKET_DATA.buy_count || 0) / total * 100);
                const holdW = ((MARKET_DATA.hold_count || 0) / total * 100);
                const sellW = ((MARKET_DATA.sell_count || 0) / total * 100);
                document.getElementById('breadth-bar').innerHTML = `
                    <div class="bg-emerald-500 h-full" style="width: ${buyW}%"></div>
                    <div class="bg-amber-500 h-full" style="width: ${holdW}%"></div>
                    <div class="bg-rose-500 h-full" style="width: ${sellW}%"></div>
                `;
            }

            if (STOCKS_DATA && STOCKS_DATA.length > 0) {
                const top = STOCKS_DATA[0];
                document.getElementById('top-ticker').innerText = top.ticker;
                document.getElementById('top-detail').innerText = `Giá: ${top.close.toLocaleString('vi-VN')} (${top.change_pct > 0 ? '+' : ''}${top.change_pct}%)`;
                document.getElementById('top-score').innerText = `${top.total_score} ĐIỂM`;
                document.getElementById('top-prob').innerText = `${top.ml_prob_up}%`;
            }

            renderTable(STOCKS_DATA);
        }

        function getSignalBadge(signal) {
            if (signal.includes('MUA MẠNH')) {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">MUA MẠNH</span>`;
            } else if (signal.includes('MUA')) {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">MUA</span>`;
            } else if (signal.includes('BÁN MẠNH')) {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40">BÁN MẠNH</span>`;
            } else if (signal.includes('BÁN')) {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-300 border border-rose-500/20">BÁN</span>`;
            } else if (signal.includes('Chờ AI')) {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">THEO DÕI (CHỜ AI)</span>`;
            } else {
                return `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20">QUAN SÁT</span>`;
            }
        }

        function renderTable(stocks) {
            const tbody = document.getElementById('stock-tbody');
            tbody.innerHTML = '';
            document.getElementById('visible-count').innerText = stocks.length;

            stocks.forEach((s, idx) => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-800/40 transition duration-150";

                const chgColor = s.change_pct > 0 ? 'text-emerald-400' : (s.change_pct < 0 ? 'text-rose-400' : 'text-slate-300');
                const chgSign = s.change_pct > 0 ? '+' : '';

                const probWidth = Math.min(Math.max(s.ml_prob_up, 10), 100);
                const probColor = s.ml_prob_up >= 60 ? 'bg-emerald-500' : (s.ml_prob_up <= 40 ? 'bg-rose-500' : 'bg-cyan-500');

                let scoreBadge = "bg-slate-800 text-slate-300";
                if (s.total_score >= 75) scoreBadge = "bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40";
                else if (s.total_score >= 60) scoreBadge = "bg-emerald-500/10 text-emerald-300 font-bold";
                else if (s.total_score <= 35) scoreBadge = "bg-rose-500/20 text-rose-400 font-bold border border-rose-500/40";
                else if (s.total_score <= 45) scoreBadge = "bg-rose-500/10 text-rose-300 font-semibold";

                tr.innerHTML = `
                    <td class="py-3 px-4 text-center text-slate-500 text-[11px]">${idx + 1}</td>
                    <td class="py-3 px-4 font-bold text-white hover:text-cyan-400 transition cursor-pointer">${s.ticker}</td>
                    <td class="py-3 px-4 text-right font-semibold text-slate-200">${s.close.toLocaleString('vi-VN', {minimumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 text-right font-semibold ${chgColor}">${chgSign}${s.change_pct.toFixed(2)}%</td>
                    <td class="py-3 px-4 text-center text-slate-300">${s.rsi ? s.rsi.toFixed(1) : '--'}</td>
                    <td class="py-3 px-4 text-center ${s.vol_vs_ma20 >= 1.3 ? 'text-amber-400 font-bold' : 'text-slate-300'}">${s.vol_vs_ma20 ? s.vol_vs_ma20.toFixed(2) : '--'}x</td>
                    <td class="py-3 px-4">
                        <div class="flex items-center justify-center gap-2">
                            <span class="w-10 text-right font-semibold ${s.ml_prob_up >= 55 ? 'text-emerald-400' : 'text-slate-300'}">${s.ml_prob_up}%</span>
                            <div class="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div class="${probColor} h-full" style="width: ${probWidth}%"></div>
                            </div>
                        </div>
                    </td>
                    <td class="py-3 px-4 text-center">
                        <span class="px-2 py-0.5 rounded-lg text-xs ${scoreBadge}">${s.total_score}</span>
                    </td>
                    <td class="py-3 px-4 text-center">${getSignalBadge(s.signal)}</td>
                    <td class="py-3 px-4 text-center text-slate-400 text-[11px]">${s.entry_range || '--'}</td>
                    <td class="py-3 px-4 text-right text-rose-400 font-semibold">${s.stoploss ? s.stoploss.toLocaleString('vi-VN', {minimumFractionDigits: 2}) : '--'}</td>
                    <td class="py-3 px-4 text-right text-emerald-400 font-semibold">${s.target_1 ? s.target_1.toLocaleString('vi-VN', {minimumFractionDigits: 2}) : '--'}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                if (btn.dataset.filter === filter) {
                    btn.className = "filter-btn active px-3.5 py-1.5 rounded-xl text-xs font-bold transition bg-cyan-500 text-slate-950";
                } else {
                    btn.className = "filter-btn px-3.5 py-1.5 rounded-xl text-xs font-semibold transition bg-slate-800 text-slate-300 hover:bg-slate-700";
                }
            });
            filterStocks();
        }

        function filterStocks() {
            const searchVal = document.getElementById('search-input').value.trim().toUpperCase();
            let filtered = STOCKS_DATA.filter(s => {
                const matchesSearch = s.ticker.includes(searchVal);
                if (!matchesSearch) return false;

                if (currentFilter === 'BUY') {
                    return s.signal.includes('MUA');
                } else if (currentFilter === 'HOLD') {
                    return s.signal.includes('QUAN SÁT') || s.signal.includes('NẮM GIỮ') || s.signal.includes('THEO DÕI');
                } else if (currentFilter === 'SELL') {
                    return s.signal.includes('BÁN');
                }
                return true;
            });

            renderTable(filtered);
        }

        window.onload = initDashboard;
    </script>
</body>
</html>
"""
        final_html = (
            raw_html
            .replace("__STOCKS_JSON__", stocks_json)
            .replace("__MARKET_JSON__", market_json)
            .replace("__DATE_STR__", date_str)
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"[Báo Cáo] Đã xuất thành công HTML Dashboard: {file_path}")
        return file_path
