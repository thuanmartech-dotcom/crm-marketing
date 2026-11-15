<a id="phu-luc-g"></a>

## PHỤ LỤC G KIỂM ĐỊNH CHỐT CHẶN SRS THEO SÁU TRỤC

**Đối tượng kiểm định:** phần thân và các phụ lục A–F của Master 1.4, trước khi thêm phụ lục này. Lưu bản đối chiếu bất biến tại `docs/archive/research-2026-10-15/CRM_MASTER_BRD_SRS_HOP_NHAT_v1.4.md`. Dòng được dẫn trong báo cáo là dòng của snapshot 1.4; mã mục và tên trường là định vị chính khi tài liệu được chỉnh tiếp.

**Phán quyết:** Conditional Go cho discovery, prototype, lựa chọn nền tảng và phát triển từng lát cắt đã đủ đặc tả; **No-Go đối với đóng băng toàn bộ SRS để đội dev chỉ việc code**, cũng như chưa có căn cứ ký nghiệm thu vận hành. Điểm đánh giá tài liệu và bản vá nằm ở Phần 6. Không có kết luận “Final 100%” chỉ từ đọc tài liệu.

Yêu cầu kiểm định là nội dung trong tệp người dùng dán `Pasted text.txt`. Ba nhánh agent rà soát song song tài chính/schema, nghiệp vụ/truy vết, bảo mật/quyền/chính sách; agent tổng hợp đối chiếu lại với Master và nguồn chính thức. Đây là bốn góc chuyên môn phân tích, không phải chứng thư của một hội đồng hành nghề độc lập hoặc bằng chứng về 15 năm kinh nghiệm cá nhân.

**Căn cứ được phân cấp:** (a) mâu thuẫn có thể chỉ ra giữa hai vị trí SRS; (b) thiếu hợp đồng hành vi/dữ liệu có tình huống chứng minh dev phải tự quyết; (c) tài liệu chính thức chứng minh tính chất nền tảng/pháp luật; (d) giải pháp thiết kế đề xuất của dự án. Nguồn (c) không tự chứng minh cách triển khai (d) đã đúng. Không phát hiện một trường trong bảng rút gọn chưa đủ để kết luận thiếu: phải tìm toàn văn và xét quy tắc 5.1/5.18/5.19 trước.

**Giới hạn:** chưa có code ứng dụng, DDL thực thi, build, cấu hình tenant, sandbox API, hợp đồng thực tế hay kết quả UAT để kiểm chứng. Các kịch bản dưới là phản ví dụ ở cấp đặc tả và ca cần chạy; không gán thành lỗi đã tái hiện trên phần mềm. Nguồn được kiểm tra ngày 15/10/2026; điều kiện tài khoản/API và áp dụng pháp luật vẫn phải được đối chiếu khi triển khai.

### G.1 PHẦN 1 — ĐỒNG BỘ CHÉO VÀ HỒI QUY

Phần 1.4 đã xử lý những lỗi cũ sau; không tính lại thành phát hiện mới: API allocate theo nghĩa vụ ở 2.5/5.11; Deal OnHold tách stage ở 5.5; Contracts có effective/notice ở 5.13; lịch hẹn/booking ở 5.18; qualifying interaction ở 5.16; Business_Subjects có sáu FK typed ở 5.18; ma trận B đã bổ sung FR30–40; U22 có guard P0 có điều kiện. Những dòng này cho thấy phản biện HTML cũ không thể dùng như mô tả nguyên trạng Master 1.4.

