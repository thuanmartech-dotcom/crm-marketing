<!-- SECTION:3 -->
<a id="module-m22"></a>

### 3.16 FR42 — M22 Quản trị nhân sự, công và lương

#### 3.16.1 Mục tiêu, quyết định và phạm vi

CR-HRM-20261018, Master1.9: chủ dự án xác nhận công ty đang quản lý nhân sự thủ công trên Excel và yêu cầu tích hợp HRM vào tài liệu dự án. M22 cung cấp hồ sơ tập trung, hợp đồng lao động, phép, công, tự phục vụ và quy trình vòng đời nhân viên; payroll được đặc tả đầy đủ nhưng bật ở giai đoạn sau. Đây là thay đổi phạm vi được yêu cầu, không phải chứng nhận công thức pháp lý, ngân sách, lịch go-live hoặc phần mềm đã chạy.

Nguồn tham khảo là phần ảnh “1.4. Phân hệ quản lý nhân sự — Hồ sơ nhân viên, chấm công và Tính lương” người dùng cung cấp ngày18/10/2026; cuối ảnh bị cắt. Chỉ tiếp nhận nội dung nhìn thấy và quyết định trong trao đổi; không coi ảnh là quy định lao động hoặc chỉ thị kỹ thuật. Các bổ sung BA dưới đây là thiết kế đề xuất để hiện thực hóa quyết định.

Mục tiêu đo sau pilot: giảm nhập liệu lặp, công thiếu chứng cứ, hợp đồng bỏ sót và thời gian chốt công; baseline thực tế do HR đo trước chuyển đổi, không tự công bố tỷ lệ tiết kiệm. Excel là nguồn migration và công cụ đối chiếu chuyển tiếp, không giữ hai nguồn ghi chính sau cutover.

| Release profile | Phạm vi bắt buộc khi bật | Ngoài phạm vi profile |
|---|---|---|
| HR-A / SL09 | Hồ sơ, tổ chức liên kết M14, hợp đồng, chứng chỉ, phép/phê duyệt, công cơ bản nhập tay/file, sửa/chốt công, tự phục vụ, nhận/nghỉ việc, audit và chuyển Excel | Chưa tính lương chính thức, chưa chuyển ngân hàng tự động, chưa cần máy sinh trắc học |
| HR-B / SL10 | Ca nâng cao, log máy chấm công khi có thiết bị/API, tăng ca, ngoại lệ, xuất công được duyệt | Chưa mặc định tự xây payroll hoặc mua thiết bị |
| HR-C / SL11 | Payroll nội bộ hoặc kết nối hệ thống ngoài, lương/khấu trừ/hoa hồng đã duyệt, khóa kỳ, phiếu lương, chi và đối soát | Bank API chỉ capability riêng; không suy file xuất thành đã trả |
| HR-D / sau khi có nhu cầu | Tuyển dụng, đào tạo, đánh giá năng lực/phúc lợi mở rộng | Chỉ backlog định hướng; cần CR/đặc tả riêng, không thuộc cam kết HR-A/B/C |

HR-A/B/C là thứ tự trong miền HR, không biến toàn HRM thành P0 của CRM và không thay lịch pilot M21. Không có ngày hoàn thành hoặc nhân sự thực tế được giả định từ số tài khoản dự trù trong Master.

#### 3.16.2 Trách nhiệm và ranh giới

M22 sở hữu Employee/Employment/EmploymentContract/Leave/Attendance/Payroll; M14 sở hữu tài khoản, membership, grant và authority; M10 sở hữu quyền hưởng/điều chỉnh hoa hồng; M09 hoặc hệ thống kế toán/ngân hàng sở hữu chứng cứ thanh toán theo tích hợp đã chọn. M16 giữ công việc/checklist; M13 giữ lịch hẹn, chỉ nhận unavailable interval cần thiết; M18 nhận projection có quyền; M19 vận chuyển sự kiện; M20 quản trị mục đích/lưu trữ dữ liệu.

Employee khác User và Contact: một người có thể chưa có tài khoản, tái tuyển dụng có employment mới, cộng tác viên có loại quan hệ riêng; không suy nhân viên từ contact khách hàng. M22 tham chiếu org M14, không tạo danh mục phòng ban cạnh tranh. M22 chỉ đề nghị cấp/thu hồi quyền qua command M14 đúng authority, không tự gán quyền dựa vào chức danh.

HR admin quản hồ sơ; line manager duyệt phép/công trong phạm vi được giao; payroll operator lập lương; payroll approver duyệt; payment operator chi/đối soát; nhân viên xem bản thân; privacy steward xử lý yêu cầu dữ liệu. Một người kiêm vai phải được cấu hình rõ, có audit; không cho tự duyệt ngoại lệ tăng thu nhập của mình. Khi thiếu người duyệt thay, giữ pending và báo owner, không tự thông qua.

#### 3.16.3 Danh mục chức năng và truy vết

Mỗi dòng là hợp đồng chức năng tối thiểu: tác nhân/đầu vào → xử lý/ngoại lệ → đầu ra và kiểm chấp nhận. Profile ghi thời điểm đầu tiên bắt buộc; controls tiếp tục áp dụng ở các profile sau.

