# Playbook Chế độ `module`: Bóc tách Module `M01–M20`

Chắt lọc quy trình 4 pha từ **BMAD Analyst** (đào sâu nghiệp vụ), **Spec-Kit** (`/clarify` + `/analyze`), **EARS** (`spec-workflow-mcp`) và **Traceability Gate** (`srs-dd`).

---

## 0. Bốn Quy ước Nền đã khóa trước khi Bóc tách (`Pre-Flight Conventions — 15/11/2026`)

1. **Truy vết mở rộng nhóm `221 missing_owner` & `PLATFORM` (`GAP-03`):**
   - Ngoài các ID có `"owner": "Mxx"` trong [requirements.json](../../../../03-planning/trace/requirements.json), Agent bắt buộc quét thêm các ID thuộc nhóm `missing_owner` / `PLATFORM` (`U01–24`, `CEO/CMO/CX/SEC/WF-U*`, `INT*`, `RV*`, `OC*`, `DB*`, `NFR01–12`, `O01–08`, `ENTITY-L*`) có liên quan trực tiếp đến `Mxx` để đưa vào bảng `Requirement trace` & `Test matrix` của `Mxx` (ghi rõ vai trò `Primary Owner` hoặc `Consumer`). Chưa sửa cứng `build_delivery_inventory.py` cho tới cuối Wave 5.
2. **Độ sâu `Per-Function` (`Mxx-Fyy`) & Mô tả Luồng Nghiệp vụ Dễ hiểu bên trong mỗi tệp `MODULE-SPEC.md`:**
   - Giữ đúng 1 tệp chuẩn `02-specs/modules/Mxx-TEN-MODULE.md` (đủ 6 mục cấp `##` của `MODULE-SPEC.md`), nhưng trong **Mục `3. Hành vi`** bắt buộc có:
     - `### 3.0A. Tổng quan Cơ chế Hoạt động của Module` (giải thích bức tranh tổng thể + sơ đồ luồng `flowchart TD` nối liền các chức năng).
     - `### 3.0B. Mô hình Máy trạng thái Cốt lõi` (`stateDiagram-v2`).
     - Tách riêng từng tiểu mục `### 3.x Mxx-Fyy — <Tên chức năng>` cho **100% chức năng** của module, trong đó mỗi chức năng đều có: (1) Mục tiêu/Actor/Preconditions, (2) **Mô tả Nghiệp vụ & Cơ chế Hoạt động Từng bước (`Step-by-Step Operational Flow`) kèm ví dụ thực tế dễ hiểu**, (3) Quy tắc chuẩn EARS gắn `[MASTER]`/`[PROPOSED]`/`[OPEN-GAP]`, và (4) Xử lý đồng thời/Idempotency/Side effects/Audit; kèm tách file `public contracts/` tại `02-specs/contracts/`.
3. **Tách bạch các Bảng gộp (`Unbundling Grouped Entities — GAP-04`) ở Mục `4. Data/API`:**
   - Khi Master `5.13/5.18/5.20` khai báo gộp nhiều bảng trên 1 dòng (ví dụ: `Users, Memberships, Role_Bindings`), phải tách thành từng bảng logic độc lập trong `erDiagram` và Từ điển cột của `Mxx` (kế thừa 10 cột chuẩn Mục `5.1`, gắn nhãn `[MASTER]` cho trường gốc và `[PROPOSED]` cho bảng/cột chi tiết hóa, giữ mã truy vết `ENTITY-Lxxxx`).
4. **Chuẩn hóa Tham số mở (`A.6–A.9` & `GAPS`) thành `Bảng Policy/Config + Safe Default (Fail-Closed)` & Nhịp độ Cuốn chiếu:**
   - Mọi tham số vận hành chưa chốt (`O01–08`, `W-O*`, `P-O*`, `H-O*`, `GAP-*`) được mô hình hóa thành bảng `Policy/Config Parameters` có kiểu dữ liệu, `Safe Default (Fail-Closed theo INV-14)` và vai trò phê duyệt để không chặn tiến độ viết spec. Thực thi cuốn chiếu từng module một (`4 pha / module`).

---

## Pha 1 — Grounding & Trace Harvest (`search-first`, đọc tối thiểu đúng nguồn)

Mục tiêu: Gom toàn bộ sự thật đã có trong Master v1.9 trước khi đặt câu hỏi hay viết bất kỳ dòng spec nào. **Tìm sự thật trong kho tài liệu là việc của Agent — tuyệt đối không hỏi người dùng những gì đã tra được từ Master/trace/research.**

1. Đọc bối cảnh kiến trúc cốt lõi:
   - [active-task.json](../../../../03-planning/agent/active-task.json) và [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md)
   - [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md), [INDEX.md](../../../../01-architecture/INDEX.md) và các ADR liên quan trong `01-architecture/decisions/` (như [ADR-001-BASELINE-AND-STACK.md](../../../../01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md)).
