# Kiểm kê và khoảng trống

Nguồn hiện hành: Master1.9, hash ở README; số liệu phần “Kết quả ban đầu” bên dưới là snapshot lịch sử1.7; kết quả số lượng lấy từ evidence/inventory-validation.json.


## Cập nhật M21 ngày18/10/2026

Sau tích hợp1.8: 21 module, 735 ID ứng viên; 221 ID cũ chưa có owner giữ nguyên để review. M21 đã có owner domain, feature/UC/rule/test matrix và P-NFR; chưa có code/UAT đã chạy. Findings/evidence hiện hành thay số snapshot dưới cho báo cáo coverage mới.

Các khoảng trống M21 có P-O01–08 trong Master A.8: volume chính xác, authority/scope chia sẻ, sản phẩm/quyền Pancake, metric/tolerance, mapping/precedence, retention/audience, schedule/budget và exception rules. API thiếu chỉ chặn API; không ép đối tác cấp data để dùng nghiệp vụ công ty. Physical DDL/OpenAPI và người phụ trách thực vẫn cần chốt trước enable.

## Kết quả ban đầu — snapshot1.7 ngày16/10/2026

Parser đã quét toàn bộ 4.170 dòng, giữ occurrences và nội dung nguồn cho từng ID nhận diện. Có 20 module; 634 ID ứng viên trong các namespace đã cấu hình, trong đó 623 có vị trí định nghĩa ứng viên. Đây gồm yêu cầu, test, control và open decision, không phải 634 chức năng khác nhau.

Đã kiểm có định nghĩa ứng viên cho FR01–40, UC01–22, NFR01–12, W-F01–14, BR-W01–10, UC-W01–10 và W-T01–40. Đồng thời thu 98 khai báo entity/nhóm entity, 24 khai báo contract/phần contract và 450 đoạn ứng viên quy tắc chưa có ID. Các nhóm entity không tương đương số bảng cần xây.

## Findings cần đọc đúng

| Kết quả máy | Số lượng | Ý nghĩa thực tế |
|---|---:|---|
| Reference-only ID | 11 | Chưa tìm được định nghĩa bằng heuristic; không tự kết luận yêu cầu bị thiếu |
| ID có nhiều definition candidates | 12 | Có thể là bảng trace hoặc phần mô tả mở rộng; không tự là xung đột |
| ID chưa gán owner | 221 | Phần lớn test/control/open item cần phân công semantic; không bịa owner để đạt coverage |
| Mục không phải test chưa trích được test link | 291 | Same-row extraction không đủ phát hiện mọi link ở đoạn khác; cần hoàn thiện trace |
| Dòng shorthand cần review | 47 | Gồm W01/T01, nhiều module và legacy namespace; có cả false positives |

Reference-only hiện tại: WF01, WF06–14, U23. Master 3.14 nói rõ WF01–14 là mã trong báo cáo nguồn, nay dùng W-F01–14; trong khi WF cũng là namespace control khác. Vì vậy không tự alias mọi WFxx sang W-Fxx. U23 đã tách U23-R/U23-L theo capability; giữ việc đối chiếu tham chiếu cũ. Findings có line/text để review từng occurrence.

Các candidate trùng FR25/FR37/FR38 do định nghĩa và ma trận truy vết; UC-W08/09/10 còn có mô tả chi tiết; W-F01 còn xuất hiện trong phụ lục thay đổi. O01–05 còn xuất hiện dưới dạng mã nguồn Odoo ở Phụ lục H: cần phân loại nguồn tham khảo riêng với open decisions ở A.6, không gộp semantics chỉ vì cùng chuỗi. Registry giữ occurrences để phát hiện vấn đề này, chưa là canonical registry đã ký.

## Gap log hành động

