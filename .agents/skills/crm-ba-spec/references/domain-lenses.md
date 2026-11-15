# Thấu kính Câu hỏi Chuyên sâu theo 5 Cụm Nghiệp vụ (`M01–M20`)

Khi chạy Pha 2 (`Cổng hỏi ngược`) của [module-workflow.md](module-workflow.md), Agent **chỉ đọc đúng Cụm chứa module đang tách** (không đọc cả file để tiết kiệm context) và ép hỏi/kiểm tra mọi điểm chưa rõ trong Master v1.9 + [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md).

---

## Cụm 1 — Định danh, Hội thoại, Kết nối & Quyền riêng tư (`M01`, `M03`, `M19`, `M20`)

- **Ranh giới hợp nhất & nguồn ghi (`M01`):** Khi 2 hồ sơ trùng SĐT/email nhưng khác `workspace` hoặc khác `Contact_Point`, hệ thống tự động merge hay tạo `Duplicate_Candidate` chờ steward duyệt? Nếu unmerge, field nào giữ lại (`survivorship rule`)?
- **Danh tính đa lớp (`M01` vs `M21` vs `M22`):** Hồ sơ người mua sàn TMĐT (`M21`) hoặc nhân viên (`M22`) có tuyệt đối bị chặn không tự sinh `Contact/Lead` trong `M01/M02` không? (`INV-18`).
- **Độ tin cậy kênh & thứ tự sự kiện (`M03`, `M19`):** Webhook/tin nhắn đến sai thứ tự (`out-of-order`) dùng trường timestamp nào của provider để xếp lại? Cơ chế xác minh chữ ký webhook và `ACK` chỉ sau khi ghi bền inbox đã rõ chưa? (`INV-07`).
- **Gửi không rõ kết quả (`M03`, `M19`):** Khi gọi API gửi tin bị timeout sau khi provider có thể đã nhận (`Unknown send outcome`), trạng thái chuyển sang `RECONCILING` thế nào để cấm retry mù gây spam khách? (`INV-08`).
- **Mục đích, Consent & Suppression (`M20`):** Hành động gửi/sync nào bắt buộc check `Consent` + `Suppression` thời gian thực? Khi khách yêu cầu xóa/ẩn danh (`Privacy_Request`), các bảng lịch sử/audit/backup xử lý `retention` vs `legal hold` ra sao?

---

## Cụm 2 — Bán hàng, Hợp đồng, Dịch vụ & Giao việc (`M02`, `M07`, `M08`, `M11`, `M12`, `M13`, `M15`, `M16`)

- **Chuyển giao qua ranh giới (`M02 → M07 → M08 → M15/M16`):** Khi chuyển trạng thái (ví dụ `Quote Approved → Contract`, `Contract Signed → Onboarding/Project/Task`), dữ liệu nào được copy làm snapshot bất biến (`quote_revision`, `SOW version`), dữ liệu nào chỉ link ID?
- **Khóa sửa & tạo Revision (`M07`, `M08`, `M15`):** Sau khi báo giá/hợp đồng/kế hoạch IMC đã được duyệt hoặc ký, sửa đổi có bắt buộc tạo phiên bản mới (`revision`) và chạy lại ma trận thẩm quyền (`M23-F04`) không?
- **Cơ chế nhận việc & Hàng đợi (`M02`, `M11`, `M13`, `M16`):** Phân biệt `Offer` (chưa accept) vs `Assigned` vs `Queue` có manager (`INV-10`)? Nếu quá hạn SLA nhận việc hoặc trùng lịch tài nguyên (`M13`), hành động leo thang (escalation) là gì?
- **Tách bạch Hoàn thành vs Cam kết (`M11`, `M12`, `M16`):** Đã tách rõ `Task Done` ≠ `SLA fulfilled` ≠ `Client Accepted` ≠ `Paid` chưa? (`INV-05`). Đổi hạn/snooze/block có giữ nguyên lịch sử vi phạm SLA không? (`INV-12`).
- **Nghiệm thu & Reopen (`M11`, `M12`, `M16`):** Nộp kết quả có bất biến theo `submission_version/hash` không? (`INV-11`). Khi khách reject/mở lại ticket sau khi đã đóng, mở `episode` mới hay reopen bản ghi cũ?

---

## Cụm 3 — Tài chính, Hoa hồng & Ngân sách (`M09`, `M10`, `M17`)

