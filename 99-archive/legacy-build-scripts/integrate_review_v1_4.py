from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR
import re, json, hashlib

root = Path(r'D:\AI Agent\CRM')
master = root / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
text = master.read_text(encoding='utf-8-sig')
original_bytes = master.read_bytes()
appendix = (root / 'working/master_appendix_f_review_1792078127639.txt').read_text(encoding='utf-8')
history = root / 'docs/archive/research-2026-10-15'
assert 'Phiên bản 1.3 — Master chính thức duy nhất' in text
assert '## PHỤ LỤC F ' not in text

def change(old, new, n=1):
    global text
    if text.count(old) != n:
        raise ValueError(f'Expected {n}, found {text.count(old)}: {old[:110]}')
    text = text.replace(old,new)

def before(marker, body):
    change(marker, body.strip()+'\n\n'+marker)

change('Phiên bản 1.3 — Master chính thức duy nhất, hợp nhất rà soát CEO, CMO, CX và kỹ thuật',
       'Phiên bản 1.4 — Master chính thức duy nhất, đã thẩm định và hợp nhất phản biện vòng hai')
change('**TỆP MASTER DUY NHẤT HIỆN HÀNH:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.3.',
       '**TỆP MASTER DUY NHẤT HIỆN HÀNH:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.4.')
change('Các tài liệu nghiên cứu cũ chỉ là hồ sơ lịch sử trong `docs/archive/research-2026-10-15/`, không phải bản đặc tả song song.',
       'Các tài liệu nghiên cứu cũ chỉ là hồ sơ lịch sử trong `docs/archive/research-2026-10-15/`, không phải bản đặc tả song song. Phụ lục F phân tích lợi/hại của bản phản biện HTML mới, quyết định nhận/sửa/bác và phương án triển khai.')
change('- [Phụ lục E — Quyết định hợp nhất 1.3 và nguồn CEO/CMO/CX](#phu-luc-e)',
       '- [Phụ lục E — Quyết định hợp nhất 1.3 và nguồn CEO/CMO/CX](#phu-luc-e)\n- [Phụ lục F — Thẩm định phản biện vòng hai và quyết định 1.4](#phu-luc-f)')

change('| POST /v1/payments/{id}/allocate | Kế toán, số dư chưa phân bổ, hóa đơn cùng tenant | Transaction atomic; 409 nếu giao dịch đã thay đổi. |',
       '| POST /v1/payments/{id}/allocate | Quyền allocate, confirmed payment và nghĩa vụ thu hợp lệ; tenant/workspace/legal entity/currency/party, số dư và expected_version; invoice không là tiền điều kiện | Transaction atomic; 409 khi balance/version thay đổi, 403 trái quyền; invoice mapping là nghiệp vụ riêng. |')
change('PK/FK dưới đây là khóa logic; toàn bộ FK nghiệp vụ phải kiểm cùng tenant và workspace tương ứng.',
       'PK/FK dưới đây là khóa logic: quan hệ nội workspace kiểm tenant/workspace; quan hệ cross-workspace chỉ hợp lệ theo bridge được cấp phép bên dưới. Không mặc định mọi FK đều phải cùng workspace, cũng không dùng FK tenant-only để bỏ kiểm quyền.')
