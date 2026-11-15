# NHẬT KÝ PHỎNG VẤN BA & BỘ CÂU HỎI KHAI THÁC NGHIỆP VỤ DỰ ÁN CRM

- **Vai trò điều phối:** Senior Business Analyst (20 năm kinh nghiệm)
- **Chủ dự án / Product Owner:** Chủ doanh nghiệp (xây dựng cho chính công ty Agency của mình)
- **Baseline tham chiếu:** [CRM_MASTER_BRD_SRS_HOP_NHAT.md](../t%C3%A0i%20li%E1%BB%87u%20tham%20kh%E1%BA%A3o/CRM_MASTER_BRD_SRS_HOP_NHAT.md) (v1.9 — 4.861 dòng), [GAPS.md](../t%C3%A0i%20li%E1%BB%87u%20tham%20kh%E1%BA%A3o/docs/delivery-plan/GAPS.md), [prompt.docx](../prompt.docx)
- **Ngày lập:** 15/11/2026
- **Trạng thái:** Đang trong quá trình `/grill-me` — **Đã chốt xong Nhánh 1 và phần đầu Nhánh 2 (Câu 1 → Câu 4)**. Xuất file để Chủ dự án kiểm tra trước khi đi tiếp từ Câu 5.

---

## PHẦN A — NHẬT KÝ CÁC CÂU HỎI ĐÃ PHỎNG VẤN & CHỐT TỪ ĐẦU BUỔI (Q1 → Q4)

### Câu hỏi #1 — Gốc cây quyết định: Mối quan hệ với tài liệu hiện có
- **Câu hỏi:** Mối quan hệ chính xác giữa bộ tài liệu hoàn chỉnh chúng ta sắp thống nhất với thư mục `tài liệu tham khảo` (Master 1.9) và `prompt.docx` hiện có là gì?
- **Các phương án đã đưa ra:**
  1. **(Recommended)** Đây chính là dự án CRM Agency Marketing B2B/B2C dựa trên nền Master 1.9: cần rà soát từng ngóc ngách còn mở (`O01–O08`, `W-O`, `P-O`, `H-O`), đối chiếu thực tế khách hàng để chốt cứng nghiệp vụ rồi hoàn thiện bộ tài liệu giao khách hàng và đặc tả cho dev/AI triển khai.
  2. Đây là dự án CRM cho một khách hàng hoặc ngành nghề KHÁC (`tài liệu tham khảo` chỉ là mẫu tham chiếu cấu trúc).
  3. Vẫn là CRM Agency Marketing nhưng làm lại gọn và thực tế hơn v1.9 để chốt nhanh MVP.
  4. Nghiệp vụ trong Master 1.9 cơ bản đã chốt, chỉ hoàn thiện bộ Spec kỹ thuật phân rã 22 module theo `prompt.docx`.
- **Chủ dự án đã chọn:** **Phương án 1**.
- **Kết luận BA:** Dùng Master 1.9 làm baseline, rà soát và khóa toàn bộ **33 tham số mở ở Phụ lục A** + **14 điểm nghẽn ở `GAPS.md`** theo thực tế vận hành công ty.

---

### Câu hỏi #2 — Nhánh 1: Định dạng đầu ra của "Bộ tài liệu hoàn chỉnh"
- **Câu hỏi:** Định dạng cuối cùng của "bộ tài liệu hoàn chỉnh" mà bạn muốn chúng ta cùng tạo ra sau khi phỏng vấn xong là cấu trúc nào?
- **Các phương án đã đưa ra:**
  1. **(Recommended)** Bộ tài liệu 2 lớp đồng bộ:
     - **Lớp 1 — Business Sign-off Pack:** BRD + SRS tổng hợp v2.0 + Ma trận Policy/UAT dễ đọc để khách hàng/Ban Giám Đốc ký chốt phạm vi.
     - **Lớp 2 — Dev/AI Context-Isolated Pack:** Chốt `00_SHARED_CONTRACTS` + tách đủ 22 Module Specs `M01–M22` + Roadmap cuốn chiếu theo `prompt.docx` và `delivery-plan`.
  2. Ưu tiên Bộ tài liệu Nghiệp vụ & Khảo sát Khách hàng trước, chưa vội tách Spec kỹ thuật `M01–M22`.
  3. Chỉ nâng cấp trực tiếp `CRM_MASTER_BRD_SRS_HOP_NHAT.md` từ v1.9 lên v2.0.
  4. Chỉ xuất ngay Bộ Spec Kỹ thuật 22 Module cho AI Agent.