| Điểm giao | Căn cứ trong snapshot 1.4 | Tình huống làm lộ khoảng trống | Nhóm phát hiện / bản vá |
| --- | --- | --- | --- |
| Intake ↔ qualification ↔ schema | 4.1/4.3; 5.2 `Leads.business_model` dòng 1301 | Form chỉ để lại tên/số liên hệ; chưa biết mua cá nhân hay doanh nghiệp nhưng schema bắt B2B/B2C trước qualification | WF01 |
| FR36/39 ↔ send API ↔ schema ↔ UAT | 3.12.7/3.12.10; 5.16 `Messages`, `SLA_Episodes`; 5.17 send; INT04/CX-U05/CX-U23 | Cùng thread hỏi giá và khiếu nại; chưa có quan hệ định danh phản hồi hoàn thành episode nào | WF02 |
| Lifecycle ↔ dictionary | 3.2.1/3.6/3.7/3.12; 5.13 nhiều cột `status` không có transition đầy đủ | Hai dev có thể cho hai đường reopen/terminate/accept khác nhau mà đều viện dẫn được mô tả hiện tại | WF03 |
| FK ↔ tên thực thể chuẩn | 5.5 dòng 1357/1368 so với 5.13/5.18 | `PipelineStages` không trùng `Pipeline_Stages`; `CommissionPolicies` chưa có dictionary hoặc alias được công bố | DB01 |
| Refund ↔ case hoàn dư | 4.13 dòng 1118 so với 3.13.4 dòng 944 | Hoàn tiền chưa allocate vẫn bị luồng chính yêu cầu reversal allocation và commission negative | DB02 |
| Khóa kỳ ↔ posting ↔ UAT | 5.12/5.13 `period_id`, `Finance_Periods`; U12/CEO-U23 | Giao dịch đọc kỳ còn mở, giao dịch khác đóng kỳ, rồi giao dịch thứ nhất commit bút toán vào kỳ đã khóa | DB03 |
| Permission revoke ↔ đường tải file | 3.12.8, 4.12, 5.16, 6.2; U16/INT23 | Link storage ký bởi service credential có thể còn dùng được dù quyền CRM của người giữ link đã bị thu hồi | SEC03 |
| Priority ↔ gate | 3.9.2 FR23; 3.4.2 FR10; 5.19; 9.5/9.12 | U19 P1 dù launch gate có thể là P0; U23 P2 dù referral là P1; test resource P0 trong lúc capability có thể chưa bật | WF04 |

Không có căn cứ khẳng định mọi bảng P1/P2 là ghost reference hoặc phải tạo trong P0: 5.19 đã cho phép capability mapping, nullable reference và feature-off hợp lệ. Lỗi còn lại là thiếu manifest triển khai cụ thể để chứng minh dependency closure, không phải số lượng bảng quá nhiều tự nó là lỗi. `client_workspace_id` được 5.1 xác định là tên migration lịch sử; không kết luận đây là cột hiện hành bị bỏ sót.

Ma trận B hiện bao phủ các nhóm FR nhưng chưa chứng minh từng hành vi P0 có test và dữ liệu định lượng riêng. Ví dụ U01 chỉ chứng minh transport dedup, không chứng minh toàn bộ identity/consent/qualification; U14 chưa phân biệt từng clock và tất cả cạnh reopen. Bản vá WF02–WF04 và DB02–DB03 bổ sung ca cho đúng các hành vi thiếu. Test được mô tả chưa là bằng chứng pass; số lượng test không dùng thay coverage.

### G.2 PHẦN 2 — TRẠNG THÁI VÀ ĐIỀU KIỆN BIÊN

