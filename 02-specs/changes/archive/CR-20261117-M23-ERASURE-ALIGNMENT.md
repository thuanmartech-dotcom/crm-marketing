# Change Proposal: `CR-20261117-M23-ERASURE-ALIGNMENT` — Đồng bộ Quyền `privacy_erasure_system_role` trên `M23`, Bổ sung Kiểm tra Hồi quy `INV-27` & Chốt Bàn giao Wave 2

## 1. Thông tin đề xuất

- **Mã đề xuất:** `CR-20261117-M23-ERASURE-ALIGNMENT`
- **Trạng thái:** `Applied & Archived` *(đã áp dụng đầy đủ vào `M23`, `CR-20261116-WAVE1-5-HARDENING`, `05-tools/`, tài liệu bàn giao Wave 2 & `CONTRACTS-REGISTRY.md`, và lưu trữ vào `02-specs/changes/archive/`)*
- **Baseline Master tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`, `SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`)
- **Phân loại nguồn:** `[PROPOSED-EXTENSION]` *(đồng bộ tài liệu `M23` với quyết định kiến trúc đã chốt, không đổi Master v1.9 và không thay đổi đề xuất `[PROPOSED]` thành `[MASTER]`)*
- **Quyết định gốc được kế thừa:**
  - [ADR-004](../../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md) (Mục 2 `Nhóm C` & Mục 3 `Ngoại lệ Kiểm soát Đa lần theo Yêu cầu Xóa cho Task_Submissions`, `W1-01`)
  - [ADR-005](../../../01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md) (Mục 4 `Tách DB Role` `privacy_erasure_system_role` & `NOBYPASSRLS` / `NOSUPERUSER`)
  - [INVARIANTS.md](../../../01-architecture/INVARIANTS.md) (`INV-13`, `INV-27`)
  - [CR-20261116-WAVE1-REVIEW-FIXES.md](CR-20261116-WAVE1-REVIEW-FIXES.md) (`W1-01`)
- **Dấu vết phê duyệt (`Approval Trace`):**
  - `Approved_By:` Chủ dự án (Yêu cầu phiên rà soát/khép tồn đọng Wave 1/1.5 ngày `2026-11-17`)
  - `Approved_Scope:` Mở và áp dụng CR đồng bộ `M23` cùng các tham chiếu hiện hành trực tiếp bị ảnh hưởng với `ADR-004`, `ADR-005` và `INV-27`; bổ sung kiểm tra hồi quy tài liệu trong `05-tools/`; cập nhật bàn giao Wave 2, trạng thái và registry liên quan (không phê duyệt thiết kế nghiệp vụ mới)
  - `Decision_Ref:` `CR-20261117-M23-ERASURE-ALIGNMENT`
  - `Approved_At:` `2026-11-17`
- **Danh sách tệp thực sự bị ảnh hưởng:**
  - **Module Spec (`Reviewed`):** [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md)
  - **Lịch sử CR (`Archived` — chỉ thêm dẫn chiếu đính chính lịch sử):** [CR-20261116-WAVE1-5-HARDENING.md](CR-20261116-WAVE1-5-HARDENING.md)
  - **Planning, Bàn giao & Registry:** [PROGRESS.md](../../../03-planning/agent/PROGRESS.md), [active-task.json](../../../03-planning/agent/active-task.json), [DECOMPOSITION-PLAN.md](../../../03-planning/DECOMPOSITION-PLAN.md), [02-specs/README.md](../../README.md), [CONTRACTS-REGISTRY.md](../../CONTRACTS-REGISTRY.md)
  - **Công cụ Kiểm chứng & Hồi quy Tài liệu (`05-tools/`):** [context_integrity.py](../../../05-tools/context_integrity.py), [verify_module_spec.py](../../../05-tools/verify_module_spec.py), [test_context_integrity.py](../../../05-tools/test_context_integrity.py), [test_verify_module_spec.py](../../../05-tools/test_verify_module_spec.py)

---

## 2. Mâu thuẫn, Tác động & Rà soát Lan truyền

### 2.1. Mâu thuẫn & Tác động (`Root Cause & Impact`)

- **Mâu thuẫn đã xác định:** Tại [M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md) Mục `6.1` (khoảng dòng `573`), vai trò PostgreSQL `privacy_erasure_system_role` vẫn giữ mô tả từ đợt Wave 1.5 cũ: *"(`chỉ scrub 1 lần M16.Task_Submissions.privacy_redacted_at ngoài Legal_Hold theo ADR-004`)"*.
- **Nguyên nhân:** Khi [CR-20261116-WAVE1-REVIEW-FIXES.md](CR-20261116-WAVE1-REVIEW-FIXES.md) (`W1-01`) nâng cấp `ADR-004`, `ADR-005`, `ADR-009`, `M16`, `C16`, `M20`, `C20` và `SL01` sang cơ chế scrub PII đa chủ thể theo từng `deletion_ledger_id` (`redacted_deletion_ledger_ids uuid[]`, giữ nguyên `content_sha256` gốc, cập nhật `redacted_content_sha256`), phần mô tả role tại `M23` Mục `6.1` chưa được đồng bộ theo; đồng thời checker `05-tools/` trước đây mới kiểm tra `M16` và `ADR-004` với mẫu chuỗi hẹp (`WHERE privacy_redacted_at IS NULL`) nên bỏ lọt câu chữ văn xuôi `"chỉ scrub 1 lần"` trong `M23`.
- **Tác động:** Nếu giữ nguyên câu chữ này, đội ngũ triển khai DB/role dựa trên `M23 §6.1` có thể cấp đặt hoặc lập trình guard ngăn `privacy_erasure_system_role` thực thi quá 1 lần trên cùng bản ghi `Task_Submissions`, làm sót PII của chủ thể dữ liệu thứ hai (trái `INV-27` và `W-T38`) hoặc làm sai lệch quy chuẩn bảo toàn `content_sha256` gốc vs `redacted_content_sha256`.

### 2.2. Kết quả Rà soát Lan truyền Có Giới hạn (`01-architecture/`, `02-specs/`, `03-planning/`, `.agents/`, `05-tools/`)

| Nhóm phân loại | Vị trí phát hiện | Kết luận & Xử lý |
|---|---|---|
| **a. Quy định hiện hành sai** | `02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md` (§6.1, dòng 573) | **Sửa qua CR này** để đồng bộ đầy đủ với `ADR-004`, `ADR-005`, `INV-27`. |
| **b. Câu cấm dùng khóa 1 lần / thiết kế cũ đã thay thế** | `01-architecture/INVARIANTS.md` (`INV-27`), `01-architecture/INDEX.md`, `01-architecture/decisions/ADR-004-*.md`, `02-specs/CONTRACTS-REGISTRY.md`, `03-planning/agent/active-task.json`, `03-planning/DECOMPOSITION-PLAN.md` (dòng 142), `.agents/skills/crm-ba-spec/references/ears-and-checklists.md`, `02-specs/changes/archive/CR-20261116-WAVE1-REVIEW-FIXES.md` | **Giữ nguyên** vì là câu cấm khóa 1 lần hoặc mô tả tường minh thiết kế cũ đã được thay thế. |
| **c. Nhật ký / CR lịch sử** | `02-specs/changes/archive/CR-20261116-WAVE1-5-HARDENING.md` (Nhánh #4 dòng 17); `03-planning/agent/PROGRESS.md` (các dòng nhật ký ngày 16/11 và sáng 17/11) | **Bảo toàn lịch sử nguyên văn**; bổ sung dẫn chiếu đính chính lịch sử trong `CR-20261116-WAVE1-5-HARDENING.md` và ghi nhật ký khép lại mới trong `PROGRESS.md`. |
| **d. Không liên quan** | `02-specs/modules/M19-*.md` (`one-time token`, `one-time refresh_token`, `one-time state_nonce`); `02-specs/FUNCTION-CATALOG.md` / `unnumbered-rules.json` (entry hành trình, hoàn phép, refund `1 lần`) | **Không sửa** vì thuộc ngữ cảnh bảo mật OAuth/nghiệp vụ khác. |

### 2.3. Đối chiếu Ngữ nghĩa Tối thiểu & Phát hiện Riêng (`Không tự thiết kế cơ chế mới`)

1. **Xóa chủ thể A rồi chủ thể B trên cùng submission (`Khớp nguồn hiện hành`):** Lần A (`deletion_ledger_id = L1`) đi qua `WHERE cardinality(active_legal_hold_ids) = 0 AND NOT (redacted_deletion_ledger_ids @> ARRAY[$L1]::uuid[])`, nối `L1`, tăng `privacy_redaction_count`, cập nhật `privacy_redacted_at` & `redacted_content_sha256`, giữ nguyên `content_sha256`. Lần B (`L2 != L1`) tiếp tục thỏa điều kiện vì `privacy_redacted_at` không phải khóa chặn một lần (`ADR-004`, `M16`, `C16`, `M20`).
2. **Phát lại cùng `deletion_ledger_id` (`Khớp nguồn hiện hành`):** `NOT (redacted_deletion_ledger_ids @> ARRAY[$L1]::uuid[])` trả `false`, lệnh chuyển thành `NO-OP` idempotent (`CR-20261116-WAVE1-REVIEW-FIXES`, `C16`).
3. **Hai lệnh xóa khác nhau chạy đồng thời (`PHÁT HIỆN RIÊNG — CHỜ BỔ SUNG QUYẾT ĐỊNH TRƯỚC DDL/CODE`):** `INV-27` và `M16` (`W-T38`) yêu cầu kiểm thử kịch bản xóa đồng thời hai chủ thể khác nhau trên cùng bản ghi `Task_Submissions`, nhưng `ADR-004`, `M16`, `C16`, `M20`, `C20` và `CR-20261116-WAVE1-REVIEW-FIXES` hiện mới định nghĩa mệnh đề `WHERE ... NOT (redacted_deletion_ledger_ids @> ...)` mà **chưa quy định tường minh cơ chế khóa/tuần tự hóa cấp dòng** (`SELECT ... FOR UPDATE` trong transaction của `privacy_erasure_system_role` trước khi đọc `result_text` và tính lại `redacted_content_sha256`, hoặc vòng lặp CAS `row_version`) để chống *lost update* dưới mức cô lập `READ COMMITTED` mặc định của PostgreSQL. Theo nguyên tắc không tự bịa cơ chế mới ngoài nguồn hiện hành, phát hiện này được ghi riêng (không chặn việc đồng bộ `M23` theo `ADR-004`/`ADR-005`/`INV-27`), và **phải dừng/chốt phần chi tiết khóa đồng thời tại `ADR-004`/`M16` trước khi viết SQL/code triển khai `W-T38` ở pha `SL01`/`SL04`**.
4. **Bản ghi đang `Legal_Hold` và xử lý tiếp sau khi gỡ hold (`Khớp nguồn hiện hành`):** Khi `cardinality(active_legal_hold_ids) > 0`, `privacy_erasure_system_role` không được scrub và `M20-F04` giữ `Privacy_Requests` ở `PARTIALLY_COMPLETED_LEGAL_HOLD`. Sau khi `M20.LegalHoldChanged(RELEASED)` gỡ hết `legal_hold_id` khiến `cardinality(active_legal_hold_ids) = 0`, luồng `CompleteRequest` tại `M20-F04` kích hoạt phần xóa còn lại và scrub thành công do `deletion_ledger_id` chưa nằm trong `redacted_deletion_ledger_ids`.
5. **Toàn vẹn nội dung & hash (`Khớp nguồn hiện hành`):** `content_sha256` gốc (khớp `M16.Task_Reviews.content_sha256_checked`) không bị ghi đè; `redacted_content_sha256` phản ánh hash sau lần scrub gần nhất kèm dấu vết `M20.Deletion_Ledger` và `M23.Audit_Logs`.
6. **Phân quyền & ranh giới `Nhóm C` (`Khớp nguồn hiện hành`):** User, `app_runtime_role` và `worker_runtime_role` vẫn bị cấm `UPDATE` nội dung bất biến trên `Task_Submissions`; `privacy_erasure_system_role` giữ `NOBYPASSRLS` / `NOSUPERUSER` và ngoại lệ tuyệt đối **không** mở rộng sang các bảng `Nhóm C` append-only khác (`Audit_Logs`, `Approval_Decisions`, `Backup_Drill_Logs`, `Task_Reviews`, `Task_Events`, `Acceptances`...).

---

## 3. Thay đổi Dự kiến & Tiêu chí Nghiệm thu

### 3.1. Thay đổi Dự kiến (`[PROPOSED]`)

1. **[M23-SYSTEM-ADMIN-SECURITY-OPS.md](../../modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md):**
   - Cập nhật `## 1. Manifest` (`Status`, `Decision_Ref`, `Approved_At` giữ `Reviewed` và giữ nguyên `[PROPOSED]`).
   - Thay thế mô tả `"chỉ scrub 1 lần M16.Task_Submissions.privacy_redacted_at"` tại Mục `6.1` (`[PROPOSED]`): `privacy_erasure_system_role` (`NOBYPASSRLS` / `NOSUPERUSER`) là role hệ thống chuyên biệt duy nhất được thực thi scrub PII có kiểm soát trên `M16.Task_Submissions.result_text` theo từng `deletion_ledger_id` ngoài `Legal_Hold` (`WHERE cardinality(active_legal_hold_ids) = 0 AND NOT (redacted_deletion_ledger_ids @> ARRAY[$deletion_ledger_id]::uuid[])`), cho phép xử lý nối tiếp các lệnh xóa khác nhau và idempotent khi phát lại cùng `deletion_ledger_id`; nối `redacted_deletion_ledger_ids`, tăng `privacy_redaction_count`, cập nhật `privacy_redacted_at` chỉ làm dấu thời gian lần xử lý gần nhất (tuyệt đối không dùng `privacy_redacted_at IS NULL` làm khóa một lần), cập nhật `redacted_content_sha256` kèm dấu vết `M20.Deletion_Ledger` & `M23.Audit_Logs`, giữ nguyên `content_sha256` gốc, không mở quyền sửa nội dung thường cho user/`app_runtime_role`/`worker_runtime_role`, và không mở rộng ngoại lệ sang các bảng `Nhóm C` append-only khác (`ADR-004`, `ADR-005`, `INV-27`).
   - Bổ sung xác nhận rõ trong ca `S-T08` (Mục `6.2`, giữ nguyên `Not Run`) rằng cả `worker_runtime_role` và `privacy_erasure_system_role` cũng bị DB từ chối `UPDATE/DELETE` trên các bảng `Nhóm C` của `M23`.
