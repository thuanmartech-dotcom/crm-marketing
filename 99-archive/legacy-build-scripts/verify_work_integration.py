from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
# Avoid collision with pre-existing WF01/WF02/WF03 service blueprints.
for marker in ['### 3.14 ', '### 4.23 ', '### 5.20 ', '### 6.6 ', '### 7.7 ', '### 8.5 ', '### 9.16 ', '### A.7 ']:
    a=s.index(marker)
    following=re.search(r'^(?:### |## |<a id=)',s[a+len(marker):],re.M)
    b=a+len(marker)+following.start() if following else len(s)
    s=s[:a]+re.sub(r'\bWF(\d{2})',r'W-F\1',s[a:b])+s[b:]
lines=s.splitlines()
for i,line in enumerate(lines):
    if 'WF01' in line or line.startswith('| FR25 Work Management') or line.startswith('**Nghiệm thu và giai đoạn:** P0 gồm'):
        lines[i]=re.sub(r'\bWF(\d{2})',r'W-F\1',line)
s='\n'.join(lines)+'\n'
s=s.replace('Contracts ||--o{ Projects : delivered_as','Contracts o|--o{ Projects : delivered_as')
s=s.replace('### 3.14 Hợp đồng nghiệp vụ Task Core dùng chung — FR25/M16','### 3.14 Hợp đồng nghiệp vụ Task Core dùng chung — FR25/M16\n\nMã chức năng W-F01–14 ở Master tương ứng WF01–14 trong báo cáo nguồn; namespace riêng để không trùng mã service blueprint WF01–03 đã có. UC-W và BR-W giữ nguyên.')
s=s.replace('### 5.20 Schema và API Work Management — FR25','### 5.20 Schema và API Work Management — FR25\n\n**Project scope:** Projects có project_type CLIENT_DELIVERY/INTERNAL. Contract/SOW/handoff bắt buộc có điều kiện với CLIENT_DELIVERY theo M08; INTERNAL cho NULL và cần sponsor/team/owner/start authorization nội bộ. Trạng thái Project ở 3.13.5 dùng chung nhưng guard hợp đồng/tiền chỉ áp client delivery theo cam kết, không áp internal project. Personal/internal/CRM task standalone cho project_id NULL. Điều này cũng áp cho bảng tổng hợp 5.13 và ERD Chương 5.')
s=s.replace('#### 9.16.4 Truy vết chức năng','#### 9.16.4 Truy vết chức năng\n\nTrong bảng dưới: W01/02… là UC-W01/02…, T01/02… là W-T01/02…; BR-W là quy tắc Task Core, không phải BR của Chương 1.')
a=s.index('#### 9.16.4 '); b=s.index('<a id="chuong-10">',a)
sub=re.sub(r'\bBR(\d{2})',r'BR-W\1',s[a:b])
s=s[:a]+sub+s[b:]
s=s.replace('Profile pilot của thiết kế: một nguồn/một inbox;', 'Profile pilot của thiết kế 1.7: thêm Task Core cá nhân/team với My Work, giao/nhận, review và reminder; W-F08–09 hoàn tất trong release P0 theo 9.16. Đồng thời giữ một nguồn/một inbox;')
s=s.replace('**Truy vết:** FR15/18/23/25–27; UC06/08/09/16;', '**Truy vết:** FR15/18/23/25–27; UC-W01–10 cho Task Core tại 4.23 và W-T01–40 tại 9.16; UC06/08/09/16 cho delivery;')
s=s.replace('### 9.1 Kế hoạch 90 ngày theo gate', '### 9.1 Kế hoạch 90 ngày theo gate\n\n**Delta 1.7:** bổ sung Task Core theo 9.16 vào gate cá nhân/team; trước cam kết lịch cần ước lượng lại thiết kế/schema/API/QA/migration cho scope mới. Bảng ngày bên dưới là khung kế hoạch tham chiếu, không bằng chứng đủ nguồn lực để hoàn thành cả Work Management trong 90 ngày.')
p.write_text(s,encoding='utf-8')

checks={
 'new_sections': all(s.count(x)==1 for x in ['### 3.14 ','### 4.23 ','### 5.20 ','### 6.6 ','### 7.7 ','### 8.5 ','### 9.16 ','### A.7 ']),
 'ten_use_cases': len(re.findall(r'^\| UC-W\d{2} ',s,re.M))==10,
 'forty_tests': len(re.findall(r'^\| W-T\d{2} \|',s,re.M))==40,
 'fourteen_features': len(re.findall(r'^\| W-F\d{2} \|',s,re.M))==14,
 'fences_balanced': len(re.findall(r'^```',s,re.M))%2==0,
 'no_old_scope': 'task/capacity chi tiết P1' not in s and 'Bắt buộc contract/SOW/handoff link' not in s,
 'backup_exists': (root/'docs/archive/CRM_MASTER_v1.6_BEFORE_WORK_2026-10-16.md').exists(),
}
anchors=re.findall(r'<a id="([^"]+)"',s)
checks['unique_explicit_anchors']=len(anchors)==len(set(anchors))
refs=re.findall(r'\]\(#([^\)]+)\)',s)
missing=sorted(set(refs)-set(anchors))
# Existing document uses explicit anchors for navigation.
checks['anchor_links_resolve']=not missing
for k,v in checks.items(): print(k, 'PASS' if v else 'FAIL')
if missing: print('Missing anchors:',missing)
assert all(checks.values())
print('Master lines:',len(s.splitlines()))
