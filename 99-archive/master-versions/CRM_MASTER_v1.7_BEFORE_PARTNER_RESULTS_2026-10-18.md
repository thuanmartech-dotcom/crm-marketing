# TÀI LIỆU ĐẶC TẢ NGHIỆP VỤ VÀ KIẾN TRÚC HỆ THỐNG CRM

Dịch vụ marketing B2B và B2C

Master BRD & SRS  
Nền tảng dùng chung và gói nghiệp vụ mở rộng đa ngành

Phiên bản 1.7 — Hợp nhất quản lý công việc cá nhân, đội nhóm, tổ chức và dự án  
Ngày 16 tháng 10 năm 2026  
Đơn vị sử dụng: Chủ dự án CRM

**Bổ sung nghiên cứu ngày 16/10/2026 — CR-OMNI-20261016:** đối chiếu bản SRS Omnichannel mới với tài liệu Pancake, Zendesk, Chatwoot và chính sách kênh; bổ sung trực tiếp FR30–32/35/40, mục 3.12.12, 9.15 và Phụ lục G. Giữ phiên bản nền 1.6; đây là bổ sung thiết kế để review, chưa xác nhận PoC/UAT hoặc phê duyệt tham số doanh nghiệp. Báo cáo audit riêng tại `docs/OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md` không thay Master.

Phạm vi thiết kế: vận hành cá nhân ban đầu; mở rộng đến 30 Sales, 10 Marketing, ban giám đốc và 2 chi nhánh. Khối lượng đầu vào khoảng 100 lead và 50 khách hàng mỗi tháng, có khả năng tăng trưởng.

Mục đích: làm cơ sở thống nhất nghiệp vụ, lựa chọn giải pháp, lập backlog phát triển, kiểm thử nghiệm thu và dự toán đầu tư. Các ngưỡng KPI, SLA và chi phí được đề xuất để chủ dự án quyết định trước khi triển khai.

**TỆP MASTER DUY NHẤT:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.7. Đây là bản đặc tả BA đang dùng để thiết kế, triển khai và nghiệm thu. Danh mục 20 module ở đầu Chương 3; mỗi module có mã chức năng, lý do cần chức năng, điều kiện xử lý, màn hình/dữ liệu, trạng thái, quyền, liên kết và tiêu chí chấp nhận. Đây là 20 ranh giới nghiệp vụ logic, không phải 20 ứng dụng/dịch vụ phải xây.

**Thay đổi đã thực hiện:** 15 nhóm sửa đổi kỹ thuật/nghiệp vụ và hai hiệu chỉnh từ vòng kiểm định 1.5 đã được áp trực tiếp vào Chương 2–9; 17 nhóm ca kiểm thử bổ sung ở 9.14. Không còn yêu cầu người đọc tự copy patch ở phụ lục. Báo cáo kiểm định và các phiên bản trước chỉ giữ trong archive; không là quy tắc song song với Master này.

**Cách sử dụng:** bắt đầu từ danh mục module tại 3.0; đọc module cần triển khai, sau đó đối chiếu UC ởChương 4, dictionary/quan hệ ởChương 5, quyền ởChương 6 và test/gate ởChương 9. Các FR01–40/UC01–22 được giữ để truy vết; bổ sung UC-W01–10, W-F01–14, BR-W01–10 và W-T01–40 cho Work Management. Đọc 3.14 → 4.23 → 5.20 → 6.6 → 8.5 → 9.16 để triển khai miền công việc dùng chung. Các tham số doanh nghiệp chưa cung cấp nằm ở A.6; hệ thống có cách xử lý khi thiếu cấu hình, không để dev tự đặt số. Nội dung 1.7 là quyết định thiết kế BA; không đồng nghĩa phần mềm/DDL/provider/UAT đã chạy đạt hoặc chính sách doanh nghiệp đã được phê duyệt.

**Hợp nhất 1.7 — CR-WORK-20261016:** theo yêu cầu chủ dự án, đã tích hợp Task Core vào M16 và phần thân Chương 3–9, nguồn nghiên cứu ở Phụ lục H. My Work, giao/nhận việc, Team Board, review, gia hạn, checklist/subtask, dependency FS và mẫu/việc định kỳ cơ bản là P0 của miền công việc; capacity theo giờ/Gantt/portfolio nâng cao là P1. Quyền tích hợp tài liệu không đồng nghĩa ngân sách, lịch go-live, license hay UAT đã được duyệt. Master là nguồn chuẩn; báo cáo nghiên cứu giữ vai trò bằng chứng lịch sử.

## Kiểm soát tài liệu

| Hạng mục | Quy định |
| --- | --- |
| Chủ sở hữu | Chủ dự án CRM; CEO phê duyệt phạm vi và ngân sách khi triển khai đội ngũ. |
| Người đọc | CEO, quản lý kinh doanh, Marketing, BA, kỹ sư, QA, kế toán và người phụ trách bảo vệ dữ liệu. |
| Mốc dữ liệu | Thông tin do chủ dự án cung cấp trong trao đổi; nguồn công khai được tra cứu ngày 15–16/10/2026. |
| Trạng thái quyết định | Đặc tả thiết kế BA hiện hành 1.7; các thay đổi đã được hợp nhất vào mục áp dụng. Tham số kinh doanh/pháp lý được quản lý theo A.6 và Policy_Versions; thiếu cấu hình chặn đúng thao tác cần cấu hình, không chặn intake. Release phải qua 9.5/9.11; chưa có biên bản UAT đã chạy. |
| Quy ước | P0: bắt buộc cho MVP; P1: sau khi lõi ổn định; P2: chỉ kích hoạt khi có nhu cầu. FR: chức năng; BR: quy tắc; NFR: phi chức năng; UC: luồng; UAT: kiểm thử. |
| Thay đổi | Mỗi thay đổi có mã CR, lý do, chủ sở hữu, tác động dữ liệu/API/chi phí/UAT, người phê duyệt và phiên bản áp dụng. |

**Lịch sử phiên bản:** 1.2 bổ sung Omnichannel và nguồn CRM tham khảo; 1.3 hợp nhất báo cáo phản biện và ba chuyên đề CEO/CMO/CX, xử lý các mâu thuẫn và thu gọn phạm vi pilot. [Quyết định hợp nhất 1.3](#phu-luc-e). Bản 1.2 được lưu lịch sử; mọi chỉnh sửa tiếp theo cập nhật đúng tệp Master này và lịch sử phiên bản.

**Phiên bản 1.7 (16/10/2026):** CR-WORK-20261016 mở rộng M16 cho personal/internal/CRM/project work; giữ invariant Omnichannel của 1.6; đồng bộ use case, schema/API, quyền, KPI và 40 ca UAT.

## Mục lục

Điều hướng đến các chương và phụ lục bên dưới. Bản này hợp nhất nội dung nguồn và bổ sung đặc tả còn thiếu; đánh giá giữ/sửa/hoãn nằm tại Phụ lục A.

- [Chương 1 — Tổng quan chiến lược và mục tiêu dự án](#chuong-1)

- [Chương 2 — Kiến trúc tổng thể và hệ sinh thái tích hợp tại Việt Nam](#chuong-2)

- [Chương 3 — Đặc tả chi tiết các phân hệ nghiệp vụ](#chuong-3)

- [Chương 4 — Use cases và luồng quy trình nghiệp vụ](#chuong-4)

- [Chương 5 — Thiết kế cơ sở dữ liệu và từ điển dữ liệu](#chuong-5)

- [Chương 6 — Phân quyền bảo mật và tuân thủ pháp lý](#chuong-6)

- [Chương 7 — Yêu cầu phi chức năng](#chuong-7)

- [Chương 8 — Hệ thống báo cáo và BI Dashboard](#chuong-8)

- [Chương 9 — Lộ trình 90 ngày quản trị thay đổi và đào tạo](#chuong-9)

- [Chương 10 — Ngân sách đầu tư và hiệu quả đầu tư](#chuong-10)
- [Phụ lục A — Đánh giá tài liệu và lý do](#phu-luc-a)
- [Phụ lục B — Truy vết và mẫu vận hành](#phu-luc-b)
- [Phụ lục C — Nguồn công khai](#phu-luc-c)
- [Phụ lục D — Nghiên cứu CRM và quyết định tích hợp](#phu-luc-d)
- [Phụ lục E — Quyết định hợp nhất 1.3 và nguồn CEO/CMO/CX](#phu-luc-e)
- [Danh mục module và điều hướng BA](#danh-muc-module)
- [Phụ lục F — Các thay đổi đã áp dụng trong1.6](#phu-luc-f)

- [Phụ lục G — Nghiên cứu Pancake và Omnichannel ngày 16/10/2026](#phu-luc-g)
- [Quản lý công việc — đặc tả lõi 3.14](#work-core)
- [Phụ lục H — Nghiên cứu giao việc và quyết định hợp nhất 1.7](#phu-luc-h)

<a id="chuong-1"></a>

## CHƯƠNG 1 TỔNG QUAN CHIẾN LƯỢC VÀ MỤC TIÊU DỰ ÁN

### 1.1 Quyết định định hướng

Xây lõi quản lý quan hệ khách hàng cho agency dịch vụ marketing, ưu tiên quản trị từ lead đến hợp đồng, thực thu, bàn giao và gia hạn. B2B quản lý doanh nghiệp, nhiều người liên hệ và vai trò ra quyết định; B2C quản lý người mua cá nhân. Không ép hai mô hình dùng chung một phễu hoặc một bộ tiêu chí qualification.

Ở giai đoạn cá nhân, một người có thể kiêm nhiều vai trò nhưng vẫn ghi lại hành động theo nghiệp vụ. Khi có đội ngũ, kích hoạt phân quyền và phân tách phê duyệt mà không di chuyển khách hàng sang hệ thống mới. Thiết kế khoảng 45 tài khoản để dự trù 40 người đã nêu cộng quản lý và vai trò hỗ trợ; số 45 là giả định ngân sách, không phải số nhân sự được xác nhận.

Tầm nhìn CEO là đo lợi nhuận và dòng tiền theo khách hàng thay vì chỉ nhìn doanh thu ký hợp đồng. Tầm nhìn CMO là nối nguồn lead, chi phí thu hút và chất lượng doanh thu. Tầm nhìn CTO là lõi ổn định, mở rộng có kiểm soát và không để khách hàng của agency bị lẫn với dữ liệu người tiêu dùng do agency xử lý thay khách hàng. BA quản lý tính nhất quán giữa quy tắc, màn hình, dữ liệu và nghiệm thu.

### 1.2 Phạm vi và giả định cần kiểm chứng

| Mã | Nội dung | Cách xử lý |
| --- | --- | --- |
| A01 | 100 lead/tháng; 50 khách/tháng | Phân biệt khách đang phục vụ, khách mới và khách thanh toán. Không suy ra conversion 50% trước khi xác định cohort. |
| A02 | Cá nhân trước và đội ngũ sau | Pilot 1 người, sau đó 5 Sales và 2 Marketing, cuối cùng mở 2 chi nhánh. |
| A03 | Kênh chưa được chỉ định | Đề xuất website/form, email công ty, Zalo OA, Facebook Page và tổng đài; chưa coi là hệ thống đang dùng. |
| A04 | Dịch vụ chưa có bảng giá | Mô hình hỗ trợ retainer, dự án trọn gói, sản xuất nội dung và phí quản lý quảng cáo. |
| A05 | Chưa có CSKH/kế toán/triển khai | Định nghĩa vai trò nghiệp vụ; CEO chỉ định người kiêm nhiệm trước go-live. |
| A06 | Chưa có ngân sách và biên lợi nhuận | Dùng kịch bản minh họa ở chương 10; không cam kết ROI. |

### 1.3 Bài toán và kết quả mong đợi

Ba ưu tiên đề xuất là tránh bỏ sót lead, bảo toàn lịch sử khách khi thay người phụ trách, và kiểm soát hợp đồng đến thực thu đến gia hạn. Đây là giả thuyết nghiệp vụ cần kiểm chứng qua phỏng vấn; chưa phải các nỗi đau được chủ dự án xác nhận.

| Mã BR | Vấn đề cần kiểm soát | Yêu cầu và bằng chứng |
| --- | --- | --- |
| BR01 | Lead không có người xử lý | Tất cả lead hợp lệ có owner hoặc hàng đợi; cảnh báo quá SLA với timestamp. |
| BR02 | Khách phụ thuộc Sales | Lịch sử thuộc tổ chức; bàn giao owner không xóa hoạt động cũ; nguồn Zalo cá nhân khai báo thủ công. |
| BR03 | Bán sai phạm vi dịch vụ | Báo giá khóa phiên bản, số vòng sửa, đầu ra, điều kiện nghiệm thu và phần không bao gồm. |
| BR04 | Lẫn phí dịch vụ và media budget | Dòng hàng có loại SERVICE, MEDIA_PASS_THROUGH, PRODUCTION; tính hoa hồng theo cơ sở được phê duyệt. |
| BR05 | Gián đoạn tái ký | Nhắc theo ngày quyết định/notice deadline và kỳ hợp đồng; 45/30/15 ngày chỉ là template cấu hình. Gắn success review, health và người chịu trách nhiệm; không áp tự động cho mọi one-off. |
| BR06 | Mở rộng ngành làm hỏng lõi | Gói ngành có namespace, phiên bản schema và workflow riêng; có kiểm thử hồi quy lõi. |

### 1.4 Ma trận KPI

Baseline được thu trong 14 ngày đầu; mục tiêu dưới đây là đề xuất pilot. Nếu mẫu dưới 30 quan sát, hiển thị cả tử số/mẫu số và không xếp hạng nhân viên bằng tỷ lệ đơn lẻ.

| KPI | Công thức | Mục tiêu và chủ sở hữu |
| --- | --- | --- |
| SLA phản hồi đầu | Lead có lần tiếp cận hợp lệ trong hạn / lead đến hạn | ≥95% trong giờ làm việc; quản lý Sales; đo p50/p95 cùng tỷ lệ. |
| Conversion cohort | Lead mới trong tháng trở thành khách trả tiền trong 90 ngày / lead hợp lệ cùng cohort | Đo baseline trước đặt mức tăng; CMO và Sales cùng ký định nghĩa. |
| Win rate | Deal Won / (Won + Lost) theo ngày đóng | Không dùng deal còn mở ở mẫu số; Sales Director chịu trách nhiệm. |
| CAC | Chi phí thu hút phân bổ / số khách mới trả tiền | Tách paid CAC và fully loaded CAC; chưa có dữ liệu thì hiển thị chưa đủ dữ liệu. |
| LTV đóng góp | Tổng doanh thu dịch vụ trừ chi phí trực tiếp trong vòng đời quan sát của cohort / số khách cohort | Không dùng ngân sách quảng cáo thu hộ; chỉ dự báo sau đủ dữ liệu giữ chân. |
| Tái ký | Hợp đồng tái ký / hợp đồng đến hạn đủ điều kiện | Đo theo số và giá trị; nêu rõ loại trừ hợp đồng một lần. |
| DSO | Phải thu bình quân / doanh thu bán chịu kỳ × số ngày kỳ | Kế toán; kèm tuổi nợ 0–30/31–60/61–90/>90 ngày. |
| Sử dụng CRM | Deal hoạt động có owner và next action đúng hạn / tổng deal hoạt động | ≥95% pilot, hướng tới 100%; loại trừ sự cố đã ghi nhận. |

### 1.5 Nghiên cứu hành vi và cách kiểm chứng

Với dịch vụ marketing, niềm tin được hình thành qua case study, năng lực thực thi, minh bạch số liệu và phản hồi nhanh. B2B thường cần nhiều người duyệt ngân sách, phạm vi và hợp đồng; B2C thường cần gói dễ hiểu, giá rõ và lịch hẹn thuận tiện. Đây là giả thuyết thiết kế, không phải kết quả khảo sát đại diện người tiêu dùng Việt Nam.

Trong 14 ngày, phỏng vấn 5 khách B2B và 5 khách B2C, rà 20 cuộc trao đổi có quyền sử dụng và 10 deal thắng/thua gần nhất. Ghi kênh đầu tiên, kênh ưu tiên, thời gian ra quyết định, lý do mất, mức tin tưởng và trở ngại thanh toán. Không suy rộng kết quả mẫu nhỏ thành tỷ lệ toàn thị trường.

Kiểm chứng ba thử nghiệm: form ngắn so với form đầy đủ; phản hồi 15 phút so với baseline; báo giá có lộ trình và tiêu chí nghiệm thu so với mẫu cũ. Chia ngẫu nhiên khi khả thi, giữ nguyên định nghĩa khách mới, không hứa mức tăng doanh số trước khi đo.

### 1.6 Ranh giới sản phẩm

MVP đi hết hành trình: hồ sơ → nhu cầu → deal → brief/báo giá/SOW → hợp đồng/kỳ thu → tiền/đối soát → bàn giao → đầu ra/nghiệm thu → ticket/khắc phục → gia hạn phù hợp. Một nguồn lead và một kênh giao tiếp trước. Có thể nhập và đối soát tài chính thủ công có kiểm soát; không bắt tự động hóa hết để đảm bảo đúng dữ liệu.

P0 giữ quyền/scope, source/consent, next action, revision/approval, tiền/phân bổ, evidence, recovery cơ bản, báo cáo ít chỉ số và backup/restore. P1 theo nhu cầu gồm tích hợp kế toán/PMS/calendar, spend/capacity, referral, health/NPS và một vòng phản hồi CRM→Meta. P2 gồm loyalty/Mini App, strategy editor đầy đủ, experiment engine, multi-touch, predictive scoring, scorecard nhân sự và AI tự hành.

Mỗi FR bên dưới có lý do, liên kết và điều kiện mở. Feature ở P1/P2 vẫn có trong thiết kế đích đến nhưng không được tính vào cam kết MVP/90 ngày. Chọn giải pháp cấu hình hoặc hybrid nhẹ trước khi tự xây toàn bộ; ngân sách và PoC quyết định nền tảng theo Chương 10.

<a id="chuong-2"></a>

## CHƯƠNG 2 KIẾN TRÚC TỔNG THỂ VÀ HỆ SINH THÁI TÍCH HỢP TẠI VIỆT NAM

### 2.1 Kiến trúc triển khai ban đầu

Đề xuất ứng dụng web responsive/PWA, backend modular monolith và PostgreSQL managed; worker bất đồng bộ xử lý webhook, lịch nhắc và tác vụ tích hợp. Dùng object storage cho hợp đồng và ghi âm, hàng đợi bền vững cho sự kiện. Chưa cần Kafka, Kubernetes hoặc lakehouse với 100 lead/tháng. Backup, quyền truy cập và tính đúng đắn tài chính cần có ngay dù lưu lượng thấp.

Nguồn sự thật phân theo miền: CRM sở hữu lead/deal/hoạt động; ERP sở hữu chứng từ kế toán và công nợ đã hạch toán; ngân hàng/provider sở hữu giao dịch thanh toán xác thực; hệ thống quản lý dự án sở hữu tác vụ giao hàng nếu đã tích hợp. Kho BI là bản chiếu phân tích, không thay thế sổ nghiệp vụ giao dịch.

### 2.2 Sơ đồ kiến trúc và ranh giới microservices

Sơ đồ dưới thể hiện hướng luồng dữ liệu. Các khối nghiệp vụ có thể cùng chạy trong một backend khi pilot; ranh giới API và sự kiện được giữ để tách dịch vụ khi tăng tải.

```mermaid
flowchart TB
  UI[Web PWA và các kênh được cấp quyền] --> GW[Gateway xác thực và kiểm scope]
  GW --> CORE[Lõi Contact Lead Deal Activity Ticket]
  GW --> PACK[Gói marketing_services]
  GW --> FIN[Tài chính và đối soát]
  CORE --> DB[(PostgreSQL)]
  PACK --> DB
  FIN --> DB
  DB --> OUTBOX[Transactional Outbox]
  OUTBOX --> QUEUE[Queue và Integration Workers]
  QUEUE --> EXT[OA Meta VoIP Ngân hàng ERP]
  DB --> BI[Read models và BI]
  DB --> AI[AI Gateway có ACL và duyệt của người]
  PACK --> ASSET[Object storage có version và ACL]
  POLICY[Consent Audit Tenant Workspace Policy] -.-> GW
  POLICY -.-> QUEUE
  POLICY -.-> AI
```

Hình 1. Kiến trúc logic; Marketing Services Pack là gói nghiệp vụ agency, không sở hữu hồ sơ khách hàng độc lập.

| Miền | Trách nhiệm | Điều kiện tách dịch vụ |
| --- | --- | --- |
| Identity và Consent | Định danh, policy, chứng cứ đồng ý | Dùng chung nhiều sản phẩm, cần vòng phát hành riêng. |
| Lead và Sales | Owner, pipeline, báo giá | Nhóm phát triển riêng và yêu cầu scale độc lập đã đo được. |
| Integration | Token, webhook, retry, mapping | Ưu tiên tách worker sớm để lỗi đối tác không chặn giao diện. |
| Finance | Phân bổ thanh toán, ledger hoa hồng | Cần kiểm soát giao dịch độc lập; giữ một owner ghi sổ. |
| AI Gateway | Redaction, model routing, quota | Không cho mô hình gọi SQL hoặc API tùy ý. |

### 2.3 Lõi dùng chung và gói ngành

`tenant_id` cô lập tổ chức; `workspace_id` phân phạm vi AGENCY/CLIENT; `branch_id` phân trách nhiệm vận hành; `legal_entity_id` xác định pháp nhân ký/hạch toán/nhận tiền. Bốn khái niệm này không thay nhau. Mỗi tenant có workspace AGENCY ngay từ pilot; workspace CLIENT chỉ xử lý dữ liệu theo phạm vi khách ủy quyền, không tự chuyển người tiêu dùng thành khách bán dịch vụ của agency.

Dữ liệu scoped dùng `workspace_id NOT NULL`. Danh mục cấp tenant được khai báo riêng. Hồ sơ Account mua dịch vụ của agency, hợp đồng và tài chính nội bộ thường thuộc AGENCY workspace; dữ liệu delivery/người tiêu dùng của khách có thể thuộc CLIENT workspace. Liên kết qua scope chỉ qua quan hệ được khai báo và kiểm quyền, không tự cấp quyền đọc toàn bộ hợp đồng/commission. Một pháp nhân/chi nhánh mặc định đủ cho pilot khi thực tế chỉ có một; không xây multi-company engine nếu chưa cần.

Core gồm Contact, Account, Lead, Deal, Activity, Ticket, Consent và Audit. Gói marketing_services bổ sung Brief, SOW, Deliverable, Acceptance, Retainer và CampaignAsset. Ngành bán lẻ bổ sung SKU/Inventory/Return; nha khoa bổ sung lịch điều trị và hồ sơ chuyên ngành với kiểm soát riêng. Không thêm hàng trăm cột tùy chọn vào Contacts cho tất cả ngành.

| Thành phần mở rộng | Cơ chế | Điều kiện an toàn |
| --- | --- | --- |
| Custom fields | field_definition theo tenant + entity + namespace | Kiểu dữ liệu, giới hạn, dữ liệu nhạy cảm, kiểm tra server; index chỉ trường được duyệt. |
| Workflow | Định nghĩa có version, trạng thái và transition | Instance cũ giữ version cũ; chuyển phiên bản bằng migration có kiểm thử. |
| Industry pack | Manifest tên, version, dependencies, migrations | Namespace marketing.*, retail.*; không được ghi trực tiếp bảng của pack khác. |
| Feature flag | Theo tenant và vai trò | Tắt tính năng không xóa dữ liệu; API vẫn kiểm quyền. |
| Khách nhiều ngành | Contact có liên kết business_line | Chia sẻ theo mục đích và quyền; không tự chia sẻ consent marketing giữa các ngành. |

Ví dụ thêm ngành giáo dục: đăng ký education.v1, thêm enrollment và course, tạo pipeline tư vấn riêng. Bản ghi Contact vẫn dùng core nhưng enrollment FK có tenant_id; không thay enum stage của pipeline marketing đang chạy. Bộ kiểm thử phải chứng minh một sales giáo dục không thấy SOW của agency nếu chưa được cấp quyền.

### 2.4 Danh mục tích hợp đề xuất

| Hệ thống | Vai trò và dữ liệu | Giai đoạn và điều kiện |
| --- | --- | --- |
| Website/form + email công ty | Thu lead có UTM, consent và nguồn; gửi thư báo giá | P0; chống spam, email domain được cấu hình, mailbox quyền công ty. |
| Zalo OA và ZBS Template Message | Inbox, nhắc lịch, thông báo giao dịch theo mẫu hợp lệ | P0/P1; OA, App, quyền và ngân sách phải được kiểm tra. Tài liệu 2026 dùng ZBS Account [S03](#s03). |
| Zalo Mini App | Đặt lịch, xem tiến độ, điểm và giới thiệu | P2; chỉ xây sau khi chứng minh khách sẽ sử dụng. Không mặc định được lấy số điện thoại. |
| Zalo cá nhân | Nguồn khách do Sales khai báo; chuyển tương tác sang kênh công ty | Không cam kết đọc đồng loạt chat cá nhân. Tích hợp không chính thức không nằm trong baseline. |
| Facebook Page và Lead Ads | Form lead, hội thoại và campaign ID | P1; app review, scope, token và chính sách gửi tin phải được xác minh theo API hiện hành. |
| TikTok Shop và Shopee | Đơn/sản phẩm của khách thuê agency khi có ủy quyền | P2, pack thương mại điện tử riêng; không trộn GMV của khách với doanh thu agency [S07](#s07), [S08](#s08). |
| Stringee hoặc OmiCall | Click-to-call, call ID, trạng thái, ghi âm | P1; chọn qua PoC về webhook, masking, chất lượng và chi phí; không mua cả hai mặc định. |
| Ngân hàng hoặc provider được cấp quyền | Giao dịch nhận tiền, mã đối soát | P0 nhập sao kê có kiểm soát; P1 API. VietQR chỉ hỗ trợ khởi tạo chuyển khoản [S04](#s04). |
| MISA AMIS Kế toán + meInvoice | Khách hàng, hóa đơn, chứng từ và trạng thái công nợ | P1; kiểm đúng API từng sản phẩm, không dùng tài liệu AMIS CRM thay cho kế toán [S05](#s05), [S06](#s06). |
| Công cụ quản lý dự án hiện có | Dự án, task, milestone, người phụ trách và nghiệm thu | Task Core CRM là nguồn chuẩn mặc định ở pilot. Connector PMS ngoài P1; project dùng PMS có source authority rõ theo 5.20/UC-W10, CRM là giao diện/projection; không hai master ghi đè. |
| GHN/GHTK | Giao POSM, quà hoặc vật phẩm | P2 chỉ khi có giao vận thực; không bắt buộc cho dịch vụ số. |

<a id="module-m19"></a>

#### ĐẶC TẢ MODULE M19 — Tích hợp và quản trị adapter

**Mục đích, tác nhân và phạm vi:** Integration owner nối tài khoản doanh nghiệp, vận hành webhook/sync và xử lý gap; Operator thao tác health/replay trong quyền hỗ trợ, không mặc nhiên đọc body hoặc gửi khách. M19 cung cấp capability và event bền vững cho module nghiệp vụ, không thay nguồn sự thật ngân hàng/ERP/provider. Pilot ưu tiên một kênh; connector chưa được cấp quyền vẫn có quy trình thủ công với provenance.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M19-F01 Đăng ký connector | Provider/app/account dự kiến, workspace owner | Nếu account nguồn đã có owner active trong namespace thì conflict; nhiều inbox dùng chung connection, không tự clone sang khách khác | Connection pending; FR30, SEC02 | Một tài khoản nguồn có nơi quản lý rõ ràng, không nhập chéo khách. |
| M19-F02 Cấp/reconnect quyền | Authorization attempt, callback, actor/session | Callback phải khớp binding và dùng một lần; server xác minh external account/scopes; sai thì không thay token cũ | Secret ref/verified scopes; SEC01 | Token phải gắn đúng người khởi tạo, workspace và tài khoản được cấp. |
| M19-F03 Khai báo capability | Account/API version và evidence test | receive/send/history/receipt/edit/delete tách verified/unsupported/pending/unknown; chưa verified không hứa chức năng | UI/feature gate; FR30/38 | Chỉ cam kết chức năng API và tài khoản thực sự cho phép. |
| M19-F04 Ingest | Chữ ký, subscription/account, event key/payload | Scope từ mapping server; lưu bền vững trước ACK; schema lạ quarantine; trùng không lặp effect | Inbound_Events→worker; FR33 | Không mất sự kiện khi trả ACK hoặc tạo hiệu ứng trùng khi retry. |
| M19-F05 Dispatch | Intent đã commit, quyền/policy hiện tại | Recheck trước gửi; không giữ DB lock khi gọi mạng; timeout bất định không retry mù POST có tác động | Attempts/receipt; FR34, M03/M20 | Gửi đúng policy hiện tại mà không giữ khóa dữ liệu chờ mạng. |
| M19-F06 Đồng bộ/phục hồi | Checkpoint, delta/page, gap | Advance cursor sau xử lý bền vững cả page; historical không phát sinh automation mới; không có history thì báo khoảng thiếu | Sync_Checkpoints/run; UC21 | Khôi phục dữ liệu thiếu và biết phần không thể phục hồi. |
| M19-F07 Health/retry | 401/403/429/timeout/backlog | Tôn trọng Retry-After/backoff/TTL; lỗi quyền dừng/reconnect, schema vào DLQ; cảnh báo có owner | Degraded/runbook/queue; FR38 | Lỗi kết nối được phát hiện và có người xử lý. |
| M19-F08 Replay/rotate | Range, dry-run, reason hoặc secret rotation | Replay qua cùng dedup/scope; không bypass consent; refresh có lock; external media fetch qua egress policy | Audit/reconcile; SEC04, UC21 | Sửa đồng bộ có kiểm soát, không bypass quyền hoặc lộ credential. |

**Màn hình và trường:** Connection detail bắt buộc provider, namespace/app khi áp dụng, external account xác minh, workspace owner, connection owner/backup và API version. Token chỉ hiển thị trạng thái/expiry, không plaintext. Capabilities có checked_at/evidence; sync hiện last success, cursor metadata, coverage_from/to, gap reason và pending age. DLQ hiển thị error code đã redact, operation range và dry-run effect; mở payload cần support grant TTL riêng. Replay bắt buộc reason, scope, range và reviewer theo rủi ro, không có nút “replay mọi thứ” không giới hạn.

**Commands và trạng thái:** `authorize`, `verify-capability`, `activate`, `refresh`, `pause-send`, `disconnect`, `reconcile`, `replay-range`. Connection pending_authorization→active→degraded→reauthorization_required→disconnected theo sự kiện; state active chỉ sau account/scopes/capability đạt điều kiện. Reconnect không chuyển owner workspace. Muốn chuyển account phải pause ingest/send, đánh giá pending intent, cursor và revoke grant cũ; lịch sử giữ scope gốc. Refresh token không được hai worker ghi đè nhau.

**Quyền và ngoại lệ:** Admin connector không tự đọc nội dung/ghi sổ; Finance mới xác nhận match thu tiền, steward mới duyệt merge. Credential dùng scope tối thiểu và vault, worker role tách migration. Sai chữ ký reject; DB không lưu được không ACK thành công; provider outage giữ backlog có TTL. API không hỗ trợ tra cứu thì unknown_outcome có xử lý thủ công/evidence, không báo đã gửi. Fetch file kiểm host/IP/redirect/token, giới hạn byte/time và quét nội dung trước publish.

**Nghiệm thu:** M19-AC01 — callback sai/replay và cùng account hai workspace bị chặn; FR30, UC17/21, Channel_Connections, SEC-U01/02. M19-AC02 — restart/replay/revoke/timeout không mất hoặc nhân effect, không retry mù; FR33/34/38, UC19/21, Inbound_Events/Outbox/Send_Attempts, U01/U15. M19-AC03 — private URL/redirect bị chặn, gap hiện thật; FR38/40, UC21, Message_Attachments/Sync_Checkpoints, SEC-U04.

### 2.5 Hợp đồng kỹ thuật tích hợp

Webhook phải xác minh chữ ký theo nhà cung cấp, kiểm timestamp/replay khi được hỗ trợ, ghi durable inbox trước khi trả 2xx. Khóa chống trùng là tenant + connector + external_event_id. Nếu đối tác không cung cấp ID ổn định, tạo hash có tài liệu và kiểm rủi ro va chạm; không dùng riêng thời điểm nhận làm khóa.

Sau commit nghiệp vụ, transactional outbox phát event. Consumer xử lý ít nhất một lần nhưng tác động nghiệp vụ chỉ một lần bằng unique key và transaction. Retry lỗi tạm thời với backoff 1/5/15/60 phút có jitter; lỗi quyền hoặc schema vào hàng đợi xử lý. Không retry mù POST thu tiền, phát hóa đơn hoặc gửi tin có phí khi chưa biết kết quả.

Event nội bộ gồm event_id, tenant_id, aggregate_type, aggregate_id, aggregate_version, occurred_at UTC, schema_version, correlation_id và payload tối thiểu. Không đưa mật khẩu, access token hoặc toàn bộ nội dung chat vào log. Sự kiện đến muộn không được làm trạng thái Paid quay về Pending.

| API nội bộ mẫu | Kiểm tra bắt buộc | Kết quả và lỗi |
| --- | --- | --- |
| POST /v1/leads | Tenant từ token, nguồn, contact method, consent purpose | 201 hoặc trả kết quả cũ theo Idempotency-Key; 422 dữ liệu sai. |
| POST /v1/leads/{id}/claim | RBAC, hàng đợi, capacity, expected_version | 200 một owner; 409 khi người khác đã nhận. |
| POST /v1/quotes/{id}/approve | Quyền, giá, biên lợi nhuận, version | 200 khóa snapshot; 403 nếu tự duyệt ngoài hạn mức. |
| POST /v1/payments/{id}/allocate | Quyền allocate, confirmed payment và nghĩa vụ thu hợp lệ; tenant/workspace/legal entity/currency/party, số dư và expected_version; invoice không là tiền điều kiện | Transaction atomic; 409 khi balance/version thay đổi, 403 trái quyền; invoice mapping là nghiệp vụ riêng. |
| POST /v1/consents/revoke | Xác thực chủ thể phù hợp, purpose và channel | Ghi event rồi chặn gửi; 202 nếu còn tác vụ lan truyền. |

### 2.6 Quản trị credential và lỗi đối tác

Token giữ trong secret manager, mỗi tenant và connector có scope tối thiểu; UI chỉ hiện trạng thái kết nối. Refresh token đồng bộ bằng lock để tránh nhiều worker ghi đè. Khi token hết hạn, connector chuyển Degraded, báo người phụ trách, lưu hàng đợi và cho phép nhập thủ công với provenance. Theo dõi quota, thời gian hết hạn, lỗi 401/403/429, backlog, duplicate và reconciliation mismatch.

> **Authorization binding:** Khởi tạo/reconnect chỉ bởi principal có quyền quản trị connection trong scope đích. Authorization attempt lưu server-side actor/session, tenant/workspace, connection, provider, expiry và trạng thái dùng một lần. Callback kiểm CSRF binding và provider; redirect đích được cấu hình trước. Dùng PKCE S256 khi flow/provider hỗ trợ theo hợp đồng đã xác minh; không fallback âm thầm bỏ kiểm bảo vệ. Sau exchange, server đọc external account/scopes từ provider và so với account dự kiến trước Active. Callback sai/đã dùng/hết hạn bị từ chối; reconnect không tự đổi chủ workspace. Không tin tenant/workspace/account do query hoặc form khách gửi.

### 2.7 Kiến trúc Omnichannel hợp nhất năm kênh

**Quyết định bổ sung ngày 15/10/2026:** CRM là điểm làm việc và hồ sơ nghiệp vụ thống nhất cho Zalo, Facebook, TikTok, Web Form và Email. “Toàn bộ” có nghĩa là toàn bộ dữ liệu thuộc phạm vi tài khoản doanh nghiệp được ủy quyền, được API cho phép và được chính sách lưu giữ cho phép. Không cam kết lấy lịch sử vô hạn, tin nhắn tài khoản cá nhân hoặc dữ liệu nền tảng chưa cấp quyền. Mỗi connector phải công bố khoảng lịch sử đồng bộ, thời điểm cập nhật cuối và phần dữ liệu còn thiếu.

Một Contact có thể có nhiều danh tính kênh, nhiều cuộc hội thoại và nhiều vai trò tại các Account. Hợp nhất hồ sơ không có nghĩa trộn các luồng chat thành một thread hoặc công khai nội dung cho mọi nhân viên. CRM quản lý Contact, Account, Lead, Deal, quyền và consent; nền tảng kênh vẫn là nguồn xác nhận việc tiếp nhận/phát tin. Nếu dùng Chatwoot, chỉ chọn một hệ thống làm chủ trạng thái hội thoại, không cho hai bộ router cùng phân công.

```mermaid
flowchart LR
  Z[Zalo OA] --> A[Adapters theo tài khoản]
  F[Facebook Page] --> A
  T[TikTok Business Messaging] --> A
  W[Web Form] --> A
  E[Gmail hoặc Microsoft 365] --> A
  A --> V[Xác thực và durable event inbox]
  V --> N[Chuẩn hóa và chống trùng]
  N --> I[Identity theo phạm vi]
  I --> C[Contact 360 và Conversation]
  C --> R[Routing và SLA]
  R --> U[Unified Inbox của CRM]
  U --> P[Quyền và chính sách gửi]
  P --> O[Transactional Outbox]
  O --> S[Worker gửi theo kênh]
  S --> A
  V --> D[Retry DLQ và đối soát]
  D --> N
```

#### Ma trận khả năng và điều kiện kết nối

| Kênh | Dữ liệu đưa vào | Gửi từ CRM | Điều kiện và giới hạn phải kiểm chứng trước cam kết |
| --- | --- | --- | --- |
| Zalo OA | Sự kiện/tin nhắn OA được API cấp; UID trong phạm vi OA; metadata được phép | Qua OA API hoặc template phù hợp sản phẩm/chính sách hiện hành | OA, app và quyền hợp lệ; kiểm tra hạn mức, cửa sổ gửi, loại nội dung, lịch sử, sự kiện thu hồi. Zalo cá nhân không được coi là OA API [R10](#r10) |
| Facebook | Page Messenger; Lead Ads là feed riêng nếu được cấp; comment là loại tương tác riêng | Page Messenger qua quyền và điều kiện gửi tương ứng | Quyền Page/app review, token, webhook; định danh có phạm vi Page. Lead Ads không tự tạo quyền nhắn Messenger; ngoài cửa sổ phải có cơ chế hợp lệ [R11](#r11) |
| TikTok | DM qua Business Messaging API cho Business Account được ủy quyền; Lead Gen và Shop qua connector khác | Chỉ khi account/app thực sự được cấp quyền messaging | API chính thức có tồn tại; chưa xác nhận tài khoản này đủ điều kiện tại Việt Nam. Không lấy API Shop thay cho DM, không suy luận Ads account có quyền inbox [R12](#r12) |
| Web Form | Submission, trường khách tự khai, consent version, UTM/referrer được phép | Form không phải kênh chat hai chiều; tạo task hoặc trả lời bằng email/kênh đã xác minh | Chống spam, kiểm tra server, submission ID; email nhập tay chưa phải email đã xác minh; không tự thêm vào marketing audience |
| Email | Mailbox doanh nghiệp được cấp quyền; thư, thread, attachment theo phạm vi cấu hình | Gmail API/Graph hoặc SMTP OAuth được phê duyệt | Watch/subscription phải gia hạn; webhook có thể chỉ chứa thông báo thay đổi, cần fetch nội dung; shared mailbox cần quyền thích hợp [R13](#r13)[R14](#r14) |

Zalo cá nhân: quy trình chuyển sang OA bằng liên kết/QR, ghi nhận hoạt động thủ công có nguồn và consent; nếu đánh giá nhà cung cấp bridge phải kiểm chứng quyền chính thức và điều khoản, không dùng cookie/session cá nhân như nền móng hệ thống. Với TikTok chưa được duyệt, nhân viên xử lý trong giao diện chính thức, CRM ghi task và đường dẫn tham chiếu; hiển thị “chưa kết nối hai chiều”. Không dùng fallback để giả lập trạng thái đã gửi.

#### Hợp đồng adapter và vòng đời kết nối

Mỗi adapter công bố `capabilities`: receive, send, attachments, delivery_receipt, read_receipt, history_backfill, edit, delete, native_reply_echo. Trạng thái từng capability là `verified`, `unsupported`, `pending_approval` hoặc `unknown`, kèm ngày test, phiên bản API và tài khoản thử. UI dựa trên capability thực tế; không hiện nút reply cho connector chỉ nhận lead.

Lifecycle: `pending_authorization → active → degraded → reauthorization_required → disconnected`. Khi token hết hạn, dừng gửi và cảnh báo người phụ trách; giữ hàng đợi có TTL. Sau cấp quyền lại, kiểm tra lại policy tại thời điểm gửi; không xả hàng loạt tin marketing đã hết hiệu lực. Thu hồi tài khoản không tự xóa dữ liệu cần lưu hợp pháp, nhưng chặn truy cập mới ngay.

Inbound: xác minh theo cơ chế nhà cung cấp, giới hạn kích thước, ghi event bền vững rồi mới ACK trong timeout của kênh. Nếu ghi thất bại, trả lỗi để retry; không ACK trước lưu. Worker parse, chuẩn hóa, deduplicate, resolve identity, cập nhật conversation và tạo routing event trong transaction. Event chứa `tenant_id`, `workspace_id`, `connection_id`, `provider_event_id`, `provider_message_id`, `occurred_at`, `received_at`, `schema_version`, `correlation_id`, `payload_ref`. Tenant/workspace lấy từ connection được xác thực, không tin giá trị do payload khách gửi.

Outbound: lưu ý định gửi và outbox trong cùng transaction; worker kiểm tra quyền, consent/purpose, loại tin, cửa sổ gửi và hạn mức. Mỗi ý định có `client_request_id` duy nhất. Provider nhận thành công mới ghi `provider_message_id`; trạng thái `accepted` không tương đương `delivered` hay `read`. Nếu timeout sau khi provider có thể đã nhận, chuyển `unknown_outcome`; tra cứu/đối soát nếu API hỗ trợ, không retry mù. Không tuyên bố exactly-once xuyên nền tảng; mục tiêu là at-least-once inbound với xử lý idempotent và kiểm soát gửi trùng outbound.

Retry có exponential backoff, jitter, tôn trọng Retry-After, giới hạn tổng thời gian; lỗi quyền/policy không retry như lỗi mạng. DLQ có mã lỗi đã làm sạch, owner, lần thử, nút replay có quyền và audit. Backfill dùng cursor/checkpoint, cùng pipeline chống trùng với realtime, không kích hoạt chiến dịch hoặc SLA mới cho dữ liệu lịch sử. Gmail cần watch renewal và history sync; Microsoft cần quản lý subscription lifecycle. Chi tiết thời hạn lấy từ tài liệu/version đang triển khai, không hardcode chung cho mọi kênh.

> Webhook resolver kiểm chữ ký và account/subscription nằm trong connection mapping được sở hữu; không dùng riêng callback URL hoặc connection ID do người gọi tự khai để quyết định workspace. Chuyển mapping không làm raw event cũ thay workspace; event giữ scope nguồn ban đầu.

> **Error envelope:** API không trả raw PostgreSQL DETAIL, tên constraint, giá trị field, ID hoặc số lượng bản ghi ngoài scope qua lỗi unique/FK. Với tài nguyên không được phép xác nhận tồn tại, dùng phản hồi nhất quán theo chính sách404/403 đã chốt; thông báo account nguồn đã được quản lý không nêu workspace/người sở hữu không có quyền xem. Log kỹ thuật chứa diagnostic được hạn chế theo quyền hỗ trợ và redact. Các key/FK vẫn kiểm toàn vẹn; không coi RLS là cơ chế che mọi thông tin từ lỗi ràng buộc. [PostgreSQL Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) lưu ý unique/FK checks bypass row security để bảo toàn integrity, có thể tạo covert channel.

### 2.8 Tổ chức code và gói ngành sau đối chiếu CRM tham khảo

Đây là **thiết kế đề xuất của dự án**, không phải cây thư mục được sao chép nguyên trạng từ một CRM. Các bằng chứng ở phụ lục D giải thích vì sao chọn module extension, API/worker riêng và mô hình quan hệ có vai trò.

```text
apps/
  web/                         # Unified Inbox, CRM, quản trị
  api/                         # HTTP, auth, composition root
  worker/                      # inbox/outbox, sync, SLA, jobs
packages/
  domains/
    identity/                  # Contact, identity links, merge review
    sales/                     # Lead, Deal, Quote
    conversations/             # Inbox, Conversation, Message, assignment
    service/                   # Ticket, SLA
    finance/                   # Payment allocation, commission ledger
  contracts/                   # OpenAPI, event schemas, typed clients
  policy/                      # RBAC/ABAC, consent, send eligibility
  connectors/
    zalo-oa/ facebook/ tiktok-business/ web-form/ email/
  industry-packs/
    marketing-services/        # Brief, SOW, deliverables, acceptance
  ui/                          # Thành phần hiển thị dùng chung
  observability/               # Trace, metrics, log redaction
db/migrations/                 # Lịch sử migration theo thứ tự toàn hệ thống
tests/contract/                # Fixtures đã khử dữ liệu cá nhân
tests/integration/             # DB, transaction, webhook replay
tests/e2e/                     # Quyền, gửi tin, UAT trọng yếu
docs/adr/                      # Quyết định và lý do thay đổi
deploy/                        # IaC, runbooks, backup/restore
```

Module có `domain`, `application`, `ports`, `adapters` khi độ phức tạp cần; không ép mọi CRUD nhỏ thành hàng chục lớp. Chỉ import API công khai của domain; CI cấm import vòng và truy cập repository nội bộ domain khác. Domain không gọi trực tiếp SDK Zalo/Meta. Adapter chuyển dữ liệu ngoài thành command/event đã kiểm tra; thư viện `contracts` không chứa nghiệp vụ hay khóa truy cập. Không có thư mục `utils` khổng lồ chứa cả pricing, routing và quyền.

Stack tham chiếu nếu tự xây: TypeScript, React cho web, NestJS cho API, PostgreSQL cho giao dịch, queue worker cho việc nền, object storage cho tệp. Đây là lựa chọn để giảm số ngôn ngữ trong đội, không là kết luận benchmark. Redis/BullMQ chỉ thêm khi cần queue/rate limit và có vận hành; có thể khởi đầu bằng PostgreSQL job queue đáng tin cậy. Không đưa Kafka, Kubernetes, ClickHouse, vector DB hoặc microfrontend vào MVP chỉ vì dự án tham khảo có chúng. AI gateway là adapter; model/version và quyền tool thay đổi độc lập core.

Manifest gói ngành gồm `pack_key`, `version`, `requires_core`, `dependencies`, `owned_entities`, `permissions`, `event_subscriptions`, `migration_ids`, `feature_flags`. Namespace ví dụ `marketing_services.sow`; không cho hai pack cùng sở hữu một field core. Cài pack cần kiểm tra dependency và migration trên bản sao dữ liệu; conflict phải chặn build, không âm thầm “pack nạp sau thắng”. Gỡ pack mặc định vô hiệu chức năng, không DROP dữ liệu. Đây là biện pháp bổ sung vì cơ chế override theo thứ tự của EspoCRM hữu dụng nhưng nếu lạm dụng có thể che thay đổi của pack khác [R02](#r02).

Pipeline phát hành: lint/typecheck → boundary checks → unit domain trọng yếu → migration/integration → connector contract tests → E2E quyền và gửi tin → dependency/license scan → staging → canary → production. Mỗi release ghi commit và schema version. Migration theo expand/migrate/contract; rollback ứng dụng không đồng nghĩa rollback dữ liệu. Chỉ tách service khi có bằng chứng bottleneck, nhu cầu cô lập hoặc ownership riêng, có ADR và số đo trước/sau.

<a id="chuong-3"></a>

## CHƯƠNG 3 ĐẶC TẢ CHI TIẾT CÁC PHÂN HỆ NGHIỆP VỤ

<a id="danh-muc-module"></a>

### 3.0 Danh mục module và cách đọc đặc tả BA

**Đơn vị đặc tả là module nghiệp vụ.** Mỗi module bên dưới có người dùng, đối tượng sở hữu, danh sách chức năng có mã, màn hình/dữ liệu, điều kiện xử lý, trạng thái, quyền, ngoại lệ và tiêu chí chấp nhận. Mã `Mxx-Fyy` là chức năng chi tiết; `FR01–40` là yêu cầu cấp hệ thống đã có; `UC01–22` là luồng đi qua nhiều module. Không tạo ba yêu cầu khác nhau chỉ vì một hành vi có ba mã truy vết.

Hai nhóm dữ liệu luôn tách: khách mua dịch vụ của agency trong AGENCY workspace; dữ liệu người tiêu dùng agency xử lý thay khách trong CLIENT workspace được ủy quyền. Chi nhánh là trách nhiệm vận hành, pháp nhân là chủ thể ký/thu tiền. Một màn hình Customer360 chỉ tổng hợp phần được phép đọc, không tạo quyền truy cập mới.

| Mã module | Module / phạm vi chính | Người dùng chính | Dữ liệu module làm chủ | Liên kết bắt buộc | Phạm vi đưa vào sử dụng |
| --- | --- | --- | --- | --- | --- |
| [M01](#module-m01) | Hồ sơ khách hàng, doanh nghiệp, định danh và hợp nhất | Sales, AM, steward | Contacts/Accounts/Contact_Points/roles/merge | M02/M03/M08/M11/M20 | P0 hồ sơ/identity; phân nhóm nâng cao P1 |
| [M02](#module-m02) | Tiếp nhận nhu cầu, phân lead, cơ hội và hoạt động bán hàng | Marketing, Sales, quản lý | Leads/Deals/assignment/stage history/Activities | M01/M03/M07/M18 | P0 |
| [M03](#module-m03) | Hộp thư hợp nhất, trả lời và điều phối hội thoại | Sales, AM, CX | Conversations/Messages/response links/assignment | M01/M02/M11/M19/M20 | P0 một kênh đủ quyền; mở rộng sau pilot |
| [M04](#module-m04) | Chăm sóc tự động và nhắc việc theo hành trình | CMO, Sales Ops, AM | Journey definition/instance/send schedule | M02/M03/M08/M11/M20 | P0 nhắc việc đơn giản; engine P1 |
| [M05](#module-m05) | Giới thiệu khách hàng và tích điểm | Marketing, Finance | Referral/reward; loyalty ledger khi bật | M01/M09/M10/M20 | Referral P1; điểm/Mini App P2 |
| [M06](#module-m06) | Trợ lý AI: tóm tắt, gợi ý, soạn nháp | Người xử lý, AI owner | AI draft/evaluation/model/prompt evidence | M01/M02/M03/M07/M20 | P1 trợ lý; tự hành P2; guard trước bật |
| [M07](#module-m07) | Danh mục dịch vụ, báo giá, SOW và phê duyệt chào bán | Sales, chuyên môn, Finance | Catalog/Quote_Lines/quote revision/approval | M02/M08/M16/M17 | P0 |
| [M08](#module-m08) | Hợp đồng, đơn dịch vụ, onboarding và gia hạn | Sales, AM, Delivery | Contract/SOW/order/service period/handoff | M07/M09/M13/M16/M11 | P0; không tự gia hạn bằng timer |
| [M09](#module-m09) | Nghĩa vụ thu, nhận tiền, phân bổ, hoàn tiền và đối soát | Finance, AM đọc summary | Receipt/evidence/obligation/allocation/refund/period | M08/M10/M17/M18 | P0 nhập/đối soát thủ công; API ERP/bank P1 |
| [M10](#module-m10) | Hoa hồng và chi thưởng bán hàng | Finance, quản lý, người hưởng | Policy snapshot/pool/commission/payout/adjustment | M02/M05/M09 | Chỉ tính/chi khi policy đủ; không có thì PendingPolicy |
| [M11](#module-m11) | Tiếp nhận hỗ trợ, khiếu nại, SLA và khắc phục sự cố | AM/CX, Delivery | Ticket/entitlement/SLA/promise/resolution | M03/M08/M09/M12/M16 | P0 |
| [M12](#module-m12) | Phản hồi, CSAT/NPS và phục hồi trải nghiệm | CX, AM, CMO | Feedback/survey/recovery/corrective action | M08/M11/M15/M18 | P0 recovery; khảo sát tự động P1 |
| [M13](#module-m13) | Lịch hẹn và đặt tài nguyên | Sales, AM, ekip | Appointment/resource/booking/reminder | M02/M08/M16 | P0 lịch đơn giản; resource theo nhu cầu; GPS P2 |
| [M14](#module-m14) | Tổ chức, chi nhánh, thành viên, quyền và bàn giao nhân sự | Owner, quản lý, Admin theo quyền | Membership/role binding/team grant/delegation | Tất cả module; đặc biệt M09/M20 | P0 phân quyền; hai nhánh khi có vận hành thật; không payroll |
| [M15](#module-m15) | Brief, chiến lược, kế hoạch IMC và phê duyệt launch | CMO, strategist, AM | Brief/approved plan/campaign/launch/learning | M07/M16/M17/M18/M12 | P0 brief và gate khi launch; editor/experiment nâng cao sau |
| [M16](#module-m16) | Quản lý công việc cá nhân, đội nhóm, tổ chức, dự án và nguồn lực | Nhân viên, trưởng nhóm, PM, AM, Delivery, reviewer, khách có quyền | Task/assignment/review/recurrence/project/deliverable/acceptance | M02/M03/M04/M08/M11/M13/M14/M15/M17/M18 | P0 Task Core, My Work/Team Board, delivery; P1 effort/capacity/Gantt/portfolio nâng cao; P2 OKR/AI nâng cao |
| [M17](#module-m17) | Ngân sách, chi phí, nguồn tiền media và rủi ro hiệu quả | CMO, Finance, Delivery lead | Budget/commitment/cost/funding authorization | M07/M09/M15/M16/M18 | Cơ bản khi có chi phí/media; forecast nâng cao P1 |
| [M18](#module-m18) | Từ điển chỉ số, báo cáo điều hành và attribution | CEO, CMO, Sales/CX/Finance | KPI definition/metric facts/report snapshot | Nhận dữ kiện có quyền từ các module | P0 số liệu lõi; attribution nâng cao P1/P2 |
| [M19](#module-m19) | Kết nối bên ngoài, nhận/phát sự kiện và phục hồi | Integration operator | Connection/capability/inbox/outbox/checkpoint | M03/M09/M18/M20 | P0 một nguồn/kênh; connector khác theo quyền thực tế |
| [M20](#module-m20) | Consent, yêu cầu dữ liệu, retention và quản trị mục đích | Privacy owner, steward, owner | Processing/consent/suppression/privacy/retention | Tất cả module xử lý dữ liệu cá nhân | Kiểm soát P0 từ ngày đầu; không đợi có engine riêng |

**Ranh giới không được nhập nhằng:** M01 sở hữu người/doanh nghiệp; M02 sở hữu nhu cầu và quyết định mua; M03 sở hữu luồng trao đổi; M08 sở hữu cam kết hợp đồng; M16 sở hữu công việc/đầu ra; M09 sở hữu tiền và phân bổ quản trị, ERP vẫn sở hữu chứng từ hạch toán. M10 dùng kết quả cash đủ điều kiện, không tự xác nhận tiền. M18 đọc dữ liệu có nguồn, không sửa giao dịch để làm đẹp báo cáo. M14 cấp quyền theo authority; M20 giới hạn mục đích dữ liệu; hai module đều không cho người dùng tự vượt quyền.

**Luồng tham chiếu:** M19→M01→M02→M07→M08→M09/M16→M11/M12→M08 tái ký. M03 giữ trao đổi và gắn đúng work item suốt luồng. M13 hỗ trợ lịch; M15/M17 hỗ trợ lập kế hoạch và thực thi; M04 tự động hóa hành động đã đủ điều kiện; M18 đo kết quả. M05/M06 chỉ mở khi có nhu cầu và điều kiện kiểm soát.

**Hợp đồng thao tác chung:** giao diện hiển thị field bắt buộc, giá trị chưa biết, readonly, lý do thao tác bị chặn và hành động khắc phục. Server là nơi quyết định validation, quyền và transition; ẩn nút không thay authorization. Create/change command có operation ID, scope lấy từ phiên/connection hợp lệ, expected_version khi có cạnh tranh; cùng key khác payload trả409. Không đủ quyền trả403 hoặc404 theo chính sách không tiết lộ tồn tại; thiếu dữ liệu trả422 có field/error code; dependency tạm lỗi trả trạng thái Pending/Blocked có owner, không giả Success. Mọi thay đổi có actor/time/source/history; các tác động liên module theo transaction/outbox, không sửa trực tiếp dữ liệu module khác.

**Màn hình điều hướng sản phẩm:** Công việc hôm nay; Khách hàng; Lead/Cơ hội; Hộp thư; Báo giá; Hợp đồng; Dự án/Đầu ra; Tài chính/Hoa hồng theo quyền; Hỗ trợ/Phản hồi; Lịch; Marketing; Báo cáo; Quản trị. Menu chỉ hiện module được bật và được cấp quyền. Admin không mặc nhiên thấy màn hình tiền/hợp đồng; người dùng cá nhân có thể kiêm vai được khai báo rõ.

Các mục số hiện hữu được giữ để không làm đứt FR/UC/schema. M03 có mô tả nghiệp vụ tại3.3 và hợp đồng kỹ thuật tại3.12; hai phần thuộc cùng module, không là hai inbox. M14 dùng3.8.2/6.1, M19 dùngChương2, M20 dùng6.3/6.4. Ngưỡng và phạm vi mở theo A.6/9.5, không suy rằng20 module phải triển khai đủ trong MVP.

### 3.1 CDP và hồ sơ khách hàng 360 độ

#### 3.1.1 FR01 Hồ sơ và định danh

**Mục đích và trách nhiệm:** FR01 Hồ sơ — Sales Ops/AM. Giữ quan hệ xuyên nhân viên và nhiều hợp đồng; tránh khách phải nhắc lại.

**Liên kết đầu vào → đầu ra:** Connector/form → Contact/Account/roles → Lead/Deal/Ticket/Project.

**Nghiệm thu và giai đoạn:** Một người đại diện hai công ty, quyền và lịch sử không lẫn; P0.

Hồ sơ hiển thị thông tin pháp nhân/cá nhân, người phụ trách, chi nhánh, nguồn, consent, timeline, deal, hợp đồng, dự án, ticket và công nợ. Người dùng chỉ xem các trường và đối tượng được cấp quyền. B2B có quan hệ contact_account_roles gồm vai trò quyết định, người dùng, tài chính và người ảnh hưởng, ngày hiệu lực và ngày kết thúc.

Chuẩn hóa số điện thoại về E.164 khi xác định được quốc gia; giữ bản gốc và không tự suy quốc gia cho số mơ hồ. Email trim và chuẩn hóa domain; không tự xóa dấu chấm hoặc phần + vì quy tắc khác nhau giữa nhà cung cấp. Tên tiếng Việt giữ dấu; bản không dấu chỉ phục vụ tìm kiếm. Mã số thuế và pháp nhân cần phân biệt trụ sở, chi nhánh và người liên hệ.

#### 3.1.2 FR02 Identity resolution và merge

**Mục đích và trách nhiệm:** FR02 Identity/merge — Steward. Tránh gọi trùng nhưng không gộp sai người và consent.

**Liên kết đầu vào → đầu ra:** Identity/evidence → candidate/merge mapping → timeline/assignment/consent.

**Nghiệm thu và giai đoạn:** Unmerge sau tin mới/revoke không gửi sai; chứng từ đã chốt không tự chuyển chủ; P0 phần chống trùng.

Ưu tiên mapping external_id đã xác thực theo tenant + channel + channel_account_id. Số điện thoại/email đã xác thực là bằng chứng mạnh nhưng có thể dùng chung hoặc tái cấp; không auto merge khi có xung đột người. Tên giống, địa chỉ giống hoặc cùng công ty chỉ tạo ứng viên. Chỉ auto-link khi định danh đã được xác minh và không có mâu thuẫn; trường hợp khác vào hàng đợi steward.

Merge giữ survivor_id, alias cũ, lý do, chứng cứ, người duyệt, snapshot và danh sách bản ghi liên quan. Trường verified thắng unverified; dữ liệu mới hơn chỉ thắng khi nguồn đủ tin cậy. Không cộng gộp consent thành quyền rộng hơn. Không merge qua tenant hoặc client_workspace; cần chia sẻ hợp lệ bằng quy trình riêng.

Unmerge dùng mapping/provenance trước và sau merge; tự tách phần đủ bằng chứng, steward xét phần mơ hồ. Chứng từ đã ký/chốt không tự đổi chủ thể theo Contact. Không hứa đảo ngược mọi tác động tự động như tin đã gửi. UAT FR02: hai người dùng chung số tổng đài phải tồn tại riêng; một webhook trùng không tạo contact mới.

#### 3.1.3 FR03 Phân nhóm RFM

**Mục đích và trách nhiệm:** FR03 RFM — CMO/AM. Phân nhóm để ưu tiên chăm sóc; chỉ có ích khi phù hợp nhịp mua.

**Liên kết đầu vào → đầu ra:** Kỳ dịch vụ, phí, payment → segmentation → journey/account review.

**Nghiệm thu và giai đoạn:** Hai khách cùng retainer nhưng lịch trả khác không bị xếp hạng máy móc; P1.

RFM là lát cắt giao dịch, không thay health. Giữ `payment_recency`, số kỳ dịch vụ/mua và service cash sau refund; loại VAT/media theo policy. Frequency không tăng thành ba lần mua khi một nghĩa vụ trả ba đợt. B2B tính theo Account, B2C theo Contact trong đúng scope.

Khách trả trước năm vẫn đang được phục vụ không bị đánh ngủ đông chỉ vì lâu không có khoản thu. Phân nhóm hành động ưu tiên hợp đồng/kỳ dịch vụ đang hiệu lực, engagement, delivery, overdue và ticket. Nhãn Khách mới/Giá trị cao/Có rủi ro/Không hoạt động có thể đồng thời tồn tại; mỗi nhãn có reason, window, version, owner và hành động. Ngưỡng được pilot theo mô hình dịch vụ; dữ liệu thiếu là Unknown. Không dùng ngưỡng R≤30/F≥6 chung cho mọi lịch trả.

<a id="module-m01"></a>

#### ĐẶC TẢ MODULE M01 — CDP và hồ sơ khách hàng

**Mục đích, tác nhân và phạm vi:** Sales/AM quản lý người và doanh nghiệp; steward xử lý định danh; Marketing dùng phân nhóm đúng mục đích. P0 gồm hồ sơ, quan hệ và chống trùng; RFM ở P1. Hồ sơ dùng chung nhưng quyền đọc từng nghiệp vụ độc lập.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M01-F01 Tạo hồ sơ | Form/inbox/nhập tay; nguồn, scope, liên hệ | Chưa rõ tên dùng nhãn provisional; không đoán quốc gia số điện thoại | Contact/Contact_Points; M02/M11 | Giữ một hồ sơ có nguồn thay vì thông tin rời rạc. |
| M01-F02 Định danh | External identity hoặc endpoint | Mapping xác minh đúng scope thì link; xung đột thì review | Identity_Links, queue steward; inbox | Tránh liên kết sai người và lộ lịch sử của khách khác. |
| M01-F03 Quan hệ B2B | Người đại diện doanh nghiệp | Ghi vai trò và hiệu lực; giữ quan hệ lịch sử | Contact_Account_Roles; Deal/Contract | Một người có thể đại diện nhiều doanh nghiệp theo từng thời kỳ. |
| M01-F04 Merge/undo | Đề nghị và evidence | Đủ chứng cứ cùng scope mới merge; undo xét provenance | Survivor/journal/alias; consent không rộng lên | Sửa gộp sai mà không mất nguồn và quyền liên hệ. |
| M01-F05 Timeline | Người dùng mở hồ sơ | Kiểm từng activity/thread/tệp, không leak count | Timeline có nguồn; Sales/Delivery/CX | Giúp người tiếp nhận hiểu ngữ cảnh trong đúng quyền được cấp. |
| M01-F06 Phân nhóm | Kỳ tính, policy Active | Frequency theo kỳ mua; tiền sau refund; thiếu dữ liệu là Unknown | Nhãn/reason/version/freshness; journey | Chăm sóc theo nhịp dịch vụ thực tế, tránh đánh nhầm khách ngủ đông. |

**Màn hình và trường:** Danh sách lọc owner/scope/lifecycle; chi tiết có liên hệ, quan hệ, timeline, consent; duplicate review có preview trước/sau. Bắt buộc scope server xác định, nguồn, display_name hoặc nhãn chưa biết. Account cần legal_name/owner; định danh thuế có quốc gia/loại khi xác minh. verified_at, evidence, journal, consent projection và số dư chỉ đọc; thay đổi bằng lệnh nghiệp vụ.

**Trạng thái/lệnh:** Identity Provisional/Verified/Conflict tách lifecycle Subscriber/Lead/Customer/Inactive. create-contact, add-contact-point, link-identity, propose-merge, approve-merge, undo-merge, archive kiểm quyền/version và audit. Archive không đồng nghĩa xóa dữ liệu.

**Quyền/ngoại lệ:** Sales sửa trong grant; steward duyệt merge; privacy owner xử lý yêu cầu dữ liệu. Hotline, số tái cấp/email chung không auto merge; không merge cross-workspace. Chứng từ đã ký không tự đổi chủ. Policy phân nhóm chưa chốt giữ Draft, chặn tự động tương ứng, vẫn quản hồ sơ.

**Nghiệm thu:** M01-AC01: hai người chung hotline vẫn riêng. M01-AC02: người đại diện hai account chỉ xem lịch sử được cấp. M01-AC03: merge/revoke/undo không phục hồi consent đã rút. M01-AC04: trả trước năm không thành ngủ đông chỉ vì lâu chưa thu tiền.

**Truy vết:** FR01–03/31/37; UC01/11/15/18; schema 5.3–5.4/5.9/5.16/5.18; quyền 6.1, retention 6.4.

### 3.2 Quản trị lead và phễu bán hàng

#### 3.2.1 FR04 Hai pipeline có kiểm soát

**Mục đích và trách nhiệm:** FR04 Pipeline — Sales Director. Dự báo và gỡ nghẽn cần cơ hội có trạng thái thật.

**Liên kết đầu vào → đầu ra:** Demand/qualification → Deal/stage history → Quote/forecast.

**Nghiệm thu và giai đoạn:** Không tạo pipeline từ ticket; quay lại giữ lineage/aging; P0.

Lead biểu diễn một nhu cầu/đợt tiếp nhận: New → Assigned → Contacting → Qualified → Converted; các nhánh Nurture, Dormant, Disqualified có lý do và điều kiện thoát. `handover_status` Marketing→Sales tách khỏi trạng thái này: Pending/Accepted/Rejected/Recycled; ghi người giao/nhận, timestamps, policy, reason/evidence. NoCapacity không phải NoFit. MQL/SAL/SQL là milestones có định nghĩa, không ghi đè lifecycle Customer của Contact.

Deal B2B: Discovery → Proposal → Negotiation → Won/Lost; B2C: Offer → Won/Lost theo gói. OnHold có lý do, review date, quy tắc forecast và lịch sử; giữ total age/active time/hold time. Không clone chỉ để làm ngắn sales cycle. Qualified cần đầu mối, nhu cầu và next action; budget/decision maker chưa rõ ghi Unknown. Vai trò ở Account khác thẩm quyền ký/nghiệm thu một hợp đồng.

Nhu cầu mới của khách cũ tạo Lead/Deal mới có lineage; hỗ trợ sau bán tạo Ticket. Cùng nhu cầu thì nối lịch sử hiện hữu, không dùng ngưỡng 14 ngày duy nhất. Kiểm trùng mềm theo buyer/account + service/campaign/nhu cầu và scope; cho phép các deal song song hợp lệ. Conversion idempotent và chỉ link activity/thread thuộc nhu cầu đó; Lost không xóa quote/history.

#### 3.2.2 FR05 Phân lead và SLA thu hồi

**Mục đích và trách nhiệm:** FR05 Routing/SLA — Sales Ops. Không bỏ sót và không hai người giành cùng lead.

**Liên kết đầu vào → đầu ra:** Scope/skill/availability/ownership → assignment + episode → activity/escalation.

**Nghiệm thu và giai đoạn:** Claim cạnh tranh, owner nghỉ ca, busy/NoAnswer và hai nhu cầu cùng contact; P0.

Router lọc tenant/workspace/quyền và phạm vi phục vụ/kỹ năng trước; ưu tiên owner hợp lệ rồi kiểm lịch khả dụng/backup và ngưỡng capacity mềm/cứng. Trùng phone/email hash chỉ cảnh báo nghi trùng, không trao quyền hoặc tự merge. Người trực thay không tự đổi chủ Deal hay quyền hưởng commission. Atomic claim/CAS hoặc row lock, history và outbox cùng transaction.

Tách đồng hồ nhận việc, nỗ lực đầu, phản hồi người thật và kết nối thành công; completion theo đúng nhu cầu/episode. NoAnswer/busy có evidence là attempt theo policy, chưa là kết nối/phản hồi thành công. Không dùng riêng 15 giây đổ chuông để chứng minh đã chăm sóc. Có next action/callback và cơ chế xử lý race khi activity đến muộn hoặc lead đang bị thu hồi.

Business calendar Asia/Ho_Chi_Minh khai báo ca, nghỉ trưa/ngày nghỉ và version; ngoài giờ theo ca tiếp. Ngưỡng pilot theo kênh/intent/nhân sự: kênh có người trực có thể thử phản hồi đầu 15–30 phút, tư vấn B2B chuyên sâu 2–4 giờ làm việc; lead có hẹn theo lịch khách. Đây là giả định cần xác nhận, không cam kết 5/15 phút cho mọi lead. Cảnh báo/thu hồi theo policy; tối đa hai lần chuyển tự động rồi queue quản lý. Chuyển owner không reset nghĩa vụ khách hàng; provider outage có exception/audit, không sửa timestamp gốc.

#### 3.2.3 FR06 Năng suất và chất lượng dữ liệu

**Mục đích và trách nhiệm:** FR06 Năng suất — Sales Manager. Giúp biết việc cần làm và dữ liệu thiếu; giảm báo cáo ngoài.

**Liên kết đầu vào → đầu ra:** Activity/next action/stage → Today/data quality → coaching.

**Nghiệm thu và giai đoạn:** Người dùng hoàn tất tác vụ đại diện, ghi thời gian/khó khăn; overdue phân nguyên nhân; P0.

100 lead/tháng chia 30 Sales chỉ khoảng 3,3 lead/người nếu phân đều, nên không mở cả 30 người nhận inbound ngay. Pilot pool 5 người, phân theo capacity và giữ nhóm chuyên ngành; tính toán capacity từ thời gian xử lý thật. Không dùng số lượng thao tác làm KPI duy nhất vì dễ khuyến khích ghi hoạt động rỗng.

<a id="module-m02"></a>

#### ĐẶC TẢ MODULE M02 — Lead và Deal

**Mục đích, tác nhân và phạm vi:** Marketing bàn giao nhu cầu; Sales qualification và theo đuổi cơ hội; Sales Ops quản queue/SLA; quản lý xử lý ngoại lệ. P0 quản Lead/Deal/next action. Lead là một nhu cầu, Contact là quan hệ; hỗ trợ sau bán đi M11.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M02-F01 Nhận nhu cầu | Event/form có source ID | Lặp trả kết quả cũ; chưa rõ model dùng Unknown, vẫn có queue/SLA | Lead/source; M01/inbox | Không bỏ sót nhu cầu hoặc đếm lặp do webhook. |
| M02-F02 Phân/nhận việc | Skill, ca, capacity, version | Scope trước continuity; hết người vào queue; claim atomic | Assignment/history/clock; Today | Xác định một người chịu trách nhiệm phù hợp và tránh tranh nhận. |
| M02-F03 Bàn giao | MQL và evidence/policy | Handover tách lifecycle; NoCapacity không là NoFit | Accepted/Rejected/Recycled và next action | Phân biệt chất lượng lead với việc Sales hết năng lực tiếp nhận. |
| M02-F04 Qualification | Discovery/nhu cầu/đầu mối | Xác nhận B2B/B2C trước Qualified; ngân sách chưa rõ giữ Unknown | Qualified/nurture/disqualify có reason | Theo đuổi đúng nhu cầu mà không ép khách khai thông tin chưa biết. |
| M02-F05 Convert | Qualified và commercial intent | Cùng conversion key trả cùng Deal; nhu cầu khác có lineage | Deal/buying group; M07 | Tạo cơ hội mua có căn cứ và chống nhân bản khi thao tác lặp. |
| M02-F06 Pipeline | Stage, quyết định khách | OnHold giữ stage/review; Won/Lost cần gate/reason | History/forecast; M08 | Phản ánh quyết định mua và dự báo thật, giữ lịch sử hoãn/thua. |
| M02-F07 Today/thu hồi | Clock, activity, callback | NoAnswer chỉ là attempt; đổi owner không reset SLA | Next action/escalation; SLA engine | Không quên lời hẹn và không dùng thao tác rỗng để che SLA. |

**Màn hình và trường:** Today có callback/queue/blocker; Lead detail có source/model/handover/activity; pipeline có aging theo B2B/B2C. Intake cần contact/provisional, nguồn, received_at, scope, owner hoặc queue. Qualification cần model/nhu cầu/đầu mối/next_action_at; B2B Deal cần Account, B2C cần buyer Contact. Due, aging, first_attempt_at và attribution lịch sử chỉ đọc. Lost cần reason; OnHold cần reason/review_at.

**Trạng thái/lệnh:** Lead New/Assigned/Contacting/Qualified/Converted, nhánh Nurture/Dormant/Disqualified. Deal Open với stage riêng; work_state Active/OnHold; kết thúc Won/Lost. claim, accept-handover, recycle, record-attempt, qualify, convert, change-stage, hold/resume/close kiểm expected_version, guard/audit; không PATCH status tự do.

**Quyền/ngoại lệ:** Sales thao tác trong grant; quản lý reassign đúng scope; Marketing không tùy ý sửa kết quả bán. Từ chối liên hệ tạo suppression phù hợp. Activity tới muộn giữ occurred/received/evidence, không xóa breach. Routing/SLA chưa duyệt giữ Draft; intake vào queue có giám sát, chưa bật rule tự động bị ảnh hưởng.

**Nghiệm thu:** M02-AC01: Unknown có owner/clock nhưng chưa convert. M02-AC02: claim cạnh tranh chỉ một thành công. M02-AC03: convert cùng intent tạo một Deal. M02-AC04: đổi ca/OnHold không xóa aging, commission hoặc SLA lịch sử.

**Truy vết:** FR04–06/28/35–36; UC01–03/20/22; schema 5.2/5.5/5.7/5.13/5.18; API 2.5; 3.13.4 và W-F01.

### 3.3 Omnichannel Inbox và Zalo tập trung

<a id="module-m03"></a>

#### ĐẶC TẢ MODULE M03 — Omnichannel Inbox và bảo vệ nội dung

**Mục đích, tác nhân và phạm vi:** Sales/AM/CX tiếp nhận, phân công và trả lời yêu cầu trên tài khoản doanh nghiệp được phép; trưởng nhóm xử lý quá tải, steward xác minh liên kết danh tính. M03 sở hữu trải nghiệm hội thoại; M19 sở hữu connector, M20 sở hữu mục đích và suppression. P0 mở một inbox/kênh; các kênh khác mở theo capability đã kiểm, không mặc định đầy đủ năm kênh.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M03-F01 Thu nhận | Event đã xác minh, connection, provider IDs | Nếu trùng canonical event thì no-op; nếu chưa rõ người thì giữ identity/provisional đúng luồng intake; không tạo Lead từ status/read event | Message/thread đúng scope; FR30/31/33, M19 | Giữ tin đúng nguồn và không biến sự kiện kỹ thuật thành khách mới. |
| M03-F02 Phân loại yêu cầu | Tin inbound, request đang mở | Nếu complaint thì link Ticket; inquiry mới thì đề xuất Lead; chưa rõ thì queue phân loại với thời gian chờ gốc | Business_Subjects và link; FR39, UC22 | Đưa hỏi mua và khiếu nại tới đúng quy trình xử lý. |
| M03-F03 Nhận/chuyển việc | Queue, actor, version, capacity | Nếu scope/skill không đạt thì từ chối; nếu hai người claim thì một thành công; chuyển người không reset SLA | Assignment history, handoff; FR35/36 | Có người trả lời chính nhưng vẫn bàn giao được khi đổi ca. |
| M03-F04 Soạn và gửi | Thread, sender, recipient, body, response_targets, file hash | Nếu note thì tuyệt đối không outbound; reply phải qua quyền/capability/purpose và file clean; đổi recipient/file sau approval phải duyệt lại | Intent/outbox; FR32/34/40, M20 | Tránh gửi nhầm tài khoản, người nhận hoặc ghi chú nội bộ. |
| M03-F05 Theo dõi kết quả | Provider receipt hoặc timeout | Accepted khác delivered/read; timeout sau request là unknown_outcome, không retry mù; receipt trùng không hoàn thành clock hai lần | Send attempts/status events; UC19 | Không báo khách đã nhận khi chưa có bằng chứng từ kênh. |
| M03-F06 Quản lý nghĩa vụ | Reply và response targets hợp lệ | Chỉ dừng clock đúng subject/episode đạt criterion; note/autoack không dừng; đóng thread không đóng mọi Ticket | SLA_Episodes; FR36/39, WF02 | Trả lời một việc không được làm mất nghĩa vụ của việc khác. |
| M03-F07 Timeline/tìm kiếm | Query, actor, ACL hiện tại | Lọc object/field/count/snippet/file trước hiển thị; Contact chung không mở thread khác; merge chỉ trong workspace | Kết quả có quyền; FR08/31/37 | Có ngữ cảnh chăm sóc mà không mở lịch sử ngoài nhiệm vụ. |
| M03-F08 Phục hồi | Gap/backfill/reconnect | Historical event chỉ bổ sung lịch sử; không gửi lại tin, tạo acquisition lead hoặc reset clock live | Coverage/gap và task xử lý; FR38, M19 | Phục hồi dữ liệu thiếu mà không gửi bù hoặc tạo nghiệp vụ trùng. |

**Màn hình và trường:** Inbox ba vùng gồm queue, thread và hồ sơ/nghĩa vụ. Luôn hiện kênh/tài khoản gửi, assignee, waiting party, nguồn live/backfill, clock đến hạn và open subjects. Composer bắt buộc thread, public reply/private note, người nhận và nội dung hoặc file; có To/CC/BCC khi email hỗ trợ, preview reply-all và response targets. Hiển thị PII theo nhiệm vụ, không hỏi lý do lặp lại cho công việc thường lệ.

**Commands và trạng thái:** `claim`, `assign`, `send`, `add-note`, `resolve`, `close`, `reopen`, `link-subject` kiểm expected_version và command key. Conversation open→resolved→closed; inbound hợp lệ reopen theo policy; waiting_party và assignment độc lập. Intent giữ queued/attempting/accepted/failed/blocked/unknown_outcome theo hợp đồng provider. Không cho PATCH tùy ý status.

**Quyền và ngoại lệ:** Agent chỉ thread được giao/chia sẻ còn hiệu lực; supervisor override trong scope có lý do. Steward duyệt merge, Operator replay, quyền này không thay quyền gửi. Hết cửa sổ hoặc revoke thì blocked; token lỗi báo degraded; không có người trực thì queue có owner nhóm. Native reply không quan sát được phải hiện gap. File bảo vệ dùng gateway kiểm quyền ở request mới sau revoke; URL không thay session.

**Nghiệm thu:** M03-AC01 — replay và claim đồng thời: một effect/assignment; FR33/35, UC17/20, Inbound_Events/Messages/Conversation_Assignments. M03-AC02 — reply báo giá không dừng complaint; FR36/39, UC19, Message_Subject_Links/SLA_Episodes, WF-U02. M03-AC03 — workspace khác, link cũ sau revoke, BCC/note và timeout/backfill đều giữ đúng quyền/trạng thái; FR08/34/37/38/40, UC12/14/21, Message_Attachments/Outbound_Intents, U16/U17/SEC-U03.

#### 3.3.1 FR07 Hội thoại thuộc tổ chức

**Mục đích và trách nhiệm:** FR07 Inbox — CX Ops. Lịch sử thuộc tổ chức, có người trả lời chính và ngữ cảnh.

**Liên kết đầu vào → đầu ra:** Kênh/identity/thread → conversation → lead/ticket/activity.

**Nghiệm thu và giai đoạn:** Private note không outbound; hội thoại không biến thành khách mới mỗi message; P0 một kênh.

Conversation có channel_account_id, external_thread_id, participants và owner; message có provider_message_id, direction, delivery state và attachment reference. Cho một người trả lời chính trong phiên, có chỉ báo đồng nghiệp đang nhập và chuyển giao có lý do. Gửi tin qua queue để kiểm policy và tránh trùng; trạng thái Accepted khác Delivered và Read.

Thiết kế ưu tiên OA và Page thuộc doanh nghiệp. Khách phát sinh trên Zalo cá nhân được tạo lead, ghi nguồn và xin chuyển sang OA/email/cổng khách khi phù hợp. Không cam kết tự thu hồi lịch sử tài khoản cá nhân, không lấy cookie/session của Sales và không dùng API không chính thức làm điều kiện vận hành cốt lõi.

#### 3.3.2 FR08 Data masking và bàn giao

**Mục đích và trách nhiệm:** FR08 Masking/bàn giao — Privacy + Ops. Dùng dữ liệu đủ cho công việc và thu hồi đúng khi nghỉ việc.

**Liên kết đầu vào → đầu ra:** Assignment/ACL → quyền liên hệ/tệp → handoff + audit.

**Nghiệm thu và giai đoạn:** Sales nghỉ việc không còn phiên/tệp, AM được trao quyền hợp lệ; P0.

API kiểm row/field policy trước khi trả dữ liệu. Người được giao nhiệm vụ liên hệ được xem số/email cần thiết trong thời gian quyền còn hiệu lực, không phải nhập lý do lặp mỗi 5 phút. Người ngoài phạm vi thấy mask/không thấy theo policy; hồ sơ nhạy cảm hoặc break-glass dùng reveal có purpose/lý do/TTL cấu hình và audit. Search, file, BI, export và AI cùng kiểm soát; rate-limit/cảnh báo bổ sung không thay authorization.

Offboarding nhân sự thu hồi login/session/token/grant, bàn giao open lead/deal/ticket, lời hứa cập nhật, draft, scheduled send, approval pending, lịch và automation ownership. Job kiểm lại authority khi chạy; người không có quyền không dùng link/file/cache cũ để đọc tiếp. Giữ actor lịch sử và quyền hưởng hoa hồng theo policy; watermark hỗ trợ truy vết, không cam kết chống chụp ảnh tuyệt đối.

### 3.4 Marketing automation và Loyalty trên Mini App

#### 3.4.1 FR09 Journey engine

**Mục đích và trách nhiệm:** FR09 Journeys — CMO/CX. Follow-up và onboarding có lịch; tránh bỏ sót hoặc nhắc sai khi đang khiếu nại.

**Liên kết đầu vào → đầu ra:** Event, purpose, consent, lifecycle → scheduled action → message/task/outcome.

**Nghiệm thu và giai đoạn:** Revoke khi đang chờ hủy marketing; refund/complaint dừng upsell phù hợp; P0 đơn giản/P1 engine.

Journey definition chứa version, entry event, filter, wait, action, exit và re-entry policy. Trước dispatch phải kiểm consent/purpose/endpoint hiện thời, suppression, kênh, mẫu được duyệt, cap toàn scope và quota và giờ yên lặng 20:00–08:00 theo chính sách nội bộ. Người dùng rút consent trong lúc chờ thì hủy các bước marketing còn lại; thông báo phục vụ hợp đồng được đánh giá theo mục đích riêng.

| Kịch bản | Trigger và nhánh | Thoát và kiểm soát |
| --- | --- | --- |
| Lead tải tài liệu | Opt-in nội dung; gửi tài liệu; sau 2 ngày đề nghị tư vấn nếu còn quyền | Thoát khi đặt lịch, từ chối, hết quyền hoặc đạt 2 tin/7 ngày theo đề xuất. |
| Báo giá chưa phản hồi | Sau 2 ngày làm việc chưa có quyết định | Tạo task Sales; chỉ gửi follow-up khi phù hợp chính sách kênh. |
| Onboarding | Hợp đồng có hiệu lực và đủ điều kiện khởi động | Xin asset, họp kickoff, thông báo thiếu tài liệu; không gửi yêu cầu mật khẩu quảng cáo qua chat. |
| Gia hạn | Mốc review/notice theo hợp đồng; template45/30/15 chỉ khi phù hợp | Nếu ticket nghiêm trọng đang mở, chuyển account manager xử lý trước chào bán. |
| Win-back | 90 ngày không hợp đồng hiệu lực | Kiểm consent và loại trừ khách khiếu nại chưa giải quyết. |

<a id="module-m04"></a>

#### ĐẶC TẢ MODULE M04 — Journey và nhắc việc có kiểm soát

**Mục tiêu, tác nhân và phạm vi:** CMO thiết kế follow-up; Sales/AM thực hiện task; người phụ trách quyền dữ liệu duyệt mục đích; worker điều phối. P0 gồm nhắc việc đơn giản theo báo giá/onboarding/gia hạn; engine nhiều nhánh P1. Journey không thay SLA, không tự gửi marketing khi chỉ có yêu cầu tư vấn.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M04-F01 Soạn phiên bản | CMO tạo mẫu, purpose, trigger, bước/chờ | Thiếu exit/re-entry/cap/owner hoặc policy chưa Active thì chỉ lưu Draft; không Activate | Definition version; M01, M18 | Giữ quy tắc follow-up có phiên bản, chủ sở hữu và lối thoát. |
| M04-F02 Xét entry | Event nghiệp vụ có ID, subject, occurred_at | Event replay trả instance cũ; backfill không tự enroll; scope/purpose không hợp lệ thì reject | Instance/key, nguồn sự kiện | Không chạy lại một hành trình chỉ vì sự kiện được giao lặp. |
| M04-F03 Lập lịch | Instance đủ điều kiện, calendar/notice | Due theo business calendar hoặc timestamp hợp đồng; không dùng mặc định45ngày thay notice60ngày | Task/intent due; M08/hợp đồng | Nhắc đúng mốc hợp đồng và giờ làm việc thực tế. |
| M04-F04 Thực thi bước | Đến hạn, ACL/consent/capability hiện tại | Task hợp lệ tạo một lần; outbound phải qua send gate; chưa có policy được duyệt thì hold | Task hoặc Outbound_Intent; inbox/outbound | Thực hiện hành động đúng quyền tại thời điểm thực sự chạy. |
| M04-F05 Arbitration | Nhiều journey cùng endpoint/purpose | Dùng chung cap/reservation gửi; incident/suppression thắng upsell; không tính cap riêng từng journey | Defer/suppress có reason; CX | Tránh nhiều chiến dịch cùng làm phiền một người nhận. |
| M04-F06 Exit và repair | Revoke, mua hàng, complaint, hết hạn, lỗi | Re-evaluate exit; hủy bước chưa gửi; provider Unknown giữ reconcile, không gửi lại mù | Exit log, case; privacy/sync | Dừng đúng khi bối cảnh đổi và xử lý lỗi có người chịu trách nhiệm. |

**Màn hình và dữ liệu:** danh sách definition theo version/status; canvas hoặc bảng bước; hàng đợi due/held/failed và timeline instance. Bắt buộc có tên, owner, scope, purpose, trigger, entry filter, action, exit, re-entry, policy/calendar version; bước gửi có connection/recipient/template/expiry. Readonly gồm nguồn event, instance key, policy decision, attempts, timestamps và exit reason. Không cho sửa instance đang chạy để đổi rule lịch sử; revision mới áp instance mới, migration instance cũ cần thao tác riêng có preview.

**Trạng thái và commands:** definition `Draft → Reviewed → Active → Paused/Retired`; `activate/pause/retire` kiểm quyền và dependencies. Instance `Scheduled → Running → Waiting → Completed/Exited`; lỗi kỹ thuật `Held/Failed` có owner, reason, retry eligibility. Pause definition chặn tạo instance và dispatch mới; resume kiểm lại quyền/expiry, không xả bù toàn bộ. `cancel/replay` có phạm vi và idempotency, không bypass suppression.

**Quyền và ngoại lệ:** CMO sửa draft; người có quyền activate duyệt version; Sales chỉ xử lý task được giao; Admin quản connector không tự có quyền audience. Cap, quiet hours, cooldown và re-entry chưa chốt giữ Draft, chặn automation tương ứng; nhắc việc thủ công vẫn dùng được. Một người kiêm vai phải có audit self-approval.

**Nghiệm thu:** `M04-AC01` replay entry ba lần chỉ một instance/effect; `M04-AC02` revoke sau enqueue chặn dispatch mới; `M04-AC03` hai journey cạnh tranh cùng cap không vượt cap đã duyệt; `M04-AC04` resume sau outage không gửi intent hết hạn. **Truy vết:** FR09; UC10/11/19/21; Journeys, Journey_Instances, Policy_Versions, Outbox, Outbound_Intents, Consent_State và Customer_Promises. Ca liên quan INT17, CMO-U07–CMO-U10, RV17.

#### 3.4.2 FR10 Loyalty và referral

**Mục đích và trách nhiệm:** FR10 Loyalty/referral — CMO/Finance. Referral có thể tạo nguồn khách; tích điểm chỉ hữu ích khi có hành vi lặp và kinh tế phù hợp.

**Liên kết đầu vào → đầu ra:** Referral + khách đủ điều kiện + thực thu → reward ledger → payout/reversal.

**Nghiệm thu và giai đoạn:** Refund không thưởng lại, referral không cộng trùng hoa hồng sales trái policy; P1 referral/P2 loyalty.

Tách referral khỏi loyalty. Referral có nguồn, referrer, khách mới theo định nghĩa, ngày/điều kiện khóa attribution, dispute và payout. Kiểm tự giới thiệu, trùng pháp nhân, khách đã có, bên liên quan và thưởng trùng với pool sales theo policy. Chỉ thưởng khi đạt điều kiện thực thu/kiểm soát hoàn tiền đã công bố; refund tạo reversal một lần. Marketing attribution không tự tạo quyền nhận thưởng.

Referral nhẹ ở P1 và không phụ thuộc Mini App. Loyalty điểm/hạng, ưu đãi và Mini App ở P2, chỉ bật khi có hành vi mua lặp và business case. Khi bật phải có earn/reserve/redeem/expire/reverse append-only, policy economics, fraud control và consent. Không áp một tỷ lệ điểm/chi tiêu giả định cho mọi agency.

<a id="module-m05"></a>

#### ĐẶC TẢ MODULE M05 — Referral và loyalty theo điều kiện kinh tế

**Mục tiêu, tác nhân và phạm vi:** Marketing ghi nhận giới thiệu; Finance xác minh thưởng và chi trả; steward xử lý trùng/người liên quan; khách hoặc đối tác là người giới thiệu. Referral nhẹ P1; điểm/hạng và Mini App P2. Mục tiêu là thưởng đúng khách mới đủ điều kiện, giữ chi phí trong chính sách; attribution marketing không tự sinh quyền nhận tiền.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M05-F01 Khai báo giới thiệu | Referrer, buyer/demand, source evidence | Thiếu evidence hoặc referrer chưa xác định thì PendingVerification; không ghi thưởng | Referral case; M01, M02 | Giữ bằng chứng ai giới thiệu nhu cầu nào trước khi xét thưởng. |
| M05-F02 Kiểm eligibility | Identity/account, lịch sử khách, policy | Self-referral, bên liên quan, khách đã có hoặc tranh chấp phải review theo policy; không auto dựa mã nhập | Eligible/Rejected/Disputed với reason | Tránh trả thưởng cho khách cũ, tự giới thiệu hoặc tranh chấp chưa rõ. |
| M05-F03 Khóa quyền hưởng | Điều kiện attribution lock đã đạt | Snapshot policy/referrer/time; nhiều người nhận theo rule đã duyệt; chưa chốt rule giữ pending | Entitlement snapshot; M10 | Không đổi quyền hưởng lịch sử theo nhân sự hay cấu hình mới. |
| M05-F04 Tính thưởng | Eligible service receipt/allocation | Chỉ nguồn tiền/pool được policy cho phép; tránh cộng trùng sales/referral; replay một effect | Reward ledger/preview; M09, M10 | Chỉ ghi thưởng từ cơ sở đủ điều kiện và không cộng trùng pool. |
| M05-F05 Duyệt và payout | Thưởng đủ điều kiện, approval và kỳ | Chỉ chi số payable chưa trả; khóa kỳ và idempotency như commission; ảnh bill không xác nhận chi | Payout/evidence; Finance | Tách tiền được hưởng khỏi tiền thực sự được duyệt và chi. |
| M05-F06 Đảo và giải quyết | Refund, fraud, dispute, correction | Đảo đúng phần gốc một lần; kỳ khóa ghi adjustment; không xóa khoản đã trả | Reversal/case; M09, M10 | Giữ chi phí thưởng đúng sau hoàn tiền hoặc phát hiện sai phạm. |
| M05-F07 Điểm tùy chọn | Feature points bật, earn/redeem request | Reserve trước redeem; expire/reverse append-only; không âm hoặc thưởng lại do retry | Loyalty_Ledger; portal/consent | Không cho một số điểm được sử dụng hai lần khi đổi thưởng. |

**Màn hình và field:** danh sách referral có status, referrer, buyer/demand, nguồn, ngày khai báo, owner; tab eligibility/evidence, reward preview và payout history. Bắt buộc có scope, định nghĩa new-customer theo policy, nguồn giới thiệu, điều kiện khóa, reward basis và approver trước khi enable thưởng. Readonly gồm snapshot đã khóa, tiền gốc đủ điều kiện, ledger entries, phần đã chi/đảo và timestamps. Mini App chỉ là một giao diện, không là điều kiện kích hoạt referral.

**Trạng thái và commands:** `Submitted → PendingVerification → Eligible → QualifiedForReward → Approved → Payable → Paid`; `Rejected/Disputed` là nhánh có reason/owner; `resolve-dispute` dẫn quyết định mới có evidence. `submit/verify/lock-attribution/approve/pay/reverse` là command riêng. Paid có thể phát reversal/adjustment liên kết, không quay về Draft để sửa số gốc. Điểm dùng `earn/reserve/redeem/release/expire/reverse`, balance là projection ledger.

**Quyền và ngoại lệ:** Marketing đề xuất, Finance duyệt/chi, người hưởng không tự duyệt ngoại lệ khi có đội ngũ. Chưa chốt reward rate, cửa sổ khách mới, điều kiện refund, thuế/chi trả, pool chồng lấn hoặc expiry thì policy Draft và không tự chi. Case manual vẫn ghi nhận được. Shared hotline không chứng minh tự giới thiệu; cần identity evidence. Không đòi consent marketing để nhận xử lý tranh chấp thưởng hợp lệ.

**Nghiệm thu:** `M05-AC01` khách cũ nhập referral code không tự được thưởng; `M05-AC02` refund partial sau payout/replay chỉ đảo đúng phần một lần; `M05-AC03` feature points tắt không tạo hard dependency Loyalty_Ledger trong P0; `M05-AC04` hai redeem đồng thời không dùng vượt điểm khả dụng. **Truy vết:** FR10; UC07/11/13; Referrals, Loyalty_Ledger, Policy_Snapshots, Payment_Allocations, Payout_Batches/Links và Commission_Adjustments khi dùng pool chung. Ca U23-R/U23-L theo feature, CMO-U21/CMO-U26, INT17.

### 3.5 AI Co-Pilot và Agentic CRM

<a id="module-m06"></a>

#### ĐẶC TẢ MODULE M06 — AI Co-Pilot có kiểm soát

**Mục đích, tác nhân và phạm vi:** Sales/AM dùng AI để giảm ghi chép và tìm thông tin đã được phép; reviewer chịu trách nhiệm xác nhận trước ghi trường thương mại hoặc gửi khách. AI owner quản model/prompt/eval; Privacy owner kiểm luồng dữ liệu và vendor. P1 là tóm tắt, rule score và draft; P2 mới xét tự hành. Khi AI tắt, thao tác thủ công vẫn hoàn chỉnh, không có endpoint/tool ngầm hoạt động.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M06-F01 Chọn nguồn | Actor chọn recording/document và mục đích | Nếu không có quyền đọc hoặc không đủ cơ sở dùng thì reject; chỉ lấy phiên bản và phần nội dung cần thiết | Source refs/hash; FR11, M20 | Không gửi cho AI nội dung người yêu cầu vốn không được đọc. |
| M06-F02 Chuẩn bị dữ liệu | Source được phép, vendor/feature policy | Nếu classification/region/retention chưa đạt thì giữ tác vụ thủ công; redact/pseudonymize không tự thành ẩn danh | Payload tối thiểu, policy evidence; Chương 6 | Giảm dữ liệu ra ngoài và chặn vendor/feature chưa đủ điều kiện. |
| M06-F03 STT/tóm tắt | Recording, model/prompt version | Nếu câu mơ hồ/số tiền/ngày hẹn thì đánh dấu cần xác nhận; không ghi đè field gốc | Draft có timestamp/nguồn; FR11 | Giảm ghi chép nhưng không biến lời nghe nhầm thành cam kết. |
| M06-F04 Chấm điểm theo rule | Fit/intent có evidence, rule version | Thiếu dữ liệu là Unknown và giảm coverage; không tự suy ngân sách; rule không dùng thuộc tính nhạy cảm không liên quan | Score/coverage/reasons; FR12 | Ưu tiên chăm sóc có giải thích thay vì suy đoán thiếu căn cứ. |
| M06-F05 Tìm kiếm RAG | Câu hỏi và ACL hiện tại | Chỉ lấy tài liệu đúng scope/version; không có nguồn thì nêu thiếu, không bịa case study/số liệu | Draft có citations; FR12/37 | Tìm lại kiến thức có quyền dùng và chỉ ra được nguồn. |
| M06-F06 Duyệt/áp dụng | Reviewer, draft version, target version | Nếu nội dung/recipient/attachment đổi sau duyệt thì approval cũ không dùng; version conflict phải xem lại | Activity/task hoặc approved intent; FR13, M03 | Người có thẩm quyền xác nhận trước khi draft thành dữ liệu thật. |
| M06-F07 Giới hạn tool | Đề nghị hành động từ model | Export/xóa/đổi quyền không tự thực hiện; refund/giá/hợp đồng không tự approve; tài liệu khách không đổi system instruction | Tool denial/audit; FR13 | Nội dung khách gửi không được trở thành lệnh vượt quyền. |
| M06-F08 Giám sát/tắt | Quota, latency, lỗi hoặc phản hồi reviewer | Vượt quota/circuit mở thì dừng gọi model và cho đường thủ công; không retry vô hạn | Usage/eval/incident; AI owner | Giới hạn chi phí và giữ công việc tiếp tục khi AI lỗi. |

**Màn hình và trường:** Khung trợ lý hiển thị source link/timestamp, model/prompt version, thời điểm, phần chưa chắc chắn và coverage. Khi tạo request bắt buộc task_type, purpose, source refs và target resource; actor/scope do server suy ra. Review hiện draft cạnh nguồn, giá trị cũ/mới và nút chấp nhận từng trường. Gửi khách phải có preview sender, recipient, body, attachment hash và reviewer. 

**Commands và trạng thái:** `request-draft`→Queued→Running→DraftReady hoặc Failed/Cancelled; `review-draft`→Accepted/Rejected; `apply-reviewed-draft` tạo effect có operation key và kiểm quyền/version hiện tại. Rejected giữ evidence theo retention, không âm thầm học lại từ PII. DraftReady không là cam kết với khách; Accepted không tự là email đã gửi. Request đang chạy có cancel/timeout; kết quả đến sau cancel không tự apply. 

**Quyền và ngoại lệ:** AI kế thừa quyền người yêu cầu ở retrieve/apply; service principal không đọc rộng để “giúp” user. Reviewer có quyền hành động đích, quyền cấu hình model không đồng nghĩa đọc call. Prompt injection, vendor outage, nguồn hết quyền và token hết hạn đều có mã lỗi, audit tối thiểu và đường xử lý thủ công. 

**Nghiệm thu:** M06-AC01 — injection/file ngoài scope không mở tool; FR13/37, UC03/14, Entity_Team_Grants/Audit_Logs, U22. M06-AC02 — số tiền/ngày hẹn chưa duyệt không apply; đổi recipient bắt duyệt lại; FR11/13/34, UC19, Activities/Approvals/Outbound_Intents. M06-AC03 — AI off hoặc vendor policy chưa đạt không gửi dữ liệu; đường thủ công còn dùng được; FR11–13, Processing_Records, RV17/WF-U04.

#### 3.5.1 FR11 Tóm tắt cuộc gọi tiếng Việt

**Mục đích và trách nhiệm:** FR11 Call summary — Sales Ops/AI owner. Tiết kiệm ghi chú nếu transcript đúng; sai số tiền/ngày hẹn làm sai cam kết.

**Liên kết đầu vào → đầu ra:** Recording được phép → STT/draft/source timestamp → human-confirmed activity.

**Nghiệm thu và giai đoạn:** Câu phủ định, số tiền, lịch hẹn, người nói và tên riêng; field quan trọng người duyệt; P1.

Ghi âm có cơ sở sử dụng → STT → che dữ liệu không cần thiết → draft nhu cầu/ngân sách/ngày hẹn → người dùng xác nhận. Giữ call_id, model/prompt version, source timestamps và reviewer; không tự ghi dữ liệu thương mại quan trọng từ câu mơ hồ.

Pilot có thể bắt đầu với 60 cuộc được phép dùng, nhiều giọng/nhiễu, nhưng không coi mẫu đó chứng nhận chất lượng tổng quát. Tách tập sửa prompt và tập kiểm; đo exact-match/precision/recall của field quan trọng, omission, unsupported claims và phân biệt người nói. Mục tiêu 95% chỉ có nghĩa trên bộ đo đã định nghĩa; confidence model không tự là xác suất đúng. Số tiền/ngày hẹn cần người xác nhận; không đạt thì chỉ transcript/summary draft. P1 sau lõi.

#### 3.5.2 FR12 Lead scoring và gợi ý hành động

**Mục đích và trách nhiệm:** FR12 Scoring/recommendation — CMO/Sales. Ưu tiên effort khi có nhiều lead; score không thay qualification.

**Liên kết đầu vào → đầu ra:** Fit/intent/coverage/outcome → explainable score → next best action.

**Nghiệm thu và giai đoạn:** Hiển thị lý do, Unknown và override; backtest theo thời gian nếu làm predictive; P1 rule/P2 predictive.

Khởi đầu bằng rule score 0–100: phù hợp dịch vụ 30, nhu cầu rõ 25, ngân sách 20, thời điểm 15, tương tác 10. Thiếu thông tin không đồng nghĩa khách kém; hiển thị coverage và lý do. Không dùng dữ liệu nhạy cảm hoặc đặc điểm không liên quan để chấm điểm. Với 100 lead/tháng, chưa có cơ sở huấn luyện mô hình dự báo đáng tin nếu chưa tích lũy nhãn và outcome đủ đại diện.

AI gợi ý câu hỏi discovery, nhắc phần SOW còn thiếu, đề xuất tài liệu case study có quyền dùng và draft email. RAG chỉ lấy tài liệu đúng tenant, đúng quyền và phiên bản còn hiệu lực; trả kèm nguồn. Khi không có nguồn, phải nêu thiếu thông tin, không tạo số liệu hiệu quả chiến dịch giả.

#### 3.5.3 FR13 Giới hạn agent tự hành

**Mục đích và trách nhiệm:** FR13 AI actions — Product/Privacy. Giới hạn hậu quả của lời gợi ý sai hoặc nội dung độc hại.

**Liên kết đầu vào → đầu ra:** User intent + current ACL + evidence → draft/approved action → tool audit.

**Nghiệm thu và giai đoạn:** Tệp khách chứa lệnh xuất dữ liệu không đổi quyền; đổi recipient sau duyệt bắt duyệt lại; P0 guard/P2 tự hành.

| Hành động | Quyền AI | Bằng chứng nghiệm thu |
| --- | --- | --- |
| Tóm tắt và tạo task nháp | Cho phép trong quyền của người gọi | Có nguồn và không làm mất bản gốc. |
| Chuyển lead theo router cố định | Worker quy tắc làm; AI chỉ gợi ý | Tái chạy không đổi owner trái policy. |
| Gửi email hoặc tin khách | Cần người duyệt ở MVP | Có preview, recipient, nội dung và audit approval. |
| Giảm giá, hợp đồng, hoàn tiền | Không tự phê duyệt | Tool bị từ chối nếu thiếu approval token đúng hành động. |
| Export, xóa khách, đổi quyền | Cấm agent tự thực hiện | Prompt injection trong file khách không mở quyền [S10](#s10). |

Giới hạn ngân sách theo tenant/ngày, timeout 30 giây cho tác vụ đồng bộ, circuit breaker khi lỗi và nút tắt AI. Không đưa khóa API vào prompt. Không cho nội dung chat/tệp khách trở thành chỉ dẫn hệ thống. Kiểm thử injection, rò rỉ chéo tenant và sự cố nhà cung cấp trước khi dùng dữ liệu thật.

### 3.6 Báo giá đơn hàng hợp đồng công nợ và hoa hồng

#### 3.6.1 FR14 Danh mục dịch vụ và báo giá

**Mục đích và trách nhiệm:** FR14 Catalog/quote — Sales + Finance. Chốt giá và lời hứa delivery, tránh bán rẻ/phạm vi mơ hồ.

**Liên kết đầu vào → đầu ra:** Catalog/cost/brief → quote revision + SOW + approval → contract/order.

**Nghiệm thu và giai đoạn:** Sửa lịch thu/số vòng sửa làm xét lại phần approval bị tác động; bản đã duyệt không tự đổi; P0.

Catalog có phiên bản/hiệu lực, đơn vị, gói/phạm vi, loại SERVICE/PRODUCTION/MEDIA_PASS_THROUGH, thuế được kế toán xác nhận, cost estimate và mẫu SOW. Thuế là cấu phần net/tax/gross của dòng, không thay loại dịch vụ. Quote revision giữ price/cost basis, currency, validity, terms, số vòng sửa, đầu ra và phần loại trừ; bản đã gửi/approved bất biến.

Tách preliminary estimate chưa ràng buộc khỏi approved offer. Thiếu cost không mặc định 0/margin 100%; approved offer cần cost hoặc ngoại lệ có quyền. Biên đóng góp = phí dịch vụ thuần − cost trực tiếp theo định nghĩa; tỷ lệ chia cho phí thuần, mẫu số 0 là N/A; ghi rõ trước/sau commission và cost allocation.

Approval theo giá/discount, margin, payment terms, phạm vi, KPI/claim và quyền sở hữu/trách nhiệm. Discount=0 không tự đủ autoapprove. Ngưỡng minh họa 5%/30% chỉ áp sau khi chủ nghiệp vụ chốt; cá nhân self-approval có log, đội ngũ tách người tạo/duyệt ngoại lệ. Đổi field làm mất hiệu lực đúng approval bị tác động; quote expired phải revalidate. Customer acceptance và nội bộ approve là hai mốc riêng.

<a id="module-m07"></a>

#### ĐẶC TẢ MODULE M07 — Danh mục và báo giá

**Mục đích, tác nhân và phạm vi:** Sales lập đề xuất; chuyên môn xác nhận scope/cost; Finance và người có hạn mức duyệt rủi ro; khách chấp thuận offer. P0 quản catalog, quote revision, SOW và approval. Draft AI/estimate không tự thành cam kết giá.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M07-F01 Catalog | Dịch vụ/gói, hiệu lực | Ghi đơn vị/loại phí/thuế/scope; đổi giá tạo version | Catalog snapshot; M16 | Sales và Delivery dùng cùng định nghĩa gói dịch vụ có hiệu lực. |
| M07-F02 Lập quote | Deal, brief, buyer, currency | Tách SERVICE/PRODUCTION/MEDIA và net/tax/gross | Quote/SOW draft; M02 | Khách hiểu rõ giá mua, phạm vi và từng loại phí. |
| M07-F03 Giá/cost | Qty, giá, giảm giá, cost | Cost thiếu là Unknown; mẫu số 0 thì margin N/A | Totals/margin basis; Finance | Tránh bán với biên lợi nhuận giả do thiếu cost hoặc sai thuế. |
| M07-F04 Trình duyệt | Revision/terms/risk | Route theo authority; thiếu policy/ngoại lệ thì chưa approve | Approval requests/audit | Người đủ thẩm quyền xét rủi ro trước khi hứa với khách. |
| M07-F05 Gửi offer | Approved revision/recipient | Kiểm expiry, quyền và tài liệu/policy kênh | Sent evidence; inbox | Chỉ gửi đúng offer được duyệt và còn hiệu lực. |
| M07-F06 Quyết định | Acceptance/rejection evidence | Xác minh authority/thời điểm; hết hạn phải revalidate | Accepted/Rejected; M08 | Chấp thuận phải đến từ người có quyền và đúng phiên bản. |
| M07-F07 Revision | Khách đổi scope/giá/lịch thu | Bản mới; xét lại approval bị tác động, giữ bản cũ | Superseded relation/approval mới | Giữ bằng chứng cam kết cũ khi đàm phán thay đổi. |

**Màn hình và trường:** Catalog theo version; quote editor có line items/SOW/cost/terms; approval inbox có diff/risk; customer preview chỉ phần publish. Bắt buộc Deal/buyer, currency, validity, loại offer, scope và loại phí từng dòng. Binding approval cần cost basis hoặc ngoại lệ, deliverables, quota sửa, acceptance criteria, exclusions/terms. Totals, tax, margin, hash/version và approval history chỉ đọc; sửa bằng draft/revision mới.

**Trạng thái/lệnh:** Draft → PendingApproval → Approved → Sent → Accepted/Rejected; Expired/Superseded theo điều kiện. Internal approval và customer acceptance là hai event riêng. create-revision, submit, approve, reject-approval, publish, record-acceptance, supersede kiểm version/authority; nội dung bản approved/gửi bất biến. API kiểm expiry khi accept/contract, không lệ thuộc cron.

**Quyền/ngoại lệ:** Sales sửa draft trong grant; approve tách edit theo từng chiều giá/margin/terms/scope. Finance không tùy ý đổi lời hứa thương mại. Email forward không tự chứng minh thẩm quyền. Policy discount/margin/thuế chưa chốt giữ Draft, chặn binding offer bị ảnh hưởng; vẫn có estimate nhãn chưa ràng buộc. Discount bằng 0 không tự đủ autoapprove.

**Nghiệm thu:** M07-AC01: thiếu cost không hiện margin 100%. M07-AC02: đổi lịch thu xét lại approval liên quan, bản cũ giữ nguyên. M07-AC03: acceptance sau expiry không được cron chậm cho qua. M07-AC04: replay không sinh thêm revision/contract.

**Truy vết:** FR14/21–23/26; UC05/06/08; Quotes/Quote_Lines, Assets/Approvals, SOW tại 5.13; API 2.5; INT08, CEO-U01–03, WF03.

#### 3.6.2 FR15 Hợp đồng và bàn giao dịch vụ marketing

**Mục đích và trách nhiệm:** FR15 Contract/handoff — AM/Delivery. Không mất lời hứa bán hàng; biết khi nào được bắt đầu và chi tiền.

**Liên kết đầu vào → đầu ra:** Accepted quote + signer + tiền/ngoại lệ + asset access → contract/service period/project.

**Nghiệm thu và giai đoạn:** Tiền đã thu nhưng invoice sync trễ không kẹt giả; cọc chỉ thu một phần chưa tự đủ; P0.

SOW ghi mục tiêu/baseline, deliverable, lịch, quota sửa, tiêu chuẩn nghiệm thu, tài sản/đầu vào khách phải cấp, stakeholder có quyền duyệt, sở hữu và loại trừ. MSA có nhiều SOW/order/project; phụ lục/CR liên kết hợp đồng gốc và version. `document_type` (MSA/CONTRACT/ADDENDUM) khác `service_model` (RETAINER/ONE_OFF).

Won, contract effective, handoff accepted, start authorized, service started, accepted, invoiced và paid là các mốc riêng. Tạo nháp theo SOW/handoff idempotency key, không unique Project chỉ theo contract_id. Kickoff cần hợp đồng hiệu lực, tiền/credit đúng điều khoản, asset/capacity và người nhận xác nhận. Ngoại lệ có người duyệt, hạn, exposure và công việc được làm; cho bắt đầu sáng tạo không tự cho chi media.

Onboarding giữ success plan/sổ cam kết: mục tiêu khách, điều đã hứa, first value, owner, due, communication cadence và evidence. Client-wait ghi interval/reason; lịch dự kiến khác ngày hợp đồng/ngày sự kiện. Quota sửa theo SOW; một vòng là batch feedback; lỗi agency không tự trừ quota đổi ý hoặc ép CR. Acceptance trỏ đúng asset version và approver. Retainer có service periods và notice date; termination chốt khối lượng/nghĩa vụ/công nợ, settlement riêng. Offboarding khách bàn giao tài sản/quyền/records đúng hợp đồng, retention và tranh chấp.

<a id="module-m08"></a>

#### ĐẶC TẢ MODULE M08 — Hợp đồng và onboarding

**Mục đích, tác nhân và phạm vi:** Sales chuyển cam kết cho AM/Delivery; người có thẩm quyền ký/duyệt ngoại lệ; Finance xác nhận funding/credit; AM quản onboarding, review và kết thúc. P0 nối hợp đồng tới khả năng bắt đầu dịch vụ; Won, hiệu lực, Paid và Active là mốc riêng.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M08-F01 Hợp đồng | Accepted quote/SOW hoặc MSA | Kiểm buyer/pháp nhân/signer; phụ lục trỏ bản gốc | Contract/signed evidence; M07 | Xác định đúng các bên, người ký và phạm vi ràng buộc. |
| M08-F02 Kỳ/nghĩa vụ | Terms, order lines | Tạo schedule theo hợp đồng; nhãn media không quyết định thuế | Order/obligations; Finance | Biến điều khoản thương mại thành nghĩa vụ thu có thể theo dõi. |
| M08-F03 Bàn giao | SOW/goals/promises/owner | Người nhận xác nhận; thiếu input thành blocker có hạn | Handoff/Success_Plan; M16 | Không làm mất lời hứa bán hàng khi chuyển sang triển khai. |
| M08-F04 Cho bắt đầu | Hiệu lực/tiền/credit/asset/capacity | Đủ gate authorize đúng scope; thiếu giữ pending/ngoại lệ | Start authorization; media gate riêng | Không bắt đầu vượt tiền, quyền hoặc nguồn lực được phép. |
| M08-F05 Onboarding | Handoff đã nhận | Theo dõi kickoff, asset access, first value, cadence | Checklist/promises; lịch/CX | Giúp khách biết việc cần cung cấp và mốc nhận giá trị đầu tiên. |
| M08-F06 Gia hạn | Notice theo điều khoản | Review giá trị/rủi ro; nhu cầu mới tạo renewal Deal | Lineage; M02/M07 | Ra quyết định tái ký đúng điều khoản thay vì chỉ chạy nhắc ngày. |
| M08-F07 Kết thúc | Termination/expiry | Settlement từng nghĩa vụ; giữ phí/tranh chấp hợp lệ | Adjustments/offboarding; Finance/CX | Chốt công việc, tiền và tài sản khi kết thúc mà không xóa nghĩa vụ. |

**Màn hình và trường:** Contract detail có versions/parties/signers, terms/SOW, kỳ thu, start gates, handoff/notice/offboarding; onboarding board có missing input/owner/due. Bắt buộc pháp nhân ký, buyer, document_type, service_model và nguồn scope. Active cần điều kiện hiệu lực/evidence; evergreen được end date trống đúng terms. Notice có value/unit/basis/timezone; planned date tách committed date. Paid/số dư, signature evidence, approval/gate history chỉ đọc.

**Trạng thái/lệnh:** Contract Draft/PendingSignature/Signed/Active/Expired/Terminated/Cancelled theo 3.13.5; ngày/điều kiện hiệu lực kiểm riêng. create, record-signature, activate, accept-handoff, authorize-start, amend, request-termination, approve-settlement, complete-offboarding kiểm quyền/version. Project idempotent theo SOW/handoff; MSA có nhiều Project. Order Completed/Terminated không tự Paid.

**Quyền/ngoại lệ:** Sales không tự ký thay khách; AM nhận bàn giao và đề xuất renewal khi có commercial permission; Finance xác nhận cash/credit, không thay scope. Cọc một phần chưa tự đủ kickoff. Ngoại lệ có approver/expiry/exposure/phần việc; không tự cho chi media. Invoice sync trễ không chặn ứng trước hợp lệ. Policy chưa chốt giữ Draft, chặn tự động bị ảnh hưởng, chuyển người chịu trách nhiệm rà soát.

**Nghiệm thu:** M08-AC01: replay handoff không nhân Project. M08-AC02: authorize sáng tạo không mở chi media. M08-AC03: reminder theo notice hợp đồng. M08-AC04: termination giữ minimum commitment/invoice hợp lệ và bàn giao tài sản đúng quyền.

**Truy vết:** FR15/16/20/25–26; UC06/08/10/13; Contracts/SOW/Orders/Obligations/Success_Plans tại 5.6/5.13/5.18; 3.13.3–4, WF03.

#### 3.6.3 FR16 Đối soát thanh toán

**Mục đích và trách nhiệm:** FR16 Reconciliation — Kế toán. Tiền thật phải truy được về khách/nghĩa vụ, không cộng lặp.

**Liên kết đầu vào → đầu ra:** Bank/provider/statement → confirmed receipt + match/allocation → balances/ERP/commission.

**Nghiệm thu và giai đoạn:** Cùng giao dịch qua API+sao kê, invoice đến muộn, hai worker phân bổ; tổng không sai; P0.

Tiền chỉ xác nhận từ ngân hàng/provider hoặc sao kê đã kiểm tra; QR/ảnh bill là tham khảo. Một giao dịch canonical có nhiều Payment_Evidence từ API/file; unique connector event không đủ chống trùng xuyên nguồn. Hai giao dịch thật cùng số tiền/ngày/nội dung không bị tự loại bằng fingerprint.

Tách verification_state, matching_state, allocation_state và reconciliation_state. Tiền confirmed vẫn có thể unidentified/unallocated. Phân bổ vào Payment_Obligations thuộc kỳ/dòng hợp đồng; Invoice_Allocation_Links đối chiếu invoice ERP khi có, không tạo cash/commission thêm. Giữ legal entity, tài khoản nhận, payer/buyer, currency. Người trả hộ vào case xác minh; không tự chuyển giữa pháp nhân.

Thứ tự phân bổ: điều khoản/kỳ đã duyệt → chỉ định được kế toán xác nhận → fallback policy được duyệt; chưa đủ cơ sở thì pending. Pro-rata không mặc định đúng mọi hợp đồng. Lock payment/obligation, kiểm số dư, insert allocation/outbox cùng transaction. Dư tiền là credit, partial giữ số còn nợ; refund/reversal liên kết phần gốc và kỳ khóa. Write-off, discount, bank fee có chứng từ là các loại khác; write-off không tạo cash-based commission.

Sales được đề xuất match có evidence, Finance duyệt; reconciliation case có owner/hạn/giải thích và đối soát CRM–ERP–bank. Nhắc nợ xét disputed amount/promise-to-pay và trạng thái ticket. Hóa đơn có nghĩa vụ pháp lý theo bản chất dịch vụ; sync ERP chậm không là quyền trì hoãn hóa đơn. Nhãn MEDIA_PASS_THROUGH không tự quyết định thuế/doanh thu.

<a id="module-m09"></a>

#### ĐẶC TẢ MODULE M09 — Nghĩa vụ thu, tiền, phân bổ và đối soát

**Mục tiêu, tác nhân và phạm vi:** Finance chịu trách nhiệm tiền thật/số dư; Sales đề xuất match; AM đọc nghĩa vụ liên quan; worker nhận evidence. P0 cho nhập sao kê thủ công có kiểm soát; API ngân hàng/ERP P1. Invoice đến muộn không ngăn ghi nhận ứng trước; QR/ảnh bill không xác nhận tiền.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M09-F01 Lập nghĩa vụ | Order_Line/kỳ/terms đã duyệt | Mỗi obligation thuộc một dòng/kỳ; currency/legal entity/buyer rõ; lịch thay đổi qua adjustment | Obligation/schedule; hợp đồng | Biết phải thu khoản nào, từ ai, khi nào và theo điều khoản nào. |
| M09-F02 Nhận bằng chứng giao dịch | API/file, account, transaction ref | Unique nguồn; API và sao kê có thể cùng một receipt; fingerprint không tự xóa giao dịch thật | Evidence/canonical Payment | Không ghi hai khoản thu cho cùng giao dịch xuất hiện ở nhiều nguồn. |
| M09-F03 Xác minh và ghép khoản thu | Evidence và đề xuất buyer/obligation | Verified receipt chưa rõ chủ thể vẫn tồn tại; trả hộ cần case/authority, không đổi pháp nhân để khớp | Confirmed/unmatched case | Tách tiền đã có thật khỏi việc chưa xác định đúng khách/nghĩa vụ. |
| M09-F04 Phân bổ tiền | Receipt confirmed, obligation, amount | Lock kỳ→receipt→obligation, kiểm số dư/scope/party/currency/version; thiếu cơ sở giữ pending; invoice không bắt buộc | Allocation/components/outbox; M10 | Tránh dùng một khoản tiền trả vượt hoặc trả nhầm nghĩa vụ. |
| M09-F05 Đối chiếu hóa đơn | Invoice ERP được xác thực | Mapping chỉ đối chiếu phần tương ứng, không tăng cash/commission; shortfall phân loại phí/discount/write-off | Links/adjustment/reconcile | Đối chiếu chứng từ mà không tạo thêm tiền hoặc hoa hồng. |
| M09-F06 Hoàn tiền | Amount, beneficiary, authority, source | Reserve đúng phần dư/allocated; Unknown không nhả theo TTL; confirm atomic, chỉ allocated mới reverse | Refund/reservations; M10 | Hoàn đúng phần được phép và giữ tiền đang có kết quả chưa rõ. |
| M09-F07 Đối soát và khóa kỳ | Sổ bank/CRM/ERP, cutoff | Posting và close khóa cùng kỳ; còn pending thì release lock và trả Pending/409; không chờ consumer dưới lock | Reconciliation/period snapshot | Đóng sổ có đối soát và không để bút toán lọt vào kỳ đã khóa. |

**Số dư bắt buộc:** C=confirmed receipt; R=confirmed refunds; A=Allocate−Reverse hiệu lực; Ru=active reserve hoàn dư; Ra(a)=tổng reserve phần allocation a. `Available=C−R−A−Ru>=0`; `R+Ru+SUM(Ra)<=C`; `Ra(a)<=A_effective(a)`. Reservation mới r thỏa `r<=A_effective(a)−Ra_existing(a)`. Không trừ Ra hai lần. Confirm hoàn allocated x đồng thời tăng R thêm x và giảm A đi x, giữ available; hoàn dư không tạo reversal giả. Partial/refund giữ components theo nguồn, không đổi media/VAT thành service.

**Màn hình/field:** receipt inbox, sao kê dry-run, matching workbench, allocation preview, obligations/aging, credit/refund cases và close checklist. Nhập bắt buộc account/pháp nhân, amount/currency, nguồn/evidence, occurred_at; allocation thêm obligation/policy/version; refund thêm beneficiary/reason/authority. Readonly: số confirmed, net allocations/reserves/remaining, ledger IDs, timestamps và kỳ khóa. Số phải hữu hạn; currency chỉ từ allowlist đã duyệt; chặn sai quantum trước cast.

**Trạng thái/commands/quyền:** verification Pending/Confirmed/Rejected độc lập matching Unidentified/Identified/Ambiguous và allocation Unallocated/Partial/Full. Commands `verify/propose-match/confirm-match/allocate/reverse/reserve-refund/confirm-refund/adjust/close-period` kiểm quyền riêng; Finance không CRUD tiền gốc; Sales không confirm/chi. Refund thiếu Contract vẫn xử lý được cho receipt chuyển nhầm qua case xác minh. Termination không tự void nợ hợp lệ; kỳ đóng chỉ nhận adjustment kỳ mở có link.

**Nghiệm thu:** `M09-AC01` API+sao kê một giao dịch tạo một receipt; hai khoản thật giống amount giữ đủ; `M09-AC02` hai allocate70 từ receipt100 không commit140; `M09-AC03` receipt100 allocated100 reserve refund20 cho available0, confirm R20/A80, replay không nhân; `M09-AC04` post/close cạnh tranh không ghi vào kỳ đã đóng. **Truy vết:** FR16; UC07/13; Payments, Payment_Evidence, Payment_Obligations/Schedules, Payment_Allocations, Invoice_Allocation_Links, Reconciliation_Cases, Obligation_Adjustments, Refund_Reservations, Finance_Periods; U09–12, INT12, RV07–08, FA02–06.

#### 3.6.4 FR17 Hoa hồng động

**Mục đích và trách nhiệm:** FR17 Commission — Sales + Finance. Minh bạch quyền hưởng, giữ động lực không chi nhầm tiền media/thuế.

**Liên kết đầu vào → đầu ra:** Eligible allocation + policy/share → preview/approval/payout → reversal/period close.

**Nghiệm thu và giai đoạn:** Hoàn một phần, đổi owner sau chốt, nhiều người hưởng và rounding không nhân chi; P0 preview khi có policy.

Base commission = eligible service cash × rate snapshot × share của pool/policy/version. Base loại VAT/media theo chính sách, sau giảm/hoàn; không lấy write-off thành thực thu. Pool hunter/renewal/referral tách và tổng share trong từng pool bằng 1. Policy snapshot truy được; đổi owner/chi nhánh/người trực inbox không đổi quyền hưởng đã chốt.

Preview khác Earned/Approved/Payable/Paid; từng chuyển trạng thái có điều kiện, authority và evidence. Khi tiêu chí chất lượng chưa có, phần liên quan pending; MVP tách base commission và quality bonus/adjustment nếu quy chế cho phép, không mặc định quality_factor=1 để chi. Bút toán số tiền bất biến; workflow status là projection của lịch sử, payout có batch và đối soát riêng.

Ví dụ không thuế: kỳ đã duyệt có 20 triệu service + 80 triệu media, thu 50 triệu và phân bổ pro-rata thì service base 10 triệu, rate5%=pool500.000; share70/30=350.000/150.000. Nếu kỳ đầu chỉ thu media, service base=0. Thiếu policy thì pending. Refund sau payout/kỳ khóa tạo adjustment liên kết, không xóa khoản đã trả hoặc tự khấu trừ ngoài quy chế hợp lệ. Preview mục tiêu ≤60 giây tính từ allocation đủ điều kiện, không từ ảnh bill/QR.

<a id="module-m10"></a>

#### ĐẶC TẢ MODULE M10 — Hoa hồng, quyền hưởng và chi trả

**Mục tiêu, tác nhân và phạm vi:** Finance tính/duyệt/đối soát; Sales xem quyền hưởng bản thân; người có authority phê duyệt policy/pool; worker tính từ allocation. P0 có preview khi chính sách đã duyệt; payout chỉ mở khi có lịch sử chi/đảo và khóa kỳ. Commission không đồng nhất doanh thu, owner hiện tại hoặc attribution marketing.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M10-F01 Chốt policy | Line/pool, basis/rate/share và authority | Snapshot version/hash; thiếu policy giữ PendingPolicy; không trỏ live rule thay snapshot cũ | Policy_Snapshot; quote/contract | Tính thưởng theo quy chế áp dụng lúc phát sinh, không theo rule mới. |
| M10-F02 Chốt người hưởng | Hunter/renewal/referral pool, contributors | Tổng share từng pool=1; kiểm người hưởng hợp lệ; đổi owner không đổi entitlement lịch sử | Pool/shares; nhân sự/grants | Giữ đúng người đóng góp và chia thưởng không vượt pool. |
| M10-F03 Tính preview | Allocation đủ điều kiện và components | Base service cash×rate snapshot×share; loại VAT/media/write-off; production theo rule riêng, không tự0/full | Preview/explanation; M09 | Người hưởng hiểu rõ số tính từ khoản thực thu nào. |
| M10-F04 Xác nhận earned | Evidence eligibility/quality theo policy | Thiếu quality giữ phần liên quan pending; không mặc định factor1 hoặc release do không trả survey | Earned/status event; CX | Không chi quyền hưởng chưa đủ điều kiện chất lượng hoặc chứng cứ. |
| M10-F05 Duyệt/payable | Entry/policy/evidence, period | Đúng authority và kỳ mở; approval không sửa amount đã post; thiếu chứng cứ từ chối có reason | Approved/Payable; Finance | Tách tính toán, phê duyệt và đủ điều kiện chi trả. |
| M10-F06 Chi và reconcile | Payable chưa chi, batch, beneficiary | Reserve phần payout, replay cùng operation một effect; Unknown phải reconcile trước retry | Payout_Batch/Links/Paid | Không chi vượt phần còn được nhận hoặc chi lặp khi timeout. |
| M10-F07 Điều chỉnh | Refund/quality/correction, entry gốc | Partial đảo không vượt phần còn hiệu lực; kỳ khóa ghi adjustment kỳ mở; không sửa Paid hoặc tự khấu trừ trái quy chế | Reverse/Adjustment; M09 | Điều chỉnh đúng sau hoàn tiền mà vẫn giữ lịch sử đã trả. |

**Màn hình/field:** policy và pool setup; bảng preview theo allocation/line/person; tab pending reason; approval queue; payout batch và statement cá nhân. Bắt buộc có scope/pháp nhân/currency, allocation gốc, user, pool, snapshot, base/rate/share/rounding trước posting; adjustment cần source/reason/evidence/authority. Readonly: công thức đã snapshot, cash components, earned/paid/reversed totals và kỳ gốc. `Deals.commission_policy_snapshot_id` chỉ default; `Policy_Snapshots` là đích canonical, không có bảng khác tên CommissionPolicies.

**Trạng thái và commands:** `Preview → Earned → Approved → Payable → Paid` là luồng chuẩn; policy có thể duyệt trước earned nhưng không payable trước cả eligibility và approval. `PendingPolicy/PendingEvidence/Disputed` có owner/review date. `freeze-policy/calculate/mark-earned/approve/release-payable/create-payout/confirm-payout/reverse` là các action riêng. Tiền posted bất biến, trạng thái là projection events; Reverse/adjustment liên kết entry gốc, không rewind entry Paid về Draft.

**Quyền/ngoại lệ:** Sales chỉ xem mình, đề xuất dispute; Finance vận hành theo grant; người hưởng không tự duyệt ngoại lệ khi có đội ngũ. Cá nhân kiêm vai có audit. Chưa chốt rate, quality, production cost basis, holdback hoặc clawback thì policy Draft chặn phần tính/chi tương ứng, không bịa tỷ lệ. Payout phải phối hợp khóa kỳ và reserved balance; gọi provider ngoài transaction, kết quả không rõ giữ reconcile.

**Nghiệm thu:** `M10-AC01` allocation chỉ media/VAT không tạo service commission; `M10-AC02` replay allocation100lần không nhân entry; `M10-AC03` đổi owner/policy không sửa entitlement đã khóa; `M10-AC04` refund partial sau Paid/khóa kỳ chỉ adjustment đúng phần một lần, giữ payout cũ. **Truy vết:** FR17; UC07/13; Commission_Entries, Commission_Pools, Policy_Snapshots, Commission_Status_Events, Commission_Adjustments, Payout_Batches/Links, Finance_Periods; U10–12, INT15, CEO-U12/13/16/23, FA01–03.

### 3.7 CSKH bảo hành dịch vụ và khiếu nại

#### 3.7.1 FR18 Ticket và SLA

**Mục đích và trách nhiệm:** FR18 Ticket — CX Lead. Khiếu nại/sự cố có trách nhiệm và kế hoạch khắc phục.

**Liên kết đầu vào → đầu ra:** Complaint/incident/entitlement → triage/response/resolution → recovery/learning.

**Nghiệm thu và giai đoạn:** Không đóng tự động P1 chỉ vì khách im lặng; reopen không xóa breach; P0.

Ticket tiếp nhận complaint/incident/question/defect/change và liên kết hợp đồng/project/deliverable qua Business_Subjects và các link typed. Entitlement snapshot lưu scope hỗ trợ, calendar, policy, authority và giới hạn. Luôn có intake khiếu nại; chưa rõ Contact dùng provisional và xác minh, không bỏ sự cố khẩn. Lỗi agency khác đổi scope; quota hết không tự từ chối lỗi.

Severity S1/S2/S3 theo impact×urgency và hợp đồng, khác P0/P1/P2 ưu tiên phát triển. Mẫu cần xác nhận: S1 phản hồi30 phút giờ có trực, giảm thiểu4 giờ; S2 phản hồi4 giờ làm việc, phương án1 ngày; S3 phản hồi1 ngày, lịch3 ngày. Không tự cam kết 24/7 khi không có người trực. Major incident có owner, containment/mitigation, affected assets và nhịp cập nhật.

Một engine SLA theo subject/episode gồm first attempt khi áp dụng, FRT, NRT, resolution và promised update; autoack/private note không dừng human clock, tin khách gửi lại không trượt hạn từ tin chưa đáp đầu. Pause theo clock/calendar/policy, pending_internal không tự pause. Reopen nối case gốc trong khoảng chính sách (mẫu7 ngày), giữ breach và remaining business time; không tự reset, không sửa timestamp lịch sử. WaitingCustomer có nhắc/hạn review, đóng no-response theo severity/điều khoản, không đóng S1 mù hoặc coi là đã xử lý. Đóng thread không tự đóng ticket khác.

<a id="module-m11"></a>

#### ĐẶC TẢ MODULE M11 — Ticket và SLA

**Mục đích, tác nhân và phạm vi:** CX/AM tiếp nhận/cập nhật; Delivery xử lý; CX Lead điều phối; Finance duyệt remedy tài chính. P0 quản intake/entitlement/clock/evidence. Người chưa xác minh vẫn báo sự cố khẩn được; không tiết lộ dữ liệu trước khi đủ quyền.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M11-F01 Intake | DM/email/form/call, vấn đề | Chưa rõ người dùng provisional; hết quota vẫn nhận complaint | Ticket/subject/source; M01/inbox | Khách luôn có nơi báo vấn đề, kể cả chưa xác minh đủ hồ sơ. |
| M11-F02 Triage | Impact/urgency/SOW | S1/S2/S3 theo policy, khác P0/P1 backlog | Owner/queue/entitlement snapshot | Xử lý theo tác động và cam kết thay vì thứ tự tin nhắn đơn thuần. |
| M11-F03 Clock | Request/episode/calendar | Một logical episode/clock; bot/note không dừng human clock | FRT/NRT/resolution/promise | Không quên phản hồi, giải quyết và lời hứa cập nhật độc lập. |
| M11-F04 Phản hồi | Message/response targets | Đúng request/criterion mới complete clock tương ứng | Response linkage; inbox | Có bằng chứng phản hồi đúng việc khách đang chờ. |
| M11-F05 Xử lý | Evidence/defect/change/remedy | Defect theo cam kết; change đi CR; refund theo authority | Work M16/Finance/update khách | Phân biệt lỗi agency, đổi phạm vi và remedy cần quyền tài chính. |
| M11-F06 Đóng/reopen | Reason/resolution evidence | Pause từng clock; giữ breach; no-response khác verified | History/closure outcome | Đóng có căn cứ và cho khách quay lại mà không xóa vi phạm cũ. |
| M11-F07 Escalation | Breach/major incident | Owner, containment, cadence; không tự quy lỗi người | Recovery/corrective action | Có người điều phối khi vượt khả năng xử lý thông thường. |

**Màn hình và trường:** Queue theo severity/owner/SLA; detail có sources/scope/entitlement, clocks/promises, remedy và linked work. Intake cần subject/description, Contact/provisional, scope, owner hoặc queue. Triage cần impact/urgency/type; resolve cần code/evidence. Due/breach/elapsed/remaining, entitlement version và message status chỉ đọc. WaitingCustomer cần reason, thông tin đang chờ và review due.

**Trạng thái/lệnh:** Open → InProgress ↔ WaitingCustomer → Resolved → Closed; reopen theo policy, giữ lịch sử. triage, assign, respond, promise-update, request-info, resolve, close, reopen, escalate kiểm version/authority. Status không tự dừng mọi clock. response_targets chỉ request được đáp; đóng thread không đóng ticket khác.

**Quyền/ngoại lệ:** CX/AM thao tác trong grant; Delivery xử lý phần được giao; refund/đền bù cần Finance. Override có reason. Outage/tin muộn/chuyển ca giữ occurred/received, deadline gốc/audit. S1 không tự đóng vì im lặng; hết quota vẫn xử lý defect. SLA/coverage/reopen chưa chốt giữ Draft, chưa bật cam kết tương ứng; không tự hứa 24/7 thiếu người trực.

**Nghiệm thu:** M11-AC01: reply Deal B không dừng clock Ticket A trong cùng thread. M11-AC02: nhiều tin chưa đáp không lùi NRT. M11-AC03: reopen giữ breach/carryover đúng policy. M11-AC04: remedy vượt quyền không thành refund đã hứa.

**Truy vết:** FR18/19/35–36/39; UC09/19–20; Tickets/Business_Subjects/SLA_Episodes/Promises/Message_Subject_Links tại 5.8/5.16/5.18; WF02–04.

<a id="module-m12"></a>

#### ĐẶC TẢ MODULE M12 — Voice of Customer và phục hồi trải nghiệm

**Mục đích, tác nhân và phạm vi:** CX/AM nhận phản hồi, thống nhất biện pháp khắc phục và xác minh kết quả; CMO xem xu hướng để sửa hành trình, Delivery sửa nguyên nhân, Finance duyệt tiền đúng thẩm quyền. P0 có intake/recovery thủ công; P1 thêm khảo sát có kiểm soát. Module không dùng điểm để ép khách sửa đánh giá hoặc tự quy lỗi nhân viên.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M12-F01 Thu feedback | Milestone/ticket/comment hoặc phản hồi trực tiếp | Nếu xác định được case thì link nguồn; chưa rõ người vẫn intake/provisional; score trống không đổi thành0 | Feedback có provenance; FR19, M03 | Giữ tiếng nói khách hàng với đúng nguồn và bối cảnh. |
| M12-F02 Chọn mẫu khảo sát | Touchpoint hoàn tất, eligible cohort | Nếu survey/reopen trùng hoặc cooldown chưa hết thì defer/cancel; không loại khách khó chỉ để đẹp điểm | Candidate/invitation có effect key; FR09/19 | Không làm đẹp điểm bằng cách chỉ chọn khách dễ hài lòng. |
| M12-F03 Gửi khảo sát | Candidate, recipient, question version | Dispatch kiểm purpose/channel/suppression và incident arbitration; không đủ điều kiện thì blocked có reason | Sent/delivered/failed; M03/M20 | Không gửi khảo sát sai thời điểm hoặc khi không còn quyền liên hệ. |
| M12-F04 Tính chỉ số | Responses hợp lệ, metric version | CSAT dùng4–5 trên tổng trả lời1–5; NPS dùng9–10 trừ0–6 theo tập áp dụng; không cộng hai thang hoặc gán im lặng là điểm thấp | Metric/sample/coverage; FR28 | Các phòng ban hiểu cùng cách tính và mức độ đại diện của mẫu. |
| M12-F05 Triage recovery | Feedback thấp/complaint hoặc phát hiện chủ động | Ngưỡng/loại kích hoạt theo policy đã duyệt; trùng incident thì liên kết, không nhân remedy; severity khác ưu tiên phát triển | Recovery owner/due; FR18/19 | Phản hồi tiêu cực trở thành việc có người chịu trách nhiệm. |
| M12-F06 Thỏa thuận biện pháp | Evidence, entitlement, phương án | Nếu refund/đền bù vượt quyền thì chuyển approval; từ chối callback phải đổi cách liên hệ hợp lệ hoặc ghi no-contact | Remedy/promise có authority; FR16/18 | Chỉ hứa biện pháp khắc phục nằm trong thẩm quyền. |
| M12-F07 Xác minh đóng | Evidence đã làm và phản hồi khách | RemedyDone chưa là Verified; không liên hệ được là outcome riêng, không giả khách hài lòng | Closure/reopen history; Ticket/recovery | Phân biệt đã làm biện pháp với việc khách đã được phục hồi trải nghiệm. |
| M12-F08 Sửa nguyên nhân | Root cause, phạm vi tái diễn | Corrective action có owner/due và evidence kiểm lại; không chuyển dữ liệu kháchA sang kháchB trái scope | Learning/checklist cập nhật; FR24/25 | Sửa nguyên nhân để lỗi không lặp lại ở khách khác. |

**Màn hình và trường:** Hàng đợi VoC lọc touchpoint, owner, severity, overdue và trạng thái liên hệ. Feedback bắt buộc source/time, question/scale version khi có score, workspace và subject/context; lưu Contact/Account/role nếu đã xác định. Case recovery bắt buộc reason, owner, review/due, linked feedback/ticket, planned remedy và authority khi liên quan tiền. Review hiển thị điểm gốc bất biến, evidence, lời hứa tiếp theo, no-contact/refused outcome và lịch sử reopen. Dashboard tách eligible/sent/delivered/responded và công bố mẫu/scope/kỳ; B2B giữ vai trò để không ngầm nhân trọng số account nhiều người trả lời.

**Commands và trạng thái:** `record-feedback`, `schedule-survey`, `triage`, `accept-owner`, `record-contact`, `agree-remedy`, `complete-remedy`, `verify`, `close`, `reopen`. Recovery detected→triaged→owner accepted→contacted→remedy agreed→remedy done→verified→closed; rẽ nhánh no-contact/refused giữ reason và người quyết định bước tiếp. Không nhảy thẳng Closed vì đã gọi ba lần; thay due/promise cần history. Request tiền tạo approval riêng, không sửa ledger từ màn hình CX.

**Quyền và ngoại lệ:** AM/CX xử lý account/project được giao; Delivery thấy phần cần sửa, không mặc nhiên đọc mọi phản hồi nhạy cảm; CMO chủ yếu aggregate.  Khách rút quyền marketing không tự xóa nghĩa vụ xử lý khiếu nại hợp lệ; từng liên hệ xét mục đích riêng. 

**Nghiệm thu:** M12-AC01 — close/reopen/replay không spam hoặc sửa điểm gốc; FR19, UC09, Feedback/Journey_Instances. M12-AC02 — refused callback không gọi tiếp; refund vượt quyền phải approval, recovery vẫn có owner; FR18/19, UC09/13, Recovery_Cases/Approvals, CX-U15. M12-AC03 — im lặng không thành0/Verified; closure có evidence và corrective action không leak; FR19/24/28, UC09/16, Feedback/Recovery_Cases/Corrective_Actions.

#### 3.7.2 FR19 CSAT và NPS

**Mục đích và trách nhiệm:** FR19 Voice of Customer — CX + CMO. Biết trải nghiệm thực và sửa nguyên nhân, không chỉ thu điểm.

**Liên kết đầu vào → đầu ra:** Touchpoint/survey/comment/ticket → feedback + recovery action → verify/root cause.

**Nghiệm thu và giai đoạn:** Điểm thấp có owner/hạn/closure evidence; chống chọn mẫu làm đẹp; P1 survey, P0 recovery.

Thu feedback ở milestone/onboarding/ticket và quan hệ, lưu nguồn/câu hỏi version/role/contact/account. CSAT1–5, tỷ lệ4–5 trên người trả lời; NPS %9–10−%0–6 theo tập đủ trải nghiệm, kỳ90 ngày là cấu hình. CES chỉ thêm ở tương tác có mục tiêu giảm effort; không cộng ba thang thành điểm chung. Báo eligible/sent/delivered/responded và sample, không trả lời khác điểm0.

Survey có unique business effect, recheck consent/channel, cooldown contact/account và arbitration với incident; một close replay không spam, reopen trước gửi xét lại. Không chỉ chọn khách dễ cho điểm cao; B2B ghi vai trò và view account-level tránh account nhiều contact bị nhân trọng số ngầm.

Recovery: detected → triaged → owner accepted → contacted → remedy agreed → remedy done → verified → closed. Có due, evidence, quyền duyệt refund/đền bù, no-contact/refused callback là kết quả riêng; không sửa điểm gốc hoặc ép khách đổi điểm. Root cause theme dẫn corrective action có owner và kiểm tái diễn, nối lại launch checklist, lời hứa Sales, scope và renewal.

### 3.8 Thực địa và chi nhánh

#### 3.8.1 FR20 Lịch hẹn và check-in

**Mục đích và trách nhiệm:** FR20 Appointment/field — Sales/AM. Hẹn đúng người/nguồn lực, giảm no-show và lỡ lịch.

**Liên kết đầu vào → đầu ra:** Availability/request → booking/confirmation → meeting/activity.

**Nghiệm thu và giai đoạn:** Double booking và đổi lịch không để reminder cũ gửi tiếp; P0 lịch/P2 GPS.

Agency ưu tiên lịch discovery, kickoff, quay chụp và nghiệm thu tại khách; tài nguyên gồm nhân sự, phòng họp và ekip. Chặn lịch trùng, lưu timezone, địa điểm, contact, mục đích và trạng thái xác nhận. Check-in GPS chỉ tại thời điểm công việc được cho phép; không theo dõi liên tục ngoài ca. Nếu khách từ chối vị trí hoặc GPS sai, cho nhập lý do và bằng chứng thay thế, quản lý xác nhận.

<a id="module-m13"></a>

#### ĐẶC TẢ MODULE M13 — Lịch hẹn và tài nguyên

**Mục đích, tác nhân và phạm vi:** Sales/AM đặt discovery/kickoff/nghiệm thu; Delivery đặt ekip; điều phối quản tài nguyên. P0 lịch khi sử dụng; reservation khi thực quản nguồn lực; calendar connector P1, GPS P2. Availability không thay ngày cam kết với khách.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M13-F01 Availability | Khoảng thời gian/người/timezone | Kiểm calendar/quyền; stale hiện chưa đủ dữ liệu | Slot gợi ý; M02/M08/M16 | Đề xuất giờ phù hợp mà không giấu dữ liệu lịch đang thiếu. |
| M13-F02 Tạo lịch | Subject/participants/start/end | End sau start; kiểm scope/liên hệ | Appointment Tentative/version | Lịch hẹn có đủ người, mục đích và mốc thời gian rõ ràng. |
| M13-F03 Giữ resource | Resource/range/TTL policy | Độc quyền chặn overlap atomic; pool cần capacity model | Booking Hold; capacity | Không bán trùng một ekip hoặc phòng cho hai cuộc hẹn. |
| M13-F04 Xác nhận | Confirmation/booking version | Recheck TTL/capacity; lỗi không confirm giả | Confirmed/reminder intent | Không xác nhận tài nguyên đã hết thời gian giữ chỗ. |
| M13-F05 Đổi/hủy | Slot mới/cancel reason | Version mới, nhả slot cũ, hủy reminder cũ | Booking/history; inbox | Không gửi nhắc lịch cũ sau khi khách đã đổi hoặc hủy. |
| M13-F06 Outcome | Completed/no-show/evidence | Thiếu GPS không tự là no-show; ghi next action | Activity; Sales/Delivery | Kết quả cuộc hẹn dẫn tới hành động tiếp theo có căn cứ. |
| M13-F07 Check-in | GPS được phép/evidence thay thế | Chỉ thu lúc công việc; cho giải trình khi từ chối/sai vị trí | Evidence/retention | Có bằng chứng công việc mà không buộc theo dõi vị trí liên tục. |

**Màn hình và trường:** Calendar ngày/tuần theo người/resource/địa điểm; booking drawer có conflict/hold expiry; detail có subject/participants/reminder/history. Bắt buộc type/title, owner, subject phù hợp, start_at/end_at/timezone và mục đích; địa điểm hoặc meeting link khi áp dụng. Participants có vai trò, contact data theo quyền. Conflict result, nguồn/freshness, expiry/audit là chỉ đọc; không sửa tùy ý provider/reminder status.

**Trạng thái/lệnh:** Appointment Tentative/Confirmed/Cancelled/Completed/NoShow; booking Hold/Confirmed/Released/Expired. create-appointment, hold-resource, confirm, reschedule, cancel, record-outcome, check-in kiểm quyền/version. Confirm kiểm TTL dù sweeper chưa chạy. Khoảng [start,end) cho lịch chạm mốc liên tiếp; không cho overlap resource độc quyền.

**Quyền/ngoại lệ:** Người đặt sửa trong grant; điều phối override có policy/audit, không vượt sức chứa vật lý. Shared resource giữ identity chung qua workspace; xem lịch không mở toàn hồ sơ khách. Connector timeout hiện pending/unknown và đối soát. TTL/ca/reminder/GPS chưa chốt giữ Draft, chặn tự động tương ứng; vẫn ghi lịch thủ công có kiểm tra phù hợp.

**Nghiệm thu:** M13-AC01: booking cạnh tranh chỉ một thành công. M13-AC02: hold hết hạn chưa sweep không confirm mù. M13-AC03: đổi/hủy chặn reminder cũ. M13-AC04: từ chối GPS có evidence thay thế, không tự no-show.

**Truy vết:** FR20/25/34; UC06/08/20; Appointments/Resources/Resource_Bookings/Availability tại 5.13/5.18; RV04/CEO-U21 và WF05.

<a id="module-m14"></a>

#### ĐẶC TẢ MODULE M14 — Tổ chức, nhóm và quyền vận hành

**Mục đích, tác nhân và phạm vi:** Ops/quản lý giao việc và bàn giao giữa Sales, AM, Delivery, Finance mà giữ đúng tenant/workspace/pháp nhân; người có thẩm quyền cấp quyền kiểm soát role/grants. P0 có user, membership, delegation và scope; chi nhánh thứ hai chỉ mở khi vận hành thực. Scorecard nhân sự ở FR27 là P2, không kéo payroll/hồ sơ sức khỏe vào CRM.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M14-F01 Thiết lập tổ chức | Tenant, branch/legal entity/workspace thật | Nếu chỉ một pháp nhân/chi nhánh thì dùng mặc định; không dùng branch thay legal entity hoặc workspace | Org catalog và policy; FR21 | Tránh lẫn chi nhánh vận hành, pháp nhân ký và phạm vi dữ liệu. |
| M14-F02 Gán membership | User/team/branch, role, effective dates | Chỉ grantor có authority được cấp; role cấu hình không cho tự nâng business access; expiry phải có hiệu lực thực | Membership/version/audit; SEC06 | Người dùng nhận đúng vai trò theo người có quyền cấp. |
| M14-F03 Chia sẻ hồ sơ | Resource typed, actions/fields, principal, thời hạn | Nếu ngoài tenant/scope hoặc vượt quyền cấp thì reject; Account grant không mở toàn CLIENT/tài chính | Entity_Team_Grants; FR08/21/37 | Phối hợp được trên hồ sơ cần thiết mà không mở toàn bộ dữ liệu khách. |
| M14-F04 Kiểm quyền | API/search/job/file/AI action | RBAC và ABAC cùng đạt, deny thắng allow; thiếu context thì fail closed; job kiểm lại khi chạy | Allow/deny có reason nội bộ; Chương 6 | Cùng một quyền được áp dụng ở giao diện, API và tác vụ nền. |
| M14-F05 Ủy nhiệm/thay ca | Khoảng vắng, backup và open work | Backup cần quyền đúng nhiệm vụ; không tự đổi Deal owner, pháp nhân hay commission lịch sử | Delegation/handoff; FR05/35 | Người thay ca tiếp tục việc mà không chiếm quyền thương mại lịch sử. |
| M14-F06 Chuyển/nghỉ việc | Quyết định đã xác nhận, effective time | Revoke session/grants trước chuyển open work; không người nhận thì queue quản lý; giữ actor cũ | Checklist/bàn giao; UC12 | Không mất công việc đang mở khi nhân sự chuyển hoặc nghỉ. |
| M14-F07 Capacity/cost | Availability và cost rate có hiệu lực | Chỉ dùng phục vụ staffing/margin khi có quyền; thiếu rate là Unknown, không suy thành0; không lộ lương | Capacity/cost snapshot; FR25/27 | Biết khả năng giao hàng và chi phí mà không lộ hồ sơ lương. |
| M14-F08 Scorecard | Metric/role/sample/context được duyệt | Chỉ khi P2 bật và dữ liệu đủ; thiếu dữ liệu không xếp hạng, không tự phạt theo số thao tác | Coaching/review; FR27/28 | Đánh giá công việc có bối cảnh và quyền giải trình. |

**Màn hình và trường:** Danh sách tổ chức hiển thị tenant, workspace type, branch, pháp nhân và active dates riêng. Cấp quyền bắt buộc principal, resource/scope, role/actions/fields, from/until theo policy, grantor/authority và reason; quyền nhạy cảm cho chính mình cần approval tách người khi có đội ngũ. Preview quyền hiệu lực giải thích nguồn Allow/Deny cho người có quyền quản trị, không lộ dữ liệu nghiệp vụ. Màn hình bàn giao gom lead, deal, thread, ticket, promise, appointment, scheduled intent và approval đang chờ; người nhận phải xác nhận phần thuộc trách nhiệm.

**Commands và trạng thái:** `invite`, `activate-user`, `grant`, `revoke`, `delegate`, `expire-grant`, `transfer-work`, `offboard` kiểm version/authority và audit. User Invited→Active→Suspended/Offboarded; reactivation là command có review, không hồi sinh mọi grant cũ. Grant Draft nếu cần duyệt→Active→Expired/Revoked; không gia hạn âm thầm để né deny. Team membership không là đường vòng cấp quyền. 

**Quyền và ngoại lệ:** Admin kỹ thuật quản connector/config được cấp nhưng không tự gán Finance/Privacy. CEO đọc báo cáo theo nhu cầu, không sửa tiền gốc. Finance nhận các command tài chính và chứng cứ tối thiểu; AM có commercial permission mới tạo/sửa renewal Quote. B2C chia sẻ Contact/Deal trực tiếp, không tạo Account giả.  Revoke phải lan tới permission version/cache và download request mới.

**Nghiệm thu:** M14-AC01 — role conflict/shared Account giữ deny/scope; FR21/37, UC14, Entity_Team_Grants, INT29/U17. M14-AC02 — Admin tự cấp Finance hoặc manager cấp ngoài branch bị chặn; FR21, Users/Teams/Audit_Logs, SEC-U06. M14-AC03 — offboarding giữ actor, revoke token, open work có người/queue; thiếu dữ liệu không xếp hạng; FR08/21/27/35, UC12/20, Conversation_Assignments/Entity_Team_Grants, U16.

**Bổ sung Work Management 1.7:** M14 quản authority giao việc/duyệt/ủy nhiệm theo 6.6, không coi membership hoặc chức danh cấp trên là quyền xem mọi private/client task. Offboarding phải chuyển cả task đang mở, assignment offer, review đang chờ, queue manager và owner của template/recurrence; không chỉ chuyển lead/deal. Lịch sử actor giữ nguyên; thiếu người nhận thì queue quản lý chịu trách nhiệm.

#### 3.8.2 FR21 Phân quyền hai chi nhánh

**Mục đích và trách nhiệm:** FR21 Branch/team — Ops/Privacy. Bàn giao/phối hợp đúng quyền khi mở rộng.

**Liên kết đầu vào → đầu ra:** Org/team/grants → scope/assignment → reporting/handoff.

**Nghiệm thu và giai đoạn:** Khách shared account, hai branch và thu tiền theo pháp nhân đúng; P0 scope/P1 vận hành hai nhánh.

Scope theo tenant/workspace/branch/legal entity và row/field policy. Tạo branch/pháp nhân mặc định khi thực tế đơn; dữ liệu Contact/Account có thể dùng chung theo grant, Deal/Project/Ticket có phạm vi riêng. Không ép branch NOT NULL cho mọi danh mục/shared record; giao dịch có trách nhiệm chi nhánh thì phải phân nhánh rõ.

Account/Contact/Deal/Project team grants có role, action/field scope, thời hạn và actor. B2C không cần Account giả để chia sẻ. Membership account không tự cho xem mọi CLIENT workspace hay tài chính agency. Deny thắng Allow là policy của dự án, phải PoC nền tảng có role merge khác. Quyền approve độc lập edit; Admin không mặc định đọc nghiệp vụ, CEO không sửa ledger bằng vai quản trị.

Chuyển nhánh bàn giao active work/promises/appointments/tickets, giữ đúng pháp nhân công nợ và commission lịch sử. Mọi đường API/search/count/file/export/AI và background job kiểm quyền hiện tại; break-glass có TTL/audit. Không dùng đổi branch để di chuyển công nợ.

### 3.9 Quản trị chiến lược marketing và IMC

#### 3.9.1 FR22 Chuỗi chiến lược đến thực thi

**Mục đích và trách nhiệm:** FR22 Strategy/IMC — CMO/Strategist. Delivery phải phục vụ mục tiêu đã thống nhất, không chỉ có lịch đăng.

**Liên kết đầu vào → đầu ra:** Business goal/baseline/brief → approved plan/version → scope/campaign/measurement.

**Nghiệm thu và giai đoạn:** Gói thiết kế nhỏ không đi đủ nghiên cứu lớn; goal thay đổi có impact review; P0 brief/P1 full.

CRM giữ chuỗi business goal/baseline → brief/giả thuyết → SOW → approved plan → campaign/deliverable → measurement → learning. Mỗi quyết định có owner, version, nguồn và tiêu chí; phân biệt kết quả cam kết với mục tiêu kỳ vọng. Scope template chọn mức bắt buộc theo gói; logo/job nhỏ không phải đi đủ nghiên cứu chiến lược lớn.

Tài liệu strategy/IMC chi tiết có thể ở Slides/Sheets/Figma; CRM giữ link phiên bản hoặc snapshot/checksum, người duyệt, thời điểm và approved scope. URL thay đổi được đơn lẻ chưa đủ evidence. Không bắt nhập lại toàn bộ message house/content matrix. P0 brief/SOW/goals gọn; editor và schema chiến lược đầy đủ chỉ mở theo nhu cầu P1/P2.

#### 3.9.2 FR23 Điều kiện phê duyệt và launch

**Mục đích và trách nhiệm:** FR23 Launch gates — CMO/AM. Ngăn chạy sai asset, sai ngân sách/quyền/tracking.

**Liên kết đầu vào → đầu ra:** Scope/budget/asset/tracking/account access → go/no-go → launch evidence.

**Nghiệm thu và giai đoạn:** Creative được thay thì approval cũ không dùng; tăng chi vượt quyền bị chặn/escalate; P0 nếu quản campaign.

Campaign chỉ Live khi đạt gate áp dụng của scope template: approved scope, budget owner và funding/credit, asset đúng version, tracking đã test nếu có measurement, quyền tài khoản, lịch và người phụ trách. Người duyệt creative khác quyền tăng chi. Logo không media không đòi tracking pixel.

Approval gắn subject/version/hash, chiều rủi ro, authority, cap/expiry và evidence (email gốc nếu dùng). Dependency map làm mất hiệu lực đúng approval bị ảnh hưởng khi đổi offer/claim/audience/ngân sách/terms. Trong optimization envelope đã duyệt có thể tinh chỉnh và audit không xin lại từng lần; vượt envelope cần duyệt. Emergency pause có quyền/playbook; CRM chặn nút không tự chặn thao tác bên Ads Manager, cần least privilege ngoài kênh và đối soát spend. API chưa hỗ trợ thì tác vụ thủ công/evidence, không giả đã điều khiển được.

#### 3.9.3 FR24 Nghiên cứu thử nghiệm và học hỏi

**Mục đích và trách nhiệm:** FR24 Experiments/learning — CMO. Không kết luận hiệu quả từ dao động nhỏ, giữ lý do quyết định.

**Liên kết đầu vào → đầu ra:** Hypothesis/baseline/design → result/limitations → approved learning.

**Nghiệm thu và giai đoạn:** Chưa đủ mẫu không gán winner; bài học khách A không chia sẻ trái quyền cho B; P1 mẫu/P2 engine.

Giữ nhật ký hypothesis, biến/đơn vị thử, population, KPI/guardrail, baseline, window, budget, stop rule và decision evidence. Khi định lượng cần thiết kế sample/contamination/time horizon thích hợp, không đổi chỉ số sau khi thấy kết quả. 100 lead agency ít không suy mọi campaign khách cũng ít mẫu; thiếu mẫu ghi chưa kết luận, không ép winner.

Learning có source, owner, confidence/limitations, ngày áp dụng và scope quyền. Root cause từ CX nối cải tiến checklist/strategy; không sao creative/data khách A sang B trái quyền. P0/P1 mẫu và decision log nhẹ; experiment orchestration nâng cao P2.

<a id="module-m15"></a>

#### ĐẶC TẢ MODULE M15 — Brief, chiến lược, IMC và phê duyệt launch

**Mục tiêu, tác nhân và phạm vi:** Strategist/CMO lập phương án; AM giữ cam kết khách; Delivery triển khai; Finance duyệt ngân sách; khách có authority duyệt phạm vi/asset. P0 là brief/SOW/goal và gate phù hợp gói; strategy editor đầy đủ P1, experiment engine P2. Job logo không bị ép nhập research/ads tracking không áp dụng.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M15-F01 Chọn template | Dịch vụ, brief, hợp đồng/scope | Chỉ yêu cầu field/gate áp dụng; N/A có reason; thiếu nguồn ghi Unknown thay số giả | Brief/checklist; quote/handoff | Job nhỏ không phải đi quy trình nặng không phục vụ khách. |
| M15-F02 Chẩn đoán và mục tiêu | Baseline, research, constraints | Phân biệt fact/assumption/target/commitment; bằng chứng có scope/quyền dùng | Diagnosis/goal version; M18 | Phân biệt dữ kiện, giả định và điều agency thực sự cam kết. |
| M15-F03 Lập strategy/IMC | Audience, positioning, message, kênh | Nối goal→SOW→campaign/deliverable→KPI; không nhân bản tài liệu chi tiết đang do Slides/Sheets quản | Approved plan refs/checksum | Mọi đầu ra và kênh thực thi phục vụ mục tiêu đã thống nhất. |
| M15-F04 Duyệt rủi ro | Subject/version/hash, approver | Creative approval không cho tăng chi; đổi claim/audience/budget/terms invalidate đúng approvals phụ thuộc | Approval trail; M17 | Không dùng một loại phê duyệt để vượt sang rủi ro khác. |
| M15-F05 Quyết định launch | Scope/budget/funding/assets/tracking/access | Gate áp dụng phải Pass; Fail trọng yếu chặn; API không hỗ trợ thì manual evidence, không giả đã chặn Ads UI | Go/NoGo/launch record | Ngăn phát hành sai asset, ngân sách, tracking hoặc quyền tài khoản. |
| M15-F06 Tối ưu và pause | Kết quả/cost/freshness, envelope | Trong envelope được duyệt thì audit; vượt quyền duyệt lại; stale data không tự tắt/chạy thêm | Change/pause task; campaign/CX | Cho phép tối ưu có kiểm soát và dừng khi có rủi ro. |
| M15-F07 Thử và học | Hypothesis, unit, KPI/window, result | Chưa đủ thiết kế/mẫu không declare winner; không đổi KPI sau xem số; lesson không chia sẻ trái scope | Learning/decision; M18 | Giữ bài học có bằng chứng thay vì kết luận thắng từ mẫu quá nhỏ. |

**Màn hình/field:** brief theo gói; bản đồ goal–scope–campaign; approval queue; launch checklist; experiment/learning log. Bắt buộc có scope/customer, owner, service template, goal, source baseline hoặc Unknown+task, SOW/version, approver/authority, plan ref/snapshot; launch bổ sung budget/funding, asset versions, access và tracking evidence khi áp dụng. Readonly: approved hash/version, quyết định client, dependency invalidations, launch/pause timestamps. URL mutable đơn lẻ không đủ làm evidence bản đã duyệt.

**Trạng thái/commands:** brief/plan `Draft → InReview → Approved → Superseded/Archived`; rejected trả Draft bằng revision có history. Campaign `Draft → Ready → Live → Paused → Completed/Cancelled`; `mark-ready/launch/pause/resume/complete` kiểm gates và version hiện tại, resume xét lại expiry/quyền. Experiment `Draft → Approved → Running → Concluded/Inconclusive/Stopped`; không dùng nhãn Winner thay kết luận có điều kiện. Hợp đồng hiệu lực, creative approved và Live là ba mốc khác nhau.

**Quyền/ngoại lệ:** người soạn không tự có authority claim/budget; client chỉ duyệt đúng project/role; AM không được hứa performance vượt SOW. Thiếu research không đồng nghĩa phải chặn mọi job: theo template, giữ assumption có owner xác minh. Claim không có căn cứ, asset sai phiên bản hoặc thiếu tiền/quyền bắt buộc thì NoGo. Ngưỡng tối ưu, stop rule và sample chưa chốt giữ Draft, chặn tự động hóa; quyết định manual có authority/evidence.

**Nghiệm thu:** `M15-AC01` creative v2 không launch bằng approval v1; `M15-AC02` logo không ads dùng N/A tracking hợp lệ; `M15-AC03` thay budget vượt envelope cần duyệt lại; `M15-AC04` mẫu nhỏ không tuyên bố winner chắc chắn hoặc sao dữ liệu khách A sang B. **Truy vết:** FR22–24; UC04/08/16; Strategy_Briefs, Marketing_Plans/IMC_Plans, Campaigns, Assets/Asset_Versions, Approvals, Experiments, Learning_Items; U19, INT16/INT22, CMO-U11–CMO-U15/CMO-U24.

### 3.10 Quản trị chiến dịch công việc và nguồn lực

#### 3.10.1 FR25 Quản lý công việc dùng chung và capacity

**Mục đích và trách nhiệm:** FR25 Work Management — Ops/Team Lead/Project Manager. Quản lý việc cá nhân, nội bộ, follow-up CRM và dự án bằng Task Core chung, rõ trách nhiệm, hạn và kết quả; Delivery Lead quản thực thi đầu ra khách hàng.

**Liên kết đầu vào → đầu ra:** Nhu cầu cá nhân/team/CRM/SOW/milestone → Task Core và assignment → thực hiện/review/completion; client acceptance và effort/cost là nghiệp vụ liên kết riêng.

**Nghiệm thu và giai đoạn:** P0 gồm W-F01–09 tại 3.14 và milestone/deliverable; P1 capacity theo giờ, Gantt, portfolio nâng cao. Claim/review/recurrence không nhân hiệu ứng, ACL không bị mở ngầm; nghỉ phép/khách chờ không bị tính thiếu năng suất. W-T01–40 tại 9.16 áp theo capability được phát hành.

P0 quản Task Core dùng chung: việc độc lập hoặc có context, giao/nhận/chuyển, My Work/Team Board, due và gia hạn, result/review, checklist/subtask, dependency Finish-to-Start, template/calendar recurrence. Giữ milestone/deliverable, QA và client acceptance riêng. Mặc định CRM là nguồn ghi task ở pilot; nếu project dùng PMS đã chọn thì khai báo source authority và mapping 5.20/UC-W10 trước bật, không hai master ghi đè.

Capacity có skill/calendar/availability, soft reservation trước chốt lớn và allocation sau kickoff; việc vắng mặt/khách chờ không tự thành KPI yếu. Task P0 có definition of done, dependency không cycle, reviewer/evidence. Estimate/actual có thể chưa nhập ở P0; lập kế hoạch effort chi tiết và availability thuộc P1, thiếu dữ liệu không coi bằng 0. Timesheet chỉ bật khi cần tính cost/capacity và lợi ích hơn nhập liệu; có thể dùng summary cost kiểm tra ở giai đoạn nhỏ. Rework do defect khác change; đổi scope đánh giá date/resource/cost và approval.

<a id="module-m16"></a>

#### ĐẶC TẢ MODULE M16 — Quản lý công việc, dự án và nguồn lực

**Mục đích, tác nhân và phạm vi:** Nhân viên quản việc cá nhân; Team Lead/PM giao việc nội bộ/dự án; Sales/AM quản follow-up; reviewer kiểm kết quả; approver khách nghiệm thu riêng. P0 Task Core và delivery, P1 effort/capacity chi tiết; timesheet khi có nhu cầu. Quy tắc nguồn ghi ở FR25. M16-F01–07 dưới đây giữ phần delivery; W-F01–14 và 3.14 đặc tả phần công việc dùng chung, không tạo module/task engine thứ hai.

| Chức năng | Kích hoạt / đầu vào | Xử lý nếu / thì | Đầu ra và liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M16-F01 Nhận project | Handoff/SOW/authorization | Cùng key không tạo lại; thiếu gate giữ PendingStart | Project/baseline; M08 | Triển khai đúng SOW được bàn giao và không nhân dự án khi replay. |
| M16-F02 Kế hoạch | Deliverable/due/owner/reviewer | Dependency không cycle; task khác đầu ra khách mua | Milestones/tasks; lịch/capacity | Có người chịu trách nhiệm và thấy được công việc phụ thuộc. |
| M16-F03 Tạo/QA | Asset version/checklist | Chưa clean/QA chưa publish; giữ version cũ | InternalReview/ClientReview; assets | Chỉ đưa đầu ra đã kiểm tra đúng phiên bản tới khách. |
| M16-F04 Feedback | Batch feedback/SOW | Defect theo cam kết; đổi ý theo quota/CR, không trừ lặp | Revision_Batches/work | Tách sửa lỗi phải làm khỏi yêu cầu mới cần đổi phạm vi. |
| M16-F05 Nghiệm thu | Version/hash/authority/decision | Task Done chưa Accepted; sai quyền giữ pending | Acceptance; billing/CX | Chứng minh khách có thẩm quyền đã duyệt đúng đầu ra. |
| M16-F06 Block/replan | Thiếu input/nghỉ/đổi scope | Lưu interval; không tự dời ngày hợp đồng; đánh giá CR | Forecast/resource plan | Hiện rủi ro trễ mà không âm thầm đổi ngày đã cam kết. |
| M16-F07 Effort/capacity | Availability/estimate/actual/rate | Tránh double allocation; thiếu cost là Unknown; giữ snapshot | Load/cost summary; margin | Không nhận việc vượt nguồn lực hoặc tính margin từ cost bị thiếu. |

**Màn hình và trường:** Overview có scope/start gate/milestone/risk/promises; delivery board có owner/reviewer/QA/feedback; review có version/decision; capacity view theo feature. Client delivery project bắt buộc contract/SOW/handoff link theo gate M08 cùng scope, owner, deliverable, planned/committed due riêng và acceptance criteria. Internal project không bắt hợp đồng; personal/internal/CRM task độc lập không bắt project. Field và validation cho Task Core ở 3.14. Publish cần asset sạch/version, reviewer và approver theo SOW. Baseline duyệt, acceptance, quota đã dùng, cost snapshot và sync source/version chỉ đọc; đổi bằng lệnh có history.

**Trạng thái/lệnh:** Project Draft/PendingStart/Active/Blocked/Completed/Terminated; deliverable Planned/InProgress/InternalReview/ClientReview/Rework/Accepted. plan, assign-work, submit-QA, publish-review, classify-feedback, request-change, record-acceptance, block, replan, complete kiểm quyền/version/gate. Replan không ghi đè committed date; đổi baseline cần CR được duyệt. Completed không tự Paid/đóng ticket.

**Quyền/ngoại lệ:** Delivery sửa work/asset được giao; AM điều phối; khách thấy phần publish; acceptance theo authority cụ thể. PMS conflict vào đối soát, không last-write-wins hai master. Chậm feedback ghi blocker; defect không ép mua CR. Availability/cost/timesheet policy chưa chốt giữ Draft, chặn automation bị ảnh hưởng nhưng vẫn vận hành milestone cơ bản.

**Nghiệm thu:** M16-AC01: MSA nhiều SOW tạo đúng project, replay không nhân bản. M16-AC02: Done không tự nghiệm thu, sai version bị chặn. M16-AC03: hết quota vẫn sửa defect; change có CR. M16-AC04: client-wait không tự dời sự kiện hoặc quy nhân viên kém năng suất.

**Truy vết:** FR15/18/23/25–27; UC-W01–10 cho Task Core tại 4.23 và W-T01–40 tại 9.16; UC06/08/09/16 cho delivery; Projects/Tasks/Deliverables/Acceptances/Change_Requests/Availability/Client_Wait_Intervals/Revision_Batches tại 5.13/5.18; WF03.

#### 3.10.2 FR26 Ngân sách và campaign health

**Mục đích và trách nhiệm:** FR26 Budget/health — Finance + CMO. Giữ tiền và phát hiện rủi ro theo objective.

**Liên kết đầu vào → đầu ra:** Approved budget/commitments/actual/KPI freshness → forecast-at-completion/alerts.

**Nghiệm thu và giai đoạn:** Dữ liệu stale=Unknown; PO thành invoice không giảm budget hai lần; P0 cơ bản/P1 forecast.

Tách agency acquisition spend, agency service economics, client media spend và client business outcomes bằng namespace/scope/beneficiary. Budget line có owner, cost bearer, funding/credit, category, currency, tax basis, kỳ và approval. Available = approved − actual − outstanding commitment khi cùng basis; commitment chuyển actual chỉ giảm phần được thay thế, không cộng đôi. Estimate to complete/contingency ghi riêng và tránh trừ lại phần đã nằm trong commitment.

Theo dõi estimated/committed/actual cost, cost-to-complete và margin-at-completion có nguồn. Thiếu cost không coi0. Pacing theo flighting; health tách financial/delivery/relationship/outcome, có component/version/freshness và action owner. Data stale là Unknown/Degraded; CPL tăng là tín hiệu điều tra, không tự tắt kênh thiếu bằng chứng. Phép chi media xét tiền được phép dùng/credit và độ trễ spend, không dùng toàn bộ số dư ngân hàng cho mọi khách.

<a id="module-m17"></a>

#### ĐẶC TẢ MODULE M17 — Ngân sách, chi phí, funding và health

**Mục tiêu, tác nhân và phạm vi:** Finance bảo vệ tiền/margin; CMO quản ngân sách campaign; AM/Delivery báo cost-to-complete; budget owner duyệt thay đổi. P0 theo dõi approved/committed/actual và funding cơ bản; forecast/capacity sâu P1. Không dùng tiền khách A để cấp quyền chi khách B; health là dữ kiện vận hành, không là kết luận khách hài lòng.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M17-F01 Lập budget | Scope/beneficiary/category/kỳ/currency | Tách acquisition agency/service economics/client media/client outcome; thiếu basis/owner thì Draft | Budget version; M15, M18 | Không trộn tiền tìm khách agency với ngân sách quảng cáo của khách. |
| M17-F02 Commit cost | PO/vendor/reservation được duyệt | Commitment có nguồn/business key; cùng khoản không ghi lặp; vượt available xin adjustment | Outstanding commitment; Delivery | Nhìn thấy khoản đã cam kết dù chưa có hóa đơn thực chi. |
| M17-F03 Ghi actual | Invoice/chi phí/spend source xác thực | Actual thay phần commitment liên quan; không cộng cả100commit+40actual thành140 | Actual/source link; Finance | Không đếm cùng một chi phí hai lần khi commitment thành actual. |
| M17-F04 Forecast | Actual, commitments, ETC và freshness | `Available=Approved−Actual−OutstandingCommitment` cùng basis; ETC không trừ lại phần đã commit | Exposure/forecast-at-completion | Biết phần ngân sách còn dùng được và chi phí để hoàn tất. |
| M17-F05 Funding media | Receipt/credit policy, budget cap | Quyền kickoff không tự cho chi media; kiểm đúng khách/pháp nhân/currency, committed/actual và freshness | Funding authorization/headroom; M09 | Không chi tiền media ngoài nguồn tài trợ hoặc hạn mức được phép. |
| M17-F06 Health và cảnh báo | Financial/delivery/relationship/outcome | Missing/stale là Unknown; flag có owner/severity/evidence; score thiếu coverage không tự Healthy/upsell | Health vector/action; CX, M18 | Phát hiện rủi ro có bằng chứng thay vì hiển thị xanh khi thiếu dữ liệu. |
| M17-F07 Adjust/review | Scope/cost/budget change, evidence | Vượt envelope cần authority; approved snapshot không sửa; thiếu API dùng task/evidence, không giả đã pause Ads | Adjustment/reapproval; M15 | Giữ ngân sách và phạm vi thay đổi trong thẩm quyền. |

**Màn hình/field:** budget theo scope/category/kỳ; commitment→actual reconciliation; funding panel; forecast và health vector. Bắt buộc: owner, scope/beneficiary/cost bearer, currency/tax basis, approved revision, source khi ghi cost, quyền duyệt; funding có contract/line/receipt hoặc credit policy, cap/expiry. Readonly: actual nguồn, outstanding còn lại, headroom, freshness, approved snapshots, các trường missing và ledger adjustment. Không nhập “0” để vượt field cost chưa biết.

**Trạng thái/commands:** budget `Draft → InReview → Approved → Superseded/Closed`; commitment `Proposed → Approved → PartiallyConsumed → Fulfilled/Cancelled`; cancellation chỉ nhả phần không còn nghĩa vụ thực tế. Funding `Pending → Authorized → Suspended/Expired/Consumed`, restore cần recheck. Commands `approve-budget/reserve-cost/record-actual/adjust-budget/authorize-media/suspend/review-health`; exposure và health là projections, không cho sửa tay số tổng để làm đẹp.

**Quyền/ngoại lệ:** Finance post/adjust đúng authority; CMO đề xuất và tối ưu trong envelope; Delivery ghi estimate/evidence được giao; client chỉ xem budget/report đã publish. Thiếu cost ghi Unknown, chặn cam kết yêu cầu margin trừ ngoại lệ có duyệt. FX hoặc basis khác không cộng chung. Spend API stale hiển thị Degraded, giảm khả năng tự quyết theo policy; không suy ngân sách còn nhiều từ bank balance. Health score/weights/threshold chưa chốt là Draft; manual review vẫn chạy, không tự trừ nhiều lần vì nhiều ticket cùng incident.

**Nghiệm thu:** `M17-AC01` commitment100→actual40 giữ outstanding60 và exposure100; `M17-AC02` funding khách A không mở chi khách B; `M17-AC03` stale/missing outcome không hiển thị xanh; `M17-AC04` đổi cost rate hiện tại không sửa snapshot kỳ chốt. **Truy vết:** FR26; UC04/06/08/16; Budget_Lines, Budget_Adjustments, Media_Funding_Authorizations, Policy_Snapshots, Metric_Facts và cost source mappings; CEO-U05/22, CMO-U16–CMO-U18/CMO-U25, RV18–19.

#### 3.10.3 FR27 Hiệu suất và phần HR tối thiểu

**Mục đích và trách nhiệm:** FR27 People scorecard — Delivery/Ops. Biết năng lực/chi phí phục vụ; tránh suy xét nhân viên từ số thao tác.

**Liên kết đầu vào → đầu ra:** Membership/availability/cost/quality → staffing/coaching.

**Nghiệm thu và giai đoạn:** Thiếu dữ liệu không xếp hạng; không tự phạt do client delay hoặc lỗi tracking; P0 membership/P2 scorecard.

P0 giữ membership, org/team/branch, delegation; availability và cost rate theo effective date khi phục vụ capacity/margin. Payroll, lương cá nhân, tuyển dụng, bệnh lý/bảo hiểm và chấm công HR thuộc hệ khác, không đưa Customer360.

Scorecard nhân sự ở P2 khi có mục tiêu/owner/dữ liệu đủ; không áp trọng số25/30/20/25 như chuẩn. Từng role có metric/đơn vị/bối cảnh project mix/quality/client-wait và quyền giải trình; thiếu dữ liệu không xếp hạng, không suy nhân quả cá nhân từ hiệu quả campaign. Không tự phạt vì thiếu thao tác hoặc AI dự báo burnout/nghỉ việc.

### 3.11 Quản trị dữ liệu đo lường và attribution

#### 3.11.1 FR28 KPI dictionary và provenance

**Mục đích và trách nhiệm:** FR28 KPI/provenance — CMO + data owner. Các phòng ban dùng cùng định nghĩa, truy được nguyên nhân số liệu.

**Liên kết đầu vào → đầu ra:** Canonical events/dimensions/version → metric fact + quality → dashboard/decision.

**Nghiệm thu và giai đoạn:** Replay không nhân denominator; tỷ lệ hiển thị cả mẫu số; sửa definition không âm thầm đổi snapshot cũ; P0.

Metric contract có code/namespace, mục đích/quyết định, formula/grain, scope/beneficiary, event time/processing time, timezone/currency/tax basis, source, owner, exclusions, version, freshness và mẫu số. P0 chọn bộ ít metric chốt định nghĩa trước dashboard. MQL/SAL/SQL dùng demand episode và transition history; no-capacity không bị gộp invalid/no-fit.

Tracking plan có event schema, trigger/ID/required fields, legal purpose, late event và correction policy. Source IDs/UTM không chứa PII trong URL; email open không chứng minh intent. Data quality errors có owner/hạn sửa; definition thay đổi giữ snapshot đã công bố và restatement trace. Payment/invoice/cost khác basis phải ghi rõ, không cùng gọi chung doanh thu.

#### 3.11.2 FR29 Phân bổ doanh thu và giới hạn suy luận

**Mục đích và trách nhiệm:** FR29 Attribution — CMO + Finance. Biết nguồn góp vào cơ hội/đóng góp, tránh phân ngân sách theo số ảo.

**Liên kết đầu vào → đầu ra:** Touchpoint + identity/role + demand/deal + cost/outcome → attributed views.

**Nghiệm thu và giai đoạn:** Own CAC không dùng media khách; money basis rõ booked/recognized/collected; P1, P0 source capture.

P0 lưu source event/IDs, UTM có quyền và nguồn tự khai riêng. First-touch/last-touch là hai model báo cáo riêng theo demand/outcome, không cộng. Window90 ngày là giả định cần theo sales cycle; quy định first từ quan hệ hay nhu cầu, last xử lý Direct ra sao. Unknown do thiếu tracking khác Direct/Organic; giữ coverage.

Touchpoint→identity→account role có hiệu lực→demand/deal→outcome với model version/currency/value basis. Không gán mọi doanh thu account cho mọi contact. Tổng credits mỗi outcome/model không vượt1, phần thiếu Unknown; multi-touch P2. Refund/late events điều chỉnh có version, giữ báo cáo cũ. Platform Google/Meta có thể claim cùng outcome, không cộng thành thực thu; attribution không chứng minh incrementality.

P1 một connector CRM→Meta qualified/outcome sau PoC: canonical event→purpose/ACL→dataset/ad account binding đúng workspace→outbox→receipt/reconcile. Won khác Paid; đổi stage không tạo nhiều purchase; correction/refund theo khả năng API thực tế. Sent/accepted khác matched/attributed; hash không thay quyền chia sẻ. Không xuất tệp khách A sang dataset B hoặc dùng tìm khách agency. Có token owner, latency/error/coverage và kill switch.

<a id="module-m18"></a>

#### ĐẶC TẢ MODULE M18 — Từ điển KPI, BI và attribution

**Mục tiêu, tác nhân và phạm vi:** CMO/Finance thống nhất chỉ số; data owner chịu chất lượng; CEO/manager đọc theo scope; analyst quản nguồn và phiên bản. P0 chốt ít metric và source capture; attribution/closed-loop connector P1, multi-touch P2. Dashboard phục vụ quyết định có evidence, không tạo nguồn ghi sổ thứ hai hoặc cộng số platform thành doanh thu thật.

| Chức năng | Kích hoạt/đầu vào | Quy tắc quyết định | Đầu ra/liên kết | Vì sao cần |
| --- | --- | --- | --- | --- |
| M18-F01 Định nghĩa metric | Code/namespace, formula, grain, owner | Thiếu denominator/basis/scope/direction/version thì Draft, không publish như KPI chuẩn | KPI_Definition; module nguồn | Các phòng ban dùng cùng định nghĩa thay vì cùng tên nhưng khác số. |
| M18-F02 Chốt target | Metric version, kỳ, objective | Chỉ target được duyệt mới đánh giá đạt; zero denominator=N/A; lower/higher/range dùng rule khác | KPI_Target; M15, M17 | So kết quả với mục tiêu đúng hướng và đúng phạm vi. |
| M18-F03 Ingest/correct fact | Canonical source/business key, time/version | Replay không nhân fact; late/correction giữ lineage và bản đã publish; thiếu nguồn không fill0 | Fact/quality issue | Số liệu truy về nguồn và có thể sửa mà không mất lịch sử. |
| M18-F04 Tính báo cáo | Scope/grain/time/currency/tax basis | CAC agency loại media khách; booked/recognized/collected riêng; tỷ lệ hiển thị tử/mẫu | Dashboard snapshot; M09 | Quyết định kinh doanh dựa trên đúng cơ sở tiền và chi phí. |
| M18-F05 Attribution | Touchpoint/identity/role/demand/outcome | First/last là model riêng; credit mỗi outcome/model≤1, phần thiếu Unknown; không lan mọi doanh thu Account cho mọi Contact | Attribution_Credits/version | Không gán vượt doanh thu hoặc nhầm attribution với quan hệ nhân quả. |
| M18-F06 Publish/drilldown | Report revision, user ACL | Cùng quyền object/field ở tổng/count/detail/export; client chỉ bản publish đúng scope | Report/evidence; quyền/search | Khách và nhân viên chỉ xem được số liệu thuộc quyền của mình. |
| M18-F07 Export outcome | Eligible outcome, dataset binding, purpose | P1 sau capability test; recheck trước send; Won≠Paid; refund correction theo API thực, không bịa attributed | Platform_Export_Intent/receipt | Phản hồi kết quả cho nền tảng đúng tài khoản, mục đích và trạng thái. |

**Màn hình và field:** metric catalog, definition comparison; source-quality queue; dashboard có drilldown; publish/restate history; attribution coverage và connector receipt. Bắt buộc có metric code/namespace, quyết định phục vụ, owner, formula/grain, tử/mẫu khi là tỷ lệ, exclusions, event/processing time, timezone, currency/tax/value basis, source/freshness rule, direction và version. Target/weight/window chưa biết lưu Draft. Readonly: source event IDs, observed sample, coverage, calculated value, last refresh, published snapshot/hash và correction lineage. Không cho chỉnh số dashboard trực tiếp; sửa nguồn hoặc definition qua workflow.

**Trạng thái/commands:** definition `Draft → Reviewed → Active → Retired`; thay công thức tạo version mới. Report `Draft → Reconciled → Published → Superseded`; restate tạo bản mới, bản đã gửi vẫn truy được. Quality issue `Open → Assigned → Fixed → Verified/AcceptedException`; không đóng bằng cách đổi missing thành0. Commands `approve-definition/ingest/recalculate/reconcile/publish/restate/export-outcome` kiểm quyền và idempotency. Export `Queued → Accepted/Rejected/Unknown/Reconciled`, Accepted không tự là Matched/Attributed.

**Quyền/ngoại lệ:** data owner đề xuất definition; Finance duyệt money basis; CMO duyệt marketing definitions; người xuất cần purpose/grant riêng. Không có đủ mẫu không xếp hạng hoặc kết luận winner/nhân quả. Unknown tracking khác Direct thật. Cohort recycle không thành khách mới; mua trả ba đợt không thành ba purchase. Score health chỉ hiển thị khi đủ định nghĩa, coverage và context; chưa được duyệt thì bốn chiều/evidence thay tự động chấm điểm. API thiếu correction giữ case/manual reconcile và công bố giới hạn.

**Nghiệm thu:** `M18-AC01` replay/late event không nhân denominator, restate giữ snapshot cũ; `M18-AC02` agency20/client300 không tính CAC bằng320; `M18-AC03` Meta/Google cùng claim không cộng thành hai outcome; `M18-AC04` CPL actual150/target100 không được đánh giá tốt theo actual/target, missing không biến0. **Truy vết:** FR28–29; UC15/16 và UC07/13 money source; KPI_Definitions/Targets, Metric_Facts, Touchpoints, Attribution_Credits, Outcome_Events, Platform_Export_Intents; INT18–20, CMO-U01–CMO-U06/CMO-U18–CMO-U23, RV19.

### 3.12 Hợp đồng kỹ thuật bổ sung của module M03 Unified Inbox

#### 3.12.1 FR30 Connections

**Mục đích và trách nhiệm:** FR30 Connections — Integration owner. Không hứa tính năng API/tài khoản chưa cho phép.

**Liên kết đầu vào → đầu ra:** Authorization/scopes/capabilities → active connection → ingest/send.

**Nghiệm thu và giai đoạn:** Kênh receive-only không có nút reply; revoke dừng đúng chiều; P0 kênh chọn.

Mỗi connection công bố capability riêng cho Lead Ads, Messenger, comment hoặc Shop, kèm scope, API version, checked_at/evidence, người sở hữu và hạn cấp quyền. Receive-only không có nút reply. Token hoặc permission bị thu hồi phải đổi trạng thái và dừng chiều bị ảnh hưởng; không hiển thị xanh chỉ vì webhook còn trả HTTP200.

**[Đề xuất bổ sung — CR-OMNI-20261016]** Manifest tách `eligibility_rule` và `pricing_rule`; lưu qualifying event, phiên bản và bằng chứng tài khoản/API. Khả năng nhận, gửi, template, lịch sử, receipt, edit/delete và call/recording được xác minh độc lập. Chưa verified thì chặn đúng thao tác tương ứng, không chặn intake đã đủ quyền. Không dùng tính năng của giao diện quản trị provider làm bằng chứng API cung cấp cùng tính năng. Chi tiết chính sách đã đối chiếu tại 3.12.12.


#### 3.12.2 FR31 Identity liên kênh

**Mục đích và trách nhiệm:** FR31 Identity liên kênh — Steward. Một hồ sơ có nhiều danh tính nhưng không dùng tên/hash làm chứng minh.

**Liên kết đầu vào → đầu ra:** Scoped external IDs + evidence → link/review → FR01/02/timeline.

**Nghiệm thu và giai đoạn:** Hai Page cùng provider_subject_id không tự merge; scope khác không leak candidate; P0.

Dùng cùng identity/link/merge engine với FR02. Provider subject ID unique trong namespace tenant/workspace/connection; phone/email có nguồn, hiệu lực và trạng thái xác minh. Hotline dùng chung, số tái cấp và chuyển công ty có lịch sử; candidate chưa xác minh không tạo quyền đọc/gửi mới.

**[Đề xuất bổ sung — CR-OMNI-20261016]** Merge dialog cho steward xem preview, chọn survivor và giá trị giữ cho từng field xung đột, đính kèm evidence và kiểm version trước commit. Agent chỉ đề nghị nếu chưa có quyền steward. Giữ thread/account/recipient/assignment khi đổi liên kết contact; không tự gộp mọi conversation đang mở theo customer_id. Regex phone/email chỉ tạo candidate; không coi Caller ID hoặc quoted email là bằng chứng xác minh. Mẫu thao tác chọn bản ghi chính/field được tham khảo từ cập nhật Pancake CRM ngày 16/09/2026 [G05](#g05); cơ chế journal, concurrency và ACL là thiết kế của CRM này.


#### 3.12.3 FR32 Unified conversations

**Mục đích và trách nhiệm:** FR32 Unified conversations — CX Ops. Tập trung thao tác mà vẫn gửi đúng luồng/tài khoản.

**Liên kết đầu vào → đầu ra:** Thread/participants/message ACL → composer/timeline → FR34/39.

**Nghiệm thu và giai đoạn:** Trả lời trong app kênh gốc được reconcile; không mở nhầm recipient; P0.

Composer hiển thị tài khoản gửi, recipient và thread. Internal note/public reply là kiểu riêng; participant To/CC/BCC và group có role/visibility. Native reply echo được đối soát khi API hỗ trợ; nếu không thì công bố gap. Attachment/báo giá phải đúng version và quyền publish; timeline không mở thread ngoài ACL.

**[Đề xuất bổ sung — CR-OMNI-20261016]** Danh sách inbox có badge account/kênh, assignee, người đang xem và trạng thái kết nối. Viewer/typing indicator chỉ hỗ trợ phối hợp, không cấp quyền hoặc thay CAS assignment. Saved view lưu điều kiện lọc và được tính lại theo ACL hiện tại. Câu trả lời nhanh có phím tắt/chủ đề và preview; mặc định chèn nháp, biến thiếu hoặc vượt giới hạn thì chặn send. Mẫu trả lời nhanh không đồng nghĩa template được provider duyệt, không vượt cửa sổ gửi. Tham khảo UI và hỗ trợ trả lời Pancake [G02](#g02), [G04](#g04).


#### 3.12.4 FR33 Inbound

**Mục đích và trách nhiệm:** FR33 Inbound — Integration owner. Webhook lặp/lệch thứ tự không nhân lead, SLA hay trạng thái.

**Liên kết đầu vào → đầu ra:** Authenticated event → durable receipt/dedup → domain update + outbox.

**Nghiệm thu và giai đoạn:** Crash sau commit, status cũ tới sau, hai sự kiện cùng nhu cầu; P0.

Inbound xác minh nguồn rồi durable write trước ACK; worker chuẩn hóa và ghi domain/outbox trong transaction. Event key có namespace/version và giữ occurred_at/received_at. Transport dedup không thay business duplicate detection. Backfill không tạo nurture/live-SLA/lead mới mù; status reducer xử lý lệch thứ tự, crash/replay không nhân effect.


#### 3.12.5 FR34 Outbound

**Mục đích và trách nhiệm:** FR34 Outbound — CX/Integration. Tin không gửi trùng hoặc gửi khi consent/quyền đã đổi.

**Liên kết đầu vào → đầu ra:** Intent + policy + recipient snapshot → attempts → accepted/delivered/unknown.

**Nghiệm thu và giai đoạn:** Provider nhận rồi timeout không tự gửi lại; duplicate click một intent; P0.

Send intent có idempotency key, recipient/asset version, expiry và attempt history. Tại dispatch kiểm lại quyền/purpose/consent/endpoint/window/quota; approval snapshot không thay eligibility hiện tại. Timeout sau khi provider có thể nhận là unknown_outcome; đối soát nếu API hỗ trợ hoặc người có quyền quyết định với audit/deadline. Không tự gửi lại mù hoặc hiển thị delivered khi chỉ accepted.


> **Email eligibility:** Manifest phân biệt email giao dịch/phục vụ yêu cầu và email marketing; sender domain/From/Reply-To được xác minh và có bằng chứng DNS/provider authentication phù hợp nơi nhận. Không tự bật marketing từ mailbox dùng báo giá. Trước mở marketing, chốt quy tắc chống spam hiện hành, nội dung nhận diện và cách từ chối; triển khai unsubscribe trong body và one-click headers khi luật/provider/product yêu cầu. Unsubscribe token ràng buộc endpoint/purpose/sender scope, không chứa PII rõ và không đòi đăng nhập CRM; không cung cấp hồ sơ cá nhân. Yêu cầu từ chối qua các kênh hợp lệ và provider unsubscribe event cùng đi vào suppression authoritative idempotent tại 6.3. Không dùng bước xác minh tài khoản nặng như DSAR để cản từ chối.
>
> Bounce/complaint được xác minh từ provider, dedup và lưu delivery event theo connection/message/endpoint. Hard bounce chặn endpoint; soft bounce có retry/backoff/expiry theo provider policy đã chốt; complaint chặn marketing theo phạm vi xác định. Đây là delivery/safety suppression, không tự giả thành consent Revoke của mọi mục đích hoặc mọi khách dùng chung địa chỉ. Mọi dispatch kiểm cả consent và delivery suppression hiện tại. Reimport/replay không tự xóa suppression; khôi phục endpoint có workflow/evidence. Thông báo giao dịch chỉ tiếp tục khi còn cơ sở và endpoint gửi được; không lách nhãn Transactional để gửi quảng cáo.

#### 3.12.6 FR35 Assignment

**Mục đích và trách nhiệm:** FR35 Assignment — CX Ops. Giữ một người xử lý chính, continuity nhưng có backup.

**Liên kết đầu vào → đầu ra:** Scope/skill/shift/capacity/owner → assignment active có version → handoff.

**Nghiệm thu và giai đoạn:** Chuyển ca/nghỉ việc/owner unavailable không reset SLA; tab của người đã được chuyển việc không còn quyền gửi. Nếu dùng lease, kiểm cả expiry/fencing; P0.

Conversation assignee là người phục vụ hiện tại, khác Deal owner là quan hệ hợp lệ. Durable assignment unique active với row_version/CAS là mặc định MVP; reassignment ghi actor/reason/time/handoff/promises và backup. Nếu triển khai lease, phải có expiry/renewal/fencing kiểm tại thao tác gửi; typing indicator không là khóa. Thay người trực không tự đổi ownership thương mại hoặc commission.

**[Đề xuất bổ sung — CR-OMNI-20261016]** Routing lọc account permission/team/skill/ca/presence/capacity trước, sau đó mới sticky nếu ứng viên còn eligible. Với việc chưa gán, phương án mặc định để review: tỷ lệ `active_load/capacity` thấp nhất, hòa chọn `last_assigned_at` cũ nhất (NULL trước), hòa nữa theo agent_id tăng dần. Reserve slot và CAS assignment phải cùng transaction/invariant; reservation tính vào tải để hai router không giành cùng slot cuối. Một chat nhiều tin chỉ tính một slot. Voice reserved/ringing/in-progress/wrap-up giữ voice slot theo policy; không coi mọi PENDING bằng không tải. Presence available/busy/offline tách voice state. Khi chưa cấu hình capacity/lịch thì intake vào queue thủ công, không tự gán bằng số 10 chat hoặc 2 chat khi gọi. Học capability xoay vòng Pancake [G01](#g01) và capacity Zendesk [G06](#g06), không khẳng định sao chép thuật toán của họ.


#### 3.12.7 FR36 Service timers

**Mục đích và trách nhiệm:** FR36 Service timers — CX Lead. Khách cần phản hồi suốt hành trình, không chỉ tin đầu.

**Liên kết đầu vào → đầu ra:** Unanswered customer turn + priority/calendar → first/next response, resolution, promised update.

**Nghiệm thu và giai đoạn:** Trả lời lần đầu rồi im lặng vẫn cảnh báo; public reply đúng request mới hoàn thành; P0.

SLA theo Business_Subject và waiting episode có clock_type nhận việc/nỗ lực/FRT/NRT/resolution/promised_update, calendar/policy version, start/completion event, breach và pause/exception history. NRT tính từ tin đầu chưa đáp; tin khách gửi lại không lùi hạn. Chỉ hoàn thành nghĩa vụ đúng request; không dừng chung theo Contact. Reopen/mitigation và pause theo policy, pending_internal không tự pause.

Tiêu chí hoàn thành response clock nêu rõ provider accepted/delivered hay evidence hợp lệ khác theo capability. Không đòi read receipt kênh không cung cấp, không gọi accepted là khách đã nhận/đọc và không coi unknown_outcome là thành công. Bot/private note không dừng human clock; phản hồi thực chất cần định nghĩa và QA mẫu, không chỉ một lời chào để né SLA. Deadline trên Lead/Ticket là projection cùng engine.


#### 3.12.8 FR37 Search/data protection

**Mục đích và trách nhiệm:** FR37 Search/data protection — Privacy/Security. Search/export/AI/file không thành đường vòng xem hồ sơ.

**Liên kết đầu vào → đầu ra:** Current role/resource/field ACL → filtered content/count/snippet → UI/BI/RAG.

**Nghiệm thu và giai đoạn:** User bị revoke không tìm snippet/count/tệp qua URL cũ; P0.

Search/filter/count/snippet/preview/file/BI/AI áp ACL hiện tại tới object và field. Account membership không tự cấp mọi CLIENT workspace. Revoke/merge/deletion cập nhật cache/index; permission version và hậu kiểm ngăn kết quả cũ lộ nội dung. Download tài liệu nhạy cảm đi qua gateway kiểm quyền hiện tại cho từng GET/Range theo 6.2; không expose raw storage presigned URL như quyền của user.


#### 3.12.9 FR38 Sync health

**Mục đích và trách nhiệm:** FR38 Sync health — Integration owner. Biết dữ liệu đang thiếu, phục hồi được mà không gây hiệu ứng lặp.

**Liên kết đầu vào → đầu ra:** Checkpoint/provider cursor/DLQ/outcome → coverage/alert/reconcile → repair.

**Nghiệm thu và giai đoạn:** Outage phục hồi không kích hoạt marketing cũ; không hứa coverage tuyệt đối nếu không có nguồn đối chiếu; P0.

Connection health gồm token/scopes, checkpoint, queue lag/DLQ, expired cursor/full sync, deletion/echo, send unknown và coverage gap. Mỗi alert có severity/owner/runbook. Replay có range/dry-run/quyền, qua idempotency và current policy; dữ liệu lịch sử/intent hết hạn không gửi bù mù. Không đo được denominator nguồn thì coverage tuyệt đối là Unknown.


#### 3.12.10 FR39 Business links

**Mục đích và trách nhiệm:** FR39 Business links — Sales/CX. Tin hỏi mới, support và feedback đi đúng nghiệp vụ.

**Liên kết đầu vào → đầu ra:** Conversation intent + existing work → linked Lead/Deal/Ticket/Deliverable.

**Nghiệm thu và giai đoạn:** Cùng contact hỏi gói mới và báo lỗi cũ, mỗi nghĩa vụ đúng owner/SLA; P0.

Một thread có nhiều yêu cầu và một request có nhiều thread. Dùng link table typed/N:M với purpose, actor/evidence và scope; giữ context của complaint, inquiry, deal hoặc deliverable. Người xử lý xác nhận khi phân loại chưa rõ. Không tạo Lead/Deal từ mọi message hoặc link mọi thread theo Contact; đóng một work item không đóng nghĩa vụ còn lại.


#### 3.12.11 FR40 Email/files

**Mục đích và trách nhiệm:** FR40 Email/files — Security/CX. Email/file là kênh mang nội dung, quyền và mã độc.

**Liên kết đầu vào → đầu ra:** Mailbox permissions + MIME/participants → quarantined/clean asset → preview/reply.

**Nghiệm thu và giai đoạn:** File chưa clean không tải/forward; recipient preview; email sender spoof không tự merge/approve; P0 khi bật.

Kiểm mailbox/sender permissions, From/To/CC/BCC và reply-all preview. HTML không thực thi script hoặc tải remote tracking mặc định. Tệp kiểm MIME thật, size/decompression và malware, giữ version/hash; chỉ clean mới download/forward, scan chưa xong có trạng thái pending. Forwarded chain/sender tự khai không tự xác minh danh tính hoặc thẩm quyền duyệt.

**[Đề xuất bổ sung — CR-OMNI-20261016]** Threading ưu tiên provider thread ID đã verified hoặc Message-ID/In-Reply-To/References trong đúng mailbox/scope; không tự gom chỉ vì cùng subject và sender trong 30 ngày. Header là bằng chứng luồng, không là chứng minh quyền hay danh tính. Reply mặc định không tự giữ CC; Reply-all cho xem trước người nhận; BCC luôn rỗng khi khởi tạo reply và không lộ qua timeline/export ngoài quyền. Inbound subject dài không bị từ chối chỉ vì giới hạn sản phẩm outbound. Media tải/scan bất đồng bộ sau khi text đã persist; email kiểm tổng MIME sau encoding, không chỉ kích thước từng file. Draft dùng user/thread scope và TTL; không lưu nhạy cảm vô hạn trong localStorage. Tham chiếu cấu trúc header [G10](#g10).


> **Remote fetch:** Dùng media endpoint/provider SDK được xác minh và allowlist endpoint theo connector; không cho khách tự chọn endpoint fetch tổng quát. Worker chỉ dùng HTTPS phù hợp provider, kiểm host/IP sau resolve và từng redirect; chặn loopback, link-local/metadata, mạng riêng và reserved ranges trừ integration nội bộ đã được thiết kế riêng. Redirect mặc định tắt; trường hợp provider cần redirect phải kiểm lại từng hop, không forward token sang host mới. Egress/network policy bảo vệ bổ sung chống DNS rebinding; không dựa kiểm chuỗi URL đơn lẻ. Giới hạn timeout, số redirect, byte tải và decompression; lỗi đưa quarantine, không cho preview/download. Credential provider chỉ gửi tới host/endpoint được phép. Chốt allowlist/quota cụ thể trong connector manifest trước bật; không cần crawler hoặc proxy URL tùy ý.

#### 3.12.12 Chính sách kênh và ranh giới vận hành đã đối chiếu ngày 16/10/2026

**[Đề xuất bổ sung — CR-OMNI-20261016]** Các quyết định dưới thay cách hiểu đơn giản hóa trong bản SRS Omnichannel mới được gửi, không thay các invariant mạnh hơn đã có tại FR30–40.

| Hạng mục | Quy tắc áp dụng vào thiết kế | Bằng chứng / giới hạn |
| --- | --- | --- |
| Zalo OA | Tách hạn được gửi và mốc tính phí; dùng policy cho OpenAPI, không dùng policy OA Manager. Lưu last_qualifying_interaction thay chỉ last_inbound_message; template là luồng đủ điều kiện riêng, không tự chuyển sau 48 giờ | [Zalo Tin Tư vấn](https://oa.zalo.me/home/documents/guides/tin-tu-van) nêu OpenAPI trong 7 ngày từ tương tác đủ điều kiện, miễn phí trong 48 giờ, ngoài 48 giờ có phí. Không hard-code bảng giá; activation phải kiểm account và policy hiện hành |
| Telegram | Verifier kiểm secret token của webhook theo adapter; event dedup dùng update_id trong bot/connection, message namespace có chat_id/message_id | [Telegram Bot API](https://core.telegram.org/bots/api#setwebhook): secret header không phải HMAC-SHA256 chung |
| Meta | Window/qualifying events/tag và ngoại lệ theo manifest đã verified; không cho nút Tag chung như đường vượt policy | Trang chính thức trả 429 trong lượt tra cứu; không coi danh mục tag hoặc ngoại lệ ở bản gửi là đã kiểm chứng |
| Webhook Zalo | Không áp thuật toán/chữ ký chung cho mọi provider | Chưa đọc được contract kỹ thuật trong lượt này; verifier cụ thể phải có tài liệu và contract test trước activation |
| Call | Call session/legs/recording có state riêng, không thêm MISSED vào conversation.status; missed sinh callback task. Browser heartbeat chỉ phản ánh presence, không thay provider call outcome | Nhà cung cấp tổng đài chưa chọn; CDR/recording có thể đến riêng. Mapping phải được PoC |
| Resolve/reopen | Không dùng mốc 24 giờ của messaging để quyết định session nghiệp vụ; thread, request, SLA episode và waiting_party tách riêng | Theo FR32/36/39. Concurrent resolve/inbound cần row_version; intent queued/sending/unknown phải được xử lý hoặc override có quyền/lý do trước resolve |
| Phiên gửi | ACK sau durable receipt; send timeout bất định dùng unknown_outcome; không retry mù và không rollback thực tế tin đã gửi | Giữ FR33/34 của Master; sơ đồ/luồng triển khai phải khớp |
| Quyền và lưu giữ | Integration Admin không mặc định đọc mọi nội dung; merge không mở quyền; retention/redaction/legal hold theo chính sách | Giữ FR37 và Chương 6; không dùng quy tắc “cấm xóa vĩnh viễn để audit” |

Khi tích hợp inbox vendor, chốt hệ thống nguồn cho connection/assignment/message/SLA và cơ chế đồng bộ. Không để Pancake/router CRM đồng thời ghi assignee không có quyền ưu tiên và chống echo. Tài liệu công khai đã đọc chưa xác nhận đầy đủ năm kênh Telegram Bot, Email và Call trong cùng sản phẩm/gói/API Pancake; phải kiểm chứng theo capability matrix trước lựa chọn.

#### Identity resolution: quy tắc quyết định

Khóa external identity là `(tenant, workspace, connection, provider_subject_id)`; email/phone chuẩn hóa là thuộc tính có nguồn, độ xác minh và thời hạn, không phải khóa toàn cầu. Không bỏ dấu chấm hoặc phần `+tag` của mọi email theo quy tắc riêng của Gmail; không gộp hotline dùng chung thành một cá nhân. Một người đại diện nhiều công ty được gắn nhiều `Contact_Account_Roles`, gồm buyer, approver, billing, end-user và hiệu lực; hướng quan hệ được khai báo rõ. Mô hình association có nhãn của HubSpot là bằng chứng thiết kế tham khảo [R07](#r07).

Tự liên kết chỉ khi đã có external identity hợp lệ trong đúng phạm vi hoặc có bằng chứng xác minh được phê duyệt. Email/phone trùng nhưng chưa xác minh tạo candidate review; tên, địa chỉ, ảnh, nội dung chat chỉ hỗ trợ tìm kiếm. Trường hợp liên kết qua form/OTP cần purpose phù hợp và audit. Cross-workspace không merge tự động, kể cả cùng email: dữ liệu khách agency A và B phải cách ly.

Merge có preview survivor, source fields, conversation refs, consent và ownership; dữ liệu xung đột lưu provenance. Không “OR consent” để biến sự đồng ý của một kênh thành đồng ý mọi kênh. Undo cần lịch sử các liên kết cũ và xử lý các thay đổi phát sinh sau merge; không chỉ đổi lại tên Contact. Customer timeline truy vấn nhiều thread nhưng vẫn tôn trọng ACL từng thread.

#### Trải nghiệm xử lý cuộc hội thoại

Màn hình ba vùng: hàng đợi và bộ lọc; cuộc hội thoại có nhãn kênh/tài khoản; hồ sơ Contact, vai trò công ty, Deal, Ticket và next action. Nhân viên được lọc “của tôi”, “chưa nhận”, “sắp quá SLA”, chi nhánh, dịch vụ; ô soạn luôn cho biết đang gửi từ OA/Page/mailbox nào. Bản nháp và ghi chú nội bộ có kiểu dữ liệu riêng, không phân biệt chỉ bằng màu. Một người mua có thể hỏi Facebook rồi gửi brief qua email: timeline liên kết sau xác minh, hai conversation vẫn độc lập.

Conversation tách `status=open/resolved/closed`, `waiting_party=agent/customer/internal/none` và assignment/queue. Reopen là event mở episode theo policy version. Pending cần reason, due và next owner; không đóng để né SLA. First/next-response, resolution và promised update là các clock khác, theo subject/episode. Năm tin khách chưa được đáp không lùi hạn từ tin chưa đáp đầu; chuyển nhóm không reset; bot/note không hoàn thành phản hồi người thật.

Routing kiểm hard scope/quyền/skill trước; owner hợp lệ được ưu tiên continuity rồi availability/backup và capacity theo policy. Claim CAS/row lock; durable assignment có version đủ cho MVP. Nếu dùng lease phải có expiry/renew/fencing, kiểm khi gửi để tab cũ không vượt quyền. Chuyển ca bàn giao note, promises, due và open work; supervisor override có lý do. Conversation assignee khác Deal owner là hợp lệ; không tự đổi commission. Typing indicator chỉ là UX, không thay idempotency/authorization.

AI chỉ đề xuất phân loại, tóm tắt và draft có liên kết message nguồn. Nội dung khách gửi là dữ liệu không đáng tin để ra lệnh cho tool; agent không được export, đổi tài khoản nhận tiền, hứa giá hay gửi chiến dịch chỉ vì trong tin nhắn có yêu cầu. Trước mỗi hành động cần kiểm tra quyền hiện tại và approval tương ứng. Retrieval giới hạn đúng tenant/workspace, không dùng chung bộ nhớ chứa nội dung nhiều khách hàng.

### 3.13 Hành trình khách hàng và hợp đồng bàn giao xuyên module

```mermaid
flowchart LR
  M[Marketing: nguồn và campaign] --> I[Nhu cầu và định danh]
  I --> S[Sales: tiếp nhận, qualification, deal]
  S --> Q[Báo giá, SOW và phê duyệt]
  Q --> C[Hợp đồng và kỳ dịch vụ]
  C --> D[Bàn giao, deliverable, nghiệm thu]
  C --> F[Nghĩa vụ thu, tiền, đối soát]
  D --> F
  F --> K[Hoa hồng và đóng góp]
  D --> X[CX: phản hồi, ticket, khắc phục]
  X --> R[Đánh giá giá trị và gia hạn]
  R --> S
  S --> M
  K --> M
  X --> M
```

Các mũi tên là trao đổi dữ kiện có kiểm quyền, không đồng nghĩa một module được tùy ý ghi vào database của module khác. Identity, consent, quyền, phiên bản, audit, event và chất lượng dữ liệu là các kiểm soát xuyên suốt.

#### 3.13.1 Bốn đối tượng không được nhập làm một

| Đối tượng | Trả lời câu hỏi | Lỗi nếu gộp |
| --- | --- | --- |
| Contact/Account | Ai đang có quan hệ với tổ chức? Đại diện cho ai? | Một người nhiều công ty bị nhập nhằng quyền/người mua |
| Inquiry/Demand episode | Lần này họ cần gì? | Mỗi tin thành lead mới hoặc nhu cầu mới bị ghi đè lịch sử cũ |
| Deal/Commercial opportunity | Có một quyết định mua cụ thể nào cần theo đuổi? | Tin hỗ trợ thành pipeline doanh thu; nhiều dịch vụ bị khóa thành một deal |
| Conversation/Ticket/Project | Đang trao đổi ở đâu, giải quyết việc gì, giao cái gì? | Gửi nhầm kênh, đóng nhầm SLA, lẫn yêu cầu sửa với khiếu nại |

Demand episode có thể chính là Lead với định nghĩa lại rõ, không bắt buộc thêm bảng mới. Buying group thuộc cơ hội cụ thể phải liên kết quan hệ Contact–Account có hiệu lực; vai trò “người duyệt” trong công ty không luôn đồng nghĩa có quyền ký hợp đồng hoặc nghiệm thu mọi dự án.

#### 3.13.2 Service blueprint tối thiểu

| Giai đoạn | Khách mong đợi | Người chịu trách nhiệm | Dữ liệu/bằng chứng cần bàn giao | Điều kiện kết thúc |
| --- | --- | --- | --- | --- |
| Tìm hiểu/để lại yêu cầu | Được hiểu đúng và biết thời gian phản hồi | Marketing + người trực | Nguồn, nhu cầu, quyền liên hệ, timestamp | Yêu cầu có người xử lý hoặc queue được giám sát |
| Qualification | Không phải khai lại, không bị hỏi form máy móc | Sales | Mục tiêu, fit, hạn, ngân sách Unknown nếu chưa rõ | Accepted/recycled/rejected có lý do |
| Đề xuất | Biết giá bao gồm gì, kết quả nào được cam kết | Sales + chuyên môn | Brief, SOW, giả định, loại phí, cost estimate | Quote/phiên bản được duyệt và khách quyết định |
| Ký và onboarding | Lời hứa bán hàng được chuyển đầy đủ | Sales + AM/Delivery | Người ký, mục tiêu thành công, lịch, asset access, giới hạn chi | Người nhận handoff chấp nhận; việc còn thiếu có owner/hạn |
| Thực hiện | Biết tiến độ, ai cần quyết định, lần cập nhật tiếp | AM + Delivery | Deliverable version, review, change, dependency | Nghiệm thu theo SOW hoặc ngoại lệ được xử lý |
| Thu tiền | Hóa đơn/đề nghị thu đúng và giải thích được | Kế toán + AM | Nghĩa vụ, chứng từ, khoản thu, phân bổ, tranh chấp | Số dư đối soát được; không suy Paid từ Won |
| Phát sinh lỗi | Có giảm thiểu, cập nhật và chịu trách nhiệm | CX/AM + xử lý kỹ thuật | Impact, priority, promise, evidence, recovery action | Khắc phục có xác nhận/kiểm tra; không chỉ đổi Closed |
| Gia hạn/rời đi | Thấy giá trị và được bàn giao tử tế | AM + Sales + CX | Success review, quyết định renewal, quyền/tài sản cần trả | Gia hạn hợp lệ hoặc offboarding hoàn tất có lịch sử |

#### 3.13.3 Quy tắc liên kết và tác động bắt buộc

Mỗi dòng dưới là một giao dịch/luồng cần định nghĩa trong SRS, không bắt buộc tách thành microservice. “Phát sự kiện” có thể là outbox nội bộ trong monolith.

| Liên kết | Trigger và dữ liệu tối thiểu | Chủ thể nhận / kết quả | Bất biến và lỗi phải có đường xử lý |
| --- | --- | --- | --- |
| Marketing → Sales | Demand qualified theo policy version, source/campaign, evidence, owner đề nghị, occurred_at | Sales nhận/từ chối/recycle; CMO có reason | Không đếm lại acquisition khi recycle; no-capacity khác no-fit; chưa ai nhận phải có queue owner |
| Identity → Timeline/quyền | Link/merge có scope, evidence và operation ID | Canonical view cập nhật; search/consent re-evaluate | Không OR consent; không tự mở thread cấm; undo có provenance |
| Deal → Quote | Scope/brief, người mua, service/currency, loại offer | Quote revision và approval request | Draft không phải approved; expired phải revalidate; thiếu cost là Unknown |
| Quote → Contract | Approved revision + customer acceptance + authority | Contract/SOW version; nghĩa vụ thu/giao | Một lời đồng ý trên thread chưa chắc có thẩm quyền; sửa terms không ghi đè snapshot |
| Contract → Project | SOW/handoff ID, scope, success criteria, tiền/ngoại lệ, capacity | Người nhận xác nhận và prerequisites | Idempotent theo handoff/SOW; MSA có nhiều project hợp lệ; Won không tự Active |
| Acceptance → Billing/collection | Deliverable/version, người có quyền, amount/milestone | Đề nghị hóa đơn/thu theo nghĩa vụ và pháp luật | Task Done không tự Accepted; không chờ acceptance nếu nghĩa vụ hóa đơn áp dụng trước đó |
| Bank → Reconciliation | External evidence, bank account/legal entity, amount/currency/time/ref | Payment canonical, case match, allocation | Hai evidence không tự hai khoản thu; hai khoản thật giống số tiền không tự bỏ một |
| Allocation → Commission | Base đúng line/policy/pool/share version | Preview có giải thích; duyệt/payout riêng | Không dùng media/tax/write-off như service cash; refund/đổi owner xử lý riêng |
| Payment + Budget → Media authorization | Funding/credit, approved spend, committed/actual, freshness | Headroom/alert/quyết định chi | CRM gate không đủ chặn Ads UI nếu quyền ngoài hệ thống rộng; có đối soát và owner |
| Ticket → Delivery/Finance | Type, entitlement, severity, evidence, remedy request | Defect/CR/refund review; customer update | Người nhận complaint không tự có quyền hứa refund; hết quota không chặn ghi nhận |
| Feedback → Recovery → Learning | Score/comment/context/role, theme và impact | Owner accepted, remedy, verification, corrective action | Không sửa điểm gốc; closed no-contact khác verified recovered; không gom dữ liệu chéo workspace |
| Health/notice → Renewal | Contract term, notice deadline, success review, risk | Renewal/expansion/reduction hoặc offboarding | Không tự gia hạn bằng timer; one-off không ép churn; giữ contract gốc |
| CRM outcome → Ad platform | Eligible event + source ID + dataset binding + purpose | Export intent/receipt/reconcile | Scope sai chặn trước gửi; sent/accepted khác attributed; policy tại send-time |
| Privacy/offboarding → Mọi consumer | Revocation/request, đối tượng/phạm vi/mục đích/hiệu lực | Revoke session/grant, stop intents, retention flow | Job/search/file/AI phải cập nhật; restore không làm sống lại suppression đã rút |

#### 3.13.4 Ngoại lệ, tiền dư và điều phối đồng thời

- NoCapacity chuyển assignment về queue có owner/escalation trong transaction với expected_version/outbox; giữ Lead lifecycle, first_attempt/history và deadline khách. Attempt limits/OnHold review là policy; không ép gọi đủ quota hoặc Lost sau60ngày. Bị từ chối liên hệ thì stop theo phạm vi phù hợp.
- API kiểm Quote expiry tại accept/contract; scheduler chỉ cập nhật projection. Contract/Order Terminated tạo settlement review từng obligation: giữ phần đã phát sinh/minimum commitments/fees hợp lệ; giảm/void phần thật sự được hủy bằng adjustment có căn cứ. ERP credit/invoice theo nguồn, không xóa ledger. Contract obligations chưa hạch toán không thay AR/denominator DSO.
- Client-wait là blocker có owner/review và replan tài nguyên riêng; không tự acceptance/billing/đổi ngày cam kết. Ticket có thể kỹ thuật đã giải quyết nhưng khách chưa xác nhận: giữ technical evidence, no-response outcome, authority và reopen; incident/notice nghĩa vụ còn mở không tự đóng theo ticket.
- Placeholder reply không chứng minh phản hồi thực chất. Nếu còn xử lý nội bộ, lưu promise due và resolution đang chạy; cho phép trạng thái Resolved/NoReplyNeeded hợp lệ, không ép hai nút mỗi message. Lời hứa tại thời điểm tuyệt đối dùng WallClock; các clock khác theo policy/entitlement, có thể24/7 chứ không luôn giờ hành chính. Assignment intervals/owner_at_breach chỉ là evidence; không tự kết tội người giữ>50%.
- Sweeper có thể SKIP LOCKED để chia queue nhưng tất cả lệnh đổi assignment/tạo-dispatch intent phải dùng cùng aggregate lock/version contract. In-flight phối hợp chuyển người có grace hữu hạn theo episode/actual attempt, không giữ vô hạn vì pending intent. Ghi breach theo due gốc; không sửa deadline chỉ vì mạng chậm. Provider call ngoài DB transaction; unknown reconcile, không giả đã gửi.
- Merge/unmerge giữ lock order nhất quán cho contact và dependent aggregates, xử lý deadlock retry có bound; resolve canonical với version và giữ origin identity/contact/evidence. Redirect không xóa nguồn, không OR consent và không sửa chủ chứng từ. Không cho cycle hoặc link sang tenant/workspace khác.
- Rounding phân bổ dùng integer minor units và rule approved: quota chính xác của nhóm dòng hợp lệ→floor→phân từng đơn vị dư theo fractional remainder giảm dần, tie-break key ổn định; phải giữ caps/currency/tax/net semantics và tổng. Không bù dư sang cấu phần thành âm hoặc sang dòng khác loại. Số liệu invoice ERP không được tự sửa cho khớp thuật toán quản trị.
- Hoàn tiền khóa receipt và phần số dư/allocations gốc, giữ reservation theo từng phần tiền trước khi gọi provider. Gọi `C` là confirmed incoming của receipt, `R` là tổng confirmed refunds, `A` là tổng Allocate trừ Reverse còn hiệu lực, `Ru` là tổng active reservations cho tiền chưa phân bổ và `Ra(a)` là tổng active reservations giữ phần của allocation `a`. `AvailableToAllocate = C − R − A − Ru >=0`. Không trừ `Ra` lần nữa vì tiền đó vẫn nằm trong `A`. Với mỗi allocation: `0 <= Ra(a) <= A_effective(a)`; khi thêm reservation mới `r`, kiểm `r <= A_effective(a) − Ra_existing(a)`. Mọi reverse/reallocate phải bảo vệ phần đang reserve. Tổng giữ/hoàn toàn receipt phải thỏa `R + Ru + SUM(Ra(a)) <= C`, cùng currency/pháp nhân/party authority. Tất cả phép kiểm và ghi thay đổi nằm trong cùng transaction theo thứ tự khóa tại 5.14.
- Reservation hoàn dư có allocation_id NULL và chỉ được tạo nếu `Ru_new <= C−R−A−Ru_existing`. Reservation hoàn phần đã phân bổ trỏ allocation gốc và cấu phần trả lại, không giải phóng allocation trước khi có kết quả xác thực. Một yêu cầu hoàn nhiều allocation có nhiều reservation lines cùng operation_id, mỗi line có item_key duy nhất; không cần bảng tài chính tổng quát mới. Khóa idempotency có scope receipt/operation/item và request hash; cùng key khác amount/beneficiary/body trả409.
- Confirmation hoàn dư cập nhật một Refund canonical, kết thúc reservation dư trong cùng transaction, không tạo Reverse allocation hoặc commission reversal nếu chưa phát sinh. Confirmation hoàn allocated cùng transaction ghi Refund, Reverse đúng allocation/components và kết thúc reservation: `R` tăng x, `A` giảm x nên available không đổi. Phát outbox để đảo đúng commission gốc đủ điều kiện theo policy/kỳ; không đảo media/tax thành service commission. Nếu giảm nghĩa vụ thương mại thì dùng Obligation_Adjustment/ERP credit có căn cứ riêng; refund không tự quyết định nghĩa vụ đã hết.
- Timeout/provider unknown giữ reservation và case reconcile; TTL đến hạn chỉ tạo cảnh báo/review, không tự giải phóng khoản có thể đã chi. Release chỉ sau kết quả xác thực không chi hoặc quyết định giải quyết có evidence/authority; retry cùng operation không tạo khoản hoàn mới. Provider call luôn ngoài DB transaction.
- Short-payment có case phân loại: payer thiếu tiền, phí ngân hàng có chứng từ, commercial discount hoặc write-off. Finance dùng adjustment đúng loại và hạn mức; ngưỡng100.000/0,5% chỉ là đề xuất, không chứng minh bản chất phí. Với gross/net settlement qua provider, định nghĩa receipt/cost/commission basis rõ; không tạo cash giả từ xóa nợ. Production commission theo line/pool/policy đã duyệt, chưa có rule là PendingPolicy; không tự full hoặc0.

#### 3.13.5 Hợp đồng chuyển trạng thái và đồng hồ

Mọi chuyển trạng thái nhận command/idempotency key và expected_version; server kiểm action/scope/authority, trạng thái nguồn, điều kiện và side effects. State/history/outbox commit atomic. Command trái trạng thái trả409, dữ liệu/guard sai trả422 hoặc403 theo quyền; không có partial effect. Không cho PATCH status tùy ý. Scheduler dùng cùng command guard. Catalog transition có version/owner; instance đang chạy chỉ đổi policy qua migration được duyệt.

Bảng sau là hợp đồng chuyển trạng thái của thiết kế. Mapping trạng thái native phải bảo toàn các điều kiện và tác động này. Các tham số kinh doanh riêng được cấu hình theo A.6; thiếu cấu hình bắt buộc chỉ chặn thao tác tương ứng, không chặn tiếp nhận nhu cầu. Mỗi mũi tên là một command riêng, không cho nhảy tùy ý qua bước. Trạng thái đích bị từ chối nội bộ không được làm mất nội dung và evidence phiên bản trước.

| Đối tượng | Chuyển trạng thái tối thiểu | Guard / tác động bắt buộc |
| --- | --- | --- |
| Lead | New→Assigned→Contacting→Qualified→Converted; lead chưa Converted→Nurture/Dormant/Disqualified; reactivate→Assigned/Contacting theo evidence | Owner hoặc queue hợp lệ; Qualified cần model/nhu cầu/next action; Converted cần result refs atomic. Disqualified cần reason; cùng nhu cầu quay lại giữ history/cohort/breach. Nhu cầu mới dùng Lead mới có lineage. |
| Handover | Pending→Accepted/Rejected/Recycled; Recycled→Pending khi đủ điều kiện | Khác Lead lifecycle; NoCapacity đưa queue/escalation, không reset tiến độ hay SLA. |
| Deal | Open stage→stage được pipeline version cho phép hoặc Won/Lost; Active↔OnHold khi Open | Won theo commercial gate được chốt, không đòi Paid. Lost có reason; reopen Lost bằng command có authority giữ closed history. Sửa sai Won có hợp đồng/order phải impact review và correction workflow, không PATCH về Open rồi tạo giao dịch lần hai. |
| Quote revision | Draft→PendingApproval→Approved→Sent→Accepted/Rejected/Expired; Draft/PendingApproval có thể hủy; bản chào bị thay→Superseded theo policy | Internal approval khác customer acceptance. Trường hợp accepted trước khi Sent cần evidence gửi ngoài CRM hợp lệ; không bỏ approval/authority/expiry. Từ chối nội bộ trả Draft khi chưa khóa, hoặc revision mới. Bản Approved bất biến nội dung; Accepted đúng hạn không Expired hồi tố. Revision mới không tự vô hiệu cam kết đã Accepted; thay cam kết qua amendment. |
| Contract | Draft→PendingSignature→Signed→Active→Expired/Terminated; Draft/PendingSignature→Cancelled | Signed khác effective; Active đủ terms/authority. Amend tạo version liên kết; suspend nếu điều khoản có thì giữ lý do/quyền/notice và không mặc định xóa nghĩa vụ. Termination dẫn settlement review. MSA không bắt quote giả; quote được link phải đúng buyer/currency/revision. |
| Order | Draft→Confirmed→InDelivery→Completed; Draft/Confirmed→Cancelled; Confirmed/InDelivery→Terminated | Confirm khóa commercial basis/lines/obligations; InDelivery cần start authorization đúng phạm vi; Completed theo deliverable/milestone policy, không tự Paid. Cancel/Terminate đánh giá nghĩa vụ/settlement, không xóa ledger. |
| Project | Draft→PendingStart→Active→Completed; Active↔Blocked; PendingStart/Active/Blocked→Terminated theo authority | Active cần handoff accepted và authorization; Blocked có reason/owner/review, không tự dời contractual date; Completed cần acceptance áp dụng. Offboarding/settlement theo dõi riêng. |
| Deliverable | Planned→InProgress→InternalReview→ClientReview→Accepted; InternalReview/ClientReview→Rework→InProgress; thay scope đi CR | Version/hash/QA/approver; defect không trừ quota đổi ý. Asset đã Accepted thay đổi tạo version và review mới; giữ acceptance cũ. Hủy đầu ra phải đi impact/settlement, không xóa phiên bản đã nghiệm thu. |
| Ticket | Open→InProgress; InProgress↔WaitingCustomer; InProgress/WaitingCustomer→Resolved→Closed; Resolved/Closed→InProgress khi reopen hợp lệ | Owner/entitlement/SLA; WaitingCustomer không pause mọi clock. Resolved cần resolution evidence/code; no-response closure khác verified. Duplicate có link tới case tiếp nhận nghĩa vụ. Reopen giữ breach và remaining time theo episode policy. |
| Conversation | open→resolved→closed; resolved/closed→open khi inbound/new work hợp lệ | waiting_party/assignment độc lập; đóng thread không đóng linked ticket/clock khác. Backfill không tự mở live episode; tab cũ phải qua assignment version khi gửi. |
| Payment | Verification Pending→Confirmed/Rejected; matching/allocation/reconciliation theo các projection riêng | Confirm cần evidence; correction bằng event/reversal, không sửa posted amount. Pending không allocate; Confirmed nhưng Unidentified vẫn tồn tại. Reject một evidence không xóa receipt được evidence khác chứng minh. Refund có state/reservation theo 3.13.4/4.13. |
| Commission | Preview→Earned→Approved→Payable→Paid; policy có thể xét approval trước earned nếu định nghĩa rõ | Earned theo eligible allocation/policy, Approved đúng authority, Payable đủ release/period; Paid cần payout confirmed. Partial payout lưu paid_amount/remaining, không mark toàn bộ Paid. Refund tạo Reverse/Adjustment liên kết, không ghi đè lịch sử Paid. |

Định nghĩa clock áp dụng cho từng transition gồm `start_event`, `completion_criterion`, `pause_allowed`, `resume_rule`, `cancel_outcome`, `reopen_carryover`, calendar/time basis và authority. Không có đủ các trường áp dụng thì policy giữ Draft, không tự tạo timeout nghiệp vụ bằng con số không được duyệt. Reassign, tin khách gửi thêm, private note, đổi priority hoặc pending_internal không tự reset clock. Promise giờ tuyệt đối giữ WallClock; thay promise cần lịch sử thỏa thuận.

<a id="work-core"></a>
### 3.14 Hợp đồng nghiệp vụ Task Core dùng chung — FR25/M16

Mã chức năng W-F01–14 ở Master tương ứng WF01–14 trong báo cáo nguồn; namespace riêng để không trùng mã service blueprint WF01–03 đã có. UC-W và BR-W giữ nguyên.

CR-WORK-20261016: các quy tắc sau đã hợp nhất thành baseline thiết kế 1.7. Tham số vận hành chưa chốt quản tại A.6; không phải các tính năng đã code/test. Nguồn và lý do thiết kế tại Phụ lục H.

M02/M03/M04/M11 tạo hoặc liên kết Task Core bằng source event/business key; không giữ bản Task thứ hai. Activities giữ sự kiện đã xảy ra, Task giữ việc cần làm; cùng xuất hiện trong My Work dưới projection có loại nguồn. Đánh dấu Task Done không tự dừng request SLA, đóng Ticket hay phát client acceptance; dùng evidence/response targets theo nghiệp vụ nguồn.

#### 3.14.1 Cấu trúc tổ chức và phân loại việc

`Tenant → Workspace → Team/Project → Task` là một cách điều hướng, không phải cây quyền cố định. Department là quan hệ tổ chức; một nhân viên có thể tham gia nhiều team/project với hiệu lực khác nhau. Branch/pháp nhân không thay workspace.

| Loại việc | Context bắt buộc | Có thể độc lập? | Quyền và điều kiện hoàn thành |
| --- | --- | --- | --- |
| Personal work | Người tạo = người làm; workspace sở hữu dữ liệu | Có | Riêng với người tạo theo policy, không tự hiện trong board team |
| Internal team task | Team/queue hoặc assignee cùng scope | Có | Team grant, owner, deadline nếu giao chính thức; review theo loại |
| CRM follow-up | Link Lead/Deal/Contact/Ticket hoặc request | Có thể tạo trước khi phân loại | Task done không tự đóng Ticket/SLA; cần evidence đúng nghĩa vụ |
| Project task | Project; parent/milestone tùy chọn | Không, nếu loại project task | Quyền dự án và gate; không đòi Contract cho internal project |
| Client deliverable work | Project/SOW/deliverable version khi áp dụng | Không | Hoàn tất nội bộ tách acceptance của khách |

“Personal” trong CRM là công việc cá nhân thuộc môi trường doanh nghiệp, không phải kho riêng cho dữ liệu đời tư. UI phải công bố quản lý có thấy không; thiết kế mặc định không cho quản lý xem chỉ vì quan hệ cấp trên. Chế độ kiểm tra đặc biệt cần quyền/audit theo Master, không hứa riêng tư tuyệt đối trước khi chốt chính sách tổ chức.

#### 3.14.2 Lifecycle, assignment và business rules

Canonical lifecycle: `DRAFT → OPEN → IN_PROGRESS → IN_REVIEW → DONE`; `CANCELED` là terminal khác Done. Cho phép simple task đi `OPEN/IN_PROGRESS → DONE` nếu không yêu cầu review. Blocked, overdue, assignment pending là thuộc tính riêng.

Assignment lifecycle: `UNASSIGNED → OFFERED → ACCEPTED`; `DECLINED` kết thúc một offer và chuyển việc về queue/manager; chuyển người tạo assignment mới, không sửa lịch sử. Chế độ giao trực tiếp không cần xác nhận là policy rõ, ghi `AUTO_ACCEPTED`, không giả người dùng đã bấm nhận.

| Transition | Actor/guard | Effect |
| --- | --- | --- |
| Draft → Open | Creator có quyền; đủ title/scope/đích giao và due của việc giao chính thức | Assignment/offer + outbox; audit |
| Open → InProgress | Assignee accepted, không hard blocker/dependency chưa đủ | started_at một lần cho episode |
| Open/InProgress → InReview | Assignee; review_required; evidence/checklist đạt | Submission immutable + reviewer snapshot, review_due |
| Open/InProgress → Done | Không review_required; tiêu chí đủ, không blocker chưa miễn trừ | Completion event, giữ due snapshot |
| InReview → Done | Reviewer đúng scope/version, không tự duyệt trái policy | Review decision + completed_at |
| InReview → InProgress | Reviewer reject với lý do | Rework episode; giữ submission cũ |
| Done → Open | Người có quyền reopen, lý do, kiểm parent/dependency | Episode mới; không xóa lần hoàn thành trước |
| Draft/Open/InProgress/InReview → Canceled | Authority + lý do + tác động con/phụ thuộc | Cancellation, không tính thành công |

**BR-W01:** một assignee chính active trên task đang thực hiện; queue giữ việc chưa nhận, có queue manager chịu trách nhiệm. Parent summary không phải assignee tổng hợp của mọi việc con.

**BR-W02:** stage là vị trí trên board, không tự định nghĩa Done. Drag/drop gửi command có guards; đổi tên cột không thay KPI hoặc acceptance.

**BR-W03:** `is_overdue = effective_due_at < now AND lifecycle NOT IN (DONE,CANCELED)`. InReview vẫn có thể overdue. Theo dõi submitted_on_time riêng để phân biệt người thực hiện và thời gian review.

**BR-W04:** due gốc lưu bất biến sau giao; due hiện tại và committed_due tách riêng. Xin gia hạn không tự đổi hạn. Snooze reminder không thay due. Late extension không xóa breach cũ.

**BR-W05:** blocker có reason/type/owner/opened_at/review_at; block không tự pause deadline hoặc SLA. Miễn trừ dependency cần quyền/lý do.

**BR-W06:** task hierarchy không cycle, P0 tối đa ba cấp; dependency P0 Finish-to-Start, cấm self/cycle, cùng workspace và trong scope được phép. Predecessor canceled không mặc định mở successor.

**BR-W07:** parent chỉ Done khi mandatory children Done hoặc được miễn trừ hợp lệ và bản thân đủ tiêu chí. Không tự đóng tất cả con khi kéo cha sang Done. Con reopen khi cha Done phải dùng command reopen family có preview hoặc bị chặn.

**BR-W08:** review gắn result_version/hash; sửa file/nội dung kết quả sau submit phải rút hoặc tạo submission mới, decision cũ không áp phiên bản mới. Self-review chỉ cho personal/simple mode hoặc override được ghi rõ.

**BR-W09:** assignee không có quyền đọc context bắt buộc thì không giao, trừ tạo sanitized task riêng đã được người có quyền duyệt; không mở quyền CRM record ngầm.

**BR-W10:** sửa/delete/transfer phải expected_version; create/bulk/recurrence có idempotency. Task đã phát sinh nghiệp vụ dùng cancel/archive, không hard-delete để giấu lịch sử.

#### 3.14.3 Danh mục chức năng W-F01–14 và ưu tiên

| ID | Chức năng | Pha đề xuất | Điều kiện nghiệm thu cốt lõi |
| --- | --- | --- | --- |
| W-F01 | Task personal/internal/CRM/project | P0 | Không bắt contract cho internal; context ACL độc lập |
| W-F02 | Giao một owner, queue, accept/decline | P0 | Một owner active, claim atomic, queue age không mất |
| W-F03 | My Work: của tôi/tôi giao/chờ tôi duyệt/theo dõi | P0 | Một task hiện nhiều view nhưng không nhân dữ liệu |
| W-F04 | Team list/board, filters/saved views | P0 | Drag/drop qua state guards; ACL áp count |
| W-F05 | Deadline, reminder, gia hạn, escalation | P0 | Không xóa breach bằng đổi hạn, notification idempotent |
| W-F06 | Comment/@mention/file/result | P0 | Không mở quyền ngầm; file clean; event audit |
| W-F07 | Review, reject/rework, reopen/cancel | P0 | Approval đúng version; Done khác Accepted |
| W-F08 | Checklist, subtask cơ bản, dependency FS | P0 giới hạn | Không cycle; child chưa đủ thì parent không Done |
| W-F09 | Template và calendar recurrence cơ bản | P0 calendar recurrence cơ bản | Unique occurrence, preview, offboarding |
| W-F10 | Effort planning/time entry/availability | P1 | Không đếm parent+child hoặc thời gian trùng |
| W-F11 | Gantt/critical path/multiple dependency types | P1 | Có baseline và dữ liệu lịch đủ; không tự dời committed date |
| W-F12 | Portfolio/nguồn lực liên phòng ban | P1 | Cross-team scope đúng, thiếu data Unknown |
| W-F13 | Goal/OKR và scorecard | P2 | Không suy từ số task Done; công thức/nguồn/phê duyệt |
| W-F14 | AI chia việc/tóm tắt/rủi ro | P2, draft trước | Có provenance/review; không tự nâng quyền/gửi/đổi hạn |

W-F01–09 là P0 của miền Work Management đã tích hợp. Pilot có thể triển khai W-F01–07 trước rồi W-F08–09, nhưng chưa hoàn tất scope thì không tuyên bố đạt toàn bộ P0. Nếu nguồn lực không đủ, điều chỉnh release scope/lịch có quyết định; không tự giữ cam kết 90 ngày mà tăng việc. W-F10–12 P1 và W-F13–14 P2. Calendar recurrence cơ bản P0; completion-based recurrence và catch-up nâng cao P1, guards vẫn bắt buộc khi bật.

#### 3.14.4 Dữ liệu và giao diện

M: bắt buộc; O: tùy chọn; M*: bắt buộc có điều kiện. Trần dữ liệu là đề xuất baseline để review.

| Field | UI | Kiểu/độ dài | M/O | Default | Validation/nguồn | Mã và thông báo |
| --- | --- | --- | --- | --- | --- | --- |
| title | Textbox | varchar(255) | M | Rỗng | Trim, 1..255 | TASK_TITLE_INVALID: Tiêu đề phải có từ 1 đến 255 ký tự. |
| description | Rich text | text, 20.000 ký tự | O | Rỗng | Sanitize; không remote script | TASK_DESCRIPTION_INVALID: Mô tả vượt giới hạn hoặc chứa nội dung không hợp lệ. |
| work_type | Dropdown | enum PERSONAL/INTERNAL/CRM/PROJECT | M | Theo màn hình | Project bắt buộc khi PROJECT | TASK_CONTEXT_REQUIRED: Vui lòng chọn phạm vi công việc phù hợp. |
| workspace_id | Selector/read-only | UUID | M | Workspace hiện tại | Membership hiện hành server | TASK_SCOPE_FORBIDDEN: Bạn không có quyền thao tác trong phạm vi này. |
| project_id | Dropdown | UUID | M* | NULL | Active project, task creation được phép | PROJECT_UNAVAILABLE: Dự án không còn nhận công việc mới. |
| assignee/queue | User/queue picker | UUID XOR UUID | M* khi giao | Personal=self | Một đích giao; active/grant; nullable ở Draft | ASSIGNMENT_INVALID: Chọn một người phụ trách hoặc một hàng chờ hợp lệ. |
| requester_id | Picker | UUID | M | Creator | Trong scope; authority không suy từ creator | REQUESTER_INVALID: Người yêu cầu không hợp lệ. |
| reviewer_id | Picker | UUID | M* review | NULL | Reviewer active, đủ grant, separation rule | REVIEWER_REQUIRED: Chọn người kiểm duyệt đủ quyền. |
| collaborators/watchers | Multi-select | UUID[], product max 50 mỗi loại | O | [] | Grant kiểm từng người; không auto-share context | PARTICIPANT_FORBIDDEN: Một hoặc nhiều thành viên không đủ quyền tham gia. |
| priority | Dropdown | LOW/NORMAL/HIGH/URGENT | M | NORMAL | URGENT có reason, authority theo team | PRIORITY_REASON_REQUIRED: Nhập lý do ưu tiên khẩn cấp. |
| planned_start/due_at | Date-time | timestamptz | O/M* | NULL | Due>=start; UTC + timezone; import past due được phép có cờ | TASK_DATE_INVALID: Hạn hoàn thành phải bằng hoặc sau thời điểm bắt đầu. |
| committed_due_at | Read-only | timestamptz | O | Context snapshot | Đổi qua change control nguồn | COMMITMENT_CHANGE_REQUIRED: Mốc cam kết cần được duyệt tại nghiệp vụ nguồn. |
| estimate_minutes | Number | integer 1..525600 | O | NULL | Không lấy NULL là 0; áp task leaf/summary policy | ESTIMATE_INVALID: Thời lượng ước tính phải là số phút dương trong giới hạn cho phép. |
| checklist | Checklist editor | item text <=500, tối đa 100 | O | [] | Required flag, actor/time; version | CHECKLIST_INCOMPLETE: Còn bước bắt buộc chưa hoàn tất. |
| parent_task_id | Picker | UUID | O | NULL | Same scope, depth<=3, không cycle | TASK_HIERARCHY_INVALID: Cấu trúc công việc bị vòng lặp hoặc vượt số cấp cho phép. |
| dependency_ids | Picker | UUID[] | O | [] | FS P0; same scope; atomic graph check | DEPENDENCY_CYCLE: Quan hệ phụ thuộc tạo thành vòng lặp. |
| completion_criteria | Textarea | text<=5.000 | M* delegated/review | Rỗng | Điều kiện đủ để reviewer đánh giá | CRITERIA_REQUIRED: Nhập tiêu chí hoàn thành trước khi giao việc. |
| result/attachments | Editor/uploader | text<=20.000; asset UUID[] | M* policy | Rỗng | Clean assets, owned scope, submission hash | RESULT_NOT_READY: Kết quả hoặc tệp chưa đủ điều kiện nộp. |
| change_reason | Textarea | varchar(1000) | M* reassign/deadline/cancel/reopen | Rỗng | 1..1000 trimmed | CHANGE_REASON_REQUIRED: Nhập lý do thay đổi. |
| row_version | Hidden | bigint | M mutation | Version vừa đọc | CAS | TASK_VERSION_CONFLICT: Công việc vừa thay đổi. Vui lòng tải lại. |
| visibility | Selector | PRIVATE/TEAM/PROJECT/EXPLICIT | M | PRIVATE personal; theo scope khác | Không giảm bảo vệ của nguồn link | VISIBILITY_FORBIDDEN: Không thể chia sẻ công việc trong phạm vi đã chọn. |

#### Màn hình bắt buộc

1. **My Work:** tabs Được giao/Tôi giao/Chờ tôi duyệt/Theo dõi; nhóm overdue/today/upcoming/no due; chọn workspace rõ; quick create tối thiểu.
2. **Team Work:** list và board, unassigned, awaiting acceptance, blocked, review overdue; workload chỉ hiển thị đúng đơn vị và coverage.
3. **Task detail:** brief, owner và roles, due/history, checklist/subtasks/dependencies, result/review, comments/audit. Action buttons theo quyền và lifecycle.
4. **Manager review:** preview yêu cầu đổi hạn/chuyển người/kết quả; so sánh phiên bản; approve/reject có lý do.
5. **Org overview:** exceptions cần quyết định, rủi ro milestone, tải nhiều nhóm; drill-down được cấp, không mặc định thấy nội dung personal/private.
6. **Automation/template:** preview occurrence, rule version, owner fallback, trạng thái lỗi; quyền activate riêng quyền soạn.

#### 3.14.5 Sơ đồ Task Core

#### Context

```mermaid
flowchart LR
  User[Nhân viên] --> My[My Work]
  Lead[Trưởng nhóm / PM] --> Team[Team Work và Review]
  CEO[Quản lý tổ chức] --> Org[Org Overview]
  My --> Work[Task Core]
  Team --> Work
  Org --> Metrics[Metric projections có ACL]
  Work --> Metrics
  CRM[Lead / Deal / Ticket / Conversation] --> Links[Typed context links]
  Links --> Work
  IAM[M14 Tổ chức và quyền] --> Work
  Auto[M04 Automation] --> Work
  Calendar[M13 Lịch] --> Work
  Work --> Review[Submission và Review]
  Review --> Delivery[M16 Deliverable / Acceptance riêng]
  Work <--> Adapter[Sync adapter có source authority]
  Adapter <--> PMS[PMS ngoài nếu được chọn]
```

#### Activity — giao, nhận và kiểm kết quả

```mermaid
flowchart TD
  A[Tạo việc và chọn cách giao] --> B{Scope và dữ liệu hợp lệ?}
  B -- Không --> C[Báo lỗi; không tạo thông báo]
  B -- Có --> D[Commit task + assignment + outbox]
  D --> E{Queue hay trực tiếp?}
  E -- Queue --> F[Queue manager theo dõi tuổi việc]
  F --> G[Thành viên claim bằng CAS]
  E -- Trực tiếp --> H[Người nhận accept hoặc decline]
  H -- Decline --> F
  H -- Accept --> I{Đủ điều kiện bắt đầu?}
  G --> I
  I -- Không --> J[Blocked và người xử lý; giữ hạn]
  J --> I
  I -- Có --> K[Thực hiện và lưu evidence]
  K --> L{Đủ checklist và việc con?}
  L -- Không --> K
  L -- Có --> M{Cần review?}
  M -- Không --> N[Done nội bộ]
  M -- Có --> O[Snapshot submission; InReview]
  O --> P{Reviewer đúng quyền/version duyệt?}
  P -- Từ chối --> K
  P -- Chấp thuận --> N
  N --> Q[Cập nhật metric và downstream event]
```

#### Sequence — nộp và duyệt có cạnh tranh

```mermaid
sequenceDiagram
  actor A as Assignee
  participant API as Work API
  participant DB as Database
  participant W as Outbox Worker
  actor R as Reviewer
  A->>API: Submit(task_version, result_version, key)
  API->>API: Quyền, checklist, con, blocker, file
  API->>DB: Transaction submission + InReview + audit/outbox
  DB-->>API: Commit
  API-->>A: Submission ID và version
  W->>DB: Đọc outbox, kiểm quyền recipient
  W-->>R: Thông báo cần review
  R->>API: Approve(submission_id, expected_version)
  API->>DB: Recheck task/submission/reviewer và CAS
  alt Version và quyền hợp lệ
    API->>DB: Decision + Done + event/outbox
    API-->>R: Approved
  else Đã thay đổi hoặc bị thu hồi quyền
    API-->>R: 409 hoặc 403
  end
  Note over DB,W: Task Done không tự tạo Client Acceptance
```

#### State — Task

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> OPEN: Giao hợp lệ
  OPEN --> IN_PROGRESS: Nhận và bắt đầu
  OPEN --> IN_REVIEW: Nộp có review
  IN_PROGRESS --> IN_REVIEW: Nộp có review
  OPEN --> DONE: Việc đơn giản đủ tiêu chí
  IN_PROGRESS --> DONE: Không cần review
  IN_REVIEW --> IN_PROGRESS: Reject có lý do
  IN_REVIEW --> DONE: Approve đúng version
  DONE --> OPEN: Reopen có quyền và lý do
  DRAFT --> CANCELED
  OPEN --> CANCELED
  IN_PROGRESS --> CANCELED
  IN_REVIEW --> CANCELED
  CANCELED --> [*]
  note right of IN_PROGRESS
    Blocked và Overdue là thuộc tính riêng
    Không tự pause cam kết hoặc SLA
  end note
```

#### ER — quan hệ chính

```mermaid
erDiagram
  WORKSPACE ||--o{ TASK : scopes
  PROJECT o|--o{ TASK : groups
  TASK o|--o{ TASK : parent_of
  TASK ||--o{ TASK_ASSIGNMENT : has_history
  TASK ||--o{ TASK_PARTICIPANT : involves
  TASK ||--o{ TASK_SUBMISSION : submits
  TASK_SUBMISSION ||--o{ TASK_REVIEW : receives
  TASK ||--o{ TASK_LINK : has_context
  TASK ||--o{ TASK_DEPENDENCY : predecessor
  TASK ||--o{ TASK_DEPENDENCY : successor
  RECURRENCE_RULE ||--o{ OCCURRENCE : generates
  OCCURRENCE o|--o| TASK : materializes
  TASK ||--o{ TASK_EVENT : audits
```

#### 3.14.6 Kịch bản xuyên phòng ban

**Tình huống:** Sales thắng cơ hội thiết kế bộ nhận diện và launch campaign. Khách có lịch khai trương cố định.

1. M08 kiểm hợp đồng/điều kiện kickoff và tạo handoff; sự kiện replay không sinh project lần hai.
2. PM tạo kế hoạch từ template version đã duyệt: nhận brief → concept → design → internal QA → khách duyệt → publish.
3. Một PM accountable, từng task có assignee; Designer và Content là cộng tác viên hoặc subtasks riêng theo đầu ra. Account manager là watcher, không tự duyệt kỹ thuật nếu không được chỉ định.
4. Designer thiếu logo gốc: mở blocker CLIENT_INPUT, AM có việc thu thập asset. Deadline khai trương không tự lùi; manager thấy at-risk.
5. Task QA không bắt đầu khi file chưa clean hoặc concept chưa đủ điều kiện; dependency waive cần người có quyền, có evidence.
6. Designer nộp v2, QA yêu cầu sửa: task rework, history giữ v2. V3 được duyệt nội bộ vẫn chưa là client acceptance.
7. Khách đổi phạm vi sau khi chốt: tạo CR, đánh giá effort/date/cost; không sửa baseline bằng kéo cột.
8. Task publish hoàn thành chỉ tạo sự kiện thực thi. Nghiệm thu, lập hóa đơn và thanh toán đi theo nghiệp vụ gốc, không cascade tùy tiện.
9. Báo cáo tuần thấy: owner workload, thời gian chờ khách, review age, forecast milestone, thiếu estimate; không quy mọi trễ cho Designer.

**Tình huống độc lập:** kế toán nhắc đối soát mỗi thứ Hai và nhân viên tự nhắc chuẩn bị họp. Hai việc không cần contract/project; recurrence của đối soát dùng calendar, personal reminder chỉ nằm My Work theo scope. Điều này là lý do không thể chỉ dùng module delivery hiện tại.

<a id="chuong-4"></a>

## CHƯƠNG 4 USE CASES VÀ LUỒNG QUY TRÌNH NGHIỆP VỤ

Các luồng sau là hợp đồng hành vi end-to-end. “Đậu” là hoàn tất đúng điều kiện; “rớt” là không được chuyển bước, lưu lý do và chuyển hàng đợi xử lý. Mỗi bước thay đổi dữ liệu ghi actor, timestamp, correlation_id và version. Không xóa lịch sử khi retry.

Các quy tắc ngoại lệ và tính tiền tại 3.13.4 áp dụng xuyên các UC. Mỗi UC giữ đúng trạng thái đã có; không xem queue/reassign như nhu cầu mới hoặc xóa breach. Các chính sách mang số cụ thể phải qua A.6 trước activate.

### 4.1 UC01 Tiếp nhận lead đa nguồn

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR01, FR04, FR05 |
| Tác nhân | Marketing, webhook worker, Sales |
| Đầu vào và tiền điều kiện | Form hợp lệ, tenant xác định, nguồn và quyền xử lý được ghi nhận |
| Luồng chính | Nhận payload → kiểm schema/chống spam → durable inbox → chuẩn hóa → tìm định danh → tạo/link lead → router chọn owner → tạo task/SLA → phản hồi nhận thành công |
| Đậu rớt và rẽ nhánh | Đậu: một lead có owner/task. Trùng event: trả kết quả cũ. Thiếu consent marketing: vẫn xử lý yêu cầu tư vấn theo cơ sở phù hợp, chặn nurture. Payload sai: quarantine, không mất dữ liệu thô tối thiểu. |
| Đầu ra và lưu trữ | Lead, contact, assignment, consent evidence; event lead.created |
| Tiêu chí nghiệm thu | Gửi cùng event 3 lần chỉ có 1 lead; hai sự kiện khác cho nhu cầu khác được liên kết nhưng không mất lịch sử. |
| Quy tắc liên kết bắt buộc | Durable receipt, provisional subject/contact, marketing consent không mặc định; business duplicate khác event duplicate; FR liên quan: 01,02,04,05,31,33. |

Yêu cầu tư vấn hợp lệ chưa rõ người mua tạo Lead `business_model=Unknown`, có Contact provisional khi cần, source và owner/queue/SLA. Không giữ lead hợp lệ ở quarantine chỉ vì chưa biết business model. Qualification xác nhận B2B/B2C trước Qualified/Converted, sau đó áp điều kiện Account/buyer Contact. Unknown không là NoFit và không bị loại khỏi mẫu số intake hợp lệ.

### 4.2 UC02 Nhận và thu hồi lead

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR05 |
| Tác nhân | Sales, SLA worker, trưởng nhóm |
| Đầu vào và tiền điều kiện | Lead assigned, deadline theo lịch ca |
| Luồng chính | Sales claim → kiểm expected_version → ghi accepted_at → tiếp cận → ghi activity có chứng cứ → cập nhật next action; sweeper rà deadline |
| Đậu rớt và rẽ nhánh | Đậu: activity hợp lệ đúng hạn. Quá hạn: cảnh báo rồi reassign. Race activity/thu hồi: lock/version chọn một kết quả, giữ log. Hết người: queue và escalation. |
| Đầu ra và lưu trữ | Assignment history, SLA breach, task gọi lại |
| Tiêu chí nghiệm thu | Hai Sales nhận cùng lúc chỉ một người thành công; lead ngoài giờ không bị phạt trước ca. |
| Quy tắc liên kết bắt buộc | CAS/version, lịch khả dụng, attempt vs response, race activity/reassign, capacity và backup; FR liên quan: 05,06,35,36. |

### 4.3 UC03 Qualification B2B và B2C

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR04 |
| Tác nhân | Sales và quản lý |
| Đầu vào và tiền điều kiện | Lead có nhu cầu và liên hệ |
| Luồng chính | Nhận/Accepted lead → discovery nhu cầu → B2B/B2C → thu trường tối thiểu/Unknown → kiểm trùng theo nhu cầu → Qualified → tạo/link Deal idempotent và đầu mối buying group tối thiểu nếu B2B |
| Đậu rớt và rẽ nhánh | Đậu: đủ tiêu chí và next action. Thiếu ngân sách: Unknown + nurture có hạn, không bịa. Không phù hợp: disqualify có reason. Khách từ chối: suppression theo phạm vi. |
| Đầu ra và lưu trữ | Deal hoặc lead nurture/disqualified |
| Tiêu chí nghiệm thu | B2C không bắt mã số thuế công ty; B2B nhiều contact không tạo nhiều doanh nghiệp trùng. |
| Quy tắc liên kết bắt buộc | Demand episode, SAL/reject/recycle, B2C buyer, buying group tối thiểu, conversion idempotent; FR liên quan: 01,04,12,28. |

Yêu cầu tư vấn hợp lệ chưa rõ người mua tạo Lead `business_model=Unknown`, có Contact provisional khi cần, source và owner/queue/SLA. Không giữ lead hợp lệ ở quarantine chỉ vì chưa biết business model. Qualification xác nhận B2B/B2C trước Qualified/Converted, sau đó áp điều kiện Account/buyer Contact. Unknown không là NoFit và không bị loại khỏi mẫu số intake hợp lệ.

### 4.4 UC04 Strategy đến campaign launch

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR22, FR23, FR24, FR26 |
| Tác nhân | Strategist, CMO/Manager, khách hàng, người chạy kênh |
| Đầu vào và tiền điều kiện | Brief, SOW, business goal, baseline |
| Luồng chính | Research → diagnosis → strategy approval → plan/budget → IMC/assets → QA/tracking → client approval → go/no-go → launch → theo dõi → post-mortem |
| Đậu rớt và rẽ nhánh | Đậu: đủ gate, đúng phiên bản. Rớt asset hoặc tracking: trả về sửa. Đổi ngân sách: duyệt lại. Thiếu quyền API: task thủ công có chứng cứ. |
| Đầu ra và lưu trữ | Approved strategy/plan/campaign, launch log, learning |
| Tiêu chí nghiệm thu | Không launch bằng bản creative cũ đã bị thay; AI không tự tăng ngân sách. |
| Quy tắc liên kết bắt buộc | Template theo gói, approval đúng subject/version, optimization envelope, quyền tài khoản và tracking khi áp dụng; FR liên quan: 22–26,30. |

### 4.5 UC05 Báo giá và phê duyệt ngoại lệ

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR14 |
| Tác nhân | Sales, trưởng nhóm, giám đốc |
| Đầu vào và tiền điều kiện | Deal qualified, service catalog, brief |
| Luồng chính | Lập quote + SOW → kiểm line type/VAT/cost → tính margin → route approval → khóa version → gửi khách → ghi quyết định |
| Đậu rớt và rẽ nhánh | Đậu: hạn mức và margin hợp lệ. Rớt: người tạo không đủ quyền duyệt, thiếu cost hoặc giá hết hạn. Khách sửa: revision mới, hủy hiệu lực approval cũ tương ứng. |
| Đầu ra và lưu trữ | Quote snapshot và approval trail |
| Tiêu chí nghiệm thu | Giảm giá vượt ngưỡng không gửi như approved; link bản cũ thể hiện superseded. |
| Quy tắc liên kết bắt buộc | Estimate vs binding offer; cost/margin/terms approval; acceptance expired; revision không ghi đè; FR liên quan: 14,21,22,26. |

### 4.6 UC06 Hợp đồng đến kickoff

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR15 |
| Tác nhân | Sales, người triển khai, kế toán, khách |
| Đầu vào và tiền điều kiện | Báo giá chấp thuận, hợp đồng và chứng cứ ký |
| Luồng chính | Xác thực signer/authority → lưu hợp đồng → Won → order → payment schedule → checklist asset → kiểm điều kiện ứng trước → người nhận handoff xác nhận → kickoff |
| Đậu rớt và rẽ nhánh | Đậu: SOW/tiền/owner đủ. Chưa có tiền: pending start. Ngoại lệ có duyệt: cho chạy nhưng gắn risk. Thiếu asset: chờ khách, không giả vờ hoàn tất. |
| Đầu ra và lưu trữ | Contract, project, milestone, handoff record |
| Tiêu chí nghiệm thu | Won không tự trở thành Paid; replay cùng handoff/SOW không tạo thêm project; một MSA có nhiều SOW/project hợp lệ. |
| Quy tắc liên kết bắt buộc | MSA/SOW, handoff acceptance, funding/credit scope, capacity, success plan; nhiều project hợp lệ; FR liên quan: 15,16,20,25,26. |

### 4.7 UC07 Nhận tiền và tính hoa hồng

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR16, FR17 |
| Tác nhân | Ngân hàng/provider, kế toán, worker |
| Đầu vào và tiền điều kiện | Giao dịch xác thực hoặc sao kê đã kiểm tra |
| Luồng chính | Verify và lưu evidence → reconcile canonical receipt xuyên nguồn → ghi nhận tiền → match buyer/nghĩa vụ → kiểm currency/legal entity/số dư → allocate/outbox → invoice mapping khi có → preview → kế toán duyệt cuối kỳ |
| Đậu rớt và rẽ nhánh | Đậu: exact match và còn số dư. Thiếu/thừa: partial/credit. Mơ hồ: unmatched. Callback timeout: query trạng thái trước replay. |
| Đầu ra và lưu trữ | Payment, allocations, ledger, commission entries |
| Tiêu chí nghiệm thu | Replay 5 lần không cộng hoa hồng; tiền media và VAT không vào cơ sở. |
| Quy tắc liên kết bắt buộc | Verification/matching/allocation riêng, cross-source evidence, invoice mapping, earned/payable policy; FR liên quan: 16,17,28. |

### 4.8 UC08 Nghiệm thu và thay đổi phạm vi

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR15, FR18, FR25 |
| Tác nhân | Delivery, Account Manager, khách |
| Đầu vào và tiền điều kiện | Deliverable đúng version, checklist QA |
| Luồng chính | QA nội bộ → review đúng version → phân loại defect/change → defect sửa theo cam kết, đổi ý theo quota/CR → acceptance có authority → billing/collection theo nghĩa vụ áp dụng |
| Đậu rớt và rẽ nhánh | Đậu: evidence acceptance đúng version. Rớt do lỗi: reopen sửa. Thêm yêu cầu: CR báo giá/duyệt, không tự coi là lỗi miễn phí. |
| Đầu ra và lưu trữ | Acceptance, revision, change request, invoice request |
| Tiêu chí nghiệm thu | Không tự nghiệm thu vì khách im lặng trừ điều khoản hợp đồng hợp lệ và quy trình đã duyệt. |
| Quy tắc liên kết bắt buộc | Defect không trừ quota đổi ý; review batch/version; client wait không tự sửa cam kết; impact cost/date; FR liên quan: 14,15,18,23,25,26. |

### 4.9 UC09 Ticket và khảo sát

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR18, FR19 |
| Tác nhân | CSKH/AM, Delivery, khách |
| Đầu vào và tiền điều kiện | Yêu cầu có liên hệ và phạm vi |
| Luồng chính | Intake/provisional khi cần → entitlement/impact/urgency → SLA subject/episode → xác minh/giảm thiểu/cập nhật → resolution evidence → đóng/reopen đúng policy → survey đủ điều kiện → recovery/root cause/verify |
| Đậu rớt và rẽ nhánh | Đậu: có resolution và evidence. Thiếu thông tin: pause giải quyết có giới hạn. Tái phát: reopen nối ticket. Điểm thấp: task follow-up, không sửa điểm. |
| Đầu ra và lưu trữ | Ticket timeline, SLA facts, CSAT response |
| Tiêu chí nghiệm thu | Pause không xóa thời gian phản hồi; survey gửi một lần dù close event replay. |
| Quy tắc liên kết bắt buộc | Entitlement/triage, FRT/NRT/update/resolution, cooldown, recovery và lịch sử reopen; FR liên quan: 18,19,36,39. |

### 4.10 UC10 Gia hạn và upsell

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR09, FR15 |
| Tác nhân | AM, Sales, khách |
| Đầu vào và tiền điều kiện | Hợp đồng đến mốc review/notice theo điều khoản và lịch tương lai; health có nguồn hoặc Unknown được AM rà soát |
| Luồng chính | Rà hiệu quả/deliverables/nợ → review với khách → xác định nhu cầu → renewal deal → báo giá → ký → tạo kỳ mới |
| Đậu rớt và rẽ nhánh | Đậu: ký mới và ghi điều kiện. Rủi ro ticket: ưu tiên khắc phục. Không tái ký: reason và bàn giao tài sản, thu hồi quyền đúng hợp đồng. |
| Đầu ra và lưu trữ | Renewal deal, churn reason, asset return checklist |
| Tiêu chí nghiệm thu | Không gia hạn tự động vì timer nếu hợp đồng không cho phép. |
| Quy tắc liên kết bắt buộc | Notice period, success review, one-off vs recurring, unique reminder, termination/offboarding; FR liên quan: 09,15,18,19,26,28. |

### 4.11 UC11 Rút consent và yêu cầu xóa

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR01, FR09 |
| Tác nhân | Chủ thể dữ liệu, privacy owner, worker |
| Đầu vào và tiền điều kiện | Yêu cầu được xác thực vừa đủ, xác định tenant/purpose |
| Luồng chính | Ghi yêu cầu → chặn marketing ngay → cập nhật consent log → tìm bản sao/export/provider → đánh giá nghĩa vụ lưu giữ → xóa/ẩn danh hoặc hạn chế → thông báo kết quả |
| Đậu rớt và rẽ nhánh | Đậu: dữ liệu thuộc phạm vi được xử lý và có evidence. Cần giữ chứng từ: hạn chế truy cập, ghi cơ sở/thời hạn. Chưa xác thực: yêu cầu thông tin tối thiểu, không tiết lộ hồ sơ. |
| Đầu ra và lưu trữ | Privacy request, suppression, deletion log |
| Tiêu chí nghiệm thu | Journey đang chờ không gửi tiếp; restore backup tái áp dụng deletion ledger. |
| Quy tắc liên kết bắt buộc | Purpose/endpoint scope, identity/merge, job cancel, retention/legal hold, search/file/backup deletion workflow; FR liên quan: 01,02,08,09,34,37,38. |

### 4.12 UC12 Bàn giao khi Sales nghỉ việc

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR08, FR21 |
| Tác nhân | Quản lý, Admin, chủ dữ liệu |
| Đầu vào và tiền điều kiện | Nhân sự chuyển vai trò/nghỉ việc đã xác nhận |
| Luồng chính | Khóa phiên đăng nhập → revoke quyền → liệt kê open work → chuyển owner có xác nhận → thông báo khách phù hợp → kiểm quyền tài sản → đóng checklist |
| Đậu rớt và rẽ nhánh | Đậu: không còn open work vô chủ. Không có người nhận: queue quản lý. Tài khoản cá nhân: xử lý theo thỏa thuận, không giả định lấy được lịch sử. |
| Đầu ra và lưu trữ | Access log, reassignment, checklist |
| Tiêu chí nghiệm thu | Sau commit khóa user/revoke grant, token phiên cũ và mọi request download mới qua URL gateway cũ bị từ chối; thử cả Range/resume, cache, tab khác và link copy. Lịch sử actor giữ nguyên. Không yêu cầu thu hồi byte người dùng đã tải. |
| Quy tắc liên kết bắt buộc | Open work, scheduled intent, approval owner, integration grant, session/file access và actor history; FR liên quan: 08,21,35,37. |

### 4.13 UC13 Hoàn tiền và điều chỉnh hoa hồng

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR16, FR17 |
| Tác nhân | Kế toán, người duyệt tài chính |
| Đầu vào và tiền điều kiện | Receipt Confirmed và evidence, số còn được hoàn, beneficiary đã xác minh, reason và refund authority; Contract/obligation/allocations chỉ bắt buộc theo phần hoàn tương ứng. Khoản chuyển nhầm/unidentified có thể hoàn qua case xác minh tài chính mà không tạo Contract giả. |
| Luồng chính | Xác định hoàn dư/hoàn phần allocation hoặc hỗn hợp → lock và kiểm số dư/components → reserve theo 3.13.4 → duyệt theo authority → dispatch ngoài transaction → xác thực kết quả → ghi Refund và kết thúc reservations atomic; chỉ phần đã allocate mới Reverse allocation và phát commission adjustment đủ điều kiện → đối soát. |
| Đậu rớt và rẽ nhánh | Unknown giữ reservation và reconcile. Hoàn dư không có allocation/commission thì không tạo reversal giả. Kỳ khóa ghi adjustment kỳ mở có link, không sửa payout/kỳ cũ. Thiếu beneficiary/authority hoặc không đủ refund headroom thì giữ case, không dispatch. |
| Đầu ra và lưu trữ | Refund, reversal ledger, commission adjustment |
| Tiêu chí nghiệm thu | Không hoàn quá số còn được hoàn; replay không đảo hai lần. |
| Quy tắc liên kết bắt buộc | Partial refund, paid commission adjustment, locked periods, provider replay và marketing outcome correction; FR liên quan: 16,17,28,29. |

### 4.14 UC14 Mở ngành hoặc client workspace mới

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR22, FR28 và kiến trúc pack |
| Tác nhân | Chủ dự án, Admin, BA, QA |
| Đầu vào và tiền điều kiện | Pack manifest, mục đích xử lý, owner |
| Luồng chính | Tạo workspace → schema migration → policy/feature flag → workflow/KPI template → dữ liệu test → isolation test → enable |
| Đậu rớt và rẽ nhánh | Đậu: không tác động ngành cũ. Mismatch migration: rollback release, không xóa hồ sơ. Contact giống ở khách khác: không auto-merge. |
| Đầu ra và lưu trữ | Pack version, migration log, role bindings |
| Tiêu chí nghiệm thu | Truy cập bằng ID của workspace khác bị chặn ở API, search, export và AI. |
| Quy tắc liên kết bắt buộc | Namespace/schema ownership, allowed cross-scope links, policy fixture, migration và activation gate; FR liên quan: 21,30,37; kiến trúc 2.8. |

### 4.15 UC15 Import và hợp nhất có kiểm soát

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR02, FR28 |
| Tác nhân | Data steward, Sales, privacy owner |
| Đầu vào và tiền điều kiện | CSV/template, nguồn dữ liệu và cơ sở sử dụng |
| Luồng chính | Upload → quét tệp → dry-run → mapping → chuẩn hóa → duplicate candidates → steward duyệt → commit batch → đối chiếu |
| Đậu rớt và rẽ nhánh | Đậu: báo cáo tổng nguồn = accepted + rejected + duplicate. Sai dòng: file lỗi có mã, không nhập im lặng. Rollback theo batch chỉ khi không có phụ thuộc mới. |
| Đầu ra và lưu trữ | Import batch, mapping, rejects, merge history |
| Tiêu chí nghiệm thu | Không import consent=true mặc định; điện thoại tổng đài không gộp mọi người. |
| Quy tắc liên kết bắt buộc | Staging/dry-run/provenance, source IDs, consent không default true, business duplicates, repair; FR liên quan: 01,02,31,33,37. |

### 4.16 UC16 Báo cáo chiến dịch và vòng học hỏi

| Thành phần | Đặc tả |
| --- | --- |
| Yêu cầu liên quan | FR24, FR26, FR28, FR29 |
| Tác nhân | Analyst, CMO, khách |
| Đầu vào và tiền điều kiện | Spend, lead, outcome, KPI version, period |
| Luồng chính | Load snapshot → kiểm freshness/duplicates → reconcile → tính chỉ số → giải thích gap → review → publish report version → learning/experiment |
| Đậu rớt và rẽ nhánh | Đậu: số truy về nguồn, đúng client. Thiếu dữ liệu: hiện thiếu, không điền 0. Client dispute: correction version, không ghi đè báo cáo đã gửi. |
| Đầu ra và lưu trữ | Report snapshot, metric facts, learning item |
| Tiêu chí nghiệm thu | Tổng attribution không vượt outcome; GMV khách không cộng doanh thu agency. |
| Quy tắc liên kết bắt buộc | Metric definition, cost/time/scope, late data, uncertainty và quyết định cải tiến có owner; FR liên quan: 22,24,26,28,29. |

### 4.17 UC17 Nhận tin năm kênh về cùng điểm làm việc

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân và tiền điều kiện | Khách, provider, adapter, worker; connection active và đã xác thực; form có cấu hình workspace server-side |
| Đầu vào | Webhook/message notification/submission với ID, thời điểm, nội dung hoặc tham chiếu nội dung |
| Luồng chính | Xác minh → lưu durable event → ACK → fetch nếu cần → normalize → dedup → identity lookup → lưu Message/Conversation → route → hiện Inbox; tạo Lead chỉ khi intent phù hợp |
| Đậu | Một tin chuẩn hóa xuất hiện đúng workspace, nguồn và người nhận; có audit/correlation ID; SLA bắt đầu theo thời gian quy định |
| Rớt và nhánh | Sai chữ ký: reject; schema lạ: quarantine; token lỗi: dừng fetch và cảnh báo; trùng: no-op; không rõ danh tính: tạo provisional contact, không merge đoán |
| Đầu ra và kiểm tra | Message, conversation, assignment, task nếu cần; replay 10 lần vẫn một hiệu ứng nghiệp vụ |
| Quy tắc liên kết bắt buộc | Capability theo account, thread/ID namespace, intake không tạo lead từ mọi message, provisional path; FR liên quan: 30–33,38,39. |

### 4.18 UC18 Liên kết Facebook, Zalo và Email của cùng khách

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales đề xuất, data steward duyệt; 3 identities trong cùng workspace và bằng chứng xác minh |
| Luồng chính | Tìm candidate → xem provenance → kiểm tra quyền → preview merge → duyệt → relink identities và refs trong transaction → lưu merge journal |
| Đậu | Timeline một Contact, ba conversation riêng; role công ty giữ nguyên; chỉ đọc phần có quyền |
| Rớt/nhánh | Tên trùng: không đủ; email chung: không merge người; khác workspace: chặn; conflict consent: giữ từng scope; phát hiện sai: undo qua journal |
| Đầu ra | Contact survivor, identity links, audit; không sửa provider ID hoặc tạo quyền gửi mới |
| Quy tắc liên kết bắt buộc | Không dùng tên/hash chưa xác minh làm authority; merge/unmerge ảnh hưởng quyền/consent rõ; FR liên quan: 01,02,31,37. |

### 4.19 UC19 Trả lời từ CRM và xử lý gửi chưa rõ kết quả

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales có quyền gửi; conversation cụ thể, body, attachment sạch, client_request_id |
| Luồng chính | Chọn người nhận/kênh → policy gate → lưu send intent/outbox → worker gửi → nhận acknowledgment → cập nhật trạng thái theo event provider |
| Đậu | Provider chấp nhận và có external ID; UI chỉ hiện delivered/read khi có chứng cứ tương ứng |
| Rớt/nhánh | Hết cửa sổ/thiếu quyền: blocked; 429: backoff; timeout sau request: unknown_outcome, tra cứu nếu được; attachment lỗi: không gửi; echo: gắn vào tin đã gửi |
| Đầu ra | Message và send attempts; không nhân đôi khi double-click; thao tác gửi lại bất định phải cảnh báo rủi ro trùng và có audit |
| Quy tắc liên kết bắt buộc | Recipient/attachment approval, eligibility dispatch, idempotency, timeout reconcile/manual policy; FR liên quan: 08,09,32,34,40. |

### 4.20 UC20 Chuyển ca, quá SLA và bàn giao khách

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Router, Sales, trưởng nhóm; lịch ca, capacity, skill, SLA policy |
| Luồng chính | Queue → atomic claim → timer phản hồi người thật → cảnh báo → escalation/chuyển người có capacity → handoff note → trả lời |
| Đậu | Có người chịu trách nhiệm, không mất tin; lịch sử chuyển người đầy đủ, SLA không bị reset |
| Rớt/nhánh | Không ai trực: queue có owner nhóm/on-call; autoack: không tính hoàn thành SLA; agent nghỉ việc: revoke session và chuyển việc; không tự sửa commission owner |
| Đầu ra | Assignment history, SLA episode, human reply activity và lý do escalation |
| Quy tắc liên kết bắt buộc | Durable assignment/version hoặc lease đủ điều kiện, promise/clock tiếp tục, owner deal không tự đổi; FR liên quan: 05,08,35,36. |

### 4.21 UC21 Mất kết nối và phục hồi không gây spam

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Operator, connection owner; cursor cuối, lỗi OAuth/subscription hoặc DLQ |
| Luồng chính | Phát hiện degraded → cảnh báo → reauthorize/renew → đọc delta từ checkpoint hoặc backfill được phép → dedup → đối soát → xác nhận healthy |
| Đậu | Dữ liệu phục hồi có nhãn historical; không tái gửi tin hoặc tạo lead/commission; coverage và gap hiển thị |
| Rớt/nhánh | API không cho lịch sử: ghi khoảng thiếu, không báo “đầy đủ”; event độc: quarantine; backlog outbound hết hạn: cancel/blocked theo policy |
| Đầu ra | Sync run, counts và checkpoint; báo cáo khoảng dữ liệu không thể phục hồi |
| Quy tắc liên kết bắt buộc | Cursor/quota/token, bounded replay, expired intents, echo/backfill và coverage/freshness; FR liên quan: 30,33,34,38. |

### 4.22 UC22 Từ yêu cầu trong inbox đến dự án marketing

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales, strategist, account manager; form/DM/email yêu cầu dịch vụ |
| Luồng chính | Phân loại inquiry → qualify B2B/B2C → xác minh Contact/Account và vai trò duyệt → brief → Deal → SOW/báo giá → ký/đặt cọc → kickoff → deliverables → nghiệm thu → gia hạn |
| Đậu | Mọi bước có owner, next action và liên kết nguồn; revenue chỉ từ nghiệp vụ hợp lệ, không từ lượt chat |
| Rớt/nhánh | Khiếu nại khách cũ: Ticket; yêu cầu ngoài SOW: change request; không đủ fit: nurture có điều kiện hoặc lost reason; nhiều người cùng Account không bị gộp Contact |
| Đầu ra | Chuỗi trace message → lead/deal → contract/project/ticket, giúp tìm lại cam kết khi bàn giao |
| Quy tắc liên kết bắt buộc | Liên kết request có mục đích; thẩm quyền/quote/SOW/handoff; không chat-to-project bỏ qua gate; FR liên quan: 04,14,15,32,39. |

### 4.23 UC-W01–10 — Luồng quản lý công việc dùng chung

Mã UC-W01–10 là mã canonical mới của Master, giữ UC01–22 nguyên trạng. Quy tắc tại 3.14, quyền 6.6, API 5.20 và UAT 9.16.

#### 4.23.1 Tổng quan use case

| ID và tên | Primary / Secondary | Preconditions và trigger | Success / failure |
| --- | --- | --- | --- |
| UC-W01 Tạo và giao việc | Creator/Manager; worker | Quyền tạo trong scope; bấm Create hoặc event template | Task + assignment + audit/outbox; sai input rollback, không notify |
| UC-W02 Nhận hoặc từ chối việc | Assignee/Queue member; router | Offer active hoặc queue grant; Accept/Claim/Decline | Một assignment accepted; conflict 409 hoặc decline có lý do về queue |
| UC-W03 Thực hiện và cộng tác | Assignee/Collaborator; scanner | Có quyền/version; start/comment/checklist/block | Update/evidence/mention đúng grant; lỗi file quarantine, không phát ra ngoài |
| UC-W04 Xin và duyệt đổi hạn/chuyển việc | Assignee/Manager; notifier | Task active; authority và người đích hợp lệ | Decision/assignment history giữ baseline; lỗi giữ owner/due cũ |
| UC-W05 Nộp và duyệt kết quả | Assignee/Reviewer; worker | Evidence, children, dependency, version đạt | Immutable submission rồi approve/reject; stale review 409 |
| UC-W06 Quản lý cha/con và phụ thuộc | Manager/Assignee có quyền; graph validator | Task cùng scope; add dependency/subtask | DAG và parent links hợp lệ; cycle rollback |
| UC-W07 Sinh việc định kỳ/mẫu | Manager; scheduler | Template/rule Active và timezone; đến kỳ | Một occurrence một task/batch; lỗi ghi gap không tự bỏ qua |
| UC-W08 Theo dõi và điều hành | Cá nhân/Lead/CEO; metrics job | Read grants; mở My Work/Team/Portfolio | Projection đúng quyền/freshness; thiếu dữ liệu hiện Unknown |
| UC-W09 Bàn giao khi nghỉ/chuyển đội | Manager/Ops; permission service | Quyết định có effective time; preview open work | Revoke + queue/handoff có audit; orphan về queue quản lý |
| UC-W10 Đồng bộ PMS | Integration owner; connector | Source mapping/version/capability verified; callback/poll | Canonical update hoặc conflict rõ; retry idempotent, không last-write-wins |

Post-condition chung: transaction thành công ghi domain change + audit + outbox; notification được gửi sau commit. Provider/email thông báo lỗi không rollback task đã tạo. Actor/tenant/workspace suy từ session/grant, không tin giá trị client tự gửi.

#### 4.23.2 Luồng chính, rẽ nhánh và ngoại lệ

#### UC-W01 / UC-W02 — Tạo, giao, nhận

1. [Creator] Chọn personal/team/CRM/project; nhập mục tiêu, đầu ra, due và cách giao: một owner, queue, hoặc tạo bản riêng từng người.
2. [System] Kiểm scope, role, linked record ACL, assignee active, reviewer và thời hạn; preview audience.
3. [Creator] Xác nhận; [System] commit Task/assignment offer/audit/outbox với idempotency key, trả task ID.
4. [Worker] Gửi notification cho người được phép; queue có alert cho queue manager, không chờ có assignee mới báo tuổi việc.
5. [Assignee] Accept hoặc Decline kèm lý do; [Queue member] Claim nếu chưa có owner.
6. [System] CAS task/version và assignment, kiểm lại eligibility; nhận thành công ghi accepted_at. Không có quyền/đã có người nhận thì 403/409.

Alternative 1a: personal tự giao, không yêu cầu accept. 1b: broadcast tạo batch và task độc lập theo từng user, không gọi đó là cộng tác trên một task. Exception 2E: thiếu quyền record hoặc người đã suspended → reject; 3E: double submit → cùng task; 5E: decline/offer timeout → queue có manager, giữ thời điểm giao đầu. Bulk lớn dùng job có kết quả từng item; không giả tất cả thành công khi một phần lỗi.

#### UC-W03 / UC-W06 — Thực hiện, phối hợp, phụ thuộc

1. [Assignee] Start; [System] kiểm accepted assignment, hard blockers và dependencies.
2. [Assignee/Collaborator] Thêm comment, file, checklist hoặc kết quả; [System] lưu actor/version, sanitize nội dung và scan file.
3. [Người có quyền] Tạo subtask/edge phụ thuộc; [System] kiểm graph dưới concurrency và commit nếu không cycle.
4. [Assignee] Báo blocked kèm nguyên nhân, người cần hỗ trợ, review_at; [System] thông báo đúng người và giữ due.
5. [Người chịu trách nhiệm blocker] Gỡ blocker; [System] ghi thời gian chờ, kiểm lại eligibility trước bước tiếp.

Alternative 2a: @mention người ngoài task → không tự mở quyền; hiện đề nghị thêm thành viên để người có quyền duyệt. 3a: dependency qua task bị hạn chế quyền → chỉ hiện “Phụ thuộc bị hạn chế truy cập”, không lộ title. Exception 1E: predecessor bị reopen → future start bị chặn, task đã chạy được đánh dấu at-risk và báo manager, không tự xóa work; 3E: đồng thời A→B và B→A → serialization/graph lock làm một request thất bại; 2E: file malware → quarantine, không cho submit dùng file đó.

#### UC-W04 — Gia hạn hoặc chuyển người

1. [Assignee] Nêu due mới hoặc người nhận, lý do và tác động.
2. [System] Tạo change request gắn task version/due version; due và owner hiện tại chưa đổi.
3. [Manager có authority] Xem ảnh hưởng milestone, workload, customer promise và chọn duyệt/từ chối.
4. [System] Recheck authority/version/target; lưu decision và áp thay đổi nguyên tử, phát notify.
5. [Người nhận mới] Accept nếu policy yêu cầu; chuyển sau khi nhận hoặc chuyển về queue theo chế độ handoff đã chọn.

Alternative 1a: personal task không cam kết ngoài được tự đổi due, vẫn có history. 3a: vượt committed customer date → phải đi change control của M16/M08, không chỉ duyệt deadline task. Exception 4E: người đích vừa nghỉ/không còn grant → reject, giữ owner cũ; 4E2: hai người duyệt hai ngày khác nhau → chỉ decision khớp version có hiệu lực. Nếu revoke khẩn cấp không thể chờ accept, chuyển open work vào queue quản lý trong cùng kế hoạch bàn giao.

#### UC-W05 — Nộp, kiểm, hoàn thành

1. [Assignee] Nộp result/evidence và chọn Submit.
2. [System] Kiểm required checklist, mandatory children, blocker/waiver, version, file clean; snapshot submission.
3. [System] Nếu không review_required thì Done; nếu có thì InReview, tạo review_due và báo reviewer.
4. [Reviewer] Đọc đúng version, approve hoặc reject có lý do.
5. [System] CAS decision; approve → Done, reject → InProgress và rework event; giữ submission cũ.
6. [System] Cập nhật KPI/task downstream; chỉ phát event “task completed”, không tự tạo “client accepted/paid”.

Alternative 3a: reviewer nghỉ việc → reviewer queue/backup theo authority, không tự approve. Exception 2E: còn con bắt buộc chưa xong → chặn với danh sách có quyền xem; 4E: owner sửa kết quả trong lúc review → bắt tạo submission mới, reviewer cũ nhận conflict; 5E: approve lặp → cùng decision, không double complete. Bấm đánh dấu hoàn thành một follow-up “gọi lại” không chứng minh khách đã được liên hệ thành công.

#### UC-W07 — Mẫu và định kỳ

1. [Manager] Chọn mode `CALENDAR` hoặc `AFTER_COMPLETION`, timezone, interval, start/end, owner/queue và template version.
2. [System] Preview ba lần sinh tiếp theo, chính sách ngày nghỉ, tháng thiếu ngày và catch-up.
3. [Manager] Activate; [Scheduler] tính occurrence key bằng rule version và kỳ danh nghĩa, không theo thời điểm chạy job.
4. [System] Recheck membership/quyền/context, upsert occurrence + task + outbox atomic.
5. [System] Ghi sinh thành công hoặc failed occurrence có owner xử lý; sửa rule chỉ ảnh hưởng occurrence chưa phát hành.

Calendar tạo kỳ mới ngay cả khi kỳ cũ còn mở, có backlog warning; after-completion chỉ tính sau Done của kỳ trước. Cancel mặc định không kích hoạt lần tiếp; manager chọn resume/skip có audit. Không sao chép result/comment/approval/time entries từ lần cũ.

Ví dụ: báo cáo thứ Hai 09:00 phải dùng CALENDAR; “kiểm tra lại sau 7 ngày kể từ khi sửa xong” dùng AFTER_COMPLETION. Nếu rule ngày 31 gặp tháng ngắn, mặc định đề xuất last-day-of-month và hiển thị preview; không tự đổi timezone. Catch-up mặc định một kỳ gần nhất và ghi các kỳ đã bỏ qua, không đổ hàng nghìn task; việc có nghĩa vụ bắt buộc đủ mỗi kỳ phải chọn catch-up-all có giới hạn/job review.

#### UC-W08 / UC-W09 / UC-W10 — Điều hành, bàn giao, đồng bộ

UC-W08: [User] chọn view/filter → [System] áp resource ACL trước count/aggregation → trả dữ liệu có freshness → [Manager] drill-down và thực hiện command phân lại việc, không sửa trực tiếp tổng KPI. Thiếu estimate/availability hiển thị coverage, không suy thành rảnh. Export kiểm quyền và giới hạn riêng.

UC-W09: [Ops] lập danh sách open task, review, template/rule, queue và automation của người sắp nghỉ → [Manager] chỉ định successor/queue → [System] revoke đúng effective time, giữ actor lịch sử, chuyển trách nhiệm còn mở → [Successor] xác nhận handoff. Không chỉ đổi assignee của task mà để recurring rule tiếp tục giao cho người cũ. Không có successor thì manager queue chịu trách nhiệm, không xóa việc.

UC-W10: [Connector] nhận source event → [System] durable receipt/dedup → kiểm external version/mapping/permission → apply nếu hợp lệ, hoặc conflict quarantine → cập nhật checkpoint sau commit. Edit từ CRM tới PMS trả pending_sync cho tới khi source chấp nhận; rejected_due/parent_closed hiện lỗi nghiệp vụ. Outage giữ local request/history, không nhận là task đã đổi thành công ở nguồn. Chuyển source of truth cần kế hoạch freeze/reconcile/import/cutover riêng.

<a id="chuong-5"></a>

## CHƯƠNG 5 THIẾT KẾ CƠ SỞ DỮ LIỆU VÀ TỪ ĐIỂN DỮ LIỆU

### 5.1 Nguyên tắc schema

PostgreSQL là lựa chọn thiết kế ban đầu. UUID làm định danh; thời gian dùng timestamptz lưu UTC, hiển thị Asia/Ho_Chi_Minh; tiền numeric(18,2), VND làm tròn 0 chữ số ở bước nghiệp vụ có quy tắc. Không dùng float cho tiền. NN = NOT NULL; NULL là chưa biết/không áp dụng, không thay bằng chuỗi rỗng. PK/FK dưới đây là khóa logic: quan hệ nội workspace kiểm tenant/workspace; quan hệ cross-workspace chỉ hợp lệ theo bridge được cấp phép bên dưới. Không mặc định mọi FK đều phải cùng workspace, cũng không dùng FK tenant-only để bỏ kiểm quyền.

Bảng nghiệp vụ scoped có trường chung dưới đây; catalog cấp tenant có ngoại lệ được khai báo, không ép Workspaces/Tenants tự tham chiếu workspace. Mỗi bảng đích có UNIQUE(tenant_id,id), và bảng scoped có UNIQUE(tenant_id,workspace_id,id) để FK ghép. Ledger giữ số tiền/policy bất biến; trạng thái workflow là projection từ status events. Schema là dictionary triển khai cần xuất DDL/OpenAPI và kiểm thử trước production; không có hai bộ tên bảng cho cùng thực thể.

Workspaces có loại AGENCY/CLIENT; tên cũ `client_workspace_id`/`Client_Workspaces` của v1.2 chỉ là mapping migration, không là cột/bảng mới song song. Dữ liệu chưa phân loại giữ ở intake/quarantine có scope xác định, không tự gán NULL để bypass quyền. Cross-scope link hợp lệ (CLIENT workspace → Account trong AGENCY) dùng relation rõ và quyền/publish tối thiểu; không áp same-workspace một cách mù lên liên kết đó.

| Trường chung | Kiểu | Ràng buộc | Ý nghĩa |
| --- | --- | --- | --- |
| id | uuid | PK, NN | ID bản ghi |
| tenant_id | uuid | FK tenants, NN | Tổ chức sở hữu; suy từ session được xác thực |
| branch_id | uuid | FK Branches; bắt buộc nếu giao dịch được phân nhánh | Phạm vi vận hành; shared catalog/account theo grant, không thay pháp nhân |
| legal_entity_id | uuid | FK Legal_Entities, NN cho hợp đồng/tài chính | Bên ký/hạch toán/nhận tiền; giữ một pháp nhân mặc định khi pilot |
| business_line_id | uuid | FK business_lines | Dòng nghiệp vụ |
| workspace_id | uuid | FK Workspaces, NN với dữ liệu scoped | Workspace AGENCY/CLIENT; không dùng NULL để biểu diễn agency |
| created_at / updated_at | timestamptz | NN, server generated | Ngày tạo/cập nhật; UTC |
| created_by / updated_by | uuid | FK users hoặc service principal | Tác nhân có trách nhiệm |
| row_version | bigint | NN, default 1, >0 | Optimistic lock; API expected_version đối chiếu trường này |
| archived_at | timestamptz | NULL | Archive không đồng nghĩa đã xóa dữ liệu cá nhân |

```mermaid
erDiagram
  Tenants ||--o{ Branches : contains
  Tenants ||--o{ Workspaces : isolates
  Accounts ||--o{ Contact_Account_Roles : represented_by
  Contacts ||--o{ Contact_Account_Roles : acts_for
  Contacts ||--o{ Leads : identifies_demand
  Accounts o|--o{ Deals : buys_B2B
  Contacts o|--o{ Deals : buys_B2C
  Leads o|--o{ Deals : qualifies
  Deals ||--o{ Quotes : proposes
  Quotes ||--o{ Contracts : accepted_as
  Contracts ||--o{ Orders : governs
  Contracts o|--o{ Projects : delivered_as
  Projects ||--o{ Deliverables : produces
  Deliverables ||--o{ Acceptances : reviewed_by
  Orders ||--o{ Invoice_Lines : billed_as
  Payments ||--o{ Payment_Allocations : allocates
  Orders ||--o{ Order_Lines : itemizes
  Order_Lines ||--o{ Payment_Obligations : schedules
  Payment_Obligations ||--o{ Payment_Allocations : receives
  Payment_Allocations ||--o{ Invoice_Allocation_Links : reconciles
  Invoice_Lines ||--o{ Invoice_Allocation_Links : maps
  Payment_Allocations ||--o{ Commission_Entries : generates
  Contacts ||--o{ Activities : has
  Contacts ||--o{ Tickets : requests
  Contacts ||--o{ Consent_Logs : records
  Workspaces ||--o{ Strategy_Briefs : owns
  Strategy_Briefs ||--o{ Marketing_Plans : directs
  Marketing_Plans ||--o{ Campaigns : organizes
```

ERD thể hiện quan hệ chính; mọi quan hệ còn chịu tenant/workspace policy. Với deal B2B bắt buộc Account, deal B2C bắt buộc buyer Contact; không tạo pháp nhân giả. Mỗi hợp đồng có thể có nhiều kỳ/order và mỗi hóa đơn có thể được thanh toán nhiều đợt.

#### Ràng buộc nội workspace và cross-workspace được cấp phép

Nội workspace dùng FK(tenant_id,workspace_id,target_id) đến key tương ứng. Cross-workspace như CLIENT Project→AGENCY Contract dùng FK vật lý cùng tenant và Workspace_Account_Links/Contract_Workspace_Grants có source/target workspace, customer account, allowed relation, effective dates và authority. Contract buyer phải khớp billing legal party của workspace/brand được ủy quyền. Nếu workspace không theo account chuẩn, quan hệ thay thế phải được phê duyệt, không bỏ kiểm.

FK composite qua bridge hoặc constraint trigger được thiết kế để kiểm cả insert/update child, đổi customer/contract/bridge đích và revoke; transaction locking bảo toàn tính đúng khi hai bên đổi đồng thời. Không dùng CHECK gọi bảng khác như sự bảo đảm toàn vẹn liên tục. Link không tự cấp quyền đọc tài liệu; publish/field ACL vẫn kiểm. Tenant context thiếu phải default-deny. Cấm merge người qua workspace chỉ để vượt ràng buộc.

Currency chỉ được bật từ allowlist đã được Finance/chủ nghiệp vụ phê duyệt, có precision/minor-unit exponent, rounding/caps, connector/ERP mapping và UAT. VND là currency cấu hình tham chiếu; chỉ bật mã tiền có precision, rounding và mapping đã được kiểm. Danh mục tiền tệ thực dùng do Finance xác nhận theo A.6. Mã char(3) không tự chứng minh hệ thống hỗ trợ currency đó. Nếu precision/quantum nhỏ hơn khả năng storage thì phải sửa schema trước enable, không tự FX hoặc làm tròn chứng từ nhập.

Mọi amount/quantity/rate/share tính tiền phải là số hữu hạn; API/import/connector từ chối NaN và ±Infinity trước ghi. Tại PostgreSQL dùng domain hoặc CHECK rõ `value NOT IN ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)` bên cạnh NULL/range policy; không coi `amount>0` là đã chặn NaN. Với cột numeric(18,2), Infinity bị giới hạn precision cũng không thay việc validate finite xuyên API và các cột numeric không ràng precision. Trước cast sang kiểu storage, parse Decimal chính xác, kiểm range/quantum và reject dữ liệu không hợp lệ; không để phép coercion của cột âm thầm làm tròn chứng từ nhập.

Giá/quantity/rate trung gian có precision do pricing policy quy định; các amount đã post VND phải là số nguyên đồng. Rounding chỉ diễn ra tại bước nghiệp vụ được snapshot theo 3.13.4; khi đã post, các cấu phần và tổng phải khớp integer units. Invoice ERP giữ nguyên số nguồn, sai quantum được reconcile, không tự sửa chứng từ. Mở rộng currency có quantum nhỏ hơn khả năng storage hiện tại bắt buộc sửa schema trước enable; không chỉ thêm mã currency.

### 5.2 Bảng Leads

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| contact_id | uuid | FK Contacts, NN khi tạo Lead nghiệp vụ | Intake event lưu trước; tạo/link contact provisional cùng transaction khi cần consent/Lead |
| account_id | uuid | FK Accounts, NULL | Có thể thiếu với B2C |
| business_model | varchar(12) | NN; Unknown/B2B/B2C; default Unknown nếu intake chưa rõ | Unknown vẫn được queue/owner/SLA; không suy từ domain/email. Trước Qualified/Converted và tạo Deal phải xác nhận B2B/B2C; lưu actor/evidence của phân loại. |
| source_code | varchar(50) | NN | Nguồn tạo lead |
| source_record_id | varchar(255) | NULL; unique có scope nguồn | Chống trùng sự kiện nguồn |
| campaign_id | uuid | FK Campaigns, NULL | Campaign acquisition đúng workspace |
| status | varchar(24) | NN, state machine | New/Assigned/Contacting/Qualified/Nurture/Dormant/Disqualified/Converted |
| owner_id | uuid | FK Users, NULL chỉ khi queued | Người phụ trách |
| queue_id | uuid | FK Queues, NULL | CHECK owner hoặc queue khi lead hoạt động |
| received_at | timestamptz | NN | Thời điểm nhận; không sửa |
| sla_due_at | timestamptz | Projection từ SLA_Episodes | Hạn obligation theo policy/subject; không reset khi đổi owner |
| handover_status / handover_policy_version | text | Pending/Accepted/Rejected/Recycled; policy version | MQL/SAL/SQL và reason/evidence trong Lead_Transitions |
| previous_lead_id / demand_key | uuid / text | FK Leads NULL; scoped demand key | Liên kết nhu cầu quay lại; không dùng để tự merge người |
| first_attempt_at | timestamptz | NULL | Lần tiếp cận có chứng cứ |
| score | smallint | NULL hoặc 0..100 | Rule score |
| score_version | varchar(30) | NULL | Phiên bản công thức |
| next_action_at | timestamptz | Bắt buộc cho lead đang chăm sóc | Hạn hành động tiếp theo |
| disqualify_reason | varchar(80) | Bắt buộc khi Disqualified | Mã lý do |

### 5.3 Bảng Contacts

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| display_name | varchar(255) | NN | Tên giữ dấu, chưa biết được gắn nhãn rõ |
| phone_ciphertext | bytea | NULL, mã hóa trường | Số điện thoại đã chuẩn hóa |
| phone_lookup_hash | bytea | NULL, indexed non-unique | HMAC để tìm ứng viên, không tự merge |
| email_ciphertext | bytea | NULL, mã hóa | Email; không global unique |
| email_lookup_hash | bytea | NULL, indexed non-unique | Tra cứu có kiểm soát |
| preferred_channel | varchar(30) | NULL | Sở thích không thay consent |
| lifecycle_stage | varchar(30) | NN | Subscriber/Lead/Customer/Inactive; khác trạng thái nhu cầu |
| identity_status | varchar(30) | NN | Provisional/Verified/Conflict; không trộn vào lifecycle |
| owner_id | uuid | FK Users | Owner hồ sơ |
| verified_at | timestamptz | NULL | Thông tin xác minh mức hồ sơ; identity có bằng chứng riêng |
| merged_into_id | uuid | FK Contacts, NULL | Không tự tham chiếu; không tạo cycle |
| traits | jsonb | NN default {} | Trường mở rộng qua schema validator |

### 5.4 Bảng Accounts

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| legal_name | varchar(255) | NN | Pháp nhân/doanh nghiệp B2B |
| tax_id / tax_country / tax_scheme | varchar / char(2) / text | NULL khi chưa rõ; legal identity đã xác minh unique theo tenant/workspace/country/scheme/tax_id | Account pháp nhân canonical; brand/business unit tham chiếu billing Account, không dùng parent_account_id để cho mọi account con trùng MST |
| domain | varchar(255) | NULL, không unique toàn cục | Chỉ bằng chứng liên kết, không định danh chắc chắn |
| parent_account_id | uuid | FK Accounts, NULL | Kiểm cycle quan hệ mẹ con |
| industry_code | varchar(50) | NULL | Ngành của khách, khác ngành của CRM pack |
| owner_id | uuid | FK Users, NN | Account owner |
| billing_address | text | NULL | Địa chỉ thanh toán |
| lifecycle_stage | varchar(30) | NN | Target/Active/Inactive |
| service_health | smallint | NULL hoặc 0..100 | Có phiên bản và freshness |

### 5.5 Bảng Deals

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| lead_id | uuid | FK Leads, NULL | Nguồn phát sinh |
| account_id | uuid | FK Accounts, B2B bắt buộc | Đơn vị mua |
| buyer_contact_id | uuid | FK Contacts, B2C bắt buộc | Cá nhân mua hoặc liên hệ chính |
| pipeline_id | uuid | FK Pipelines, NN | Pipeline có business_model |
| stage_id | uuid | FK Pipeline_Stages, NN | Stage thuộc đúng pipeline/version |
| owner_id | uuid | FK Users, NN | Sales chính |
| service_amount | numeric(18,2) | NN >=0 | Giá trị dịch vụ dự kiến không VAT |
| media_amount | numeric(18,2) | NN >=0 default 0 | Media riêng |
| currency | char(3) | NN | VND mặc định |
| expected_close_date | date | NULL | Ngày dự kiến, khác ngày thực |
| closed_at | timestamptz | NULL | Thời điểm Won/Lost, có stage history |
| lifecycle_status / work_state | text / text | Open/Won/Lost theo stage category; Active/OnHold khi Open | Hoãn không thay stage_id Proposal/Negotiation; consistency kiểm trong command |
| on_hold_since / hold_reason / review_at / previous_deal_id | timestamptz / text / timestamptz / uuid | Lý do/hẹn khi OnHold; lineage FK NULL | Hold interval ghi history, accumulated_hold_seconds là cache readonly có thể rebuild |
| lost_reason | varchar(80) | NN khi Lost | Bắt buộc lý do |
| next_action_at | timestamptz | NN khi open | Hạn tiếp theo |
| commission_policy_snapshot_id | uuid | FK Policy_Snapshots, NULL khi PendingPolicy hoặc chưa áp commission | Snapshot default được duyệt cho cơ hội; không trỏ rule live. Chính sách cuối áp dụng theo từng Order_Line/pool/eligible allocation; không đổi người hưởng lịch sử theo owner hiện tại. |

Conversion có stable `conversion_key` theo tenant/workspace/Lead/demand và `opportunity_intent_key` do server xác định, khác HTTP request key. Concurrent conversion của cùng logical intent trả cùng Deal/result refs. Nhu cầu có nhiều cơ hội thật phải có intent keys riêng và evidence/actor; không UNIQUE toàn cục `lead_id` vì có thể có nhiều Deal hợp lệ. Conversion mapping lưu result refs/policy/actor; chỉ commit Converted sau khi tạo/link kết quả thành công.

### 5.6 Bảng Orders

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| deal_id | uuid | FK Deals, NN | Nguồn bán |
| contract_id | uuid | FK Contracts, NN | Điều khoản chi phối |
| order_no | varchar(50) | NN unique tenant, gồm cả bản archived | Mã đã phát hành không tái sử dụng; số nháp khác reference thanh toán. Nếu cần numbering theo pháp nhân/series phải có ADR và match có scope, không partial unique theo archived_at. |
| status | varchar(30) | NN | Draft/Confirmed/InDelivery/Completed/Cancelled/Terminated |
| currency | char(3) | NN | Không phân bổ chéo tiền tệ trực tiếp |
| subtotal | numeric(18,2) | NN >=0 | Trước thuế sau giảm |
| tax_amount | numeric(18,2) | NN >=0 | Theo chứng từ được duyệt |
| total_amount | numeric(18,2) | NN >=0 | CHECK total = subtotal + tax |
| payment_state | varchar(30) | NN | Unpaid/Partial/Paid/PartialRefund/Refunded projection; Completed/Terminated không tự Paid |
| service_start / service_end | date | NULL, end >= start | Kỳ cung cấp |
| external_erp_id | varchar(255) | NULL unique theo connector | Mapping ERP |

### 5.7 Bảng Activities

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| contact_id | uuid | FK Contacts, NULL | Chủ thể liên quan |
| account_id | uuid | FK Accounts, NULL | Tổ chức liên quan |
| lead_id / deal_id | uuid | FK Leads/Deals, NULL | Quan hệ tường minh |
| campaign_id | uuid | FK Campaigns, NULL | Nguồn campaign |
| actor_id | uuid | FK Users/service principal, NN | Người thực hiện/service |
| source_channel_identity_id / origin_contact_id | uuid | FK scoped NULL theo nguồn | Provenance để merge/unmerge và trace hoạt động |
| activity_type | varchar(30) | NN | Call/Email/Meeting/Message/Note |
| occurred_at | timestamptz | NN | Khi hoạt động xảy ra |
| received_at | timestamptz | NN | Khi hệ thống nhận |
| provider_event_id | varchar(255) | NULL unique connector scope | Chống trùng |
| outcome | varchar(50) | NULL | Connected/NoAnswer/Delivered/... |
| evidence_asset_id | uuid | FK Assets, NULL | Recording hoặc tài liệu |
| summary | text | NULL, kiểm quyền | Tóm tắt được người dùng xác nhận |
| ai_draft | jsonb | NULL | Không coi là dữ liệu đã xác minh |

### 5.8 Bảng Tickets

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| contact_id | uuid | FK Contacts, NN | Người yêu cầu |
| account_id | uuid | FK Accounts, NULL | B2B |
| contract_id / project_id | uuid | FK Contracts/Projects, NULL | Phạm vi phục vụ |
| subject | varchar(255) | NN | Tóm tắt không lộ dữ liệu không cần thiết |
| description | text | NN | Chi tiết kiểm quyền |
| severity | varchar(4) | S1/S2/S3; NULL chỉ khi triage_state=Pending | Hoàn tất triage phải có severity theo impact×urgency; chưa rõ vẫn tiếp nhận vào queue, không chặn containment. |
| entitlement_snapshot_id / business_subject_id | uuid | FK Entitlement_Snapshots / Business_Subjects | Scope/SLA/quyền hỗ trợ và subject chuẩn |
| status | varchar(30) | NN | Open/InProgress/WaitingCustomer/Resolved/Closed |
| owner_id | uuid | FK Users, NULL khi queued | Người xử lý |
| queue_id | uuid | FK Queues; bắt buộc khi active mà chưa có owner | Open/InProgress/WaitingCustomer phải có owner hoặc queue được giám sát; assignment changes có history/version |
| request_type / triage_state | text / text | Unknown/Complaint/Incident/Question/Defect/Change; Pending/Completed | Intake chưa rõ được Unknown/Pending. Completed cần impact/urgency/severity và entitlement áp dụng; không chờ phân loại mới nhận vấn đề khẩn |
| first_response_due_at / next_response_due_at / resolution_due_at | timestamptz | Projection từ SLA engine; NULL nếu không áp dụng | Các clock độc lập, giữ breach history |
| next_customer_update_at / impact / urgency | timestamptz / text / text | Theo incident/promise policy | Nhịp cập nhật và phân loại tác động |
| resolved_at | timestamptz | NULL | Có resolution code |
| parent_ticket_id | uuid | FK Tickets, NULL | Reopen/cùng nguyên nhân |
| sla_policy_version | varchar(30) | NN | Đóng băng chính sách tại tạo |

### 5.9 Bảng Consent_Logs

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| contact_id | uuid | FK Contacts, NN | Chủ thể trong đúng phạm vi |
| purpose_code | varchar(80) | NN | Mục đích cụ thể |
| contact_point_id / source_channel_identity_id / origin_contact_id | uuid | FK Contact_Points/Channel_Identities/Contacts; NULL có semantics rõ | Endpoint cụ thể hoặc contact-wide scope; provenance không mất khi merge |
| channel | varchar(30) | NN | Email/Zalo/SMS/... |
| action | varchar(20) | NN Grant/Revoke/Expire | Log bất biến |
| policy_version | varchar(50) | NN | Thông báo đã trình bày |
| occurred_at | timestamptz | NN | Thời điểm hành động |
| received_at | timestamptz | NN | Thời điểm server nhận |
| evidence_asset_id | uuid | FK Assets, NULL có lý do | Bằng chứng được bảo vệ |
| source | varchar(50) | NN | Form/Portal/AgentVerified |
| idempotency_key | varchar(255) | NN unique tenant | Ngăn ghi lại một event |
| supersedes_id | uuid | FK Consent_Logs, NULL | Chuỗi sửa sai có dấu vết |

### 5.10 Bảng Payments

Payment là giao dịch canonical; evidence nguồn được lưu riêng. Số tiền đã xác thực không biến mất khi chưa match.

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| legal_entity_id / bank_account_id | uuid | FK Legal_Entities/Bank_Accounts, NN | Chủ thể và tài khoản nhận/chi; cùng tenant |
| amount / currency / direction | numeric(18,2) / char(3) / text | amount>0; In/Refund | Số gốc; không phân bổ chéo currency ngầm |
| payer_ref / buyer_account_id / buyer_contact_id | text / uuid / uuid | NULL khi unidentified; FK scoped | Người trả có thể khác người mua, cần case xác minh |
| verification_state / confirmed_at | text / timestamptz | Pending/Confirmed/Rejected; timestamp theo evidence | Xác thực tách matching |
| matching_state | text | Unidentified/Identified/Ambiguous | Không thay verification_state |
| allocation_state / reconciliation_state | text | Projection; Unallocated/Partial/Full và Open/Reconciled/Disputed | Theo allocation ledger/case |
| reference / bank_transaction_ref | text | Theo namespace tài khoản/provider | Candidate dedup, không fingerprint unique toàn cục |
| original_payment_id | uuid | FK Payments NULL cho khoản gốc | Refund/reversal liên kết; partial refund không phủ toàn giao dịch |

Payment_Evidence giữ connector/provider_transaction_id, sao kê dòng nào, verified_by/at, raw ref, payment_id và mapping version. Unique nguồn ở evidence; một Payment nhiều evidence. Kế toán xác nhận canonical match xuyên nguồn, giữ audit khi mơ hồ.

### 5.11 Bảng Payment_Allocations

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| payment_id | uuid | FK Payments, NN | Giao dịch canonical đã xác thực |
| obligation_id | uuid | FK Payment_Obligations, NN | Đích nghĩa vụ/kỳ/dòng order xác định; không rỗng |
| amount / currency | numeric(18,2) / char(3) | >0; khớp payment/nghĩa vụ | Lock tổng hiệu lực không vượt tiền hoặc nghĩa vụ |
| service_net / production_net / media_net / tax_component / other_component | numeric(18,2) | >=0; tổng cấu phần = amount theo rounding policy | Phân rã loại phí và thuế theo nghĩa vụ/version, không tự coi toàn tiền là service |
| eligible_service_net | numeric(18,2) | Projection theo policy, không vượt net của loại dòng đủ điều kiện | Cơ sở commission; không cộng thêm thành cấu phần tiền thứ hai |
| allocation_policy_version | text | NN | Điều khoản/kỳ được duyệt hoặc quyết định Finance |
| entry_type / reverses_id | text / uuid | Allocate/Reverse; FK gốc nếu Reverse | Append-only, không đảo quá phần còn hiệu lực |
| idempotency_key | text | Unique trong tenant/workspace | Replay cùng command một effect |

Invoice_Allocation_Links liên kết allocation với invoice line và mapped amount, có điều chỉnh/đảo/audit. Invoice sync đến sau chỉ bổ sung mapping, không thêm allocation/cash/commission. Bỏ phụ thuộc `invoice_line_id NOT NULL` khỏi allocation; không thay bằng đích tùy ý rỗng. Không phân bổ qua pháp nhân/party/currency/scope nếu chưa có nghiệp vụ chuyển hợp lệ.

Quy ước dấu của Payment_Allocations: amount và các cấu phần lưu trị tuyệt đối không âm; Allocate làm tăng phần đã phân bổ, Reverse làm giảm phần hiệu lực của allocation gốc. Reverse phải giữ cùng currency/pháp nhân và chỉ đảo cấu phần còn hiệu lực; không cộng amount Reverse như receipt mới. Số dư tính từ tổng có dấu theo entry_type, không UPDATE bản gốc.

### 5.12 Bảng Commission_Entries

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| allocation_id / user_id | uuid | FK Payment_Allocations/Users, NN | Gốc cash đủ điều kiện và người hưởng |
| pool_id / policy_snapshot_id | uuid | FK Commission_Pools/Policy_Snapshots, NN | Tách pool, truy được policy version/effective date |
| base_amount / rate / share | numeric | Base>=0; rate/share theo policy | Không gồm phần media/thuế/write-off ngoài base được phép |
| amount / currency / rounding_policy | numeric / char(3) / text | NN | Giá trị bất biến sau posting |
| entry_type / reverses_id / period_id | text / uuid / uuid | Base/Reverse; FK gốc/kỳ | Reversal không vượt phần được đảo; kỳ khóa có adjustment |
| entry_key | text | Unique tenant/workspace/allocation/user/pool/policy/type/operation | Chống replay, hỗ trợ partial reversals khác operation |

Commission_Status_Events lưu Preview/Approved/Earned/Payable/Paid/Reversed theo policy; trạng thái hiện tại là projection, không sửa amount gốc. Payout_Batches/Payout_Links lưu chi thực tế và phần đã trả. Commission_Adjustments cho quality bonus/điều chỉnh có reason/evidence/authority; không dùng quality_factor chưa đo làm tiền chắc được hưởng. Tổng share=1 trong pool và version áp dụng; attribution lịch sử độc lập owner hiện tại.

`Policy_Definitions` là định danh chính sách; `Policy_Versions` là phiên bản cấu hình Draft/Reviewed/Active; `Policy_Snapshots` đóng băng phiên bản và tham số đã duyệt tại sự kiện nghiệp vụ. Snapshot lưu `policy_version_id`, `snapshot_hash`, `effective_at`, `approved_by/at`, basis/rate/rounding/eligibility và scope áp dụng; đã được ledger tham chiếu thì không sửa. Không có bảng song song tên `CommissionPolicies`. Pointer mặc định trên Deal không thay snapshot gắn với line/pool/commission entry. Chưa có policy cho dòng/pool thì giữ `PendingPolicy`, không phát Earned/Payable hoặc tự tính0/full. Migration đổi tên field cũ giữ mapping và không tự chụp policy hiện hành để thay snapshot lịch sử chưa xác định.

Quy ước dấu của Commission_Entries: Base là khoản phát sinh dương; Reverse giữ trị tuyệt đối và làm giảm phần còn hiệu lực của entry được tham chiếu. Commission_Adjustments khai báo direction Credit/Debit và reason; credit tăng quyền hưởng, debit giảm quyền hưởng theo quy chế. Không cộng bút toán đảo vào tổng earned như khoản thưởng mới. Partial payout và reversal giữ số đã trả lịch sử, phần phải xử lý tiếp được thể hiện riêng.

### 5.13 Các bảng mở rộng bắt buộc theo phân hệ

Các bảng dưới dùng trường chung tại 5.1. UUID FK cùng tenant áp dụng cho mọi tên *_id; trường quan hệ không tồn tại chưa được phép tạo bằng JSON tùy ý. Phần mở rộng được triển khai theo priority, không phải tất cả đều bắt buộc trong pilot cá nhân.

| Bảng | Trường chuyên biệt chính | Ràng buộc nghiệp vụ |
| --- | --- | --- |
| Tenants, Branches, Business_Lines | code varchar(50), name varchar(255), status varchar(20) | Code unique trong cha; Branches/Business_Lines FK tenant. |
| Users, Memberships, Role_Bindings | auth_subject varchar(255), role_id uuid, branch_id uuid, valid_until timestamptz | Principal có nhiều binding; không lấy tenant từ request body. |
| Workspaces | workspace_type AGENCY/CLIENT, client_account_id uuid NULL, controller_name text, processing_scope text | Một AGENCY mặc định/tenant; CLIENT gắn account agency qua link có kiểm quyền; có ủy quyền/DPA phù hợp. |
| Contact_Account_Roles | contact_id uuid, account_id uuid, role_code varchar(30), valid_from/to date | Quan hệ nhiều-nhiều; một người có thể đại diện nhiều công ty. |
| Pipelines, Pipeline_Stages | model varchar(8), definition_version int, stage_code text, transition_rules jsonb | Stage phải thuộc pipeline; không đổi trực tiếp instance đang chạy. |
| Queues, Assignments | queue_id uuid, lead_id uuid, owner_id uuid, from_at/to_at timestamptz, reason text | Chỉ một assignment active cho mỗi lead; partial unique index. |
| Quotes, Quote_Lines | deal_id uuid, revision int, status Draft/PendingApproval/Approved/Sent/Accepted/Rejected/Expired/Superseded/Cancelled, expires_at timestamptz, accepted_at timestamptz NULL, cost_total numeric NULL, cost_basis/version, service_id uuid, qty/unit_price numeric, line_type text | Version/bản giá bất biến sau approval; API kiểm expiry/authority/revision tại thời điểm chấp thuận, không chỉ cron. Phản hồi trễ được xét theo evidence thời điểm; Accepted đúng hạn không tự Expired. Net/tax/gross và rounding policy tách. |
| Contracts, SOW_Versions | Contracts.status theo 3.13.5; accepted_quote_id/parent_contract_id uuid NULL, document_type/service_model text, legal_entity_id/signer_contact_id uuid, status, signed_asset_id, revision; effective_from/effective_to date NULL theo lifecycle; notice_value/unit/basis, notice_deadline_at timestamptz NULL, renewal_mode, allocation_policy_snapshot_id | Draft chưa biết ngày được NULL; Active phải đủ điều kiện hiệu lực, evergreen có end NULL. Notice theo điều khoản/kỳ và timezone, có audit khi đổi; không default PASS_THROUGH_FIRST hoặc auto-renew. MSA nhiều SOW/project; settlement riêng. Trạng thái và command theo 3.13.5; không PATCH status tự do. |
| Invoice_Lines | order_id uuid, external_invoice_id text, line_type text, net/tax/gross numeric(18,2), currency char(3) | Chứng từ gốc ERP; lịch sử điều chỉnh riêng; không tự hủy pháp lý. |
| Projects, Deliverables, Acceptances | Projects.status, Deliverables.status theo 3.13.5; contract_id/sow_version_id uuid, handoff_key text, owner_id uuid, planned/committed_due_at timestamptz, asset_version_id uuid, accepted_by uuid, max_revisions/used_revisions int | Unique handoff effect không unique contract; batch sửa/defect khác quota; client-wait intervals; acceptance đúng version/authority. Trạng thái và command theo 3.13.5; không PATCH status tự do. |
| Change_Requests | project_id uuid, scope_delta text, cost_delta numeric, schedule_delta int, status text | Duyệt trước đổi baseline; giữ liên kết phụ lục. |
| Strategy_Briefs | workspace_id uuid, goal text, baseline jsonb, diagnosis text, stp jsonb, proof_refs jsonb, status text, revision int | Gói ngành marketing; approved version đóng băng. |
| Marketing_Plans, IMC_Plans | strategy_id uuid, period daterange, funnel jsonb, message_house jsonb, content_matrix jsonb, measurement jsonb | Schema version kiểm tra JSON; không chạy mã tùy ý. |
| Campaigns | Campaigns.status Draft/Ready/Live/Paused/Completed/Cancelled theoM15; plan_id uuid, objective text, owner_id uuid, start/end timestamptz, status text | Phân biệt agency acquisition và client campaign; gate launch. |
| Budget_Lines, Budget_Adjustments | campaign_id uuid, category text, approved/actual/committed numeric, currency char(3), approval_id uuid | Giảm committed khi actual ghi nhận; lưu adjustment ledger. |
| Tasks và miền Work Management | Task/assignment/participants/submission/review/change request/dependency/recurrence tại 5.20 | project_id nullable theo work_type; scoped FK; lifecycle riêng; không gộp schema Task, Time_Entries và Availability thành một bảng. |
| Time_Entries, Resource_Allocations, Availability | Task/user/period/duration và availability theo lịch, hiệu lực | P1; schema tách ở 5.20; không double count parent/child, không coi missing estimate là 0. |
| KPI_Definitions, KPI_Targets, Metric_Facts | metric_code text, formula_version int, grain text, source text, period date, value numeric, freshness_at timestamptz | Unique metric + dimension hash + period + version; Null khác 0. |
| Touchpoints, Attribution_Credits | contact_id uuid, campaign_id uuid, occurred_at timestamptz, outcome_id uuid, model_version text, credit numeric | Tổng credit mỗi outcome/model ≤1; Unknown nhận phần thiếu. |
| Experiments, Learning_Items | hypothesis text, metric_id uuid, design jsonb, result text, evidence_refs jsonb, applicability text | Không tự chuyển bài học khách A sang B; version và confidence. |
| Journeys, Journey_Instances | definition jsonb, version int, contact_id uuid, current_step text, exit_reason text | Instance giữ version; suppression kiểm lại trước từng action. |
| Loyalty_Ledger, Referrals | contact_id uuid, points numeric, entry_type text, source_payment_id uuid, referrer_id uuid | Không tự giới thiệu; đảo điểm qua ledger, không UPDATE balance tùy ý. |
| Assets, Asset_Versions, Approvals | object_key text, checksum text, mime text, size bigint, status text, approver_id uuid, approved_hash text | Quét malware, gateway/share grant theo6.2, approve đúng checksum/version. |
| Consent_State, Processing_Records | contact_id uuid, purpose text, channel text, legal_basis text, evidence_ref text | Consent_State là projection log; cơ sở khác consent được ghi riêng. |
| Privacy_Requests, Retention_Policies | subject_id uuid, type text, due_at timestamptz, legal_hold bool, retention_days int | Mục đích và cơ sở lưu; xóa cả projection theo quy trình. |
| Outbox, Webhook_Inbox, Connector_Mappings | event_id uuid, connector_id uuid, payload jsonb, status text, retry_count int | Unique event scope; encryption/retention cho payload. |
| Audit_Logs | actor_id uuid, action text, target_id uuid, correlation_id uuid, reason/evidence | Append-only, redact PII; không xóa/sửa để thay correction nghiệp vụ. |
| Finance_Periods | legal_entity_id uuid NN, ledger_kind text NN, period_start/period_end date NN, status Open/Closed, closed_at timestamptz NULL, closed_by uuid NULL, close_watermark text NULL, row_version bigint NN | Kỳ `[period_start,period_end)` theo timezone pháp nhân, end>start; không chồng lấn trong tenant/workspace/legal entity/ledger_kind. `Closed` phải có actor/time và đối soát đóng kỳ. |

### 5.14 Index transaction và ràng buộc

Index trọng tâm: Leads(tenant_id,owner_id,status,sla_due_at), Activities(tenant_id,contact_id,occurred_at DESC), Deals(tenant_id,pipeline_id,stage_id,owner_id), Tickets(tenant_id,status,resolution_due_at), Consent_Logs(tenant_id,contact_id,purpose_code,channel,occurred_at DESC). Index workspace trên bảng xử lý thay khách. Chỉ thêm index sau xem query plan; tránh đánh index mọi custom field.

Phân bổ tiền chạy trong transaction: khóa canonical payment và obligation balance, kiểm tổng hiệu lực, insert allocation/outbox, commit. Consumer commission idempotent theo allocation/pool/policy/operation; không giả exactly-once giữa hệ thống. FK ghép tenant/workspace áp dụng dữ liệu scoped; cross-scope relations được khai báo riêng và kiểm quyền. workspace_id của dữ liệu scoped không NULL. Các thuộc tính optional khác có unique nullable phải dùng NULLS NOT DISTINCT/partial index khi semantics cần, không giả NULL tự chống trùng. Không giữ DB lock khi gọi provider ngoài.

RLS kiểm tenant và phạm vi là lớp bổ sung cho policy ở application. Service DB role không sở hữu bảng, không BYPASSRLS; migration role tách biệt. Với bảng cần ép owner qua policy dùng FORCE ROW LEVEL SECURITY và kiểm thử restore/job theo role thật [S09](#s09). Search, cache, storage key và vector index cũng mang tenant/workspace; RLS trong SQL không tự bảo vệ những kho này.

Mọi lệnh post/adjust/reverse/payout và close-period thuộc cùng sổ phải khóa cùng `Finance_Periods` row trong transaction, kiểm trạng thái sau lấy lock rồi mới ghi ledger/outbox hoặc đóng kỳ. Thứ tự lock thống nhất là kỳ theo khóa scope/ID ổn định → receipt → obligation/allocation → commission/payout aggregate; lệnh nhiều kỳ khóa theo cùng thứ tự. Không giữ lock khi gọi provider. `close-period` chỉ commit khi các đối soát bắt buộc và financial events tới `close_watermark` đã xử lý hoặc được lập danh sách ngoại lệ có thẩm quyền; không đóng dựa vào read model có thể trễ.

Nếu còn event bắt buộc chưa xử lý, close trả Pending/409 kèm công việc cần giải quyết và kết thúc transaction/nhả khóa; không giữ period lock để đợi consumer cũng cần khóa đó. Thử đóng lại bằng command có idempotency/version sau khi các prerequisite hoàn tất.

Ledger post có `period_id`, `posting_date` theo timezone kỳ và `source_occurred_at/received_at` riêng; `posting_date` phải trong kỳ đã chọn và kỳ còn Open tại commit theo lock contract. Sự kiện đến muộn/refund sau khóa ghi adjustment ở kỳ mở được Finance chọn, giữ link entry/kỳ/sự kiện gốc; không đổi ngày sự kiện hoặc tự mở lại kỳ đóng. Period selection không được dùng ngày nhận webhook để viết đè lịch sử kinh tế. Bảng ERP sở hữu thì mapping và quyền đóng kỳ theo ERP; CRM không tạo bản kỳ đối lập.

### 5.15 Migration và lifecycle dữ liệu

Import qua staging, validate, dry-run và báo cáo lỗi trước commit. Giữ source_record_id để chạy lại; không nhập consent bằng default true. Backup mapping/source snapshot có hạn lưu. Export migration phải có metadata về schema và encoding UTF-8, mã hóa khi chuyển.

Áp dụng expand → migrate → contract cho schema: thêm trường tương thích, backfill có checkpoint, kiểm số lượng/checksum, đổi ứng dụng, sau đó mới bỏ trường cũ qua release được duyệt. Không rollback dữ liệu tài chính bằng DROP TABLE. Tài liệu này định nghĩa schema nghiệp vụ; khi phát triển phải xuất DDL/OpenAPI versioned và contract tests tương ứng.

### 5.16 Schema Omnichannel bổ sung

Các bảng dưới bổ sung cho schema Chương 5. UUID là khóa nội bộ; external IDs luôn là text để không mất số 0 đầu hoặc vượt miền số. Mọi bảng có `id uuid PK`, `tenant_id uuid NOT NULL`, `workspace_id uuid NOT NULL`, `created_at timestamptz NOT NULL`. Bảng thay đổi trạng thái có `updated_at`, `row_version bigint`. FK gồm tenant/workspace với khóa đích tương ứng để chặn liên kết chéo phạm vi; không chỉ dựa bộ lọc UI. Tên bảng trong đặc tả được ánh xạ snake_case trong migration.

| Bảng | Trường nghiệp vụ và kiểu | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| Channel_Connections | provider varchar(40); provider_namespace text NN; external_account_id text; secret_ref text; capabilities jsonb; scopes jsonb; status varchar(30); api_version text; expires_at timestamptz NULL; last_sync_at timestamptz NULL | Connection giữ một owner workspace bất biến khi active. Trong một tenant, tại một thời điểm chỉ một connection ở trạng thái active/degraded/reauthorization_required sở hữu `(provider, provider_namespace, external_account_id)`; `provider_namespace` gồm app/region hoặc phần namespace provider thực sự dùng. Cưỡng chế bằng key/registry unique và transaction khi activate/reconnect; không chỉ unique theo workspace. Nhiều Inbox nội bộ được dùng chung một connection. Muốn chuyển chủ phải pause ingest/send, kiểm ủy quyền/account, chốt cursor và pending intents, revoke grant cũ rồi chuyển có audit/migration; không tự chép lịch sử sang khách mới. Multiplexing nhiều workspace chỉ mở khi có routing/publish policy riêng đã kiểm isolation; mặc định không hỗ trợ. Secret giữ trong vault; capability có checked_at/evidence. |
| Channel_Identities | connection_id uuid FK; provider_subject_id text; contact_id uuid FK NULL; verification_status varchar(30); evidence_ref uuid NULL; verified_at timestamptz NULL | Unique tenant/workspace/connection/provider_subject_id; NULL contact trong quarantine/provisional; không unique tên hoặc ảnh |
| Inboxes | name text; connection_id uuid FK; branch_id uuid FK NULL; team_id uuid FK; routing_policy_id uuid FK; status varchar(20) | Một connection có thể nhiều hàng đợi nội bộ; inbound resolver xác định một inbox đích, tránh fanout tạo trùng |
| Conversations | inbox_id uuid FK; connection_id uuid FK; channel_identity_id uuid FK; provider_thread_id text NULL; status open/resolved/closed; waiting_party agent/customer/internal/none; assignee_id uuid FK NULL; team_id uuid FK; opened_at timestamptz; last_message_at/last_inbound_at timestamptz NULL; last_qualifying_interaction_at timestamptz NULL; qualifying_event_id/type; messaging_policy_version; eligibility_projection jsonb; source_mode varchar(20) | Partial unique connection + provider_thread_id khi có thread bền vững; nếu provider không có, lưu session rule/version; source_mode live/backfill/manual |
| Conversation_Participants | conversation_id uuid FK; participant_key text; channel_identity_id uuid FK NULL; role varchar(20); visible_to_customer boolean | Unique conversation/participant_key/role; email To/CC/BCC và agent tách vai trò; không render BCC ra ngoài |
| Messages | conversation_id uuid FK; connection_id uuid FK; provider_message_id text NULL; client_request_id uuid NULL; direction varchar(12); visibility varchar(12); content_type varchar(40); body_ref text NULL; occurred_at timestamptz; received_at timestamptz; delivery_status varchar(25); deleted_at timestamptz NULL | Partial unique connection/provider_message_id; partial unique workspace/client_request_id; private note không có outbound; body mã hóa/ACL; không dùng text content làm dedup key |
| Message_Attachments | message_id uuid FK; object_key text; mime_type text; size_bytes bigint; sha256 char(64); scan_status varchar(20); expires_at timestamptz NULL | size>=0; MIME/size/scan policy; chỉ clean mới tải/forward. Tệp cần quyền hiện thời qua download gateway theo6.2; asset publish theo share grant; không expose raw storage presigned URL. |
| Message_Status_Events | message_id uuid FK; connection_id uuid FK; provider_event_id text; status varchar(30); occurred_at timestamptz; received_at timestamptz; detail jsonb | Append-only; unique connection/event/type; reducer theo transition của provider, không ghi đè trạng thái bằng thứ tự nhận đơn thuần |
| Inbound_Events | connection_id uuid FK; event_key text; event_type text; payload_ref text; occurred_at timestamptz NULL; received_at timestamptz; processing_status varchar(20); attempts int; error_code text NULL | Unique connection/event_key; provider ID ưu tiên; fallback key có version và giữ raw reference; payload retention ngắn có cấu hình |
| Outbound_Intents | message_id uuid FK; idempotency_key uuid; policy_snapshot jsonb; status varchar(25); next_attempt_at timestamptz NULL; expires_at timestamptz; attempt_count int | Unique workspace/idempotency_key; policy_snapshot không thay thế recheck khi gửi; unknown_outcome cần reconcile |
| Send_Attempts | outbound_intent_id uuid FK; attempt_no int; request_ref text; provider_response_ref text NULL; started_at timestamptz; completed_at timestamptz NULL; outcome varchar(25) | Unique intent/attempt_no; log đã bỏ token/PII; không giả định network timeout là rejected |
| Conversation_Assignments | conversation_id uuid FK; assignee_id uuid FK NULL; team_id uuid FK; assigned_at timestamptz; released_at timestamptz NULL; reason text; actor_id uuid FK NULL | Partial unique conversation khi released_at NULL; giữ history chuyển ca; concurrency qua transaction |
| SLA_Episodes | business_subject_id uuid FK NN; waiting_episode_key text; start_event_id/completion_event_id uuid; policy/calendar_version text; clock_type text; time_basis BusinessCalendar/WallClock; remaining_business_seconds bigint NULL; owner_at_breach_id uuid NULL; started_at/due_at timestamptz; stopped_at/breach_at timestamptz NULL; pause_intervals jsonb; exception_ref uuid NULL; outcome text | Subject typed và FK thật; claim/attempt/FRT/NRT/resolution/promised_update độc lập; một clock nguồn chuẩn, deadline Lead/Ticket projection; chuyển nhóm không reset |
| Sync_Checkpoints | connection_id uuid FK; stream_key text; cursor_encrypted text NULL; coverage_from timestamptz NULL; coverage_to timestamptz NULL; last_success_at timestamptz NULL; gap_reason text NULL | Unique connection/stream_key; advance cursor sau xử lý bền vững toàn page; coverage không giả lập từ thời điểm cài app |
| Identity_Merge_Journal | survivor_id uuid FK; merged_contact_id uuid FK; evidence_ref uuid; before_refs jsonb; actor_id uuid FK; approved_at timestamptz; undone_at timestamptz NULL | Lưu quan hệ trước merge và operation ID; quyền riêng; không lưu vô hạn PII chỉ để hỗ trợ undo |

FK `Messages.connection_id` phải khớp connection của Inbox/Conversation; cưỡng chế bằng composite references hoặc invariant được kiểm thử trong transaction. Khóa unique cho message cần theo namespace thực của provider; nếu provider chỉ đảm bảo ID trong thread thì thêm provider_thread_id vào khóa. Một identity nhiều conversation; một conversation nhiều participant; một Contact nhiều identity. Account không đồng nghĩa Contact, Inbox không đồng nghĩa Channel Connection.

Index tối thiểu: `(tenant_id, workspace_id, assignee_id, status, last_message_at DESC)` trên Conversations; `(conversation_id, occurred_at, id)` trên Messages; pending intents theo next_attempt_at; inbound pending theo received_at. Search index dùng document ACL và xóa đồng bộ; PostgreSQL full-text là điểm xuất phát, chưa cần Elasticsearch khi chưa đo tải. Tệp và raw payload không nhét toàn bộ vào event JSON; chỉ lưu object reference có retention và access check.

SLA_Episodes có logical unique key `(tenant_id,workspace_id,business_subject_id,waiting_episode_key,clock_type)`. Episode key dựa canonical request/unanswered turn/lifecycle event theo policy, không theo worker attempt hoặc received_at. Reopen hợp lệ có episode key mới liên kết `prior_episode_id`, carryover/breach history theo policy. Duplicate/reassignment không đổi key; nhiều clock khác type được tồn tại, hai FRT cùng episode thì không. Constraint/index vật lý hoặc invariant native tương đương phải được kiểm dưới concurrency trước bật.

### 5.17 Hợp đồng API nội bộ và giao dịch mẫu

| Endpoint đề xuất | Kiểm tra bắt buộc | Kết quả/lỗi |
| --- | --- | --- |
| POST /v1/conversations/{id}/messages | RBAC + workspace + recipient + capability + send policy; Idempotency-Key | 202 queued với intent_id; replay cùng key/body trả cùng intent; khác body trả 409 |
| POST /v1/conversations/{id}/claim | Team membership, capacity, expected row_version | 200 nhận thành công; 409 đã được người khác nhận |
| POST /v1/identity-merge-reviews | Cùng phạm vi, evidence, review permission | 201 review pending; không tự merge chỉ vì API được gọi |
| POST /v1/connections/{id}/replay | Operator role, event range, dry-run preview, reason | Job ID; từng event qua dedup, không bypass quyền/consent |
| GET /v1/contacts/{id}/timeline | Contact access và từng conversation/message access | Cursor pagination; không leak counts/snippet của thread bị cấm |

Ví dụ transaction inbound: insert event guard → upsert identity theo scoped key → insert message theo provider key → update conversation summary → insert domain outbox → mark processed → commit. Nếu unique conflict, đọc bản ghi hiện hữu và xử lý phần status mới nếu đó là event khác; không nuốt tất cả exception như “trùng”. Job retry sau crash phải cho kết quả nhất quán. Giao dịch gọi provider nằm ngoài DB transaction để không giữ lock trong khi chờ mạng.

API `POST /v1/conversations/{id}/messages` nhận `response_targets[]` khi phản hồi một nghĩa vụ. Server kiểm quyền từng subject, quan hệ với thread, recipient, episode/version hiện hành và trạng thái assignment. Client không được tự đặt clock completed. Worker lưu evidence khi đạt completion criterion của policy; reducer chỉ hoàn thành clock thuộc response targets hợp lệ. Reply chưa phân loại vẫn gửi được khi đủ quyền/policy nhưng không tự dừng tất cả SLA; đưa vào queue làm rõ nếu còn nghĩa vụ chưa xác định. Autoack/private note/unknown_outcome không hoàn thành human clock. Một phản hồi thực chất có thể đáp nhiều yêu cầu; không ép mỗi message chỉ thuộc một request.

Inbound chưa rõ request được lưu và có intake clock theo policy, rồi người phụ trách phân loại. Lúc phân loại không reset thời gian khách chờ; lưu nguồn và ánh xạ episode, không tự tạo mọi clock trên tất cả resource của Contact. Completion criterion nêu accepted/delivered hoặc evidence khác theo capability, khác xác nhận khách đã đọc.

### 5.18 Dữ liệu bổ sung cho liên kết nghiệp vụ 1.3

Các bảng logic có thể ánh xạ capability của nền tảng được chọn; không bắt tạo mọi bảng độc lập. Khi triển khai phải có schema/FK/version thật, không generic JSON để né isolation. Bảng ở P1/P2 chỉ tạo khi module mở.

| Miền / đối tượng | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Legal_Entities, Bank_Accounts | legal name/tax identity, currency, account ref, authority | Pháp nhân ký/nhận tiền; mặc định một khi pilot; secret không ở field thường |
| Contact_Points, Identity_Links | contact_id, loại/endpoint encrypted+lookup hash, verified/status/effective dates, origin refs | Endpoint vs người tách; hotline/shared không unique toàn cục; provenance sau merge |
| Lead_Transitions, Deal_Stage_History | entity_id, from/to, occurred/received, policy, actor, reason/evidence, hold interval | MQL/SAL/SQL/handover history; không sửa cohort/aging bằng ghi đè |
| Entity_Team_Grants | contact/account/deal/project/ticket FK typed, user/team, role, field/actions, from/until | Mỗi grant đúng một resource; deny-wins theo policy; B2C không cần Account Có grantor_id, authority/approval_ref, reason, created/revoked_at; kiểm grant authority riêng, không dùng quyền U resource để tự cấp quyền. |
| Order_Lines | order_id, line_type, approved revision, net/tax/gross, currency, service period | Phiên bản loại phí/cost; khác Invoice_Lines gốc ERP |
| Payment_Schedules, Payment_Obligations | order_line_id, schedule_id, due_at, net/tax/gross/currency, policy, remaining projection | Mỗi obligation chỉ thuộc một dòng order/kỳ; tổng nghĩa vụ theo bản hợp đồng còn hiệu lực |
| Payment_Evidence, Reconciliation_Cases | payment_id NULL khi unresolved, connector/event ID, raw ref, verification, proposed match, owner/due/resolution | Một receipt nhiều evidence; cùng source unique; không tự dedup theo amount/text |
| Invoice_Allocation_Links | allocation_id, invoice_line_id, mapped amount, entry_type/reversal, actor/evidence | Mapping không ghi receipt/commission lần nữa; tổng mapping không vượt phần tương ứng |
| Commission_Pools, Policy_Snapshots, Commission_Status_Events, Payout_Batches/Links, Commission_Adjustments | pool/version/effective rules, status evidence, amount paid, adjustment reason | Share/payout số dư đúng; freeze policy; không UPDATE tiền gốc |
| Business_Subjects | lead_id/deal_id/ticket_id/conversation_id/project_id/deliverable_id uuid NULL, subject_type enum | CHECK num_nonnulls(sáu FK)=1 VÀ type khớp FK; mỗi FK unique scoped; subject kế thừa scope target. Không tự tạo SLA cho mọi type; clock chỉ theo policy đã bật. |
| Conversation_Subject_Links | conversation_id, business_subject_id, purpose, actor/evidence/effective dates | N:M qua FK thật; đúng scope hoặc bridge cross-workspace được cấp phép. Đọc link không mở toàn hồ sơ đích; các clock còn lại không đóng theo một thread. |
| Entitlement_Snapshots, Customer_Promises | contract/SOW/version, support calendar/rules, authority; subject/promise owner/due/source | Tại thời điểm áp dụng; hết quota không chặn complaint intake; update promise có lịch sử |
| Success_Plans, Feedback, Recovery_Cases, Corrective_Actions | project/account/role, baseline/target/first-value, score/question version, recovery owner/due/remedy/evidence | Verify khác no-contact; giữ score gốc; theme cải tiến không chia sẻ data trái workspace |
| Client_Wait_Intervals, Revision_Batches | deliverable/version, requested/answered_at, reason, feedback_batch, defect/change | Không cộng trùng interval; không tự dời contractual date; lỗi khác quota đổi ý |
| Media_Funding_Authorizations | contract/line/budget, funding receipt/credit policy, cap/expires, committed/actual/freshness | Phép chi riêng kickoff; không dùng tiền khách khác; thiếu spend data ghi degraded |
| Outcome_Events, Platform_Export_Intents | demand/deal/outcome ID/version/value basis, source IDs, dataset binding, purpose/policy, receipt | Closed-loop P1; scope mismatch chặn; refund/correction theo provider capability |

| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Appointments | type/title, subject link, owner/participants, start_at/end_at timestamptz NN, timezone, status Tentative/Confirmed/Cancelled/Completed/NoShow | end>start, finite và non-NULL; reschedule version hủy reminder cũ; GPS/evidence check-in chỉ khi feature phù hợp được bật |
| Resources, Resource_Bookings | tenant resource_id, appointment_id, capacity model, start/end, status Hold/Confirmed/Released/Expired, hold_expires_at, row_version | Resource độc quyền dùng range[start,end) non-overlap cho active status; resource chia sẻ nhiều workspace vẫn giữ identity chung. Hold hết TTL được release dưới lock, confirm kiểm lại; pool capacity>1 cần model riêng |
| Workspace_Account_Links, Contract_Workspace_Grants | source/target workspace, buyer/billing account, contract/project, relation type, validity, authority/evidence | Bridge tenant-consistent theo loại quan hệ, kiểm khi đổi đích; không đồng nghĩa broad data grant |
| Brands, Business_Units | display_name, billing_account_id, customer reference, effective dates | Tùy chọn P1 theo nghiệp vụ; giữ pháp nhân thanh toán canonical. Deal/Project có brand reference khi cần |
| Obligation_Adjustments | obligation_id, direction Debit/Credit, type/reason, amount>0, currency, policy/approval/evidence/ERP ref, reversal | Append-only; net obligation = gross + debit − credit; adjustment không tạo cash/commission. Credit vượt phần còn phải thu đi xử lý credit/refund đúng nguồn, không chặn bằng công thức gross đơn giản |
| Refund_Reservations | original_payment_id NN, operation_id/item_key NN, allocation_id NULL khi hoàn dư, amount>0, currency, component snapshot, beneficiary/evidence, request_hash, state Reserved/Dispatching/Unknown/Confirmed/Released/Rejected, expires/reconcile_at | Unique tenant/workspace/receipt/operation/item; allocated reservation giữ phần allocation chưa được reserve, unallocated reservation giữ available cash. Chuyển Confirmed cùng ghi Refund/reversal áp dụng, không double-subtract. Unknown quá hạn không tự nhả. |
| Policy_Definitions, Policy_Versions | typed config/scope/unit/owner/source/version/effective_at, Draft/Reviewed/Active, precedence/validation | Có thể là config platform thay bảng riêng; seed HTML chỉ Draft. Policy không có người sở hữu không tự bật |

| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Message_Subject_Links | message_id, business_subject_id; link_role request_source/response_to/context; waiting_episode_key hoặc sla_episode_id/clock_type khi response_to; actor/source/evidence | FK/scope hợp lệ; message có thể đáp nhiều request được xác nhận. Internal note chỉ context, không hoàn thành human-response clock. Có thể ánh xạ quan hệ native, không bắt thêm một bảng vật lý riêng. |

| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Email_Delivery_Events, Endpoint_Suppressions | connection/message/contact_point refs; provider event ID; event_type; reason; purpose/sender scope; occurred/received; source/evidence; effective/released_at | Event append-only và idempotent; suppression current-state có provenance; từ chối khác hard-bounce khác consent; cập nhật atomically trước dispatch tiếp. |

Projection last_inbound/qualifying interaction lấy occurred_at/evidence hợp lệ theo reducer, không lấy reply outbound hoặc thời gian backfill để gia hạn cửa sổ. Eligibility khác phí/quota; provider/message class/permission/policy version quyết định tại dispatch. Chữ ký webhook không bắt mọi Channel_Identity có Contact: trạng thái kỹ thuật/anonymous/quarantine giữ NULL; promote Lead/Ticket/Consent mới tạo/link Contact tạm trong transaction theo đường intake.

`Inbound_Events` là canonical durable inbox cho kênh; `Webhook_Inbox` ở 5.13 là tên năng lực chung, ánh xạ cùng ingestion registry thay vì tạo hai consumer nhận cùng payload. Outbox vẫn là hướng phát sự kiện. Consent_State chỉ projection; permission/suppression kiểm tại dispatch. FK start/completion event và provenance phải trỏ canonical event registry hoặc source typed được kiểm transaction khi xuất DDL.

### 5.19 Gate triển khai vật lý và dependency closure

Không có quota bảng P0 mặc định. Mỗi capability ánh xạ bảng/field/API/provider do CRM/ERP/PMS/connector sở hữu, dependency, nguồn ghi, feature flag, migration, test và owner. Các bảng logic có thể ánh xạ đối tượng của nền tảng; không đếm tên bảng thành effort hoặc cam kết90ngày.

| Lát cắt | Bắt buộc trước bật | Có thể hoãn/tích hợp | Điều kiện mở |
| --- | --- | --- | --- |
| Nền/quyền/hồ sơ | Scope, principal/grant, contact/demand, audit, purpose/retention/suppression, source IDs | Bộ máy pack/metadata lớn, tự động hóa privacy chưa cần có bảng riêng | Không leak và thực hiện quy trình dữ liệu được; controls áp từ ngày đầu |
| Sales→contract→cash | Pipeline, activity, quote/SOW/version, contract/obligation, evidence/allocation/adjustment/period nếu tự ghi tiền | API ERP; commission nếu chưa có chính sách; PMS chi tiết | Tiền/quyền/history/reconcile đúng; field bắt buộc có mapping hoặc feature không bật |
| Một inbox/kênh | Identity/thread, durable event/outbox, send policy/attempt, assignments/SLA và health tối thiểu | Kênh thứhai, five-channel feature parity, survey engine | Quyền tài khoản/capability và recovery đã test |
| Delivery/CX | Handoff, deliverable/acceptance, issue/recovery/promises, lịch nếu thực dùng | Timesheet/editor strategy/scorecard, resource reservations nếu chưa quản ekip | SOW và request liên kết đúng, không quên cam kết |
| Mở rộng | Dependency closure và ngân sách vận hành của feature | Loyalty, MTA, AI tự hành theo business case | DDL/API + migration + UAT tương ứng, không chỉ thêm bảng |

Invoice mapping chỉ bắt buộc khi theo dõi chứng từ; chọn manual mapping hoặc ERP connector tương ứng. Commission payout/adjustment cần trước khi chi thật, không được gắn P1 rồi cho P0 payout thiếu lịch sử. Processing/retention có thể cấu hình/registry bên ngoài nhưng trách nhiệm không được hoãn. Nullable feature reference hoặc cột chưa tạo chỉ hợp lệ khi API/feature flag không yêu cầu nó và migration đã kiểm.

### 5.20 Schema và API Work Management — FR25

**Project scope:** Projects có project_type CLIENT_DELIVERY/INTERNAL. Contract/SOW/handoff bắt buộc có điều kiện với CLIENT_DELIVERY theo M08; INTERNAL cho NULL và cần sponsor/team/owner/start authorization nội bộ. Trạng thái Project ở 3.13.5 dùng chung nhưng guard hợp đồng/tiền chỉ áp client delivery theo cam kết, không áp internal project. Personal/internal/CRM task standalone cho project_id NULL. Điều này cũng áp cho bảng tổng hợp 5.13 và ERD Chương 5.

#### Entity đề xuất

| Entity | Nội dung và invariant |
| --- | --- |
| Tasks | tenant/workspace, type, title, requester, project nullable, lifecycle, stage, priority, due/current/baseline, row_version; FK scope đầy đủ |
| Task_Assignments | task/user/queue, offered/accepted/released, reason, effective dates; một active assignment; assignee/queue XOR |
| Task_Participants | user + role + grant source/effective dates; unique active task/user/role; watcher không ngầm có quyền sửa |
| Task_Links | task → typed resource registry có FK thật; relation source/context/fulfills; không dùng text object_type/id không kiểm tồn tại |
| Task_Dependencies | predecessor/successor/type/waiver; unique edge; cấm self/cycle với concurrent writes |
| Task_Checklist_Items | text, required, completed_by/at, version; không tự thành task có lịch độc lập |
| Task_Submissions / Reviews | result version/hash/evidence, reviewer, decision/reason; append history, không ghi đè submission đã review |
| Task_Change_Requests | due/owner/scope change, before/after, requester, approver, status, source version |
| Task_Blockers | type/reason/owner, opened/closed/review_at, external/internal, valid waiver |
| Task_Comments / Assets | actor, visibility, safe content, asset ref, revisions, mentions; access kiểm hiện thời |
| Task_Templates / Versions | immutable active version, role placeholders, checklist, defaults; resolved context khi instantiate |
| Recurrence_Rules / Occurrences | mode, timezone, schedule, version, nominal occurrence, task_id; unique(rule,version,nominal_key) |
| Time_Entries / Allocations | task/user, duration, date/period, remaining estimate, approval; đơn vị phút; không gộp với user availability |
| Task_Events / Outbox | event type, aggregate version, actor/reason, trace, payload đã tối thiểu hóa; notification sau commit |
| External_Task_Mappings | source/external_id/version/last_synced; field authority; sync operation status; unique source ID đúng scope |

Index: `(workspace,assignee,lifecycle,due_at,id)`, `(workspace,team,lifecycle,due_at,id)`, `(project,parent_task_id)`, pending offers/reviews theo due; indexes trên dependency endpoints và occurrences. Tất cả schema là logical design; DDL cần DB/vendor được chọn và migration review, không coi bảng này là đã chạy migration.

Graph concurrency: serialize thay đổi dependency theo graph scope hoặc serializable transaction có retry; chỉ chạy DFS trước INSERT mà không khóa không đủ chặn cycle đồng thời. Kiểm cả hierarchy và dependency semantics của subtree. Mặc định không cho dependency giữa ancestor và descendant để tránh self-deadlock hoàn thành.

#### API contract đề xuất

| Endpoint | Guard | Kết quả |
| --- | --- | --- |
| POST /v1/tasks | Permission, scoped context, Idempotency-Key | 201; replay key/body trả cùng task, khác body 409 |
| POST /v1/tasks/{id}/claim hoặc /accept | Active offer/queue grant, expected_version | 200 hoặc 409; chỉ một owner |
| POST /v1/tasks/{id}/decline | Offer đúng người, reason | Queue fallback + audit; không cancel task |
| POST /v1/tasks/{id}/change-requests | Proposed diff, reason, version | 201 pending; due/owner chưa đổi |
| POST /v1/task-change-requests/{id}/decisions | Authority, request/task version | 200 approved/rejected hoặc 409 |
| POST /v1/tasks/{id}/submissions | Evidence, children, blocker, policy | 201; InReview/Done theo policy |
| POST /v1/submissions/{id}/reviews | Reviewer, exact submission version | Decision idempotent; stale 409 |
| POST /v1/tasks/{id}/dependencies | Scope + graph atomic validation | 201 hoặc 422 cycle/invalid |
| POST /v1/tasks/{id}/reopen hoặc /cancel | Authority + impact preview + reason | 200; không xóa history |
| GET /v1/work/my hoặc /team/{id} | Filter/scope/ACL, cursor | 200 projection; không leak counts |

Mutation chặn 403 nếu thiếu quyền; 409 khi state/version conflict; 422 khi dữ liệu/nghiệp vụ không hợp lệ. Job lớn trả 202 + job_id và kết quả từng item. HTTP success của gửi yêu cầu sync không đồng nghĩa PMS đã áp dụng.

**Quyết định vật lý:** PostgreSQL theo 5.1 là DB thiết kế ban đầu; 5.20 là hợp đồng logical để lập migration, chưa là DDL đã chạy. Tất cả bảng có id UUID, tenant_id/workspace_id, created_at và scoped FK theo 5.1; bảng mutable có row_version. Assignment history là nguồn; assignee/queue hiện tại trên Tasks nếu có chỉ là projection được cập nhật trong cùng transaction. Draft có thể chưa có active assignment; việc OPEN phải có assignee hoặc queue chịu trách nhiệm.

**Migration:** kiểm kê task/next action/reminder cũ và task bên PMS; map source_id→task_id có unique key, dry-run count/status/owner/due/ACL; giữ original_created_at và nguồn; không replay notification/recurrence lịch sử. Freeze nguồn cũ khi cutover, đối soát delta, checkpoint và orphan tasks; rollback app không được xóa tác vụ mới, cần reconcile trước trả nguồn ghi cũ. Việc CRM chưa đủ dữ liệu giữ queue làm rõ, không tạo hợp đồng giả.

<a id="chuong-6"></a>

## CHƯƠNG 6 PHÂN QUYỀN BẢO MẬT VÀ TUÂN THỦ PHÁP LÝ

### 6.1 Mô hình quyền

RBAC quyết định hành động, ABAC quyết định phạm vi tenant/branch/team/owner/client workspace và mức nhạy cảm. Quyền Deny thắng Allow khi xung đột. C/R/U/D là tạo/đọc/sửa/archive; xóa vĩnh viễn chỉ qua privacy workflow. X/I là export/import. Quyền phê duyệt là quyền riêng theo loại chứng từ/hạn mức, không suy ra từ U.

CMO không mặc nhiên là quản trị hệ thống hoặc được xem lương; Admin không mặc nhiên được đọc hợp đồng/ghi âm. CEO xem báo cáo toàn tổ chức nhưng không thay người hạch toán để chỉnh khoản thu. Ở chế độ cá nhân có thể kiêm vai nhưng giữ audit và chuyển sang phân tách khi đủ nhân sự.

| Vai trò | Phạm vi | CRM C/R/U/D | Export / Import |
| --- | --- | --- | --- |
| Chủ dự án/CEO | Toàn tenant; nhạy cảm theo nhu cầu | R; C/U qua vai nghiệp vụ; D qua stewardship | X có phê duyệt, watermark và log; I chỉ khi được gán steward |
| Giám đốc kinh doanh | Sales toàn tenant hoặc chi nhánh phụ trách | C/R/U lead/deal; D yêu cầu steward | X tổng hợp; X PII có duyệt; I staging |
| Trưởng nhóm Sales | Nhóm/chi nhánh được giao | C/R/U; reassign trong nhóm; không hard delete | X PII mặc định không; I staging khi cấp |
| Sales | Owner và grant còn hiệu lực | C/R/U Lead/Deal/Quote/Activity được giao; R payment state/obligation và Ticket summary cần thiết; R commission bản thân; không raw finance/PII ngoài nhiệm vụ | Không X danh sách; I hàng loạt chỉ khi có quyền riêng |
| CMO/Marketing Manager | Campaign/audience được giao | C/R/U campaign; đọc contact đã mask, không sửa ledger | X aggregate; activation qua connector có policy; I staging |
| Marketing thực thi | Task/asset/campaign tham gia | C/R/U task/asset; R hồ sơ tối thiểu | Không X PII; I asset theo quyền |
| AM/CSKH | Account/Contact/Project/contract grant đúng nhiệm vụ | C/R/U onboarding/success plan/ticket/recovery; tạo/sửa renewal/upsell Deal/Quote khi có commercial permission; R SOW/acceptance và công nợ summary liên quan; approve/refund quyền riêng | X tài liệu publish đúng khách, không X customer list |
| Delivery | Project/deliverable/campaign được phân | C/R/U task/asset/deliverable phù hợp giai đoạn; R brief/SOW/plan; acceptance theo authority, không đọc commission/finance nội bộ mặc định | Không X PII; nhập asset/evidence theo quyền dự án |
| Kế toán | Tenant/legal entity và hồ sơ tài chính được gán | R approved quote/contract/SOW/acceptance/billing identity tối thiểu. Commands post/allocate/reconcile/propose-adjust/reverse/close-period theo quyền và hạn mức riêng; không UPDATE/DELETE tiền gốc/khóa kỳ tùy ý hoặc sửa commercial Lead/Deal | X sổ đối soát được duyệt, I sao kê có mapping và dedup; duyệt ngoại lệ tách người theo quy chế |
| Data steward/Privacy owner | Phạm vi yêu cầu dữ liệu | Merge/archive/xóa theo workflow; R tối thiểu cần thiết | X/I cho tác vụ có duyệt và thời hạn |
| Admin kỹ thuật | Cấu hình/connector/health | Không C/R/U/D dữ liệu nghiệp vụ mặc định | Không X/I nghiệp vụ; break-glass có TTL và log |
| Khách qua portal | Chính client workspace và project được mời | R tài liệu publish; C feedback; approve đúng vai | Download asset đã chia sẻ, không export hệ thống |

Account/Contact/Deal/Project grants được kiểm cùng role và độ nhạy cảm; chia sẻ Account không tự cho đọc tài chính agency hay toàn CLIENT workspace. Policy Deny-wins phải được test trên nền tảng thật (EspoCRM có semantics gộp quyền rộng hơn theo tài liệu tham khảo). Kiểm quyền object/action/field ở API, search/count/snippet, file, export, BI và AI; cache/index có permission version và revoke propagation. Job kiểm authority hiện tại khi thực thi, không chỉ lúc enqueue. RLS role thật không owner/BYPASSRLS, tenant context reset/transaction-scoped khi dùng pool. MFA và quản lý phiên theo rủi ro; break-glass có mục đích/TTL/audit.

Activity/timeline kiểm quyền trên chính activity và các resource restrictions áp dụng (account/deal/project/branch), bên cạnh quyền Contact. Không suy Contact access=mọi lịch sử; không dùng OR branch để vượt account deny. Activity B2C/field NULL/internal note có policy riêng, không hard-code AND mọi cột. Counts/snippet/file/AI tuân cùng quyền.

Với pool PostgreSQL: bắt đầu explicit transaction, bind context từ identity/server-side mapping qua SET LOCAL hoặc parameterized set_config(...,true), rồi mới chạy query scoped; missing/invalid context fail closed. Không dùng session-level context cho request dùng chung pool; bảo đảm không có stale session baseline và scoped query ngoài transaction. App role không owner/BYPASSRLS; SQL injection hoặc quyền đổi context tùy ý vẫn phải phòng, SET LOCAL không tự xác thực người dùng. Các job/cursor/retry có cùng contract và test hai tenant liên tiếp trên một connection.

> **Thẩm quyền cấp quyền:** Quản lý users/teams/role bindings, resource grants, field policies và break-glass là các action riêng, không suy từ quyền cấu hình connector hoặc sửa bản ghi. Mỗi grant/policy change lưu grantor, authority/approval, resource/actions/fields, thời hạn và reason; server kiểm quyền cấp trên đúng scope. Người cấp không được tự cấp thêm quyền nhạy cảm hoặc ủy quyền vượt authority đã được phê duyệt; membership update không là đường vòng. Khi có đội ngũ, thay quyền tenant-wide, tài chính, privacy/export và break-glass cho chính mình cần người có thẩm quyền khác duyệt; chế độ cá nhân được khai báo rõ, owner chấp nhận kiêm nhiệm và giữ audit, không giả có separation of duties. Revoke/cấp mới cập nhật permission version và consumer theo contract hiện có. Technical Admin chỉ triển khai policy đã duyệt, không mặc nhiên được tự cấp business access. Dữ liệu support khi cần dùng grant TTL đúng phạm vi.

### 6.2 Bảo vệ dữ liệu và chống thất thoát

MFA cho quản lý, Admin, kế toán; session timeout cấu hình, revoke khi nghỉ việc. Mã hóa đường truyền, mã hóa storage/backup, bảo vệ khóa trong secret manager. Tệp upload kiểm MIME thật, kích thước, malware; tệp cần quyền hiện thời tải qua gateway theo hợp đồng dưới đây. Không public bucket; tên file không là biện pháp bảo mật.

Export thực thi ở backend, giới hạn dòng và purpose; yêu cầu người duyệt khác với người yêu cầu khi có đội ngũ. Gắn user/time/request_id vào tệp, log phạm vi và số dòng, hết hạn link. Che dữ liệu trong preview, autocomplete, notification và log. Không tuyên bố chặn được camera hay người đã có quyền ghi nhớ thông tin. DLP và cảnh báo bất thường hỗ trợ phát hiện, không thay chính sách truy cập.

Audit ghi actor, impersonation nếu có, action, target, trước/sau đã redact, reason, correlation_id, IP theo mục đích hợp lệ. Tách quyền xóa log khỏi Admin ứng dụng; cấu hình immutable storage khi cần. Bản ghi tài chính dùng correction/reversal; consent dùng log grant/revoke. Không ghi tràn dữ liệu cá nhân vào audit chỉ vì yêu cầu truy vết.

> **Download và revoke:** File PII, hợp đồng, ghi âm, dữ liệu tài chính và export nội bộ đi qua download gateway kiểm session/principal, object ACL, scan status và grant hiện tại ở mỗi request, kể cả Range/resume. Không trả raw storage presigned URL cho nhóm này; không cache public nội dung bảo vệ. URL gateway mang token không thay session/ACL và không mở rộng scope. Sau commit revoke, request download mới hoặc Range mới phải bị từ chối; byte đã tải hoặc stream đã được cấp trước revoke không thể thu hồi chắc chắn. Asset publish cho khách dùng share grant riêng đúng recipient/resource/expiry; nếu chọn bearer link phải hiển thị rõ tính chất có thể chuyển tiếp và có cơ chế revoke ở gateway. Hệ lưu trữ chỉ chấp nhận yêu cầu từ gateway/service được phép.

<a id="module-m20"></a>

#### ĐẶC TẢ MODULE M20 — Quản trị dữ liệu cá nhân và quyền chủ thể

**Mục đích, tác nhân và phạm vi:** Privacy owner quản mục đích, cơ sở xử lý, yêu cầu chủ thể, retention và nhà cung cấp; Ops/Integration thực thi, Finance/pháp lý xác nhận phần phải lưu. Phân biệt agency xử lý khách bán dịch vụ và dữ liệu theo chỉ dẫn khách. P0 có controls; có thể dùng registry/quy trình ngoài CRM được mapping, không hoãn trách nhiệm vì chưa xây privacy engine.

| Chức năng | Kích hoạt / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc | Vì sao cần |
| --- | --- | --- | --- | --- |
| M20-F01 Phê duyệt xử lý | Connector/feature mới, data classes, purpose | Chưa có owner/cơ sở/vai trò/phạm vi thì giữ Draft, không activate; consent không thay hợp đồng xử lý theo chỉ dẫn | Processing_Records/policy; UC14 | Biết dữ liệu được dùng cho mục đích nào và ai chịu trách nhiệm. |
| M20-F02 Grant/revoke consent | Endpoint/purpose/channel, evidence/version | Grant phải có bằng chứng phù hợp; revoke hợp lệ commit suppression trước xác nhận; không OR consent sau merge | Consent_Logs/Consent_State; FR02/09 | Chứng minh và thực thi đúng quyền đồng ý/rút lại theo phạm vi. |
| M20-F03 Chặn gửi | Intent và suppression hiện tại | Dispatch recheck authoritative; unsubscribe/bounce/complaint giữ semantics riêng; import không hồi sinh quyền | Allowed/blocked có reason; FR34, SEC05 | Quyền đã rút phải có hiệu lực ở lần gửi thực tế. |
| M20-F04 Nhận yêu cầu | Request type, received_at, phạm vi và xác minh vừa đủ | Không tiết lộ hồ sơ trước xác minh; valid_request_received_at không bị reset tùy tiện; case thiếu thông tin vẫn có owner/history | Privacy_Requests; UC11 | Chủ thể có đường yêu cầu mà chưa cần hệ thống biết đầy đủ danh tính. |
| M20-F05 Tính hạn/xử lý | Loại quyền, vai trò, legal policy Active | Chỉ dùng rule có nguồn chính xác, nhánh áp dụng, đơn vị/calendar/trigger và owner đã duyệt; response/action/extension tách riêng | Due/history/tasks; Chương 6.3 | Không dùng một hạn chung cho các nghĩa vụ pháp lý khác nhau. |
| M20-F06 Retention/xóa | Đến hạn hoặc request được duyệt | Có legal hold thì hạn chế đúng phần/cơ sở; không hold thì xóa/ẩn danh theo scope; backup theo vòng đời và ledger khi restore | Deletion evidence; UC11/NFR06 | Không giữ vô hạn hoặc xóa nhầm phần đang có nghĩa vụ lưu. |
| M20-F07 Vendor/AI/xuyên biên giới | Dữ liệu ra cloud/AI/support | Chưa đủ điều kiện vendor/feature/region/retention thì không chuyển; no-train không tự thành zero retention | Vendor/flow review; M06/M19 | Dữ liệu không rời hệ thống chỉ vì một tính năng cloud đã được bật. |
| M20-F08 Sự cố | Phát hiện/awareness, loại dữ liệu/ảnh hưởng | Cô lập, bảo toàn evidence và đánh giá nghĩa vụ ngay; Confirmed không tự reset mốc pháp lý | Incident/notification tasks; Ops/privacy | Có phản ứng và xem xét nghĩa vụ ngay khi phát hiện sự cố. |

**Màn hình và trường:** Registry xử lý bắt buộc purpose, role controller/processor theo tình huống, scope/data classes, nguồn, cơ sở, recipient/vendor, nơi xử lý, owner và effective version. Yêu cầu chủ thể cần request_type, received_at, identity assurance/evidence tối thiểu, valid_request_received_at khi đủ thủ tục, owner, response/action due và kết quả từng phạm vi. Policy pháp lý lưu exact source/điều khoản, nhánh vai trò/ngoại lệ, trigger, ngày làm việc hay lịch, timezone, extension/notice rule và người duyệt; chưa chốt thì Draft và có gate xử lý phù hợp, không tự seed một hạn chung. Retention/hold có object scope, lý do/cơ sở, review date và authority, không bool vô thời hạn thiếu owner.

**Commands và trạng thái:** `approve-processing`, `record-consent`, `revoke`, `receive-request`, `verify-scope`, `assign-obligations`, `extend-with-notice`, `execute-restriction/deletion`, `review-hold`, `close-request`. Request Received→Validating→InProgress→Completed hoặc PartiallyCompleted/Refused với lý do; thiếu thông tin có task, không âm thầm đổi deadline. Policy Draft→Reviewed→Active; thay policy có version/effective date. 

**Quyền và ngoại lệ:** Steward chỉ xem dữ liệu cần cho case, quyền xóa không từ CRUD thông thường; xuất phản hồi chủ thể cần xác minh recipient. Marketing không được sửa suppression; Operator không tự đổi legal basis. Chứng từ phải lưu được hạn chế truy cập, không dùng lại marketing.  

**Nghiệm thu:** M20-AC01 — revoke/merge/import vẫn chặn đúng endpoint/purpose; FR02/09/34, UC11/18, Consent_Logs/Outbound_Intents, U15/SEC-U05. M20-AC02 — loại quyền/vai trò dùng đúng legal policy đã duyệt; xác minh không reset hạn; UC11, Privacy_Requests/Policy_Versions. M20-AC03 — hold một phần, deletion/restore và vendor gate giữ đúng phạm vi; FR13/37, UC11/21, Processing_Records/Retention_Policies, INT26/RV17.

Nếu legal policy chưa cấu hình, Privacy owner vẫn phải tiếp nhận, tính hạn và xử lý thủ công theo căn cứ áp dụng, lưu evidence; không hoãn nghĩa vụ luật định để chờ cấu hình hệ thống. Chỉ chức năng tự tính hạn/thực thi tự động bị chặn cho tới khi policy được xác nhận.

### 6.3 Khung pháp lý Việt Nam tại thời điểm nghiên cứu

Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 là căn cứ pháp lý năm 2026. Nghị định 356/2025/NĐ-CP có hiệu lực từ 01/01/2026; Điều 42 quy định Nghị định 13/2023/NĐ-CP hết hiệu lực từ cùng ngày. Vì vậy bản này giữ Nghị định 13 làm tham chiếu lịch sử, không coi đó là căn cứ hiện hành duy nhất [S01](#s01), [S02](#s02). Các nghĩa vụ cụ thể phải được đối chiếu với vai trò xử lý dữ liệu của doanh nghiệp trước go-live.

Thiết kế cần quản lý mục đích/cơ sở xử lý, chứng cứ consent khi áp dụng, quyền chủ thể, retention, nhà cung cấp và chuyển dữ liệu xuyên biên giới. Agency phải phân biệt dữ liệu tự thu để bán dịch vụ và dữ liệu xử lý theo chỉ dẫn khách hàng. Không mặc định “dùng cá nhân” hoặc doanh nghiệp nhỏ là miễn mọi nghĩa vụ. Hồ sơ đánh giá tác động và trường hợp ngoại lệ cần được người phụ trách pháp lý kiểm tra theo mô hình thực tế.

| Nhóm kiểm soát | Thực hiện trong CRM | Chứng cứ và người chịu trách nhiệm |
| --- | --- | --- |
| Mục đích xử lý | Purpose registry; bảng Processing_Records | Privacy owner phê duyệt mô tả, dữ liệu và cơ sở trước bật connector. |
| Consent | Thông báo versioned, lựa chọn rõ, log grant/revoke | Evidence truy xuất được; không dùng checkbox chọn sẵn làm baseline. |
| Quyền chủ thể | Request queue, xác minh vừa đủ, hạn xử lý theo quy định áp dụng | Có owner, due_at, kết quả và lý do phần chưa xóa. |
| Nhà cung cấp | Vendor register, phạm vi dữ liệu, nơi xử lý, subprocessor, điều khoản xóa | Hợp đồng/DPA, security review và phương án thay thế. |
| Xuyên biên giới | Ghi luồng sang cloud/AI/support và bên nhận | Pháp lý xác định nghĩa vụ hồ sơ, thủ tục và điều kiện áp dụng. |
| Sự cố | Phát hiện, cô lập, bảo toàn evidence, đánh giá phạm vi | Incident register và quy trình thông báo theo nghĩa vụ hiện hành. |
| Quảng cáo và tin nhắn | Kiểm mục đích, suppression, chính sách kênh, danh sách chặn liên quan | Không đánh đồng đồng ý nhận dịch vụ với đồng ý quảng cáo mọi kênh. |
| Ghi âm và GPS | Thông báo, quyền truy cập hẹp, thu tối thiểu | Không giám sát liên tục; cơ sở xử lý và thời hạn được duyệt. |

#### Deadline pháp lý và luồng AI: cấu hình theo nghĩa vụ

Privacy_Requests lưu received_at, valid_request_received_at, verified_at, request_type, legal_basis/version, response_due_at, action_due_at, extension/history và owner. Tính deadline theo loại quyền/sự kiện đúng thủ tục ở S02 và policy pháp lý đã xác nhận; không mặc định72h sau verified_at hoặc dùng xác minh để reset hạn. Incident lưu detected/awareness/assessment/confirmed và notification obligations riêng; không đợi nhãn Confirmed mới xem xét clock. Privacy owner xác nhận nhánh/recipient/căn cứ áp dụng.

Suppression cho yêu cầu hợp lệ được commit atomically trước xác nhận xử lý thành công; dispatch recheck trạng thái authoritative, không chờ cleanup15phút mới chặn marketing. Cleanup queued/replicas có SLO đo riêng; unavailable và in-flight có reconciliation/exception, không hứa0giây vật lý hay thu hồi chắc chắn tin provider đã nhận. Không đổi consent dựa yêu cầu giả chưa được xác minh vừa đủ.

AI data gateway áp minimization, data classification và pseudonymization/redaction có policy; mapping placeholder là dữ liệu có thể tái định danh, cần kiểm quyền/retention. Training permission, retention/log/cache/feature settings, region/subprocessor và căn cứ chuyển dữ liệu là tiêu chí riêng; không dùng nhãn Training Opt-out như ZDR. Trường hợp vendor/feature chưa đáp ứng, giữ tác vụ thủ công/khôngAI phù hợp. Không gửi CCCD/tài khoản/PII không cần thiết hoặc tin toàn thread chỉ vì đã dùng regex che số.

### 6.4 Lưu giữ xóa và legal hold

Thời hạn sau là đề xuất vận hành, không phải khẳng định thời hạn pháp luật: lead không hoạt động rà soát sau 180 ngày; ghi âm 90 ngày; payload tích hợp tối thiểu 30 ngày; log bảo mật 180 ngày. Privacy owner điều chỉnh theo mục đích, hợp đồng và nghĩa vụ lưu trữ. Chứng từ kế toán/hợp đồng không xóa theo một TTL chung; kế toán/pháp lý đặt lịch lưu riêng và legal hold khi cần.

Xóa gồm primary store, cache, search, BI, AI vector, tệp và tác vụ connector. Backup hết hạn theo vòng đời; sau khôi phục phải áp lại deletion/suppression ledger trước mở truy cập. Legal hold hạn chế truy cập và ngăn dùng lại cho marketing; không giữ vô thời hạn chỉ vì kỹ thuật chưa có nút xóa.

### 6.5 Quyền và bảo vệ dữ liệu trong inbox hợp nhất

| Vai trò | Xem/nhắn | Gộp danh tính | Quản trị kết nối | Xuất và replay |
| --- | --- | --- | --- | --- |
| Sales | Thread được phân công/được chia sẻ trong workspace; gửi qua policy gate | Đề xuất, không tự duyệt merge rủi ro | Không đọc token | Không export mặc định; không replay |
| Trưởng nhóm | Thread thuộc nhóm/chi nhánh được cấp; chuyển người có lý do | Duyệt theo phạm vi nếu được giao stewardship | Xem health, yêu cầu reconnect | Export theo quyền riêng và audit; không xem secret |
| Marketing | Chỉ conversation/segment có purpose và quyền được cấp | Xem candidate cần thiết, không merge hàng loạt | Quản lý chiến dịch không mặc nhiên quản lý mailbox | Không lấy raw inbox làm danh sách broadcast |
| Operator tích hợp | Metadata lỗi đã khử PII; mở nội dung cần quyền hỗ trợ có thời hạn | Không | Kết nối/rotate qua vault và approval nội bộ | Replay theo range, lý do và audit; không gửi tùy ý |
| CEO | Dashboard và hồ sơ theo role được cấp | Không mặc định | Không cần secret | Quyền xem tổng hợp không mặc nhiên cho bulk export |

Tách mailbox agency nội bộ và mailbox hỗ trợ khách hàng; không đồng bộ toàn bộ email nhân sự vào CRM. Lưu consent/purpose theo nguồn, thời điểm, nội dung thông báo, phạm vi và việc rút lại. Có quyền xử lý yêu cầu dịch vụ không tự đồng nghĩa được remarketing. Quy định pháp lý ở 6.3 tiếp tục áp dụng; policy kênh và consent là các điều kiện bổ sung, không thay thế nhau.

Xóa/ẩn dữ liệu cần propagate tới body store, attachment, search, read model, AI cache và bên xử lý liên quan theo chính sách đã phê duyệt. Backup có vòng đời riêng và suppression khi restore; legal hold áp dụng đúng phần có cơ sở lưu giữ. Watermark và khóa export giảm rủi ro nhưng không ngăn tuyệt đối chụp màn hình; kiểm soát cần least privilege, đào tạo và audit. Không tuyên bố gom về CRM sẽ tự động ngăn Sales dùng kênh riêng.

### 6.6 Quyền và trách nhiệm quản lý công việc

| Vai trò | Trách nhiệm chính | Không mặc định có quyền |
| --- | --- | --- |
| Requester | Nêu nhu cầu, tiêu chí đầu ra | Duyệt thay người có thẩm quyền |
| Creator | Tạo bản ghi, có thể là automation | Làm người chịu trách nhiệm kết quả |
| Assignee | Chịu trách nhiệm thực hiện chính, báo blocker | Tự đổi hạn cam kết, tự mở quyền file |
| Collaborator | Thực hiện phần việc được phân | Đổi owner hoặc duyệt hoàn thành |
| Reviewer | Kiểm kết quả theo tiêu chí và version | Thay khách nghiệm thu hợp đồng |
| Watcher | Theo dõi và nhận tin theo grant | Sửa nội dung hoặc tự mời người khác |
| Team lead / Project manager | Phân bổ, ưu tiên, xử lý escalations | Xem mọi workspace/finance/private task |
| Org admin | Cấu hình cấu trúc và quyền trong authority | Đọc/sửa toàn bộ công việc nghiệp vụ |
| Worker | Nhắc hạn, lặp việc, đồng bộ | Bỏ qua quyền hiện hành vì đã lập lịch trước |

Trong RACI đơn giản, assignee là R chính, accountable là người giao/quản lý được chỉ định; reviewer có quyền duyệt cụ thể. Không dùng creator_id làm mặc định bất biến cho mọi authority.

| Action | Assignee | Collaborator | Reviewer | Manager có scope | Admin cấu hình |
| --- | --- | --- | --- | --- | --- |
| Xem task/file | Có grant hiện tại | Có grant hiện tại | Có grant hiện tại | Theo grant quản lý | Không mặc định |
| Cập nhật tiến độ/kết quả | Có | Phần được cấp | Nhận xét review | Có theo authority | Không mặc định |
| Giao/chuyển owner | Theo quyền delegate | Không | Không mặc định | Có trong phạm vi cấp | Không mặc định |
| Xin đổi hạn | Có | Đề nghị qua owner | Có cho review due | Có | Không |
| Duyệt đổi hạn | Chỉ task tự quản không cam kết ngoài | Không | Nếu được chỉ định | Có trong authority | Không |
| Submit | Có | Không mặc định | Không | Có nếu được thao tác thay, có audit | Không |
| Approve/reject | Không nếu cần tách người | Không | Có với submission version | Có nếu reviewer/override hợp lệ | Không |
| Cancel/reopen | Theo policy personal | Không | Theo quyền | Có lý do, scope và version | Không |
| Export/config workflow | Quyền riêng | Quyền riêng | Quyền riêng | Quyền riêng | Chỉ config được cấp |

Mọi task link tới CRM record được kiểm quyền riêng ở cả hai phía. Quyền xem task không tự mở hợp đồng/file; quyền xem contact không tự mở mọi task. Notification không đưa tiêu đề nhạy cảm ra email/push cho người đã bị revoke.

<a id="chuong-7"></a>

## CHƯƠNG 7 YÊU CẦU PHI CHỨC NĂNG

### 7.1 Hồ sơ tải và tiêu chuẩn nghiệm thu

Khối lượng giao dịch hiện tại thấp nhưng số người dùng có thể khoảng 45. Số event quảng cáo của khách hàng không suy ra từ 100 lead agency; phải đo riêng trước nhập raw ad events. Kịch bản kiểm tải dưới đây là mục tiêu thiết kế có điều kiện, không phải kết quả benchmark đã thực hiện.

| Mã | Yêu cầu | Cách đo và ngưỡng đề xuất |
| --- | --- | --- |
| NFR01 | Thao tác phổ biến | P95 API nội bộ đọc/ghi ≤800 ms trên dữ liệu 100.000 contacts và 1 triệu activities; loại thời gian API ngoài, báo riêng. |
| NFR02 | Giao diện | P95 mở danh sách lead ≤2 giây trên mạng 4G mô phỏng; ghi rõ thiết bị, RTT, bandwidth. |
| NFR03 | Tải đồng thời | 50 phiên hoạt động, 10 request/giây duy trì 30 phút, burst 50 request/giây 5 phút; lỗi nội bộ <1%, không mất ghi. |
| NFR04 | Webhook | ACK P95 ≤2 giây sau ghi inbox bền vững; queue backlog bình thường <60 giây. |
| NFR05 | Khả dụng | SLO 99,9%/tháng cho hành trình login/read/write CRM; tháng 30 ngày tương đương 43,2 phút downtime. |
| NFR06 | Khôi phục | Production RPO ≤15 phút, RTO ≤4 giờ; pilot RPO 24 giờ/RTO 8 giờ phải được chấp nhận rõ. |
| NFR07 | Isolation | 0 truy cập chéo tenant/workspace trong bộ kiểm thử âm; áp cả API, file, search, BI, AI. |
| NFR08 | Tiền và replay | Replay100lần không nhân effect thuộc module đã bật; tiền/commission cần test khi dùng; điểm loyalty chỉ khi mở P2. Ledger/caps/rounding đối chiếu đúng; không yêu cầu tạo Loyalty_Ledger để pass MVP. |
| NFR09 | Khả năng sử dụng | Tạo next action, ghi kết quả gọi, mở khách từ task trong tối đa 3 thao tác điều hướng; ≥90% người pilot hoàn thành không trợ giúp. |
| NFR10 | Khả năng tiếp cận | Nhãn form rõ, thao tác bàn phím, focus, tương phản phù hợp, lỗi có hướng sửa; không chỉ dùng màu. |
| NFR11 | Quan sát | Correlation xuyên request/event; alarm failure/backlog/quota; log không chứa secret và PII không cần thiết. |
| NFR12 | Tính di chuyển | Xuất dữ liệu được phép cùng dictionary, assets và external IDs; test nhập lại một tập mẫu vào môi trường độc lập. |

### 7.2 Độ sẵn sàng và vận hành

99,9% yêu cầu hạ tầng, on-call và vận hành tương ứng; không phải thuộc tính tự có của microservices. Production dùng app có khả năng phục hồi, DB managed HA khi ngân sách cho phép, health check và triển khai rolling. Định nghĩa SLI bằng probe hành trình người dùng; bảo trì có kế hoạch và phụ thuộc đối tác hiển thị riêng, không âm thầm bỏ khỏi số liệu tổng trải nghiệm.

Tích hợp lỗi vẫn phải cho CRM đọc/ghi và lưu backlog. Circuit breaker ngăn retry bão; bulkhead cho AI/tổng đài khỏi chiếm worker tài chính. Alert critical nếu mất backup, payment mismatch, nghi rò dữ liệu; alert warning nếu chậm connector. Có runbook, người trực và escalation backup.

### 7.3 DRP cụ thể

Backup DB có PITR đủ RPO production, snapshot hằng ngày, retention dự kiến 30 ngày; object storage bật versioning và policy phù hợp. Bản sao tách account hoặc miền lỗi, quyền backup không đồng nhất Admin ứng dụng. Kiểm checksum và thử restore định kỳ; có backup không đồng nghĩa restore được.

Runbook: tuyên bố sự cố → chặn ghi nếu cần → chọn recovery point → khôi phục DB/object/secrets theo quyền → replay outbox có dedup → áp deletion ledger → đối soát số lượng và tổng tiền → smoke test login/lead/payment → người phụ trách cho mở lại → thông báo và post-mortem. Diễn tập ít nhất trước go-live và hằng quý, đo RPO/RTO thực tế.

### 7.4 Mobile offline và UX

PWA ưu tiên Today gồm cuộc hẹn, lead đến hạn và next action. Chỉ yêu cầu dữ liệu tối thiểu lúc tạo lead; thông tin bổ sung tại qualification. Tìm kiếm tiếng Việt có/không dấu, số điện thoại mask, lọc theo owner và deadline. Form lưu nháp rõ ràng, không báo thành công khi server chưa nhận.

Offline MVP chỉ cho nháp ghi chú/task, không approve hợp đồng hoặc payment. Đồng bộ bằng client_operation_id; xung đột version cần người dùng chọn, không last-write-wins cho giá/owner/consent. Không cache PII diện rộng trên thiết bị cá nhân; hết phiên xóa cache nhạy cảm và không cho offline export.

### 7.5 Kiểm thử bảo mật và release

Tách dev/staging/prod, dữ liệu test ẩn danh. CI kiểm unit rule, integration tiền/SLA, policy, contract connector và smoke workflow; quét dependency/secret. Release có migration plan, feature flag, rollback app và kế hoạch sửa dữ liệu. Không chạy kiểm thử có phí thật hoặc gửi tin thật cho khách từ môi trường test.

### 7.6 NFR và quan sát vận hành Omnichannel

Các ngưỡng sau là mục tiêu thiết kế cần đo trong PoC, không phải hiệu năng đã đạt. 100 leads/tháng không cho biết tải message: phải đo messages/conversation, số mailbox, attachment và burst chiến dịch.

| Mã | SLI/SLO đề xuất | Phương pháp xác minh |
| --- | --- | --- |
| ONFR01 | p95 từ event nhận hợp lệ đến Inbox hiển thị <= 5 giây ở tải baseline đã chốt | Timestamp received_at đến projected_at; tách thời gian provider chưa giao, không gọi đó là độ trễ CRM |
| ONFR02 | ACK sau durable write trong timeout provider; ngân sách nội bộ p95 <= 1 giây | Test payload tối đa, DB chậm, restart worker; khi DB không lưu được không ACK thành công |
| ONFR03 | Không trùng hiệu ứng với 10 lần replay cùng event; không leak dữ liệu giữa hai workspace | Integration tests với duplicate, concurrent delivery, same external ID khác connection |
| ONFR04 | Chịu profile thử 10 event/giây trong 15 phút, burst 50 event/giây trong 60 giây | Fixture không PII, ghi queue lag, DB CPU, latency và thời gian drain; đây là profile dự phòng để test, chưa là forecast |
| ONFR05 | Cảnh báo connection lỗi/quyền hết hạn và backlog vượt 5 phút | Fault injection; owner nhận cảnh báo có runbook; suppress alert lặp có kiểm soát |
| ONFR06 | Availability CRM 99,9% đo riêng với khả dụng từng provider | Báo cáo hai lớp, kể cả thời gian provider lỗi; không loại lỗi nhà cung cấp khỏi trải nghiệm người dùng mà giấu đi |

Metrics: inbound_received/accepted/rejected/deduplicated/failed, oldest_pending_age, outbound_unknown, provider429, renewal_failures, identity_review_backlog, SLA_breach. Trace dùng correlation ID xuyên adapter-worker-domain; log không chứa token, body chat hoặc email raw mặc định. Read receipt không được hỗ trợ là `unknown`, không phải `false` hay “khách chưa đọc”. DR drill phải bao gồm credential restore có kiểm soát, cursor, outbox và suppression; không replay tất cả send intent sau restore như gửi mới.

### 7.7 NFR và vận hành Task Core

**[Đề xuất bổ sung]** Profile kiểm thử: 50 người dùng đồng thời, 100.000 task, 1 triệu event/comment, 10 mutation/giây, 1.000 recurrence đến hạn cùng phút. Đây là tải kiểm thử đề xuất cho lộ trình mở rộng, không phải hiện trạng đo được.

| Nhóm | Yêu cầu nghiệm thu |
| --- | --- |
| Hiệu năng | List/board p95<=1s, mutation p95<=1s không gồm scan/sync; phân trang cursor 50 item, có tie-break id |
| Nhắc hạn | p95<=60s sau due của notification khi hệ khỏe; lịch business timezone, quiet hours và escalation exceptions có policy |
| Nhất quán | DB transaction cho assignment/status + audit/outbox; không yêu cầu distributed exactly-once; consumer idempotent |
| Bảo mật | ACL hiện tại cho API/search/count/export/file/notification; không auto-grant do mention/link; permission revocation cập nhật cache |
| Phục hồi | Restart scheduler/outbox không sinh occurrence trùng; DLQ có operator/replay permission; trạng thái partial rõ |
| Thời gian | UTC storage + business timezone; date-only có cutoff/calendar explicit; SLA và task reminder không dùng chung clock tùy tiện |
| Accessibility | Không chỉ phân biệt status bằng màu; thao tác board có đường list/keyboard tương đương |
| Audit | Ai đổi gì, trước/sau, lý do, delegated actor, source system và approval version; retention theo Master |
| Mobile/offline | Draft được phép; approve/reassign/submit phải online và recheck; không ghi last-write-wins khi conflict |
| Observability | Offer/review quá hạn, orphan tasks, recurrence gaps, sync conflicts, notification retry, missing estimates; mỗi alert có owner |

Notification chỉ là nhắc, không là nguồn chuẩn của trạng thái. “Đã gửi push” không đồng nghĩa “nhân viên đã nhận việc”. Action từ email/deep link phải mở session được kiểm quyền lại.

<a id="chuong-8"></a>

## CHƯƠNG 8 HỆ THỐNG BÁO CÁO VÀ BI DASHBOARD

### 8.1 Dashboard theo quyết định

Mỗi biểu đồ có kỳ đo, time basis, filter scope, source, last_refreshed_at và link drill-down. Dữ liệu nhạy cảm theo quyền; màn hình tổng không tạo đường vòng để export PII. “Realtime” chỉ dùng cho dữ liệu thực sự có sự kiện cập nhật; báo cáo chậm phải ghi độ trễ, không đổi nhãn để tạo cảm giác chính xác.

| Vai trò | Báo cáo trọng tâm | Quyết định và tần suất |
| --- | --- | --- |
| CEO | Phí dịch vụ, biên đóng góp, thực thu, tuổi nợ, pipeline, tái ký, tập trung doanh thu top khách | Điều chỉnh ưu tiên và nguồn lực; tiền gần realtime, tài chính đã chốt theo ngày/kỳ. |
| CMO | Sourced pipeline, CAC, CPL/CPQL, MQL→SAL→SQL, channel spend, campaign health, tracking quality | Phân bổ ngân sách và kiểm tra nút thắt; refresh 15–60 phút tùy API, đối soát hằng ngày. |
| Giám đốc kinh doanh | Deal theo stage, aging, win/loss, cycle, forecast, SLA, capacity pool | Gỡ nghẽn và coaching; operational ≤5 phút. |
| Trưởng nhóm | Lead chưa owner, quá SLA, next action trễ, workload, lý do reject | Phân lại công việc; operational ≤1 phút mục tiêu khi hệ thống khỏe. |
| Sales | Today, khách cần gọi, báo giá chờ, hợp đồng sắp ký, commission preview | Hành động tiếp theo; không xếp hạng khi mẫu quá nhỏ. |
| AM/Delivery | Onboarding, milestone, vòng sửa, nghiệm thu, ticket, gia hạn | Phân bổ ekip và giữ chất lượng; ≤5 phút nội bộ. |
| Kế toán | Unmatched payment, công nợ, credit chưa phân bổ, refund, payout | Đối soát trước khóa kỳ; ledger nội bộ gần realtime, ERP có freshness riêng. |
| Khách hàng | Deliverable, tiến độ, quyết định cần duyệt, KPI campaign được chia sẻ | Duyệt và theo dõi phạm vi hợp đồng; snapshot có version. |

### 8.2 Công thức phải thống nhất

| Chỉ số | Công thức | Điều kiện tránh hiểu sai |
| --- | --- | --- |
| CPL | Chi phí acquisition / lead hợp lệ cùng phạm vi | Không lấy lead của khách agency làm mẫu số cho chi phí tìm khách agency. |
| CPQL | Chi phí acquisition / lead qualified | Định nghĩa qualification versioned; mẫu số 0 → N/A. |
| Proposal win rate | Deal thắng có proposal / proposal deals đã có kết quả | Không dùng tổng báo giá revision làm mẫu số. |
| Sales cycle | Trung vị ngày từ qualified đến Won | Kèm số mẫu và percentile, tách B2B/B2C. |
| Margin đóng góp | Phí dịch vụ thuần − chi phí trực tiếp phân bổ | Không đồng nhất với lợi nhuận kế toán sau mọi chi phí. |
| ROAS | Doanh thu được gán theo model / ad spend | Không đồng nghĩa ROMI, không chứng minh nhân quả. |
| ROMI | (Đóng góp tăng thêm ước tính do marketing − chi phí marketing) / chi phí marketing | Nếu không đo incrementality, ghi proxy/attributed ROMI và phương pháp. |
| Retainer MRR | Phí dịch vụ định kỳ chuẩn hóa tháng đang hiệu lực | Loại one-off/media; khác cash thu trong tháng. |
| Capacity utilization | Giờ công đã phân cho delivery / giờ khả dụng | Phân biệt billable utilization và tổng workload. |
| Adoption chất lượng | Bản ghi active đủ owner/next action/evidence / tổng active | Login count chỉ chỉ báo kỹ thuật phụ. |

Bốn scope đo lường tách: acquisition cost của agency; service economics agency; client media spend; client business outcome. CAC agency không dùng media khách; doanh số khách không thành doanh thu agency. Metric lưu grain, time/currency/tax basis, beneficiary và freshness. Unknown do thiếu nguồn khác Direct/Organic. MQL/SAL/SQL theo demand episode/transition, không đếm acquisition lại khi recycle. LTV quan sát khác dự báo lifetime; cohort tuổi khác nhau cần cùng cửa sổ quan sát. Sales cycle báo total/active/hold và open aging; không clone hoặc OnHold làm đẹp tỷ lệ. Renewal/expansion/contraction/churn theo recurring model; one-off đủ điều kiện tái ký riêng.

Health theo financial/delivery/relationship/outcome component có nguồn, missing là Unknown; kết quả phải dẫn action owner. Survey response rate nêu eligible/sent/delivered; NPS contact và account view nêu weight/role. Restore/restate giữ snapshot đã công bố. First/last và platform-attributed views riêng, không cộng các model thành tổng tiền.

Health MVP dùng các chiều tài chính, giao hàng, quan hệ và outcome riêng với evidence, freshness, coverage và action owner. Missing không tự100 hoặc0. Score tùy chọn có metric direction/window/sample/weights/version; quan sát100 với coverage60% phải hiện thiếu dữ liệu, không tự Healthy/upsell. Không tính actual/target cho mọi KPI: CPL thấp tốt, revenue cao tốt, một số metric có target range. Risk flags như S1/unpaid cần severity/aging/value/dispute context; nhiều ticket cùng incident không tự trừ lặp. Score chạy shadow/pilot trước khi dùng tự động; không lấy trọng số30/30/20/20 và cap40 làm chuẩn chưa được phê duyệt.

### 8.3 Kiểm soát sai số và phân tích

Data quality dashboard đo completeness, duplicate candidate rate, unresolved identities, orphan FK, missing attribution, stale connectors và chênh lệch ERP. Owner xử lý từng lỗi, có SLA; không che lỗi bằng “0”. Thay đổi định nghĩa metric lưu version và ngày áp dụng, báo cáo lịch sử có thể tái tính nhưng phải giữ snapshot đã công bố.

Forecast MVP là tổng deal amount × xác suất stage cấu hình, tách committed/best case/pipeline; xác suất chưa hiệu chỉnh phải ghi “giả định”. Không gắn nhãn AI forecast nếu chỉ nhân hệ số. Với dữ liệu nhỏ, báo khoảng kịch bản và risk thay vì một con số chắc chắn.

### 8.4 Dashboard Omnichannel và định nghĩa không gây hiểu nhầm

| Người dùng | Chỉ số/quyết định | Quy tắc đo |
| --- | --- | --- |
| CEO | Inquiry đủ điều kiện → hợp đồng → lợi nhuận gộp theo nguồn | Một người chat nhiều kênh không tự thành nhiều khách mới; giữ first-touch và assisted-touch riêng |
| CMO | Lead hợp lệ, cost/qualified inquiry, conversion theo campaign | Tách paid/organic/unknown; thiếu UTM không điền đoán; phí quảng cáo khách hàng không cộng CAC agency |
| Giám đốc kinh doanh | Queue aging, first-human-response, tỷ lệ mất lead, workload | Median và p90 cùng mẫu số; autoack tách; không phạt Sales do outage provider được ghi nhận |
| Trưởng nhóm | Unassigned, sắp vi phạm SLA, số cuộc mở theo capacity | Reassignment không reset đồng hồ; chuyển pending phải có lý do |
| Sales | Công việc tiếp theo, lịch sử cam kết, draft, người cần follow-up | Chỉ thấy phạm vi được cấp; conversation active không đồng nghĩa cơ hội bán mới |
| Operator | Connection health, coverage gap, retry/DLQ, send unknown | “Không có sự kiện” không đủ kết luận khỏe; kết hợp token, heartbeat/sync và lịch sử lưu lượng |

Tỷ lệ hợp nhất đúng phải đo bằng mẫu được steward xác minh, không tối ưu chỉ “merge rate”. Tỷ lệ thu nhận = số ID hợp lệ ghi nhận / số ID trong nguồn đối soát có thể quan sát; nếu provider không cung cấp denominator thì ghi “không đo được độ bao phủ tuyệt đối”, không báo 100%. Mỗi dashboard hiện timezone, freshness, phạm vi dữ liệu và định nghĩa metric version.

### 8.5 Capacity và KPI quản lý công việc

#### Capacity

P0 dùng WIP theo số việc đang làm, phân nhóm loại việc; không so một task “gọi lại 5 phút” với một task “dựng video 2 ngày” bằng số lượng.

P1: `available_minutes = scheduled_work_minutes − approved_unavailable_minutes − fixed_commitments_minutes`, loại khoảng chồng lặp trước khi trừ. `load_ratio = allocated_remaining_minutes_in_period / available_minutes`. Mẫu số 0 hiển thị unavailable, không chia 0; estimate thiếu hiển thị coverage Unknown. Phân bổ theo lịch, không lấy toàn remaining effort đổ vào ngày due.

Parent summary không cộng effort nếu đã tổng hợp children; time entry ghi một task leaf, projection lên parent chỉ đọc. Timesheet không mặc định là chấm công HR, không suy đã làm ít giờ là kém hiệu suất.

#### KPI dictionary tối thiểu

| Metric | Định nghĩa | Quyết định / chống làm đẹp số |
| --- | --- | --- |
| Unassigned age | now − queue_entered_at cho việc chưa có assignee | Manager phân bổ; giữ tuổi gốc qua chuyển queue |
| Acceptance latency | accepted_at − offered_at từng assignment | Phát hiện giao sai người/thiếu phản hồi; autoaccepted báo riêng |
| Due-cohort completion rate | Task có due trong kỳ và DONE trước/equal due / task đủ điều kiện có due trong kỳ | Bao gồm task còn mở quá hạn trong mẫu số; canceled báo riêng, không loại tùy ý |
| Submitted on time | Lần nộp đạt format trước due / task cần nộp trong kỳ | Tách khỏi approved on time để thấy review bottleneck |
| First-pass acceptance | Submission đầu được approve / task có decision review đầu | Không lấy task chưa review làm reject hoặc success |
| Review age/latency | Chờ từ submission hiện hành tới decision/now | Reviewer queue và backup |
| Blocked time | Hợp các khoảng blocker active, phân loại internal/external | Không trừ khỏi elapsed mà giấu trễ; không cộng chồng |
| Reopen rate | Task có reopen sau Done / task Done trong cohort đã định | Phân biệt lỗi chất lượng với scope mới |
| WIP | Unique task InProgress/InReview theo scope và type | Không đếm watchers/collaborators như task riêng |
| Estimate coverage | Task có estimate hợp lệ / task cần planning | Thiếu dữ liệu không là nhàn rỗi |
| Milestone reliability | Milestone đạt evidence trước committed_due / milestone tới hạn | Task Done không thay acceptance |

Mỗi metric giữ time basis/calendar/version, filter scope và mẫu số. Due gốc và due hiện hành báo song song; đổi hạn sau khi trễ không hồi tố làm KPI gốc đẹp lên. Không dùng bảng xếp hạng task count làm cơ sở duy nhất đánh giá nhân viên.

<a id="chuong-9"></a>

## CHƯƠNG 9 LỘ TRÌNH 90 NGÀY QUẢN TRỊ THAY ĐỔI VÀ ĐÀO TẠO

### 9.1 Kế hoạch 90 ngày theo gate

**Delta 1.7:** bổ sung Task Core theo 9.16 vào gate cá nhân/team; trước cam kết lịch cần ước lượng lại thiết kế/schema/API/QA/migration cho scope mới. Bảng ngày bên dưới là khung kế hoạch tham chiếu, không bằng chứng đủ nguồn lực để hoàn thành cả Work Management trong 90 ngày.

Kế hoạch tính từ ngày khởi động được chủ dự án chọn, không tự ấn định ngày bắt đầu. 90 ngày hướng tới MVP ổn định; không bao gồm tự xây toàn bộ CRM/CDP/HRM/AI/sàn thương mại điện tử. Với cá nhân không có đội kỹ thuật, ưu tiên cấu hình giải pháp có sẵn hoặc hybrid nhẹ và kéo dài kế hoạch nếu nguồn lực không đáp ứng.

| Thời gian | Phạm vi | Gate và người xác nhận |
| --- | --- | --- |
| Ngày 1–10 | Discovery, làm rõ 50 khách, danh mục dịch vụ, pain point, vai trò, inventory dữ liệu | Chủ dự án chốt scope P0, giả định và người chịu trách nhiệm. |
| Ngày 11–20 | Prototype/pilot cá nhân: hồ sơ, lead, next action, pipeline, mẫu brief/SOW | Thực hiện 10 tình huống thật đã ẩn danh; baseline nhập liệu và usability. |
| Ngày 21–35 | Quyền/scope, import staging, quote, contract, task/SLA, audit, consent | QA pass dedup/isolation; Sales và Marketing xác nhận quy tắc. |
| Ngày 36–50 | Payment thủ công kiểm soát, commission preview, handoff, ticket, dashboard | Kế toán/owner đối soát bộ số mẫu; không có sai lệch tiền. |
| Ngày 51–65 | Pilot 5 Sales + 2 Marketing; một nguồn lead và một kênh giao tiếp | ≥95% active records có owner/next action; lỗi critical =0. |
| Ngày 66–75 | Fix pilot, thử 2 chi nhánh, kiểm chuỗi brief/SOW/approval và bàn giao; restore drill | Pass quyền chi nhánh, backup/restore, SLA và offboarding. |
| Ngày 76–85 | UAT đầy đủ P0, dry-run migration, đào tạo, rehearsal cutover | Chủ nghiệp vụ ký UAT; phát hiện critical/high chưa xử lý thì no-go. |
| Ngày 86–90 | Go-live theo nhóm, hypercare, rà chỉ số hằng ngày | Hoạt động ổn định; bàn giao runbook, owner và backlog P1. |

### 9.2 Nguồn lực và trách nhiệm

Chủ dự án quyết phạm vi/ngân sách; BA quản rule/KPI/traceability; technical lead quản API/schema/security; QA quản UAT; Sales champion và Marketing champion hướng dẫn nhóm; người phụ trách tài chính đối soát; privacy owner kiểm mục đích/retention. Chưa có người giữ một vai thì CEO chỉ định kiêm nhiệm rõ ràng, không giả định chức năng tự vận hành.

Họp backlog hằng tuần, review pilot hai lần/tuần, báo rủi ro theo owner và hạn. CR vượt phạm vi 90 ngày phải ghi chi phí/lợi ích và ảnh hưởng ngày go-live. Tích hợp không có quyền API đúng hạn chuyển sang nhập thủ công kiểm soát, không dùng scraping làm lối tắt mặc định.

### 9.3 Quy chế sử dụng và động lực

CRM là nguồn ghi nhận chính cho owner, pipeline, next action và chứng cứ bàn giao. Báo cáo họp lấy từ CRM; bỏ báo cáo Excel trùng khi đối soát đạt. Sales được thấy lợi ích trực tiếp: ít nhập lại, lịch nhắc, báo giá mẫu, lịch sử khách và hoa hồng minh bạch.

Giai đoạn đầu hướng dẫn và sửa quy trình; sau đó nhắc nhở, coaching và xử lý theo nội quy hợp lệ. Không thiết kế phạt tiền/cắt lương làm biện pháp thay kỷ luật lao động. Thưởng chất lượng dữ liệu phải có tiêu chí công bố trước, xác minh và cơ chế khiếu nại; khoản hoa hồng đã phát sinh theo thỏa thuận không bị tước tùy ý chỉ vì thiếu thao tác CRM. Quy chế cần rà soát pháp lý trước áp dụng [S13](#s13).

Có cơ chế sự cố: nếu hệ thống/tổng đài lỗi thì ghi exception và cho backfill có chứng cứ; không buộc nhân viên giả timestamp. Quản lý cũng phải làm approval trong CRM, tránh yêu cầu Sales dùng hệ thống nhưng duyệt qua chat không lưu bằng chứng.

### 9.4 Chương trình đào tạo

| Nhóm | Nội dung và thời lượng đề xuất | Bài kiểm tra thực hành |
| --- | --- | --- |
| Cá nhân/chủ dự án | 2 buổi ×90 phút: pipeline, brief, quote, payment, review | Tự chạy 1 lead B2B và 1 B2C từ intake đến gia hạn. |
| Sales | 2 buổi ×90 phút: Today, SLA, discovery, báo giá, handoff | Nhận lead, ghi call đúng, tạo quote, xử lý mất deal. |
| Marketing | 2 buổi ×120 phút: strategy/IMC, campaign, KPI, consent | Tạo plan, QA tracking, trình duyệt và đọc lỗi spend. |
| Quản lý | 90 phút: capacity, exception, dashboard, approval | Duyệt đúng hạn mức, thu hồi lead và kiểm audit. |
| Tài chính/AM | 2 buổi ×90 phút: partial payment/refund; nghiệm thu/ticket | Đối soát 3 trường hợp và phân biệt defect/change request. |
| Admin/Privacy | 120 phút: quyền, offboarding, backup, yêu cầu dữ liệu | Thu hồi phiên, kiểm isolation, diễn tập request và restore. |

### 9.5 Bộ UAT tối thiểu

Mỗi release có `Release_Acceptance_Profile` được version và phê duyệt, gồm capability/FR bật, dependencies, nguồn ghi, provider, luồng tiền, policy versions, owner và mapping test. Mỗi test tách `test_severity` (hậu quả), `delivery_priority` (giai đoạn capability) và `applicability_expression`. Nhãn P0/P1/P2 không thay biểu thức áp dụng.

Mọi control về tiền/quyền/consent/gửi đúng người/SLA/phục hồi của capability đang bật phải Pass trước go-live. Applicability False ghi Not Applicable với evidence API/job/role/flag không có đường sử dụng capability; không ghi Pass. Applicability True chưa chạy là Not Run và chưa đủ điều kiện ký. Deferred chỉ cho capability chưa bật có dependency closure; không được defer control của capability đang chạy. QA/business owner ký cùng actual/build/fixture/evidence; không nghiệm thu bằng tỷ lệ số test.

| Test | Sửa applicability trong các bảng 9.5/9.12/9.13 |
| --- | --- |
| U19/M11 | P0 control khi launch/publish cần approval được bật; N/A khi ngoài phạm vi; không hoãn control vì nhãn P1 cũ. |
| U23-R/U23-L (điều kiện áp dụng) | Tách `U23-R` reversal referral khi referral P1 bật; `U23-L` reversal điểm khi loyalty P2 bật. |
| U20/M25 | Khi dùng spend nhập tay/sync/report phải thử thiếu dữ liệu/freshness; không bắt mua API spend P1. Không dùng spend thì N/A có evidence. |
| CEO-U21/RV04 | Concurrency resource là P0 control khi reservation bật; nếu chỉ lịch cá nhân thì N/A resource và vẫn thử lịch/hủy reminder đang dùng. |
| U11/U12/FA và commission | Cash/allocation test theo phần cash bật; payout/refund/commission có control tương ứng trước bật, không bật payout rồi defer adjustment. |
| U22/INT27/INT28/OC20 | Guard trước bật AI; eval model/STT N/A khi AI off; kiểm feature-off không còn đường tool/retrieval ngoài ý muốn. |

Profile pilot của thiết kế 1.7: thêm Task Core cá nhân/team với My Work, giao/nhận, review và reminder; W-F08–09 hoàn tất trong release P0 theo 9.16. Đồng thời giữ một nguồn/một inbox; quyền, contact/demand, pipeline/next action, quote/SOW, contract/obligation, receipt nhập tay có kiểm soát, handoff/milestone/ticket và recovery. Không AI, không điểm, không forecast health tự động, không bắt API ERP/spend/resource engine nếu chưa dùng. Thay đổi so với profile phải có CR/effort/dependency/test trước activation; mục tiêu năm kênh không trở thành năm kênh bắt buộc trong 90 ngày.

| Test | Liên kết | Dữ liệu hoặc hành động | Kết quả mong đợi | Ưu tiên |
| --- | --- | --- | --- | --- |
| U01 | UC01 | Webhook lặp 3 lần | 1 lead, 1 assignment, đủ log | P0 |
| U02 | UC02 | Hai Sales claim đồng thời | 1 thành công, 1 conflict; owner không thay ngẫu nhiên | P0 |
| U03 | UC02 | Lead 18:00 thứ Sáu | Deadline tính từ ca kế tiếp theo lịch nghỉ | P0 |
| U04 | UC02 | Không activity sau SLA | Thu hồi có history; tối đa 2 vòng rồi escalation | P0 |
| U05 | UC03 | B2C không có doanh nghiệp | Cho tạo deal không cần account giả | P0 |
| U06 | UC15 | Hai contact dùng chung số | Không tự merge; steward có hàng đợi | P0 |
| U07 | UC05 | Giảm giá vượt quyền | Chặn gửi approved; đúng người duyệt | P0 |
| U08 | UC06 | Won; điều khoản yêu cầu ứng trước; chưa đủ cọc và không có approved credit/start exception | Order có thể tạo; Paid không bật; kickoff pending. Approved credit/ngoại lệ chỉ mở đúng công việc được duyệt, không tự cho chi media | P0 khi áp dụng |
| U09 | UC07 | Ảnh chuyển khoản chưa có xác thực | Không ghi confirmed hoặc commission | P0 |
| U10 | UC07 | Thu 50% + media + VAT | Base chỉ phần dịch vụ đủ điều kiện; tiền còn lại đúng | P0 |
| U11 | UC07 | Replay payment 100 lần | Ledger/commission không nhân bản | P0 |
| U12 | UC13 | Refund sau khóa kỳ | Adjustment kỳ mới; không sửa kỳ cũ | P0 |
| U13 | UC08 | Khách thêm đầu việc | CR riêng; không âm thầm đổi SOW | P0 |
| U14 | UC09 | Pause rồi reopen ticket | Timer phản hồi giữ nguyên; nguyên nhân truy được | P0 |
| U15 | UC11 | Rút consent khi journey chờ | Chặn bước gửi tiếp và có propagation log | P0 |
| U16 | UC12 | User đã offboard dùng token/URL gateway cũ | Sau commit revoke, request GET/Range/download mới bị từ chối; không đòi thu hồi byte đã tải | P0 |
| U17 | UC14 | Dùng ID workspace khác | Không lộ qua API/search/file/BI/AI | P0 |
| U18 | UC15 | Import có 2 dòng sai/consent trống | Dry-run báo lỗi; không gán true mặc định | P0 |
| U19 | UC04 | Đổi creative sau approval | Gate yêu cầu duyệt đúng version mới; N/A khi không có launch/publish cần approval | P0 control khi bật |
| U20 | UC16 | Spend thiếu một ngày | Freshness/partial rõ, không tính như 0 | P0 |
| U21 | NFR06 | Khôi phục backup môi trường độc lập | Đạt RPO/RTO mục tiêu và đối soát tiền | P0 |
| U22 | FR13 | Prompt injection trong tệp khách | Không export/đổi quyền/gửi tin tự động; feature-off không mở tool bypass | P0 guard trước bật AI; N/A model test nếu không triển khai AI |
| U23-R | FR10 | Refund khoản referral đủ điều kiện | Đảo thưởng giới thiệu đúng phần một lần, giữ lịch sử | P0 control khi referral P1 bật |
| U23-L | FR10 | Refund giao dịch đã phát điểm loyalty | Đảo điểm đúng phần một lần; không nhân effect do replay | P0 control khi loyalty P2 bật |
| U24 | NFR09 | 5 người pilot ghi cuộc gọi | ≥90% hoàn tất không trợ giúp; không quá 3 điều hướng | P0 |

### 9.6 Cutover rollback và hypercare

Trước cutover: chốt data owner, backup, freeze cửa sổ ghi cũ, export delta, import staging, reconcile count + tổng tiền + owner + consent, chạy smoke và ký go/no-go. Nếu lệch tiền, lỗi isolation hoặc thiếu backup thì no-go. Không xóa hệ thống nguồn ngay sau chuyển đổi.

Rollback ứng dụng khác rollback dữ liệu: nếu đã có giao dịch mới, phải xuất delta và đối soát trước quay về hệ thống cũ. Một hệ thống được chỉ định nguồn ghi tại từng thời điểm; tránh hai bên cùng phát hóa đơn hoặc gửi tin. Hypercare ít nhất 2 tuần sau go-live, không ép kết thúc chỉ vì hết ngày 90; ghi lỗi, owner, SLA và thông báo người dùng.

### 9.7 Backlog sau MVP

P1 theo nhu cầu: connector kế toán/PMS/calendar/spend, workload theo effort/availability và Gantt/portfolio nâng cao (My Work/Team Board/WIP cơ bản đã ở P0), referral nhẹ, health/NPS và một closed-loop CRM→Meta đã PoC; AI draft/STT khi đo đạt. P2: Mini App/loyalty, strategy editor đầy đủ, experiment engine, multi-touch, predictive scoring và scorecard nhân sự. FR guard tiền/quyền/consent/AI phải đạt trước bật chức năng tương ứng. HRM/payroll, retail inventory và hồ sơ y tế là pack/tích hợp riêng qua dự án có phạm vi, dữ liệu và đánh giá tuân thủ riêng.

### 9.8 Gate Omnichannel và kế hoạch lựa chọn nền tảng

Đợt triển khai cá nhân ưu tiên một nguồn lead và một kênh giao tiếp đã đủ quyền; không mặc định bật cùng mailbox/OA/Facebook. Sau pilot mới mở toàn đội và kênh còn lại. Mục tiêu năm kênh không đồng nghĩa cả năm phải bật dù chưa được provider cấp quyền. Ngày 1–15 kiểm kê tài khoản, quyền, khoảng lịch sử, consent, demo inbound/outbound và 3 lựa chọn nền tảng. Ngày 16–30 xây/đấu nối foundation identity/event/inbox và pilot. Ngày 31–60 bổ sung kênh đủ quyền, routing, lead/deal và handoff. Ngày 61–75 fault tests, security, training. Ngày 76–90 cutover theo nhóm và hypercare. Mốc phụ thuộc app review phải ghi riêng trong critical path.

So sánh PoC ba hướng: (A) CRM hiện hữu tùy biến như Espo/Frappe với adapter; (B) core CRM riêng và inbox engine Chatwoot; (C) SaaS được kiểm chứng quyền năm kênh. Chưa chọn sản phẩm chỉ từ website. Mỗi phương án phải chạy cùng fixtures, đo chi phí nâng cấp, quyền, export dữ liệu và thao tác thực tế; không cộng tổng số tính năng để che một lỗi cách ly dữ liệu.

### 9.9 UAT bổ sung cho Omnichannel

| ID | Kịch bản và dữ liệu thử | Kết quả Đậu; nếu sai là Rớt |
| --- | --- | --- |
| OC01 | Một tin gửi 10 webhook giống nhau | Một message, một routing effect; log dedup đầy đủ |
| OC02 | Hai Page có cùng chuỗi subject ID, khác người | Hai identities; không gộp Contact tự động |
| OC03 | Hai client workspace dùng cùng email khách | Không đọc chéo hoặc merge chéo; search không leak snippet |
| OC04 | Hai nhân viên claim đồng thời | Một người thành công; người còn lại nhận conflict, không ghi đè |
| OC05 | Double-click send và retry request của browser | Một intent với cùng Idempotency-Key; khác body bị từ chối |
| OC06 | Provider nhận tin nhưng API timeout | unknown_outcome; không tự tạo tin thứ hai; operator có đối soát |
| OC07 | Read event đến trước delivered event | Không lùi trạng thái; giữ event ledger; không tự suy read nếu không có |
| OC08 | Token hết hạn rồi kết nối lại sau 2 giờ | Cảnh báo, checkpoint resume; tin hết hạn không bị gửi bù trái policy |
| OC09 | Import lịch sử 30 ngày | Timeline có nhãn lịch sử; không tạo SLA live/campaign/lead lặp |
| OC10 | Autoack trong 1 giây, người thật sau SLA | Autoack không che vi phạm first-human-response |
| OC11 | Private note chứa thông tin giá vốn | Không tạo outbound; khách không thấy qua API/attachment/share |
| OC12 | Merge nhầm rồi undo sau có message mới | Khôi phục links có review, không mất message và audit |
| OC13 | Email reply-all với CC/BCC và HTML nguy hiểm | Preview đúng recipients; không lộ BCC, không thực thi script |
| OC14 | Attachment có mã độc/URL hết hạn | Quarantine/chặn tải; renew URL cần quyền hiện tại |
| OC15 | TikTok account không được cấp messaging | UI pending/unsupported; không báo đã đồng bộ hoặc dùng scraping |
| OC16 | Facebook reply ngoài điều kiện gửi hợp lệ | Block có lý do; chỉ dùng phương thức khác khi đủ điều kiện |
| OC17 | Khách rút marketing consent khi intent đang queue | Recheck trước gửi, cancel/blocked; không làm mất ticket dịch vụ hợp lệ |
| OC18 | Sales nghỉ việc, còn thread/Deal đang mở | Revoke access, bàn giao, không đổi hoa hồng vô căn cứ |
| OC19 | Restore DB có send intents cũ | Đối soát trước resume, không phát lại hàng loạt; audit restore |
| OC20 | Người dùng yêu cầu AI đọc hồ sơ workspace khác qua chat | Bị chặn ở retrieval/tool policy; không chỉ dựa prompt |
| OC21 | Provider không cho backfill khoảng mất kết nối | Báo gap và coverage đúng, không tuyên bố 100% dữ liệu |
| OC22 | Form spam/replay, email chưa xác minh | Chống trùng/rate limit; chưa auto-merge hoặc consent marketing |
| OC23 | Sales trả lời từ console chính thức của kênh | Nếu hỗ trợ echo thì reconcile; nếu không, công bố gap và quy chế xử lý |
| OC24 | Nâng version marketing pack cùng pack ngành thử | Không trùng namespace/migration/quyền; thất bại thì chặn release |

Điều kiện go-live: toàn bộ test cách ly, gửi nhầm, duplicate, consent, private note và DR phải đậu; các kênh còn chờ quyền phải có trạng thái và fallback được chủ nghiệp vụ chấp nhận. Bằng chứng UAT gồm dataset đã khử PII, build ID, API version, actual/expected, người kiểm và ngày. Tài liệu này là đặc tả kiểm thử, **chưa phải biên bản UAT đã chạy trên hệ thống**.

### 9.10 UAT tích hợp xuyên module phiên bản 1.3

Các ca sau bổ sung U01–24 và OC01–24, không thay test cũ còn áp dụng. Kết quả chưa chạy; mỗi ca có fixture/expected/actual/evidence/owner. P0 của luồng đã bật phải qua trước go-live.

| Mã | Tình huống phân biệt đúng/sai | Kết quả bắt buộc | Trace |
| --- | --- | --- | --- |
| INT01 | Lead Ads/webform vào lặp rồi lịch sử backfill | Một effect live; backfill không nurture/khởi SLA mới; source ID giữ | UC01/17, FR33 |
| INT02 | Hai người dùng hotline, contact đại diện nhiều công ty | Không merge/credit/share trái scope; Unknown có review | FR01/02/31/29 |
| INT03 | Sales từ chối vì hết capacity | Không gọi là lead rác; re-route có owner và giữ thời gian | FR04/05/28 |
| INT04 | Một contact đang hỏi giá và khiếu nại | Gọi hỏi giá không dừng SLA complaint; liên kết đúng request | FR36/39 |
| INT05 | Đã trả lời đầu, khách gửi 5 tin tiếp; agent chuyển ca | NRT từ tin chưa đáp đầu, không trượt hạn, promise được bàn giao | FR35/36 |
| INT06 | Hết quota nhưng đầu ra không đúng SOW | Nhận defect, không ép mua vòng sửa, giữ evidence | FR15/18/25 |
| INT07 | Khách chậm duyệt khi ngày sự kiện cố định | Ghi waiting/risk; không tự dời cam kết hoặc cộng trùng delay | FR15/20/25 |
| INT08 | Quote không giảm giá nhưng đổi credit term | Review đúng chiều rủi ro; bản approved cũ không đổi | FR14/15/21 |
| INT09 | MSA có hai SOW, replay handoff một SOW | Hai project hợp lệ; replay không tạo thứ ba | UC06, FR15 |
| INT10 | Tiền đã xác thực chưa có invoice trong CRM | Tiền tồn tại, match/allocation theo nghĩa vụ, invoice due còn theo dõi | FR16 |
| INT11 | API và sao kê cùng một khoản; hai khoản thật giống nhau | Hai evidence một payment khi đủ chứng minh; không bỏ khoản thật vì fingerprint | FR16/38 |
| INT12 | Hai worker phân bổ cùng số dư; invoice đến sau | Không vượt số dư; không tăng cash/commission khi link invoice | FR16/17 |
| INT13 | Đợt đầu chỉ thu media, sau đó refund service | Base service theo kỳ đúng; refund đảo đúng phần một lần | FR16/17/26 |
| INT14 | Write-off, bank fee có chứng từ, discount | Loại điều chỉnh khác nhau; cash không tăng bởi write-off | FR16/17/28 |
| INT15 | Đổi owner sau payout, refund sau khóa kỳ | Giữ người hưởng lịch sử, payout và adjustment đúng policy | FR17/21 |
| INT16 | Cho kickoff nội dung, chưa cho chi media | Không tự mở quyền chi; exposure có hạn; spend ngoài app được phát hiện | FR15/23/26 |
| INT17 | Hai journey cùng cap; revoke sau enqueue | Không vượt cap trong scope đúng; dispatch chặn marketing đã rút quyền | FR09/34 |
| INT18 | Dataset khách B gắn nhầm lead khách A | Fail closed; payload không đi; lỗi có owner sửa | FR28/29/30/34 |
| INT19 | Khách trả trước năm, hợp đồng đang phục vụ | Không tự win-back vì payment recency lớn; health theo dữ kiện | FR03/09/15 |
| INT20 | First/last/platform attribution cùng claim outcome | Không cộng thành doanh thu thật; Unknown khác Direct; refund có version | FR28/29 |
| INT21 | Client approver NPS thấp, end-user CSAT cao | Hai metric/role giữ riêng; recovery và account review có owner | FR19/01 |
| INT22 | Một lỗi launch lặp ở nhiều khách | Corrective action chung nhưng dữ liệu khách còn cách ly; xác minh tái diễn | FR18/19/23/24 |
| INT23 | Bị revoke quyền khi tab/search/job còn mở | Kiểm lại send/export/download; snippet/count/AI không leak | FR08/13/35/37 |
| INT24 | Email spoof/forward file độc, internal note | Không auto-approve/merge; file quarantine; BCC/note không gửi ra | FR02/32/40 |
| INT25 | Provider đã nhận send rồi timeout | Unknown, reconcile/quyết định có dấu vết; không tự gửi lặp | FR34/38 |
| INT26 | Restore backup trước một revoke và payment mới | Phục hồi suppression/đối soát trước outbound; không nhân tiền/commission | UC11/13/21, NFR06/08 |
| INT27 | AI nghe nhầm “không phải 50 triệu” thành “50 triệu” | Field chưa xác minh không vào quote; source timestamp, người duyệt | FR11/12/14 |
| INT28 | Tệp khách chứa lệnh export/đổi tài khoản nhận tiền | Tool policy từ chối; nội dung tệp không đổi quyền/approval | FR13/37 |
| INT29 | Hai role allow/deny trên nền tảng ứng viên | Kết quả đúng policy được chốt, không mặc định từ tên RBAC | FR21/37 |
| INT30 | Hợp đồng notice 60 ngày, retainer ngắn hạn, one-off | Lịch theo điều khoản, không catch-up spam, không giả auto-renew | UC10, FR09/15 |

### 9.11 Nhịp điều hành và điều kiện ký nghiệm thu

| Nhịp | Việc cần quyết định | Đầu ra, không chỉ dashboard |
| --- | --- | --- |
| Hằng ngày | Lead/ticket/promise/next action trễ, handoff bị chặn, connector lỗi | Người xử lý, hành động tiếp, hạn và lý do ngoại lệ |
| Theo lượt đối soát | Tiền chưa khớp, invoice/cash lệch, refund/commission pending | Reconciliation case được giải thích và đóng đúng bằng chứng |
| Hằng tuần | Pipeline đủ fit, capacity, margin at risk, media funding, khách có rủi ro | Quyết định nhận/từ chối/dời việc, phê duyệt ngoại lệ giới hạn |
| Hằng tháng/kỳ review | Hiệu quả nguồn, chất lượng delivery, recovery, retention, chi phí | Thay đổi ngân sách/dịch vụ/quy trình có owner và kiểm chứng lần sau |
| Trước release/đổi policy | Quyền, migration, connector, timer, số tiền | UAT/rollback/restore được ký; không sửa rule production thiếu version |

Với cá nhân đây có thể là checklist ngắn. Không biến CRM thành thêm nhiều cuộc họp hoặc báo cáo trùng.

Một chức năng chỉ được coi đủ đặc tả khi có: mục tiêu/quyết định phục vụ; owner; actor và scope; trigger; precondition; dữ liệu đầu vào; state machine; success/exception; side effects và idempotency; quyền; audit; metric; UAT. Mỗi thay đổi có ADR/CR liên kết FR→UC→schema/API→test.

Gate trước go-live:

1. Chủ nghiệp vụ chốt scope P0 và giải quyết các mâu thuẫn trong CR01–12 của phần được triển khai.
2. Có bản dictionary/DDL/API versioned duy nhất; không để engineering tự suy từ bảng mô tả rút gọn.
3. Ca tiền/quyền/consent/SLA trọng yếu đạt trên môi trường đại diện; lỗi sai tiền, truy cập trái quyền hoặc gửi trái policy chưa xử lý là no-go. Các lỗi khác có mức độ và quyết định xử lý rõ.
4. Mỗi connector có bằng chứng capability/tài khoản/API version, owner, quota/error handling và đường xử lý thủ công khi mất kết nối.
5. Đối soát dữ liệu mẫu và restore diễn tập đạt; nguồn dữ liệu được nhập có quyền, mapping và retention rõ.
6. Người dùng pilot làm được công việc, đo thời gian/nhập trùng/lỗi; mục tiêu SLA thực sự có người đáp ứng.
7. Hóa đơn, thuế, bảo vệ dữ liệu, quyền sử dụng media, thưởng/hoa hồng và điều khoản khách đã được người có trách nhiệm xác nhận theo mô hình thực tế. Đây là gate nghiệp vụ, không phải tuyên bố đã hoàn tất kiểm toán pháp lý trong báo cáo này.

Dữ kiện còn thiếu để chọn cấu hình cuối: “50 khách/tháng” nghĩa gì; dịch vụ và mẫu hợp đồng; pháp nhân/tài khoản nhận tiền; kênh/API hiện có; ERP/PMS; chính sách commission/cost; ngân sách và người bảo trì. Những dữ kiện này không ngăn rà soát thiết kế, nhưng ngăn kết luận có căn cứ rằng một sản phẩm cụ thể là tốt nhất.

### 9.12 Ca nghiệm thu chuyên sâu theo vai trò

76 ca chuyên đề sau có giao nhau với bộ INT; không tính như các bằng chứng độc lập hoặc kết quả đã pass. Chọn ca theo module/giai đoạn triển khai, đối chiếu và gộp test case ID khi lập test plan.

#### Tài chính và CEO

| ID | Tình huống | Kết quả đạt | FR |
| --- | --- | --- | --- |
| CEO-U01 P0 | Cost chưa nhập hoặc hết hiệu lực | Không hiển thị biên 100%; yêu cầu xác nhận/review đúng quyền | 14,26,28 |
| CEO-U02 P0 | Quote đã approved, sửa SOW hoặc lịch trả | Approval ảnh hưởng mất hiệu lực; bản cũ không bị viết đè | 14,15 |
| CEO-U03 P0 | Người liên hệ chấp thuận nhưng không có quyền nghiệm thu | Giữ evidence; không tự chuyển accepted khi chưa đủ thẩm quyền | 01,15,21 |
| CEO-U04 P0 | Hợp đồng khung có hai SOW; replay handoff của một SOW | Hai gói delivery hợp lệ; replay không tạo bản thứ ba | 15,25 |
| CEO-U05 P0 | Chỉ được duyệt kickoff sáng tạo, chưa duyệt chi media | Cho đúng phần công việc; không mở ngân sách quảng cáo ngoài quyền | 15,23,26 |
| CEO-U06 P0 | Tiền xác thực nhưng chưa biết hóa đơn/chủ thể | Tiền vẫn tồn tại confirmed; case match mở; không tạo commission vô căn cứ | 16,17 |
| CEO-U07 P0 | Cùng giao dịch xuất hiện qua bank API và file sao kê | Hai evidence, một payment canonical; không tăng thực thu hai lần | 16 |
| CEO-U08 P0 | Hai giao dịch thật cùng ngày/số tiền/nội dung | Không tự bỏ một giao dịch chỉ do fingerprint | 16 |
| CEO-U09 P0 | Hai worker phân bổ 70 triệu từ cùng số dư 100 triệu | Không commit tổng 140 triệu; transaction thua nhận conflict/retry rõ | 16 |
| CEO-U10 P0 | Phân bổ payment của pháp nhân A sang nghĩa vụ pháp nhân B | Chặn hoặc đi nghiệp vụ hợp lệ riêng; không sửa scope để lách | 16,21 |
| CEO-U11 P0 | Invoice đến sau khoản ứng trước đã phân bổ | Mapping cập nhật; cash và commission không nhân đôi | 15,16,17 |
| CEO-U12 P0 | Hợp đồng service/media, kỳ đầu chỉ thu media | Commission service bằng 0 hoặc pending theo dữ kiện; không pro-rata tùy tiện | 16,17 |
| CEO-U13 P0 | Refund một phần service sau payout; callback replay | Đảo đúng phần một lần; giữ payout cũ và adjustment theo quy chế | 16,17 |
| CEO-U14 P0 | Write-off 1 triệu thay vì khách thực trả | AR giảm theo ERP nhưng cash-based commission không tăng | 16,17,28 |
| CEO-U15 P0 | Đổi Sales/chi nhánh giữa dự án | Không tự chuyển quyền hưởng lịch sử; handoff task/ticket/ACL có audit | 17,21 |
| CEO-U16 P0 | Quality chưa có và kỳ trả tới hạn | Hiện pending theo policy; không mặc định factor=1 | 17,18,19 |
| CEO-U17 P0 | Client workspace user mở link hợp đồng/commission agency | Chỉ truy cập phần đã được publish/grant; chặn dữ liệu nội bộ | 15,17,21 |
| CEO-U18 P0 | Thu hồi quyền sau khi job export đã xếp hàng | Recheck tại execution/download; không xuất nhờ snapshot quyền cũ | 21 |
| CEO-U19 P0 | Khách chậm feedback nhưng ngày khai trương cố định | Ghi thời gian chờ/rủi ro; không tự dời cam kết | 15,20,25 |
| CEO-U20 P0 | Hết quota sửa nhưng deliverable lỗi so với SOW | Đi quy trình defect; không tự bắt mua thêm vòng sửa | 15,18 |
| CEO-U21 P0 | Hai booking đồng thời cho một ekip độc quyền | Chỉ một reservation hợp lệ; hold hết hạn nhả tài nguyên | 20,25 |
| CEO-U22 P0 | Chuyển committed cost thành actual | Tổng forecast cost không cộng trùng; truy được nguồn | 26,28 |
| CEO-U23 P0 | Kỳ tài chính đã khóa, ERP điều chỉnh sau | Adjustment kỳ cho phép + lịch sử, báo cáo đã công bố truy được | 16,17,28 |
| CEO-U24 P0 | Khách dispute invoice và automation đang nhắc nợ | Route theo policy; không xóa nợ, không gửi nội dung sai/ngược lịch xử lý | 07,09,16,18 |
| CEO-U25 | Retainer hủy giữa kỳ hoặc rollover chưa dùng | Kết quả theo đúng điều khoản version, không pro-rata/rollover ngầm | 15,16,28 |
| CEO-U26 P0 | Restore DB rồi replay payment/invoice/outbox | Không tạo thêm cash, commission, project hay thông báo đã gửi; reconciliation còn thực hiện được | 15,16,17 |

#### Marketing và CMO

Mã CMO-U01–CMO-U26 thay tên cũ M01–M26 để phân biệt với mã module M01–M20; nội dung ca không đổi.

| Mã | Tình huống | Kết quả phải đạt |
| --- | --- | --- |
| CMO-U01 | Khách B2B hiện hữu nảy sinh nhu cầu mới | Quan hệ Customer được giữ; demand/deal mới có lineage, không tính khách mới lần hai |
| CMO-U02 | Sales từ chối vì hết capacity | Reason no-capacity; không cộng vào invalid lead; trưởng nhóm có hành động điều phối |
| CMO-U03 | Lead chuyển MQL→Recycle→MQL | Không đếm acquisition lead mới; giữ hai episode chuyển trạng thái và thời gian từng lần |
| CMO-U04 | Contact đại diện hai account | Touchpoint chỉ credit deal có liên kết hợp lệ, không lan toàn bộ doanh thu hai công ty |
| CMO-U05 | Khách trả trước năm, vẫn đang phục vụ | Không auto win-back/dormant chỉ do R>90; hiển thị hợp đồng/period paid đúng |
| CMO-U06 | Một hóa đơn thanh toán ba đợt | Cash đủ ba khoản nhưng purchase/service frequency không tăng thành ba |
| CMO-U07 | Hai journey đồng thời, cap 2/7 ngày | Tổng marketing sends trong scope không vượt cap; có lý do defer/suppress |
| CMO-U08 | Rút consent lúc đang chờ gửi | Dispatch kiểm lại và hủy bước marketing chưa gửi; audit giữ policy decision |
| CMO-U09 | Retry event 10 lần | Một send effect và một canonical outcome, nhiều attempt logs nếu cần |
| CMO-U10 | Ticket nghiêm trọng đang mở | Upsell bị chặn/AM review; cập nhật xử lý ticket vẫn hoạt động theo mục đích phù hợp |
| CMO-U11 | Creative approved v1, sửa offer v2 | Không dùng approval v1 cho v2; người duyệt có đúng authority |
| CMO-U12 | Điều chỉnh nhỏ trong hạn mức tối ưu đã duyệt | Lưu audit; không bắt duyệt lại phần không chịu tác động |
| CMO-U13 | Logo đơn lẻ không có ads | Gate không đòi tracking pixel; vẫn có scope, asset version, acceptance |
| CMO-U14 | Khách chờ duyệt 5 ngày | Client-wait và forecast đổi có lịch sử; contractual deadline không âm thầm đổi |
| CMO-U15 | Lỗi do agency phải sửa | Ghi defect/rework, không tự trừ quota change request của khách |
| CMO-U16 | Commitment 100, actual 40 | Outstanding commitment 60; tổng exposure không thành 140 |
| CMO-U17 | Sửa cost rate hiện tại | Chi phí kỳ đã chốt giữ snapshot; thay đổi hồi tố cần adjustment/restate |
| CMO-U18 | Agency spend 20, client media 300 | CAC agency chỉ dùng cost đủ điều kiện agency, không 320 |
| CMO-U19 | UTM mất do lỗi và truy cập Direct thật | Hai bucket/phân loại riêng; data quality issue không biến thành Direct |
| CMO-U20 | Một outcome được Meta và Google cùng claim | CRM không cộng hai platform totals thành doanh thu thật |
| CMO-U21 | Refund một phần sau đóng kỳ | Delta revenue/referral/credit theo policy, giữ snapshot báo cáo cũ |
| CMO-U22 | Connector Meta bị gán nhầm dataset khách B cho khách A | Fail closed trước gửi; có lỗi cấu hình để admin sửa; không lộ payload A |
| CMO-U23 | Won chưa trả tiền | Won event và cash event khác; không gửi Paid hoặc tính thưởng đủ điều kiện nếu chưa có cash |
| CMO-U24 | A/B có 8 observations mỗi nhóm | Hiển thị sample/uncertainty; không tự tuyên bố winner đủ tin cậy theo rule chưa đạt |
| CMO-U25 | Spend API ngừng cập nhật | Freshness Degraded/Unknown; không hiển thị campaign health xanh mặc định |
| CMO-U26 | Có referrer nhưng khách đã tồn tại | Kiểm new-customer policy và dispute; không tự thưởng chỉ vì nhập mã referral |

#### Dịch vụ và CX

| UAT | Tình huống | Kết quả bắt buộc |
| --- | --- | --- |
| CX-U01 | Cùng người đại diện hai doanh nghiệp; agent chỉ được một bên | Không lộ deal, ticket, note, số lượng hay attachment bên kia. |
| CX-U02 | Hai người dùng chung hotline; một người đổi công ty | Không tự merge; role cũ kết thúc đúng hiệu lực; lịch sử giữ phạm vi cũ. |
| CX-U03 | Khách gửi 5 tin trước khi agent trả lời | Next-response due tính từ tin đầu chưa được trả lời, không bị trượt mỗi lần có tin mới. |
| CX-U04 | Bot chào, agent private note, rồi chuyển nhóm | Human-response timer vẫn chạy; chuyển nhóm không reset. |
| CX-U05 | Một khách hỏi giá và khiếu nại đồng thời | Hai work item liên kết; trả lời hỏi giá không hoàn thành SLA khiếu nại. |
| CX-U06 | Agent đã hứa cập nhật 15:00 nhưng chưa có lời giải | Đến 15:00 vẫn phải cập nhật tiến độ; resolution clock giữ đúng policy. |
| CX-U07 | Agent đặt pending_internal hoặc đổi priority sau breach | Không xóa vi phạm cũ; pause/hạn mới có lý do, version và audit. |
| CX-U08 | Một provider message đến trễ sau outage | occurred/received giữ nguyên; provider delay thấy được; không quy tất cả lỗi cho agent hoặc che thời gian khách chờ. |
| CX-U09 | Người cũ đang soạn khi cuộc hội thoại chuyển ca | Gửi từ tab cũ bị kiểm version; agent mới có handoff note và due hiện hữu. |
| CX-U10 | Khách hết revision quota nhưng deliverable sai SOW | Tiếp nhận/triage bình thường; phân loại lỗi và xử lý theo cam kết, không ép mua CR. |
| CX-U11 | Yêu cầu thêm ngoài SOW | CR ghi chi phí/lịch/phê duyệt; không làm mất ticket source và không đổi hợp đồng âm thầm. |
| CX-U12 | Phàn nàn lộ tài sản, chưa xác minh Contact | Intake khẩn có owner; xác minh vừa đủ; không tiết lộ dữ liệu, không bỏ qua containment. |
| CX-U13 | Close event replay; reopen trước survey gửi | Một survey hợp lệ; policy hoãn/hủy có reason; score cũ không bị thay. |
| CX-U14 | NPS 2/10 của approver, user khác cho CSAT 5/5 | Hai nguồn/metric/role tồn tại độc lập; recovery phù hợp; không lấy trung bình để tuyên bố khỏe. |
| CX-U15 | Khách từ chối callback | Không tự gọi tiếp; chọn kênh/cách phục hồi hợp lệ và ghi lý do. |
| CX-U16 | Remedy cần refund vượt hạn mức AM | Yêu cầu phê duyệt tài chính; chưa tạo hoàn tiền hoặc hứa chắc trước approval. |
| CX-U17 | Một lỗi launch xuất hiện ở nhiều Account | Gộp theme, tạo corrective action, owner, kiểm tra tái diễn; không gộp dữ liệu khách vượt phạm vi. |
| CX-U18 | Hợp đồng yêu cầu báo gia hạn trước 60 ngày | Reminder dựa notice deadline; 45 ngày không dùng cứng. |
| CX-U19 | Kết thúc hợp đồng đang có dispute công nợ | Bàn giao/thu hồi đúng quyền/hợp đồng; không xóa bằng chứng hoặc tự khóa tài sản của khách. |
| CX-U20 | Consent bị rút sau enqueue; Contact vừa merge | Policy tại send chặn đúng purpose/endpoint; suppression còn hiệu lực sau undo. |
| CX-U21 | Chuyển nhân sự, có scheduled send và approval pending | Tất cả work item được bàn giao/hold có owner; actor lịch sử không bị xóa. |
| CX-U22 | CRM đọc bình thường nhưng Page đã mất scope gửi | Registry degraded; UI giải thích lỗi; không báo delivered, không tự đổi sang kênh khác. |
| CX-U23 | Một conversation có hai ticket, ticket A resolved | Chỉ clock thuộc A dừng; ticket B vẫn hiển thị due và owner. |
| CX-U24 | Bảng health thiếu deliverable và survey mới | Unknown/data stale xuất hiện; không mặc định xanh hoặc tự upsell. |

### 9.13 Nghiệm thu bổ sung sau phản biện vòng hai

Các ca dưới là đặc tả chưa chạy trên sản phẩm/DB/provider. Số liệu Decimal trong F.4 là phép kiểm logic độc lập, không thay bằng chứng tích hợp. Ca quyền/tiền/pháp lý của feature được bật là gate trước go-live.

| ID | Tình huống | Kết quả bắt buộc |
| --- | --- | --- |
| RV01 | Link thread với Deal/Project/Deliverable và nhiều request | Đúng type/FK/scope; có link không tự tạo mọi SLA hoặc mở quyền đọc |
| RV02 | Deal Negotiation hoãn rồi trở lại, review quá lâu | Stage giữ nguyên, hold history khớp; escalate không Lost giả |
| RV03 | Draft/evergreen/notice theo60ngày và đổi terms | Constraint theo lifecycle; reminder kịp notice, không default offsets sai basis |
| RV04 | Hold booking hết hạn chưa sweep, hai người confirm | Confirm recheck/release, chỉ một booking hợp lệ; [end,start kế] không overlap; resource pool đúng capacity |
| RV05 | Outbound sau inbound, CTA tương tác và backfill cũ | Reply không kéo window; eligibility theo provider/event class, không24hchung |
| RV06 | Termination còn phí tối thiểu và invoice đã phát hành | Settlement giữ nghĩa vụ hợp lệ; adjustment/credit evidence, không void/xóa nợ mù |
| RV07 | Phí ngân hàng có evidence và payer thực sự trả thiếu | Loại xử lý khác nhau, approval đúng, cash-based base theo policy không bị write-off làm tăng |
| RV08 | Hoàn dư song song với allocate và provider timeout | Reservation/lock không chi/phân bổ vượt; confirmation đúng một effect; unknown không nhả mù |
| RV09 | Amount3VND, năm share0,6VND và caps khác nhau | Tổng3, không âm, cap đúng, tie-break tái lập; không sai tax/dòng để bù |
| RV10 | Cross-workspace cùng tenant nhưng khác khách; đổi Contract buyer sau grant | Chặn link sai cả insert/update; không chỉ kiểm một lần bằng CHECK function |
| RV11 | Signed read/status/spam và inquiry có consent | Không tạo Contact cho mọi event; promote nghiệp vụ cần FK có Contact hợp lệ, evidence không mất |
| RV12 | Ownership40/35/25, provider outage, bàn giao sát hạn | Không autoquy lỗi50%; giữ intervals/owner/cause; clock khách không reset |
| RV13 | Placeholder reply chọn waitingcustomer nhưng việc vẫn nội bộ | Không coi state chọn là bằng chứng chất lượng; còn due/update, QA và escalation |
| RV14 | Pending intent trước hạn được tạo liên tục | Không giữ lead vô hạn hoặc sửa breach; aggregate version/dispatch/reassign nhất quán |
| RV15 | Hai tenant dùng cùng pooled connection, rollback/savepoint/missing context | Default-deny, không rò session baseline; job/query không đi ngoài context contract |
| RV16 | Các loại privacy request, xác minh trễ và breach xác nhận muộn | Response/action/notification theo policy/căn cứ; không reset due khi verified/confirmed |
| RV17 | Revoke commit khi intent queue/inflight; vendor có no-train nhưng có logs | New dispatch bị chặn; inflight audit/reconcile; retention được đánh giá riêng, không tuyên bố ZDR giả |
| RV18 | Production cost đổi sau quote/thu một phần, quality survey không trả lời | Basis/pool/version đúng; preview/holdback/true-up theo quy chế; không autoqualify14ngày |
| RV19 | Score100coverage60%, CPLtarget100actual150, tickets cùng incident | Coverage/direction/dedup đúng; không xanh giả, không weight chưa approved |
| RV20 | Tắt featureP1 có FK/table dependency; seed thứBảy/selfdiscount/480phút | Dependency closure có mapping/nullability hợp lệ; configDraft không đổi lịch/quyền production |

### 9.14 Nghiệm thu các hợp đồng BA đã hợp nhất

Các ca dưới đã là yêu cầu kiểm thử hiện hành, không còn là patch chờ dán. Actual/evidence chưa có; QA thực thi theo release profile tại9.5.

| ID | Tình huống | Kết quả bắt buộc |
| --- | --- | --- |
| WF-U01 | Inbound hợp lệ chưa biết B2B/B2C, sau đó xác nhận người mua | Một Lead Unknown có owner/queue/timer; không Account giả; convert bị chặn trước phân loại, sau xác nhận convert đúng một effect |
| WF-U02 | Thread có khiếu nại A và báo giá B; reply B, rồi reply A+B; receipt trùng | Reply B không dừng clock A; reply A+B chỉ dừng clock đạt criterion; target ngoài quyền bị chặn; replay không lặp completion/history |
| WF-U03 | Chuyển hợp lệ/trái phép/replay/concurrent cho từng đối tượng bật trong release | Guard và effect đúng bảng transition đã duyệt; không sửa tự do status. Deal reopen không sinh lại cash/project; Blocked không dời cam kết; Completed chưa Paid còn công nợ; pause/reopen giữ đúng breach |
| WF-U04 | Profile chỉ cash thủ công + một inbox; sau đó bật launch/referral/AI | Test áp dụng và N/A có căn cứ; bật feature tự yêu cầu control liên quan trước activation, không bỏ qua U19/U23 vì nhãn cũ |
| WF-U05 | Hai event ID khác cùng request; hai lệnh convert khác HTTP key cùng intent; nhu cầu có hai cơ hội thật | Một FRT/episode/type và một Deal cho cùng intent; hai intent hợp lệ có hai Deal; reassign không thêm clock; reopen có lineage tới episode trước |
| FA01 | Quote/line dùng snapshot A; policy version B có hiệu lực sau thu tiền hoặc owner đổi | Ledger cũ giữ A và người hưởng cũ; dòng chưa khóa policy vào PendingPolicy; FK đích tồn tại đúng scope, không trỏ bảng alias chưa định nghĩa |
| FA04 | Receipt100, allocated100; reserve allocated refund20; đồng thời lệnh allocate/reverse khác | Available vẫn0, không−20; phần20 đã reserve không được dùng lại. Confirmed refund làm R=20/A=80; available0; replay không nhân refund/reversal |
| FA05 | Receipt100 chưa allocated, không có Contract, reserve hoàn20 và allocate90 đồng thời | Chỉ kết quả giữ bất biến được commit; refund hợp lệ không cần Contract giả và không sinh commission negative giả; Unknown không tự nhả khi hết TTL |
| FA02 | T1 chuẩn bị post, T2 close-period cùng kỳ; đổi thứ tự lấy lock hai lần | Chỉ một thứ tự commit hợp lệ: post trước rồi close có đối soát, hoặc close trước làm post từ chối/route adjustment kỳ mở; không có entry chèn vào kỳ đã đóng |
| FA03 | Allocation đã commit nhưng consumer commission còn pending ở cutoff | Close kiểm watermark và xử lý/ngoại lệ có audit; event tới muộn không âm thầm post về kỳ đóng; kỳ khác pháp nhân không chặn hoặc nhận nhầm entry |
| FA06 | Import/API gửi NaN/Infinity, số vượt range hoặc amount VND phân số không được policy cho phép; currency chưa bật | Từ chối trước cast/post với mã lỗi rõ; không tạo ledger NaN hoặc silently round. Giá/rate trung gian hợp lệ vẫn được tính bằng Decimal rồi round đúng bước; currency chưa supported không bị nhận chỉ vì char(3) hợp lệ |
| SEC-U01 | Callback khác phiên/scope/provider, callback replay; reconnect chọn account khác | Reject, không sửa connection/token hiện hữu; account/scopes được xác minh trước Active. Provider không hỗ trợ cơ chế yêu cầu phải có flow thay thế đã review, không tắt kiểm tra. |
| SEC-U02 | Đồng thời activate cùng Page/OA/mailbox vào hai CLIENT workspace, rồi reconnect/move account; gửi ID/key target ngoài quyền | Một activation thắng; activation còn lại conflict rõ nhưng không lộ owner/workspace ngoài quyền. Không nhập hai bản event khác scope; move có quy trình, lịch sử giữ scope gốc; lỗi FK/unique không trả raw DETAIL. |
| SEC-U03 | Cấp link file nhạy cảm, revoke user/grant, thử GET/Range/link copy không session | Request mới bị từ chối; cache không trả nội dung. Tài liệu publish chỉ đọc qua share grant riêng còn hiệu lực. |
| SEC-U04 | URL localhost/metadata/private IPv4+IPv6, redirect từ host hợp lệ sang private, DNS đổi IP và file quá cỡ | Không chạm đích mạng bị cấm/không lộ token; quarantine hoặc reject có audit metadata; worker tiếp tục xử lý event hợp lệ. |
| SEC-U05 | Unsubscribe qua body/header/provider khi journey đang đợi; hard-bounce/complaint trùng rồi import lại | Marketing không gửi tiếp; không lộ hồ sơ hoặc đòi login; không tự hồi sinh endpoint khi import. Soft bounce tuân retry/expiry; provider/sender authentication đạt trước bật gửi. |
| SEC-U06 | Admin connector tự gán role Finance, manager cấp quyền ngoài branch, user tự thêm team, tự kéo dài break-glass | Từ chối nếu thiếu grant authority/approval; grant hợp lệ có TTL/actor/evidence. Test bản pilot một owner và bản nhiều user với separation khác nhau. |

### 9.15 Nghiệm thu bổ sung từ nghiên cứu Omnichannel ngày 16/10/2026

**[Đề xuất bổ sung — CR-OMNI-20261016]** Các ca dưới chưa được chạy. Bằng chứng nghiệm thu phải có account/API version, policy version, request/response đã che bí mật, trace_id, DB invariant và kết quả UI. Không coi tài liệu tính năng vendor là kết quả PoC.

| ID | Kịch bản | Kết quả bắt buộc |
| --- | --- | --- |
| OM-G01 | Zalo qua mốc 48 giờ nhưng còn trong eligibility OpenAPI đã verified | Không block chỉ do quá 48 giờ; tính phí/entitlement theo policy; thiếu budget thì chặn phần gửi có phí |
| OM-G02 | Telegram valid secret, event lặp, edit cùng message ID, hai chat cùng message ID | Verifier không đòi HMAC chung; dedup event đúng, edit không bị mất, khác chat không va khóa |
| OM-G03 | Hai router cạnh tranh slot cuối; hai người claim cùng thread | Capacity reservation và assignment nhất quán, không vượt tải; một claim thắng |
| OM-G04 | Merge contact khi đang gọi/chat; người xem chỉ có quyền một Page | Giữ call/thread/recipient; không mở ACL, snippet/count/file của Page còn lại |
| OM-G05 | Reply-all và BCC; email cùng subject không liên quan | Preview đúng recipients; BCC không kế thừa/lộ; subject không tự gộp |
| OM-G06 | Quick reply ngoài window hoặc thiếu biến | Không tự gửi/bypass; hiển thị lỗi và giữ draft |
| OM-G07 | Browser mất mạng; CDR đến trước recording | Presence và call outcome tách; recording pending/unavailable phản ánh thực tế |
| OM-G08 | Provider nhận send rồi timeout; callback READ trước response | Unknown không retry mù; reducer không lùi trạng thái; SLA không complete trùng |
| OM-G09 | Resolve đồng thời inbound; backfill sau resolve | CAS không làm mất nghĩa vụ mới; historical event không tự reopen live |
| OM-G10 | Kết nối vendor inbox đồng bộ hai chiều assignment/echo | Có một nguồn chuẩn từng trường, không vòng lặp đổi owner hoặc cộng KPI hai lần |

Bộ ca chi tiết bổ trợ OM-R01–32 và tám UC trong báo cáo `docs/OMNICHANNEL_AUDIT_RESEARCH_2026-10-16.md` phục vụ review; các gate và FR của Master là nguồn chuẩn khi triển khai. Capability chưa verified, policy chưa rõ, retention chưa chốt hoặc không có cơ chế xử lý unknown send là điều kiện chặn bật chức năng liên quan.

### 9.16 Nghiệm thu Work Management và rollout 1.7

CR-WORK-20261016 thêm scope nghiệp vụ, không xác nhận ngân sách/effort hoặc go-live. Trình tự: pilot cá nhân → một team có reviewer → nhiều team/dự án; lựa chọn nguồn ghi CRM/PMS phải xong trước migration. NFR theo 7.7, cấu hình còn mở tại A.6. Các ca dưới là yêu cầu kiểm thử, chưa có kết quả Pass.

#### 9.16.1 Bộ test W-T01–40

| ID | Kịch bản | Expected result |
| --- | --- | --- |
| W-T01 | Tạo personal task không có khách/project | Hợp lệ; My Work hiển thị, không tạo Account/Contract giả |
| W-T02 | Giao task record khách A cho người chỉ có scope khách B | Reject; không leak title/context qua notification |
| W-T03 | Hai người claim cùng task trong queue | Một accepted assignment; người còn lại 409 |
| W-T04 | Double submit create với cùng key | Một task; key cùng payload replay, khác payload 409 |
| W-T05 | Broadcast cho user trùng trong nhiều nhóm | Dedup người nhận theo batch snapshot; task riêng đúng từng người |
| W-T06 | Decline offer hoặc hết hạn nhận | Về queue có manager, giữ giao lần đầu và reason |
| W-T07 | Revoke assignee sau khi mở form trước submit | Backend chặn thao tác, không dựa UI cached permission |
| W-T08 | @mention người ngoài scope | Không tự grant; không gửi snippet nhạy cảm |
| W-T09 | Watcher sửa owner hoặc deadline bằng API | 403 dù xem được task |
| W-T10 | Kéo card vào cột tên Done nhưng chưa review | Không vượt lifecycle guard; không tự completed |
| W-T11 | Hai approval gia hạn dựa cùng version | Một decision áp dụng; decision còn lại conflict |
| W-T12 | Gia hạn sau deadline đã breach | Due mới có hiệu lực; baseline/breach lịch sử còn nguyên |
| W-T13 | Snooze reminder | Không đổi due/committed_due/SLA |
| W-T14 | Submit thiếu checklist bắt buộc/file chưa clean | 422; không InReview/Done |
| W-T15 | Sửa result khi reviewer đang approve | Submission version guard; không duyệt nhầm bản mới |
| W-T16 | Reviewer tự là assignee ở task cần tách người | Chặn hoặc override explicit có authority/audit |
| W-T17 | Approve callback/job gửi lặp | Một completion effect/notification intent |
| W-T18 | Task Done nhưng client chưa acceptance | Deliverable chưa tự Accepted; chưa kích thanh toán sai |
| W-T19 | Parent Done còn child bắt buộc mở | Chặn; không tự hoàn tất child |
| W-T20 | Reopen child dưới parent Done | Chặn hoặc atomic reopen-family có preview, không âm thầm inconsistency |
| W-T21 | A→B và B→A tạo đồng thời | Không commit cả hai; graph không cycle |
| W-T22 | Cancel predecessor | Successor không tự được phép bắt đầu nếu chưa có waiver |
| W-T23 | Reopen predecessor khi successor đã InProgress | Cảnh báo at-risk, giữ work history, không xóa tiến độ |
| W-T24 | Scheduler chạy lại cùng occurrence sau crash | Một task/occurrence; không double notify |
| W-T25 | Calendar recurrence khi tuần trước chưa xong | Kỳ mới theo policy, báo backlog; không mất kỳ |
| W-T26 | Completion recurrence khi kỳ trước bị canceled | Không tự tạo kỳ mới mặc định; cần quyết định resume |
| W-T27 | Lịch ngày 31, leap year, timezone/DST khác | Preview và materialization thống nhất với policy |
| W-T28 | Scheduler gián đoạn 100 kỳ | Catch-up theo rule, ghi missed occurrences; không tạo storm vô kiểm soát |
| W-T29 | Assignee nghỉ việc còn task/review/template | Revoke, chuyển queue/successor cả các rule tương lai; actor cũ giữ |
| W-T30 | Capacity có parent summary và subtasks | Không tính effort hai lần; NULL estimate hiện unknown |
| W-T31 | Available minutes bằng 0 | Unavailable, không chia 0 hoặc giả capacity vô hạn |
| W-T32 | PMS từ chối due mới/parent closed | Pending chuyển failed/conflict rõ; CRM không báo đã áp dụng |
| W-T33 | Sync echo hai chiều cùng phiên bản | Một effect, không vòng lặp update/task duplicate |
| W-T34 | Notification service down sau Task commit | Task vẫn tồn tại; retry thông báo idempotent |
| W-T35 | Task chưa Done nhưng quá due trong kỳ báo cáo | Nằm mẫu số due cohort; không biến mất vì chỉ đếm task hoàn thành |
| W-T36 | Private task trong dashboard/search/export team | Không lộ title/count/attachment ngoài chính sách đã chốt |
| W-T37 | Comment XSS/file giả MIME | Render an toàn/quarantine; không thực thi mã hoặc gửi file bẩn |
| W-T38 | Source record bị archive/delete giữa create/link | Kiểm FK/version; không dangling link; task giữ tombstone context theo retention |
| W-T39 | Đổi workflow/stage đang có task active | Mapping/version/migration có preview; không đổi nghĩa completed lịch sử |
| W-T40 | Offline draft cũ sync sau đổi owner | Conflict/permission check, không last-write-wins |

#### 9.16.2 Rủi ro và kiểm soát

| Rủi ro | Biểu hiện sớm | Kiểm soát thiết kế |
| --- | --- | --- |
| Task bị bỏ quên trong queue | Unassigned age tăng nhưng reminder cá nhân bằng 0 | Queue manager, acceptance deadline, escalation |
| Quá nhiều notification | Người dùng tắt tất cả thông báo | Digest cho thay đổi thường; real-time cho giao việc/review/escalation; preferences có policy |
| Càng chia nhỏ càng KPI cao | Task count tăng, milestone vẫn trễ | Due cohort, quality, milestone evidence; không thưởng theo count thuần |
| Review thành nút thắt | InReview age cao | Reviewer queue/capacity/backup và submitted-on-time riêng |
| Cấp quyền ngầm qua cộng tác | Mention/file link lộ khách khác | Resource ACL và preview audience; sharing command riêng |
| Tự động hóa sinh việc vô hạn | Recurrence backlog, task duplicate | Occurrence unique, catch-up cap, rule owner và circuit breaker |
| Hai nguồn ghi đè | Status nhảy ngược, deadline mất | Source authority theo field, version/conflict, không last-write-wins |
| Thay scope không kiểm tác động | Nhiều task mới nhưng baseline giữ xanh | CR, reforecast, explicit impact lên cam kết/resource/cost |

#### 9.16.3 Definition of Ready / Done

**Ready để Dev bắt đầu:** PO chốt scope release, nơi ghi task chuẩn, quyền private/team, mode giao/nhận, review, due change, recurrence, parent/dependency và source mapping. BA chốt field/error/API/state matrix và trace; QA có fixture/expected outcomes. Các tham số chưa chốt phải có hành vi safe default rõ, không để Dev tự đoán.

**Done để phát hành:** core flow và W-T tests thuộc scope chạy đạt; tenant/workspace/file isolation đạt; concurrency/recurrence recovery đạt; dashboard được đối soát bằng dataset có expected metrics; migration/rollback đã diễn tập; người pilot làm được công việc chính; tài liệu vận hành và owner alert đầy đủ. Không ghi Passed chỉ vì báo cáo này đã được viết.

#### 9.16.4 Truy vết chức năng

Trong bảng dưới: W01/02… là UC-W01/02…, T01/02… là W-T01/02…; BR-W là quy tắc Task Core, không phải BR của Chương 1.

| Nhu cầu | Chức năng / UC | Rule / dữ liệu | Test |
| --- | --- | --- | --- |
| Việc cá nhân/nội bộ không cần hợp đồng | W-F01/03, W01/08 | work_type/context/visibility | T01/36 |
| Giao và nhận rõ trách nhiệm | W-F02, W01/02/09 | BR-W01, assignments/offers | T03/05/06/29 |
| Kiểm soát hạn và bàn giao | W-F05, W04 | BR-W03/04, change requests | T11/12/13 |
| Cộng tác an toàn | W-F06, W03 | BR-W09, participants/comments/assets | T02/07/08/09/37 |
| Duyệt đúng kết quả | W-F07, W05 | BR-W08, submissions/reviews | T14/15/16/17/18 |
| Cấu trúc và dependency | W-F08, W06 | BR-W06/07, graph | T19/20/21/22/23 |
| Việc định kỳ ổn định | W-F09, W07 | Rule/occurrence/version | T24/25/26/27/28 |
| Điều hành bằng số đúng | W-F10/12, W08 | KPI/cohort/effort coverage | T30/31/35 |
| Tích hợp không ghi đè | W10 | External mappings/operation | T32/33/38/40 |

**Đào tạo và rollout:** nhân viên thực hành create/accept/block/submit, trưởng nhóm thực hành queue/change request/review/offboarding; dùng dữ liệu giả có hai workspace để kiểm scope. Pilot W-F01–07 trước, bổ sung W-F08–09 trong release P0; estimate/timesheet/Gantt chỉ bật P1 khi có owner dữ liệu. API sync/capacity nâng cao N/A có lý do nếu chưa bật; các guard quyền/version/idempotency không được miễn. Bổ sung công việc này vào gate 9.1/9.5, lập lại estimate trước cam kết thời hạn.

<a id="chuong-10"></a>

## CHƯƠNG 10 NGÂN SÁCH ĐẦU TƯ VÀ HIỆU QUẢ ĐẦU TƯ

### 10.1 Nguyên tắc ước tính

Các con số dưới đây là giả định lập kế hoạch theo triệu đồng, chưa VAT và không phải báo giá bất kỳ nhà cung cấp nào. Giữ cùng phạm vi MVP để so sánh; hệ thống đầy đủ mọi P1/P2 và đa ngành chưa nằm trong giá. Không dùng bảng giá cũ trong playbook để ra quyết định mua năm 2026. Lấy ít nhất 2–3 báo giá theo cùng bộ UAT và kiểm chi phí API, lưu trữ, export, hỗ trợ và chấm dứt dịch vụ.

TCO36 = triển khai một lần + 36 × chi phí vận hành tháng + dự phòng. Bao gồm license, nhân sự kỹ thuật/vận hành, hạ tầng, tích hợp và usage giả định. Không bao gồm media budget của khách, lương Sales/Marketing thường xuyên, thuế, chi phí vốn, tăng giá tương lai và mở rộng ngoài scope; các khoản này cần lập kịch bản riêng nếu phát sinh.

### 10.2 So sánh ba phương án cho khoảng 45 tài khoản

| Phương án | Một lần | Mỗi tháng | TCO 36 tháng gồm dự phòng 15% |
| --- | --- | --- | --- |
| SaaS tùy biến | 120 | 18 | (120 + 36×18) ×1,15 = 883,2 |
| Hybrid | 350 | 28 | (350 + 36×28) ×1,15 = 1.561,7 |
| In-house | 900 | 65 | (900 + 36×65) ×1,15 = 3.726,0 |

Chi phí monthly minh họa: SaaS 9 license + 4 vận hành/integration + 3 usage + 2 storage/backup; Hybrid 8 license + 12 support engineering + 5 cloud + 3 usage; In-house 48 kỹ thuật vận hành + 12 cloud/tool/security + 5 usage. Đây là cách phân rã giả định để lấy báo giá, không hàm ý một mức phí mua được mọi tính năng đã mô tả.

Chi phí triển khai minh họa: SaaS 30 discovery + 40 cấu hình + 20 migration + 20 tích hợp + 10 đào tạo; Hybrid 50 discovery + 140 core/extension + 80 integration + 40 migration/UAT + 40 security/training; In-house 100 BA/design + 500 build + 150 QA/security + 80 migration/integration + 70 rollout. Chi phí tăng nếu yêu cầu HA, trực 24/7, nhiều connector hoặc dữ liệu nguồn kém.

### 10.3 Phương án cá nhân trước

Không mua 45 seats ngay. Ngân sách thử nghiệm giả định: 10–30 triệu thiết lập, 0,5–2 triệu/tháng cho công cụ và usage nhỏ; chưa gồm thời gian tự làm và custom development. Nếu cần tự xây production, dải này không áp dụng. Pilot 30 ngày dùng một pipeline B2B/B2C, 1 form, 1 inbox hoặc ghi nhận thủ công, mẫu brief/SOW, payment đối soát và next action.

Chỉ mở rộng khi có bằng chứng dữ liệu đầy đủ, tiết kiệm thao tác và quy trình lặp lại được. Với 100 lead/tháng, xây nền tảng enterprise từ đầu khó có ROI nếu giá trị hợp đồng thấp; quyết định đầu tư phải dựa biên đóng góp và giá trị tài sản phần mềm mong muốn, không chỉ số lượng nhân viên.

### 10.4 Mô hình ROI và nhạy cảm

Ví dụ minh họa cho Hybrid: mỗi khách mới tăng thêm đem lại 12 triệu đồng đóng góp trong kỳ giả định; tiết kiệm vận hành quy đổi 15 triệu/tháng chỉ được tính nếu thực sự giảm chi hoặc tạo năng lực có giá trị. Không cộng cùng khoản giờ tiết kiệm vào cả giảm nhân sự và tăng doanh thu nếu chưa có chứng cứ tránh đếm đôi.

| Kịch bản | Khách tăng thêm/tháng | Lợi ích gross/tháng | Lợi ích sau vận hành 28/tháng |
| --- | --- | --- | --- |
| Thận trọng | 2 | 2×12 +15 =39 | 11 |
| Cơ sở | 4 | 4×12 +15 =63 | 35 |
| Thuận lợi | 6 | 6×12 +15 =87 | 59 |

Giả định ramp-up 3 tháng không có lợi ích nhưng vẫn trả vận hành, sau đó 33 tháng đạt mức ổn định. ROI36 = (33 × lợi ích gross/tháng − TCO36) / TCO36. Với Hybrid: thận trọng (1.287−1.561,7)/1.561,7 = −17,6%; cơ sở (2.079−1.561,7)/1.561,7 = 33,1%; thuận lợi (2.871−1.561,7)/1.561,7 = 83,8%. Đây là ROI danh nghĩa chưa chiết khấu và không phải dự báo chắc chắn.

Payback minh họa chưa tính dự phòng: chi ban đầu cộng 3 tháng vận hành = 350+84=434; thời gian từ bắt đầu ≈3+434/net benefit tháng. Tương ứng 42,5; 15,4; 10,4 tháng. Nếu net benefit ≤0 thì không có payback trong mô hình. Khi trình duyệt ngân sách chính thức, lập dòng tiền từng tháng có dự phòng, thuế và discount rate được chủ dự án chọn.

Điểm hòa vốn ổn định với giả định trên: khách tăng thêm cần để trang trải vận hành = (28−15)/12≈1,08 khách/tháng, chưa thu hồi chi đầu tư. Không suy ra 4 khách tăng thêm chỉ vì có 100 lead; conversion tăng từ đâu phải được pilot chứng minh.

### 10.5 Tiêu chí chọn giải pháp

| Tiêu chí | Trọng số | Cách chứng minh |
| --- | --- | --- |
| Phù hợp agency và B2B/B2C | 25% | Chạy UC03/05/06/08 với dữ liệu mẫu. |
| Cô lập dữ liệu và quyền | 20% | U17 và kiểm export/file/AI; tiêu chí loại nếu không đạt. |
| Tích hợp và di chuyển dữ liệu | 20% | Webhook replay, API scopes, export hoàn chỉnh và test nhập lại. |
| UX và adoption | 15% | Pilot người dùng thật, thời gian thao tác và feedback. |
| TCO và hợp đồng | 15% | Báo giá 36 tháng cùng scope, usage và exit cost. |
| Năng lực hỗ trợ | 5% | SLA, escalation, backup/restore evidence và trách nhiệm hai bên. |

Chấm 0–5 có bằng chứng, quy đổi trọng số; chưa có PoC thì để “chưa đánh giá”. Không mặc định SlimCRM, AMIS hay giải pháp quốc tế thắng từ nội dung tiếp thị. MISA AMIS Kế toán/meInvoice là ứng viên tích hợp tài chính; chọn CRM lõi là quyết định khác. Phương án đề xuất là SaaS cấu hình hoặc hybrid nhẹ cho pilot, chỉ tự xây sâu khi phần khác biệt agency và nhu cầu đa ngành đã được kiểm chứng.

### 10.6 TCO bổ sung cho hợp nhất năm kênh

Không coi connector là miễn phí sau lần cài đầu. Chi phí gồm phát triển adapter, app review, license inbox, message/template, email provider, object storage, log retention, vận hành token, API changes và hỗ trợ outage. Chi phí bán hàng/marketing hiện tại cần đo trước khi khẳng định tiết kiệm nhân sự.

Ví dụ lập kế hoạch **không phải báo giá thị trường**: 30 ngày công foundation + 5 connector × 10 ngày + 20 ngày UAT/hardening = 100 ngày công. Giả định 3 triệu VND/ngày → 300 triệu; dự phòng 25% → 375 triệu triển khai. Giả định vận hành tăng thêm 5 triệu/tháng + bảo trì 2 ngày/tháng × 3 triệu = 11 triệu/tháng; 36 tháng = 396 triệu. Tổng minh họa 771 triệu chưa gồm VAT, phí provider/license và AI. Hướng thuê engine/SaaS có thể giảm ngày xây nhưng tăng thuê bao và chi phí kết nối; phải thay số bằng báo giá/PoC. Nếu Chương 10.2 đã gồm một hạng mục, chỉ cộng phần chênh lệch, không cộng trùng 771 triệu.

Mô hình volume: 100 inquiry/tháng × 30 message/inquiry = 3.000 message, cộng 50 khách đang phục vụ × 80 message = 4.000, tổng 7.000/tháng là **kịch bản giả định**. Chạy nhạy cảm ×1, ×5, ×10; thêm file size, retention và số tài khoản kênh. “50 khách/tháng” chưa được xác nhận là khách mới, khách active hay đơn; không sử dụng con số đó để suy conversion 50%.

ROI tăng thêm = lợi nhuận gộp đóng góp từ hợp đồng thực sự tăng + giá trị thời gian tiết kiệm thực hiện được − chi phí Omni tăng thêm. Chỉ quy attribution khi có nhóm/thời kỳ so sánh đủ tương đồng; việc thấy thêm message trong CRM không tự chứng minh tăng doanh thu. Gate quyết định: nếu cá nhân chưa có lượng inbox lớn, triển khai foundation và 2–3 kênh ưu tiên trước, bảo toàn khả năng mở rộng năm kênh.

<a id="phu-luc-a"></a>

## PHỤ LỤC A ĐÁNH GIÁ VÀ HỢP NHẤT TÀI LIỆU DỰ ÁN

### A.1 Kết luận đánh giá

Bộ nguồn có nhiều ý tưởng tốt nhưng chưa có một đặc tả xuyên suốt đủ chặt từ nghiệp vụ đến dữ liệu, quyền, ngoại lệ, nghiệm thu và chi phí. Nên giữ tư duy chiến lược của Agency V3, khung điều hành CMO, modular monolith và governance từ tài liệu kỹ thuật/HRM, cùng phương pháp triển khai lấy người dùng làm trọng tâm từ playbook. Không ghép nguyên văn các file vì sẽ lặp nội dung, giữ mâu thuẫn và làm phình phạm vi.

Bản hợp nhất này giữ lõi CRM dùng chung, đặt nghiệp vụ agency vào gói marketing_services, tách dữ liệu phục vụ từng khách thuê agency và đưa HRM đầy đủ thành tích hợp/pack độc lập. “Chưa phù hợp” không có nghĩa nội dung nguồn luôn sai; quyết định bên dưới phân biệt lỗi khái niệm, thiếu đặc tả, giả định chưa kiểm chứng, nội dung cũ và tính năng tốt nhưng chưa đến lúc làm.

### A.2 Danh mục nguồn và phạm vi đã đọc

Đã đọc toàn bộ văn bản, bảng trong 4 tệp DOCX, 2 tệp Markdown và 71 trang PDF trong thư mục docs tại thời điểm rà soát. Các DOCX không chứa tệp ảnh trong word/media. Đã kiểm tra trực quan trang 39 của PDF để xác nhận bối cảnh và niên đại số liệu tăng trưởng. Hai cặp tệp trùng được xác nhận bằng SHA-256; tổng cộng 7 tệp tương ứng 5 nội dung độc lập. Không xóa hoặc sửa các tệp nguồn.

| Mã | Tài liệu | Phạm vi và nhận xét về nguồn |
| --- | --- | --- |
| D01 | docs/Nghien-cuu-He-thong-CRM-Marketing-Enterprise-B2B.md | Bản nghiên cứu 02/07/2026. Mục lục có 13 mục nhưng phần nội dung kết thúc tại 4.5; thiếu các mục 5–13 đã liệt kê. |
| D01b | docs/CRM V8/Nghien-cuu-He-thong-CRM-Marketing-Enterprise-B2B.md | Trùng byte hoàn toàn D01; tên thư mục V8 không chứng minh nội dung mới hơn. |
| D02 | docs/CRM_Marketing_Phan_Tich_Nghiep_Vu_CMO.docx | Bản BA 1.0, phần A–G; tốt cho góc nhìn CMO, chưa phải SRS kỹ thuật chi tiết. |
| D02b | docs/CRM_Marketing_Phan_Tich_Nghiep_Vu_CMO - Copy.docx | Trùng byte hoàn toàn D02; không tính thành nguồn bằng chứng độc lập. |
| D03 | docs/CRM_Tich_Nghiep_Vu.docx | Bản CRM Marketing & HRM 2.0; có phần mở rộng HRM và phụ lục lặp lại phần lớn D02. |
| D04 | docs/Quy_trinh_Agency_Marketing_va_CRM_v3_Strategy_IMC.docx | Agency V3 Strategy & IMC, 14 mục; phù hợp nhất với đặc thù dịch vụ marketing. |
| D05 | docs/CRM V8/slimcrm_crm_playbook_version_2.0.pdf | 71 trang PDF, nguồn tổng hợp/biên dịch của nhà cung cấp; tốt cho đào tạo và adoption, không dùng làm bằng chứng độc lập về giá/tính năng năm 2026. |

D04 dẫn PHILIP KOTLER vol 1 và vol 2 3 cùng phiên bản V2, nhưng các tệp đó không có trong docs. Bản này không tuyên bố đã đọc chúng và không coi nội dung được dẫn gián tiếp là nguồn gốc đã xác minh. Các trang thương mại được tài liệu cũ dẫn cũng không tự trở thành nguồn đã xác minh; nguồn công khai thực sự dùng trong lần này được ghi riêng ở phụ lục C.

### A.3 Những phần tốt được giữ hoặc bổ sung

Bảng A.3–A.4 lưu lịch sử kế thừa; phạm vi/field/giai đoạn hiện hành theo Chương 3/5/9 và hồ sơ module M01–M20 của phiên bản 1.6. Các quyết định trong nguồn cũ không ghi đè baseline mới.

| Mã | Vị trí nguồn | Phần tốt | Đã hợp nhất thế nào | Lý do |
| --- | --- | --- | --- | --- |
| G01 | D04 mục 3–5 | Tách mục tiêu kinh doanh, strategy và plan | Giữ thành FR22; strategy quyết định đối tượng/định vị, plan phân ngân sách và nguồn lực. | Giúp agency giải quyết vấn đề kinh doanh trước khi chạy kênh. |
| G02 | D04 mục 6–8 | Funnel toàn vòng đời và IMC | Bổ sung FR23, message house, channel role, content matrix, launch gate. | Tránh IMC bị rút thành content calendar; nối bán hàng với retention. |
| G03 | D04 mục 12–13 | Experiment và learning repository | Bổ sung FR24, experiment design, evidence, scope quyền và version. | Biến tổng kết thành tài sản học hỏi có thể tái sử dụng hợp lệ. |
| G04 | D02 phần B | Task, capacity và chất lượng đầu ra | Bổ sung FR25/27, definition of done, reviewer, time entry và availability. | Đội marketing cần năng lực giao hàng, không chỉ dashboard lead. |
| G05 | D02 phần C | Brief, budget, health score, cảnh báo | Giữ FR26 nhưng thêm commitments, freshness và approval revision. | Đo được chi tiêu và nguyên nhân can thiệp mà không che dữ liệu thiếu. |
| G06 | D02 phần D | KPI tổng và KPI theo ngành | Giữ FR28 cùng metric dictionary versioned và namespace. | Đổi ngành không làm sai định nghĩa và báo cáo lịch sử. |
| G07 | D02 phần E/F | Customer 360, consent và quyền theo scope | Giữ chương 3/6; bổ sung field masking, export policy, privacy request. | Thông tin khách liền mạch nhưng không mở quyền cho mọi nhân viên. |
| G08 | D03 kiến trúc CTO | Modular monolith có thể tách dịch vụ | Giữ chương 2; worker integration tách áp lực sớm. | Phù hợp pilot cá nhân và vẫn có đường mở rộng. |
| G09 | D03 liên kết CRM và HRM | Capacity, cost center, delegation | Giữ phần HR tối thiểu, đồng bộ cost rate có kiểm quyền. | Tính chi phí và xử lý người vắng mà không xây payroll trước. |
| G10 | D01 mục 2/3.2 | Idempotency, traceability và event version | Giữ outbox/inbox, dedup, retry và correlation_id. | Ngăn mất lead và ghi tiền hai lần khi webhook lặp. |
| G11 | D01 mục 3.3/4 | Account-centric và buying group B2B | Giữ nhưng contact–account nhiều-nhiều, B2C có buyer cá nhân. | Bám hành vi mua doanh nghiệp đồng thời hỗ trợ B2C. |
| G12 | D01 mục 3.3 | Survivorship, merge/unmerge history | Giữ FR02 với guardrail và steward review. | Có khả năng sửa gộp sai và không làm consent rộng lên. |
| G13 | D05 trang PDF 46–55 | Chọn theo nhu cầu, must-have và dùng thử | Bổ sung tiêu chí PoC và scorecard ở chương 10. | Tránh chọn công cụ chỉ vì nhiều tính năng hoặc nội dung quảng cáo. |
| G14 | D05 trang PDF 58–63 | Con người, quy trình, hệ thống, đào tạo và migration | Bổ sung pilot theo nhóm, cutover, rollback, training theo vai. | Giảm rủi ro triển khai thất bại do nhập liệu nặng và thiếu chủ sở hữu. |
| G15 | D05 trang PDF 29–30/42 | Duy trì ngữ cảnh khách và chăm sóc dịch vụ | Giữ ticket, account review, gia hạn và chuẩn hóa bàn giao. | Agency phải bảo vệ chất lượng sau bán, không chỉ chốt hợp đồng. |

### A.4 Những phần cần sửa hoãn hoặc không đưa vào baseline

| Mã | Nguồn hoặc khoảng trống | Vấn đề | Quyết định | Lý do |
| --- | --- | --- | --- | --- |
| R01 | D01 mục lục và kết thúc 4.5 | Thiếu nội dung đã hứa trong mục lục | Hoàn thiện thành 10 chương ở bản này. | Không thể giao dev dựa trên các mục chỉ có tên mà chưa có đặc tả. |
| R02 | D01 mục 2 và 4.3; D02 A.2 | Warehouse là source of truth chung nhưng OLTP cũng được mô tả nguồn ghi | Sửa thành nguồn sự thật theo miền ở 2.1. | Kho phân tích có trễ và không thay transaction system cho tiền, consent và hợp đồng. |
| R03 | D01 mục 3.2/3.4/4.5 | Kafka/Flink/Cassandra/ClickHouse/lakehouse và sharding sớm | Hoãn tới có tải đo được; dùng PostgreSQL + queue + object storage. | 100 lead/tháng không tự tạo nhu cầu nhiều tầng lưu trữ và đội SRE. |
| R04 | D01 mục 3.2 | Event sourcing bị gắn là bắt buộc cho consent pháp lý | Sửa thành chứng cứ log bất biến; kiến trúc event sourcing là lựa chọn. | Nghĩa vụ chứng minh không tự đồng nghĩa một công nghệ triển khai bắt buộc. |
| R05 | D01 mục 3.3; D03 quy tắc khách hàng | Auto merge dựa phone/email/domain hoặc fingerprint quá rộng | Chỉ auto-link định danh xác minh không xung đột; steward review phần còn lại. | Số dùng chung/tái cấp, domain tập đoàn và thiết bị dùng chung gây gộp sai người. |
| R06 | D01 schema Account/Contact | Domain UNIQUE và Contact một Account | Bỏ domain unique toàn cục; thêm Contact_Account_Roles. | Một công ty có nhiều domain và một người có thể đại diện nhiều doanh nghiệp. |
| R07 | D01 mục 4.3/4.5 | Activity mặc định chỉ ở ClickHouse và TTL 3 năm | Hoạt động nghiệp vụ ở OLTP; analytics bản sao khi cần; retention theo mục đích. | Ghi chú/call/task là nghiệp vụ vận hành; không phải mọi event cần 3 năm. |
| R08 | D02 phần F.2 | CMO có cấu hình phân quyền hệ thống và quyền khách hàng rất rộng | Tách CMO, Admin và Privacy owner; xem dữ liệu theo nhu cầu. | Vai trò marketing không mặc nhiên có quyền thay policy hoặc đọc toàn PII/HR. |
| R09 | D02 phần B/C/D; D03 AI HR | AI dự báo hiệu suất, burnout, nghỉ việc và khả năng chuyển đổi | Giữ trợ lý nháp; hoãn dự báo, bỏ suy đoán sức khỏe/nhân sự khỏi MVP. | Thiếu dữ liệu đại diện và dễ gây quyết định không công bằng hoặc rò dữ liệu. |
| R10 | D02 D.2/D.3; D03 KPI | Mọi chiến dịch dùng cùng bộ KPI và chuỗi MQL→SQL→PQL | Định nghĩa metric tùy objective; PQL là tín hiệu song song ở pack SaaS. | Brand, dịch vụ và product-led growth không có cùng tuyến chuyển đổi bắt buộc. |
| R11 | D02 D.3.4 | CPM mô tả theo nghìn tiếp cận | Chuẩn hóa CPM theo 1.000 impressions; cost per 1.000 reached users là metric khác. | Trộn reach và impression làm so sánh chi phí sai khi frequency thay đổi. |
| R12 | D03 phạm vi HRM | Tuyển dụng/chấm công/lương/bảo hiểm trong cùng roadmap rộng | Hoãn thành HRM riêng; MVP chỉ organization, capacity, delegation và cost allocation. | Làm phình phạm vi, tăng dữ liệu nhạy cảm và chậm giải quyết lead–cash. |
| R13 | D03 phụ lục; D01b/D02b | Nội dung lặp và bản copy không có thay đổi | Hợp nhất một lần, lập source register, không xóa bản gốc. | Lặp không tăng giá trị, dễ khiến các bản lệch nhau khi chỉnh sửa. |
| R14 | D04 mục 13 | Quy trình toàn bộ quá dài nếu ép mọi job đi đủ tầng | Tạo scope_template gọn/đầy đủ ở FR22. | Dự án chiến lược cần nghiên cứu sâu; một job nhỏ không cần đủ nghi thức. |
| R15 | D04 các template | Phê duyệt mới có tên nhưng thiếu version và invalidation | Bổ sung approval theo hash/version và gate launch. | Không thể nghiệm thu khi khách duyệt một creative nhưng đội chạy bản khác. |
| R16 | D05 trang PDF 8–9/17–18 | SaaS/cloud/self-hosted và license bị chia cứng | Sửa so sánh theo trách nhiệm vận hành, khả năng tùy biến, license và TCO [S12](#s12). | SaaS là mô hình dịch vụ cloud; self-hosted có thể trên cloud, không luôn mua đứt. |
| R17 | D05 trang PDF 15/38–39 | Tỷ lệ tăng trưởng được dùng dễ như hiệu quả mặc định | Không đưa tỷ lệ cũ vào KPI/ROI; dùng baseline và kịch bản của dự án. | Trang 39 ghi khảo sát Salesforce 2014–2016; khác thời gian, mẫu và doanh nghiệp hiện tại. |
| R18 | D05 trang PDF 56/64 | Danh sách nhà cung cấp và đánh giá tốt nhất có tính quảng bá | Chỉ xem như danh mục tham khảo, không mặc định chọn; PoC theo UAT. | Nguồn do nhà cung cấp biên soạn và chưa xác minh giá/tính năng hiện thời. |
| R19 | D05 trang PDF 63 | Số lần login như thước đo áp dụng chính | Thay bằng owner/next action/evidence, thời gian hoàn thành việc và tỷ lệ sai. | Login có thể cao nhưng hồ sơ thiếu, không phản ánh giá trị sử dụng. |
| R20 | D05 trang PDF 59 | Dùng nhiều phần mềm bị xem như vô nghĩa | Sửa thành tránh nhập trùng và có source owner rõ. | CRM tích hợp kế toán, tổng đài, dự án là hợp lý khi giao diện và dữ liệu thống nhất. |
| R21 | D01/D03 tuân thủ; đề bài ban đầu | Chỉ dùng Nghị định 13/2023 cho năm 2026 | Cập nhật Luật 91/2025 và Nghị định 356/2025, nêu trạng thái NĐ13. | Điều 42 NĐ356 quy định NĐ13 hết hiệu lực từ 01/01/2026. |
| R22 | Khoảng trống chung các nguồn | Chưa tách dữ liệu agency và dữ liệu người dùng của khách thuê agency | Bổ sung client_workspace, processing purpose và isolation test. | Rủi ro trộn tệp khách hàng là đặc thù quan trọng của marketing agency. |
| R23 | Khoảng trống chung các nguồn | Chưa đủ partial/refund/replay/media pass-through và commission ledger | Bổ sung FR16/17, UC07/13 và schema ledger. | Chỉ mô tả doanh thu/ROI không đủ để kiểm soát tiền thật. |
| R24 | Khoảng trống chung các nguồn | Thiếu RPO/RTO, cutover, rollback, UAT và traceability cụ thể | Bổ sung chương 7/9 và phụ lục B. | Đây là điều kiện để triển khai và nghiệm thu có bằng chứng, không chỉ thuyết trình. |
| R25 | Yêu cầu chống Sales ôm khách | Zalo cá nhân và chống export tuyệt đối chưa có căn cứ khả thi | OA tập trung, nhập nguồn cá nhân, masking server, DLP và audit. | Không hứa đọc chat cá nhân hoặc chặn tuyệt đối camera; phải có quyền API thật. |
| R26 | Yêu cầu thưởng phạt sử dụng CRM | Dễ biến kỷ luật dữ liệu thành phạt tiền/cắt lương | Thiết kế coaching, thưởng hợp lệ, đối soát và nội quy được rà soát. | Bảo đảm quy chế sử dụng không tạo hành vi xử lý lao động không phù hợp. |

### A.5 Phần bổ sung mới và giá trị thực tế

Bản mới bổ sung ranh giới tenant/branch/business line/client workspace; approval theo version; quyết định dùng trước cá nhân rồi đội ngũ; 16 luồng có nhánh đậu/rớt; dictionary tám bảng bắt buộc cùng payment/commission; ma trận quyền theo phạm vi; SLA đo theo lịch; NFR có cách đo; DRP/cutover; UAT liên kết; và TCO/ROI có giả định kiểm tra được. Đây là các thiết kế đề xuất từ phân tích nhu cầu, không gán thành nội dung vốn có trong nguồn.

Khung đa ngành không có nghĩa một workflow áp dụng tất cả. Core giữ định danh, hoạt động, quyền, tài chính và các cơ chế chung; từng pack sở hữu dữ liệu chuyên ngành, mẫu KPI và state machine. Muốn mở một ngành cần migration, policy và UAT tương ứng. Với ngành nhạy cảm như sức khỏe/tài chính, phải bổ sung phân tích pháp lý và chuyên môn trước bật tính năng.

### A.6 Quyết định còn mở trước triển khai

| Mã | Cần làm rõ | Chủ trì và mốc |
| --- | --- | --- |
| O01 | 50 khách/tháng là active, khách mới hay khách trả tiền; lead unique tính thế nào | Chủ dự án, ngày 1–3. |
| O02 | Dịch vụ cụ thể, giá, retainer, số vòng sửa và mẫu hợp đồng | Chủ dự án/BA, ngày 1–7. |
| O03 | Nhân sự đã có hay mục tiêu tương lai; ai kiêm kế toán, AM và privacy | Chủ dự án, ngày 1–5. |
| O04 | Kênh, OA/Page, domain, tài khoản ngân hàng và phần mềm hiện hữu | BA/technical lead, ngày 1–10. |
| O05 | Ngân sách pilot/36 tháng, quyền sở hữu mã nguồn và khả năng thuê kỹ thuật | Chủ dự án, trước chọn nhà cung cấp. |
| O06 | Agency có xử lý data khách cuối thay khách hàng hay chỉ báo cáo tổng hợp | Chủ dự án/privacy owner, trước client workspace thật. |
| O07 | Chính sách hoa hồng, attribution và điều kiện hoàn/đảo | Sales + kế toán, trước cấu hình ledger. |
| O08 | Yêu cầu 24/7, legal entity của chi nhánh và khả năng DR | Chủ dự án/technical lead, trước cam kết SLA. |

Mỗi policy/parameter cần type/unit/scope, owner, source/evidence, default đề xuất, version/effective_at, Draft/Reviewed/Active và validation. Chốt lịch/ngày làm việc thực tế, phân biệt claim/FRT/discovery, notice basis, self-approval/discount, cost/margin, tolerance/waterfall/production basis và quality fallback. Policy cấu hình phải được review trước Active; working day không cố định480phút nếu ca được khai báo7,5giờ. Lịch thứBảy chỉ bật khi chủ dự án xác nhận. Legal deadline policy không được thay bằng marketing/internal SLA tùy ý.

Các điểm mở không ngăn sử dụng tài liệu làm baseline thiết kế và thảo luận. Chúng ngăn việc coi mọi giả định trong bản này là quyết định đã phê duyệt hoặc báo giá cam kết. Mọi cập nhật tiếp theo thực hiện trong đúng tệp Master duy nhất, tăng version và giữ lịch sử quyết định. Không yêu cầu người dùng đọc các báo cáo nguồn để hiểu baseline hiện hành.

### A.7 Quyết định và tham số Work Management 1.7

CR-WORK-20261016 đã hợp nhất phạm vi và quy tắc theo yêu cầu chủ dự án. Mặc định thiết kế: CRM Task Core làm nguồn ghi pilot; một owner + collaborators; offer/accept cho việc giao, personal autoaccepted; review theo task type; delegated due change cần authority; private scope không tự mở cho cấp trên; chỉ deliverable/task publish mới tới khách; calendar recurrence cơ bản; WIP ở P0, effort/capacity chi tiết P1.

| ID | Tham số còn cần cấu hình trước bật | Khi thiếu / owner |
| --- | --- | --- |
| W-O01 | Team queue manager, offer timeout, escalation recipient và lịch | Không activate queue/offer automation khi thiếu quản lý; việc cá nhân vẫn dùng; Ops |
| W-O02 | Task type cần review, reviewer/backup và review due | Không phát hành loại có review nếu không có reviewer hợp lệ; simple task không review hiển thị rõ; Team Lead |
| W-O03 | Calendar/timezone, quiet hours và reminder | Lưu UTC, business timezone Asia/Ho_Chi_Minh; chưa có lịch được duyệt thì không tự áp business-day rules; Ops |
| W-O04 | Personal visibility, retention, client publish | Private mặc định, không cấp quyền theo cấp trên; không tự publish; owner/privacy |
| W-O05 | Nguồn task từng project và connector authority | Mặc định CRM; PMS chưa verified không nhận là đã sync; technical owner/PM |
| W-O06 | Capacity, estimate/time entry policy | WIP có type; thiếu estimate/availability hiện Unknown, không auto-route bằng giờ; PM |
| W-O07 | License/chi phí, nhân lực và lịch release | Chưa có dự toán thì không hứa đủ P0 mới trong 90 ngày; chủ dự án |

Đây là tham số cấu hình, không trì hoãn viết schema/use case hoặc yêu cầu đọc báo cáo riêng. Tất cả default và policy override phải có version/effective date và authority; hướng dẫn cấu hình không được vượt guard của Master.

<a id="phu-luc-b"></a>

## PHỤ LỤC B MA TRẬN TRUY VẾT VÀ MẪU VẬN HÀNH

| Nhóm yêu cầu | Luồng | Dữ liệu và quyền | Nghiệm thu |
| --- | --- | --- | --- |
| FR01–03 Customer 360 | UC01/11/15 | Contacts, Accounts, Channel_Identities, Consent; steward | U01/U06/U15/U18 |
| FR04–06 Lead/pipeline | UC01/02/03 | Leads, Deals, Assignments; owner/team | U01–U05 |
| FR07–08 Inbox/masking | UC01/12 | Conversations, Messages, Assets; scope | U16/U17 và kiểm masking API |
| FR09–10 Journey/referral/loyalty | UC10/11/13 | Consent/suppression; Journey/Referral theo feature; Loyalty_Ledger chỉ points P2 | U15/OC17/INT17; U23-R/U23-L theo referral/points được bật; không bắt points trong P0 |
| FR11–13 AI | UC03 hỗ trợ, không quyết định | AI drafts, model/prompt version; user ACL | U22 và bộ 60 call được phép |
| FR14–17 Sales/finance | UC05/06/07/08/13 | Quote/Contract/Order/Payment/Commission | U07–U13 |
| FR18–21 CS/branch | UC09/10/12/14 | Ticket, project, branch và lịch | U14/U16/U17 |
| FR22–24 Strategy/IMC | UC04/08/16 | Strategy, Plans, Assets, Experiments | U13/U19 và kiểm gate launch |
| FR25 Work Management | UC-W01–10; UC06/08/12 | Tasks/assignment/review/dependency/recurrence; 3.14/5.20/6.6 | W-T01–40, W-F01–14; 9.16 |
| FR26–27 Budget/people | UC04/06/08/16 | Availability, cost, budget; quyền dữ liệu nhân sự | U19/U20, commitment→actual; không dùng task count làm scorecard duy nhất |
| FR28–29 KPI/attribution | UC15/16 | Metric facts, touchpoints, credits | U18/U20; tổng attribution đối soát |
| FR30–32 Connections/Identity/Thread | UC17/18/19/22 | Channel_Connections/Identities, Inboxes, Conversations/Participants, journal; scoped ACL/capability | OC01–03/11–13/15/23; INT02/24; RV05/11 |
| FR33–34 Inbound/Outbound | UC17/19/21 | Inbound_Events, Messages/Status, Outbound_Intents/Attempts/Outbox; policy/idempotency | OC01/05–09/16–17/19; INT01/17/25/26; RV05/14/17 |
| FR35–36 Assignment/Timers | UC02/09/20 | Assignments, Business_Subjects, SLA_Episodes/Promises; version/calendar | U02–04; OC04/10/18; INT04/05/23; CX-U03–CX-U09; RV01/12/13/14 |
| FR37 Search/File/Protection | UC11/12/14/18 | ACL/grants, search/cache/file/RLS; không bypass bằng link | U16/17; OC03/14/20; INT23/28/29; RV10/15/17 |
| FR38 Sync/Recovery | UC21 | Checkpoints, connection, event/intent state, coverage/reconcile | OC08/09/19/21; INT11/25/26; RV14/17 |
| FR39–40 Business Links/Email | UC17/19/22 | Business_Subjects/Conversation links/Message_Attachments; typed FK/MIME/policy | OC11/13/14; INT04/24; CX-U05/23; RV01/05/10 |
| NFR01–12 | Mọi luồng | Monitoring, restore, policy, export; feature scope | Load test, U17/U21/U24, portability và RV tests theo module bật |

### B.1 Mẫu brief dịch vụ marketing

Mã khách/workspace; người liên hệ và người duyệt; sản phẩm; mô hình B2B/B2C; mục tiêu kinh doanh; baseline và nguồn; phân khúc; vấn đề ưu tiên; ngân sách phí dịch vụ/media riêng; thời điểm; phạm vi đề nghị; điều kiện nghiệm thu; tài sản khách phải cấp; quyền sử dụng dữ liệu; rủi ro; người chịu trách nhiệm; next action. Trường chưa biết ghi Unknown và task làm rõ, không thay bằng giả định không nhãn.

### B.2 Mẫu SOW và nghiệm thu

Mỗi deliverable có tên, số lượng, format, thời hạn, người cung cấp đầu vào, số vòng sửa, tiêu chuẩn QA, người duyệt khách và evidence. Bảng loại trừ nêu rõ media budget, mua tài nguyên, quyền sở hữu, vận hành sau bàn giao và cam kết performance nếu có. Nghiệm thu ghi asset version/checksum, quyết định Accept/Reject, lý do, thời điểm và thẩm quyền người ký.

### B.3 Mẫu kiểm tra campaign trước launch

Objective và strategy được duyệt; ngân sách đúng version; audience/exclusion và purpose hợp lệ; asset QA; URL và tracking test; offer và claim có chứng cứ; quyền tài khoản kênh; người giám sát; thời gian chạy; stop rule; phương án rollback; client approval. Kết quả từng mục là Pass/Fail/NotApplicable có lý do; Fail trọng yếu chặn launch.

### B.4 Mẫu hội nghị đánh giá khách hàng hằng tháng

Kết quả theo mục tiêu; deliverable đã nghiệm thu; spend và fee tách biệt; hạn chế dữ liệu; ticket mở; điều đã học; quyết định cần khách duyệt; kế hoạch tháng sau; rủi ro và owner; lịch gia hạn. Không dùng report marketing của khách để thay báo cáo tài chính agency.

### B.5 Mẫu yêu cầu thay đổi và quyết định kiến trúc

CR/ADR ID; vấn đề; bối cảnh và nguồn; lựa chọn; tác động người dùng/dữ liệu/API/quyền/chi phí; lựa chọn được đề xuất; lý do; người quyết; ngày; tiêu chí xem xét lại; kế hoạch migration/rollback; UAT bổ sung. Ví dụ ADR01 chọn modular monolith vì tải hiện tại thấp; xem xét tách khi đo được contention hoặc cần nhóm phát hành độc lập, không chỉ vì số lượng dòng code tăng.

<a id="phu-luc-c"></a>

## PHỤ LỤC C NGUỒN CÔNG KHAI VÀ GIỚI HẠN XÁC MINH

Nguồn công khai được tra cứu ngày 15/10/2026. Tài liệu chính thức dùng để xác minh pháp lý, khả năng nền tảng và các nguyên tắc kỹ thuật cụ thể; ngưỡng vận hành, kiến trúc lựa chọn, chi phí và chính sách nội bộ là đề xuất của dự án. Chưa thử API trên tài khoản doanh nghiệp thật, chưa thu báo giá và chưa có khảo sát khách hàng riêng của doanh nghiệp.

<a id="s01"></a>

#### S01 Công báo Luật số 91/2025/QH15

[Công báo Luật số 91/2025/QH15](https://congbao.chinhphu.vn/cong-bao/cong-bao-so-971-972-ngay-24-07-2025-45574.htm)

Khung pháp lý dữ liệu cá nhân; không thay việc đối chiếu từng nghĩa vụ.

<a id="s02"></a>

#### S02 Nghị định 356/2025/NĐ-CP bản Công báo

[Nghị định 356/2025/NĐ-CP bản Công báo](https://congbao.cdnchinhphu.vn/180507251028987904/2026/1/17/356signed-1768638052103952849513.pdf)

Điều 42 hiệu lực và thay thế NĐ13; chương 6.3.

<a id="s03"></a>

#### S03 Zalo OA hướng dẫn ZBS Account

[Zalo OA hướng dẫn ZBS Account](https://oa.zalo.me/home/documents/guides/huong-dan-tao-zbs-account)

Tên ZBS Account từ 01/01/2026 và dịch vụ liên quan; không suy ra mọi loại tin được gửi.

<a id="s04"></a>

#### S04 NAPAS chuyển nhanh bằng mã VietQR

[NAPAS chuyển nhanh bằng mã VietQR](https://napas.com.vn/dich-vu-chuyen-tien-nhanh-napas-247)

VietQR hỗ trợ chuyển khoản; cơ chế xác nhận tiền phải thiết kế với nguồn ngân hàng/provider.

<a id="s05"></a>

#### S05 MISA cổng tài liệu tích hợp

[MISA cổng tài liệu tích hợp](https://www.misa.vn/tich-hop/tai-lieu/)

Tách tài liệu AMIS Kế toán, meInvoice và CRM; cần chọn đúng sản phẩm.

<a id="s06"></a>

#### S06 MISA tổng quan Open API CRM

[MISA tổng quan Open API CRM](https://www.misa.vn/154981/tong-quan-open-api-misa-crm/)

Ứng viên tích hợp API; không coi phạm vi CRM API là phạm vi kế toán.

<a id="s07"></a>

#### S07 TikTok Shop Partner API

[TikTok Shop Partner API](https://partner.tiktokshop.com/docv2/api-document)

Ủy quyền và phạm vi theo đối tác; chưa xác nhận endpoint cho từng tính năng dự án.

<a id="s08"></a>

#### S08 Shopee Open Platform

[Shopee Open Platform](https://open.shopee.com/faq/92)

Điểm kiểm chứng với nhà cung cấp; chưa chốt quyền chat/đơn và hạn mức cho tài khoản cụ thể.

<a id="s09"></a>

#### S09 PostgreSQL Row Security Policies

[PostgreSQL Row Security Policies](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)

RLS bổ sung giới hạn truy cập hàng; vẫn cần policy ở ứng dụng và kho ngoài SQL.

<a id="s10"></a>

#### S10 OWASP Top 10 cho LLM và GenAI

[OWASP Top 10 cho LLM và GenAI](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf)

Tham chiếu rủi ro prompt injection, lộ dữ liệu và quyền agent; dùng cho test design.

<a id="s11"></a>

#### S11 AMA định nghĩa Marketing

[AMA định nghĩa Marketing](https://www.ama.org/the-definition-of-marketing-what-is-marketing/)

Kiểm tra định hướng tạo và trao đổi giá trị của D04; không phải chứng cứ KPI của doanh nghiệp.

<a id="s12"></a>

#### S12 NIST Definition of Cloud Computing

[NIST Definition of Cloud Computing](https://www.nist.gov/publications/nist-definition-cloud-computing)

Phân biệt mô hình dịch vụ và triển khai; sửa phân loại SaaS/cloud quá cứng trong playbook.

<a id="s13"></a>

#### S13 Bộ luật Lao động 2019 Điều 127

[Bộ luật Lao động 2019 Điều 127](https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Bo-Luat-lao-dong-2019-333670.aspx)

Bản toàn văn tra cứu; quy chế thưởng/kỷ luật cần rà soát theo tình trạng pháp lý và hợp đồng thực tế.

<a id="s14"></a>

#### S14 Zalo OA khởi tạo ứng dụng và cấp quyền

[Zalo OA khởi tạo ứng dụng và cấp quyền](https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195)

OA OpenAPI và cấp quyền ứng dụng; không chứng minh khả năng đọc lịch sử Zalo cá nhân.

### Dấu vân tay tệp nguồn

SHA-256 dùng để xác định bản trùng và truy vết phiên bản đã rà soát.

- `docs/CRM V8/Nghien-cuu-He-thong-CRM-Marketing-Enterprise-B2B.md`: `24e613221ef74664408885f3be1f4e1a77bb48620799d3c4ff8d86fdf0701763`
- `docs/CRM V8/slimcrm_crm_playbook_version_2.0.pdf`: `61910ac9efad3c72cc5da1adf5f0aba65bbb0d105e77daba81e43160a0182af5`
- `docs/CRM_Marketing_Phan_Tich_Nghiep_Vu_CMO - Copy.docx`: `073a9e78a11455fcee573161cbfc60783b1559d9e038d0c8ba86e76dbaeed52f`
- `docs/CRM_Marketing_Phan_Tich_Nghiep_Vu_CMO.docx`: `073a9e78a11455fcee573161cbfc60783b1559d9e038d0c8ba86e76dbaeed52f`
- `docs/CRM_Tich_Nghiep_Vu.docx`: `36947a2c5979900345aa2f7cb23f356aec9b278a1828b32f0513b57270a5ae21`
- `docs/Nghien-cuu-He-thong-CRM-Marketing-Enterprise-B2B.md`: `24e613221ef74664408885f3be1f4e1a77bb48620799d3c4ff8d86fdf0701763`
- `docs/Quy_trinh_Agency_Marketing_va_CRM_v3_Strategy_IMC.docx`: `099ef06b91d03811beaf996ea33a00adb6ba473a0bbb48ff8e101d70d19ef364`


### C.1 Nguồn kỹ thuật cho các hợp đồng đã hợp nhất

Các nguồn sau hỗ trợ nguyên tắc kỹ thuật; cấu hình nghiệp vụ và thiết kế cụ thể là quyết định của dự án, chưa là kết quả chạy phần mềm.

| Nguồn | Dùng cho hợp đồng |
| --- | --- |
| [PostgreSQL numeric](https://www.postgresql.org/docs/current/datatype-numeric.html) | Số hữu hạn, scale/quantum tại5.1; không dùng amount>0 thay validation NaN. |
| [PostgreSQL locking](https://www.postgresql.org/docs/current/explicit-locking.html) | Khóa nhất quán, retry và post/close-period tại5.14. |
| [RFC9700](https://www.rfc-editor.org/rfc/rfc9700.html) | OAuth callback/session/provider binding tại2.6. |
| [AWS presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) | Phân biệt bearer storage URL với quyền user; gateway6.2. |
| [OWASP SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | Egress/remote fetch FR40. |
| [Google sender guidelines](https://support.google.com/mail/answer/81126?hl=en) | Sender authentication/unsubscribe theo loại sender tạiFR34. |
| [NĐ91/2020 chống thư rác](https://vanban.chinhphu.vn/default.aspx?docid=200773&pageid=27160) | Email quảng cáo phải đối chiếu văn bản áp dụng khi bật; không chỉ dựa consent dữ liệu cá nhân. |

<a id="phu-luc-d"></a>

## PHỤ LỤC D NGHIÊN CỨU CRM THAM KHẢO VÀ QUYẾT ĐỊNH TÍCH HỢP

### D.1 Phương pháp, phạm vi và độ chắc chắn

Ngày đối chiếu: **15/10/2026**. “Tốt nhất” được hiểu theo độ phù hợp: mở rộng nhiều ngành, agency B2B/B2C, inbox năm kênh, khả năng nâng cấp, dữ liệu và tổng chi phí. Không có sản phẩm tốt nhất tuyệt đối. Chọn sáu dự án có code/tài liệu kiến trúc công khai (Twenty, EspoCRM, Frappe CRM, Odoo, SuiteCRM, Chatwoot) và ba nền tảng doanh nghiệp để học mô hình (Salesforce, HubSpot, Microsoft Dynamics/Dataverse). Chatwoot là engine hội thoại, không thay toàn bộ CRM/ERP.

Đã đối chiếu một số tệp code/manifest công khai và tài liệu chính thức; chưa clone/đọc toàn bộ code của chín sản phẩm, chưa chạy benchmark, chưa kiểm thử tích hợp với tài khoản của doanh nghiệp. Các URL `main`, `develop`, `master` là nhánh thay đổi, không phải snapshot bất biến; khi chọn triển khai phải pin commit/tag, lockfile, LICENSE và lưu bằng chứng PoC. Không lấy số sao GitHub, quảng cáo AI hoặc tính năng trên website làm bằng chứng hiệu năng/ROI. Mã nguồn tải qua shell thất bại do kết nối môi trường; các nhận định dưới dùng nội dung nguồn đọc qua công cụ web. Đoạn này mô tả vòng nghiên cứu mã nguồn ban đầu; lịch sử các vòng nghiên cứu sau và phạm vi xác minh được ghi tạiE.6, không dùng trạng thái cũ để thay kết quả thiết kế hiện hành.

Phân biệt: **quan sát** là nội dung nguồn chứng minh; **đề xuất** là suy luận thiết kế cho dự án; **rủi ro** là điều kiện có thể gây hại, không là cáo buộc sản phẩm có lỗi. Không đưa kết luận “framework X nhanh hơn Y” khi chưa đo.

### D.2 So sánh có bằng chứng và điều kiện áp dụng

| Dự án | Quan sát đã có nguồn | Điều nên áp dụng và vị trí tích hợp | Điều có thể hại nếu áp dụng sai / quyết định |
| --- | --- | --- | --- |
| Twenty | Server package có NestJS, TypeORM, BullMQ, OpenTelemetry; lệnh chạy API/worker riêng và package workspace [R01](#r01) | API/worker tách entrypoint, contracts dùng chung, tracing; áp dụng 2.8 và 7.6 | Sao chép toàn bộ dependency làm tăng gánh nâng cấp và vận hành ở 100 lead/tháng; học cấu trúc, không chép toàn stack. LICENSE cần đọc theo package, không mặc định permissive [R16](#r16) |
| EspoCRM | Extension backend/frontend có thư mục riêng, metadata/controller override theo order [R02](#r02) | Pack ngành có namespace, routes và dependency rõ; áp dụng 2.8, OC24 | Hai pack override cùng key có thể che nhau; thêm conflict detection. Không sửa core trực tiếp; workflow/sales add-on phải kiểm tra edition và báo giá, không mặc định miễn phí |
| Frappe CRM | Frontend manifest dùng Vue/Vite; framework DocType mô tả dữ liệu và hành vi [R03](#r03)[R04](#r04) | Metadata có schema/validation và form tái sử dụng; xét PoC nếu chọn hệ sinh thái Frappe | Custom mọi thứ bằng script không kiểm thử gây lệch giữa môi trường; giữ quy tắc tiền/quyền trong logic được test, migration versioned. Không chọn Vue chỉ vì sản phẩm dùng Vue |
| Odoo CRM | Module crm có models/views/security/data/tests/wizard và manifest; có pipeline, activities và leads [R05](#r05) | Đóng gói ngành có model, UI, quyền và test đi cùng; hoạt động tiếp theo gắn opportunity | Lôi cả ERP vào giai đoạn cá nhân tăng phạm vi/đào tạo; chỉ xét mạnh khi thực sự cần vận hành ERP chung. Không tự cho rằng community có mọi tính năng enterprise |
| SuiteCRM 8 | Tài liệu extension tách app/backend/modules/config, Angular và Symfony extension [R06](#r06) | Extension có cấu trúc và dependency injection; UI cấu hình tái sử dụng | Microfrontend tạo thêm build/version/runtime seam; chưa cần cho đội nhỏ. Nếu chọn SuiteCRM, PoC nâng cấp extension bắt buộc thay vì giả định tương thích |
| Chatwoot | ContactInbox nối contact/inbox, unique inbox+source_id trong model; API Channel cho kênh tùy biến [R08](#r08)[R09](#r09) | Tách người–danh tính kênh–conversation; dùng làm lựa chọn engine inbox trong PoC | Hai router/master cùng sửa assignee/status gây vòng lặp; adapter custom không tự tạo quyền Zalo/TikTok. Thêm Rails engine là thêm stack vận hành, không mặc định bắt buộc. Enterprise license tách [R17](#r17) |
| Salesforce | Hướng dẫn lựa chọn automation theo độ phức tạp và một entrypoint chính cho object [R18](#r18) | Rule registry, thứ tự, chống recursion, version hóa và test; phân biệt AI với nghiệp vụ deterministic | Nhiều trigger không owner gây side effect và khó audit; chuyển mọi rule sang agent AI làm kết quả không ổn định. Không suy ra code nội bộ Salesforce từ tài liệu công khai |
| HubSpot | Associations API hỗ trợ quan hệ có nhãn, hướng quan hệ và limits theo subscription [R07](#r07) | Contact–Account nhiều vai trò, decision maker/billing, provenance; áp dụng 3.12 và schema hiện hữu | Ép một Contact chỉ một công ty làm sai B2B; copy raw type ID sang hệ khác gây lỗi. Quyền/tier API phải kiểm chứng khi mua |
| Dynamics/Dataverse | Solution layer tách base managed và app extensions; quản lý source và deployment [R19](#r19)[R20](#r20) | Core contract ổn định, pack version/dependency, dev/staging/prod và release artifact | Tùy biến trực tiếp production gây drift và phụ thuộc vòng; lớp extension không giải quyết permission sai. Chưa xác nhận license/tổng chi phí phù hợp giai đoạn cá nhân |

### D.3 Quy trình nghiệp vụ được tích hợp và lý do

1. **Account và vai trò người mua:** giữ riêng người duyệt ngân sách, người ký và người nghiệm thu; một người có thể nhiều vai trò. Bằng chứng mô hình associations [R07](#r07); suy luận cho agency giúp tránh gửi báo giá cho sai người hoặc mất quan hệ khi người đại diện chuyển công ty. Đã tích hợp 3.12, UC18, UC22.
2. **Next action trên cơ hội:** mỗi Deal mở có owner, việc tiếp theo và hạn, theo cách CRM tổ chức pipeline/activities như Odoo [R05](#r05). Với agency, quote không được treo vô hạn; lost reason và stage gate phải xác định. Không ép mọi chat thành Deal vì làm sai conversion.
3. **Quản trị automation:** registry event → điều kiện → hành động → owner → version → test; lấy nguyên tắc quản trị từ Salesforce [R18](#r18). Mỗi intent gửi/commission được xử lý idempotent; import và replay có chế độ riêng. Chế độ bypass chỉ bỏ automation được chỉ định, không bypass tenant/ACL/audit.
4. **Tách identity theo kênh:** bằng chứng cụ thể từ ContactInbox của Chatwoot [R08](#r08); dự án bổ sung tenant/workspace và kiểm chứng danh tính. Tên giống nhau là tín hiệu tìm kiếm yếu; gộp nhầm có thể lộ hợp đồng/chiến dịch của khách khác.
5. **Gói ngành và ALM:** học extension Espo/Suite và base solution Microsoft [R02](#r02)[R06](#r06)[R19](#r19); dự án bổ sung namespace conflict checks và migration ownership. Custom qua core patch làm mỗi lần nâng cấp phải giải quyết xung đột và có nguy cơ mất bản vá.
6. **Phục hồi đồng bộ:** Gmail mô tả notifications có thể trễ/mất và cần sync dự phòng [R13](#r13). Dự án áp dụng checkpoint/dedup/reconcile cho từng provider theo khả năng, không hứa webhook luôn giao đủ hoặc đủ lịch sử.

### D.4 Những lựa chọn không đưa vào MVP và lý do gây hại theo bối cảnh

| Lựa chọn | Điều kiện gây hại và cơ chế | Khi nào cân nhắc lại |
| --- | --- | --- |
| Microservices cho mọi entity | Đội nhỏ phải quản lý distributed transaction, network retry và nhiều deployments trước khi có tải; tăng thời gian tìm lỗi | Có ranh giới đội/tải/cô lập rõ, số đo và nguồn lực vận hành |
| Metadata/EAV không giới hạn | Field không kiểm soát kiểu, quyền và index làm report khó đúng và query chậm; tên ngành đụng nhau | Metadata có schema registry; fields trọng yếu được typed và migration kiểm thử |
| Fork sâu một CRM để có đủ năm kênh | Nợ merge upstream; mất đường nâng cấp và bản vá; vẫn không vượt được giới hạn API | Có owner fork dài hạn và kinh phí, không có extension đáp ứng |
| Scrape Zalo cá nhân/TikTok bằng session | Credential mong manh, không kiểm soát quyền, không có hợp đồng API ổn định; dễ gián đoạn và lộ nội dung | Không là baseline; chỉ dùng cơ chế chính thức được xác minh |
| AI tự merge, tự báo giá, tự gửi | Sai định danh hoặc cam kết thương mại khuếch đại ra khách thật; khó rollback tin đã gửi | Task rủi ro thấp có eval, policy gate, phạm vi tool và approval |
| Một inbox cho mọi khách agency không workspace ACL | Nhân sự account A đọc brief/chi phí của account B qua search/AI/attachment | Luôn yêu cầu isolation; một UI hợp nhất vẫn phải lọc quyền từng tài nguyên |
| Cam kết 100% lịch sử/đọc tin trên mọi kênh | API không cung cấp backfill/read receipt thì không có dữ liệu để chứng minh | Chỉ cam kết capability đã test và coverage đo được |
| Đánh giá Sales theo số tin/autoack | Tạo động cơ spam, đóng/mở ticket để né SLA; không phản ánh chất lượng qualification | Đo phản hồi người thật, next action, conversion và chất lượng bằng mẫu |

Các rủi ro trên là phân tích thiết kế của dự án, không khẳng định mọi sản phẩm tham khảo đều mắc lỗi. Chi phí cụ thể, mức độ bảo mật và tốc độ chỉ được kết luận sau PoC.

### D.5 Nhật ký nguồn và giới hạn xác minh

Nguồn R01–R20 được đối chiếu ngày 15/10/2026. Nội dung tóm tắt mỗi nguồn chỉ dùng làm bằng chứng cho quan sát tương ứng; thiết kế chi tiết ở các chương là đề xuất riêng. Không xem nhánh development là release production đã ổn định.

| ID | Nguồn chính thức | Bằng chứng dùng / giới hạn |
| --- | --- | --- |
| <a id="r01"></a>R01 | [Twenty server package.json](https://raw.githubusercontent.com/twentyhq/twenty/main/packages/twenty-server/package.json) | Dependency và script API/worker/workspace; không chứng minh runtime performance |
| <a id="r02"></a>R02 | [EspoCRM Modules](https://docs.espocrm.com/development/modules/) | Thư mục extension và override order; cần kiểm thử xung đột của pack thực tế |
| <a id="r03"></a>R03 | [Frappe CRM frontend package](https://raw.githubusercontent.com/frappe/crm/develop/frontend/package.json) | Vue/Vite và scripts; không xác minh toàn backend bằng file này |
| <a id="r04"></a>R04 | [Frappe DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes) | Mô hình metadata; không phải cam kết mọi customization upgrade-safe |
| <a id="r05"></a>R05 | [Odoo CRM module 19.0](https://github.com/odoo/odoo/tree/19.0/addons/crm) | Cấu trúc module và nghiệp vụ CRM; nhánh tham khảo, không khẳng định latest |
| <a id="r06"></a>R06 | [SuiteCRM extension structure](https://docs.suitecrm.com/8.x/developer/extensions/extension-structure/) | Phân vùng frontend/backend/config và DI; không benchmark |
| <a id="r07"></a>R07 | [HubSpot Associations](https://developers.hubspot.com/docs/api-reference/latest/crm/associations/associate-records/guide) | Quan hệ có nhãn/hướng; URL v4 chuyển sang tài liệu mới khi đối chiếu, version triển khai cần pin riêng |
| <a id="r08"></a>R08 | [Chatwoot ContactInbox model](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/app/models/contact_inbox.rb) | Liên kết contact/inbox/source và unique index; đề xuất tenant/workspace là bổ sung của dự án |
| <a id="r09"></a>R09 | [Chatwoot API Channel](https://www.chatwoot.com/hc/user-guide/articles/1677839703-how-to-create-an-api-channel-inbox) | Kênh tích hợp tùy biến; không có nghĩa hỗ trợ native mọi kênh Việt Nam |
| <a id="r10"></a>R10 | [Zalo OA khởi tạo ứng dụng và cấp quyền](https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195) | Cơ chế ứng dụng/OA; chưa thử tài khoản doanh nghiệp, không chứng minh quyền Zalo cá nhân |
| <a id="r11"></a>R11 | [Meta Messenger API — official Postman workspace](https://www.postman.com/meta/messenger-platform-api/documentation/iyp204x/messenger-platform-api) | Page messaging và điều kiện cửa sổ gửi; chính sách/permission cần xác minh theo app tại triển khai |
| <a id="r12"></a>R12 | [TikTok Business Messaging Education Hub](https://business-api.tiktok.com/portal/bm-api/education-hub) | API DM cho authorized Business Accounts; trang động, nội dung được tìm thấy qua chỉ mục tìm kiếm chính thức, chưa xác minh eligibility tài khoản Việt Nam |
| <a id="r13"></a>R13 | [Gmail push notifications](https://developers.google.com/workspace/gmail/api/guides/push) | Watch, history notification, renewal và khả năng mất/trễ; không phải body email trong mọi webhook |
| <a id="r14"></a>R14 | [Graph Outlook change notifications](https://learn.microsoft.com/en-us/graph/outlook-change-notifications-overview?tabs=http) | Subscription và phạm vi quyền mailbox; không tự đồng bộ shared mailbox bằng mọi delegated scope |
| <a id="r15"></a>R15 | [SuiteCRM frontend architecture](https://docs.suitecrm.com/8.x/developer/architecture/front-end-architecture/) | UI tái sử dụng và cấu hình; không suy ra mọi UI nghiệp vụ đều nên metadata hóa |
| <a id="r16"></a>R16 | [Twenty LICENSE](https://github.com/twentyhq/twenty/blob/main/LICENSE) | Phải kiểm tra điều khoản theo thành phần; không đưa kết luận pháp lý chỉ từ tên repo |
| <a id="r17"></a>R17 | [Chatwoot LICENSE](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/LICENSE) | MIT phần ngoài ngoại lệ; enterprise và dependency có điều khoản riêng |
| <a id="r18"></a>R18 | [Salesforce record-triggered automation](https://architect.salesforce.com/docs/architect/decision-guides/guide/record-triggered.html) | Quy tắc governance/entrypoint; không có mã nguồn nội bộ của nền tảng |
| <a id="r19"></a>R19 | [Microsoft organize solutions](https://learn.microsoft.com/en-us/power-platform/alm/organize-solutions) | Base solution và app extension; áp dụng nguyên tắc, không sao chép quy trình enterprise quá nặng |
| <a id="r20"></a>R20 | [Microsoft solution concepts](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm) | Source/deployment managed-unmanaged; không định giá sản phẩm |

### D.6 Ma trận thay đổi so với bản hợp nhất 1.1

| Nội dung cũ | Đánh giá và bổ sung bản 1.2 | Lý do |
| --- | --- | --- |
| Modular monolith + industry pack | Giữ; thêm code boundary, pack manifest và CI ở 2.8 | Phù hợp quy mô, nhưng chỉ nói “modular” chưa ngăn coupling/đụng ngành |
| Inbox tập trung ở 3.3 | Giữ, mở rộng 2.7 và 3.12 thành năm kênh có capability | Thiếu hợp đồng ingest/send, policy và coverage dễ hứa quá API |
| Contact 360 và merge | Bổ sung identity scoped, review/undo, association roles | Cùng tên/email không bảo đảm cùng người hoặc quyền đọc chung |
| Webhook retry/outbox | Bổ sung durable ACK, echo, unknown outcome, backfill | Retry mù có thể gửi trùng; ACK sớm có thể mất tin |
| FR01–29, UC01–16 | Thêm FR30–40, UC17–22 | Chuyển yêu cầu Omni thành hành vi kiểm thử được |
| Schema nghiệp vụ nền | Thêm 15 bảng Omni ở 5.16 và API contracts 5.17 | Activities đơn lẻ không đủ message status, identities và sync checkpoints |
| Quyền/DR/BI | Thêm 6.5, 7.6, 8.4 | Search, AI, restore và dashboard có thể làm lộ hoặc đếm sai dữ liệu |
| UAT và 90 ngày | Thêm OC01–24 và gate phê duyệt kênh | Kết nối API được duyệt là phụ thuộc bên ngoài, không tự giải quyết bằng lập trình |
| TCO/ROI | Thêm 10.6 và ví dụ chi phí có giả định | Omni tạo chi phí vận hành liên tục; không suy doanh thu từ số tin nhắn |

Quyết định hiện tại: ưu tiên kiến trúc core + pack và Omnichannel có adapter; chọn nền tảng cụ thể sau PoC cùng bộ OC tests. Phiên bản 1.3 đã tích hợp các kết luận rà soát vào phần thân; đây là tài liệu thiết kế/ước lượng/nghiệm thu, chưa là chứng nhận hệ thống đã triển khai.


<a id="phu-luc-e"></a>

## PHỤ LỤC E HỢP NHẤT CHÍNH THỨC PHIÊN BẢN 1.3

### E.1 Vì sao có nhiều bản và cách sử dụng từ nay

Các báo cáo phản biện được tạo để phân biệt tài liệu nguồn với kết luận đánh giá, giữ bằng chứng/giới hạn và nghiên cứu song song theo vai. Ở vòng trước, kết quả đã dừng ở báo cáo riêng mà chưa cập nhật Master; đó là thiếu bước hợp nhất, không phải yêu cầu anh phải vận hành nhiều bản đặc tả.

Từ phiên bản 1.3 chỉ dùng `CRM_MASTER_BRD_SRS_HOP_NHAT.md`. Bản này tích hợp lý do/liên kết của 40 FR, quy tắc 22 UC, dữ liệu, quyền, phạm vi và nghiệm thu. Không ghép mọi nhận xét vào như yêu cầu bắt buộc: loại các kết luận không có bằng chứng (90%, tiết kiệm40%, ngưỡng SLA/quota cứng), không đưa những sửa nguy hiểm (dừng mọi SLA theo contact, sticky trước quyền, tự xóa chênh lệch, clone để làm đẹp cycle). Tính năng chưa cần giữ P1/P2 ngay trong Master; dữ kiện chưa biết ở A.6.

### E.2 Hồ sơ lịch sử đã hợp nhất

| Tệp nguồn lịch sử | Lý do tạo | Kết quả dùng trong Master |
| --- | --- | --- |
| gemini-code-1792004600780.md | Báo cáo kiểm toán do người dùng cung cấp | Giữ vấn đề có căn cứ; sửa suy diễn/phương án gây lỗi mới |
| PHAN_TICH_PHAN_BIEN_CRM_2026-10-15.md | Đối chiếu báo cáo với SRS và nguồn chính thức | Sửa pipeline/SLA/routing/masking/payment/schema/phạm vi |
| RESEARCH_CEO_CRM_2026-10-15.md | Nghiên cứu song song góc điều hành/tài chính | Hợp đồng, legal entity, money/commission, cost/media, 26 ca chuyên đề |
| RESEARCH_CMO_CRM_2026-10-15.md | Nghiên cứu góc marketing | Handover, RFM, scope metrics, attribution, closed-loop, 26 ca chuyên đề |
| RESEARCH_CX_CRM_2026-10-15.md | Nghiên cứu góc trải nghiệm/dịch vụ | NRT/entitlement/promises/recovery/offboarding, 24 ca chuyên đề |
| CRM_RESEARCH_REVIEW_CEO_CMO_CX_2026-10-15.md | Tổng hợp nghiên cứu và kiểm tra liên kết | 40 FR rationale/dependencies; 22 UC; INT01–30; quyết định và nguồn |
| CRM_DOCUMENT_INDEX.md; CRM_CAP_NHAT_V1_2.md | Chỉ dẫn bản cũ và nhật ký 1.2 | Giữ lịch sử; Master hiện tại đã tự chứa version/phạm vi/nguồn |

Các tệp trên và snapshot các bản cũ ở `docs/archive/research-2026-10-15/`; không là bản chính thức song song. Không cần đọc chúng để nắm yêu cầu hiện hành. Tệp nguồn gốc trong docs vẫn là bằng chứng lịch sử, không phải các phiên bản Master mới.

### E.3 Quyết định và lý do hợp nhất

| Mã | Thay đổi cần chốt | Lý do ưu tiên / owner | Tác động |
| --- | --- | --- | --- |
| CR01 | Một mô hình scope + legal entity + cross-scope links hợp lệ | Chặn lộ dữ liệu/sai tài chính; Tech lead + Finance + Privacy | Ch.2/5/6, FR01/16/21/30/37 |
| CR02 | Canonical schema và dictionary, loại mô tả chồng lấn | Dev không tự đoán field/index/FK; BA + Tech | ERD/5.13/5.16/API/UAT |
| CR03 | Demand episode và Marketing→Sales handover | Đo chất lượng lead và giữ lịch sử; CMO + Sales | FR04/05/28/29, UC01/03 |
| CR04 | Receipt–allocation–invoice–reconciliation | Tránh sai tiền và commission; Finance | FR15–17, UC06/07/13 |
| CR05 | SLA subject, NRT, promised update, calendar | Chặn bỏ quên khách/đóng nhầm timer; CX + Sales Ops | FR05/18/35/36/39 |
| CR06 | SOW/approval dependency/handoff/success plan | Bảo toàn cam kết và margin; Sales + AM + CMO | FR14/15/22–26 |
| CR07 | Entitlement/defect/change/recovery/offboarding | Phục vụ và khắc phục có trách nhiệm; CX + Delivery | FR15/18/19, UC08–10 |
| CR08 | Cost/commitment/funding và phép chi media | Không lãi giả hoặc dùng nhầm tiền khách; Finance + CMO | FR14/16/23/25/26 |
| CR09 | KPI dictionary và bốn scope tài chính | Dashboard không dẫn tới quyết định sai; CMO + Finance | FR03/28/29, Ch.8 |
| CR10 | Quyền team/grants/role conflict/field ACL | Bàn giao đủ mà không mở rộng dữ liệu; Privacy + Ops | FR08/21/37, Ch.6 |
| CR11 | Connector capability và recovery contract | Không hứa quyền/lịch sử API chưa có; Integration owner | FR30–40, UC17–21 |
| CR12 | Consent/purpose/endpoint + send arbitration | Ngăn gửi sai/trùng và không mất suppression; CMO + Privacy | FR02/09/13/34/37 |
| CR13 | PoC/observability/restore/go-live ownership | Chứng minh vận hành trước mở rộng; Tech + Ops + QA | Ch.7/9/10 |
| CR14 | AI evaluation/approval binding | Sai gợi ý không thành cam kết/chi tiền; AI owner + nghiệp vụ | FR11–13; P0 guard khi bật AI |

CR01–12 đã được tích hợp ở cấp quy tắc thiết kế trong phiên bản 1.3; tham số và cấu hình thực tế cần chốt trước khi phát triển phần tương ứng; không có nghĩa phải xây toàn bộ connector/AI ngay trong MVP. CR13 bắt đầu sớm và xuyên suốt. CR14 kích hoạt khi có AI. Ưu tiên độ đúng của chuỗi giao dịch hơn thêm màn hình hoặc cắt số bảng cho đẹp.

### E.3b Quan sát mã nguồn và giới hạn

Phần này chỉ nêu các quan sát đã có nguồn; lựa chọn thiết kế của dự án được ghi riêng. Bảng không phải xếp hạng sản phẩm.

| Nguồn đã đọc | Quan sát cụ thể | Áp dụng/điều kiện PoC |
| --- | --- | --- |
| [Frappe CRM crm_deal.py](https://raw.githubusercontent.com/frappe/crm/develop/crm/fcrm/doctype/crm_deal/crm_deal.py) | Có primary contact, status history, lost reason, forecasting và SLA. `share_with_agent` xử lý DocShare khi đổi owner; `contact_exists` tìm contact bằng email/phone | Học lịch sử và gate. Không sao chép identity match hoặc sharing rồi mặc định đáp ứng workspace/Account Team của dự án; đọc call chain và test quyền thực |
| [EspoCRM Roles](https://docs.espocrm.com/administration/roles-management/) | Tài liệu mô tả gộp nhiều vai trò theo quyền rộng hơn | Khác yêu cầu Deny-wins của SRS. PoC role conflict bắt buộc; đây là khác semantics, không phải kết luận EspoCRM có lỗi bảo mật |
| [AWS outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Pattern ghi dữ liệu/outbox cùng transaction, xử lý lặp ở consumer | Áp dụng nhất quán command→event; không cần thêm message broker phức tạp khi chưa có nhu cầu |
| [ERPNext payment_entry.py](https://raw.githubusercontent.com/frappe/erpnext/version-15/erpnext/accounts/doctype/payment_entry/payment_entry.py) | `validate_duplicate_entry` kiểm trùng dòng References của một payment; có validation allocation/reference | Không được suy hàm này chống cùng bank transaction qua API và file. PoC cross-source và concurrent allocations vẫn bắt buộc |
| [ERPNext Payment Reconciliation](https://docs.frappe.io/erpnext/payment-reconciliation) | Liên kết khoản tiền đã có với hóa đơn, không ghi khoản thu ngân hàng lần hai | Áp dụng tách receipt khỏi invoice mapping. Không tự suy hỗ trợ đầy đủ nghĩa vụ hóa đơn/commission agency Việt Nam |
| [Odoo crm_lead.py 19.0](https://raw.githubusercontent.com/odoo/odoo/19.0/addons/crm/models/crm_lead.py) | `crm.lead` có UTM/activity, company/team/user, stage và dữ liệu forecast | Học source capture và stage history; một trường UTM hiện tại không thay touchpoint ledger; không mặc định multi-company bằng client-workspace isolation |
| [Odoo sale_order.py 18.0](https://raw.githubusercontent.com/odoo/odoo/18.0/addons/sale/models/sale_order.py) | Nhánh CEO đọc `action_confirm` và các điểm chuyển trạng thái | Confirm sale không tự chứng minh đủ ứng trước, thẩm quyền và capacity. Không ghép hành vi branch18/19 thành một bản cài đã kiểm thử |
| [Chatwoot sla_policy.rb](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/enterprise/app/models/sla_policy.rb) | Có first-response, next-response, resolution thresholds và business hours | Cơ sở thiết kế NRT; không sao chép ngưỡng, không coi đây là SLA miễn phí trong mọi edition |
| [Chatwoot applied_sla.rb](https://github.com/chatwoot/chatwoot/blob/develop/enterprise/app/models/applied_sla.rb) | Nhánh CX đọc NRT theo waiting_since và trạng thái có thể còn lịch sử missed | Giữ breach history; cần test reopen/pause/ticket subject của dự án riêng |
| [Chatwoot ContactInbox](https://github.com/chatwoot/chatwoot/blob/develop/app/models/contact_inbox.rb) | Model ánh xạ contact–inbox–source, không chỉ một phone trên Contact | Áp dụng identity theo kênh; không coi HMAC widget là xác minh danh tính mọi kênh |
| [Chatwoot Enterprise LICENSE](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/enterprise/LICENSE) | Điều kiện production/subscription/seat khác quyền dùng code để phát triển/thử nghiệm | Phải kiểm edition và hợp đồng triển khai; code công khai không tự là quyền dùng miễn phí |

### E.4 Nguồn chuyên môn bổ sung và ý nghĩa

| Nguồn | Điều dùng trong đánh giá | Giới hạn |
| --- | --- | --- |
| [HubSpot lifecycle stages](https://knowledge.hubspot.com/records/use-lifecycle-stages?tab=content) | Phân biệt lifecycle/lead status và thời gian stage; tham chiếu cho handover | Không ép doanh nghiệp dùng toàn bộ stage của vendor |
| [Mautic Campaign Builder](https://kb.mautic.org/article/creating-campaigns.html) và [Email 7.2](https://docs.mautic.org/en/7.2/channels/emails.html) | Decision/action/condition và quy tắc gửi; tham chiếu journey | Tài liệu khác phiên bản/ngày; chưa chạy Mautic, không tuyên bố đã đọc source Mautic |
| [Microsoft SLA](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/define-service-level-agreements) | KPI có start/calendar/pause khác nhau | Không sao chép ngưỡng hoặc semantics sang CRM khác mà không PoC |
| [Bain Closing the loop](https://media.bain.com/Images/LOYALTY_INSIGHTS_Closing_the_loop.pdf) | Phương pháp liên hệ/khắc phục và học hỏi từ feedback | Tài liệu phương pháp, không phải benchmark ROI 2026 |
| [Qualtrics CES](https://www.qualtrics.com/en-au/articles/customer-experience/customer-effort-score/) | Đo công sức của khách ở tương tác cụ thể | Chỉ thêm khi có owner cải tiến; không cộng cơ học CES/CSAT/NPS |
| [Meta Blueprint CRM](https://www.facebookblueprint.com/student/activity/603002-improve-lead-quality-with-meta-conversions-api-for-crm) | Landing page mô tả mục tiêu kết nối CRM và lead quality | Chưa chứng minh payload/quyền/hiệu suất tài khoản hiện tại |
| [Facebook greeting Help](https://www.facebook.com/help/1698046970464236/) | Nhánh CX ghi nhận nội dung greeting tự động; lượt kiểm lại của agent tổng hợp chuyển login/blocked | Bằng chứng truy cập không ổn định; không dùng làm xác nhận API window hiện hành hoặc khảo sát cộng đồng |
| [Meta Lead Generation Guide](https://about.fb.com/ltam/wp-content/uploads/sites/14/2023/11/LeadGenerationGuide.pdf) | Hướng tích hợp lead với CRM; mức truy cập khác nhau giữa các nhánh | Tài liệu 2023, không đủ chứng minh entitlement/API ngày triển khai |

Nguồn PostgreSQL, AWS, OWASP, NIST, Gmail, Microsoft Graph và W3C được dẫn ngay tại từng nhận định kỹ thuật ở Chương 2/6/7 và E.5. Các source register chuyên đề giữ đường dẫn/hàm đã đọc và giới hạn riêng; không dùng nguồn không mở được như bằng chứng đã xác minh đầy đủ.

### E.5 Bằng chứng kỹ thuật bổ sung

| Nguồn | Nguyên tắc dùng | Giới hạn |
| --- | --- | --- |
| [AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Ghi nghiệp vụ/outbox cùng transaction; consumer idempotent | Không yêu cầu AWS/microservices |
| [OWASP API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) | Kiểm quyền object/action ở backend | Không thay test quyền theo schema dự án |
| [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | RAG không tự loại prompt injection; tool gate | Không phải chứng nhận AI an toàn |
| [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | Quản trị rủi ro/đo lường GenAI | Eval theo tác vụ và dữ liệu có quyền |
| [Gmail push](https://developers.google.com/workspace/gmail/api/guides/push) | Watch/history/checkpoint và sync bù | Kiểm scope/quota/version khi kết nối |
| [Microsoft Graph Outlook](https://learn.microsoft.com/en-us/graph/outlook-change-notifications-overview) | Subscription và mailbox permissions | Không suy shared mailbox dùng mọi quyền delegated |
| [WCAG2.2](https://www.w3.org/TR/WCAG22/) | Mục tiêu accessibility phù hợp, kiểm keyboard/focus/forms | Không tuyên bố đạt chỉ vì có label |
| [Chính phủ NĐ70/2025 về hóa đơn](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-70-2025-nd-cp-sua-doi-bo-sung-quy-dinh-ve-hoa-don-chung-tu-11925032321512617.htm) | Không mặc định mọi tạm ứng marketing được chờ nghiệm thu mới xuất hóa đơn | Kiểm bản chất dịch vụ/văn bản áp dụng tại triển khai |

### E.6 Độ chắc chắn và lịch sử thay đổi

Đây là hợp nhất tài liệu/desk research và đọc một số file mã nguồn, chưa cài/chạy benchmark hay chứng nhận mọi edition. Ba agent đã hoàn thành nghiên cứu ban đầu; lượt phản biện thứ hai bị giới hạn sử dụng, agent tổng hợp tự kiểm cuối. Không có kết quả lượt hai được dùng như bằng chứng. Facebook bị giới hạn đăng nhập/truy cập, không có khảo sát đại diện nhóm cộng đồng. Branch GitHub có thể thay đổi; PoC phải pin release/commit/license/tài khoản và UAT.

| Phiên bản | Ngày | Nội dung và thẩm quyền sử dụng |
| --- | --- | --- |
| 1.2 | 15/10/2026 | Bản trước rà soát chuyên sâu; đã lưu lịch sử |
| 1.3 | 15/10/2026 | Baseline trước phản biện vòng hai, được lưu snapshot; nội dung phù hợp kế thừa1.4 |
| 1.4 | 15/10/2026 | Baseline lịch sử đã được kiểm định ở bản1.5; snapshot lưu trong archive |
| 1.5 | 15/10/2026 | Bản có báo cáo kiểm định, chưa áp patch; đã lưu snapshot lịch sử |
| 1.6 | 15/10/2026 | Master hiện hành:20 module BA, áp15 nhóm sửa đổi và hai hiệu chỉnh, hợp nhất17 nhóm test vào9.14; nghiệm thu thực thi theoChương 9 |

NFR99,9% là mục tiêu cần năng lực vận hành; RTO4h phục hồi thảm họa không bảo đảm vẫn đạt SLO tháng. Bộ kiểm tải phải chốt dataset/shape/role/capability; chọn ACK nội bộ p95≤1giây cho kênh khi khả thi (NFR04 tổng≤2giây không thay timeout provider), báo riêng provider lag. Gate restore gồm suppression/deletion/cursor/outbox và đối soát tiền trước bật outbound; dữ liệu thiếu không coi0 hoặc healthy.

<a id="phu-luc-f"></a>

## PHỤ LỤC F CÁC THAY ĐỔI ĐÃ HỢP NHẤT TRONG ĐẶC TẢ BA1.6

Đây là nhật ký thay đổi đã áp dụng vào phần thân, không phải danh sách patch để người dùng tự dán. Snapshot1.5 giữ báo cáo kiểm định cũ ở `docs/archive/research-2026-10-15/CRM_MASTER_BRD_SRS_HOP_NHAT_v1.5.md`. Bản chính thức hiện hành luôn là tệp Master tại thư mục gốc.

| Thay đổi đã thực hiện | Module và vị trí quy định hiện hành | Ca kiểm chấp nhận |
| --- | --- | --- |
| Bổ sung20 hồ sơ module có chức năng/màn hình/dữ liệu/quyền/ngoại lệ/liên kết | Danh mục3.0 và các khối M01–M20 tại phần nghiệp vụ/tích hợp/quyền | Mxx-AC theo từng module; trace FR/UC được giữ |
| Đồng bộ field intake Ticket: queue, request type và triage state; chưa rõ severity vẫn nhận vấn đề | M11;5.8, triage hoàn tất phải đủ severity/impact/urgency | M11-AC và kiểm intake Unknown/Pending có queue |
| W-F01 — Lead Unknown được vào queue/SLA; chỉ bắt B2B/B2C trước qualification/convert | M02; UC01/UC03;5.2 | WF-U01 |
| WF02 — Message gắn đúng subject/response episode; reply không dừng mọi SLA | M03/M11;5.17/5.18 | WF-U02 |
| WF03 — Commands, allowed transitions, guard và tác động cho các đối tượng lõi | M02/M07/M08/M09/M10/M11/M16;3.13.5 | WF-U03 |
| WF04 — Release profile và test applicability, tách N/A/Not Run/Deferred/Pass | Mọi module;9.5/9.11 | WF-U04; U19/U23-R/U23-L và nhóm theo profile |
| WF05 — Stable conversion key và logical unique SLA episode | M02/M11;5.5/5.16 | WF-U05 |
| DB01 — Policy pointer tới snapshot có version, không FK sang bảng không định nghĩa | M10;5.5/5.12 | FA01 |
| DB02 — Tách hoàn dư và hoàn allocated; sửa số dư và reservation headroom | M09;3.13.4/UC13/5.18 | FA04/FA05 |
| DB03 — Post và close khóa cùng kỳ; pending không giữ khóa đợi consumer | M09/M10;5.13/5.14 | FA02/FA03 |
| DB04 — Số tiền hữu hạn, currency allowlist/quantum, validate trước cast | M07/M09/M10/M17;5.1 | FA06 |
| SEC01 — Callback OAuth gắn actor/session/provider/account/scope | M19;2.6 | SEC-U01 |
| SEC02 — External account có namespace owner, activate/reconnect chống trùng scope | M19/M03;2.7/5.16 | SEC-U02 |
| SEC03 — Download gateway kiểm quyền hiện tại, thay raw URL cho tệp nhạy cảm | M03/M14/M20;FR37/UC12/5.16/6.2 | SEC-U03/U16 |
| SEC04 — Remote fetch có egress/redirect/IP/credential policy | M19/M03;FR40 | SEC-U04 |
| SEC05 — Email unsubscribe/bounce/complaint và sender activation | M03/M04/M20;FR34/5.18 | SEC-U05 |
| SEC06 — Grant authority và ngăn tự nâng quyền qua role/team/config | M14;5.18/6.1 | SEC-U06 |
| Hai hiệu chỉnh — Pipeline_Stages dùng một tên; U08 nêu đúng cọc/credit exception | M02/M08;5.5/9.5 | Kiểm dictionary/U08 |

**Trạng thái bàn giao:** các sửa đổi trên đã là đặc tả thiết kế hiện hành. Chưa chạy code/DDL/provider/UAT; các điều kiện phê duyệt cấu hình cụ thể vẫn theoA.6. Kỹ sư triển khai field/command/migration và QA thực hiện ca theo release profile; không ghi Pass chỉ vì nội dung đã được viết vào tài liệu.

<a id="phu-luc-g"></a>
## PHỤ LỤC G NGHIÊN CỨU PANCAKE VÀ OMNICHANNEL NGÀY 16/10/2026

Đã đọc tài liệu công khai để học hành vi sản phẩm, chưa dùng demo có đăng nhập hoặc API với tài khoản thật. Không suy đoán DB/queue/locking nội bộ Pancake. Giá, quyền gói, giới hạn tài khoản và hỗ trợ đủ năm kênh trong cùng inbox/API cần PoC. Báo cáo audit bản gửi đạt 54/100 là đánh giá bản gửi, không là điểm Master hoặc sản phẩm vendor.

| ID | Nguồn | Quan sát và áp dụng |
| --- | --- | --- |
| <a id="g01"></a>G01 | [Pancake giới thiệu](https://docs.pancake.biz/pancake/intro?lang=vi) | Inbox nhiều nền tảng, phân chia theo tỷ lệ/giờ/online; áp dụng cấu hình routing, không khẳng định thuật toán |
| <a id="g02"></a>G02 | [Pancake giao diện](https://docs.pancake.biz/pancake/st-f7/st-p4?lang=vi) | Assignee, người đang xem, màu trang; áp dụng badge/context ở FR32 |
| <a id="g03"></a>G03 | [Pancake phân quyền](https://docs.pancake.biz/pancake/st-f7/st-p8?lang=vi) | Quyền trang/tính năng và quyền nguồn Facebook; tham khảo scope thay vì role toàn cục |
| <a id="g04"></a>G04 | [Pancake hỗ trợ trả lời](https://docs.pancake.biz/pancake/st-f7/st-p3?lang=vi) | Mẫu/phím tắt/chủ đề và chèn/gửi; CRM đề xuất chèn nháp mặc định |
| <a id="g05"></a>G05 | [Pancake CRM changelog](https://docs.pancake.biz/crm/st-f6/st-p1?lang=vi) | Mục 16/09/2026: chọn survivor/field khi merge; áp dụng FR31 |
| <a id="g06"></a>G06 | [Zendesk routing](https://support.zendesk.com/hc/en-us/articles/4409149119514-About-omnichannel-routing) | Availability/capacity cho email/call/messaging; tham khảo FR35 |
| <a id="g07"></a>G07 | [Chatwoot customer context](https://www.chatwoot.com/hc/user-guide/articles/1677237449-lesson-3-b-mastering-core-features) | Merge contact giữ lịch sử; không suy ra thuật toán hay quyền từ mô tả này |
| <a id="g08"></a>G08 | [Zalo Tin Tư vấn](https://oa.zalo.me/home/documents/guides/tin-tu-van) | Chính sách eligibility/pricing phân biệt; áp dụng 3.12.12 |
| <a id="g09"></a>G09 | [Telegram Bot API](https://core.telegram.org/bots/api#setwebhook) | Secret token và update events; áp dụng connector verifier/dedup |
| <a id="g10"></a>G10 | [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322) | Header email; quy tắc gom an toàn là đề xuất riêng của CRM |

**Giới hạn xác minh:** Meta policy/webhook trả HTTP 429; tài liệu kỹ thuật webhook Zalo không đọc được trong lượt này. Không đưa message tag Meta hoặc thuật toán chữ ký Zalo chưa kiểm chứng thành yêu cầu triển khai cụ thể. API Pancake landing chưa cung cấp đủ nội dung để xác nhận coverage theo từng kênh. Không coi việc ecosystem có CRM, email hoặc call là bằng chứng một gói inbox hỗ trợ toàn bộ.

**Trạng thái CR-OMNI-20261016:** đã bổ sung nội dung nghiên cứu vào đúng FR và gate; routing/capacity, SLA, retention, chi phí và nhà cung cấp call vẫn cần cấu hình/phê duyệt theo A.6. Báo cáo chi tiết A/B/C và Mermaid là tài liệu review liên kết, không tạo baseline thứ hai.


<a id="phu-luc-h"></a>
## PHỤ LỤC H NGHIÊN CỨU GIAO VIỆC VÀ QUYẾT ĐỊNH HỢP NHẤT 1.7

CR-WORK-20261016, ngày 16/10/2026: chủ dự án yêu cầu hợp nhất vào Master. Nội dung normative đã nằm trong 3.14/4.23/5.20/6.6/7.7/8.5/9.16/A.7; phụ lục này lưu bằng chứng và tiêu chí chọn engine. Báo cáo nghiên cứu riêng không là baseline thứ hai. Nguồn là tài liệu công khai, chưa đăng nhập demo/benchmark/PoC; chưa xác nhận edition, giá hoặc API thực tế của doanh nghiệp.

### H.1 Pancake CRM và Pancake Work

**Quan sát:** Pancake CRM có module Nhiệm vụ, khu vực Công việc cá nhân, việc đang mở/quá hạn, phân loại, ưu tiên, người phụ trách/người liên quan, đối tượng CRM liên kết và nhắc việc. Trạng thái có thể cấu hình; một số trạng thái hệ thống không xóa được. [P01 — Nhiệm vụ](https://docs.pancake.biz/crm/st-f2/st-p8?lang=vi).

Pancake Work có bảng Kanban với thẻ/cột và kéo thả tiến độ. Đây là sản phẩm Work trong hệ sinh thái; không dùng bằng chứng này để kết luận toàn bộ chức năng đã có trong CRM Tasks. [P02 — Kanban](https://docs.pancake.biz/pancakework/st-f3/st-p3?lang=vi).

**Phân tích BA:** cách tổ chức này làm điểm bắt đầu công việc gần hồ sơ khách hàng, đồng thời có bề mặt cộng tác riêng. CRM của dự án nên học đường vào My Work và liên kết nhiệm vụ với lead/deal/ticket. Tuy nhiên phải làm rõ mapping trạng thái, notification và quyền khi nối với công cụ Work.

**Cần PoC:** một người nghỉ việc thì task và reminder đi đâu; kéo thả có vượt approval không; comment/file có chia sẻ ra khách không; đồng bộ task giữa CRM và Work có đủ chiều/API hay chỉ thông báo. Chưa có bằng chứng trong các trang đã đọc để xác nhận đầy đủ dependency, effort planning và portfolio của toàn bộ gói CRM.

### H.2 Bitrix24 — giao việc có vai trò và kiểm soát hoàn thành

**Quan sát:** task có creator, một assignee chính, participants và observers. Chọn nhiều assignees khi tạo có thể sinh các task riêng. Có lựa chọn yêu cầu kết quả khi hoàn thành, gửi kết quả để người giao duyệt và cho phép người làm đổi deadline. [B01 — Create a task](https://helpdesk.bitrix24.com/open/25865519/).

Tài liệu phân biệt vai trò tham gia task với quyền sửa/giao việc; quyền của dự án và quyền chung cần xét cùng nhau. [B02 — Task permissions](https://helpdesk.bitrix24.com/open/25908803/). Template hỗ trợ tái sử dụng thông tin và người tham gia. [B03 — Task templates](https://helpdesk.bitrix24.com/open/20883624/).

**Phân tích BA:** đây là mẫu tham khảo phù hợp nhất cho quy trình quản lý giao việc nội bộ của dự án: trách nhiệm chính rõ, phối hợp rõ, giao xong vẫn có bước kiểm kết quả. Không nên sao chép nguyên quy tắc quyền cấp trên sang mô hình agency nhiều workspace; quản lý nhân sự chưa chắc được xem tài liệu của mọi khách.

**Đề xuất áp dụng:** tách `creator_id`, `requester_id`, `assignee_id`, `reviewer_id` và collaborators/watchers. Chỉ thiết lập reviewer bắt buộc cho loại việc cần duyệt; không bắt việc nhắc gọi đơn giản đi qua nhiều bước.

### H.3 HubSpot — tổ chức công việc theo hoạt động CRM

**Quan sát:** task có người phụ trách, ưu tiên, hạn, reminder và liên kết record; cũng tạo được việc không liên kết record. Recurrence có điều kiện seat và cách sinh tiếp được tài liệu mô tả. [H01 — Create tasks](https://knowledge.hubspot.com/tasks/create-tasks?service=content_creation).

Task queue của HubSpot là cơ chế nhóm/lọc/chia sẻ; queue dùng chung cho phép nhiều người xem và hoàn thành tập việc. Workflow/sequence có thể thêm task vào queue khi gói hỗ trợ. [H02 — Task queues](https://knowledge.hubspot.com/tasks/use-task-queues).

**Phân tích BA:** phù hợp thiết kế một màn hình tập trung việc cần làm, tạo follow-up ngay từ record. Tuy nhiên nhãn “queue” không chứng minh đã có reserve capacity hoặc exclusive claim. CRM này phải tự định nghĩa rõ task được chia sẻ khác task chưa có người chịu trách nhiệm.

**Đề xuất áp dụng:** tạo việc ít thao tác; context CRM tùy chọn; saved views là truy vấn, không phải bảng Task thứ hai. Không lấy việc gán queue làm bằng chứng một người đã nhận trách nhiệm.

### H.4 Salesforce — hàng chờ và quyền sở hữu công việc

**Quan sát:** Task có thể nằm trong queue; thông báo/reminder giao việc chỉ phát khi chuyển từ queue sang người dùng cụ thể. Đổi owner của record cha không tự chuyển các task đang ở queue. Giao cho nhiều người tạo assignment riêng. [S01 — Considerations for Using Tasks](https://help.salesforce.com/s/articleView?id=sales.task_considerations.htm&language=en_US&type=5).

Action Plans của các cloud/edition được liệt kê hỗ trợ template giao task vào queue để thành viên nhận ownership; không phải tính năng mặc định mọi Salesforce CRM. [S02 — Action Plan Tasks to Queues](https://help.salesforce.com/s/articleView?id=ind.fsc_action_plans_queues.htm&language=en_US&type=5).

**Phân tích BA:** trách nhiệm queue và trách nhiệm cá nhân là hai giai đoạn. Hệ thống của dự án cần quản lý tuổi việc chưa nhận, người quản queue và escalation riêng; nếu chỉ đợi reminder của assignee thì việc có thể nằm vô hạn ở queue.

**Đề xuất áp dụng:** thêm `queue_entered_at`, `assignment_offered_at`, `accepted_at`, `queue_manager_id`; chuyển account owner không tự viết lại task ownership. Công việc đang xử lý cần workflow bàn giao riêng.

### H.5 Zoho CRM + Zoho Projects — phân tách bán hàng và thực thi

**Quan sát:** Zoho CRM có Tasks/Meetings/Calls và reminder/recurrence. [Z01 — Tasks FAQ](https://help.zoho.com/portal/en/kb/crm/faqs/activity-management/articles/faqs-tasks-module). Zoho Projects cung cấp task/subtask và recurring work. [Z02 — Tasks and subtasks](https://www.zoho.com/projects/task-details.html).

Tích hợp CRM–Projects hỗ trợ tạo/liên kết project, đồng bộ một số trường task và comment hai chiều. Tài liệu nêu giới hạn: đổi hạn vượt lịch strict project hoặc mở subtask khi parent còn đóng có thể bị từ chối. [Z03 — CRM integration](https://help.zoho.com/portal/en/kb/projects/integration/zoho-apps/articles/crm-integration).

**Phân tích BA:** việc hiển thị và sửa task từ CRM không khiến CRM tự trở thành nơi có quyền cuối cùng với mọi quy tắc dự án. Integration phải xử lý trạng thái “đề nghị thay đổi đang chờ hệ nguồn chấp nhận”, không báo thành công giả rồi âm thầm ghi đè lại.

**Đề xuất áp dụng:** nếu dùng PMS ngoài, lưu source system/external ID/version, sync operation và lỗi nghiệp vụ. Một request đổi hạn từ CRM được gửi tới hệ nguồn chuẩn; chỉ cập nhật canonical state khi nguồn chấp nhận hoặc dùng optimistic UI có nhãn pending rõ ràng.

### H.6 Odoo CRM + Project — quản lý thực thi trong hệ sinh thái

**Quan sát:** Odoo Project có task/subtask, dependency, recurring task; dashboard tập hợp milestone, giờ, chi phí và doanh thu theo cấu hình. [O01 — Project](https://www.odoo.com/documentation/19.0/applications/services/project.html), [O02 — Dashboard](https://www.odoo.com/documentation/19.0/applications/services/project/project_management/project_dashboard.html).

Odoo phân biệt stage trên board và status của task. [O03 — Stages/statuses, bản tài liệu 19.0](https://www.odoo.com/documentation/19.0/nl/applications/services/project/tasks/task_stages_statuses.html). Recurrence tạo lần tiếp sau khi việc trước Done/Canceled; một số thành phần như timesheet/comment/subtask không được sao chép. [O04 — Recurring tasks](https://www.odoo.com/documentation/19.0/applications/services/project/tasks/recurring_tasks.html). Dependency chặn successor tới khi predecessor đạt trạng thái đủ điều kiện của sản phẩm. [O05 — Dependencies, saas-19.3](https://www.odoo.com/documentation/saas-19.3/applications/services/project/tasks/task_dependencies.html).

**Phân tích BA:** thiết kế stage tùy chỉnh cần đi cùng lifecycle chuẩn để thống kê không phụ thuộc tên cột. Recurrence “sau khi xong” không thay cho lịch “mỗi thứ Hai” dù việc tuần trước còn mở. Không mặc định Cancelled của predecessor là đã đáp ứng điều kiện nghiệp vụ; phải có waiver riêng khi dùng cho báo giá/QA/launch.

**Đề xuất áp dụng:** stage riêng theo team; canonical lifecycle ổn định; dependency P0 chỉ Finish-to-Start; tiến độ dự án dựa đầu ra được chấp nhận hoặc cách tính có version, không suy từ số thẻ chuyển Done.

### H.7 Dynamics 365 — hoạt động, ownership và danh sách việc tiếp theo

**Quan sát:** Sales có work list/Up next và xử lý hoạt động trong bối cảnh khách; tài liệu phân biệt skip/snooze theo loại hoạt động. [D01 — Work list / Up next](https://learn.microsoft.com/en-us/dynamics365/sales/connect-with-customers). Task API của Dataverse là loại activity, có owner là user/team và liên kết regarding tới đối tượng khác. [D02 — Task EntityType](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/task?view=dataverse-latest).

**Phân tích BA:** user/team ownership, business unit và record liên quan là các chiều khác nhau. Cần bề mặt “việc tiếp theo” nhất quán nhưng không nên gom task, meeting, ticket và call vào một state machine chung.

**Đề xuất áp dụng:** My Work là projection từ Task và nghĩa vụ CRM, có loại nguồn và command đúng nguồn. Snooze reminder chỉ lùi thông báo; không mặc định dời contractual due hoặc xóa lịch sử trễ.

### H.8 So sánh theo mô hình — không phải bảng xếp hạng mua sắm

| Hệ sinh thái | Mô hình được nguồn thể hiện | Điều đáng học | Điều phải kiểm trước chọn |
| --- | --- | --- | --- |
| Pancake | CRM Tasks + sản phẩm Work | Công việc cá nhân gần hồ sơ khách | API và đồng bộ giữa hai sản phẩm |
| Bitrix24 | CRM cùng Tasks/Projects | Role công việc, review, delegation | Quyền thực tế theo plan/project và isolation |
| HubSpot | CRM activities, task views/queues | Tạo nhanh, follow-up, xử lý danh sách | Queue semantics, seat/workflow entitlement |
| Salesforce | Activity/task ownership, queue; Action Plans theo cloud | Nhận ownership và quy trình dựa template | Edition, behavior thông báo khi task chưa có owner |
| Zoho | CRM + Projects tích hợp | Tách sales khỏi delivery, integration có quy tắc | Field sync, conflict, quyền và license hai bên |
| Odoo | Project trong hệ sinh thái app | Stage/status, dependency, effort/project reporting | Version, module/edition, cấu hình kế toán/planning |
| Dynamics 365 | Activity + user/team ownership + work list | Context và việc tiếp theo, metadata ownership | App/license, security role và tùy biến |

Không dùng dấu “không có” cho Gantt, portfolio, approval hoặc recurrence của một sản phẩm nếu các nguồn đã đọc chưa chứng minh sự vắng mặt. Các điểm trên là trọng tâm học thiết kế; chưa đủ cơ sở chốt tổng chi phí hoặc sản phẩm tốt nhất.

### H.9 PoC và quyết định build/buy

Chấm trên quy trình thực, không trên demo do vendor chọn. Nhập cùng một bộ dữ liệu giả lập: 3 team, 2 workspace khách, 1 internal project, 30 task, 2 recurring rules, 2 reviewers, một người nghỉ việc và một task hạn chế quyền.

| Nhóm | Trọng số đề xuất | Bằng chứng cần |
| --- | ---: | --- |
| Giao/nhận/review và ngoại lệ | 25 | Thực hiện scenario, lịch sử quyết định, không bypass bằng board |
| Quyền, audit, cô lập dữ liệu | 20 | Cross-workspace/file/search/export tests |
| Kết nối CRM và API/portability | 20 | Task/link/status migration, API limit, source authority, export |
| Trải nghiệm cá nhân/team | 15 | Người pilot tự hoàn thành các việc chính, số bước và lỗi |
| Planning/reporting | 10 | Metric đúng, coverage dữ liệu, parent/child không double count |
| TCO/vận hành | 10 | Báo giá theo user/app/API/storage, admin effort, support/exit |

Mỗi tiêu chí chấm 0–5 dựa bằng chứng; unknown để trống và báo coverage, không tự chấm 0 hoặc 5. Tính tổng chỉ khi đủ coverage tối thiểu do PO chốt. Isolation sai, không xuất được dữ liệu cần thiết, task ownership mơ hồ hoặc không có cách giữ lịch sử là gate fail dù tổng điểm cao.

TCO 36 tháng = triển khai/migration + license/app add-on + integration/API/storage + vận hành/đào tạo + nâng cấp/support + chi phí exit. Chưa có báo giá nên không đưa con số tiết kiệm hoặc ngày công giả thành dự toán được cam kết.

### H.10 Danh mục nguồn và giới hạn xác minh

Các ID dưới là nguồn của quan sát, không chứng nhận thiết kế đề xuất. Nguồn chính thức được đối chiếu ngày 16/10/2026; phiên bản/gói có thể thay đổi khi triển khai.

| ID | Nguồn | Phạm vi bằng chứng |
| --- | --- | --- |
| P01 | [Pancake CRM Tasks](https://docs.pancake.biz/crm/st-f2/st-p8?lang=vi) | Module và hành vi nhiệm vụ; nội dung lập chỉ mục, open page trả body hạn chế |
| P02 | [Pancake Work Kanban](https://docs.pancake.biz/pancakework/st-f3/st-p3?lang=vi) | Board Work; không tự thuộc CRM Tasks |
| B01 | [Bitrix24 Create a task](https://helpdesk.bitrix24.com/open/25865519/) | Role, task riêng cho nhiều assignees, tùy chọn review/deadline |
| B02 | [Bitrix24 Task permissions](https://helpdesk.bitrix24.com/open/25908803/) | Quyền task/project; plan cần kiểm |
| B03 | [Bitrix24 Templates](https://helpdesk.bitrix24.com/open/20883624/) | Template nhiệm vụ |
| H01 | [HubSpot Create tasks](https://knowledge.hubspot.com/tasks/create-tasks?service=content_creation) | Task fields, record optional, recurrence/seat |
| H02 | [HubSpot Task queues](https://knowledge.hubspot.com/tasks/use-task-queues) | Group/share semantics; workflow subscription |
| S01 | [Salesforce Task considerations](https://help.salesforce.com/s/articleView?id=sales.task_considerations.htm&language=en_US&type=5) | Queue ownership/notifications và task assignment |
| S02 | [Salesforce Action Plans queues](https://help.salesforce.com/s/articleView?id=ind.fsc_action_plans_queues.htm&language=en_US&type=5) | Cloud/edition-specific feature |
| Z01 | [Zoho CRM Tasks FAQ](https://help.zoho.com/portal/en/kb/crm/faqs/activity-management/articles/faqs-tasks-module) | Tasks và hoạt động CRM |
| Z02 | [Zoho Projects Tasks](https://www.zoho.com/projects/task-details.html) | Tasks/subtasks/recurrence ở Projects |
| Z03 | [Zoho CRM–Projects integration](https://help.zoho.com/portal/en/kb/projects/integration/zoho-apps/articles/crm-integration) | Fields sync và giới hạn thực thi |
| O01 | [Odoo 19 Project](https://www.odoo.com/documentation/19.0/applications/services/project.html) | Phạm vi module Project |
| O02 | [Odoo 19 Dashboard](https://www.odoo.com/documentation/19.0/applications/services/project/project_management/project_dashboard.html) | Dashboard, milestone/effort/financial context |
| O03 | [Odoo 19 stages/statuses](https://www.odoo.com/documentation/19.0/nl/applications/services/project/tasks/task_stages_statuses.html) | Tách stage và status; bản chính thức tiếng Hà Lan, English open timeout |
| O04 | [Odoo 19 recurrence](https://www.odoo.com/documentation/19.0/applications/services/project/tasks/recurring_tasks.html) | Trigger/copy behavior qua nội dung chính thức được lập chỉ mục |
| O05 | [Odoo saas-19.3 dependencies](https://www.odoo.com/documentation/saas-19.3/applications/services/project/tasks/task_dependencies.html) | Dependency guard; không mặc định mọi phiên bản giống nhau |
| D01 | [Dynamics Sales work list](https://learn.microsoft.com/en-us/dynamics365/sales/connect-with-customers) | Up next/skip/snooze; license/security role cần kiểm |
| D02 | [Dataverse Task API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/task?view=dataverse-latest) | Activity model, user/team owner và context references |

**Trạng thái bàn giao 1.7:** Task Core đã hợp nhất vào phần thân Master. Chưa chọn vendor qua PoC hoặc có UAT đã chạy. Các tham số cấu hình và ngân sách/lịch còn mở tại A.7; baseline không yêu cầu đọc báo cáo nguồn mới hiểu chức năng.