2. Trích xuất toàn bộ dữ kiện thuộc module `Mxx` (`search-first` để tránh đặt trùng tên entity/command giữa 22 module):
   - Tìm dòng nguồn của `Mxx` trong [modules.json](../../../../03-planning/trace/modules.json) và các mục liên quan trong [source-sections.json](../../../../03-planning/trace/source-sections.json).
   - Lọc các requirement có `"owner": "Mxx"` hoặc `"Mxx"` trong `"consumers"` tại [requirements.json](../../../../03-planning/trace/requirements.json), và đối chiếu entity/contract đã khai báo trong [entities-contracts.json](../../../../03-planning/trace/entities-contracts.json) cùng các file có sẵn ở `02-specs/contracts/`.
   - Đọc các đoạn chức năng của `Mxx` trong [FUNCTION-CATALOG.md](../../../../02-specs/FUNCTION-CATALOG.md).
   - Dùng `read_file` (theo `StartLine`/`EndLine`) đọc đúng các phần Master v1.9 trong [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md).
   - Đối chiếu `04-research/` nếu Master có tham chiếu mở rộng chưa rõ ngữ cảnh.
3. Đọc khuôn mẫu chuẩn:
   - [MODULE-SPEC.md](../../../../02-specs/templates/MODULE-SPEC.md)
   - [CONTRACT.md](../../../../02-specs/templates/CONTRACT.md) (nếu module phát sinh public command/event liên module).

---

## Pha 2 — Cổng Hỏi Ngược Hai Tầng (BMAD + `/speckit.clarify`)

Tuyệt đối **không nhảy thẳng vào viết file `Mxx-*.md`** khi vừa đọc xong Master. Phải rà soát các điểm mù bằng checklist chung tại [ears-and-checklists.md](ears-and-checklists.md) **KẾT HỢP** đúng **1 Cụm nghiệp vụ tương ứng** trong [domain-lenses.md](domain-lenses.md) (chỉ đọc phần Cụm của `Mxx`, không nạp cả file) và phân loại thành 2 tầng:

### Tầng 1 — Blocking Clarify (Hỏi chặn ngay bằng `ask_question`)
Áp dụng cho các vấn đề làm sai lệch cấu trúc domain hoặc xung đột giữa các module:
- Ranh giới sở hữu entity/state giữa `Mxx` và module hàng xóm (ví dụ: `M01` vs `M02`, `M08` vs `M09`, `M16` vs `M14`, `M23` vs `M14/M20`).
- State machine cốt lõi (trạng thái hợp lệ, chuyển trạng thái bị cấm, ai có quyền chuyển).
- Nguồn chân lý (Single Source of Truth) khi có nhiều kênh/nguồn ghi đè nhau.
- Hợp đồng công khai (`public command/event`) ảnh hưởng sang module khác.

> **Cách hỏi chuẩn:** Sử dụng công cụ `ask_question`, hỏi **từng quyết định một** theo thứ tự phụ thuộc (hoặc gộp 1 câu ngắn nếu độc lập), **luôn đặt phương án `(Recommended)` lên đầu** kèm lý giải ngắn theo `INVARIANTS.md`. Nếu quyết định đó chốt một ranh giới kiến trúc hoặc đánh đổi quan trọng xuyên module, ghi thêm ADR mới vào `01-architecture/decisions/ADR-NNN-TEN-NGAN.md` theo mẫu [ADR-001-BASELINE-AND-STACK.md](../../../../01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md).

### Tầng 2 — Non-Blocking Gaps (Ghi nhận `[OPEN-GAP]`, không làm tắc luồng)
Áp dụng cho tham số vận hành hoặc chi tiết chưa thể chốt ngay ở bước thiết kế:
- Ngưỡng SLA/timeout cụ thể, hạn mức ngân sách, tỷ lệ hoa hồng cụ thể, tên nhân sự thực tế, vendor credential cụ thể.
- Ghi nhãn `[OPEN-GAP: GAP-Mxx-NN]` trực tiếp tại mục liên quan trong spec **và** bổ sung dòng tương ứng vào [GAPS.md](../../../../03-planning/GAPS.md).

---

## Pha 3 — Soạn thảo Đặc tả (`MODULE-SPEC.md` + EARS + Hybrid Contract)

Tạo tệp tại `02-specs/modules/Mxx-TEN-MODULE.md` (tên ASCII viết hoa, không dấu, dùng `-`), giữ đủ 6 mục lớn của [MODULE-SPEC.md](../../../../02-specs/templates/MODULE-SPEC.md):

1. **`## 1. Manifest`**
   - Ghi rõ Baseline (`v1.9`, SHA-256 từ `active-task.json`), các section/line nguồn Master.
   - `Status`: khởi tạo là `Draft` (chỉ lên `Reviewed`/`Ready` sau khi chủ dự án duyệt).
   - Domain owner (vai trò), owned entities, commands/events/projections, consumers, core/pack boundary, `Read first` / `Read on demand`.
2. **`## 2. Requirement trace`**
   - Liệt kê **tất cả** ID từ `requirements.json` có `owner == Mxx` (không bỏ sót ID nào!).
   - Bảng chuẩn: `| ID nguồn | Source anchor/line | Ý nghĩa | Owner/consumer | Priority | Applicability | Test | Evidence |`
   - Cột `Evidence` bắt buộc ghi `Not Run`.
