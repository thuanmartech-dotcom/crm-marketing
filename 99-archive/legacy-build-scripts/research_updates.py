"""Research integration, kept separate so the master can be regenerated."""
import re

SECTIONS = {}
SECTIONS[2] = r'''
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
| Zalo OA | Sự kiện/tin nhắn OA được API cấp; UID trong phạm vi OA; metadata được phép | Qua OA API hoặc template phù hợp sản phẩm/chính sách hiện hành | OA, app và quyền hợp lệ; kiểm tra hạn mức, cửa sổ gửi, loại nội dung, lịch sử, sự kiện thu hồi. Zalo cá nhân không được coi là OA API [R10] |
| Facebook | Page Messenger; Lead Ads là feed riêng nếu được cấp; comment là loại tương tác riêng | Page Messenger qua quyền và điều kiện gửi tương ứng | Quyền Page/app review, token, webhook; định danh có phạm vi Page. Lead Ads không tự tạo quyền nhắn Messenger; ngoài cửa sổ phải có cơ chế hợp lệ [R11] |
| TikTok | DM qua Business Messaging API cho Business Account được ủy quyền; Lead Gen và Shop qua connector khác | Chỉ khi account/app thực sự được cấp quyền messaging | API chính thức có tồn tại; chưa xác nhận tài khoản này đủ điều kiện tại Việt Nam. Không lấy API Shop thay cho DM, không suy luận Ads account có quyền inbox [R12] |
| Web Form | Submission, trường khách tự khai, consent version, UTM/referrer được phép | Form không phải kênh chat hai chiều; tạo task hoặc trả lời bằng email/kênh đã xác minh | Chống spam, kiểm tra server, submission ID; email nhập tay chưa phải email đã xác minh; không tự thêm vào marketing audience |
| Email | Mailbox doanh nghiệp được cấp quyền; thư, thread, attachment theo phạm vi cấu hình | Gmail API/Graph hoặc SMTP OAuth được phê duyệt | Watch/subscription phải gia hạn; webhook có thể chỉ chứa thông báo thay đổi, cần fetch nội dung; shared mailbox cần quyền thích hợp [R13][R14] |

Zalo cá nhân: quy trình chuyển sang OA bằng liên kết/QR, ghi nhận hoạt động thủ công có nguồn và consent; nếu đánh giá nhà cung cấp bridge phải kiểm chứng quyền chính thức và điều khoản, không dùng cookie/session cá nhân như nền móng hệ thống. Với TikTok chưa được duyệt, nhân viên xử lý trong giao diện chính thức, CRM ghi task và đường dẫn tham chiếu; hiển thị “chưa kết nối hai chiều”. Không dùng fallback để giả lập trạng thái đã gửi.

#### Hợp đồng adapter và vòng đời kết nối

Mỗi adapter công bố `capabilities`: receive, send, attachments, delivery_receipt, read_receipt, history_backfill, edit, delete, native_reply_echo. Trạng thái từng capability là `verified`, `unsupported`, `pending_approval` hoặc `unknown`, kèm ngày test, phiên bản API và tài khoản thử. UI dựa trên capability thực tế; không hiện nút reply cho connector chỉ nhận lead.

Lifecycle: `pending_authorization → active → degraded → reauthorization_required → disconnected`. Khi token hết hạn, dừng gửi và cảnh báo người phụ trách; giữ hàng đợi có TTL. Sau cấp quyền lại, kiểm tra lại policy tại thời điểm gửi; không xả hàng loạt tin marketing đã hết hiệu lực. Thu hồi tài khoản không tự xóa dữ liệu cần lưu hợp pháp, nhưng chặn truy cập mới ngay.

Inbound: xác minh theo cơ chế nhà cung cấp, giới hạn kích thước, ghi event bền vững rồi mới ACK trong timeout của kênh. Nếu ghi thất bại, trả lỗi để retry; không ACK trước lưu. Worker parse, chuẩn hóa, deduplicate, resolve identity, cập nhật conversation và tạo routing event trong transaction. Event chứa `tenant_id`, `workspace_id`, `connection_id`, `provider_event_id`, `provider_message_id`, `occurred_at`, `received_at`, `schema_version`, `correlation_id`, `payload_ref`. Tenant/workspace lấy từ connection được xác thực, không tin giá trị do payload khách gửi.

Outbound: lưu ý định gửi và outbox trong cùng transaction; worker kiểm tra quyền, consent/purpose, loại tin, cửa sổ gửi và hạn mức. Mỗi ý định có `client_request_id` duy nhất. Provider nhận thành công mới ghi `provider_message_id`; trạng thái `accepted` không tương đương `delivered` hay `read`. Nếu timeout sau khi provider có thể đã nhận, chuyển `unknown_outcome`; tra cứu/đối soát nếu API hỗ trợ, không retry mù. Không tuyên bố exactly-once xuyên nền tảng; mục tiêu là at-least-once inbound với xử lý idempotent và kiểm soát gửi trùng outbound.

Retry có exponential backoff, jitter, tôn trọng Retry-After, giới hạn tổng thời gian; lỗi quyền/policy không retry như lỗi mạng. DLQ có mã lỗi đã làm sạch, owner, lần thử, nút replay có quyền và audit. Backfill dùng cursor/checkpoint, cùng pipeline chống trùng với realtime, không kích hoạt chiến dịch hoặc SLA mới cho dữ liệu lịch sử. Gmail cần watch renewal và history sync; Microsoft cần quản lý subscription lifecycle. Chi tiết thời hạn lấy từ tài liệu/version đang triển khai, không hardcode chung cho mọi kênh.

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

Manifest gói ngành gồm `pack_key`, `version`, `requires_core`, `dependencies`, `owned_entities`, `permissions`, `event_subscriptions`, `migration_ids`, `feature_flags`. Namespace ví dụ `marketing_services.sow`; không cho hai pack cùng sở hữu một field core. Cài pack cần kiểm tra dependency và migration trên bản sao dữ liệu; conflict phải chặn build, không âm thầm “pack nạp sau thắng”. Gỡ pack mặc định vô hiệu chức năng, không DROP dữ liệu. Đây là biện pháp bổ sung vì cơ chế override theo thứ tự của EspoCRM hữu dụng nhưng nếu lạm dụng có thể che thay đổi của pack khác [R02].

Pipeline phát hành: lint/typecheck → boundary checks → unit domain trọng yếu → migration/integration → connector contract tests → E2E quyền và gửi tin → dependency/license scan → staging → canary → production. Mỗi release ghi commit và schema version. Migration theo expand/migrate/contract; rollback ứng dụng không đồng nghĩa rollback dữ liệu. Chỉ tách service khi có bằng chứng bottleneck, nhu cầu cô lập hoặc ownership riêng, có ADR và số đo trước/sau.
'''

