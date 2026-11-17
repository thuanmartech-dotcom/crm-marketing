# Hướng dẫn Sử dụng Chi tiết Skill `crm-ba-spec`

Tài liệu này hướng dẫn cách gọi và phối hợp với Agent khi dùng skill `crm-ba-spec` để bóc tách hoặc bảo trì đặc tả module (`M01–M24`), lập/bảo trì slice (`SL00–SL11`), rà soát chéo, xuất phiếu hỏi Stakeholder và quản lý thay đổi spec.

---

## 1. Các câu lệnh (Prompt) mẫu để gọi nhanh

Skill được phát hiện qua `.agents/skills/crm-ba-spec/SKILL.md`. Bạn chỉ cần nhắn theo ngữ cảnh hoặc gọi thẳng tên skill:

### A. Tách mới / Hoàn thiện / Bảo trì một Module (`M01–M24`)
- **Bước chuẩn bị Wave 2–6 (Kế hoạch 2 Cấp):**
  > `Dùng skill crm-ba-spec lập Kế hoạch tổng Wave 2 (03-planning/waves/WAVE-2-PLAN.md theo WAVE-PLAN.md) và Kế hoạch hoàn thành module đầu tiên M01 (03-planning/modules/M01-COMPLETION-PLAN.md theo MODULE-COMPLETION-PLAN.md), không thực thi soạn spec vội.`
- **Cú pháp tách mới (`M01–M20`, gồm hoàn thiện `M18`):**
  > `Dùng skill crm-ba-spec tách đặc tả module M01 theo 03-planning/modules/M01-COMPLETION-PLAN.md (liên tục xử lý việc được phép, gặp quyết định chặn thì ghi Blocking Register và dừng hỏi tôi chốt).`
- **Muốn Agent hỏi kỹ từng quyết định kiến trúc/edge-case trước khi viết:**
  > `Dùng skill crm-ba-spec tách module M02. Áp dụng /grill-me ở Pha 2 để hỏi tôi chốt hết state machine và ranh giới với M01, M07 trước khi tạo file.`
- **Muốn tách riêng phần Contract liên module hoặc mở rộng additive contract Wave trước (`Backward Contract Drift`):**
  > `Dùng skill crm-ba-spec chế độ review-change mở Change Proposal mở rộng additive contract C19 để M03 sử dụng, cập nhật CONTRACTS-REGISTRY.md và ghi [PENDING-BACKSYNC].`

### B. Lập hoặc Bảo trì đặc tả Lát cắt Triển khai (`SL00–SL11`)
- **Cú pháp chuẩn (`SL00`, `SL02–SL07`):**
  > `Dùng skill crm-ba-spec chế độ slice lập đặc tả cho SL02 (Omnichannel Intake & Inbox tối thiểu).`
- **Lưu ý điều kiện:** Các module chính nằm trong slice (ví dụ `M01`, `M03`, `M19` cho `SL02`) nên được tách module spec trước để tránh slice phải tự định nghĩa lại domain model. Nếu sửa slice đã `Reviewed` (`SL01`, `SL08`, `SL09–11`), đi qua Change Proposal (`CR-*`).

### C. Rà soát chéo chống lệch spec (`Analyze`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng A - Analyze) rà soát chéo cụm M01, M02, M03 và đối chiếu INVARIANTS.md.`

### D. Sửa đổi spec đã `Reviewed` / `Ready` (`OpenSpec Change Proposal`)
- **Bước đề xuất (`propose`):**
  > `Dùng skill crm-ba-spec chế độ review-change tạo Change Proposal sửa quy tắc đối soát trong M21 / SL08.`
- **Bước áp dụng (`apply` & `archive`):**
  > `Tôi đồng ý CR-20261115-xxx, hãy apply vào spec đích, cập nhật GAPS/PROGRESS, archive CR và chạy kiểm chứng.`

### E. Chạy song song theo Sóng phụ thuộc (`Coordinator + Subagents`)
- **Cú pháp chuẩn (ví dụ Sóng 1 nền tảng):**
  > `Dùng skill crm-ba-spec chạy song song Pha 1 & Pha 2 cho Sóng 1 (M14, M19, M20, M01), gom câu hỏi Blocking gửi tôi chốt trước khi viết file.`
- **Cú pháp chờ theo phụ thuộc:**
  > `Tách song song M14, M19, M20, M01; M03 và M02 giữ chờ tới khi có Public Contract của M01 và M19 mới chạy tiếp.`

### F. Xuất Phiếu hỏi Stakeholder (`/to-questionnaire`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng C) gom các [OPEN-GAP] của M09, M10, M17 thành phiếu câu hỏi cho phòng Tài chính/Kế toán duyệt.`

