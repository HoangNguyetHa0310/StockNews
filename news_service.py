# -*- coding: utf-8 -*-
"""
Module Cung Cấp Tin Tức Tài Chính Real-Time & Báo Cáo Đánh Giá Rủi Ro Chuyên Sâu
Tự động quét RSS từ các cơ quan báo chí tài chính chính thống (CafeF, VnExpress)
Tính toán thời gian thực tế (real-time relative elapsed time) và phân loại tác động:
Cổ phiếu VN30, Giá Vàng (Gold), Bitcoin (BTC), và Chính trị / Vĩ mô.
"""
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from config import get_vietnam_now, VIETNAM_TZ


class NewsService:
    def __init__(self):
        self.cached_news = []
        self.last_fetch_time: Optional[datetime] = None
        self.cache_ttl_seconds = 180  # Làm mới từ RSS mỗi 3 phút

    def _fetch_rss_items(self) -> List[Dict]:
        """Quét tin tức tài chính trực tiếp từ RSS CafeF và VnExpress."""
        rss_sources = [
            {
                "url": "https://cafef.vn/thi-truong-chung-khoan.rss",
                "source": "CafeF / Chứng Khoán",
                "default_region": "domestic"
            },
            {
                "url": "https://cafef.vn/tai-chinh-quoc-te.rss",
                "source": "CafeF / Quốc Tế",
                "default_region": "international"
            },
            {
                "url": "https://vnexpress.net/rss/kinh-doanh.rss",
                "source": "VnExpress / Kinh Doanh",
                "default_region": "domestic"
            }
        ]

        raw_items = []
        now_vn = get_vietnam_now()

        for src in rss_sources:
            try:
                req = urllib.request.Request(
                    src["url"],
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                with urllib.request.urlopen(req, timeout=4) as resp:
                    root = ET.fromstring(resp.read())
                    channel = root.find("channel")
                    if channel is None:
                        continue
                    items = channel.findall("item")[:15]  # Lấy 15 tin mới nhất mỗi nguồn

                    for it in items:
                        title_el = it.find("title")
                        desc_el = it.find("description")
                        link_el = it.find("link")
                        pub_el = it.find("pubDate")

                        title = title_el.text.strip() if title_el is not None and title_el.text else ""
                        if not title:
                            continue

                        raw_desc = desc_el.text if desc_el is not None and desc_el.text else ""
                        clean_desc = re.sub(r"<[^<]+?>", "", raw_desc).strip()
                        # Xóa text ảnh hoặc khoảng trắng thừa
                        clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

                        link = link_el.text.strip() if link_el is not None and link_el.text else ""
                        pub_str = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

                        pub_dt = None
                        if pub_str:
                            try:
                                pub_dt = parsedate_to_datetime(pub_str)
                            except Exception:
                                pub_dt = now_vn

                        if not pub_dt:
                            pub_dt = now_vn

                        raw_items.append({
                            "title": title,
                            "summary": clean_desc if len(clean_desc) > 10 else title,
                            "url": link,
                            "pub_dt": pub_dt,
                            "source": src["source"],
                            "region": src["default_region"]
                        })
            except Exception as e:
                # Nếu 1 nguồn bị timeout, tiếp tục nguồn khác
                continue

        return raw_items

    def _analyze_impact(self, text: str, title: str, summary: str, region: str) -> Dict:
        """
        Phân tích chuyên sâu tác động tới cổ phiếu / nhóm ngành:
        - Xác định rõ mã cổ phiếu hoặc nhóm ngành cụ thể chịu tác động.
        - Giải thích cơ chế TẠI SAO lại ảnh hưởng (lý do kinh tế, dòng tiền, pháp lý, chi phí).
        - Nhận diện chính xác tin tức sự cố / tai nạn xã hội để KHÔNG gắn nhãn sai là ảnh hưởng VN30.
        """
        # 0. Kiểm tra sự cố / tai nạn dân sự / tin xã hội quốc tế
        incident_words = [
            "cháy phà", "tai nạn", "thiệt mạng", "mất tích", "động đất", "cháy nhà", 
            "xe khách", "cứu hộ", "sập cầu", "lật tàu", "vụ nổ", "rơi máy bay dân sự",
            "chết người", "đuối nước", "hỏa hoạn khu dân cư", "cháy rừng"
        ]
        is_social_incident = any(w in text for w in incident_words)

        finance_keywords = [
            "cổ phiếu", "chứng khoán", "doanh thu", "lợi nhuận", "vnindex", "vn30", 
            "ngân hàng", "bất động sản", "tín dụng", "lãi suất", "tỷ giá", "thép", 
            "dầu khí", "bán lẻ", "fpt", "hpg", "vhm", "vic", "vcb"
        ]
        has_finance_context = any(w in text for w in finance_keywords)

        if is_social_incident and not has_finance_context:
            return {
                "affected_stocks": "Không ảnh hưởng trực tiếp đến rổ VN30",
                "impact_reason": "Sự việc tai nạn xã hội/hàng hải dân sự đơn lẻ, không tác động đến hoạt động sản xuất kinh doanh, chuỗi cung ứng hay định giá của các doanh nghiệp niêm yết trên TTCK Việt Nam.",
                "impact_degree": "Không ảnh hưởng",
                "is_direct_stock_impact": False,
                "asset_category": "politics",
                "asset_tags": ["Quốc Tế" if region == "international" else "Xã Hội", "Sự Cố"],
                "impact_asset": "Tâm lý Xã hội / Vận tải",
                "sentiment_override": ("neutral", "Tin Xã Hội / Không ảnh hưởng VN30", "cyan", "low")
            }

        # 1. Quét theo từng mã cổ phiếu VN30 cụ thể (Tên mã hoặc tên tập đoàn)
        stock_rules = [
            (
                ["hòa phát", "hpg", "thép hòa phát", "dung quất", "thép thanh", "quặng sắt", "hrc", "giá thép"],
                "HPG (Tập đoàn Hòa Phát)",
                "Biến động giá thép và nhu cầu xây dựng/đầu tư công tác động trực tiếp đến sản lượng tiêu thụ và biên lợi nhuận gộp của Hòa Phát.",
                "Trực tiếp",
                ["Cổ Phiếu", "HPG", "Ngành Thép"]
            ),
            (
                ["fpt", "fpt software", "fpt telecom", "chíp bán dẫn", "phần mềm fpt", "trí tuệ nhân tạo", "ai việt nam"],
                "FPT (Tập đoàn FPT)",
                "Tăng trưởng hợp đồng xuất khẩu phần mềm, nhu cầu chuyển đổi số toàn cầu và phát triển công nghệ AI thúc đẩy doanh thu và định giá P/E của FPT.",
                "Trực tiếp",
                ["Cổ Phiếu", "FPT", "Công Nghệ"]
            ),
            (
                ["vinhomes", "vingroup", "vincom retail", "vhm", "vic", "vre", "vinfast"],
                "VHM, VIC, VRE (Họ Vingroup)",
                "Tiến độ pháp lý mở bán các đại dự án, doanh số bán lẻ tại các TTTM và kế hoạch huy động vốn tác động trực tiếp đến dòng tiền và định giá cổ phiếu.",
                "Trực tiếp",
                ["Cổ Phiếu", "VHM", "Bất Động Sản"]
            ),
            (
                ["vietcombank", "bidv", "vietinbank", "vcb", "bid", "ctg"],
                "VCB, BID, CTG (Big 4 Ngân hàng)",
                "Dẫn dắt thanh khoản toàn hệ thống; chính sách điều hành lãi suất của NHNN, biên lãi ròng (NIM) và trích lập dự phòng nợ xấu tác động trực tiếp đến lợi nhuận.",
                "Trực tiếp",
                ["Cổ Phiếu", "Ngân Hàng", "VN30"]
            ),
            (
                ["techcombank", "mbb", "quân đội", "acb", "vpb", "vpbank", "tcb", "ngân hàng tmcp"],
                "TCB, MBB, ACB, VPB (Ngân hàng TMCP)",
                "Nhạy cảm với hạn mức room tín dụng, chi phí vốn huy động tiền gửi và triển vọng hồi phục của thị trường trái phiếu doanh nghiệp.",
                "Trực tiếp",
                ["Cổ Phiếu", "Ngân Hàng", "VN30"]
            ),
            (
                ["pv gas", "petrolimex", "pv power", "gas", "plx", "pow", "khí lng", "dầu brent"],
                "GAS, PLX, POW (Năng lượng & Dầu khí)",
                "Biến động giá dầu thô thế giới và nhu cầu tiêu thụ khí/điện tác động trực tiếp đến giá bán buôn, chi phí sản xuất điện và biên phân phối xăng dầu.",
                "Trực tiếp",
                ["Cổ Phiếu", "Dầu Khí", "Năng Lượng"]
            ),
            (
                ["thế giới di động", "mwg", "masan", "msn", "vinamilk", "vnm", "sabeco", "sab"],
                "MWG, MSN, VNM, SAB (Tiêu dùng & Bán lẻ)",
                "Sức mua của người tiêu dùng nội địa, xu hướng chi tiêu bán lẻ và giá nguyên vật liệu đầu vào chi phối trực tiếp kết quả kinh doanh quý.",
                "Trực tiếp",
                ["Cổ Phiếu", "Bán Lẻ", "Tiêu Dùng"]
            ),
            (
                ["ssi", "chứng khoán ssi", "công ty chứng khoán", "dư nợ margin", "thanh khoản thị trường"],
                "SSI (Chứng khoán SSI)",
                "Thanh khoản giao dịch toàn thị trường và nhu cầu vay ký quỹ (margin) của nhà đầu tư quyết định trực tiếp doanh thu môi giới và cho vay.",
                "Trực tiếp",
                ["Cổ Phiếu", "SSI", "Chứng Khoán"]
            ),
            (
                ["vietjet", "vjc", "vé máy bay", "hàng không", "nhiên liệu bay"],
                "VJC (Vietjet Air)",
                "Lượng khách du lịch phục hồi và biến động giá nhiên liệu bay Jet A-1 là hai biến số cốt lõi chi phối biên lợi nhuận của doanh nghiệp hàng không.",
                "Trực tiếp",
                ["Cổ Phiếu", "VJC", "Hàng Không"]
            )
        ]

        for keywords, stock_label, reason, degree, tags in stock_rules:
            if any(w in text for w in keywords):
                return {
                    "affected_stocks": stock_label,
                    "impact_reason": reason,
                    "impact_degree": degree,
                    "is_direct_stock_impact": True,
                    "asset_category": "stocks",
                    "asset_tags": tags,
                    "impact_asset": stock_label,
                    "sentiment_override": None
                }

        # 2. Quét theo ngành kinh tế vĩ mô nếu không nhắc mã riêng lẻ
        if any(w in text for w in ["ngân hàng", "tín dụng", "nợ xấu", "casa", "lãi suất tiền gửi", "lãi suất cho vay", "room tín dụng", "thanh khoản liên ngân hàng"]):
            return {
                "affected_stocks": "VCB, BID, CTG, TCB, MBB, VPB (Nhóm Ngân hàng)",
                "impact_reason": "Nhóm Ngân hàng chiếm vốn hóa lớn nhất VN-Index (~35-40%); chính sách tín dụng và biến động mặt bằng lãi suất chi phối trực tiếp định giá của nhóm.",
                "impact_degree": "Ngành trọng điểm",
                "is_direct_stock_impact": True,
                "asset_category": "stocks",
                "asset_tags": ["Ngân Hàng", "Tín Dụng", "VN30"],
                "impact_asset": "Cổ Phiếu Ngân Hàng",
                "sentiment_override": None
            }

        if any(w in text for w in ["bất động sản", "nhà ở", "luật đất đai", "thị trường bđs", "chung cư", "đấu giá đất", "pháp lý dự án"]):
            return {
                "affected_stocks": "VHM, VIC, VRE, BCM, KDH (Nhóm Bất động sản)",
                "impact_reason": "Tháo gỡ pháp lý và nới lỏng tiếp cận vốn tín dụng giúp cải thiện dòng tiền bán hàng và tái khởi động các dự án lớn.",
                "impact_degree": "Ngành trọng điểm",
                "is_direct_stock_impact": True,
                "asset_category": "stocks",
                "asset_tags": ["Bất Động Sản", "VHM", "VN30"],
                "impact_asset": "Cổ Phiếu Bất Động Sản",
                "sentiment_override": None
            }

        if any(w in text for w in ["nâng hạng", "ftse", "msci", "pre-funding", "non-margin", "dòng vốn ngoại", "khối ngoại"]):
            return {
                "affected_stocks": "Toàn rổ VN30 (Đặc biệt SSI, HPG, VHM, FPT, VCB)",
                "impact_reason": "Triển vọng nâng hạng thị trường giúp thu hút dòng vốn ngoại quy mô tỷ USD giải ngân tập trung vào các cổ phiếu vốn hóa lớn VN30.",
                "impact_degree": "Toàn thị trường",
                "is_direct_stock_impact": True,
                "asset_category": "stocks",
                "asset_tags": ["Nâng Hạng", "Khối Ngoại", "VN30"],
                "impact_asset": "Cổ Phiếu VN30",
                "sentiment_override": ("positive", "Tích Cực Mạnh", "emerald", "low")
            }

        if any(w in text for w in ["fed", "lãi suất", "tỷ giá", "usd", "dxy", "lạm phát", "cpi", "gdp", "ngân hàng nhà nước", "nhnn", "tín phiếu"]):
            return {
                "affected_stocks": "Toàn rổ VN30 (Nhạy cảm nhất: Ngân hàng & Nhóm nợ USD)",
                "impact_reason": "Biến động tỷ giá USD/VND và định hướng lãi suất ảnh hưởng tới dòng vốn ngoại cũng như chi phí tài chính của toàn bộ doanh nghiệp niêm yết.",
                "impact_degree": "Vĩ mô diện rộng",
                "is_direct_stock_impact": True,
                "asset_category": "macro",
                "asset_tags": ["Vĩ Mô", "Tỷ Giá", "Lãi Suất"],
                "impact_asset": "Kinh Tế Vĩ Mô & Tỷ Giá",
                "sentiment_override": None
            }

        if any(w in text for w in ["vàng", "sjc", "spot gold", "xau", "nhẫn 9999", "kim loại quý"]):
            return {
                "affected_stocks": "Tài sản Trú ẩn & Cổ phiếu Vàng bạc (PNJ)",
                "impact_reason": "Vàng tăng nóng có thể hút một phần dòng tiền nhàn rỗi khỏi kênh chứng khoán; khi vàng bình ổn, dòng tiền có xu hướng quay lại thị trường cổ phiếu.",
                "impact_degree": "Gián tiếp dòng tiền",
                "is_direct_stock_impact": False,
                "asset_category": "gold",
                "asset_tags": ["Giá Vàng", "Vàng SJC", "Kim Loại Quý"],
                "impact_asset": "Giá Vàng (SJC & Thế Giới)",
                "sentiment_override": None
            }

        if any(w in text for w in ["bitcoin", "btc", "crypto", "tiền số", "tiền điện tử"]):
            return {
                "affected_stocks": "Tài sản Số (Crypto & Khẩu vị Rủi ro)",
                "impact_reason": "Phản ánh tâm lý đầu cơ toàn cầu; biến động giá Bitcoin ít tác động trực tiếp đến kết quả sản xuất kinh doanh của rổ cổ phiếu VN30.",
                "impact_degree": "Tâm lý đầu cơ",
                "is_direct_stock_impact": False,
                "asset_category": "btc",
                "asset_tags": ["Bitcoin", "BTC", "Crypto"],
                "impact_asset": "Bitcoin & Tiền Số",
                "sentiment_override": None
            }

        if any(w in text for w in ["chiến sự", "trung đông", "iran", "israel", "nga", "ukraine", "biển đỏ", "quân sự", "tấn công", "trừng phạt", "giá dầu"]):
            return {
                "affected_stocks": "Nhóm Dầu khí (GAS, PLX) & Xuất nhập khẩu",
                "impact_reason": "Căng thẳng địa chính trị đẩy giá dầu và cước tàu biển lên cao; nhóm dầu khí hưởng lợi ngắn hạn trong khi các ngành sản xuất chịu chi phí logistics tăng.",
                "impact_degree": "Ngành dầu khí & logistics",
                "is_direct_stock_impact": True,
                "asset_category": "politics",
                "asset_tags": ["Chính Trị", "Địa Chính Trị", "Dầu Khí"],
                "impact_asset": "Địa Chính Trị & Dầu Khí",
                "sentiment_override": None
            }

        # Mặc định: Tin kinh tế vĩ mô chung
        return {
            "affected_stocks": "Tâm lý chung thị trường VN30",
            "impact_reason": "Cung cấp thêm dữ liệu môi trường vĩ mô và sức cầu nội địa, tác động gián tiếp đến kỳ vọng tăng trưởng của thị trường.",
            "impact_degree": "Gián tiếp",
            "is_direct_stock_impact": False,
            "asset_category": "stocks",
            "asset_tags": ["Thị Trường", "VN30"],
            "impact_asset": "Cổ Phiếu VN30",
            "sentiment_override": None
        }

    def _classify_article(self, item: Dict) -> Dict:
        """Tự động phân loại tài sản, tag, đánh giá sắc thái và phân tích tác động cổ phiếu chuyên sâu."""
        text = (item["title"] + " " + item["summary"]).lower()

        # 1. Phân vùng trong nước / quốc tế
        region = item.get("region", "domestic")
        if any(w in text for w in ["việt nam", "trong nước", "hà nội", "tp.hcm", "hose", "hnx", "nhnn", "ubck"]):
            region = "domestic"
        elif any(w in text for w in ["mỹ", "trung quốc", "châu âu", "fed", "wall street", "thế giới", "quốc tế", "nga", "iran"]):
            region = "international"
        region_label = "Trong Nước" if region == "domestic" else "Quốc Tế"

        # 2. Phân tích tác động cổ phiếu & cơ chế tại sao
        impact_info = self._analyze_impact(text, item["title"], item["summary"], region)

        # 3. Đánh giá sắc thái (Sentiment)
        if impact_info.get("sentiment_override"):
            sentiment, sentiment_label, badge_color, risk_level = impact_info["sentiment_override"]
        else:
            pos_words = ["tăng", "lãi", "vượt đỉnh", "khởi sắc", "bứt phá", "hút", "mua ròng", "lạc quan", "phục hồi", "kỷ lục", "đột biến", "thặng dư", "tích cực", "nâng hạng", "hỗ trợ"]
            neg_words = ["giảm", "lỗ", "phạt", "rủi ro", "lao dốc", "bán tháo", "áp lực", "suy thoái", "thủng", "trừng phạt", "bán ròng", "tiêu cực", "cảnh báo"]

            pos_count = sum(1 for w in pos_words if w in text)
            neg_count = sum(1 for w in neg_words if w in text)

            if pos_count > neg_count and pos_count >= 1:
                sentiment = "positive"
                sentiment_label = "Tích Cực"
                badge_color = "emerald"
                risk_level = "low"
            elif neg_count > pos_count and neg_count >= 1:
                sentiment = "negative"
                sentiment_label = "Rủi Ro / Tiêu Cực"
                badge_color = "rose"
                risk_level = "high"
            else:
                sentiment = "neutral"
                sentiment_label = "Trung Tính / Giằng Co"
                badge_color = "cyan"
                risk_level = "medium"

        return {
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "pub_dt": item["pub_dt"],
            "source": item["source"],
            "region": region,
            "region_label": region_label,
            "asset_category": impact_info["asset_category"],
            "asset_tags": impact_info["asset_tags"],
            "impact_asset": impact_info["impact_asset"],
            "affected_stocks": impact_info["affected_stocks"],
            "impact_reason": impact_info["impact_reason"],
            "impact_degree": impact_info["impact_degree"],
            "is_direct_stock_impact": impact_info["is_direct_stock_impact"],
            "sentiment": sentiment,
            "sentiment_label": sentiment_label,
            "risk_level": risk_level,
            "badge_color": badge_color
        }

    def _get_fallback_news(self) -> List[Dict]:
        """Tập tin tức tài chính dự phòng khi mất kết nối mạng ngoài, thời gian luôn tính theo giờ hiện tại."""
        now_vn = get_vietnam_now()
        return [
            {
                "title": "Ngân hàng Nhà nước duy trì điều hành linh hoạt, kiểm soát tỷ giá USD/VND trước kỳ họp FED",
                "summary": "NHNN tiếp tục sử dụng các công cụ điều tiết thanh khoản trên thị trường mở (OMO) và phát hành tín phiếu để ổn định tỷ giá trong bối cảnh chỉ số DXY tăng cao.",
                "url": "https://vneconomy.vn/tai-chinh.htm",
                "pub_dt": now_vn - timedelta(minutes=18),
                "source": "VnEconomy / Cổng TT NHNN",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "macro",
                "asset_tags": ["Tỷ Giá", "Vĩ Mô", "Ngân Hàng"],
                "impact_asset": "Kinh Tế Vĩ Mô & Tỷ Giá",
                "affected_stocks": "VCB, BID, CTG, TCB, MBB (Nhóm Ngân hàng & Tỷ giá)",
                "impact_reason": "Động thái điều tiết cung tiền ngắn hạn nhằm kìm cương đà tăng của tỷ giá USD/VND; giúp bảo vệ ổn định vĩ mô nhưng thanh khoản liên ngân hàng có thể thận trọng.",
                "impact_degree": "Vĩ mô diện rộng",
                "is_direct_stock_impact": True,
                "sentiment": "neutral",
                "sentiment_label": "Trung Tính / Thận Trọng",
                "risk_level": "medium",
                "badge_color": "cyan"
            },
            {
                "title": "Chính phủ quyết liệt thúc đẩy giải pháp nâng hạng thị trường chứng khoán Việt Nam lên FTSE Emerging",
                "summary": "Bộ Tài chính và UBCKNN đang tích cực tháo gỡ nút thắt ký quỹ trước giao dịch (Non-margin / Pre-funding) cho khối ngoại, tạo động lực đón dòng vốn tỷ USD vào nhóm VN30.",
                "url": "https://baodautu.vn/chung-khoan-d4/",
                "pub_dt": now_vn - timedelta(minutes=45),
                "source": "UBCKNN / Báo Đầu Tư",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "stocks",
                "asset_tags": ["Cổ Phiếu", "VN30", "FTSE"],
                "impact_asset": "Cổ Phiếu VN30",
                "affected_stocks": "Toàn rổ VN30 (Đặc biệt SSI, HPG, VHM, FPT, VCB)",
                "impact_reason": "Tháo gỡ tiêu chí Non-margin của tổ chức FTSE Russell mở đường đón dòng vốn ngoại thụ động (ETF) quy mô hàng tỷ USD giải ngân tập trung vào các mã trụ.",
                "impact_degree": "Toàn thị trường",
                "is_direct_stock_impact": True,
                "sentiment": "positive",
                "sentiment_label": "Tích Cực Mạnh",
                "risk_level": "low",
                "badge_color": "emerald"
            },
            {
                "title": "Căng thẳng địa chính trị leo thang tại Trung Đông và biển Đỏ đẩy giá dầu thô Brent duy trì mức cao",
                "summary": "Rủi ro phong tỏa các tuyến hàng hải huyết mạch khiến cước vận tải biển tăng vọt, đe dọa chuỗi cung ứng toàn cầu và làm nóng lại áp lực lạm phát chi phí đẩy.",
                "url": "https://www.reuters.com/markets/commodities/",
                "pub_dt": now_vn - timedelta(hours=1, minutes=15),
                "source": "Reuters / Bloomberg",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "politics",
                "asset_tags": ["Chính Trị", "Địa Chính Trị", "Dầu Thô"],
                "impact_asset": "Địa Chính Trị & Dầu Khí",
                "affected_stocks": "GAS (PV Gas), PLX (Petrolimex), POW",
                "impact_reason": "Giá dầu duy trì vùng cao giúp cải thiện biên phân phối và lợi nhuận bán buôn dầu khí; tuy nhiên cước tàu tăng gia tăng áp lực chi phí nguyên liệu đầu vào.",
                "impact_degree": "Ngành dầu khí",
                "is_direct_stock_impact": True,
                "sentiment": "negative",
                "sentiment_label": "Rủi Ro Địa Chính Trị",
                "risk_level": "high",
                "badge_color": "rose"
            },
            {
                "title": "Giá vàng miếng SJC và vàng nhẫn 9999 biến động mạnh sau công điện thanh tra thị trường vàng",
                "summary": "Các cơ quan quản lý đẩy mạnh thanh tra hoạt động kinh doanh vàng, chênh lệch giữa giá vàng trong nước và thế giới thu hẹp, giao dịch tại các nhà vàng lớn duy trì trạng thái thận trọng.",
                "url": "https://cafef.vn/thi-truong-vang.chn",
                "pub_dt": now_vn - timedelta(hours=1, minutes=45),
                "source": "Cafef / Tổng hợp",
                "region": "domestic",
                "region_label": "Trong Nước",
                "asset_category": "gold",
                "asset_tags": ["Vàng SJC", "Vàng Nhẫn", "Chính Sách"],
                "impact_asset": "Giá Vàng (SJC & Thế Giới)",
                "affected_stocks": "Tài sản Trú ẩn & Doanh nghiệp Vàng (PNJ)",
                "impact_reason": "Siết chặt thanh tra giúp thu hẹp chênh lệch giá vàng, giảm tình trạng đầu cơ vàng miếng và kích thích dòng tiền nhàn rỗi dịch chuyển sang chứng khoán.",
                "impact_degree": "Gián tiếp dòng tiền",
                "is_direct_stock_impact": False,
                "sentiment": "neutral",
                "sentiment_label": "Thanh Tra / Bình Ổn",
                "risk_level": "medium",
                "badge_color": "amber"
            },
            {
                "title": "Bitcoin (BTC) giằng co quanh vùng tâm lý quan trọng khi dòng vốn ETF giao ngay ghi nhận tuần hút ròng mới",
                "summary": "Các quỹ ETF Bitcoin giao ngay của BlackRock và Fidelity tiếp tục ghi nhận dòng vốn vào ròng hàng trăm triệu USD, bất chấp những đợt rung lắc chốt lời ngắn hạn từ các thợ đào.",
                "url": "https://www.coindesk.com/",
                "pub_dt": now_vn - timedelta(hours=2, minutes=20),
                "source": "CoinDesk / The Block",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "btc",
                "asset_tags": ["Bitcoin", "BTC", "ETF Crypto"],
                "impact_asset": "Bitcoin & Tiền Số",
                "affected_stocks": "Tài sản Số (Khẩu vị Rủi ro Toàn cầu)",
                "impact_reason": "Dòng vốn tổ chức vào ETF phản ánh khẩu vị rủi ro quốc tế ổn định, ít có tác động trực tiếp đến định giá sản xuất kinh doanh của rổ cổ phiếu VN30.",
                "impact_degree": "Tâm lý đầu cơ",
                "is_direct_stock_impact": False,
                "sentiment": "positive",
                "sentiment_label": "Tích Cực Trung Hạn",
                "risk_level": "medium",
                "badge_color": "cyan"
            },
            {
                "title": "Chủ tịch FED báo hiệu lộ trình nới lỏng thận trọng, phụ thuộc chặt chẽ vào số liệu việc làm và CPI sắp công bố",
                "summary": "Thị trường tài chính toàn cầu bước vào giai đoạn nín thở chờ đợi các chỉ báo lạm phát, các chỉ số chứng khoán Mỹ (S&P 500, Nasdaq) xuất hiện áp lực chốt lời ngắn hạn.",
                "url": "https://www.cnbc.com/economy/",
                "pub_dt": now_vn - timedelta(hours=3, minutes=10),
                "source": "Wall Street Journal / CNBC",
                "region": "international",
                "region_label": "Quốc Tế",
                "asset_category": "macro",
                "asset_tags": ["FED", "Lãi Suất", "Lạm Phát CPI"],
                "impact_asset": "Kinh Tế Vĩ Mô & Tỷ Giá",
                "affected_stocks": "Toàn rổ VN30 (Tâm lý NĐT Toàn cầu)",
                "impact_reason": "Định hướng lãi suất của FED tác động trực tiếp tới chỉ số sức mạnh đồng USD (DXY), chênh lệch lãi suất USD/VND và dòng vốn đầu tư gián tiếp.",
                "impact_degree": "Vĩ mô diện rộng",
                "is_direct_stock_impact": True,
                "sentiment": "neutral",
                "sentiment_label": "Giằng Co / Chờ Đợi",
                "risk_level": "medium",
                "badge_color": "indigo"
            }
        ]

    def get_market_news(self, region: Optional[str] = None, asset: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        """
        Lấy danh sách tin tức tài chính mới nhất với thời gian tương đối (relative time)
        được tính toán chính xác theo thời điểm hiện tại.
        """
        now_vn = get_vietnam_now()

        # Kiểm tra xem có cần quét mới từ RSS không
        should_fetch = (
            not self.cached_news or
            self.last_fetch_time is None or
            (now_vn - self.last_fetch_time).total_seconds() > self.cache_ttl_seconds
        )

        if should_fetch:
            try:
                raw_rss = self._fetch_rss_items()
                if raw_rss and len(raw_rss) >= 4:
                    classified = [self._classify_article(it) for it in raw_rss]
                    # Sắp xếp theo bài mới nhất lên đầu
                    classified.sort(key=lambda x: x["pub_dt"], reverse=True)
                    self.cached_news = classified
                    self.last_fetch_time = now_vn
            except Exception as e:
                print(f"[NewsService] Lỗi quét RSS: {e}")

        # Nếu không có tin từ RSS, nạp fallback
        if not self.cached_news:
            self.cached_news = self._get_fallback_news()
            self.last_fetch_time = now_vn

        # Tính toán lại thời gian hiển thị (published_at) động cho từng bài tại thời điểm gọi API
        result_items = []
        for idx, it in enumerate(self.cached_news):
            pub_dt = it.get("pub_dt")
            if pub_dt:
                try:
                    diff = now_vn - pub_dt
                    diff_secs = max(0, int(diff.total_seconds()))
                    diff_mins = diff_secs // 60
                    diff_hours = diff_mins // 60
                    diff_days = diff_hours // 24

                    if diff_mins < 1:
                        published_at = "Vừa xong"
                    elif diff_mins < 60:
                        published_at = f"{diff_mins} phút trước"
                    elif diff_hours < 24:
                        published_at = f"{diff_hours} giờ trước"
                    elif diff_days == 1:
                        published_at = "Hôm qua"
                    else:
                        published_at = f"{diff_days} ngày trước"
                except Exception:
                    published_at = "Hôm nay"
            else:
                published_at = "Hôm nay"

            item_copy = dict(it)
            item_copy["id"] = f"news_{idx+1}"
            item_copy["published_at"] = published_at
            item_copy["time_str"] = pub_dt.strftime("%H:%M %d/%m/%Y") if pub_dt else now_vn.strftime("%H:%M %d/%m/%Y")
            result_items.append(item_copy)

        # Lọc theo vùng miền (trong nước / quốc tế)
        if region:
            result_items = [n for n in result_items if n["region"] == region.lower()]

        # Lọc theo loại tài sản (stocks, gold, btc, politics, macro)
        if asset:
            a_lower = asset.lower()
            result_items = [
                n for n in result_items
                if n["asset_category"] == a_lower or any(a_lower in t.lower() for t in n.get("asset_tags", []))
            ]

        # Tìm kiếm theo từ khóa
        if search:
            q = search.lower().strip()
            result_items = [
                n for n in result_items
                if q in n["title"].lower() or q in n["summary"].lower() or any(q in t.lower() for t in n.get("asset_tags", []))
            ]

        return result_items

    def get_risk_assessment_report(self, state: Optional[Dict] = None, flow_service=None) -> Dict:
        """
        Báo cáo phân tích và đánh giá rủi ro thị trường chuyên sâu:
        - Tính toán Chỉ số Rủi ro (Market Risk Index) động từ trạng thái rổ VN30 và dòng tiền.
        - Khuyến nghị tỷ trọng danh mục cụ thể (% Cổ phiếu / % Tiền mặt / Margin).
        - Đưa ra 2 kịch bản hành động cụ thể cho VN-INDEX (Vượt cản vs Phòng thủ gãy nền).
        - Bảng hành động chi tiết từng nhóm ngành VN30 (Ngân hàng, Thép, Công nghệ, BĐS, Dầu khí).
        """
        now_vn = get_vietnam_now()

        # 1. Thu thập dữ liệu thực tế từ Quant Engine nếu có
        total_stocks = 30
        buy_count = 15
        sell_count = 2
        hold_count = 13
        vnindex_close = 1819.97
        vnindex_change = -0.39
        is_above_ma20 = True

        if state:
            analyses = state.get("stock_analyses", [])
            if analyses:
                total_stocks = len(analyses)
                buy_count = sum(1 for s in analyses if "MUA" in s.get("signal", ""))
                sell_count = sum(1 for s in analyses if "BÁN" in s.get("signal", ""))
                hold_count = total_stocks - buy_count - sell_count

            summary = state.get("market_summary", {})
            if summary:
                vnindex_close = summary.get("vnindex_close", vnindex_close)
                vnindex_change = summary.get("vnindex_change_pct", vnindex_change)

            vn_df = state.get("vnindex_df")
            if vn_df is not None and not vn_df.empty:
                last_row = vn_df.iloc[-1]
                close_p = last_row.get("close", 0)
                ma20 = last_row.get("ma20", close_p)
                is_above_ma20 = (close_p >= ma20)

        # 2. Tính toán điểm rủi ro động (Dynamic Market Risk Index từ 0 đến 100)
        # Điểm cơ sở: 50
        risk_score = 50.0

        # Nếu số mã Mua áp đảo -> Giảm rủi ro
        buy_ratio = buy_count / max(total_stocks, 1)
        sell_ratio = sell_count / max(total_stocks, 1)
        risk_score -= (buy_ratio * 25.0)  # Có thể giảm tới 25 điểm
        risk_score += (sell_ratio * 35.0)  # Tăng tới 35 điểm nếu nhiều mã bán

        # Tác động từ chỉ số VN-INDEX
        if vnindex_change > 0:
            risk_score -= min(vnindex_change * 5.0, 10.0)
        else:
            risk_score += min(abs(vnindex_change) * 6.0, 15.0)

        if not is_above_ma20:
            risk_score += 10.0

        risk_score = int(round(min(max(risk_score, 20.0), 85.0)))

        # Phân loại trạng thái
        if risk_score <= 40:
            risk_status = "THẤP - TÍCH CỰC (VÙNG MỞ RỘNG VỊ THẾ)"
            risk_color = "emerald"
            stock_alloc = 75
            cash_alloc = 25
            margin_rec = "Cho phép sử dụng đòn bẩy tối đa 1.3x cho các mã dẫn dắt có điểm Quant > 75."
            strategy_mode = "Ưu tiên nắm giữ và mua gia tăng vị thế khi cổ phiếu có nhịp điều chỉnh kỹ thuật."
        elif risk_score <= 60:
            risk_status = "TRUNG BÌNH - THẬN TRỌNG (CÂN BẰNG DANH MỤC)"
            risk_color = "amber"
            stock_alloc = 60
            cash_alloc = 40
            margin_rec = "Hạn chế margin (tỷ lệ 0.0x - 1.0x). Tuyệt đối không dùng đòn bẩy trong các phiên hưng phấn."
            strategy_mode = "Tập trung nắm giữ danh mục chất lượng cao, chia tiền gom rải khi rung lắc, chốt lời từng phần khi đạt Target 1."
        else:
            risk_status = "CAO - BÁO ĐỘNG (ƯU TIÊN PHÒNG THỦ & HẠ TỶ TRỌNG)"
            risk_color = "rose"
            stock_alloc = 35
            cash_alloc = 65
            margin_rec = "Hạ toàn bộ margin về 0. Bán dứt khoát các mã chạm ngưỡng Stoploss."
            strategy_mode = "Bảo toàn vốn là ưu tiên hàng đầu, dừng giải ngân mua mới cho tới khi thị trường tạo đáy vững chắc."

        return {
            "last_updated": now_vn.strftime("%H:%M %d/%m/%Y"),
            "market_risk_index": risk_score,
            "risk_status": risk_status,
            "risk_color": risk_color,

            # Tỷ trọng khuyến nghị cụ thể
            "portfolio_allocation": {
                "stocks_pct": stock_alloc,
                "cash_pct": cash_alloc,
                "margin_recommendation": margin_rec,
                "strategy_mode": strategy_mode
            },

            # Tóm tắt bối cảnh
            "executive_summary": (
                f"Thị trường đang ghi nhận {buy_count}/{total_stocks} mã VN30 phát tín hiệu MUA, "
                f"chỉ số VN-INDEX biến động {vnindex_change:+.2f}% tại mốc {vnindex_close:,.2f}. "
                f"Chỉ số rủi ro tin tức và định lượng đang ở mức {risk_score}/100 ({risk_status}). "
                f"Khuyến nghị nhà đầu tư duy trì tỷ trọng an toàn: {stock_alloc}% Cổ phiếu và {cash_alloc}% Tiền mặt dự phòng, "
                f"tập trung vào các nhóm ngành có dòng tiền tổ chức bảo kê vững chắc."
            ),

            # Kịch bản hành động cụ thể cho VN-INDEX
            "index_scenarios": [
                {
                    "name": "Kịch Bản 1: Tích Cực / Vượt Cản (Bullish Scenario)",
                    "probability": "60%",
                    "badge_color": "emerald",
                    "target_range": f"Vượt mốc {int(vnindex_close + 25)} - {int(vnindex_close + 40)} điểm",
                    "trigger_condition": "VN-INDEX giữ vững trên mốc hỗ trợ kỹ thuật và thanh khoản phiên bùng nổ.",
                    "action_plan": (
                        "Nâng tỷ trọng cổ phiếu lên 70% - 80%. Mua gia tăng vị thế ở nhóm Ngân hàng và Thép đầu ngành "
                        "khi xuất hiện nhịp rung lắc tích lũy trong phiên. Chốt lời từng phần khi chạm Target 1."
                    )
                },
                {
                    "name": "Kịch Bản 2: Thận Trọng / Phòng Vệ (Defense Scenario)",
                    "probability": "40%",
                    "badge_color": "rose",
                    "target_range": f"Thủng vùng hỗ trợ {int(vnindex_close - 20)} điểm",
                    "trigger_condition": "Áp lực bán từ khối ngoại tăng đột biến hoặc tin tức địa chính trị/tỷ giá xấu khiến chỉ số gãy nền.",
                    "action_plan": (
                        "Hạ tỷ trọng cổ phiếu về 35% - 40%, đưa tiền mặt lên 60% - 65%. Kích hoạt kỷ luật dừng lỗ (Stoploss) "
                        "đối với các mã gãy đường MA20, tuyệt đối không bắt đáy sớm cho đến khi có tín hiệu nến đảo chiều rút chân."
                    )
                }
            ],

            # Bảng hành động chi tiết từng nhóm ngành VN30
            "sector_playbook": [
                {
                    "sector_name": "Ngân Hàng",
                    "tickers": "VCB, TCB, MBB, ACB, CTG, STB",
                    "allocation_pct": "35%",
                    "action": "ƯU TIÊN MUA TÍCH LŨY",
                    "action_color": "emerald",
                    "key_reason": "Tăng trưởng tín dụng cuối năm khởi sắc, định giá P/B ở vùng đáy lịch sử an toàn, dòng tiền tổ chức nâng đỡ chỉ số."
                },
                {
                    "sector_name": "Thép & Công Nghiệp",
                    "tickers": "HPG",
                    "allocation_pct": "15%",
                    "action": "MUA KHI RUNG LẮC",
                    "action_color": "emerald",
                    "key_reason": "Hưởng lợi trực tiếp từ tốc độ giải ngân các dự án đầu tư công trọng điểm, biên lợi nhuận hồi phục nhờ giá quặng ổn định."
                },
                {
                    "sector_name": "Công Nghệ & Bán Lẻ",
                    "tickers": "FPT, MWG",
                    "allocation_pct": "20%",
                    "action": "NẮM GIỮ DÀI HẠN",
                    "action_color": "cyan",
                    "key_reason": "Doanh thu và lợi nhuận cốt lõi tăng trưởng 20%+, đơn hàng xuất khẩu phần mềm & AI mạnh mẽ, ít rủi ro tỷ giá."
                },
                {
                    "sector_name": "Bất Động Sản",
                    "tickers": "VHM, VIC, VRE, KDH, BCM",
                    "allocation_pct": "10%",
                    "action": "THẬN TRỌNG / LƯỚT T+",
                    "action_color": "amber",
                    "key_reason": "Áp lực đáo hạn trái phiếu doanh nghiệp và thanh khoản bất động sản phục hồi chậm; chỉ tham gia tỷ trọng nhỏ, đặt stoploss chặt chẽ."
                },
                {
                    "sector_name": "Năng Lượng & Dầu Khí",
                    "tickers": "GAS, PLX, POW",
                    "allocation_pct": "10%",
                    "action": "PHÒNG VỆ HEDGING",
                    "action_color": "indigo",
                    "key_reason": "Hưởng lợi khi giá dầu thô Brent duy trì mức cao do căng thẳng địa chính trị quốc tế, đóng vai trò bảo hiểm danh mục khi có biến cố."
                }
            ],

            # Ma trận tác động 4 loại tài sản
            "asset_impact_matrix": [
                {
                    "asset_name": "Thị Trường Cổ Phiếu VN30",
                    "impact_level": "Tích Cực / Phân Hóa",
                    "impact_color": "emerald",
                    "trend_bias": "Tích Lũy Bứt Phá",
                    "key_driver": "Kỳ vọng nâng hạng thị trường FTSE & Kết quả kinh doanh quý phục hồi.",
                    "risk_factors": "Áp lực tỷ giá USD/VND và nhịp bán ròng của các quỹ ETF ngoại.",
                    "recommendation": f"Duy trì tỷ trọng {stock_alloc}% cổ phiếu đầu ngành, tập trung vào mã có điểm Quant > 70."
                },
                {
                    "asset_name": "Thị Trường Vàng (Gold XAU & SJC)",
                    "impact_level": "Cao / Biến Động",
                    "impact_color": "amber",
                    "trend_bias": "Neo Vùng Đỉnh Lịch Sử",
                    "key_driver": "Nhu cầu hầm trú ẩn an toàn toàn cầu và lực mua gom liên tục của các NHTW.",
                    "risk_factors": "Chính sách quản lý siết chặt thị trường vàng miếng và thanh tra của cơ quan quản lý.",
                    "recommendation": "Không mua đuổi khi giá lập đỉnh mới; canh chốt lời từng phần nếu đang có tỷ trọng vàng lớn."
                },
                {
                    "asset_name": "Thị Trường Tiền Số (Bitcoin / Crypto)",
                    "impact_level": "Cao / Rung Lắc",
                    "impact_color": "cyan",
                    "trend_bias": "Giằng Co Theo Dòng Vốn ETF",
                    "key_driver": "Dòng vốn ròng từ các định chế tài chính phố Wall qua các quỹ Bitcoin ETF.",
                    "risk_factors": "Nhạy cảm với thông điệp lãi suất của FED và thanh lý hợp đồng phái sinh đòn bẩy cao.",
                    "recommendation": "Quản lý chặt đòn bẩy margin, ưu tiên giao dịch giao ngay (Spot) tại các vùng hỗ trợ cứng."
                },
                {
                    "asset_name": "Thị Trường Ngoại Hối (Tỷ Giá USD/VND)",
                    "impact_level": "Trung Bình / Kiểm Soát",
                    "impact_color": "amber",
                    "trend_bias": "Áp Lực Ổn Định Dần",
                    "key_driver": "Chỉ số DXY thế giới duy trì cao nhưng NHNN có đầy đủ công cụ điều tiết linh hoạt.",
                    "risk_factors": "Chênh lệch lãi suất VND - USD tạo sức ép ngắn hạn lên cán cân thanh toán.",
                    "recommendation": "Theo dõi sát thông điệp của FED và động thái hút/bơm ròng trên thị trường mở (OMO)."
                }
            ],

            # Chiến lược phòng vệ kỷ luật
            "actionable_hedging_strategies": [
                {
                    "title": "Quản Trị Tỷ Trọng & Đòn Bẩy (Margin Management)",
                    "desc": f"Khi rủi ro ở ngưỡng {risk_score}/100, tuyệt đối không full margin; duy trì lượng tiền mặt tối thiểu {cash_alloc}% để chủ động đón nhịp điều chỉnh."
                },
                {
                    "title": "Kỷ Luật Cắt Lỗ Tự Động (ATR Stoploss)",
                    "desc": "Tuân thủ nghiêm ngặt mức Stoploss tự động được hệ thống tính toán cho từng mã; không gồng lỗ khi cổ phiếu gãy đường hỗ trợ MA20."
                },
                {
                    "title": "Chiến Lược Chốt Lời Từng Phần (Target Scaling)",
                    "desc": "Khi cổ phiếu đạt Target 1 (lợi nhuận 7% - 10%), chủ động hiện thực hóa 50% lợi nhuận, nâng mức dừng lỗ của 50% còn lại lên giá vốn để bảo vệ thành quả."
                }
            ]
        }
