# Thẩm định CMO: CRM cho agency marketing B2B/B2C

Ngày nghiên cứu: 15/10/2026, Asia/Saigon. Phạm vi: FR03, FR09–10, FR22–29; phần giao nhau với lead, hợp đồng, tài chính, CX và tích hợp Meta. Đây là thẩm định đặc tả, chưa phải kiểm thử sản phẩm.

## 1. Kết luận điều hành

Thiết kế có nền tảng đúng: tách B2B/B2C, agency/client, media thu hộ/phí dịch vụ, attribution/nhân quả, task/capacity, phê duyệt theo version. Không nên xóa toàn bộ phần strategy/IMC vì nó kiểm soát điều agency đã hứa, đã được khách duyệt và thực sự giao. Tuy nhiên, nhiều FR mới dừng ở mô tả nguyên tắc; chưa đủ để hai đội kỹ thuật độc lập xây ra cùng một hành vi và báo cáo.

Những điểm cần sửa trước khi giao triển khai:

1. **Tách vòng đời khách hàng, từng nhu cầu mua và từng deal.** Contact có thể đã là khách nhưng đang có nhu cầu mua mới; MQL không được ghi đè quan hệ khách hàng. Ghi các lần bàn giao Marketing→Sales và lý do nhận/từ chối/trả về.
2. **RFM thanh toán không phải health score.** Khách trả trước năm có R cao nhưng không phải mất gắn kết. Ngày thanh toán, kỳ dịch vụ, hạn thanh toán, tình trạng delivery và sức khỏe quan hệ phải là các tín hiệu riêng.
3. **Unknown khác Direct.** Không có UTM vì lỗi tracking hoặc vì chưa biết nguồn không được biến thành kênh Direct. First/last touch phải gắn outcome và model version; không lấy một trường source hiện tại trên contact làm lịch sử đầy đủ.
4. **Tách bốn tập tiền:** chi phí tìm khách của agency, phí agency được hưởng, ngân sách truyền thông của khách, kết quả doanh thu của khách. Chỉ nối bằng scope và hợp đồng; không cộng các tập này để tạo CAC/ROAS đẹp.
5. **Đóng vòng chất lượng lead với nền tảng quảng cáo**, nhưng qua bộ xuất dữ liệu có quyền, mapping và chống trùng. Có CRM nhập lead chưa đồng nghĩa đã phản hồi chất lượng về Meta.
6. **Thiết kế tối thiểu nhưng đủ bằng chứng:** brief/SOW, budget, asset version, approval, deliverable, acceptance, outcome. Hoãn editor strategy đầy đủ, MTA, loyalty điểm và xếp hạng nhân sự.

Các đề xuất sau là suy luận thiết kế áp dụng cho quy mô tài liệu, không phải tuyên bố mọi CRM trên thị trường hoặc mọi agency bắt buộc dùng cùng workflow.

## 2. Phương pháp và độ chắc chắn

Đã đọc và đối chiếu các mục 1.4–1.6, 3.1–3.4, 3.9–3.11, 8.1–8.3, mapping/UAT liên quan trong `CRM_MASTER_BRD_SRS_HOP_NHAT.md`, cùng phần phản biện trong `PHAN_TICH_PHAN_BIEN_CRM_2026-10-15.md`. Không sửa hai tài liệu này.

Nhãn bằng chứng: **D** = nội dung tài liệu gốc đã đọc; **W** = nội dung chính thức được công cụ web trả về; **C** = đọc trực tiếp phần code GitHub; **S** = search snippet, chưa mở đủ; **I** = kết luận/suy luận thiết kế của người thẩm định. Không dùng số sao GitHub, số người trong group hoặc tuyên bố quảng cáo làm chứng minh phù hợp nghiệp vụ.

## 3. Ma trận chức năng: phải có để làm quyết định gì, nối với đâu