before('### 5.2 Bảng Leads', '''#### Ràng buộc nội workspace và cross-workspace được cấp phép

Nội workspace dùng FK(tenant_id,workspace_id,target_id) đến key tương ứng. Cross-workspace như CLIENT Project→AGENCY Contract dùng FK vật lý cùng tenant và Workspace_Account_Links/Contract_Workspace_Grants có source/target workspace, customer account, allowed relation, effective dates và authority. Contract buyer phải khớp billing legal party của workspace/brand được ủy quyền. Nếu workspace không theo account chuẩn, quan hệ thay thế phải được phê duyệt, không bỏ kiểm.

FK composite qua bridge hoặc constraint trigger được thiết kế để kiểm cả insert/update child, đổi customer/contract/bridge đích và revoke; transaction locking bảo toàn tính đúng khi hai bên đổi đồng thời. Không dùng CHECK gọi bảng khác như sự bảo đảm toàn vẹn liên tục. Link không tự cấp quyền đọc tài liệu; publish/field ACL vẫn kiểm. Tenant context thiếu phải default-deny. Cấm merge người qua workspace chỉ để vượt ràng buộc.
''')
change('| hold_reason / review_at / previous_deal_id | text / timestamptz / uuid | Bắt buộc lý do/hẹn nếu OnHold; lineage FK NULL | Giữ total age/active time; không clone làm đẹp cycle |',
'''| lifecycle_status / work_state | text / text | Open/Won/Lost theo stage category; Active/OnHold khi Open | Hoãn không thay stage_id Proposal/Negotiation; consistency kiểm trong command |
| on_hold_since / hold_reason / review_at / previous_deal_id | timestamptz / text / timestamptz / uuid | Lý do/hẹn khi OnHold; lineage FK NULL | Hold interval ghi history, accumulated_hold_seconds là cache readonly có thể rebuild |''')
change('| order_no | varchar(50) | NN unique tenant | Mã dễ đọc |',
       '| order_no | varchar(50) | NN unique tenant, gồm cả bản archived | Mã đã phát hành không tái sử dụng; số nháp khác reference thanh toán. Nếu cần numbering theo pháp nhân/series phải có ADR và match có scope, không partial unique theo archived_at. |')
change('| tax_id | varchar(40) | NULL; unique tenant + workspace khi xác minh | Không dùng mã thuế giả cho cá nhân |',
       '| tax_id / tax_country / tax_scheme | varchar / char(2) / text | NULL khi chưa rõ; legal identity đã xác minh unique theo tenant/workspace/country/scheme/tax_id | Account pháp nhân canonical; brand/business unit tham chiếu billing Account, không dùng parent_account_id để cho mọi account con trùng MST |')
change('| Quotes, Quote_Lines | deal_id uuid, revision int, expires_at date, service_id uuid, qty numeric, unit_price numeric, line_type text | Approved snapshot immutable; line_type SERVICE/PRODUCTION/MEDIA_PASS_THROUGH, tax code/net/tax/gross là cấu phần riêng. |',
       '| Quotes, Quote_Lines | deal_id uuid, revision int, status Draft/PendingApproval/Approved/Sent/Accepted/Rejected/Expired/Superseded, expires_at timestamptz, accepted_at timestamptz NULL, cost_total numeric NULL, cost_basis/version, service_id uuid, qty/unit_price numeric, line_type text | Version/bản giá bất biến sau approval; API kiểm expiry/authority/revision tại thời điểm chấp thuận, không chỉ cron. Phản hồi trễ được xét theo evidence thời điểm; Accepted đúng hạn không tự Expired. Net/tax/gross và rounding policy tách. |')
change('| Contracts, SOW_Versions | accepted_quote_id uuid NULL, parent_contract_id uuid NULL, document_type text, service_model text, legal_entity_id uuid, signer_contact_id uuid, status text, signed_asset_id uuid, revision int | MSA nhiều SOW/order/project; authority/effective conditions; notice/termination/settlement riêng; quote bổ sung gắn hợp đồng gốc. |',
       '| Contracts, SOW_Versions | accepted_quote_id/parent_contract_id uuid NULL, document_type/service_model text, legal_entity_id/signer_contact_id uuid, status, signed_asset_id, revision; effective_from/effective_to date NULL theo lifecycle; notice_value/unit/basis, notice_deadline_at timestamptz NULL, renewal_mode, allocation_policy_snapshot_id | Draft chưa biết ngày được NULL; Active phải đủ điều kiện hiệu lực, evergreen có end NULL. Notice theo điều khoản/kỳ và timezone, có audit khi đổi; không default PASS_THROUGH_FIRST hoặc auto-renew. MSA nhiều SOW/project; settlement riêng. |')
