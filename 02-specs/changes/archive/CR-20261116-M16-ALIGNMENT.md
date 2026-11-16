# Change Proposal: `CR-20261116-M16-ALIGNMENT`

> **Luồng OpenSpec (`Propose -> Apply -> Archive`):** Tệp đề xuất đồng bộ kiến trúc và hợp đồng liên module cho đợt bóc tách module **`M16` (`Work / Projects / Task Core`)**, khóa 5 quyết định Q1–Q5 đã chốt với Chủ dự án thông qua [ADR-009](../../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md).

---

## 1. Thông tin đề xuất

- **Mã đề xuất:** `CR-20261116-M16-ALIGNMENT`
- **Trạng thái:** `Applied (ADR-009, INDEX.md, C14, M23, SL01, M16 & C16 Đồng bộ Đầy đủ)`
- **Baseline Master tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`)
- **Phân loại nguồn:** `[MASTER-CLARIFICATION]` + `[PROPOSED-EXTENSION]`
- **Tài liệu bị ảnh hưởng:**
  - Architecture ADRs (`01-architecture/decisions/`): Tạo mới [ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md](../../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md)
  - Architecture Navigation: [INDEX.md](../../../01-architecture/INDEX.md) *(bổ sung `ADR-009` & ghi chú SSoT Shared Platform Asset Registry `Assets/Asset_Versions` `ENTITY-L2783`)*
  - Public Contracts (`02-specs/contracts/`): Cập nhật additive trên [M14-PRINCIPAL-ACCESS-DECISION.md](../../contracts/M14-PRINCIPAL-ACCESS-DECISION.md) *(Mục `2.2`: thêm `WORK_QUEUE`, `TASK_TEMPLATE`, `RECURRENCE_RULE`, `TIME_ENTRY`, `RESOURCE_ALLOCATION`, `PARTNER_EXCEPTION_CASE` & 7 `action` + tham chiếu `CR-20261116-M16-ALIGNMENT`/`ADR-009`, giữ Status `Reviewed`)*; đồng thời phát hành hợp đồng [M16-TASK-CORE-COMMANDS.md](../../contracts/M16-TASK-CORE-COMMANDS.md)
  - Module Specs (`02-specs/modules/`): Phát hành đặc tả đích [M16-WORK-PROJECTS-TASK-CORE.md](../../modules/M16-WORK-PROJECTS-TASK-CORE.md); cập nhật delta nhẹ trên [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) *(`Assets/Asset_Versions` `ENTITY-L2783` + `Download Gateway SEC03`, `M16` trong `M23-F04` Approval Matrix cho `Project_Change_Requests` & `Self-Review Override`, và `M23-F11`)*; đính chính 1 câu diễn đạt trên `Contract_Workspace_Grants` của [M14-ORG-ACCESS-DELEGATION.md](../../modules/M14-ORG-ACCESS-DELEGATION.md) *(Mục `4.2`, không đổi schema, giữ nguyên `Reviewed`)*
  - Slices (`02-specs/slices/`): Cập nhật delta nhẹ trên [SL01-INTERNAL-WORK.md](../../slices/SL01-INTERNAL-WORK.md) *(khóa điểm mở `Queue/grants/membership` dòng `~95` sang `M16.Work_Queues` có `queue_manager_user_id NOT NULL`)*

---

## 2. Lý do thay đổi & Phạm vi (Why & What)

- **5 Quyết định Kiến trúc đã chốt với Chủ dự án (Q1–Q5 trong `ADR-009`):**
  1. **Q1 — Phân tách Workspace & Client Acceptance (`[MASTER]` + `[PROPOSED]`):** Đặt toàn bộ `Projects`, `Tasks` thực thi, QA nội bộ (`InternalReview`), blockers, comments nội bộ, `Time_Entries` và `standard_cost_rate` tại **`AGENCY workspace`**. Chỉ Publish các gói `Deliverable / Client Review` đã qua QA (`M16-F03`) sang **`CLIENT workspace`** thông qua `M14.Contract_Workspace_Grants` để `PORTAL_CLIENT` xem và ký `Acceptances` (`CEO-U03`, `CEO-U17`, `INV-01/02/05`).
  2. **Q2 — `Tasks <-> Deliverables`, `Task_Links` & 2-Tier Change Requests (`[MASTER]` + `[PROPOSED]`):** Bổ sung `deliverable_id uuid NULL` trên `Tasks` với composite check cùng `project_id` và `workspace_id`; `Task_Links` dùng Typed Resource Columns (`target_module`, `target_resource_type`, `target_resource_id`, `target_workspace_id`, `relation_type`) + Target Verification Port kiểm ACL `M14` hai đầu và hỗ trợ `sanitized_standalone_task` (`BR-W09`, `W-T02`, `W-T38`, không dùng 15 FK vật lý chéo bảng); tách cứng `Task_Change_Requests` (đổi hạn/người nội bộ trong khung `committed_due_at`) khỏi `Project_Change_Requests` (`5.13 L2771`, đổi SOW/chi phí/`committed_due_at` leo thang sang `M08`/`M07`/`M17`).
  3. **Q3 — `Work_Queues`, Ranh giới `M14` vs `M16` RACI & SSoT To-Do (`[MASTER]` + `[PROPOSED]`):** Tạo bảng `Work_Queues` độc lập tại `M16` (bắt buộc `queue_manager_user_id NOT NULL`, tách khỏi `M02` Lead Queue & `M03` Inbox, khóa `SL01 L95`); mở rộng additive `C14` (`resource_type`: `WORK_QUEUE`, `TASK_TEMPLATE`, `RECURRENCE_RULE`, `TIME_ENTRY`, `RESOURCE_ALLOCATION`, `PARTNER_EXCEPTION_CASE`; `action`: `CLAIM`, `ACCEPT_OFFER`, `DECLINE_OFFER`, `SUBMIT_RESULT`, `PUBLISH_REVIEW`, `REOPEN`, `WAIVE_DEPENDENCY`) trong khi `M16` kiểm RACI nội bộ (`Watcher` cấm sửa `W-T09`, `Assignee` cấm self-approve `W-T16`); giữ `M16.Tasks` là SSoT duy nhất cho việc cần làm (`Leads.next_action_at` / `Deals.next_action_at` chỉ là projection từ follow-up task đang mở theo `INV-04`, còn `M02.Activities` là việc đã xảy ra).
  4. **Q4 — `ReopenTaskFamily` & `ClientReview -> Rework` (`[MASTER]` + `[PROPOSED]`):** Chặn reopen đơn lẻ dưới cha `DONE`, bắt buộc gọi command `ReopenTaskFamily` atomic có preview tác động (`BR-W07`, `W-T20`); khi khách trả `Deliverable` ở `ClientReview -> Rework` (`M16-F04`), giữ nguyên lịch sử Task cũ ở `DONE` (bảo toàn KPI `first-pass acceptance` / `submitted_on_time` tại `8.5`), tạo `Revision_Batch` phân loại `DEFECT` (không trừ quota `M16-AC03`, `CEO-U20`) vs `CHANGE` (tính quota/CR) và sinh Task sửa đổi mới gắn vào batch đó.
  5. **Q5 — Shared Platform Asset Registry & Public Contract `M16` (`[MASTER]` + `[PROPOSED]`):** Đặt `Assets` & `Asset_Versions` (`ENTITY-L2783`) làm Shared Platform Asset Registry dùng chung (`M03/M07/M08/M15/M16/M22`) tích hợp chuỗi `Download Gateway SEC03` (`M14 ACL + M20 Privacy/Scan + M23-F07`), còn `M16` chỉ giữ `Task_Assets` & `Deliverable_Asset_Refs`; khóa đặc tả `02-specs/contracts/M16-TASK-CORE-COMMANDS.md` gồm 3 cổng Command (`CreateTaskByBusinessKey`; `InitializeProjectFromHandoff` + `PublishDeliverableForClientReview` / `RecordClientAcceptance`; `ListOpenWorkForPrincipal` / `TransferWorkOwnership`) và 8 Domain Events qua `M23-F12` (`INV-05`).
- **Không thuộc phạm vi (Non-goals):**
  - Không sửa `00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md` (`v1.9` giữ nguyên SHA-256).
  - Không sinh mã nguồn ứng dụng, DDL SQL migration hay chạy test phần mềm (`Documentation-Only`).
  - Không tạo breaking change đối với `Output` hoặc logic 7 bước của `C14`, giữ nguyên schema & Status `Reviewed` của `M14-ORG-ACCESS-DELEGATION.md` và `M20-PRIVACY-CONSENT-RETENTION.md` (`M14` chỉ đính chính 1 câu diễn đạt trên `Contract_Workspace_Grants` khớp `Q1`; `M14` đã hỗ trợ `PORTAL_CLIENT`, `Teams.queue_manager_user_id` và 8 nhóm `Offboarding_Checklist_Items`; `M20` đã có `EvaluateAssetDownloadPrivacyGate` `SEC03` cho `ENTITY-L2783`).
  - Các cập nhật đồng bộ toàn kho (`02-specs/README.md`, `03-planning/GAPS.md`, `03-planning/DECOMPOSITION-PLAN.md`, `03-planning/agent/PROGRESS.md`, `active-task.json`) được thực hiện tại bước Coordinator tổng hợp cuối cùng sau Fresh-Context Audit.

---

## 3. Phân tích tác động (Impact & Breaking Check)

- **Breaking Contract Change?** `Không` — Cập nhật trên [M14-PRINCIPAL-ACCESS-DECISION.md](../../contracts/M14-PRINCIPAL-ACCESS-DECISION.md) là **additive-only** ở tập enum `resource_type` (5 giá trị) và `action` (7 giá trị) trong `EvaluateAccessDecisionInput` (tất cả consumer hiện hữu của Wave 1 không bị ảnh hưởng); đồng thời thiết lập hợp đồng mới cho `02-specs/contracts/M16-TASK-CORE-COMMANDS.md`.
- **Ảnh hưởng [INVARIANTS.md](../../../01-architecture/INVARIANTS.md):** Tuân thủ và củng cố `INV-01`, `INV-02`, `INV-04`, `INV-05`, `INV-06`, `INV-09`, `INV-10`, `INV-11`, `INV-12`, `INV-13`, `INV-14`, `INV-22`, `INV-23`, `INV-24`.
- **Đối soát `M14-ORG-ACCESS-DELEGATION.md` & `M20-PRIVACY-CONSENT-RETENTION.md`:**
  - [M14-ORG-ACCESS-DELEGATION.md](../../modules/M14-ORG-ACCESS-DELEGATION.md) đã trỏ `resource_type` trực tiếp về enum `C14`, hỗ trợ `PORTAL_CLIENT`, `Contract_Workspace_Grants` (đã đính chính diễn đạt theo `Q1` tại Mục `4.2`), `Entity_Team_Grants` và liệt kê đủ `TASK`, `TASK_OFFER`, `TASK_REVIEW`, `RECURRING_TEMPLATE`, `QUEUE_MANAGER` trong `Offboarding_Checklist_Items` $\rightarrow$ không thay đổi schema/contract và giữ nguyên Status `Reviewed`.
  - [M20-PRIVACY-CONSENT-RETENTION.md](../../modules/M20-PRIVACY-CONSENT-RETENTION.md) đã giữ cổng `EvaluateAssetDownloadPrivacyGate` (`SEC03`, `ADR-006`) trên `Assets` (`ENTITY-L2783`) $\rightarrow$ tương thích hoàn toàn với mô hình Shared Platform Asset Registry tại `M23` + `SEC03` mà không phát sinh xung đột SSoT.
- **Ảnh hưởng Test Matrix (`W-T01..40`, `M16-AC01..04`):** Toàn bộ ca kiểm thử vẫn ở trạng thái **`Not Run`** (giai đoạn `Documentation-Only`).

---

## 4. Kế hoạch áp dụng (`Apply` Checklist)

- [x] Chốt 5 quyết định Q1–Q5 và ban hành [ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md](../../../01-architecture/decisions/ADR-009-M16-WORK-PROJECTS-TASK-CORE-BOUNDARIES.md).
- [x] Cập nhật [INDEX.md](../../../01-architecture/INDEX.md) (thêm `ADR-009` & ghi chú SSoT `Assets / Asset_Versions` `ENTITY-L2783`).
- [x] Cập nhật additive trên [M14-PRINCIPAL-ACCESS-DECISION.md](../../contracts/M14-PRINCIPAL-ACCESS-DECISION.md) (Mục `2.2` `resource_type` & `action` + tham chiếu CR/ADR, giữ nguyên `Reviewed`).
- [x] Cập nhật delta nhẹ trên [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) (Shared Platform Asset Registry `ENTITY-L2783` + `Download Gateway SEC03` và phạm vi `M16` trong `M23-F04`).
- [x] Cập nhật delta nhẹ trên [SL01-INTERNAL-WORK.md](../../slices/SL01-INTERNAL-WORK.md) (khóa điểm mở dòng `~95` theo `ADR-009`: `M16.Work_Queues` riêng bắt buộc `queue_manager_user_id NOT NULL`).
- [x] Áp dụng đầy đủ vào đặc tả đích [M16-WORK-PROJECTS-TASK-CORE.md](../../modules/M16-WORK-PROJECTS-TASK-CORE.md) & [M16-TASK-CORE-COMMANDS.md](../../contracts/M16-TASK-CORE-COMMANDS.md), đính chính `Contract_Workspace_Grants` trên `M14`, cập nhật `02-specs/README.md` / `03-planning/GAPS.md` / `03-planning/DECOMPOSITION-PLAN.md` / `PROGRESS.md` / `active-task.json`, vá sạch kết quả Fresh-Context Re-Audit và chạy đủ 4 cổng kiểm chứng `05-tools/`.
