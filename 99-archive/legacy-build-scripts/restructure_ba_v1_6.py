from pathlib import Path
import re, json, hashlib

ROOT=Path(__file__).resolve().parent.parent
MASTER=ROOT/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
raw=MASTER.read_bytes()
original=raw.decode('utf-8')
assert 'Phiên bản 1.5 —' in original[:1000]
archive=ROOT/'docs/archive/research-2026-10-15'
snapshot=archive/'CRM_MASTER_BRD_SRS_HOP_NHAT_v1.5.md'
assert not snapshot.exists(), 'Do not rerun against a different baseline.'
body=original.split('<a id="phu-luc-f"></a>',1)[0].rstrip()
g=original[original.index('## PHỤ LỤC G '):]
applied=[]

def patch_block(code):
    m=re.search(r'^#### G\.6\.\d+ Bản vá '+code+r' — .*?\n(.*?)(?=^#### |\Z)',g,re.M|re.S)
    assert m, code
    return m.group(1)

def replace_row(prefix, replacement, section=None):
    global body
    if section:
        start=body.index(section)
        end=body.find('\n### ',start+len(section))
        if end<0: end=len(body)
        old=body[start:end]
        hits=[x for x in old.splitlines() if x.startswith(prefix)]
        assert len(hits)==1,(prefix,hits)
        body=body[:start]+old.replace(hits[0],replacement,1)+body[end:]
    else:
        hits=[x for x in body.splitlines() if x.startswith(prefix)]
        assert len(hits)==1,(prefix,hits)
        body=body.replace(hits[0],replacement,1)

def before(marker,text):
    global body
    assert body.count(marker)==1,marker
    body=body.replace(marker,text.rstrip()+'\n\n'+marker,1)

def prose_between(text,start,end):
    return text.split(start,1)[1].split(end,1)[0].strip()

# WF01 intake Unknown.
row=next(x for x in patch_block('WF01').splitlines() if x.startswith('| business_model'))
replace_row('| business_model |',row)
rule=prose_between(patch_block('WF01'),'**Bổ sung vào quy tắc bắt buộc của UC01 tại 4.1 và UC03 tại 4.3:**','**Bổ sung tại')
before('### 4.2 UC02',rule)
before('### 4.4 UC04',rule)
applied.append('WF01')

# WF02 explicit response targets.
row=next(x for x in patch_block('WF02').splitlines() if x.startswith('| Message_Subject_Links'))
before('Projection last_inbound/qualifying interaction', '| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |\n| --- | --- | --- |\n'+row)
prose=prose_between(patch_block('WF02'),'**Bổ sung sau bảng API tại Mục 5.17 và liên kết tại FR36/FR39:**','**Bổ sung tại')
before('### 5.18 Dữ liệu bổ sung',prose)
applied.append('WF02')

# WF03 transition contract, with native state column mapping.
state=prose_between(patch_block('WF03'),'**Bổ sung Mục 3.13.5 sau Mục 3.13.4; cập nhật các ô status tại 5.2/5.5/5.6/5.8/5.13/5.16 tham chiếu mục này:**','**Bổ sung tại')
state=state.replace('Bảng sau là **baseline chuyển trạng thái đề xuất để chủ nghiệp vụ chốt**. Mapping native phải bảo toàn guards; chưa phê duyệt transition/cấu hình bắt buộc của một capability thì capability đó chưa được activate.', 'Bảng sau là hợp đồng chuyển trạng thái của thiết kế. Mapping trạng thái native phải bảo toàn các điều kiện và tác động này. Các tham số kinh doanh riêng được cấu hình theo A.6; thiếu cấu hình bắt buộc chỉ chặn thao tác tương ứng, không chặn tiếp nhận nhu cầu.')
before('<a id="chuong-4"></a>', '#### 3.13.5 Hợp đồng chuyển trạng thái và đồng hồ\n\n'+state)
for prefix in ('| Contracts, SOW_Versions |','| Projects, Deliverables, Acceptances |'):
    line=next(x for x in body.splitlines() if x.startswith(prefix))
    replace_row(prefix,line[:-1].rstrip()+' Trạng thái và command theo 3.13.5; không PATCH status tự do. |')
applied.append('WF03')