| ID / chức năng | Profile; tác nhân và đầu vào | Xử lý, đầu ra, điều kiện chấp nhận | Truy vết |
|---|---|---|---|
| M22-F01 Hồ sơ nhân viên | A; HR nhập hoặc import mã, tên, loại quan hệ, ngày vào, pháp nhân | Mã duy nhất trong tenant; hồ sơ thiếu trường cần thiết là Draft; không ép CCCD/hôn nhân nếu không có mục đích; kích hoạt Employment riêng | UC-H01; BR-H01; H-T01/02 |
| M22-F02 Tổ chức và điều chuyển | A; HR nhận org M14, quản lý, ngày hiệu lực | Lưu lịch sử chức danh/phòng ban; không ghi đè kỳ cũ hoặc tự mở quyền khách hàng; xung đột lịch hiệu lực phải giải quyết | UC-H02; BR-H02; H-T03/04 |
| M22-F03 Hợp đồng và phụ lục | A; HR lập điều khoản, loại quan hệ, thời hạn, bản ký | Draft/review/sign/active riêng; không tự coi upload là ký; phụ lục có hiệu lực, nhắc hết hạn có owner; loại hợp đồng được cấu hình và rà soát | UC-H03; BR-H03; H-T05/06 |
| M22-F04 Năng lực và hồ sơ đính kèm | A; HR/nhân viên gửi bằng cấp, chứng chỉ, hạn, minh chứng | Pending verification tới khi HR xác nhận; nhắc hết hạn; file riêng tư, không đưa vào search khách hàng | UC-H03; BR-H04; H-T07 |
| M22-F05 Chính sách phép và sổ phép | A; HR cấu hình loại phép, đơn vị, hạn mức, tích lũy/chuyển năm | Version theo pháp nhân/nhóm/ngày; credit/debit/reserve/release có nguồn; thiếu policy giữ pending, không tự trừ phép | UC-H04; BR-H05; H-T08/09 |
| M22-F06 Xin/duyệt/hủy phép | A; nhân viên chọn khoảng và người thay, quản lý duyệt | Tính theo lịch làm; kiểm trùng đơn và số dư kể cả reserved; từ chối có lý do; hủy đã duyệt qua phê duyệt và hoàn phép đúng một lần | UC-H04; BR-H06; H-T10/11 |
| M22-F07 Lịch làm và ca cơ bản | A; HR gán lịch tuần, giờ nghỉ, ngày nghỉ và timezone | Phiên bản lịch có hiệu lực; nhân viên thiếu lịch không bị tự đánh vắng; không hồi tố công đã khóa | UC-H05; BR-H07; H-T12 |
| M22-F08 Công cơ bản và nhập file | A; HR nhập ngày/giờ/trạng thái từ Excel | Preview lỗi, nguồn/file hash; công nhập thủ công phải ghi người/lý do; chưa duyệt không thành dữ liệu lương | UC-H05; BR-H08; H-T13/14 |
| M22-F09 Ca nâng cao và đổi ca | B; quản lý lập ca tuần/tháng, đổi ca có người nhận | Chặn trùng ca không hợp lệ; ca qua đêm gắn ngày ca bắt đầu, lưu mốc UTC và timezone; sửa lịch đã dùng tạo phiên bản | UC-H05; BR-H07; H-T15/16 |
| M22-F10 Thiết bị chấm công | B; operator mapping device/person, nhận log | Log gốc bất biến, khóa chống trùng; chưa map vào quarantine; offline nhận bù, thiết bị sai giờ cảnh báo; ưu tiên chỉ nhận mã nhân viên và timestamp | UC-H06; BR-H08; H-T17/18 |
| M22-F11 Sửa công và ngoại lệ | A; nhân viên yêu cầu quên công/công tác/làm từ xa | Gửi chứng cứ tối thiểu; quản lý duyệt; giữ trước/sau và lý do; thiếu công là exception, không tự coi nghỉ không lương | UC-H07; BR-H09; H-T19/20 |
| M22-F12 Tăng ca | B; nhân viên/quản lý đề nghị khoảng, loại ngày | Duyệt kế hoạch và xác nhận thực tế riêng; giao với giờ làm được chấp nhận; overtime có rule hiệu lực; vượt ngưỡng policy cảnh báo/chặn theo cấu hình | UC-H07; BR-H10; H-T21/22 |
| M22-F13 Đối soát và khóa công | A; HR chọn kỳ/pháp nhân | Liệt kê ngoại lệ, yêu cầu sửa còn mở; chỉ khóa khi được xử lý hoặc ngoại lệ có thẩm quyền; export có version; mở lại cần lý do và kiểm payroll đã dùng | UC-H08; BR-H11; H-T23/24 |
| M22-F14 Chính sách thu nhập | C; payroll cấu hình lương cơ bản, phụ cấp, thưởng, đơn vị, cách chia kỳ | Component có tính chất thuế/bảo hiểm theo policy, công thức/rounding/effective date; không hard-code tỷ lệ; thiếu cấu hình chặn tính chính thức | UC-H09; BR-H12; H-T25/26 |
| M22-F15 Khấu trừ và tạm ứng | C; payroll nhập bảo hiểm, thuế, người phụ thuộc, tạm ứng và lịch thu hồi | Khoản hợp lệ có căn cứ/duyệt; quản khoản dư tạm ứng; không tự phạt tiền từ kỷ luật/đi muộn; cảnh báo net âm chờ xử lý | UC-H09; BR-H13; H-T27/28 |
| M22-F16 Tính và đối soát lương | C; payroll chọn công khóa, hợp đồng/policy/biến động | Snapshot đầu vào, tính lặp cùng input cho cùng kết quả; vào/nghỉ/tăng lương giữa kỳ tách đoạn; bảng chênh kỳ trước và lỗi cần xử lý | UC-H09; BR-H14; H-T29/30 |
| M22-F17 Duyệt và khóa lương | C; approver duyệt đúng revision | Chặn người lập tự duyệt ngoại lệ của mình; thay input làm mất hiệu lực duyệt bản nháp; khóa giữ snapshot; sửa sau khóa bằng adjustment | UC-H10; BR-H15; H-T31/32 |
| M22-F18 Hoa hồng qua lương | C; nhận M10 payable đã duyệt, employee mapping | Claim khoản chi duy nhất qua payroll hoặc M10; ghi nguồn/entry/amount; giữ quyền hưởng lịch sử khi đổi owner/nghỉ việc; hoàn tiền tạo adjustment | UC-H11; BR-H16; H-T33/34 |
| M22-F19 Phiếu lương và thắc mắc | C; nhân viên xem phiếu Published, gửi dispute | Chỉ bản thân/người có quyền; xem chi tiết gross/net/component/kỳ; dispute có owner/SLA cấu hình, không sửa phiếu khóa trực tiếp | UC-H12; BR-H17; H-T35/36 |
| M22-F20 Chi lương và đối soát | C; finance tạo lệnh/file từ bảng đã khóa và duyệt | Tài khoản nhận đã xác nhận; checksum/tổng tiền; file xuất là Exported; Paid chỉ khi có chứng cứ/đối soát; partial/failed/unknown xử lý từng dòng | UC-H13; BR-H18; H-T37/38 |
| M22-F21 Tiếp nhận và thử việc | A; HR lập checklist, người phụ trách, hạn | Hợp đồng, tài sản, hướng dẫn, đánh giá thử việc; nhắc hạn; hoàn tất checklist không tự tăng lương hoặc cấp mọi quyền | UC-H14; BR-H19; H-T39 |
| M22-F22 Nghỉ việc và tái tuyển | A; HR xác nhận ngày hiệu lực, checklist bàn giao | M14 thu hồi quyền; M16/M03/M02 nhận bàn giao; giữ actor và quyền hưởng M10; settlement là luồng riêng; tái tuyển không phục hồi grant cũ | UC-H14; BR-H19; H-T40/41 |
| M22-F23 Tài sản, thưởng và kỷ luật | A; HR ghi quyết định, tài sản cấp/thu hồi, chứng cứ | Theo dõi xác nhận bàn giao/trả; kỷ luật không tự khấu trừ; thưởng vào payroll cần khoản và phê duyệt riêng; tránh thay toàn bộ hệ thống tài sản | UC-H14; BR-H20; H-T42 |
| M22-F24 Tự phục vụ hồ sơ | A; nhân viên xem/sửa trường được phép | Thay thông tin nhạy cảm tạo đề nghị HR xác minh; không tự sửa lương/quản lý/số dư phép; thay ngân hàng có xác minh trước kỳ chi | UC-H12; BR-H17; H-T43 |
| M22-F25 Báo cáo và xuất dữ liệu | A, mở thêm C; HR/manager/finance theo quyền | Bộ lọc kỳ/pháp nhân/org, cảnh báo thiếu dữ liệu, export có audit; manager chỉ nhận công/availability và cost rate được phép, không suy lương | UC-H15; BR-H21; H-T44 |
| M22-F26 Migration Excel | A; data steward chọn file, mapping và cutover | Dry-run, lỗi từng dòng, đối soát, batch commit/rollback có điều kiện; mở số dư phép có chứng cứ; không âm thầm ghi đè hồ sơ hiện hữu | UC-H16; BR-H22; H-T45/46 |
| M22-F27 Bảo mật và vòng đời dữ liệu | A; HR/privacy cấu hình quyền và retention | Bảo vệ row/field/file/export/search/AI; legal hold ngăn purge; yêu cầu sửa/xóa có xác minh và xử lý retention, không xóa sổ đã khóa tùy tiện | UC-H15; BR-H23; H-T47 |
| M22-F28 Kết nối và phục hồi | A interface, B/C adapter; operator theo dõi queue | Schema version/idempotency/retry/quarantine, không đưa lương vào log; sự kiện không rõ trạng thái tiền phải reconcile; cảnh báo và runbook restore | UC-H06/13/16; BR-H24; H-T48 |

