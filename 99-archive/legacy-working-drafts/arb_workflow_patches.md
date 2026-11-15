#### G.6.3 Bản vá WF01 — Intake chưa biết B2B/B2C

**Thay thế dòng `business_model` tại Mục 5.2 bằng:**

| business_model | varchar(12) | NN; Unknown/B2B/B2C; default Unknown nếu intake chưa rõ | Unknown vẫn được queue/owner/SLA; không suy từ domain/email. Trước Qualified/Converted và tạo Deal phải xác nhận B2B/B2C; lưu actor/evidence của phân loại. |

**Bổ sung vào quy tắc bắt buộc của UC01 tại 4.1 và UC03 tại 4.3:**

Yêu cầu tư vấn hợp lệ chưa rõ người mua tạo Lead `business_model=Unknown`, có Contact provisional khi cần, source và owner/queue/SLA. Không giữ lead hợp lệ ở quarantine chỉ vì chưa biết business model. Qualification xác nhận B2B/B2C trước Qualified/Converted, sau đó áp điều kiện Account/buyer Contact. Unknown không là NoFit và không bị loại khỏi mẫu số intake hợp lệ.

**Bổ sung tại Mục 9.13:**

| WF-U01 | Inbound hợp lệ chưa biết B2B/B2C, sau đó xác nhận người mua | Một Lead Unknown có owner/queue/timer; không Account giả; convert bị chặn trước phân loại, sau xác nhận convert đúng một effect |

#### G.6.4 Bản vá WF02 — Phản hồi đúng yêu cầu và SLA episode

**Bổ sung quan hệ logic vào bảng Mục 5.18:**

| Message_Subject_Links | message_id, business_subject_id; link_role request_source/response_to/context; waiting_episode_key hoặc sla_episode_id/clock_type khi response_to; actor/source/evidence | FK/scope hợp lệ; message có thể đáp nhiều request được xác nhận. Internal note chỉ context, không hoàn thành human-response clock. Có thể ánh xạ quan hệ native, không bắt thêm một bảng vật lý riêng. |

**Bổ sung sau bảng API tại Mục 5.17 và liên kết tại FR36/FR39:**

API `POST /v1/conversations/{id}/messages` nhận `response_targets[]` khi phản hồi một nghĩa vụ. Server kiểm quyền từng subject, quan hệ với thread, recipient, episode/version hiện hành và trạng thái assignment. Client không được tự đặt clock completed. Worker lưu evidence khi đạt completion criterion của policy; reducer chỉ hoàn thành clock thuộc response targets hợp lệ. Reply chưa phân loại vẫn gửi được khi đủ quyền/policy nhưng không tự dừng tất cả SLA; đưa vào queue làm rõ nếu còn nghĩa vụ chưa xác định. Autoack/private note/unknown_outcome không hoàn thành human clock. Một phản hồi thực chất có thể đáp nhiều yêu cầu; không ép mỗi message chỉ thuộc một request.

Inbound chưa rõ request được lưu và có intake clock theo policy, rồi người phụ trách phân loại. Lúc phân loại không reset thời gian khách chờ; lưu nguồn và ánh xạ episode, không tự tạo mọi clock trên tất cả resource của Contact. Completion criterion nêu accepted/delivered hoặc evidence khác theo capability, khác xác nhận khách đã đọc.

**Bổ sung tại Mục 9.13:**

| WF-U02 | Thread có khiếu nại A và báo giá B; reply B, rồi reply A+B; receipt trùng | Reply B không dừng clock A; reply A+B chỉ dừng clock đạt criterion; target ngoài quyền bị chặn; replay không lặp completion/history |

#### G.6.5 Bản vá WF03 — Hợp đồng chuyển trạng thái

**Bổ sung Mục 3.13.5 sau Mục 3.13.4; cập nhật các ô status tại 5.2/5.5/5.6/5.8/5.13/5.16 tham chiếu mục này:**

Mọi chuyển trạng thái nhận command/idempotency key và expected_version; server kiểm action/scope/authority, trạng thái nguồn, điều kiện và side effects. State/history/outbox commit atomic. Command trái trạng thái trả409, dữ liệu/guard sai trả422 hoặc403 theo quyền; không có partial effect. Không cho PATCH status tùy ý. Scheduler dùng cùng command guard. Catalog transition có version/owner; instance đang chạy chỉ đổi policy qua migration được duyệt.

Bảng sau là **baseline chuyển trạng thái đề xuất để chủ nghiệp vụ chốt**. Mapping native phải bảo toàn guards; chưa phê duyệt transition/cấu hình bắt buộc của một capability thì capability đó chưa được activate. Mỗi mũi tên là một command riêng, không cho nhảy tùy ý qua bước. Trạng thái đích bị từ chối nội bộ không được làm mất nội dung và evidence phiên bản trước.

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
| Payment | Verification Pending→Confirmed/Rejected; matching/allocation/reconciliation theo các projection riêng | Confirm cần evidence; correction bằng event/reversal, không sửa posted amount. Pending không allocate; Confirmed nhưng Unidentified vẫn tồn tại. Reject một evidence không xóa receipt được evidence khác chứng minh. Refund có state/reservation theo DB02. |
| Commission | Preview→Earned→Approved→Payable→Paid; policy có thể xét approval trước earned nếu định nghĩa rõ | Earned theo eligible allocation/policy, Approved đúng authority, Payable đủ release/period; Paid cần payout confirmed. Partial payout lưu paid_amount/remaining, không mark toàn bộ Paid. Refund tạo Reverse/Adjustment liên kết, không ghi đè lịch sử Paid. |

