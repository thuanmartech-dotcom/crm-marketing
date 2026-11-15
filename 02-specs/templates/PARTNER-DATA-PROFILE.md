# Phiếu cấu hình chia sẻ dữ liệu đối tác — M21

Mẫu nghiệp vụ để hai bên xác nhận phạm vi, không thay hợp đồng hoặc biểu mẫu pháp lý được phê duyệt. Các trường có thể áp dụng tùy NONE/SUMMARY/FILE/API_READ; không yêu cầu đối tác mở toàn bộ tài khoản.

| Hạng mục | Nội dung điền / nguyên tắc |
|---|---|
| Đối tác / Account / workspace | ID nội bộ và chủ thể; bridge được cấp phép |
| Shop và kênh | Shop ID, provider/product, ai xác nhận sở hữu; không chỉ tên hiển thị |
| Mục tiêu sử dụng | Quyết định dịch vụ/báo cáo cần hỗ trợ |
| Chế độ chia sẻ | NONE / SUMMARY / FILE / API_READ; nguồn fallback nào được phép |
| Kỳ và lịch | Timezone, cutoff, lịch cung cấp, nguồn ngày tạo/giao/hoàn/settlement |
| Chỉ số | Metric code/version, unit, currency, numerator/denominator, refund/tax/ship treatment |
| Phạm vi dữ liệu | Aggregate hay order detail; trường bị cấm/PII không cần lấy |
| Phân quyền | Người cung cấp, importer, reviewer, report approver; người được xem report/detail/export |
| Xác nhận số liệu | Partner-reported hay reconciled; evidence và người có authority |
| Nguồn chuẩn | Precedence và cách xử lý file/API overlap; không cộng nguồn trùng |
| Hiệu lực / thu hồi | Ngày bắt đầu/kết thúc, người có quyền revoke, cách dừng access/job |
| Retention / hold | Policy version cho raw/staged/aggregate/report/audit và cleanup |
| Khi thiếu dữ liệu | Báo unavailable/partial/stale; chỉ số nào không thể xác minh; phần dịch vụ nào vẫn báo cáo được |
| Ngoại lệ | Ai nhận task, threshold, hạn, evidence để đóng case |
| API nếu có | App/account/scopes, operation read allowlist, quota/capability test; không ghi secret vào phiếu |
| Phê duyệt | Actor/authority/time/version/hash/evidence; sửa phải revision mới |

Trước publish một report, người duyệt kiểm audience, scope, source versions, as-of, uncertainty và quyền hiện hành. Đối tác NONE vẫn có thể duyệt báo cáo tiến độ/công việc; không ép điền metric values hoặc credential để hoàn tất phiếu.