#### 3.16.4 Quy tắc nghiệp vụ

| ID | Quy tắc bắt buộc |
|---|---|
| BR-H01 | employee_id ổn định theo tenant, employee_code duy nhất; CCCD/email chỉ là tín hiệu phát hiện trùng, không tự merge; Employment theo pháp nhân và khoảng hiệu lực. |
| BR-H02 | Không chồng khoảng phân công chính trong cùng employment; nhiều assignment hợp lệ phải có tỷ lệ/loại rõ. Thay org không sửa lịch sử quyền, công hoặc chi phí đã khóa. |
| BR-H03 | Ngày kết thúc có thể trống theo loại được duyệt; gia hạn/phụ lục không ghi đè bản ký; employment effective và trạng thái chữ ký kiểm riêng. |
| BR-H04 | File có type/size/scan/checksum/version/classification; link tải có kiểm quyền mỗi request; chứng chỉ khai báo chưa xác minh không hiển thị Verified. |
| BR-H05 | Phép dùng ledger có ngày hiệu lực và policy snapshot; lịch nghỉ/làm quyết định số lượng; chuyển năm có cap/expiry theo cấu hình, không bịa định mức. |
| BR-H06 | Reserve số dư khi submit trong transaction; approve chuyển reserve thành debit đúng một lần; reject/cancel release; concurrent request không làm âm số dư trừ khi policy cho phép rõ. |
| BR-H07 | Calendar theo employment/site/timezone; đổi lịch sau chốt chỉ adjustment hoặc mở kỳ có authority; giờ nghỉ, ca gãy/đêm tính từ interval, không chỉ trừ hai timestamp đầu-cuối. |
| BR-H08 | Dedupe theo source+external_event_id, fallback khóa được thống nhất với thiết bị; log gốc giữ nguyên, derived attendance có version; file retry không nhân công. |
| BR-H09 | Sửa công cần requester, reason, before/after, evidence và approver; không tự duyệt bản thân; công tác/remote có quy trình thay thế khi không có GPS/thiết bị. |
| BR-H10 | Approved overtime khác actual overtime; thời gian thanh toán là phần thực tế được xác nhận theo policy; không cộng trùng giờ thường, phép và tăng ca. |
| BR-H11 | Khóa công theo pháp nhân/kỳ có fingerprint đầu vào; payroll đã tiêu thụ thì không sửa âm thầm; chênh lệch phải truy được kỳ và employee gốc. |
| BR-H12 | Component/formula có effective dates, rounding, currency, nguồn chuẩn và người duyệt; thay policy không chạy lại lịch sử khóa; thiếu rate trả ValidationError, không coi bằng0. |
| BR-H13 | Thuế/bảo hiểm/tạm ứng có căn cứ và phiên bản chính sách được người phụ trách xác nhận; kỷ luật không tự sinh khoản trừ; không cam kết tuân thủ chỉ vì công thức chạy được. |
| BR-H14 | Gross là tổng earnings được chấp nhận; net = gross − employee deductions + các khoản hoàn/tạm ứng được khai báo trong thiết kế component; chi phí employer không tự trừ net; ngăn cộng một khoản hai lần. |
| BR-H15 | Run version duy nhất theo scope/kỳ/type; approval gắn snapshot hash; Locked không đổi trực tiếp, adjustment tham chiếu dòng gốc và kỳ mở; lịch sử vẫn xem được. |
| BR-H16 | M10 là nguồn quyền hưởng; một commission entry có payment route/reservation duy nhất, tổng settled/reserved không vượt payable; payroll thất bại chỉ release qua đối soát, không tự trả ở cả hai nơi. |
| BR-H17 | Employee self-service scope chính mình; thay bank cần xác minh và audit, không gửi số tài khoản đầy đủ qua email; phiếu chỉ phát hành sau duyệt, Published không có nghĩa Paid. |
| BR-H18 | Maker/checker và hạn mức chi theo policy; export/checksum khác bank acknowledgement/settlement; Unknown chặn retry tạo giao dịch mới cho đến khi xác minh bằng reference. |
| BR-H19 | Offboarding có effective_at, revoke và kiểm pending jobs; thiếu người nhận đưa queue quản lý; tái tuyển giữ Employee, Employment mới và grant review mới; không xóa actor cũ. |
| BR-H20 | Thu hồi tài sản có trạng thái/biên bản; thiếu tài sản mở exception riêng, không tự giữ toàn bộ lương hoặc tự khấu trừ. |
| BR-H21 | Availability chỉ truyền khoảng vắng và backup cần thiết; work timesheet khác attendance; manager không được đọc lương qua cost projection hoặc nhóm báo cáo quá nhỏ theo policy. |
| BR-H22 | Import giữ source row/batch/hash; mapping version, rejected rows, create/update mode và expected version; commit theo batch rõ ràng, không có partial import im lặng. |
| BR-H23 | Least privilege theo tenant/pháp nhân/employee/field; deny áp dụng search/API/file/export/AI; admin kỹ thuật không mặc nhiên có quyền HR/payroll; retention policy và legal hold kiểm trước xóa. |
| BR-H24 | Event delivery at-least-once với consumer idempotency; lỗi mapping/policy vào queue có owner; replay không tạo thêm công/phép/chi; dữ liệu nhạy cảm bị loại khỏi telemetry. |

#### 3.16.5 Màn hình và trạng thái

Màn hình gồm: HR Home (cảnh báo/hồ sơ thiếu), danh sách nhân viên, hồ sơ tabs, org/assignment, hợp đồng/phụ lục, phép/sổ phép, lịch ca, công ngày/kỳ và exceptions, hộp duyệt, onboarding/offboarding, import center, payroll workbench, phiếu lương, payment reconciliation, reports và policy settings. Mỗi list có scope, filters, pagination, export theo quyền và trạng thái dữ liệu; form báo lỗi theo trường, không mất bản nháp; bulk action preview và kết quả từng dòng. Dashboard không đưa CCCD/lương vào thông báo chung.