SECTIONS[3] = r'''
### 3.12 Đặc tả Unified Inbox và Customer 360 mở rộng

| Mã | Yêu cầu bắt buộc | Tiêu chí nghiệm thu |
| --- | --- | --- |
| FR30 | Kết nối năm nhóm kênh qua registry và capability matrix | Mỗi tài khoản hiển thị trạng thái, scope, owner, last sync, lịch sử có/thiếu; kênh chưa duyệt không ghi là đã tích hợp |
| FR31 | Hợp nhất danh tính có bằng chứng và phân vùng | Cùng tên/ảnh không tự merge; cùng provider ID ở hai Page/OA không tự coi cùng người; hỗ trợ reject, merge và undo có audit |
| FR32 | Inbox hợp nhất nhưng giữ thread và channel identity | Nhìn thấy nguồn và tài khoản gửi; đổi channel phải chọn conversation khác và kiểm tra quyền; private note không vào outbound |
| FR33 | Inbound chống trùng, xử lý lệch thứ tự và backfill | Gửi lại event không tạo message/lead/SLA lần hai; lịch sử không kích hoạt marketing; status cũ không ghi lùi status mới |
| FR34 | Outbound có policy gate, idempotency và trạng thái bất định | Double-click tạo một send intent; timeout chưa rõ không hiển thị delivered hoặc tự gửi lại |
| FR35 | Phân công theo skill, ca và capacity | Một assignee đang giữ lease; owner Contact/Deal có thể khác assignee Conversation; nghỉ việc bàn giao được |
| FR36 | SLA phản hồi người thật và escalation | Autoack không dừng first-human-response clock; ngoài giờ theo business calendar; chuyển nhóm không reset clock |
| FR37 | Tìm kiếm và hiển thị bảo vệ dữ liệu | Search, preview, attachment, export và AI retrieval đều áp dụng tenant/workspace/row/field policy |
| FR38 | Sync health, replay, đối soát và chất lượng dữ liệu | Operator thấy backlog, event lỗi, cursor, thời gian mất kết nối và coverage; replay có quyền, audit và không nhân đôi hiệu ứng |
| FR39 | Liên kết hội thoại với nghiệp vụ phù hợp | Một complaint tạo Ticket; inquiry mới có thể tạo Lead; không mỗi message tạo Lead/Deal; support không bị tính là lead acquisition |
| FR40 | Email và file an toàn | Không leak BCC, không render script/remote tracking mặc định; file quarantine trước mở; reply-all phải hiển thị người nhận |

#### Identity resolution: quy tắc quyết định

Khóa external identity là `(tenant, workspace, connection, provider_subject_id)`; email/phone chuẩn hóa là thuộc tính có nguồn, độ xác minh và thời hạn, không phải khóa toàn cầu. Không bỏ dấu chấm hoặc phần `+tag` của mọi email theo quy tắc riêng của Gmail; không gộp hotline dùng chung thành một cá nhân. Một người đại diện nhiều công ty được gắn nhiều `Contact_Account_Roles`, gồm buyer, approver, billing, end-user và hiệu lực; hướng quan hệ được khai báo rõ. Mô hình association có nhãn của HubSpot là bằng chứng thiết kế tham khảo [R07].

Tự liên kết chỉ khi đã có external identity hợp lệ trong đúng phạm vi hoặc có bằng chứng xác minh được phê duyệt. Email/phone trùng nhưng chưa xác minh tạo candidate review; tên, địa chỉ, ảnh, nội dung chat chỉ hỗ trợ tìm kiếm. Trường hợp liên kết qua form/OTP cần purpose phù hợp và audit. Cross-workspace không merge tự động, kể cả cùng email: dữ liệu khách agency A và B phải cách ly.

Merge có preview survivor, source fields, conversation refs, consent và ownership; dữ liệu xung đột lưu provenance. Không “OR consent” để biến sự đồng ý của một kênh thành đồng ý mọi kênh. Undo cần lịch sử các liên kết cũ và xử lý các thay đổi phát sinh sau merge; không chỉ đổi lại tên Contact. Customer timeline truy vấn nhiều thread nhưng vẫn tôn trọng ACL từng thread.

#### Trải nghiệm xử lý cuộc hội thoại

Màn hình ba vùng: hàng đợi và bộ lọc; cuộc hội thoại có nhãn kênh/tài khoản; hồ sơ Contact, vai trò công ty, Deal, Ticket và next action. Nhân viên được lọc “của tôi”, “chưa nhận”, “sắp quá SLA”, chi nhánh, dịch vụ; ô soạn luôn cho biết đang gửi từ OA/Page/mailbox nào. Bản nháp và ghi chú nội bộ có kiểu dữ liệu riêng, không phân biệt chỉ bằng màu. Một người mua có thể hỏi Facebook rồi gửi brief qua email: timeline liên kết sau xác minh, hai conversation vẫn độc lập.

State machine: `new → queued → assigned → open → pending_customer/pending_internal → resolved → reopened`. Chuyển pending cần reason, due_at, next owner; không cho đóng chỉ để né SLA. First-response SLA và resolution SLA là hai clock khác; policy quy định rõ trạng thái nào được pause. Tin mới sau resolved tạo reopen episode hoặc conversation mới theo rule có version, không sửa ngược KPI lịch sử.

Routing ưu tiên workspace/branch/skill rồi ca và capacity, sau đó sticky assignment nếu còn hợp lệ. Claim dùng compare-and-swap/row lock; hai người nhận cùng lúc chỉ một thành công. Chuyển ca cần handoff note, lịch sử assignee và task tiếp theo. Supervisor có override kèm lý do; không tự đổi người sở hữu Deal và hoa hồng chỉ vì người trực inbox trả lời.

AI chỉ đề xuất phân loại, tóm tắt và draft có liên kết message nguồn. Nội dung khách gửi là dữ liệu không đáng tin để ra lệnh cho tool; agent không được export, đổi tài khoản nhận tiền, hứa giá hay gửi chiến dịch chỉ vì trong tin nhắn có yêu cầu. Trước mỗi hành động cần kiểm tra quyền hiện tại và approval tương ứng. Retrieval giới hạn đúng tenant/workspace, không dùng chung bộ nhớ chứa nội dung nhiều khách hàng.
'''

