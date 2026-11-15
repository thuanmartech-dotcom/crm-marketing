import json
from pathlib import Path

cards = []

def add(id, title, insert_before, markdown):
    cards.append(dict(id=id, title=title, insert_before=insert_before, markdown=markdown.strip()+"\n\n"))

add('M03', 'Omnichannel Inbox và bảo vệ nội dung', '#### 3.3.1 FR07 Hội thoại thuộc tổ chức', r'''
##### M03. Đặc tả BA — Omnichannel Inbox và bảo vệ nội dung

**Mục đích, tác nhân và phạm vi:** Sales/AM/CX tiếp nhận, phân công và trả lời yêu cầu trên tài khoản doanh nghiệp được phép; trưởng nhóm xử lý quá tải, steward xác minh liên kết danh tính. M03 sở hữu trải nghiệm hội thoại; M19 sở hữu connector, M20 sở hữu mục đích và suppression. P0 mở một inbox/kênh; các kênh khác mở theo capability đã kiểm, không mặc định đầy đủ năm kênh.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M03-F01 Thu nhận | Event đã xác minh, connection, provider IDs | Nếu trùng canonical event thì no-op; nếu chưa rõ người thì giữ identity/provisional đúng luồng intake; không tạo Lead từ status/read event | Message/thread đúng scope; FR30/31/33, M19 |
| M03-F02 Phân loại yêu cầu | Tin inbound, request đang mở | Nếu complaint thì link Ticket; inquiry mới thì đề xuất Lead; chưa rõ thì queue phân loại với thời gian chờ gốc | Business_Subjects và link; FR39, UC22 |
| M03-F03 Nhận/chuyển việc | Queue, actor, version, capacity | Nếu scope/skill không đạt thì từ chối; nếu hai người claim thì một thành công; chuyển người không reset SLA | Assignment history, handoff; FR35/36 |
| M03-F04 Soạn và gửi | Thread, sender, recipient, body, response_targets, file hash | Nếu note thì tuyệt đối không outbound; reply phải qua quyền/capability/purpose và file clean; đổi recipient/file sau approval phải duyệt lại | Intent/outbox; FR32/34/40, M20 |
| M03-F05 Theo dõi kết quả | Provider receipt hoặc timeout | Accepted khác delivered/read; timeout sau request là unknown_outcome, không retry mù; receipt trùng không hoàn thành clock hai lần | Send attempts/status events; UC19 |
| M03-F06 Quản lý nghĩa vụ | Reply và response targets hợp lệ | Chỉ dừng clock đúng subject/episode đạt criterion; note/autoack không dừng; đóng thread không đóng mọi Ticket | SLA_Episodes; FR36/39, WF02 |
| M03-F07 Timeline/tìm kiếm | Query, actor, ACL hiện tại | Lọc object/field/count/snippet/file trước hiển thị; Contact chung không mở thread khác; merge chỉ trong workspace | Kết quả có quyền; FR08/31/37 |
| M03-F08 Phục hồi | Gap/backfill/reconnect | Historical event chỉ bổ sung lịch sử; không gửi lại tin, tạo acquisition lead hoặc reset clock live | Coverage/gap và task xử lý; FR38, M19 |

**Màn hình và trường:** Inbox ba vùng gồm queue, thread và hồ sơ/nghĩa vụ. Luôn hiện kênh/tài khoản gửi, assignee, waiting party, nguồn live/backfill, clock đến hạn và open subjects. Composer bắt buộc thread, public reply/private note, người nhận và nội dung hoặc file; có To/CC/BCC khi email hỗ trợ, preview reply-all và response targets. File pending/quarantine không có nút tải/forward; reveal PII theo nhiệm vụ, không hỏi lý do lặp lại cho công việc thường lệ.

**Commands và trạng thái:** `claim`, `assign`, `send`, `add-note`, `resolve`, `close`, `reopen`, `link-subject` kiểm expected_version và command key. Conversation open→resolved→closed; inbound hợp lệ có thể reopen theo policy; waiting_party và assignment độc lập. Intent giữ queued/attempting/accepted/failed/blocked/unknown_outcome theo hợp đồng provider. Không cho PATCH tùy ý status.

**Quyền và ngoại lệ:** Agent chỉ thread được giao/chia sẻ còn hiệu lực; supervisor override trong scope có lý do. Steward duyệt merge, Operator replay, quyền này không thay quyền gửi. Hết cửa sổ hoặc revoke thì blocked; token lỗi báo degraded; không có người trực thì queue có owner nhóm. Native reply không quan sát được phải hiện gap. File bảo vệ dùng gateway kiểm quyền ở request mới sau revoke; URL không thay session.

**Nghiệm thu:** M03-AC01 — replay inbound mười lần và hai agent claim: một message, một assignment hiện hành; FR33/35, UC17/20, Inbound_Events/Messages/Conversation_Assignments, OC01/OC02. M03-AC02 — cùng thread có báo giá và complaint, reply chỉ báo giá không dừng complaint; FR36/39, UC19, Message_Subject_Links/SLA_Episodes, WF-U02. M03-AC03 — workspace khác, link file cũ sau revoke và BCC/note thử xuất ra ngoài đều bị chặn; FR08/37/40, UC12/14, Message_Attachments/Entity_Team_Grants, U16/U17/SEC-U03. M03-AC04 — timeout rồi receipt/backfill đến muộn không gửi lặp hoặc mở clock mới; FR34/38, UC21, Outbound_Intents/Send_Attempts, OC và INT áp dụng.
''')