3. **`## 3. Hành vi`**
   - Viết mọi rule hành vi, guard và xử lý lỗi bằng cú pháp **EARS** (xem [ears-and-checklists.md](ears-and-checklists.md)) kèm nhãn `[MASTER]`, `[PROPOSED]`, hoặc `[OPEN-GAP]`.
   - Bao phủ đủ: State machine (Mermaid `stateDiagram-v2` nếu có ≥ 3 trạng thái), Main flow, Exceptions, Concurrency (`expected_version`/CAS), Idempotency/Retry, Side effects/Outbox, Audit & Metric.
4. **`## 4. Data/API`**
   - Logical ERD scoped (Mermaid `erDiagram`), bảng thuộc tính logic (chỉ rõ `[OPEN-GAP]` nếu thiếu field quyết định), Lifecycle/History.
   - **Quy tắc Hybrid Contract:**
     - Lệnh/API nội bộ trong module: mô tả trực tiếp bảng Command/Query/Error envelope ngay tại mục này.
     - **Public cross-module command hoặc domain event** (có module khác tiêu thụ): tách file riêng vào `02-specs/contracts/<PRODUCER>-<TEN-CONTRACT>.md` theo mẫu [CONTRACT.md](../../../../02-specs/templates/CONTRACT.md) và đặt link tham chiếu từ mục `Data/API` của cả Producer lẫn Consumer.
5. **`## 5. UI/operations`**
   - Screens, actions, 4 trạng thái UI (`empty` / `loading` / `error` / `permission denied`), freshness, logs/alerts/runbook/retention/error ownership.
6. **`## 6. Migration và gate`**
   - Upgrade/backfill/flag closure + Test applicability matrix (`Not Run`, phân biệt rõ điều kiện áp dụng `N/A` nếu có lý do).

---

## Pha 4 — Analyze & Verify Gate (Spec-Kit `/analyze` + `srs-dd` Checker)

Trước khi báo hoàn thành cho người dùng, tự kiểm tra chéo và chạy tool:

1. **Checklist tự kiểm (`/analyze`) & Fresh-Context Review:**
   - Mọi ID thuộc `Mxx` trong `requirements.json` đều đã xuất hiện trong bảng `Requirement trace` chưa?
   - Có mâu thuẫn nào với `INVARIANTS.md` (ví dụ: ghi đè projection thành nguồn ghi, gộp tenant/workspace, vượt quyền `M14`/`M20`, bỏ qua `M19` outbox)?
   - Có từ ngữ mơ hồ kiểu *"hệ thống xử lý phù hợp"*, *"tùy chỉnh linh hoạt"* mà chưa chuyển thành điều kiện EARS hoặc `[OPEN-GAP]` không?
   - Có chữ `Pass` / `Passed` / `Verified` nào lọt vào cột `Evidence` không? (Phải là `Not Run`).
   - *(Trước khi nâng từ `Draft` → `Reviewed` hoặc cuối một Sóng song song):* Khuyến nghị phóng 1 subagent `research` (context sạch, read-only) đối chiếu độc lập `Mxx-*.md` với `INVARIANTS.md` + Master v1.9 để tránh thiên kiến tự chấm.
2. **Cập nhật điều hướng & nhật ký (`Handoff`):**
   - *(Nếu chạy đơn lẻ / hoặc vai Coordinator):* Cập nhật dòng `Mxx` trong [02-specs/README.md](../../../../02-specs/README.md) (trạng thái + link tệp), ghi nhật ký bàn giao chuẩn `Handoff` vào [03-planning/agent/PROGRESS.md](../../../../03-planning/agent/PROGRESS.md) (gồm: *Đã khóa / Contract mới / Blocking GAP chờ chốt / Lệnh gợi ý phiên sau*) và các GAP mới vào [GAPS.md](../../../../03-planning/GAPS.md).
   - *(Nếu đang là Worker trong sóng song song):* **Không sửa** `README.md`, `PROGRESS.md`, `GAPS.md`; trả về danh sách GAP & tóm tắt để Coordinator hợp nhất.
   - *(Lưu ý chuyển tiếp `M18`):* Khi hoàn thiện phần baseline `M18-F01–07` vào [M18-BI-REPORTING-EXPANSION.md](../../../../02-specs/modules/M18-BI-REPORTING-EXPANSION.md), gỡ tên tệp này khỏi `LEGACY_EXEMPT_MODULES` trong `05-tools/verify_module_spec.py`.
3. **Chạy lệnh kiểm chứng:**
   - *(Worker song song):* Chỉ chạy `python 05-tools/verify_module_spec.py --file 02-specs/modules/Mxx-TEN-MODULE.md`.
   - *(Đơn lẻ hoặc Coordinator cuối sóng):* Chạy đủ 4 lệnh:
     ```powershell
     python 05-tools/build_delivery_inventory.py
     python 05-tools/verify_delivery_plan.py
     python 05-tools/verify_hrm_integration.py
     python 05-tools/verify_module_spec.py --file 02-specs/modules/Mxx-TEN-MODULE.md
     ```
