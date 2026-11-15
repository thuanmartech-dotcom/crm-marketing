# Rà soát xuyên chương — workflow/trace — Master 1.4

Phạm vi: đọc toàn văn Master1.4 (Chương1–10, A–F); đối chiếu rules ở3.13.4 và gate5.19/9.11 trước kết luận. Đây là audit đặc tả. Không có bằng chứng chạy ứng dụng/DB/provider. Không xác định Blocker runtime từ tài liệu. Bốn Major dưới là thiếu/không đồng bộ đặc tả có thể làm implementation sai; không khẳng định phần mềm đang có lỗi.

## W01 — Major — Lead intake buộc biết B2B/B2C trước bước qualification

Căn cứ:5.2 dòng1301 business_model NN chỉB2B/B2C; UC01 dòng956 tạo Lead từ form hợp lệ; UC03 dòng988 mới discovery/phân loạiB2B/B2C;7.4 cho dữ liệu tối thiểu. Đã rà toàn văn: chưa có lifecycle semantics Unknown/Unclassified cho model Lead. Intake/quarantine hiện có là bước giữ sự kiện, không giải thích cách lead hợp lệ chưa rõ model được đưa vào queue/SLA vận hành.

Phản ví dụ: khách DM “Tôi cần tư vấn quay video, liên hệ email này” chưa biết người mua cá nhân hay đại diện công ty. Nếu tạo Lead ngay thì phải đoán model hoặc insert không hợp lệ; nếu giữ quarantine thì lead hợp lệ không vào SLA/owner theoUC01.

Patch thay dòngbusiness_model5.2:

| business_model | varchar(12) | NN; Unknown/B2B/B2C; default Unknown ở intake chưa rõ | Unknown được nhận queue/owner/SLA, không tự suy từ email/domain. Trước Qualified/Converted và tạo Deal phải xác nhậnB2B/B2C; lịch sử phân loại cóactor/evidence. |

Patch thêmUC01/UC03:

> Yêu cầu tư vấn hợp lệ chưa rõ người mua cá nhân/doanh nghiệp tạo Lead business_model=Unknown, Contact provisional nếu cần, source/evidence và queue/owner/SLA như lead hợp lệ khác. Không dùng quarantine thay hàng đợi chăm sóc chỉ vì chưa phân loại. Qualification xác nhậnB2B/B2C trước Qualified/Converted; lúc đó mới áp điều kiện Account/buyer Contact. Unknown không bị coi làNoFit hoặc mất denominator intake.

Test W-U01: một inbound hợp lệ không cung cấp model → một LeadUnknown cóowner/queue/timer; không tạoAccount giả; chặnconvert tới khi phân loại; phân loạiB2B rồiconvert đúng một lần.

## W02 — Major — Chưa có quan hệ message→request/episode để chứng minh phản hồi đúng nghĩa vụ

Căn cứ:FR36 dòng800 yêu cầu publicreply đúng request;FR39 dòng839 mộtthread nhiều yêu cầu;3.13.4 đã nói không đóng tất cảclock;5.18 dòng1587 chỉConversation_Subject_Links ở grainthread→subject;5.16 Messages dòng1544 không chứa subject/episode;5.17 API send dòng1564 không có lựa chọn nghĩa vụ được phản hồi. Nguyên tắc đúng đã có, thiếu hợp đồng dữ liệu/command thực thi. Không kết luận cần thêm một bảng vật lý riêng.

Phản ví dụ: một emailthread cóTicketA khiếu nại vàDealB báo giá, một reply nói riêng giáDealB. Nếu reducer chỉthấypublicreply trênthread thì không biếtclock nàođược hoàn thành; nếu hoàn tấtcả hai sẽvi phạmINT04/CX-U23.

Patch thêm5.18 và5.17:

> Message_Subject_Links (logical relation, có thể ánh xạ bảng native) gồm message_id, business_subject_id, link_role=request_source/response_to/context, actor/source/evidence và created_at. response_to chỉ rõ waiting_episode_key hoặc SLA_episode_id/clock_type đủ để định danh nghĩa vụ đang được đáp. Message nội bộ chỉ được linkcontext, không làmresponse completion. Inbound phân loại chưa rõ vẫn lưu/tạo intakeclock theo policy, vào queue làm rõ; không tự mở mọiclock của mọiworkitem liên quanContact.
>
> POST /v1/conversations/{id}/messages nhận response_targets[] tùy loại thao tác. Server kiểm quyền từngsubject, linkthread hợp lệ, episode/version còn đúng vàrecipient; không tinclient tự tuyên bốclock đã hoàn thành. Worker ghiresponse evidence khi đạt completioncriterion củapolicy, reducer chỉ hoàn thànhclock thuộcresponse_targets hợp lệ. Không cótarget thìmessage vẫn đượcgửi khi hợp lệ nhưng không tự dừng tấtcảSLA. Cùngreply có thểđáp nhiềurequest khi người xửlý xácnhận; không ép mộtreply chỉmộtrequest. Autoack/note/unknown_outcome không hoàn thànhhumanclock.

Test W-U02:thread cóA+B, replytargetB→clockA vẫnchạy; duplicateproviderreceipt khôngstop hai lần; replytargetA khôngcóquyềnA→403/noeffect; replythựcchấtđápA+B cóhai targets→chỉclockđủcriterion dừng.

## W03 — Major — Có state enums nhưng chưa đủ transition contract cho các đối tượng lõi

Căn cứ:9.11 dòng1996 tự đặt tiêu chí có state machine;5.2/5.5/5.6/5.8/5.13 chỉenum hoặc fieldstatus.3.13.4 bổ sung nhiềuexception nhưng chưa định nghĩa đầyđủ allowedfrom/to, actor vàeffect. Đây thiếuđặc tả logic, khác việcchưa xuấtDDL vật lý đã được5.19/9.11 côngbố.

Patch thêm mục “Hợp đồng chuyển trạng thái bắt buộc” sau3.13.4. Các tên dưới là mô hình logic, nền tảng được mapstatus native nhưng phải bảo toàn guard:

> Mọi transition nhận command_id/idempotency_key vàexpected_version, kiểmquyền/action/scope hiện tại,allowedfrom/to, preconditions, sideeffects; state/history/outbox commitatomic. Transition trái phép trả409/422 không cópartialeffect. Job/scheduler không cóquyền bypassguard. Không choPATCHstatus tựdo. Catalogtransition cóversion vàowner; instance giữpolicyversion hoặc migration đượcduyệt.