add('M06', 'AI Co-Pilot có kiểm soát', '#### 3.5.1 FR11 Tóm tắt cuộc gọi tiếng Việt', r'''
##### M06. Đặc tả BA — AI Co-Pilot có kiểm soát

**Mục đích, tác nhân và phạm vi:** Sales/AM dùng AI để giảm ghi chép và tìm thông tin đã được phép; reviewer chịu trách nhiệm xác nhận trước ghi trường thương mại hoặc gửi khách. AI owner quản model/prompt/eval; Privacy owner kiểm luồng dữ liệu và vendor. P1 là tóm tắt, rule score và draft; P2 mới xét tự hành. Khi AI tắt, thao tác thủ công vẫn hoàn chỉnh, không có endpoint/tool ngầm hoạt động.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M06-F01 Chọn nguồn | Actor chọn recording/document và mục đích | Nếu không có quyền đọc hoặc không đủ cơ sở dùng thì reject; chỉ lấy phiên bản và phần nội dung cần thiết | Source refs/hash; FR11, M20 |
| M06-F02 Chuẩn bị dữ liệu | Source được phép, vendor/feature policy | Nếu classification/region/retention chưa đạt thì giữ tác vụ thủ công; redact/pseudonymize không tự thành ẩn danh | Payload tối thiểu, policy evidence; Chương6 |
| M06-F03 STT/tóm tắt | Recording, model/prompt version | Nếu câu mơ hồ/số tiền/ngày hẹn thì đánh dấu cần xác nhận; không ghi đè field gốc | Draft có timestamp/nguồn; FR11 |
| M06-F04 Chấm điểm theo rule | Fit/intent có evidence, rule version | Thiếu dữ liệu là Unknown và giảm coverage; không tự suy ngân sách; rule không dùng thuộc tính nhạy cảm không liên quan | Score/coverage/reasons; FR12 |
| M06-F05 Tìm kiếm RAG | Câu hỏi và ACL hiện tại | Chỉ lấy tài liệu đúng scope/version; không có nguồn thì nêu thiếu, không bịa case study/số liệu | Draft có citations; FR12/37 |
| M06-F06 Duyệt/ap dụng | Reviewer, draft version, target version | Nếu nội dung/recipient/attachment đổi sau duyệt thì approval cũ không dùng; version conflict phải xem lại | Activity/task hoặc approved intent; FR13, M03 |
| M06-F07 Giới hạn tool | Đề nghị hành động từ model | Export/xóa/đổi quyền không tự thực hiện; refund/giá/hợp đồng không tự approve; tài liệu khách không đổi system instruction | Tool denial/audit; FR13 |
| M06-F08 Giám sát/tắt | Quota, latency, lỗi hoặc phản hồi reviewer | Vượt quota/circuit mở thì dừng gọi model và cho đường thủ công; không retry vô hạn | Usage/eval/incident; AI owner |

**Màn hình và trường:** Khung trợ lý hiển thị source link/timestamp, model/prompt version, thời điểm, phần chưa chắc chắn và coverage. Khi tạo request bắt buộc task_type, purpose, source refs và target resource; actor/scope do server suy ra. Review hiện draft cạnh nguồn, giá trị cũ/mới và nút chấp nhận từng trường. Gửi khách phải có preview sender, recipient, body, attachment hash và reviewer. Confidence của model không được gắn nhãn xác suất đúng khi chưa hiệu chuẩn.

**Commands và trạng thái:** `request-draft`→Queued→Running→DraftReady hoặc Failed/Cancelled; `review-draft`→Accepted/Rejected; `apply-reviewed-draft` tạo effect có operation key và kiểm quyền/version hiện tại. Rejected giữ evidence theo retention, không âm thầm học lại từ PII. DraftReady không là cam kết với khách; Accepted không tự là email đã gửi. Request đang chạy có cancel/timeout; kết quả đến sau cancel không tự apply. Logical draft và evaluation metadata phải có mapping nền tảng trước bật, không bắt một bảng vật lý riêng.

**Quyền và ngoại lệ:** AI kế thừa quyền người yêu cầu ở retrieve/apply; service principal không đọc rộng để “giúp” user. Reviewer có quyền hành động đích, quyền cấu hình model không đồng nghĩa đọc call. Prompt injection, vendor outage, nguồn hết quyền và token hết hạn đều có mã lỗi, audit tối thiểu và đường xử lý thủ công. Budget theo tenant/ngày là policy Active có owner, không lấy số seed làm phê duyệt ngân sách.

**Nghiệm thu:** M06-AC01 — file khách yêu cầu export hoặc đọc tenant khác không mở tool/quyền; FR13/37, UC03/14, Entity_Team_Grants/Audit_Logs, U22/INT27/INT28. M06-AC02 — câu phủ định, số tiền và lịch hẹn được so nguồn, trường quan trọng không apply trước reviewer; FR11, Activities/Assets và draft mapping, bộ eval call được phép tại3.5.1. M06-AC03 — đổi recipient hoặc revoke source sau tạo draft thì không dùng approval/ACL cũ; FR13/34, UC19, Approvals/Outbound_Intents, INT và SEC áp dụng. M06-AC04 — AI off, quota hết và vendor giữ log dù no-train: đường thủ công hoạt động, policy vendor chưa đạt thì không gửi dữ liệu; FR11–13, Processing_Records, RV17/WF-U04.
''')

