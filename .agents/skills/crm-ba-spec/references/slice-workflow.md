# Playbook Chế độ `slice`: Lập & Bảo trì Đặc tả Lát cắt Triển khai (`SL00–SL11`)

Dùng khi tổng hợp nhiều module đã bóc tách thành một lát cắt bàn giao thực tế (`SL00`, `SL02–SL07`), hoặc khi cập nhật/đối soát các slice đã tồn tại (`SL01`, `SL08`, `SL09–11` qua Change Proposal). Tham chiếu chuẩn mực từ [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md), [ROADMAP.md](../../../../03-planning/ROADMAP.md) và [ADR-002..009](../../../../01-architecture/INDEX.md).

---

## Pha 1 — Kiểm tra điều kiện tiên quyết & Cổng Ngữ cảnh Protocol v2

1. Tuân thủ [AGENTS.md](../../../../AGENTS.md) Mục 4 (`Protocol v2`): đọc [active-task.json](../../../../03-planning/agent/active-task.json), phần Sticky đầu [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md), [ROADMAP.md](../../../../03-planning/ROADMAP.md), [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md), [INDEX.md](../../../../01-architecture/INDEX.md), [CONTRACTS-REGISTRY.md](../../../../02-specs/CONTRACTS-REGISTRY.md) và [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md).
2. Chạy `python 05-tools/build_module_context.py --module <Mxx> --out "<ArtifactDir>/scratch/context-<Mxx>.md" --check-tokens`, đọc gói và chạy `--verify-packet` cho **từng module thuộc phạm vi slice** trước khi soạn/cập nhật đặc tả slice (Python trích xuất không gọi LLM nhưng đọc gói vẫn tốn token; telemetry mặc định `UNKNOWN` nếu không gắn `--transcript` của đúng phiên hiện tại).
3. Kiểm tra các module thuộc slice (theo bảng tại [02-specs/README.md](../../../../02-specs/README.md)):
   - Nếu module chính chưa có spec trong `02-specs/modules/`, ghi rõ phạm vi slice chỉ đóng băng phần đã có spec hoặc đề xuất tách module trước.
4. Đọc đầy đủ các public contract liên quan trong `02-specs/contracts/` (kể cả `C14`, `C16`, `C19`, `C20`, `C23`, `C24` — các ô `...` trong registry phải đọc tiếp file nguồn) và các ADR tương ứng trong `01-architecture/decisions/`.

---

## Pha 2 — Clarification Gate cho Ranh giới Lát cắt

Thực hiện hỏi chặn (qua công cụ hỏi tương tác hiện có như `ask_question`, hoặc hỏi trực tiếp bằng văn bản nếu môi trường không hỗ trợ tool tương tác) nếu phát hiện sự mơ hồ về:
- **In-scope vs Out-of-scope:** Chức năng nào bật ở slice này, chức năng nào hoãn sang slice sau (`P1/P2`) hoặc bị chặn bởi feature flag/capability?
- **Chiến lược dữ liệu giả / Mock vs Live:** Ví dụ tích hợp `M19` kênh ngoài khi chưa có credential thật (mock ở slice này, gate live sang slice sau) vs sự kiện nội bộ chạy qua `M23-F12`.
- **Điều kiện thoát (Exit Criteria)** của slice trước khi mở slice kế tiếp.

---

## Pha 3 — Soạn hoặc Cập nhật `02-specs/slices/SLxx-TEN-SLICE.md`

*(Nếu `SLxx` đang ở trạng thái `Reviewed`/`Ready`, mọi sửa đổi bắt buộc đi qua Change Proposal tại `02-specs/changes/` theo `review-change-workflow.md`.)* Bố cục bám sát chuẩn [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md):

1. **Manifest & Baseline:** Ghi rõ `v1.9` + chuỗi `SHA-256` chuẩn từ `active-task.json`, danh sách module tham gia, phụ thuộc slice trước (`SL00`...), trạng thái (`Draft` / `Reviewed` / `Ready (Scope: ...)`, kèm `Approved_Scope`, `Approved_By`, `Decision_Ref`, `Approved_At` khi rời `Draft` — luôn giữ tinh thần `Documentation-Only`, chưa có code/test chạy).
2. **Phạm vi & Feature Flag Closure:** Bảng rõ từng ID (`FR/BR/UC/Mxx-Fxx`) thuộc `In-Scope`, `Deferred`, hoặc `Gated (Feature Flag OFF)`.
3. **Luồng End-to-End xuyên module:** Sơ đồ Mermaid `sequenceDiagram` hoặc `flowchart LR` dẫn chiếu đúng ranh giới kiến trúc hiện hành theo [ADR-002..009](../../../../01-architecture/INDEX.md): `M14` (quyền & 6 GUC `BindDbTransactionContext`), **`M23-F12` (Outbox/DLQ sự kiện nội bộ dùng chung `Lane 2` theo `ADR-005`)**, **`M19` (chỉ tích hợp & Outbox/Inbox kênh ngoài theo `ADR-005`)**, `M20` (consent/privacy/retention/erasure), và `M24` (notification/permission cache/3-lane queue isolation).
4. **Hợp đồng & Thay đổi dữ liệu tối thiểu trong slice:** Chỉ liệt kê phần bảng/API thực sự cần cho lát cắt này (tránh phình scope) và giữ phân loại bảng theo `ADR-004`.
5. **Test Applicability Matrix:** Bảng chuẩn phân loại toàn bộ test ID liên quan thành `Applicable in SLxx` vs `Deferred / N/A (kèm lý do rõ ràng)`; có đủ Tiền điều kiện, Hành động, Kết quả quan sát được; cột `Status/Evidence` luôn là `Not Run`.
6. **Danh sách Gate & Blocking Gaps:** Liệt kê mọi `[OPEN-GAP: GAP-...]` chặn triển khai/kích hoạt của slice này và đồng bộ 7 trường phân loại vào [03-planning/GAPS.md](../../../../03-planning/GAPS.md).

---

## Pha 4 — Verify & Đồng bộ

1. Cập nhật link & trạng thái dòng `SLxx` trong [02-specs/README.md](../../../../02-specs/README.md).
2. Cập nhật [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md) (và `GAPS.md` nếu có GAP mới/đóng GAP).
3. Chạy đủ bộ kiểm chứng toàn kho theo **Mục 4 của [SKILL.md](../SKILL.md)** (`--build-registry` nếu có đổi contract/module/ADR + 4 script toàn kho, không thay bằng `--file`).
