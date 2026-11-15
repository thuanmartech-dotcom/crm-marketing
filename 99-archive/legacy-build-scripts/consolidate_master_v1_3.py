from pathlib import Path
import re
import json
import hashlib

ROOT = Path(r'D:\AI Agent\CRM')
MASTER = ROOT / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
REVIEW = ROOT / 'CRM_RESEARCH_REVIEW_CEO_CMO_CX_2026-10-15.md'
ARCHIVE = ROOT / 'docs' / 'archive' / 'research-2026-10-15'
original = MASTER.read_text(encoding='utf-8-sig')
review = REVIEW.read_text(encoding='utf-8-sig')
text = original
changes = []

def replace(old, new, count=1):
    global text
    actual = text.count(old)
    if actual != count:
        raise ValueError(f'Expected {count} occurrences, got {actual}: {old[:110]}')
    text = text.replace(old, new)
    changes.append(old[:90])

def section(heading, body):
    global text
    pattern = rf'(?m)^{re.escape(heading)}\n.*?(?=^#{{1,{len(heading)-len(heading.lstrip("#"))}}} |\Z)'
    # Explicit heading-level boundary also respects intervening HTML chapter anchors.
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError(f'Cannot find section {heading}')
    old = match.group(0)
    trailing = re.search(r'\n(<a id="[^"]+"></a>\n\n)$', old)
    tail = trailing.group(1) if trailing else ''
    text = text[:match.start()] + heading + '\n\n' + body.strip() + '\n\n' + tail + text[match.end():]
    changes.append(heading)

def review_section(number):
    match = re.search(rf'(?m)^## {number}\. .*?\n(.*?)(?=^## |\Z)', review, re.S)
    if not match:
        raise ValueError(f'Missing review section {number}')
    return match.group(1).strip()

def insert_before(marker, addition):
    replace(marker, addition.strip() + '\n\n' + marker)

fr_rows = {}
uc_rows = {}
for line in review.splitlines():
    if re.match(r'^\| FR\d{2}\b', line):
        cells = [v.strip() for v in line.strip().strip('|').split('|')]
        fr_rows[re.match(r'FR\d{2}', cells[0]).group()] = cells
    if re.match(r'^\| UC\d{2}\b', line):
        cells = [v.strip() for v in line.strip().strip('|').split('|')]
        uc_rows[re.match(r'UC\d{2}', cells[0]).group()] = cells
assert len(fr_rows) == 40 and len(uc_rows) == 22

replace('Phiên bản 1.2 — hợp nhất tài liệu, nghiên cứu CRM và Omnichannel năm kênh',
        'Phiên bản 1.3 — Master chính thức duy nhất, hợp nhất rà soát CEO, CMO, CX và kỹ thuật')
replace('**Đọc nhanh:** Phụ lục A ghi 15 điểm được kế thừa và 26 điểm cần sửa, hoãn hoặc bổ sung, với vị trí nguồn và lý do. Phần thân là đặc tả hệ thống đã hợp nhất, không phải bản ghép lại các tài liệu cũ.',
'''**TỆP MASTER DUY NHẤT HIỆN HÀNH:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản 1.3. Dùng tệp này để thống nhất yêu cầu, thiết kế, lựa chọn giải pháp và lập nghiệm thu. Nội dung rà soát CEO/CMO/CX đã được tích hợp vào 40 FR, 22 UC, schema, quyền, báo cáo và UAT. Các tài liệu nghiên cứu cũ chỉ là hồ sơ lịch sử trong `docs/archive/research-2026-10-15/`, không phải bản đặc tả song song.

**Cách đọc:** Chương 3 nêu chức năng, lý do, chủ trách nhiệm và liên kết; 3.13 quy định các bàn giao xuyên module; Chương 5 là dictionary thống nhất; Chương 9 chứa phạm vi, gate và UAT; Phụ lục E ghi quyết định hợp nhất và nguồn nghiên cứu. Các tham số kinh doanh chưa được cung cấp được ghi tại A.6; điều đó không tạo thêm một bản Master khác. Đây là đặc tả chính thức của dự án, chưa phải chứng nhận phần mềm đã xây/chạy đạt hoặc các giả định ngân sách đã được phê duyệt.''')
replace('| Trạng thái quyết định | Các lựa chọn thiết kế là đề xuất. Chưa có xác nhận nhà cung cấp, giá dịch vụ, ngân sách hoặc mẫu hợp đồng thực tế. |',
        '| Trạng thái quyết định | Phiên bản đặc tả chính thức hiện hành. Các quy tắc được xác định trong bản này là baseline thiết kế; tham số SLA/giá/thuế/hoa hồng, sản phẩm và ngân sách còn cần xác nhận theo A.6 trước kích hoạt nghiệp vụ tương ứng. Chưa có biên bản UAT production. |')
replace('**Cập nhật 1.2:** bổ sung kiến trúc hợp nhất Zalo, Facebook, TikTok, Web Form, Email; FR30–40, UC17–22, 24 UAT Omnichannel và nghiên cứu chín sản phẩm/nền tảng. [Đọc nghiên cứu và quyết định](#phu-luc-d).',
'''**Lịch sử phiên bản:** 1.2 bổ sung Omnichannel và nguồn CRM tham khảo; 1.3 hợp nhất báo cáo phản biện và ba chuyên đề CEO/CMO/CX, xử lý các mâu thuẫn và thu gọn phạm vi pilot. [Quyết định hợp nhất 1.3](#phu-luc-e). Bản 1.2 được lưu lịch sử; mọi chỉnh sửa tiếp theo cập nhật đúng tệp Master này và lịch sử phiên bản.''')
replace('- [Phụ lục D — Nghiên cứu CRM và quyết định tích hợp](#phu-luc-d)',
        '- [Phụ lục D — Nghiên cứu CRM và quyết định tích hợp](#phu-luc-d)\n- [Phụ lục E — Quyết định hợp nhất 1.3 và nguồn CEO/CMO/CX](#phu-luc-e)')
replace('| BR05 | Gián đoạn tái ký | Nhắc trước ngày hết hạn 45/30/15 ngày, gắn health score và người chịu trách nhiệm. |',
        '| BR05 | Gián đoạn tái ký | Nhắc theo ngày quyết định/notice deadline và kỳ hợp đồng; 45/30/15 ngày chỉ là template cấu hình. Gắn success review, health và người chịu trách nhiệm; không áp tự động cho mọi one-off. |')

section('### 1.6 Ranh giới sản phẩm', '''MVP đi hết hành trình: hồ sơ → nhu cầu → deal → brief/báo giá/SOW → hợp đồng/kỳ thu → tiền/đối soát → bàn giao → đầu ra/nghiệm thu → ticket/khắc phục → gia hạn phù hợp. Một nguồn lead và một kênh giao tiếp trước. Có thể nhập và đối soát tài chính thủ công có kiểm soát; không bắt tự động hóa hết để đảm bảo đúng dữ liệu.

P0 giữ quyền/scope, source/consent, next action, revision/approval, tiền/phân bổ, evidence, recovery cơ bản, báo cáo ít chỉ số và backup/restore. P1 theo nhu cầu gồm tích hợp kế toán/PMS/calendar, spend/capacity, referral, health/NPS và một vòng phản hồi CRM→Meta. P2 gồm loyalty/Mini App, strategy editor đầy đủ, experiment engine, multi-touch, predictive scoring, scorecard nhân sự và AI tự hành.

Mỗi FR bên dưới có lý do, liên kết và điều kiện mở. Feature ở P1/P2 vẫn có trong thiết kế đích đến nhưng không được tính vào cam kết MVP/90 ngày. Chọn giải pháp cấu hình hoặc hybrid nhẹ trước khi tự xây toàn bộ; ngân sách và PoC quyết định nền tảng theo Chương 10.''')

replace('Mỗi bản ghi thuộc tenant_id là tổ chức sở hữu dữ liệu. branch_id phân phạm vi chi nhánh trong tổ chức. business_line_id phân ngành hoặc dòng dịch vụ, không thay thế tenant. client_workspace_id dùng cho dữ liệu người tiêu dùng xử lý thay một khách hàng agency; tuyệt đối không mặc định đưa họ thành khách hàng bán dịch vụ của agency.',
'''`tenant_id` cô lập tổ chức; `workspace_id` phân phạm vi AGENCY/CLIENT; `branch_id` phân trách nhiệm vận hành; `legal_entity_id` xác định pháp nhân ký/hạch toán/nhận tiền. Bốn khái niệm này không thay nhau. Mỗi tenant có workspace AGENCY ngay từ pilot; workspace CLIENT chỉ xử lý dữ liệu theo phạm vi khách ủy quyền, không tự chuyển người tiêu dùng thành khách bán dịch vụ của agency.

Dữ liệu scoped dùng `workspace_id NOT NULL`. Danh mục cấp tenant được khai báo riêng. Hồ sơ Account mua dịch vụ của agency, hợp đồng và tài chính nội bộ thường thuộc AGENCY workspace; dữ liệu delivery/người tiêu dùng của khách có thể thuộc CLIENT workspace. Liên kết qua scope chỉ qua quan hệ được khai báo và kiểm quyền, không tự cấp quyền đọc toàn bộ hợp đồng/commission. Một pháp nhân/chi nhánh mặc định đủ cho pilot khi thực tế chỉ có một; không xây multi-company engine nếu chưa cần.''')

