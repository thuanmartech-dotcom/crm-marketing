---
name: crm-ba-spec
description: >-
  Hệ thống quy trình phân tích BA & chuẩn hóa đặc tả cho dự án CRM (Master v1.9 -> 02-specs/).
  Kích hoạt khi người dùng yêu cầu phân tích, brainstorm, tách hoặc bảo trì đặc tả module (M01–M24),
  tách/bảo trì lát cắt triển khai (SL00–SL11), tách public contract (02-specs/contracts/),
  rà soát chéo đặc tả (Analyze), xuất phiếu hỏi stakeholder, hoặc đề xuất sửa đổi đặc tả đã chốt (Change Proposal).
  Chắt lọc tinh hoa BMAD Analyst + Spec-Kit (/clarify, /analyze) + EARS + srs-dd + OpenSpec,
  tuân thủ tuyệt đối kỷ luật Documentation-Only trong AGENTS.md.
---

# CRM BA & Spec-Driven Workflow (`crm-ba-spec`)

Skill điều phối phân tích nghiệp vụ (BA) và tách đặc tả từ [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`) sang `02-specs/` trước khi giao AI Coding Agent.

## 1. Ranh giới bất biến (Không bao giờ vi phạm)

1. **Documentation-Only:** Tuyệt đối không tạo code ứng dụng (`src/`, `apps/`, `packages/`), `package.json`, SQL migration hay chạy test phần mềm.
2. **Master v1.9 là nguồn sự thật nghiệp vụ:** Không sửa trực tiếp `00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md` nếu chưa có quyết định cập nhật baseline; mọi suy diễn mới phải tách bạch rõ bằng 3 nhãn nguồn:
   - `[MASTER]` — Quy định/ID có sẵn trong Master v1.9 (kèm anchor/dòng nguồn).
   - `[PROPOSED]` — Đề xuất thiết kế kỹ thuật/nghiệp vụ mới khi brainstorm. Đề xuất đã được duyệt vẫn giữ `[PROPOSED]` kèm `decision_ref` và trạng thái duyệt; **tuyệt đối không đổi thành `[MASTER]`**.
   - `[OPEN-GAP: GAP-...]` — Điểm thiếu/chưa chốt; **tuyệt đối không bịa số liệu KPI, SLA, công thức hay tên cột**, phải ghi đủ 7 trường phân loại vào [GAPS.md](../../../03-planning/GAPS.md).
3. **Không đọc lẫn `99-archive/`** làm nguồn thiết kế hiện hành.
4. **Trung thực kiểm chứng & ranh giới trạng thái:** Mọi trạng thái test ứng dụng CRM luôn là `Not Run` (các script ở `05-tools/` chỉ kiểm chứng tài liệu/checker, không thay thế test ứng dụng). Trạng thái `Ready (Scope: ...)` chỉ khẳng định đủ đặc tả cho phạm vi bàn giao đó, **không tự cho phép chuyển khỏi giai đoạn `Documentation-Only`**.
5. **Khóa đường sửa tài liệu đã duyệt:** Mọi chỉnh sửa trên tài liệu đã `Reviewed` hoặc `Ready` (kể cả đóng GAP sau câu trả lời Stakeholder lẫn mở rộng additive contract Wave trước) đều phải đi qua Change Proposal tại `02-specs/changes/`.

---

## 2. Chọn chế độ thực thi theo yêu cầu (`M01–M24`, `SL00–SL11`)

Xác định đúng chế độ và **chỉ đọc playbook tương ứng** trong `references/` để tiết kiệm context:

| Chế độ | Khi nào dùng | Playbook bắt buộc đọc |
|---|---|---|
| **`module`** | Tách mới/hoàn thiện đặc tả module (`M01–M20`, gồm hoàn thiện `M18-F01–07`) kèm public contract; hoặc rà soát cấu trúc module | [references/module-workflow.md](references/module-workflow.md) |
| **`slice`** | Lập mới đặc tả lát cắt triển khai (`SL00`, `SL02–SL07`) hoặc nâng cấp/đối soát slice hiện có (`SL01`, `SL08`, `SL09–11` qua CR) | [references/slice-workflow.md](references/slice-workflow.md) |
| **`review-change`** | Rà chéo chống lệch spec (`Luồng A: Analyze / Fresh-Context`), xuất Phiếu hỏi Stakeholder (`Luồng C`), hoặc sửa/rà khớp bất kỳ spec nào đã `Reviewed`/`Ready` gồm `M14/16/19/20/23/24`, `M21/22`, `C14..C24`, `SL01` (`Luồng B: OpenSpec CR`) | [references/review-change-workflow.md](references/review-change-workflow.md) |

Ngoài ra:
- Đối chiếu nhanh mẫu câu EARS và checklist 7 điểm chung tại [references/ears-and-checklists.md](references/ears-and-checklists.md) khi viết mục hành vi.
- Đọc **1 Cụm Chính tương ứng** cộng thêm **các Cụm Liên miền được kích hoạt** (theo Bảng Kích hoạt Liên miền) trong [references/domain-lenses.md](references/domain-lenses.md) để hỏi xoáy bẫy đặc thù cho từng module thuộc `M01–M24`.
- Từ **Wave 2–6**, áp dụng **Mô hình Kế hoạch 2 Cấp** ([WAVE-PLAN.md](../../../03-planning/templates/WAVE-PLAN.md) tại `03-planning/waves/WAVE-x-PLAN.md` và [MODULE-COMPLETION-PLAN.md](../../../03-planning/templates/MODULE-COMPLETION-PLAN.md) tại `03-planning/modules/Mxx-COMPLETION-PLAN.md`): liên tục xử lý mọi việc đã được phép trong phạm vi rõ ràng, nhưng **tuyệt đối không tự chốt nghiệp vụ** để đóng module cho đủ kế hoạch; khi gặp điểm chặn thật từ Chủ dự án hoặc phụ thuộc chưa chốt, dừng đúng nhánh đó, ghi rõ người trả lời & điều kiện tiếp tục vào `Blocking Register` và giữ nguyên giai đoạn `Documentation-Only`.
- Xem ví dụ lệnh gọi và quy trình tương tác chi tiết cho người dùng tại [references/usage-guide.md](references/usage-guide.md).

---

## 3. Chế độ chạy song song theo Sóng (`Coordinator + Subagents`)

Khi người dùng yêu cầu chạy song song nhiều module (ví dụ theo Sóng phụ thuộc trong [INDEX.md](../../../01-architecture/INDEX.md)), **bắt buộc tuân thủ 4 khóa an toàn** (do kho hiện chưa dùng `.git`):

1. **Khóa phạm vi ghi của Worker:** Mỗi Subagent chỉ được tạo/sửa file của chính module mình (`02-specs/modules/Mxx-*.md`, `02-specs/contracts/Mxx-*.md`) và chạy kiểm cục bộ `--file` rồi trả kết quả cục bộ về Coordinator.
2. **Gom cổng hỏi ngược:** Chạy song song Pha 1–2 để trích danh sách câu hỏi Blocking về Coordinator; Coordinator hỏi người dùng chốt một lượt (qua công cụ hỏi tương tác hiện có như `ask_question`, hoặc hỏi trực tiếp bằng văn bản nếu phiên không có tool tương tác) rồi mới thả song song Pha 3.
3. **Chờ Public Contract theo DAG:** Module sau (`M02`, `M03`, `M08`, `M09`, `M10`...) chỉ chạy Pha 3 khi module nền tảng đã chốt xong Public Contract liên quan.
4. **Chỉ Coordinator ghi file dùng chung & tổng kiểm:** Duy nhất Coordinator hợp nhất các cập nhật vào `02-specs/README.md`, `03-planning/GAPS.md`, `03-planning/agent/PROGRESS.md`, tái sinh `CONTRACTS-REGISTRY.md` và chạy đủ bộ lệnh kiểm chứng toàn kho ở Mục 4 sau khi sóng kết thúc.

---

## 3B. Kỷ luật Ngữ cảnh Protocol v2, Telemetry & Khóa Liên kết Chéo

1. **1 Module / 1 Phiên sạch:** Không chạy xuyên nhiều module trong cùng 1 hội thoại (module lớn như `M03` tách 2 phiên theo pha).
2. **Nạp & Kiểm chứng Ngữ cảnh (Protocol v2 — theo [AGENTS.md](../../../AGENTS.md) Mục 4):**
   - Đọc tối thiểu [active-task.json](../../../03-planning/agent/active-task.json), phần Sticky đầu [PROGRESS.md](../../../03-planning/agent/PROGRESS.md), [INVARIANTS.md](../../../01-architecture/INVARIANTS.md), [INDEX.md](../../../01-architecture/INDEX.md) và [CONTRACTS-REGISTRY.md](../../../02-specs/CONTRACTS-REGISTRY.md).
   - Chạy `python 05-tools/build_module_context.py --module <Mxx> --out "<ArtifactDir>/scratch/context-<Mxx>.md" --check-tokens` (thay `<ArtifactDir>` bằng đường dẫn thực ngoài kho; với slice chạy cho từng module thuộc phạm vi, với review workflow/checker chọn module đại diện và các module bị ảnh hưởng). Script Python trích xuất không gọi LLM, **nhưng việc đọc gói kết quả vẫn tốn token**.
   - Đọc gói vừa trích xuất, đúng `contracts/*.md`, `ADR-*` và dải dòng `Master v1.9` được chỉ định (qua `read_file` theo khoảng dòng; các ô tóm tắt có `...` trong `CONTRACTS-REGISTRY.md` bắt buộc phải đọc tiếp file nguồn).
   - Trước khi soạn spec, chạy `python 05-tools/build_module_context.py --verify-packet "<ArtifactDir>/scratch/context-<Mxx>.md"`. Nếu nguồn hoặc gói thay đổi phải tạo lại và đọc delta; `.receipt.json` chứng minh phiên bản nguồn/gói, không chứng minh agent đã đọc hoặc hiểu.
3. **Telemetry Phiên & Ngưỡng Phanh 2 Mức Đèn (`Protocol v2`):**
   - `session_token_telemetry` mặc định là **`UNKNOWN`**; chỉ truyền `--transcript <duong-dan>` khi đã xác định đúng transcript của **phiên hiện tại** (tuyệt đối không tự chọn transcript gần nhất). **`UNKNOWN` không đồng nghĩa `GREEN`**; không dừng/compact/mở chat từ số liệu của phiên khác.
   - Chỉ khi telemetry gắn đúng phiên hiện tại báo vượt ngưỡng mới kích hoạt phanh:
     - **Đèn Vàng (`170.000–210.000` tokens):** Cấm phóng Subagent chạy lâu (`> 3 phút`) để tránh hết hạn Prompt Cache khi nhận kết quả; tự hoàn tất phần việc còn lại trong phiên.
     - **Đèn Đỏ (`> 210.000` tokens):** Dừng mở rộng ngay, lưu file xuống đĩa, ghi bàn giao ngắn vào [PROGRESS.md](../../../03-planning/agent/PROGRESS.md) và mở phiên mới sạch (hoặc `/compact`).
4. **File-Backed Subagent Handoff & Phân tầng Model:**
   - Mọi Subagent (`Re-Auditor` / `Researcher` / `Worker`) ghi báo cáo chi tiết vào `<ArtifactDir>/scratch/` (**ngoài kho `d:\AI Agent\CRM`** để không ảnh hưởng `verify_delivery_plan.py`), và chỉ gửi tóm tắt **`< 1.500` ký tự** + đường dẫn file qua cơ chế nhắn tin giữa các agent (hoặc trả về trực tiếp cho Coordinator).
   - Khuyến nghị dùng model nhẹ/nhanh cho đọc quét/kiểm bảng cơ học; dùng model mạnh cho `Pha 2` hỏi chặn, `Pha 3` thiết kế & `Fresh-Context Re-Audit`.
5. **Xử lý Lệch Ngược (`Backward Contract Drift` qua CR bắt buộc):** Khi module Wave 2–5 cần mở rộng field/event/enum của Contract đã `Reviewed`/`Ready` ở Wave trước, **bắt buộc mở Change Proposal nhẹ (`CR-*`) tại `02-specs/changes/`** (nếu người dùng đã phê duyệt đúng phạm vi mở rộng đó thì ghi nhận luôn phê duyệt vào CR, không hỏi lại máy móc), chỉ sửa **additive** trên `02-specs/contracts/*.md`, chạy `--build-registry` cập nhật [CONTRACTS-REGISTRY.md](../../../02-specs/CONTRACTS-REGISTRY.md), và ghi `[PENDING-BACKSYNC]` vào [PROGRESS.md](../../../03-planning/agent/PROGRESS.md) để gom đồng bộ vào `modules/*.md` cuối Wave (chỉ đóng/archive CR sau khi backsync hoàn tất; không nạp lại toàn văn `modules/` cũ vào phiên hiện tại).

---

## 4. Cổng kiểm chứng bắt buộc (Quy định Duy nhất cho Toàn bộ Skill)

Mọi playbook đều tuân theo đúng 1 quy chuẩn kiểm chứng duy nhất dưới đây:

1. **Trong lúc đang soạn thảo hoặc vai Worker song song:** Được phép kiểm riêng từng file đang viết:
   ```powershell
   python 05-tools/verify_module_spec.py --file <duong-dan-file>
   ```
   Worker trả kết quả kiểm cục bộ về Coordinator; kết quả `--file` **không thay thế** kiểm chứng toàn kho.
2. **Khi kết thúc phiên có sửa tài liệu trong `01-architecture/`, `02-specs/`, `03-planning/` (hoặc vai Coordinator cuối sóng):**
   - Cập nhật bảng trạng thái trong [02-specs/README.md](../../../02-specs/README.md) (nếu có thêm/đổi trạng thái module hoặc slice).
   - Cập nhật nhật ký phiên tại [03-planning/agent/PROGRESS.md](../../../03-planning/agent/PROGRESS.md) và [03-planning/GAPS.md](../../../03-planning/GAPS.md) (nếu phát sinh/cập nhật `[OPEN-GAP]`).
   - Tái sinh [CONTRACTS-REGISTRY.md](../../../02-specs/CONTRACTS-REGISTRY.md) (nếu có thêm/sửa module, contract hoặc ADR) và chạy **đủ bộ kiểm chứng toàn kho** (KHÔNG dùng `--file`) từ `d:\AI Agent\CRM`:
     ```powershell
     python 05-tools/build_module_context.py --build-registry
     python 05-tools/build_delivery_inventory.py
     python 05-tools/verify_delivery_plan.py
     python 05-tools/verify_hrm_integration.py
     python 05-tools/verify_module_spec.py
     ```
3. Không tuyên bố `Ready`, `implementation-ready` hay `Pass` nếu còn lỗi từ các script trên hoặc còn GAP chặn phạm vi tương ứng chưa chốt.