2. **[CR-20261116-WAVE1-5-HARDENING.md](CR-20261116-WAVE1-5-HARDENING.md):** Giữ nguyên văn lịch sử Nhánh #4 và bổ sung 1 ghi chú dẫn chiếu đính chính tới `CR-20261116-WAVE1-REVIEW-FIXES.md` và `CR-20261117-M23-ERASURE-ALIGNMENT.md`.
3. **Kiểm tra hồi quy `05-tools/`:**
   - Bổ sung hàm kiểm tra có mục tiêu `find_inv27_erasure_issues()` và mở rộng `wave_guard_issues()` trong [context_integrity.py](../../../05-tools/context_integrity.py) + tích hợp vào [verify_module_spec.py](../../../05-tools/verify_module_spec.py) để bắt mô tả cho phép scrub chỉ 1 lần hoặc tái đưa khóa `privacy_redacted_at IS NULL` vào cơ chế cho phép xóa, kiểm tra quan hệ `privacy_erasure_system_role` với `INV-27`/`ADR-004` trên đúng phần tài liệu liên quan, đồng thời không báo sai đối với câu cấm dùng khóa 1 lần, mô tả thiết kế cũ đã thay thế hoặc nội dung CR lịch sử.
   - Bổ sung ca test hồi quy trong [test_context_integrity.py](../../../05-tools/test_context_integrity.py) và [test_verify_module_spec.py](../../../05-tools/test_verify_module_spec.py) chạy trên thư mục tạm (`tempfile`) không làm bẩn spec thật.
   - *Giới hạn:* Kiểm tra hồi quy này là công cụ kiểm tra cấu trúc và mẫu hồi quy có mục tiêu, **không thay thế rà soát ngữ nghĩa toàn bộ**.
