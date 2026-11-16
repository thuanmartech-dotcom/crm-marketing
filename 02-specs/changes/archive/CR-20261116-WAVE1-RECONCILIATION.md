# Change Proposal: `CR-20261116-WAVE1-RECONCILIATION`

> **Luồng OpenSpec (`Propose -> Apply -> Archive`):** Tệp đề xuất hợp nhất dùng để xử lý toàn bộ phát hiện `CRITICAL / HIGH / MEDIUM / INFO` từ đợt rà soát độc lập Luồng A trên cụm Wave 1 (`M14`, `M20`, `M19` và 3 Public Contract) trước khi mở khóa bóc tách `M16` và Wave 2.

---

## 1. Thông tin đề xuất

- **Mã đề xuất:** `CR-20261116-WAVE1-RECONCILIATION`
- **Trạng thái:** `Applied` *(Đã hoàn tất áp dụng toàn bộ khắc phục, tái kiểm Fresh-Context cho `M14`, `M20`, `M19` đạt `CRITICAL = 0, HIGH = 0`, khôi phục trạng thái `Reviewed` và chạy thông qua đủ 4 script `05-tools/` ngày 16/11/2026)*
- **Baseline Master tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`)
- **Phân loại nguồn:** `[MASTER-CLARIFICATION]` + `[PROPOSED-EXTENSION]`
- **Tài liệu bị ảnh hưởng:**
  - Architecture ADRs (`01-architecture/decisions/`): Bổ sung `ADR-002` .. `ADR-008`
  - Architecture Navigation: [INDEX.md](../../../01-architecture/INDEX.md)
  - Module Specs (`02-specs/modules/`): [M14-ORG-ACCESS-DELEGATION.md](../../modules/M14-ORG-ACCESS-DELEGATION.md), [M20-PRIVACY-CONSENT-RETENTION.md](../../modules/M20-PRIVACY-CONSENT-RETENTION.md), [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), kèm delta SSoT nhẹ tại [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) và [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md)
  - Public Contracts (`02-specs/contracts/`): [M14-PRINCIPAL-ACCESS-DECISION.md](../../contracts/M14-PRINCIPAL-ACCESS-DECISION.md), [M20-SUPPRESSION-PRIVACY-GATE.md](../../contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [M19-DURABLE-INGEST-OUTBOX.md](../../contracts/M19-DURABLE-INGEST-OUTBOX.md)
  - Slices & Planning & Tools: [SL01-INTERNAL-WORK.md](../../slices/SL01-INTERNAL-WORK.md), [02-specs/README.md](../../README.md), [DECOMPOSITION-PLAN.md](../../../03-planning/DECOMPOSITION-PLAN.md), [GAPS.md](../../../03-planning/GAPS.md), [PROGRESS.md](../../../03-planning/agent/PROGRESS.md), [active-task.json](../../../03-planning/agent/active-task.json), [verify_module_spec.py](../../../05-tools/verify_module_spec.py)

---

## 2. Lý do thay đổi & Phạm vi (Why & What)

- **Vấn đề phát hiện (Luồng A — Analyze + 3 Fresh-Context Auditors):**
  1. `C14` chứa lỗ hổng `CompileScopeFilter` (`OR branch_id` vô điều kiện, thiếu `Role DENY`, `Break-Glass`, `RESTRICTED_LEGAL_HOLD`), lệch `expected_permission_version` 3 chiều, sai tên GUC PG `SET LOCAL`, thiếu 2 schema và thiếu >25 `resource_type`/hành động `M19`.
  2. `M19`/`C19` thiếu 4/6 JSON schema, thiếu `EnqueueOutboundIntent`, lệch enum output, hổng race `PAUSED` & thiếu `tenant_id` trên unique index `Channel_Connections`, mâu thuẫn 3 khóa `Inbound_Events` (gây lỗi SQL `ON CONFLICT`), đổi tên `Message_Status_Events` thành `Delivery_Receipt_Events`, phạm điều cấm Master `3.12.12` (hardcode Zalo `HMAC-SHA256` & Meta tag policy).
  3. `M20`/`C20` gán sai Test ID (`U01`, `U21`) và thiếu `U22`/`INT28`/`OC20`, rút bớt cấu trúc `Consent_Logs` (`5.9`), làm mất bảng `Email_Delivery_Events`, thiếu `POST /v1/consents/revoke` (`202`), hứa `0 giây` trái Master `6.3` (`L3172`), thiếu `sender_profile_id`/`contact_id` từ `M19`, thiếu `TIKTOK` và bỏ sót `SEC03` Gateway.
  4. Xung đột SSoT xuyên `M14/M19/M20/M22/M23/M24` (`Break_Glass_Grants`, `Audit_Logs`, `Policy_Definitions/Versions`, `Tenant_Operating_Modes`, `Principal_Permission_Versions` vs Cache, `Scorecard_Reviews`, `Bank_Accounts`, `Departments`, External vs Internal Outbox, `O03/GAP-06`, `O06`), thiếu 3 cột `5.1` (`business_line_id`), thiếu 4 cột Test Matrix `6.2`, và gắn nhầm `[MASTER]` cho chi tiết `[PROPOSED]`.
- **Thay đổi đề xuất (đã chốt qua phiên `/grill-me` 6 bước ngày 16/11/2026):**
  1. Hạ tạm trạng thái `M14`, `M20`, `M19` và 3 contract sang `Draft (Reconciling via CR-20261116-WAVE1-RECONCILIATION)` trong suốt quá trình vá.
  2. Tách và chốt **7 ADR (`ADR-002` .. `ADR-008`)** trong `01-architecture/decisions/` theo định hướng Modular Monolith/PostgreSQL của `ADR-001`.
  3. Cập nhật đồng bộ 3 module, 3 public contract, delta SSoT tại `INDEX/SL01/M23/M24/DECOMPOSITION-PLAN/README`, đăng ký bổ sung GAP mới vào `GAPS.md`, và nâng cấp `verify_module_spec.py`.
- **Không thuộc phạm vi (Non-goals):**
  - Không sửa `00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md` (`v1.9` giữ nguyên SHA-256).
  - Không viết mã nguồn ứng dụng, DDL SQL migration hay Dockerfile (`Documentation-Only`).
  - Không viết lại toàn bộ cấu trúc legacy của `M21/M22/M23/M24/SL01` (chỉ vá delta SSoT tối thiểu để hết mâu thuẫn).

---

## 3. Phân tích tác động (Impact & Breaking Check)

- **Breaking Contract Change?** `Có` — Ảnh hưởng toàn bộ Consumer của `M14` (Org/ACL/Handover/LegalHold), `M19` (Channel/Inbox/Outbox/Receipts), và `M20` (Suppression/Consent/Privacy/Vendor/DR Gate). Cần cập nhật đồng bộ trước khi bắt đầu bóc tách `M16` và Wave 2 (`M01`, `M03`, `M02`, `M13`).
- **Ảnh hưởng `INVARIANTS.md`:** Khôi phục tuân thủ đầy đủ `INV-01, INV-02, INV-06, INV-07, INV-08, INV-09, INV-13, INV-14, INV-16, INV-21, INV-22, INV-23, INV-24, INV-25`.
- **Tác động Test Matrix & GAPS:** Chuẩn hóa đủ cột `Severity`, `Actual`, `Build`, `Fixture` (giữ `Status = Not Run`, `Actual = Not Run`); bổ sung `U22`, `INT28`, `RV20`, `NFR07`, `H-T04`, `P-T*` đúng vai trò; đăng ký đầy đủ các `[OPEN-GAP]` phát hiện mới vào `GAPS.md`.

---

## 4. Kế hoạch áp dụng (`Apply` Checklist)

- [x] Đã chốt đủ 6 bước quyết định `/grill-me` với chủ dự án.
- [x] Tách xong `ADR-002` .. `ADR-008` tại `01-architecture/decisions/`.
- [x] Cập nhật đồng bộ 3 Public Contracts (`M14`, `M20`, `M19`) với đầy đủ JSON Schema Input/Output & Domain Events.
- [x] Cập nhật đồng bộ 3 Module Specs (`M14`, `M20`, `M19`) đạt 100% checklist `MODULE-SPEC.md` & `module-workflow.md`.
- [x] Cập nhật delta SSoT tại `INDEX.md`, `M23`, `M24`, `SL01`, `DECOMPOSITION-PLAN.md`, `02-specs/README.md`, `GAPS.md`, `PROGRESS.md`, `active-task.json`.
- [x] Nâng cấp `05-tools/verify_module_spec.py` kiểm cấu trúc `standard_module_spec` & `contracts` chặt hơn.
- [x] Tái rà soát Fresh-Context (`CRITICAL = 0`, `HIGH = 0`) và chạy đủ 4 script `05-tools/*.py` thành công.
- [x] Nâng trạng thái Wave 1 về `Reviewed`, cập nhật CR sang `Applied` và dời sang `02-specs/changes/archive/`.
