# ADR-009 — Ranh giới Kiến trúc `M16` (`Work / Projects / Task Core`), Client Acceptance, `Assets` Registry, Capacity & Hợp đồng Liên Module

**Status:** `Approved (Wave 1.5 Hardening — CR-20261116-WAVE1-5-HARDENING)`  
**Phạm vi:** `M16`, `C16` (`M16-TASK-CORE-COMMANDS`), `M14` (`C14`, `M14-F07`), `M23` (`F04 Approval_Requests/Decisions`, `F07`, `F10`, `F12`, `C23`), `M20` (`SEC03/F06`), `M02`, `M03`, `M07`, `M08`, `M11`, `M13`, `M15`, `M17`, `M18`, `M21`, `M22`, `M24`, `SL01`  
**Truy vết:** [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`3.10.1 L1132–1169`, `3.13.5 L1542–1543`, `3.14 L1552–1760`, `4.23 UC-W01–10 L2358–2442`, `5.13 L2770–2771, L2776–2777, L2783`, `5.18 L2873, L2881`, `5.20 L2913–2961`, `6.6 L3196–3225`, `8.5 L3429–3456`, `9.16 W-T01–40 L3847–3932`, `A.7 W-O01–07 L4222–4236`, `CEO-U03/17/19/20`), [INVARIANTS.md](../INVARIANTS.md) (`INV-01..06`, `INV-09..14`, `INV-22..25`), [ADR-002](ADR-002-ORG-ISOLATION-RLS-AND-SCOPE-FILTER.md), [ADR-003](ADR-003-PERMISSION-VERSION-CACHE-AND-MODE-GOVERNANCE.md), [ADR-004](ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md), [ADR-005](ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md), [ADR-006](ADR-006-DOWNLOAD-GATEWAY-REMOTE-FETCH-AND-AI-GATEWAY.md), [ADR-007](ADR-007-PRIVACY-CANONICAL-HASH-LEGAL-HOLD-AND-DR-FENCE.md), [ADR-008](ADR-008-OMNICHANNEL-CONTRACTS-RECEIPTS-AND-CROSS-EVENTS.md)

---

## Context

Để đồng bộ dứt điểm ranh giới kiến trúc cho `M16` (`Work / Projects / Task Core`) và `SL01` cùng cụm nền tảng Wave 1.5 (`CR-20261116-WAVE1-5-HARDENING`), cần khóa chặt 5 quyết định Q1–Q5 kèm các điều chỉnh chống trùng lặp & hoàn thiện event:

1. **Ranh giới Workspace cho Dự án & Nghiệm thu khách hàng (`AGENCY` vs `CLIENT`):** Chốt nơi lưu `Projects`, `Tasks` thực thi, `Task_Blockers`, bình luận nội bộ, `Time_Entries` và `standard_cost_rate` so với gói `Deliverables / Client Review / Acceptances` mà khách hàng (`PORTAL_CLIENT`) xem và ký duyệt qua RLS 2 chiều & Write Port `SECURITY DEFINER` (`ADR-002`, `INV-01/02`, `CEO-U17`).
2. **Liên kết `Tasks <-> Deliverables`, `Task_Links` & Phê duyệt Nội bộ vs Nghiệm thu Khách:** Khóa composite FK `Tasks.deliverable_id`, `Task_Links` (Typed Resource Columns + Target Verification Port), tách rõ **`M23-F04 Approval_Requests/Approval_Decisions (Nhóm C)`** cho duyệt **nội bộ** (`Project_Change_Requests`, `Task_Change_Requests`, `Self-Review Override`) với **`M16.Acceptances (Nhóm C)`** cho nghiệm thu khách hàng ngoài.
3. **Điểm mở `Queue`, Ranh giới ACL `M14` vs RACI `M16`, SSoT To-Do & Capacity (`M14-F07` vs `M16-F07`):** Khóa `Work_Queues.queue_manager_user_id NOT NULL` ngay lúc tạo, tách ranh giới `M14-F07` (`gross_available_hours_after_hr_leave`) với `M16-F07` (`net_available_minutes` sau `M23-F10` & `M13`) chống trừ 2 lần phép `M22`, và giữ SSoT `M16.Tasks` trước `M02` (`INV-04`).
4. **Reopen dưới cha `DONE` & Client Rework bảo toàn KPI (`8.5`):** Cơ chế `ReopenTaskFamily` atomic và luồng `Deliverable: ClientReview -> Rework` sinh `Revision_Batches` + `Tasks` sửa đổi mới mà không mở lại Task cũ đã `DONE`.
5. **Sở hữu `Assets / Asset_Versions` (`ENTITY-L2783`) & Hợp đồng Public `M16` (`11` Domain Events):** Đặt `Assets`/`Asset_Versions` tại Shared Platform Registry `M23` + `SEC03`, và khóa **3 nhóm cổng Command + 11 Domain Events chuẩn** của `M16` (bổ sung 3 event còn thiếu `M16.TaskLifecycleOrStageChanged`, `M16.DeliverableReworkRequested`, `M16.DeliverableRevisionBatchOpened`).

