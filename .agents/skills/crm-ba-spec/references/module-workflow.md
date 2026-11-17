# Playbook Chế độ `module`: Bóc tách & Hoàn thiện Module (`M01–M24`)

Chắt lọc quy trình 4 pha từ **BMAD Analyst** (đào sâu nghiệp vụ), **Spec-Kit** (`/clarify` + `/analyze`), **EARS** (`spec-workflow-mcp`) và **Traceability Gate** (`srs-dd`). Áp dụng tạo mới/hoàn thiện `M01–M20` (gồm hoàn thiện `M18-F01–07`); riêng các module đã `Reviewed` (`M14/16/19/20/23/24`) hoặc legacy `M21/22` khi cần sửa phải đi qua `review-change` (`CR-*`).

---

## 0. Bốn Quy ước Nền đã khóa trước khi Bóc tách (`Pre-Flight Conventions`)

1. **Truy vết mở rộng nhóm `221 missing_owner` & `PLATFORM` (`GAP-03`):**
   - Ngoài các ID có `"owner": "Mxx"` trong [requirements.json](../../../../03-planning/trace/requirements.json), Agent bắt buộc quét thêm các ID thuộc nhóm `missing_owner` / `PLATFORM` (`U01–24`, `CEO/CMO/CX/SEC/WF-U*`, `INT*`, `RV*`, `OC*`, `DB*`, `NFR01–12`, `O01–08`, `ENTITY-L*`) có liên quan trực tiếp đến `Mxx` để đưa vào bảng `Requirement trace` & `Test matrix` của `Mxx` (ghi rõ vai trò `Primary Owner` hoặc `Consumer`). Chưa sửa cứng `build_delivery_inventory.py` cho tới cuối Wave 5.
2. **Độ sâu `Per-Function` (`Mxx-Fyy`) & Cấu trúc Chuẩn 6 Phần Con bên trong mỗi tệp `MODULE-SPEC.md`:**
   - Giữ đúng 1 tệp chuẩn `02-specs/modules/Mxx-TEN-MODULE.md` (đủ 6 mục cấp `##` của `MODULE-SPEC.md`), nhưng trong **Mục `3. Hành vi`** bắt buộc có:
     - `### 3.0A. Tổng quan Cơ chế Hoạt động của Module` (giải thích bức tranh tổng thể + sơ đồ luồng `flowchart TD` nối liền các chức năng).
     - `### 3.0B. Mô hình Máy trạng thái Cốt lõi` (`stateDiagram-v2` nếu có ≥ 3 trạng thái, hoặc nêu rõ `N/A` kèm lý do nếu stateless).
     - Tách riêng từng tiểu mục `### 3.x Mxx-Fyy — <Tên chức năng>` cho **100% chức năng** của module (đủ danh mục trong `FUNCTION-CATALOG.md`), mỗi chức năng gồm đủ 6 phần con: (1) `- **Mục tiêu & Phạm vi:**`, (2) `- **Tác nhân & Kích hoạt:**`, (3) `- **Tiền điều kiện & Đầu vào bắt buộc:**`, (4) `- **Mô tả Nghiệp vụ & Cơ chế Hoạt động Từng bước:**` (kèm ví dụ thực tế dễ hiểu), (5) `- **Đồng thời, Idempotency & Tác động phụ / Outbox:**` (hoặc ghi rõ `N/A` có lý do), và (6) `- **Ngoại lệ & Quy tắc Hành vi (EARS):**` gắn `[MASTER]`/`[PROPOSED]`/`[OPEN-GAP]` kèm mã rule cục bộ (vd: `R-M01-F01-01`) và mã Test liên kết; kèm tách file `public contracts/` tại `02-specs/contracts/`.