SECTIONS[4] = r'''
### 4.17 UC17 Nhận tin năm kênh về cùng điểm làm việc

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân và tiền điều kiện | Khách, provider, adapter, worker; connection active và đã xác thực; form có cấu hình workspace server-side |
| Đầu vào | Webhook/message notification/submission với ID, thời điểm, nội dung hoặc tham chiếu nội dung |
| Luồng chính | Xác minh → lưu durable event → ACK → fetch nếu cần → normalize → dedup → identity lookup → lưu Message/Conversation → route → hiện Inbox; tạo Lead chỉ khi intent phù hợp |
| Đậu | Một tin chuẩn hóa xuất hiện đúng workspace, nguồn và người nhận; có audit/correlation ID; SLA bắt đầu theo thời gian quy định |
| Rớt và nhánh | Sai chữ ký: reject; schema lạ: quarantine; token lỗi: dừng fetch và cảnh báo; trùng: no-op; không rõ danh tính: tạo provisional contact, không merge đoán |
| Đầu ra và kiểm tra | Message, conversation, assignment, task nếu cần; replay 10 lần vẫn một hiệu ứng nghiệp vụ |

### 4.18 UC18 Liên kết Facebook, Zalo và Email của cùng khách

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales đề xuất, data steward duyệt; 3 identities trong cùng workspace và bằng chứng xác minh |
| Luồng chính | Tìm candidate → xem provenance → kiểm tra quyền → preview merge → duyệt → relink identities và refs trong transaction → lưu merge journal |
| Đậu | Timeline một Contact, ba conversation riêng; role công ty giữ nguyên; chỉ đọc phần có quyền |
| Rớt/nhánh | Tên trùng: không đủ; email chung: không merge người; khác workspace: chặn; conflict consent: giữ từng scope; phát hiện sai: undo qua journal |
| Đầu ra | Contact survivor, identity links, audit; không sửa provider ID hoặc tạo quyền gửi mới |

### 4.19 UC19 Trả lời từ CRM và xử lý gửi chưa rõ kết quả

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales có quyền gửi; conversation cụ thể, body, attachment sạch, client_request_id |
| Luồng chính | Chọn người nhận/kênh → policy gate → lưu send intent/outbox → worker gửi → nhận acknowledgment → cập nhật trạng thái theo event provider |
| Đậu | Provider chấp nhận và có external ID; UI chỉ hiện delivered/read khi có chứng cứ tương ứng |
| Rớt/nhánh | Hết cửa sổ/thiếu quyền: blocked; 429: backoff; timeout sau request: unknown_outcome, tra cứu nếu được; attachment lỗi: không gửi; echo: gắn vào tin đã gửi |
| Đầu ra | Message và send attempts; không nhân đôi khi double-click; thao tác gửi lại bất định phải cảnh báo rủi ro trùng và có audit |

### 4.20 UC20 Chuyển ca, quá SLA và bàn giao khách

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Router, Sales, trưởng nhóm; lịch ca, capacity, skill, SLA policy |
| Luồng chính | Queue → atomic claim → timer phản hồi người thật → cảnh báo → escalation/chuyển người có capacity → handoff note → trả lời |
| Đậu | Có người chịu trách nhiệm, không mất tin; lịch sử chuyển người đầy đủ, SLA không bị reset |
| Rớt/nhánh | Không ai trực: queue có owner nhóm/on-call; autoack: không tính hoàn thành SLA; agent nghỉ việc: revoke session và chuyển việc; không tự sửa commission owner |
| Đầu ra | Assignment history, SLA episode, human reply activity và lý do escalation |

### 4.21 UC21 Mất kết nối và phục hồi không gây spam

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Operator, connection owner; cursor cuối, lỗi OAuth/subscription hoặc DLQ |
| Luồng chính | Phát hiện degraded → cảnh báo → reauthorize/renew → đọc delta từ checkpoint hoặc backfill được phép → dedup → đối soát → xác nhận healthy |
| Đậu | Dữ liệu phục hồi có nhãn historical; không tái gửi tin hoặc tạo lead/commission; coverage và gap hiển thị |
| Rớt/nhánh | API không cho lịch sử: ghi khoảng thiếu, không báo “đầy đủ”; event độc: quarantine; backlog outbound hết hạn: cancel/blocked theo policy |
| Đầu ra | Sync run, counts và checkpoint; báo cáo khoảng dữ liệu không thể phục hồi |

### 4.22 UC22 Từ yêu cầu trong inbox đến dự án marketing

| Thuộc tính | Đặc tả |
| --- | --- |
| Tác nhân/đầu vào | Sales, strategist, account manager; form/DM/email yêu cầu dịch vụ |
| Luồng chính | Phân loại inquiry → qualify B2B/B2C → xác minh Contact/Account và vai trò duyệt → brief → Deal → SOW/báo giá → ký/đặt cọc → kickoff → deliverables → nghiệm thu → gia hạn |
| Đậu | Mọi bước có owner, next action và liên kết nguồn; revenue chỉ từ nghiệp vụ hợp lệ, không từ lượt chat |
| Rớt/nhánh | Khiếu nại khách cũ: Ticket; yêu cầu ngoài SOW: change request; không đủ fit: nurture có điều kiện hoặc lost reason; nhiều người cùng Account không bị gộp Contact |
| Đầu ra | Chuỗi trace message → lead/deal → contract/project/ticket, giúp tìm lại cam kết khi bàn giao |
'''