| Đối tượng | Lệnh/chuyển hợp lệ tối thiểu | Guard và sideeffects bắt buộc |
| --- | --- | --- |
| Lead | New→Assigned→Contacting→Qualified→Converted; active→Nurture/Dormant/Disqualified; reactivate theoevidence | Queue/owner đúng; Unknown đượcintake nhưng Qualified cầnmodel/nhucầu/nextaction; Converted cần kếtquảconversion atomic; Disqualified cầnreason; quaylạigiữhistory/cohort. |
| Lead handover | Pending→Accepted/Rejected/Recycled; recycled→Pending khiđủđiềukiện | Kháclifecycle; rejectNoCapacity đưaqueue+escalation khôngreset leadprogress/SLA. |
| Deal | Openstage→Openstage/Won/Lost; Active↔OnHold chỉkhiOpen | Pipelineversion/role/nextaction; Won theo commercialgate đượcchốt, không cầnPaid; Lost córeason/evidence; reopen bằngcommand cóauthority giữclosedhistory và khôngtái phát sinhcontract/cash. |
| Quote revision | Draft→PendingApproval→Approved→Sent→Accepted/Rejected/Expired; revision mớiSupersedeoffer cũtheopolicy | Tách internalapprovals vàcustomeracceptanceevents; nhậnApproved hoặcSent phải cóacceptanceauthority/expiry/terms; approvalkhôngđủ thìkhôngacceptedbinding. Từchốinộibộ trảDraft/newrevision córeason; snapshot đãapproved bấtbiến;Acceptedđúnghạn khôngExpirengược. |
| Contract | Draft→PendingSignature→Signed→Active→Expired/Terminated; Draft/PendingSignature→Cancelled | Signed vàeffective làhai mốc;Active cần authority/effectiveterms;phụlục córevisionriêng; termination→settlementreview, khôngauto voidledger. MSA không buộccóacceptedquote; accepted_quote nếu có phải đúngbuyer/currency/revision. |
| Order | Draft→Confirmed→InDelivery→Completed; Draft/Confirmed→Cancelled; Confirmed/InDelivery→Terminated | Confirmkhóa approved commercialbasis/lines/obligations;InDelivery cầnstartauthorization;Completed theodeliverables/milestones đượcquyđịnh, không tựPaid;Cancel/Terminate cósettlement theođiềukhoản, không xóatiền. |
| Project | Draft→PendingStart→Active→Completed; Active↔Blocked; Active/Blocked→Terminated | Active cầnhandoffaccepted vàauthorization đúngscope;Blocked cầnreason/owner/review, không tựdờicontractdate;Completed cầnacceptanceápdụng/offboarding cònhiệnriêng; nhiềuSOW nhiềuProjecthợplệ. |
| Deliverable | Planned→InProgress→InternalReview→ClientReview→Accepted; review→Rework; change→CR | Version/hash/QA vàapprover;defect khôngtrừquotađổiý; Acceptedasset đổi thìversionreviewmới, khôngghiđèacceptancegốc. |
| Ticket | Open→InProgress↔WaitingCustomer→Resolved→Closed; Resolved/Closed→reopen theo policy | Triage/SLA/owner; WaitingCustomer khôngtựpausemọiclock;Resolved cầntechnicalevidence/outcomecode;Closednoresponse khácverified;reopen giữbreach vàremainingtime theoepisodepolicy. |
| Conversation | open→resolved→closed; resolved/closed→open khiinbound/newwork hợp lệ | waiting_party táchstatus; khôngclose linkedtickets hoặcclockkhác;reopenhistoricalbackfill khôngtựmởliveclock;routing vàassignmentversion kiểmriêng. |
| Payment | VerificationPending→Confirmed/Rejected; matching/allocation/reconciliation làprojection độc lập | Confirmcầnbankevidence; correction bằngevent/reversal, khôngsửaamountđãpost;Pending khôngallocate;ConfirmedUnidentified vẫn tồn tại; rejectevidencekhôngxóacashcanonical đãđượcnguồnkhácchứngminh. |
| Commission | Preview→Earned→Approved→Payable→Paid (policy có thểđảo thứtự Earned/Approved nhưngguard phảiđượcversion) | Earned theoeligibleallocation/policy;Approved đúngauthority;Payable đủrelease/period;Paid cópayoutconfirmed;partialpayout hiệnpaidamount+remaining, khôngmarkPaidtoànbộ;refund tạoReverse/Adjustment độc lập, khôngghiđèPaidgốc. |

> Mỗi transition phải có test hợp lệ/tráiphép/replay/concurrent và mappingstatusnative trướcfeatureactivation. Đây làbaseline đềxuất cầnchủnghiệpvụ duyệt, không được giảlàpolicyđãxácnhận. Tax/legaltrigger vẫn theo6.3 vàcăn cứ đãduyệt.

Test W-U03: PATCHstatus trực tiếp bịchặn; hai accept/convert cùngversion chỉmộtlogicaleffect;BlockedProject khônglùideadlinecontract;Dealreopen khôngsinhProject/cashlại;OrderCompleted chưaPaidvẫnbáocôngnợ.

## W04 — Major — Logical idempotency keys của conversion/SLA chưa được định danh