Employee Draft→Active→Inactive; Employment Planned→Active→Ended (probation là giai đoạn cấu hình, không lẫn login). Leave Draft→Submitted→Approved/Rejected; CancelRequested→Cancelled khi đã Approved. Attendance Draft→Exception/Ready→Approved→Locked. Payroll Draft→Calculated→Reviewed→Approved→Locked; nháp có thể Superseded; điều chỉnh là run riêng. Payment Prepared→Authorized→Exported/Submitted→PartiallySettled/Settled/Failed/Unknown. Một payment batch chỉ Settled khi mọi dòng phải chi đã đối soát; không dùng một trạng thái Paid thay cả vòng đời bảng lương.

<!-- SECTION:4 -->
### 4.25 UC-H01–16 — Quy trình nhân sự

Tất cả UC yêu cầu scope và authority hợp lệ, audit/correlation_id; từ chối không thay đổi ledger. Người thay thế phải được ủy nhiệm còn hiệu lực. Timeout không đồng nghĩa thất bại nghiệp vụ; kiểm command result trước retry.

| ID | Tác nhân, tiền điều kiện | Luồng chính → hậu điều kiện | Nhánh lỗi/ngoại lệ |
|---|---|---|---|
| UC-H01 | HR; legal entity và mã nhân viên có quy tắc | Nhập/kiểm trùng → lưu Draft → xác minh → activate Employment → nhân viên xuất hiện đúng scope | Thiếu dữ liệu giữ Draft; trùng khả nghi chờ steward, không tự merge |
| UC-H02 | HR và quản lý có authority; Employment tồn tại | Chọn ngày/assignment → kiểm lịch → duyệt → tới hiệu lực cập nhật projection/org request → giữ lịch sử | Xung đột ngày, backdate đã khóa hoặc grant thiếu giữ pending/reject |
| UC-H03 | HR; mẫu/loại và sign authority đã cấu hình | Tạo hợp đồng/phụ lục → review → ghi chứng cứ ký → activate theo ngày → nhắc hạn; hồ sơ bằng cấp kiểm riêng | Chưa ký không giả Signed; file lỗi quarantine; nhắc trùng dedupe |
| UC-H04 | Nhân viên và manager; lịch/policy/số dư đã nạp | Chọn khoảng → preview → reserve/submit → duyệt → ledger debit và unavailable event → hủy được duyệt hoàn ledger | Trùng đơn, race số dư, manager vắng, nửa ngày/lễ; không tự duyệt |
| UC-H05 | HR/manager; lịch làm hợp lệ | Lập lịch → gán nhân viên → công tay/file hoặc ca → preview → ghi derived công → đưa exceptions | Ca đêm/ca gãy, đổi ca, thiếu lịch; chưa khóa không xuất chính thức |
| UC-H06 | Operator; connector được cấp quyền | Nhận log → validate/map/dedupe → append log → tính công version → cập nhật checkpoint | Device offline, clock skew, unknown employee, replay; queue có owner |
| UC-H07 | Nhân viên/manager; kỳ còn mở | Gửi sửa công/tăng ca → xác minh → duyệt đúng revision → tính lại dự thảo → xác nhận kết quả | Kỳ khóa qua adjustment, sửa khi duyệt trả conflict; GPS thiếu có chứng cứ thay thế |
| UC-H08 | HR approver; kỳ và người lao động được đối soát | Xem lỗi/đơn mở → xử lý → approve/lock → xuất công version hoặc chuyển payroll | Ngoại lệ chưa giải quyết chặn lock; mở lại kiểm consumer payroll |
| UC-H09 | Payroll operator; policy và công đã khóa | Chọn kỳ → snapshot → tính thành phần → đối chiếu tổng/biến động → Reviewed | Thiếu rate/công, net âm, mid-period change hoặc phụ thuộc thiếu → exception, không giả0 |
| UC-H10 | Payroll approver; Reviewed và checksum | Kiểm chênh → approve bản đúng → lock → publish khi được phép | Input đổi vô hiệu duyệt trước lock; sau lock tạo adjustment kỳ mở |
| UC-H11 | Payroll và M10; entry Payable | Claim route → import component có source → duyệt/run → chi → xác nhận settlement về M10 | Retry/chuyển route/hoàn tiền xử lý reservation và adjustment; nghỉ việc không mất entitlement |
| UC-H12 | Nhân viên; account-employee mapping | Xem dữ liệu/phiếu của mình → gửi correction/dispute → owner xử lý → thông báo trạng thái | Không mở phiếu người khác bằng URL; bank change đợi xác minh; dispute không sửa locked run |
| UC-H13 | Finance maker/checker; run Locked | Chuẩn bị từng dòng → xác nhận bank → duyệt → export hoặc submit adapter → nhận evidence → reconcile | Partial/Unknown/Failed tách dòng, không retry mù; người chưa trả vẫn có payable |
| UC-H14 | HR/manager; quyết định nhận/nghỉ việc được xác nhận | Checklist owner/due → hoàn tất hoặc exception → activate/revoke tại effective time → bàn giao có người nhận | Người nghỉ còn hoa hồng, tài sản chưa trả, không người nhận; quyết toán riêng, không trì hoãn revoke |
| UC-H15 | HR/manager/privacy; quyền theo mục đích | Chọn report/data request → lọc scope/field → preview/export hoặc xử lý retention → audit | Thiếu quyền, legal hold, nhóm nhỏ gây suy lương; giữ phản hồi không lộ existence trái quyền |
| UC-H16 | Steward+HR approver; file và cutover plan | Inventory/mapping → staging dry-run → sửa lỗi → đối soát → approve batch → commit → kiểm sau → chốt nguồn ghi | Rollback chỉ batch chưa có downstream; đã phát sinh nghiệp vụ dùng compensating correction và đối soát |

<!-- SECTION:5 -->
### 5.22 Dữ liệu, giao diện tích hợp và chuyển đổi M22

#### 5.22.1 Dictionary logic

Mọi record có id, tenant_id, legal_entity_id khi áp dụng, classification, created_by/at, version; business date dùng lịch Asia/Ho_Chi_Minh trừ site có timezone khác được cấu hình; timestamp lưu UTC kèm timezone nguồn. Tiền dùng decimal và currency, không float; công/phép lưu quantity và unit, không trộn ngày/giờ nếu thiếu conversion rule. Đây là schema logic, chưa là DDL được nghiệm thu.