SECTIONS[5] = r'''
### 5.16 Schema Omnichannel bổ sung

Các bảng dưới bổ sung cho schema Chương 5. UUID là khóa nội bộ; external IDs luôn là text để không mất số 0 đầu hoặc vượt miền số. Mọi bảng có `id uuid PK`, `tenant_id uuid NOT NULL`, `workspace_id uuid NOT NULL`, `created_at timestamptz NOT NULL`. Bảng thay đổi trạng thái có `updated_at`, `row_version bigint`. FK gồm tenant/workspace với khóa đích tương ứng để chặn liên kết chéo phạm vi; không chỉ dựa bộ lọc UI. Tên bảng trong đặc tả được ánh xạ snake_case trong migration.

| Bảng | Trường nghiệp vụ và kiểu | Ràng buộc/ý nghĩa |
| --- | --- | --- |
| Channel_Connections | provider varchar(40); external_account_id text; secret_ref text; capabilities jsonb; scopes jsonb; status varchar(30); api_version text; expires_at timestamptz NULL; last_sync_at timestamptz NULL | Unique tenant/workspace/provider/external_account_id; secret_ref trỏ vault, không lưu token plaintext; capability có checked_at/evidence |
| Channel_Identities | connection_id uuid FK; provider_subject_id text; contact_id uuid FK NULL; verification_status varchar(30); evidence_ref uuid NULL; verified_at timestamptz NULL | Unique tenant/workspace/connection/provider_subject_id; NULL contact trong quarantine/provisional; không unique tên hoặc ảnh |
| Inboxes | name text; connection_id uuid FK; branch_id uuid FK NULL; team_id uuid FK; routing_policy_id uuid FK; status varchar(20) | Một connection có thể nhiều hàng đợi nội bộ; inbound resolver xác định một inbox đích, tránh fanout tạo trùng |
| Conversations | inbox_id uuid FK; channel_identity_id uuid FK; provider_thread_id text NULL; status varchar(30); assignee_id uuid FK NULL; team_id uuid FK; opened_at timestamptz; last_message_at timestamptz NULL; source_mode varchar(20) | Partial unique connection + provider_thread_id khi có thread bền vững; nếu provider không có, lưu session rule/version; source_mode live/backfill/manual |
| Conversation_Participants | conversation_id uuid FK; participant_key text; channel_identity_id uuid FK NULL; role varchar(20); visible_to_customer boolean | Unique conversation/participant_key/role; email To/CC/BCC và agent tách vai trò; không render BCC ra ngoài |
| Messages | conversation_id uuid FK; connection_id uuid FK; provider_message_id text NULL; client_request_id uuid NULL; direction varchar(12); visibility varchar(12); content_type varchar(40); body_ref text NULL; occurred_at timestamptz; received_at timestamptz; delivery_status varchar(25); deleted_at timestamptz NULL | Partial unique connection/provider_message_id; partial unique workspace/client_request_id; private note không có outbound; body mã hóa/ACL; không dùng text content làm dedup key |
| Message_Attachments | message_id uuid FK; object_key text; mime_type text; size_bytes bigint; sha256 char(64); scan_status varchar(20); expires_at timestamptz NULL | size >= 0; allowlist/size policy; signed URL ngắn hạn; chỉ clean mới được tải hoặc forward |
| Message_Status_Events | message_id uuid FK; provider_event_id text; status varchar(30); occurred_at timestamptz; received_at timestamptz; detail jsonb | Append-only; unique connection/event/type; reducer theo transition của provider, không ghi đè trạng thái bằng thứ tự nhận đơn thuần |
| Inbound_Events | connection_id uuid FK; event_key text; event_type text; payload_ref text; occurred_at timestamptz NULL; received_at timestamptz; processing_status varchar(20); attempts int; error_code text NULL | Unique connection/event_key; provider ID ưu tiên; fallback key có version và giữ raw reference; payload retention ngắn có cấu hình |
| Outbound_Intents | message_id uuid FK; idempotency_key uuid; policy_snapshot jsonb; status varchar(25); next_attempt_at timestamptz NULL; expires_at timestamptz; attempt_count int | Unique workspace/idempotency_key; policy_snapshot không thay thế recheck khi gửi; unknown_outcome cần reconcile |
| Send_Attempts | outbound_intent_id uuid FK; attempt_no int; request_ref text; provider_response_ref text NULL; started_at timestamptz; completed_at timestamptz NULL; outcome varchar(25) | Unique intent/attempt_no; log đã bỏ token/PII; không giả định network timeout là rejected |
| Conversation_Assignments | conversation_id uuid FK; assignee_id uuid FK NULL; team_id uuid FK; assigned_at timestamptz; released_at timestamptz NULL; reason text; actor_id uuid FK NULL | Partial unique conversation khi released_at NULL; giữ history chuyển ca; concurrency qua transaction |
| SLA_Episodes | conversation_id uuid FK; policy_version text; clock_type varchar(30); started_at timestamptz; due_at timestamptz; stopped_at timestamptz NULL; pause_intervals jsonb; outcome varchar(20) | first_human_response và resolution là episode khác; chuyển nhóm không tạo clock mới; calendar/timezone có version |
| Sync_Checkpoints | connection_id uuid FK; stream_key text; cursor_encrypted text NULL; coverage_from timestamptz NULL; coverage_to timestamptz NULL; last_success_at timestamptz NULL; gap_reason text NULL | Unique connection/stream_key; advance cursor sau xử lý bền vững toàn page; coverage không giả lập từ thời điểm cài app |
| Identity_Merge_Journal | survivor_id uuid FK; merged_contact_id uuid FK; evidence_ref uuid; before_refs jsonb; actor_id uuid FK; approved_at timestamptz; undone_at timestamptz NULL | Lưu quan hệ trước merge và operation ID; quyền riêng; không lưu vô hạn PII chỉ để hỗ trợ undo |

FK `Messages.connection_id` phải khớp connection của Inbox/Conversation; cưỡng chế bằng composite references hoặc invariant được kiểm thử trong transaction. Khóa unique cho message cần theo namespace thực của provider; nếu provider chỉ đảm bảo ID trong thread thì thêm provider_thread_id vào khóa. Một identity nhiều conversation; một conversation nhiều participant; một Contact nhiều identity. Account không đồng nghĩa Contact, Inbox không đồng nghĩa Channel Connection.

Index tối thiểu: `(tenant_id, workspace_id, assignee_id, status, last_message_at DESC)` trên Conversations; `(conversation_id, occurred_at, id)` trên Messages; pending intents theo next_attempt_at; inbound pending theo received_at. Search index dùng document ACL và xóa đồng bộ; PostgreSQL full-text là điểm xuất phát, chưa cần Elasticsearch khi chưa đo tải. Tệp và raw payload không nhét toàn bộ vào event JSON; chỉ lưu object reference có retention và access check.

### 5.17 Hợp đồng API nội bộ và giao dịch mẫu

| Endpoint đề xuất | Kiểm tra bắt buộc | Kết quả/lỗi |
| --- | --- | --- |
| POST /v1/conversations/{id}/messages | RBAC + workspace + recipient + capability + send policy; Idempotency-Key | 202 queued với intent_id; replay cùng key/body trả cùng intent; khác body trả 409 |
| POST /v1/conversations/{id}/claim | Team membership, capacity, expected row_version | 200 nhận thành công; 409 đã được người khác nhận |
| POST /v1/identity-merge-reviews | Cùng phạm vi, evidence, review permission | 201 review pending; không tự merge chỉ vì API được gọi |
| POST /v1/connections/{id}/replay | Operator role, event range, dry-run preview, reason | Job ID; từng event qua dedup, không bypass quyền/consent |
| GET /v1/contacts/{id}/timeline | Contact access và từng conversation/message access | Cursor pagination; không leak counts/snippet của thread bị cấm |

Ví dụ transaction inbound: insert event guard → upsert identity theo scoped key → insert message theo provider key → update conversation summary → insert domain outbox → mark processed → commit. Nếu unique conflict, đọc bản ghi hiện hữu và xử lý phần status mới nếu đó là event khác; không nuốt tất cả exception như “trùng”. Job retry sau crash phải cho kết quả nhất quán. Giao dịch gọi provider nằm ngoài DB transaction để không giữ lock trong khi chờ mạng.
'''

