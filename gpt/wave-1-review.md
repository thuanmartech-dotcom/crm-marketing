# Báo cáo review Wave 1

Ngày 16/11/2026. Phạm vi chính gồm M14, M20, M19, M16 và bốn public contract tương ứng. ADR và kế hoạch được dùng để đối chiếu các phụ thuộc trực tiếp. Wave 1.5 chỉ được tham chiếu tại giao diện liên quan, chưa được audit toàn bộ. Không review các wave sau.

Đây là review đặc tả. Dự án đang ở giai đoạn Documentation-Only, chưa có bằng chứng thực thi ứng dụng. Các tình huống dưới đây là suy luận từ quy tắc đã viết, chưa phải lỗi được tái hiện trên phần mềm.

## Kết quả

Phát hiện 5 điểm cần xử lý, gồm 3 HIGH và 2 MEDIUM. Đề nghị xử lý các điểm HIGH trước khi dùng hợp đồng Wave 1 làm đầu vào triển khai. Mọi hướng xử lý dưới đây mang nhãn [PROPOSED], chưa áp dụng vào dự án.

### W1-01 — HIGH — Xóa PII một lần có thể bỏ sót chủ thể tiếp theo

**Bằng chứng.** M16 mục 4, dòng bảng `Task_Submissions`, quy định ngoại lệ cập nhật với `WHERE privacy_redacted_at IS NULL AND cardinality(active_legal_hold_ids) = 0`. C16 dòng 607 và C20 mục 3.2 cũng yêu cầu scrub đúng một lần, giữ hash gốc. Tham chiếu [M16](../02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md), [C16](../02-specs/contracts/M16-TASK-CORE-COMMANDS.md), [C20](../02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md).

**Tình huống.** Một submission chứa PII của A và B. Yêu cầu xóa A được xử lý và đặt `privacy_redacted_at`. Khi B yêu cầu xóa sau đó, điều kiện `IS NULL` ngăn lần scrub tiếp theo. Spec chưa bảo đảm lần đầu luôn loại bỏ PII của mọi chủ thể. Điều này có thể để lại dữ liệu B dù yêu cầu đã được tiếp nhận.

**[PROPOSED] Hướng giải quyết.** Đặt idempotency theo yêu cầu xóa/chủ thể và phiên bản submission, thay vì cờ đã redact toàn bản ghi. Cho phép nhiều lần redact có kiểm soát, mỗi lần giữ dấu vết xử lý và kiểm legal hold hiện hành. Phân biệt hash bằng chứng nguyên bản với hash nội dung sau redact để việc kiểm hash không diễn giải sai. Chốt cách tìm đủ các chủ thể trong nội dung và asset liên quan.

**Ca nghiệm thu đề xuất.** Xóa A rồi B trên cùng submission, phát lại mỗi event nhiều lần, xử lý hai yêu cầu đồng thời, giữ hold rồi gỡ hold và xử lý lại. PII của từng chủ thể phải được xử lý đủ, lịch sử review giữ truy vết.

### W1-02 — HIGH — Worker hết lease chưa có quy tắc chặn worker cũ gửi tiếp