---

## Đề nghị (5 Quyết định Kiến trúc Đã Chốt Q1–Q5)

### 1. Q1 — Phân tách `AGENCY` vs `CLIENT` Workspace & Luồng `Client Acceptance` (`[MASTER]` + `[PROPOSED]`)

- **Dữ liệu nội bộ nằm tại `AGENCY workspace` (`INV-01`, `INV-02`):** Toàn bộ `Projects`, `Tasks` thực thi, `Task_Assignments`, `Task_Submissions`, `Task_Reviews` (QA nội bộ `InternalReview`), `Task_Blockers`, `Task_Comments` nội bộ, `Time_Entries`, `Resource_Allocations` và `standard_cost_rate` (`M14-F07`) được lưu và vận hành độc quyền trong **`AGENCY workspace`**.
- **Publish có chọn lọc sang `CLIENT workspace` (`M16-F03`, `CEO-U17`):** Chỉ khi một `Deliverable` vượt qua cổng QA nội bộ (`InternalReview -> ClientReview`), command `PublishDeliverableForClientReview` mới cập nhật phạm vi publish (`published_to_client_workspace_id`, `Deliverable_Asset_Refs` trỏ bản `Asset_Versions` có `scan_status = 'CLEAN'`) sang **`CLIENT workspace`** thông qua cầu nối **`M14.Contract_Workspace_Grants`** (`ADR-002`, `5.18 L2881`, `RV10`).
- **Cô lập tuyệt đối, RLS 2 chiều & Ký `Acceptances` (`M16-F05`, `CEO-U03`, `INV-05`, `ADR-002`):**
  - Khách hàng (`principal_type = PORTAL_CLIENT` trong `C14`) chỉ xem được gói Deliverable đã Publish theo rule RLS `SELECT`: `published_to_client_workspace_id = app.current_workspace_id AND status IN ('CLIENT_REVIEW', 'REWORK', 'ACCEPTED')` **hội với `Contract_Workspace_Grants` RLS 2 chiều đang `ACTIVE`**.
  - Ghi nhận nghiệm thu `RecordClientAcceptance` (và gửi phản hồi `REWORK`) đi qua **Write Port `SECURITY DEFINER`** kiểm cứng `actor_id == portal_principal_id` (`app.current_principal_id`), khớp `authorized_client_approvers[]`, `sow_version_id`, `asset_version_id` và `content_sha256` để ghi vào bảng bất biến **`M16.Acceptances` (`Nhóm C`)**; **tuyệt đối không dùng chung bảng `Acceptances` với sổ duyệt nội bộ `M23-F04`**.
  - **Cấm tuyệt đối** lộ `Task_Blockers`, comment nội bộ, `Time_Entries` hay `standard_cost_rate` sang `CLIENT workspace`, và không cho phép `PORTAL_CLIENT` mở link ngược vào hồ sơ `AGENCY` (`CEO-U17`).
  - `Task DONE` không tự kích hoạt `Client Acceptance` hoặc `Paid` (`INV-05`, `W-T18`).

### 2. Q2 — `Tasks <-> Deliverables`, `Task_Links`, `2-Tier Change Requests` & Phê duyệt Nội bộ `M23-F04`

- **Liên kết `Tasks <-> Deliverables` (`[PROPOSED]` trên nền `Master 5.13/5.20`):**
  - Bổ sung cột **`deliverable_id uuid NULL`** trên bảng `Tasks`.
  - Bắt buộc composite FK bảo đảm khi `deliverable_id IS NOT NULL` thì `Tasks.project_id IS NOT NULL`, `Tasks.tenant_id = Deliverables.tenant_id`, `Tasks.workspace_id = Deliverables.workspace_id` và **`Tasks.project_id = Deliverables.project_id`**.