| Đối tượng | Phần đã có căn cứ trong SRS | Điểm chưa đủ để đóng băng | Kết quả phải giữ khi vá |
| --- | --- | --- | --- |
| Lead | FR04/05, UC01–03, 5.2 có tám trạng thái, queue và lịch sử | Chưa đủ bảng from/event/guard/to cho Nurture, Dormant, Recycled và conversion; business model chưa biết bị ép lựa chọn | WF01/WF03: giữ nhu cầu và lịch sử; quay lại theo cùng nhu cầu không xóa breach/cohort |
| Deal | 3.2.1/5.5 có stage + Open/Won/Lost + Active/OnHold | Reopen Lost và sửa sai Won chưa có command/authority/side-effect đủ rõ | WF03: không đưa Won đang có hợp đồng thành Open chỉ bằng sửa stage; OnHold không xóa total age |
| Quote | 3.6.1, UC05, 5.13 có version/expiry và acceptance | Chưa tách đủ retry/status event với thay đổi nội dung; cần đường từ Rejected/Expired tới revision mới thay vì sửa bản cũ | WF03: approval gắn revision, accepted_at và evidence; cron không lật Accepted thành Expired |
| Contract | FR15/5.13 có hiệu lực/notice/termination | Cột `status` chưa liệt kê và khóa các đường amend/suspend/terminate/settlement | WF03: không đồng nhất signed, effective, start authorized và settled |
| Order | 5.6 có sáu status và payment_state riêng | Điều kiện Confirmed/InDelivery/Completed/Terminated và quan hệ nhiều deliverable chưa thành transition contract | WF03/DB02: Complete không tự Paid; cancellation không xóa nghĩa vụ đã phát sinh |
| Project/Deliverable | FR15/25/UC08 có handoff/QA/acceptance/defect | Các cột status và đường reject/rework/client-wait/acceptance còn gộp trong dictionary | WF03: acceptance đúng phiên bản, không im lặng thành duyệt nếu không có điều khoản hợp lệ |
| Payment | FR16/5.10 đã tách verification/matching/allocation/reconciliation | Refund reserved/unknown/confirmed với tiền đã allocate chưa có hợp đồng đủ chi tiết cho hai giao dịch cạnh tranh | DB02: không vừa refund vừa tái dùng tiền, không tạo cash/commission giả |
| Commission | FR17/5.12 có lifecycle và payout tách | Chưa có transition table đầy đủ; close-period race và adjustment sau payout còn thiếu hợp đồng | WF03/DB03: tiền append-only, workflow projection, payout không bị xóa hồi tố |
| Ticket | FR18/5.8 có WaitingCustomer/Resolved/Closed, reopen giữ lịch sử | No-response, duplicate, technical resolution và reopen theo episode cần command/guard/clock riêng | WF03/WF02: không dùng closed để ngừng nghĩa vụ pháp lý hay request còn mở |
| Conversation | 3.12 tách status/waiting_party/assignment | Nhiều request trong một thread chưa gắn reply với đúng request/clock | WF02/WF03: resolved thread không tự resolve ticket; tab cũ không gửi sau reassignment |

**Các đồng hồ phải được kiểm riêng:** nhận việc, nỗ lực đầu, FRT, NRT, resolution, duyệt đầu ra và promised update. 3.13.4 đã xác định promise tuyệt đối dùng WallClock, còn clock khác theo policy/calendar; không nhận xét rằng mọi clock đang bị ép giờ hành chính. Start cần event/subject/episode; Pause cần lý do và quyền cho clock cho phép; Resume giữ thời gian đã tiêu; Cancel cần outcome; Reset chỉ cho episode mới hợp lệ, không do chuyển owner/khách gửi thêm tin/agent đổi status. Bản vá WF02/WF03 ràng buộc rõ đường này.

Các ca lách phải thử: lời chào rỗng dừng SLA; chọn WaitingCustomer khi còn việc nội bộ; tạo send intent liên tục giữ assignment; close/reopen để xóa breach; thay priority sau quá hạn; trả lời hỏi giá để dừng đồng hồ khiếu nại; backdate activity; dùng native reply không có echo để tự tuyên bố đã hoàn thành. 1.4 đã cấm phần lớn về nguyên tắc, nhưng vẫn cần completion evidence và transition contract để kỹ sư/QA kiểm nhất quán. Không thể chứng minh “kín 100%” nếu chưa thực thi model và fault tests.

### G.3 PHẦN 3 — DỮ LIỆU, TIỀN VÀ ĐỒNG THỜI

**Các ràng buộc đã hợp lý:** Contact phone/email non-unique; provisional Contact trước nghiệp vụ yêu cầu FK; canonical receipt có nhiều evidence; allocation trỏ obligation thay invoice; order_no không tái dùng khi archive; Business_Subjects đúng một FK typed; cross-workspace có bridge được cấp phép. Không lặp lại khuyến nghị bỏ NOT NULL/UNIQUE một cách đại trà. `NN` hợp lệ hay không phụ thuộc thời điểm promote bản ghi và nghiệp vụ của trường.