add('M12', 'Voice of Customer và phục hồi trải nghiệm', '#### 3.7.2 FR19 CSAT và NPS', r'''
##### M12. Đặc tả BA — Voice of Customer và phục hồi trải nghiệm

**Mục đích, tác nhân và phạm vi:** CX/AM nhận phản hồi, thống nhất biện pháp khắc phục và xác minh kết quả; CMO xem xu hướng để sửa hành trình, Delivery sửa nguyên nhân, Finance duyệt tiền đúng thẩm quyền. P0 có intake/recovery thủ công; P1 thêm khảo sát có kiểm soát. Module không dùng điểm để ép khách sửa đánh giá hoặc tự quy lỗi nhân viên.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M12-F01 Thu feedback | Milestone/ticket/comment hoặc phản hồi trực tiếp | Nếu xác định được case thì link nguồn; chưa rõ người vẫn intake/provisional; score trống không đổi thành0 | Feedback có provenance; FR19, M03 |
| M12-F02 Chọn mẫu khảo sát | Touchpoint hoàn tất, eligible cohort | Nếu survey/reopen trùng hoặc cooldown chưa hết thì defer/cancel; không loại khách khó chỉ để đẹp điểm | Candidate/invitation có effect key; FR09/19 |
| M12-F03 Gửi khảo sát | Candidate, recipient, question version | Dispatch kiểm purpose/channel/suppression và incident arbitration; không đủ điều kiện thì blocked có reason | Sent/delivered/failed; M03/M20 |
| M12-F04 Tính chỉ số | Responses hợp lệ, metric version | CSAT dùng4–5 trên tổng trả lời1–5; NPS dùng9–10 trừ0–6 theo tập áp dụng; không cộng hai thang hoặc gán im lặng là điểm thấp | Metric/sample/coverage; FR28 |
| M12-F05 Triage recovery | Feedback thấp/complaint hoặc phát hiện chủ động | Ngưỡng/loại kích hoạt theo policy đã duyệt; trùng incident thì liên kết, không nhân remedy; severity khác ưu tiên phát triển | Recovery owner/due; FR18/19 |
| M12-F06 Thỏa thuận biện pháp | Evidence, entitlement, phương án | Nếu refund/đền bù vượt quyền thì chuyển approval; từ chối callback phải đổi cách liên hệ hợp lệ hoặc ghi no-contact | Remedy/promise có authority; M07 tài chính, FR18 |
| M12-F07 Xác minh đóng | Evidence đã làm và phản hồi khách | RemedyDone chưa là Verified; không liên hệ được là outcome riêng, không giả khách hài lòng | Closure/reopen history; Ticket/recovery |
| M12-F08 Sửa nguyên nhân | Root cause, phạm vi tái diễn | Corrective action có owner/due và evidence kiểm lại; không chuyển dữ liệu kháchA sang kháchB trái scope | Learning/checklist cập nhật; FR24/25 |

**Màn hình và trường:** Hàng đợi VoC lọc touchpoint, owner, severity, overdue và trạng thái liên hệ. Feedback bắt buộc source/time, question/scale version khi có score, workspace và subject/context; lưu Contact/Account/role nếu đã xác định. Case recovery bắt buộc reason, owner, review/due, linked feedback/ticket, planned remedy và authority khi liên quan tiền. Review hiển thị điểm gốc bất biến, evidence, lời hứa tiếp theo, no-contact/refused outcome và lịch sử reopen. Dashboard tách eligible/sent/delivered/responded và công bố mẫu/scope/kỳ; B2B giữ vai trò để không ngầm nhân trọng số account nhiều người trả lời.

**Commands và trạng thái:** `record-feedback`, `schedule-survey`, `triage`, `accept-owner`, `record-contact`, `agree-remedy`, `complete-remedy`, `verify`, `close`, `reopen`. Recovery detected→triaged→owner accepted→contacted→remedy agreed→remedy done→verified→closed; rẽ nhánh no-contact/refused giữ reason và người quyết định bước tiếp. Không nhảy thẳng Closed vì đã gọi ba lần; thay due/promise cần history. Request tiền tạo approval riêng, không sửa ledger từ màn hình CX.

**Quyền và ngoại lệ:** AM/CX xử lý account/project được giao; Delivery thấy phần cần sửa, không mặc nhiên đọc mọi phản hồi nhạy cảm; CMO chủ yếu aggregate. Nguồn ẩn danh giữ phạm vi cho phép, không đoán người từ nội dung. Khách rút quyền marketing không tự xóa nghĩa vụ xử lý khiếu nại hợp lệ; từng liên hệ xét mục đích riêng. Nhiều Ticket cùng incident không tự phạt health nhiều lần; thiếu response không release quality bonus mù.

**Nghiệm thu:** M12-AC01 — close/reopen/replay cùng touchpoint không spam, không xóa điểm cũ; FR19, UC09, Feedback/Journey_Instances, CX-U và INT áp dụng. M12-AC02 — khách từ chối gọi và remedy cần refund vượt quyền: không gọi tiếp hoặc hứa tiền sai, vẫn có owner/next action; FR18/19, Recovery_Cases/Customer_Promises/Approvals, CX-U15. M12-AC03 — không phản hồi survey hiển thị coverage, không thành0 hay Verified; FR19/28, Feedback/Recovery_Cases, CX-U và RV14 áp dụng. M12-AC04 — closure có evidence, reopen giữ lineage; corrective action nối checklist nhưng không leak khách khác; UC09/16, Corrective_Actions/Learning_Items, INT/CX áp dụng.
''')

