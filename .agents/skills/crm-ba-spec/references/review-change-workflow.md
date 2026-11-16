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
3. *(Khuyến nghị từ ECC & Giao thức Tiết kiệm Token)* Kiểm tra `session_token_telemetry`: nếu phiên đang `GREEN (<170k)`, dùng 1 subagent `research` **context sạch (read-only)** đọc độc lập các file spec vừa viết + [CONTRACTS-REGISTRY.md](../../../../02-specs/CONTRACTS-REGISTRY.md) + `contracts/*.md` liên quan + [INVARIANTS.md](../../../../01-architecture/INVARIANTS.md).
   - **Bắt buộc File-Backed Output:** Subagent ghi toàn bộ báo cáo chi tiết (`[File:Line]`, trích dẫn sửa đề xuất) vào `<ArtifactDir>/scratch/reaudit-<pham-vi>.md` (**ngoài kho `d:\AI Agent\CRM`**), và chỉ gửi về Coordinator qua `send_message` bản tóm tắt **`< 1.500` ký tự** (Verdict + counts `CRITICAL/HIGH/MEDIUM/INFO` + top blockers + đường dẫn file).
   - Nếu phiên đang `YELLOW (170k–210k)` hoặc `RED (>210k)`, không phóng subagent chạy lâu trong phiên đó; bàn giao sang phiên mới sạch để chạy Re-Audit.
4. Đọc đối chiếu thủ công **8 điểm nóng** (5 lõi + 3 bẫy phân tán/trạng thái từ bài học Wave 1):
   - **Data Ownership & `ADR-004` / `ADR-005` Conflict:** Hai module có cùng tự nhận là nguồn ghi cho 1 entity không? Bảng `Nhóm C Append-Only` có lỡ gắn `updated_at/updated_by/row_version/archived_at` trái `ADR-004` không? Có nhầm lẫn giữa `M19` (tích hợp ngoài) với `M23-F12` (Outbox nội bộ) trái `ADR-005` không?
   - **Contract Mismatch & Traceability:** Producer công bố event/schema A nhưng Consumer ở module khác kỳ vọng field B? Chuỗi `Nguồn → Chức năng (Mxx-Fyy) → Rule/State → Contract → Ca kiểm thử` có đứt gãy hoặc thiếu nhánh từ chối/kết quả quan sát được không?
   - **Invariant Violation:** Có luồng nào vi phạm `INVARIANTS.md` (ví dụ: `Done` tự kích `Paid`, ghi thẳng sang `M22` payroll, bypass `M14`/`M20`, `PATCH status` tự do không qua command)?
   - **Silent Assumptions & Approval Drift:** Có rule `[PROPOSED]` nào chưa được chủ dự án duyệt nhưng lại viết như `[MASTER]`, hoặc `[PROPOSED]` đã duyệt nhưng bị sửa nhãn thành `[MASTER]` không? Tài liệu `Reviewed`/`Ready` có đủ `Approved_Scope`/`Approved_By`/`Decision_Ref` không?
   - **GAP Drift & Safe Default Abuse:** Có `[OPEN-GAP]` mới nhắc trong spec nhưng chưa đăng ký đủ 7 trường vào [GAPS.md](../../../../03-planning/GAPS.md) không? Có tự chọn số liệu kinh doanh làm `Safe Default` không?
   - **Lease & Fencing CAS (`W1-02`):** Mọi worker/job nhả DB lock giữa các pha (gọi HTTP/AI/Gateway) có `lease_token` fencing kiểm CAS tại **cả bước micro-commit lẫn bước ghi kết quả cuối** và có cơ chế chống late-response ghi đè không?
   - **Single Reaper / State Decision Table (`W1-03`):** Nếu một máy trạng thái xuất hiện đồng thời ở ADR, Module Spec và Contract, mọi tổ hợp biên (timeout × TTL × retry × error) có dùng chung **1 bảng chân trị duy nhất** không?
   - **Multi-Subject Idempotency & Test Semantics (`W1-01`, `W1-04`, `W1-05`):** Cơ chế xóa/ẩn danh/redact có hỗ trợ **nhiều chủ thể nối tiếp trên cùng 1 bản ghi** (`deletion_ledger_id` thay vì cờ 1 lần `IS NULL`), bảng kiểm thử có tách bạch ca hợp lệ vs ca xung đột, và trạng thái trong `active-task.json` có khớp `DECOMPOSITION-PLAN.md` & `02-specs/README.md` không?
5. Đọc theo đoạn bằng công cụ đọc theo khoảng dòng hiện có (như `read_file` với `StartLine`/`EndLine`) từ file báo cáo ở `scratch/` và hỏi người dùng chốt hướng xử lý với các mục `CRITICAL / HIGH` trước khi sửa (qua CR nếu spec đã `Reviewed`/`Ready`).

---

## Luồng C — Xuất Phiếu hỏi Stakeholder (`/to-questionnaire` style)

Dùng khi trong [GAPS.md](../../../../03-planning/GAPS.md) hoặc trong các file `Mxx-*.md` / `SLxx-*.md` tích tụ nhiều `[OPEN-GAP]` cần **người thật ở các phòng ban khác nhau** chốt (Finance, Legal/Privacy, Ops, Đối tác Pancake, Tech Lead):