# WF04 applicable acceptance profile.
profile=prose_between(patch_block('WF04'),'**Thay đoạn mở đầu Mục 9.5; bổ sung dẫn chiếu tại 5.19/9.11:**','**Bổ sung tại')
profile=profile.replace('Profile pilot đề xuất:', 'Profile pilot của thiết kế:')
profile=profile.replace('| U23 |','| U23-R/U23-L (điều kiện áp dụng) |')
old=re.search(r'(### 9\.5 Bộ UAT tối thiểu\n\n)(.*?)(?=\n\n\| Test \|)',body,re.S)
assert old
body=body[:old.start(2)]+profile+body[old.end(2):]
replace_row('| U19 |','| U19 | UC04 | Đổi creative sau approval | Gate yêu cầu duyệt đúng version mới; N/A khi không có launch/publish cần approval | P0 control khi bật |')
replace_row('| U23 |','| U23-R | FR10 | Refund khoản referral đủ điều kiện | Đảo thưởng giới thiệu đúng phần một lần, giữ lịch sử | P0 control khi referral P1 bật |\n| U23-L | FR10 | Refund giao dịch đã phát điểm loyalty | Đảo điểm đúng phần một lần; không nhân effect do replay | P0 control khi loyalty P2 bật |')
applied.append('WF04')

# WF05 logical uniqueness.
keys=prose_between(patch_block('WF05'),'**Bổ sung sau bảng Deals tại 5.5 và SLA_Episodes tại 5.16:**','**Bổ sung tại')
conversion,episodes=keys.split('\n\n',1)
before('### 5.6 Bảng Orders',conversion)
before('### 5.17 Hợp đồng API',episodes)
applied.append('WF05')

# DB01 policy snapshot pointer.
db=patch_block('DB01')
replace_row('| commission_policy_id |',next(x for x in db.splitlines() if x.startswith('| commission_policy_snapshot_id')))
policy=prose_between(db,'**Bổ sung sau bảng Commission_Entries tại Mục 5.12:**','**Bổ sung ca')
before('### 5.13 Các bảng',policy)
before('### 5.12 Bảng Commission_Entries','Quy ước dấu của Payment_Allocations: amount và các cấu phần lưu trị tuyệt đối không âm; Allocate làm tăng phần đã phân bổ, Reverse làm giảm phần hiệu lực của allocation gốc. Reverse phải giữ cùng currency/pháp nhân và chỉ đảo cấu phần còn hiệu lực; không cộng amount Reverse như receipt mới. Số dư tính từ tổng có dấu theo entry_type, không UPDATE bản gốc.')
before('### 5.13 Các bảng','Quy ước dấu của Commission_Entries: Base là khoản phát sinh dương; Reverse giữ trị tuyệt đối và làm giảm phần còn hiệu lực của entry được tham chiếu. Commission_Adjustments khai báo direction Credit/Debit và reason; credit tăng quyền hưởng, debit giảm quyền hưởng theo quy chế. Không cộng bút toán đảo vào tổng earned như khoản thưởng mới. Partial payout và reversal giữ số đã trả lịch sử, phần phải xử lý tiếp được thể hiện riêng.')
applied.append('DB01')

# DB02 refund arithmetic and lifecycle, including the reviewed corrections.
db=patch_block('DB02')
refund=prose_between(db,'**Thay thế bullet bắt đầu “Hoàn tiền dư chưa phân bổ” tại Mục 3.13.4 bằng:**','**Thay thế dòng Refund_Reservations')
refund=refund.replace('theo lock order DB03','theo thứ tự khóa tại 5.14')
old=next(x for x in body.splitlines() if x.startswith('- Hoàn tiền dư chưa phân bổ:'))
body=body.replace(old,refund,1)
replace_row('| Refund_Reservations |',next(x for x in db.splitlines() if x.startswith('| Refund_Reservations |')))
for prefix in ('| Đầu vào và tiền điều kiện |','| Luồng chính |','| Đậu rớt và rẽ nhánh |'):
    region=db.split('**Thay thế các dòng Đầu vào/Luồng chính/Đậu rớt',1)[1]
    row=next(x for x in region.splitlines() if x.startswith(prefix))
    replace_row(prefix,row,'### 4.13 UC13')
applied.append('DB02')

# DB03 post/close lock contract.
db=patch_block('DB03')
rows='\n'.join(x for x in db.splitlines() if x.startswith('| Audit_Logs |') or x.startswith('| Finance_Periods |'))
replace_row('| Audit_Logs, Finance_Periods |',rows)
locking=prose_between(db,'**Bổ sung sau đoạn transaction tại Mục 5.14:**','**Bổ sung ca')
before('### 5.15 Migration',locking)
applied.append('DB03')

