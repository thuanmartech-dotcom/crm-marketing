# Báo cáo tích hợp quản trị nhân sự — 18/10/2026

Đã nâng [Master lên1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md#module-m22), bổ sung M22 theo yêu cầu chủ dự án: công ty đang quản lý nhân sự bằng Excel và muốn chuyển vào cùng hệ thống CRM. Bản1.8 được lưu nguyên trạng tại archive trước sửa.

## Nội dung đã hoàn thành

- 28 chức năng có đầu vào, quy tắc, đầu ra, ngoại lệ và truy vết nghiệm thu.
- 16 luồng nghiệp vụ; 24 quy tắc; 48 tình huống UAT; 8 yêu cầu phi chức năng; 10 nhóm tham số cần xác nhận khi triển khai.
- Hồ sơ/hợp đồng/chứng chỉ; cơ cấu và điều chuyển; phép/ca/công/tăng ca; tự phục vụ; onboarding/offboarding; tài sản/thưởng/kỷ luật; payroll/thuế/bảo hiểm/tạm ứng; hoa hồng; phiếu lương/khiếu nại; chi và đối soát; báo cáo/bảo mật/migration.
- Tích hợp vào thân các chương3–9 và A.9; cập nhật danh mục22module, phiên bản, navigation, lộ trình, ownership, gap log, manifest, invariants và registry có hash nguồn.
- Bản đọc riêng [M22](../../02-specs/modules/M22-HUMAN-RESOURCES.md) và [SL09–11](../../02-specs/slices/SL09-11-HRM.md) để triển khai thuận tiện; Master vẫn là nguồn chuẩn.

## Quyết định thiết kế chính

HR-A trước: hồ sơ/hợp đồng/phép/công cơ bản/tự phục vụ/bàn giao và chuyển Excel. HR-B thêm ca/tăng ca/thiết bị nếu có. HR-C triển khai payroll nội bộ hoặc tích hợp phần mềm ngoài sau khi chính sách và công đã ổn định; đối chiếu tối thiểu hai kỳ trước vận hành chính thức. Bank API là capability riêng sau file chi có duyệt.

M14 giữ authority; M10 giữ quyền hưởng hoa hồng; M22 không dựng bộ quyền/hoa hồng thứ hai. Một nguồn chi cho mỗi khoản; bảng lương/file xuất không tự được coi đã thanh toán. Hồ sơ nhạy cảm tách quyền khỏi CRM và AI tìm kiếm chung.

Excel chuyển qua inventory → mapping → dry-run → đối soát → phê duyệt → cutover → kiểm sau/rollback có điều kiện. Chưa nhận file thật nên chưa khẳng định dữ liệu sạch hoặc đã nhập.

## Kiểm tra và giới hạn

Đã chạy builder inventory, kiểm package và kiểm riêng HRM: mã yêu cầu được định nghĩa, liên kết/truy vết tồn tại, mỗi chức năng nối UC/rule/test, đủ48ca được bao phủ, module dẫn xuất khớp nội dung Master và checksum baseline nhất quán. Kết quả tại [bằng chứng HRM](../../03-planning/evidence/hrm-integration-validation.json) và [kiểm package](../../03-planning/evidence/package-validation.json).

Đây là hoàn thành cập nhật tài liệu BA, chưa viết ứng dụng hoặc chạy48ca UAT. Các khoảng trống registry cũ của CRM vẫn được giữ và công khai; không tuyên bố đã khắc phục toàn bộ yêu cầu cũ trong đợt HRM.

Cần thu thập khi triển khai: quy mô thật/pháp nhân, file Excel, lịch/ca/phép, người duyệt, công thức lương và hiệu lực thuế/bảo hiểm, phương án phần mềm payroll/ngân hàng, retention và ngân sách. Không bịa tỷ lệ hoặc deadline. Tuyển dụng/đào tạo/đánh giá/phúc lợi nâng cao được ghi backlog HR-D, cần đặc tả riêng trước triển khai.
