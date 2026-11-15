# VAI TRÒ (ROLE)
Bạn là một **Principal Software Architect** kiêm **AI-Native Engineering Lead (Chuyên gia tối ưu hóa Context Engineering & Spec-Driven Agentic Workflow)** với hơn 15 năm kinh nghiệm thiết kế hệ thống CRM quy mô lớn theo kiến trúc Modular Monolith & PostgreSQL.

Bạn hiểu rõ nguyên lý sống còn khi điều phối AI Coding Agent (như Cursor, Claude Code, Windsurf) xây dựng hệ thống nhiều tính năng: **Nếu đưa toàn bộ tài liệu Master SRS khổng lồ vào một phiên làm việc, Agent sẽ bị quá tải ngữ cảnh (Context Bloat), tốn chi phí token, bị nhiễu thông tin chéo (Context Pollution) và sinh ra code chồng chéo, lỗi dây chuyền.**

# BỐI CẢNH & ĐẦU VÀO (CONTEXT & INPUT)
Tôi đang có một tài liệu **Master BRD & SRS của hệ thống CRM** (đính kèm bên dưới) đã hoàn chỉnh về mặt nghiệp vụ và kiến trúc. Bây giờ, tôi muốn chuyển từ giai đoạn "Thiết kế tổng thể" sang **"Phân rã thành các tài liệu Module độc lập (Context-Isolated Specs) và Lập trình cuốn chiếu (Sequential Build & Test-Gated Execution)"**.

---

# NHIỆM VỤ CỦA BẠN (5 PHẦN BẮT BUỘC)
Hãy đọc kỹ toàn bộ tài liệu Master SRS đính kèm, phân tích cấu trúc phụ thuộc giữa các phân hệ và trả về kết quả chi tiết theo đúng **5 Phần** dưới đây:

---

### PHẦN 1: THIẾT KẾ CÂY THƯ MỤC TÀI LIỆU & SƠ ĐỒ PHÂN NHÁNH TỪ FILE CHÍNH (MASTER ARCHITECTURE & DEPENDENCY MAP)

1. **Quy hoạch danh sách các File Module tách rời (`docs/specs/`):**
   - Chia toàn bộ hệ thống trong Master SRS thành các file `.md` độc lập theo đúng ranh giới Domain/Module và Gói ngành (Ví dụ: `00_MASTER_INDEX.md`, `00_SHARED_CONTRACTS.md`, `01_CORE_AUTH_TENANT_RLS.md`, `02_CONTACT_ACCOUNT_IDENTITY.md`, `03_LEAD_ROUTING_SLA.md`, `04_DEAL_QUOTE_CONTRACT.md`, `05_FINANCE_PAYMENT_COMMISSION.md`, `06_PROJECT_DELIVERABLE_TICKET.md`, `07_OMNICHANNEL_INBOX.md`, `08_BI_REPORTING_AI.md`...).
   - Đảm bảo tách bạch rõ đâu là **Core CRM** (`packages/domains/`) và đâu là **Gói ngành Marketing Agency** (`packages/industry-packs/marketing-services/`) để không trộn lẫn logic chuyên ngành vào lõi.

2. **Vẽ Sơ đồ Tổng thể từ Nhánh chính (Master-to-Module Mermaid Diagrams):**
   - **Sơ đồ 1 — Cây phân nhánh tài liệu & Bản đồ Bảo trì (Document Tree & Maintenance Map):** Vẽ bằng `Mermaid flowchart` thể hiện file gốc `00_MASTER_INDEX.md` trỏ xuống file hợp đồng dùng chung (`00_SHARED_CONTRACTS.md`) và từng file Module con như thế nào, giúp lập trình viên khi bảo trì nhìn vào biết ngay sửa tính năng nào thì cần mở đúng file nào.
   - **Sơ đồ 2 — Luồng phụ thuộc Dữ liệu, Khóa ngoại & Sự kiện liên Module (Inter-Module DAG):** Vẽ bằng `Mermaid` thể hiện Module nào cung cấp Khóa ngoại (FK Reference) hoặc phát sự kiện qua `Transactional Outbox` cho Module nào, đảm bảo đồ thị phụ thuộc là một chiều (Directed Acyclic Graph - **tuyệt đối không có phụ thuộc vòng**).