# DB04 finite/quantum and supported currencies.
db=patch_block('DB04')
money=prose_between(db,'**Bổ sung cuối đoạn đầu Mục 5.1:**','**Bổ sung ca')
money=money.replace('Đề xuất pilot dùng VND trước; đây chưa là quyết định hạn chế currency đã được chủ dự án chấp thuận.', 'VND là currency cấu hình tham chiếu; chỉ bật mã tiền có precision, rounding và mapping đã được kiểm. Danh mục tiền tệ thực dùng do Finance xác nhận theo A.6.')
before('### 5.2 Bảng Leads',money)
applied.append('DB04')

# SEC01 OAuth authorization binding.
sec=patch_block('SEC01')
binding=prose_between(sec,'**Bổ sung sau đoạn đầu Mục 2.6:**','**Bổ sung dòng')
before('### 2.7 Kiến trúc',binding)
applied.append('SEC01')

# SEC02 external-account namespace ownership.
sec=patch_block('SEC02')
ownership=prose_between(sec,'**Thay ô Ràng buộc/ý nghĩa của `Channel_Connections` tại Mục 5.16 bằng:**','**Bổ sung vào')
ownership=re.sub(r'^>\s*','',ownership,flags=re.M)
ownership=ownership.replace('Bổ sung `provider_namespace text NN` vào trường nghiệp vụ của Channel_Connections. ','')
line=next(x for x in body.splitlines() if x.startswith('| Channel_Connections |'))
cells=line.split('|')
cells[2]=cells[2].replace('provider varchar(40);','provider varchar(40); provider_namespace text NN;')
cells[3]=' '+ownership+' '
replace_row('| Channel_Connections |','|'.join(cells))
resolver=prose_between(sec,'**Bổ sung vào Mục 2.7:**','**Bổ sung dòng')
before('### 2.8 Tổ chức code',resolver)
applied.append('SEC02')

# SEC03 current authorization on sensitive downloads.
sec=patch_block('SEC03')
download=prose_between(sec,'**Thay câu về download URL ký trong đoạn đầu Mục 6.2 bằng khối dưới; thay câu cuối đoạn FR37 tại3.12.8 theo cùng hợp đồng download:**','**Thay ô Tiêu chí')
body=body.replace('Tệp upload kiểm MIME thật, kích thước, malware; download dùng URL ký ngắn hạn và kiểm ACL tại lúc cấp.', 'Tệp upload kiểm MIME thật, kích thước, malware; tệp cần quyền hiện thời tải qua gateway theo hợp đồng dưới đây.',1)
before('### 6.3 Khung pháp lý',download)
body=body.replace('Download kiểm quyền lúc cấp URL; link ký ngắn hạn không là cơ chế trao quyền vượt scope.', 'Download tài liệu nhạy cảm đi qua gateway kiểm quyền hiện tại cho từng GET/Range theo 6.2; không expose raw storage presigned URL như quyền của user.',1)
result=prose_between(sec,'**Thay ô Tiêu chí nghiệm thu UC12 tại Mục 4.12 bằng:**','**Thay ô kết quả U16')
result=re.sub(r'^>\s*','',result,flags=re.M)
replace_row('| Tiêu chí nghiệm thu |','| Tiêu chí nghiệm thu | '+result+' |','### 4.12 UC12')
replace_row('| U16 |','| U16 | UC12 | User đã offboard dùng token/URL gateway cũ | Sau commit revoke, request GET/Range/download mới bị từ chối; không đòi thu hồi byte đã tải | P0 |')
line=next(x for x in body.splitlines() if x.startswith('| Message_Attachments |'))
cells=line.split('|'); cells[3]=' size>=0; MIME/size/scan policy; chỉ clean mới tải/forward. Tệp cần quyền hiện thời qua download gateway theo6.2; asset publish theo share grant; không expose raw storage presigned URL. '
replace_row('| Message_Attachments |','|'.join(cells))
body=body.replace('Quét malware, URL ký hạn ngắn, approve đúng checksum/version.', 'Quét malware, gateway/share grant theo6.2, approve đúng checksum/version.',1)
applied.append('SEC03')

