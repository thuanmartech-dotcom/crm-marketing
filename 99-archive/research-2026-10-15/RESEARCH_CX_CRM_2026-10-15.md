# Thẩm định chuyên sâu CRM từ góc độ CX và vận hành dịch vụ agency

Ngày nghiên cứu: 15/10/2026, Asia/Saigon. Phạm vi: FR01–02, FR04–08, FR18–19 và FR30–40 trong `CRM_MASTER_BRD_SRS_HOP_NHAT.md` phiên bản 1.2; đọc đối chiếu `PHAN_TICH_PHAN_BIEN_CRM_2026-10-15.md`. Đây là thẩm định tài liệu và đọc mã nguồn tham khảo, không phải kết quả chạy thử hệ thống.

## 1. Kết luận điều hành

Thiết kế đã đúng hướng ở định danh có bằng chứng, tách Contact/Account/Conversation, giữ lịch sử bàn giao, chống gửi trùng và không coi bot trả lời là người thật. Tuy nhiên, **chưa đủ đặc tả để tuyên bố tất cả module đã chuẩn hoặc sẵn sàng giao lập trình**. Khoảng trống lớn nhất không phải thiếu nhiều màn hình; đó là thiếu cam kết dịch vụ có thể thực thi và thiếu vòng khép kín từ trải nghiệm đến khắc phục rồi học hỏi.

Ba lý do kinh doanh cần bảo vệ:

1. **CEO:** biết ai chịu trách nhiệm với cam kết nào, chi phí phục vụ phát sinh ở đâu và tại sao khách rời đi. Doanh thu ký hợp đồng không chứng minh trải nghiệm thành công.
2. **CMO:** chỉ đo inquiry bán hàng đủ điều kiện như đầu vào acquisition; không biến yêu cầu hỗ trợ, phàn nàn hay gửi thêm tài liệu thành lead mới. Khi cam kết bán hàng khác thực tế giao hàng, phản hồi phải trở lại thông điệp và quy trình qualification.
3. **CX:** khách không cần kể lại vấn đề, không bị bỏ quên sau lần phản hồi đầu, biết khi nào được cập nhật và nhận đúng kết quả đã cam kết. Điểm CSAT/NPS chỉ là tín hiệu; hành động phục hồi và ngăn tái diễn mới là vòng quản trị.

Các ưu tiên phải sửa trước baseline:

| Ưu tiên | Khoảng trống cụ thể | Quyết định đề xuất |
| --- | --- | --- |
| P0 | FR36/SLA_Episodes mới nêu first-human-response và resolution | Thêm next-response SLA, thời điểm cập nhật đã hứa và breach history; không cho một lời chào đầu tiên che khuất nhiều ngày im lặng sau đó. |
| P0 | Có nhiều SLA nhưng chưa chốt chủ thể và nguồn ghi nhận | Lead response đo inquiry bán hàng; inbox response đo waiting episode; resolution đo Ticket/case. Link có bằng chứng, không dừng mọi timer của Contact. |
| P0 | FR18 chưa có entitlement snapshot theo hợp đồng/gói dịch vụ | Ticket ghi hợp đồng/đầu ra/phạm vi hỗ trợ, support calendar, phiên bản SLA và cách phân loại defect/change. Luôn tiếp nhận khiếu nại; không chặn ghi nhận chỉ vì hết quota. |
| P0 | P1 đang gom mất quyền, rò rỉ tài sản, campaign sai | Thêm impact × urgency, incident owner, containment và escalation. Sự cố quảng cáo đang tiêu tiền sai không nên chờ hết giờ hỗ trợ thông thường nếu hợp đồng có trực. |
| P0 | FR39 có mô tả liên kết nhưng schema chưa chỉ ra quan hệ đủ cụ thể | Bổ sung link Conversation–Ticket/Inquiry/Deal/Project có scope và audit; nhiều cuộc hội thoại có thể cùng một vấn đề, một hội thoại có thể chứa nhiều yêu cầu. |
| P0 | State machine conversation đang trộn công việc, assignment và lifecycle | Tách lifecycle, assignment/queue và waiting party; chuyển người không đổi lifecycle hoặc reset SLA. |
| P0 | FR35 dùng từ lease nhưng schema không có expiry/fencing | Chọn durable assignment với compare-and-swap; chỉ thêm lease nếu thực sự cần và có token/expiry/fencing. Chỉ báo đang gõ không phải khóa chống gửi trùng. |
| P0 | Điểm thấp chỉ tạo task, thiếu quy trình phục hồi | Recovery case có owner, due, nguyên nhân, hành động, quyền bồi hoàn và xác nhận kết quả; escalation khi không liên hệ được. |
| P1 | Health score/gia hạn có nhắc nhưng không đủ định nghĩa | Quy tắc explainable, tính tại Account/Contract, dữ liệu thiếu = Unknown; không coi ít ticket là khỏe hoặc trả tiền đều là hài lòng. |
| P1 | Chưa đủ vòng học hỏi ở cấp hệ thống | Gộp chủ đề lỗi lặp, assign cải tiến cho Delivery/CMO/Finance, đo tái diễn và phản hồi lại khách khi thích hợp. |

