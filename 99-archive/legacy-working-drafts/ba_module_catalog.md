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
| [M16](#module-m16) | Dự án, milestone, đầu ra, sửa đổi và nghiệm thu | AM, Delivery, khách có quyền | Project/deliverable/version/acceptance/change | M08/M11/M13/M15/M17 | P0 đầu ra/milestone; task/capacity chi tiết P1 |
| [M17](#module-m17) | Ngân sách, chi phí, nguồn tiền media và rủi ro hiệu quả | CMO, Finance, Delivery lead | Budget/commitment/cost/funding authorization | M07/M09/M15/M16/M18 | Cơ bản khi có chi phí/media; forecast nâng cao P1 |
| [M18](#module-m18) | Từ điển chỉ số, báo cáo điều hành và attribution | CEO, CMO, Sales/CX/Finance | KPI definition/metric facts/report snapshot | Nhận dữ kiện có quyền từ các module | P0 số liệu lõi; attribution nâng cao P1/P2 |
| [M19](#module-m19) | Kết nối bên ngoài, nhận/phát sự kiện và phục hồi | Integration operator | Connection/capability/inbox/outbox/checkpoint | M03/M09/M18/M20 | P0 một nguồn/kênh; connector khác theo quyền thực tế |
| [M20](#module-m20) | Consent, yêu cầu dữ liệu, retention và quản trị mục đích | Privacy owner, steward, owner | Processing/consent/suppression/privacy/retention | Tất cả module xử lý dữ liệu cá nhân | Kiểm soát P0 từ ngày đầu; không đợi có engine riêng |

**Ranh giới không được nhập nhằng:** M01 sở hữu người/doanh nghiệp; M02 sở hữu nhu cầu và quyết định mua; M03 sở hữu luồng trao đổi; M08 sở hữu cam kết hợp đồng; M16 sở hữu công việc/đầu ra; M09 sở hữu tiền và phân bổ quản trị, ERP vẫn sở hữu chứng từ hạch toán. M10 dùng kết quả cash đủ điều kiện, không tự xác nhận tiền. M18 đọc dữ liệu có nguồn, không sửa giao dịch để làm đẹp báo cáo. M14 cấp quyền theo authority; M20 giới hạn mục đích dữ liệu; hai module đều không cho người dùng tự vượt quyền.

**Luồng tham chiếu:** M19→M01→M02→M07→M08→M09/M16→M11/M12→M08 tái ký. M03 giữ trao đổi và gắn đúng work item suốt luồng. M13 hỗ trợ lịch; M15/M17 hỗ trợ lập kế hoạch và thực thi; M04 tự động hóa hành động đã đủ điều kiện; M18 đo kết quả. M05/M06 chỉ mở khi có nhu cầu và điều kiện kiểm soát.

**Hợp đồng thao tác chung:** giao diện hiển thị field bắt buộc, giá trị chưa biết, readonly, lý do thao tác bị chặn và hành động khắc phục. Server là nơi quyết định validation, quyền và transition; ẩn nút không thay authorization. Create/change command có operation ID, scope lấy từ phiên/connection hợp lệ, expected_version khi có cạnh tranh; cùng key khác payload trả409. Không đủ quyền trả403 hoặc404 theo chính sách không tiết lộ tồn tại; thiếu dữ liệu trả422 có field/error code; dependency tạm lỗi trả trạng thái Pending/Blocked có owner, không giả Success. Mọi thay đổi có actor/time/source/history; các tác động liên module theo transaction/outbox, không sửa trực tiếp dữ liệu module khác.

**Màn hình điều hướng sản phẩm:** Công việc hôm nay; Khách hàng; Lead/Cơ hội; Hộp thư; Báo giá; Hợp đồng; Dự án/Đầu ra; Tài chính/Hoa hồng theo quyền; Hỗ trợ/Phản hồi; Lịch; Marketing; Báo cáo; Quản trị. Menu chỉ hiện module được bật và được cấp quyền. Admin không mặc nhiên thấy màn hình tiền/hợp đồng; người dùng cá nhân có thể kiêm vai được khai báo rõ.

Các mục số hiện hữu được giữ để không làm đứt FR/UC/schema. M03 có mô tả nghiệp vụ tại3.3 và hợp đồng kỹ thuật tại3.12; hai phần thuộc cùng module, không là hai inbox. M14 dùng3.8.2/6.1, M19 dùngChương2, M20 dùng6.3/6.4. Ngưỡng và phạm vi mở theo A.6/9.5, không suy rằng20 module phải triển khai đủ trong MVP.