- **`Task_Links` — Typed Resource Columns + Target Verification Port (`5.20 L2924`, `BR-W09`, `W-T02`, `W-T38`):**
  - Thay vì tạo 15 FK vật lý chéo bảng, `Task_Links` sử dụng bộ **Typed Resource Columns** (`target_module`, `target_resource_type`, `target_resource_id`, `target_workspace_id`, `relation_type`).
  - Trước khi ghi/đọc `Task_Links`, `M16` bắt buộc gọi Target Verification Port xác minh tồn tại và gọi `M14.EvaluateAccessDecision` kiểm ACL hai đầu (`Task` và `Target Resource` — `INV-02`, `W-T02`, `6.6 L3224`); hỗ trợ `sanitized_standalone_task` (`BR-W09`) khi có duyệt hợp lệ.
- **Tách cứng 2 tầng Change Requests & Phê duyệt Nội bộ `M23-F04` (`ADR-004`):**
  - **Tầng 1 — `Task_Change_Requests` (Nội bộ Task Core):** Dùng cho đổi `due_at` nội bộ, đổi `assignee_id` / `reviewer_id` nằm trong giới hạn `committed_due_at` và không đổi SOW/ngân sách (`UC-W04`), giữ nguyên `baseline_due_at` & breach lịch sử (`BR-W04`, `W-T12`).
  - **Tầng 2 — `Project_Change_Requests` (`5.13 L2771` — Cấp Dự án/Thương mại):** Mọi thay đổi tác động `scope_delta`, `cost_delta`, `schedule_delta`, hoặc vượt **`committed_due_at`** bắt buộc khởi tạo `Project_Change_Requests` và leo thang sang `M08`, `M07`, `M17`.
  - **Sổ Phê duyệt Nội bộ Dùng chung `M23-F04` (`Approval_Requests` `Nhóm A` + `Approval_Decisions` `Nhóm C`):** Toàn bộ luồng duyệt **nội bộ** của `M16` (`Project_Change_Requests`, `Task_Change_Requests` cần cấp quản lý duyệt, `Self-Review Override`) chạy trên `Approval_Requests` / `Approval_Decisions` của **`M23-F04`** (`ADR-004`), tách biệt hoàn toàn khỏi **`M16.Acceptances`** (dành riêng cho nghiệm thu khách hàng).

### 3. Q3 — `M16.Work_Queues`, Ranh giới `M14` vs `M16`, Capacity (`M14-F07` vs `M16-F07`) & SSoT To-Do (`INV-04`)

- **Khóa `M16.Work_Queues.queue_manager_user_id NOT NULL` ngay lúc tạo:**
  - `M16.Work_Queues` độc lập hoàn toàn với `M02.Queues` và `M03` Inbox queue; **bắt buộc cột `queue_manager_user_id uuid NOT NULL` ngay tại thời điểm tạo (`INSERT`)** (`BR-W01`, `W-O01` — cấm tạo queue tạm vô chủ rồi mới gán sau). Khi manager nghỉ việc, `M14-F06` khóa/bàn giao qua `Offboarding_Checklist_Items` loại `QUEUE_MANAGER`; giữ quy tắc `assignee_id XOR queue_id` khi phát hành Task.
- **Phân định `M14` (`C14`) vs `M16` RACI:**
  - **`M14` (`C14`):** Giữ cổng `EvaluateAccessDecision`, `CompileScopeFilter` (Entity-Mapped Compiler `ADR-002`) và `BindDbTransactionContext` (6 GUC). Bao gồm đầy đủ `resource_type` (`PROJECT`, `DELIVERABLE`, `TASK`, `WORK_QUEUE`, `TASK_TEMPLATE`, `RECURRENCE_RULE`, `TIME_ENTRY`, `RESOURCE_ALLOCATION`, `PARTNER_EXCEPTION_CASE`, `ASSET`) và `action` (`CLAIM`, `ACCEPT_OFFER`, `DECLINE_OFFER`, `SUBMIT_RESULT`, `PUBLISH_REVIEW`, `REOPEN`, `WAIVE_DEPENDENCY`).
  - **`M16` RACI Guards:** `Watcher` chỉ được `READ` và bị chặn `403` mọi sửa đổi (`W-T09`); `Assignee` bị chặn tự duyệt (`self-approve`, `W-T16`, `BR-W08`) trừ ngoại lệ hợp lệ qua `M23-F04 Approval_Requests/Decisions`.