fr_content = {
'FR03': '''RFM là lát cắt giao dịch, không thay health. Giữ `payment_recency`, số kỳ dịch vụ/mua và service cash sau refund; loại VAT/media theo policy. Frequency không tăng thành ba lần mua khi một nghĩa vụ trả ba đợt. B2B tính theo Account, B2C theo Contact trong đúng scope.

Khách trả trước năm vẫn đang được phục vụ không bị đánh ngủ đông chỉ vì lâu không có khoản thu. Phân nhóm hành động ưu tiên hợp đồng/kỳ dịch vụ đang hiệu lực, engagement, delivery, overdue và ticket. Nhãn Khách mới/Giá trị cao/Có rủi ro/Không hoạt động có thể đồng thời tồn tại; mỗi nhãn có reason, window, version, owner và hành động. Ngưỡng được pilot theo mô hình dịch vụ; dữ liệu thiếu là Unknown. Không dùng ngưỡng R≤30/F≥6 chung cho mọi lịch trả.''',
'FR04': '''Lead biểu diễn một nhu cầu/đợt tiếp nhận: New → Assigned → Contacting → Qualified → Converted; các nhánh Nurture, Dormant, Disqualified có lý do và điều kiện thoát. `handover_status` Marketing→Sales tách khỏi trạng thái này: Pending/Accepted/Rejected/Recycled; ghi người giao/nhận, timestamps, policy, reason/evidence. NoCapacity không phải NoFit. MQL/SAL/SQL là milestones có định nghĩa, không ghi đè lifecycle Customer của Contact.

Deal B2B: Discovery → Proposal → Negotiation → Won/Lost; B2C: Offer → Won/Lost theo gói. OnHold có lý do, review date, quy tắc forecast và lịch sử; giữ total age/active time/hold time. Không clone chỉ để làm ngắn sales cycle. Qualified cần đầu mối, nhu cầu và next action; budget/decision maker chưa rõ ghi Unknown. Vai trò ở Account khác thẩm quyền ký/nghiệm thu một hợp đồng.

Nhu cầu mới của khách cũ tạo Lead/Deal mới có lineage; hỗ trợ sau bán tạo Ticket. Cùng nhu cầu thì nối lịch sử hiện hữu, không dùng ngưỡng 14 ngày duy nhất. Kiểm trùng mềm theo buyer/account + service/campaign/nhu cầu và scope; cho phép các deal song song hợp lệ. Conversion idempotent và chỉ link activity/thread thuộc nhu cầu đó; Lost không xóa quote/history.''',
'FR05': '''Router lọc tenant/workspace/quyền và phạm vi phục vụ/kỹ năng trước; ưu tiên owner hợp lệ rồi kiểm lịch khả dụng/backup và ngưỡng capacity mềm/cứng. Trùng phone/email hash chỉ cảnh báo nghi trùng, không trao quyền hoặc tự merge. Người trực thay không tự đổi chủ Deal hay quyền hưởng commission. Atomic claim/CAS hoặc row lock, history và outbox cùng transaction.

Tách đồng hồ nhận việc, nỗ lực đầu, phản hồi người thật và kết nối thành công; completion theo đúng nhu cầu/episode. NoAnswer/busy có evidence là attempt theo policy, chưa là kết nối/phản hồi thành công. Không dùng riêng 15 giây đổ chuông để chứng minh đã chăm sóc. Có next action/callback và cơ chế xử lý race khi activity đến muộn hoặc lead đang bị thu hồi.

Business calendar Asia/Ho_Chi_Minh khai báo ca, nghỉ trưa/ngày nghỉ và version; ngoài giờ theo ca tiếp. Ngưỡng pilot theo kênh/intent/nhân sự: kênh có người trực có thể thử phản hồi đầu 15–30 phút, tư vấn B2B chuyên sâu 2–4 giờ làm việc; lead có hẹn theo lịch khách. Đây là giả định cần xác nhận, không cam kết 5/15 phút cho mọi lead. Cảnh báo/thu hồi theo policy; tối đa hai lần chuyển tự động rồi queue quản lý. Chuyển owner không reset nghĩa vụ khách hàng; provider outage có exception/audit, không sửa timestamp gốc.''',
'FR08': '''API kiểm row/field policy trước khi trả dữ liệu. Người được giao nhiệm vụ liên hệ được xem số/email cần thiết trong thời gian quyền còn hiệu lực, không phải nhập lý do lặp mỗi 5 phút. Người ngoài phạm vi thấy mask/không thấy theo policy; hồ sơ nhạy cảm hoặc break-glass dùng reveal có purpose/lý do/TTL cấu hình và audit. Search, file, BI, export và AI cùng kiểm soát; rate-limit/cảnh báo bổ sung không thay authorization.

Offboarding nhân sự thu hồi login/session/token/grant, bàn giao open lead/deal/ticket, lời hứa cập nhật, draft, scheduled send, approval pending, lịch và automation ownership. Job kiểm lại authority khi chạy; người không có quyền không dùng link/file/cache cũ để đọc tiếp. Giữ actor lịch sử và quyền hưởng hoa hồng theo policy; watermark hỗ trợ truy vết, không cam kết chống chụp ảnh tuyệt đối.''',
'FR10': '''Tách referral khỏi loyalty. Referral có nguồn, referrer, khách mới theo định nghĩa, ngày/điều kiện khóa attribution, dispute và payout. Kiểm tự giới thiệu, trùng pháp nhân, khách đã có, bên liên quan và thưởng trùng với pool sales theo policy. Chỉ thưởng khi đạt điều kiện thực thu/kiểm soát hoàn tiền đã công bố; refund tạo reversal một lần. Marketing attribution không tự tạo quyền nhận thưởng.

Referral nhẹ ở P1 và không phụ thuộc Mini App. Loyalty điểm/hạng, ưu đãi và Mini App ở P2, chỉ bật khi có hành vi mua lặp và business case. Khi bật phải có earn/reserve/redeem/expire/reverse append-only, policy economics, fraud control và consent. Không áp một tỷ lệ điểm/chi tiêu giả định cho mọi agency.''',
'FR11': '''Ghi âm có cơ sở sử dụng → STT → che dữ liệu không cần thiết → draft nhu cầu/ngân sách/ngày hẹn → người dùng xác nhận. Giữ call_id, model/prompt version, source timestamps và reviewer; không tự ghi dữ liệu thương mại quan trọng từ câu mơ hồ.

Pilot có thể bắt đầu với 60 cuộc được phép dùng, nhiều giọng/nhiễu, nhưng không coi mẫu đó chứng nhận chất lượng tổng quát. Tách tập sửa prompt và tập kiểm; đo exact-match/precision/recall của field quan trọng, omission, unsupported claims và phân biệt người nói. Mục tiêu 95% chỉ có nghĩa trên bộ đo đã định nghĩa; confidence model không tự là xác suất đúng. Số tiền/ngày hẹn cần người xác nhận; không đạt thì chỉ transcript/summary draft. P1 sau lõi.''',
'FR14': '''Catalog có phiên bản/hiệu lực, đơn vị, gói/phạm vi, loại SERVICE/PRODUCTION/MEDIA_PASS_THROUGH, thuế được kế toán xác nhận, cost estimate và mẫu SOW. Thuế là cấu phần net/tax/gross của dòng, không thay loại dịch vụ. Quote revision giữ price/cost basis, currency, validity, terms, số vòng sửa, đầu ra và phần loại trừ; bản đã gửi/approved bất biến.

Tách preliminary estimate chưa ràng buộc khỏi approved offer. Thiếu cost không mặc định 0/margin 100%; approved offer cần cost hoặc ngoại lệ có quyền. Biên đóng góp = phí dịch vụ thuần − cost trực tiếp theo định nghĩa; tỷ lệ chia cho phí thuần, mẫu số 0 là N/A; ghi rõ trước/sau commission và cost allocation.

Approval theo giá/discount, margin, payment terms, phạm vi, KPI/claim và quyền sở hữu/trách nhiệm. Discount=0 không tự đủ autoapprove. Ngưỡng minh họa 5%/30% chỉ áp sau khi chủ nghiệp vụ chốt; cá nhân self-approval có log, đội ngũ tách người tạo/duyệt ngoại lệ. Đổi field làm mất hiệu lực đúng approval bị tác động; quote expired phải revalidate. Customer acceptance và nội bộ approve là hai mốc riêng.''',
'FR15': '''SOW ghi mục tiêu/baseline, deliverable, lịch, quota sửa, tiêu chuẩn nghiệm thu, tài sản/đầu vào khách phải cấp, stakeholder có quyền duyệt, sở hữu và loại trừ. MSA có nhiều SOW/order/project; phụ lục/CR liên kết hợp đồng gốc và version. `document_type` (MSA/CONTRACT/ADDENDUM) khác `service_model` (RETAINER/ONE_OFF).

Won, contract effective, handoff accepted, start authorized, service started, accepted, invoiced và paid là các mốc riêng. Tạo nháp theo SOW/handoff idempotency key, không unique Project chỉ theo contract_id. Kickoff cần hợp đồng hiệu lực, tiền/credit đúng điều khoản, asset/capacity và người nhận xác nhận. Ngoại lệ có người duyệt, hạn, exposure và công việc được làm; cho bắt đầu sáng tạo không tự cho chi media.

Onboarding giữ success plan/sổ cam kết: mục tiêu khách, điều đã hứa, first value, owner, due, communication cadence và evidence. Client-wait ghi interval/reason; lịch dự kiến khác ngày hợp đồng/ngày sự kiện. Quota sửa theo SOW; một vòng là batch feedback; lỗi agency không tự trừ quota đổi ý hoặc ép CR. Acceptance trỏ đúng asset version và approver. Retainer có service periods và notice date; termination chốt khối lượng/nghĩa vụ/công nợ, settlement riêng. Offboarding khách bàn giao tài sản/quyền/records đúng hợp đồng, retention và tranh chấp.''',
'FR16': '''Tiền chỉ xác nhận từ ngân hàng/provider hoặc sao kê đã kiểm tra; QR/ảnh bill là tham khảo. Một giao dịch canonical có nhiều Payment_Evidence từ API/file; unique connector event không đủ chống trùng xuyên nguồn. Hai giao dịch thật cùng số tiền/ngày/nội dung không bị tự loại bằng fingerprint.

Tách verification_state, matching_state, allocation_state và reconciliation_state. Tiền confirmed vẫn có thể unidentified/unallocated. Phân bổ vào Payment_Obligations thuộc kỳ/dòng hợp đồng; Invoice_Allocation_Links đối chiếu invoice ERP khi có, không tạo cash/commission thêm. Giữ legal entity, tài khoản nhận, payer/buyer, currency. Người trả hộ vào case xác minh; không tự chuyển giữa pháp nhân.

Thứ tự phân bổ: điều khoản/kỳ đã duyệt → chỉ định được kế toán xác nhận → fallback policy được duyệt; chưa đủ cơ sở thì pending. Pro-rata không mặc định đúng mọi hợp đồng. Lock payment/obligation, kiểm số dư, insert allocation/outbox cùng transaction. Dư tiền là credit, partial giữ số còn nợ; refund/reversal liên kết phần gốc và kỳ khóa. Write-off, discount, bank fee có chứng từ là các loại khác; write-off không tạo cash-based commission.

Sales được đề xuất match có evidence, Finance duyệt; reconciliation case có owner/hạn/giải thích và đối soát CRM–ERP–bank. Nhắc nợ xét disputed amount/promise-to-pay và trạng thái ticket. Hóa đơn có nghĩa vụ pháp lý theo bản chất dịch vụ; sync ERP chậm không là quyền trì hoãn hóa đơn. Nhãn MEDIA_PASS_THROUGH không tự quyết định thuế/doanh thu.''',
'FR17': '''Base commission = eligible service cash × rate snapshot × share của pool/policy/version. Base loại VAT/media theo chính sách, sau giảm/hoàn; không lấy write-off thành thực thu. Pool hunter/renewal/referral tách và tổng share trong từng pool bằng 1. Policy snapshot truy được; đổi owner/chi nhánh/người trực inbox không đổi quyền hưởng đã chốt.

Preview khác Earned/Approved/Payable/Paid; từng chuyển trạng thái có điều kiện, authority và evidence. Khi tiêu chí chất lượng chưa có, phần liên quan pending; MVP tách base commission và quality bonus/adjustment nếu quy chế cho phép, không mặc định quality_factor=1 để chi. Bút toán số tiền bất biến; workflow status là projection của lịch sử, payout có batch và đối soát riêng.

Ví dụ không thuế: kỳ đã duyệt có 20 triệu service + 80 triệu media, thu 50 triệu và phân bổ pro-rata thì service base 10 triệu, rate5%=pool500.000; share70/30=350.000/150.000. Nếu kỳ đầu chỉ thu media, service base=0. Thiếu policy thì pending. Refund sau payout/kỳ khóa tạo adjustment liên kết, không xóa khoản đã trả hoặc tự khấu trừ ngoài quy chế hợp lệ. Preview mục tiêu ≤60 giây tính từ allocation đủ điều kiện, không từ ảnh bill/QR.''',
'FR18': '''Ticket tiếp nhận complaint/incident/question/defect/change và liên kết hợp đồng/project/deliverable qua Business_Subjects và các link typed. Entitlement snapshot lưu scope hỗ trợ, calendar, policy, authority và giới hạn. Luôn có intake khiếu nại; chưa rõ Contact dùng provisional và xác minh, không bỏ sự cố khẩn. Lỗi agency khác đổi scope; quota hết không tự từ chối lỗi.

Severity S1/S2/S3 theo impact×urgency và hợp đồng, khác P0/P1/P2 ưu tiên phát triển. Mẫu cần xác nhận: S1 phản hồi30 phút giờ có trực, giảm thiểu4 giờ; S2 phản hồi4 giờ làm việc, phương án1 ngày; S3 phản hồi1 ngày, lịch3 ngày. Không tự cam kết 24/7 khi không có người trực. Major incident có owner, containment/mitigation, affected assets và nhịp cập nhật.

Một engine SLA theo subject/episode gồm first attempt khi áp dụng, FRT, NRT, resolution và promised update; autoack/private note không dừng human clock, tin khách gửi lại không trượt hạn từ tin chưa đáp đầu. Pause theo clock/calendar/policy, pending_internal không tự pause. Reopen nối case gốc trong khoảng chính sách (mẫu7 ngày), giữ breach và remaining business time; không tự reset, không sửa timestamp lịch sử. WaitingCustomer có nhắc/hạn review, đóng no-response theo severity/điều khoản, không đóng S1 mù hoặc coi là đã xử lý. Đóng thread không tự đóng ticket khác.''',
'FR19': '''Thu feedback ở milestone/onboarding/ticket và quan hệ, lưu nguồn/câu hỏi version/role/contact/account. CSAT1–5, tỷ lệ4–5 trên người trả lời; NPS %9–10−%0–6 theo tập đủ trải nghiệm, kỳ90 ngày là cấu hình. CES chỉ thêm ở tương tác có mục tiêu giảm effort; không cộng ba thang thành điểm chung. Báo eligible/sent/delivered/responded và sample, không trả lời khác điểm0.

Survey có unique business effect, recheck consent/channel, cooldown contact/account và arbitration với incident; một close replay không spam, reopen trước gửi xét lại. Không chỉ chọn khách dễ cho điểm cao; B2B ghi vai trò và view account-level tránh account nhiều contact bị nhân trọng số ngầm.

Recovery: detected → triaged → owner accepted → contacted → remedy agreed → remedy done → verified → closed. Có due, evidence, quyền duyệt refund/đền bù, no-contact/refused callback là kết quả riêng; không sửa điểm gốc hoặc ép khách đổi điểm. Root cause theme dẫn corrective action có owner và kiểm tái diễn, nối lại launch checklist, lời hứa Sales, scope và renewal.''',
'FR21': '''Scope theo tenant/workspace/branch/legal entity và row/field policy. Tạo branch/pháp nhân mặc định khi thực tế đơn; dữ liệu Contact/Account có thể dùng chung theo grant, Deal/Project/Ticket có phạm vi riêng. Không ép branch NOT NULL cho mọi danh mục/shared record; giao dịch có trách nhiệm chi nhánh thì phải phân nhánh rõ.

Account/Contact/Deal/Project team grants có role, action/field scope, thời hạn và actor. B2C không cần Account giả để chia sẻ. Membership account không tự cho xem mọi CLIENT workspace hay tài chính agency. Deny thắng Allow là policy của dự án, phải PoC nền tảng có role merge khác. Quyền approve độc lập edit; Admin không mặc định đọc nghiệp vụ, CEO không sửa ledger bằng vai quản trị.

Chuyển nhánh bàn giao active work/promises/appointments/tickets, giữ đúng pháp nhân công nợ và commission lịch sử. Mọi đường API/search/count/file/export/AI và background job kiểm quyền hiện tại; break-glass có TTL/audit. Không dùng đổi branch để di chuyển công nợ.''',
'FR22': '''CRM giữ chuỗi business goal/baseline → brief/giả thuyết → SOW → approved plan → campaign/deliverable → measurement → learning. Mỗi quyết định có owner, version, nguồn và tiêu chí; phân biệt kết quả cam kết với mục tiêu kỳ vọng. Scope template chọn mức bắt buộc theo gói; logo/job nhỏ không phải đi đủ nghiên cứu chiến lược lớn.

Tài liệu strategy/IMC chi tiết có thể ở Slides/Sheets/Figma; CRM giữ link phiên bản hoặc snapshot/checksum, người duyệt, thời điểm và approved scope. URL thay đổi được đơn lẻ chưa đủ evidence. Không bắt nhập lại toàn bộ message house/content matrix. P0 brief/SOW/goals gọn; editor và schema chiến lược đầy đủ chỉ mở theo nhu cầu P1/P2.''',
'FR23': '''Campaign chỉ Live khi đạt gate áp dụng của scope template: approved scope, budget owner và funding/credit, asset đúng version, tracking đã test nếu có measurement, quyền tài khoản, lịch và người phụ trách. Người duyệt creative khác quyền tăng chi. Logo không media không đòi tracking pixel.

Approval gắn subject/version/hash, chiều rủi ro, authority, cap/expiry và evidence (email gốc nếu dùng). Dependency map làm mất hiệu lực đúng approval bị ảnh hưởng khi đổi offer/claim/audience/ngân sách/terms. Trong optimization envelope đã duyệt có thể tinh chỉnh và audit không xin lại từng lần; vượt envelope cần duyệt. Emergency pause có quyền/playbook; CRM chặn nút không tự chặn thao tác bên Ads Manager, cần least privilege ngoài kênh và đối soát spend. API chưa hỗ trợ thì tác vụ thủ công/evidence, không giả đã điều khiển được.''',
'FR24': '''Giữ nhật ký hypothesis, biến/đơn vị thử, population, KPI/guardrail, baseline, window, budget, stop rule và decision evidence. Khi định lượng cần thiết kế sample/contamination/time horizon thích hợp, không đổi chỉ số sau khi thấy kết quả. 100 lead agency ít không suy mọi campaign khách cũng ít mẫu; thiếu mẫu ghi chưa kết luận, không ép winner.

Learning có source, owner, confidence/limitations, ngày áp dụng và scope quyền. Root cause từ CX nối cải tiến checklist/strategy; không sao creative/data khách A sang B trái quyền. P0/P1 mẫu và decision log nhẹ; experiment orchestration nâng cao P2.''',
'FR25': '''P0 quản milestone/deliverable, owner/reviewer, due, QA, acceptance và dependency thiết yếu. Task nội bộ khác đầu ra khách mua. Chọn PMS hoặc CRM module làm nguồn ghi task duy nhất; đồng bộ external ID/version/status, không hai master ghi đè.

Capacity có skill/calendar/availability, soft reservation trước chốt lớn và allocation sau kickoff; việc vắng mặt/khách chờ không tự thành KPI yếu. Khi cần task chi tiết: estimate/actual, definition of done, dependency không cycle, reviewer/evidence. Timesheet chỉ bật khi cần tính cost/capacity và lợi ích hơn nhập liệu; có thể dùng summary cost kiểm tra ở giai đoạn nhỏ. Rework do defect khác change; đổi scope đánh giá date/resource/cost và approval.''',
'FR26': '''Tách agency acquisition spend, agency service economics, client media spend và client business outcomes bằng namespace/scope/beneficiary. Budget line có owner, cost bearer, funding/credit, category, currency, tax basis, kỳ và approval. Available = approved − actual − outstanding commitment khi cùng basis; commitment chuyển actual chỉ giảm phần được thay thế, không cộng đôi. Estimate to complete/contingency ghi riêng và tránh trừ lại phần đã nằm trong commitment.

Theo dõi estimated/committed/actual cost, cost-to-complete và margin-at-completion có nguồn. Thiếu cost không coi0. Pacing theo flighting; health tách financial/delivery/relationship/outcome, có component/version/freshness và action owner. Data stale là Unknown/Degraded; CPL tăng là tín hiệu điều tra, không tự tắt kênh thiếu bằng chứng. Phép chi media xét tiền được phép dùng/credit và độ trễ spend, không dùng toàn bộ số dư ngân hàng cho mọi khách.''',
'FR27': '''P0 giữ membership, org/team/branch, delegation; availability và cost rate theo effective date khi phục vụ capacity/margin. Payroll, lương cá nhân, tuyển dụng, bệnh lý/bảo hiểm và chấm công HR thuộc hệ khác, không đưa Customer360.

Scorecard nhân sự ở P2 khi có mục tiêu/owner/dữ liệu đủ; không áp trọng số25/30/20/25 như chuẩn. Từng role có metric/đơn vị/bối cảnh project mix/quality/client-wait và quyền giải trình; thiếu dữ liệu không xếp hạng, không suy nhân quả cá nhân từ hiệu quả campaign. Không tự phạt vì thiếu thao tác hoặc AI dự báo burnout/nghỉ việc.''',
'FR28': '''Metric contract có code/namespace, mục đích/quyết định, formula/grain, scope/beneficiary, event time/processing time, timezone/currency/tax basis, source, owner, exclusions, version, freshness và mẫu số. P0 chọn bộ ít metric chốt định nghĩa trước dashboard. MQL/SAL/SQL dùng demand episode và transition history; no-capacity không bị gộp invalid/no-fit.

Tracking plan có event schema, trigger/ID/required fields, legal purpose, late event và correction policy. Source IDs/UTM không chứa PII trong URL; email open không chứng minh intent. Data quality errors có owner/hạn sửa; definition thay đổi giữ snapshot đã công bố và restatement trace. Payment/invoice/cost khác basis phải ghi rõ, không cùng gọi chung doanh thu.''',
'FR29': '''P0 lưu source event/IDs, UTM có quyền và nguồn tự khai riêng. First-touch/last-touch là hai model báo cáo riêng theo demand/outcome, không cộng. Window90 ngày là giả định cần theo sales cycle; quy định first từ quan hệ hay nhu cầu, last xử lý Direct ra sao. Unknown do thiếu tracking khác Direct/Organic; giữ coverage.

Touchpoint→identity→account role có hiệu lực→demand/deal→outcome với model version/currency/value basis. Không gán mọi doanh thu account cho mọi contact. Tổng credits mỗi outcome/model không vượt1, phần thiếu Unknown; multi-touch P2. Refund/late events điều chỉnh có version, giữ báo cáo cũ. Platform Google/Meta có thể claim cùng outcome, không cộng thành thực thu; attribution không chứng minh incrementality.

P1 một connector CRM→Meta qualified/outcome sau PoC: canonical event→purpose/ACL→dataset/ad account binding đúng workspace→outbox→receipt/reconcile. Won khác Paid; đổi stage không tạo nhiều purchase; correction/refund theo khả năng API thực tế. Sent/accepted khác matched/attributed; hash không thay quyền chia sẻ. Không xuất tệp khách A sang dataset B hoặc dùng tìm khách agency. Có token owner, latency/error/coverage và kill switch.'''
}