3. **Tách bạch các Bảng gộp (`Unbundling Grouped Entities — GAP-04`) theo [ADR-004](../../../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md):**
   - Khi Master `5.13/5.18/5.20` khai báo gộp nhiều bảng trên 1 dòng, phải tách thành **1 bảng = 1 dòng** độc lập trong `erDiagram` và Từ điển cột `4.2` của `Mxx`.
   - **Dẫn chiếu trực tiếp [ADR-004](../../../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md) cho phân loại nhóm kế thừa** (không tự viết lại biến thể khác chuẩn): chỉ rõ mỗi bảng thuộc **`Nhóm A`** (`12` cột chuẩn gồm `branch_id`, `legal_entity_id`, `business_line_id` + `workspace_id NN`), **`Nhóm B-Catalog`** (`workspace_id NULL`, cho phép `CLIENT` đọc), **`Nhóm B-Governance-Sensitive`** (`workspace_id NULL`, khóa `app.current_workspace_type IN ('AGENCY', 'SYSTEM')`), hay **`Nhóm C Append-Only`** (gồm `occurred_at`, `received_at`, `correlation_id` — **tuyệt đối cấm `updated_at`, `updated_by`, `row_version`, `archived_at`**, áp dụng `Redact-Before-Insert`); đồng thời dùng `active_legal_hold_ids uuid[] DEFAULT '{}'` khi chịu chi phối `M20-F06`. Gắn nhãn `[MASTER]` cho thực thể/trường gốc, `[PROPOSED]` cho chi tiết hóa và giữ mã `ENTITY-Lxxxx`.
4. **Phân loại 7 Trường GAP & Tách `Safe Default` khỏi `Gate` (`INV-14`):**
   - Mọi tham số vận hành hoặc quy tắc còn mở (`O01–08`, `W-O*`, `P-O*`, `H-O*`, `GAP-*`) phải đăng ký đủ **7 trường phân loại** tại [GAPS.md](../../../../03-planning/GAPS.md) và ánh xạ vào bảng `4.3 Policy/Config Parameters` (`Chặn thiết kế? | Chặn triển khai? | Chặn kích hoạt? | Phạm vi bị chặn | Hành vi khi thiếu cấu hình (Fail-Closed) | Người quyết định | Điều kiện đóng`).
   - `Safe Default (Fail-Closed)` chỉ giúp tiếp tục viết luồng thiết kế mà **không chứng minh chức năng sẵn sàng triển khai**. Tuyệt đối không tự chọn một con số kinh doanh (như tỷ lệ hoa hồng, hạn mức ngân sách) rồi coi là mặc định an toàn; chức năng phụ thuộc phải giữ gate đóng (`Fail-Closed`). Thực thi cuốn chiếu từng module một (`4 pha / module`).

---

## Pha 1 — Grounding & Trace Harvest (`05-tools` Extractor + Contract-First)

Mục tiêu: Gom toàn bộ sự thật đã có trong Master v1.9 và bề mặt liên kết 24 module với lượng token tối thiểu trước khi đặt câu hỏi hay viết spec. **Tìm sự thật trong kho tài liệu là việc của Agent — tuyệt đối không hỏi người dùng những gì đã tra được từ Master/trace/research.**

1. **Pha 0 (Cổng nạp ngữ cảnh Protocol v2 theo [AGENTS.md](../../../../AGENTS.md) Mục 4):** Đọc [active-task.json](../../../../03-planning/agent/active-task.json), phần Sticky đầu [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md), [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md), [INDEX.md](../../../../01-architecture/INDEX.md) và [CONTRACTS-REGISTRY.md](../../../../02-specs/CONTRACTS-REGISTRY.md). Sau đó chạy lệnh trích xuất 4 lớp & 2 chiều (thay `<ArtifactDir>` bằng đường dẫn thực **ngoài kho** để không làm hỏng `verify_delivery_plan.py`):
   ```powershell
   python 05-tools/build_module_context.py --module <Mxx> --out "<ArtifactDir>/scratch/context-<Mxx>.md" --check-tokens
   ```
   *(Lưu ý: Script Python trích xuất không gọi LLM, nhưng việc đọc gói kết quả vẫn tốn token; telemetry mặc định `UNKNOWN` trừ khi truyền `--transcript` của đúng phiên hiện tại.)*
2. Đọc gói ngữ cảnh vừa trích xuất (`context-<Mxx>.md`) thay vì tự nạp toàn bộ `requirements.json` (`2,77 MB`) hay các file `modules/*.md` đã xong:
   - Dùng công cụ đọc tệp theo dải dòng hiện có (ví dụ `read_file` theo `StartLine`/`EndLine`) đọc đúng các mục Master v1.9 trong [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) và đọc đầy đủ `02-specs/contracts/*.md`, `ADR-*.md` được liệt kê trong `context-<Mxx>.md` (các ô tóm tắt có `...` trong `CONTRACTS-REGISTRY.md` bắt buộc phải đọc tiếp file nguồn).
   - Đối chiếu `02-specs/modules/*.md` cũ hoặc `04-research/` **chỉ theo dải dòng cụ thể** khi cần tra ngoại lệ mà `CONTRACTS-REGISTRY.md` chưa đủ chi tiết.
