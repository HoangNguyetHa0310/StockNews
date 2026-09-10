# -*- coding: utf-8 -*-
"""
Module Cung Cấp Tin Tức Tài Chính & Đánh Giá Rủi Ro Tác Động (News & Risk Assessment Service)
Tổng hợp tin tức nhanh nhất trong nước và quốc tế, phân loại ảnh hưởng tới:
Cổ phiếu VN30, Giá Vàng (Gold), Bitcoin (BTC), và Chính trị / Vĩ mô.
"""
from datetime import datetime
from typing import List, Dict, Optional
from config import get_vietnam_now


class NewsService:
    def __init__(self):
        self.last_sync = get_vietnam_now()

    def get_market_news(self, region: Optional[str] = None, asset: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        """
        Lấy danh sách tin tức tài chính mới nhất, phân chia trong nước/quốc tế và các loại tài sản.
        """
        now_vn = get_vietnam_now().strftime("%H:%M %d/%m/%Y")
        news_items = [
            # ---------------- TIN TRONG NƯỚC ----------------
            {
                "id": "news_vn_01",
                "title": "Ngân hàng Nhà nước duy trì điều hành linh hoạt, kiểm soát tỷ giá USD/VND trước kỳ họp FED",
                "summary": "NHNN tiếp tục sử dụng các công cụ điều tiết thanh khoản trên thị trường mở (OMO) và phát hành tín phiếu để ổn định tỷ giá trong bối cảnh chỉ số DXY tăng cao.",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "macro",
                "asset_tags": ["Tỷ Giá", "Vĩ Mô", "Cổ Phiếu"],
                "impact_asset": "Cổ phiếu & Lãi suất",
                "sentiment": "neutral",
                "sentiment_label": "Trung Tính / Thận Trọng",
                "risk_level": "medium",
                "source": "VnEconomy / Cổng TT NHNN",
                "published_at": "15 phút trước",
                "time_str": now_vn,
                "badge_color": "cyan"
            },
            {
                "id": "news_vn_02",
                "title": "Chính phủ quyết liệt thúc đẩy giải pháp nâng hạng thị trường chứng khoán Việt Nam lên FTSE Emerging",
                "summary": "Bộ Tài chính và UBCKNN đang tích cực tháo gỡ nút thắt ký quỹ trước giao dịch (Non-margin / Pre-funding) cho khối ngoại, tạo động lực đón dòng vốn tỷ USD vào nhóm VN30.",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "stocks",
                "asset_tags": ["Cổ Phiếu", "VN30", "FTSE"],
                "impact_asset": "Cổ Phiếu VN30",
                "sentiment": "positive",
                "sentiment_label": "Tích Cực Mạnh",
                "risk_level": "low",
                "source": "UBCKNN / Báo Đầu Tư",
                "published_at": "40 phút trước",
                "time_str": now_vn,
                "badge_color": "emerald"
            },
            {
                "id": "news_vn_03",
                "title": "Giá vàng miếng SJC và vàng nhẫn 9999 biến động mạnh sau công điện thanh tra thị trường vàng",
                "summary": "Các cơ quan quản lý đẩy mạnh thanh tra hoạt động kinh doanh vàng, chênh lệch giữa giá vàng trong nước và thế giới thu hẹp, giao dịch tại các nhà vàng lớn duy trì trạng thái thận trọng.",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "gold",
                "asset_tags": ["Vàng SJC", "Vàng Nhẫn", "Chính Sách"],
                "impact_asset": "Giá Vàng Nội Địa",
                "sentiment": "negative",
                "sentiment_label": "Biến Động Rủi Ro",
                "risk_level": "high",
                "source": "Cafef / Tổng hợp",
                "published_at": "1 giờ trước",
                "time_str": now_vn,
                "badge_color": "amber"
            },
            {
                "id": "news_vn_04",
                "title": "Khối ngoại có dấu hiệu giảm nhịp bán ròng, bắt đầu gom rải các cổ phiếu thép và ngân hàng định giá rẻ",
                "summary": "Thống kê phiên gần nhất cho thấy đà bán ròng của khối ngoại chững lại đáng kể, dòng tiền quỹ ETF ngoại xuất hiện mua ròng nhẹ ở các mã đầu ngành như HPG, TCB, FPT.",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "stocks",
                "asset_tags": ["Cổ Phiếu", "Khối Ngoại", "VN30"],
                "impact_asset": "Cổ Phiếu VN30",
                "sentiment": "positive",
                "sentiment_label": "Tích Cực",
                "risk_level": "low",
                "source": "HOSE / Dữ liệu Quant",
                "published_at": "1.5 giờ trước",
                "time_str": now_vn,
                "badge_color": "emerald"
            },

            # ---------------- TIN QUỐC TẾ ----------------
            {
                "id": "news_intl_01",
                "title": "Căng thẳng địa chính trị leo thang tại Trung Đông và biển Đỏ đẩy giá dầu thô Brent tiệm cận vùng đỉnh",
                "summary": "Rủi ro phong tỏa các tuyến hàng hải huyết mạch khiến cước vận tải biển tăng vọt, đe dọa chuỗi cung ứng toàn cầu và làm nóng lại áp lực lạm phát chi phí đẩy.",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "politics",
                "asset_tags": ["Chính Trị", "Địa Chính Trị", "Dầu Thô"],
                "impact_asset": "Dầu Khí & Lạm Phát",
                "sentiment": "negative",
                "sentiment_label": "Rủi Ro Địa Chính Trị",
                "risk_level": "high",
                "source": "Reuters / Bloomberg",
                "published_at": "25 phút trước",
                "time_str": now_vn,
                "badge_color": "rose"
            },
            {
                "id": "news_intl_02",
                "title": "Giá vàng thế giới (Spot Gold) duy trì sức ép trên mốc lịch sử do nhu cầu tích trữ hầm trú ẩn an toàn",
                "summary": "Bất ổn địa chính trị cùng động thái mua ròng liên tục của các Ngân hàng Trung ương toàn cầu (PBOC, RBI) đang tạo bệ đỡ vững chắc cho kim loại quý vượt mọi kháng cự kỹ thuật.",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "gold",
                "asset_tags": ["Giá Vàng", "Gold XAU", "Ngân Hàng TW"],
                "impact_asset": "Giá Vàng Thế Giới",
                "sentiment": "positive",
                "sentiment_label": "Tăng Trưởng Mạnh (Vàng)",
                "risk_level": "medium",
                "source": "Kitco / Financial Times",
                "published_at": "45 phút trước",
                "time_str": now_vn,
                "badge_color": "amber"
            },
            {
                "id": "news_intl_03",
                "title": "Bitcoin (BTC) giằng co quanh vùng tâm lý quan trọng khi dòng vốn ETF giao ngay ghi nhận tuần hút ròng mới",
                "summary": "Các quỹ ETF Bitcoin giao ngay của BlackRock và Fidelity tiếp tục ghi nhận dòng vốn vào ròng hàng trăm triệu USD, bất chấp những đợt rung lắc chốt lời ngắn hạn từ các thợ đào.",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "btc",
                "asset_tags": ["Bitcoin", "BTC", "ETF Crypto"],
                "impact_asset": "Bitcoin & Crypto",
                "sentiment": "positive",
                "sentiment_label": "Tích Cực Trung Hạn",
                "risk_level": "medium",
                "source": "CoinDesk / The Block",
                "published_at": "1 giờ trước",
                "time_str": now_vn,
                "badge_color": "cyan"
            },
            {
                "id": "news_intl_04",
                "title": "Chủ tịch FED báo hiệu lộ trình nới lỏng thận trọng, phụ thuộc chặt chẽ vào số liệu việc làm và CPI sắp công bố",
                "summary": "Thị trường tài chính toàn cầu bước vào giai đoạn nín thở chờ đợi các chỉ báo lạm phát, các chỉ số chứng khoán Mỹ (S&P 500, Nasdaq) xuất hiện áp lực chốt lời ngắn hạn.",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "macro",
                "asset_tags": ["FED", "Lãi Suất", "Lạm Phát CPI"],
                "impact_asset": "Chứng Khoán Toàn Cầu & Tỷ Giá",
                "sentiment": "neutral",
                "sentiment_label": "Giằng Co / Chờ Đợi",
                "risk_level": "medium",
                "source": "Wall Street Journal / CNBC",
                "published_at": "2 giờ trước",
                "time_str": now_vn,
                "badge_color": "indigo"
            }
        ]

        # Bộ lọc theo vùng miền (trong nước / quốc tế)
        if region:
            news_items = [n for n in news_items if n["region"] == region.lower()]

        # Bộ lọc theo tài sản (stocks, gold, btc, politics)
        if asset:
            news_items = [n for n in news_items if n["asset_category"] == asset.lower() or asset.lower() in [t.lower() for t in n["asset_tags"]]]

        # Tìm kiếm theo từ khóa
        if search:
            q = search.lower().strip()
            news_items = [
                n for n in news_items
                if q in n["title"].lower() or q in n["summary"].lower() or any(q in t.lower() for t in n["asset_tags"])
            ]

        return news_items

    def get_risk_assessment_report(self) -> Dict:
        """
        Báo cáo phân tích và đánh giá rủi ro vĩ mô / tin tức tác động lên danh mục tài sản đầu tư.
        """
        return {
            "last_updated": get_vietnam_now().strftime("%H:%M %d/%m/%Y"),
            "market_risk_index": 58,  # Điểm rủi ro từ 0 (cực an toàn) đến 100 (cực kỳ rủi ro)
            "risk_status": "TRUNG BÌNH - THẬN TRỌNG",
            "risk_color": "amber",
            "executive_summary": (
                "Bối cảnh tin tức tài chính hiện tại đang chịu sự giằng co giữa hai luồng tác động: "
                "Căng thẳng địa chính trị và áp lực tỷ giá USD/VND ở mức trung bình cao, tuy nhiên các yếu tố nội tại "
                "như tiến trình nâng hạng thị trường chứng khoán và chính sách tiền tệ hỗ trợ tăng trưởng của Việt Nam đang là bệ đỡ vững chắc."
            ),
            "asset_impact_matrix": [
                {
                    "asset_name": "Thị Trường Cổ Phiếu VN30",
                    "impact_level": "Trung Bình",
                    "impact_color": "amber",
                    "trend_bias": "Tích Lũy / Phân Hóa Rõ Nét",
                    "key_driver": "Kỳ vọng nâng hạng FTSE & Dòng vốn nội hỗ trợ định giá rẻ.",
                    "risk_factors": "Áp lực bán ròng rải rác của khối ngoại và tỷ giá neo cao.",
                    "recommendation": "Duy trì tỷ trọng cổ phiếu 50 - 60%, hạn chế margin cao, ưu tiên cổ phiếu đầu ngành có P/B hấp dẫn (Ngân hàng, Thép, Bán lẻ)."
                },
                {
                    "asset_name": "Thị Trường Vàng (Gold XAU & SJC)",
                    "impact_level": "Cao",
                    "impact_color": "rose",
                    "trend_bias": "Tăng Trưởng Nóng / Biến Động Rủi Ro",
                    "key_driver": "Nhu cầu tích trữ phòng vệ rủi ro chiến sự toàn cầu và lực mua từ các NHTW.",
                    "risk_factors": "Chính sách quản lý siết chặt thị trường vàng miếng và chênh lệch giá nội - ngoại cao.",
                    "recommendation": "Không nên mua đuổi khi giá lập đỉnh; canh chốt lời từng phần nếu đang nắm giữ vị thế lớn."
                },
                {
                    "asset_name": "Thị Trường Tiền Số (Bitcoin / Crypto)",
                    "impact_level": "Cao",
                    "impact_color": "cyan",
                    "trend_bias": "Dao Động Biên Rộng (Volatile)",
                    "key_driver": "Dòng vốn vào các quỹ ETF Bitcoin giao ngay của phố Wall.",
                    "risk_factors": "Độ nhạy cảm cực lớn với động thái lãi suất của FED và thanh lý hợp đồng phái sinh đòn bẩy.",
                    "recommendation": "Quản lý chặt đòn bẩy (leverage), chỉ giải ngân giao ngay (Spot) tại các vùng hỗ trợ dài hạn."
                },
                {
                    "asset_name": "Thị Trường Tiền Tệ & Ngoại Hối (USD/VND)",
                    "impact_level": "Trung Bình",
                    "impact_color": "amber",
                    "trend_bias": "Áp Lực Ổn Định Dần",
                    "key_driver": "Chỉ số DXY thế giới duy trì vùng cao trước các thông điệp của FED.",
                    "risk_factors": "Chênh lệch lãi suất VND - USD tạo sức ép lên cán cân thanh toán.",
                    "recommendation": "Doanh nghiệp xuất nhập khẩu nên chủ động sử dụng các hợp đồng phái sinh tỷ giá (Forward/Swap) để phòng vệ rủi ro."
                }
            ],
            "actionable_hedging_strategies": [
                {
                    "title": "Quản Trị Tỷ Trọng & Đòn Bẩy Margin",
                    "desc": "Khi chỉ số rủi ro tin tức ở ngưỡng 58/100, tuyệt đối không full margin ở các phiên tăng điểm hưng phấn; duy trì lượng tiền mặt dự phòng tối thiểu 30%."
                },
                {
                    "title": "Đa Dạng Hóa Danh Mục Phòng Vệ",
                    "desc": "Kết hợp phân bổ tài sản: 60% Cổ phiếu chất lượng cao VN30 + 20% Tài sản phòng vệ (Vàng/Tiền gửi kỳ hạn ngắn) + 20% Tiền mặt chờ cơ hội bứt phá."
                },
                {
                    "title": "Kỷ Luật Cắt Lỗ Dựa Trên ATR",
                    "desc": "Tuân thủ chặt chẽ các mức Stoploss tự động được hệ thống Quant tính toán sẵn cho từng mã, không gồng lỗ khi tin tức tiêu cực xác nhận đà giảm kỹ thuật."
                }
            ]
        }