for fr, body in fr_content.items():
    heading = re.search(rf'(?m)^#### [^\n]*\b{fr}\b[^\n]*', text)
    if not heading:
        raise ValueError(fr)
    section(heading.group(), body)

# The original table FR30–40 becomes explicit requirements in the same chapter.
omni_table = re.search(r'(?m)^\| Mã \| Yêu cầu bắt buộc \| Tiêu chí nghiệm thu \|\n\| ---.*?(?=^#### Identity resolution)', text, re.S)
assert omni_table
omni = []
for i in range(30, 41):
    fr = f'FR{i:02}'
    row = fr_rows[fr]
    label = row[0].split(' — ')[0]
    omni.append(f'#### 3.12.{i-29} {label}\n\n{row[3]}\n')
text = text[:omni_table.start()] + '\n\n'.join(omni) + '\n\n' + text[omni_table.end():]

# Each FR carries its own rationale, owner/dependencies and acceptance criterion.
for i in range(1, 41):
    fr = f'FR{i:02}'
    row = fr_rows[fr]
    heading = re.search(rf'(?m)^#### [^\n]*\b{fr}\b[^\n]*', text)
    assert heading, fr
    meta = (f'\n\n**Mục đích và trách nhiệm:** {row[0]}. {row[1]}.\n\n'
            f'**Liên kết đầu vào → đầu ra:** {row[2]}.\n\n'
            f'**Nghiệm thu và giai đoạn:** {row[4]}.')
    text = text[:heading.end()] + meta + text[heading.end():]