3. **Xác minh gói trước khi sang Pha 3 (soạn spec):** Chạy `python 05-tools/build_module_context.py --verify-packet "<ArtifactDir>/scratch/context-<Mxx>.md"`. Nếu nguồn hoặc gói thay đổi, phải tạo lại gói và đọc phần delta (`.receipt.json` chỉ chứng minh phiên bản nguồn/gói, không chứng minh Agent đã đọc hay hiểu).
4. Đọc khuôn mẫu chuẩn & Kế hoạch 2 Cấp (từ Wave 2–6):
   - [MODULE-SPEC.md](../../../../02-specs/templates/MODULE-SPEC.md)
   - [CONTRACT.md](../../../../02-specs/templates/CONTRACT.md) (nếu module phát sinh public command/event liên module).
   - Nếu là **Wave 2–6**: kiểm tra/lập Kế hoạch tổng Wave `03-planning/waves/WAVE-x-PLAN.md` (theo [WAVE-PLAN.md](../../../../03-planning/templates/WAVE-PLAN.md)) nếu chưa có, và khởi tạo/đọc phiếu Kế hoạch hoàn thành module `03-planning/modules/Mxx-COMPLETION-PLAN.md` (theo [MODULE-COMPLETION-PLAN.md](../../../../03-planning/templates/MODULE-COMPLETION-PLAN.md) — chỉ lưu con trỏ nguồn & bảng điều phối, không chép lặp nội dung đặc tả).

---

## Pha 2 — Cổng Hỏi Ngược Hai Tầng (BMAD + `/speckit.clarify`)

Tuyệt đối **không nhảy thẳng vào viết file `Mxx-*.md`** khi vừa đọc xong Master. Phải rà soát các điểm mù bằng checklist chung tại [ears-and-checklists.md](ears-and-checklists.md) **KẾT HỢP** **1 Cụm Chính tương ứng + các Cụm Liên miền được kích hoạt** trong [domain-lenses.md](domain-lenses.md) (không nạp phần không liên quan) và phân loại thành 2 tầng:

### Tầng 1 — Blocking Clarify (Hỏi chặn trước khi chốt thiết kế)
Áp dụng cho các vấn đề làm sai lệch cấu trúc domain hoặc xung đột giữa các module:
- Ranh giới sở hữu entity/state giữa `Mxx` và module hàng xóm (ví dụ: `M01` vs `M02`, `M08` vs `M09`, `M16` vs `M14`, `M23` vs `M14/M20`).
- State machine cốt lõi (trạng thái hợp lệ, chuyển trạng thái bị cấm, ai có quyền chuyển).
- Nguồn chân lý (Single Source of Truth) khi có nhiều kênh/nguồn ghi đè nhau.
- Hợp đồng công khai (`public command/event`) ảnh hưởng sang module khác.

> **Cách hỏi chuẩn & Tính di động Tool:** Sử dụng công cụ hỏi tương tác hiện có (như `ask_question`), hoặc đặt câu hỏi lựa chọn trực tiếp bằng văn bản nếu phiên không hỗ trợ tool tương tác. Hỏi **từng quyết định một** theo thứ tự phụ thuộc (hoặc gộp 1 câu ngắn nếu độc lập), **luôn đặt phương án `(Recommended)` lên đầu** kèm lý giải ngắn theo `INVARIANTS.md`. Với quyết định chặn, phải đợi người dùng chốt câu trả lời (liên tục làm tiếp phần độc lập không bị phụ thuộc, nhưng **tuyệt đối không tự chốt nghiệp vụ** để đóng module; nếu còn điểm chặn chưa trả lời được, cập nhật rõ vào `Blocking Register` của `03-planning/modules/Mxx-COMPLETION-PLAN.md` kèm người trả lời và điều kiện tiếp tục). Nếu quyết định chốt ranh giới kiến trúc quan trọng xuyên module, ghi thêm ADR mới vào `01-architecture/decisions/ADR-NNN-TEN-NGAN.md` theo mẫu [ADR-001-BASELINE-AND-STACK.md](../../../../01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md).

