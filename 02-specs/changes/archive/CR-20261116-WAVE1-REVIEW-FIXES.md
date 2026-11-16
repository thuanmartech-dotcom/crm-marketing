# Change Proposal: `CR-20261116-WAVE1-REVIEW-FIXES` — Vá 5 Điểm Rà soát Độc lập Wave 1 (`W1-01..W1-05`) & Nâng cấp Cổng Kiểm chứng Ngữ nghĩa

- **Change ID:** `CR-20261116-WAVE1-REVIEW-FIXES`
- **Ngày lập & áp dụng:** `16/11/2026`
- **Trạng thái:** `Applied & Archived`
- **Nguồn kích hoạt:** Báo cáo rà soát độc lập Wave 1 ([gpt/wave-1-review.md](../../../gpt/wave-1-review.md)) và phiên `/grill-me` 3 nhánh đã được Chủ dự án phê duyệt.
- **Phạm vi ảnh hưởng:**
  - **ADRs:** [ADR-004](../../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](../../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-008](../../../01-architecture/decisions/ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md), [ADR-009](../../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md), [INDEX.md](../../../01-architecture/INDEX.md)
  - **Modules & Slices:** [M16-WORK-PROJECTS-TASK-CORE.md](../../modules/M16-WORK-PROJECTS-TASK-CORE.md), [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [M20-PRIVACY-CONSENT-RETENTION.md](../../modules/M20-PRIVACY-CONSENT-RETENTION.md), [SL01-INTERNAL-WORK.md](../../slices/SL01-INTERNAL-WORK.md)
  - **Public Contracts:** [M16-TASK-CORE-COMMANDS.md](../../contracts/M16-TASK-CORE-COMMANDS.md) (`C16`), [M19-DURABLE-INGEST-OUTBOX.md](../../contracts/M19-DURABLE-INGEST-OUTBOX.md) (`C19`), [M20-SUPPRESSION-PRIVACY-GATE.md](../../contracts/M20-SUPPRESSION-PRIVACY-GATE.md) (`C20`)
  - **Planning, Tooling & Skills:** [active-task.json](../../../03-planning/agent/active-task.json), [DECOMPOSITION-PLAN.md](../../../03-planning/DECOMPOSITION-PLAN.md), [PROGRESS.md](../../../03-planning/agent/PROGRESS.md), [02-specs/README.md](../../README.md), [verify_module_spec.py](../../../05-tools/verify_module_spec.py), [review-change-workflow.md](../../../.agents/skills/crm-ba-spec/references/review-change-workflow.md), [module-workflow.md](../../../.agents/skills/crm-ba-spec/references/module-workflow.md).

---

## 1. Động lực & Phân tích Nguyên nhân Gốc (`Root Cause Analysis`)

Qua đối soát độc lập tại `gpt/wave-1-review.md`, bộ đặc tả Wave 1 (`M14`, `M20`, `M19`, `M16` và 4 Public Contracts) còn tồn tại **3 điểm `HIGH` và 2 điểm `MEDIUM`** xuất phát từ hai nhóm nguyên nhân:
1. **Thiếu sót phân tích ca biên đa tác nhân/đa sự kiện nối tiếp khi viết spec:**
   - Thiết kế ngoại lệ xóa PII trên `Task_Submissions` dùng cờ một lần (`WHERE privacy_redacted_at IS NULL`) dẫn đến bỏ sót chủ thể B nếu cùng một submission chứa PII của cả A và B và hai chủ thể yêu cầu xóa ở hai thời điểm khác nhau (`W1-01`).
   - Thiết kế lease trên `M19.Outbound_Intents` chỉ kiểm CAS lúc claim đầu vào mà thiếu `lease_token` (fencing token) tại bước micro-commit `http_attempted_at` và Pha 3 commit kết quả (`W1-02`), đồng thời mô tả điều kiện Reaper bằng văn xuôi rời rạc gây mâu thuẫn giữa `ADR-005` (`RETRY_WAITING`) và `M19`/`C19` (`QUEUED`) (`W1-03`).
   - Viết tắt gộp dòng kiểm thử `W-T15` tại `C16:623` làm hiểu ngược rằng gọi `WithdrawSubmission` khi đang duyệt sẽ bị chặn `409` (`W1-04`).
   - Trường `next_actions` trong `active-task.json` chưa cập nhật sát tiến độ sau khi đóng Wave 1.5 (`W1-05`).
2. **Giới hạn của công cụ kiểm chứng tự động (`05-tools/verify_module_spec.py`) & Checklist trong `crm-ba-spec`:**
   - Script trước đây chỉ kiểm tra cấu trúc mục, JSON hợp lệ và độ phủ mã ID (syntactic check) mà chưa kiểm tra ngữ nghĩa chéo giữa ADR, Module, Contract và `active-task.json`.

---

## 2. Chi tiết 3 Quyết định Thiết kế Đã Chốt Qua `/grill-me`

### 2.1. Giải quyết `W1-01` (HIGH) — Đa lần Redact có Kiểm soát theo `deletion_ledger_id` & Tách đôi Hash trên `Task_Submissions` (`[PROPOSED]`)

1. **Bỏ điều kiện khóa một lần `WHERE privacy_redacted_at IS NULL`:**
   - Thay thế bằng cơ chế **Idempotency theo từng lệnh xóa (`redacted_deletion_ledger_ids uuid[] NOT NULL DEFAULT '{}'`)** kết hợp kiểm tra `active_legal_hold_ids`:
     - Điều kiện cho phép `privacy_erasure_system_role` thực thi scrub:
       `WHERE cardinality(active_legal_hold_ids) = 0 AND NOT (redacted_deletion_ledger_ids @> ARRAY[$deletion_ledger_id]::uuid[])`.
     - Cho phép một bản ghi `Task_Submissions` được scrub nhiều lần khi có nhiều chủ thể dữ liệu khác nhau (ví dụ xóa chủ thể A trước, xóa chủ thể B sau) hoặc khi gỡ `Legal_Hold` (`M20-F04 PARTIALLY_COMPLETED_LEGAL_HOLD -> COMPLETED`), trong khi phát lại cùng một sự kiện `M20.SubjectErasureExecuted` (`deletion_ledger_id` đã có trong `redacted_deletion_ledger_ids`) là `NO-OP` idempotent.
2. **Phân biệt Hash Bằng chứng Nguyên bản vs Hash Nội dung Sau Redact:**
   - Giữ nguyên bất biến vĩnh viễn cột **`content_sha256 char(64) NOT NULL`** (hash composite của nội dung và `asset_version_ids[]` tại đúng thời điểm nộp bài, khớp `Task_Reviews.content_sha256_checked`).
   - Bổ sung 3 cột kiểm toán redact trên `Task_Submissions`:
     - `redacted_content_sha256 char(64) NULL` (hash SHA-256 của `result_text` + `asset_version_ids[]` sau lần redact gần nhất; `NULL` khi `privacy_redaction_count = 0`).
     - `privacy_redaction_count int NOT NULL DEFAULT 0 CHECK (privacy_redaction_count >= 0)`.
     - `redacted_deletion_ledger_ids uuid[] NOT NULL DEFAULT '{}'`.
     - Giữ `privacy_redacted_at timestamptz NULL` là mốc thời gian của lần redact gần nhất.
   - **Quy tắc Kiểm tra Toàn vẹn (`Hash Verification Rule`):** Khi `privacy_redaction_count = 0`, trình kiểm chứng đối chiếu trực tiếp với `content_sha256`; khi `privacy_redaction_count > 0`, `content_sha256` chứng minh bằng chứng gốc lúc `Task_Reviews` chấm duyệt, còn `redacted_content_sha256` chứng minh toàn vẹn nội dung hiện hành sau khi scrub hợp pháp (kèm dấu vết trong `M20.Deletion_Ledger` và `M23.Audit_Logs`).
3. **Cơ chế Truy tìm Đủ Chủ thể trong `M16`:**
   - Khi nhận `M20.SubjectErasureExecuted` (mang `deletion_ledger_id`, `subject_hmac_sha256`, `erased_subject_refs[]`, `endpoint_hmac_hashes_by_version[]`), `M16` xác định tập bản ghi liên quan qua **cả 3 nguồn**: (a) các `Tasks` có `Task_Links` trỏ tới `(target_module, target_resource_type, target_resource_id)` nằm trong `erased_subject_refs[]` và toàn bộ `Task_Submissions`/`Task_Comments`/`Task_Assets` thuộc các `Tasks` đó, (b) cột `subject_hmac_sha256` trên `Tasks` và `Task_Submissions`, và (c) quét khớp mẫu định danh/hash trong `result_text` / `body_sanitized` của các công việc liên quan; đồng thời phối hợp `M23` ẩn danh/thu hồi `Assets`/`Asset_Versions` ngoài `Legal_Hold`.

### 2.2. Giải quyết `W1-02` & `W1-03` (HIGH) — Fencing bằng `lease_token` tại Micro-Commit & Pha 3 + Bảng Quyết định Reaper 8 Nhánh Dùng Chung (`[PROPOSED]`)

1. **Bổ sung `lease_token uuid NULL` & `pre_socket_reclaim_count int NN DEFAULT 0` trên `M19.Outbound_Intents` (`W1-02`):**
   - **Pha 1 (CAS Claim):** Worker sinh `lease_token` (UUID v4/v7 duy nhất cho mỗi lượt giữ lease) và thực thi:
     `UPDATE Outbound_Intents SET status = 'DISPATCHING', lease_owner_id = $worker_id, lease_token = $lease_token, lease_expires_at = $lease_exp, row_version = row_version + 1 WHERE id = $id AND status IN ('QUEUED', 'RETRY_WAITING') AND row_version = $expected_version`.
   - **Pha 2 (Micro-Commit Pre-Socket CAS Fencing):** Sau khi vượt qua recheck `M14` + `M20` và ngay trước khi mở socket HTTP, Worker **bắt buộc** thực thi CAS kiểm quyền sở hữu lease:
     `UPDATE Outbound_Intents SET http_attempted_at = now(), row_version = row_version + 1 WHERE id = $id AND status = 'DISPATCHING' AND lease_owner_id = $worker_id AND lease_token = $lease_token AND lease_expires_at > now()`.
     **Chỉ khi `affected_rows == 1` và `COMMIT` thành công thì Worker mới được phép phát HTTP request.** Nếu `affected_rows == 0` (do worker bị treo quá `lease_expires_at` hoặc đã bị Reaper thu hồi), Worker **phải hủy bỏ ngay lập tức trước khi mở socket**, chặn tuyệt đối trường hợp Worker A tỉnh dậy gửi trùng với Worker B.
   - **Pha 3 (Result Commit & Late-Response Handling):**
     - Mở transaction mới, `INSERT INTO Send_Attempts` (gắn `outbound_intent_id`, `attempt_no`, `lease_token` trong metadata/audit, `started_at`, `completed_at`).
     - Cập nhật `Outbound_Intents` kiểm tra khớp `WHERE id = $id AND lease_token = $lease_token AND status = 'DISPATCHING'`.
     - **Xử lý kết quả về muộn sau khi Reaper đã chuyển sang `UNKNOWN_OUTCOME`:** Vì khi `http_attempted_at IS NOT NULL`, Reaper chỉ chuyển sang `UNKNOWN_OUTCOME` (không bao giờ giao cho Worker B gửi lại), nếu phản hồi HTTP của chính `lease_token` đó về muộn trong khi bản ghi đang ở `UNKNOWN_OUTCOME` (chưa bị đóng bởi Operator), Pha 3 ghi nhận `Send_Attempts` và được phép hợp nhất có điều kiện (`WHERE id = $id AND status = 'UNKNOWN_OUTCOME' AND lease_token_last_attempted = $lease_token`) sang `ACCEPTED` (nếu có `provider_message_id` `2xx`) hoặc giữ `UNKNOWN_OUTCOME` kèm bằng chứng để đối soát, tuyệt đối không ghi đè nếu đã có lượt xử lý mới hơn.
2. **Bảng Quyết định Reaper 8 Nhánh Thống nhất giữa `ADR-005`, `M19` và `C19` (`W1-03`):**
   Khi Reaper quét các bản ghi quá hạn lease (`status = 'DISPATCHING' AND now() > lease_expires_at`), áp dụng duy nhất bảng chân trị 8 nhánh sau:

| Nhánh | `http_attempted_at` | Hạn `TTL` (`expires_at`) | `allow_auto_retry` | Trạng thái Đích (`Outbound_Intents.status`) | Cập nhật Bộ đếm & Hành động Bắt buộc |
|---:|---|---|---|---|---|
| **1–4** | `IS NOT NULL` *(đã qua micro-commit trước socket)* | Còn hoặc Hết (`now() < expires_at` hoặc `>=`) | `true` hoặc `false` | **`UNKNOWN_OUTCOME`** | Xóa `lease_owner_id`/`lease_token`/`lease_expires_at` (giữ vết `last_attempted_lease_token`), đặt `allow_auto_retry = false`, đặt `reconcile_due_at = now() + 15m`, tăng `attempt_count = attempt_count + 1`, mở việc đối soát (`GAP-M19-06`). **Cấm tuyệt đối đẩy về `QUEUED`/`RETRY_WAITING` mù.** |
| **5–6** | `IS NULL` *(chắc chắn chưa mở socket HTTP)* | **Đã hết TTL** (`now() >= expires_at`) | `true` hoặc `false` | **`EXPIRED_CANCELLED`** | Xóa lease, đặt `block_reason_code = 'INTENT_TTL_EXPIRED_BEFORE_SOCKET'`, giữ nguyên `attempt_count`, phát `M19.OutboundDispatchResulted(EXPIRED_CANCELLED)`. |
| **7** | `IS NULL` *(chắc chắn chưa mở socket HTTP)* | **Còn TTL** (`now() < expires_at`) | **`true`** | **`RETRY_WAITING`** *(hoặc `FAILED_TERMINAL` nếu vượt trần reclaim)* | Xóa lease, tăng `pre_socket_reclaim_count = pre_socket_reclaim_count + 1` (**không** tăng `attempt_count` gọi provider vì chưa phát HTTP), đặt `next_attempt_at` theo lịch backoff; nếu `pre_socket_reclaim_count > max_pre_socket_reclaims` (mặc định `3`) $\rightarrow$ chuyển `FAILED_TERMINAL` (`PRE_SOCKET_WORKER_CRASH_LIMIT`). |
| **8** | `IS NULL` *(chắc chắn chưa mở socket HTTP)* | **Còn TTL** (`now() < expires_at`) | **`false`** | **`QUEUED`** *(hoặc `FAILED_TERMINAL` nếu vượt trần reclaim)* | Vì **chắc chắn 100% chưa chạm socket mạng** (worker sập trước micro-commit CAS), xóa lease, tăng `pre_socket_reclaim_count = pre_socket_reclaim_count + 1`, giữ `attempt_count = 0` và trả về `QUEUED` để worker khỏe tiếp nhận; nếu `pre_socket_reclaim_count > max_pre_socket_reclaims` (mặc định `3`) $\rightarrow$ chuyển `FAILED_TERMINAL` (`PRE_SOCKET_WORKER_CRASH_LIMIT`) để chống vòng lặp nhận lại vô tận. |

### 2.3. Giải quyết `W1-04`, `W1-05` (MEDIUM) & Nâng cấp Cấu hình Kiểm chứng Dự án

1. **`W1-04` (`C16:623` & `M16:1069`):** Viết tách bạch 4 tình huống kiểm thử cho `W-T15`: (a) Assignee gọi `WithdrawSubmission` hợp lệ (đúng quyền + `expected_version` khi `IN_REVIEW`) thành công `200 OK` (`IN_REVIEW -> IN_PROGRESS`, `WITHDRAWN`); (b) sửa trực tiếp `Task_Submissions` bất biến hoặc `SaveResultDraft` khi đang `IN_REVIEW` mà không rút bị chặn `409/422`; (c) Reviewer duyệt vào `submission_id`/`submission_no` đã `WITHDRAWN` trả `409 TASK_VERSION_CONFLICT`; (d) đua đồng thời `WithdrawSubmission` và `ReviewSubmission` chỉ có đúng 1 lệnh được commit.
2. **`W1-05` (`active-task.json`):** Đồng bộ `next_actions`, tách rõ `spec_review_status` (`Reviewed`) và `implementation_readiness` (`Blocked_By_Open_Policy_Gaps`), cập nhật danh sách module còn lại (`Wave 2..6`).
3. **Nâng cấp `05-tools/verify_module_spec.py` & `.agents/skills/crm-ba-spec/`:**
   - Bổ sung hàm `check_cross_doc_consistency()` trong `verify_module_spec.py` tự động kiểm tra đồng bộ trạng thái giữa `active-task.json`, `DECOMPOSITION-PLAN.md`, `02-specs/README.md` và kiểm tra ngữ nghĩa chống tái diễn `W1-01..W1-04`.
   - Mở rộng checklist rà soát trong `review-change-workflow.md` và `module-workflow.md` lên 9 điểm nóng bắt buộc.