SECTIONS[6] = r'''
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
'''

SECTIONS[7] = r'''
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
'''

SECTIONS[8] = r'''
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
'''

SECTIONS[9] = r'''
### 9.8 Gate Omnichannel và kế hoạch lựa chọn nền tảng

Đợt triển khai cá nhân ưu tiên form + một mailbox + OA hoặc Facebook đã đủ quyền. Sau pilot mới mở toàn đội và kênh còn lại. Mục tiêu năm kênh không đồng nghĩa cả năm phải bật dù chưa được provider cấp quyền. Ngày 1–15 kiểm kê tài khoản, quyền, khoảng lịch sử, consent, demo inbound/outbound và 3 lựa chọn nền tảng. Ngày 16–30 xây/đấu nối foundation identity/event/inbox và pilot. Ngày 31–60 bổ sung kênh đủ quyền, routing, lead/deal và handoff. Ngày 61–75 fault tests, security, training. Ngày 76–90 cutover theo nhóm và hypercare. Mốc phụ thuộc app review phải ghi riêng trong critical path.

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
'''

SECTIONS[10] = r'''
### 10.6 TCO bổ sung cho hợp nhất năm kênh

Không coi connector là miễn phí sau lần cài đầu. Chi phí gồm phát triển adapter, app review, license inbox, message/template, email provider, object storage, log retention, vận hành token, API changes và hỗ trợ outage. Chi phí bán hàng/marketing hiện tại cần đo trước khi khẳng định tiết kiệm nhân sự.

Ví dụ lập kế hoạch **không phải báo giá thị trường**: 30 ngày công foundation + 5 connector × 10 ngày + 20 ngày UAT/hardening = 100 ngày công. Giả định 3 triệu VND/ngày → 300 triệu; dự phòng 25% → 375 triệu triển khai. Giả định vận hành tăng thêm 5 triệu/tháng + bảo trì 2 ngày/tháng × 3 triệu = 11 triệu/tháng; 36 tháng = 396 triệu. Tổng minh họa 771 triệu chưa gồm VAT, phí provider/license và AI. Hướng thuê engine/SaaS có thể giảm ngày xây nhưng tăng thuê bao và chi phí kết nối; phải thay số bằng báo giá/PoC. Nếu Chương 10.2 đã gồm một hạng mục, chỉ cộng phần chênh lệch, không cộng trùng 771 triệu.

Mô hình volume: 100 inquiry/tháng × 30 message/inquiry = 3.000 message, cộng 50 khách đang phục vụ × 80 message = 4.000, tổng 7.000/tháng là **kịch bản giả định**. Chạy nhạy cảm ×1, ×5, ×10; thêm file size, retention và số tài khoản kênh. “50 khách/tháng” chưa được xác nhận là khách mới, khách active hay đơn; không sử dụng con số đó để suy conversion 50%.

ROI tăng thêm = lợi nhuận gộp đóng góp từ hợp đồng thực sự tăng + giá trị thời gian tiết kiệm thực hiện được − chi phí Omni tăng thêm. Chỉ quy attribution khi có nhóm/thời kỳ so sánh đủ tương đồng; việc thấy thêm message trong CRM không tự chứng minh tăng doanh thu. Gate quyết định: nếu cá nhân chưa có lượng inbox lớn, triển khai foundation và 2–3 kênh ưu tiên trước, bảo toàn khả năng mở rộng năm kênh.
'''