Các giá trị 5/15 phút, 30 phút, 7 ngày, 45/30/15 ngày và 90 ngày là **chính sách đề xuất để pilot**, không có nguồn nào biến chúng thành chuẩn phổ quát cho agency.

## 2. Bằng chứng bên ngoài và giới hạn

Ký hiệu: **D** = tài liệu chính thức; **C** = đọc file mã nguồn thật; **S** = suy luận/thiết kế đề xuất cho dự án. Không dùng sự hiện diện của chức năng ở nhà cung cấp làm bằng chứng rằng doanh nghiệp này bắt buộc phải mua hay tự xây chức năng đó.

| Mã | Nguồn đã đọc | Quan sát kiểm chứng được | Áp dụng và giới hạn |
| --- | --- | --- | --- |
| CX01 D | [Chatwoot: Service Level Agreements](https://app.chatwoot.com/hc/user-guide/articles/1713167310-service-level-agreemtns) | Phân biệt FRT, NRT và RT; gắn SLA qua điều kiện automation. | Cơ sở tham khảo để phát hiện thiếu next-response; không sao chép ngưỡng mẫu thành SLA hợp đồng. |
| CX02 C | [Chatwoot `sla_policy.rb`](https://github.com/chatwoot/chatwoot/blob/develop/enterprise/app/models/sla_policy.rb) | Có threshold first/next/resolution và cờ business hours. | Xác nhận cấu trúc ba loại đồng hồ tồn tại trong mã, thuộc thư mục Enterprise. |
| CX03 C | [Chatwoot `applied_sla.rb`](https://github.com/chatwoot/chatwoot/blob/develop/enterprise/app/models/applied_sla.rb) | NRT dùng `conversation.waiting_since`; trạng thái gồm active, hit, missed, active_with_misses; hàm deadline dùng lịch hỗ trợ khi được cấu hình. | Tham khảo bảo toàn vi phạm và episode khách chờ; không chứng minh mọi trường hợp pause/reopen của dự án đã được hỗ trợ. |
| CX04 C | [Chatwoot `contact_inbox.rb`](https://github.com/chatwoot/chatwoot/blob/develop/app/models/contact_inbox.rb) | Khóa unique inbox/source_id; mapping contact–inbox riêng; có thuộc tính hmac_verified. | Cơ sở tách người và định danh theo kênh; HMAC của widget không tự chứng minh cùng con người ở Facebook, email và Zalo. |
| CX05 C | [Chatwoot `conversation.rb`](https://github.com/chatwoot/chatwoot/blob/develop/app/models/conversation.rb) | Có account, inbox, contact, contact_inbox, assignee và waiting_since riêng. | Ủng hộ tách các khái niệm, không suy từ đây rằng kiến trúc agency workspace được sản phẩm giải quyết sẵn. |
| CX06 C | [Chatwoot `csat_survey_response.rb`](https://github.com/chatwoot/chatwoot/blob/develop/app/models/csat_survey_response.rb) | Rating giới hạn 1–5; gắn message, conversation, contact; message_id unique; review notes có người/thời điểm cập nhật riêng. | Tham khảo provenance và chống lặp; rule một survey/ticket là quyết định dự án, không phải suy ra tự động từ unique message. |
| CX07 D/C | [Root license](https://github.com/chatwoot/chatwoot/blob/develop/LICENSE), [Enterprise license](https://github.com/chatwoot/chatwoot/blob/develop/enterprise/LICENSE) | License gốc tách thư mục enterprise; giấy phép enterprise có điều kiện sử dụng production và seat. | Không được lập ngân sách “GitHub có code nên SLA dùng miễn phí”. Xác nhận edition và điều khoản khi lựa chọn nền tảng. |
| CX08 D | [Microsoft: Configure SLAs](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/define-service-level-agreements) | Cho nhiều KPI với thời điểm bắt đầu khác nhau, lịch làm việc và pause criteria theo KPI; cảnh báo field thay đổi có thể hủy SLA item. | Cơ sở thiết kế SLA facts theo policy version, không suy mọi sản phẩm có cùng cơ chế. |
| CX09 D | [Microsoft: Entitlements](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/create-entitlement-define-support-terms-customer) | Quyền hỗ trợ có thời hạn, loại dịch vụ, số giờ/case, kênh, contact và SLA. | Tham khảo khái niệm entitlement; không chép tùy chọn chặn tạo case khi quota hết vào luồng khiếu nại agency. |
| CX10 D | [Bain: Closing the loop](https://media.bain.com/Images/LOYALTY_INSIGHTS_Closing_the_loop.pdf) | Phản hồi cần được liên hệ để hiểu/khắc phục và chia sẻ bài học với frontline/lãnh đạo. | Cơ sở vòng phục hồi và cải tiến. Nguồn phương pháp lâu năm, không dùng như benchmark hiệu suất 2026. |
| CX11 D | [Qualtrics: Customer Effort Score](https://www.qualtrics.com/en-au/articles/customer-experience/customer-effort-score/) | CES đánh giá mức công sức để giải quyết yêu cầu hoặc hoàn thành tương tác. | Dùng có chọn lọc ở onboarding/hỗ trợ; không cộng tùy tiện CES, CSAT và NPS thành điểm chung. Không dùng các tỷ lệ marketing trong bài để cam kết ROI. |
| CX12 D | [Facebook Help: Automated greeting](https://www.facebook.com/help/1698046970464236/) | Facebook mô tả greeting/instant reply là phản hồi tự động cấu hình trong Business Suite. | Chứng minh cần phân biệt autoack với phản hồi người thật. Không dùng làm tài liệu API permissions. |
| CX13 D | [Meta: Lead Generation Guide](https://about.fb.com/ltam/wp-content/uploads/sites/14/2023/11/LeadGenerationGuide.pdf) | Tài liệu Meta có hướng đồng bộ lead vào CRM để xử lý tiếp. | Chứng cứ mục đích tích hợp; tài liệu cũ không chứng minh quyền, phiên bản API hay cửa sổ gửi hiện tại. |

**Giới hạn Facebook:** đã tìm trên Facebook Help và Meta chính thức, nhưng các trang developer về Messenger policy overview/send messages/user profile trả lỗi truy cập trong phiên. Vì vậy **không chứng nhận quy tắc cửa sổ gửi, HUMAN_AGENT, app review hay quyền cụ thể cho ngày 15/10/2026**. Không dùng bài bán phần mềm, bài group hoặc Reddit thay cho policy hiện hành. Đây là gate xác minh của connector trước pilot, không phải lý do bỏ chức năng policy gate. Không có nghiên cứu group Facebook riêng tư hay phỏng vấn người vận hành thực tế trong lần này.

**Giới hạn GitHub:** đã đọc trực tiếp nội dung các file trên nhánh `develop`; chưa khóa được commit SHA, chưa clone, build hay chạy test. Nhánh có thể thay đổi. Khi đưa vào ADR hoặc PoC phải pin release/commit + edition + license, rồi chạy UAT của dự án. Mã nguồn đọc được là bằng chứng cấu trúc, không phải bằng chứng tính đúng runtime.

## 3. Rà từng chức năng: vì sao cần, liên kết và điều kiện đúng

Đánh giá bên dưới là **S** dựa trên tài liệu dự án và bằng chứng ở mục 2. “Giữ và hoàn thiện” không có nghĩa triển khai hiện tại đã đạt.

| FR | Đánh giá/phạm vi | Vì sao cần trong agency | Liên kết bắt buộc | Quy tắc vận hành và kiểm thử phân biệt đúng/sai |
| --- | --- | --- | --- | --- |
| FR01 Hồ sơ | Giữ, P0 | Một người có thể là approver của công ty A và billing của B; cùng một Account có nhiều stakeholder. Gộp sai làm gửi nhầm hợp đồng hoặc mất continuity. | FR02/31 identity; FR04 inquiry; FR15 contract; FR18 case; FR19 survey; consent; ACL | Vai trò có hiệu lực theo thời gian và nguồn xác minh. Người liên hệ chuyển công ty không kéo toàn bộ dữ liệu công ty cũ sang công ty mới. UAT: cùng Contact có hai vai trò thuộc hai Account, user chỉ thấy Account được cấp. |
| FR02 Merge | Giữ, P0; tự động mạnh ở P1 | Chống tạo nhiều hồ sơ nhưng phải tránh tiết lộ dữ liệu sau gộp nhầm. | FR01, FR31, journal, consent, FR37 search/AI | Scoped identity là bằng chứng; phone/email trùng chỉ tạo candidate khi chưa chắc. Merge transaction có preview, survivor, provenance; không OR consent. UAT: hotline chung không merge; undo giữ lịch sử gửi và yêu cầu steward xử lý thay đổi phát sinh. |
| FR04 Pipeline | Sửa rõ entity, P0 | Cơ hội có nhiều bước mua, nhưng người chưa có nhu cầu mua không nên thành forecast. | Inquiry/Lead → Contact/Account → Deal; FR14 quote; FR15 handoff; FR28 KPI | SRS đang mô tả pipeline từ New đến Won nhưng nói Nurture là lead: phải chốt Lead và Deal mỗi entity giữ stage nào, conversion idempotent, qualification reason và source snapshot. UAT: khách đang mua hỏi hỗ trợ không sinh Deal; khách mới chưa biết budget ghi Unknown. |
| FR05 Routing/SLA lead | Giữ, bổ sung P0 | Lead không mất khi người cũ nghỉ; continuity hữu ích nhưng không vượt quyền hoặc giữ lead vô hạn. | FR04, FR35 workforce; FR36 SLA; FR07 evidence | Tách accept assignment, first attempt, first connected và first substantive response. Không cho “gửi thành công” mơ hồ tính là liên hệ thành công. Thu hồi xử lý race với call đang chạy bằng version/transaction. UAT: hai nhân viên claim chỉ một thắng; activity về muộn không xóa lịch sử trễ. |
| FR06 Năng suất | Giữ, P0 đơn giản | Dữ liệu 100 lead/tháng không biện minh chia đều 30 Sales; counting thao tác dễ tạo hoạt động rỗng. | FR05 capacity; FR25 work; FR28 dictionary; CX outcomes | Đo workload theo thời gian xử lý và backlog, không riêng số lead. Tách ca, part-time, kỹ năng và việc phục vụ khách hiện tại. UAT: một Sales chăm 10 hợp đồng không bị xem là “rảnh” chỉ vì ít lead. |
| FR07 Hội thoại tổ chức | Giữ, P0 ở kênh pilot | Giữ cam kết khách, giảm kể lại và bàn giao; không phụ thuộc tài khoản cá nhân. | FR30–40, FR18 case, FR15 scope | Conversation gắn sender account và thread; source capability rõ. Ghi chú nội bộ là message type riêng. UAT: đổi Page phải tạo/chọn thread phù hợp; private note không lọt vào transcript gửi khách. |
| FR08 Masking/offboarding nhân sự | Giữ, P0 | Bảo vệ dữ liệu và đảm bảo khách không bị bỏ lại khi nhân sự rời đi. | Identity/ACL; queues; credentials; scheduled intents; open objects | Offboarding phải xử lý cả bản nháp, scheduled sends, approval đang chờ, automation do user sở hữu và private tasks. Không xóa actor lịch sử. UAT: token cũ không dùng được, file URL kiểm quyền, scheduled message của người nghỉ không tự chạy nếu mất authority. |
| FR18 Ticket | Giữ và nâng cấp, P0 | Khiếu nại, lỗi deliverable, yêu cầu mới và sự cố có chi phí/owner khác nhau. | FR15 contract/acceptance; FR25 task; FR16 refund; FR19 feedback; FR39 links | Intake luôn mở, triage xác định complaint/incident/defect/change/question. Entitlement snapshot và authority quyết định xử lý/tính phí; không bắt khách biết phân loại. UAT: hết vòng sửa nhưng lỗi agency vẫn được nhận/sửa theo cam kết; mất quyền chưa rõ contact vẫn ghi nhận vào queue xác minh. |
| FR19 CSAT/NPS | Giữ tối thiểu; CSAT P0, relationship NPS P1 | Cần biết trải nghiệm và nguyên nhân, nhưng khảo sát sau ticket không đo toàn bộ quan hệ agency. | Ticket, deliverable, Account/role, recovery case, renewal, FR24 learning | Một survey/ticket cần định nghĩa reopen/cooldown và lần gửi thất bại. Lưu eligible/sent/delivered/responded, score gốc, câu hỏi/version. UAT: close replay không spam; reopen trước gửi thì hoãn; điểm thấp tạo một recovery case và không sửa điểm. |
| FR30 Channel registry | Giữ P0 cho kênh thực dùng; năm kênh theo gate | Tránh tuyên bố “tích hợp” khi chỉ cài app nhưng chưa có quyền/read history/send. | Credentials, FR33/34, FR38, capability matrix | State disconnected/pending_review/connected/degraded/revoked; permission, API version, owner và evidence checked_at. UAT: token còn sống nhưng quyền Page bị gỡ phải degraded/revoked, không xanh giả. |
| FR31 Cross-channel identity | Giữ P0 manual-assisted | Hợp nhất đúng giảm hỏi lại; hợp nhất sai gây lộ dữ liệu và gửi nhầm. | FR01/02, connection, consent, FR37 | Một ID trong provider phải có namespace cụ thể. Không dùng avatar, tên, text chat làm xác minh. UAT: cùng provider_subject_id trong hai connection giữ riêng; OTP chỉ liên kết đúng scope/mục đích. |
| FR32 Unified inbox | Giữ P0 | Người xử lý có ngữ cảnh nhưng vẫn biết đang trả lời ở đâu và tới ai. | FR07, identity, FR39, permissions | Tách lifecycle khỏi queued/assigned, bổ sung recipient preview và quyền từng thread. UAT: Contact được xem không tự mở mọi conversation; BCC chỉ nội bộ người được phép. |
| FR33 Inbound | Giữ P0 | Provider gửi trùng/lệch thứ tự không được sinh nhiều khách, nhiều SLA hoặc nhiều email. | Inbound_Events, Messages, identity, SLA, outbox, checkpoints | Durable write trước ACK; dedup theo scope provider; backfill không kích marketing. Live delayed event phải giữ occurred/received và đo provider lag riêng. UAT: replay 100 lần, status delivered đến trước accepted, crash giữa event/message/outbox. |
| FR34 Outbound | Giữ P0 | Hai người hoặc retry không được gửi trùng báo giá, lời hứa hoặc nhắc nợ. | Consent/suppression, channel policy, FR35 assignment, FR40 files | Intent idempotency, recheck quyền/recipient/consent tại send time; unknown_outcome đi reconcile. Một intent khác ID nhưng nội dung giống không tự dedup bằng text. UAT: withdraw consent sau queue trước send chặn marketing; timeout không tự coi thất bại rồi gửi lần hai. |
| FR35 Assignment | Sửa thuật ngữ lease, P0 | Cần một người chịu trách nhiệm hiện tại, vẫn cho chuyên gia cộng tác. | FR05, team/shift/capacity, FR36, handoff | Durable assignment unique active + row_version đủ cho MVP. Nếu lease thì thêm expiry, renewal và fencing kiểm ở send để người giữ lease cũ không gửi. UAT: nhận đồng thời, ca kết thúc, người cũ mở tab rồi gửi sau khi chuyển người. |
| FR36 SLA | Sửa P0 | Khách có thể bị bỏ quên sau first reply; tốc độ đầu không thay chất lượng hoàn tất. | FR05, FR18, Messages, SLA_Episodes, business calendar, FR38 | Thêm next-response và promised update; clocks theo case/episode, không theo toàn Contact. Bot/autoack/private note không hoàn thành human clock. UAT: 5 tin liên tiếp không dời due từ tin đầu chưa trả lời; chuyển nhóm không reset; pending_internal không pause để làm đẹp KPI. |
| FR37 Search/preview | Giữ P0 | Lọc ở trang hồ sơ chưa đủ; snippet, count, AI và attachment có thể lộ dữ liệu. | ACL tenant/workspace/row/field; identity merge; retention | Query và hậu kiểm tài liệu cùng phạm vi; cache có permission version; revoke/merge cập nhật index. UAT: user mất quyền sau khi kết quả đã cache không mở file/snippet; count không tiết lộ thread cấm. |
| FR38 Sync health | Giữ P0 ở kênh pilot | Inbox trống có thể là không có khách hoặc hệ thống mất kết nối; CEO cần phân biệt. | Connection, raw events, checkpoints, retry, alerts, privacy retention | Owner cảnh báo + runbook + thời gian khôi phục; coverage unknown không ghi 100%. Reconcile/replay có dry run, kiểm effect. UAT: hết token, mất webhook, backlog, payload đã hết retention; dashboard ghi dữ liệu không đủ. |
| FR39 Business links | Sửa schema P0 | Một complaint có thể đi qua Facebook và email; nhiều vấn đề có thể nằm trong cùng thread. | Conversation ↔ Inquiry/Ticket/Deal/Contract/Project; FR28 attribution | Link N:M có purpose/actor/source, scope và thời gian; một case có source conversation chính nhưng không mất các thread còn lại. Không gộp case chỉ vì cùng Contact. UAT: một khách hỏi quote và phàn nàn hóa đơn tạo hai work items và hai nghĩa vụ phản hồi. |
| FR40 Email/file | Giữ P0 | Email có nhiều người nhận, tài liệu hợp đồng và file thiết kế chứa thông tin nhạy cảm. | Messages/Participants, assets/scan, outbound policy, retention | Kiểm From/To/CC/reply-all và permitted sender, quarantine, MIME thực, kích thước, URL expiry. Khi scan lỗi cho trạng thái pending, không silently drop. UAT: file có đuôi ảnh nhưng thực thi bị chặn; forward không đem theo internal notes/BCC. |

## 4. Logic SLA cần sửa thành đặc tả thực thi

### 4.1 Chủ thể và bốn cam kết khác nhau

| Nghĩa vụ | Bắt đầu | Dừng thành công | Không được coi là thành công |
| --- | --- | --- | --- |
| Lead first attempt | Inquiry mới hợp lệ vào hàng đợi theo lịch sales | Attempt có evidence trong đúng inquiry | Mở contact; gọi về khiếu nại khác; chỉ đổi stage |
| First human response | Inbound cần phục vụ đầu episode | Phản hồi người thật gửi qua kênh cho phép, đáp ứng định nghĩa substantive reply | Bot greeting; note nội bộ; accepted chưa rõ kết quả nếu policy yêu cầu gửi thành công |
| Next response | Tin đầu tiên chưa được đáp của khách sau lần trả lời trước | Agent phản hồi cho vấn đề đang chờ | Mỗi tin khách gửi lại làm reset due; assignment change |
| Resolution/mitigation/update | Case mở / sự cố bắt đầu / lời hứa cập nhật | Evidence kết quả hoặc hành động cập nhật đúng nghĩa vụ | Đóng conversation để né case; chờ nội bộ bị coi như chờ khách |

Đề xuất `SLA_Episodes` thêm `subject_type/subject_id` (hoặc FK cụ thể với ràng buộc), `episode_id`, `clock_type`, `policy_version`, `calendar_version`, `start_event_id`, `completion_event_id`, `breach_at`, `pause_reason`, `exception_ref`. Mỗi loại đồng hồ dùng một `source of truth`; bảng Tickets có thể giữ due_at projection nhưng không được tự tính khác với SLA engine.

Thời điểm bắt đầu cần hai cách nhìn: SLA nội bộ tính từ CRM nhận được event hợp lệ; trải nghiệm khách tính từ event khách gửi khi timestamp nguồn đáng tin. Báo riêng provider delay, không sửa timestamp để làm đẹp báo cáo. Backfill lịch sử không sinh hàng loạt breach vận hành hiện tại, nhưng phải có nhãn coverage/historical mode.

Trong giờ hỗ trợ 08:30–17:30 không mặc định có nghĩa 9 giờ liên tục nếu tổ chức nghỉ trưa. Cần calendar intervals, ngày nghỉ, múi giờ và version. Không thay đổi calendar hồi tố để xóa vi phạm. Provider outage có thể được phân tích trách nhiệm riêng nhưng không biến thời gian khách chờ thành bằng không.

### 4.2 Priority và incident

Phân loại severity theo tác động, phạm vi và khẩn cấp; ví dụ campaign đang chi tiền sai, lộ asset hay mất quyền quảng cáo cần playbook khác “không mở được một file”. Tên mức nên tách `Severity S1/S2/S3` khỏi `P0/P1/P2` của backlog để tránh hiểu nhầm. Chỉ số response, containment/mitigation và permanent resolution không dùng chung một timestamp.

Lưu `impact`, `urgency`, `severity_reason`, `incident_owner`, `affected_contracts/assets`, `mitigation_at`, `next_customer_update_at`. Công cụ CRM nhắc và ghi nhận, không tự được cấp quyền tắt campaign hoặc đổi tài khoản nhận tiền. Nếu không có on-call và hợp đồng 24/7 thì mô tả giờ tiếp nhận/giờ xử lý trung thực; tiếp nhận tự động 24/7 không đồng nghĩa có người xử lý 24/7.

## 5. Bổ sung lifecycle CX đúng đặc thù dịch vụ marketing

Các đề xuất sau nối vào module hiện có, không nhất thiết tạo thêm hệ thống độc lập.

### 5.1 Onboarding có định nghĩa giá trị đầu tiên

FR15/UC06 đã có handoff, tiền ứng, asset checklist và kickoff. Cần thêm success plan: mục tiêu khách, baseline, người phê duyệt, nhịp cập nhật, kết quả đầu tiên có thể kiểm chứng, rủi ro và trách nhiệm hai bên. Có thể là field/checklist của Project trong MVP.

Luồng đề xuất: `handoff_pending → accepted → prerequisites_pending → kickoff_ready → active → first_value_verified`. Mỗi prerequisite có owner, due, evidence và blocker. Khách thiếu asset chỉ chuyển trạng thái chờ; không tự dời nghĩa vụ hợp đồng nếu chưa có phê duyệt thay đổi. “First value” là kết quả đã thống nhất như tài khoản tracking được kiểm chứng hoặc deliverable đầu được chấp thuận; không mặc định là ROI/doanh số mà agency không kiểm soát.

UAT: sales hứa 20 bài nhưng SOW 12 bài thì xuất hiện discrepancy task trước kickoff; một payment xác nhận không tự nghĩa là đã sẵn sàng triển khai; gỡ người phê duyệt khỏi Account buộc xác nhận approver mới.

### 5.2 Voice of Customer và phục hồi

CSAT tại ticket, feedback tại milestone và NPS quan hệ là ba ngữ cảnh riêng. Với B2B, lưu vai trò người trả lời và Account; không để Account có 10 contact vô tình nặng gấp 10 lần Account có 1 contact trong chỉ số điều hành. Báo view contact-level và account-level với cách chọn/weight công bố; không suy “người dùng thích” đồng nghĩa “người quyết định tái ký”.

Khảo sát ngắn, tự nguyện, có frequency cap ở contact/account, xử lý channel permission tại thời điểm gửi. Không gửi khảo sát tự động vào lúc đang có incident nghiêm trọng mà chưa kiểm policy; không chỉ khảo sát người được nhân viên chọn vì dễ cho điểm cao. Response rate cần định nghĩa rõ mẫu số: eligible, sent hay delivered; báo các denominator riêng nếu delivery không quan sát được.

Recovery state: `detected → triaged → owner_accepted → contacted → remedy_agreed → remedy_done → verified → closed`. Không liên hệ được có lịch thử lại hữu hạn và lý do đóng khác “đã hài lòng”. Khách không muốn gọi lại phải được tôn trọng. Remedy có thể là sửa đầu ra, giải thích hóa đơn, điều chỉnh lịch hoặc refund theo authority; gắn FR15/16/18/25. Không yêu cầu khách sửa điểm cũ sau phục hồi.

Ở outer loop, root cause theme liên kết CR/backlog cải tiến, owner và ngày đánh giá tái diễn. Một lỗi tracking lặp ở 5 khách cần thay checklist launch FR23, không chỉ đóng 5 tickets riêng. Một phàn nàn về “Sales hứa doanh số” cần nối qualification/báo giá và thông điệp CMO.

### 5.3 Health, gia hạn và offboarding khách

Health score giải thích được nên gồm độ đạt kết quả cam kết, trễ deliverable, reopen/escalation, stakeholder coverage, mức độ tham gia và payment risk. Không dùng doanh thu/CSAT làm toàn bộ health; không có phản hồi là Unknown. Lưu window, weight/version và từng component; nợ thanh toán là financial risk, chưa chứng minh khách bất mãn. Ở quy mô hiện tại, red/amber/green với lý do rõ và AM review tốt hơn ML.

Nhắc 45/30/15 ngày phải so với ngày notice/renewal clause của hợp đồng, không chỉ expiry. Một hợp đồng yêu cầu báo trước 60 ngày không thể đợi ngày còn 45 mới bắt đầu. Renewal opportunity có link original contract và loại renew/expand/downsell; không sửa deal cũ hoặc tự gia hạn bằng timer.

UC10 đã nhắc asset return; cần state kết thúc riêng: quyết định không tái ký → chốt phạm vi còn lại → bàn giao asset/source file/quyền truy cập theo hợp đồng → đối soát → xác nhận → hạn chế/xóa theo retention. Phân biệt offboarding nhân viên FR08 và offboarding khách. Không thu hồi quyền của khách đối với tài sản thuộc khách chỉ để gây sức ép thanh toán; tranh chấp phải theo authority/hợp đồng.

## 6. Các bất nhất kỹ thuật cần chốt với BA/CTO

1. **Lifecycle conversation:** `new → queued → assigned → open → pending...` trộn status xử lý với assignment. Nên giữ `lifecycle = open/resolved/closed`, `waiting_party = agent/customer/internal/none`, assignment/queue là dữ liệu riêng; reopen là event mở episode. Có thể dùng enum khác, miễn semantics đồng nhất ở API, UI, reporting.
2. **Ticket status khác conversation status:** Tickets có Open/InProgress/WaitingCustomer/Resolved/Closed còn conversation có reopened/pending_internal. Cần transition map rõ; đóng thread không tự đóng ticket đang điều tra, resolved case không bắt buộc xóa/mất thread.
3. **Schema chưa thể hiện link FR39:** cần N:M có type/ID FK hợp lệ hoặc từng link table typed. JSON generic entity_id không được dùng để né foreign key và workspace isolation.
4. **Conversations uniqueness nhắc connection nhưng row chưa khai báo connection_id:** chọn thêm connection_id với composite FK consistency hoặc unique theo inbox/provider scope phù hợp. Không viết migration từ mô tả hiện tại mà đoán.
5. **SLA_Episodes chưa đủ liên kết Ticket/Inquiry:** hiện chỉ conversation_id, trong khi cả Lead và Ticket có SLA. Chốt có một engine nhiều subject hay nhiều policy engine; tránh ba đồng hồ có ba cách tính.
6. **“Một assignee giữ lease” thiếu trường lease:** durable assignment là lựa chọn đơn giản hợp lý; nếu dùng lease cần fencing, không chỉ timeout client.
7. **Unverified identity có contact NULL, Tickets contact NN:** cần tạo provisional contact riêng hoặc intake chưa có ticket chính thức có ownership và SLA triage; không từ chối tiếp nhận sự cố khẩn chỉ vì thiếu hồ sơ hoàn chỉnh.
8. **Consent theo Contact + channel chưa đủ endpoint:** nếu một Contact có hai email/số điện thoại, cần xác định grant/revoke áp endpoint nào, mục đích, tổ chức và provenance. Cơ chế suppression không được biến mất khi merge/unmerge hoặc restore. Đây là yêu cầu thiết kế; nghĩa vụ pháp lý cụ thể cần nguồn luật và review riêng.
9. **Workspace chưa thống nhất:** lõi `client_workspace_id NULL` khác omni `workspace_id NOT NULL`; parent review đã phát hiện. Chốt agency workspace mặc định, client workspaces và composite FKs trước nối Contact/Case/Conversation.
10. **Chỉ báo typing không chống reply trùng:** phối hợp là UX; send cần kiểm assignment version và outbound idempotency. Supervisor override phải audit và không phá nghĩa vụ hỗ trợ.

## 7. Bộ nghiệm thu bổ sung tập trung CX

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

## 8. Cách triển khai phù hợp nhất với quy mô hiện tại

P0 gồm intake, identity có review thủ công, một–hai kênh thực dùng, owner/queue, response clocks rõ, ticket/defect/change, entitlement snapshot, handoff, recovery đơn giản và dashboard overdue. Chỉ cần các field, view, workflow và liên kết trong CRM có sẵn nếu sản phẩm đáp ứng; không cần tự xây một CDP hay contact center hoàn chỉnh để phục vụ khoảng 100 lead/tháng.

P1 bổ sung NPS quan hệ B2B, health score explainable, kế hoạch account review, taxonomy root cause và tự động hóa có dữ liệu pilot. Chỉ thêm CES khi biết tương tác nào cần giảm công sức và ai sẽ sửa nó. Cần đo workload hỗ trợ thật trước khi mở thêm pool inbound hoặc cam kết SLA cao hơn.

Chatwoot là ứng viên cho inbox/support, **không tự thay CRM thương mại, quản lý SOW, tiền và gia hạn của agency**. Nếu hybrid, chọn CRM làm nguồn chuẩn Contact/Account/Contract/Ticket nghiệp vụ hoặc quy định rõ Ticket system of record ở support; không có hai master ghi đè lẫn nhau. Mapping qua immutable external IDs, event outbox, dedup và reconciliation; quyền workspace phải được kiểm riêng. PoC xác minh license/edition và từng UAT trước quyết định.

Người vận hành phải có tên cụ thể: AM chịu trách nhiệm quan hệ và recovery; Delivery chịu trách nhiệm khắc phục; Sales giữ qualification/handoff; Finance giữ refund/payment; Operator giữ connector; CX owner quản survey, root cause và chất lượng phục hồi. Một người có thể kiêm nhưng dashboard vẫn phải phân biệt nghĩa vụ.

**Tiêu chí go-live:** BA chốt các rule còn mở; mỗi kênh có capability evidence; critical UAT pass; có owner trực và escalation thật; dữ liệu pilot cho phép đo thời gian khách chờ, kết quả sửa lỗi và tính đúng liên kết. Chưa có bằng chứng runtime thì chỉ kết luận “thiết kế đã được rà”, không kết luận “hệ thống đã chuẩn”.