change('last_message_at timestamptz NULL; source_mode varchar(20) | Partial unique connection + provider_thread_id',
       'last_message_at/last_inbound_at timestamptz NULL; last_qualifying_interaction_at timestamptz NULL; qualifying_event_id/type; messaging_policy_version; eligibility_projection jsonb; source_mode varchar(20) | Partial unique connection + provider_thread_id')
change('policy/calendar_version text; clock_type text; started_at/due_at timestamptz;',
       'policy/calendar_version text; clock_type text; time_basis BusinessCalendar/WallClock; remaining_business_seconds bigint NULL; owner_at_breach_id uuid NULL; started_at/due_at timestamptz;')
change('| Business_Subjects | lead_id NULL, ticket_id NULL, conversation_id NULL; subject_type | CHECK đúng một FK NN và unique scoped theo resource; FK tenant/workspace; subject là cầu SLA/link, không chứa status thay nghiệp vụ |',
       '| Business_Subjects | lead_id/deal_id/ticket_id/conversation_id/project_id/deliverable_id uuid NULL, subject_type enum | CHECK num_nonnulls(sáu FK)=1 VÀ type khớp FK; mỗi FK unique scoped; subject kế thừa scope target. Không tự tạo SLA cho mọi type; clock chỉ theo policy đã bật. |')
change('| Conversation_Subject_Links | conversation_id, business_subject_id, purpose, actor/evidence/effective dates | Quan hệ N:M có quyền; Subject của Deal/Project nếu cần dùng link table typed riêng, không giả FK generic |',
       '| Conversation_Subject_Links | conversation_id, business_subject_id, purpose, actor/evidence/effective dates | N:M qua FK thật; đúng scope hoặc bridge cross-workspace được cấp phép. Đọc link không mở toàn hồ sơ đích; các clock còn lại không đóng theo một thread. |')
before('`Inbound_Events` là canonical durable inbox', '''| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Appointments | type/title, subject link, owner/participants, start_at/end_at timestamptz NN, timezone, status Tentative/Confirmed/Cancelled/Completed/NoShow | end>start, finite và non-NULL; reschedule version hủy reminder cũ; GPS/evidence check-in chỉ khi feature phù hợp được bật |
| Resources, Resource_Bookings | tenant resource_id, appointment_id, capacity model, start/end, status Hold/Confirmed/Released/Expired, hold_expires_at, row_version | Resource độc quyền dùng range[start,end) non-overlap cho active status; resource chia sẻ nhiều workspace vẫn giữ identity chung. Hold hết TTL được release dưới lock, confirm kiểm lại; pool capacity>1 cần model riêng |
| Workspace_Account_Links, Contract_Workspace_Grants | source/target workspace, buyer/billing account, contract/project, relation type, validity, authority/evidence | Bridge tenant-consistent theo loại quan hệ, kiểm khi đổi đích; không đồng nghĩa broad data grant |
| Brands, Business_Units | display_name, billing_account_id, customer reference, effective dates | Tùy chọn P1 theo nghiệp vụ; giữ pháp nhân thanh toán canonical. Deal/Project có brand reference khi cần |
| Obligation_Adjustments | obligation_id, direction Debit/Credit, type/reason, amount>0, currency, policy/approval/evidence/ERP ref, reversal | Append-only; net obligation = gross + debit − credit; adjustment không tạo cash/commission. Credit vượt phần còn phải thu đi xử lý credit/refund đúng nguồn, không chặn bằng công thức gross đơn giản |
| Refund_Reservations | original_payment_id, request/operation ID, amount, allocation linkage NULL nếu hoàn dư, state, expires/reconcile_at | Dư khả dụng trừ reservation; provider unknown không nhả tiền mù. Confirmation chuyển reserve thành confirmed refund một lần; không trừ hai lần |
| Policy_Definitions, Policy_Versions | typed config/scope/unit/owner/source/version/effective_at, Draft/Reviewed/Active, precedence/validation | Có thể là config platform thay bảng riêng; seed HTML chỉ Draft. Policy không có người sở hữu không tự bật |

Projection last_inbound/qualifying interaction lấy occurred_at/evidence hợp lệ theo reducer, không lấy reply outbound hoặc thời gian backfill để gia hạn cửa sổ. Eligibility khác phí/quota; provider/message class/permission/policy version quyết định tại dispatch. Chữ ký webhook không bắt mọi Channel_Identity có Contact: trạng thái kỹ thuật/anonymous/quarantine giữ NULL; promote Lead/Ticket/Consent mới tạo/link Contact tạm trong transaction theo đường intake.
''')

