# SL09–11 — Triển khai HRM theo giai đoạn

Nguồn chuẩn: [Master1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md#module-m22); bản đọc [M22](../modules/M22-HUMAN-RESOURCES.md). Không có code/DDL/UAT đã chạy. HRM đã được chấp thuận tích hợp vào tài liệu; các gate dưới là điều kiện triển khai, không yêu cầu duyệt lại quyết định phạm vi.

## SL09 / HR-A — Thay Excel ở hồ sơ, phép và công cơ bản

Features: M22-F01–08, F11, F13, F21–28 ở phần A. Chưa enable payroll, ca nâng cao, device hoặc bank. M14 authority/identity, M16 checklist, M19 outbox/import và M20 privacy cần có controls phù hợp; không đòi tất cả module CRM hoàn thiện trước pilot.

Demo end-to-end: dry-run Excel → HR đối soát/commit → activate nhân viên/hợp đồng → nhân viên xin phép → manager duyệt → công nhập file/sửa công có duyệt → khóa công/xuất → offboard kiểm bàn giao và revoke. Hồ sơ, phép và công là nguồn chuẩn sau cutover; payroll tiếp tục công cụ hiện tại đến HR-C.

Test bắt buộc: H-T01–14, H-T19–20, H-T23, H-T39–48 theo capability A. H-T24 kiểm chống sửa kỳ đã có consumer khóa bằng contract fixture; H-T35 kiểm quyền tài liệu/self-service bằng fixture, chưa tuyên bố payroll chạy. H-T48 chạy các phần queue/restore/load có trong profile. Controls theo H-NFR luôn áp dụng đúng phạm vi.

Exit: HR/data owner/approver/backup được chỉ định; H-O đầu vào A đã chốt; Excel đối soát không có sai lệch chưa giải thích; quyền/API/file/export được kiểm; lịch/phép được duyệt; backup/restore và rollback diễn tập; HR/QA/IT sign-off có evidence. Chưa có file thật thì migration vẫn Not Run, không đánh dấu hoàn thành bằng fixture.

## SL10 / HR-B — Công nâng cao

Thêm M22-F09–10/F12 và F28 adapter khi có. Test thêm H-T15–18/H-T21–22; regression F05–08/F11/F13 và quyền/ledger. Các ca kiểm thiết bị không áp dụng chỉ khi release profile ghi rõ không bật connector, có owner và lý do; không biến thành Pass. Mục tiêu demo ca đêm → log offline gửi bù → sửa/OT duyệt → đối soát khóa công. Không dùng log thô làm công tính lương.

## SL11 / HR-C — Payroll có kiểm soát

Thêm M22-F14–20 và mở rộng F24–28; H-T24–38 cùng H-T43–48 và regression công/leave/M10. Chọn INTERNAL hoặc EXTERNAL theo pháp nhân/kỳ. EXTERNAL kiểm mapping/output/reconcile của engine ngoài bằng chứng thực tế, không yêu cầu xây engine nội bộ cho đủ checklist.

Demo: công Locked + policy effective → calculate hoặc import approved external run → review/approve/lock → publish payslip → claim commission route → file chi được duyệt → evidence từng dòng → reconcile, kèm partial/unknown/refund/adjustment. Chạy song song tối thiểu hai kỳ, chỉ một nguồn thực hiện chi. Bank API là capability riêng; file route vẫn phải kiểm double payout và trạng thái unknown/manual reconciliation.

Exit: policy/chuyên môn payroll được xác nhận; không còn chênh lệch đối chiếu chưa xử lý; M10 reservation/settlement và phân tách maker/checker đạt; bank identity và amount checksum kiểm; ownership hỗ trợ kỳ đầu rõ. Các tham số pháp lý không được suy từ tài liệu nguồn cũ hoặc ảnh.

## Cấu hình release và bằng chứng

Release manifest phải liệt kê từng H-T01–48 với Pass/Fail/Not Run/Blocked/N/A, phần fixture/live, actor/scope, policy version và evidence. N/A có applicability false/lý do/owner; controls tiền/quyền không được miễn chỉ vì phần khác chưa bật. Trạng thái mặc định hiện tại toàn bộ Not Run.

Các bước rollback: dừng writer/import/export mới; ghi nhận command đang chạy; reconcile hiệu ứng đã xảy ra; restore chỉ theo runbook giữ external payment evidence; batch có downstream dùng compensating correction. Không restore DB để giả giao dịch ngân hàng chưa xảy ra. Đào tạo HR, manager, employee và finance theo màn hình/quy trình trước enable profile tương ứng.