Căn cứ:FR04/UC03 yêu cầuconversionidempotent;5.5lead_id khôngcó logicaluniqueness/cardinality;5.16 SLA_Episodes cówaiting_episode_key nhưngkhôngdeclaredunique;textoutbox/eventidempotency lànguyêntắcchung, khôngđịnhnghĩa conversion/episode businesskey.5.19/9.11 đãgateDDL nhưngchưađủlogiccardinality nếudev tựđoán.

Phảnvídụ: eventA vàB kháctransportID cùngrequest cùngstartclock, mỗiconsumer cóeventdedupđúng nhưng vẫn tạo haiFRT clock; hai browserconvertcùngLead vớicommandIDkhác có thể tạo haiDeal cho mộtconversion.

Patch thêm5.5/5.16:

> Conversion operation có stable conversion_key theo tenant/workspace/lead/demand và commercialintent do server xác định, không chỉtheoHTTPrequest. Concurrentconvert cùnglogicalintent trảcùngDeal/resultmapping. Khi một nhu cầu có nhiều cơhội thật, mỗiopportunity_intent_key riêngcóevidence/actor; khôngUNIQUElead_id toàncụcvì cóthểcónhiềuDealcóthậthợplệ. ConversionHistory/mapping lưuoperationkey,resultrefs,policy,actor; converted_at vàleadstatus chỉcommit sau resultrefs thànhcông.
>
> SLA_Episodes unique logicalkey(tenant_id,workspace_id,business_subject_id,waiting_episode_key,clock_type). waiting_episode_key lấy từcanonical unansweredturn/request/lifecycleevent theo policy, không dùngIDworkerattempt hayreceived_at. Clock mới saureopen cóepisodekeymới liênkếtprior_episode_id và carryover/breachhistorytheopolicy; reassign/duplicateevent khôngđổi key. Cóthểmultipleclock độc lập nhưngkhônghaiFRT cùngepisode. Constraint/indexphysical hoặc equivalentplatform invariant phải đượcchứngminhtrướcbật.

Test W-U04:haieventID khácnhau cùnglogicalrequest→mộtFRT;haiconvertHTTPkeykhác cùngintent→mộtDeal;nhucầucóhaiopportunityintentđượcduyệt→haiDealhợplệ;reassignkhôngthêmclock;reopenclockmớiliênkếtclockcũ.

## Minor/biên tập, không là Blocker

- U19 dòng1893 nhãnP1 trongkhiFR23P0nếucócampaign. Sửa “P0 khi launch campaign được bật; N/A nếu ngoài scope; phần mởrộngP1 theofeature”. TươngtựU23P2 đangbaogồmreferralP1:đổi “theogiaiđoạnreferralP1/pointsP2đãbật”. TránhđọcnhãnUATthànhquyềnhoãncontrol.
- A.3 dòng2227 ghi “phạmvi/field/giaiđoạn hiện hành...phiênbản1.3” dùMaster1.4;A.5 nói16luồnglàdiễnbiếnbảncũ.Đánhnhãn “lịch sửhợpnhất”hoặcsửaversionhiệnhành. Khôngảnhhưởngruntime.

## Những điểm không báo lỗi sau kiểm tra toàn văn

Đã có rule: refund dư/reservation vàunknown; quoteexpiry tạiAPI;reopenkhôngreset; crossworkspacegrant/constrainttrigger;noinvoiceallocation; productionPendingPolicy;calendarcoreP0khácconnectorP1;P0controlscondfeature;deletion/suppressionrestore. ChưacóDDLhayprovideraccounttestlàgiớihạnreadiness đãcôngbố,không phải tựđộng chứngminhcontradiction.

Kếtluận: tiếp tục thiết kế/PoC cóđiềukiện, chưa cơ sởproduction sign-off. BốnMajornàylà phần cầncụthểhóa trướcfreezeAPI/DDL, khônglà tỷlệsailỗitoànMaster.

## W05 — Major — Thiếu release profile để hợp nhất nhãn test và phạm vi điều kiện

