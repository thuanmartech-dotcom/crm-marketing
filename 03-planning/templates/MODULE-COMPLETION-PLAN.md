# Mxx — Kế hoạch Hoàn thành Module (`Documentation-Only`)

> Khuôn mẫu phiếu điều phối cho `03-planning/modules/Mxx-COMPLETION-PLAN.md`. Đây là **kế hoạch điều phối thực thi đặc tả**, không thay thế [Master v1.9](../../00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) và không sao chép lặp lại nội dung chi tiết của file đặc tả `02-specs/modules/Mxx-*.md` hay [GAPS.md](../GAPS.md).

---

## 1. Định danh, Trạng thái & Ranh giới

- **Module:** `Mxx` — `<Tên module>`
- **Kế hoạch Wave chủ quản:** `../waves/WAVE-x-PLAN.md`
- **Gói ngữ cảnh Protocol v2:** `<ArtifactDir>/scratch/context-Mxx.md` *(kiểm bằng `--verify-packet` trước khi soạn)*
- **Trạng thái hoàn thành đặc tả:** `Not_Started` | `In_Progress` | `Blocked_By_Decision` | `Blocked_By_Dependency` | `Draft_Complete` | `Reviewed` | `Ready (Scope: ...)`
- **Ranh giới giai đoạn:** **`Documentation-Only`** (`application_write_scope: null`, `application_tests: "Not Run"`). *"Hoàn thành"* nghĩa là hoàn thành đặc tả trong phạm vi đã chốt, **không** cho phép chuyển sang viết mã nguồn ứng dụng.

---

## 2. Phạm vi & Nguồn Truy vết (Con trỏ nguồn)

- **Phạm vi IDs sở hữu (`requirements.json`):** `<N>` owned IDs (`owner == Mxx`) + nhóm ID liên quan `missing_owner`/`PLATFORM` (`GAP-03`).
- **Mục & Dải dòng Master v1.9:** `<Liệt kê mục/line ngắn từ context-Mxx.md>`
- **ADR & Contract đầu vào bắt buộc:** `ADR-001..009`, `C14`, `C16`, `C19`, `C20`, `C23`, `C24` *(chọn đúng danh sách liên quan trong `context-Mxx.md`)*.
- **Ngưỡng áp dụng `INV-26..28`:** `<Ghi rõ áp dụng hoặc không áp dụng cho module này kèm lý do>`.

---

## 3. Đầu ra Cần Hoàn thành

- [ ] **Đặc tả Module:** `02-specs/modules/Mxx-TEN-MODULE.md` (đủ `6` mục chuẩn, `9` cột trace, `6` phần con/chức năng, `ADR-004` tách bảng, `10` cột test matrix `Not Run`).
- [ ] **Public Contract (nếu phát sinh command/event liên module):** `02-specs/contracts/Mxx-TEN-CONTRACT.md`.
- [ ] **Change Proposal (nếu sửa tài liệu đã `Reviewed`/`Ready` hoặc `Backward Contract Drift`):** `02-specs/changes/CR-*.md`.
- [ ] **Đồng bộ Kho & Đăng ký:** [GAPS.md](../GAPS.md) (`7` trường GAP), [02-specs/README.md](../../02-specs/README.md), [active-task.json](../agent/active-task.json), [PROGRESS.md](../agent/PROGRESS.md), [CONTRACTS-REGISTRY.md](../../02-specs/CONTRACTS-REGISTRY.md).

---

## 4. Trình tự Xử lý & Tiến trình Từng Pha

| Bước | Pha | Mục tiêu & Hành động | Trạng thái | Ghi chú / Phiên |
|---|---|---|---|---|
| 1 | Pha 0–1 (`Grounding`) | Đọc lõi + sinh/verify `context-Mxx.md` + đọc Master/Contracts/ADRs liên quan | `Pending` | |
| 2 | Pha 2 (`Clarify`) | Rà checklist + Cụm lens liên quan; hỏi chốt quyết định Tầng 1; ghi GAP Tầng 2 vào `GAPS.md` | `Pending` | |
| 3 | Pha 3 (`Author`) | Soạn/cập nhật `Mxx-*.md`, `Cxx-*.md`, `CR-*` (nếu có) theo chuẩn EARS & `ADR-004/005` | `Pending` | |
| 4 | Pha 4 (`Analyze & Verify`) | Rà soát ngữ nghĩa / Fresh-Context Re-Audit; chạy `--build-registry` + `4` lệnh `05-tools/` | `Pending` | |
| 5 | Kết phiên (`Handoff`) | Cập nhật bảng `02-specs/README.md`, `active-task.json`, `PROGRESS.md` & phiếu kế hoạch này | `Pending` | |

---

## 5. Kỷ luật Chạy Liên tục & Điểm Phải Dừng Chờ (`Blocking Register`)

- **Nguyên tắc xử lý:** Agent **liên tục xử lý** mọi phần việc đã được phép trong phạm vi rõ ràng; **tuyệt đối không tự chốt nghiệp vụ, tự bịa thông số hay bỏ qua phụ thuộc chưa khóa để đóng module cho đủ kế hoạch**.
- **Khi gặp điểm chặn thật:** Dừng đúng nhánh bị chặn, ghi nhận trung thực vào bảng dưới đây và cập nhật trạng thái module sang `Blocked_By_Decision` hoặc `Blocked_By_Dependency` (hoặc giữ phần độc lập ở `Draft` và ghi rõ phần nào còn treo).

| ID Chặn | Vấn đề / Quyết định Còn thiếu | Phân loại (`Decision` / `Dependency`) | Người Trả lời / Nguồn Chốt | Điều kiện Tiếp tục | Trạng thái |
|---|---|---|---|---|---|
| `BLK-Mxx-01` | `<Ví dụ: Ranh giới auto-merge vs Duplicate_Candidate>` | `Decision` | `Chủ dự án` | `Xác nhận phương án Tầng 1 hoặc mở GAP Fail-Closed nếu thuộc cấu hình vận hành` | `Open` |

---

## 6. Điều kiện Hoàn thành & Kiểm chứng Bắt buộc

Module `Mxx` chỉ được đánh dấu hoàn thành đặc tả (`Draft_Complete` hoặc `Reviewed` / `Ready (Scope: ...)` theo ngưỡng Wave Plan) khi đạt đủ:
1. Bao phủ `100%` ID `owner == Mxx` và nhóm `missing_owner` liên quan (`GAP-03`); truy vết khép kín `Nguồn → Mxx-Fyy / Contract → Test (## 6.2)` giữ `Not Run`.
2. Toàn bộ quyết định Tầng 1 (ranh giới, state machine, SSoT, Public Contract) đã chốt với Chủ dự án; mọi tham số mở Tầng 2 đã đăng ký đủ `7` trường vào [GAPS.md](../GAPS.md) ở chế độ `Fail-Closed`.
3. Không còn mục `Open` nào trong `Blocking Register` chặn phạm vi mục tiêu của kế hoạch này; mọi phụ thuộc chéo với module khác đã khóa contract hoặc có `CR-*` hợp lệ.
4. Vượt qua đủ bộ kiểm chứng toàn kho (`--build-registry` + `build_delivery_inventory.py` + `verify_delivery_plan.py` + `verify_hrm_integration.py` + `verify_module_spec.py`) với `application_tests: "Not Run"`.
