# Contract `M16-TASK-CORE-COMMANDS` — Cổng Lệnh Task Core, Bàn giao Dự án, Nghiệm thu Khách hàng & Tiếp quản Công việc

- **Contract ID:** `CONTRACT-M16-WORK-DELIVERY-v1.0`
- **Provider Owner:** `M16` (Công việc, Dự án, Task Core & Nghiệm thu Kỹ thuật)
- **Consumers:** `M02`, `M03`, `M04`, `M06`, `M07`, `M08`, `M09`, `M10`, `M11`, `M12`, `M13`, `M14` (`M14-F06/F08`), `M15`, `M17`, `M18`, `M20`, `M21`, `M22`, `M23-F04/F12`, `M24` (`M24-F05/F06`)
- **Baseline & ADRs liên quan:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`3.6.2 FR15`, `3.10.1 FR25`, `3.10.3 FR27`, `3.13.3–3.13.5`, `3.14 W-F01–14 & BR-W01–10`, `3.15 BR-P17 & M21-F12`, `4.6 UC06`, `4.8 UC08`, `4.12 UC12`, `4.23 UC-W01–10`, `4.24 UC-P09`, `5.1`, `5.13`, `5.18`, `5.20`, `6.6`, `7.4`, `7.7`, `8.5`, `9.12 CEO-U03..05/15/17/19/20`, `9.16 W-T01–40`, `A.7 W-O01–07`, `M16-F01–07`, `M16-AC01–04`), [M16-WORK-PROJECTS-TASK-CORE.md](../modules/M16-WORK-PROJECTS-TASK-CORE.md), [CR-20261116-WAVE1-5-HARDENING.md](../changes/archive/CR-20261116-WAVE1-5-HARDENING.md), [ADR-002](../../01-architecture/decisions/ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](../../01-architecture/decisions/ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](../../01-architecture/decisions/ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](../../01-architecture/decisions/ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-009](../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md), [M14-PRINCIPAL-ACCESS-DECISION.md](M14-PRINCIPAL-ACCESS-DECISION.md), [M20-SUPPRESSION-PRIVACY-GATE.md](M20-SUPPRESSION-PRIVACY-GATE.md), [M19-DURABLE-INGEST-OUTBOX.md](M19-DURABLE-INGEST-OUTBOX.md), [M23-PLATFORM-GOVERNANCE-OUTBOX.md](M23-PLATFORM-GOVERNANCE-OUTBOX.md)
- **Trạng thái:** `Reviewed (Wave 1 — M16 Contract Baseline v1.0; CR-20261116-WAVE1-5-HARDENING Applied; CR-20261116-WAVE1-REVIEW-FIXES Applied & Verified; CR-20261116-SKILL-TEMPLATE-ALIGN Applied)`
- **Approved_Scope:** `Wave 1/1.5 Task Core & Delivery Acceptance Public Contract`
- **Approved_By:** `Chủ dự án`
- **Decision_Ref:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Approved_At:** `2026-11-16`
- **Chính sách Breaking Change:** Additive-only cho trường mới tùy chọn; mọi thay đổi cấu trúc bắt buộc của `Input`/`Output`, tập enum `work_type`/`typed_links`/`lifecycle_status`, hoặc Event Envelope `schema_version = "1.0"` (gồm đủ `11` Domain Events) bắt buộc giữ tương thích ngược (upcaster/dual-publish) cho hàng đợi `M23-F12.Internal_Outbox_Events` & backlog đồng bộ PMS `M19` đang tồn đọng, và cập nhật đồng bộ `M14`, `M20`, `M08`, `M16`, `M23`, `M24` cùng toàn bộ Consumers liên quan.

---

## 1. Hợp đồng Kiểm tra Đặc tả (`12 Phần Chuẩn CONTRACT.md`)

| Phần | Quy định chuẩn hóa của Hợp đồng |
|---|---|
| **Meaning** | `M16` là **nguồn sự thật duy nhất cho Task Core dùng chung (`W-F01–14`) và Giao nhận Dự án / Nghiệm thu Kỹ thuật (`M16-F01–07`)**, cung cấp 3 trụ cột cổng công khai: (1) **Task Core Cross-Module Creation & Lifecycle** (`CreateTaskByBusinessKey` + `TaskLifecycleCommandNote`) phục vụ `M02`, `M03`, `M04`, `M06` *(chỉ sau human draft review có `ai_draft_approval_token` & hash khớp draft)*, `M11`, `M12`, `M14`, `M15`, `M18-F11`, `M19`, `M20`, `M21-F12`, `M22` với `Work_Queues` độc lập (`queue_manager_user_id NOT NULL` ngay lúc tạo), `Task_Board_Stages` có version (`M23-F11`/`Policy_Versions`), `Task_Links` (Typed Resource Columns + Target Verification Port chặn `archived_at IS NOT NULL`), và `Assets / Asset_Versions` (`ENTITY-L2783`) qua `Download Gateway SEC03`; (2) **Project Handoff, Client Publish & Acceptance** (`InitializeProjectFromHandoff`, `PublishDeliverableForClientReview`, `RecordClientAcceptance`) giữ `Projects` & `Tasks` nội bộ tại `AGENCY workspace` và chỉ phát hành mảng `asset_refs[]` (`[{asset_id, asset_version_id, asset_checksum}]`) sang `CLIENT workspace` qua `M14.Contract_Workspace_Grants` để `PORTAL_CLIENT` (đúng `actor_id == entry.portal_principal_id`) ký `Acceptances` bất biến hoặc mở `Revision_Batches` / `Revision_Items` tách `DEFECT` vs `CHANGE`; (3) **Offboarding & Handover Port** (`ListOpenWorkForPrincipal`, `TransferWorkOwnership`) phục vụ `M14-F06` (`UC12`, `UC-W09`, `W-T29`) bao phủ 9 nhóm việc mở gồm `TASK` (`OPEN/IN_PROGRESS/IN_REVIEW` theo `current_assignee_id`), `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER`, `PROJECT_OWNER`, `QA_REVIEWER`, `TASK_CHANGE_APPROVER`, `PROJECT_CHANGE_APPROVER` *(rollup vào 13 category của `M14-F06`: `PROJECT_OWNER -> TASK`, `QA_REVIEWER -> TASK_REVIEW`, `TASK_CHANGE_APPROVER / PROJECT_CHANGE_APPROVER -> PENDING_APPROVAL`)*. **Khóa cứng `INV-05`:** `Task Completed (DONE)` KHÁC `Deliverable Accepted`, KHÁC `Ticket Closed / SLA Stopped`, KHÁC `Contact Reached`, KHÁC `Paid`. Internal Domain Outbox dùng **`M23-F12.Internal_Outbox_Events` (`Lane 2`, `ADR-005`)** cho đủ **`11` Domain Events**, tuyệt đối không dùng `M19` cho sự kiện nội bộ (`M19` chỉ dành cho PMS sync `UC-W10` hoặc thông báo kênh ngoài). |
| **Actor/scope** | Mọi lệnh `C16` bắt buộc truyền **`actor_id`** + **`actor_type` (`USER \| SERVICE_PRINCIPAL \| PORTAL_CLIENT`)** đã xác thực từ session/job context phía server (**không tin `tenant_id` hoặc `workspace_id` trần từ payload client**, `INV-01`). **Chặn cứng mọi `AI_AGENT` principal** không có `ai_draft_approval_token` hợp lệ dù truyền `source_module != 'M06'`; `PORTAL_CLIENT` bị chặn `403` trên mọi lệnh tạo/sửa `Tasks` & `Projects` nội bộ (`AGENCY`) và chỉ được gọi `RecordClientAcceptance` / phản hồi thông qua Write Port `SECURITY DEFINER` kiểm cứng **`actor_id == entry.portal_principal_id`** trong `Projects.authorized_client_approvers[]` (`ADR-002`, `CEO-U03`). `Projects`, `Tasks`, `Work_Queues`, `Task_Board_Stages`, `Task_Submissions`, `Task_Reviews`, `Task_Links` nằm trong `AGENCY workspace`; `CLIENT workspace` chỉ nhận gói `Deliverable / Client Review` đã publish qua `M14.Contract_Workspace_Grants` (`CEO-U17`). Mọi truy vấn/lệnh kiểm tra đồng bộ qua `M14.EvaluateAccessDecision` & `M14.CompileScopeFilter` (`C14`) và `M14.BindDbTransactionContext` (6 GUC). |
| **Preconditions** | Caller thỏa `M14.EvaluateAccessDecision` (`execution_mode = 'GUARDED_EXECUTION'` + `expected_permission_version` cho Worker, Bulk, `PublishDeliverableForClientReview`, `RecordClientAcceptance`, `TransferWorkOwnership`, và `Download Gateway SEC03`); PG connection chạy `M14.BindDbTransactionContext` (6 GUC gồm `app.current_workspace_type`). **Task Core:** `work_type` (`PERSONAL \| INTERNAL \| CRM \| PROJECT`) khớp `visibility_scope` (`PRIVATE \| PERSONAL \| TEAM \| PROJECT \| EXPLICIT \| WORKSPACE` — `PRIVATE <-> C14 PERSONAL` khóa `requester == assignee`, `EXPLICIT -> C14 PERSONAL` + whitelist, `PROJECT -> WORKSPACE`, `C14` SQL Compiler kiểm `NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT')` để ẩn khỏi team board `W-O04`); khi `OPEN` bắt buộc `assignee_user_id XOR queue_id` và `Work_Queues.queue_manager_user_id IS NOT NULL` (bắt buộc ngay lúc tạo queue cho mọi trạng thái); `OPEN -> DONE` & `OPEN -> IN_REVIEW` bắt buộc `assignment_status IN ('ACCEPTED', 'AUTO_ACCEPTED')`; khi `review_required = true` bắt buộc có `reviewer_id` hợp lệ (`W-O02`). Chặn `PublishTask`, `StartTask`, `Time_Entries` khi `Projects.status == 'PENDING_START'`. **`M06` / `AI_AGENT` Guard (`W-F14`):** bất kỳ principal `AI_AGENT` hoặc `source_module == 'M06'` chỉ được gọi `CreateTaskByBusinessKey` khi có **`ai_draft_approval_token`** hợp lệ do server ký kèm `draft_content_sha256` khớp draft `M06`. **`Task_Links` & `Assets` Port (`BR-W09`, `BR-P17`, `W-T38`):** chặn mọi target/asset có `archived_at IS NOT NULL`; kiểm `M14 READ` + `workspace_id` trước khi gắn `asset_version_id` vào `Task_Assets`/`Deliverable_Asset_Refs` hoặc liên kết `Task_Links` hai đầu; nếu assignee thiếu ACL đích thì từ chối trừ khi `allow_sanitized_fallback = true` kèm **`sanitized_approval_ref`** (`M23-F04.Approval_Requests == APPROVED`). **Publish & Acceptance:** `PublishDeliverableForClientReview` yêu cầu `qa_status == 'QA_PASSED'`, mọi phần tử trong `asset_refs[]` đạt `Asset_Versions.scan_status == 'CLEAN'` (`M20`) & `M14 READ` + `workspace_id`, `M14.Contract_Workspace_Grants` đang hiệu lực; `RecordClientAcceptance` kiểm phía server **`actor_id == entry.portal_principal_id`** (khi `PORTAL_CLIENT`), `now() BETWEEN grant_valid_from AND coalesce(grant_valid_until, 'infinity')`, `max_acceptance_scope` (`ALL_DELIVERABLES \| MILESTONE_ONLY`), **`evidence_asset_id IS NOT NULL (CLEAN)`** khi `actor_type = 'USER'` (`INTERNAL_PROXY_WITH_EVIDENCE`), và khớp chính xác mảng `expected_asset_refs[]` + `expected_deliverable_version`. |
| **Input** | Xem 7 cặp JSON Schema đầy đủ ở Mục 2 (`CreateTaskByBusinessKeyInput`, `TaskLifecycleCommandNote`, `InitializeProjectFromHandoffInput`, `PublishDeliverableForClientReviewInput`, `RecordClientAcceptanceInput`, `ListOpenWorkForPrincipalInput`, `TransferWorkOwnershipInput`). Mọi khối JSON hợp lệ chuẩn `json.loads()`, không dùng comment `//`. |
| **Output** | Xem 7 Output JSON Schema đầy đủ ở Mục 2 (`CreateTaskByBusinessKeyOutput`, `TaskLifecycleCommandOutput`, `InitializeProjectFromHandoffOutput`, `PublishDeliverableForClientReviewOutput`, `RecordClientAcceptanceOutput`, `ListOpenWorkForPrincipalOutput`, `TransferWorkOwnershipOutput`). Không trả raw DB row; mọi danh sách/đếm qua `M14.CompileScopeFilter` (`W-T36`). |
| **Errors** | Chuẩn Error Envelope `{code, message, field_errors, correlation_id}`. Mã lỗi bắt buộc: `403 AUTH_RBAC_FORBIDDEN` (thiếu quyền vai trò/trạng thái từ `M14`, Watcher sửa owner/hạn `W-T09`, `AI_AGENT` thiếu `ai_draft_approval_token` hợp lệ dù giả `source_module`, `PORTAL_CLIENT` gọi lệnh nội bộ, hoặc người không khớp `actor_id == entry.portal_principal_id` / hết hạn grant / vượt `max_acceptance_scope` trong `authorized_client_approvers[]` ký nghiệm thu `CEO-U03` — sub-code `ACCEPTANCE_AUTHORITY_REQUIRED`); `403 TASK_TARGET_CONTEXT_ACL_DENIED` (Target Verification Port phát hiện thiếu quyền `M14` hai đầu trên `Task_Links` hoặc thiếu `M14 READ` + `workspace_id` trên `asset_version_id`); `404 RESOURCE_NOT_FOUND_OR_DENIED` (**Chính sách Non-Disclosure `U17`:** che giấu sự tồn tại bản ghi/title/count ngoài workspace hoặc thiếu bridge hợp lệ); `409 IDEMPOTENCY_PAYLOAD_CONFLICT` (trùng `idempotency_key`/`client_operation_id` hoặc `handoff_key` / `source_business_key` khác canonical body `W-T04`); `409 TASK_VERSION_CONFLICT` (lệch `expected_version`, thua cuộc đua `claim` `W-T03`, sửa result khi đang duyệt `W-T15`, lệch `expected_asset_refs[]`/`expected_deliverable_version` `M16-AC02`, PWA offline sync conflict `W-T40`, hoặc `AUTH_PERMISSION_VERSION_STALE` từ `M14`); `422 ASSIGNMENT_INVALID` / `422 DELIVERABLE_LOCKED_FOR_REOPEN` (chặn `ReopenTask`/`ReopenTaskFamily` khi `Deliverables.status IN ('INTERNAL_REVIEW', 'CLIENT_REVIEW', 'REWORK', 'ACCEPTED')` hoặc bất kỳ nút cây có `active_legal_hold_ids <> '{}'`); `422 PARENT_DONE_REOPEN_FORBIDDEN` (`W-T20`); `422 PARENT_HAS_ACTIVE_OR_DONE_CHILDREN` (chặn `CancelTask` đơn lẻ trên cha khi chưa gọi `CancelTaskFamily`); `422 PROJECT_PENDING_START_BLOCKED`; `422 TARGET_ARCHIVED_FORBIDDEN` (`archived_at IS NOT NULL`); `422 EVIDENCE_ASSET_REQUIRED` (thiếu `evidence_asset_id` `CLEAN` khi `actor_type = 'USER'`); `422 SANITIZED_FALLBACK_NOT_APPROVED` (`allow_sanitized_fallback = true` thiếu `sanitized_approval_ref` đã duyệt tại `M23-F04`). |
| **Concurrency** | Optimistic locking qua `row_version` (`expected_version`) + CAS nguyên tử cho `claim`, `accept`, `submit`, `withdraw`, `review`, `publish-review`, `record-acceptance`, `reopen`, `cancel`, `transfer` (`INV-09`, `INV-10`, `INV-11`, `W-T03`, `W-T15`). `Task_Dependencies`, `parent_task_id`, `CancelTask` và `CancelTaskFamily` serialize theo `(tenant_id, workspace_id, graph_scope)` hoặc `SERIALIZABLE` retry hữu hạn (`W-T21`). Đồng bộ PWA offline qua `client_operation_id` + `expected_version` (`Master 7.4`, `W-T40`, cấm LWW). `RecordClientAcceptance` khóa deliverable & kiểm khớp `expected_deliverable_version` + toàn bộ `expected_asset_refs[]` (`M16-AC02`). Không giữ DB lock khi gọi `M19` PMS sync hoặc notification worker (`INV-06`). |
| **Idempotency** | **Trụ cột 1:** `idempotency_key` theo `(tenant_id, workspace_id, actor_id, command_name, idempotency_key)`, `client_operation_id` (`Master 7.4` PWA offline task/draft sync + `W-T40`) + **dedup business key `UNIQUE (tenant_id, workspace_id, source_module, source_business_key, episode_no)`** (`M21-F12`/`UC-P09`, `M04`, `M18-F11`, `M02`, `M03`, `M11`, `M12`, `M15`, `M20`, `M22`) — replay cùng payload trả bản ghi đã tạo sau khi kiểm lại `M14` read ACL; khác payload trả `409 IDEMPOTENCY_PAYLOAD_CONFLICT` (`W-T04`). **Trụ cột 2:** `InitializeProjectFromHandoff` chống trùng theo `handoff_key` (`CLIENT_DELIVERY`), `sow_version_id`, và `UNIQUE (tenant_id, workspace_id, idempotency_key)` trên `Projects` (chống trùng `INTERNAL` project khi `handoff_key IS NULL`); `PublishDeliverableForClientReview` & `RecordClientAcceptance` idempotent theo `(deliverable_id, deliverable_version, published_package_sha256 / verified_package_sha256, idempotency_key)`. **Trụ cột 3:** `TransferWorkOwnership` idempotent theo `(tenant_id, offboarding_case_id, transfer_phase, item_category, item_id)` & `idempotency_key`. Thời hạn lưu key cấu hình qua `M23.Policy_Versions` (`[OPEN-GAP: GAP-M16-05]` — đề xuất `[PROPOSED]` tối thiểu `72 giờ`, không tự mặc định `24h`). |
| **Transaction** | Mọi lệnh ghi chạy trong **1 DB transaction nguyên tử** (`INV-06`): `BindDbTransactionContext` (6 GUC) $\rightarrow$ mutate domain (`Tasks`, `Task_Assignments`, `Task_Board_Stages`, `Task_Links`, `Projects`, `Deliverables`, `Acceptances` Nhóm C, `Revision_Batches`, `Revision_Items`, `Client_Wait_Intervals`) $\rightarrow$ ghi `M23.Audit_Logs` (`Redact-Before-Insert`) $\rightarrow$ ghi **`M23-F12.Internal_Outbox_Events` (`Lane 2: STANDARD_INTERACTIVE`)**. Mọi tác vụ ngoài (`M24-F05`/`M24.Internal_Notifications`, `M24-F06` read model, `M18` BI projection, `M14-F08` Scorecard, `M19` PMS sync `UC-W10`) chỉ chạy sau commit; lỗi thông báo/sync không rollback giao dịch `M16` (`W-T34`). |
| **Compatibility** | `schema_version = "1.0"`. Trường mới tùy chọn theo nguyên tắc additive-only; consumers (`M02–M24`) bỏ qua trường chưa biết. Tính năng theo từng lát cắt (`SL01` text-only vs upload tệp `GAP-14`, `SL04` delivery/acceptance & DDL `ALTER TABLE Tasks ADD CONSTRAINT fk_*`, `SL06` recurrence/dependencies, `P1` capacity/PMS `UC-W10`) được khóa cổng bằng `M23-F09` Feature Flags (`CAPABILITY_DISABLED` khi `OFF`). |
| **Audit/privacy** | Mọi bảng `Nhóm C` (`Acceptances`, `Task_Reviews`, `Task_Events`, `M23.Audit_Logs`) áp chuẩn **Redact-Before-Insert (`ADR-004`)**. Riêng `Task_Submissions` & `Tasks` mang `redacted_deletion_ledger_ids uuid[]`, `privacy_redaction_count`, `privacy_redacted_at`, `redacted_content_sha256` & `subject_hmac_sha256` để `privacy_erasure_system_role` redact PII **đa lần có kiểm soát theo từng `deletion_ledger_id`** (chống chạy lặp bằng `NOT (redacted_deletion_ledger_ids @> ARRAY[$deletion_ledger_id]::uuid[])`) khi nhận `M20.SubjectErasureExecuted` ngoài hold (**giữ nguyên `content_sha256` gốc** làm bằng chứng lúc nộp và tách biệt với `redacted_content_sha256` sau scrub — `W1-01`). Hỗ trợ Multi-`Legal_Hold` qua `active_legal_hold_ids uuid[] DEFAULT '{}'` khi nhận `M20.LegalHoldChanged` mọi scope (`CONTRACT \| PROJECT \| DELIVERABLE \| TASK \| ASSET \| TICKET \| CONTACT \| ACCOUNT \| EMPLOYEE`). `Task_Links` không tự cấp quyền đọc đích (`INV-02`); `Assets / Asset_Versions` (`ENTITY-L2783`) tải qua `Download Gateway SEC03` (`ADR-006`). |
| **Tests** | `M16-AC01..04`, `W-T01..40` (`W-T02/03/04/06/07/08/09/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/29/34/36/37/38/40`), `CEO-U03/04/05/15/17/19/20`, `CMO-U13/14/15`, `CX-U10/11/21`, `P-T32/33/34`, `U16`, `U17`, `SEC-U03`, `INT23`, `INT29`. Toàn bộ ở trạng thái **`Not Run`**. |