# SEC04 remote fetch, SEC05 email delivery rules and suppression.
sec=patch_block('SEC04')
fetch=prose_between(sec,'**Bổ sung sau đoạn FR40 tại Mục 3.12.11:**','**Bổ sung dòng')
before('#### Identity resolution: quy tắc quyết định',fetch)
sec=patch_block('SEC05')
email=prose_between(sec,'**Bổ sung vào FR34 tại Mục 3.12.5:**','**Bổ sung dữ liệu')
before('#### 3.12.6 FR35 Assignment',email)
row=next(x for x in sec.splitlines() if x.startswith('| Email_Delivery_Events'))
before('Projection last_inbound/qualifying interaction','| Miền / đối tượng bổ sung | Dữ liệu tối thiểu | Ràng buộc và phạm vi |\n| --- | --- | --- |\n'+row)
applied.extend(['SEC04','SEC05'])

# SEC06 control-plane grant authority.
sec=patch_block('SEC06')
grant=prose_between(sec,'**Bổ sung sau đoạn Mục 6.1 dòng1651:**','**Bổ sung vào ô')
before('### 6.2 Bảo vệ dữ liệu',grant)
line=next(x for x in body.splitlines() if x.startswith('| Entity_Team_Grants |'))
replace_row('| Entity_Team_Grants |',line[:-1].rstrip()+' Có grantor_id, authority/approval_ref, reason, created/revoked_at; kiểm grant authority riêng, không dùng quyền U resource để tự cấp quyền. |')
applied.append('SEC06')

# Minor regressions: canonical name and precise kickoff fixture.
body=body.replace('FK PipelineStages','FK Pipeline_Stages')
# Align ticket intake fields with the BA module's actual minimum inputs.
replace_row('| severity |','| severity | varchar(4) | S1/S2/S3; NULL chỉ khi triage_state=Pending | Hoàn tất triage phải có severity theo impact×urgency; chưa rõ vẫn tiếp nhận vào queue, không chặn containment. |')
ticket_section='### 5.8 Bảng Tickets'
ticket_start=body.index(ticket_section)
ticket_end=body.index('### 5.9',ticket_start)
ticket=body[ticket_start:ticket_end]
ticket=ticket.replace('| owner_id | uuid | FK Users, NULL khi queued | Người xử lý |', '| owner_id | uuid | FK Users, NULL khi queued | Người xử lý |\n| queue_id | uuid | FK Queues; bắt buộc khi active mà chưa có owner | Open/InProgress/WaitingCustomer phải có owner hoặc queue được giám sát; assignment changes có history/version |\n| request_type / triage_state | text / text | Unknown/Complaint/Incident/Question/Defect/Change; Pending/Completed | Intake chưa rõ được Unknown/Pending. Completed cần impact/urgency/severity và entitlement áp dụng; không chờ phân loại mới nhận vấn đề khẩn |')
body=body[:ticket_start]+ticket+body[ticket_end:]
replace_row('| U08 |','| U08 | UC06 | Won; điều khoản yêu cầu ứng trước; chưa đủ cọc và không có approved credit/start exception | Order có thể tạo; Paid không bật; kickoff pending. Approved credit/ngoại lệ chỉ mở đúng công việc được duyệt, không tự cho chi media | P0 khi áp dụng |')
body=body.replace('Bảng A.3–A.4 lưu lý do kế thừa nguồn từ các vòng trước; phạm vi/field/giai đoạn hiện hành theo Chương 3/5/9 phiên bản 1.3.', 'Bảng A.3–A.4 lưu lịch sử kế thừa; phạm vi/field/giai đoạn hiện hành theo Chương3/5/9 và hồ sơ module M01–M20 của phiên bản1.6.')

# Promote all 17 new acceptance specifications into actual Chapter9.
new_tests=re.findall(r'^\| ((?:WF-U|FA|SEC-U)\d{2}) \|([^\n]*)',g,re.M)
assert len(new_tests)==17
test_table='### 9.14 Nghiệm thu các hợp đồng BA đã hợp nhất\n\nCác ca dưới đã là yêu cầu kiểm thử hiện hành, không còn là patch chờ dán. Actual/evidence chưa có; QA thực thi theo release profile tại9.5.\n\n| ID | Tình huống | Kết quả bắt buộc |\n| --- | --- | --- |\n'
test_table+='\n'.join('| '+tid+' |'+rest for tid,rest in new_tests)
before('<a id="chuong-10"></a>',test_table)