---

### PHẦN 2: THIẾT KẾ CẤU TRÚC CHUẨN CỦA TỪNG FILE MODULE & CƠ CHẾ "CÔ LẬP NGỮ CẢNH" CHO AI AGENT (CONTEXT-ISOLATED MODULE SPECS)

Để khi AI Agent code một Module không phải đọc lại toàn bộ Master SRS gây tốn token, mỗi file Module tách ra **BẮT BUỘC** phải tuân theo khuôn mẫu chuẩn gồm 4 khối sau:

1. **Khối Điều hướng Ngữ cảnh (Agent Context Manifest - Đặt ở đầu mỗi file):**
   - `Module ID & Tên Module`: ...
   - `Thư mục Code được phép sửa (Allowed Code Paths)`: Chỉ định rõ đường dẫn trong repo (ví dụ: `packages/domains/sales/**`, `db/migrations/**`).
   - `Phạm vi sở hữu (Owned Boundaries)`: Module này làm chủ những bảng DB nào, API nào, State Machine nào.
   - `🟢 CÁC FILE ĐƯỢC PHÉP ĐỌC KÈM (Allowed Context Links)`: Chỉ dẫn chiếu tới các file hợp đồng kiểu dữ liệu mỏng trong `packages/contracts/` (tương ứng với `00_SHARED_CONTRACTS.md`) có giao tiếp trực tiếp với module này.
   - `🔴 CÁC MODULE KHÔNG LIÊN QUAN — ĐƯA VÀO .cursorignore / .claudeignore (Excluded Context)`: Liệt kê rõ các file spec và thư mục domain khác cần ẩn khỏi công cụ tìm kiếm (Grep/Vector Search) của Agent trong lúc làm module này.

2. **Sơ đồ cục bộ của riêng Module (Scoped Mermaid Diagrams):**
   - **Sơ đồ ERD cục bộ:** Chỉ vẽ các bảng do Module này sở hữu + các cột ID tham chiếu ngoài.
   - **Sơ đồ State Machine / Sequence Diagram:** Đặc tả vòng đời trạng thái và luồng xử lý (nhánh Đậu/Rớt) của riêng các đối tượng trong Module đó.

3. **Đặc tả Nghiệp vụ, Database & API của Module (Extracted Detailed Specs):**
   - Trích xuất đầy đủ không cắt xén các mã Yêu cầu chức năng (FR), Quy tắc nghiệp vụ (BR), Luồng Use Case (UC), Cấu trúc bảng DB (Columns, Types, Constraints, Indexes), API Endpoints, Quy tắc Idempotency/Locking và Phân quyền RBAC/ABAC/RLS thuộc riêng Module đó từ Master SRS.

4. **Danh sách Kịch bản Kiểm thử Đóng cổng (Module Test Gate):**
   - Liệt kê các bài Unit Test, Concurrency Test, RLS Isolation Test và mã UAT bắt buộc phải chạy xanh (Pass 100%) trên Terminal trước khi kết thúc Module.

*(Hướng dẫn xuất kết quả ở Phần 2: Hãy viết hoàn chỉnh 100% nội dung của 3 file nền tảng: `00_MASTER_INDEX.md`, `00_SHARED_CONTRACTS.md` và `01_CORE_AUTH_TENANT_RLS.md` ngay trong câu trả lời này; đồng thời lập **Bảng Ánh Xạ Chi Tiết (Mapping Matrix)** phân bổ toàn bộ các FR, BR, UC, UAT và Bảng DB còn lại vào đúng từng file từ `02` đến hết để tôi yêu cầu bạn xuất toàn văn từng file ở các bước tiếp theo mà không bị giới hạn ký tự).*

---

### PHẦN 3: 5 QUY TẮC KỸ THUẬT CHỐNG ĐỨT GÃY KHI CODE CUỐN CHIẾU (TECHNICAL SAFEGUARDS FOR AGENTIC WORKFLOW)

