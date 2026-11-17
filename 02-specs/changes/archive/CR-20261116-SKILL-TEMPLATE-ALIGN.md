# Change Proposal `CR-20261116-SKILL-TEMPLATE-ALIGN` — Đồng bộ Wave 1/1.5 theo Chuẩn `crm-ba-spec` & Checker v2

- **CR ID:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Ngày tạo:** `2026-11-16`
- **Status:** `Applied & Archived` *(Chủ dự án yêu cầu thực hiện trọn Đợt 2B: nâng cấp checker + mở/áp dụng/archive CR đồng bộ Wave 1/1.5 theo chuẩn template Đợt 2A)*
- **Approved_Scope:** `Wave 1/1.5 Template & Traceability Alignment (M14, M16, M19, M20, M23, M24, C14, C16, C19, C20, C23, C24, SL01)`
- **Approved_By:** `Chủ dự án`
- **Decision_Ref:** `CR-20261116-SKILL-TEMPLATE-ALIGN`
- **Approved_At:** `2026-11-16`
- **Backward_Drift:** `Additive-Only Metadata & Alignment` (không đổi semantic domain invariant hay Breaking schema của các Contract/Module Wave 1/1.5; giữ nguyên toàn bộ nhãn `[PROPOSED]` & `Not Run` cho mọi kiểm thử ứng dụng).

---

## 1. Bối cảnh & Mục tiêu

Sau khi **Đợt 2A** nâng cấp chuẩn hóa 2 khuôn mẫu tại [MODULE-SPEC.md](../../templates/MODULE-SPEC.md), [CONTRACT.md](../../templates/CONTRACT.md) và [GAPS.md](../../../03-planning/GAPS.md), **Đợt 2B** nâng cấp công cụ kiểm chứng [verify_module_spec.py](../../../05-tools/verify_module_spec.py) kèm bộ kiểm thử công cụ [test_verify_module_spec.py](../../../05-tools/test_verify_module_spec.py) để rà soát nghiêm ngặt hơn. Do đó đã mở và áp dụng CR đồng bộ nhẹ trên các đặc tả Wave 1/1.5 ở trạng thái `Reviewed`:

1. **6 Module Spec `Reviewed` (`M14`, `M16`, `M19`, `M20`, `M23`, `M24`):**
   - Bổ sung đủ 4 trường duyệt Manifest (`Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At`) theo `MODULE-SPEC.md`.
   - Mở rộng toàn bộ bảng `## 2. Requirement trace` lên **9 cột** chuẩn bằng cách thêm cột **`Hành vi / Contract`** (trỏ rõ `### 3.x` / `Mxx-Fyy` / `Cxx` hoặc phạm vi giao diện/migration tương ứng).
   - Chuẩn hóa đủ 6 phần con tường minh cho mỗi tiểu mục chức năng `### 3.x` trên `M16` (tách `- **Mục tiêu, Tác nhân & Phạm vi:**` thành `- **Mục tiêu & Phạm vi:**` và `- **Tác nhân & Kích hoạt:**` trên toàn bộ `M16-F01..07` và `W-F01..14`).
   - Đồng bộ 1-1 cột `Test` ở `## 2` với cột `Mã Test` ở `## 6.2`: thay các ô chỉ viết văn xuôi bằng mã Test chuẩn hoặc `[OPEN-GAP: ...]`; chuẩn hóa các mã ghép trong `## 6.2` để 100% Test ID ở `## 2` đều tồn tại trong `## 6.2`; vá lỗi thừa ký tự `|` tại dòng `CEO-U01` trong `## 6.2` của `M14` để đủ 10 cột chuẩn.

2. **6 Public Contracts `Reviewed` (`C14`, `C16`, `C19`, `C20`, `C23`, `C24`):**
   - Bổ sung khối JSON **`Ví dụ (Example)`** khớp với các trường schema đã khai báo ở `## 2` trên `C14`, `C19`, `C20`, `C23`, `C24` (bên cạnh `ExampleTaskCompletedEvent` sẵn có của `C16`).
   - Thay thế `"payload": {}` rỗng ở khối Event Envelope `### 3.1` của `C14`, `C16`, `C23`, `C24` bằng object field-map mô tả không rỗng; bổ sung khối JSON Event Envelope chuẩn `6` trường cho `C19` & `C20` tại `### 3.1` để đồng nhất `CONTRACT.md`.
   - Bổ sung metadata `Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At` trong phần đầu mỗi Contract.

3. **Slice `SL01` (`SL01-INTERNAL-WORK.md`):**
   - Bổ sung chuỗi `SHA-256` nguyên văn của Master v1.9 (`b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`) và bảng Manifest chuẩn có `Status`, `Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At`, giữ nguyên toàn vẹn bảng `## 9. Test applicability` (`W-T01..40`, `W-T18 đầy đủ`, `W-T15` / `SL01-T07` `200 / 409 / IN_PROGRESS`, `Not Run`).

---

## 2. Danh sách Tệp Tác động (`Affected Scope`)

- **Modules:** [M14-ORG-ACCESS-DELEGATION.md](../../modules/M14-ORG-ACCESS-DELEGATION.md), [M16-WORK-PROJECTS-TASK-CORE.md](../../modules/M16-WORK-PROJECTS-TASK-CORE.md), [M19-INTEGRATION-ADAPTERS-OUTBOX.md](../../modules/M19-INTEGRATION-ADAPTERS-OUTBOX.md), [M20-PRIVACY-CONSENT-RETENTION.md](../../modules/M20-PRIVACY-CONSENT-RETENTION.md), [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md), [M24-PERFORMANCE-AND-PRODUCTIVITY.md](../../modules/M24-PERFORMANCE-AND-PRODUCTIVITY.md).
- **Contracts:** [M14-PRINCIPAL-ACCESS-DECISION.md](../../contracts/M14-PRINCIPAL-ACCESS-DECISION.md), [M16-TASK-CORE-COMMANDS.md](../../contracts/M16-TASK-CORE-COMMANDS.md), [M19-DURABLE-INGEST-OUTBOX.md](../../contracts/M19-DURABLE-INGEST-OUTBOX.md), [M20-SUPPRESSION-PRIVACY-GATE.md](../../contracts/M20-SUPPRESSION-PRIVACY-GATE.md), [M23-PLATFORM-GOVERNANCE-OUTBOX.md](../../contracts/M23-PLATFORM-GOVERNANCE-OUTBOX.md), [M24-PRODUCTIVITY-CACHE-QUEUE.md](../../contracts/M24-PRODUCTIVITY-CACHE-QUEUE.md).
- **Slices & Registry:** [SL01-INTERNAL-WORK.md](../../slices/SL01-INTERNAL-WORK.md), [CONTRACTS-REGISTRY.md](../../CONTRACTS-REGISTRY.md).

---

## 3. Kết quả Nghiệm thu (`Applied & Archived`)

- Đã tái sinh [CONTRACTS-REGISTRY.md](../../CONTRACTS-REGISTRY.md) (`--build-registry`).
- Toàn bộ 4 lệnh kiểm chứng toàn kho (`build_delivery_inventory.py`, `verify_delivery_plan.py`, `verify_hrm_integration.py`, `verify_module_spec.py`) và bộ `unittest` công cụ (`test_verify_module_spec.py`, `test_context_integrity.py`) đạt `100%` (`all_passed: true`, `bad_links: []`).
- Toàn bộ kiểm thử ứng dụng CRM giữ nguyên **`Not Run`** (`Documentation-Only`).
