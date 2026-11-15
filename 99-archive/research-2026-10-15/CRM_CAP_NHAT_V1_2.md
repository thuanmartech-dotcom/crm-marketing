# Bản ghi cập nhật tài liệu CRM phiên bản 1.2

Ngày cập nhật: 15/10/2026.

Tài liệu hệ thống đầy đủ: [CRM_MASTER_BRD_SRS_HOP_NHAT.md](./CRM_MASTER_BRD_SRS_HOP_NHAT.md).

## Phạm vi doanh nghiệp

- Ngành khởi đầu: dịch vụ marketing, phục vụ B2B và B2C.
- Vận hành cá nhân trước, thiết kế để mở rộng đến 30 Sales, 10 Marketing, ban giám đốc và 2 chi nhánh.
- Dữ liệu đầu vào: khoảng 100 lead và 50 khách hàng mỗi tháng, có thể tăng. Ý nghĩa “50 khách hàng/tháng” cần xác nhận trước khi tính conversion hoặc ROI.
- Lõi dùng chung và gói ngành độc lập để mở rộng sang ngành khác, hạn chế xung đột dữ liệu, quyền và nghiệp vụ.

## Nội dung đã hoàn tất

Tài liệu hợp nhất phiên bản 1.2 gồm 10 chương, 75 bảng và 22 luồng nghiệp vụ. Nội dung bổ sung:

1. Kiến trúc Omnichannel hợp nhất Zalo, Facebook, TikTok, Web Form và Email: hồ sơ khách hàng, inbox tập trung, phân công, SLA, chống trùng và phục hồi đồng bộ.
2. Đối chiếu 9 sản phẩm/nền tảng: Twenty, EspoCRM, Frappe CRM, Odoo, SuiteCRM, Chatwoot, Salesforce, HubSpot và Microsoft Dynamics/Dataverse. Phụ lục D có nguồn chính thức, phần nên áp dụng và rủi ro theo bối cảnh.
3. Cấu trúc code đề xuất, ranh giới module, hợp đồng adapter và cơ chế gói ngành có namespace, dependency và migration riêng.
4. Bổ sung FR30–40, UC17–22, 15 bảng dữ liệu Omnichannel và 24 ca UAT OC01–24.
5. Bổ sung phân quyền inbox, bảo vệ dữ liệu, chỉ số vận hành, dashboard, lộ trình triển khai và mô hình TCO có giả định rõ ràng.

## Quyết định cốt lõi

- Một hồ sơ khách hàng có thể liên kết nhiều danh tính kênh và nhiều cuộc hội thoại; không trộn mọi thread thành một luồng gửi chung.
- Phân vùng tenant/workspace và kiểm tra quyền tại API, tìm kiếm, attachment, export và AI retrieval.
- Không tự gộp khách chỉ vì trùng tên, ảnh hoặc email chưa xác minh; merge cần bằng chứng, audit và khả năng xử lý hoàn tác.
- Tiếp nhận sự kiện bền vững trước ACK; xử lý idempotent; gửi qua outbox và kiểm tra chính sách tại thời điểm gửi.
- Timeout gửi chưa rõ kết quả phải được đối soát, không tự retry mù gây gửi trùng.
- Autoack không được tính là phản hồi người thật để hoàn thành SLA.
- Ưu tiên modular monolith và gói ngành; chỉ tách microservices khi có bằng chứng về tải, cô lập hoặc tổ chức đội ngũ.
- Lựa chọn nền tảng cụ thể sau PoC với cùng bộ kiểm thử, chưa chọn chỉ từ danh sách tính năng.

## Giới hạn đã ghi nhận

“Hợp nhất toàn bộ” giới hạn trong dữ liệu được tài khoản doanh nghiệp ủy quyền, API cung cấp và chính sách lưu giữ cho phép. Không cam kết lịch sử vô hạn hoặc truy cập tin nhắn cá nhân ngoài quyền được cấp.

TikTok có Business Messaging API cho tài khoản đủ điều kiện; chưa xác minh quyền sử dụng của tài khoản doanh nghiệp này. Zalo cá nhân không được coi là tương đương Zalo OA API. Mỗi connector cần công bố khả năng đã kiểm chứng, khoảng lịch sử và phần dữ liệu còn thiếu.

Nghiên cứu dựa trên tài liệu chính thức và một số tệp mã nguồn/manifest công khai, chưa phải đánh giá toàn bộ codebase, benchmark hoặc PoC chạy với tài khoản thực tế. Các chi phí và ngưỡng hiệu năng là giả định/mục tiêu thiết kế, không phải báo giá hoặc kết quả đã đạt.

Ba agent được khởi chạy song song nhưng dừng do giới hạn sử dụng; không có kết quả agent được sử dụng. Công việc nghiên cứu và hợp nhất được tiếp tục trực tiếp.

## Kiểm tra tài liệu

Đã kiểm tra cấu trúc 10 chương, bảng Markdown, liên kết nội bộ, các mã yêu cầu/luồng/UAT bổ sung và sự hiện diện của nguồn nghiên cứu. Kết quả kiểm tra không có lỗi; 7 tệp nguồn đã rà soát giữ nguyên.

- Kết quả kiểm tra: [working/validation.json](./working/validation.json).
- Script tạo tài liệu: [build_crm_master.py](./build_crm_master.py).
- Nội dung cập nhật nghiên cứu: [working/research_updates.py](./working/research_updates.py).

Kiểm tra trên xác nhận cấu trúc tài liệu, không thay thế nghiệm thu hệ thống CRM đã triển khai.