replace('State machine: `new → queued → assigned → open → pending_customer/pending_internal → resolved → reopened`. Chuyển pending cần reason, due_at, next owner; không cho đóng chỉ để né SLA. First-response SLA và resolution SLA là hai clock khác; policy quy định rõ trạng thái nào được pause. Tin mới sau resolved tạo reopen episode hoặc conversation mới theo rule có version, không sửa ngược KPI lịch sử.',
'''Conversation tách `status=open/resolved/closed`, `waiting_party=agent/customer/internal/none` và assignment/queue. Reopen là event mở episode theo policy version. Pending cần reason, due và next owner; không đóng để né SLA. First/next-response, resolution và promised update là các clock khác, theo subject/episode. Năm tin khách chưa được đáp không lùi hạn từ tin chưa đáp đầu; chuyển nhóm không reset; bot/note không hoàn thành phản hồi người thật.''')
replace('Routing ưu tiên workspace/branch/skill rồi ca và capacity, sau đó sticky assignment nếu còn hợp lệ. Claim dùng compare-and-swap/row lock; hai người nhận cùng lúc chỉ một thành công. Chuyển ca cần handoff note, lịch sử assignee và task tiếp theo. Supervisor có override kèm lý do; không tự đổi người sở hữu Deal và hoa hồng chỉ vì người trực inbox trả lời.',
'''Routing kiểm hard scope/quyền/skill trước; owner hợp lệ được ưu tiên continuity rồi availability/backup và capacity theo policy. Claim CAS/row lock; durable assignment có version đủ cho MVP. Nếu dùng lease phải có expiry/renew/fencing, kiểm khi gửi để tab cũ không vượt quyền. Chuyển ca bàn giao note, promises, due và open work; supervisor override có lý do. Conversation assignee khác Deal owner là hợp lệ; không tự đổi commission. Typing indicator chỉ là UX, không thay idempotency/authorization.''')
replace('Một assignee đang giữ lease; owner Contact/Deal có thể khác assignee Conversation; nghỉ việc bàn giao được',
        'Một assignment active có version; owner Contact/Deal có thể khác assignee Conversation; nghỉ việc bàn giao được', count=0) if False else None

# Cross-functional lifecycle, obligations, metrics and operating contracts are embedded.
flow = review_section(3)
flow = flow.replace('### 3.1 ', '#### 3.13.1 ').replace('### 3.2 ', '#### 3.13.2 ')
contracts = review_section(8)
insert_before('<a id="chuong-4"></a>', '### 3.13 Hành trình khách hàng và hợp đồng bàn giao xuyên module\n\n' + flow + '\n\n#### 3.13.3 Quy tắc liên kết và tác động bắt buộc\n\n' + contracts)

# Update each original UC in place, preserving the useful detail and adding traceability.
for i in range(1, 23):
    uc = f'UC{i:02}'
    heading = re.search(rf'(?m)^### 4\.[^\n]*\b{uc}\b[^\n]*', text)
    assert heading, uc
    start = heading.end()
    end_match = re.search(r'(?m)^### |^<a id="chuong-5"', text[start:])
    end = start + end_match.start()
    body = text[start:end].rstrip()
    row = uc_rows[uc]
    body += f'\n| Quy tắc liên kết bắt buộc | {row[1]}; FR liên quan: {row[2]}. |\n\n'
    text = text[:start] + body + text[end:]

replace('Discovery → chọn B2B/B2C → thu trường bắt buộc → kiểm trùng deal đang mở → chuyển Qualified → tạo deal và buying group nếu B2B',
        'Nhận/Accepted lead → discovery nhu cầu → B2B/B2C → thu trường tối thiểu/Unknown → kiểm trùng theo nhu cầu → Qualified → tạo/link Deal idempotent và đầu mối buying group tối thiểu nếu B2B')
replace('một contract chỉ sinh một project từ cùng handoff event.',
        'replay cùng handoff/SOW không tạo thêm project; một MSA có nhiều SOW/project hợp lệ.')