### Tầng 2 — Non-Blocking Gaps (Ghi nhận `[OPEN-GAP]`, không làm tắc luồng)
Áp dụng cho tham số vận hành hoặc chi tiết chưa thể chốt ngay ở bước thiết kế:
- Ngưỡng SLA/timeout cụ thể, hạn mức ngân sách, tỷ lệ hoa hồng cụ thể, tên nhân sự thực tế, vendor credential cụ thể.
- Ghi nhãn `[OPEN-GAP: GAP-Mxx-NN]` trực tiếp tại mục liên quan trong spec **và** đăng ký đầy đủ 7 trường phân loại vào [GAPS.md](../../../../03-planning/GAPS.md) + Mục `4.3` (phân tách `Chặn thiết kế?` vs `Chặn triển khai?` vs `Chặn kích hoạt?`).

---

## Pha 3 — Soạn thảo Đặc tả (`MODULE-SPEC.md` + EARS + Hybrid Contract)

Tạo tệp tại `02-specs/modules/Mxx-TEN-MODULE.md` (tên ASCII viết hoa, không dấu, dùng `-`), giữ đủ 6 mục lớn và chuẩn đầu ra của [MODULE-SPEC.md](../../../../02-specs/templates/MODULE-SPEC.md):

1. **`## 1. Manifest`**
   - Ghi rõ Baseline (`v1.9` và đúng chuỗi `SHA-256` từ `active-task.json`), các section/line nguồn Master.
   - `Status`: khởi tạo là `Draft`. Khi được duyệt lên `Reviewed` hoặc `Ready (Scope: <phạm vi>)`, bắt buộc ghi kèm `Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At` (`Ready` chỉ dùng theo phạm vi cụ thể đã sạch GAP chặn phạm vi đó và **không** rời `Documentation-Only`).
   - Domain owner (vai trò), owned entities, commands/events/projections, consumers, core/pack boundary, `Read first` / `Read on demand`.
2. **`## 2. Requirement trace`**
   - Liệt kê **tất cả** ID từ `requirements.json` có `owner == Mxx` (và nhóm mở rộng `GAP-03`) **bên trong hàng của bảng Markdown** (không giấu trong comment hay đoạn văn rời).
   - Bảng chuẩn **9 cột**: `| ID nguồn | Source anchor/line | Ý nghĩa | Owner/consumer | Hành vi / Contract | Priority | Applicability | Test | Evidence |`
   - Cột `Hành vi / Contract` trỏ rõ `### 3.x` / `Mxx-Fyy` / `Cxx` (hoặc `N/A (<lý do>)`); cột `Test` liệt kê rõ mã Test tồn tại trong `## 6.2` (hoặc `N/A (<lý do>)` / `[OPEN-GAP: ...]`); cột `Evidence` bắt buộc ghi `Not Run`.
3. **`## 3. Hành vi`**
   - Đủ `3.0A`, `3.0B`, và toàn bộ tiểu mục `### 3.x Mxx-Fyy` đủ 6 phần con.
   - Viết mọi rule hành vi, guard và xử lý lỗi bằng cú pháp **EARS** (xem [ears-and-checklists.md](ears-and-checklists.md)) kèm nhãn `[MASTER]`, `[PROPOSED]`, hoặc `[OPEN-GAP]` (đề xuất đã duyệt giữ `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`), gắn mã rule cục bộ + mã Test liên kết.
   - Bao phủ đủ: State machine (`stateDiagram-v2` nếu ≥ 3 trạng thái), Main flow, Exceptions, Concurrency (`expected_version`/CAS), Idempotency/Retry, Side effects/Dual Outbox (`M19` ngoài vs `M23-F12` nội bộ theo `ADR-005`), Audit & Metric.
