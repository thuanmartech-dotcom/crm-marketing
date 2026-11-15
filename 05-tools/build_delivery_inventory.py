"""Reproducible, conservative inventory. No application code or Master mutations."""
from pathlib import Path
import re, json, csv, hashlib, sys
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
MASTER = ROOT / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
OUT = ROOT / '03-planning'
raw = MASTER.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
lines = raw.decode('utf-8-sig').splitlines()
version_match = re.search(r'^Phiên bản (\d+\.\d+)', raw.decode('utf-8-sig'), re.M)
version = version_match[1] if version_match else 'UNRESOLVED'
for folder in ('trace', 'agent', 'evidence'):
    (OUT / folder).mkdir(parents=True, exist_ok=True)

def save(path, obj):
    (OUT / path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

PREFIX = r'(?:M\d{2}-(?:AC|F)|UC-H|BR-H|H-NFR|H-T|H-O|UC-P|BR-P|P-NFR|P-T|P-O|UC-W|BR-W|W-F|W-T|W-O|OM-G|ONFR|NFR|FR|BR|UC|(?:CEO|CMO|CX|SEC|WF)-U|SEC|DB|CR|RV|INT|OC|FA|WF|U|O)'
TOKEN = re.compile(r'(?<![A-Za-z0-9_-])(' + PREFIX + r')(\d{2})(-[A-Z])?(?![A-Za-z0-9_])')
RANGE = re.compile(r'^\s*[–—-]\s*(?:(' + PREFIX + r'))?(\d{2})(?![\dA-Za-z_])')
SLASH = re.compile(r'^/(\d{2})(?![\dA-Za-z_])')
modules, headings, context = [], [], ''
for n, line in enumerate(lines, 1):
    if line.startswith('#'):
        context = line.lstrip('# ').strip()
        headings.append({'line': n, 'level': len(line)-len(line.lstrip('#')), 'heading': context})
    m = re.match(r'\| \[(M\d{2})\]\(#module-m\d{2}\) \|', line)
    if m:
        cells = [x.strip() for x in line.strip('|').split('|')]
        modules.append({'id':m[1], 'name':cells[1], 'actors':cells[2], 'owned_data_source':cells[3],
                        'dependencies_source':cells[4], 'priority_source':cells[5], 'source_line':n,
                        'implementation_status':'Not Implemented / repository not established'})

fr_owner = {}
for nums, owner in [([1,2,3],'M01'),([4,5,6],'M02'),([7,8]+list(range(30,41)),'M03'),
    ([9],'M04'),([10],'M05'),([11,12,13],'M06'),([14],'M07'),([15],'M08'),([16],'M09'),
    ([17],'M10'),([18],'M11'),([19],'M12'),([20],'M13'),([21],'M14'),([22,23,24],'M15'),
    ([25,27],'M16'),([26],'M17'),([28,29],'M18'),([41],'M21'),([42],'M22')]:
    for v in nums: fr_owner[f'FR{v:02}'] = owner
uc_owner = dict(zip([f'UC{i:02}' for i in range(1,23)],
 ['M02','M02','M02','M15','M07','M08','M09','M16','M11','M08','M20','M14','M09','M14','M01','M18','M03','M01','M03','M03','M19','M16']))
br_owner = dict(zip([f'BR{i:02}' for i in range(1,7)], ['M02','M03','M07','M09','M08','PLATFORM']))
work_links = {1:([1,3],[1,8],[1,36]),2:([2],[1,2,9],[3,5,6,29]),3:([3],[8],[1,36]),
 4:([4],[8],[10,36]),5:([5],[4],[11,12,13]),6:([6],[3],[2,7,8,9,37]),
 7:([7],[5],[14,15,16,17,18]),8:([8],[6],[19,20,21,22,23]),9:([9],[7],[24,25,26,27,28])}
registry = {}
unresolved = []
section = ''
for n, line in enumerate(lines,1):
    if line.startswith('#'): section = line.lstrip('# ').strip()
    matches = list(TOKEN.finditer(line))
    for match in matches:
        prefix, num, suffix = match[1], match[2], match[3] or ''
        ids = [(prefix + num + suffix, 'literal')]
        tail = line[match.end():]
        rm = RANGE.match(tail)
        if rm and not suffix:
            endprefix, end = rm[1] or prefix, int(rm[2])
            if endprefix == prefix and int(num) < end <= int(num)+150:
                ids += [(prefix + f'{j:02}', 'range_expansion') for j in range(int(num)+1,end+1)]
        else:
            while not suffix and (sm := SLASH.match(tail)):
                ids.append((prefix + sm[1], 'slash_expansion'))
                tail = tail[sm.end():]
        cleaned = line.replace('**','').replace('`','')
        first = cleaned.strip().lstrip('|').split('|')[0].strip()
        literal = prefix+num+suffix
        row_definition = line.startswith('|') and re.match(re.escape(literal)+r'(?:\s|$)', first) is not None
        # Multi-ID applicability rows and lists are references, not definitions.
        if re.match(re.escape(literal)+r'[/–]', first) or 'điều kiện áp dụng' in first: row_definition = False
        heading_definition = bool(re.match(r'^#{3,4}\s+[\d.]+\s+'+re.escape(literal)+r'\s',cleaned))
        inline_definition = bool(re.search(r'(?:^|[;。]\s*)'+re.escape(literal)+r'\s*[:—]', cleaned))
        if prefix.startswith('M') and '-AC' in prefix and re.search(re.escape(literal)+r'[:\s]+[^;]+',cleaned) and 'Nghiệm thu:' in cleaned:
            inline_definition = True
        if re.match(r'^,\d+%',line[match.end():]):
            continue  # e.g. NFR99,9% is a percentage, not a requirement ID.
        for rid, origin in ids:
            isdef = origin=='literal' and (row_definition or heading_definition or inline_definition)
            item = registry.setdefault(rid, {'id':rid,'kind':prefix,'occurrences':[]})
            occurrence={'line':n,'section':section,'origin':origin,'classification':'definition_candidate' if isdef else 'reference','text':line}
            if occurrence not in item['occurrences']: item['occurrences'].append(occurrence)
    if re.search(r'(?<![\w-])(?:W|T)\d{2}(?!\d)', line) or re.search(r'\bM\d{2}/M\d{2}\b',line):
        unresolved.append({'line':n,'text':line,'reason':'Context-dependent shorthand/legacy namespace: inspect manually; not silently canonicalized'})

def owner_for(rid):
    if rid.startswith(('UC-H','BR-H','H-NFR','H-T','H-O')): return 'M22','namespace and reviewed M22 ownership'
    if rid.startswith(('UC-P','BR-P','P-NFR','P-T','P-O')): return 'M21','namespace and reviewed M21 ownership'
    if rid.startswith(('W-F','W-T','UC-W','BR-W','W-O')): return 'M16','namespace'
    if re.match(r'M\d{2}-',rid): return rid[:3],'namespace'
    if rid in fr_owner: return fr_owner[rid], 'analyst mapping from module catalog'
    if rid in uc_owner: return uc_owner[rid], 'proposed command/flow owner; consumers separate'
    if rid in br_owner: return br_owner[rid], 'analyst mapping'
    if rid.startswith('ONFR'): return 'M19','proposed operational control owner; M03 consumer'
    if rid.startswith('NFR'): return 'PLATFORM','proposed cross-cutting control owner'
    if rid.startswith('OM-G'): return 'M03','proposed integration scenario owner; M19 consumer'
    if rid.startswith('FA'): return 'M09','proposed financial control owner; M10 consumer'
    if rid.startswith('SEC'):
        return {'01':'M19','02':'M19','03':'M14','04':'M19','05':'M20','06':'M14'}.get(rid[-2:]),'proposed security control owner'
    return None, 'unresolved; requires semantic review'

tests = set()
for rid, item in registry.items():
    if re.match(r'^(?:H-T|P-T|W-T|OM-G|(?:CEO|CMO|CX|SEC|WF)-U|U|OC|INT|RV|FA)\d|^M\d{2}-AC',rid): tests.add(rid)
refs_by_line = {}
for rid, item in registry.items():
    for o in item['occurrences']: refs_by_line.setdefault(o['line'],set()).add(rid)
for rid,item in registry.items():
    definitions = [o for o in item['occurrences'] if o['classification']=='definition_candidate']
    item['definition_status'] = 'candidate_found' if definitions else 'reference_only_unresolved'
    item['definition_lines'] = sorted(set(o['line'] for o in definitions))
    item['owner'],item['owner_basis'] = owner_for(rid)
    item['consumers'] = sorted(set(re.findall(r'\bM\d{2}\b',' '.join(o['text'] for o in definitions))) - {item['owner']})
    item['consumer_status']='candidate co-mentions only; not authoritative dependency graph'
    item['source']={'path':str(MASTER),'sha256':sha,'lines':sorted(set(o['line'] for o in item['occurrences']))}
    item['priority'] = sorted(set(re.findall(r'\bP[012]\b',' '.join(o['text'] for o in definitions)))) or ['Unresolved / see release profile']
    item['applicability']='Evaluate against versioned release profile; no implicit Pass/N/A'
    item['slice']=['SL01 candidate' if item['owner']=='M16' else 'Roadmap / ownership review']
    if item['owner']=='M21': item['slice']=['SL08 partner results; applicability per mode']
    if item['owner']=='M22': item['slice']=['SL09 HR-A / SL10 HR-B / SL11 HR-C; applicability per profile']
    item['slice_scope_note']='M16 membership does not imply all M16 requirements are enabled in SL01; see SL01 applicability matrix'
    item['implementation_status']='Not Implemented / no application evidence'
    item['verification_status']='Not Run'
    item['evidence']=[]
    item['tests'] = sorted({ref for o in definitions for ref in refs_by_line.get(o['line'],set()) if ref in tests and ref!=rid})
    item['test_link_basis']='explicit same-definition co-mention; not complete semantic trace'
    if rid.startswith('W-F') and int(rid[-2:]) in work_links:
        item['tests']=[f'W-T{j:02}' for j in work_links[int(rid[-2:])][2]]
        item['test_link_basis']='reviewed mapping from 9.16.4 plus related 9.16 cases'

# Reviewed M21 feature rows propagate test coverage to linked UC/rules, not inferred from arbitrary co-mentions.
partner_trace=[]
for rid,item in registry.items():
    if re.fullmatch(r'M21-F\d{2}',rid):
        owned_lines=[o['line'] for o in item['occurrences'] if o['classification']=='definition_candidate' and o['text'].startswith('| M21-F')]
        related=set().union(*(refs_by_line.get(n,set()) for n in owned_lines))
        partner_trace.append({'feature':rid,'use_cases':sorted(x for x in related if x.startswith('UC-P')),
            'rules':sorted(x for x in related if x.startswith('BR-P')),'tests':item['tests'],'source_lines':owned_lines})
for row in partner_trace:
    for rid in row['use_cases']+row['rules']:
        registry[rid]['tests']=sorted(set(registry[rid]['tests'])|set(row['tests']))
        registry[rid]['test_link_basis']='Reviewed feature/UC/rule/test matrix in Master 3.15.3'
if 'FR41' in registry:
    registry['FR41']['tests']=[f'P-T{i:02}' for i in range(1,41)]
    registry['FR41']['test_link_basis']='Master 9.17 explicit module acceptance scope'
for i, nums in {1:[7,28,39],2:[11,12,15,39],3:[13,15,18,25],4:[2,6,30,31,36],5:[19,20,28],6:[11,12,20,38],7:[35,37,40],8:[1,20,28,32]}.items():
    rid=f'P-NFR{i:02}'
    if rid in registry:
        registry[rid]['tests']=[f'P-T{n:02}' for n in nums]
        registry[rid]['test_link_basis']='Reviewed M21 NFR-to-UAT control mapping'

# Reviewed HRM matrix; definition rows hold explicit UC/rule/test links.
hrm_trace=[]
for rid,item in registry.items():
    if re.fullmatch(r'M22-F\d{2}',rid):
        owned_lines=[o['line'] for o in item['occurrences'] if o['classification']=='definition_candidate' and o['text'].startswith('| M22-F')]
        related=set().union(*(refs_by_line.get(n,set()) for n in owned_lines))
        hrm_trace.append({'feature':rid,'use_cases':sorted(x for x in related if x.startswith('UC-H')),
            'rules':sorted(x for x in related if x.startswith('BR-H')),'tests':item['tests'],'source_lines':owned_lines})
for row in hrm_trace:
    for rid in row['use_cases']+row['rules']:
        registry[rid]['tests']=sorted(set(registry[rid]['tests'])|set(row['tests']))
        registry[rid]['test_link_basis']='Reviewed feature/UC/rule/test matrix in Master 3.16.3'
if 'FR42' in registry:
    registry['FR42']['tests']=[f'H-T{i:02}' for i in range(1,49)]
    registry['FR42']['test_link_basis']='Master 9.18 module acceptance scope; applicability per profile'

# Keep grouped entity declarations intact; do not invent physical names from slash shorthand.
entities, contracts, uncoded = [], [], []
section=''
for n,line in enumerate(lines,1):
    if line.startswith('#'):
        heading = line.lstrip('# ').strip()
        if re.match(r'^(?:\d+\.|CHƯƠNG|PHỤ LỤC|[A-I]\.)', heading): section=heading
    if re.match(r'^5\.',section) and not re.match(r'^\| (?:POST|GET|PATCH|PUT|DELETE) ',line) and (re.match(r'^### 5\.\d+ Bảng ',line) or (line.startswith('|') and re.match(r'^(5\.13|5\.16|5\.18|5\.20|5\.21|5\.22)\b',section))):
        first=line.strip('| ').split('|')[0].strip()
        if first in ('Bảng','Bảng logic','Entity','Endpoint') or first.startswith(('---','POST ','GET ')) or not re.search(r'[A-Z][a-zA-Z_]+',first): continue
        entities.append({'id':f'ENTITY-L{n:04}','declaration':first,'source_line':n,'section':section,'text':line,
            'owner':'M16' if section.startswith('5.20') else None,'owner_status':'proposed' if section.startswith('5.20') else 'Needs review',
            'consumers':[],'slice':'SL01 candidate' if section.startswith('5.20') else 'Unassigned',
            'priority':'Capability-dependent','applicability':'Requires physical mapping before enable',
            'implementation_status':'Logical only','tests':[],'evidence':[], 'physical_name_status':'Unresolved; preserve source grouping/aliases'})
    if (re.match(r'^(2\.5|2\.7|3\.13|5\.17|5\.20|5\.21|5\.22)\b',section) and (line.startswith('###') or re.match(r'^\| (?:POST|GET|PATCH|PUT|DELETE) ',line))):
        contracts.append({'id':f'CONTRACT-L{n:04}','source_line':n,'section':section,'text':line,'owner':'M16' if section.startswith('5.20') else None,
            'consumers':[],'slice':'SL01 candidate' if section.startswith('5.20') else 'Unassigned','priority':'Capability-dependent',
            'applicability':'Scope/version/guards must be resolved','implementation_status':'Logical / proposed','tests':[],'evidence':[]})
    if line.strip() and not line.startswith(('#','```','<a ')) and re.search(r'(?i)bắt buộc|không được|phải |không tự|chặn |không mặc định|không đồng nghĩa|fail.closed',line) and not TOKEN.search(line):
        uncoded.append({'id':f'UNNUMBERED-L{n:04}','source_line':n,'section':section,'text':line,'status':'candidate; includes historical appendix text, requires review',
            'owner':None,'consumers':[],'slice':'Unassigned','priority':'Unresolved','applicability':'Review canonical vs historical text',
            'implementation_status':'Not Implemented','tests':[],'evidence':[]})

for entity in entities:
    if entity['section'].startswith('5.22'):
        entity.update(owner='M22',owner_status='reviewed logical ownership; physical design pending',slice='SL09/SL10/SL11 per HR profile',tests=[f'H-T{i:02}' for i in range(1,49)],consumers=['M10','M14','M16','M18','M19','M20'])
    if entity['section'].startswith('5.21'):
        entity.update(owner='M21',owner_status='reviewed domain ownership; physical design pending',slice='SL08',tests=[f'P-T{i:02}' for i in range(1,41)],consumers=['M18','M19','M14','M20'])
for contract in contracts:
    if contract['section'].startswith('5.22'): contract.update(owner='M22',slice='SL09/SL10/SL11 per HR profile',tests=[f'H-T{i:02}' for i in range(1,49)])
    if contract['section'].startswith('5.21'): contract.update(owner='M21',slice='SL08',tests=[f'P-T{i:02}' for i in range(1,41)])
findings={
 'duplicate_definition_candidates': {k:v['definition_lines'] for k,v in registry.items() if len(v['definition_lines'])>1},
 'reference_only_ids': [k for k,v in registry.items() if not v['definition_lines']],
 'missing_owner': [k for k,v in registry.items() if v['owner'] is None],
 'requirements_without_extracted_test_link': [k for k,v in registry.items() if k not in tests and not v['tests']],
 'unresolved_shorthand':unresolved,
 'limitations':['Candidate definitions are heuristic; repeated applicability tables may cause false duplicate candidates.',
 'Range and same-prefix slash expansion supported; context-dependent aliases retained for manual review.',
 'No proof of semantic completeness, no physical schema certification, no application test results.',
 'Entity grouping preserves slash aliases; canonical entity ownership still requires review.',
 'Unnumbered rule candidates include historical appendices; do not treat them as new authoritative rules.']}
payload={'baseline_version':version,'source_sha256':sha,'records':list(sorted(registry.values(),key=lambda v:v['id']))}
save('trace/partner-results-trace.json',{'baseline_version':version,'source_sha256':sha,'feature_matrix':partner_trace})
save('trace/hrm-trace.json',{'baseline_version':version,'source_sha256':sha,'feature_matrix':hrm_trace})
save('trace/requirements.json',payload)
save('trace/modules.json',modules)
save('trace/entities-contracts.json',{'source_sha256':sha,'entities':entities,'contracts':contracts})
save('trace/unnumbered-rules.json',{'source_sha256':sha,'candidates':uncoded})
save('trace/findings.json',findings)
save('trace/source-sections.json',headings)
with (OUT/'trace/coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['id','kind','owner','definition_lines','test_links','verification','implementation','owner_basis'])
    for v in payload['records']: w.writerow([v['id'],v['kind'],v['owner'] or 'UNRESOLVED',','.join(map(str,v['definition_lines'])),','.join(v['tests']),v['verification_status'],v['implementation_status'],v['owner_basis']])
expected_module_count={'1.9':22,'1.8':21}.get(version,20)
checks={'module_count_matches_baseline':len(modules)==expected_module_count,'module_ids_exact':{m['id'] for m in modules}=={f'M{i:02}' for i in range(1,expected_module_count+1)},
 'FR01_40_defined':all(registry.get(f'FR{i:02}',{}).get('definition_lines') for i in range(1,41)),
 'UC01_22_defined':all(registry.get(f'UC{i:02}',{}).get('definition_lines') for i in range(1,23)),
 'work_namespaces_defined':all(registry.get(f'{p}{i:02}',{}).get('definition_lines') for p,end in [('W-F',14),('BR-W',10),('UC-W',10),('W-T',40)] for i in range(1,end+1)),
 'NFR01_12_defined':all(registry.get(f'NFR{i:02}',{}).get('definition_lines') for i in range(1,13)),
 'partner_namespaces_defined':version not in ('1.8','1.9') or all(registry.get(f'{p}{i:02}',{}).get('definition_lines') for p,end in [('M21-F',14),('UC-P',10),('BR-P',20),('P-T',40),('P-NFR',8),('P-O',8)] for i in range(1,end+1)),
 'hrm_namespaces_defined':version!='1.9' or all(registry.get(f'{p}{i:02}',{}).get('definition_lines') for p,end in [('M22-F',28),('UC-H',16),('BR-H',24),('H-T',48),('H-NFR',8),('H-O',10)] for i in range(1,end+1)),
 'hrm_trace_complete':version!='1.9' or len(hrm_trace)==28 and all(r['use_cases'] and r['rules'] and r['tests'] for r in hrm_trace),
 'no_application_pass_claims':all(v['verification_status']=='Not Run' for v in registry.values()),
 'master_unchanged':hashlib.sha256(MASTER.read_bytes()).hexdigest()==sha,
 'source_lines_valid':all(1<=o['line']<=len(lines) and lines[o['line']-1]==o['text'] for v in registry.values() for o in v['occurrences'])}
summary={'source':str(MASTER),'version':version,'sha256':sha,'source_lines':len(lines),'generated_at':datetime.now(timezone.utc).isoformat(),
 'counts':{'modules':len(modules),'unique_id_candidates':len(registry),'definition_candidates':sum(bool(v['definition_lines']) for v in registry.values()),
 'reference_only_ids':len(findings['reference_only_ids']),'duplicate_definition_candidates':len(findings['duplicate_definition_candidates']),
 'missing_owner':len(findings['missing_owner']),'without_test_link':len(findings['requirements_without_extracted_test_link']),
 'entity_declarations':len(entities),'contract_declarations':len(contracts),'unnumbered_candidates':len(uncoded),'unresolved_shorthand_lines':len(unresolved)},'checks':checks}
save('evidence/inventory-validation.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
if not all(checks.values()): raise SystemExit('Inventory checks failed; inspect before delivery')
