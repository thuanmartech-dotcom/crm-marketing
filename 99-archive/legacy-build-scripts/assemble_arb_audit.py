from pathlib import Path
from decimal import Decimal
import re, json, hashlib

root = Path(r'D:\AI Agent\CRM')
master = root / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
old_bytes = master.read_bytes()
old = old_bytes.decode('utf-8')
assert 'Phiên bản 1.4 —' in old[:1000] and '## PHỤ LỤC G ' not in old
archive = root / 'docs/archive/research-2026-10-15'
snapshot = archive / 'CRM_MASTER_BRD_SRS_HOP_NHAT_v1.4.md'
assert not snapshot.exists()

intro = (root/'working/arb_audit_intro.md').read_text(encoding='utf-8')
# Canonical finding IDs: SEC01 OAuth; SEC02 external namespace.
intro = intro.replace('| SEC01, P0 cho connector được bật |', '| SEC02, P0 cho connector được bật |')
intro = intro.replace('| SEC02, P0 khi dùng OAuth |', '| SEC01, P0 khi dùng OAuth |')
intro = intro.replace('SEC01 cần khóa ownership', 'SEC02 cần khóa ownership')
intro = intro.replace('SEC01, P0 cho connector', 'SEC02, P0 cho connector')
intro = intro.replace('DB04 làm rõ dấu reversal/caps/currency scale khi hiện thực ledger', 'DB04 làm rõ số hữu hạn/quantum/currency scale khi hiện thực ledger')
intro = intro.replace('| Email marketing |', '| Email marketing |')
intro = intro.replace('| Search/BI/AI/merge |', '| Cấp quyền quản trị | 6.1/5.18 chưa xác định grant authority và ngăn tự nâng quyền | SEC06, trước mở nhiều người dùng/cấp quyền |\n| Search/BI/AI/merge |')
intro = intro.replace('SEC02–04 là yêu cầu', 'SEC01/SEC03/SEC04 là yêu cầu')
intro = intro.replace('WF02–WF04 và DB02–DB03', 'WF02–WF05 và DB02–DB03')
verdict = (root/'working/arb_audit_verdict.md').read_text(encoding='utf-8')
workflow = (root/'working/arb_workflow_patches.md').read_text(encoding='utf-8')
fin = (root/'working/audit_finance_schema.md').read_text(encoding='utf-8')
sec = (root/'working/audit_security_privacy.md').read_text(encoding='utf-8')

def section(text, title, next_title):
    return text.split(title,1)[1].split(next_title,1)[0].strip()

finance_sections = []
for source_id, target_id, heading, number in [
    ('01','01','Pointer chính sách và snapshot thống nhất',8),
    ('03','02','Hoàn tiền chưa và đã phân bổ',9),
    ('02','03','Khóa kỳ và posting đồng thời',10),
    ('04','04','Số hữu hạn và currency quantum',11),
]:
    part = section(fin, f'## Patch FS-F{source_id}', f'## Patch FS-F{int(source_id)+1:02}')
    # The rest of source heading is descriptive, followed by the patch itself.
    part = part[part.index('\n'):].strip()
    if target_id == '04':
        start = part.index('P0 chỉ kích hoạt currency')
        end = part.index('Mọi amount/quantity/rate/share')
        part = part[:start] + ('Currency chỉ được bật từ allowlist đã được Finance/chủ nghiệp vụ phê duyệt, có precision/minor-unit exponent, rounding/caps, connector/ERP mapping và UAT. Đề xuất pilot dùng VND trước; đây chưa là quyết định hạn chế currency đã được chủ dự án chấp thuận. Mã char(3) không tự chứng minh hệ thống hỗ trợ currency đó. Nếu precision/quantum nhỏ hơn khả năng storage thì phải sửa schema trước enable, không tự FX hoặc làm tròn chứng từ nhập.\n\n') + part[end:]
    finance_sections.append(f'#### G.6.{number} Bản vá DB{target_id} — {heading}\n\n'+part+'\n')