### G. Rà soát độc lập & Đóng gói bàn giao phiên (`Fresh-Context Review` + `Handoff`)
- **Rà soát bằng subagent context sạch:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng A) chạy subagent context sạch đối chiếu M01-CUSTOMER-IDENTITY-MERGE.md với INVARIANTS.md.`
- **Bàn giao cuối phiên dài:**
  > `Tổng hợp handoff cuối phiên vào PROGRESS.md (đã khóa gì, contract nào mới, GAP nào đang chờ, lệnh chạy phiên tiếp theo).`

---

## 2. Điều gì diễn ra trong 1 phiên bóc tách Module chuẩn?

Mỗi **1 phiên sạch** chỉ phụ trách **1 module** (riêng module lớn như `M03` tách 2 phiên theo pha; tuân thủ **Protocol v2** tại [AGENTS.md](../../../../AGENTS.md) Mục 4 — phanh `Đèn Vàng 170k` / `Đèn Đỏ 210k` chỉ áp dụng khi telemetry được gắn tường minh đúng transcript của phiên hiện tại, mặc định là `UNKNOWN`). Khi bạn gọi Agent tách một module (ví dụ `M01`), Agent sẽ chạy đúng **4 pha**:

1. **Pha 0 + Pha 1 — Nạp & Xác minh Ngữ cảnh có Chọn lọc (`Protocol v2`):**
   - Agent đọc manifest `active-task.json`, phần Sticky đầu `PROGRESS.md`, `INVARIANTS.md`, `INDEX.md`, [CONTRACTS-REGISTRY.md](../../../../02-specs/CONTRACTS-REGISTRY.md), rồi chạy `python 05-tools/build_module_context.py --module M01 --out "<ArtifactDir>/scratch/context-M01.md" --check-tokens` *(thay `<ArtifactDir>` bằng đường dẫn thực ngoài kho; Python trích xuất không gọi LLM nhưng việc đọc gói kết quả vẫn tốn token)*.
   - Đọc gói `context-M01.md`, các Contract & ADR liên quan đầy đủ (mọi ô có `...` trong registry phải đọc tiếp file nguồn), đúng dải dòng tương ứng trong `CRM_MASTER_BRD_SRS_HOP_NHAT.md` (`v1.9`), và chạy `--verify-packet` xác minh gói trước khi sang Pha 3.
2. **Pha 2 — Cổng hỏi ngược 2 tầng (tương tác linh hoạt theo công cụ hỏi hiện có hoặc trực tiếp trong chat):**
   - Agent **không tự bịa** các quyết định ranh giới hay rule thiếu.
   - Với **Tầng 1 (Blocking)** — Agent dùng công cụ hỏi tương tác (như `ask_question`) hoặc hỏi trực tiếp bằng văn bản có phương án `(Recommended)` cho từng quyết định chặn, ví dụ:
     - *Ranh giới dữ liệu:* Contact trùng SĐT ở 2 workspace có được gộp tự động hay chỉ link theo `M01` + kiểm quyền `M14`?
     - *State machine:* Khi merge 2 Contact (`MERGED`), bản ghi nguồn bị khóa chỉ đọc hay cho phép unmerge?
     - *Concurrency:* Khi 2 nhân viên sửa cùng 1 hồ sơ thì dùng `expected_version` chặn hay last-write-wins?
   - Với **Tầng 2 (Non-blocking)** — các tham số chưa chốt được ngay (timeout cụ thể, ngưỡng cảnh báo trùng...) sẽ được gắn `[OPEN-GAP: GAP-M01-xx]` và ghi đủ 7 trường phân loại vào `03-planning/GAPS.md` (tách rõ chỉ hỗ trợ viết spec vs chặn triển khai/kích hoạt).
3. **Pha 3 — Sinh đặc tả chuẩn EARS & Hybrid Contract:**
   - Tạo `02-specs/modules/M01-CUSTOMER-IDENTITY-MERGE.md` theo đúng 6 mục của `MODULE-SPEC.md` (bảng `Requirement trace` 9 cột nối tới `### 3.x` / Contract và mã Test trong `## 6.2`, `4.2` tuân thủ 4 nhóm `ADR-004`).
   - Mọi hành vi viết theo câu điều kiện **EARS** (`Khi ...`, `Nếu ...`, `Trong khi ... phải ...`) và gắn nhãn `[MASTER]` / `[PROPOSED]` / `[OPEN-GAP]` (đề xuất được duyệt giữ nguyên `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`).
   - Nếu phát sinh command/event public gửi sang module khác (ví dụ `ContactMerged` gửi cho `M02`, `M03`, `M08`), Agent tách riêng ra `02-specs/contracts/M01-CONTACT-MERGED.md` theo `CONTRACT.md` (có JSON field schema và ví dụ JSON payload). Nếu cần bổ sung ngược vào Contract Wave trước đã `Reviewed`/`Ready`, đi qua `CR-*` nhẹ và ghi `[PENDING-BACKSYNC]` vào `PROGRESS.md`.
