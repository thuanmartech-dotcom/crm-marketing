# Hướng dẫn Sử dụng Chi tiết Skill `crm-ba-spec`

Tài liệu này hướng dẫn cách gọi và phối hợp với Agent khi dùng skill `crm-ba-spec` để bóc tách đặc tả `M01–M20`, lập slice `SL00–SL07`, rà soát chéo và quản lý thay đổi spec.

---

## 1. Các câu lệnh (Prompt) mẫu để gọi nhanh

Skill được Antigravity tự động phát hiện qua `.agents/skills/crm-ba-spec/SKILL.md`. Bạn chỉ cần nhắn theo ngữ cảnh hoặc gọi thẳng tên skill:

### A. Tách mới / Hoàn thiện một Module (`M01–M20`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec tách đặc tả module M01 (Hồ sơ khách hàng, doanh nghiệp, định danh và hợp nhất).`
- **Muốn Agent hỏi kỹ từng quyết định kiến trúc/edge-case trước khi viết:**
  > `Dùng skill crm-ba-spec tách module M02. Áp dụng /grill-me ở Pha 2 để hỏi tôi chốt hết state machine và ranh giới với M01, M07 trước khi tạo file.`
- **Muốn tách riêng phần Contract liên module của module đã có:**
  > `Dùng skill crm-ba-spec rà và tách các public cross-module contracts của M16 ra 02-specs/contracts/.`

### B. Lập đặc tả Lát cắt Triển khai (`SL00`, `SL02–SL07`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec chế độ slice lập đặc tả cho SL02 (Omnichannel Intake & Inbox tối thiểu).`
- **Lưu ý điều kiện:** Các module chính nằm trong slice (ví dụ `M01`, `M03`, `M19` cho `SL02`) nên được tách module spec trước để tránh slice phải tự định nghĩa lại domain model.

### C. Rà soát chéo chống lệch spec (`Analyze`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng A - Analyze) rà soát chéo cụm M01, M02, M03 và đối chiếu INVARIANTS.md.`

### D. Sửa đổi spec đã `Reviewed` / `Ready` (`OpenSpec Change Proposal`)
- **Bước đề xuất (`propose`):**
  > `Dùng skill crm-ba-spec chế độ review-change tạo Change Proposal sửa quy tắc đối soát trong M21 / SL08.`
- **Bước áp dụng (`apply` & `archive`):**
  > `Tôi đồng ý CR-20261115-xxx, hãy apply vào spec đích, cập nhật GAPS/PROGRESS, archive CR và chạy kiểm chứng.`

### E. Chạy song song theo Sóng phụ thuộc (`Coordinator + Subagents`)
- **Cú pháp chuẩn (ví dụ Sóng 1 nền tảng):**
  > `Dùng skill crm-ba-spec chạy song song Pha 1 & Pha 2 cho Sóng 1 (M14, M19, M20, M01), gom câu hỏi Blocking gửi tôi chốt trước khi viết file.`
- **Cú pháp chờ theo phụ thuộc:**
  > `Tách song song M14, M19, M20, M01; M03 và M02 giữ chờ tới khi có Public Contract của M01 và M19 mới chạy tiếp.`