| Entity | Trường chính và invariant | Quan hệ/nguồn chuẩn |
|---|---|---|
| Employee | employee_code, name, contacts, status; private identity/bank fields tách quyền; code unique tenant | M22; user_id optional mapping verified M14; không FK đồng nhất Contact |
| Employment | employee_id, legal_entity_id, relationship_type, start/end, stage | Một Employee nhiều Employment; overlap phải đúng loại và được duyệt |
| EmployeeAssignment | employment_id, org_ref, manager_ref, title, from/until, allocation | Org M14; lịch sử effective-dated; primary overlap bị chặn |
| EmploymentContract / ContractAmendment | employment_id, type, terms_version, start/end, signature_evidence, supersedes | Khác Contract khách hàng M08; document private; signed không ghi đè |
| Credential / EmployeeDocument | type, issuer, valid_until, verification, storage_ref, checksum, classification | File gateway M20; không lưu public URL |
| HRPolicyVersion | policy_type, jurisdiction/context, effective dates, formula, rounding, approver | Policy xuất bản bất biến; lịch sử được snapshot |
| WorkCalendar / ShiftAssignment | timezone, intervals, breaks, day_type, effective dates, employee | Ca có start/end đầy đủ; không mặc định giờ ngày tiếp theo là cùng ngày |
| LeaveAccount / LeaveEntry / LeaveRequest | type, quantity/unit, reserve/debit/credit/release, source, interval, approver, version | Unique source-action; số dư tính từ ledger và effective date |
| AttendanceRaw / AttendanceDay | source_event_id, device, employee mapping, raw timestamp; derived intervals/status/source_version | Raw append-only; derived gắn lịch/policy; unique source key |
| AttendanceCorrection / OvertimeRequest | before/after, reason/evidence, planned/actual, decision, revision | Duyệt đúng version; không ghi đè log gốc |
| AttendancePeriod | entity, period, employee_scope, input_hash, lock_actor/time, version | Payroll tham chiếu exact locked version |
| CompensationAssignment / PayComponent | employment, component, rate/formula, effectivity, taxable/insurance flags, currency | Policy được xác nhận; assignment thay đổi giữa kỳ tách đoạn |
| EmployeeDeduction / AdvanceLedger | kind, basis, approved amount, balance, schedule, source | Thuế/bảo hiểm/người phụ thuộc riêng classification; employee/employer contribution riêng |
| PayrollRun / PayrollLine | period/type, version, snapshots, gross/deductions/net, approval_hash, status | Unique approved active regular run theo employment/kỳ; bổ sung bằng adjustment link |
| CommissionPayrollLink | commission_entry_id, route, reservation_ref, amount, settled, payroll_line | M10 nguồn entitlement; transaction/contract reservation chống double payout |
| Payslip / PayrollDispute | employee, run_version, publish_time, secure_file, dispute_owner/status | Phiếu bất biến theo run; dispute không sửa ledger |
| SalaryPaymentBatch / SalaryPaymentItem | run_ref, amount, destination_version, instruction_id, provider_ref, status/evidence | Idempotency key unique; từng item có allocation/settlement; ngoài CRM cash receipt |
| EmployeeLifecycle / AssetCustody / HRDecision | type, effective_at, checklist_ref, evidence, asset_status, responsible | M16 checklist; M14 quyền; HRDecision không tự tạo deduction |
| HRImportBatch / HRImportRow | file_hash, mapping_version, row_no, external_key, preview_diff, status, errors | Commit keys bền vững; source provenance; không chứa mật khẩu |

Không đọc private repository giữa domain. M22 gọi port M10 reserve/release/settle commission; chuyển trạng thái qua outbox/saga có reconcile, không giả có transaction phân tán. Payroll external mode lưu external run reference, totals và reconciliation, không tính lại cạnh tranh với phần mềm chuẩn. Chọn INTERNAL hoặc EXTERNAL theo pháp nhân/kỳ trước enable, không vận hành hai engine chính thức cho cùng kỳ.

#### 5.22.2 Hợp đồng API/event dự kiến

Các endpoint nằm dưới `/hr/v1`; tên dưới là logical contract cần chốt DTO/schema ở thiết kế kỹ thuật. Mutation yêu cầu actor, scope, command_id/idempotency_key, expected_version, reason khi sửa nhạy cảm. Sai scope trả403 hoặc404 theo policy chống enumeration; conflict version409; thiếu policy422; response gồm result_id/status/version/correlation_id, không trả PII dư thừa. GET phân trang/field mask; export qua job có expiry và quyền kiểm lại lúc tải.

| Endpoint | Ý nghĩa và guards |
|---|---|
| POST /employees; POST /employees/{id}/employment | Kiểm mã/mapping, legal entity, quyền HR; không cấp login mặc định |
| POST /assignments; POST /employment-contracts/{id}/activate | Effective date, evidence/revision và authority |
| POST /leave-requests; POST /leave-requests/{id}/decisions | Reserve/approve/reject/cancel transaction, expected version, self-approval guard |
| POST /attendance/imports; POST /attendance/events | Staging hoặc log append; source authentication, mapping và dedupe |
| POST /attendance-corrections; POST /overtime-requests/{id}/decisions | Before/after, actual/planned, reviewer và kỳ khóa |
| POST /attendance-periods/{id}/lock | Exceptions resolved, fingerprint, downstream check khi reopen |
| POST /payroll-runs; POST /payroll-runs/{id}/calculate | INTERNAL mode, locked inputs, policy version, idempotent snapshot |
| POST /payroll-runs/{id}/approve; POST /payroll-runs/{id}/lock | Approve đúng revision; maker/checker; không thay locked line |
| POST /commission-links/reserve; POST /commission-links/{id}/settle | M10 authority, reservation, unique payment route và evidence |
| POST /salary-payment-batches; POST /salary-payment-items/{id}/reconcile | Locked approved amount, verified bank version, reference/evidence, partial/unknown |
| GET /me/payslips; POST /payroll-disputes | Identity mapping; own published only; dispute owner |
| POST /lifecycle-actions; POST /imports/{id}/commit | Effective offboarding command hoặc approved batch; downstream-safe rollback |

Events: `hr.employment.changed.v1`, `hr.availability.changed.v1`, `hr.attendance.locked.v1`, `hr.payroll.locked.v1`, `hr.salary.settled.v1`, `hr.offboarding.effective.v1`. Envelope gồm event_id, aggregate_id/version, tenant/entity, occurred_at/effective_at, schema_version, correlation_id. Payload tối thiểu; consumers lấy dữ liệu qua API có quyền. Salary event không broadcast lương vào bus đọc chung. Availability không gửi lý do sức khỏe. Consumer nhận out-of-order phải so version/rebuild, không ghi đè projection mới bằng event cũ.

#### 5.22.3 Excel migration và cutover

1. HR inventory file/sheet, người sở hữu, kỳ và nguồn chuẩn; chỉ đọc bản sao. Chưa có file Excel thật nên mapping/chất lượng dữ liệu thực tế chưa xác nhận.
2. Chuẩn hóa mã nhân viên, pháp nhân, ngày dd/mm/yyyy, leading zero của mã/điện thoại/tài khoản; phân biệt blank/0/unknown. XLSX đọc giá trị có kiểm formula/cached value, macro không thực thi; CSV export escape formula injection.
3. Staging theo batch; mapping version gồm cột nguồn→field, type, required, transform, sensitivity. Tách nhân viên/hợp đồng/phép/công/lương lịch sử; không nhập lương lịch sử như lệnh chi mới.
4. Dry-run báo created/updated/skipped/rejected, duplicate candidates, foreign-key errors và diff nhạy cảm. HR duyệt merge mapping thủ công; lỗi không bị bỏ qua im lặng.
5. Đối soát số người theo trạng thái/pháp nhân, hợp đồng, tổng phép mở đầu, tổng công theo kỳ; lương lịch sử nếu nhập đối chiếu gross/net/tổng đã chi. Mọi sai lệch phải có biên bản giải thích và người duyệt; không làm tròn để giấu lệch.
6. HR xác nhận cutover_at và nguồn ghi sau cutover. Chốt delta giữa dry-run và cutover, backup/staging snapshot, commit batch idempotent; giữ file gốc được bảo vệ theo retention.
7. Kiểm ngay sau import bằng mẫu do HR chọn và totals; batch chưa có downstream có thể reverse bằng command, không xóa cứng lịch sử. Đã có nghiệp vụ phát sinh phải correction có liên kết và đối soát lại.
8. Sau chấp nhận HR-A, Excel vận hành cũ chỉ đọc. Payroll giai đoạn chuyển tiếp vẫn được tính/đối chiếu trong công cụ hiện tại theo owner rõ; khi HR-C chính thức, chốt lại system of record payroll. Chạy song song ít nhất hai kỳ liên tiếp với bộ kết quả được duyệt, không phát hai lệnh chi.