Căn cứ: 9.5 nói toàn bộ P0 phải pass; U19 gắn P1 dù FR23 là P0 nếu quản campaign; U23 gắn P2 nhưng referral thuộc P1; U20 spend gắn P0 dù connector spend P1; CEO-U21 resource booking gắn P0 trong khi 5.19 cho hoãn nếu chưa quản ekip. Master đã nêu feature applicability rải rác ở 5.19, 9.10, 9.12, 9.13, nên đây không phải hoàn toàn thiếu nguyên tắc conditional gate. Khoảng trống là chưa có một phép quyết định áp dụng đủ cụ thể để QA phân biệt Not Run, Not Applicable và Deferred. Sai nhãn có thể gây hoãn control cần thiết hoặc buộc xây feature chưa bật.

Patch thay đoạn mở đầu 9.5 và thêm vào 9.11:

> Mỗi release có Release_Acceptance_Profile versioned, người chịu trách nhiệm và ngày phê duyệt; ghi capability/FR đã bật, phần control bắt buộc, feature/provider/luồng tiền liên quan, owner, dữ liệu thử và mapping tới test. Test có ba thuộc tính riêng: test_severity (mức hậu quả nếu sai), delivery_priority (giai đoạn đưa capability vào sản phẩm) và applicability_expression (điều kiện test có hiệu lực). Nhãn P0/P1/P2 cũ là gợi ý giai đoạn, không thay thế biểu thức áp dụng.
>
> Mọi test control về tiền, quyền, consent, gửi đúng người, SLA và phục hồi của capability đang bật phải Pass trước go-live. Test có biểu thức áp dụng False được ghi Not Applicable kèm bằng chứng feature bị tắt và không có đường API/job/role sử dụng capability đó; không được ghi Pass. Test áp dụng True nhưng chưa chạy là Not Run, chưa đủ điều kiện ký. Deferred chỉ được dùng cho capability chưa bật với dependency closure chứng minh; không được defer control của một capability đã bật. QA và business owner ký release profile cùng actual/evidence; acceptance không suy từ số test hoặc tỷ lệ phần trăm tổng.

| Test/nhóm | Applicability và gate sau sửa |
| --- | --- |
| U19, M11 và gate approval/launch | P0 control khi có launch hoặc publish campaign/asset cần approval; N/A nếu chưa bật hành vi đó. Giai đoạn feature mở rộng không hạ mức control. |
| U23 | Khi referral đã bật ở P1 thì thử reversal reward referral; khi loyalty points bật ở P2 thì thử reversal points. Hai trường hợp tách test ID/fixture, không ép điểm P2 vào referral. |
| U20, M25 | Khi nhập/sync/report spend, thử thiếu dữ liệu và freshness cho nguồn đang dùng. Không có API connector vẫn có thể thử manual import; nếu không sử dụng spend thì N/A có evidence feature off. |
| CEO-U21, RV04 | Khi quản tài nguyên độc quyền/reservation thì control concurrency là P0. Nếu chỉ tích hợp lịch cá nhân không có resource booking, N/A cho exclusion/pool test và chạy test lịch/hủy reminder thuộc FR20 đang bật. |
| U11/U12 và các test commission | Receipt/allocation control theo phần cash đã bật; commission/payout/refund test áp dụng khi luồng tương ứng được bật. Không bật payout nếu chưa kiểm adjustment/payout control. |
| U22, INT27–28, OC20 | Guard bắt buộc trước bật AI; model/STT eval N/A khi AI off. Kiểm AI off không còn đường tool/retrieval mở ngoài ý muốn. |

Test W-U05: lập profile release chỉ có cash thủ công + một inbox, không AI/spend/ekip/points; QA xác định control bắt buộc của feature đang chạy, các N/A có evidence. Bật launch hoặc referral phải tự làm test tương ứng Applicable trước activation, không dựa nhãn U19P1/U23P2 cũ để bỏ test.