| FR / kết luận | Vì sao cần và quyết định phục vụ | Liên kết bắt buộc | Thiếu gì / sửa như thế nào | Ưu tiên |
| --- | --- | --- | --- | --- |
| FR03 — Giữ phân nhóm, sửa tên và logic | AM biết ai cần onboarding, review, xử lý nợ hay tái kích hoạt. CMO biết tập đủ điều kiện nhận chiến dịch | FR01/02 danh tính; FR15 hợp đồng/bàn giao; FR16 tiền; kỳ dịch vụ; FR18 ticket; FR19 CSAT/NPS; FR09 suppression | RFM chỉ là lát cắt giao dịch. Tách `payment_recency`, `service_period_count`, `net_service_cash`, `payment_overdue`, `engagement_recency`, `delivery_risk`. Segment có thể đồng thời nhiều nhãn; quy tắc ưu tiên hành động rõ | P0 segment thủ công/có giải thích; tự động P1 |
| FR09 — Giữ, cần orchestration chặt | Tránh bỏ follow-up nhưng không làm khách nhận dồn tin hoặc tiếp tục bán khi đang khiếu nại | Consent/purpose; identity; lead/deal/ticket; outbox; connector; activity | Frequency cap toàn tổ chức/scope, không chỉ mỗi journey. Có priority arbitration, expiry, unique effect key, suppression check sát lúc gửi, hủy khi goal đạt, manual pause, kill switch và lịch sử quyết định gửi/không gửi | P0 nhắc nội bộ và một flow; builder tổng quát P1 |
| FR10 — Tách referral khỏi loyalty | Referral đo khách giới thiệu có chất lượng; loyalty chỉ đáng làm khi tăng giữ chân đủ bù chi phí | Contact/account; new-customer rule; deal; cash allocation; refund; payout; consent | Referral eligibility/lock/dispute, nhân viên và bên liên quan, giới hạn thưởng, refund một phần, trùng người nhận tiền. Marketing credit khác quyền nhận thưởng. Không yêu cầu Mini App để referral tồn tại | Referral đơn giản P1; points/tier P2 |
| FR22 — Giữ traceability, giảm nhập liệu | CEO/CMO biết chiến dịch phục vụ mục tiêu nào; tránh làm rất nhiều nội dung nhưng không giải quyết mục tiêu hợp đồng | Brief→quote/SOW→contract→plan→deliverable→metric | Scope template theo gói. Mỗi objective có baseline, target, time horizon, owner, evidence; phân biệt chỉ tiêu cam kết với mục tiêu kỳ vọng. Lưu link và version tài liệu ngoài, không tái tạo toàn bộ slide | P0 brief/KPI/SOW gọn; editor strategy/IMC đầy đủ P2 |
| FR23 — Giữ và làm rõ approval dependency | Tránh chạy nhầm creative hoặc chi vượt tiền đã được duyệt, bảo vệ quan hệ khách hàng | FR22 scope; FR26 budget; asset version; client stakeholder role; provider connection; FR25 tasks | Approval là đối tượng có subject/version/scope/approver/cap/expiry. Thay đổi chỉ vô hiệu approval chịu tác động. Có delegated approver, reject/revise, emergency pause và phạm vi tối ưu đã cho phép | P0 |
| FR24 — Giữ nguyên tắc, hoãn tự động hóa | CMO phân biệt ý tưởng, tín hiệu quan sát và kết luận đáng dùng; không dồn tiền vào "winner" do ngẫu nhiên | FR22 hypothesis; FR26 spend; FR28 outcome; FR29 model; knowledge permissions | Đơn vị ngẫu nhiên hóa, eligible population, sample plan, contamination, minimum detectable effect nếu định lượng, test duration và decision log. Mẫu nhỏ ghi chưa kết luận, không ép tìm winner | P0 nhật ký quyết định; P2 experiment engine |
| FR25 — Giữ quản lý đầu ra; không xây PMS thứ hai | Sales biết khả năng nhận dự án; Delivery biết còn công việc nào và ai duyệt. Capacity ngăn bán quá năng lực | Order/SOW→project→deliverable→task; FR23 approval; FR26 cost; FR27 availability | Tách deliverable khách mua khỏi task nội bộ. Có planned vs actual, rework reason, client-wait, acceptance/defect/change request. One source of write; soft reservation trước ký, hard allocation sau kickoff | P0 milestone/owner/acceptance; P1 task/capacity integration |
| FR26 — Giữ, cần hai sổ quản trị | CMO quản pacing ngân sách khách; CEO quản biên đóng góp agency. Hai câu hỏi khác nhau | Client campaign/ad account; contract lines; commitments; actual cost; timesheet; supplier; FX; FR28 | `budget_owner`, `funding_source`, `cost_bearer`, `pass_through`, currency, tax basis, service period. Distinguish spent/accrued/paid, commitments/estimate-to-complete; không cộng dự phòng hai lần | P0 nếu triển khai media/delivery; tự động spend P1 |
| FR27 — Thu gọn | Quản lý phân người và tính cost rate, không biến CRM thành HRM | User/team/membership; availability; skill; task; rate effective date | Trọng số 25/30/20/25 là giả định, chưa có bằng chứng thích hợp mọi vai trò. Lưu cost rate theo thời điểm, hạn quyền; không lấy impact campaign cá nhân làm quan hệ nhân quả | P0 membership; P1 capacity/cost; P2 scorecard nếu có nhu cầu |
| FR28 — Giữ, P0 thực sự | Không có định nghĩa thống nhất thì dashboard dẫn đến phân ngân sách sai; đây là điều kiện của đo lường, không phải việc BI làm sau | Mọi FR tạo event/outcome, source contract, branch/workspace, time/currency, financial close | Event schema + metric contract; data owner, freshness SLA, late event policy, exclusions version, validation. MQL/SAL/SQL hiện chỉ được nhắc, cần chuyển thành state transition cụ thể | P0 cho bộ metric nhỏ |
| FR29 — Giữ attribution đơn giản, sửa scope | CMO biết khách đến từ đâu và kênh nào góp phần; không trả thưởng hoặc cắt kênh dựa số không đối soát | Touchpoint→identity→demand/deal→outcome→cash/recognition; campaign/spend; refunds; FR28 | Model-specific credits, eligible touch window, Direct/Unknown riêng, event/processing time, frozen snapshot/restate, unassigned identity, refunds. Account-level association có thời hạn; không tự chia mọi doanh thu account cho mọi contact | P0 nguồn và first/last báo cáo riêng; P2 MTA |

