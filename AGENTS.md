# Quy chuẩn vận hành AI Agent — Giai đoạn Brainstorm & Chuẩn hóa Tài liệu

Tệp này quy định kỷ luật làm việc cho mọi AI Agent thao tác trên kho tài liệu `D:\AI Agent\CRM`.

---

## 1. Phạm vi & Ranh giới tuyệt đối (Documentation-Only)

1. **KHÔNG sinh mã nguồn ứng dụng:** Không tạo thư mục code app (`src/`, `packages/`, `apps/`), `package.json`, SQL migration, Dockerfile hay chạy test phần mềm cho đến khi bộ đặc tả hoàn chỉnh và chủ dự án chuyển giai đoạn.
2. **Master v1.9 là nguồn chuẩn nghiệp vụ:** Mọi đặc tả chi tiết ở `02-specs/` phải truy vết về [CRM_MASTER_BRD_SRS_HOP_NHAT.md](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md). Không tự ý bịa thêm quy tắc kinh doanh, số liệu KPI/SLA, tên bảng vật lý hoặc chính sách doanh nghiệp khi chưa xác nhận với chủ dự án; các điểm chưa chốt phải ghi nhận vào [03-planning/GAPS.md](03-planning/GAPS.md) hoặc mục tham số mở của module.
3. **Không dùng `99-archive/` làm nguồn thiết kế hiện hành:** Toàn bộ thư mục [99-archive/](99-archive/README.md) chỉ phục vụ đối chiếu lịch sử; không đọc lẫn vào luồng brainstorm hiện tại và **tuyệt đối không chạy lại** các script trong `99-archive/legacy-build-scripts/`.

---

## 2. Quy tắc tổ chức & đặt tên tệp mới

- **Thư mục đang hoạt động:** Chỉ ghi nhận đặc tả mới vào `01-architecture/`, `02-specs/` (gồm `modules/`, `slices/`, `contracts/` cho public cross-module contract và `changes/` cho Change Proposal) hoặc `03-planning/`. Quy trình/skill nội bộ cho AI Agent lưu tại `.agents/skills/`.
- **Quy ước đặt tên tệp mới:** Dùng ASCII không dấu, không khoảng trắng (`Mxx-TEN-MODULE.md` cho module spec theo chuẩn `M21`/`M22`, `SLxx-TEN-SLICE.md` cho slice spec theo chuẩn `SL01`/`SL08`, hoặc `kebab-case` cho tài liệu phụ trợ).
- **Bảo toàn mã định danh:** Giữ nguyên mã module `M01–M22` và toàn bộ namespace ID (`FR`, `BR`, `UC`, `NFR`, `W-F`, `BR-W`, `UC-W`, `W-T`, `M21-F`, `UC-P`, `BR-P`, `P-T`, `M22-F`, `UC-H`, `BR-H`, `H-T`...) theo Master v1.9. Không tự ý gộp hoặc đổi tên mã slice `SL00–SL11`.

---

## 3. Quy trình chuẩn khi Brainstorm & Tách đặc tả Module (`M01–M20`)

Khi được yêu cầu phân tích hoặc tách mới một module/slice, **kích hoạt Workspace Skill [crm-ba-spec](.agents/skills/crm-ba-spec/SKILL.md)** (`module`, `slice`, hoặc `review-change`) và thực hiện đủ:

1. **Đọc ngữ cảnh tối thiểu trước:**
   - [03-planning/agent/active-task.json](03-planning/agent/active-task.json) và [03-planning/agent/PROGRESS.md](03-planning/agent/PROGRESS.md)
   - [01-architecture/INVARIANTS.md](01-architecture/INVARIANTS.md) và [01-architecture/INDEX.md](01-architecture/INDEX.md)
   - Đúng các mục liên quan trong [00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (tra dòng nhanh bằng [03-planning/trace/source-sections.json](03-planning/trace/source-sections.json) và [03-planning/trace/requirements.json](03-planning/trace/requirements.json))
   - Các báo cáo/nguồn liên quan trong `04-research/` nếu cần đối chiếu nguồn gốc.
2. **Tuân thủ khuôn mẫu & Cổng hỏi ngược:** Bắt buộc dùng [MODULE-SPEC.md](02-specs/templates/MODULE-SPEC.md) cho module mới, viết hành vi theo chuẩn EARS kèm nhãn `[MASTER]` / `[PROPOSED]` / `[OPEN-GAP]`, hỏi chặn qua `ask_question` đối với quyết định ranh giới/state machine, và dùng [CONTRACT.md](02-specs/templates/CONTRACT.md) tại `02-specs/contracts/` cho public cross-module command/event.
3. **Phân biệt rõ trạng thái thông tin:** Tách bạch giữa (a) quy định đã có trong Master v1.9, (b) đề xuất thiết kế mới khi brainstorm, và (c) giả định/câu hỏi còn mở cần chủ dự án chốt. Thay đổi trên spec đã `Reviewed`/`Ready` đi qua `02-specs/changes/`.
4. **Cập nhật điều hướng & kiểm chứng sau mỗi thay đổi:**
   - Cập nhật trạng thái bảng trong [02-specs/README.md](02-specs/README.md) và nhật ký trong [03-planning/agent/PROGRESS.md](03-planning/agent/PROGRESS.md).
   - Chạy đủ 4 lệnh kiểm chứng trước khi kết thúc phiên:
     ```powershell
     python 05-tools/build_delivery_inventory.py
     python 05-tools/verify_delivery_plan.py
     python 05-tools/verify_hrm_integration.py
     python 05-tools/verify_module_spec.py
     ```
   - Chỉ báo cáo trạng thái test ứng dụng là `Not Run`; tuyệt đối không ghi `Pass` khi chưa có phần mềm chạy thật.