| Bất biến | Đặc tả đang có / tình huống cần kiểm | Kết luận |
| --- | --- | --- |
| SERVICE/PRODUCTION/MEDIA và VAT | 3.6.1/3.6.4/5.11: loại phí khác cấu phần tax; components tổng bằng allocation; production pending nếu chưa policy | Định hướng đúng; DB04 làm rõ dấu reversal/caps/currency scale khi hiện thực ledger |
| Thu thiếu | 3.13.4: phí ngân hàng có evidence khác thiếu tiền, discount, write-off | Không auto xóa nợ theo ngưỡng; khoản cash-based commission không tăng bởi write-off; cần policy thực tế trước bật |
| Thu thừa | 3.13.4/5.18: credit và refund reservation | DB02 cần tách hoàn dư khỏi hoàn phần đã allocate và khóa đồng thời các balance liên quan |
| Thu gộp nhiều kỳ/loại phí | 3.6.3/5.11: theo điều khoản, Finance-confirmed instructions, fallback được duyệt | Không mặc định pro-rata hoặc MEDIA_FIRST; giữ cap từng obligation, tax/net và đúng người mua/pháp nhân |
| Refund sau khóa kỳ | 4.13/5.12: adjustment kỳ sau, link bút toán gốc | DB03 cần định nghĩa kỳ theo miền/scope và tuần tự hóa close/post; không sửa ngày ngân hàng để ép vào kỳ mở |
| Hai người allocate/merge/claim | 2.5/3.13.4/5.14 có lock/CAS/idempotency | Có nguyên tắc; DB02/DB03/WF02 cụ thể hóa điểm còn thiếu. Chưa có bằng chứng runtime cho deadlock/race |
| Webhook lặp/lệch thứ tự | 2.7/FR33/5.16 có receipt guard/reducer/history | SEC01 cần khóa ownership namespace ngoài để không tạo hai connection độc lập nhận cùng business event |

PostgreSQL xác nhận CHECK đọc hàng khác không bảo đảm toàn vẹn liên tục, khóa phải nhất quán và transaction có thể bị abort/retry. Vì vậy các tổng balance/share/mapping không chỉ là CHECK có subquery; cần giao dịch/constraint và test lịch xen kẽ cụ thể. [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html). Đây là căn cứ về cơ chế DB, không phải kết quả chạy schema CRM.

### G.4 PHẦN 4 — BẢO MẬT, PHÂN QUYỀN VÀ TUÂN THỦ

6.1 đã trao AM quyền renewal/upsell có điều kiện, Delivery quyền brief/SOW/acceptance và Finance quyền commands thay CRUD sổ tiền. Như vậy không còn đúng nếu nói AM không thể thực hiện UC10 hoặc Finance chỉ được xem. Cần PoC permission thực, nhất là platform gộp quyền rộng hơn Deny-wins của dự án. Pilot một người có thể kiêm vai nhưng vẫn phải ghi vai nghiệp vụ và quyết định; không dựng người phê duyệt thứ hai giả.

| Đường rủi ro | Điểm cụ thể cần khóa | Phát hiện / phạm vi |
| --- | --- | --- |
| Cùng OA/Page/mailbox ở nhiều workspace | 5.16 unique connection chỉ gồm tenant/workspace/provider/account, chưa xác định external namespace owner/routing | SEC01, P0 cho connector được bật |
| OAuth cấp quyền nhầm scope | 2.6/2.7 chưa ràng buộc callback với người khởi tạo, tenant/workspace, provider và account đã kiểm | SEC02, P0 khi dùng OAuth |
| Tệp sau revoke | 4.12/6.2: cấp URL đã kiểm ACL không đủ để chặn URL còn hạn sau revoke CRM | SEC03, P0 cho tệp cần quyền hiện thời |
| Worker tải URL ngoài | FR40/2.7/5.16 chỉ nêu scan/MIME, thiếu hợp đồng egress/SSRF trước fetch | SEC04, P0 nếu hệ thống tự fetch attachment/URL |
| Email marketing | 3.4.1/6.5 chưa mô tả adapter unsubscribe/bounce/complaint và sender setup | SEC05, trước bật email quảng cáo; thư phục vụ yêu cầu/hợp đồng xét purpose riêng |
| Search/BI/AI/merge | 3.1.2/3.12.8/6.1/6.3 đã có ACL/provenance/revoke/current policy | Giữ kiểm tra âm hiện có; không suy prompt/RLS tự bảo vệ tất cả kho ngoài SQL |