# Add source references once in the current source register, not an audit annex.
sources='''### C.1 Nguồn kỹ thuật cho các hợp đồng đã hợp nhất

Các nguồn sau hỗ trợ nguyên tắc kỹ thuật; cấu hình nghiệp vụ và thiết kế cụ thể là quyết định của dự án, chưa là kết quả chạy phần mềm.

| Nguồn | Dùng cho hợp đồng |
| --- | --- |
| [PostgreSQL numeric](https://www.postgresql.org/docs/current/datatype-numeric.html) | Số hữu hạn, scale/quantum tại5.1; không dùng amount>0 thay validation NaN. |
| [PostgreSQL locking](https://www.postgresql.org/docs/current/explicit-locking.html) | Khóa nhất quán, retry và post/close-period tại5.14. |
| [RFC9700](https://www.rfc-editor.org/rfc/rfc9700.html) | OAuth callback/session/provider binding tại2.6. |
| [AWS presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) | Phân biệt bearer storage URL với quyền user; gateway6.2. |
| [OWASP SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | Egress/remote fetch FR40. |
| [Google sender guidelines](https://support.google.com/mail/answer/81126?hl=en) | Sender authentication/unsubscribe theo loại sender tạiFR34. |
| [NĐ91/2020 chống thư rác](https://vanban.chinhphu.vn/default.aspx?docid=200773&pageid=27160) | Email quảng cáo phải đối chiếu văn bản áp dụng khi bật; không chỉ dựa consent dữ liệu cá nhân. |
'''
before('<a id="phu-luc-d"></a>',sources)
body=body.replace('ở S02/Phụ lục F','ở S02 và policy pháp lý đã xác nhận')
body=body.replace('Trong một tenant, tại một thời điểm chỉ một connection Active/Degraded/ReauthorizationRequired sở hữu', 'Trong một tenant, tại một thời điểm chỉ một connection ở trạng thái active/degraded/reauthorization_required sở hữu')
body=body.replace('Connection giữ một owner workspace bất biến khi Active.', 'Connection giữ một owner workspace bất biến khi active.')
body=body.replace('### 3.13.5', '### 3.13.5')

# Module cards authored in parallel, inserted into the functional specifications.
cards=[]
for filename in ('ba_modules_workflow.json','ba_modules_finance.json','ba_modules_security.json'):
    cards.extend(json.loads((ROOT/'working'/filename).read_text(encoding='utf-8-sig')))
assert len(cards)==20 and len({x['id'] for x in cards})==20
for item in cards:
    md=item['markdown'].strip()
    md=re.sub(r'^##### .*?\n','',md,count=1).strip()
    md=md.replace('M06-F06 Duyệt/ap dụng', 'M06-F06 Duyệt/áp dụng')
    md=md.replace('  reveal PII theo nhiệm vụ', ' Hiển thị PII theo nhiệm vụ')
    md=md.replace('Thiếu exit/re-entry/cap/owner hoặc policy Active thì chỉ lưu Draft;', 'Thiếu exit/re-entry/cap/owner hoặc policy chưa Active thì chỉ lưu Draft;')
    md=md.replace('Ca liên quan INT17, M07–M10, RV17.', 'Ca liên quan INT17, CMO-U07–CMO-U10, RV17.')
    md=md.replace('Ca U23 theo feature, M21/M26, INT17.', 'Ca U23-R/U23-L theo feature, CMO-U21/CMO-U26, INT17.')
    md=md.replace('U19, INT08–11, M11–15/M24.', 'U19, INT16/INT22, CMO-U11–CMO-U15/CMO-U24.')
    md=md.replace('CEO-U05/22, M16–18/M25, RV18–19.', 'CEO-U05/22, CMO-U16–CMO-U18/CMO-U25, RV18–19.')
    md=md.replace('INT18–20, M01–06/M18–23, RV19.', 'INT18–20, CMO-U01–CMO-U06/CMO-U18–CMO-U23, RV19.')
    if item['id']=='M20':
        md+='\n\nNếu legal policy chưa cấu hình, Privacy owner vẫn phải tiếp nhận, tính hạn và xử lý thủ công theo căn cứ áp dụng, lưu evidence; không hoãn nghĩa vụ luật định để chờ cấu hình hệ thống. Chỉ chức năng tự tính hạn/thực thi tự động bị chặn cho tới khi policy được xác nhận.\n'
    text=f'<a id="module-{item["id"].lower()}"></a>\n\n#### ĐẶC TẢ MODULE {item["id"]} — {item["title"]}\n\n'+md+'\n'
    before(item['insert_before'],text)