replace('Verify → dedup provider transaction → match reference → kiểm amount/currency → allocate → ledger receipt → commission preview → kế toán duyệt cuối kỳ',
        'Verify và lưu evidence → reconcile canonical receipt xuyên nguồn → ghi nhận tiền → match buyer/nghĩa vụ → kiểm currency/legal entity/số dư → allocate/outbox → invoice mapping khi có → preview → kế toán duyệt cuối kỳ')
replace('QA nội bộ → gửi review → nhận phản hồi → phân loại defect/change → sửa trong vòng cho phép hoặc CR → nghiệm thu → milestone billing',
        'QA nội bộ → review đúng version → phân loại defect/change → defect sửa theo cam kết, đổi ý theo quota/CR → acceptance có authority → billing/collection theo nghĩa vụ áp dụng')
replace('Tạo ticket → severity → SLA → xác minh → giải quyết → khách xác nhận/đóng theo policy → survey → phân tích điểm',
        'Intake/provisional khi cần → entitlement/impact/urgency → SLA subject/episode → xác minh/giảm thiểu/cập nhật → resolution evidence → đóng/reopen đúng policy → survey đủ điều kiện → recovery/root cause/verify')
replace('Hợp đồng còn 45 ngày, health data đủ',
        'Hợp đồng đến mốc review/notice theo điều khoản và lịch tương lai; health có nguồn hoặc Unknown được AM rà soát')

# Unified workspace naming. Client_Workspaces is an old schema name, not a second entity.
text = text.replace('client_workspace_id', 'workspace_id').replace('Client_Workspaces', 'Workspaces')
text = text.replace('FK client_workspaces, NULL | NULL cho dữ liệu agency; có giá trị cho xử lý thay khách',
                    'FK Workspaces, NN với dữ liệu scoped | Workspace AGENCY/CLIENT; không dùng NULL để biểu diễn agency')
replace('Mỗi bảng nghiệp vụ mutable có các trường chung trong bảng sau; bảng ledger/log bất biến chỉ dùng id, tenant_id, created_at, created_by và scope cần thiết, không có cập nhật/xóa thường xuyên. Mọi bảng đều có UNIQUE(tenant_id,id) để FK ghép tham chiếu. Schema dưới là baseline thiết kế, chưa phải migration SQL đã chạy.',
'''Bảng nghiệp vụ scoped có trường chung dưới đây; catalog cấp tenant có ngoại lệ được khai báo, không ép Workspaces/Tenants tự tham chiếu workspace. Mỗi bảng đích có UNIQUE(tenant_id,id), và bảng scoped có UNIQUE(tenant_id,workspace_id,id) để FK ghép. Ledger giữ số tiền/policy bất biến; trạng thái workflow là projection từ status events. Schema là dictionary triển khai cần xuất DDL/OpenAPI và kiểm thử trước production; không có hai bộ tên bảng cho cùng thực thể.

Workspaces có loại AGENCY/CLIENT; tên cũ `client_workspace_id`/`Client_Workspaces` của v1.2 chỉ là mapping migration, không là cột/bảng mới song song. Dữ liệu chưa phân loại giữ ở intake/quarantine có scope xác định, không tự gán NULL để bypass quyền. Cross-scope link hợp lệ (CLIENT workspace → Account trong AGENCY) dùng relation rõ và quyền/publish tối thiểu; không áp same-workspace một cách mù lên liên kết đó.''')
replace('| branch_id | uuid | FK branches, NULL theo miền | Phạm vi chi nhánh, không thay tenant |',
        '| branch_id | uuid | FK Branches; bắt buộc nếu giao dịch được phân nhánh | Phạm vi vận hành; shared catalog/account theo grant, không thay pháp nhân |\n| legal_entity_id | uuid | FK Legal_Entities, NN cho hợp đồng/tài chính | Bên ký/hạch toán/nhận tiền; giữ một pháp nhân mặc định khi pilot |')
text = text.replace('  Contacts ||--o{ Leads : originates', '  Contacts ||--o{ Leads : identifies_demand')
replace('  Invoice_Lines ||--o{ Payment_Allocations : settled_by',
'''  Orders ||--o{ Order_Lines : itemizes
  Order_Lines ||--o{ Payment_Obligations : schedules
  Payment_Obligations ||--o{ Payment_Allocations : receives
  Payment_Allocations ||--o{ Invoice_Allocation_Links : reconciles
  Invoice_Lines ||--o{ Invoice_Allocation_Links : maps''')
replace('| contact_id | uuid | FK Contacts, NULL lúc intake | Gắn sau identity resolution |',
        '| contact_id | uuid | FK Contacts, NN khi tạo Lead nghiệp vụ | Intake event lưu trước; tạo/link contact provisional cùng transaction khi cần consent/Lead |')
replace('New/Assigned/Contacting/Qualified/Nurture/Disqualified/Converted',
        'New/Assigned/Contacting/Qualified/Nurture/Dormant/Disqualified/Converted')
replace('| sla_due_at | timestamptz | NULL khi chưa assigned | Hạn theo lịch làm việc |',
        '| sla_due_at | timestamptz | Projection từ SLA_Episodes | Hạn obligation theo policy/subject; không reset khi đổi owner |\n| handover_status / handover_policy_version | text | Pending/Accepted/Rejected/Recycled; policy version | MQL/SAL/SQL và reason/evidence trong Lead_Transitions |\n| previous_lead_id / demand_key | uuid / text | FK Leads NULL; scoped demand key | Liên kết nhu cầu quay lại; không dùng để tự merge người |')
replace('| lifecycle_stage | varchar(30) | NN | Subscriber/Lead/Customer/Inactive |',
        '| lifecycle_stage | varchar(30) | NN | Subscriber/Lead/Customer/Inactive; khác trạng thái nhu cầu |\n| identity_status | varchar(30) | NN | Provisional/Verified/Conflict; không trộn vào lifecycle |')
replace('| closed_at | timestamptz | NULL | Thời điểm Won/Lost |',
        '| closed_at | timestamptz | NULL | Thời điểm Won/Lost, có stage history |\n| hold_reason / review_at / previous_deal_id | text / timestamptz / uuid | Bắt buộc lý do/hẹn nếu OnHold; lineage FK NULL | Giữ total age/active time; không clone làm đẹp cycle |')
replace('Draft/Confirmed/InDelivery/Completed/Cancelled', 'Draft/Confirmed/InDelivery/Completed/Cancelled/Terminated')
replace('Unpaid/Partial/Paid/Refunded projection', 'Unpaid/Partial/Paid/PartialRefund/Refunded projection; Completed/Terminated không tự Paid')
replace('| actor_id | uuid | FK Users, NN | Người thực hiện/service |',
        '| actor_id | uuid | FK Users/service principal, NN | Người thực hiện/service |\n| source_channel_identity_id / origin_contact_id | uuid | FK scoped NULL theo nguồn | Provenance để merge/unmerge và trace hoạt động |')
replace('| priority | varchar(4) | NN P1/P2/P3 | Theo ma trận |',
        '| severity | varchar(4) | NN S1/S2/S3 | Impact × urgency theo entitlement, khác priority backlog P0/P1/P2 |\n| entitlement_snapshot_id / business_subject_id | uuid | FK Entitlement_Snapshots / Business_Subjects | Scope/SLA/quyền hỗ trợ và subject chuẩn |')
replace('| first_response_due_at | timestamptz | NN | SLA phản hồi |\n| resolution_due_at | timestamptz | NN | SLA giải quyết |',
        '| first_response_due_at / next_response_due_at / resolution_due_at | timestamptz | Projection từ SLA engine; NULL nếu không áp dụng | Các clock độc lập, giữ breach history |\n| next_customer_update_at / impact / urgency | timestamptz / text / text | Theo incident/promise policy | Nhịp cập nhật và phân loại tác động |')
replace('| purpose_code | varchar(80) | NN | Mục đích cụ thể |',
        '| purpose_code | varchar(80) | NN | Mục đích cụ thể |\n| contact_point_id / source_channel_identity_id / origin_contact_id | uuid | FK Contact_Points/Channel_Identities/Contacts; NULL có semantics rõ | Endpoint cụ thể hoặc contact-wide scope; provenance không mất khi merge |')

section('### 5.10 Bảng Payments', '''Payment là giao dịch canonical; evidence nguồn được lưu riêng. Số tiền đã xác thực không biến mất khi chưa match.

| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| legal_entity_id / bank_account_id | uuid | FK Legal_Entities/Bank_Accounts, NN | Chủ thể và tài khoản nhận/chi; cùng tenant |
| amount / currency / direction | numeric(18,2) / char(3) / text | amount>0; In/Refund | Số gốc; không phân bổ chéo currency ngầm |
| payer_ref / buyer_account_id / buyer_contact_id | text / uuid / uuid | NULL khi unidentified; FK scoped | Người trả có thể khác người mua, cần case xác minh |
| verification_state / confirmed_at | text / timestamptz | Pending/Confirmed/Rejected; timestamp theo evidence | Xác thực tách matching |
| matching_state | text | Unidentified/Identified/Ambiguous | Không thay verification_state |
| allocation_state / reconciliation_state | text | Projection; Unallocated/Partial/Full và Open/Reconciled/Disputed | Theo allocation ledger/case |
| reference / bank_transaction_ref | text | Theo namespace tài khoản/provider | Candidate dedup, không fingerprint unique toàn cục |
| original_payment_id | uuid | FK Payments NULL cho khoản gốc | Refund/reversal liên kết; partial refund không phủ toàn giao dịch |

Payment_Evidence giữ connector/provider_transaction_id, sao kê dòng nào, verified_by/at, raw ref, payment_id và mapping version. Unique nguồn ở evidence; một Payment nhiều evidence. Kế toán xác nhận canonical match xuyên nguồn, giữ audit khi mơ hồ.''')