APPENDIX = r'''
<a id="phu-luc-d"></a>

## PHỤ LỤC D NGHIÊN CỨU CRM THAM KHẢO VÀ QUYẾT ĐỊNH TÍCH HỢP

### D.1 Phương pháp, phạm vi và độ chắc chắn

Ngày đối chiếu: **15/10/2026**. “Tốt nhất” được hiểu theo độ phù hợp: mở rộng nhiều ngành, agency B2B/B2C, inbox năm kênh, khả năng nâng cấp, dữ liệu và tổng chi phí. Không có sản phẩm tốt nhất tuyệt đối. Chọn sáu dự án có code/tài liệu kiến trúc công khai (Twenty, EspoCRM, Frappe CRM, Odoo, SuiteCRM, Chatwoot) và ba nền tảng doanh nghiệp để học mô hình (Salesforce, HubSpot, Microsoft Dynamics/Dataverse). Chatwoot là engine hội thoại, không thay toàn bộ CRM/ERP.

Đã đối chiếu một số tệp code/manifest công khai và tài liệu chính thức; chưa clone/đọc toàn bộ code của chín sản phẩm, chưa chạy benchmark, chưa kiểm thử tích hợp với tài khoản của doanh nghiệp. Các URL `main`, `develop`, `master` là nhánh thay đổi, không phải snapshot bất biến; khi chọn triển khai phải pin commit/tag, lockfile, LICENSE và lưu bằng chứng PoC. Không lấy số sao GitHub, quảng cáo AI hoặc tính năng trên website làm bằng chứng hiệu năng/ROI. Mã nguồn tải qua shell thất bại do kết nối môi trường; các nhận định dưới dùng nội dung nguồn đọc qua công cụ web. Ba agent song song đã dừng vì giới hạn sử dụng, không có kết quả agent được đưa vào báo cáo.

Phân biệt: **quan sát** là nội dung nguồn chứng minh; **đề xuất** là suy luận thiết kế cho dự án; **rủi ro** là điều kiện có thể gây hại, không là cáo buộc sản phẩm có lỗi. Không đưa kết luận “framework X nhanh hơn Y” khi chưa đo.

### D.2 So sánh có bằng chứng và điều kiện áp dụng

| Dự án | Quan sát đã có nguồn | Điều nên áp dụng và vị trí tích hợp | Điều có thể hại nếu áp dụng sai / quyết định |
| --- | --- | --- | --- |
| Twenty | Server package có NestJS, TypeORM, BullMQ, OpenTelemetry; lệnh chạy API/worker riêng và package workspace [R01] | API/worker tách entrypoint, contracts dùng chung, tracing; áp dụng 2.8 và 7.6 | Sao chép toàn bộ dependency làm tăng gánh nâng cấp và vận hành ở 100 lead/tháng; học cấu trúc, không chép toàn stack. LICENSE cần đọc theo package, không mặc định permissive [R16] |
| EspoCRM | Extension backend/frontend có thư mục riêng, metadata/controller override theo order [R02] | Pack ngành có namespace, routes và dependency rõ; áp dụng 2.8, OC24 | Hai pack override cùng key có thể che nhau; thêm conflict detection. Không sửa core trực tiếp; workflow/sales add-on phải kiểm tra edition và báo giá, không mặc định miễn phí |
| Frappe CRM | Frontend manifest dùng Vue/Vite; framework DocType mô tả dữ liệu và hành vi [R03][R04] | Metadata có schema/validation và form tái sử dụng; xét PoC nếu chọn hệ sinh thái Frappe | Custom mọi thứ bằng script không kiểm thử gây lệch giữa môi trường; giữ quy tắc tiền/quyền trong logic được test, migration versioned. Không chọn Vue chỉ vì sản phẩm dùng Vue |
| Odoo CRM | Module crm có models/views/security/data/tests/wizard và manifest; có pipeline, activities và leads [R05] | Đóng gói ngành có model, UI, quyền và test đi cùng; hoạt động tiếp theo gắn opportunity | Lôi cả ERP vào giai đoạn cá nhân tăng phạm vi/đào tạo; chỉ xét mạnh khi thực sự cần vận hành ERP chung. Không tự cho rằng community có mọi tính năng enterprise |
| SuiteCRM 8 | Tài liệu extension tách app/backend/modules/config, Angular và Symfony extension [R06] | Extension có cấu trúc và dependency injection; UI cấu hình tái sử dụng | Microfrontend tạo thêm build/version/runtime seam; chưa cần cho đội nhỏ. Nếu chọn SuiteCRM, PoC nâng cấp extension bắt buộc thay vì giả định tương thích |
| Chatwoot | ContactInbox nối contact/inbox, unique inbox+source_id trong model; API Channel cho kênh tùy biến [R08][R09] | Tách người–danh tính kênh–conversation; dùng làm lựa chọn engine inbox trong PoC | Hai router/master cùng sửa assignee/status gây vòng lặp; adapter custom không tự tạo quyền Zalo/TikTok. Thêm Rails engine là thêm stack vận hành, không mặc định bắt buộc. Enterprise license tách [R17] |
| Salesforce | Hướng dẫn lựa chọn automation theo độ phức tạp và một entrypoint chính cho object [R18] | Rule registry, thứ tự, chống recursion, version hóa và test; phân biệt AI với nghiệp vụ deterministic | Nhiều trigger không owner gây side effect và khó audit; chuyển mọi rule sang agent AI làm kết quả không ổn định. Không suy ra code nội bộ Salesforce từ tài liệu công khai |
| HubSpot | Associations API hỗ trợ quan hệ có nhãn, hướng quan hệ và limits theo subscription [R07] | Contact–Account nhiều vai trò, decision maker/billing, provenance; áp dụng 3.12 và schema hiện hữu | Ép một Contact chỉ một công ty làm sai B2B; copy raw type ID sang hệ khác gây lỗi. Quyền/tier API phải kiểm chứng khi mua |
| Dynamics/Dataverse | Solution layer tách base managed và app extensions; quản lý source và deployment [R19][R20] | Core contract ổn định, pack version/dependency, dev/staging/prod và release artifact | Tùy biến trực tiếp production gây drift và phụ thuộc vòng; lớp extension không giải quyết permission sai. Chưa xác nhận license/tổng chi phí phù hợp giai đoạn cá nhân |

### D.3 Quy trình nghiệp vụ được tích hợp và lý do

1. **Account và vai trò người mua:** giữ riêng người duyệt ngân sách, người ký và người nghiệm thu; một người có thể nhiều vai trò. Bằng chứng mô hình associations [R07]; suy luận cho agency giúp tránh gửi báo giá cho sai người hoặc mất quan hệ khi người đại diện chuyển công ty. Đã tích hợp 3.12, UC18, UC22.
2. **Next action trên cơ hội:** mỗi Deal mở có owner, việc tiếp theo và hạn, theo cách CRM tổ chức pipeline/activities như Odoo [R05]. Với agency, quote không được treo vô hạn; lost reason và stage gate phải xác định. Không ép mọi chat thành Deal vì làm sai conversion.
3. **Quản trị automation:** registry event → điều kiện → hành động → owner → version → test; lấy nguyên tắc quản trị từ Salesforce [R18]. Mỗi intent gửi/commission được xử lý idempotent; import và replay có chế độ riêng. Chế độ bypass chỉ bỏ automation được chỉ định, không bypass tenant/ACL/audit.
4. **Tách identity theo kênh:** bằng chứng cụ thể từ ContactInbox của Chatwoot [R08]; dự án bổ sung tenant/workspace và kiểm chứng danh tính. Tên giống nhau là tín hiệu tìm kiếm yếu; gộp nhầm có thể lộ hợp đồng/chiến dịch của khách khác.
5. **Gói ngành và ALM:** học extension Espo/Suite và base solution Microsoft [R02][R06][R19]; dự án bổ sung namespace conflict checks và migration ownership. Custom qua core patch làm mỗi lần nâng cấp phải giải quyết xung đột và có nguy cơ mất bản vá.
6. **Phục hồi đồng bộ:** Gmail mô tả notifications có thể trễ/mất và cần sync dự phòng [R13]. Dự án áp dụng checkpoint/dedup/reconcile cho từng provider theo khả năng, không hứa webhook luôn giao đủ hoặc đủ lịch sử.

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
| R01 | [Twenty server package.json](https://raw.githubusercontent.com/twentyhq/twenty/main/packages/twenty-server/package.json) | Dependency và script API/worker/workspace; không chứng minh runtime performance |
| R02 | [EspoCRM Modules](https://docs.espocrm.com/development/modules/) | Thư mục extension và override order; cần kiểm thử xung đột của pack thực tế |
| R03 | [Frappe CRM frontend package](https://raw.githubusercontent.com/frappe/crm/develop/frontend/package.json) | Vue/Vite và scripts; không xác minh toàn backend bằng file này |
| R04 | [Frappe DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes) | Mô hình metadata; không phải cam kết mọi customization upgrade-safe |
| R05 | [Odoo CRM module 19.0](https://github.com/odoo/odoo/tree/19.0/addons/crm) | Cấu trúc module và nghiệp vụ CRM; nhánh tham khảo, không khẳng định latest |
| R06 | [SuiteCRM extension structure](https://docs.suitecrm.com/8.x/developer/extensions/extension-structure/) | Phân vùng frontend/backend/config và DI; không benchmark |
| R07 | [HubSpot Associations](https://developers.hubspot.com/docs/api-reference/latest/crm/associations/associate-records/guide) | Quan hệ có nhãn/hướng; URL v4 chuyển sang tài liệu mới khi đối chiếu, version triển khai cần pin riêng |
| R08 | [Chatwoot ContactInbox model](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/app/models/contact_inbox.rb) | Liên kết contact/inbox/source và unique index; đề xuất tenant/workspace là bổ sung của dự án |
| R09 | [Chatwoot API Channel](https://www.chatwoot.com/hc/user-guide/articles/1677839703-how-to-create-an-api-channel-inbox) | Kênh tích hợp tùy biến; không có nghĩa hỗ trợ native mọi kênh Việt Nam |
| R10 | [Zalo OA khởi tạo ứng dụng và cấp quyền](https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195) | Cơ chế ứng dụng/OA; chưa thử tài khoản doanh nghiệp, không chứng minh quyền Zalo cá nhân |
| R11 | [Meta Messenger API — official Postman workspace](https://www.postman.com/meta/messenger-platform-api/documentation/iyp204x/messenger-platform-api) | Page messaging và điều kiện cửa sổ gửi; chính sách/permission cần xác minh theo app tại triển khai |
| R12 | [TikTok Business Messaging Education Hub](https://business-api.tiktok.com/portal/bm-api/education-hub) | API DM cho authorized Business Accounts; trang động, nội dung được tìm thấy qua chỉ mục tìm kiếm chính thức, chưa xác minh eligibility tài khoản Việt Nam |
| R13 | [Gmail push notifications](https://developers.google.com/workspace/gmail/api/guides/push) | Watch, history notification, renewal và khả năng mất/trễ; không phải body email trong mọi webhook |
| R14 | [Graph Outlook change notifications](https://learn.microsoft.com/en-us/graph/outlook-change-notifications-overview?tabs=http) | Subscription và phạm vi quyền mailbox; không tự đồng bộ shared mailbox bằng mọi delegated scope |
| R15 | [SuiteCRM frontend architecture](https://docs.suitecrm.com/8.x/developer/architecture/front-end-architecture/) | UI tái sử dụng và cấu hình; không suy ra mọi UI nghiệp vụ đều nên metadata hóa |
| R16 | [Twenty LICENSE](https://github.com/twentyhq/twenty/blob/main/LICENSE) | Phải kiểm tra điều khoản theo thành phần; không đưa kết luận pháp lý chỉ từ tên repo |
| R17 | [Chatwoot LICENSE](https://raw.githubusercontent.com/chatwoot/chatwoot/develop/LICENSE) | MIT phần ngoài ngoại lệ; enterprise và dependency có điều khoản riêng |
| R18 | [Salesforce record-triggered automation](https://architect.salesforce.com/docs/architect/decision-guides/guide/record-triggered.html) | Quy tắc governance/entrypoint; không có mã nguồn nội bộ của nền tảng |
| R19 | [Microsoft organize solutions](https://learn.microsoft.com/en-us/power-platform/alm/organize-solutions) | Base solution và app extension; áp dụng nguyên tắc, không sao chép quy trình enterprise quá nặng |
| R20 | [Microsoft solution concepts](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm) | Source/deployment managed-unmanaged; không định giá sản phẩm |

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

Quyết định hiện tại: ưu tiên kiến trúc core + pack và Omnichannel có adapter; chọn nền tảng cụ thể sau PoC cùng bộ OC tests. Đây là baseline tài liệu hoàn chỉnh để thiết kế/ước lượng và nghiệm thu, chưa là chứng nhận hệ thống đã triển khai.
'''