4. **Chốt bàn giao Wave 2 & Đồng bộ trạng thái:** Cập nhật Sticky & nhật ký tại [PROGRESS.md](../../../03-planning/agent/PROGRESS.md), [active-task.json](../../../03-planning/agent/active-task.json), [DECOMPOSITION-PLAN.md](../../../03-planning/DECOMPOSITION-PLAN.md), [02-specs/README.md](../../README.md) và tái sinh [CONTRACTS-REGISTRY.md](../../CONTRACTS-REGISTRY.md) đúng phạm vi `M01 → M03 → M02 → M13`, loại bỏ hoàn toàn các điểm chặn giả từ sandbox (`BLK-W2-*`, `M11/M12`, `M08/M15`) khỏi chỉ dẫn hành động hiện tại mà vẫn bảo toàn lịch sử sandbox.
5. **Không thuộc phạm vi (`Non-goals`):** Không sửa Master v1.9, không sinh code ứng dụng/DDL/Docker, không tạo `WAVE-2-PLAN.md`/`M01-COMPLETION-PLAN.md` hay đặc tả `M01`, không đóng các GAP nghiệp vụ không liên quan, không tự bịa cơ chế khóa đồng thời mới ngoài nguồn.

### 3.2. Tiêu chí Nghiệm thu (`Acceptance Criteria`)