before('<a id="chuong-6"></a>', '''### 5.19 Gate triển khai vật lý và dependency closure

Không có quota bảng P0 mặc định. Mỗi capability ánh xạ bảng/field/API/provider do CRM/ERP/PMS/connector sở hữu, dependency, nguồn ghi, feature flag, migration, test và owner. Các bảng logic có thể ánh xạ đối tượng của nền tảng; không đếm tên bảng thành effort hoặc cam kết90ngày.

| Lát cắt | Bắt buộc trước bật | Có thể hoãn/tích hợp | Điều kiện mở |
| --- | --- | --- | --- |
| Nền/quyền/hồ sơ | Scope, principal/grant, contact/demand, audit, purpose/retention/suppression, source IDs | Bộ máy pack/metadata lớn, tự động hóa privacy chưa cần có bảng riêng | Không leak và thực hiện quy trình dữ liệu được; controls áp từ ngày đầu |
| Sales→contract→cash | Pipeline, activity, quote/SOW/version, contract/obligation, evidence/allocation/adjustment/period nếu tự ghi tiền | API ERP; commission nếu chưa có chính sách; PMS chi tiết | Tiền/quyền/history/reconcile đúng; field bắt buộc có mapping hoặc feature không bật |
| Một inbox/kênh | Identity/thread, durable event/outbox, send policy/attempt, assignments/SLA và health tối thiểu | Kênh thứhai, five-channel feature parity, survey engine | Quyền tài khoản/capability và recovery đã test |
| Delivery/CX | Handoff, deliverable/acceptance, issue/recovery/promises, lịch nếu thực dùng | Timesheet/editor strategy/scorecard, resource reservations nếu chưa quản ekip | SOW và request liên kết đúng, không quên cam kết |
| Mở rộng | Dependency closure và ngân sách vận hành của feature | Loyalty, MTA, AI tự hành theo business case | DDL/API + migration + UAT tương ứng, không chỉ thêm bảng |

Invoice mapping chỉ bắt buộc khi theo dõi chứng từ; chọn manual mapping hoặc ERP connector tương ứng. Commission payout/adjustment cần trước khi chi thật, không được gắn P1 rồi cho P0 payout thiếu lịch sử. Processing/retention có thể cấu hình/registry bên ngoài nhưng trách nhiệm không được hoãn. Nullable feature reference hoặc cột chưa tạo chỉ hợp lệ khi API/feature flag không yêu cầu nó và migration đã kiểm.
''')

