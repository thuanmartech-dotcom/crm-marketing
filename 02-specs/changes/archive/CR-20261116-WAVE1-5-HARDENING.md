# Change Proposal: `CR-20261116-WAVE1-5-HARDENING`

> **Luồng OpenSpec (`Propose -> Apply -> Archive`):** Hồ sơ đồng bộ và vá toàn diện cụm **Wave 1 (`M14/C14`, `M20/C20`, `M19/C19`, `M16/C16`)** cùng trục nền tảng **`M23/C23`, `M24/C24`, `SL01`, `ADR-002..009`, `03-planning/GAPS.md`**, chốt theo phiên phỏng vấn `/grill-me` 6 nhánh ngày `16/11/2026` trước khi phê duyệt `Reviewed` toàn cụm và chuyển **Wave 2 (`M01`)**.

---

## 1. Thông tin đề xuất

- **Mã đề xuất:** `CR-20261116-WAVE1-5-HARDENING`
- **Trạng thái:** `Applied & Archived (16/11/2026 — Vượt Fresh-Context Re-Audit Wave 1.5 với CRITICAL: 0, HIGH: 0, MEDIUM: 0; Tests: Not Run)`
- **Baseline Master tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`)
- **Phân loại nguồn:** `[MASTER-CLARIFICATION]` + `[PROPOSED-EXTENSION]`
- **Quyết định `/grill-me` 6 nhánh đã chốt với Chủ dự án:**
  1. **Nhánh #1 (Lộ trình Wave 1.5):** Mở ngay **Wave 1.5** nâng chuẩn đầy đủ `M23` & `M24` (kèm Public Contracts mới **`C23`** & **`C24`**), vá toàn bộ lỗ hổng kỹ thuật liên module Wave 1, đồng bộ `SL01`/`GAPS.md` và gỡ miễn kiểm `--strict-all` cho `M23`/`M24`/`SL01` trong `verify_module_spec.py` trước khi sang Wave 2 (`M01`).
  2. **Nhánh #2 (`FORCE RLS` & Entity-Mapped `CompileScopeFilter`):** Giữ `Deliverables`/`Acceptances` tại `AGENCY` với RLS `SELECT` 2 chiều có điều kiện (`published_to_client_workspace_id = current_ws` + `status IN ('CLIENT_REVIEW','REWORK','ACCEPTED')` + `Contract_Workspace_Grants` active) + Write Gateway Port `SECURITY DEFINER` kiểm cứng `actor_id == portal_principal_id` cho `PORTAL_CLIENT`; tách `SECURITY DEFINER` Bootstrap Resolver tối thiểu cho `M19` Webhook (`(provider, provider_namespace, webhook_token)`) + fan-out từng workspace cho `Offboarding` / `VerifyPostRestoreComplianceGate`; thay AST cột cứng trong `C14` thành **Entity-Mapped Compiler** và tách `Nhóm B-Catalog` vs `Nhóm B-Governance-Sensitive`.
  3. **Nhánh #3 (`DR Startup Fence`, `permission_version` Rollback & Xoay khóa `HMAC`):** Đảo thứ tự `ADR-007` — khóa toàn 3 làn + `M16` Schedulers $\rightarrow$ chạy `M14` Security Reconciliation từ PITR #6 **`M14.Security_Revocation_Ledger`** + nhảy cóc `acl_epoch / permission_version` vượt mốc trước sự cố + xóa 100% session `M23-F02` & cache `M24-F06` + hủy/dịch timer (`offer_expires_at`, `hold_expires_at`) + chạy `M20.VerifyPostRestoreComplianceGate` (bao phủ cả `M23-F12.Internal_Outbox_Events`) **TRƯỚC** khi replay `M23-F12` và mở lại worker; tách khóa HMAC & lưu `hmac_key_version` trên mọi bảng HMAC kèm tra cứu multi-version (`ACTIVE + VERIFY_ONLY`).
  4. **Nhánh #4 (PII Erasure vs `Nhóm C`/`Task_Submissions` & Multi-`Legal_Hold`):** Quy định **Redact-Before-Insert** cho mọi bảng `Nhóm C` + cho phép `privacy_erasure_system_role` scrub PII đúng 1 lần trên `Task_Submissions` (ghi `privacy_redacted_at`, giữ nguyên `content_sha256` gốc khi không vướng hold); bổ sung `erased_subject_refs[]` trên `M20.SubjectErasureExecuted` (thêm `M14`/`M23`/`M24` + thu hồi `Export_Requests`); thay `legal_hold_status` đơn trị bằng mảng **`active_legal_hold_ids uuid[] DEFAULT '{}'`** + thêm `PROJECT | DELIVERABLE | TASK` vào `M20.Legal_Holds`.
  5. **Nhánh #5 (`ENTITY-L2783` `Assets`/`Approvals`, Capacity/Scorecard & Wire Liên Module):** Tách 2 bảng `Assets` & `Asset_Versions` và đặt `Approval_Requests` + `Approval_Decisions` (`Nhóm C`) làm Sổ duyệt nội bộ dùng chung tại **`M23-F04`** (tách biệt khỏi `M16.Acceptances`); `M14-F07` giữ `gross_available_hours_after_hr_leave` + `standard_cost_rate` + `availability_status`, còn `M16-F07` trừ tiếp lịch `M23-F10` & `M13` ra `net_available_minutes` (chống trừ 2 lần phép `M22`); bổ sung wire `C16 -> M18/M24-F06/M14-F08`; khoanh vùng rule chặn `BANK/HRM` tại `C20:105` riêng cho `AI_*` (mở cho `M19_EXTERNAL_WEBHOOK`); bổ sung `PMS` / `TASK_SYNC` / `CONFLICT` vào `C19`/`M16`; phủ đủ 13 hạng mục `M14-F06` & vá state machines `Tasks`/`Deliverables`/`Outbound_Intents`/`Channel_Connections`.
  6. **Nhánh #6 (Chốt chi tiết cuối & Áp dụng ngay):** Khóa `Work_Queues.queue_manager_user_id NOT NULL` ngay từ lúc tạo; hợp nhất 5 giá trị `Task_Blockers.blocker_type` (`CLIENT_INPUT | INTERNAL_DEPENDENCY | TECHNICAL | APPROVAL_WAIT | RESOURCE`); tách rõ `ONFR05` (`5 phút` phát hiện) với `[OPEN-GAP: GAP-M19-11]` (`[PROPOSED] 15 phút/đợt` gom cảnh báo); sửa `C16` thành `Wave 1` và áp dụng đồng bộ ngay qua đội Worker tách phạm vi ghi + Fresh-Context Re-Audit.

---

## 2. Danh sách Tài liệu Chịu Tác động (`Scope Map`)

- **Kiến trúc & ADRs (`01-architecture/`):** [INDEX.md](../../../01-architecture/INDEX.md), `ADR-002` .. `ADR-009`.
- **Nền tảng Mới & Nâng chuẩn (`M23/C23`, `M24/C24`):**
  - `02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md` + mới `02-specs/contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md` (`C23`)
  - `02-specs/modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md` + mới `02-specs/contracts/M24-PRODUCTIVITY-CACHE-QUEUE.md` (`C24`)
- **Wave 1 Specs & Contracts:**
  - `02-specs/modules/M14-ORG-ACCESS-DELEGATION.md` + `02-specs/contracts/M14-PRINCIPAL-ACCESS-DECISION.md` (`C14`)
  - `02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md` + `02-specs/contracts/M20-SUPPRESSION-PRIVACY-GATE.md` (`C20`)
  - `02-specs/modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md` + `02-specs/contracts/M19-DURABLE-INGEST-OUTBOX.md` (`C19`)
  - `02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md` + `02-specs/contracts/M16-TASK-CORE-COMMANDS.md` (`C16`)
- **Slices, Điều hướng & Công cụ Kiểm chứng:**
  - `02-specs/slices/SL01-INTERNAL-WORK.md`, `02-specs/README.md`, `03-planning/GAPS.md`, `03-planning/DECOMPOSITION-PLAN.md`, `03-planning/agent/PROGRESS.md`, `active-task.json`, `05-tools/verify_module_spec.py`.

---

## 3. Phân tích Tác động & Quy tắc An toàn (`Impact Check`)

- **Breaking Contract Check:** Có thay đổi additive & sửa lỗi đồng bộ trên `C14`, `C20`, `C19`, `C16` (bổ sung `actor_type`, `asset_version_id`, `endpoint_hashes_by_version`, `erased_subject_refs[]`, `TaskLifecycleOrStageChanged`, `DeliverableReworkRequested`, `DeliverableRevisionBatchOpened`, `CONFLICT`, Entity-Mapped `CompileScopeFilter`), nhưng không phá vỡ mô hình domain Wave 2–5 chưa triển khai vì hiện toàn bộ đang ở giai đoạn **`Documentation-Only`** (`Not Run`).
- **Bảo vệ `verify_delivery_plan.py` & `verify_module_spec.py`:** Giữ nguyên cột chuẩn và điểm neo `## 9. Test applicability` ... `W-T18 đầy đủ` trên `SL01`; không tạo mã nguồn ứng dụng hay SQL DDL thật; giữ nguyên SHA-256 Master `v1.9`.