- [x] `CR-20261117-M23-ERASURE-ALIGNMENT` được mở, phê duyệt theo phạm vi đã cấp và ghi nhận đầy đủ nguồn/phê duyệt trước khi sửa `M23`.
- [x] `M23` không còn quy định `"scrub 1 lần"`, đầy đủ cơ chế `redacted_deletion_ledger_ids`, `redacted_content_sha256`, `content_sha256` gốc, `Legal_Hold`, phân quyền role và ranh giới `Nhóm C`.
- [x] Kiểm tra hồi quy trong `05-tools/` bắt đúng fixture đột biến `M23` & khóa `privacy_redacted_at IS NULL`, đạt trên bản đúng hiện hành và không báo sai câu cấm/mô tả lịch sử/CR.
- [x] Bàn giao Wave 2 tách bạch lịch sử sandbox khỏi chỉ dẫn hành động (`M01 → M03 → M02 → M13`).
- [x] Toàn bộ lệnh kiểm chứng kho (`--build-registry`, `build_delivery_inventory.py`, `verify_delivery_plan.py`, `verify_hrm_integration.py`, `verify_module_spec.py`) và bộ `unittest` checker đạt 100%; test ứng dụng giữ `Not Run`.
- [x] CR được cập nhật kết quả kiểm chứng thực tế, chuyển sang `Applied & Archived` và kiểm chứng lại liên kết sau khi di chuyển.