<!-- SECTION:6 -->
### 6.8 Phân quyền và bảo vệ dữ liệu M22

| Vai trò | Được phép trong scope | Không mặc nhiên được phép |
|---|---|---|
| Employee | Hồ sơ công khai của mình, đề nghị sửa, phép/công bản thân, phiếu Published | Sửa rate, số dư ledger, manager, duyệt đơn mình hoặc xem đồng nghiệp |
| Line manager | Danh sách đội ngũ được giao, duyệt phép/công, availability, checklist | CCCD/bank/lương chi tiết, hồ sơ riêng tư của khách khác, tự duyệt thu nhập |
| HR operator | Hồ sơ/hợp đồng/nhân sự trong pháp nhân; chuẩn bị công/import | Tự cấp Finance/M14 grant; chuyển tiền hoặc xem mọi payroll nếu chưa được cấp |
| HR approver | Duyệt công/nhân sự đúng scope và authority | Sửa trực tiếp ledger/locked period hoặc duyệt khi xung đột lợi ích |
| Payroll operator | Compensation/deductions, lập và đối soát bảng lương | Tự phê duyệt ngoại lệ có lợi cho mình; tự thực hiện bank payout |
| Payroll approver | Duyệt đúng snapshot và phát hành phiếu theo quyền | Thay tài khoản nhận tiền không qua xác minh hoặc ghi đè kỳ khóa |
| Finance payment | Số tiền cần chi, người nhận/bank được phép, đối soát | Hồ sơ kỷ luật, lý do nghỉ, mọi chứng chỉ/CCCD nếu không cần |
| CEO/report viewer | Tổng hợp theo grant; chi tiết chỉ khi có quyền rõ | Quyền toàn bộ PII do chức danh mặc định |
| Technical admin | Connector/health/config được giao, telemetry đã che | Nội dung hồ sơ/lương, tự cấp business grant |

M14 thực thi authority; M20 quản lý mục đích, yêu cầu truy cập/sửa/xóa, retention và legal hold; M22 áp dụng trên row/field/attachment/list/search/export/notification/AI. Không bật đưa hồ sơ nhân sự vào AI index chung; chức năng AI riêng cần scope/mục đích và review độc lập. Audit hành động xem/xuất trường nhạy cảm, thay bank/rate/policy, approve/reopen/payment và impersonation nếu có; không ghi nguyên CCCD/bank/lương vào application log.

Sinh trắc học không bắt buộc cho HR-A/B: nếu dùng máy, mặc định chỉ nhận employee key/time/status. Việc thu/lưu template mặt/vân tay, vị trí GPS, thông tin sức khỏe cần phạm vi, căn cứ xử lý và retention được người có trách nhiệm xác nhận trước enable. Không suy consent là căn cứ duy nhất cho mọi dữ liệu lao động. Thiết kế này không đưa tỷ lệ thuế/bảo hiểm hoặc kết luận pháp lý hiện hành; phải xác nhận policy áp dụng tại thời điểm chạy.

<!-- SECTION:7 -->
### 7.9 H-NFR — Chất lượng và vận hành HRM

Các ngưỡng dưới là mục tiêu kỹ thuật đề xuất để lập test, cần xác nhận tải theo H-O01; không là kết quả đo hay SLA đã ký.

| ID | Tiêu chí kiểm được | Truy vết |
|---|---|---|
| H-NFR01 | Thử truy cập chéo tenant/employee/field qua API/file/search/export đều bị chặn; không có PII nhạy cảm trong log/notification chung | H-T35/43/47 |
| H-NFR02 | Cùng input/policy version cho cùng công/lương; decimal/rounding có test; 100 replay không nhân ledger hoặc payment | H-T14/29/33/38/48 |
| H-NFR03 | Profile đề xuất 100 nhân viên, 12 tháng công, 20 phiên đồng thời: p95 list/profile dưới2giây; import1.000 dòng dưới60giây bằng background job; thực đo trước enable | H-T45/48 |
| H-NFR04 | Mục tiêu RPO≤24giờ, RTO≤8giờ đề xuất; restore thử vào môi trường cô lập, đối soát totals và audit; owner xác nhận phù hợp kỳ lương | H-T48 |
| H-NFR05 | Form mobile dùng được với xin phép/sửa công/xem phiếu; lỗi theo trường, keyboard navigation, không lộ nhạy cảm trên màn hình thông báo | H-T10/19/35 |
| H-NFR06 | Job có correlation, retry giới hạn, dead-letter có owner; cảnh báo import/connector/revoke/payment Unknown theo ngưỡng cấu hình | H-T18/38/40/48 |
| H-NFR07 | Kỳ khóa/file ký/snapshot có checksum và audit append-only; sửa/purge qua authority/retention, không sửa lịch sử để che sai lệch | H-T06/24/32/47 |
| H-NFR08 | Adapter có schema version và contract fixture; payload cũ/đến muộn/không hỗ trợ bị xử lý rõ, rollback deploy không nhân hiệu ứng | H-T17/46/48 |

<!-- SECTION:8 -->
### 8.7 Báo cáo nhân sự và định nghĩa chỉ số

HR Home có headcount active theo Employment tại ngày chốt, mới vào/nghỉ, thử việc/hợp đồng/chứng chỉ sắp hạn, hồ sơ thiếu, đơn chờ duyệt và công exception. Khi đếm nhân sự toàn công ty dùng distinct Employee, khi đếm theo pháp nhân dùng Employment và ghi rõ khả năng trùng; không cộng bừa hai loại.

Phép còn = credit có hiệu lực − debit − reserve còn mở; thể hiện riêng phép khả dụng và đã dùng. Công hiển thị expected intervals, actual approved, missing và overtime approved, không coi chưa có dữ liệu là vắng. Lương theo kỳ/pháp nhân gồm gross, employee deductions, net payable, employer cost và chênh kỳ trước; total paid lấy settlement, remaining = payable − settled − khoản hủy hợp lệ. Pending/Unknown hiển thị riêng.

