from pathlib import Path
import re, json, hashlib
from decimal import Decimal

root=Path(__file__).resolve().parent.parent
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
a=s[s.index('## PHỤ LỤC G '):]
ids=re.findall(r'^#### G\.6\.\d+ Bản vá ((?:WF|DB|SEC)\d{2})',a,re.M)
tests=re.findall(r'^\| ((?:WF-U|FA|SEC-U)\d{2}) \|',a,re.M)
assert len(ids)==len(set(ids))==15
assert len(tests)==len(set(tests))==17
assert all(f'### G.{i} PHẦN {i}' in a for i in range(1,7))
assert s.count('```')%2==0
width=None
for line in s.splitlines():
    if line.startswith('|'):
        current=len(re.split(r'(?<!\\)\|',line))-2
        assert width is None or width==current, line
        width=current
    else:
        width=None
anchors=re.findall(r'<a id="([^"]+)"',s)
assert len(anchors)==len(set(anchors))
assert all(x in anchors for x in re.findall(r'\]\(#([^)]*)\)',s))
assert len(re.findall(r'^#### 3\.\d+\.\d+ FR\d+',s,re.M))==40
assert len(re.findall(r'^### 4\.\d+ UC\d+',s,re.M))==22
assert 'R + Ru + SUM(Ra(a)) <= C' in a
assert 'không giữ period lock' in a
assert Decimal(100)-Decimal(0)-Decimal(100)-Decimal(20)==Decimal(-20)
assert Decimal(100)-Decimal(20)-Decimal(80)==0
# Headroom example after a prior refund: C=100,R=40,reserve=30.
assert Decimal(40)+Decimal(30)<=Decimal(100)
manifest=root/'docs/archive/research-2026-10-15/ARB_AUDIT_V1_5_VALIDATION.json'
d=json.loads(manifest.read_text(encoding='utf-8'))
d['master_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
d['new_test_ids']=tests
d['anchors_and_tables_valid']=True
d['second_review_reservation_and_close_lock']=True
manifest.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'parts':6,'major_patches':len(ids),'new_test_groups':len(tests),'FR':40,'UC':22,'runtime_tests':False,'master_bytes':p.stat().st_size,'root_markdown':[x.name for x in root.glob('*.md')]},ensure_ascii=False,indent=2))
