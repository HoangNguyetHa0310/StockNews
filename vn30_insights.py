# -*- coding: utf-8 -*-
"""
Module Tri Thức & Phân Tích Chuyên Sâu Cổ Phiếu VN30 (VN30 Insights Engine)
Cung cấp thông tin doanh nghiệp, tin tức vĩ mô/ngành tác động,
và sinh lý do khuyến nghị chi tiết (Vì sao nên mua/bán/giữ, vì sao tăng giá, tin tức tác động).
"""

VN30_PROFILES = {
    "VCB": {
        "company_name": "Ngân hàng TMCP Ngoại thương Việt Nam",
        "sector": "Ngân hàng",
        "news_impact": "Hưởng lợi từ chính sách tiền tệ nới lỏng của NHNN, vị thế đầu ngành kiểm soát tốt tỷ lệ nợ xấu dưới 1.2%, và kế hoạch phát hành riêng lẻ tăng vốn điều lệ củng cố hệ số an toàn vốn CAR.",
        "growth_driver": "Biên lãi thuần (NIM) duy trì ổn định nhờ chi phí vốn thấp nhất hệ thống, vị thế số 1 mảng thanh toán quốc tế và tài trợ thương mại.",
        "risk_factor": "Áp lực trích lập dự phòng rủi ro tín dụng nếu nợ nhóm 2 ngành bất động sản gia tăng."
    },
    "TCB": {
        "company_name": "Ngân hàng TMCP Kỹ Thương Việt Nam",
        "sector": "Ngân hàng",
        "news_impact": "Động thái phục hồi của thị trường bất động sản và trái phiếu doanh nghiệp tháo gỡ nút thắt tài chính, dòng tiền gửi không kỳ hạn CASA quay lại mốc 40%.",
        "growth_driver": "Đón đầu chu kỳ tăng trưởng tín dụng bán lẻ và cho vay mua nhà; nền tảng công nghệ số và hệ sinh thái tài chính Masterise/Masan vượt trội.",
        "risk_factor": "Độ nhạy cảm cao với biến động của thị trường bất động sản dự án phân khúc cao cấp."
    },
    "FPT": {
        "company_name": "Công ty Cổ phần FPT",
        "sector": "Công nghệ thông tin",
        "news_impact": "Hưởng lợi trực tiếp từ làn sóng đầu tư AI toàn cầu, quan hệ đối tác chiến lược cùng Nvidia xây dựng AI Factory, và doanh thu xuất khẩu phần mềm sang Nhật Bản/Mỹ tăng trên 25%.",
        "growth_driver": "Tăng trưởng kép lợi nhuận ròng bền vững trên 20%/năm; mở rộng mảng đào tạo nhân lực bán dẫn và chuyển đổi số cho các tập đoàn đa quốc gia.",
        "risk_factor": "Biến động tỷ giá đồng Yên Nhật (JPY) và đồng USD ảnh hưởng đến doanh thu quy đổi từ thị trường nước ngoài."
    },
    "HPG": {
        "company_name": "Tập đoàn Hòa Phát",
        "sector": "Thép & Công nghiệp",
        "news_impact": "Chính phủ đẩy mạnh giải ngân đầu tư công các dự án cao tốc Bắc - Nam và sân bay Long Thành; tiến độ đại dự án Khu liên hợp Dung Quất 2 bám sát kế hoạch vận hành giai đoạn 1.",
        "growth_driver": "Công suất thép cuộn cán nóng (HRC) tăng gấp đôi lên 11 triệu tấn/năm khi Dung Quất 2 hoàn thành, củng cố vị thế độc tôn cung ứng HRC tại Việt Nam.",
        "risk_factor": "Áp lực cạnh tranh từ thép giá rẻ nhập khẩu từ Trung Quốc và biến động giá than cốc/quặng sắt thế giới."
    },
    "MWG": {
        "company_name": "CTCP Đầu tư Thế Giới Di Động",
        "sector": "Bán lẻ",
        "news_impact": "Chuỗi Bách Hóa Xanh chính thức đạt điểm hòa vốn và bước vào chu kỳ đóng góp lợi nhuận ròng; chính sách giảm thuế VAT 2% tiếp tục hỗ trợ kích cầu tiêu dùng nội địa.",
        "growth_driver": "Tối ưu hóa chi phí vận hành sau tái cấu trúc mạng lưới cửa hàng Thế Giới Di Động & Điện Máy Xanh; biên lợi nhuận cải thiện rõ nét.",
        "risk_factor": "Sức mua của người tiêu dùng đối với các mặt hàng điện thoại, điện máy cao cấp chưa phục hồi hoàn toàn."
    },
    "ACB": {
        "company_name": "Ngân hàng TMCP Á Châu",
        "sector": "Ngân hàng",
        "news_impact": "Tăng trưởng tín dụng tập trung nhóm khách hàng cá nhân và SME lành mạnh; chất lượng tài sản thuộc top đầu không vướng nợ xấu trái phiếu doanh nghiệp.",
        "growth_driver": "Quản trị rủi ro khắt khe, tỷ lệ nợ xấu luôn duy trì thấp nhất toàn ngành, sinh lời ROE cao và ổn định trên 22%.",
        "risk_factor": "Tăng trưởng tín dụng thận trọng có thể làm chậm nhịp mở rộng thị phần trong giai đoạn thị trường bứt phá."
    },
    "MBB": {
        "company_name": "Ngân hàng TMCP Quân đội",
        "sector": "Ngân hàng",
        "news_impact": "Tiếp tục dẫn đầu hệ thống về quy mô người dùng số (hơn 25 triệu tài khoản) và tỷ lệ tiền gửi CASA cao, tham gia tái cơ cấu ngân hàng thương mại yếu kém để nhận hạn mức tín dụng cao hơn.",
        "growth_driver": "Lợi thế chi phí vốn rẻ vượt trội, tệp khách hàng quân đội và doanh nghiệp vừa & nhỏ trung thành, động lực từ các công ty con (MBS, MIC, MB Ageas).",
        "risk_factor": "Áp lực quản trị chất lượng nợ từ phân khúc tài chính tiêu dùng MCredit."
    },
    "CTG": {
        "company_name": "Ngân hàng TMCP Công Thương Việt Nam",
        "sector": "Ngân hàng",
        "news_impact": "Tín dụng tăng trưởng mạnh trong các ngành sản xuất kinh doanh ưu tiên; tỷ lệ bao phủ nợ xấu duy trì ở mức an toàn cao trên 160%.",
        "growth_driver": "Lợi thế mạng lưới chi nhánh rộng khắp cả nước, dòng tiền gửi dồi dào từ các tập đoàn nhà nước và doanh nghiệp FDI.",
        "risk_factor": "Áp lực tăng vốn cấp 1 để đáp ứng chuẩn an toàn vốn Basel III."
    },
    "BID": {
        "company_name": "Ngân hàng TMCP Đầu tư và Phát triển Việt Nam",
        "sector": "Ngân hàng",
        "news_impact": "Dẫn đầu quy mô tổng tài sản toàn hệ thống ngân hàng Việt Nam; kế hoạch phát hành riêng lẻ cho nhà đầu tư ngoại tiếp tục là chất xúc tác lớn.",
        "growth_driver": "Dòng vốn tín dụng phục vụ các dự án trọng điểm quốc gia, chi phí trích lập dự phòng giảm dần mở rộng biên lợi nhuận trước thuế.",
        "risk_factor": "Biên lãi ròng (NIM) chịu áp lực thu hẹp do phải triển khai các gói tín dụng hỗ trợ lãi suất cho doanh nghiệp."
    },
    "HDB": {
        "company_name": "Ngân hàng TMCP Phát triển TP.HCM",
        "sector": "Ngân hàng",
        "news_impact": "Được cấp hạn mức tín dụng cao nhờ tham gia tái cơ cấu tổ chức tín dụng; chính sách chia cổ tức đều đặn bằng tiền mặt và cổ phiếu trên 25%.",
        "growth_driver": "Khai thác tối đa hệ sinh thái hàng không Vietjet và chuỗi giá trị nông nghiệp, nông thôn tại các tỉnh phía Nam.",
        "risk_factor": "Tỷ trọng tín dụng tập trung vào mảng tài trợ chuỗi cần kiểm soát chặt chẽ rủi ro thanh khoản."
    },
    "MSN": {
        "company_name": "CTCP Tập đoàn Masan",
        "sector": "Tiêu dùng & Bán lẻ",
        "news_impact": "Quỹ ngoại Bain Capital giải ngân vốn đầu tư; chuỗi siêu thị WinCommerce duy trì chuỗi tăng trưởng doanh số trên từng cửa hàng (LFL).",
        "growth_driver": "Giảm áp lực chi phí lãi vay sau khi tái cơ cấu dòng vốn; mảng chế biến thịt MEATLife và Masan High-Tech Materials hưởng lợi từ chu kỳ giá vonfram.",
        "risk_factor": "Đòn bẩy tài chính còn ở mức khá cao so với mặt bằng các doanh nghiệp sản xuất tiêu dùng."
    },
    "SSI": {
        "company_name": "CTCP Chứng khoán SSI",
        "sector": "Chứng khoán & Tài chính",
        "news_impact": "Tiến trình tháo gỡ nút thắt ký quỹ Non-margin (pre-funding) và triển khai hệ thống giao dịch KRX, kỳ vọng nâng hạng thị trường Việt Nam lên FTSE Emerging.",
        "growth_driver": "Thị phần môi giới top đầu và quy mô vốn chủ sở hữu lớn nhất ngành chứng khoán, hưởng lợi trực tiếp từ thanh khoản thị trường tăng vọt.",
        "risk_factor": "Biến động thị trường cổ phiếu ngắn hạn ảnh hưởng trực tiếp đến danh mục tự doanh FVTPL."
    },
    "VHM": {
        "company_name": "CTCP Vinhomes",
        "sector": "Bất động sản",
        "news_impact": "Luật Đất đai, Luật Nhà ở và Luật Kinh doanh BĐS mới có hiệu lực hỗ trợ pháp lý các đại dự án; doanh số mở bán các phân khu tại Ocean Park 2, 3 và Royal Island ghi nhận tích cực.",
        "growth_driver": "Quỹ đất sạch khổng lồ, năng lực triển khai dự án thần tốc và dòng tiền mặt dồi dào từ hoạt động chuyển nhượng lô lớn cho đối tác quốc tế.",
        "risk_factor": "Áp lực nghĩa vụ bảo lãnh và hỗ trợ vốn cho các dự án trong hệ sinh thái Vingroup."
    },
    "VIC": {
        "company_name": "Tập đoàn Vingroup",
        "sector": "Đa ngành & Xe điện",
        "news_impact": "VinFast mở rộng mạng lưới phân phối xe điện tại các thị trường Đông Nam Á (Indonesia, Philippines, Ấn Độ) và mạng lưới trạm sạc V-GREEN tăng tốc phủ sóng.",
        "growth_driver": "Mảng bất động sản Vinhomes và du lịch nghỉ dưỡng Vinpearl tiếp tục là trụ cột dòng tiền ổn định hỗ trợ quá trình mở rộng mảng xe điện toàn cầu.",
        "risk_factor": "Nhu cầu vốn đầu tư lớn cho VinFast và áp lực nợ vay trong bối cảnh mặt bằng lãi suất quốc tế còn neo cao."
    },
    "VRE": {
        "company_name": "CTCP Vincom Retail",
        "sector": "Bất động sản bán lẻ",
        "news_impact": "Tỷ lệ lấp đầy các trung tâm thương mại Vincom Mega Mall và Center duy trì trên 85%; mở mới các TTM tại các đại đô thị đông dân cư.",
        "growth_driver": "Dòng tiền cho thuê ổn định và dài hạn từ các thương hiệu bán lẻ quốc tế (Uniqlo, Zara, H&M) và chuỗi F&B hàng đầu.",
        "risk_factor": "Xu hướng mua sắm thương mại điện tử trực tuyến cạnh tranh một phần lượng khách đến trung tâm thương mại truyền thống."
    },
    "GAS": {
        "company_name": "Tổng Công ty Khí Việt Nam",
        "sector": "Dầu khí & Tiện ích",
        "news_impact": "Giá dầu Brent duy trì trên 75 USD/thùng do rủi ro xung đột Trung Đông; chuỗi dự án Khí Điện Lô B - Ô Môn đẩy nhanh tiến độ triển khai.",
        "growth_driver": "Độc quyền phân phối khí tự nhiên và LNG nhập khẩu phục vụ các nhà máy điện khí theo Quy hoạch điện 8; lượng tiền mặt gửi ngân hàng dồi dào trên 30.000 tỷ đồng.",
        "risk_factor": "Sản lượng khí từ các mỏ truyền thống suy giảm cần vốn đầu tư lớn vào các mỏ mới."
    },
    "PLX": {
        "company_name": "Tập đoàn Xăng Dầu Việt Nam",
        "sector": "Năng lượng & Xăng dầu",
        "news_impact": "Chính phủ áp dụng cơ chế điều chỉnh giá xăng dầu 7 ngày/lần giúp hạn chế rủi ro trích lập giảm giá hàng tồn kho; sản lượng tiêu thụ xăng dầu tăng trưởng theo GDP.",
        "growth_driver": "Nắm giữ trên 50% thị phần phân phối xăng dầu toàn quốc với hơn 5.500 cây xăng tại các vị trí đắc địa nhất cả nước.",
        "risk_factor": "Biến động mạnh của giá dầu thô thế giới ảnh hưởng đến biên lợi nhuận gộp trong các chu kỳ điều hành giá."
    },
    "POW": {
        "company_name": "Tổng Công ty Điện lực Dầu khí Việt Nam",
        "sector": "Năng lượng điện",
        "news_impact": "Nhu cầu tiêu thụ điện năng phục vụ sản xuất công nghiệp và sinh hoạt tăng cao; tiến độ dự án điện khí Nhơn Trạch 3 & 4 sắp hoàn tất đóng điện.",
        "growth_driver": "Cơ cấu nguồn điện đa dạng (điện khí, thủy điện, điện than); dự án LNG Nhơn Trạch 3 & 4 là động lực tăng trưởng doanh thu chính giai đoạn 2025-2027.",
        "risk_factor": "Thiếu hụt nguồn khí tự nhiên đầu vào làm giảm sản lượng huy động của các nhà máy điện khí Cà Mau và Nhơn Trạch."
    },
    "SAB": {
        "company_name": "Tổng CTCP Bia - Rượu - Nước giải khát Sài Gòn",
        "sector": "Đồ uống & Tiêu dùng",
        "news_impact": "Tối ưu hóa hệ thống phân phối và bao bì sản phẩm; các chiến dịch tiếp thị kích cầu tiêu dùng trong các mùa lễ hội.",
        "growth_driver": "Thị phần bia số 1 phân khúc phổ thông tại Việt Nam; bảng cân đối tài chính lành mạnh với lượng tiền mặt dồi dào và không có nợ vay ròng.",
        "risk_factor": "Nghị định 100 về nồng độ cồn và đề xuất tăng thuế tiêu thụ đặc biệt đối với đồ uống có cồn tác động lên sản lượng tiêu thụ."
    },
    "VNM": {
        "company_name": "Công ty Cổ phần Sữa Việt Nam",
        "sector": "Thực phẩm & Tiêu dùng",
        "news_impact": "Chiến lược tái định vị thương hiệu thu hút thế hệ tiêu dùng trẻ; giá sữa bột nguyên liệu thế giới duy trì vùng thấp hỗ trợ mở rộng biên lãi gộp.",
        "growth_driver": "Doanh thu xuất khẩu sang thị trường Trung Đông và châu Á tăng trưởng tích cực; dòng tiền hoạt động kinh doanh cực kỳ ổn định và tỷ lệ trả cổ tức tiền mặt cao.",
        "risk_factor": "Thị trường sữa nội địa đã bước vào giai đoạn bão hòa, áp lực cạnh tranh gia tăng từ các dòng sữa hạt và sản phẩm nhập khẩu."
    },
    "VJC": {
        "company_name": "Công ty Cổ phần Hàng không VietJet",
        "sector": "Hàng không",
        "news_impact": "Lượng khách du lịch quốc tế đến Việt Nam hồi phục mạnh mẽ; mở mới các đường bay thẳng kết nối Việt Nam với các thành phố lớn tại Ấn Độ, Trung Quốc và Úc.",
        "growth_driver": "Mô hình hàng không chi phí thấp (LCC) linh hoạt, tăng cường doanh thu phụ trợ (ancillary) có biên lợi nhuận cao, mở rộng đội tàu bay Airbus thế hệ mới.",
        "risk_factor": "Biến động giá nhiên liệu bay Jet A1 và biến động tỷ giá USD/VND do các khoản vay thuê mua máy bay."
    },
    "GVR": {
        "company_name": "Tập đoàn Công nghiệp Cao su Việt Nam",
        "sector": "Cao su & Bất động sản KCN",
        "news_impact": "Giá cao su tự nhiên thế giới tăng mạnh do nguồn cung thắt chặt; đẩy mạnh tiến độ chuyển đổi đất cao su sang phát triển các khu công nghiệp trọng điểm.",
        "growth_driver": "Quỹ đất cao su chuyển đổi lên đến hàng chục nghìn hecta tại Bình Dương, Đồng Nai, Tây Ninh đón làn sóng dịch chuyển chuỗi cung ứng FDI.",
        "risk_factor": "Thủ tục pháp lý phê duyệt quy hoạch và tiền chuyển đổi mục đích sử dụng đất mất nhiều thời gian."
    },
    "BCM": {
        "company_name": "Tổng Công ty Đầu tư và Phát triển Công nghiệp",
        "sector": "Bất động sản KCN",
        "news_impact": "Dòng vốn FDI giải ngân vào Việt Nam tiếp tục lập kỷ lục mới; các khu công nghiệp VSIP và Bàu Bàng thu hút các tập đoàn công nghệ cao như Lego, Pandora.",
        "growth_driver": "Vị thế số 1 về phát triển hạ tầng khu công nghiệp tại vùng kinh tế trọng điểm Đông Nam Bộ, quỹ đất sẵn sàng cho thuê lớn nhất cả nước.",
        "risk_factor": "Đòn bẩy tài chính và áp lực chi phí lãi vay để đầu tư hạ tầng các dự án quy mô lớn."
    },
    "STB": {
        "company_name": "Ngân hàng TMCP Sài Gòn Thương Tín",
        "sector": "Ngân hàng",
        "news_impact": "Giai đoạn cuối của đề án tái cơ cấu ngân hàng; chuẩn bị đấu giá thu hồi nợ xấu tại Khu công nghiệp Phong Phú và khoản cổ phần VAMC.",
        "growth_driver": "Sau khi hoàn tất xử lý xong toàn bộ nợ xấu VAMC, ngân hàng sẽ được NHNN phê duyệt kế hoạch tăng vốn và chia cổ tức sau nhiều năm dồn lực trích lập dự phòng.",
        "risk_factor": "Tiến độ đấu giá tài sản bảo đảm phụ thuộc vào điều kiện pháp lý và thanh khoản của thị trường bất động sản."
    },
    "TPB": {
        "company_name": "Ngân hàng TMCP Tiên Phong",
        "sector": "Ngân hàng",
        "news_impact": "Tiếp tục dẫn đầu về mô hình ngân hàng tự động LiveBank 24/7; chi phí trích lập dự phòng rủi ro nợ xấu có xu hướng tạo đỉnh và giảm dần.",
        "growth_driver": "Tối ưu hóa chi phí vận hành (CIR) thấp nhờ tỷ lệ số hóa giao dịch đạt trên 90%, đẩy mạnh mảng cho vay mua ô tô và tiêu dùng cá nhân.",
        "risk_factor": "Tỷ lệ nợ xấu nhóm khách hàng cá nhân nhạy cảm với sự phục hồi của nền kinh tế."
    },
    "VIB": {
        "company_name": "Ngân hàng TMCP Quốc tế Việt Nam",
        "sector": "Ngân hàng",
        "news_impact": "Duy trì vị thế số 1 về thị phần cho vay mua ô tô và phát hành thẻ tín dụng; chính sách chia cổ tức tiền mặt đều đặn hấp dẫn nhà đầu tư.",
        "growth_driver": "Tập trung 100% vào phân khúc bán lẻ có biên lãi ròng (NIM) cao; khả năng kiểm soát chi phí vận hành và quản lý danh mục qua nền tảng số.",
        "risk_factor": "Độ nhạy cảm với mặt bằng lãi suất cho vay tiêu dùng và mức độ hồi phục của thị trường ô tô trong nước."
    },
    "VPB": {
        "company_name": "Ngân hàng TMCP Việt Nam Thịnh Vượng",
        "sector": "Ngân hàng",
        "news_impact": "Hoàn tất thương vụ bán 15% cổ phần cho đối tác chiến lược SMBC (Nhật Bản) nâng vốn chủ sở hữu lên vị trí top 2 toàn hệ thống; mảng tài chính tiêu dùng FE Credit tái cấu trúc thành công.",
        "growth_driver": "Bộ đệm vốn dày bậc nhất ngành ngân hàng cho phép mở rộng quy mô tín dụng tốc độ cao, hỗ trợ mở rộng cho vay khách hàng FDI và doanh nghiệp lớn.",
        "risk_factor": "Chi phí trích lập dự phòng và nợ xấu từ danh mục cho vay tín chấp FE Credit cần thêm thời gian để trở lại mức bình thường."
    },
    "SHB": {
        "company_name": "Ngân hàng TMCP Sài Gòn - Hà Nội",
        "sector": "Ngân hàng",
        "news_impact": "Hoàn tất chuyển nhượng vốn công ty tài chính SHB Finance cho đối tác Krungsri (Thái Lan); chi trả cổ tức bằng tiền mặt và cổ phiếu tỷ lệ 16%.",
        "growth_driver": "Mở rộng tài trợ các dự án năng lượng tái tạo và chuỗi sản xuất nông nghiệp công nghệ cao; định giá P/B đang ở vùng thấp so với mặt bằng trung bình ngành.",
        "risk_factor": "Tỷ trọng cho vay các dự án năng lượng và bất động sản đòi hỏi năng lực thẩm định rủi ro chặt chẽ."
    },
    "SSB": {
        "company_name": "Ngân hàng TMCP Đông Nam Á",
        "sector": "Ngân hàng",
        "news_impact": "Nhận được các khoản tài trợ vốn và tín dụng xanh dài hạn từ các tổ chức tài chính quốc tế (IFC, DFC); hoàn tất phát hành cổ phiếu riêng lẻ củng cố vốn cấp 1.",
        "growth_driver": "Tập trung chiến lược phát triển tài chính bền vững, tín dụng xanh cho các doanh nghiệp vừa và nhỏ do phụ nữ làm chủ.",
        "risk_factor": "Thanh khoản giao dịch cổ phiếu trên sàn còn tương đối cô đặc so với các ngân hàng thương mại cùng nhóm."
    },
    "BVH": {
        "company_name": "Tập đoàn Bảo Việt",
        "sector": "Bảo hiểm & Tài chính",
        "news_impact": "Doanh thu phí bảo hiểm nhân thọ và phi nhân thọ tiếp tục giữ vững thị phần số 1 toàn quốc; dòng tiền dồi dào từ danh mục tiền gửi ngân hàng và trái phiếu chính phủ.",
        "growth_driver": "Lợi thế quy mô tài sản đầu tư tài chính lớn nhất ngành bảo hiểm, được hưởng lợi trực tiếp khi mặt bằng lãi suất tiền gửi và lợi suất trái phiếu chính phủ tạo đáy phục hồi.",
        "risk_factor": "Tăng trưởng doanh thu khai thác mới của kênh bảo hiểm qua ngân hàng (Bancassurance) chịu sự kiểm soát chặt chẽ hơn từ Luật Kinh doanh Bảo hiểm sửa đổi."
    }
}