add('M14', 'Tổ chức, nhóm và quyền vận hành', '#### 3.8.2 FR21 Phân quyền hai chi nhánh', r'''
##### M14. Đặc tả BA — Tổ chức, nhóm và quyền vận hành

**Mục đích, tác nhân và phạm vi:** Ops/quản lý giao việc và bàn giao giữa Sales, AM, Delivery, Finance mà giữ đúng tenant/workspace/pháp nhân; người có thẩm quyền cấp quyền kiểm soát role/grants. P0 có user, membership, delegation và scope; chi nhánh thứ hai chỉ mở khi vận hành thực. Scorecard nhân sự ở FR27 là P2, không kéo payroll/hồ sơ sức khỏe vào CRM.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M14-F01 Thiết lập tổ chức | Tenant, branch/legal entity/workspace thật | Nếu chỉ một pháp nhân/chi nhánh thì dùng mặc định; không dùng branch thay legal entity hoặc workspace | Org catalog và policy; FR21 |
| M14-F02 Gán membership | User/team/branch, role, effective dates | Chỉ grantor có authority được cấp; role cấu hình không cho tự nâng business access; expiry phải có hiệu lực thực | Membership/version/audit; SEC06 |
| M14-F03 Chia sẻ hồ sơ | Resource typed, actions/fields, principal, thời hạn | Nếu ngoài tenant/scope hoặc vượt quyền cấp thì reject; Account grant không mở toàn CLIENT/tài chính | Entity_Team_Grants; FR08/21/37 |
| M14-F04 Kiểm quyền | API/search/job/file/AI action | RBAC và ABAC cùng đạt, deny thắng allow; thiếu context thì fail closed; job kiểm lại khi chạy | Allow/deny có reason nội bộ; Chương6 |
| M14-F05 Ủy nhiệm/thay ca | Khoảng vắng, backup và open work | Backup cần quyền đúng nhiệm vụ; không tự đổi Deal owner, pháp nhân hay commission lịch sử | Delegation/handoff; FR05/35 |
| M14-F06 Chuyển/nghỉ việc | Quyết định đã xác nhận, effective time | Revoke session/grants trước chuyển open work; không người nhận thì queue quản lý; giữ actor cũ | Checklist/bàn giao; UC12 |
| M14-F07 Capacity/cost | Availability và cost rate có hiệu lực | Chỉ dùng phục vụ staffing/margin khi có quyền; thiếu rate là Unknown, không suy thành0; không lộ lương | Capacity/cost snapshot; FR25/27 |
| M14-F08 Scorecard | Metric/role/sample/context được duyệt | Chỉ khi P2 bật và dữ liệu đủ; thiếu dữ liệu không xếp hạng, không tự phạt theo số thao tác | Coaching/review; FR27/28 |

**Màn hình và trường:** Danh sách tổ chức hiển thị tenant, workspace type, branch, pháp nhân và active dates riêng. Cấp quyền bắt buộc principal, resource/scope, role/actions/fields, from/until theo policy, grantor/authority và reason; quyền nhạy cảm cho chính mình cần approval tách người khi có đội ngũ. Preview quyền hiệu lực giải thích nguồn Allow/Deny cho người có quyền quản trị, không lộ dữ liệu nghiệp vụ. Màn hình bàn giao gom lead, deal, thread, ticket, promise, appointment, scheduled intent và approval đang chờ; người nhận phải xác nhận phần thuộc trách nhiệm.

**Commands và trạng thái:** `invite`, `activate-user`, `grant`, `revoke`, `delegate`, `expire-grant`, `transfer-work`, `offboard` kiểm version/authority và audit. User Invited→Active→Suspended/Offboarded; reactivation là command có review, không hồi sinh mọi grant cũ. Grant Draft nếu cần duyệt→Active→Expired/Revoked; không gia hạn âm thầm để né deny. Team membership không là đường vòng cấp quyền. Một owner pilot được kiêm vai theo chế độ khai báo, không ghi giả đã có separation of duties.

**Quyền và ngoại lệ:** Admin kỹ thuật quản connector/config được cấp nhưng không tự gán Finance/Privacy. CEO đọc báo cáo theo nhu cầu, không sửa tiền gốc. Finance nhận các command tài chính và chứng cứ tối thiểu; AM có commercial permission mới tạo/sửa renewal Quote. B2C chia sẻ Contact/Deal trực tiếp, không tạo Account giả. Chuyển branch không chuyển công nợ hoặc cash; thay pháp nhân cần nghiệp vụ hợp lệ riêng. Revoke phải lan tới permission version/cache và download request mới.

**Nghiệm thu:** M14-AC01 — hai role xung đột và shared Account không mở thread/commission ngoài quyền; FR21/37, Entity_Team_Grants/Accounts, INT29/U17. M14-AC02 — Admin tự thêm Finance, manager cấp ngoài branch hoặc kéo dài break-glass bị chặn; FR21, Users/Teams/grant mapping/Audit_Logs, SEC-U06. M14-AC03 — nghỉ việc khi có intent/promise/open ticket: token cũ bị từ chối, việc có người/queue nhận và lịch sử actor giữ nguyên; FR08/21/35, UC12/20, U16/INT23. M14-AC04 — capacity thiếu cost và scorecard thiếu mẫu không tạo0/xếp hạng hoặc phạt tự động; FR25/27/28, effective rate/metric mapping, CEO/CMO/CX tests áp dụng.
''')