section('### 5.11 Bảng Payment_Allocations', '''| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| payment_id | uuid | FK Payments, NN | Giao dịch canonical đã xác thực |
| obligation_id | uuid | FK Payment_Obligations, NN | Đích nghĩa vụ/kỳ/dòng order xác định; không rỗng |
| amount / currency | numeric(18,2) / char(3) | >0; khớp payment/nghĩa vụ | Lock tổng hiệu lực không vượt tiền hoặc nghĩa vụ |
| eligible_service_net / tax_component / media_component | numeric(18,2) | >=0; decomposition theo policy version | Cơ sở commission, không tự coi toàn tiền là service |
| allocation_policy_version | text | NN | Điều khoản/kỳ được duyệt hoặc quyết định Finance |
| entry_type / reverses_id | text / uuid | Allocate/Reverse; FK gốc nếu Reverse | Append-only, không đảo quá phần còn hiệu lực |
| idempotency_key | text | Unique trong tenant/workspace | Replay cùng command một effect |

Invoice_Allocation_Links liên kết allocation với invoice line và mapped amount, có điều chỉnh/đảo/audit. Invoice sync đến sau chỉ bổ sung mapping, không thêm allocation/cash/commission. Bỏ phụ thuộc `invoice_line_id NOT NULL` khỏi allocation; không thay bằng đích tùy ý rỗng. Không phân bổ qua pháp nhân/party/currency/scope nếu chưa có nghiệp vụ chuyển hợp lệ.''')

section('### 5.12 Bảng Commission_Entries', '''| Trường | Kiểu | Khóa và ràng buộc | Mô tả |
| --- | --- | --- | --- |
| allocation_id / user_id | uuid | FK Payment_Allocations/Users, NN | Gốc cash đủ điều kiện và người hưởng |
| pool_id / policy_snapshot_id | uuid | FK Commission_Pools/Policy_Snapshots, NN | Tách pool, truy được policy version/effective date |
| base_amount / rate / share | numeric | Base>=0; rate/share theo policy | Không gồm phần media/thuế/write-off ngoài base được phép |
| amount / currency / rounding_policy | numeric / char(3) / text | NN | Giá trị bất biến sau posting |
| entry_type / reverses_id / period_id | text / uuid / uuid | Base/Reverse; FK gốc/kỳ | Reversal không vượt phần được đảo; kỳ khóa có adjustment |
| entry_key | text | Unique tenant/workspace/allocation/user/pool/policy/type/operation | Chống replay, hỗ trợ partial reversals khác operation |

Commission_Status_Events lưu Preview/Approved/Earned/Payable/Paid/Reversed theo policy; trạng thái hiện tại là projection, không sửa amount gốc. Payout_Batches/Payout_Links lưu chi thực tế và phần đã trả. Commission_Adjustments cho quality bonus/điều chỉnh có reason/evidence/authority; không dùng quality_factor chưa đo làm tiền chắc được hưởng. Tổng share=1 trong pool và version áp dụng; attribution lịch sử độc lập owner hiện tại.''')

# Remove obsolete schema definitions, not their conceptual information.
text = re.sub(r'(?m)^\| (?:Identities|Merge_Events|Conversations, Messages) \|[^\n]*\n', '', text)
replace('| Workspaces | client_account_id uuid, controller_name text, processing_scope text | Mỗi workspace chỉ xử lý đúng khách được giao; có DPA/ủy quyền. |',
        '| Workspaces | workspace_type AGENCY/CLIENT, client_account_id uuid NULL, controller_name text, processing_scope text | Một AGENCY mặc định/tenant; CLIENT gắn account agency qua link có kiểm quyền; có ủy quyền/DPA phù hợp. |')
replace('Approved snapshot immutable; line_type tách service/media/tax.',
        'Approved snapshot immutable; line_type SERVICE/PRODUCTION/MEDIA_PASS_THROUGH, tax code/net/tax/gross là cấu phần riêng.')
replace('| Contracts, SOW_Versions | quote_id uuid, signer_contact_id uuid, status text, signed_asset_id uuid, sow_version int | Chứng cứ ký và version; ngày kết thúc không trước bắt đầu. |',
        '| Contracts, SOW_Versions | accepted_quote_id uuid NULL, parent_contract_id uuid NULL, document_type text, service_model text, legal_entity_id uuid, signer_contact_id uuid, status text, signed_asset_id uuid, revision int | MSA nhiều SOW/order/project; authority/effective conditions; notice/termination/settlement riêng; quote bổ sung gắn hợp đồng gốc. |')
replace('| Projects, Deliverables, Acceptances | contract_id uuid, owner_id uuid, deliverable_type text, due_at timestamptz, asset_version_id uuid, accepted_by uuid | Acceptance trỏ đúng version và evidence; reject reason bắt buộc. |',
        '| Projects, Deliverables, Acceptances | contract_id/sow_version_id uuid, handoff_key text, owner_id uuid, planned/committed_due_at timestamptz, asset_version_id uuid, accepted_by uuid, max_revisions/used_revisions int | Unique handoff effect không unique contract; batch sửa/defect khác quota; client-wait intervals; acceptance đúng version/authority. |')
replace('Phân bổ tiền và hoa hồng phải chạy trong transaction: khóa payment/invoice balance, kiểm tổng, insert allocation, insert outbox, commit. Unique entry_key ở commission là chốt chống replay. Foreign key ghép tenant_id ngăn liên kết vô tình qua tổ chức. Với workspace NULL, dùng quy tắc unique có NULLS NOT DISTINCT hoặc partial index phù hợp; không giả định unique nullable mặc nhiên chống trùng.',
'''Phân bổ tiền chạy trong transaction: khóa canonical payment và obligation balance, kiểm tổng hiệu lực, insert allocation/outbox, commit. Consumer commission idempotent theo allocation/pool/policy/operation; không giả exactly-once giữa hệ thống. FK ghép tenant/workspace áp dụng dữ liệu scoped; cross-scope relations được khai báo riêng và kiểm quyền. workspace_id của dữ liệu scoped không NULL. Các thuộc tính optional khác có unique nullable phải dùng NULLS NOT DISTINCT/partial index khi semantics cần, không giả NULL tự chống trùng. Không giữ DB lock khi gọi provider ngoài.''')
replace('| Conversations | inbox_id uuid FK; channel_identity_id uuid FK; provider_thread_id text NULL; status varchar(30); assignee_id uuid FK NULL; team_id uuid FK; opened_at timestamptz; last_message_at timestamptz NULL; source_mode varchar(20) |',
        '| Conversations | inbox_id uuid FK; connection_id uuid FK; channel_identity_id uuid FK; provider_thread_id text NULL; status open/resolved/closed; waiting_party agent/customer/internal/none; assignee_id uuid FK NULL; team_id uuid FK; opened_at timestamptz; last_message_at timestamptz NULL; source_mode varchar(20) |')
replace('| Message_Status_Events | message_id uuid FK; provider_event_id text;',
        '| Message_Status_Events | message_id uuid FK; connection_id uuid FK; provider_event_id text;')
replace('| SLA_Episodes | conversation_id uuid FK; policy_version text; clock_type varchar(30); started_at timestamptz; due_at timestamptz; stopped_at timestamptz NULL; pause_intervals jsonb; outcome varchar(20) | first_human_response và resolution là episode khác; chuyển nhóm không tạo clock mới; calendar/timezone có version |',
        '| SLA_Episodes | business_subject_id uuid FK NN; waiting_episode_key text; start_event_id/completion_event_id uuid; policy/calendar_version text; clock_type text; started_at/due_at timestamptz; stopped_at/breach_at timestamptz NULL; pause_intervals jsonb; exception_ref uuid NULL; outcome text | Subject typed và FK thật; claim/attempt/FRT/NRT/resolution/promised_update độc lập; một clock nguồn chuẩn, deadline Lead/Ticket projection; chuyển nhóm không reset |')