| ID | Dữ kiện / gap | Quyết định đề nghị | Owner vai trò | Chặn gì |
|---|---|---|---|---|
| GAP-01 | Đã có AGENTS.md giai đoạn tài liệu (Documentation-Only); chưa có manifest hoặc repo mã nguồn ứng dụng | Giữ nguyên trạng thái chỉ viết tài liệu cho tới khi xong spec; xác nhận build mới/configure/hybrid và lập ADR trước khi scaffold code | Chủ dự án + Tech lead | Code production; không chặn spec |
| GAP-02 | Stack ở 2.8 là tham chiếu, chưa có repo triển khai | Ưu tiên đánh giá TS/React/NestJS/PostgreSQL nếu tự xây; phiên bản chưa pin | Tech lead | Build và test commands thật |
| GAP-03 | 221 ID chưa có owner và shorthand lịch sử | Review theo từng nhóm; mỗi requirement một accountable owner, nhiều consumer | BA + domain owner | Tuyên bố hoàn tất trace toàn hệ thống |
| GAP-04 | Dictionary logical, có grouped names như Task_Submissions / Reviews | Chốt tên bảng, field, constraints, indexes, policy và API schema cho SL01 trước migration | DB lead + BA | SL01 implementation-ready |
| GAP-05 | Team/reviewer/queue manager chưa chỉ định | Fixture giả cho review; trước pilot thật cấu hình W-O01/02 | Ops + Team lead | Giao việc/review live |
| GAP-06 | Visibility/retention/publish chưa cấu hình doanh nghiệp | Giữ private không mở cho cấp trên; chưa publish; xác nhận W-O04 | Owner + privacy | Dữ liệu cá nhân thật |
| GAP-07 | Offer timeout, lịch, reminder, review due chưa có policy active | Không bật timer tự động khi thiếu; UI báo chưa cấu hình | Ops | Automation theo lịch |
| GAP-08 | Chưa có kênh/account/API capability được xác minh | SL02 mock trước; live chỉ sau thử tài khoản được phép | Integration owner | Nhận/gửi live |
| GAP-09 | Nơi ghi task có thể đổi nếu dùng PMS | SL01 đề xuất CRM theo A.7; adapter PMS off; không dual-write | PM + Tech lead | Sync PMS |
| GAP-10 | Không có migration/test suite/run logs ứng dụng | Tạo sau ADR và physical contract; mọi ca CRM hiện Not Run | Dev + QA | Merge/enable/release |
| GAP-11 | Baseline P0 lớn hơn SL01 | SL01 là milestone kỹ thuật; giữ W-F08/09 và CRM P0 trong roadmap | PO | Tuyên bố hoàn tất P0 |
| GAP-12 | Ngân sách/nhân lực/hạ tầng/DR chưa chốt O05/O08/W-O07 | Ước tính sau spike, không hứa 90 ngày hoặc SLO đã đạt | Owner + Ops | Lịch go-live/SLA |
| GAP-13 | Endpoint start/block/update/result draft chưa đầy đủ ở 5.20 | Thiết kế command table trước sinh OpenAPI; không dùng PATCH status tự do | M16 BA + Tech | SL01 contract-ready |
| GAP-14 | P0 asset/comment có scan/retention; pilot text-only chỉ là tập con | Upload/comment UI và API off nếu chưa kiểm; giữ các ca tương ứng trong release tiếp | M16 + M20 | Tuyên bố W-F06 hoàn tất |
| GAP-15 | Ngưỡng chuyển `SOLO/PILOT -> TEAM` (`M23-F05`) và TTL Break-glass (`M23-F03`) mới ở mức đề xuất | Chốt số lượng người duyệt tối thiểu (đề xuất $\ge 3$ quản lý) và trần TTL Break-glass (đề xuất 2–4 giờ) trước khi đóng spec `SL00` | Owner/CEO + Security | Đóng spec chi tiết `M23` |
| GAP-16 | Chưa chốt danh mục chuẩn dùng chung (`M23-F11`) và khung `Quiet Hours` mặc định (`M23-F10`) | Chốt bộ lý do Won/Lost/Hold/Cancel, thuế/tiền tệ, mẫu ZNS/Email và lịch nghỉ lễ công ty | Ops Lead + BA | `M23-F10/11` ready |
| GAP-17 | Chưa chốt ngưỡng kích hoạt cảnh báo DLP (`M23-F08`) | Xác định ngưỡng số dòng/lần export/lỗi 403 bất thường trước khi bật cảnh báo tự động ở `SL07` | Security + Tech | Bật `M23-F08` |
| GAP-18 | Chưa chốt công nghệ Read Model/Search/Queue (`M24-F01/06/07/08`) và chu kỳ Archiving | Chọn sau khi hoàn tất ADR stack thật (`GAP-02`), đảm bảo tách 3 làn queue và `permission_version` invalidation | Tech Lead + SRE | Benchmark & code `M24` |
| GAP-M14-01 | Chưa chốt trần số ngày ủy nhiệm tự kích hoạt (`delegation_max_duration_days` tại `M14-F05`) | Áp dụng `Safe Default = 14 ngày` (vượt quá 14 ngày hoặc chứa quyền nhạy cảm bắt buộc `Branch Manager / Owner` duyệt trước khi `ACTIVE`) | Ops Lead + Owner | Chỉ chặn tự kích hoạt ủy nhiệm dài hạn |

## Phạm vi parser và kiểm semantic

Parser mở dải ID cùng prefix và shorthand slash dạng FR01/02; giữ reference và definition candidates riêng. Nó không giải nghĩa mọi bảng trace có W01/T01 hoặc mọi đoạn văn. Không suy “mục không có test link” là “không có test trong Master”. Không lấy consumer co-mention làm dependency chuẩn. Danh sách unnumbered có cả phụ lục lịch sử và Mermaid; review trước promote thành requirement.

NFR/controls xuyên module không bị xóa: owner PLATFORM là trách nhiệm kỹ thuật đề xuất, không phải module M21. Capability hiện chưa enable nên trạng thái test là Not Run; chỉ được ghi N/A khi có release profile và bằng chứng không có đường sử dụng. Hoãn tính năng không hoãn quyền/audit của tính năng đang chạy.

Thứ tự xử lý: SL01 quyền + semantics + physical schema → trace SL01 được review → test fixtures → code. Sau đó chuẩn hóa ownership/test links phần còn lại trước từng slice. Chưa cần chốt chính sách hoa hồng để thiết kế Task Core; thiếu policy hoa hồng vẫn chặn payout.

## Cập nhật HRM1.9

M22 đã có đặc tả28chức năng/16UC/24rules/48UAT/8NFR; các H-O01–10 ở Master A.9 là đầu vào triển khai còn mở. Đã xác nhận hiện trạng Excel, chưa nhận file thật; không giả đã làm sạch/import dữ liệu. Chưa chọn INTERNAL/EXTERNAL payroll, thiết bị hoặc bank adapter. Số liệu kiểm kê hiện hành lấy evidence/inventory-validation.json; snapshot1.8 phía trên là lịch sử.