---

## 4. Kết quả Kiểm chứng Thực tế (`Actual Verification Results`)

- **Cổng nạp ngữ cảnh (Protocol v2 — trước khi chỉnh sửa):** Đã sinh, đọc đầy đủ và chạy `build_module_context.py --verify-packet` cho `context-M23.md` & `context-M16.md` tại `<ArtifactDir>/scratch/` (`context_valid: true`, `issues: []`; `session_token_telemetry: UNKNOWN`).
- **Tái sinh Registry & Toàn bộ Checker Kho (chạy sau khi archive CR):**
  - `python 05-tools/build_module_context.py --build-registry`: cập nhật `02-specs/CONTRACTS-REGISTRY.md`.
  - `python 05-tools/build_delivery_inventory.py`: toàn bộ `12/12` `checks` đạt `true`.
  - `python 05-tools/verify_delivery_plan.py`: `all` checks `true`, `bad_links: []`, `bad_fences: []`.
  - `python 05-tools/verify_hrm_integration.py`: `15/15` checks `true`.
  - `python 05-tools/verify_module_spec.py`: `all_passed: true` (`9` modules, `3` slices, `6` contracts, `6` changes, `8` skills, `1` registry; `cross_doc_consistency.passed: true`, `issues: []`; `session_token_telemetry: UNKNOWN`).
- **Bộ kiểm thử hồi quy `05-tools/` (`unittest`):**
  - `python -m unittest discover -s 05-tools -p "test_*.py" -v`: chạy `20` ca kiểm thử (`test_context_integrity.py` + `test_verify_module_spec.py`), bắt trượt đúng fixture đột biến `M23`, khóa `privacy_redacted_at IS NULL` và mixed-clause, đồng thời pass bản hiện hành, câu cấm dùng khóa 1 lần, mô tả thiết kế cũ và nội dung CR lịch sử.
- **Giới hạn & Trạng thái Ứng dụng:**
  - *Giới hạn checker:* Bộ kiểm tra hồi quy trong `05-tools/` xác minh cấu trúc, dấu vết trường `INV-27`/`ADR-004` theo từng phần tài liệu và mẫu cấm ở mức mệnh đề; **không thay thế rà soát ngữ nghĩa toàn bộ**.
  - *Phát hiện riêng cần chốt trước DDL/code (`W-T38`):* Hai lệnh xóa `deletion_ledger_id` khác nhau chạy đồng thời trên cùng `M16.Task_Submissions` hiện mới có mệnh đề `WHERE` idempotency, chưa quy định tường minh cơ chế khóa/tuần tự hóa cấp dòng (`SELECT ... FOR UPDATE` hoặc CAS `row_version`) tại `ADR-004`/`M16`.
  - *Kiểm thử phần mềm ứng dụng CRM:* **`Not Run`** (`Documentation-Only`).