- **Chủ dự án đã chọn:** **Phương án 1**, kèm **yêu cầu bổ sung bắt buộc**:
  - Phải có **Sơ đồ luồng hoạt động tổng thể của toàn dự án (Tầng cao nhất / Level 0)**.
  - Tiếp theo là **Sơ đồ luồng của từng chức năng (Level 1 / Level 2)**.
  - Các sơ đồ luồng chức năng phải **có liên kết logic với nhau** (đầu ra của luồng này khớp nối với đầu vào của luồng kế tiếp) và **có mô tả hướng dẫn đầy đủ**.

---

### Câu hỏi #3 — Nhánh 2: Bối cảnh thực tế đơn vị sử dụng, Quy mô & Mô hình sở hữu (`O01`, `O03`, `O08`, `H-O01`)
- **Câu hỏi:** Thực trạng đơn vị sở hữu/sử dụng hệ thống (khách hàng của dự án này) hiện tại đang ở quy mô và mô hình nào?
- **Các phương án đã đưa ra:**
  1. **(Recommended)** Một công ty Agency Marketing cụ thể đang giai đoạn tinh gọn/khởi đầu (1–7 nhân sự kiêm nhiệm, đang quản lý bằng Excel/Zalo/Pancake) với lộ trình mở rộng lên ~45 nhân sự và 2 chi nhánh — giữ cấu trúc 1 Agency chủ quản kèm nhiều Client Workspace cho đối tác.
  2. Công ty Agency đã có sẵn đội ngũ hoàn chỉnh (~20–45+ nhân sự, 2 chi nhánh, đủ phòng ban) cần số hóa ngay từ Phase 1.
  3. Sản phẩm CRM đóng gói/SaaS đa khách hàng (Multi-tenant) bán cho nhiều công ty khác nhau.
  4. Doanh nghiệp đa pháp nhân/đa mô hình (vừa Agency B2B vừa tự bán lẻ B2C) với 2 chi nhánh hạch toán độc lập ngay từ đầu.
- **Chủ dự án đã chọn:** **Phương án 1**, kèm **xác nhận bổ sung**: *"tôi đang làm cho công ty của tôi"*.
- **Kết luận BA:**
  - Đây là hệ thống xây cho **chính công ty Agency của Chủ dự án**.
  - Nguyên tắc thiết kế bắt buộc: **Pilot phải chạy nhẹ nhàng cho 1–7 người kiêm nhiệm** (không ép luồng duyệt rườm rà gây tắc nghẽn ngày đầu), nhưng **kiến trúc dữ liệu & định danh phải thiết kế sẵn** để mở rộng lên ~45 nhân sự và 2 chi nhánh mà không phải đập đi xây lại.

---

### Câu hỏi #4 — Nhánh 2: Định hướng Công nghệ & Thời điểm chốt Tech Stack (`O05`, `GAP-01`, `GAP-02`)
Câu hỏi này đã đi qua 3 lượt trao đổi để làm rõ tác động kỹ thuật đối với bộ tài liệu:

- **Lượt 4a — Câu hỏi gốc:** Hướng thực thi kỹ thuật nào được chốt cho dự án (`Self-build TS/React/NestJS/PostgreSQL`, `Stack TS/ngôn ngữ khác`, `Hybrid/Odoo/Frappe/EspoCRM`, hay `Giữ trung lập để làm PoC`)?
  - *Phản hồi Chủ dự án:* Hỏi đánh giá xem công nghệ ở Phương án 1 (`TS + React + NestJS + PostgreSQL`) đã tối ưu chưa, vì sao và phương án nào tốt hơn.
  - *Phân tích BA đã trả lời:*
    - **Ưu điểm của `TS + React + NestJS + PostgreSQL`:** Đồng nhất 1 ngôn ngữ (AI Coding Agent ít lỗi lệch kiểu giữa FE/BE/Contracts); `NestJS` ép ranh giới 22 module chặt (tránh AI import chéo); `PostgreSQL` có Row-Level Security (RLS) tách `AGENCY` vs `CLIENT` workspace vs `HRM` và Transaction ACID cho tài chính/hoa hồng, đồng thời kiêm Outbox queue không cần Redis/Kafka sớm.
    - **Nhược điểm nếu làm sai cách:** Tự xây cả 22 module (kể cả Omnichannel 5 kênh và Tính lương `M22`) cho team 1–7 người từ con số 0 là rất nặng nếu không cắt lát MVP chặt; `NestJS` có boilerplate nhiều hơn `Fastify/Hono`.
    - **So sánh:** Tự chủ + AI code cuốn chiếu dài hạn → `TS + React + NestJS + PostgreSQL` (cắt MVP chặt) là tối ưu nhất; cần ra dùng gấp trong 2–4 tuần với chi phí bảo trì thấp nhất → `Hybrid` (tận dụng Chatwoot/MISA/HRM ngoài) kinh tế hơn.
- **Lượt 4b — Đề xuất thêm phương án tách 2 bước:** Đưa ra thêm lựa chọn *"Tách 2 giai đoạn: chốt sạch 100% Nghiệp vụ & Sơ đồ luồng Lớp 1 trước, cuối buổi mới chọn công nghệ để sinh Lớp 2"*.
  - *Phản hồi Chủ dự án:* Hỏi *"phương án thứ 4 có làm ảnh hưởng gì đến dự án này không?"*
  - *Phân tích BA đã trả lời:* Không ảnh hưởng xấu; ngược lại giúp tập trung 100% vào nghiệp vụ thực tế không bị định kiến công cụ chi phối, chọn stack ở cuối buổi chuẩn xác hơn, và toàn bộ Lớp 1 giữ nguyên giá trị để sinh Lớp 2 (chỉ cần vẫn chốt rõ các phần mềm ngoài công ty đang giữ lại như Pancake/Zalo/Kế toán).
- **Lượt 4c — Câu hỏi xác nhận chốt:**
  1. **(Recommended)** Chốt Phương án 4 (Khai thác và thống nhất sạch 100% Nghiệp vụ + Sơ đồ luồng Lớp 1 trước, cuối buổi nhìn tổng thể rồi chốt Tech Stack để sinh Bộ Spec Lớp 2).
  2. Chốt luôn Phương án 1 ngay bây giờ: Tự xây (`TypeScript + React + NestJS + PostgreSQL`).
  3. Chốt luôn Phương án 3 ngay bây giờ: `Hybrid`.
- **Chủ dự án đã chọn:** *"chọn phương án 1, nhưng hãy xuất bộ câu hỏi phỏng vấn từ nảy đến giờ ra 1 file để tôi check trước."*
- **Cần Chủ dự án check lại 1 điểm nhỏ tại đây:** Trong lượt 4c, vị trí số 1 là **làm sạch Nghiệp vụ Lớp 1 trước, chốt Tech Stack ở cuối buổi**. Bạn xác nhận giúp đúng là ý này (hay ý bạn muốn chốt cứng luôn `Self-build TypeScript + React + NestJS + PostgreSQL` ngay từ bây giờ)?

---

## PHẦN B — LỘ TRÌNH CÁC CÂU HỎI TIẾP THEO ĐỂ BẠN XEM TRƯỚC (CÂU #5 TRỞ ĐI)

Đây là bản đồ những ngóc ngách chúng ta sẽ đi lần lượt **từng câu một** ở các bước kế tiếp (bám sát toàn bộ các mục còn mở trong Master 1.9):

### Nhánh 2 (tiếp) — Pháp nhân, Chi nhánh & Bộ máy hiện tại (`O03`, `O08`, `H-O01`)
- **Câu #5:** Thực tế công ty hiện tại đang có chính xác bao nhiêu người, làm những vai trò gì (ai kiêm Sales, Account/CSKH, Media, Kế toán, HR, Bảo vệ dữ liệu), và 2 chi nhánh trong lộ trình có dùng **1 pháp nhân chung** hay **2 pháp nhân xuất hóa đơn/thu tiền độc lập**?
- **Câu #6:** Hiện tại đang quản lý những dữ liệu nào ở **Excel / Google Sheet / Zalo cá nhân / Pancake** cần mang vào hệ thống (data khách hàng, hợp đồng, công việc, nhân sự)?