4. **`## 4. Data/API`**
   - Logical ERD scoped (Mermaid `erDiagram`), bảng thuộc tính logic `4.2` (**1 bảng = 1 dòng**) tuân thủ chặt 4 nhóm kế thừa của [ADR-004](../../../../01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md) (`Nhóm A`, `Nhóm B-Catalog`, `Nhóm B-Governance-Sensitive`, `Nhóm C Append-Only` cấm `updated_at/updated_by/row_version/archived_at`), bảng `4.3` có đủ 7 trường phân loại GAP, và bảng `4.4` Command/Query/Error envelope.
   - **Quy tắc Hybrid Contract & Backward Drift qua CR:**
     - Lệnh/API nội bộ trong module: mô tả trực tiếp bảng Command/Query/Error envelope ngay tại `4.4`.
     - **Public cross-module command hoặc domain event** (có module khác tiêu thụ): tách file riêng vào `02-specs/contracts/<PRODUCER>-<TEN-CONTRACT>.md` theo mẫu [CONTRACT.md](../../../../02-specs/templates/CONTRACT.md) (đủ bảng 12 phần, schema JSON thực chất không rỗng và ví dụ JSON payload) và đặt link tham chiếu từ mục `Data/API` của cả Producer lẫn Consumer.
     - **Nếu cần bổ sung ngược vào Contract Wave trước đã `Reviewed`/`Ready` (`Backward Drift`):** **Bắt buộc mở `CR-*` tại `02-specs/changes/`** (nếu người dùng đã phê duyệt đúng phạm vi thì ghi nhận luôn phê duyệt vào CR), chỉ sửa **additive** trên `contracts/*.md` + chạy `--build-registry` + ghi `[PENDING-BACKSYNC]` vào [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md) để gom đồng bộ vào `modules/*.md` cuối Wave trước khi đóng CR.
5. **`## 5. UI/operations`**
   - Screens, actions, 4 trạng thái UI (`empty` / `loading` / `error` / `permission denied`), freshness, logs/alerts/runbook/retention/error ownership.
6. **`## 6. Migration và gate`**
   - Upgrade/backfill/flag closure + bảng `6.2 Test Applicability Matrix` **10 cột chuẩn** (mỗi dòng có đủ Tiền điều kiện + Hành động + Kết quả quan sát được, `Build = N/A (Docs-Only)`, `Actual = Not Run / No Repo`, `Status/Evidence = Not Run`, `N/A` phải kèm lý do rõ ràng).

---

## Pha 4 — Analyze & Verify Gate (Spec-Kit `/analyze` + `srs-dd` Checker)

Trước khi báo hoàn thành cho người dùng, tự kiểm tra chéo và chạy tool:

1. **Checklist tự kiểm (`/analyze`) & Fresh-Context Review:**
   - Mọi ID thuộc `Mxx` trong `requirements.json` đều đã xuất hiện trong bảng `## 2. Requirement trace`, trỏ sang `### 3.x` / `Contract` và nối tới mã Test tồn tại ở `## 6.2` chưa?
   - Có mâu thuẫn nào với `INVARIANTS.md` hoặc ADR hiện hành không (ví dụ: ghi đè projection thành nguồn ghi, gộp tenant/workspace, vượt quyền `M14`/`M20`, bỏ qua Dual Outbox theo `ADR-005` giữa `M19` tích hợp ngoài và `M23-F12` sự kiện nội bộ, hoặc gắn `updated_at/row_version` lên bảng `Nhóm C` trái `ADR-004`)?
   - Có bẫy phân tán/đa tác nhân nào chưa khóa chưa: (a) worker nhả DB lock thiếu `lease_token` fencing CAS ở micro-commit/Pha 3; (b) bảng quyết định Reaper/State Machine lệch giữa ADR vs Module vs Contract; (c) cơ chế xóa PII/redact dùng cờ 1 lần làm sót chủ thể thứ hai; (d) mô tả gộp ca test làm đảo nghĩa hành vi hợp lệ?
   - Có từ ngữ mơ hồ kiểu *"hệ thống xử lý phù hợp"*, *"tùy chỉnh linh hoạt"* mà chưa chuyển thành điều kiện EARS hoặc `[OPEN-GAP]` không? Mọi `[OPEN-GAP]` đã đăng ký đủ 7 trường vào `GAPS.md` chưa?
   - Có chữ `Pass` / `Passed` / `Verified` nào lọt vào cột `Evidence`/`Status` không? (Phải là `Not Run`).
   - *(Trước khi phóng Subagent `research` `Fresh-Context Review` — theo [AGENTS.md](../../../../AGENTS.md) Mục 4):* Telemetry mặc định là `UNKNOWN` nếu không truyền `--transcript <duong-dan>` của đúng phiên hiện tại (tuyệt đối không tự chọn transcript gần nhất; `UNKNOWN` không đồng nghĩa `GREEN` và không dựa vào số liệu phiên khác để dừng/compact/mở chat):
     - Nếu telemetry gắn đúng phiên hiện tại báo `GREEN (<170k)` (hoặc khi `UNKNOWN` trong phiên mới còn gọn và cần rà độc lập): Phóng `Fresh-Context Research Subagent` (khuyến nghị model mạnh cho Audit chéo liên module; model nhẹ cho kiểm máy móc). Subagent **ghi toàn bộ báo cáo vào `<ArtifactDir>/scratch/reaudit-<Mxx>.md`** và chỉ gửi tóm tắt `< 1.500` ký tự về Coordinator.
     - Nếu telemetry của đúng phiên hiện tại báo `YELLOW (170k–210k)`: **Cấm** phóng Subagent chạy lâu `> 3 phút` (tránh hết hạn Prompt Cache); tự đối chiếu & chạy verify trong phiên.
     - Nếu telemetry của đúng phiên hiện tại báo `RED (>210k)`: Dừng mở rộng, lưu file + ghi `Handoff` vào `PROGRESS.md` để sang phiên sạch chạy Re-Audit.