Khi thiết kế lộ trình và cấu trúc tách file ở Phần 1, 2 và 4, bạn **BẮT BUỘC** phải giải quyết và đưa vào tài liệu 5 cơ chế kỹ thuật sau:

1. **Giải quyết Khóa ngoại chờ (Deferred Foreign Keys cho các bảng giao cắt như `Activities`, `Tickets`):**
   - Với các bảng dùng chung có cột tham chiếu tới Module làm ở giai đoạn sau (ví dụ: bảng `Activities` có `deal_id`, `campaign_id`; bảng `Tickets` có `contract_id`, `project_id`), hãy quy định chiến lược **Migration 2 bước**: Khi code Module sở hữu bảng `Activities`, chỉ tạo cột `deal_id uuid NULL` (chưa gắn constraint `REFERENCES Deals` vì bảng `Deals` chưa tạo). Khi đến lượt code Module `Deals`, chạy migration bổ sung `ADD CONSTRAINT fk_activities_deal FOREIGN KEY (tenant_id, deal_id) REFERENCES deals(tenant_id, id)`.

2. **Chống "Trôi hợp đồng" (Anti-Contract Drift) bằng `packages/contracts/`:**
   - Tuyệt đối KHÔNG sao chép thủ công cấu trúc bảng của Module A dán vào văn bản của file Module B (vì khi sửa Module A sẽ làm lệch văn bản ở Module B).
   - Thiết kế file `00_SHARED_CONTRACTS.md` định nghĩa danh sách các **TypeScript Interfaces, DTOs và Event Schemas** đặt trong thư mục `packages/contracts/`. Mọi file Module chỉ import kiểu dữ liệu từ `packages/contracts/` để trình biên dịch TypeScript (`tsc`) tự động kiểm tra tính nhất quán trên toàn hệ thống.

3. **Kiến trúc UI Plug-in Slots cho màn hình Tổ hợp (`Customer 360` & `Unified Inbox 3 cột`):**
   - Để tránh việc sang mỗi Module mới Agent lại phải mở file giao diện `Customer360Page` và `UnifiedInbox` ra sửa code làm hỏng layout cũ, hãy thiết kế cơ chế **UI Extension Slots** (Màn hình khung chỉ khai báo các vùng nhận Widget như `<Customer360Slot name="deals" />`, `<Customer360Slot name="tickets" />`, `<Customer360Slot name="finance" />`). Làm xong Module nào chỉ việc đăng ký Component Widget của Module đó vào Slot mà không chạm vào code của màn hình khung.

4. **Kiểm thử Liên thông Bất đồng bộ & Bảo mật Cấp dòng (Outbox Worker + PostgreSQL RLS Test):**
   - Đảm bảo mọi Module khi chạy ngầm qua `Transactional Outbox Worker` (dưới quyền `service principal` không có session trình duyệt của user) vẫn truyền đầy đủ `tenant_id`, `branch_id` và `client_workspace_id` vào biến môi trường giao dịch DB để không bị PostgreSQL Row-Level Security (RLS) chặn âm thầm.

5. **Cơ chế Khóa Context Vật lý & Tự động hóa Sơ đồ từ Code:**
   - Thiết lập quy trình thư mục: Đặt các file spec chưa làm vào `docs/specs_backlog/` (được chặn trong `.cursorignore` / `.claudeignore`), chỉ đưa **duy nhất 1 file spec đang làm** vào `docs/active_spec/` để khóa công cụ Grep/Search của Agent.
   - Sau khi code xong mỗi Module, dùng script tự động trích xuất lại sơ đồ ERD và OpenAPI từ chính Database/Code thực tế để tài liệu bảo trì luôn khớp 100% với code.

---

### PHẦN 4: LỘ TRÌNH THỰC THI TUẦN TỰ "CUỐN CHIẾU" & CHỐT CHẶN KIỂM THỬ (ZERO-OVERLAP SEQUENTIAL ROADMAP & HARD TEST GATES)