Các lý do và giải pháp trong bảng là **I**, dựa trên khoảng trống **D**, không phải toàn bộ đều được nhà cung cấp nào xác nhận. Nguồn chính thức bên dưới chứng minh các pattern có thật, không chứng minh phần mềm đã thỏa toàn bộ yêu cầu này.

## 4. Các vấn đề nghiệp vụ cần đặc tả lại

### 4.1 Vòng đời quan hệ khác vòng đời nhu cầu

SRS nhắc MQL→SAL→SQL trong dashboard nhưng pipeline FR04 chỉ có New/Contacting/Qualified... Chưa định nghĩa mapping, owner và timestamp. Đây là chỗ Marketing có thể gọi lead tốt còn Sales gọi lead rác, trong khi hai bên dùng hai mẫu số khác nhau.

Đề xuất bổ sung một đối tượng logic `demand_episode` hoặc dùng Lead hiện có với ý nghĩa một nhu cầu tại một thời điểm. Tối thiểu gồm `account_or_contact`, product/service, source event, lifecycle dates, qualification policy version, status, owner, disqualification/recycle reason và next review date. Không bắt tạo bảng mới nếu sản phẩm chọn đã biểu diễn được đúng nghĩa này.

Luồng đề xuất: intake hợp lệ → kiểm fit/intent → MQL hoặc nurturing → Sales Accepted/Rejected/Recycle → discovery → SQL/deal → won/lost. B2C đơn giản có thể gộp bước nhận/qualification; không biến nhiều stage thành chỉ tiêu nhập liệu. Handover có thời hạn theo loại nhu cầu và giờ làm việc; SAL là xác nhận nhận việc, không phải chứng minh đủ khả năng mua. Reject phải phân biệt invalid/spam/duplicate/no fit/no capacity/not now để CMO sửa đúng khâu. No capacity là lỗi năng lực phục vụ, không phải lead kém chất lượng.

