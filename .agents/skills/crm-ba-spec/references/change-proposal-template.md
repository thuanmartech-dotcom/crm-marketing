# Change Proposal Template (`OpenSpec` Style for CRM)

Lưu tại `02-specs/changes/CR-YYYYMMDD-<TEN-NGAN>.md` khi đề xuất sửa đổi một đặc tả đã `Reviewed` / `Ready` trong `02-specs/`.

---

## 1. Thông tin đề xuất

- **Mã đề xuất:** `CR-YYYYMMDD-<TEN-NGAN>`
- **Trạng thái:** `Proposed` | `Approved` | `Applied` | `Rejected`
- **Baseline Master tham chiếu:** `v1.9` (`SHA-256: b6a3279f328e96e1e97d845e209be7a326516a0dba5e3a033d88e1f2162e421c`)
- **Phân loại nguồn:** `[MASTER-CLARIFICATION]` (làm rõ câu chữ Master có sẵn) | `[PROPOSED-EXTENSION]` (đề xuất mới ngoài Master)
- **Tài liệu bị ảnh hưởng:**
  - Module: `02-specs/modules/...`
  - Contract: `02-specs/contracts/...`
  - Slice / Planning: `02-specs/slices/...`, `03-planning/GAPS.md`

---

## 2. Lý do thay đổi & Phạm vi (Why & What)

- **Vấn đề phát hiện:** (Mô tả ngắn lỗ hổng, mâu thuẫn hoặc yêu cầu mới).
- **Thay đổi đề xuất:** (Liệt kê theo cú pháp EARS `[PROPOSED]`).
- **Không thuộc phạm vi (Non-goals):** (Nêu rõ những gì giữ nguyên, không sửa Master v1.9).

---

## 3. Phân tích tác động (Impact & Breaking Check)

- **Breaking Contract Change?** `Có` / `Không` (Nếu Có, liệt kê các module Consumer cần cập nhật).
- **Ảnh hưởng `INVARIANTS.md`:** Đối chiếu xem có chạm `INV-*` nào không.
- **Tác động Test Matrix & GAPS:** Liệt kê Test ID hoặc `GAP-*` cần thêm/sửa.

---

## 4. Kế hoạch áp dụng (`Apply` Checklist)

- [ ] Đã chốt các câu hỏi Blocking với chủ dự án.
- [ ] Đã cập nhật file `02-specs/modules/` / `contracts/` / `slices/` liên quan.
- [ ] Đã cập nhật `03-planning/GAPS.md` và `03-planning/agent/PROGRESS.md`.
- [ ] Đã chạy đủ 4 script `05-tools/*.py` và không phát sinh lỗi mới.
- [ ] Đã chuyển file này sang `02-specs/changes/archive/` sau khi áp dụng xong.