catalog=(ROOT/'working/ba_module_catalog.md').read_text(encoding='utf-8')
before('### 3.1 CDP và hồ sơ',catalog)
body=body.replace('### 3.12 Đặc tả Unified Inbox và Customer 360 mở rộng','### 3.12 Hợp đồng kỹ thuật bổ sung của module M03 Unified Inbox')

# Set one explicit authority and history; old audit appendices only in snapshot.
body=body.replace('Phiên bản 1.5 — Master chính thức duy nhất, bổ sung kiểm định sáu trục; chưa Baseline Freeze','Phiên bản 1.6 — Đặc tả BA theo20 module; đã hợp nhất sửa đổi vào phần thân',1)
start=body.index('**TỆP MASTER DUY NHẤT HIỆN HÀNH:**')
end=body.index('## Kiểm soát tài liệu',start)
body=body[:start]+'''**TỆP MASTER DUY NHẤT:** `CRM_MASTER_BRD_SRS_HOP_NHAT.md` — phiên bản1.6. Đây là bản đặc tả BA đang dùng để thiết kế, triển khai và nghiệm thu. Danh mục20 module ở đầu Chương3; mỗi module có mã chức năng, điều kiện xử lý, màn hình/dữ liệu, trạng thái, quyền, liên kết và tiêu chí chấp nhận. Đây là20 ranh giới nghiệp vụ logic, không phải20 ứng dụng/dịch vụ phải xây.

**Thay đổi đã thực hiện:** 15 nhóm sửa đổi kỹ thuật/nghiệp vụ và hai hiệu chỉnh từ vòng kiểm định1.5 đã được áp trực tiếp vào Chương2–9; 17 nhóm ca kiểm thử bổ sung ở9.14. Không còn yêu cầu người đọc tự copy patch ở phụ lục. Báo cáo kiểm định và các phiên bản trước chỉ giữ trong archive; không là quy tắc song song với Master này.

**Cách sử dụng:** bắt đầu từ danh mục module tại3.0; đọc module cần triển khai, sau đó đối chiếu UC ởChương4, dictionary/quan hệ ởChương5, quyền ởChương6 và test/gate ởChương9. Các FR01–40/UC01–22 được giữ để truy vết. Các tham số doanh nghiệp chưa cung cấp nằm ởA.6; hệ thống có cách xử lý khi thiếu cấu hình, không để dev tự đặt số. Nội dung1.6 là quyết định thiết kế BA; không đồng nghĩa phần mềm/DDL/provider/UAT đã chạy đạt hoặc chính sách doanh nghiệp đã được phê duyệt.

'''+body[end:]
replace_row('| Trạng thái quyết định |','| Trạng thái quyết định | Đặc tả thiết kế BA hiện hành1.6; các thay đổi đã được hợp nhất vào mục áp dụng. Tham số kinh doanh/pháp lý được quản lý theo A.6 và Policy_Versions; thiếu cấu hình chặn đúng thao tác cần cấu hình, không chặn intake. Release phải qua9.5/9.11; chưa có biên bản UAT đã chạy. |')
body=body.replace('- [Phụ lục F — Thẩm định phản biện vòng hai và quyết định 1.4](#phu-luc-f)\n- [Phụ lục G — Kiểm định sáu trục, phán quyết và 15 bản vá](#phu-luc-g)', '- [Danh mục module và điều hướng BA](#danh-muc-module)\n- [Phụ lục F — Các thay đổi đã áp dụng trong1.6](#phu-luc-f)')
body=body.replace('| 1.5 | 15/10/2026 | Master duy nhất hiện hành; bổ sung audit G theo sáu phần, điểm70/100 cho đặc tả1.4, 15 Major/hai Minor, đầy đủ patch; chưa freeze/production sign-off |','| 1.5 | 15/10/2026 | Bản có báo cáo kiểm định, chưa áp patch; đã lưu snapshot lịch sử |\n| 1.6 | 15/10/2026 | Master hiện hành:20 module BA, áp15 nhóm sửa đổi và hai hiệu chỉnh, hợp nhất17 nhóm test vào9.14; nghiệm thu thực thi theoChương9 |')
body=body.replace('snapshot Master1.2 ở','snapshot các bản cũ ở')
body=body.replace('Không autoactivate seed từ tài liệu phản biện;', 'Policy cấu hình phải được review trước Active;')
body=body.replace('Ba agent song song đã dừng vì giới hạn sử dụng, không có kết quả agent được đưa vào báo cáo.', 'Đoạn này mô tả vòng nghiên cứu mã nguồn ban đầu; lịch sử các vòng nghiên cứu sau và phạm vi xác minh được ghi tạiE.6, không dùng trạng thái cũ để thay kết quả thiết kế hiện hành.')
body=body.replace('| 1.4 | 15/10/2026 | Baseline được rà soát ở G, đã lưu snapshot; kế thừa đặc tả trong 1.5, chưa áp các patch mới của G |','| 1.4 | 15/10/2026 | Baseline lịch sử đã được kiểm định ở bản1.5; snapshot lưu trong archive |')
# CMO acceptance IDs must not collide with the new module identifiers.
body=re.sub(r'(?m)^\| M(\d{2}) \|',r'| CMO-U\1 |',body)
body=body.replace('#### Marketing và CMO\n\n','#### Marketing và CMO\n\nMã CMO-U01–CMO-U26 thay tên cũ M01–M26 để phân biệt với mã module M01–M20; nội dung ca không đổi.\n\n',1)
body=body.replace('Nguồn R01–R20 được đối chiếu ngày 15/10/2026.', 'Nguồn R01–R20 được đối chiếu ngày 15/10/2026.')
body=body.replace('U23 khi referral/points được bật', 'U23-R/U23-L theo referral/points được bật')
body=body.replace('U23 khi referral/points', 'U23-R/U23-L theo referral/points')