before('### 4.1 UC01 Tiếp nhận lead đa nguồn', '''Các quy tắc ngoại lệ và tính tiền tại 3.13.4 áp dụng xuyên các UC. Mỗi UC giữ đúng trạng thái đã có; không xem queue/reassign như nhu cầu mới hoặc xóa breach. Các chính sách mang số cụ thể phải qua A.6 trước activate.
''')
before('<a id="chuong-4"></a>', '''#### 3.13.4 Ngoại lệ, tiền dư và điều phối đồng thời

- NoCapacity chuyển assignment về queue có owner/escalation trong transaction với expected_version/outbox; giữ Lead lifecycle, first_attempt/history và deadline khách. Attempt limits/OnHold review là policy; không ép gọi đủ quota hoặc Lost sau60ngày. Bị từ chối liên hệ thì stop theo phạm vi phù hợp.
- API kiểm Quote expiry tại accept/contract; scheduler chỉ cập nhật projection. Contract/Order Terminated tạo settlement review từng obligation: giữ phần đã phát sinh/minimum commitments/fees hợp lệ; giảm/void phần thật sự được hủy bằng adjustment có căn cứ. ERP credit/invoice theo nguồn, không xóa ledger. Contract obligations chưa hạch toán không thay AR/denominator DSO.
- Client-wait là blocker có owner/review và replan tài nguyên riêng; không tự acceptance/billing/đổi ngày cam kết. Ticket có thể kỹ thuật đã giải quyết nhưng khách chưa xác nhận: giữ technical evidence, no-response outcome, authority và reopen; incident/notice nghĩa vụ còn mở không tự đóng theo ticket.
- Placeholder reply không chứng minh phản hồi thực chất. Nếu còn xử lý nội bộ, lưu promise due và resolution đang chạy; cho phép trạng thái Resolved/NoReplyNeeded hợp lệ, không ép hai nút mỗi message. Lời hứa tại thời điểm tuyệt đối dùng WallClock; các clock khác theo policy/entitlement, có thể24/7 chứ không luôn giờ hành chính. Assignment intervals/owner_at_breach chỉ là evidence; không tự kết tội người giữ>50%.
- Sweeper có thể SKIP LOCKED để chia queue nhưng tất cả lệnh đổi assignment/tạo-dispatch intent phải dùng cùng aggregate lock/version contract. In-flight phối hợp chuyển người có grace hữu hạn theo episode/actual attempt, không giữ vô hạn vì pending intent. Ghi breach theo due gốc; không sửa deadline chỉ vì mạng chậm. Provider call ngoài DB transaction; unknown reconcile, không giả đã gửi.
- Merge/unmerge giữ lock order nhất quán cho contact và dependent aggregates, xử lý deadlock retry có bound; resolve canonical với version và giữ origin identity/contact/evidence. Redirect không xóa nguồn, không OR consent và không sửa chủ chứng từ. Không cho cycle hoặc link sang tenant/workspace khác.
- Rounding phân bổ dùng integer minor units và rule approved: quota chính xác của nhóm dòng hợp lệ→floor→phân từng đơn vị dư theo fractional remainder giảm dần, tie-break key ổn định; phải giữ caps/currency/tax/net semantics và tổng. Không bù dư sang cấu phần thành âm hoặc sang dòng khác loại. Số liệu invoice ERP không được tự sửa cho khớp thuật toán quản trị.
- Hoàn tiền dư chưa phân bổ: lock receipt/số dư, reserve refund amount và authority, gửi lệnh theo hệ thống có quyền, chờ xác thực, ghi Refund linked original; không cần đảo allocation chưa từng có hoặc clawback service commission không phát sinh. Nếu refund phần đã allocate, reversal đúng phần gốc. Available = confirmed incoming − confirmed refunds − net active allocations − active refund reservations theo cùng ledger scope; không tính confirmation đồng thời như cả reserve lẫn refund. Pending/unknown refund không được giải phóng số dư để allocate lại mù.
- Short-payment có case phân loại: payer thiếu tiền, phí ngân hàng có chứng từ, commercial discount hoặc write-off. Finance dùng adjustment đúng loại và hạn mức; ngưỡng100.000/0,5% chỉ là đề xuất, không chứng minh bản chất phí. Với gross/net settlement qua provider, định nghĩa receipt/cost/commission basis rõ; không tạo cash giả từ xóa nợ. Production commission theo line/pool/policy đã duyệt, chưa có rule là PendingPolicy; không tự full hoặc0.
''')

change('| Sales | Owner và hồ sơ chia sẻ có hạn | C/R/U phần được giao; không D chính thức | Không X danh sách; không I hàng loạt mặc định |',
       '| Sales | Owner và grant còn hiệu lực | C/R/U Lead/Deal/Quote/Activity được giao; R payment state/obligation và Ticket summary cần thiết; R commission bản thân; không raw finance/PII ngoài nhiệm vụ | Không X danh sách; I hàng loạt chỉ khi có quyền riêng |')