2. **Cập nhật điều hướng & nhật ký (`Handoff`):**
   - *(Nếu chạy đơn lẻ / hoặc vai Coordinator):* Tái sinh [CONTRACTS-REGISTRY.md](../../../../02-specs/CONTRACTS-REGISTRY.md) (`--build-registry`), cập nhật dòng `Mxx` trong [02-specs/README.md](../../../../02-specs/README.md) (trạng thái + link tệp), đồng bộ `active-task.json` (`wave*_specs`, `proposed_next_slice`), cập nhật `03-planning/modules/Mxx-COMPLETION-PLAN.md` (nếu Wave 2–6; chỉ xác nhận hoàn thành đặc tả `Documentation-Only` khi đạt đủ điều kiện hoàn thành và không còn mục chặn phạm vi mục tiêu), cập nhật mục **`## 0. Sticky Wave Context` ở đầu** [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md) **và** ghi nhật ký phiên mới ở cuối `PROGRESS.md` (gồm: *Module mục tiêu, đường dẫn gói ngữ cảnh & kết quả `--verify-packet`, trạng thái telemetry, quyết định áp dụng/không áp dụng `W1` (`INV-26..28`) có lý do, đã khóa / Contract mới / `[PENDING-BACKSYNC]` nếu có / Blocking GAP chờ chốt / Lệnh gợi ý phiên sau*), cùng các GAP mới đủ 7 trường vào [GAPS.md](../../../../03-planning/GAPS.md).
   - *(Nếu đang là Worker trong sóng song song):* **Không sửa** `README.md`, `PROGRESS.md`, `GAPS.md`; trả về tóm tắt `< 1.500` ký tự + đường dẫn file kết quả + kết quả kiểm cục bộ `--file` để Coordinator hợp nhất.
   - *(Lưu ý chuyển tiếp `M18`):* Khi hoàn thiện phần baseline `M18-F01–07` vào [M18-BI-REPORTING-EXPANSION.md](../../../../02-specs/modules/M18-BI-REPORTING-EXPANSION.md), gỡ tên tệp này khỏi `LEGACY_EXEMPT_MODULES` trong `05-tools/verify_module_spec.py`.
3. **Chạy lệnh kiểm chứng theo Quy chuẩn Duy nhất tại `SKILL.md` Mục 4:**
   - *(Worker song song):* Chỉ chạy `python 05-tools/verify_module_spec.py --file 02-specs/modules/Mxx-TEN-MODULE.md` (kèm contract mới tạo nếu có).
   - *(Đơn lẻ hoặc Coordinator kết thúc phiên):* Chạy đủ bộ kiểm chứng toàn kho quy định tại Mục 4 của [SKILL.md](../SKILL.md) (`--build-registry` + 4 lệnh toàn kho gồm `verify_module_spec.py` **không** `--file`).