add('M19', 'Tích hợp và quản trị adapter', '### 2.5 Hợp đồng kỹ thuật tích hợp', r'''
##### M19. Đặc tả BA — Tích hợp và quản trị adapter

**Mục đích, tác nhân và phạm vi:** Integration owner nối tài khoản doanh nghiệp, vận hành webhook/sync và xử lý gap; Operator thao tác health/replay trong quyền hỗ trợ, không mặc nhiên đọc body hoặc gửi khách. M19 cung cấp capability và event bền vững cho module nghiệp vụ, không thay nguồn sự thật ngân hàng/ERP/provider. Pilot ưu tiên một kênh; connector chưa được cấp quyền vẫn có quy trình thủ công với provenance.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M19-F01 Đăng ký connector | Provider/app/account dự kiến, workspace owner | Nếu account nguồn đã có owner active trong namespace thì conflict; nhiều inbox dùng chung connection, không tự clone sang khách khác | Connection pending; FR30, SEC02 |
| M19-F02 Cấp/reconnect quyền | Authorization attempt, callback, actor/session | Callback phải khớp binding và dùng một lần; server xác minh external account/scopes; sai thì không thay token cũ | Secret ref/verified scopes; SEC01 |
| M19-F03 Khai báo capability | Account/API version và evidence test | receive/send/history/receipt/edit/delete tách verified/unsupported/pending/unknown; chưa verified không hứa chức năng | UI/feature gate; FR30/38 |
| M19-F04 Ingest | Chữ ký, subscription/account, event key/payload | Scope từ mapping server; lưu bền vững trước ACK; schema lạ quarantine; trùng không lặp effect | Inbound_Events→worker; FR33 |
| M19-F05 Dispatch | Intent đã commit, quyền/policy hiện tại | Recheck trước gửi; không giữ DB lock khi gọi mạng; timeout bất định không retry mù POST có tác động | Attempts/receipt; FR34, M03/M20 |
| M19-F06 Đồng bộ/phục hồi | Checkpoint, delta/page, gap | Advance cursor sau xử lý bền vững cả page; historical không phát sinh automation mới; không có history thì báo khoảng thiếu | Sync_Checkpoints/run; UC21 |
| M19-F07 Health/retry | 401/403/429/timeout/backlog | Tôn trọng Retry-After/backoff/TTL; lỗi quyền dừng/reconnect, schema vào DLQ; cảnh báo có owner | Degraded/runbook/queue; FR38 |
| M19-F08 Replay/rotate | Range, dry-run, reason hoặc secret rotation | Replay qua cùng dedup/scope; không bypass consent; refresh có lock; external media fetch qua egress policy | Audit/reconcile; SEC04, UC21 |

**Màn hình và trường:** Connection detail bắt buộc provider, namespace/app khi áp dụng, external account xác minh, workspace owner, connection owner/backup và API version. Token chỉ hiển thị trạng thái/expiry, không plaintext. Capabilities có checked_at/evidence; sync hiện last success, cursor metadata, coverage_from/to, gap reason và pending age. DLQ hiển thị error code đã redact, operation range và dry-run effect; mở payload cần support grant TTL riêng. Replay bắt buộc reason, scope, range và reviewer theo rủi ro, không có nút “replay mọi thứ” không giới hạn.

**Commands và trạng thái:** `authorize`, `verify-capability`, `activate`, `refresh`, `pause-send`, `disconnect`, `reconcile`, `replay-range`. Connection pending_authorization→active→degraded→reauthorization_required→disconnected theo sự kiện; state active chỉ sau account/scopes/capability đạt điều kiện. Reconnect không chuyển owner workspace. Muốn chuyển account phải pause ingest/send, đánh giá pending intent, cursor và revoke grant cũ; lịch sử giữ scope gốc. Refresh token không được hai worker ghi đè nhau.

**Quyền và ngoại lệ:** Admin connector không tự đọc nội dung/ghi sổ; Finance mới xác nhận match thu tiền, steward mới duyệt merge. Credential dùng scope tối thiểu và vault, worker role tách migration. Sai chữ ký reject; DB không lưu được không ACK thành công; provider outage giữ backlog có TTL. API không hỗ trợ tra cứu thì unknown_outcome có xử lý thủ công/evidence, không báo đã gửi. Fetch file kiểm host/IP/redirect/token, giới hạn byte/time và quét nội dung trước publish.

**Nghiệm thu:** M19-AC01 — callback sai phiên/replay và activate cùng account vào hai workspace không đổi mapping/token hợp lệ; FR30, UC17/21, Channel_Connections, SEC-U01/02. M19-AC02 — restart sau durable write, duplicate và out-of-order không mất/nhân effect; FR33/38, Inbound_Events/Outbox/Sync_Checkpoints, U01/OC/INT áp dụng. M19-AC03 — revoke sau enqueue và timeout sau request không gửi lại mù; FR34, UC19, Outbound_Intents/Send_Attempts, U15/INT26. M19-AC04 — media URL private/metadata/redirect bị chặn; gap không phục hồi được hiển thị thật; FR38/40, Message_Attachments/Sync_Checkpoints, SEC-U04/OC15.
''')