change('| AM/CSKH/Delivery | Khách/dự án được phân | C/R/U ticket/deliverable; R SOW liên quan | X tài liệu được phép cho đúng khách; không X customer list |',
'''| AM/CSKH | Account/Contact/Project/contract grant đúng nhiệm vụ | C/R/U onboarding/success plan/ticket/recovery; tạo/sửa renewal/upsell Deal/Quote khi có commercial permission; R SOW/acceptance và công nợ summary liên quan; approve/refund quyền riêng | X tài liệu publish đúng khách, không X customer list |
| Delivery | Project/deliverable/campaign được phân | C/R/U task/asset/deliverable phù hợp giai đoạn; R brief/SOW/plan; acceptance theo authority, không đọc commission/finance nội bộ mặc định | Không X PII; nhập asset/evidence theo quyền dự án |''')
change('| Kế toán | Chứng từ trong tenant được gán | R hợp đồng; C/R/U reconciliation; không U lead | X sổ đối soát được duyệt; I sao kê kiểm soát |',
       '| Kế toán | Tenant/legal entity và hồ sơ tài chính được gán | R approved quote/contract/SOW/acceptance/billing identity tối thiểu. Commands post/allocate/reconcile/propose-adjust/reverse/close-period theo quyền và hạn mức riêng; không UPDATE/DELETE tiền gốc/khóa kỳ tùy ý hoặc sửa commercial Lead/Deal | X sổ đối soát được duyệt, I sao kê có mapping và dedup; duyệt ngoại lệ tách người theo quy chế |')
before('### 6.2 Bảo vệ dữ liệu và chống thất thoát', '''Activity/timeline kiểm quyền trên chính activity và các resource restrictions áp dụng (account/deal/project/branch), bên cạnh quyền Contact. Không suy Contact access=mọi lịch sử; không dùng OR branch để vượt account deny. Activity B2C/field NULL/internal note có policy riêng, không hard-code AND mọi cột. Counts/snippet/file/AI tuân cùng quyền.

Với pool PostgreSQL: bắt đầu explicit transaction, bind context từ identity/server-side mapping qua SET LOCAL hoặc parameterized set_config(...,true), rồi mới chạy query scoped; missing/invalid context fail closed. Không dùng session-level context cho request dùng chung pool; bảo đảm không có stale session baseline và scoped query ngoài transaction. App role không owner/BYPASSRLS; SQL injection hoặc quyền đổi context tùy ý vẫn phải phòng, SET LOCAL không tự xác thực người dùng. Các job/cursor/retry có cùng contract và test hai tenant liên tiếp trên một connection.
''')
before('### 6.4 Lưu giữ xóa và legal hold', '''#### Deadline pháp lý và luồng AI: cấu hình theo nghĩa vụ

Privacy_Requests lưu received_at, valid_request_received_at, verified_at, request_type, legal_basis/version, response_due_at, action_due_at, extension/history và owner. Tính deadline theo loại quyền/sự kiện đúng thủ tục ở S02/Phụ lục F; không mặc định72h sau verified_at hoặc dùng xác minh để reset hạn. Incident lưu detected/awareness/assessment/confirmed và notification obligations riêng; không đợi nhãn Confirmed mới xem xét clock. Privacy owner xác nhận nhánh/recipient/căn cứ áp dụng.

Suppression cho yêu cầu hợp lệ được commit atomically trước xác nhận xử lý thành công; dispatch recheck trạng thái authoritative, không chờ cleanup15phút mới chặn marketing. Cleanup queued/replicas có SLO đo riêng; unavailable và in-flight có reconciliation/exception, không hứa0giây vật lý hay thu hồi chắc chắn tin provider đã nhận. Không đổi consent dựa yêu cầu giả chưa được xác minh vừa đủ.

AI data gateway áp minimization, data classification và pseudonymization/redaction có policy; mapping placeholder là dữ liệu có thể tái định danh, cần kiểm quyền/retention. Training permission, retention/log/cache/feature settings, region/subprocessor và căn cứ chuyển dữ liệu là tiêu chí riêng; không dùng nhãn Training Opt-out như ZDR. Trường hợp vendor/feature chưa đáp ứng, giữ tác vụ thủ công/khôngAI phù hợp. Không gửi CCCD/tài khoản/PII không cần thiết hoặc tin toàn thread chỉ vì đã dùng regex che số.
''')

