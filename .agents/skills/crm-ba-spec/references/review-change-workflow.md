# Playbook Chế độ `review-change`: Rà soát Chéo (`/analyze`) & Đề xuất Thay đổi (`OpenSpec`)

Kết hợp 2 tinh hoa:
- **Spec-Kit `/speckit.analyze`:** Đọc chéo nhiều module/contract để tìm lỗ hổng, trùng lặp sở hữu dữ liệu, mâu thuẫn `INVARIANTS.md` hoặc ID mồ côi.
- **OpenSpec (`propose → apply → archive`):** Cô lập mọi sửa đổi trên spec đã `Reviewed`/`Ready` thành một Change Proposal trước khi ghi đè vào tài liệu chính.

---

## Luồng A — Rà soát Chéo (`Analyze Audit`)

1. Xác định phạm vi rà soát (ví dụ: cặp module giao thoa `M02–M07–M08`, cụm tài chính `M09–M10–M17`, hoặc toàn bộ `02-specs/modules/`).
2. Chạy script kiểm chứng tự động trước để lấy danh sách lỗi máy móc & độ phủ ID:
   ```powershell
   python 05-tools/verify_module_spec.py
   ```
3. Đọc đối chiếu thủ công 5 điểm nóng:
   - **Data Ownership Conflict:** Hai module có cùng tự nhận là nguồn ghi cho 1 entity không?
   - **Contract Mismatch:** Producer công bố event/schema A nhưng Consumer ở module khác kỳ vọng field B?
   - **Invariant Violation:** Có luồng nào vi phạm `INVARIANTS.md` (ví dụ: `Done` tự kích `Paid`, ghi thẳng sang `M22` payroll, bypass `M14`/`M20`, `PATCH status` tự do không qua command)?
   - **Silent Assumptions:** Có rule `[PROPOSED]` nào chưa được chủ dự án duyệt nhưng lại viết như `[MASTER]` không?
   - **GAP Drift:** Có GAP mới nhắc trong spec nhưng chưa đăng ký vào [GAPS.md](../../../../03-planning/GAPS.md)?
4. Xuất báo cáo kiểm tra gồm các nhóm `CRITICAL / HIGH / MEDIUM / INFO` và hỏi người dùng chốt hướng xử lý trước khi sửa.

---

## Luồng B — Đề xuất Thay đổi Spec (`OpenSpec: propose → apply → archive`)

Dùng khi cần sửa một spec đã được review/chốt (`M21`, `M22`, `SL01`, hoặc bất kỳ `Mxx` nào đã rời trạng thái `Draft` ban đầu) mà **không làm mất dấu vết lý do thay đổi**:

### Bước 1: `Propose`
- Tạo tệp `02-specs/changes/CR-YYYYMMDD-<TEN-NGAN>.md` theo mẫu [change-proposal-template.md](change-proposal-template.md).
- Nêu rõ:
  - Động lực & nguồn yêu cầu thay đổi (phân biệt `[MASTER]` vs `[PROPOSED]`).
  - Danh sách tệp bị ảnh hưởng (`Mxx`, `SLxx`, `contracts/*.md`, `GAPS.md`, `FUNCTION-CATALOG.md`).
  - Phân tích tác động ngược (Breaking change? Ảnh hưởng consumer nào? Cần cập nhật test matrix nào?).
- Nếu có Breaking change hoặc đổi ranh giới module: **bắt buộc hỏi xác nhận qua `ask_question`** trước khi sang Bước 2.

### Bước 2: `Apply`
- Sau khi chủ dự án duyệt `CR-*`:
  1. Cập nhật đúng phần delta vào các file đích trong `02-specs/modules/`, `02-specs/contracts/`, `02-specs/slices/`, `03-planning/GAPS.md`.
  2. Gắn tham chiếu `CR-YYYYMMDD-*` tại mục `Manifest` / lịch sử thay đổi của file vừa sửa.
  3. Cập nhật trạng thái trong Change Proposal sang `Applied`.

### Bước 3: `Archive`
- Chuyển/lưu bản Change Proposal đã `Applied` vào `02-specs/changes/archive/CR-YYYYMMDD-<TEN-NGAN>.md` (vẫn giữ link tham chiếu được kiểm tra bởi `verify_delivery_plan.py`) và ghi nhận vào [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md).
- Chạy đủ 4 script kiểm chứng ở `05-tools/`.