---

## 2. Schemas Đầy đủ cho 3 Trụ cột Cổng Công khai (`14 JSON Schemas`)

> **Quy ước kiểm chứng JSON:** Toàn bộ khối `json` dưới đây tuân thủ cú pháp JSON chuẩn (`json.loads()` hợp lệ, không dùng comment). Tệp đính kèm (`Assets / Asset_Versions`, `ENTITY-L2783`) được quản lý qua Shared Platform Asset Registry và truy xuất bắt buộc qua `Download Gateway SEC03` (`M14 ACL + M20 EvaluateAssetDownloadPrivacyGate + M23-F07`, `ADR-006`).

### 2.1. Trụ cột 1A — `CreateTaskByBusinessKeyInput` & `CreateTaskByBusinessKeyOutput` (`W-F01/02`, `M21-F12`, `UC-P09`, `M18-F11`, `M04`)

```json
{
  "CreateTaskByBusinessKeyInput": {
    "tenant_id": "uuid (NN — suy xuất từ auth session hoặc trusted service context, cấm tin payload client)",
    "workspace_id": "uuid (NN — AGENCY workspace sở hữu task nội bộ)",
    "actor_id": "uuid (NN — user hoặc service principal thực hiện lệnh)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (PORTAL_CLIENT bị chặn 403 trên Task Core nội bộ; mọi AI_AGENT principal đều qua guard W-F14 bất kể source_module)",
    "expected_permission_version": "integer (bigint NN — kiểm tra M14 GUARDED_EXECUTION)",
    "idempotency_key": "uuid (NN — khóa idempotency theo tenant/workspace/actor/command)",
    "client_operation_id": "uuid | null (Master 7.4 PWA offline task/draft sync + W-T40)",
    "source_module": "M02 | M03 | M04 | M06 | M11 | M12 | M14 | M15 | M16 | M18 | M19 | M20 | M21 | M22",
    "source_business_key": "string | null (NN khi tạo từ domain nguồn/automation/exception để chống trùng; UNIQUE theo tenant/workspace/source_module/source_business_key/episode_no)",
    "episode_no": "integer (NN >= 1, default 1 — phân biệt các lần mở lại/episode hợp lệ trên cùng source_business_key)",
    "ai_draft_approval_token": {
      "required_when": "source_module == M06 OR caller principal là AI_AGENT (chặn cứng mọi AI_AGENT thiếu token hợp lệ dù truyền source_module != M06)",
      "approval_request_id": "uuid | null (ref server-side M23-F04 Approval_Requests / M06 human draft confirmation)",
      "draft_id": "uuid | null",
      "draft_content_sha256": "string | null (char(64) — server đối chiếu khớp hash bản draft đã được con người duyệt tại M06)",
      "signed_verification_token": "string | null (server-signed verification token, cấm tin tự khai)"
    },
    "work_type": "PERSONAL | INTERNAL | CRM | PROJECT",
    "visibility_scope": "PRIVATE | PERSONAL | TEAM | PROJECT | EXPLICIT | WORKSPACE (PRIVATE <-> PERSONAL; ánh xạ M16.Tasks.visibility [PRIVATE | TEAM | PROJECT | EXPLICIT] <-> C14 [PERSONAL | TEAM | WORKSPACE], EXPLICIT -> C14 PERSONAL + whitelist; C14 SQL Compiler kiểm NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT'))",
    "project_id": "uuid | null (bắt buộc non-null khi work_type = PROJECT; chỉ cho DRAFT nếu Projects.status = PENDING_START; chặn archived_at IS NOT NULL)",
    "milestone_id": "uuid | null (Composite FK cùng project_id tới Project_Milestones)",
    "deliverable_id": "uuid | null (Composite FK cùng project_id tới Deliverables)",
    "revision_batch_id": "uuid | null (Composite FK cùng project_id & deliverable_id tới Revision_Batches)",
    "parent_task_id": "uuid | null (cùng workspace và cùng project_id nếu thuộc project, archived_at IS NULL, depth <= 3, không cycle)",
    "title": "string (NN, trimmed 1..255 chars)",
    "description": "string | null (sanitized text/markdown, max 20000 chars)",
    "completion_criteria": "string | null (max 5000 chars; bắt buộc non-null khi initial_lifecycle = OPEN ở chế độ delegated hoặc review_required = true)",
    "priority": "LOW | NORMAL | HIGH | URGENT",
    "priority_reason": "string | null (bắt buộc non-null khi priority = URGENT)",
    "initial_lifecycle": "DRAFT | OPEN (bắt buộc DRAFT nếu Projects.status == PENDING_START)",
    "assignment_mode": "DIRECT_AUTO_ACCEPT | OFFER_ACCEPT | QUEUE_POOL | UNASSIGNED",
    "assignee_user_id": "uuid | null (bắt buộc XOR với queue_id khi initial_lifecycle = OPEN)",
    "queue_id": "uuid | null (FK M16.Work_Queues với queue_manager_user_id NOT NULL & archived_at IS NULL; XOR với assignee_user_id khi initial_lifecycle = OPEN)",
    "requester_id": "uuid (NN — default actor_id; authority không tự suy từ creator)",
    "review_required": "boolean (default false)",
    "reviewer_id": "uuid | null (bắt buộc non-null và active/đủ grant khi review_required = true; tách người theo W-O02)",
    "watcher_user_ids": [
      "uuid (tối đa 50, kiểm M14 ACL từng người, không tự mở context link)"
    ],
    "collaborator_user_ids": [
      "uuid (tối đa 50, kiểm M14 ACL từng người, không tự mở context link)"
    ],
    "planned_start_at": "timestamptz | null (UTC)",
    "due_at": "timestamptz | null (UTC — ánh xạ planned_due_at / effective_due_at; bắt buộc >= planned_start_at; bắt buộc non-null khi giao chính thức ngoài PERSONAL)",
    "committed_due_at": "timestamptz | null (UTC — read-only snapshot từ SOW/nguồn nếu có)",
    "allow_past_due_import": "boolean (default false)",
    "subject_hmac_sha256": "string | null (char(64) — optional lookup khi link subject cho M20.SubjectErasureExecuted)",
    "asset_version_ids": [
      "uuid (optional — mỗi phần tử phải vượt qua kiểm M14 READ + khớp workspace_id + archived_at IS NULL + M20 scan_status == CLEAN trước khi gắn vào Task_Assets)"
    ],
    "allow_sanitized_fallback": "boolean (default false — BR-W09 & BR-P17: cho phép tạo sanitized task khi assignee không có quyền đọc context nguồn)",
    "sanitized_approval_ref": {
      "required_when": "allow_sanitized_fallback == true",
      "approval_request_id": "uuid | null (FK server-side tới M23-F04 Approval_Requests trạng thái APPROVED)",
      "approval_decision_id": "uuid | null (FK tới M23-F04 Approval_Decisions)",
      "redacted_summary_sha256": "string | null (char(64) — khớp SHA-256 của redacted_summary đã duyệt)",
      "redacted_summary": "string | null (không chứa PII khách hàng/đối tác thô)"
    },
    "typed_links": [
      {
        "target_module": "M01 | M02 | M03 | M04 | M06 | M07 | M08 | M09 | M11 | M12 | M13 | M14 | M15 | M16 | M17 | M18 | M19 | M20 | M21 | M22",
        "target_resource_type": "CONTACT | ACCOUNT | LEAD | DEAL | CONVERSATION | MESSAGE | QUOTE | ORDER | CONTRACT | INVOICE_LINE | PAYMENT | TICKET | FEEDBACK | RECOVERY_CASE | APPOINTMENT | STRATEGY_BRIEF | IMC_PLAN | JOURNEY | CAMPAIGN | BUDGET | REPORT | PROJECT | DELIVERABLE | TASK | ASSET | OFFBOARDING_CASE | CONTRACT_WORKSPACE_GRANT | CHANNEL_CONNECTION | OUTBOUND_INTENT | SYNC_RUN | QUARANTINED_EVENT | PARTNER_EXCEPTION_CASE | PARTNER_REPORT | PRIVACY_REQUEST | DATA_INCIDENT | EMPLOYEE",
        "target_resource_id": "uuid (NN — kiểm tồn tại & archived_at IS NULL qua Target Verification Port)",
        "target_workspace_id": "uuid (NN — kiểm M14 bridge nếu khác workspace_id)",
        "relation_type": "SOURCE_ORIGIN | CONTEXT_REF | FULFILLS_OBLIGATION | REMEDIATION_FOR | BLOCKING_REF | SANITIZED_REFERENCE"
      }
    ],
    "correlation_id": "uuid (NN)"
  },
  "CreateTaskByBusinessKeyOutput": {
    "task_id": "uuid",
    "workspace_id": "uuid",
    "work_type": "PERSONAL | INTERNAL | CRM | PROJECT",
    "visibility_scope": "PRIVATE | PERSONAL | TEAM | PROJECT | EXPLICIT | WORKSPACE (PRIVATE <-> PERSONAL; ánh xạ M16.Tasks.visibility [PRIVATE | TEAM | PROJECT | EXPLICIT] <-> C14 [PERSONAL | TEAM | WORKSPACE], EXPLICIT -> C14 PERSONAL + whitelist; C14 SQL Compiler kiểm NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT'))",
    "lifecycle_status": "DRAFT | OPEN",
    "assignment_status": "UNASSIGNED | OFFERED | ACCEPTED | AUTO_ACCEPTED",
    "assignee_user_id": "uuid | null",
    "queue_id": "uuid | null",
    "row_version": "integer (bigint >= 1)",
    "is_sanitized_context": "boolean",
    "verified_links_count": "integer (>= 0)",
    "idempotent_replay": "boolean",
    "created_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Kiểm duyệt `CreateTaskByBusinessKey` (`BR-W01..10`, `BR-P17`, `W-F14`):**
> - **Ràng buộc `Work_Queues`, `archived_at` & `PENDING_START`:** `Work_Queues` là thực thể riêng do `M16` sở hữu và bắt buộc **`queue_manager_user_id IS NOT NULL` ngay lúc tạo** (`W-O01`). Khi `initial_lifecycle = OPEN`, từ chối `422 ASSIGNMENT_INVALID` nếu vừa truyền cả `assignee_user_id` lẫn `queue_id`, thiếu cả hai, user đích không `ACTIVE`, hoặc `Work_Queues` đang `archived_at IS NOT NULL` / không `ACTIVE`. Nếu `Projects.status == 'PENDING_START'`, chỉ cho tạo `DRAFT` (chuẩn bị) và chặn `OPEN` (`422 PROJECT_PENDING_START_BLOCKED`). Chặn gắn bất kỳ `project_id`, `milestone_id`, `deliverable_id`, `revision_batch_id`, `parent_task_id`, `asset_version_id` hay `target_resource_id` nào có `archived_at IS NOT NULL` (`422 TARGET_ARCHIVED_FORBIDDEN`).
> - **`Task_Links` Target Verification Port & `Assets` ACL (`BR-W09`, `BR-P17`, `W-T38`):** Mỗi phần tử trong `typed_links[]` đi qua Target Verification Port kiểm tra bản ghi đích tồn tại với `archived_at IS NULL` và kiểm `M14.EvaluateAccessDecision` cho **cả caller lẫn assignee** (`target_workspace_id` khác `workspace_id` phải có bridge `Workspace_Account_Links` / `Contract_Workspace_Grants` hợp lệ); khi đích bị archive/xóa về sau hoặc nhận `M20.SubjectErasureExecuted`, `M16` cập nhật `Task_Links.target_tombstoned_at = now()`. Nếu assignee không có quyền đọc context nguồn: mặc định chặn `403 TASK_TARGET_CONTEXT_ACL_DENIED`; chỉ cho phép tiếp tục khi `allow_sanitized_fallback = true` VÀ `sanitized_approval_ref` trỏ tới `M23-F04.Approval_Requests` đã `APPROVED` kèm khớp `redacted_summary_sha256` (thiếu trả `422 SANITIZED_FALLBACK_NOT_APPROVED`). Mọi `asset_version_ids[]` bắt buộc vượt qua `M14 READ` + kiểm khớp `workspace_id` + `scan_status == 'CLEAN'` trước khi chèn `Task_Assets`.
> - **Chặn cứng `M06` / Mọi `AI_AGENT` Principal (`W-F14`):** Bất kỳ caller thuộc `AI_AGENT` hoặc mang `source_module == 'M06'` thiếu **`ai_draft_approval_token`** hợp lệ do server ký (có `approval_request_id`/`draft_id` đã được con người duyệt và `draft_content_sha256` khớp bản draft tại `M06`) bị chặn ngay **`403 AUTH_RBAC_FORBIDDEN`**, kể cả khi payload giả mạo truyền `source_module != 'M06'`.

### 2.2. Trụ cột 1B — `TaskLifecycleCommandNote` & `TaskLifecycleCommandOutput` (`UC-W02..06`, `BR-W02..10`)

```json
{
  "TaskLifecycleCommandNote": {
    "command_name": "PUBLISH_DRAFT | CLAIM_FROM_QUEUE | ACCEPT_OFFER | DECLINE_OFFER | START_WORK | MOVE_STAGE | SAVE_RESULT_DRAFT | SUBMIT_FOR_REVIEW_OR_DONE | WITHDRAW_SUBMISSION | REVIEW_SUBMISSION | REQUEST_CHANGE | DECIDE_CHANGE_REQUEST | REPORT_BLOCKER | RESOLVE_BLOCKER | REOPEN_TASK | REOPEN_TASK_FAMILY | CANCEL_TASK | CANCEL_TASK_FAMILY | ADD_DEPENDENCY | WAIVE_DEPENDENCY",
    "http_endpoint_mapping": "POST /v1/tasks/{id}/publish | /claim | /accept | /decline | /start | /stage-move | PUT /result-draft | POST /submissions | /submissions/{subId}/withdraw | POST /v1/submissions/{id}/reviews | POST /change-requests | POST /v1/task-change-requests/{id}/decisions | POST /blockers | /unblock | /reopen | /reopen-family | /cancel | /cancel-family | /dependencies | /dependencies/{depId}/waive",
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid (NN)",
    "task_id": "uuid (NN)",
    "actor_id": "uuid (NN)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (PORTAL_CLIENT bị chặn 403 trên các lệnh lifecycle Task nội bộ AGENCY)",
    "expected_version": "integer (bigint NN — phải khớp Tasks.row_version; lệch trả 409 TASK_VERSION_CONFLICT)",
    "expected_permission_version": "integer (bigint NN — kiểm tra M14 GUARDED_EXECUTION)",
    "idempotency_key": "uuid (NN)",
    "client_operation_id": "uuid | null (Master 7.4 PWA offline sync + W-T40 — không LWW khi lệch expected_version)",
    "command_payload": {
      "submission_id": "uuid | null (bắt buộc cho WITHDRAW_SUBMISSION & REVIEW_SUBMISSION)",
      "expected_result_version": "integer | null (bắt buộc cho SUBMIT_FOR_REVIEW_OR_DONE [đối chiếu Tasks.row_version] & REVIEW_SUBMISSION [đối chiếu Task_Submissions.submission_no] theo BR-W08)",
      "submission_content_sha256": "string | null (char(64) composite SHA-256 của result_text + ordered asset_version_ids[] + asset_checksum[], khớp Task_Submissions.content_sha256)",
      "result_text": "string | null (sanitized text max 20000 chars)",
      "asset_version_ids": [
        "uuid (mọi Asset_Version bắt buộc kiểm M14 READ + khớp workspace_id + archived_at IS NULL + M20 Asset_Versions.scan_status == CLEAN trước SUBMIT; tải qua SEC03 asset_domain = CRM_ATTACHMENT)"
      ],
      "asset_refs": [
        {
          "asset_id": "uuid (NN)",
          "asset_version_id": "uuid (NN)",
          "asset_checksum": "string (char(64) SHA-256 == Asset_Versions.content_sha256 — tách riêng khỏi submission_content_sha256 tổng hợp)"
        }
      ],
      "target_stage_code": "string | null (chỉ dùng cho MOVE_STAGE qua Task_Board_Stages & guards BR-W02)",
      "target_stage_schema_version": "integer | null (bắt buộc cho MOVE_STAGE để khớp danh mục Task_Board_Stages M23-F11)",
      "review_decision": "APPROVED | REJECTED | null",
      "change_request_type": "DUE_EXTENSION | REASSIGN | BOTH | null (đổi SOW/vượt committed_due_at dùng endpoint Project_Change_Requests, không đi qua TaskLifecycleCommandNote)",
      "proposed_due_at": "timestamptz | null (UTC — không tự xóa breach lịch sử BR-W04)",
      "proposed_assignee_id": "uuid | null",
      "proposed_queue_id": "uuid | null",
      "blocker_type": "CLIENT_INPUT | INTERNAL_DEPENDENCY | TECHNICAL | APPROVAL_WAIT | RESOURCE | null",
      "blocker_owner_id": "uuid | null",
      "blocker_review_at": "timestamptz | null (UTC)",
      "reopen_mode": "PREVIEW | COMMIT | null (bắt buộc cho REOPEN_TASK_FAMILY khi cha đang DONE)",
      "affected_expected_versions": [
        "integer (danh sách row_version các task trong nhánh cho REOPEN_TASK_FAMILY / CANCEL_TASK_FAMILY COMMIT atomic)"
      ],
      "reason": "string | null (bắt buộc 1..1000 chars cho DECLINE_OFFER, REJECTED, REQUEST_CHANGE, DECIDE_CHANGE_REQUEST, REOPEN_TASK, REOPEN_TASK_FAMILY, CANCEL_TASK, CANCEL_TASK_FAMILY, WAIVE_DEPENDENCY, OVERRIDE)",
      "override_approval_request_id": "uuid | null (FK server-side tới M23-F04 Approval_Requests trạng thái APPROVED cho ngoại lệ Self-Review W-T16 — cấm client tự khai boolean)",
      "predecessor_task_id": "uuid | null (chỉ dùng cho ADD_DEPENDENCY / WAIVE_DEPENDENCY — Finish-to-Start cùng workspace, archived_at IS NULL, atomic graph cycle check)"
    },
    "non_cascade_invariants": {
      "done_does_not_imply_client_accepted": true,
      "done_does_not_close_ticket_or_sla": true,
      "done_does_not_confirm_contact_reach": true,
      "done_does_not_imply_paid": true,
      "board_drag_drop_uses_guarded_commands": true
    },
    "correlation_id": "uuid (NN)"
  },
  "TaskLifecycleCommandOutput": {
    "task_id": "uuid",
    "lifecycle_status": "DRAFT | OPEN | IN_PROGRESS | IN_REVIEW | DONE | CANCELED",
    "assignment_status": "UNASSIGNED | OFFERED | ACCEPTED | AUTO_ACCEPTED",
    "row_version": "integer (bigint)",
    "submission_id": "uuid | null",
    "result_version": "integer | null",
    "submission_content_sha256": "string | null (char(64) composite hash của Task_Submissions)",
    "asset_checksums": [
      "string (char(64) — từng Asset_Versions.content_sha256 trong asset_version_ids[])"
    ],
    "review_decision": "APPROVED | REJECTED | null",
    "is_overdue": "boolean",
    "is_blocked": "boolean",
    "idempotent_replay": "boolean",
    "processed_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Chuyển trạng thái Bắt buộc (`BR-W02..08`, `Master 5.20`, `3.13.5 CONTRACT-L1528`):**
> - **Cấm `PATCH status` tự do (`W-T10`, `CONTRACT-L1528`):** Mọi thao tác kéo thả Kanban board bắt buộc gọi đúng command có guard (`START_WORK`, `MOVE_STAGE` đối chiếu `Task_Board_Stages`, `SUBMIT_FOR_REVIEW_OR_DONE`, `REVIEW_SUBMISSION`), không nhảy qua bước kiểm duyệt `IN_REVIEW`.
> - **Khóa `OPEN -> DONE` / `OPEN -> IN_REVIEW` & `PENDING_START`:** Mọi chuyển tiếp từ `OPEN` sang `IN_PROGRESS`, `IN_REVIEW`, hoặc `DONE` (simple task) đều bắt buộc **`assignment_status IN ('ACCEPTED', 'AUTO_ACCEPTED')`** (chặn hoàn tất việc `UNASSIGNED`/`OFFERED`). Khi `Projects.status == 'PENDING_START'`, từ chối `422 PROJECT_PENDING_START_BLOCKED` đối với `PUBLISH_DRAFT` và `START_WORK`.
> - **Nộp, Rút & Duyệt Theo Phiên bản (`BR-W08`, `W-T14`, `W-T15`, `W-T19`):** `SUBMIT_FOR_REVIEW_OR_DONE` chặn `422 ASSIGNMENT_INVALID` nếu thiếu checklist bắt buộc, còn mandatory subtasks chưa `DONE`, còn hard blocker chưa miễn trừ, hoặc có phần tử trong `asset_version_ids[]` chưa `CLEAN` / thiếu `M14 READ` + `workspace_id`. Khi đã vào `IN_REVIEW`, `Task_Submissions` bất biến nội dung (`submission_content_sha256` tổng hợp tách biệt với `asset_checksum` từng `Asset_Versions`); để sửa kết quả đang chờ duyệt, Assignee bắt buộc gọi **`WITHDRAW_SUBMISSION`** (`IN_REVIEW -> IN_PROGRESS`, `Task_Submissions -> WITHDRAWN`) rồi nộp bản mới — quyết định duyệt gửi vào `submission_id`/`expected_result_version` cũ bị chặn `409 TASK_VERSION_CONFLICT`.
> - **Gia hạn, Blocker, `CancelTask` & `ReopenTaskFamily` (`BR-W03..07`):** Gia hạn (`DUE_DATE`) giữ nguyên `original_due_at` & breach lịch sử; nếu vượt `committed_due_at` bắt buộc chuyển qua `Project_Change_Requests`. **`CANCEL_TASK`** giữ graph lock `(tenant_id, workspace_id, graph_scope)`, chặn `422 PARENT_HAS_ACTIVE_OR_DONE_CHILDREN` nếu còn con active/`DONE` trừ khi gọi **`CANCEL_TASK_FAMILY`**, và chặn khi `active_legal_hold_ids <> '{}'`. **`REOPEN_TASK` & `REOPEN_TASK_FAMILY`** bị **CẤM (`422 DELIVERABLE_LOCKED_FOR_REOPEN`)** khi `Deliverables.status IN ('INTERNAL_REVIEW', 'CLIENT_REVIEW', 'REWORK', 'ACCEPTED')` hoặc bất kỳ nút nào trong cây có `active_legal_hold_ids <> '{}'`; đồng thời vẫn cấm reopen con đơn lẻ dưới cha `DONE` (`422 PARENT_DONE_REOPEN_FORBIDDEN`, `W-T20`).

### 2.3. Trụ cột 2A — `InitializeProjectFromHandoffInput` & `InitializeProjectFromHandoffOutput` (`M16-F01`, `M08-F03/04`, `UC06`)

```json
{
  "InitializeProjectFromHandoffInput": {
    "tenant_id": "uuid (NN)",
    "agency_workspace_id": "uuid (NN — Projects & Tasks nội bộ luôn lưu tại AGENCY workspace)",
    "actor_id": "uuid (NN — người xác nhận handoff hoặc trusted service M08)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (PORTAL_CLIENT bị chặn 403)",
    "expected_permission_version": "integer (bigint NN — M14 GUARDED_EXECUTION)",
    "handoff_key": "string | null (bắt buộc NN khi project_type = CLIENT_DELIVERY; NULL hợp lệ cho INTERNAL; 1 MSA có nhiều handoff_key/sow_version_id khác nhau theo M16-AC01)",
    "idempotency_key": "uuid (NN — UNIQUE (tenant_id, workspace_id, idempotency_key) trên Projects, chống trùng cả INTERNAL project khi handoff_key IS NULL)",
    "project_type": "CLIENT_DELIVERY | INTERNAL",
    "contract_id": "uuid | null (bắt buộc non-null khi project_type = CLIENT_DELIVERY; NULL hợp lệ cho INTERNAL)",
    "sow_version_id": "uuid | null (bắt buộc non-null và unique scope khi project_type = CLIENT_DELIVERY; NULL cho INTERNAL)",
    "order_id": "uuid | null",
    "sponsor_user_id": "uuid | null (bắt buộc non-null khi project_type = INTERNAL theo M16.Projects CHECK)",
    "start_authorization_ref": "string | null (bắt buộc non-null khi project_type = INTERNAL theo 5.20 L2915)",
    "legal_entity_id": "uuid (NN cho CLIENT_DELIVERY — khớp pháp nhân hợp đồng CEO-U10; lấy mặc định theo M14 nếu INTERNAL)",
    "branch_id": "uuid | null",
    "business_line_id": "uuid | null",
    "client_account_id": "uuid | null (bắt buộc non-null khi project_type = CLIENT_DELIVERY)",
    "client_workspace_id": "uuid | null (CLIENT workspace tiếp nhận publish nếu bật portal khách hàng)",
    "start_authorization_mode": "FULL | CREATIVE_ONLY_NO_MEDIA | PENDING_START",
    "project_name": "string (NN, trimmed 1..255 chars)",
    "project_owner_id": "uuid (NN — PM accountable tại AGENCY workspace)",
    "planned_start_at": "timestamptz | null (UTC)",
    "committed_due_at": "timestamptz | null (UTC — cam kết hợp đồng chỉ đổi qua Approved Change_Request)",
    "max_revisions": "integer | null (>= 0; cấu hình theo SOW cho CLIENT_DELIVERY)",
    "authorized_client_approvers": [
      {
        "contact_id": "uuid (NN — danh sách người có thẩm quyền ký nghiệm thu theo CEO-U03)",
        "portal_principal_id": "uuid | null (bắt buộc khớp actor_id == entry.portal_principal_id khi PORTAL_CLIENT ký nghiệm thu)",
        "role_code": "string (NN)",
        "max_acceptance_scope": "ALL_DELIVERABLES | MILESTONE_ONLY",
        "grant_valid_from": "timestamptz (UTC)",
        "grant_valid_until": "timestamptz | null (UTC)"
      }
    ],
    "deliverable_seeds": [
      {
        "sow_deliverable_code": "string (NN)",
        "title": "string (NN, 1..255 chars)",
        "committed_due_at": "timestamptz | null (UTC)",
        "acceptance_criteria": "string (NN)",
        "requires_client_acceptance": true
      }
    ],
    "template_version_id": "uuid | null (kiểm archived_at IS NULL nếu có)",
    "correlation_id": "uuid (NN)"
  },
  "InitializeProjectFromHandoffOutput": {
    "project_id": "uuid",
    "project_type": "CLIENT_DELIVERY | INTERNAL",
    "project_status": "DRAFT | PENDING_START | ACTIVE",
    "start_authorization_mode": "FULL | CREATIVE_ONLY_NO_MEDIA | PENDING_START",
    "agency_workspace_id": "uuid",
    "client_workspace_id": "uuid | null",
    "contract_workspace_grant_id": "uuid | null",
    "created_deliverable_ids": [
      "uuid"
    ],
    "row_version": "integer (bigint >= 1)",
    "idempotent_replay": "boolean",
    "initialized_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Khởi tạo Dự án (`M16-F01`, `M16-AC01`, `CEO-U04`, `CEO-U05`):**
> - **1 MSA nhiều Project & Chống trùng `INTERNAL` (`M16-AC01`):** Khóa chống trùng áp dụng trên `(tenant_id, agency_workspace_id, handoff_key)` và `(tenant_id, agency_workspace_id, sow_version_id)` cho `CLIENT_DELIVERY`, cộng thêm **`UNIQUE (tenant_id, workspace_id, idempotency_key)` trên `Projects`** để chống trùng khi tạo dự án `INTERNAL` (`handoff_key IS NULL`). Tuyệt đối **không** đặt `UNIQUE (contract_id)` để 1 hợp đồng khung MSA có thể mở nhiều SOW/Project hợp lệ. Replay trả `project_id` hiện hữu (`idempotent_replay = true`); cùng key khác SOW/scope trả `409 IDEMPOTENCY_PAYLOAD_CONFLICT`.
> - **`start_authorization_mode` (`CEO-U05`):** Nếu `PENDING_START`, `Projects.status` giữ ở `PENDING_START` — **chặn `PublishTask`, `StartTask` và `Time_Entries` (`422 PROJECT_PENDING_START_BLOCKED`)**, chỉ cho chuẩn bị task `DRAFT`. Nếu `CREATIVE_ONLY_NO_MEDIA`, cho phép `ACTIVE` phần sản xuất nội dung nhưng phát cờ khóa giải ngân/chạy ngân sách media sang `M17`/`M15`.

### 2.4. Trụ cột 2B — `PublishDeliverableForClientReviewInput` & `PublishDeliverableForClientReviewOutput` (`M16-F03`, `ADR-009`)

```json
{
  "PublishDeliverableForClientReviewInput": {
    "tenant_id": "uuid (NN)",
    "agency_workspace_id": "uuid (NN)",
    "client_workspace_id": "uuid (NN — CLIENT workspace nhận gói publish)",
    "project_id": "uuid (NN)",
    "deliverable_id": "uuid (NN)",
    "actor_id": "uuid (NN — PM hoặc Delivery Lead có quyền publish trong AGENCY)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (chỉ cho phép AGENCY USER hoặc SERVICE_PRINCIPAL; PORTAL_CLIENT bị chặn 403)",
    "expected_permission_version": "integer (bigint NN — M14 GUARDED_EXECUTION)",
    "expected_deliverable_version": "integer (bigint NN — CAS Deliverables.row_version)",
    "idempotency_key": "uuid (NN)",
    "qa_status": "QA_PASSED (bắt buộc == QA_PASSED; chưa QA đạt bị từ chối 422)",
    "internal_review_submission_id": "uuid (NN — chứng cứ đã qua InternalReview hợp lệ)",
    "asset_refs": [
      {
        "asset_id": "uuid (NN — Shared Platform Asset Registry ENTITY-L2783)",
        "asset_version_id": "uuid (NN — phiên bản bất biến Asset_Versions, kiểm M14 READ + workspace_id + archived_at IS NULL)",
        "asset_checksum": "string (char(64) SHA-256 NN — bắt buộc khớp Asset_Versions.content_sha256)"
      }
    ],
    "contract_workspace_grant_id": "uuid (NN — cầu nối M14.Contract_Workspace_Grants đang ACTIVE cho DELIVERABLE)",
    "publish_notes": "string | null (sanitized client-facing notes, max 5000 chars)",
    "response_due_at": "timestamptz | null (UTC)",
    "correlation_id": "uuid (NN)"
  },
  "PublishDeliverableForClientReviewOutput": {
    "deliverable_id": "uuid",
    "deliverable_status": "CLIENT_REVIEW",
    "deliverable_version": "integer (bigint)",
    "published_asset_refs": [
      {
        "asset_id": "uuid",
        "asset_version_id": "uuid",
        "asset_checksum": "string (char(64))",
        "gateway_asset_ref": "string (SEC03 Download Gateway reference — cấm trả Storage presigned URL thô)"
      }
    ],
    "published_package_sha256": "string (char(64) — composite hash của toàn gói asset_refs đã publish)",
    "client_workspace_id": "uuid",
    "client_wait_interval_id": "uuid (mở bản ghi Client_Wait_Intervals ngay khi publish)",
    "wait_started_at": "timestamptz (UTC)",
    "idempotent_replay": "boolean",
    "published_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Publish sang `CLIENT workspace` (`M16-F03`, `ADR-006`, `ADR-009`):**
> - Kiểm tra đồng thời 4 chốt chặn trước khi ghi `CLIENT_REVIEW`: (1) `qa_status == 'QA_PASSED'` và `internal_review_submission_id` đã `APPROVED` (chặn nếu `Projects.status` đã `TERMINATED` hoặc `Deliverables.archived_at IS NOT NULL`); (2) cho từng phần tử trong `asset_refs[]` (`min 1` item), kiểm `M14 READ` + khớp `workspace_id` + `archived_at IS NULL` và gọi `M20` kiểm `Asset_Versions.scan_status == 'CLEAN'` + không vướng hold/erasure chặn phát hành (`422 ASSIGNMENT_INVALID` nếu chưa `CLEAN`); (3) kiểm `M14.Contract_Workspace_Grants` đang `ACTIVE` (`revoked_at IS NULL`) cho cặp `agency_workspace_id -> client_workspace_id` và `contract_id` của Project (`403 AUTH_RBAC_FORBIDDEN` hoặc `404 RESOURCE_NOT_FOUND_OR_DENIED` nếu sai cầu nối); (4) xác minh mọi `asset_version_id` + `asset_checksum` bất biến (`409 TASK_VERSION_CONFLICT` nếu tệp đã đổi).
> - Trong cùng transaction publish, `M16` tự động mở bản ghi `Client_Wait_Intervals` (`is_open = true`, `requested_at = now()`) và phát event `M16.ClientWaitIntervalRecorded` + `M16.DeliverablePublishedForReview` tới `M24-F06` / `M24-F05` / `M08` / `M18` / `M12` để tách bạch thời gian chờ khách với năng suất nội bộ (`M16-AC04`, `CMO-U14`).

### 2.5. Trụ cột 2C — `RecordClientAcceptanceInput` & `RecordClientAcceptanceOutput` (`M16-F05`, `UC08`, `CEO-U03`, `M16-AC02/03`)

```json
{
  "RecordClientAcceptanceInput": {
    "tenant_id": "uuid (NN)",
    "client_workspace_id": "uuid | null (bắt buộc NN khi actor_type = PORTAL_CLIENT; có thể NULL khi actor_type = USER theo INTERNAL_PROXY_WITH_EVIDENCE và chưa bật portal khách)",
    "project_id": "uuid (NN)",
    "deliverable_id": "uuid (NN)",
    "actor_id": "uuid (NN — PORTAL_CLIENT hoặc USER đại diện hợp lệ được M14 xác thực)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (chỉ cho phép PORTAL_CLIENT hoặc USER proxy có chứng từ; SERVICE_PRINCIPAL bị chặn 403)",
    "actor_contact_id": "uuid | null (bắt buộc NN và khớp entry trong Projects.authorized_client_approvers[] khi actor_type = PORTAL_CLIENT; nullable khi USER proxy nội bộ kèm evidence_asset_id)",
    "expected_permission_version": "integer (bigint NN — M14 GUARDED_EXECUTION)",
    "expected_deliverable_version": "integer (bigint NN — CAS Deliverables.row_version)",
    "expected_asset_refs": [
      {
        "asset_id": "uuid (NN)",
        "asset_version_id": "uuid (NN — phải khớp đúng danh sách Asset_Versions đã publish)",
        "asset_checksum": "string (char(64) SHA-256 NN — đối chiếu Asset_Versions.content_sha256; tải qua SEC03 asset_domain = CONTRACT_OR_FINANCE_DOC với requires_watermark = true)"
      }
    ],
    "idempotency_key": "uuid (NN)",
    "decision": "ACCEPTED | REJECTED",
    "rejection_classification": "DEFECT | CHANGE | MIXED | null (bắt buộc non-null khi decision = REJECTED; nếu MIXED hệ thống tạo Revision_Items tách nhánh DEFECT không bị CR thương mại deadlock)",
    "feedback_summary": "string | null (bắt buộc non-null khi decision = REJECTED, max 10000 chars)",
    "evidence_asset_id": "uuid | null (bắt buộc IS NOT NULL và scan_status == CLEAN qua SEC03 khi actor_type = USER / INTERNAL_PROXY_WITH_EVIDENCE; tùy chọn với PORTAL_CLIENT)",
    "decision_recorded_at": "timestamptz (UTC)",
    "correlation_id": "uuid (NN)"
  },
  "RecordClientAcceptanceOutput": {
    "acceptance_id": "uuid (bản ghi Acceptances Nhóm C Append-Only bất biến)",
    "deliverable_id": "uuid",
    "deliverable_status": "ACCEPTED | REWORK",
    "deliverable_version": "integer (bigint)",
    "decision": "ACCEPTED | REJECTED",
    "verified_asset_refs": [
      {
        "asset_id": "uuid",
        "asset_version_id": "uuid",
        "asset_checksum": "string (char(64))"
      }
    ],
    "verified_package_sha256": "string (char(64))",
    "closed_client_wait_interval_id": "uuid | null",
    "wait_duration_minutes": "integer | null (>= 0)",
    "revision_batch_id": "uuid | null (khởi tạo khi decision = REJECTED)",
    "revision_batch_type": "DEFECT | CHANGE | MIXED | null",
    "revision_items_created": "integer (>= 0 — số dòng Revision_Items tách DEFECT vs CHANGE)",
    "quota_consumed_delta": "integer (0 với ACCEPTED hoặc DEFECT; +1 với CHANGE còn quota; 0 kèm ProjectChangeRequestRaised nếu hết quota)",
    "reopened_done_tasks": false,
    "idempotent_replay": "boolean",
    "recorded_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Khóa cứng Nghiệm thu (`M16-F04/05`, `INV-05`, `INV-11`, `CEO-U03`, `M16-AC02/03`, `ADR-002`):**
> - **Kiểm quyền Người ký Tại Server (`CEO-U03`, Write Port `SECURITY DEFINER`):**
>   - Khi `actor_type = 'PORTAL_CLIENT'`: `M14.EvaluateAccessDecision` xác nhận quyền trên `client_workspace_id` + `Contract_Workspace_Grants` còn hiệu lực, đồng thời Write Port kiểm cứng trên server **`actor_id == entry.portal_principal_id`** (khớp `app.current_principal_id`), `entry.contact_id == actor_contact_id` trong `Projects.authorized_client_approvers[]`, kiểm tại server **`now() BETWEEN grant_valid_from AND coalesce(grant_valid_until, 'infinity')`**, và kiểm **`max_acceptance_scope`** (`ALL_DELIVERABLES` hoặc `MILESTONE_ONLY` theo phạm vi được cấp).
>   - Khi `actor_type = 'USER'` (`INTERNAL_PROXY_WITH_EVIDENCE`): bắt buộc **`evidence_asset_id IS NOT NULL`** với `Asset_Versions.scan_status == 'CLEAN'` + `M14 READ` + `workspace_id` (thiếu trả `422 EVIDENCE_ASSET_REQUIRED`).
>   - Nếu bất kỳ điều kiện thẩm quyền nào không đạt $\rightarrow$ giữ bằng chứng phản hồi hoặc trả `403 AUTH_RBAC_FORBIDDEN` (`ACCEPTANCE_AUTHORITY_REQUIRED`), tuyệt đối không chuyển Deliverable sang `ACCEPTED`.
> - **Khớp Mảng `expected_asset_refs[]` & Version (`M16-AC02`):** Nếu danh sách `expected_asset_refs[]` (`asset_id`, `asset_version_id`, `asset_checksum`) hoặc `expected_deliverable_version` không khớp chính xác gói đang ở `CLIENT_REVIEW` $\rightarrow$ trả `409 TASK_VERSION_CONFLICT`.
> - **Phân loại `REJECTED` & Bảng `Revision_Items` (`DEFECT` vs `CHANGE`, `M16-F04`, `M16-AC03`, `CEO-U20`, `CX-U10`):**
>   - `DEFECT` (lỗi so với SOW đã cam kết): tạo `Revision_Batch` & các dòng **`Revision_Items (item_type = 'DEFECT', quota_consumed = false)`** (vẫn xử lý sửa ngay cả khi `used_revisions >= max_revisions`), sinh task sửa lỗi mới — **tuyệt đối không tự động reopen các `Tasks` đã `DONE` trước đó** (`reopened_done_tasks = false`).
>   - `CHANGE` (đổi ý/thêm yêu cầu): nếu còn `used_revisions < max_revisions`, tạo `Revision_Items (item_type = 'CHANGE', quota_consumed = true)` và tăng `used_revisions` (`quota_consumed_delta = +1`); nếu hết quota hoặc đổi phạm vi/hạn/chi phí $\rightarrow$ gắn CR (`Project_Change_Requests`) và phát `M16.ProjectChangeRequestRaised`. Trong batch `MIXED`, nhánh `DEFECT` trong `Revision_Items` được mở task sửa ngay, **tuyệt đối không bị deadlock bởi quy trình duyệt thương mại của CR `CHANGE`**. Phát `M16.DeliverableReworkRequested` & `M16.DeliverableRevisionBatchOpened`.
> - **Chốt `Client_Wait_Intervals` & Ghi `Acceptances` Nhóm C (`Redact-Before-Insert`):** Đóng `Client_Wait_Intervals` đang mở (`answered_at`, tính `duration_minutes >= 0` không cộng trùng `ENTITY-L2873`) và chèn bản ghi bất biến vào `Acceptances` (`Nhóm C`, cấm `UPDATE/DELETE` bởi app/worker role, `Redact-Before-Insert`).

### 2.6. Trụ cột 3A — `ListOpenWorkForPrincipalInput` & `ListOpenWorkForPrincipalOutput` (`M14-F06`, `UC12`, `UC-W09`, `W-T29`)

```json
{
  "ListOpenWorkForPrincipalInput": {
    "tenant_id": "uuid (NN)",
    "workspace_id": "uuid | null (NULL để quét toàn tenant qua fan-out từng workspace khi OFFBOARD; non-null khi BRANCH_TRANSFER/ROLE_CHANGE theo phạm vi cũ)",
    "offboarding_case_id": "uuid (NN)",
    "principal_id": "uuid (NN — user đang bị khóa hoặc chuyển bộ phận)",
    "actor_id": "uuid (NN — M14-F06 orchestrator hoặc Ops/Manager thực thi quét)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (PORTAL_CLIENT bị chặn 403)",
    "case_type": "OFFBOARD | BRANCH_TRANSFER | ROLE_CHANGE",
    "from_branch_id": "uuid | null",
    "include_categories": [
      "TASK",
      "TASK_OFFER",
      "TASK_REVIEW",
      "RECURRING_TEMPLATE",
      "QUEUE_MANAGER",
      "PROJECT_OWNER",
      "QA_REVIEWER",
      "TASK_CHANGE_APPROVER",
      "PROJECT_CHANGE_APPROVER"
    ],
    "cursor": "string | null",
    "limit": "integer (default 100, max 500)",
    "correlation_id": "uuid (NN)"
  },
  "ListOpenWorkForPrincipalOutput": {
    "offboarding_case_id": "uuid",
    "principal_id": "uuid",
    "total_open_items": "integer (>= 0)",
    "items": [
      {
        "item_category": "TASK | TASK_OFFER | TASK_REVIEW | RECURRING_TEMPLATE | QUEUE_MANAGER | PROJECT_OWNER | QA_REVIEWER | TASK_CHANGE_APPROVER | PROJECT_CHANGE_APPROVER",
        "item_id": "uuid",
        "workspace_id": "uuid",
        "branch_id": "uuid | null",
        "current_status": "string (với TASK bao gồm cả OPEN, IN_PROGRESS, và IN_REVIEW đang gắn current_assignee_id)",
        "due_at": "timestamptz | null (UTC)",
        "recommended_custodian_id": "uuid (suy xuất từ Work_Queues.queue_manager_user_id -> Branch Manager -> Tenant Owner)",
        "requires_recipient_acceptance": "boolean"
      }
    ],
    "next_cursor": "string | null"
  }
}
```

### 2.7. Trụ cột 3B — `TransferWorkOwnershipInput` & `TransferWorkOwnershipOutput` (`M14-F06`, `UC12`, `UC-W09`, `W-T29`)

```json
{
  "TransferWorkOwnershipInput": {
    "tenant_id": "uuid (NN)",
    "offboarding_case_id": "uuid (NN)",
    "from_principal_id": "uuid (NN)",
    "transfer_phase": "PHASE_1_CUSTODIAN_LOCK | PHASE_2_CONFIRMED_HANDOVER",
    "actor_id": "uuid (NN — M14-F06 orchestrator hoặc Manager/Confirmed Recipient)",
    "actor_type": "USER | SERVICE_PRINCIPAL | PORTAL_CLIENT (PORTAL_CLIENT bị chặn 403)",
    "expected_permission_version": "integer (bigint NN — M14 GUARDED_EXECUTION)",
    "idempotency_key": "uuid (NN)",
    "default_custodian_id": "uuid (NN cho PHASE_1_CUSTODIAN_LOCK — Custodian tạm thời tránh việc vô chủ)",
    "confirmed_recipient_id": "uuid | null (bắt buộc non-null cho PHASE_2_CONFIRMED_HANDOVER khi có item CONFIRMED; cho phép null khi handover_status = CANCELLED_BY_MANAGER; nếu non-null phải ACTIVE và đủ M14 grant tại workspace/branch đích)",
    "items": [
      {
        "item_category": "TASK | TASK_OFFER | TASK_REVIEW | RECURRING_TEMPLATE | QUEUE_MANAGER | PROJECT_OWNER | QA_REVIEWER | TASK_CHANGE_APPROVER | PROJECT_CHANGE_APPROVER",
        "item_id": "uuid",
        "workspace_id": "uuid",
        "expected_item_version": "integer | null (bigint CAS nếu item còn mở)",
        "target_user_id": "uuid | null (dùng target riêng hoặc fallback default_custodian_id / confirmed_recipient_id; null hợp lệ khi CANCELLED_BY_MANAGER)",
        "handover_status": "PENDING_ACCEPT | CONFIRMED | CANCELLED_BY_MANAGER"
      }
    ],
    "preserve_created_by_and_history": true,
    "reason": "string (NN, 1..1000 chars)",
    "correlation_id": "uuid (NN)"
  },
  "TransferWorkOwnershipOutput": {
    "offboarding_case_id": "uuid",
    "transfer_phase": "PHASE_1_CUSTODIAN_LOCK | PHASE_2_CONFIRMED_HANDOVER",
    "transferred_count": "integer (>= 0)",
    "results": [
      {
        "item_category": "TASK | TASK_OFFER | TASK_REVIEW | RECURRING_TEMPLATE | QUEUE_MANAGER | PROJECT_OWNER | QA_REVIEWER | TASK_CHANGE_APPROVER | PROJECT_CHANGE_APPROVER",
        "item_id": "uuid",
        "status": "TRANSFERRED | SKIPPED_ALREADY_CLOSED | CONFLICT | REJECTED_TARGET_INELIGIBLE",
        "new_owner_id": "uuid | null",
        "new_row_version": "integer | null",
        "preserved_created_by": true,
        "error_code": "string | null"
      }
    ],
    "idempotent_replay": "boolean",
    "processed_at": "timestamptz (UTC)"
  }
}
```

> **Quy tắc Bàn giao 2 Pha cho 9 Hạng mục `M16` (`M14-F06`, `UC12`, `UC-W09`, `W-T29`):**
> - **Pha 1 (`PHASE_1_CUSTODIAN_LOCK`):** Khi nhận `M14.UserOffboardingLocked`, ngay lập tức chuyển quyền giám hộ tạm sang `default_custodian_id` (hoặc `queue_manager_user_id`) đối với cả **9 hạng mục**: (1) **`TASK` đang `OPEN` / `IN_PROGRESS` / `IN_REVIEW`** (gắn `current_assignee_id = from_principal_id` để không mồ côi khi reject/withdraw), (2) `TASK_OFFER` đang chờ nhận (trả về queue có manager, giữ `queue_entered_at` ban đầu), (3) `TASK_REVIEW` đang chờ `from_principal_id` duyệt (chuyển reviewer queue/custodian, không auto-approve `SL01 L65`), (4) `RECURRING_TEMPLATE` (`Recurrence_Rules.default_assignee_id` / `Task_Templates.owner_user_id`) để lịch tiếp theo không sinh việc cho người đã nghỉ (`UC-W09`), (5) `QUEUE_MANAGER` để `Work_Queues.queue_manager_user_id` luôn `NOT NULL` (`W-O01`), (6) **`PROJECT_OWNER`** (`Projects.owner_id`, `Deliverables.owner_id`, `Client_Wait_Intervals.owner_id`), (7) **`QA_REVIEWER`** (`Deliverables.qa_reviewer_id` chưa `ACCEPTED/CANCELLED`), (8) **`TASK_CHANGE_APPROVER`** (`Task_Change_Requests` đang `PENDING`), và (9) **`PROJECT_CHANGE_APPROVER`** (`Project_Change_Requests` đang chờ duyệt tại `M16`).
> - **Pha 2 (`PHASE_2_CONFIRMED_HANDOVER`):** Khớp enum `handover_status` (`PENDING_ACCEPT | CONFIRMED | CANCELLED_BY_MANAGER`) với `C14`: khi `CONFIRMED`, bàn giao sang `confirmed_recipient_id` sau khi kiểm tra người nhận `ACTIVE` và đủ `M14` ACL trên `Task_Links` (tránh mở quyền ngầm khi bàn giao); khi **`CANCELLED_BY_MANAGER`**, cho phép `confirmed_recipient_id = null` và giữ nguyên Custodian/trạng thái an toàn mà không làm việc vô chủ. **Bắt buộc giữ nguyên `created_by` và toàn bộ lịch sử `Task_Assignments`, `Task_Submissions`, `Task_Reviews` cũ (`CEO-U15`, `UC12`).**
> - **Ánh xạ Rollup 9 Hạng mục `ListOpenWorkForPrincipal` vào 13 Category `M14-F06` (`C14:419-433`):** 5 hạng mục giữ nguyên 1-1 (`TASK`, `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER`); 4 hạng mục mở rộng rollup vào bộ tổng hợp `M14-F06` như sau: **`PROJECT_OWNER -> TASK`**, **`QA_REVIEWER -> TASK_REVIEW`**, và **`TASK_CHANGE_APPROVER / PROJECT_CHANGE_APPROVER -> PENDING_APPROVAL`**.

---

## 3. Domain Events Phát hành & Tiêu thụ (Qua Internal Outbox `M23-F12` — `ADR-005`)

> **Khóa Hạ tầng Outbox (`ADR-005`, `INV-23`):** Toàn bộ **11 sự kiện nghiệp vụ nội bộ** dưới đây được ghi nguyên tử vào **`M23-F12.Internal_Outbox_Events`** và vận chuyển trên **`Lane 2 (STANDARD_INTERACTIVE)`**. Tuyệt đối **không** đẩy các sự kiện nội bộ này vào `M19.Outbound_Intents` (`M19` chỉ xử lý tích hợp kênh ngoài và đồng bộ PMS ngoài `UC-W10`).

### 3.1. Envelope Chuẩn Mọi Sự kiện `M16` (`schema_version = "1.0"`)

```json
{
  "event_id": "uuid",
  "event_type": "M16.TaskCreated | M16.TaskDeadlineOrAssignmentChanged | M16.TaskLifecycleOrStageChanged | M16.TaskCompleted | M16.ProjectInitialized | M16.DeliverablePublishedForReview | M16.DeliverableReworkRequested | M16.DeliverableRevisionBatchOpened | M16.DeliverableAccepted | M16.ProjectChangeRequestRaised | M16.ClientWaitIntervalRecorded",
  "aggregate_type": "TASK | PROJECT | DELIVERABLE | REVISION_BATCH | ACCEPTANCE | CHANGE_REQUEST | CLIENT_WAIT_INTERVAL | WORK_QUEUE",
  "aggregate_id": "uuid",
  "aggregate_version": "integer (bigint >= 1)",
  "schema_version": "1.0",
  "tenant_id": "uuid",
  "workspace_id": "uuid",
  "occurred_at": "timestamptz (UTC)",
  "correlation_id": "uuid",
  "causation_id": "uuid | null",
  "payload": {
    "task_id": "uuid | null",
    "deliverable_id": "uuid | null",
    "status": "string",
    "detail_note": "Object field-map cụ thể theo từng dòng Sự kiện §3.2"
  }
}
```

### 3.2. Danh mục 11 Sự kiện Phát hành (`Published Events` via `M23-F12.Internal_Outbox_Events`)

| Event Name | Aggregate & Payload Trọng yếu | Consumers Bắt buộc | Hành động & Bất biến Phải thực thi phía Consumer |
|---|---|---|---|
| `M16.TaskCreated` | `task_id`, `workspace_id`, `work_type`, `visibility_scope` (`PRIVATE \| PERSONAL \| TEAM \| PROJECT \| EXPLICIT \| WORKSPACE` — ánh xạ `M16.Tasks.visibility` `PRIVATE\|TEAM\|PROJECT\|EXPLICIT` $\leftrightarrow$ `C14` `PERSONAL\|TEAM\|WORKSPACE`; `C14` lọc `NOT IN ('PERSONAL', 'PRIVATE', 'EXPLICIT')`), `source_module`, `source_business_key`, `episode_no`, `lifecycle_status`, `assignment_status`, `assignee_user_id`, `queue_id`, `reviewer_id`, `project_id`, `effective_due_at`, `is_sanitized_context`, `row_version` | `M24-F06`, `M24-F05`, `M21`, `M11`, `M02`, `M03`, `M18` | `M24-F06` chiếu vào read model `My Work` / `Team Board` có ACL; `M24-F05` (`M24.Internal_Notifications`) phát thông báo nội bộ sau commit và kiểm lại quyền recipient (không lộ title `PERSONAL`/`PRIVATE` hoặc context cấm `W-T02`/`W-T36`); `M21`/`M11`/`M02`/`M03` lưu liên kết ID thực thi & cập nhật projection `next_action_at` (`INV-04`); `M18` cập nhật WIP & cohort dự kiến |
| `M16.TaskDeadlineOrAssignmentChanged` | `task_id`, `workspace_id`, `work_type`, `source_module`, `source_business_key`, `previous_due_at`, `effective_due_at`, `committed_due_at`, `previous_assignee_user_id`, `new_assignee_user_id`, `new_queue_id`, `change_reason`, `changed_by_actor_id`, `row_version` | `M02`, `M24-F05`, `M24-F06`, `M18`, `M11` | `M02` cập nhật lại read projection `Leads/Deals.next_action_at` từ task follow-up đang mở mà không xóa breach/lịch sử (`INV-04`, `BR-W04`); `M24-F05` thông báo assignee/reviewer mới sau khi kiểm lại ACL; `M24-F06` làm mới Read Model; `M18` ghi nhận lần điều chỉnh hạn (`delay history`) mà giữ nguyên `original_due_at` |
| `M16.TaskLifecycleOrStageChanged` | `task_id`, `workspace_id`, `project_id`, `deliverable_id`, `work_type`, `previous_lifecycle`, `new_lifecycle`, `previous_stage_code`, `new_stage_code`, `stage_schema_version`, `assignment_status`, `submission_id`, `changed_by_actor_id`, `reason`, `row_version` | `M24-F06`, `M24-F05`, `M18`, `M02`, `M03`, `M11`, `M21` | `M24-F06` đồng bộ tức thì Read Model `My Work` & `Team Board` (`stage_code` khớp `Task_Board_Stages`); `M24-F05` gửi thông báo chuyển trạng thái (`IN_REVIEW`, `WITHDRAWN`, `REJECTED`, `REOPEN`, `CANCELED`) sau recheck ACL; `M18` tính `Review age` & `Reopen rate` theo `lifecycle`, không tính KPI từ `stage_code` (`BR-W02`); module nguồn đồng bộ trạng thái hiển thị (giữ nguyên `INV-05`) |
| `M16.TaskCompleted` | `task_id`, `workspace_id`, `work_type`, `source_module`, `source_business_key`, `episode_no`, `completed_by_user_id`, `completed_at`, `effective_due_at`, `submitted_on_time`, `completed_on_time`, `project_id`, `deliverable_id`, **`does_not_imply_acceptance: true`**, **`does_not_close_ticket_sla: true`**, **`does_not_confirm_contact_reach: true`** | `M02`, `M03`, `M04`, `M11`, `M12`, `M18`, `M21`, `M22`, `M24-F06` | Cập nhật trạng thái hiển thị `Task = DONE` ở module nguồn và `M18`/`M24-F06`. **Cấm tuyệt đối (`INV-05`, `W-T18`, `BR-P17`):** không tự đóng `Ticket`/`SLA` (`M11`), không tự đánh dấu khách đã liên hệ (`M02`/`M03`), không tự đóng khiếu nại/đối soát (`M21`), không tự phát `DeliverableAccepted` (`M08`), không tự phát `Paid` (`M09`), không tự phạt/thưởng lương (`M22`) |
| `M16.ProjectInitialized` | `project_id`, `agency_workspace_id`, `client_workspace_id`, `project_type`, `handoff_key`, `contract_id`, `sow_version_id`, `legal_entity_id`, `start_authorization_mode`, `committed_due_at`, `max_revisions`, `project_owner_id`, `deliverable_ids[]` | `M08`, `M15`, `M17`, `M18`, `M24-F06` | `M08` xác nhận hoàn tất bàn giao `Handoff -> Project` (`UC06`); `M15` gắn `project_id` vào kế hoạch/chiến dịch thực thi; `M17` áp khóa kiểm soát ngân sách theo `start_authorization_mode` (ví dụ `CREATIVE_ONLY_NO_MEDIA` chặn mở hạn mức media `CEO-U05`); `M18` & `M24-F06` cập nhật danh mục dự án & baseline |
| `M16.DeliverablePublishedForReview` | `deliverable_id`, `project_id`, `agency_workspace_id`, `client_workspace_id`, `contract_grant_id`, `deliverable_version`, `asset_refs[]`, `published_package_sha256`, `published_by_actor_id`, `published_at` | `M24-F06`, `M24-F05`, `M08`, `M18`, `M12` | `M24-F06` cập nhật Read Model `Deliverable` ở cả `AGENCY` & `CLIENT` projection; `M24-F05` gửi thông báo có liên kết an toàn tới `PORTAL_CLIENT` thuộc `authorized_client_approvers[]` (tải `asset_refs[]` qua `Download Gateway SEC03`, cấm nhúng dữ liệu nội bộ `AGENCY`); `M08`/`M18` cập nhật mốc `INTERNAL_REVIEW -> CLIENT_REVIEW` |
| `M16.DeliverableReworkRequested` | `deliverable_id`, `project_id`, `agency_workspace_id`, `client_workspace_id`, `deliverable_version`, `asset_refs[]`, `rejection_source` (`INTERNAL_QA \| CLIENT_REVIEW`), `classification` (`DEFECT \| CHANGE \| MIXED`), `requested_by_actor_id`, `reason`, `rework_requested_at` | `M24-F06`, `M24-F05`, `M08`, `M11`, `M18`, `M14-F08` | `M24-F06` cập nhật trạng thái `Deliverable = REWORK` cho Portal & Delivery Board; `M24-F05` cảnh báo PM/Delivery Lead/QA; `M08`/`M11` ghi nhận vòng trả sửa trên SOW/Ticket (`CX-U10`); `M18` & `M14-F08` (`Scorecard_Reviews`) lưu bối cảnh `DEFECT` vs `CHANGE` |
| `M16.DeliverableRevisionBatchOpened` | `revision_batch_id`, `deliverable_id`, `project_id`, `agency_workspace_id`, `batch_no`, `classification` (`DEFECT \| CHANGE \| MIXED`), `revision_items[]` (`[{item_id, item_type, quota_consumed, linked_project_cr_id, spawned_task_id}]`), `quota_consumed_delta`, `used_revisions_after`, `max_revisions`, `affected_user_ids[]`, `opened_at` | `M24-F06`, `M24-F05`, `M08`, `M18`, `M14-F08` | `M18` & `M14-F08` (`Scorecard_Reviews`) tiếp nhận `classification` + `affected_user_ids[]` để tách lỗi thực thi (`DEFECT`) khỏi đổi ý khách hàng (`CHANGE`) mà **không reopen Task cũ đã `DONE`** (`Q4`, `M14-AC03`); `M08` theo dõi biến động `used_revisions` / `max_revisions`; `M24-F06`/`M24-F05` cập nhật danh sách task sửa mới |
| `M16.DeliverableAccepted` | `acceptance_id`, `deliverable_id`, `project_id`, `agency_workspace_id`, `client_workspace_id`, `contract_id`, `sow_version_id`, `deliverable_version`, `asset_refs[]`, `verified_package_sha256`, `accepted_by_contact_id`, `accepted_at` | `M24-F06`, `M08`, `M09`, `M10-F04`, `M12-F01`, `M15-F05`, `M18` | `M24-F06` làm mới Read Model trạng thái `ACCEPTED` cho `AGENCY` & `CLIENT`; `M08` cập nhật tiến độ nghiệm thu theo SOW/Order; `M09` mở điều kiện phát hành đề nghị thu/hóa đơn theo milestone hợp đồng (không đồng nghĩa đã `Paid`); `M10-F04` ghi nhận nghiệm thu kỹ thuật làm bằng chứng phụ trợ (hoa hồng tính theo cash allocation `M09`); `M12-F01` đánh giá gửi CSAT/NPS; `M15-F05` mở cổng launch; `M18` ghi `Milestone reliability` |
| `M16.ProjectChangeRequestRaised` | `project_cr_id`, `project_id`, `deliverable_id`, `contract_id`, `sow_version_id`, `legal_entity_id`, `branch_id`, `request_type` (`SCOPE_CHANGE \| QUOTA_EXCEEDED_REVISION \| SCHEDULE_BASELINE_SHIFT \| COST_IMPACT`), `cost_delta`, `currency`, `schedule_delta_days`, `proposed_committed_due_at`, `touches_committed_due_at`, `raised_by_actor_id`, `revision_batch_id` | `M07`, `M08`, `M17`, `M23-F04` | `M07` khởi tạo báo giá/phụ lục sửa đổi nếu có tăng phạm vi/chi phí (`UC08`); `M08` giữ `committed_due_at` & hợp đồng gốc bất biến cho tới khi phụ lục được ký duyệt; `M17` rà soát điều chỉnh ngân sách dự án; `M23-F04` gọi `EvaluateApprovalMatrix` (`C23:77-78, 309`) đủ `legal_entity_id`, `branch_id`, `currency`, `cost_delta`, `schedule_delta_days`, `proposed_committed_due_at` & `touches_committed_due_at` |
| `M16.ClientWaitIntervalRecorded` | `client_wait_interval_id`, `project_id`, `deliverable_id`, `owner_id`, `user_id` (`= Client_Wait_Intervals.owner_id`), `affected_user_ids[]` (`= [Deliverables.owner_id, Tasks active assignees]`), `reason_code` (`= Client_Wait_Intervals.reason_code`), `requested_at`, `answered_at`, `duration_minutes` (`= EXTRACT(EPOCH FROM (coalesce(answered_at, now()) - requested_at))/60`), `is_open` (`= (answered_at IS NULL)`) | `M08`, `M14-F08`, `M17-F06`, `M18` | `M08` ghi nhận bằng chứng khách chậm phản hồi mà **không tự dời `committed_due_at`** (`CEO-U19`); `M14-F08` tách trừ thời gian chờ khách theo `user_id`/`owner_id` & `affected_user_ids[]` khỏi thẻ điểm vận hành nhân viên (`M16-AC04`); `M17-F06` cập nhật cảnh báo rủi ro tiến độ; `M18` báo cáo tách bạch `Client-Wait` vs `Blocked time` nội bộ |

> **Quy tắc Suy xuất Payload `M16.ClientWaitIntervalRecorded` từ DB (`M16.Client_Wait_Intervals` — `M16:450, 813`):**
> - `user_id`: suy xuất trực tiếp từ `Client_Wait_Intervals.owner_id` (người chịu trách nhiệm theo dõi đòi phản hồi khách hàng).
> - `affected_user_ids[]`: tập hợp `[Deliverables.owner_id]` hợp với các `Tasks.current_assignee_id` đang active (`lifecycle IN ('OPEN', 'IN_PROGRESS', 'IN_REVIEW')`) thuộc `deliverable_id` (hoặc `project_id` nếu `deliverable_id IS NULL`).
> - `reason_code`: lấy khớp cột `Client_Wait_Intervals.reason_code`.
> - `duration_minutes`: tính bằng `EXTRACT(EPOCH FROM (coalesce(answered_at, now()) - requested_at))/60`.
> - `is_open`: tính bằng `(answered_at IS NULL)`.

```json
{
  "ExampleTaskCompletedEvent": {
    "event_id": "11111111-2222-4333-8444-555555555555",
    "event_type": "M16.TaskCompleted",
    "aggregate_type": "TASK",
    "aggregate_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
    "aggregate_version": 5,
    "schema_version": "1.0",
    "tenant_id": "99999999-1111-4222-8333-444444444444",
    "workspace_id": "77777777-1111-4222-8333-444444444444",
    "occurred_at": "2026-11-16T05:10:00Z",
    "correlation_id": "cccccccc-1111-4222-8333-444444444444",
    "causation_id": "dddddddd-1111-4222-8333-444444444444",
    "payload": {
      "task_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
      "workspace_id": "77777777-1111-4222-8333-444444444444",
      "work_type": "CRM",
      "source_module": "M11",
      "source_business_key": "ticket:T-2026-001",
      "episode_no": 1,
      "completed_by_user_id": "55555555-1111-4222-8333-444444444444",
      "completed_at": "2026-11-16T05:10:00Z",
      "effective_due_at": "2026-11-16T08:00:00Z",
      "submitted_on_time": true,
      "completed_on_time": true,
      "project_id": null,
      "deliverable_id": null,
      "does_not_imply_acceptance": true,
      "does_not_close_ticket_sla": true,
      "does_not_confirm_contact_reach": true
    }
  }
}
```

### 3.3. Danh mục Sự kiện Liên Module mà `M16` Bắt buộc Tiêu thụ (`Subscribed Events`)

| Nguồn & Event | Hành vi Xử lý Idempotent Tại `M16` |
|---|---|
| **`M14.PermissionVersionBumped`** (`C14`) | Vô hiệu hóa cache kiểm quyền cục bộ của `principal_id`; từ chối ngay mọi lệnh `GUARDED_EXECUTION` (`Publish`, `Accept`, `Transfer`, Bulk, Background) đang giữ `expected_permission_version` cũ (`409 AUTH_PERMISSION_VERSION_STALE`); ép kiểm lại quyền recipient trước khi phát thông báo. |
| **`M14.UserOffboardingLocked`** (`C14`, `M14-F06`) | Kích hoạt ngay `ListOpenWorkForPrincipal` & `TransferWorkOwnership(PHASE_1_CUSTODIAN_LOCK)` cho đủ 9 hạng mục (`TASK [OPEN/IN_PROGRESS/IN_REVIEW theo current_assignee_id]`, `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER`, `PROJECT_OWNER`, `QA_REVIEWER`, `TASK_CHANGE_APPROVER`, `PROJECT_CHANGE_APPROVER`) về `default_custodian_id` (`queue_manager_user_id` fallback `Branch Manager`), giữ nguyên `created_by` & lịch sử (`UC12`, `W-T29`). |
| **`M14.WorkHandoverAssigned`** (`C14`, `M14-F06`) | Khi `handover_status = 'CONFIRMED'`, kích hoạt `TransferWorkOwnership(PHASE_2_CONFIRMED_HANDOVER)` chuyển giao đích danh sang `to_recipient_id` (`confirmed_recipient_id`, kiểm tra lại ACL đối với `Task_Links`); khi `CANCELLED_BY_MANAGER`, cho phép `confirmed_recipient_id = null` và giữ nguyên Custodian/hủy chờ bàn giao mà không làm việc vô chủ. |
| **`M14.WorkspaceActivated`** (`C14`, `UC14`) | Ghi nhận `client_workspace_id` vừa kích hoạt cùng `client_account_id` và `default_legal_entity_id` để cho phép ánh xạ tại `InitializeProjectFromHandoff` (vẫn yêu cầu `Contract_Workspace_Grants` hợp lệ trước mọi lượt `PublishDeliverableForClientReview`). |
| **`M20.SubjectErasureExecuted`** (`C20`, `UC11`, `W1-01`) | Tiêu thụ `deletion_ledger_id`, `erased_subject_refs[]`, `endpoint_hmac_hashes[]` & `subject_hmac_sha256`: truy tìm qua **cả 3 nguồn** (`Task_Links` trỏ `erased_subject_refs[]`, `subject_hmac_sha256`, và quét khớp mẫu/hash trong nội dung liên quan) để ẩn danh PII trên `Tasks` (`title`/`description`/`result_draft_text` gắn `privacy_redacted_at`), `Task_Comments`, `Task_Links` (cập nhật `target_tombstoned_at = now()` + xóa cache tóm tắt PII), `Assets` không thuộc hold (`REDACTED-SUBJECT-#...`), và cho phép **`privacy_erasure_system_role`** scrub PII **đa lần có kiểm soát theo từng `deletion_ledger_id`** trên `Task_Submissions` (`WHERE cardinality(active_legal_hold_ids) = 0 AND NOT (redacted_deletion_ledger_ids @> ARRAY[$deletion_ledger_id]::uuid[])`, nối `redacted_deletion_ledger_ids`, tăng `privacy_redaction_count`, cập nhật `privacy_redacted_at` & `redacted_content_sha256`, **bắt buộc giữ nguyên `content_sha256` gốc**). Giữ nguyên cấu trúc lịch sử và bảng `Nhóm C` đã `Redact-Before-Insert`. |
| **`M20.LegalHoldChanged`** (`C20`, `ADR-007`) | Xử lý đầy đủ mọi scope **`CONTRACT \| PROJECT \| DELIVERABLE \| TASK \| ASSET \| TICKET \| CONTACT \| ACCOUNT \| EMPLOYEE`**: cập nhật mảng **`active_legal_hold_ids uuid[]`** (`array_append` khi `status = 'ACTIVE'`, `array_remove` đúng `legal_hold_id` khi `RELEASED`) trên `Projects`, `Deliverables`, `Tasks`, `Acceptances`, `Task_Submissions`, `Task_Reviews` liên quan; khóa sửa/reopen/hủy/purge khi `cardinality(active_legal_hold_ids) > 0` và đồng bộ trạng thái `RESTRICTED_LEGAL_HOLD` cho `Download Gateway SEC03`. |
| **`M23.FeatureFlagUpdated`** (`M23-F09`) | Thực thi `Feature Flag Closure` (`RV20`): đóng/mở tức thì các endpoint & worker theo lát cắt (`SL01` text-only vs file upload `GAP-14`, `SL04` client publish/acceptance, `SL06` recurrence/dependencies, `P1` capacity/timesheet/PMS sync `UC-W10`), từ chối `404/422 CAPABILITY_DISABLED` khi tắt cờ. |
| **`M19.InboundEventPersisted`** (`C19` — *chỉ PMS sync `UC-W10`*) | Chỉ xử lý khi `provider = 'PMS'` và kết nối `Channel_Connections` + `External_Task_Mappings` đã verified (`W-O05`): đối chiếu `echo_operation_key` / `last_outbound_intent_id` + `external_version` để chặn echo loop (`W-T33`); cập nhật trạng thái/hạn theo `source_authority` từng field; xung đột đưa vào đối soát `CONFLICT`, tuyệt đối không last-write-wins. |
| **`M19.OutboundDispatchResulted`** (`C19` — *chỉ PMS sync `UC-W10` hoặc kênh ngoài*) | Cập nhật `External_Task_Mappings` (`last_outbound_intent_id`, `echo_operation_key`) từ `PENDING_SYNC` sang `SYNCED \| UNKNOWN_OUTCOME \| FAILED_TERMINAL \| CONFLICT` (`W-T32`: nếu PMS từ chối due/parent closed thì hiển thị lỗi nghiệp vụ rõ, không báo đã áp dụng ở nguồn) hoặc ghi nhận trạng thái thông báo kênh ngoài khi bật. |

---

## 4. Compatibility, Privacy & Test Matrix (`MODULE-SPEC` Aligned)

| Test ID | Mục tiêu Kiểm chứng Hợp đồng `C16` | Severity | Applicability | Status | Actual / Build / Fixture |
|---|---|---|---|---|---|
| `W-T01` / `W-T36` | Tạo `PERSONAL` task độc lập không cần Account/Contract giả; manager/dashboard team không lộ title, count hay attachment của task `PERSONAL` | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-W01-ACL` |
| `W-T02` / `BR-W09` / `BR-P17` | Target Verification Port chặn `403 TASK_TARGET_CONTEXT_ACL_DENIED` khi assignee thiếu quyền context và chặn `422 TARGET_ARCHIVED_FORBIDDEN` khi `archived_at IS NOT NULL`; `allow_sanitized_fallback` thiếu `sanitized_approval_ref` (`M23-F04`) trả `422 SANITIZED_FALLBACK_NOT_APPROVED`, không leak PII | `P0 Critical` | `SL01+` (`CRM/M21`) | `Not Run` | `Not Run / No Repo / Fixture-LINK-02` |
| `W-T03` / `W-T04` | Hai actor cùng `claim` task trên `Work_Queues` (`queue_manager_user_id NOT NULL` ngay lúc tạo) $\rightarrow$ 1 winner, 1 `409 TASK_VERSION_CONFLICT`; double submit `CreateTaskByBusinessKey` hoặc trùng `source_business_key` cùng payload replay, khác payload `409 IDEMPOTENCY_PAYLOAD_CONFLICT`; `Projects` `INTERNAL` chống trùng qua `idempotency_key` | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-CAS-03` |
| `W-T07` / `W-T09` / `INT23` | Revoke quyền assignee/reviewer giữa mở form và submit hoặc worker `GUARDED_EXECUTION` lệch `expected_permission_version` $\rightarrow$ `403`/`409`; Watcher gọi API đổi owner/hạn $\rightarrow$ `403 AUTH_RBAC_FORBIDDEN`; `AI_AGENT` thiếu `ai_draft_approval_token` bị chặn `403` dù giả `source_module` | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-REV-07` |
| `W-T10` / `W-T14` / `W-T15` / `W-T16` / `W-T17` | Kéo card không qua guard (`Task_Board_Stages`) hoặc thiếu checklist/`asset_version_ids[]` bẩn (`scan_status != CLEAN`) hoặc thiếu `M14 READ` + `workspace_id` $\rightarrow$ chặn; `WithdrawSubmission` đúng quyền/`expected_version` khi `IN_REVIEW` $\rightarrow$ `200 OK` (`IN_PROGRESS`, `WITHDRAWN`), sửa trực tiếp `Task_Submissions`/`SaveResultDraft` khi đang `IN_REVIEW` không rút $\rightarrow$ chặn `409/422`, Reviewer duyệt `submission_id` đã rút hoặc đua đồng thời rút và duyệt $\rightarrow$ `409 TASK_VERSION_CONFLICT`; self-review thiếu `override_approval_request_id` (`M23-F04`) bị chặn; approve callback lặp chỉ sinh 1 completion effect (`W1-04`) | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-RVW-15` |
| `W-T18` / `INV-05` | `M16.TaskCompleted` (`effective_due_at`) luôn mang `does_not_imply_acceptance: true`, `does_not_close_ticket_sla: true`, `does_not_confirm_contact_reach: true`; Task `DONE` không tự chấp thuận Deliverable, đóng Ticket, xác nhận reach, giải quyết case `M21` hay tính `Paid` | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-INV05-18` |
| `W-T19` / `W-T20` / `W-T21` | Parent `DONE` bị chặn khi còn mandatory child mở; `CancelTask` giữ graph lock chặn hủy cha còn con active/`DONE` trừ `CancelTaskFamily`; `ReopenTask`/`ReopenTaskFamily` bị chặn `422 DELIVERABLE_LOCKED_FOR_REOPEN` khi Deliverable `INTERNAL_REVIEW/CLIENT_REVIEW/REWORK/ACCEPTED` hoặc cây có `active_legal_hold_ids <> '{}'`; `Task_Dependencies` serialized không cycle | `P0 Critical` | `SL06+` | `Not Run` | `Not Run / No Repo / Fixture-DAG-21` |
| `W-T29` / `UC12` / `CEO-U15` | Nhận `M14.UserOffboardingLocked` & `M14.WorkHandoverAssigned` chuyển đủ 9 hạng mục (`TASK [OPEN/IN_PROGRESS/IN_REVIEW]`, `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER`, `PROJECT_OWNER`, `QA_REVIEWER`, `TASK_CHANGE_APPROVER`, `PROJECT_CHANGE_APPROVER`) qua 2 pha (`PENDING_ACCEPT -> CONFIRMED \| CANCELLED_BY_MANAGER` với `confirmed_recipient_id = null`), giữ nguyên `created_by` & lịch sử | `P0 Critical` | `SL01+` | `Not Run` | `Not Run / No Repo / Fixture-OFFB-29` |
| `M16-AC01` / `CEO-U04` / `CEO-U05` | 1 MSA có 2 SOW tạo đúng 2 `Projects` qua `InitializeProjectFromHandoff`; replay cùng `handoff_key`/`sow_version_id` không nhân bản; `PENDING_START` chặn `PublishTask`/`StartTask`/`Time_Entries`; `CREATIVE_ONLY_NO_MEDIA` không mở chi ngân sách ads | `P0 Critical` | `SL04+` | `Not Run` | `Not Run / No Repo / Fixture-PRJ-01` |
| `M16-AC02` / `CEO-U03` / `CEO-U17` / `U16` / `U17` | `PublishDeliverableForClientReview` kiểm `QA_PASSED` + `M20 CLEAN` + `M14 READ` + `Contract_Workspace_Grants` với mảng `asset_refs[]`; `RecordClientAcceptance` kiểm cứng server `actor_id == entry.portal_principal_id`, `grant_valid_from/until`, `max_acceptance_scope`, bắt buộc `evidence_asset_id CLEAN` khi `actor_type = USER`, lệch `expected_asset_refs[]` trả `409`, link `AGENCY` trả `404` | `P0 Critical` | `SL04+` | `Not Run` | `Not Run / No Repo / Fixture-ACC-02` |
| `M16-AC03` / `M16-AC04` / `CEO-U19` / `CEO-U20` | `RecordClientAcceptance(REJECTED)`: tạo `Revision_Items` tách `DEFECT` khỏi `CHANGE` trong `MIXED` (CR thương mại không deadlock `DEFECT`), `DEFECT` không trừ `max_revisions` & không auto-reopen task đã `DONE`; phát `M16.DeliverableReworkRequested` & `DeliverableRevisionBatchOpened` tới `M18`/`M14-F08`/`M24-F06`; `Client_Wait_Intervals` gắn `owner_id/user_id` | `P0 Critical` | `SL04+` | `Not Run` | `Not Run / No Repo / Fixture-REV-03` |
| `P-T32..34` / `W-T32..34` / `W-T38` / `W-T40` | `M21-F12` (`UC-P09`) tạo task exception idempotent theo `source_business_key`; notification/PMS lỗi không rollback task (`M23-F12` + `M24.Internal_Notifications` retry idempotent, `M19` PMS `CONFLICT` + `echo_operation_key`); source bị archive/erasure đặt `Task_Links.target_tombstoned_at` & scrub `Task_Submissions` đa lần theo từng `deletion_ledger_id` (`redacted_deletion_ledger_ids[]`, xóa đủ A rồi B ngoài Hold, giữ `content_sha256` gốc + cập nhật `redacted_content_sha256` — `W1-01`); offline PWA `client_operation_id` trả `409` khi conflict | `P0 Critical` | `SL01/SL08/P1` | `Not Run` | `Not Run / No Repo / Fixture-INT-32` |