add('M20', 'Quản trị dữ liệu cá nhân và quyền chủ thể', '### 6.3 Khung pháp lý Việt Nam tại thời điểm nghiên cứu', r'''
##### M20. Đặc tả BA — Quản trị dữ liệu cá nhân và quyền chủ thể

**Mục đích, tác nhân và phạm vi:** Privacy owner quản mục đích, cơ sở xử lý, yêu cầu chủ thể, retention và nhà cung cấp; Ops/Integration thực thi, Finance/pháp lý xác nhận phần phải lưu. Phân biệt agency xử lý khách bán dịch vụ và dữ liệu người tiêu dùng theo chỉ dẫn khách. P0 có controls và hồ sơ tối thiểu; có thể dùng registry/quy trình ngoài CRM được mapping, không hoãn trách nhiệm vì chưa xây privacy engine.

| Chức năng | Trigger / đầu vào | Quy tắc If–Else | Đầu ra / phụ thuộc |
| --- | --- | --- | --- |
| M20-F01 Phê duyệt xử lý | Connector/feature mới, data classes, purpose | Chưa có owner/cơ sở/vai trò/phạm vi thì giữ Draft, không activate; consent không thay hợp đồng xử lý theo chỉ dẫn | Processing_Records/policy; UC14 |
| M20-F02 Grant/revoke consent | Endpoint/purpose/channel, evidence/version | Grant phải có bằng chứng phù hợp; revoke hợp lệ commit suppression trước xác nhận; không OR consent sau merge | Consent_Logs/Consent_State; FR02/09 |
| M20-F03 Chặn gửi | Intent và suppression hiện tại | Dispatch recheck authoritative; unsubscribe/bounce/complaint giữ semantics riêng; import không hồi sinh quyền | Allowed/blocked có reason; FR34, SEC05 |
| M20-F04 Nhận yêu cầu | Request type, received_at, phạm vi và xác minh vừa đủ | Không tiết lộ hồ sơ trước xác minh; valid_request_received_at không bị reset tùy tiện; case thiếu thông tin vẫn có owner/history | Privacy_Requests; UC11 |
| M20-F05 Tính hạn/xử lý | Loại quyền, vai trò, legal policy Active | Chỉ dùng rule có nguồn chính xác, nhánh áp dụng, đơn vị/calendar/trigger và owner đã duyệt; response/action/extension tách riêng | Due/history/tasks; Chương6.3 |
| M20-F06 Retention/xóa | Đến hạn hoặc request được duyệt | Có legal hold thì hạn chế đúng phần/cơ sở; không hold thì xóa/ẩn danh theo scope; backup theo vòng đời và ledger khi restore | Deletion evidence; UC11/NFR06 |
| M20-F07 Vendor/AI/xuyên biên giới | Dữ liệu ra cloud/AI/support | Chưa đủ điều kiện vendor/feature/region/retention thì không chuyển; no-train không tự thành zero retention | Vendor/flow review; M06/M19 |
| M20-F08 Sự cố | Phát hiện/awareness, loại dữ liệu/ảnh hưởng | Cô lập, bảo toàn evidence và đánh giá nghĩa vụ ngay; Confirmed không tự reset mốc pháp lý | Incident/notification tasks; Ops/privacy |

**Màn hình và trường:** Registry xử lý bắt buộc purpose, role controller/processor theo tình huống, scope/data classes, nguồn, cơ sở, recipient/vendor, nơi xử lý, owner và effective version. Yêu cầu chủ thể cần request_type, received_at, identity assurance/evidence tối thiểu, valid_request_received_at khi đủ thủ tục, owner, response/action due và kết quả từng phạm vi. Policy pháp lý lưu exact source/điều khoản, nhánh vai trò/ngoại lệ, trigger, ngày làm việc hay lịch, timezone, extension/notice rule và người duyệt; chưa chốt thì Draft và có gate xử lý phù hợp, không tự seed một hạn chung. Retention/hold có object scope, lý do/cơ sở, review date và authority, không bool vô thời hạn thiếu owner.

**Commands và trạng thái:** `approve-processing`, `record-consent`, `revoke`, `receive-request`, `verify-scope`, `assign-obligations`, `extend-with-notice`, `execute-restriction/deletion`, `review-hold`, `close-request`. Request Received→Validating→InProgress→Completed hoặc PartiallyCompleted/Refused với lý do; thiếu thông tin có task, không âm thầm đổi deadline. Policy Draft→Reviewed→Active; thay policy có version/effective date. Xóa kỹ thuật có từng target/task/result, chưa đủ evidence không ghi Completed toàn bộ.

**Quyền và ngoại lệ:** Steward chỉ xem dữ liệu cần cho case, quyền xóa không từ CRUD thông thường; xuất phản hồi chủ thể cần xác minh recipient. Marketing không được sửa suppression; Operator không tự đổi legal basis. Chứng từ phải lưu được hạn chế truy cập, không dùng lại marketing. Restore áp deletion/suppression trước mở truy cập/outbound; dữ liệu đã gửi provider có reconciliation, không cam kết thu hồi tuyệt đối. Không yêu cầu login CRM để unsubscribe có token hợp lệ.

**Nghiệm thu:** M20-AC01 — revoke sau enqueue, merge/unmerge và import vẫn chặn đúng purpose/endpoint; FR02/09/34, UC11/18, Consent_Logs/Contact_Points/Outbound_Intents, U15/CX-U20/SEC-U05. M20-AC02 — hai loại quyền/nhánh pháp lý dùng đúng policy/clock, xác minh không reset hạn; UC11, Privacy_Requests/Policy_Versions, RV và legal fixtures được duyệt. M20-AC03 — legal hold một phần, xóa projection/file/vector và restore không hồi sinh dữ liệu cấm; FR37, UC11/21, Retention_Policies/Processing_Records, INT26/U21. M20-AC04 — vendor no-train còn log hoặc incident chưa Confirmed không vượt gate dữ liệu/clock; FR11/13/30, Processing_Records/Audit_Logs, RV17 và incident fixtures áp dụng.
''')