Dashboard manager nhận availability/workload; không dùng số task/giờ có mặt làm điểm đánh giá duy nhất. Cost allocation sang M17 theo cost rate version và timesheet được phép, không mặc định net salary là cost rate. Báo cáo lương chỉ cho role được cấp; export giữ filters/as_of/policy version/coverage và audit. Hợp đồng cảnh báo theo ngưỡng H-O03; không mặc định mọi hợp đồng đều có ngày hết hạn. Tỷ lệ nghỉ việc hoặc chi phí trung bình chỉ triển khai khi denominator và nhóm đủ lớn đã được định nghĩa/phê duyệt.

<!-- SECTION:9 -->
### 9.18 UAT và triển khai M22

#### 9.18.1 Danh mục kiểm thử nghiệp vụ

Tất cả H-T01–48 hiện ở trạng thái **Not Run**; mô tả là expected result để QA viết fixture, không phải bằng chứng ứng dụng đạt. Mỗi ca chạy có actor/scope, input, policy version, bước thực hiện, expected/actual, evidence và reviewer. HR-A phải đạt các ca của feature A và controls áp dụng; HR-B thêm B; HR-C thêm C; không dùng hoãn payroll để bỏ kiểm quyền/import/ledger phép.

| ID | Tình huống kiểm thử | Kết quả bắt buộc |
|---|---|---|
| H-T01 | Tạo mã nhân viên trùng trong cùng tenant và cùng mã ở tenant khác | Cùng tenant conflict; khác tenant không rò hồ sơ |
| H-T02 | Người chưa có User, hồ sơ thiếu trường và tái tuyển | Draft được lưu; Active cần đủ trường; không bắt tạo login hoặc nhân đôi Employee |
| H-T03 | Hai primary assignment chồng ngày | Chặn hoặc yêu cầu loại concurrent được phép; lịch sử giữ nguyên |
| H-T04 | Điều chuyển sang đội khác, mở URL khách hàng cũ/mới | Chỉ quyền M14 hiệu lực quyết định; chức danh không tự mở access |
| H-T05 | Hợp đồng không xác định hạn và hợp đồng sắp hết hạn | Không ép ngày kết thúc; nhắc đúng policy/người nhận một lần mỗi mốc |
| H-T06 | Upload bản chưa ký, thay phụ lục sau hiệu lực | Không tự Signed; version mới, bản ký cũ/checksum giữ nguyên |
| H-T07 | Chứng chỉ chưa xác minh, file độc hại/URL người khác | Không Verified; file quarantine hoặc access denied |
| H-T08 | Phép tích lũy/chuyển năm/hết hạn và policy đổi | Ledger theo ngày/version; không đổi số dư lịch sử khóa |
| H-T09 | Thiếu policy và hai request đồng thời dùng cùng số dư | Thiếu policy chặn submit; reserve không vượt số dư cho phép |
| H-T10 | Xin nửa ngày trùng lễ/ngày nghỉ trên mobile | Preview tính theo lịch và đơn vị, không trừ cả ngày sai |
| H-T11 | Approve/reject/cancel replay và người duyệt nghỉ | Chỉ một debit/release; delegation hợp lệ hoặc pending, không autoapprove |
| H-T12 | Nhân viên thiếu calendar hoặc lịch thay sau chốt | Exception rõ; không tự vắng và không sửa kỳ khóa |
| H-T13 | Excel công có blank,0, ngày sai và employee lạ | Phân biệt các giá trị; lỗi từng dòng không bị nhập âm thầm |
| H-T14 | Import lại file công100lần | Không nhân giờ/dòng nghiệp vụ, truy được batch/row |
| H-T15 | Ca22:00–06:00 có nghỉ giữa ca | Gắn đúng ngày ca; trừ break theo interval, không âm giờ |
| H-T16 | Đổi ca tạo trùng lịch hoặc sửa ca đã có công khóa | Chặn xung đột; amendment có kiểm downstream |
| H-T17 | Device replay/out-of-order/unmapped employee | Unique log, quarantine unknown, projection không lùi version |
| H-T18 | Device offline rồi gửi bù, timestamp lệch giờ | Không mất log; exception clock skew, không tự sửa raw |
| H-T19 | Quên công, remote không có GPS, sửa công của mình | Chứng cứ thay thế và phê duyệt; không tự approve |
| H-T20 | Reviewer duyệt revision cũ khi request vừa đổi | Conflict409; audit trước/sau; không áp bản cũ |
| H-T21 | Tăng ca đăng ký3giờ, thực tế2giờ, chỉ1giờ xác nhận | Tính phần được xác nhận theo policy, không tự lấy3giờ |
| H-T22 | Tăng ca trùng phép/giờ thường hoặc vượt giới hạn policy | Chặn/exception theo rule, không cộng trùng |
| H-T23 | Chốt công còn đơn sửa pending | Chặn hoặc exception được duyệt đúng authority, có evidence |
| H-T24 | Mở công sau khi payroll đã khóa | Không sửa input snapshot; adjustment có tham chiếu |
| H-T25 | Chính sách lương thiếu rate và thay rate giữa tháng | Thiếu chặn tính; có rate tách đoạn hiệu lực đúng |
| H-T26 | Thay tỷ lệ/công thức sau khóa kỳ trước | Kỳ cũ giữ snapshot, kỳ mới dùng version mới |
| H-T27 | Employer contribution, employee deduction, tạm ứng | Employer cost không trừ net; tạm ứng có số dư và không thu hồi hai lần |
| H-T28 | Net âm hoặc quyết định kỷ luật được nhập | Exception review; không tự sinh khoản phạt/trừ lương |
| H-T29 | Tính lại cùng input nhiều lần và rounding nhiều component | Kết quả deterministic; tổng chi tiết khớp tổng kỳ theo rule |
| H-T30 | Vào/nghỉ giữa kỳ, nghỉ không lương và truy lĩnh | Proration theo policy được duyệt, không mặc định chia30ngày |
| H-T31 | Maker duyệt ngoại lệ của mình hoặc duyệt snapshot cũ | Chặn; thay input buộc review lại |
| H-T32 | Sửa payroll Locked và tạo adjustment | Không sửa trực tiếp; adjustment kỳ mở nối dòng gốc |
| H-T33 | M10 và payroll đồng thời claim cùng hoa hồng | Chỉ một route/reservation;100replay không chi trùng |
| H-T34 | Refund sau chi hoa hồng hoặc nhân viên đã nghỉ | Điều chỉnh theo policy/entry gốc; không xóa quyền hưởng vô căn cứ |
| H-T35 | Mở phiếu người khác bằng URL/export/mobile notification | Denied, không rò số tiền; bản thân chỉ thấy Published |
| H-T36 | Khiếu nại phiếu lương đã khóa | Tạo dispute có owner, response history; không sửa phiếu gốc |
| H-T37 | Export bank file và một dòng thực trả ít hơn | Exported chưa Paid; partial được đối soát riêng, còn payable |
| H-T38 | Timeout bank, retry và xác nhận muộn | Unknown chặn lệnh chi mới; reconcile theo reference không double pay |
| H-T39 | Kết thúc thử việc nhưng chưa có quyết định lương/quyền | Nhắc người phụ trách; không tự nâng lương hoặc grant |
| H-T40 | Nghỉ việc có session/job/scheduled send và task chưa bàn giao | Revoke đúng effective time, job kiểm lại quyền; task về người nhận/queue |
| H-T41 | Tái tuyển dụng sau offboard | Employment mới, actor/entitlement cũ còn; không hồi sinh quyền cũ |
| H-T42 | Chưa trả tài sản và quyết định thưởng/kỷ luật | Exception tài sản riêng; không tự giữ/trừ lương; thưởng cần approval |
| H-T43 | Nhân viên đổi bank và tự sửa rate/manager | Bank pending verification; rate/manager bị từ chối, audit có dấu vết |
| H-T44 | Manager export tổng hợp/cost rate hoặc nhóm một người | Field mask/group policy ngăn suy lương; report ghi as_of/coverage |
| H-T45 | Dry-run1000dòng có mã leading zero, formula, duplicate và lỗi ngày | Preview đúng kiểu/row errors, không thực thi macro/formula; totals đối soát |
| H-T46 | Commit retry, delta cutover và rollback có downstream | Không nhân dữ liệu; delta được duyệt; rollback có downstream bị chặn, dùng correction |
| H-T47 | API/search/AI/file cross-scope, purge gặp legal hold | Tất cả deny đúng scope; hold ngăn xóa; log không chứa PII nhạy cảm |
| H-T48 | Queue replay100lần, schema cũ, restore và đo tải | Không nhân hiệu ứng; unsupported quarantine; restore khớp totals; ghi số đo so H-NFR, chưa đạt thì không enable |