1. Quét toàn bộ `[OPEN-GAP]` theo phạm vi người dùng yêu cầu (1 module, 1 sóng, hoặc toàn bộ `GAPS.md`).
2. Gom nhóm câu hỏi theo **Owner vai trò / Người quyết định** (mỗi vai trò 1 mục riêng, viết bằng ngôn ngữ nghiệp vụ dễ hiểu — tránh thuật ngữ code nặng).
3. Với mỗi câu hỏi, trình bày đủ thông tin: `Mã GAP` | `Câu hỏi cần chốt` | `Hành vi khi thiếu cấu hình / Gợi ý` | `Chặn thiết kế / triển khai / kích hoạt phạm vi nào` | `Điều kiện đóng`.
4. **Cổng Kiểm tra Trạng thái Trước khi Áp dụng Câu trả lời Stakeholder (KHÓA ĐƯỜNG BỎ QUA CR):**
   - Kiểm tra `Status` trong `## 1. Manifest` của **từng tệp tài liệu chịu ảnh hưởng** (`modules/*.md`, `contracts/*.md`, `slices/*.md`):
     - **Nếu tài liệu đang ở `Draft`:** Cập nhật trực tiếp vào tài liệu `Draft` đó và cập nhật trạng thái/quyết định tại `GAPS.md`.
     - **Nếu tài liệu đã `Reviewed` hoặc `Ready`:** **Cấm sửa thẳng!** Câu trả lời của Stakeholder trở thành đầu vào cho **Luồng B (`Change Proposal: CR-*`)**. Nếu người dùng/Stakeholder đã xác nhận đúng phạm vi câu trả lời đó khi gửi về, **ghi nhận luôn phê duyệt & người quyết định vào `CR-*` (kèm `decision_ref`, không hỏi xác nhận lại máy móc)**; chỉ hỏi bổ sung nếu câu trả lời phát sinh Breaking Change hoặc mâu thuẫn chưa rõ phạm vi. Áp dụng delta vào các tài liệu đích (giữ nguyên nhãn `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`).
   - **Chỉ được đóng GAP trong `GAPS.md` SAU KHI** toàn bộ tài liệu chịu ảnh hưởng đã được cập nhật đồng bộ và vượt qua cổng kiểm chứng toàn kho ở **Mục 4 của [SKILL.md](../SKILL.md)**.

---

## Luồng B — Đề xuất Thay đổi Spec (`OpenSpec: propose → apply → archive`)

Dùng bắt buộc cho **mọi sửa đổi** trên spec đã được review/chốt (`M14/16/19/20/23/24`, `M21`, `M22`, `SL01`, `SL08`, `SL09–11`, `C14..C24`, hoặc bất kỳ `Mxx`/`SLxx`/`Cxx` nào đã rời trạng thái `Draft` — **bao gồm cả đóng GAP từ Luồng C và `Backward Contract Drift`**) mà **không làm mất dấu vết lý do thay đổi**:

### Bước 1: `Propose`
- Tạo tệp `02-specs/changes/CR-YYYYMMDD-<TEN-NGAN>.md` theo mẫu [change-proposal-template.md](change-proposal-template.md).
- Nêu rõ:
  - Động lực & nguồn yêu cầu thay đổi (phân biệt `[MASTER]` vs `[PROPOSED]`; giữ `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`).
  - Danh sách tệp bị ảnh hưởng (`Mxx`, `SLxx`, `contracts/*.md`, `GAPS.md`, `FUNCTION-CATALOG.md`).
  - Phân tích tác động ngược (Breaking change? Ảnh hưởng consumer nào? Cần cập nhật test matrix nào?).
- Nếu có Breaking change hoặc đổi ranh giới module mà người dùng chưa phê duyệt tường minh đúng phạm vi đó: **bắt buộc hỏi xác nhận** qua công cụ hỏi tương tác hiện có (như `ask_question`) hoặc hỏi trực tiếp bằng văn bản trước khi sang Bước 2. Nếu người dùng đã phê duyệt tường minh đúng phạm vi thay đổi, ghi nhận thẳng phê duyệt đó vào CR (`Approved`) và chuyển sang Bước 2 không hỏi lại máy móc.

### Bước 2: `Apply`
- Sau khi `CR-*` ở trạng thái `Approved`:
  1. Cập nhật đúng phần delta vào các file đích trong `02-specs/modules/`, `02-specs/contracts/`, `02-specs/slices/`, `03-planning/GAPS.md`. *(Với `Backward Contract Drift` giữa Wave 2–5 chỉ mở rộng additive vào Contract Wave trước: áp dụng delta lên `contracts/*.md` trong khuôn khổ CR này, chạy `--build-registry` và ghi `[PENDING-BACKSYNC]` vào `PROGRESS.md` để gom đồng bộ vào `modules/*.md` cuối Wave nhằm tránh phình token; giữ CR mở cho tới khi backsync xong.)*
  2. Gắn tham chiếu `CR-YYYYMMDD-*` (`Decision_Ref`) tại mục `Manifest` / lịch sử thay đổi của file vừa sửa; chỉ đóng GAP khi mọi file chịu ảnh hưởng đã cập nhật xong.
  3. Cập nhật trạng thái trong Change Proposal sang `Applied`.

### Bước 3: `Archive`
- Chuyển/lưu bản Change Proposal đã `Applied` vào `02-specs/changes/archive/CR-YYYYMMDD-<TEN-NGAN>.md` (vẫn giữ link tham chiếu được kiểm tra bởi `verify_delivery_plan.py`) và ghi nhận vào [PROGRESS.md](../../../../03-planning/agent/PROGRESS.md).
- Chạy đủ cổng kiểm chứng toàn kho theo **Mục 4 của [SKILL.md](../SKILL.md)** (`--build-registry` + 4 lệnh toàn kho, không thay bằng `--file`).