**Bằng chứng.** M19 dòng 324–334 và C19 mục 2.3 quy định CAS lúc claim, lease, micro-commit `http_attempted_at`, rồi gọi HTTP. ADR-005 dòng 28–35 cho sweeper thu hồi lease khi chưa có dấu HTTP. Các đoạn này chưa quy định CAS kiểm quyền sở hữu lease tại micro-commit và khi ghi kết quả. Tham chiếu [M19](../02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [C19](../02-specs/contracts/M19-DURABLE-INGEST-OUTBOX.md), [ADR-005](../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md).

**Tình huống.** Worker A claim rồi bị treo trước dấu HTTP. Lease hết, sweeper cho worker B nhận lại. A tiếp tục chạy, ghi dấu và gửi trong khi B cũng thực hiện. CAS lúc claim ban đầu không đủ xác định A còn quyền gửi ở thời điểm này. Kết quả đến muộn cũng có thể ghi đè kết quả của lượt xử lý mới.

**[PROPOSED] Hướng giải quyết.** Đặc tả token thế hệ lease/attempt. Micro-commit trước HTTP phải CAS theo trạng thái, token, owner và hạn lease, chỉ gửi khi cập nhật thành công. Sau dấu HTTP, sweeper phải giữ đường UNKNOWN và đối soát. Kết quả đến muộn phải gắn đúng attempt và được hợp nhất có điều kiện. Dùng idempotency phía provider khi capability đã được xác minh.

**Ca nghiệm thu đề xuất.** Tạm dừng A trước micro-commit, hết lease, cho B claim rồi chạy lại A. A phải dừng trước HTTP. Thêm ca kết quả A về muộn sau sweeper để bảo đảm không ghi đè trạng thái mới.

### W1-03 — HIGH — Quy tắc retry sau hết lease mâu thuẫn giữa ADR và contract

**Bằng chứng.** ADR-005 dòng 35 chỉ cho về `RETRY_WAITING` khi `http_attempted_at IS NULL`, `allow_auto_retry = true` và còn TTL, đồng thời tăng `attempt_no`. M19 dòng 173/332 và C19 mục Concurrency, mục 2.3 lại mô tả về `QUEUED` khi dấu HTTP NULL, thiếu hai điều kiện còn lại ở nhánh này. Tham chiếu các tệp tại W1-02.

**Tác động.** Hai cách triển khai hợp lý theo hai tài liệu sẽ cho hành vi khác nhau đối với lệnh hết TTL hoặc cấm auto-retry. Lệnh có thể bị đưa lại vào hàng chờ hoặc mắc vòng nhận lại, trong khi ý định thiết kế muốn khóa retry theo loại rủi ro. Các kiểm TTL ở bước gửi giúp giảm rủi ro nhưng không giải quyết mâu thuẫn của state machine.

**[PROPOSED] Hướng giải quyết.** Chốt một bảng quyết định reaper dùng chung cho module, contract và ADR. Bao phủ riêng đã thử HTTP, chưa thử HTTP còn TTL được retry, hết TTL, và cấm auto-retry. Quy định trạng thái đích, tăng attempt và cách tạo công việc đối soát cho từng nhánh. Chủ dự án/Tech Lead cần chốt nhánh cấm retry nhưng chắc chắn chưa gửi, vì ADR hiện chưa nêu đầy đủ trạng thái đích.

**Ca nghiệm thu đề xuất.** Ma trận dấu HTTP NULL/non-NULL × TTL còn/hết × auto-retry bật/tắt. Mỗi tổ hợp có đúng một kết quả, không tự gửi lại khi chưa xác định được kết quả ngoài hệ thống.

### W1-04 — MEDIUM — Ca kiểm thử rút submission trái với hành vi đã đặc tả

**Bằng chứng.** Master dòng 1605, BR-W08 cho rút hoặc tạo submission mới khi sửa kết quả. C16 dòng 213 cho `WITHDRAW_SUBMISSION` chuyển `IN_REVIEW -> IN_PROGRESS`, chỉ từ chối quyết định duyệt cũ. Nhưng dòng 623 viết “rút submission (WithdrawSubmission) hay sửa khi đang duyệt trả 409”. Tham chiếu [Master](../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md), [C16](../02-specs/contracts/M16-TASK-CORE-COMMANDS.md).

**Tác động.** QA có thể coi thao tác rút hợp lệ là lỗi và yêu cầu chặn, làm mất đường sửa kết quả trước review.

**[PROPOSED] Hướng giải quyết.** Viết lại ca kiểm thử thành các tình huống riêng. Rút đúng quyền/version được thành công. Sửa trực tiếp submission bất biến bị chặn. Duyệt phiên bản đã rút trả conflict. Đua đồng thời rút và duyệt chỉ có một kết quả được commit.

### W1-05 — MEDIUM — Manifest phiên làm việc đã lệch trạng thái Wave 1

**Bằng chứng.** `active-task.json` còn ghi M16/C16 Drafted/Audited, chờ Reviewed và đề xuất chốt trước Wave 2. `DECOMPOSITION-PLAN.md` và C16 hiện ghi Reviewed sau Wave 1.5. Tham chiếu [manifest](../03-planning/agent/active-task.json), [kế hoạch](../03-planning/DECOMPOSITION-PLAN.md).

**Tác động.** Agent được hướng dẫn đọc manifest đầu phiên có thể mở lại bước đã hoàn tất hoặc chọn sai công việc tiếp theo. Đây là lỗi điều phối tài liệu, chưa chứng minh lỗi nghiệp vụ M14/M16.

**[PROPOSED] Hướng giải quyết.** Đồng bộ manifest với quyết định review được xác nhận, giữ riêng trạng thái review tài liệu và readiness triển khai. Bổ sung kiểm tra nhất quán trạng thái giữa manifest, README và kế hoạch. Các GAP chính sách còn mở cần có owner, phạm vi bị chặn và quyết định trước khi bật chức năng.

## Thứ tự xử lý đề xuất

1. Tech Lead và BA chốt W1-02/W1-03 cùng một bảng trạng thái dispatch/reaper.
2. Privacy Owner và BA chốt W1-01, đặc biệt trường hợp nhiều chủ thể và legal hold.
3. BA/QA sửa kỳ vọng W1-04 và đối chiếu state machine.
4. Người quản lý tài liệu đồng bộ W1-05 sau khi xác nhận trạng thái.

Các sửa đổi spec Reviewed nên được gom thành Change Proposal khi chủ dự án cho phép áp dụng. Báo cáo này chỉ cung cấp đề xuất để xét duyệt.

## Kiểm chứng và giới hạn

Đã chạy `verify_module_spec.py --file` cho từng module và contract M14/M20/M19/M16. Cả 8 kết quả `passed = true`, lưu tại [wave-1-validation.json](wave-1-validation.json). Đây là kiểm tra cấu trúc/trace mà script hỗ trợ, không xác nhận các hành vi cạnh tranh hoặc tính đầy đủ nghiệp vụ.

Đã đọc nhánh `--file` của script trước khi chạy để xác nhận nhánh này chỉ xuất kết quả ra stdout. Không chạy chế độ tổng hợp hoặc bộ sinh inventory vì chúng ghi evidence vào dự án. Chỉ tạo đầu ra trong `gpt/`, theo yêu cầu người dùng. Test ứng dụng **Not Run**.

Review tập trung vào hợp đồng liên module, state machine gửi, quyền riêng tư, vòng review và trạng thái điều phối. Chưa xác nhận an toàn toàn bộ Wave 1, chưa chạy PoC provider, test cạnh tranh, kiểm DB/RLS thực tế hay UAT. Các GAP hiện có về policy, provider và cấu hình vẫn cần được xử lý theo phạm vi bật chức năng.
