# Chuẩn Viết EARS, Nhãn Nguồn & Checklist Khai thác BA

Tài liệu tra cứu nhanh khi soạn thảo `02-specs/modules/Mxx-*.md` và `02-specs/contracts/*.md`.

---

## 1. Năm mẫu câu EARS bắt buộc cho Hành vi & Rule

Mỗi quy tắc nghiệp vụ/hành vi quan trọng phải viết rõ ràng theo mẫu EARS (hạn chế câu thụ động hoặc từ ngữ mơ hồ như *"hợp lý"*, *"tự động xử lý"*, *"nếu cần"*):

| Loại yêu cầu | Mẫu câu chuẩn (Việt / Anh kết hợp thuật ngữ) | Ví dụ áp dụng cho CRM |
|---|---|---|
| **Ubiquitous** (Luôn đúng) | `Hệ thống / <Module> phải luôn <hành vi>.` | `[MASTER] M14 phải luôn kiểm tra tenant_id + workspace_id + resource_grant trước khi trả về dữ liệu nghiệp vụ.` |
| **Event-Driven** (Theo sự kiện) | `Khi <trigger/command/event>, <Module> phải <hành vi>.` | `[MASTER] Khi nhận lệnh SubmitTaskResult, M16 phải tạo bản ghi Task_Submission bất biến gắn version mới.` |
| **State-Driven** (Theo trạng thái) | `Trong khi <trạng thái/điều kiện duy trì>, <Module> phải <hành vi>.` | `[PROPOSED] Trong khi hợp đồng ở trạng thái SUSPENDED, M08 phải chặn tạo mới Service_Period nhưng vẫn cho phép xem lịch sử đối soát.` |
| **Unwanted / Error** (Ngoại lệ / Lỗi) | `Nếu <điều kiện lỗi/xung đột/thiếu quyền>, <Module> phải <hành vi từ chối/bù trừ>.` | `[MASTER] Nếu expected_version gửi lên khác phiên bản hiện tại, M16 phải từ chối cập nhật với mã lỗi CONFLICT_VERSION và không ghi đè dữ liệu.` |
| **Optional / Capability** (Theo gói/flag) | `Khi <capability/feature_flag> được bật, nếu <điều kiện>, <Module> phải <hành vi>.` | `[MASTER] Khi capability API_READ được bật và grant đối tác còn hiệu lực, M21 phải đọc đơn qua adapter read-only của M19.` |

---

## 2. Quy tắc Gắn nhãn Nguồn (Chống AI bịa rule)

Mọi đoạn đặc tả trong `Hành vi`, `Data/API`, `UI/operations` phải mang 1 trong 3 nhãn ở đầu mục hoặc đầu dòng:

- **`[MASTER]`** — Truy vết trực tiếp về `CRM_MASTER_BRD_SRS_HOP_NHAT.md` (nên ghi kèm mã `FRxx/BRxx/UCxx` hoặc mục `3.x/5.x`).
- **`[PROPOSED]`** — Thiết kế chi tiết do BA/AI đề xuất để cụ thể hóa Master (ví dụ: tên command chuẩn, error code, UI state, CAS lock). Chờ Tech Lead/PO review. **Sau khi được duyệt, vẫn giữ nguyên nhãn `[PROPOSED]` kèm `decision_ref` (tuyệt đối không đổi thành `[MASTER]`).**
- **`[OPEN-GAP: GAP-...]`** — Điểm chưa có đủ dữ kiện quyết định. Không được tự điền con số kinh doanh giả định làm rule cứng; phải đăng ký đủ 7 trường phân loại vào `03-planning/GAPS.md`.

---

## 3. Checklist Khai thác Edge Case (BMAD Analyst Gate)

Trước khi chốt bản draft của bất kỳ module (`M01–M24`) hoặc slice (`SL00–SL11`) nào, Agent phải rà soát từng hạng mục dưới đây xem đã trả lời hoặc ghi `[OPEN-GAP]` chưa:

1. **Ranh giới sở hữu & Kế thừa bảng (`ADR-004`):** Module này là *nguồn ghi duy nhất (SoT)* của entity nào? Entity nào chỉ giữ tham chiếu ID/projection từ module khác? Mỗi bảng trong `4.2` đã phân loại đúng `Nhóm A` (12 cột) / `Nhóm B-Catalog` / `Nhóm B-Governance-Sensitive` / `Nhóm C Append-Only` (tuyệt đối cấm `updated_at/updated_by/row_version/archived_at`) chưa?
2. **Vòng đời & State Machine:** Trạng thái khởi tạo là gì? Chuyển trạng thái nào bị cấm? Có trạng thái kết thúc bất biến không? Hủy/mở lại (reopen) xử lý ra sao?
3. **Đồng thời & Bất biến (Concurrency & Idempotency):** Nếu 2 người/2 job cùng thao tác 1 bản ghi thì ai thắng (`expected_version` / lock)? Nếu webhook/retry gửi trùng `idempotency_key` cùng body vs khác body thì trả về gì?
4. **Quyền & Phạm vi (`M14` / `M20` / `M23`):** Phân tách quyền cấp Tenant vs Workspace vs Entity grant (`6` GUC theo `ADR-002`)? Có PII nào cần che (`Redact-Before-Insert`), có ràng buộc consent/suppression/`active_legal_hold_ids[]` (`M20`) hoặc Maker–Checker (`M23`) không?
5. **Tích hợp ngoài & Side Effects (`ADR-005` Dual Outbox):** Tác động liên module nội bộ (tạo task chéo, cập nhật projection, thông báo nội bộ) đã đi qua **`M23-F12.Internal_Outbox_Events`** (`Lane 2`) sau commit chưa? Giao tiếp hệ thống bên ngoài (gửi tin nhắn, webhook, API đối tác, PMS) đã đi qua **`M19`** chưa? Khi downstream lỗi/timeout thì xử lý `UNKNOWN_OUTCOME` hay đẩy DLQ đúng tuyến (`M23-F12` vs `M19`) ra sao?
6. **4 Trạng thái UI & Khối lượng lớn:** Đã mô tả đủ màn hình khi `Empty` (chưa có dữ liệu / chưa cấu hình policy), `Loading`, `Error`, `Permission Denied` (non-disclosure)? Thao tác hàng loạt có dry-run/giới hạn (`M24-F03`) không?
7. **Truy vết khép kín & Kiểm thử trung thực:** Đã nối khép kín `ID nguồn → Chức năng (Mxx-Fyy) → Quy tắc EARS/State → Contract → Ca kiểm thử` (mỗi ca kiểm thử đủ Tiền điều kiện, Hành động, Kết quả quan sát được) và giữ nguyên trạng thái `Not Run` chưa?
8. **Lease Fencing & Bảng Reaper Thống nhất (`INV-26`):** Nếu module có worker/scheduler nhả DB lock giữa các pha xử lý, đã có `lease_token` fencing CAS ở **cả micro-commit lẫn pha ghi kết quả cuối** và dùng chung 1 bảng chân trị Reaper cho mọi tổ hợp biên (`http_attempted_at × TTL × retry`) giữa ADR, Module và Contract chưa?
9. **Xóa PII Đa chủ thể & Tách đôi Hash (`INV-27`):** Nếu module có bảng nội dung bất biến cho phép ẩn danh PII (`Messages`, `Notes`, `Submissions`, `AI_Drafts`...), đã dùng `redacted_deletion_ledger_ids uuid[]` (cấm khóa 1 lần `IS NULL`), truy tìm đủ chủ thể đa nguồn (links + HMAC + nội dung) và tách riêng `content_sha256` gốc với `redacted_content_sha256` chưa?
10. **Tách Ca Kiểm thử & Đồng bộ Manifest (`INV-28`):** Đã tách riêng ca test thành công (`200 OK`) khỏi ca xung đột/stale (`409`) và cập nhật đồng bộ `active-task.json`, `DECOMPOSITION-PLAN.md`, `02-specs/README.md`, `PROGRESS.md` (Section `## 0` đầu file) chưa?