insert_before('<a id="chuong-6"></a>', '''### 5.18 Dữ liệu bổ sung cho liên kết nghiệp vụ 1.3

Các bảng logic có thể ánh xạ capability của nền tảng được chọn; không bắt tạo mọi bảng độc lập. Khi triển khai phải có schema/FK/version thật, không generic JSON để né isolation. Bảng ở P1/P2 chỉ tạo khi module mở.

| Miền / đối tượng | Dữ liệu tối thiểu | Ràng buộc và phạm vi |
| --- | --- | --- |
| Legal_Entities, Bank_Accounts | legal name/tax identity, currency, account ref, authority | Pháp nhân ký/nhận tiền; mặc định một khi pilot; secret không ở field thường |
| Contact_Points, Identity_Links | contact_id, loại/endpoint encrypted+lookup hash, verified/status/effective dates, origin refs | Endpoint vs người tách; hotline/shared không unique toàn cục; provenance sau merge |
| Lead_Transitions, Deal_Stage_History | entity_id, from/to, occurred/received, policy, actor, reason/evidence, hold interval | MQL/SAL/SQL/handover history; không sửa cohort/aging bằng ghi đè |
| Entity_Team_Grants | contact/account/deal/project/ticket FK typed, user/team, role, field/actions, from/until | Mỗi grant đúng một resource; deny-wins theo policy; B2C không cần Account |
| Order_Lines | order_id, line_type, approved revision, net/tax/gross, currency, service period | Phiên bản loại phí/cost; khác Invoice_Lines gốc ERP |
| Payment_Schedules, Payment_Obligations | order_line_id, schedule_id, due_at, net/tax/gross/currency, policy, remaining projection | Mỗi obligation chỉ thuộc một dòng order/kỳ; tổng nghĩa vụ theo bản hợp đồng còn hiệu lực |
| Payment_Evidence, Reconciliation_Cases | payment_id NULL khi unresolved, connector/event ID, raw ref, verification, proposed match, owner/due/resolution | Một receipt nhiều evidence; cùng source unique; không tự dedup theo amount/text |
| Invoice_Allocation_Links | allocation_id, invoice_line_id, mapped amount, entry_type/reversal, actor/evidence | Mapping không ghi receipt/commission lần nữa; tổng mapping không vượt phần tương ứng |
| Commission_Pools, Policy_Snapshots, Commission_Status_Events, Payout_Batches/Links, Commission_Adjustments | pool/version/effective rules, status evidence, amount paid, adjustment reason | Share/payout số dư đúng; freeze policy; không UPDATE tiền gốc |
| Business_Subjects | lead_id NULL, ticket_id NULL, conversation_id NULL; subject_type | CHECK đúng một FK NN và unique scoped theo resource; FK tenant/workspace; subject là cầu SLA/link, không chứa status thay nghiệp vụ |
| Conversation_Subject_Links | conversation_id, business_subject_id, purpose, actor/evidence/effective dates | Quan hệ N:M có quyền; Subject của Deal/Project nếu cần dùng link table typed riêng, không giả FK generic |
| Entitlement_Snapshots, Customer_Promises | contract/SOW/version, support calendar/rules, authority; subject/promise owner/due/source | Tại thời điểm áp dụng; hết quota không chặn complaint intake; update promise có lịch sử |
| Success_Plans, Feedback, Recovery_Cases, Corrective_Actions | project/account/role, baseline/target/first-value, score/question version, recovery owner/due/remedy/evidence | Verify khác no-contact; giữ score gốc; theme cải tiến không chia sẻ data trái workspace |
| Client_Wait_Intervals, Revision_Batches | deliverable/version, requested/answered_at, reason, feedback_batch, defect/change | Không cộng trùng interval; không tự dời contractual date; lỗi khác quota đổi ý |
| Media_Funding_Authorizations | contract/line/budget, funding receipt/credit policy, cap/expires, committed/actual/freshness | Phép chi riêng kickoff; không dùng tiền khách khác; thiếu spend data ghi degraded |
| Outcome_Events, Platform_Export_Intents | demand/deal/outcome ID/version/value basis, source IDs, dataset binding, purpose/policy, receipt | Closed-loop P1; scope mismatch chặn; refund/correction theo provider capability |

`Inbound_Events` là canonical durable inbox cho kênh; `Webhook_Inbox` ở 5.13 là tên năng lực chung, ánh xạ cùng ingestion registry thay vì tạo hai consumer nhận cùng payload. Outbox vẫn là hướng phát sự kiện. Consent_State chỉ projection; permission/suppression kiểm tại dispatch. FK start/completion event và provenance phải trỏ canonical event registry hoặc source typed được kiểm transaction khi xuất DDL.
''')

insert_before('### 6.2 Bảo vệ dữ liệu và chống thất thoát', '''Account/Contact/Deal/Project grants được kiểm cùng role và độ nhạy cảm; chia sẻ Account không tự cho đọc tài chính agency hay toàn CLIENT workspace. Policy Deny-wins phải được test trên nền tảng thật (EspoCRM có semantics gộp quyền rộng hơn theo tài liệu tham khảo). Kiểm quyền object/action/field ở API, search/count/snippet, file, export, BI và AI; cache/index có permission version và revoke propagation. Job kiểm authority hiện tại khi thực thi, không chỉ lúc enqueue. RLS role thật không owner/BYPASSRLS, tenant context reset/transaction-scoped khi dùng pool. MFA và quản lý phiên theo rủi ro; break-glass có mục đích/TTL/audit.''')

insert_before('### 8.3 Kiểm soát sai số và phân tích', '''Bốn scope đo lường tách: acquisition cost của agency; service economics agency; client media spend; client business outcome. CAC agency không dùng media khách; doanh số khách không thành doanh thu agency. Metric lưu grain, time/currency/tax basis, beneficiary và freshness. Unknown do thiếu nguồn khác Direct/Organic. MQL/SAL/SQL theo demand episode/transition, không đếm acquisition lại khi recycle. LTV quan sát khác dự báo lifetime; cohort tuổi khác nhau cần cùng cửa sổ quan sát. Sales cycle báo total/active/hold và open aging; không clone hoặc OnHold làm đẹp tỷ lệ. Renewal/expansion/contraction/churn theo recurring model; one-off đủ điều kiện tái ký riêng.

Health theo financial/delivery/relationship/outcome component có nguồn, missing là Unknown; kết quả phải dẫn action owner. Survey response rate nêu eligible/sent/delivered; NPS contact và account view nêu weight/role. Restore/restate giữ snapshot đã công bố. First/last và platform-attributed views riêng, không cộng các model thành tổng tiền.''')

# Remove remaining contradictory operational defaults from roadmap and old summaries.
text = text.replace('P1: OA/Meta/VoIP được phê duyệt, payment API, đồng bộ kế toán, strategy/IMC đầy đủ, workload và KPI library. P2: Mini App, loyalty/referral, experiments nâng cao, multi-touch, AI STT và scoring dự báo có đánh giá.',
'''P1 theo nhu cầu: connector kế toán/PMS/calendar/spend, workload, referral nhẹ, health/NPS và một closed-loop CRM→Meta đã PoC; AI draft/STT khi đo đạt. P2: Mini App/loyalty, strategy editor đầy đủ, experiment engine, multi-touch, predictive scoring và scorecard nhân sự. FR guard tiền/quyền/consent/AI phải đạt trước bật chức năng tương ứng.''')
text = text.replace('cấu hình strategy/IMC gọn; restore drill', 'kiểm chuỗi brief/SOW/approval và bàn giao; restore drill')
text = text.replace('Đợt triển khai cá nhân ưu tiên form + một mailbox + OA hoặc Facebook đã đủ quyền.',
                    'Đợt triển khai cá nhân ưu tiên một nguồn lead và một kênh giao tiếp đã đủ quyền; không mặc định bật cùng mailbox/OA/Facebook.')
text = text.replace('lịch sử activities vẫn', 'lịch sử activities vẫn')
text = text.replace('Unknown/Direct', 'Unknown và Direct tách riêng')
text = text.replace('Contacts, Accounts, Identities, Consent', 'Contacts, Accounts, Channel_Identities, Consent')
text = text.replace('Chuyển thành tenant/branch/business line/client workspace', 'Chuyển thành tenant/workspace/branch/legal entity')

uat_body = review_section(10)
uat_body = re.sub(r'^Các ca dưới.*?\n\n', '', uat_body, flags=re.S)
insert_before('<a id="chuong-10"></a>', '''### 9.10 UAT tích hợp xuyên module phiên bản 1.3

Các ca sau bổ sung U01–24 và OC01–24, không thay test cũ còn áp dụng. Kết quả chưa chạy; mỗi ca có fixture/expected/actual/evidence/owner. P0 của luồng đã bật phải qua trước go-live.

''' + uat_body + '\n\n### 9.11 Nhịp điều hành và điều kiện ký nghiệm thu\n\n' + re.search(r'### 12\.3 Nhịp vận hành\n(.*?)(?=### 12\.4)', review, re.S).group(1).strip() + '\n\n' + review_section(13))

# Integrate each specialist's detailed test set in the master, rather than requiring annex reading.
specialist_tables = []
for name, label, pattern in [
    ('RESEARCH_CEO_CRM_2026-10-15.md', 'Tài chính và CEO', r'^\| CEO-U\d'),
    ('RESEARCH_CMO_CRM_2026-10-15.md', 'Marketing và CMO', r'^\| M\d{2} \|'),
    ('RESEARCH_CX_CRM_2026-10-15.md', 'Dịch vụ và CX', r'^\| CX-U\d'),
]:
    src = (ROOT / name).read_text(encoding='utf-8-sig')
    lines = src.splitlines()
    starts = [i for i,l in enumerate(lines) if re.match(pattern,l)]
    assert starts
    first, last = min(starts), max(starts)
    table = '\n'.join(lines[first-2:last+1])
    specialist_tables.append('#### ' + label + '\n\n' + table)
insert_before('<a id="chuong-10"></a>', '### 9.12 Ca nghiệm thu chuyên sâu theo vai trò\n\n76 ca chuyên đề sau có giao nhau với bộ INT; không tính như các bằng chứng độc lập hoặc kết quả đã pass. Chọn ca theo module/giai đoạn triển khai, đối chiếu và gộp test case ID khi lập test plan.\n\n' + '\n\n'.join(specialist_tables))

replace('### A.3 Những phần tốt được giữ hoặc bổ sung',
        '### A.3 Những phần tốt được giữ hoặc bổ sung\n\nBảng A.3–A.4 lưu lý do kế thừa nguồn từ các vòng trước; phạm vi/field/giai đoạn hiện hành theo Chương 3/5/9 phiên bản 1.3. Các quyết định trong nguồn cũ không ghi đè baseline mới.')
replace('Bản kế tiếp chỉ cập nhật các điểm thay đổi, giữ lịch sử quyết định và version.',
        'Mọi cập nhật tiếp theo thực hiện trong đúng tệp Master duy nhất, tăng version và giữ lịch sử quyết định. Không yêu cầu người dùng đọc các báo cáo nguồn để hiểu baseline hiện hành.')
replace('Đây là baseline tài liệu hoàn chỉnh để thiết kế/ước lượng và nghiệm thu, chưa là chứng nhận hệ thống đã triển khai.',
        'Phiên bản 1.3 đã tích hợp các kết luận rà soát vào phần thân; đây là tài liệu thiết kế/ước lượng/nghiệm thu, chưa là chứng nhận hệ thống đã triển khai.')

decisions = review_section(11)
decisions = decisions.replace('Backlog quyết định và ưu tiên sửa SRS', 'Quyết định đã hợp nhất')
decisions = decisions.replace('CR01–12 cần quyết định trước khi phát triển phần tương ứng;',
                              'CR01–12 đã được tích hợp ở cấp quy tắc thiết kế trong phiên bản 1.3; tham số và cấu hình thực tế cần chốt trước khi phát triển phần tương ứng;')