---

## 4. Kế hoạch Áp dụng (`Apply` Checklist)

- [x] Khởi tạo và phê duyệt phương án `CR-20261116-WAVE1-5-HARDENING` qua phiên `/grill-me` 6 nhánh.
- [x] Áp dụng cập nhật đồng bộ `ADR-002..009` & `INDEX.md`.
- [x] Nâng chuẩn `M23`/`C23` & `M24`/`C24` đủ 6 phần `MODULE-SPEC` / 12 phần `CONTRACT` & 10-cột Test Matrix `Not Run`.
- [x] Vá sạch lỗi liên module trên `M14/C14`, `M20/C20`, `M19/C19`, `M16/C16`, `SL01`.
- [x] Đồng bộ `GAPS.md`, `02-specs/README.md`, `DECOMPOSITION-PLAN.md`, `PROGRESS.md`, `active-task.json` và bật kiểm chuẩn mặc định cho `M23`/`M24`/`SL01` trong `verify_module_spec.py`.
- [x] Thực thi Fresh-Context Re-Audit độc lập (gồm 2 lượt đối soát & vá sạch `CRITICAL`/`HIGH`/`MEDIUM`), chạy đủ `4` script `05-tools/*.py` và lưu trữ CR này vào `02-specs/changes/archive/`.

---

## Ghi chú đính chính lịch sử (giữ nguyên nguyên văn lịch sử CR phía trên)

- **Bối cảnh:** Mục 1 phía trên lưu nguyên văn mô tả tại thời điểm Wave 1.5 (`2026-11-16`) trước đợt vá `W1-01` và trước đồng bộ `M23`.
- **Đính chính hiện hành:** Khóa một lần `privacy_redacted_at IS NULL` và cụm `"chỉ scrub 1 lần"` cho `privacy_erasure_system_role` đã bị bãi bỏ bởi [CR-20261116-WAVE1-REVIEW-FIXES.md](CR-20261116-WAVE1-REVIEW-FIXES.md) (`INV-27`, `ADR-004`, `M16/C16`, `M20/C20`) và đã được đồng bộ dứt điểm vào `M23` qua [CR-20261117-M23-ERASURE-ALIGNMENT.md](CR-20261117-M23-ERASURE-ALIGNMENT.md). Không sử dụng mô tả cũ ở Mục 1 làm quy chuẩn hiện hành.