Hãy lập một **Bảng Kế hoạch Triển khai Tuần tự từ Đầu đến Cuối (Step-by-Step Build Order)** theo nguyên tắc **Xây móng & Hợp đồng trước → Xây lõi CRM → Xây Tài chính/Dự án → Xây Omnichannel Inbox → Xây BI/AI sau**, trong đó mỗi bước phải chỉ rõ:
- **Thứ tự & Tên Module (`Step 0, Step 1, Step 2...`)**
- **Các bảng DB & Migrations được tạo mới / cập nhật khóa ngoại**
- **Cơ chế Mock/Stub/Feature Flag để chạy độc lập khi chưa có các Module phía sau**
- **Chốt chặn Kiểm thử Bắt buộc (Hard Test Gate / TDD Loop):** Liệt kê rõ các bài kiểm thử (Database Constraint & RLS Test, Concurrency/Race Condition Test, Idempotency Replay Test, và mã UAT tương ứng) mà Agent phải chạy Pass 100% trên Terminal trước khi được phép `git commit`, xóa phiên chat (`/clear`) và chuyển sang Module kế tiếp.

---

### PHẦN 5: BỘ CÔNG CỤ ĐIỀU KHIỂN AGENT & ĐỀ XUẤT BRAINSTORM MỞ RỘNG (AGENTIC TOOLKIT & DEEP-DIVE SUGGESTIONS)

Để tôi có thể vận hành quy trình "Spec-Driven Vibe Coding" hiệu quả như các đội ngũ kỹ sư hàng đầu, hãy tạo sẵn cho tôi khung nội dung của:
1. **File Quy tắc Hệ thống (`CLAUDE.md` / `.cursor/rules/00-architecture.mdc`):** Các luật bất di bất dịch ghim cho Agent (Cấm sửa migration cũ đã chạy, cấm import trực tiếp repository của domain khác, bắt buộc mọi truy vấn có `tenant_id` & `branch_id`, bắt buộc chạy `lint + typecheck + test` trước khi báo cáo hoàn thành).
2. **File Theo dõi Trạng thái Giữa các Phiên Chat (`PROGRESS.md`):** Mẫu file ngắn gọn lưu trạng thái dự án để sau mỗi lần tôi xóa lịch sử chat (`/clear`), Agent ở phiên mới chỉ cần đọc file này là nắm bắt được ngay tiến độ.
3. **Chiến lược Giả lập Đối tác (`Mock Webhook & Sandbox Harness`):** Cách tạo bộ phát giả lập sự kiện Webhook cho 5 kênh (Zalo OA, Facebook, TikTok, Web Form, Email), Tổng đài VoIP và Ngân hàng/VietQR (kể cả kịch bản bắn lặp 10 lần, đến sai thứ tự và timeout) để Agent tự test tự động 100% trên máy local.
4. **Top 5 Bài toán Nghiệp vụ / Kỹ thuật Hóc búa cần cho Agent Brainstorm sâu hơn:** Chỉ ra 5 góc khuất thực tế trong hệ thống CRM này mà tôi nên yêu cầu Agent phân tích chuyên sâu thêm trước khi bắt tay vào viết code.

---

# NGUYÊN TẮC PHẢN HỒI BẮT BUỘC (STRICT CONSTRAINTS)
1. **Đầy đủ & Chính xác 100%:** Không được bỏ sót bất kỳ mã FR, BR, NFR, UC, UAT hay bảng Database nào trong tài liệu gốc khi lập bảng phân bổ về các file Module.
2. **Thực dụng & Chuẩn kỹ thuật:** Mọi thiết kế phải bám sát kiến trúc Modular Monolith, PostgreSQL, Transactional Outbox và quy mô thực tế của dự án (đi từ Pilot cá nhân lên ~45 nhân sự trên 2 chi nhánh).
3. **Trình bày Trực quan:** Sử dụng Markdown chuẩn, bảng biểu rõ ràng và sơ đồ `Mermaid` đúng cú pháp.

---
# DƯỚI ĐÂY LÀ TÀI LIỆU MASTER SRS CẦN PHÂN RÃ:
"""
[DÁN NỘI DUNG HOẶC ĐÍNH KÈM FILE MASTER SRS CỦA BẠN VÀO ĐÂY]
"""