change('| NFR08 | Tiền và replay | Replay 100 lần một event không nhân tiền, điểm hoặc hoa hồng; tổng ledger đối chiếu chính xác theo quy tắc làm tròn. |',
       '| NFR08 | Tiền và replay | Replay100lần không nhân effect thuộc module đã bật; tiền/commission cần test khi dùng; điểm loyalty chỉ khi mở P2. Ledger/caps/rounding đối chiếu đúng; không yêu cầu tạo Loyalty_Ledger để pass MVP. |')
change('| U22 | FR13 | Prompt injection trong tệp khách | Không export/đổi quyền/gửi tin tự động | P1 |',
       '| U22 | FR13 | Prompt injection trong tệp khách | Không export/đổi quyền/gửi tin tự động; feature-off không mở tool bypass | P0 guard trước bật AI; N/A model test nếu không triển khai AI |')
before('### 8.3 Kiểm soát sai số và phân tích', '''Health MVP dùng các chiều tài chính, giao hàng, quan hệ và outcome riêng với evidence, freshness, coverage và action owner. Missing không tự100 hoặc0. Score tùy chọn có metric direction/window/sample/weights/version; quan sát100 với coverage60% phải hiện thiếu dữ liệu, không tự Healthy/upsell. Không tính actual/target cho mọi KPI: CPL thấp tốt, revenue cao tốt, một số metric có target range. Risk flags như S1/unpaid cần severity/aging/value/dispute context; nhiều ticket cùng incident không tự trừ lặp. Score chạy shadow/pilot trước khi dùng tự động; không lấy trọng số30/30/20/20 và cap40 làm chuẩn chưa được phê duyệt.
''')
before('Các điểm mở không ngăn sử dụng tài liệu làm baseline thiết kế và thảo luận.', '''Mỗi policy/parameter cần type/unit/scope, owner, source/evidence, default đề xuất, version/effective_at, Draft/Reviewed/Active và validation. Chốt lịch/ngày làm việc thực tế, phân biệt claim/FRT/discovery, notice basis, self-approval/discount, cost/margin, tolerance/waterfall/production basis và quality fallback. Không autoactivate seed từ tài liệu phản biện; working day không cố định480phút nếu ca được khai báo7,5giờ. Lịch thứBảy chỉ bật khi chủ dự án xác nhận. Legal deadline policy không được thay bằng marketing/internal SLA tùy ý.
''')

trace = '''| FR30–32 Connections/Identity/Thread | UC17/18/19/22 | Channel_Connections/Identities, Inboxes, Conversations/Participants, journal; scoped ACL/capability | OC01–03/11–13/15/23; INT02/24; RV05/11 |
| FR33–34 Inbound/Outbound | UC17/19/21 | Inbound_Events, Messages/Status, Outbound_Intents/Attempts/Outbox; policy/idempotency | OC01/05–09/16–17/19; INT01/17/25/26; RV05/14/17 |
| FR35–36 Assignment/Timers | UC02/09/20 | Assignments, Business_Subjects, SLA_Episodes/Promises; version/calendar | U02–04; OC04/10/18; INT04/05/23; CX-U03–CX-U09; RV01/12/13/14 |
| FR37 Search/File/Protection | UC11/12/14/18 | ACL/grants, search/cache/file/RLS; không bypass bằng link | U16/17; OC03/14/20; INT23/28/29; RV10/15/17 |
| FR38 Sync/Recovery | UC21 | Checkpoints, connection, event/intent state, coverage/reconcile | OC08/09/19/21; INT11/25/26; RV14/17 |
| FR39–40 Business Links/Email | UC17/19/22 | Business_Subjects/Conversation links/Message_Attachments; typed FK/MIME/policy | OC11/13/14; INT04/24; CX-U05/23; RV01/05/10 |
'''
change('| NFR01–12 | Mọi luồng | Monitoring, restore, policy, export | Load test, U17/U21/U24, portability test |',
       trace + '| NFR01–12 | Mọi luồng | Monitoring, restore, policy, export; feature scope | Load test, U17/U21/U24, portability và RV tests theo module bật |')