security_sections = []
for i in range(1,7):
    marker = f'## SEC{i:02} — '
    end_marker = f'## SEC{i+1:02} — ' if i<6 else '## Các điểm chưa'
    part = section(sec, marker, end_marker)
    title, body = part.split('\n',1)
    # Keep ready-to-paste instructions, not duplicate the agent's whole working memo.
    patch_start = body.index('**Bổ sung') if i != 2 else body.index('**Thay ô')
    body = body[patch_start:]
    if i == 2:
        body = body.replace('Connection giữ một owner workspace', 'Bổ sung `provider_namespace text NN` vào trường nghiệp vụ của Channel_Connections. Connection giữ một owner workspace')
    if i == 3:
        body = body.replace('**Bổ sung cuối đoạn đầu Mục 6.2; cập nhật mô tả URL tại FR37 theo cùng quy tắc:**',
          '**Thay câu về download URL ký trong đoạn đầu Mục6.2 bằng khối dưới; thay câu cuối đoạn FR37 tại3.12.8 theo cùng hợp đồng download:**')
        body = body.replace('**Thay kết quả U16 và bổ sung SEC-U03 tại9.13:**',
          '**Thay ô kết quả U16 tại9.5 bằng:**\n\n> Sau commit revoke, token phiên cũ và mọi GET/Range/download mới qua link gateway cũ bị từ chối; giữ actor lịch sử. Không yêu cầu thu hồi byte đã tải.\n\n**Thay ô ràng buộc Message_Attachments tại5.16 bằng:**\n\n> size>=0; MIME/size/scan policy; chỉ clean mới download/forward. Tệp cần quyền hiện thời đi download gateway theo6.2; không expose raw presigned storage URL. Asset publish dùng share grant đúng phạm vi.\n\n**Bổ sung SEC-U03 tại9.13:**')
    if i == 5:
        body += ('\n\nCăn cứ sender authentication/one-click tùy loại sender: [Google sender guidelines](https://support.google.com/mail/answer/81126?hl=en). Phạm vi email quảng cáo cần đối chiếu [NĐ91/2020 bản Chính phủ](https://vanban.chinhphu.vn/default.aspx?docid=200773&pageid=27160) cùng văn bản áp dụng khi triển khai; không khẳng định chưa có unsubscribe trong SRS là bằng chứng doanh nghiệp đã vi phạm.\n')
    security_sections.append(f'#### G.6.{11+i} Bản vá SEC{i:02} — {title.strip()}\n\n'+body.strip()+'\n')

close = (root/'working/arb_audit_close.md').read_text(encoding='utf-8')
annex = '\n\n'.join([intro, verdict, workflow, *finance_sections, *security_sections, close])
annex = re.sub(r'Mục(?=\d)', 'Mục ', annex)
annex = re.sub(r'(?<=\d)(?=(?:triệu|phút|giờ|ngày|tháng|đồng)\b)', ' ', annex)
annex = annex.replace('theo3.13.4','theo 3.13.4').replace('tại6.3','tại 6.3').replace('tại5.18','tại 5.18').replace('tại9.13','tại 9.13')

new = old.replace('Phiên bản 1.4 — Master chính thức duy nhất, đã thẩm định và hợp nhất phản biện vòng hai',
                  'Phiên bản 1.5 — Master chính thức duy nhất, bổ sung kiểm định sáu trục; chưa Baseline Freeze',1)
new = new.replace('— phiên bản 1.4. Dùng tệp này', '— phiên bản 1.5. Dùng tệp này',1)
new = new.replace('Phụ lục F phân tích lợi/hại của bản phản biện HTML mới, quyết định nhận/sửa/bác và phương án triển khai.',
    'Phụ lục F giữ thẩm định phản biện HTML. **Phụ lục G là kiểm định mới nhất theo sáu trục: 15 Major, hai Minor và bản vá cho từng lỗi. Phần đặc tả nghiệp vụ kế thừa 1.4; các patch G là đề xuất chưa tự áp vào phần thân. Không dùng Master này như SRS đã đóng băng hoặc UAT đã đạt.**',1)