#### 9.18.2 Gates và trách nhiệm rollout

HR-A: HR owner và approver cụ thể; H-O01–05/08–10 được chốt ở phần áp dụng; dữ liệu Excel có đối soát, policy phép/calendar và quyền được duyệt; UAT profile đạt; backup/restore/cutover/rollback diễn tập. Pilot một nhóm đại diện có cả manager/nhân viên, không mặc định triển khai toàn công ty. Nhân viên thực hành xem hồ sơ/xin phép/sửa công, manager duyệt/ủy nhiệm, HR chốt công/import và bàn giao. Sign-off HR nghiệp vụ, QA bằng chứng, IT vận hành, chủ dự án phạm vi go-live.

HR-B: thêm mẫu ca đêm/đổi ca/thiết bị lỗi, clock mapping và owner connector; quy tắc OT được xác nhận. Nếu chưa có thiết bị thì chỉ enable phần ca/OT, không đánh dấu connector đã đạt hoặc chặn HR-A.

HR-C: quyết định INTERNAL/EXTERNAL, cấu hình lương/thuế/bảo hiểm đã được người phụ trách chuyên môn xác nhận, authority chi và bank verification, M10 route/reconcile, tối thiểu hai kỳ song song khớp kết quả đã duyệt và không có sai lệch chưa xử lý. Bắt đầu file chi có duyệt; bank API cần gate riêng với sandbox/provider evidence và xử lý Unknown. Chuẩn bị hỗ trợ kỳ đầu, escalation owner, phương án dừng export/chi khi sai và quyết toán hiệu chỉnh.

HR-D chỉ discovery/backlog: tuyển dụng (requisition/candidate/interview/offer), đào tạo (plan/enrolment/certificate), đánh giá (goals/review/appeal), phúc lợi (eligibility/enrolment). Không có acceptance đầy đủ ở bản này; phải đặc tả trước cam kết triển khai. Không bổ sung suy đoán sức khỏe/nghỉ việc bằng AI vào HR-A/B/C.

<!-- SECTION:A -->
### A.9 Quyết định, tham số mở và tác động chi phí M22

Quyết định đã có: tích hợp HRM vào cùng hệ thống, phân quyền riêng; thay quản lý Excel theo giai đoạn; đặc tả đầy đủ A/B/C, ưu tiên A trước tính lương. Không yêu cầu người dùng duyệt lại quyết định này. Các tham số sau là đầu vào triển khai cần thu thập, không cản trở hoàn thành bộ tài liệu.

| ID | Cần xác nhận / accountable | Khi thiếu |
|---|---|---|
| H-O01 | HR/IT: nhân sự thực tế, pháp nhân, loại lao động, site/timezone, concurrent users, volume file/log | Giữ giả định tải7.9 là đề xuất; không suy45user là45nhân viên |
| H-O02 | HR: file Excel gốc, sheet/owner, mã định danh, số dư phép/công và kỳ cutover | Chỉ thiết kế mapping, chưa chạy import thật |
| H-O03 | HR: mẫu/loại hợp đồng, signature authority, lịch nhắc, thử việc và checklist | Draft/nhắc cấu hình chưa bật, không tự áp loại trong ảnh |
| H-O04 | HR: lịch làm/ca, phép, holidays, rounding công, sửa công/OT và hạn mức | Chặn submit/tính chính thức cần policy, vẫn lưu hồ sơ Draft |
| H-O05 | Chủ dự án: HR approver/backup, privacy owner, scope và self-approval policy | Không tự approve; queue có owner tạm được chỉ định |
| H-O06 | Kế toán/payroll: công thức, tỷ lệ/ngày hiệu lực, người phụ thuộc, cách chia kỳ, INTERNAL/EXTERNAL | HR-C chưa enable, không hard-code tỷ lệ |
| H-O07 | Finance: M10 payment route, bank provider/file format, hạn mức, checker và reconcile | Chưa chi lương/hoa hồng qua M22; không phát hai lệnh chi |
| H-O08 | Privacy/IT: retention từng loại dữ liệu, legal hold, mục đích/căn cứ xử lý và thiết bị | Không mở thu thập sinh trắc/GPS ngoài scope; chưa purge tự động |
| H-O09 | IT/HR: backup/restore targets, tải, owner queue, hỗ trợ và ngưỡng cảnh báo | Gate vận hành chưa đạt; không cam kết SLA chưa đo |
| H-O10 | Chủ dự án/HR: nhóm pilot, tiêu chí sign-off, đào tạo, ngân sách và lịch rollout | Lộ trình là thứ tự đề xuất, không là deadline/budget duyệt |

TCO bổ sung phải tách: làm sạch/migration Excel, phát triển hoặc license HRM, adapter chấm công/payroll/bank, thiết bị nếu mua, storage hồ sơ riêng tư, bảo mật/audit/backup, đào tạo, hỗ trợ kỳ công/lương và cập nhật policy. Không cộng ngân sách này vào dự toán cũ mà không re-estimate; không giả integration miễn phí. Lợi ích đo bằng thời gian xử lý và lỗi thực tế trước/sau, không cộng đôi tiết kiệm giờ với giảm nhân sự khi chưa có bằng chứng.

M22-F01–28 → UC-H01–16/BR-H01–24 → H-T01–48 là ma trận truy vết tại3.16.3; H-NFR01–08 có mapping riêng7.9. Registry được sinh lại từ Master1.9; mọi application verification vẫn Not Run. Quy tắc HRM hoãn trong bản1.8 được thay bằng phạm vi/gate cụ thể này; payroll vẫn giai đoạn sau, không biến M14 thành engine lương.