### Nhánh 3 — Sản phẩm dịch vụ, Phễu B2B vs B2C & Hợp đồng (`O01`, `O02`, `A01`, `A04`, `BR03–BR05`)
- **Câu #7:** Làm rõ cụm **"Lead B2C của công ty"** (trong `A01` ghi `500–100` chưa chuẩn hóa): Thực tế công ty bạn bán dịch vụ Marketing **chỉ cho doanh nghiệp/chủ shop (B2B)** hay có bán cả gói nhỏ/dịch vụ cho **khách hàng cá nhân (B2C)**? Nếu có B2C thì gói đó là gì, giá trị và quy trình chốt khác B2B thế nào?
- **Câu #8:** Danh mục gói dịch vụ thực tế của Agency (Retainer hàng tháng, Dự án trọn gói, Sản xuất nội dung, Phí quản lý Ads % ngân sách hay cố định), quy chuẩn **số vòng sửa tối đa**, **cơ chế chốt nghiệm thu** và **luật gia hạn/báo trước (notice deadline)** khi kết thúc kỳ?
- **Câu #9:** Định nghĩa chính xác **"Khách hàng mới / Khách hàng trả tiền / Lead trùng (Dedup)"** (`O01`): Trùng theo số điện thoại, Zalo ID, email hay mã số thuế; một người đại diện quản lý 3 shop khác nhau tính là 1 Contact hay 3 Account?

### Nhánh 4 — Omnichannel, Kênh tiếp nhận & Ranh giới Dữ liệu Đối tác (`O04`, `O06`, `P-O01–08`, `M21`)
- **Câu #10:** Các kênh liên lạc công ty thực sự dùng ở Phase 1 (Zalo OA công ty vs Zalo cá nhân của Sales, Facebook Fanpage, TikTok, Hotline/VoIP, Web Form, Email) — cái nào đã có tài khoản/API chính chủ, cái nào chưa?
- **Câu #11:** Làm rõ thực trạng **Đối tác dùng Pancake & 2.000–5.000 đơn/tháng (`A01`, `A03`, `P-O01–08`)**:
  - Con số 2.000–5.000 đơn là của **1 đối tác hay tổng các đối tác**? Đối tác dùng cụ thể **Pancake POS hay Pancake CRM / Botcake**?
  - Giai đoạn đầu đối tác chấp nhận cung cấp kết quả ở mức nào: **Không cung cấp (`NONE`)**, **Nhập tay số tổng (`SUMMARY`)**, **Gửi file Excel đối soát (`FILE`)**, hay **Cấp API đọc (`API_READ`)**?
- **Câu #12:** Ranh giới pháp lý dữ liệu người tiêu dùng cuối (`O06`, `P-O06`): Công ty chỉ xem báo cáo tổng hợp hiệu quả chiến dịch hay có đứng ra **trực tiếp nhắn tin CSKH / xử lý đơn hoàn cho người mua lẻ của đối tác** không?

### Nhánh 5 — Sales Pipeline, Giao việc nội bộ (`M16`) & Lịch vận hành (`W-O01–07`, `GAP-05–09`)
- **Câu #13:** Quy tắc phân chia Lead & SLA phản hồi đầu (`BR01`): Ai nhận lead mới (chia vòng tròn Round-robin, đổ vào hàng đợi chung để Sales tự giật Claim, hay Manager giao tay)? Thời gian phản hồi chuẩn (15 phút, 30 phút?) và khi quá hạn thì xử lý thế nào (thu hồi hay chỉ cảnh báo)?
- **Câu #14:** Luồng giao việc nội bộ (`M16` — `W-O01..W-O04`):
  - Khi nhận việc từ đồng nghiệp/sếp có cần nút **"Nhận / Từ chối có lý do" (Offer/Accept)** hay giao thẳng là phải làm?
  - Loại việc nào **bắt buộc qua bước Review/Duyệt kết quả** trước khi tính Done, loại việc nào nhân viên tự đánh dấu Done?
  - Việc cá nhân tự tạo trên "My Work": Cấp trên có được xem không hay mặc định **Private tuyệt đối**?