- **Độ chính xác tiền tệ & Tỷ giá (`M09`, `M10`, `M17`):** Mọi trường tiền có dùng `Decimal` (precision/scale cụ thể) và quy tắc làm tròn (`HALF_UP` / `HALF_EVEN`) thống nhất chưa? Đa tiền tệ dùng tỷ giá snapshot tại thời điểm nào (chặn cộng gộp khác currency)?
- **Bất biến chứng từ & Bù trừ (`M09`, `M10`, `M17`):** Khi chứng từ thu (`Receipt`), phân bổ (`Allocation`), hoa hồng (`Commission`) hoặc chi phí (`Cost`) đã khóa/post, hệ thống có **cấm `DELETE/UPDATE`** và bắt buộc tạo bút toán điều chỉnh/đảo (`reversal/adjustment`) có lý do & evidence không?
- **Phân bổ nhiều phần & Đóng kỳ (`M09`, `M17`):** Một `Receipt` trả cho nhiều `Obligation` (hoặc trả từng phần, hoàn tiền một phần) xử lý thứ tự ưu tiên phân bổ thế nào? Khi kỳ kế toán đã đóng (`Period_Closed`), hành động ghi lùi ngày bị chặn ra sao?
- **Phòng chống chi trùng (`M10` vs `M22`):** Đã khóa ranh giới `M10` giữ quyền hưởng hoa hồng (`Policy snapshot`), còn `M22` chỉ nhận claim route để chi qua payroll (không chi trùng 2 nơi)? (`INV-18` / HRM invariants).
- **Tách tiền Media khách vs Doanh thu Agency (`M09`, `M17`):** Luồng tiền media thu hộ/chi hộ khách hàng có tách biệt khỏi doanh thu phí dịch vụ và bị khóa duyệt theo `Approval Matrix` (`M23-F04`) / cấm bulk-approve (`INV-25`) không?

---

## Cụm 4 — Tự động hóa, Điểm thưởng, AI & Báo cáo (`M04`, `M05`, `M06`, `M18`)

- **An toàn tự động hóa (`M04`):** Cơ chế chống bão thông báo (`rate-limit` / `frequency cap`), chặn vòng lặp vô hạn (`re-entry guard`), và tuân thủ `Quiet Hours` từ lịch chuẩn `M23-F10` (`INV-23`)? Khi dữ liệu lịch sử được import hàng loạt, có cờ tắt trigger Journey không?
- **Sổ cái điểm thưởng & Thu hồi (`M05`):** Ledger tích điểm có append-only không? Khi đơn hàng/thanh toán bị hủy hoặc hoàn tiền (`M09`), điểm đã thưởng xử lý âm điểm/thu hồi hay khóa đổi thưởng ra sao? Có kiểm chống tự giới thiệu (`self-referral`)?
- **An toàn AI & Provenance (`M06`):** AI chỉ tạo `Draft` chờ người duyệt hay được auto-send? Trước khi gửi prompt sang LLM, lớp redaction PII (`M20`) chạy ở đâu? Đã lưu đủ `model/prompt_version/source_citations/evaluation` để truy vết chưa?
- **Độ trung thực số liệu (`M18`):** Đã khóa đúng `grain`, `time basis`, `status basis` chưa? Thiếu dữ liệu phải trả `NULL / Unavailable` (tuyệt đối không fake `0` hay `0%` khi mẫu số = 0)? Report snapshot đã phát hành bất biến ra sao khi dữ liệu nguồn sửa sau? (`INV-19`, `INV-20`).

---

## Cụm 5 — Tổ chức, Quyền hạn & Cấu hình lõi (`M14` — liên thông `M23`, `M24`)

- **Phân cấp phạm vi dữ liệu (`M14`):** Quy tắc kế thừa và cô lập giữa `Tenant → Legal Entity → Branch → Workspace (AGENCY vs CLIENT)` (`INV-01`)? Khi thiếu context phạm vi thì fail-closed thế nào? (`INV-13`).
- **Quyền thực thi vs Chức danh (`M14` vs `M22`):** Thay đổi phòng ban/chức danh bên `M22` có tuyệt đối không tự mở rộng quyền đọc dữ liệu nhạy cảm nếu thiếu `Role Binding / Entity_Team_Grant`? (`INV-02`).
- **Chuyển giao, Kiêm nhiệm & Break-glass (`M14`, `M23`):** `Delegation` (nghỉ phép/bàn giao nhân sự) có bắt buộc `effective_from/to` và tự thu hồi khi hết hạn không? Quyền khẩn cấp `Break-glass` (`M23-F03`) ghi vào `M14` theo TTL và có kiểm `Maker != Checker` khi ở chế độ `TEAM` không? (`INV-22`).
- **Đồng bộ cache quyền (`M14` vs `M24`):** Khi thu hồi quyền (`Revoke`) hoặc đóng phiên khẩn cấp (`M23-F02`), `permission_version` bị invalidate ngay lập tức để Read Model/Cache không phục vụ quyền cũ (`INV-25`) và Download Gateway (`INV-24`) chặn tải file ngay?