4. **Pha 4 — Fresh-Context Review (File-Backed) & Cổng kiểm chứng Toàn kho (`SKILL.md` Mục 4):**
   - Kiểm tra độ phủ ID và đối soát ngữ nghĩa thủ công (`session_token_telemetry` mặc định `UNKNOWN` nếu không truyền `--transcript <path>` của đúng phiên hiện tại; `UNKNOWN` không đồng nghĩa `GREEN`), cập nhật `CONTRACTS-REGISTRY.md`, `02-specs/README.md` và `03-planning/agent/PROGRESS.md` (kèm đường dẫn gói, kết quả `--verify-packet` và quyết định `W1`).
   - Cuối phiên bắt buộc chạy đủ bộ kiểm chứng toàn kho ở Mục 4 `SKILL.md` (không thay bằng `--file`) và chỉ báo `Not Run` cho test ứng dụng.

---

## 3. Lệnh kiểm tra thủ công trong Terminal (nếu bạn muốn tự kiểm)

Chạy tại `d:\AI Agent\CRM`:

```powershell
# Tái sinh Bảng tra cứu liên module & trích xuất gói ngữ cảnh gọn cho M01 (có thể thêm --transcript <path-phien-hien-tai>)
python 05-tools/build_module_context.py --build-registry --module M01 --out "<ArtifactDir>/scratch/context-M01.md" --check-tokens

# Xác minh gói ngữ cảnh và nguồn trước khi soạn đặc tả (Protocol v2)
python 05-tools/build_module_context.py --verify-packet "<ArtifactDir>/scratch/context-M01.md"

# Kiểm tra toàn bộ 02-specs/ (modules, contracts, changes, registry) và xuất báo cáo độ phủ ID
python 05-tools/verify_module_spec.py

# Kiểm tra riêng 1 file module vừa viết
python 05-tools/verify_module_spec.py --file 02-specs/modules/M01-CUSTOMER-IDENTITY-MERGE.md

# Chạy trọn bộ cổng kiểm chứng của dự án
python 05-tools/build_module_context.py --build-registry
python 05-tools/build_delivery_inventory.py
python 05-tools/verify_delivery_plan.py
python 05-tools/verify_hrm_integration.py
python 05-tools/verify_module_spec.py
```

Kết quả chi tiết (gồm danh sách ID còn thiếu của từng module so với `requirements.json`, `unknown_cross_module_refs` và `session_token_telemetry`) được ghi tại `03-planning/evidence/module-spec-validation.json`.

---

## 4. Xử lý các tình huống thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Muốn Agent giữ trạng thái `Draft` để team review tiếp, chưa muốn chốt | Nói rõ: *"Giữ `Status: Draft`, phần nào chưa rõ thì ghi `[OPEN-GAP]` vào `GAPS.md`."* |
| Muốn chốt nâng trạng thái một module từ `Draft` → `Reviewed` hoặc `Ready` | Nhắn: *"Chốt `M01` lên `Reviewed` (hoặc `Ready` cho `SL02`) sau khi tôi xác nhận các `[PROPOSED]` và đối soát các `[OPEN-GAP]`."* Agent sẽ ghi nhận `Approved_Scope`, `Approved_By`, `Decision_Ref` trong Manifest (vẫn giữ `[PROPOSED]` kèm `decision_ref` và vẫn trong giai đoạn `Documentation-Only`). |
| Gửi trả lời Stakeholder cho các `[OPEN-GAP]` ở tài liệu đã `Reviewed`/`Ready` | Dùng chế độ `review-change`: Agent tự kiểm tra `Status` file; nếu đã `Reviewed`/`Ready` sẽ mở `CR-*` (ghi nhận luôn phê duyệt nếu bạn đã chốt đúng phạm vi), áp dụng sửa đổi và chỉ đóng GAP sau khi toàn bộ tài liệu liên quan đạt kiểm chứng. |
| Muốn sửa một phần trong `M21`, `M22`, `SL01` đã ổn định | Gọi chế độ `review-change` để đi qua `02-specs/changes/CR-*.md` thay vì sửa chéo không dấu vết. |
| Telemetry phiên hiện tại chạm ngưỡng `YELLOW/RED` (`~170k–210k` tokens qua `--transcript` của đúng phiên) hoặc chuẩn bị sang module mới | Yêu cầu Agent ghi `Handoff` vào `PROGRESS.md` và mở cuộc trò chuyện mới sạch (1 module / 1 phiên; không dựa vào telemetry của phiên khác khi đang `UNKNOWN`). |
| Muốn kiểm tra nghiêm ngặt cả file mở rộng (`M18`, `M23`, `M24`) theo đủ 6 mục `MODULE-SPEC.md` | Chạy `python 05-tools/verify_module_spec.py --strict-all`. |