sources = review_section(7)
sources = sources.replace('### 7.1 Nguồn chuyên môn bổ sung và ý nghĩa', '### E.4 Nguồn chuyên môn bổ sung và ý nghĩa')
sources = sources.replace('ở mục 6.', 'ở Chương 2/6/7 và E.5.')
text += '''\n\n<a id="phu-luc-e"></a>

## PHỤ LỤC E HỢP NHẤT CHÍNH THỨC PHIÊN BẢN 1.3

### E.1 Vì sao có nhiều bản và cách sử dụng từ nay

Các báo cáo phản biện được tạo để phân biệt tài liệu nguồn với kết luận đánh giá, giữ bằng chứng/giới hạn và nghiên cứu song song theo vai. Ở vòng trước, kết quả đã dừng ở báo cáo riêng mà chưa cập nhật Master; đó là thiếu bước hợp nhất, không phải yêu cầu anh phải vận hành nhiều bản đặc tả.

Từ phiên bản 1.3 chỉ dùng `CRM_MASTER_BRD_SRS_HOP_NHAT.md`. Bản này tích hợp lý do/liên kết của 40 FR, quy tắc 22 UC, dữ liệu, quyền, phạm vi và nghiệm thu. Không ghép mọi nhận xét vào như yêu cầu bắt buộc: loại các kết luận không có bằng chứng (90%, tiết kiệm40%, ngưỡng SLA/quota cứng), không đưa những sửa nguy hiểm (dừng mọi SLA theo contact, sticky trước quyền, tự xóa chênh lệch, clone để làm đẹp cycle). Tính năng chưa cần giữ P1/P2 ngay trong Master; dữ kiện chưa biết ở A.6.

### E.2 Hồ sơ lịch sử đã hợp nhất

| Tệp nguồn lịch sử | Lý do tạo | Kết quả dùng trong Master |
| --- | --- | --- |
| gemini-code-1792004600780.md | Báo cáo kiểm toán do người dùng cung cấp | Giữ vấn đề có căn cứ; sửa suy diễn/phương án gây lỗi mới |
| PHAN_TICH_PHAN_BIEN_CRM_2026-10-15.md | Đối chiếu báo cáo với SRS và nguồn chính thức | Sửa pipeline/SLA/routing/masking/payment/schema/phạm vi |
| RESEARCH_CEO_CRM_2026-10-15.md | Nghiên cứu song song góc điều hành/tài chính | Hợp đồng, legal entity, money/commission, cost/media, 26 ca chuyên đề |
| RESEARCH_CMO_CRM_2026-10-15.md | Nghiên cứu góc marketing | Handover, RFM, scope metrics, attribution, closed-loop, 26 ca chuyên đề |
| RESEARCH_CX_CRM_2026-10-15.md | Nghiên cứu góc trải nghiệm/dịch vụ | NRT/entitlement/promises/recovery/offboarding, 24 ca chuyên đề |
| CRM_RESEARCH_REVIEW_CEO_CMO_CX_2026-10-15.md | Tổng hợp nghiên cứu và kiểm tra liên kết | 40 FR rationale/dependencies; 22 UC; INT01–30; quyết định và nguồn |
| CRM_DOCUMENT_INDEX.md; CRM_CAP_NHAT_V1_2.md | Chỉ dẫn bản cũ và nhật ký 1.2 | Giữ lịch sử; Master hiện tại đã tự chứa version/phạm vi/nguồn |

Các tệp trên và snapshot Master1.2 ở `docs/archive/research-2026-10-15/`; không là bản chính thức song song. Không cần đọc chúng để nắm yêu cầu hiện hành. Tệp nguồn gốc trong docs vẫn là bằng chứng lịch sử, không phải các phiên bản Master mới.

### E.3 Quyết định và lý do hợp nhất

''' + decisions + '\n\n### E.3b Quan sát mã nguồn và giới hạn\n\n' + sources + '''

### E.5 Bằng chứng kỹ thuật bổ sung

| Nguồn | Nguyên tắc dùng | Giới hạn |
| --- | --- | --- |
| [AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Ghi nghiệp vụ/outbox cùng transaction; consumer idempotent | Không yêu cầu AWS/microservices |
| [OWASP API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) | Kiểm quyền object/action ở backend | Không thay test quyền theo schema dự án |
| [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | RAG không tự loại prompt injection; tool gate | Không phải chứng nhận AI an toàn |
| [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | Quản trị rủi ro/đo lường GenAI | Eval theo tác vụ và dữ liệu có quyền |
| [Gmail push](https://developers.google.com/workspace/gmail/api/guides/push) | Watch/history/checkpoint và sync bù | Kiểm scope/quota/version khi kết nối |
| [Microsoft Graph Outlook](https://learn.microsoft.com/en-us/graph/outlook-change-notifications-overview) | Subscription và mailbox permissions | Không suy shared mailbox dùng mọi quyền delegated |
| [WCAG2.2](https://www.w3.org/TR/WCAG22/) | Mục tiêu accessibility phù hợp, kiểm keyboard/focus/forms | Không tuyên bố đạt chỉ vì có label |
| [Chính phủ NĐ70/2025 về hóa đơn](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-70-2025-nd-cp-sua-doi-bo-sung-quy-dinh-ve-hoa-don-chung-tu-11925032321512617.htm) | Không mặc định mọi tạm ứng marketing được chờ nghiệm thu mới xuất hóa đơn | Kiểm bản chất dịch vụ/văn bản áp dụng tại triển khai |

### E.6 Độ chắc chắn và lịch sử thay đổi

Đây là hợp nhất tài liệu/desk research và đọc một số file mã nguồn, chưa cài/chạy benchmark hay chứng nhận mọi edition. Ba agent đã hoàn thành nghiên cứu ban đầu; lượt phản biện thứ hai bị giới hạn sử dụng, agent tổng hợp tự kiểm cuối. Không có kết quả lượt hai được dùng như bằng chứng. Facebook bị giới hạn đăng nhập/truy cập, không có khảo sát đại diện nhóm cộng đồng. Branch GitHub có thể thay đổi; PoC phải pin release/commit/license/tài khoản và UAT.

| Phiên bản | Ngày | Nội dung và thẩm quyền sử dụng |
| --- | --- | --- |
| 1.2 | 15/10/2026 | Bản trước rà soát chuyên sâu; đã lưu lịch sử |
| 1.3 | 15/10/2026 | Master duy nhất hiện hành; đã hợp nhất CEO/CMO/CX/phản biện; tham số chưa cung cấp theo A.6, go-live theo Chương9 |

NFR99,9% là mục tiêu cần năng lực vận hành; RTO4h phục hồi thảm họa không bảo đảm vẫn đạt SLO tháng. Bộ kiểm tải phải chốt dataset/shape/role/capability; chọn ACK nội bộ p95≤1giây cho kênh khi khả thi (NFR04 tổng≤2giây không thay timeout provider), báo riêng provider lag. Gate restore gồm suppression/deletion/cursor/outbox và đối soát tiền trước bật outbound; dữ liệu thiếu không coi0 hoặc healthy.
'''

# Remove misleading old algorithm/fields from historical text where it acts as current guidance.
text = text.replace('Unmerge phục hồi mapping theo snapshot; các hoạt động phát sinh sau merge cần steward phân bổ lại.',
                    'Unmerge dùng mapping/provenance trước và sau merge; tự tách phần đủ bằng chứng, steward xét phần mơ hồ. Chứng từ đã ký/chốt không tự đổi chủ thể theo Contact.')
text = text.replace('Trước mỗi bước gửi phải kiểm consent hiện thời, suppression, kênh, mẫu được duyệt, quota',
                    'Trước dispatch phải kiểm consent/purpose/endpoint hiện thời, suppression, kênh, mẫu được duyệt, cap toàn scope và quota')
text = text.replace('| Gia hạn | Hết hạn sau 45/30/15 ngày |',
                    '| Gia hạn | Mốc review/notice theo hợp đồng; template45/30/15 chỉ khi phù hợp |')
text = text.replace('| Có assignee đang giữ lease |', '| Có assignment active có version |')
text = text.replace('tenant/client', 'tenant/workspace')

# Validate before replacing the canonical file or reorganizing source files.
assert 'Phiên bản 1.3' in text
assert len(re.findall(r'^#### .*\bFR\d{2}\b', text, re.M)) == 40
assert len(re.findall(r'^### 4\.\d+ UC\d{2}\b', text, re.M)) == 22
assert len(re.findall(r'^\| INT\d{2} \|', text, re.M)) == 30
assert not re.search(r'^\| (?:Identities|Merge_Events|Conversations, Messages) \|', text, re.M)
assert 'FK InvoiceLines, NN' not in text
assert 'quality_factor 1' not in text
assert 'Unknown/Direct' not in text
assert 'TTL 5 phút' not in text
assert 'NULL cho dữ liệu agency' not in text
assert text.count('```') % 2 == 0

ARCHIVE.mkdir(parents=True, exist_ok=True)
snapshot = ARCHIVE / 'CRM_MASTER_BRD_SRS_HOP_NHAT_v1.2.md'
if snapshot.exists():
    raise ValueError('Snapshot already exists; do not overwrite historical baseline')
snapshot.write_bytes(MASTER.read_bytes())
MASTER.write_text(text, encoding='utf-8', newline='\n')
manifest = {
    'master': MASTER.name, 'version': '1.3', 'date': '2026-10-15',
    'previous_snapshot': snapshot.name,
    'previous_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    'master_sha256': hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    'functional_requirements': 40, 'use_cases': 22, 'integrated_uat': 30,
    'changes': changes,
    'runtime_tests': 'Not run; document consolidation only',
}
(ARCHIVE / 'CONSOLIDATION_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k != 'changes'}, ensure_ascii=False, indent=2))
