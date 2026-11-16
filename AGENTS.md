# Quy chuẩn vận hành AI Agent — Giai đoạn Brainstorm & Chuẩn hóa Tài liệu

Tệp này quy định kỷ luật làm việc cho mọi AI Agent thao tác trên kho tài liệu `D:\AI Agent\CRM`.

---

## 1. Phạm vi & Ranh giới tuyệt đối (Documentation-Only)

1. **KHÔNG sinh mã nguồn ứng dụng:** Không tạo thư mục code app (`src/`, `packages/`, `apps/`), `package.json`, SQL migration, Dockerfile hay chạy kiểm thử phần mềm ứng dụng cho đến khi bộ đặc tả hoàn chỉnh và chủ dự án chuyển giai đoạn (các script kiểm chứng tài liệu/checker trong `05-tools/` không phải kiểm thử phần mềm CRM).
2. **Master v1.9 là nguồn chuẩn nghiệp vụ:** Mọi đặc tả chi tiết ở `02-specs/` phải truy vết về [CRM_MASTER_BRD_SRS_HOP_NHAT.md](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md). Không tự ý bịa thêm quy tắc kinh doanh, số liệu KPI/SLA, tên bảng vật lý hoặc chính sách doanh nghiệp khi chưa xác nhận với chủ dự án; các điểm chưa chốt phải ghi nhận vào [03-planning/GAPS.md](03-planning/GAPS.md) hoặc mục tham số mở của module.
3. **Không dùng `99-archive/` làm nguồn thiết kế hiện hành:** Toàn bộ thư mục [99-archive/](99-archive/README.md) chỉ phục vụ đối chiếu lịch sử; không đọc lẫn vào luồng brainstorm hiện tại và **tuyệt đối không chạy lại** các script trong `99-archive/legacy-build-scripts/`.

---

## 2. Quy tắc tổ chức & đặt tên tệp mới

- **Thư mục đang hoạt động:** Chỉ ghi nhận đặc tả mới vào `01-architecture/`, `02-specs/` (gồm `modules/`, `slices/`, `contracts/` cho public cross-module contract và `changes/` cho Change Proposal) hoặc `03-planning/`. Quy trình/skill nội bộ cho AI Agent lưu tại `.agents/skills/`.
- **Quy ước đặt tên tệp mới:** Dùng ASCII không dấu, không khoảng trắng (`Mxx-TEN-MODULE.md` cho module spec theo chuẩn `M21`/`M22`, `SLxx-TEN-SLICE.md` cho slice spec theo chuẩn `SL01`/`SL08`, hoặc `kebab-case` cho tài liệu phụ trợ).
- **Bảo toàn mã định danh:** Giữ nguyên mã module `M01–M22` theo Master v1.9 (cùng mã mở rộng đề xuất `M23–M24`, `M18-F08–11`) và toàn bộ namespace ID (`FR`, `BR`, `UC`, `NFR`, `W-F`, `BR-W`, `UC-W`, `W-T`, `M21-F`, `UC-P`, `BR-P`, `P-T`, `M22-F`, `UC-H`, `BR-H`, `H-T`...). Không tự ý gộp hoặc đổi tên mã slice `SL00–SL11`.

---

## 3. Quy trình chuẩn khi Brainstorm, Tách đặc tả & Bảo trì (`M01–M24`, `SL00–SL11`)

Khi được yêu cầu phân tích, tách mới hoặc bảo trì một module/slice, **kích hoạt Workspace Skill [crm-ba-spec](.agents/skills/crm-ba-spec/SKILL.md)** (`module`, `slice`, hoặc `review-change`) và thực hiện đủ:

1. **Đọc ngữ cảnh tối thiểu trước:**
   - [03-planning/agent/active-task.json](03-planning/agent/active-task.json), [03-planning/agent/PROGRESS.md](03-planning/agent/PROGRESS.md) và [02-specs/CONTRACTS-REGISTRY.md](02-specs/CONTRACTS-REGISTRY.md)
   - [01-architecture/INVARIANTS.md](01-architecture/INVARIANTS.md), [01-architecture/INDEX.md](01-architecture/INDEX.md) và các ADR liên quan trong `01-architecture/decisions/`
   - Chạy `python 05-tools/build_module_context.py --module <Mxx>` để xác định đúng dải dòng liên quan trong [00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md](00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (tránh nạp nguyên file `requirements.json` hay toàn văn Master)
   - Các báo cáo/nguồn liên quan trong `04-research/` nếu cần đối chiếu nguồn gốc.
2. **Tuân thủ khuôn mẫu & Cổng hỏi ngược:** Bắt buộc dùng [MODULE-SPEC.md](02-specs/templates/MODULE-SPEC.md) cho module mới, viết hành vi theo chuẩn EARS kèm nhãn `[MASTER]` / `[PROPOSED]` / `[OPEN-GAP]`, thực hiện cổng hỏi chặn cho quyết định ranh giới/state machine (qua công cụ hỏi tương tác hiện có như `ask_question`, hoặc hỏi trực tiếp bằng văn bản nếu môi trường không có tool tương tác), và dùng [CONTRACT.md](02-specs/templates/CONTRACT.md) tại `02-specs/contracts/` cho public cross-module command/event.
3. **Phân biệt rõ trạng thái thông tin & Khóa sửa spec đã duyệt:** Tách bạch giữa (a) quy định đã có trong Master v1.9 (`[MASTER]`), (b) đề xuất thiết kế mới (`[PROPOSED]` — kể cả sau khi được duyệt vẫn giữ `[PROPOSED]` kèm `decision_ref`, không đổi thành `[MASTER]`), và (c) điểm còn mở (`[OPEN-GAP]` phân loại rõ phạm vi chặn). Mọi thay đổi trên spec đã `Reviewed`/`Ready` (kể cả khi đóng GAP từ trả lời Stakeholder hoặc mở rộng contract Wave trước) phải đi qua Change Proposal tại `02-specs/changes/`.
4. **Cập nhật điều hướng & kiểm chứng sau mỗi thay đổi:**
   - Cập nhật trạng thái bảng trong [02-specs/README.md](02-specs/README.md) và nhật ký trong [03-planning/agent/PROGRESS.md](03-planning/agent/PROGRESS.md).
   - Trong lúc soạn thảo hoặc vai Worker song song có thể chạy kiểm cục bộ `--file`; khi kết thúc phiên có sửa tài liệu (hoặc vai Coordinator cuối sóng), bắt buộc chạy tái sinh registry (nếu có thêm/sửa module, contract hoặc ADR) và đủ 4 lệnh kiểm chứng toàn kho:
     ```powershell
     python 05-tools/build_module_context.py --build-registry
     python 05-tools/build_delivery_inventory.py
     python 05-tools/verify_delivery_plan.py
     python 05-tools/verify_hrm_integration.py
     python 05-tools/verify_module_spec.py
     ```
   - Chỉ báo cáo trạng thái test ứng dụng là `Not Run`; tuyệt đối không ghi `Pass` khi chưa có phần mềm chạy thật. Trạng thái tài liệu `Ready` theo phạm vi cũng không tự cho phép chuyển khỏi giai đoạn `Documentation-Only`.


## 4. Cổng nạp ngữ cảnh đầu phiên — protocol v2

Quy trình này thay thế hướng dẫn cũ trong skill về tự dò transcript, “0 token LLM” và ngữ cảnh tự động đầy đủ. Áp dụng cho module, slice và review/change. Đây là quy trình agent bắt buộc thực hiện, không phải hook chạy khi mở chat.

1. Đọc manifest, Sticky đầu PROGRESS, INVARIANTS, INDEX và registry. Đường dẫn tương đối trong manifest tính từ thư mục chứa manifest.
2. Chạy `python 05-tools/build_module_context.py --module Mxx --out "<ArtifactDir>/scratch/context-Mxx.md" --check-tokens`, thay placeholder bằng đường dẫn thực ngoài kho. Với slice, chạy cho từng module thuộc phạm vi; với review workflow/checker, chọn module đại diện và các module bị ảnh hưởng. Thiếu nguồn hoặc registry cũ phải xử lý lỗi; tái sinh registry khi nguồn thay đổi.
3. Đọc gói, hợp đồng/ADR liên quan và dải dòng Master. Các tóm tắt có `...` phải đọc tiếp nguồn. Registry là chỉ mục, không thay thế quyết định gốc. Danh sách kết quả không giới hạn số mục; đọc theo đoạn khi cần. Python trích xuất không gọi LLM, nhưng đọc kết quả vẫn tốn token.
4. Trước khi soạn spec, chạy `python 05-tools/build_module_context.py --verify-packet "<ArtifactDir>/scratch/context-Mxx.md"`. Nếu gói hoặc nguồn đổi, tạo lại và đọc delta. File `.receipt.json` chứng minh phiên bản nguồn/gói, không chứng minh agent đã đọc hoặc hiểu. Cập nhật tiến độ cần ghi module, đường dẫn gói, kết quả kiểm và quyết định W1 áp dụng/không áp dụng có lý do.
5. Telemetry mặc định `UNKNOWN`; chỉ dùng `--transcript` khi đã xác định đúng phiên hiện tại. Không tự chọn transcript gần nhất. UNKNOWN không đồng nghĩa GREEN; không dừng/compact/mở chat từ số liệu phiên khác.
6. Checker chỉ kiểm cấu trúc và mẫu hồi quy khai báo; vẫn phải rà ngữ nghĩa. Contract Reviewed/Ready kể cả additive vẫn cần Change Proposal theo Mục 3.