change('| FR09–10 Journey/loyalty | UC10/11/13 | Journey instances, Consent, Loyalty_Ledger | U15/U23; P2 chỉ khi bật |',
       '| FR09–10 Journey/referral/loyalty | UC10/11/13 | Consent/suppression; Journey/Referral theo feature; Loyalty_Ledger chỉ points P2 | U15/OC17/INT17; U23 khi referral/points được bật; không bắt points trong P0 |')

rv = '''### 9.13 Nghiệm thu bổ sung sau phản biện vòng hai

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
'''
before('<a id="chuong-10"></a>',rv)

change('| 1.3 | 15/10/2026 | Master duy nhất hiện hành; đã hợp nhất CEO/CMO/CX/phản biện; tham số chưa cung cấp theo A.6, go-live theo Chương9 |',
       '| 1.3 | 15/10/2026 | Baseline trước phản biện vòng hai, được lưu snapshot; nội dung phù hợp kế thừa1.4 |\n| 1.4 | 15/10/2026 | Master duy nhất hiện hành; vá lỗi đã xác minh và hợp nhất thẩm định HTML ở F, tham số chưa chốt theo A.6; go-live theo Chương9 |')
text += '\n\n' + appendix.strip() + '\n'

# Independent arithmetic/counterexample checks; no CRM runtime is implied.
parts=[Decimal('.6')]*5
bad=[Decimal('3')-sum(x.quantize(Decimal('1'),rounding=ROUND_HALF_UP) for x in parts[1:])]+[Decimal('1')]*4
fixed=[x.quantize(Decimal('1'),rounding=ROUND_FLOOR) for x in parts]
for i in range(int(Decimal('3')-sum(fixed))): fixed[i]+=1
assert min(bad)<0 and sum(bad)==3
assert min(fixed)>=0 and sum(fixed)==3
review_lines=(root/'working/gemini_review_1792078127639.txt').read_text(encoding='utf-8').splitlines()
p0_names=[]
for line in review_lines:
    if re.match(r'^(236|237|238|239|240|241):',line):
        body=re.sub(r'^\d+: (?:\| )?\d+\. [^:]+:\s*','',line)
        p0_names.extend(x.strip().rstrip('.') for x in body.split(','))
assert len(set(p0_names))==81
assert len(re.findall(r'^#### .*\bFR\d{2}\b',text,re.M))==40
assert len(re.findall(r'^### 4\.\d+ UC\d{2}\b',text,re.M))==22
assert len(re.findall(r'^\| RV\d{2} \|',text,re.M))==20
assert len(re.findall(r'^\| R\d{2} ',appendix,re.M))==42
assert text.count('```')%2==0
history.mkdir(parents=True,exist_ok=True)
snapshot=history/'CRM_MASTER_BRD_SRS_HOP_NHAT_v1.3.md'
if snapshot.exists(): raise RuntimeError('Snapshot exists; do not overwrite')
snapshot.write_bytes(original_bytes)
master.write_text(text,encoding='utf-8',newline='\n')
checks={
    'master':master.name,'version':'1.4','source':'gemini-code-1792078127639.html',
    'source_sha256':hashlib.sha256((root/'gemini-code-1792078127639.html').read_bytes()).hexdigest(),
    'snapshot_sha256':hashlib.sha256(original_bytes).hexdigest(),
    'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
    'FR':40,'UC':22,'review_findings':42,'RV_UAT':20,'html_P0_unique_names':81,'html_config_rows':24,
    'rounding_counterexample':list(map(str,bad)),'corrected_example':list(map(str,fixed)),
    'runtime_DB_provider_tests':'not run; document and arithmetic validation only'
}
(history/'REVIEW_V1_4_VALIDATION.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if 'sha256' not in k},ensure_ascii=True,indent=2))