Đối chiếu nguồn: OAuth phải chống CSRF và trộn authorization server; storage presigned URL là bearer token; tải URL bên ngoài cần kiểm soát SSRF. Các nguồn giải thích vì sao SEC02–04 là yêu cầu cần có, không chứng minh đã xảy ra khai thác. [RFC9700 §2.1/§4.7](https://www.rfc-editor.org/rfc/rfc9700.html), [AWS presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html), [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

**Pháp lý Việt Nam:** 6.3/F.5 đã bỏ DSAR “72 giờ từ verified_at”, tách request/incident và giữ hạn theo loại nghĩa vụ. Đây là hướng đúng. Không có chứng cứ từ việc đọc SRS để kết luận doanh nghiệp đã tuân thủ đầy đủ Luật91/NĐ356: còn chưa biết vai trò kiểm soát/xử lý, mục đích, khách hàng ủy quyền, vendor/region, hợp đồng và hồ sơ áp dụng. F.5 chỉ tóm tắt; khi cấu hình phải chép đủ nhánh Điều5, mốc nhận yêu cầu đúng thủ tục, response/action/extension và các trường hợp bên xử lý, không dùng đoạn tóm tắt làm bảng luật duy nhất. [Nghị định356 bản Công báo, Điều5/42](https://congbao.cdnchinhphu.vn/180507251028987904/2026/1/17/356signed-1768638052103952849513.pdf).

**Năm kênh:** Zalo/Meta phải dùng policy theo account, message class và qualifying event; TikTok DM khác Lead Gen/Shop và chưa xác minh quyền của tài khoản dự án; Web Form không tự có consent marketing hoặc email verified; Email cần đủ mailbox scope và luồng unsubscribe nếu gửi quảng cáo. Không thấy trong 1.4 một cam kết hiện hành cho phép chung 24h cả Meta/Zalo, hoặc lấy API TikTok Shop làm DM. Phần đúng này không cần vá ngược lại. Chưa có sandbox nên capability vẫn pending cho tới khi có evidence.

### G.5 PHẦN 5 — SẴN SÀNG LẬP TRÌNH VÀ PHẠM VI MVP

Không phải mọi câu định tính đều cần một con số. “Phản hồi thực chất” cần taxonomy/evidence và QA; “có thẩm quyền” cần grant/authority; “privacy phù hợp” cần căn cứ áp dụng. Gán ngẫu nhiên 15 phút, 60 ngày hay 5% chỉ đổi điểm mờ thành quyết định kinh doanh chưa được phê duyệt. Cách chốt là policy contract có owner/version, dữ liệu đầu vào, if–else, outcome, fallback và activation gate.

| Vị trí / đối tượng | Quyết định còn cần xác định | Hệ quả mặc định an toàn trước khi chốt |
| --- | --- | --- |
| 3.1.1/3.1.2, Contact_Points/identity | Quốc gia chuẩn hóa, evidence verified, xung đột và auto-link rule | Candidate review; không tự merge/gửi thêm kênh |
| 3.2.1/4.3, qualification | Fields theo gói/B2B/B2C, MQL/SAL/SQL và no-fit taxonomy | Intake Unknown; chưa auto qualify hoặc tính score như xác suất |
| 3.2.2/5.16, routing/timers | Ca/nghỉ, capacity mềm/cứng, target từng clock, claim/response evidence, warning/escalation/grace | Policy Draft chặn bật router/SLA tự động; tác vụ thủ công có owner vẫn vận hành |
| 3.6.1/4.5, approval | Cost basis, discount/margin/payment terms, authority/cap/expiry, dependency invalidation | Không coi draft là offer được duyệt; không autoapprove vì discount=0 |
| 3.6.2/3.9.2, start/media | Điều kiện kickoff, ngoại lệ, asset/capacity, funding cap, stale-spend và emergency authority | Chặn đúng phần công việc/chi chưa đủ điều kiện; không chặn intake |
| 3.6.3/3.13.4/5.11, money | Buyer/payer match, tolerance, waterfall, tax/net, refund/adjustment reasons, minor units | Giữ unallocated/pending case; không tự đoán phí hoặc loại phí |
| 3.6.4/5.12, commission | Eligible line basis/rate/share/pool, earned/payable, quality fallback, true-up và payout authority | PendingPolicy/preview; không chi thật khi thiếu policy |
| 3.7.1/4.9, service | Severity matrix, entitlement, pause/resume/no-response/reopen window, substantive reply rubric | Intake vẫn nhận, triage và containment thủ công; không tự xóa breach |
| 3.7.2, survey/recovery | Eligibility, cooldown, suppression khi incident, low-score route/owner/due, closure evidence | Recovery ghi tay được; survey automation chưa bật |
| 3.8.1/5.18, booking | Resource độc quyền/pool, hold TTL, ca/timezone, reminders | Lịch cá nhân đơn giản; reservation chưa bật nếu không quản ekip |
| 3.9–3.10, scope/delivery | SOW template, revision quota/defect, optimization envelope, cost source, task master | Brief/SOW/milestone tối thiểu; không bắt editor/strategy/capacity engine |
| 3.11/8.2/8.3, KPI | Tập metric P0, source/time/grain/currency, zero denominator, forecast stage probabilities | Không đủ dữ liệu → N/A/Unknown; hiện số tuyệt đối và nguồn, không dự báo AI giả |
| 8.2, health | Direction/window/sample/freshness/weights/risk flags và action owner | Vector bằng chứng; score không tự xanh hoặc tự upsell |
| 2.7/5.16, connectors | Account capabilities/API version/history/window/quota/backfill/delete/echo | Chỉ một kênh đủ quyền; capability chưa test không hứa parity |
| 6.1/6.2, access | Field/action/resource grants, break-glass TTL, session policy, file route | Deny thiếu context; không expose URL storage như quyền vĩnh viễn |
| 6.3/6.4, privacy | Controller/processor mapping, legal deadline branch, retention/legal hold, vendor và cross-border obligations | Không bật luồng dữ liệu chưa có căn cứ; request queue/owner và chặn marketing hợp lệ vẫn có ngay |
| 7.1/7.6, NFR | Shape/roles/dataset, thiết bị/RTT, measurement window, error budget, backup profile | Mục tiêu được gắn test profile; không trình bày như kết quả benchmark |
| 9.1/9.8/10.3/10.6, release | Một hay 2–3 kênh, feature flags, nguồn lực, external approvals, chi phí và P0 applicability | Pilot một nguồn/một kênh theo 1.6; mở rộng phải qua manifest WF04 |

Bảng này thống kê các nhóm quyết định trong baseline hiện có; khi triển khai cần một bản ghi typed cho từng policy, không dùng một ô bảng để thay toàn bộ cấu hình. A.6 đã công khai nhiều dữ kiện chưa biết; đây là gate kích hoạt theo module, không phải mọi câu cần hỏi lại người dùng ngay trong vòng audit.

MVP phù hợp khối lượng đã nêu: hồ sơ/nhu cầu → owner/next action → quote/SOW → hợp đồng/nghĩa vụ → đối soát thủ công có kiểm soát → handoff/đầu ra/nghiệm thu → ticket/recovery/nhắc review. Một nguồn và một kênh; ưu tiên CRM có sẵn cấu hình/hybrid nếu PoC đáp ứng. Chưa có dữ liệu chứng minh phải tự xây tất cả, phải có 81 bảng, hoặc phải dùng Chatwoot. P0 luôn cần scope/quyền/consent/audit/backup; engine survey/AI/score/referral/đa kênh/ERP tự động mở sau theo dependency closure. WF04 chặn tính năng phụ thuộc P1 chưa bật mà vẫn coi P0 đã hoàn chỉnh.