Nguồn đối chiếu: HubSpot tách lifecycle stage với Lead Status và lưu thời gian vào/ra stage. Đây là pattern hữu ích, không yêu cầu sao chép toàn bộ stage mặc định. [HubSpot lifecycle stages](https://knowledge.hubspot.com/records/use-lifecycle-stages?tab=content).

### 4.2 RFM: phản ví dụ chứng minh ngưỡng hiện tại không đủ

Khách A trả trước 12 tháng ngày 01/01; đến tháng 5 vẫn đang được phục vụ tốt. R = 120 ngày không có nghĩa khách ngủ đông. Khách B trả từng tháng nhưng nhiều ticket nghiêm trọng không trở thành khỏe chỉ vì R≤30. F=6 "kỳ thanh toán" cũng không thể so trực tiếp giữa hợp đồng tháng/quý/năm.

Giữ RFM tài chính để phân tích cash relationship, nhưng phân nhóm vận hành ưu tiên hợp đồng đang hiệu lực, lịch thu theo hợp đồng và kết quả delivery. Nếu chuẩn hóa F theo service period thì phải gọi đúng là số kỳ dịch vụ được thanh toán/phủ tiền, không còn là tần suất giao dịch thuần. Ngưỡng cao/thấp theo service model, cohort, quan sát đủ; không tự coi refund chậm là khách không có giá trị. Customer risk có reason codes và action owner; không gộp tất cả thành một điểm mù.

### 4.3 Journey: khách nhận thông điệp nào là quyết định cấp quan hệ

Hai journey cùng cho 2 tin/7 ngày có thể tạo 4 tin cho một contact. Một consent revocation xảy ra sau lúc scheduler chọn danh sách nhưng trước lúc gửi phải chặn ở dispatch. Một retry không được tạo tin lần hai. Khách có ticket nghiêm trọng nên bị suppression upsell nhưng thông tin xử lý sự cố cần tiếp tục theo mục đích phù hợp.

Đề xuất `send_intent` → eligibility/policy check → reserve frequency budget → durable outbox → provider dispatch → delivery result; khóa idempotency theo scope + journey instance + step + business event + recipient/channel. Global arbitration áp trong phạm vi đúng chủ thể xử lý dữ liệu; không kéo hồ sơ người tiêu dùng giữa các khách agency chỉ để kiểm cap. Platform window/quota và internal quiet hours là hai rule riêng.

Mautic có campaign decisions/actions/conditions, send scheduling và frequency behavior; tài liệu cũng nêu transactional email khác marketing email. Điều này củng cố nhu cầu phân mục đích; **không có nghĩa đặt nhãn transactional là tự có cơ sở gửi hoặc được bỏ qua mọi policy**. [Mautic campaign builder](https://kb.mautic.org/article/creating-campaigns.html), [Mautic emails](https://docs.mautic.org/en/7.2/channels/emails.html).

### 4.4 Strategy, approval, delivery: tối thiểu cần một chuỗi bằng chứng

Chuỗi gọn: mục tiêu khách → giả thuyết giải quyết → scope đã ký → ngân sách/creative đã duyệt → phiên bản thực chạy → đầu ra nghiệm thu → kết quả và bài học. CRM giữ ID, version, trạng thái, owner và liên kết; tài liệu chiến lược/creative có thể ở công cụ ngoài. Bằng chứng duyệt cần xác định ai có quyền duyệt khoản nào: người duyệt nội dung có thể không có quyền duyệt tăng chi tiêu.

Không lấy tracking test làm gate bắt buộc cho một job thiết kế logo không có media. Không vô hiệu toàn bộ approval khi sửa chính tả không làm thay đổi claim/scope. Ngược lại, đổi offer/claim/giá ở trang đích là thay đổi có thể ảnh hưởng approval dù banner không đổi. Template phải định nghĩa dependency map giữa approval subject và thay đổi có tác động.

Task Done khác deliverable Accepted. Revision do agency sửa lỗi theo phạm vi đã cam kết không mặc định trừ quota chỉnh sửa của khách. Client-wait phải có start/end/reason/request evidence; due date theo cam kết không tự đổi, còn forecast delivery có thể cập nhật. Khách duyệt xong mới đổi scope là change request có tác động thời gian/chi phí và người duyệt.

### 4.5 Chi phí và capacity: giữ đo lường, tránh áp đặt timesheet

Với quy mô nhỏ, có thể dùng chi phí freelancer thực tế và labor allocation chuẩn theo gói, ghi rõ estimated. Chỉ bắt timesheet chi tiết nếu cần báo giá theo giờ, kiểm biên lợi nhuận hoặc capacity mà lợi ích vượt chi phí nhập. Mỗi khoản cost chỉ có một nguồn ghi chính; sửa rate hiện tại không được tự thay toàn bộ cost lịch sử đã chốt.

Available budget = approved − actual − outstanding commitment là công thức đúng khi ba số cùng scope/currency/tax basis/time basis. Nếu supplier invoice mới ghi nhận một phần, chỉ giảm phần commitment đã được thay thế; nếu canceled commitment, trả lại phần còn lại. Estimated cost to complete là dự báo riêng, không trừ lần nữa nếu đã nằm trong commitment. Margin hiện tại cần kèm dự báo margin hoàn thành, vì dự án đang làm dở chưa tiêu đủ chi phí có thể trông rất lãi.

Odoo mô tả project profitability dựa trên khoản thu và chi phí gắn project/analytic account; kết quả search của tài liệu chính thức hỗ trợ pattern liên kết này. Chưa mở được đầy đủ trang trong phiên do timeout, nên không dùng để khẳng định edition, module dependency hoặc out-of-box compatibility. [Odoo project profitability](https://www.odoo.com/documentation/19.0/applications/services/project/project_management/project_profitability.html).

## 5. Đo lường, attribution và vòng phản hồi Meta

### 5.1 Bốn sổ đo lường không được trộn

| Tập dữ liệu | Ví dụ | Dùng cho | Không được dùng cho |
| --- | --- | --- | --- |
| Agency acquisition | 20 triệu agency tự chạy để tìm khách agency | CPL/CPQL/CAC agency | Tổng media spend của khách |
| Agency service economics | Phí dịch vụ 40 triệu, cost delivery 25 triệu | Biên đóng góp 15 triệu trước overhead theo định nghĩa | Doanh thu bán hàng của khách |
| Client campaign spend | Khách cấp 300 triệu media | Pacing, client CPL/ROAS | CAC agency, phí agency kiếm được |
| Client business outcome | Khách báo bán 900 triệu | Client ROAS khi đủ mapping/model | Doanh thu agency 900 triệu |

Ví dụ trên chỉ minh họa đại số, không phải benchmark. `scope_type`, workspace, beneficiary, outcome owner, metric namespace và cost basis phải có ngay tại ingest; dashboard chỉ lọc sau cùng không đủ.

### 5.2 First/last touch là mô hình nội bộ phải tự định nghĩa rõ

GA4 mô tả attribution là phân bổ credit cho touchpoints và hiện có các model cụ thể; last click có quy tắc xử lý Direct. Vì vậy model CRM `first-touch`/`last-touch` không mặc nhiên giống số Google/Meta. [Google Analytics attribution](https://support.google.com/analytics/answer/10596866?hl=en).

Tối thiểu cần chọn:

- Outcome là lead accepted, deal won, service revenue, hay cash received? Mỗi outcome có ID, value, currency, occurred_at và revision.
- First touch từ đầu quan hệ hay đầu nhu cầu hiện tại? Last touch có bỏ direct không? Lookback 90 ngày là giả định, không chuẩn chung; cần theo chu kỳ bán/gói dịch vụ và đủ dữ liệu.
- Acquisition source, recent interaction source và self-reported source là ba trường khác nghĩa. Khách nói được bạn giới thiệu nhưng UTM là Google brand search: giữ cả hai, không ép ghi đè.
- Một account nhiều contact, một contact nhiều account: chỉ credit khi quan hệ có scope và thời hạn phù hợp với nhu cầu/deal. Không chia mọi deal của công ty cho mọi contact đã chạm marketing.
- Tổng credit từng outcome/model = 1 sau bổ sung Unknown; core attribution credits không vượt 1. Referral payout share và Sales commission share là hai ledger khác, không gộp vào marketing credit.
- Không được cộng doanh thu first-touch và last-touch thành tổng. Không cộng attributed revenue giữa Google, Meta và CRM vì mỗi hệ thống có thể claim cùng conversion.
- Refund có delta/reversal và version; late touchpoint sau khóa kỳ tạo restatement được ghi lịch sử. Không sửa mất snapshot báo cáo đã gửi khách.

### 5.3 Chỉnh KPI để ra quyết định đúng

| KPI hiện có | Bổ sung bắt buộc |
| --- | --- |
| CAC | Tách kỳ chi tiêu với cohort khách; ghi rõ blended/paid/fully loaded, sales cost đã gồm chưa; có acquisition lag; 0 khách mới là N/A, không 0 |
| LTV đóng góp | Tên hiện tại thực chất là observed cumulative contribution/customer; không gọi lifetime forecast nếu cohort chưa trưởng thành. Cohort tuổi khác nhau không so trực tiếp |
| MQL→SAL→SQL | Đếm unique demand episode, giữ timestamps và reject reason; không đếm contact chuyển qua lại nhiều lần thành nhiều lead mới |
| Win rate | Kèm no-decision, paused, re-open và cohort age; không loại mọi deal khó bằng OnHold để nâng tỷ lệ |
| Sales cycle | Ngoài median Won cần lost duration, open aging và total/active duration; chỉ xem Won bỏ qua deal đang tắc |
| ROAS/ROMI | Chỉ rõ outcome value basis, refunds, tax, time window và model. ROI có attribution không tự thành incrementality |
| Revenue/retention | Phân loại new/renewal/expansion/contraction/churn; retainer recurring fee khác invoice/cash; điều kiện đủ tái ký phải nhất quán |
| Health score | Từng thành phần, weight version, freshness, unknown; mở màn hình phải dẫn tới hành động và owner, không chỉ màu |

### 5.4 Closed-loop CRM→Meta: bổ sung năng lực, không hứa hiệu suất

Nguồn Meta Blueprint công khai mô tả kết nối CRM qua Conversions API để tối ưu qualified leads và theo dõi trạng thái tích hợp/lead coverage. Nội dung mở được là trang mô tả mục tiêu khóa học, không phải toàn bộ tài liệu API hay kết quả thử nghiệm. [Meta Blueprint — Improve lead quality with Conversions API for CRM](https://www.facebookblueprint.com/student/activity/603002-improve-lead-quality-with-meta-conversions-api-for-crm).

Đề xuất kỹ thuật **I**: trạng thái qualification có bằng chứng → canonical CRM outcome event → kiểm quyền/mục đích/phạm vi → mapping connector version → outbox → gửi dataset/ad account được cấu hình → receipt/error → retry/reconciliation. Lưu source platform lead/click IDs khi có quyền và khi được trả về; không tự chế ID. Mapping event names/parameters/correction behavior phải kiểm tài liệu phiên bản API và PoC tài khoản thật. Không khẳng định mọi flow instant forms/website/messaging cùng payload hay cùng điều kiện.

**Guard dữ liệu:** lead tìm khách cho agency chỉ xuất về dataset agency; người tiêu dùng của khách A chỉ xuất dataset A theo quyền được cấp; không lấy contact của khách A làm custom audience tìm khách agency; không dùng dữ liệu khách B để bù volume A. Dataset binding có scope; token/ad account có owner; preflight reject mismatch. Hash identifier không thay thế phân quyền và cơ sở xử lý.

**Guard tính đúng:** Won khác Paid; Sales đổi stage liên tục không tạo nhiều purchase. Cần event IDs và attempt logs ổn định; biết sent/accepted/rejected khác matched/attributed. Theo dõi eligible events, export coverage, error rate, latency, stale connection; không coi HTTP 200 là chứng minh tối ưu quảng cáo tốt. Refund/correction phải theo khả năng chính thức của API hiện dùng, không tự giả định có thể thu hồi mọi event.

P0: lưu source IDs, qualification/outcome lineage và scope đúng. P1: một connector closed-loop sau khi dữ liệu đủ sạch, tài khoản đủ điều kiện và thử nghiệm có baseline. Không đặt ngưỡng volume hoặc lời hứa giảm CPL bằng các số đọc từ cộng đồng chưa kiểm chứng.

## 6. GitHub: đã kiểm chứng gì và chưa chứng minh gì

Đã mở code `odoo/odoo`, branch `19.0`, file `addons/crm/models/crm_lead.py`. Trong code quan sát được `crm.lead` kế thừa `utm.mixin`, có campaign/source/medium, company/team/salesperson, loại lead/opportunity, lost reason, xác suất và expected close date. Code tính prorated revenue từ expected revenue × probability và monthly recurring revenue từ số tháng plan. Đây là **C** về các pattern triển khai. [Code Odoo CRM](https://github.com/odoo/odoo/blob/19.0/addons/crm/models/crm_lead.py).

Hàm tính duplicate candidates có sử dụng quyền cao cho việc tìm ứng viên theo thiết kế của Odoo. Không suy ra đây là lỗi Odoo; nhưng cũng không được copy pattern sang multi-client workspace mà chưa kiểm threat model. UTM fields trên lead không tự tạo touchpoint ledger/MTA. Field `referred` không tương đương referral payout/anti-fraud ledger.

Branch đang thay đổi; phiên nghiên cứu chưa ghim commit hash, chưa clone/build/chạy test. Do đó **không khẳng định bản cài đặt bất kỳ có đúng hành vi, đủ licensing/edition, an toàn tenant hoặc đáp ứng SRS này**. Việc chọn Odoo, Frappe, Espo hay sản phẩm khác phải do PoC chức năng quyết định. Hai URL thử đọc `FrequencyRule.php` của Mautic không truy xuất được; không có kết luận "đã đọc code Mautic". Tài liệu Mautic đọc được chỉ được gắn nhãn W.

## 7. Bộ nghiệm thu CMO đề xuất

| Mã | Tình huống | Kết quả phải đạt |
| --- | --- | --- |
| M01 | Khách B2B hiện hữu nảy sinh nhu cầu mới | Quan hệ Customer được giữ; demand/deal mới có lineage, không tính khách mới lần hai |
| M02 | Sales từ chối vì hết capacity | Reason no-capacity; không cộng vào invalid lead; trưởng nhóm có hành động điều phối |
| M03 | Lead chuyển MQL→Recycle→MQL | Không đếm acquisition lead mới; giữ hai episode chuyển trạng thái và thời gian từng lần |
| M04 | Contact đại diện hai account | Touchpoint chỉ credit deal có liên kết hợp lệ, không lan toàn bộ doanh thu hai công ty |
| M05 | Khách trả trước năm, vẫn đang phục vụ | Không auto win-back/dormant chỉ do R>90; hiển thị hợp đồng/period paid đúng |
| M06 | Một hóa đơn thanh toán ba đợt | Cash đủ ba khoản nhưng purchase/service frequency không tăng thành ba |
| M07 | Hai journey đồng thời, cap 2/7 ngày | Tổng marketing sends trong scope không vượt cap; có lý do defer/suppress |
| M08 | Rút consent lúc đang chờ gửi | Dispatch kiểm lại và hủy bước marketing chưa gửi; audit giữ policy decision |
| M09 | Retry event 10 lần | Một send effect và một canonical outcome, nhiều attempt logs nếu cần |
| M10 | Ticket nghiêm trọng đang mở | Upsell bị chặn/AM review; cập nhật xử lý ticket vẫn hoạt động theo mục đích phù hợp |
| M11 | Creative approved v1, sửa offer v2 | Không dùng approval v1 cho v2; người duyệt có đúng authority |
| M12 | Điều chỉnh nhỏ trong hạn mức tối ưu đã duyệt | Lưu audit; không bắt duyệt lại phần không chịu tác động |
| M13 | Logo đơn lẻ không có ads | Gate không đòi tracking pixel; vẫn có scope, asset version, acceptance |
| M14 | Khách chờ duyệt 5 ngày | Client-wait và forecast đổi có lịch sử; contractual deadline không âm thầm đổi |
| M15 | Lỗi do agency phải sửa | Ghi defect/rework, không tự trừ quota change request của khách |
| M16 | Commitment 100, actual 40 | Outstanding commitment 60; tổng exposure không thành 140 |
| M17 | Sửa cost rate hiện tại | Chi phí kỳ đã chốt giữ snapshot; thay đổi hồi tố cần adjustment/restate |
| M18 | Agency spend 20, client media 300 | CAC agency chỉ dùng cost đủ điều kiện agency, không 320 |
| M19 | UTM mất do lỗi và truy cập Direct thật | Hai bucket/phân loại riêng; data quality issue không biến thành Direct |
| M20 | Một outcome được Meta và Google cùng claim | CRM không cộng hai platform totals thành doanh thu thật |
| M21 | Refund một phần sau đóng kỳ | Delta revenue/referral/credit theo policy, giữ snapshot báo cáo cũ |
| M22 | Connector Meta bị gán nhầm dataset khách B cho khách A | Fail closed trước gửi; có lỗi cấu hình để admin sửa; không lộ payload A |
| M23 | Won chưa trả tiền | Won event và cash event khác; không gửi Paid hoặc tính thưởng đủ điều kiện nếu chưa có cash |
| M24 | A/B có 8 observations mỗi nhóm | Hiển thị sample/uncertainty; không tự tuyên bố winner đủ tin cậy theo rule chưa đạt |
| M25 | Spend API ngừng cập nhật | Freshness Degraded/Unknown; không hiển thị campaign health xanh mặc định |
| M26 | Có referrer nhưng khách đã tồn tại | Kiểm new-customer policy và dispute; không tự thưởng chỉ vì nhập mã referral |

## 8. Nguồn, chỗ đã đọc và giới hạn truy cập

| Nguồn | Nội dung thực sự quan sát | Mức bằng chứng / giới hạn |
| --- | --- | --- |
| [HubSpot lifecycle stages](https://knowledge.hubspot.com/records/use-lifecycle-stages?tab=content) | Đã mở phần định nghĩa stage, lead status, timestamp/time in stage, cập nhật lifecycle; trang ghi cập nhật 17/07/2026 | W. Mô hình tham khảo của vendor, không chuẩn bắt buộc |
| [Meta Blueprint CRM CAPI](https://www.facebookblueprint.com/student/activity/603002-improve-lead-quality-with-meta-conversions-api-for-crm) | Đã mở trang công khai; đọc learning objectives về CRM integration, qualified lead optimization, integration status và lead coverage | W. Chỉ landing description khóa học; chưa xem webinar/API schema |
| [Meta Lead Generation Guide](https://about.fb.com/ltam/wp-content/uploads/sites/14/2023/11/LeadGenerationGuide.pdf) | Search trả đoạn về CRM + CAPI và conversion leads; open PDF lỗi | S. Không dùng làm bằng chứng về điều kiện phiên bản API hiện tại |
| [Facebook Business Help URL đã thử](https://www.facebook.com/business/help/582993041093988) | Open lỗi, không đọc được nội dung | Không tính là nguồn xác nhận. Không có group/post Facebook được đọc đầy đủ trong nhánh nghiên cứu này |
| [Google Analytics attribution](https://support.google.com/analytics/answer/10596866?hl=en) | Search trả nội dung chính thức về 3 model, direct treatment, attribution/lookback settings; open sau đó bị 429 | W qua search result body; không coi là đã kiểm cấu hình tài khoản hay API |
| [Mautic emails 7.2](https://docs.mautic.org/en/7.2/channels/emails.html) | Đã mở phần template/segment emails, frequency queue, scheduling/A-B description | W. Tính năng vendor không tự đáp ứng policy CRM |
| [Mautic campaign builder](https://kb.mautic.org/article/creating-campaigns.html) | Đã mở decisions/actions/conditions, re-entry, scheduling và khác biệt transactional frequency | W. Bài ngày 11/07/2022, dùng pattern; cần PoC bản chọn |
| [Odoo CRM source 19.0](https://github.com/odoo/odoo/blob/19.0/addons/crm/models/crm_lead.py) | Đã đọc code fields/inheritance, expected/recurring revenue computations và duplicate candidate comment | C. Chưa ghim commit, chưa run code |
| [Odoo project profitability](https://www.odoo.com/documentation/19.0/applications/services/project/project_management/project_profitability.html) | Search trả nội dung project/analytic account/revenue/cost; open timeout | S/W limited body. Không xác nhận licensing/edition/module dependencies |

Không dùng bài Reddit xuất hiện trong kết quả tìm kiếm để làm kết luận chuẩn. Không suy diễn đã khảo sát Facebook cộng đồng chỉ vì đọc được tài liệu Meta. Muốn kết luận thị trường agency Việt Nam cần thêm phỏng vấn có chủ đích, case study có quyền sử dụng và dữ liệu vận hành; nghiên cứu desk research hiện tại không thay thế bước đó.

## 9. Phương án triển khai khuyến nghị

**P0:** một lead source; một kênh giao tiếp; lifecycle/demand/deal rõ; source IDs + UTM và Unknown chuẩn; brief/SOW/approval/deliverable gọn; dữ liệu thu tiền/cost có scope; 8–12 metric được chốt định nghĩa; suppression và audit đủ dùng. CEO phê duyệt scope, CMO sở hữu taxonomy/qualification, Sales xác nhận handover, AM sở hữu acceptance, kế toán sở hữu tiền và cost đã chốt.

**P1:** automation giới hạn có frequency control; một closed-loop Meta connector đã PoC; project/capacity integration; referral đơn giản; campaign spend và KPI reconciliation; health rules có action owner. Gate mở rộng là dữ liệu/tỷ lệ lỗi/thời gian thao tác đạt tiêu chí pilot, không chỉ đã có màn hình.

**P2:** loyalty điểm/Mini App, strategy editor đầy đủ, MTA hoặc mô hình dự báo, experiment orchestration, nhân sự scorecard. Chỉ mở khi có quyết định cụ thể cần năng lực đó và chi phí vận hành/độ tin cậy được chứng minh.

Lựa chọn tốt nhất với thông tin hiện có là cấu hình CRM đã có + tích hợp nhẹ, giữ một nguồn ghi cho mỗi nghiệp vụ. Không có bằng chứng đủ để khẳng định một vendor cụ thể là tốt nhất hoặc xây mới toàn bộ sẽ rẻ hơn. Bộ UAT trên phải được dùng chung khi PoC các phương án.