- **Phân tách Chuỗi Tính Năng lực Nhân sự (`M14-F07` vs `M16-F07` — Chống Trừ 2 Lần Nghỉ phép `M22`):**
  - **`M14-F07` (`Capacity_Cost_Snapshots`):** Tiếp nhận `hr.availability.changed.v1` từ `M22` (chỉ trạng thái khả dụng, **không chứa lý do nghỉ phép hay lương `INV-02`, `6.8`**), cung cấp **`gross_available_hours_after_hr_leave`** (quỹ giờ khả dụng thô đã trừ sẵn ngày nghỉ phép/nghỉ bệnh HRM `M22`), kèm `standard_cost_rate` và `availability_status`.
  - **`M16-F07` (Resource Capacity & Allocation):** Nhận `gross_available_hours_after_hr_leave` từ `M14-F07` (**tuyệt đối KHÔNG trừ lại phép `M22`**), trừ tiếp ngày lễ / giờ làm việc chuẩn / `Quiet Hours` từ **`M23-F10` (`System_Calendars`)**, lịch hẹn từ **`M13` (`Appointments/Bookings`)**, và giờ đã phân bổ trong `Resource_Allocations` để xuất **`net_available_minutes`** (phút khả dụng ròng còn lại).
- **SSoT duy nhất cho To-Do (`INV-04`, `3.14 L1558`):** `M16.Tasks` là nguồn ghi duy nhất; `Leads.next_action_at` / `Deals.next_action_at` tại `M02` chỉ là projection chỉ đọc; `M02.Activities` lưu sự kiện đã xảy ra.

### 4. Q4 — `ReopenTaskFamily` Atomic & Luồng `ClientReview -> Rework` Bảo toàn KPI (`8.5`)

- **Chặn Reopen đơn lẻ dưới cha `DONE` (`BR-W07`, `W-T20`):** Cấm reopen đơn lẻ child task dưới parent `DONE`; bắt buộc gọi **`ReopenTaskFamily`** kèm **Impact Preview** (`W-T23`) và lý do hợp lệ, bảo toàn lịch sử submission/completion trước đó.
- **Luồng `Deliverable: ClientReview -> Rework` (`M16-F04`, `M16-AC03`, `CEO-U20`, `8.5`):**
  - Giữ nguyên 100% các `Tasks` vòng cũ ở trạng thái `DONE` cùng `Task_Submissions`/`Task_Reviews` (có áp ngoại lệ redact có kiểm soát theo từng `deletion_ledger_id` qua `redacted_deletion_ledger_ids[]`, cập nhật `redacted_content_sha256` và giữ nguyên `content_sha256` gốc bởi `privacy_erasure_system_role` nếu có yêu cầu xóa PII hợp pháp `ADR-004`), tránh làm méo KPI `first-pass acceptance` và `submitted_on_time`.
  - Tạo bản ghi **`Revision_Batches`** phân loại `DEFECT` (không trừ `used_revisions`, vẫn sửa khi hết quota) vs `CHANGE` (trừ quota hoặc mở `Project_Change_Requests`), sinh các `Tasks` sửa đổi mới gắn `revision_batch_id`, và phát đồng bộ sự kiện `M16.DeliverableReworkRequested` & `M16.DeliverableRevisionBatchOpened`.

### 5. Q5 — Shared Platform Asset Registry (`ENTITY-L2783`) & Hợp đồng Public `M16-TASK-CORE-COMMANDS` (`11` Domain Events)

- **`Assets` & `Asset_Versions` (`ENTITY-L2783`) tại `M23` + `Download Gateway SEC03` (`ADR-004`, `ADR-006`):**
  - `M23` quản trị bảng `Assets` (`Nhóm A`) & `Asset_Versions` (`Nhóm A`) tách riêng cho toàn hệ thống; cấp `asset_version_id (PENDING)` ngay lúc upload; mọi lượt tải đi qua `Download Gateway SEC03` kiểm `M14` (cả `ASSET` và `owner_resource`) + `M20` (`Asset_Versions.scan_status == 'CLEAN'`, `Deletion_Ledger`, `active_legal_hold_ids[]`, `6.8`) + `M23-F07` (Watermark/Audit).
  - `M16` chỉ giữ 2 bảng liên kết nghiệp vụ `Task_Assets` và `Deliverable_Asset_Refs` tham chiếu `asset_id` / `asset_version_id` và `approved_hash`.