- **Câu #15:** Lịch làm việc tiêu chuẩn của công ty (`W-O03`, `H-O04`, `A.6`): Giờ hành chính mỗi ngày là 8 tiếng (480 phút) hay 7,5 tiếng? Có tính thứ Bảy (cả ngày / nửa ngày) vào hạn SLA và ngày phép không?

### Nhánh 6 — Tài chính, Ngân sách Ads (Media Pass-through) & Hoa hồng (`O07`, `BR04`, `H-O07`)
- **Câu #16:** Dòng tiền & Media Budget (`BR04`): Tiền chạy quảng cáo của khách là **khách tự nạp thẳng thẻ/tài khoản Ads của khách**, hay **chuyển qua tài khoản công ty để công ty nạp hộ / xuất hóa đơn**? (Rất quan trọng để tách doanh thu thực vs tiền thu hộ và tính thuế/biên lợi nhuận).
- **Câu #17:** Cơ chế ghi nhận thanh toán & Đối soát công nợ: Giai đoạn đầu nhập phiếu thu/ảnh chuyển khoản thủ công có người duyệt, hay cần tích hợp **VietQR / Webhook biến động số dư ngân hàng (Casso/SePay)**? Có tích hợp phần mềm kế toán (như MISA) ở Phase nào?
- **Câu #18:** Chính sách Hoa hồng (`O07`, `H-O06/07`): Tính hoa hồng theo **Doanh số ký (Contract Value)** hay **Thực thu không gồm tiền chạy Ads (Service Cash Collected)**? Khi khách hủy giữa chừng hoặc phải hoàn tiền thì có **thu hồi/khấu trừ hoa hồng (Clawback)** ở kỳ sau không? Ai hưởng hoa hồng (Sales chốt mới, Account tái ký, hay cả đội Media/Content theo KPI)?

### Nhánh 7 — Nhân sự, Chấm công, Lương & Chuyển đổi từ Excel (`H-O01–10`, `M22`)
- **Câu #19:** Thực trạng file Excel nhân sự hiện nay gồm những bảng/sheet nào (Hồ sơ hợp đồng, Theo dõi phép, Bảng chấm công, Bảng tính lương)? Các quy tắc nhạy cảm nhất về **cách chấm công** (chấm tay/Excel, Wi-Fi/GPS trên web/app, hay máy chấm công vân tay) và **công thức tính lương/OT/phạt đi muộn**?
- **Câu #20:** Chốt phạm vi triển khai `M22 HRM` theo từng đợt: Đợt đầu làm gọn `HR-A` (Hồ sơ + Hợp đồng + Nghỉ phép + Chấm công cơ bản thay Excel) và giữ tính lương `HR-C` ở Excel/Kế toán ngoài trước, hay bắt buộc hệ thống tính ra bảng lương hoàn chỉnh ngay Phase 1?

### Nhánh 8 — Bảo mật, Vận hành 24/7, Thứ tự Slice & Tiêu chí Nghiệm thu (`O08`, `GAP-10–14`)
- **Câu #21:** Yêu cầu chịu tải, bảo mật & vận hành (`O08`, `W-O04`, `H-O08`): Khung giờ hoạt động thực tế (chỉ giờ hành chính hay có trực inbox buổi tối/cuối tuần), ai là người giữ quyền tối cao xem dữ liệu tài chính/lương/PII khách hàng, và mức độ backup/khôi phục sự cố mong muốn?
- **Câu #22:** Chốt **Thứ tự ưu tiên các lát cắt (Release Roadmap)**: Bạn muốn chạy Pilot đầu tiên từ **luồng bán hàng & giữ khách (Lead → Deal → Thu tiền)** hay **luồng giao việc nội bộ (`SL01`)** hay **báo cáo kết quả đối tác (`SL08`)**?
- **Câu #23 (Chốt cuối buổi — Kỹ thuật Lớp 2):** Sau khi nhìn toàn bộ 22 câu nghiệp vụ đã chốt ở trên, xác nhận lại **Tech Stack cuối cùng** và cấu trúc cây thư mục Spec để sinh toàn bộ **Bộ tài liệu Lớp 1 + Lớp 2**.