acceptance = {
 'M03': 'M03-AC01 — replay và claim đồng thời: một effect/assignment; FR33/35, UC17/20, Inbound_Events/Messages/Conversation_Assignments. M03-AC02 — reply báo giá không dừng complaint; FR36/39, UC19, Message_Subject_Links/SLA_Episodes, WF-U02. M03-AC03 — workspace khác, link cũ sau revoke, BCC/note và timeout/backfill đều giữ đúng quyền/trạng thái; FR08/34/37/38/40, UC12/14/21, Message_Attachments/Outbound_Intents, U16/U17/SEC-U03.',
 'M06': 'M06-AC01 — injection/file ngoài scope không mở tool; FR13/37, UC03/14, Entity_Team_Grants/Audit_Logs, U22. M06-AC02 — số tiền/ngày hẹn chưa duyệt không apply; đổi recipient bắt duyệt lại; FR11/13/34, UC19, Activities/Approvals/Outbound_Intents. M06-AC03 — AI off hoặc vendor policy chưa đạt không gửi dữ liệu; đường thủ công còn dùng được; FR11–13, Processing_Records, RV17/WF-U04.',
 'M12': 'M12-AC01 — close/reopen/replay không spam hoặc sửa điểm gốc; FR19, UC09, Feedback/Journey_Instances. M12-AC02 — refused callback không gọi tiếp; refund vượt quyền phải approval, recovery vẫn có owner; FR18/19, UC09/13, Recovery_Cases/Approvals, CX-U15. M12-AC03 — im lặng không thành0/Verified; closure có evidence và corrective action không leak; FR19/24/28, UC09/16, Feedback/Recovery_Cases/Corrective_Actions.',
 'M14': 'M14-AC01 — role conflict/shared Account giữ deny/scope; FR21/37, UC14, Entity_Team_Grants, INT29/U17. M14-AC02 — Admin tự cấp Finance hoặc manager cấp ngoài branch bị chặn; FR21, Users/Teams/Audit_Logs, SEC-U06. M14-AC03 — offboarding giữ actor, revoke token, open work có người/queue; thiếu dữ liệu không xếp hạng; FR08/21/27/35, UC12/20, Conversation_Assignments/Entity_Team_Grants, U16.',
 'M19': 'M19-AC01 — callback sai/replay và cùng account hai workspace bị chặn; FR30, UC17/21, Channel_Connections, SEC-U01/02. M19-AC02 — restart/replay/revoke/timeout không mất hoặc nhân effect, không retry mù; FR33/34/38, UC19/21, Inbound_Events/Outbox/Send_Attempts, U01/U15. M19-AC03 — private URL/redirect bị chặn, gap hiện thật; FR38/40, UC21, Message_Attachments/Sync_Checkpoints, SEC-U04.',
 'M20': 'M20-AC01 — revoke/merge/import vẫn chặn đúng endpoint/purpose; FR02/09/34, UC11/18, Consent_Logs/Outbound_Intents, U15/SEC-U05. M20-AC02 — loại quyền/vai trò dùng đúng legal policy đã duyệt; xác minh không reset hạn; UC11, Privacy_Requests/Policy_Versions. M20-AC03 — hold một phần, deletion/restore và vendor gate giữ đúng phạm vi; FR13/37, UC11/21, Processing_Records/Retention_Policies, INT26/RV17.'
}
for c in cards:
    c['markdown'] = c['markdown'].split('**Nghiệm thu:**')[0] + '**Nghiệm thu:** ' + acceptance[c['id']] + '\n\n'
    c['markdown'] = c['markdown'].replace('M07 tài chính, FR18', 'FR16/18')
    if c['id'] == 'M03':
        c['markdown'] = c['markdown'].replace('có thể reopen theo policy', 'reopen theo policy')
    if c['id'] == 'M20':
        c['markdown'] = c['markdown'].replace('dữ liệu người tiêu dùng theo chỉ dẫn khách', 'dữ liệu theo chỉ dẫn khách').replace('P0 có controls và hồ sơ tối thiểu;', 'P0 có controls;').replace('Không yêu cầu login CRM để unsubscribe có token hợp lệ.', '')
    for text in {
      'M03': ['File pending/quarantine không có nút tải/forward; '],
      'M06': ['Confidence của model không được gắn nhãn xác suất đúng khi chưa hiệu chuẩn. ', 'Logical draft và evaluation metadata phải có mapping nền tảng trước bật, không bắt một bảng vật lý riêng. ', 'Budget theo tenant/ngày là policy Active có owner, không lấy số seed làm phê duyệt ngân sách. '],
      'M12': ['Nhiều Ticket cùng incident không tự phạt health nhiều lần; thiếu response không release quality bonus mù.', 'Nguồn ẩn danh giữ phạm vi cho phép, không đoán người từ nội dung. '],
      'M14': ['Một owner pilot được kiêm vai theo chế độ khai báo, không ghi giả đã có separation of duties.', 'Chuyển branch không chuyển công nợ hoặc cash; thay pháp nhân cần nghiệp vụ hợp lệ riêng. '],
      'M20': ['Restore áp deletion/suppression trước mở truy cập/outbound; dữ liệu đã gửi provider có reconciliation, không cam kết thu hồi tuyệt đối. ', 'Không yêu cầu login CRM để unsubscribe có token hợp lệ.', 'Xóa kỹ thuật có từng target/task/result, chưa đủ evidence không ghi Completed toàn bộ.']
    }.get(c['id'], []):
        c['markdown'] = c['markdown'].replace(text.rstrip(), '')

out = Path(r'D:/AI Agent/CRM/working/ba_modules_security.json')
out.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8')
master = Path(r'D:/AI Agent/CRM/CRM_MASTER_BRD_SRS_HOP_NHAT.md').read_text(encoding='utf-8-sig')
for c in cards:
    assert master.count(c['insert_before']) == 1, c['insert_before']
    assert c['markdown'].startswith('##### '+c['id']+'.')
    print(c['id'], len(c['markdown'].split()), 'words', c['markdown'].count('| '+c['id']+'-F'), 'function rows')
print(out)