new = new.replace('| Trạng thái quyết định | Phiên bản đặc tả chính thức hiện hành.',
    '| Trạng thái quyết định | Master hiện hành, chưa đủ điều kiện Baseline Freeze toàn bộ theo kiểm định G. Phần đặc tả kế thừa 1.4; bản vá G chờ quyết định/áp đúng mục và kiểm chứng. Phiên bản đặc tả chính thức hiện hành.',1)
new = new.replace('- [Phụ lục F — Thẩm định phản biện vòng hai và quyết định 1.4](#phu-luc-f)',
    '- [Phụ lục F — Thẩm định phản biện vòng hai và quyết định 1.4](#phu-luc-f)\n- [Phụ lục G — Kiểm định sáu trục, phán quyết và 15 bản vá](#phu-luc-g)',1)
new = new.replace('| 1.4 | 15/10/2026 | Master duy nhất hiện hành; vá lỗi đã xác minh và hợp nhất thẩm định HTML ở F, tham số chưa chốt theo A.6; go-live theo Chương9 |',
    '| 1.4 | 15/10/2026 | Baseline được rà soát ở G, đã lưu snapshot; kế thừa đặc tả trong 1.5, chưa áp các patch mới của G |\n| 1.5 | 15/10/2026 | Master duy nhất hiện hành; bổ sung audit G theo sáu phần, điểm70/100 cho đặc tả1.4, 15 Major/hai Minor, đầy đủ patch; chưa freeze/production sign-off |',1)
new = new.rstrip()+'\n\n'+annex.rstrip()+'\n'

# Structural checks: all six parts, 15 distinct Major patch headings, two Minor.
for i in range(1,7):
    assert f'### G.{i} PHẦN {i}' in new
patch_ids = re.findall(r'^#### G\.6\.\d+ Bản vá ((?:WF|DB|SEC)\d{2})', new, re.M)
assert len(patch_ids)==15 and len(set(patch_ids))==15, patch_ids
assert new.count('<a id="phu-luc-g"></a>')==1
assert len(re.findall(r'^#### 3\.\d+\.\d+ FR\d+',new,re.M))==40
assert len(re.findall(r'^### 4\.\d+ UC\d+',new,re.M))==22
assert new.count('```') % 2 == 0
bad_tables=[]
width=None
for i,line in enumerate(new.splitlines(),1):
    if line.startswith('|'):
        count=len(re.split(r'(?<!\\)\|',line))-2
        if width is not None and count!=width: bad_tables.append([i,width,count])
        width=count
    else: width=None
assert not bad_tables, bad_tables
# Reproduce specification arithmetic only; no database or app is run.
C,R,A,Ru,Ra = map(Decimal,['100','0','100','0','20'])
old_available=C-R-A-Ru-Ra
new_available=C-R-A-Ru
confirmed_available=C-(R+Ra)-(A-Ra)-Ru
assert [old_available,new_available,confirmed_available] == [Decimal('-20'),Decimal('0'),Decimal('0')]

snapshot.write_bytes(old_bytes)
master.write_text(new,encoding='utf-8',newline='\n')
manifest={
 'audited_version':'1.4','current_document_version':'1.5',
 'specification_patches_applied_to_body':False,
 'snapshot_sha256':hashlib.sha256(old_bytes).hexdigest(),
 'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
 'major_findings':patch_ids,'major_count':15,'minor_count':2,
 'score_document_review':70,'score_max':100,
 'new_test_groups':17,'FR':40,'UC':22,
 'tables_structurally_consistent':True,'six_parts_present':True,
 'arithmetic_counterexample':{'old_available':str(old_available),'correct_available':str(new_available),'after_refund':str(confirmed_available)},
 'runtime_tests_run':False,'database_tests_run':False,'provider_tests_run':False,
 'note':'Self-produced structural/arithmetic validation record, not independent certification.'
}
(archive/'ARB_AUDIT_V1_5_VALIDATION.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