### F. Xuất Phiếu hỏi Stakeholder (`/to-questionnaire`)
- **Cú pháp chuẩn:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng C) gom các [OPEN-GAP] của M09, M10, M17 thành phiếu câu hỏi cho phòng Tài chính/Kế toán duyệt.`

### G. Rà soát độc lập & Đóng gói bàn giao phiên (`Fresh-Context Review` + `Handoff`)
- **Rà soát bằng subagent context sạch:**
  > `Dùng skill crm-ba-spec chế độ review-change (Luồng A) chạy subagent context sạch đối chiếu M01-CUSTOMER-IDENTITY-MERGE.md với INVARIANTS.md.`
- **Bàn giao cuối phiên dài:**
  > `Tổng hợp handoff cuối phiên vào PROGRESS.md (đã khóa gì, contract nào mới, GAP nào đang chờ, lệnh chạy phiên tiếp theo).`

---

## 2. Điều gì diễn ra trong 1 phiên bóc tách Module chuẩn?

Khi bạn gọi Agent tách một module (ví dụ `M01`), Agent sẽ chạy đúng **4 pha**:

1. **Pha 1 — Thu thập ngữ cảnh (bạn không cần làm gì):**
   - Agent tự đọc `INVARIANTS.md`, `INDEX.md`, `modules.json`, `requirements.json`, `FUNCTION-CATALOG.md` và các dòng tương ứng trong `CRM_MASTER_BRD_SRS_HOP_NHAT.md` (`v1.9`).
2. **Pha 2 — Cổng hỏi ngược 2 tầng (bạn tương tác qua `ask_question`):**
   - Agent **không tự bịa** các quyết định ranh giới hay rule thiếu.
   - Với **Tầng 1 (Blocking)** — Agent bật hộp chọn `ask_question` hỏi từng câu kèm phương án `(Recommended)`, ví dụ:
     - *Ranh giới dữ liệu:* Contact trùng SĐT ở 2 workspace có được gộp tự động hay chỉ link theo `M01` + kiểm quyền `M14`?
     - *State machine:* Khi merge 2 Contact (`MERGED`), bản ghi nguồn bị khóa chỉ đọc hay cho phép unmerge?
     - *Concurrency:* Khi 2 nhân viên sửa cùng 1 hồ sơ thì dùng `expected_version` chặn hay last-write-wins?
   - Với **Tầng 2 (Non-blocking)** — các tham số chưa chốt được ngay (timeout cụ thể, ngưỡng cảnh báo trùng...) sẽ được gắn `[OPEN-GAP: GAP-M01-xx]` và ghi vào `03-planning/GAPS.md`.
3. **Pha 3 — Sinh đặc tả chuẩn EARS & Hybrid Contract:**
   - Tạo `02-specs/modules/M01-CUSTOMER-IDENTITY-MERGE.md` theo đúng 6 mục của `MODULE-SPEC.md`.
   - Mọi hành vi viết theo câu điều kiện **EARS** (`Khi ...`, `Nếu ...`, `Trong khi ... phải ...`) và gắn nhãn `[MASTER]` / `[PROPOSED]` / `[OPEN-GAP]`.
   - Nếu phát sinh command/event public gửi sang module khác (ví dụ `ContactMerged` gửi cho `M02`, `M03`, `M08`), Agent tách riêng ra `02-specs/contracts/M01-CONTACT-MERGED.md` theo `CONTRACT.md`.
4. **Pha 4 — Tự kiểm tra & Chạy 4 script kiểm chứng:**
   - Agent tự rà soát độ phủ ID từ `requirements.json` (không bỏ sót `FR/BR/UC`), cập nhật `02-specs/README.md` và `03-planning/agent/PROGRESS.md`.
   - Chạy đủ 4 lệnh ở `05-tools/` và chỉ báo `Not Run` cho test ứng dụng.

---

## 3. Lệnh kiểm tra thủ công trong Terminal (nếu bạn muốn tự kiểm)

Chạy tại `d:\AI Agent\CRM`:

```powershell
# Kiểm tra toàn bộ 02-specs/ (modules, contracts, changes) và xuất báo cáo độ phủ ID
python 05-tools/verify_module_spec.py

# Kiểm tra riêng 1 file module vừa viết
python 05-tools/verify_module_spec.py --file 02-specs/modules/M01-CUSTOMER-IDENTITY-MERGE.md

# Chạy trọn bộ 4 cổng kiểm chứng của dự án
python 05-tools/build_delivery_inventory.py
python 05-tools/verify_delivery_plan.py
python 05-tools/verify_hrm_integration.py
python 05-tools/verify_module_spec.py
```

Kết quả chi tiết (gồm danh sách ID còn thiếu của từng module so với `requirements.json`) được ghi tại `03-planning/evidence/module-spec-validation.json`.

---

## 4. Xử lý các tình huống thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Muốn Agent giữ trạng thái `Draft` để team review tiếp, chưa muốn chốt | Nói rõ: *"Giữ `Status: Draft`, phần nào chưa rõ thì ghi `[OPEN-GAP]` vào `GAPS.md`."* |
| Muốn chốt nâng trạng thái một module từ `Draft` → `Reviewed` | Nhắn: *"Chốt `M01` lên `Reviewed` sau khi tôi xác nhận các `[PROPOSED]` và đóng `GAP-M01-*`."* |
| Muốn sửa một phần trong `M21`, `M22`, `SL01` đã ổn định | Gọi chế độ `review-change` để đi qua `02-specs/changes/CR-*.md` thay vì sửa chéo không dấu vết. |
| Muốn kiểm tra nghiêm ngặt cả file mở rộng (`M18`, `M23`, `M24`) theo đủ 6 mục `MODULE-SPEC.md` | Chạy `python 05-tools/verify_module_spec.py --strict-all`. |
