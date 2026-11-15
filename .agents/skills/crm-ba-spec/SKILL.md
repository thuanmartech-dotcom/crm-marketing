---
name: crm-ba-spec
description: >-
  Hệ thống quy trình phân tích BA & chuẩn hóa đặc tả cho dự án CRM (Master v1.9 -> 02-specs/).
  Kích hoạt khi người dùng yêu cầu phân tích, brainstorm, tách đặc tả module (M01–M20),
  tách lát cắt triển khai (SL00, SL02–SL07), tách public contract (02-specs/contracts/),
  rà soát chéo đặc tả (Analyze), hoặc đề xuất sửa đổi đặc tả đã chốt (Change Proposal).
  Chắt lọc tinh hoa BMAD Analyst + Spec-Kit (/clarify, /analyze) + EARS + srs-dd + OpenSpec,
  tuân thủ tuyệt đối kỷ luật Documentation-Only trong AGENTS.md.
---

# CRM BA & Spec-Driven Workflow (`crm-ba-spec`)

Skill điều phối phân tích nghiệp vụ (BA) và tách đặc tả từ [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (`v1.9`) sang `02-specs/` trước khi giao AI Coding Agent.

## 1. Ranh giới bất biến (Không bao giờ vi phạm)

1. **Documentation-Only:** Tuyệt đối không tạo code ứng dụng (`src/`, `apps/`, `packages/`), `package.json`, SQL migration hay chạy test phần mềm.
2. **Master v1.9 là nguồn sự thật nghiệp vụ:** Không sửa trực tiếp `00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md` nếu chưa có quyết định cập nhật baseline; mọi suy diễn mới phải tách bạch rõ bằng 3 nhãn nguồn:
   - `[MASTER]` — Quy định/ID có sẵn trong Master v1.9 (kèm anchor/dòng nguồn).
   - `[PROPOSED]` — Đề xuất thiết kế kỹ thuật/nghiệp vụ mới khi brainstorm.
   - `[OPEN-GAP]` — Điểm thiếu/chưa chốt; **tuyệt đối không bịa số liệu KPI, SLA, công thức hay tên cột**, phải ghi vào [GAPS.md](../../../03-planning/GAPS.md).
3. **Không đọc lẫn `99-archive/`** làm nguồn thiết kế hiện hành.
4. **Trung thực kiểm chứng:** Mọi trạng thái test ứng dụng luôn là `Not Run`; chỉ báo cáo kết quả kiểm chứng tài liệu sau khi chạy đủ script ở `05-tools/`.

---

## 2. Chọn chế độ thực thi theo yêu cầu

Xác định đúng chế độ và **chỉ đọc playbook tương ứng** trong `references/` để tiết kiệm context:

| Chế độ | Khi nào dùng | Playbook bắt buộc đọc |
|---|---|---|
| **`module`** | Tách mới hoặc hoàn thiện đặc tả một module (`M01–M20`) kèm contract liên module | [references/module-workflow.md](references/module-workflow.md) |
| **`slice`** | Lập đặc tả lát cắt triển khai (`SL00`, `SL02–SL07`) từ các module đã có | [references/slice-workflow.md](references/slice-workflow.md) |
| **`review-change`** | Rà chéo chống lệch spec (`/analyze`, `Fresh-Context Review`), xuất Phiếu hỏi Stakeholder, hoặc sửa spec đã `Reviewed`/`Ready` (`OpenSpec`) | [references/review-change-workflow.md](references/review-change-workflow.md) |

Ngoài ra:
- Đối chiếu nhanh mẫu câu EARS và checklist 7 điểm chung tại [references/ears-and-checklists.md](references/ears-and-checklists.md) khi viết mục hành vi.
- Đọc đúng **1 Cụm tương ứng** trong [references/domain-lenses.md](references/domain-lenses.md) để hỏi xoáy bẫy đặc thù theo từng nhóm nghiệp vụ (`M01–M20`).
- Xem ví dụ lệnh gọi và quy trình tương tác chi tiết cho người dùng tại [references/usage-guide.md](references/usage-guide.md).

---

## 3. Chế độ chạy song song theo Sóng (`Coordinator + Subagents`)

Khi người dùng yêu cầu chạy song song nhiều module (ví dụ theo Sóng phụ thuộc trong [INDEX.md](../../../01-architecture/INDEX.md)), **bắt buộc tuân thủ 4 khóa an toàn** (do kho hiện chưa dùng `.git`):

1. **Khóa phạm vi ghi của Worker:** Mỗi Subagent chỉ được tạo/sửa file của chính module mình (`02-specs/modules/Mxx-*.md`, `02-specs/contracts/Mxx-*.md`) và chạy kiểm đơn lẻ `--file`.
2. **Gom cổng hỏi ngược:** Chạy song song Pha 1–2 để trích danh sách câu hỏi Blocking về Coordinator; Coordinator hỏi người dùng chốt một lượt rồi mới thả song song Pha 3.
3. **Chờ Public Contract theo DAG:** Module sau (`M02`, `M03`, `M08`, `M09`, `M10`...) chỉ chạy Pha 3 khi module nền tảng đã chốt xong Public Contract liên quan.
4. **Chỉ Coordinator ghi file dùng chung & tổng kiểm:** Duy nhất Coordinator hợp nhất các cập nhật vào `02-specs/README.md`, `03-planning/GAPS.md`, `03-planning/agent/PROGRESS.md` và chạy bộ 4 script ở `05-tools/` sau khi sóng kết thúc.

---

## 4. Cổng kiểm chứng bắt buộc trước khi kết thúc phiên

Sau mọi chỉnh sửa trong `01-architecture/`, `02-specs/`, `03-planning/`:

1. Cập nhật bảng trạng thái trong [02-specs/README.md](../../../02-specs/README.md) (nếu có thêm/đổi trạng thái module hoặc slice).
2. Cập nhật nhật ký phiên tại [03-planning/agent/PROGRESS.md](../../../03-planning/agent/PROGRESS.md) và [03-planning/GAPS.md](../../../03-planning/GAPS.md) (nếu phát sinh `[OPEN-GAP]`).
3. Chạy đủ 4 lệnh kiểm chứng sau từ thư mục gốc `d:\AI Agent\CRM`:
   ```powershell
   python 05-tools/build_delivery_inventory.py
   python 05-tools/verify_delivery_plan.py
   python 05-tools/verify_hrm_integration.py
   python 05-tools/verify_module_spec.py
   ```
4. Không tuyên bố `implementation-ready` hay `Pass` nếu còn lỗi từ các script trên hoặc còn Blocking GAP chưa chốt.
