from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[1]
p=root/'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
s=p.read_text(encoding='utf-8')
anchors=re.findall(r'<a id="([^"]+)"',s)
refs=re.findall(r'\]\(#([^\)]+)\)',s)
errors=[]
if len(anchors)!=len(set(anchors)):errors.append('Duplicate anchors')
errors += ['Missing anchor '+x for x in refs if x not in anchors]
if '\ufffd' in s:errors.append('Unicode replacement character')
if s.count('```')%2:errors.append('Unclosed code fence')
table_count=0; expected=None
for n,line in enumerate(s.splitlines(),1):
 if line.startswith('|'):
  cells=len(re.split(r'(?<!\\)\|',line))-2
  if expected is None:expected=cells;table_count+=1
  elif cells!=expected:errors.append(f'Table columns at line {n}: {cells} != {expected}')
 else:expected=None
for i in range(1,11):
 if len(re.findall(rf'^## CHƯƠNG {i} ',s,re.M))!=1:errors.append(f'Chapter {i}')
for i in range(1,23):
 if not re.search(rf'^### 4\.\d+ UC{i:02d} ',s,re.M):errors.append(f'Missing UC{i:02d}')
for prefix, start, end in [('FR',30,40),('OC',1,24)]:
 for i in range(start,end+1):
  if not re.search(rf'^\| {prefix}{i:02d} \|',s,re.M):errors.append(f'Missing {prefix}{i:02d}')
for i in range(1,21):
 if f'<a id="r{i:02d}"></a>' not in s:errors.append(f'Missing research source R{i:02d}')
for name in ['Leads','Contacts','Accounts','Deals','Orders','Activities','Tickets','Consent_Logs']:
 if not re.search(rf'^### 5\.\d+ Bảng {name}$',s,re.M):errors.append(name)
manifest=json.loads((root/'working/sources/manifest.json').read_text(encoding='utf-8'))
for f in manifest:
 if hashlib.sha256((root/f['path']).read_bytes()).hexdigest()!=f['hash']:errors.append('Source changed '+f['path'])
assert abs((350+36*28)*1.15-1561.7)<1e-6
result={'file':str(p),'bytes':p.stat().st_size,'words_whitespace':len(s.split()),'chapters':10,'tables':table_count,'internal_links':len(refs),'source_files_unchanged':len(manifest),'errors':errors}
(root/'working/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