def augment(text):
    if '## PHỤ LỤC D NGHIÊN CỨU CRM' in text:
        raise ValueError('Research already integrated; regenerate from base instead')
    text = text.replace('Phiên bản 1.1 hợp nhất tài liệu dự án', 'Phiên bản 1.2 — hợp nhất tài liệu, nghiên cứu CRM và Omnichannel năm kênh')
    for chapter, body in SECTIONS.items():
        next_anchor = f'<a id="chuong-{chapter+1}"></a>' if chapter < 10 else '<a id="phu-luc-a"></a>'
        assert next_anchor in text, next_anchor
        text = text.replace(next_anchor, body.strip()+'\n\n'+next_anchor, 1)
    text += '\n\n'+APPENDIX.strip()+'\n'
    text = text.replace('## Mục lục', '**Cập nhật 1.2:** bổ sung kiến trúc hợp nhất Zalo, Facebook, TikTok, Web Form, Email; FR30–40, UC17–22, 24 UAT Omnichannel và nghiên cứu chín sản phẩm/nền tảng. [Đọc nghiên cứu và quyết định](#phu-luc-d).\n\n## Mục lục',1)
    for i in range(1,21):
        rid=f'R{i:02d}'
        parts=text.rsplit(f'| {rid} |',1)
        assert len(parts)==2, rid
        text=f'| <a id="{rid.lower()}"></a>{rid} |'.join(parts)
        text=text.replace(f'[{rid}]',f'[{rid}](#{rid.lower()})')
    text=text.replace('- [Phụ lục C — Nguồn công khai](#phu-luc-c)', '- [Phụ lục C — Nguồn công khai](#phu-luc-c)\n- [Phụ lục D — Nghiên cứu CRM và quyết định tích hợp](#phu-luc-d)')
    return text

if __name__ == '__main__':
    from pathlib import Path
    p=Path(__file__).resolve().parents[1]/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
    p.write_text(augment(p.read_text(encoding='utf-8')),encoding='utf-8')