def generate_ticker_reasoning(ticker: str, analysis: dict) -> dict:
    """
    Sinh lý do khuyến nghị chi tiết, tin tức tác động, và động lực tăng giá
    dựa trên các tham số định lượng thực tế của cổ phiếu.
    """
    ticker_upper = ticker.upper()
    profile = VN30_PROFILES.get(ticker_upper, {
        "company_name": f"Công ty Cổ phần {ticker_upper}",
        "sector": "Doanh nghiệp rổ VN30",
        "news_impact": "Chịu tác động bởi chính sách vĩ mô, lãi suất và biến động dòng vốn cơ cấu quỹ ETF rổ VN30.",
        "growth_driver": "Vị thế doanh nghiệp đầu ngành và thanh khoản top đầu thị trường.",
        "risk_factor": "Áp lực điều chỉnh theo chỉ số chung VN-INDEX."
    })

    signal = analysis.get("signal", "QUAN SÁT / NẮM GIỮ")
    total_score = analysis.get("total_score", 50.0)
    trend_score = analysis.get("trend_score", 50.0)
    flow_score = analysis.get("flow_score", 50.0)
    rsi = analysis.get("rsi", 50.0)
    vol_vs_ma20 = analysis.get("vol_vs_ma20", 1.0)
    ml_prob_up = analysis.get("ml_prob_up", 50.0)
    close = analysis.get("close", 0.0)
    target_1 = analysis.get("target_1", round(close * 1.05, 2))
    target_2 = analysis.get("target_2", round(close * 1.10, 2))
    stoploss = analysis.get("stoploss", round(close * 0.95, 2))
    entry_range = analysis.get("entry_range", f"{round(close*0.99, 2)} - {round(close*1.01, 2)}")
    risk_reward = analysis.get("risk_reward_ratio", 1.8)

    # 1. Sinh lý do khuyến nghị kỹ thuật (recommendation_reason)
    if "MUA" in signal:
        if "MẠNH" in signal:
            rec_reason = (
                f"Tín hiệu MUA MẠNH bùng nổ: Tổng điểm Quant đạt rất cao ({total_score}/100), "
                f"xu hướng kỹ thuật ({trend_score}/100) vượt trội khi giá nằm trên toàn bộ các đường SMA20/50. "
                f"Động lượng RSI ({rsi}) đang trong pha tăng giá mạnh mẽ, dòng tiền gia tăng với thanh khoản gấp {vol_vs_ma20}x MA20. "
                f"Mô hình AI dự phóng xác suất tăng giá T+3 đạt {ml_prob_up}%, thích hợp mở vị thế mua chủ động quanh vùng {entry_range}."
            )
        else:
            rec_reason = (
                f"Tín hiệu MUA tích cực: Điểm Quant đạt {total_score}/100 điểm. "
                f"Giá duy trì trên hỗ trợ động SMA20, RSI ({rsi}) ở vùng tích lũy tăng trưởng, "
                f"khối lượng dòng tiền đạt {vol_vs_ma20}x MA20. Mô hình AI đánh giá xác suất tăng giá T+3 đạt {ml_prob_up}%, "
                f"cho điểm giải ngân an toàn với mục tiêu ngắn hạn tại {target_1}."
            )
        why_price_changes = (
            f"Cổ phiếu có động lực tăng giá nhờ sự đồng thuận giữa dòng tiền kỹ thuật bứt phá "
            f"và yếu tố cơ bản ngành {profile['sector']}. Tỷ lệ Lợi nhuận/Rủi ro hấp dẫn đạt {risk_reward}:1, "
            f"kỳ vọng chinh phục Target 1 tại {target_1} (+{round(((target_1/close)-1)*100, 1) if close > 0 else 5.0}%) "
            f"và Target 2 tại {target_2}."
        )
    elif "BÁN" in signal:
        if "MẠNH" in signal:
            rec_reason = (
                f"Tín hiệu BÁN MẠNH / THOÁT VỊ THẾ: Điểm Quant rơi sâu xuống mức cảnh báo ({total_score}/100), "
                f"xu hướng kỹ thuật suy yếu ({trend_score}/100) khi giá gãy các mốc hỗ trợ quan trọng. "
                f"Chỉ số RSI ({rsi}) suy giảm và AI cảnh báo xác suất giảm giá ngắn hạn (khả năng tăng chỉ {ml_prob_up}%). "
                f"Khuyến nghị nhà đầu tư quyết liệt cắt lỗ hoặc hạ toàn bộ tỷ trọng margin tại {stoploss} để bảo toàn vốn."
            )
        else:
            rec_reason = (
                f"Tín hiệu BÁN / HẠ TỶ TRỌNG: Điểm tổng hợp đạt {total_score}/100. "
                f"Áp lực điều chỉnh ngắn hạn xuất hiện khi chỉ báo RSI ({rsi}) suy yếu hoặc phân kỳ âm, "
                f"dòng tiền ({flow_score}/100) chưa có sự hỗ trợ của lực cầu bắt đáy. "
                f"Khuyến nghị hạ tỷ trọng cổ phiếu về mức an toàn, đặt điểm chặn lỗ nghiêm ngặt tại {stoploss}."
            )
        why_price_changes = (
            f"Áp lực giảm giá bắt nguồn từ sự suy yếu của lực cầu và động thái chốt lời ngắn hạn. "
            f"Cần thận trọng trước ngưỡng kháng cự trên và nguy cơ cổ phiếu lùi về kiểm định đáy cũ quanh {stoploss}."
        )
    else:  # THEO DÕI / NẮM GIỮ
        rec_reason = (
            f"Khuyến nghị THEO DÕI / NẮM GIỮ: Điểm kỹ thuật đạt {total_score}/100. "
            f"Cổ phiếu đang trong pha tích lũy siết nền biên độ hẹp quanh {close}, RSI ({rsi}) ở trạng thái trung tính. "
            f"Xác suất AI T+3 ({ml_prob_up}%) chưa phát tín hiệu bứt phá rõ rệt. "
            f"Nhà đầu tư nên tiếp tục nắm giữ vị thế hiện có, kiên nhẫn quan sát vùng hỗ trợ {analysis.get('support_1', round(close*0.97, 2))} "
            f"và chờ dòng tiền xác nhận vượt cản {analysis.get('resistance_1', round(close*1.03, 2))} trước khi gia tăng tỷ trọng."
        )
        why_price_changes = (
            f"Biến động giá hiện tại mang tính chất tích lũy đi ngang và phân hóa theo thị trường chung. "
            f"Khi có tin tức hỗ trợ và dòng tiền tổ chức kích hoạt, cổ phiếu có tiềm năng bứt phá hướng tới mục tiêu {target_1}."
        )

    return {
        "company_name": profile["company_name"],
        "sector": profile["sector"],
        "recommendation_reason": rec_reason,
        "news_impact": profile["news_impact"],
        "why_price_changes": why_price_changes,
        "growth_driver": profile["growth_driver"],
        "risk_factor": profile["risk_factor"],
        "target_1_pct": round(((target_1 / close) - 1.0) * 100.0, 1) if close > 0 else 5.0,
        "stoploss_pct": round(((stoploss / close) - 1.0) * 100.0, 1) if close > 0 else -3.0,
    }
