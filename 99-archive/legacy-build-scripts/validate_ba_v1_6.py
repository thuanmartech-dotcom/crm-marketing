from pathlib import Path
from decimal import Decimal
import re,json,hashlib
root=Path(__file__).resolve().parent.parent
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
assert 'Phiên bản 1.6' in s[:1000]
modules=re.findall(r'^#### ĐẶC TẢ MODULE (M\d{2}) — ([^\n]+)',s,re.M)
assert len(modules)==20 and len({x[0] for x in modules})==20
function_ids=re.findall(r'^\| (M\d{2}-F\d{2})\b',s,re.M)
assert len(function_ids)==len(set(function_ids))
acceptance_ids=set(re.findall(r'\bM\d{2}-AC\d{2}\b',s))
counts={}
for mid,title in modules:
    fs=[x for x in function_ids if x.startswith(mid+'-')]
    ac=[x for x in acceptance_ids if x.startswith(mid+'-')]
    assert len(fs)>=5,(mid,'functions',len(fs))
    assert len(ac)>=3,(mid,'acceptance',len(ac))
    counts[mid]={'title':title,'functions':len(fs),'acceptance':len(ac)}
assert len(re.findall(r'^#### 3\.\d+\.\d+ FR\d+',s,re.M))==40
assert len(re.findall(r'^### 4\.\d+ UC\d+',s,re.M))==22
assert len(re.findall(r'^\| CMO-U\d{2} \|',s,re.M))==26
assert '## PHỤ LỤC G ' not in s
assert 'các patch G là đề xuất chưa tự áp' not in s
for token in ('| business_model | varchar(12)','| commission_policy_snapshot_id |','| Message_Subject_Links |','R + Ru + SUM(Ra(a)) <= C','không giữ period lock','provider_namespace text NN','**Authorization binding:**','**Thẩm quyền cấp quyền:**','### 9.14'):
    assert token in s,token
for forbidden in ('FK PipelineStages','FK CommissionPolicies','Available = confirmed incoming − confirmed refunds − net active allocations − active refund reservations'):
    assert forbidden not in s,forbidden
new_tests=re.findall(r'^\| ((?:WF-U|FA|SEC-U)\d{2}) \|',s,re.M)
assert len(new_tests)==len(set(new_tests))==17
width=None
for n,line in enumerate(s.splitlines(),1):
    if line.startswith('|'):
        current=len(re.split(r'(?<!\\)\|',line))-2
        assert width is None or width==current, ('table',n,width,current,line)
        width=current
    else: width=None
assert s.count('```')%2==0
anchors=re.findall(r'<a id="([^"]+)"',s)
assert len(anchors)==len(set(anchors))
for ref in re.findall(r'\]\(#([^)]*)\)',s): assert ref in anchors,ref
# Arithmetic consistency of the written rules only, not a DB/app test.
C,R,A,Ru,Ra=map(Decimal,['100','0','100','0','20'])
assert C-R-A-Ru==0
assert R+Ru+Ra<=C
assert C-(R+Ra)-(A-Ra)-Ru==0
f=root/'docs/archive/research-2026-10-15/BA_RESTRUCTURE_V1_6_VALIDATION.json'
d=json.loads(f.read_text(encoding='utf-8'))
d.update({'master_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'module_function_count':len(function_ids),'module_acceptance_count':len(acceptance_ids),'module_details':counts,'table_and_anchor_validation':True,'spec_arithmetic_checked':True,'runtime_tests_run':False})
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'modules':20,'functions':len(function_ids),'acceptance_criteria':len(acceptance_ids),'FR':40,'UC':22,'applied_changes':len(d['applied_changes']),'new_test_groups':len(new_tests),'runtime_tests':False,'root_markdown':[x.name for x in root.glob('*.md')]},ensure_ascii=False,indent=2))
