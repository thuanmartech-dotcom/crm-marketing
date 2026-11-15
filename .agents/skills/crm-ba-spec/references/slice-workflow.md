# Playbook Chế độ `slice`: Lập đặc tả Lát cắt Triển khai (`SL00`, `SL02–SL07`)

Dùng khi tổng hợp nhiều module đã bóc tách thành một lát cắt bàn giao thực tế (Vertical Slice), tham chiếu chuẩn mực từ [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md) và [ROADMAP.md](../../../../03-planning/ROADMAP.md).

---

## Pha 1 — Kiểm tra điều kiện tiên quyết

1. Đọc [ROADMAP.md](../../../../03-planning/ROADMAP.md), [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md) và [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md) để nắm cấu trúc chuẩn.
2. Kiểm tra các module thuộc slice (theo bảng tại [02-specs/README.md](../../../../02-specs/README.md)):
   - Nếu module chính chưa có spec trong `02-specs/modules/`, ghi rõ phạm vi slice chỉ đóng băng phần đã có spec hoặc đề xuất tách module trước.
3. Đọc các public contract liên quan trong `02-specs/contracts/` (nếu có).

---

## Pha 2 — Clarification Gate cho Ranh giới Lát cắt

Hỏi ngược qua `ask_question` (tầng 1) nếu phát hiện sự mơ hồ về:
- **In-scope vs Out-of-scope:** Chức năng nào bật ở slice này, chức năng nào hoãn sang slice sau (P1/P2) hoặc bị chặn bởi feature flag/capability?
- **Chiến lược dữ liệu giả / Mock vs Live:** Ví dụ tích hợp `M19` khi chưa có credential thật (mock ở slice này, gate live sang slice sau).
- **Điều kiện thoát (Exit Criteria)** của slice trước khi mở slice kế tiếp.

---

## Pha 3 — Soạn `02-specs/slices/SLxx-TEN-SLICE.md`

Bố cục bám sát chuẩn [SL01-INTERNAL-WORK.md](../../../../02-specs/slices/SL01-INTERNAL-WORK.md):

1. **Manifest & Baseline:** SHA-256 Master v1.9, danh sách module tham gia, phụ thuộc slice trước (`SL00`...), trạng thái (`Draft — chưa có code/test chạy`).
2. **Phạm vi & Feature Flag Closure:** Bảng rõ từng ID (`FR/BR/UC/Mxx-Fxx`) thuộc `In-Scope`, `Deferred`, hoặc `Gated (Feature Flag OFF)`.
3. **Luồng End-to-End xuyên module:** Sơ đồ Mermaid `sequenceDiagram` hoặc `flowchart LR` thể hiện rõ ranh giới command/event/outbox qua `M14` (quyền), `M19` (outbox/inbox), `M20` (consent/retention).
4. **Hợp đồng & Thay đổi dữ liệu tối thiểu trong slice:** Chỉ liệt kê phần bảng/API thực sự cần cho lát cắt này (tránh phình scope).
5. **Test Applicability Matrix:** Phân loại toàn bộ test ID liên quan thành `Applicable in SLxx` vs `Deferred / N/A (kèm lý do rõ ràng)`; cột `Status/Evidence` luôn là `Not Run`.
6. **Danh sách Gate & Blocking Gaps:** Liệt kê `GAP-*` chặn implementation của slice này.

---

## Pha 4 — Verify & Đồng bộ

1. Cập nhật link & trạng thái dòng `SLxx` trong [02-specs/README.md](../../../../02-specs/README.md).
2. Cập nhật [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md).
3. Chạy 4 script trong `05-tools/` (xem `SKILL.md`).