- **Khóa cấu trúc Public Contract `02-specs/contracts/M16-TASK-CORE-COMMANDS.md` (`INV-05`):**
  - **3 Cổng Command Chính:**
    1. `CreateTaskByBusinessKey` (kèm `TaskLifecycleCommandNote`)
    2. Nhóm Project & Deliverable Ports: `InitializeProjectFromHandoff`, `PublishDeliverableForClientReview`, `RecordClientAcceptance`
    3. Nhóm Handover/Offboarding Ports: `ListOpenWorkForPrincipal`, `TransferWorkOwnership`
  - **11 Domain Events chuẩn qua Internal Outbox `M23-F12` (`Lane 2` — `ADR-005`, `INV-05`, `CR-20261116-WAVE1-5-HARDENING`):**
    1. `M16.TaskCreated`
    2. `M16.TaskDeadlineOrAssignmentChanged` *(cập nhật projection `next_action_at` cho `M02`, không xóa breach)*
    3. `M16.TaskCompleted` *(luôn mang `INV-05`: không tự đồng nghĩa `Client Accepted`, `Ticket Closed/SLA Stopped`, `Contact Reached` hay `Paid`)*
    4. `M16.ProjectInitialized` *(xác nhận bàn giao SOW/Order sang `M08`, `M15`, `M17`, `M18`)*
    5. `M16.DeliverablePublishedForReview` *(thông báo phát hành gói sạch sang `CLIENT workspace` qua `M14.Contract_Workspace_Grants`)*
    6. `M16.DeliverableAccepted` *(mở điều kiện xuất hóa đơn/thu tiền `M09` & khảo sát `M12`, chưa đồng nghĩa `Paid`)*
    7. `M16.ProjectChangeRequestRaised` *(kích hoạt đánh giá SOW/chi phí/ngân sách tại `M08`, `M07`, `M17` qua `M23-F04 Approval_Requests/Decisions`)*
    8. `M16.ClientWaitIntervalRecorded` *(bằng chứng chờ khách cho `M08`/`M14-F08`/`M18`, không tự dời `committed_due_at`)*
    9. **`M16.TaskLifecycleOrStageChanged`** *(đồng bộ thay đổi `lifecycle_status` / `stage` trên Task cho `M24-F06` Read Model, `M24-F05` Notifications, `M18` BI và đồng bộ `M19` PMS `UC-W10`)*
    10. **`M16.DeliverableReworkRequested`** *(thông báo chuyển `Deliverable` từ `CLIENT_REVIEW`/`INTERNAL_REVIEW` sang `REWORK` kèm `classification = DEFECT | CHANGE | MIXED` và cập nhật quota `used_revisions` tới `M08`, `M11`, `M18`, `M24-F05/F06`)*
    11. **`M16.DeliverableRevisionBatchOpened`** *(thông báo mở `Revision_Batches` mới kèm danh sách `Tasks` sửa đổi gắn `revision_batch_id` phục vụ `M18` đo KPI `8.5` và `M24-F06`)*

---

## So sánh

- **Để `M16` tự trừ lại phép `M22`, dùng chung `Acceptances` cho duyệt nội bộ, cho phép `Work_Queues` thiếu `queue_manager_user_id`, hoặc bỏ sót 3 event lifecycle/rework:** Gây lỗi trừ kép quỹ giờ nhân sự, trộn lẫn bằng chứng pháp lý khách hàng với quy trình nội bộ, tạo hàng chờ mồ côi khi offboarding, và làm `M24-F06`/`M18`/`M19 PMS` bị mù trạng thái task/rework. Khóa chặt theo 5 điểm Q1–Q5 giải quyết dứt điểm mọi đứt gãy.

## Hệ quả và điều kiện thay đổi

- Cập nhật [M16-WORK-PROJECTS-TASK-CORE.md](../../02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md), [M16-TASK-CORE-COMMANDS.md](../../02-specs/contracts/M16-TASK-CORE-COMMANDS.md) (`11 Domain Events`, `queue_manager_user_id NOT NULL`, `M14-F07` vs `M16-F07`, `M23-F04 Approval_Requests/Decisions`), [M14-ORG-ACCESS-DELEGATION.md](../../02-specs/modules/M14-ORG-ACCESS-DELEGATION.md) (`M14-F07` `gross_available_hours_after_hr_leave`), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), `C23`, `C24`, và [INDEX.md](../INDEX.md).
