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
- **`[PROPOSED]`** — Thiết kế chi tiết do BA/AI đề xuất để cụ thể hóa Master (ví dụ: tên command chuẩn, error code, UI state, CAS lock). Chờ Tech Lead/PO review.
- **`[OPEN-GAP: GAP-Mxx-NN]`** — Điểm chưa có đủ dữ kiện quyết định. Không được tự điền con số giả định làm rule cứng.

---

## 3. Checklist Khai thác Edge Case (BMAD Analyst Gate)

Trước khi chốt bản draft của bất kỳ module `M01–M20` nào, Agent phải rà soát từng hạng mục dưới đây xem đã trả lời hoặc ghi `[OPEN-GAP]` chưa:

1. **Ranh giới sở hữu (Domain Ownership):** Module này là *nguồn ghi duy nhất (SoT)* của entity nào? Entity nào chỉ giữ tham chiếu ID/projection từ module khác?
2. **Vòng đời & State Machine:** Trạng thái khởi tạo là gì? Chuyển trạng thái nào bị cấm? Có trạng thái kết thúc bất biến không? Hủy/mở lại (reopen) xử lý ra sao?
3. **Đồng thời & Bất biến (Concurrency & Idempotency):** Nếu 2 người/2 job cùng thao tác 1 bản ghi thì ai thắng (`expected_version` / lock)? Nếu webhook/retry gửi trùng `idempotency_key` cùng body vs khác body thì trả về gì?
4. **Quyền & Phạm vi (M14 / M20):** Phân tách quyền cấp Tenant vs Workspace vs Entity grant? Có PII nào cần che (mask/redact), có ràng buộc consent/suppression (`M20`) hoặc Maker–Checker (`M23`) không?
5. **Tích hợp ngoài & Side Effects (M19):** Tác động ngoài DB (gửi tin, tạo task chéo, bắn webhook) có đi qua Outbox sau commit transaction không? Khi downstream lỗi/timeout thì retry hay đẩy DLQ/quarantine?
6. **4 Trạng thái UI & Khối lượng lớn:** Đã mô tả đủ màn hình khi `Empty` (chưa có dữ liệu / chưa cấu hình policy), `Loading`, `Error`, `Permission Denied` (non-disclosure)? Thao tác hàng loạt có dry-run/giới hạn không?
7. **Khả năng kiểm thử trung thực:** Mọi mục kiểm thử đều gắn với tiêu chí đạt cụ thể và giữ nguyên trạng thái `Not Run`.