change_log=(ROOT/'working/ba_change_log.md').read_text(encoding='utf-8')
body+='\n\n'+change_log
body=body.replace('theo20 module','theo 20 module')
assert len(applied)==len(set(applied))==15
assert len(re.findall(r'^#### 3\.\d+\.\d+ FR\d+',body,re.M))==40
assert len(re.findall(r'^### 4\.\d+ UC\d+',body,re.M))==22
assert len(re.findall(r'^#### ĐẶC TẢ MODULE M\d{2}',body,re.M))==20
assert 'các patch G là đề xuất' not in body and '## PHỤ LỤC G ' not in body
assert 'FK CommissionPolicies' not in body and 'FK PipelineStages' not in body
assert '| business_model | varchar(12)' in body
assert 'AvailableToAllocate = C − R − A − Ru' in body
assert body.count('```')%2==0
anchors=re.findall(r'<a id="([^"]+)"',body)
assert len(anchors)==len(set(anchors))
for ref in re.findall(r'\]\(#([^)]*)\)',body): assert ref in anchors,ref

snapshot.write_bytes(raw)
MASTER.write_text(body.rstrip()+'\n',encoding='utf-8',newline='\n')
manifest={'version':'1.6','snapshot_1_5_sha256':hashlib.sha256(raw).hexdigest(),'master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'module_count':20,'applied_changes':applied,'FR':40,'UC':22,'new_test_groups':17,'runtime_tests_run':False,'module_function_count':len(re.findall(r'\| M\d{2}-F\d{2}',body))}
(archive/'BA_RESTRUCTURE_V1_6_VALIDATION.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
readme=archive/'README.md'
readme.write_text('''# Hồ sơ lịch sử CRM — không phải bản hiện hành

Bản Master duy nhất là [CRM_MASTER_BRD_SRS_HOP_NHAT.md](<D:/AI Agent/CRM/CRM_MASTER_BRD_SRS_HOP_NHAT.md>), phiên bản1.6. Danh mục module BA ở3.0; các sửa đổi từ kiểm định1.5 đã được áp trực tiếp vào phần thân, 17 nhóm test bổ sung ở9.14. Nhật ký hợp nhất ởPhụ lục F hiện hành.

Thư mục này giữ snapshot1.2/1.3/1.4/1.5 và các báo cáo nguồn. Phụ lục F/G trong snapshot1.4/1.5 là lịch sử kiểm định; không dùng trạng thái “patch chưa áp” hoặc “Master hiện hành” trong bản lịch sử để ghi đè bản1.6. Các báo cáo chuyên đề là nguồn phân tích, không phải đặc tả song song. Không cần mở bản lịch sử để sử dụng Master hiện hành.

Các manifest JSON ghi SHA-256, thay đổi và kết quả kiểm cấu trúc/phép tính của tài liệu. Chúng là metadata do công cụ tổng hợp, không phải chứng nhận kiểm thử ứng dụng/DB/provider độc lập.
''',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