Định nghĩa clock áp dụng cho từng transition gồm `start_event`, `completion_criterion`, `pause_allowed`, `resume_rule`, `cancel_outcome`, `reopen_carryover`, calendar/time basis và authority. Không có đủ các trường áp dụng thì policy giữ Draft, không tự tạo timeout nghiệp vụ bằng con số không được duyệt. Reassign, tin khách gửi thêm, private note, đổi priority hoặc pending_internal không tự reset clock. Promise giờ tuyệt đối giữ WallClock; thay promise cần lịch sử thỏa thuận.

**Bổ sung tại Mục 9.13:**

| WF-U03 | Chuyển hợp lệ/trái phép/replay/concurrent cho từng đối tượng bật trong release | Guard và effect đúng bảng transition đã duyệt; không sửa tự do status. Deal reopen không sinh lại cash/project; Blocked không dời cam kết; Completed chưa Paid còn công nợ; pause/reopen giữ đúng breach |

#### G.6.6 Bản vá WF04 — Gate theo release và feature thực bật

**Thay đoạn mở đầu Mục 9.5; bổ sung dẫn chiếu tại 5.19/9.11:**

Mỗi release có `Release_Acceptance_Profile` được version và phê duyệt, gồm capability/FR bật, dependencies, nguồn ghi, provider, luồng tiền, policy versions, owner và mapping test. Mỗi test tách `test_severity` (hậu quả), `delivery_priority` (giai đoạn capability) và `applicability_expression`. Nhãn P0/P1/P2 không thay biểu thức áp dụng.

Mọi control về tiền/quyền/consent/gửi đúng người/SLA/phục hồi của capability đang bật phải Pass trước go-live. Applicability False ghi Not Applicable với evidence API/job/role/flag không có đường sử dụng capability; không ghi Pass. Applicability True chưa chạy là Not Run và chưa đủ điều kiện ký. Deferred chỉ cho capability chưa bật có dependency closure; không được defer control của capability đang chạy. QA/business owner ký cùng actual/build/fixture/evidence; không nghiệm thu bằng tỷ lệ số test.

| Test | Sửa applicability trong các bảng 9.5/9.12/9.13 |
| --- | --- |
| U19/M11 | P0 control khi launch/publish cần approval được bật; N/A khi ngoài phạm vi; không hoãn control vì nhãn P1 cũ. |
| U23 | Tách `U23-R` reversal referral khi referral P1 bật; `U23-L` reversal điểm khi loyalty P2 bật. |
| U20/M25 | Khi dùng spend nhập tay/sync/report phải thử thiếu dữ liệu/freshness; không bắt mua API spend P1. Không dùng spend thì N/A có evidence. |
| CEO-U21/RV04 | Concurrency resource là P0 control khi reservation bật; nếu chỉ lịch cá nhân thì N/A resource và vẫn thử lịch/hủy reminder đang dùng. |
| U11/U12/FA và commission | Cash/allocation test theo phần cash bật; payout/refund/commission có control tương ứng trước bật, không bật payout rồi defer adjustment. |
| U22/INT27/INT28/OC20 | Guard trước bật AI; eval model/STT N/A khi AI off; kiểm feature-off không còn đường tool/retrieval ngoài ý muốn. |

Profile pilot đề xuất: một nguồn/một inbox; quyền, contact/demand, pipeline/next action, quote/SOW, contract/obligation, receipt nhập tay có kiểm soát, handoff/milestone/ticket và recovery. Không AI, không điểm, không forecast health tự động, không bắt API ERP/spend/resource engine nếu chưa dùng. Thay đổi so với profile phải có CR/effort/dependency/test trước activation; mục tiêu năm kênh không trở thành năm kênh bắt buộc trong 90 ngày.

**Bổ sung tại Mục 9.13:**

| WF-U04 | Profile chỉ cash thủ công + một inbox; sau đó bật launch/referral/AI | Test áp dụng và N/A có căn cứ; bật feature tự yêu cầu control liên quan trước activation, không bỏ qua U19/U23 vì nhãn cũ |

#### G.6.7 Bản vá WF05 — Business keys của conversion và SLA

**Bổ sung sau bảng Deals tại 5.5 và SLA_Episodes tại 5.16:**

Conversion có stable `conversion_key` theo tenant/workspace/Lead/demand và `opportunity_intent_key` do server xác định, khác HTTP request key. Concurrent conversion của cùng logical intent trả cùng Deal/result refs. Nhu cầu có nhiều cơ hội thật phải có intent keys riêng và evidence/actor; không UNIQUE toàn cục `lead_id` vì có thể có nhiều Deal hợp lệ. Conversion mapping lưu result refs/policy/actor; chỉ commit Converted sau khi tạo/link kết quả thành công.

SLA_Episodes có logical unique key `(tenant_id,workspace_id,business_subject_id,waiting_episode_key,clock_type)`. Episode key dựa canonical request/unanswered turn/lifecycle event theo policy, không theo worker attempt hoặc received_at. Reopen hợp lệ có episode key mới liên kết `prior_episode_id`, carryover/breach history theo policy. Duplicate/reassignment không đổi key; nhiều clock khác type được tồn tại, hai FRT cùng episode thì không. Constraint/index vật lý hoặc invariant native tương đương phải được kiểm dưới concurrency trước bật.

**Bổ sung tại Mục 9.13:**

| WF-U05 | Hai event ID khác cùng request; hai lệnh convert khác HTTP key cùng intent; nhu cầu có hai cơ hội thật | Một FRT/episode/type và một Deal cho cùng intent; hai intent hợp lệ có hai Deal; reassign không thêm clock; reopen có lineage tới episode trước |

