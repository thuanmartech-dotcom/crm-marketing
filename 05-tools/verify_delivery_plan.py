"""Artifact checks only. Does not execute or certify CRM behavior."""
from pathlib import Path
import hashlib, json, re, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
master = root / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
arch = root / '01-architecture'
specs = root / '02-specs'
planning = root / '03-planning'
research = root / '04-research'

checks = {}
inventory = json.loads((planning / 'evidence' / 'inventory-validation.json').read_text(encoding='utf8'))
checks['master_hash_matches_baseline'] = hashlib.sha256(master.read_bytes()).hexdigest() == inventory['sha256']
checks['inventory_checks_pass'] = all(inventory['checks'].values())

bad_links = []
bad_fences = []
loaded = []

for folder in (planning, research):
    for p in folder.rglob('*.json'):
        json.loads(p.read_text(encoding='utf8'))
        loaded.append(str(p.relative_to(root)))

md_files = [root / 'README.md', root / 'AGENTS.md']
for folder in (arch, specs, planning, research):
    md_files.extend(folder.rglob('*.md'))

for p in sorted(set(md_files)):
    if not p.exists():
        continue
    text = p.read_text(encoding='utf8')
    if len(re.findall(r'^```', text, re.M)) % 2:
        bad_fences.append(str(p.relative_to(root)))
    for href in re.findall(r'\]\(([^)]+)\)', text):
        if href.startswith(('http://', 'https://', '#')):
            continue
        target = (p.parent / href.split('#')[0]).resolve()
        if not target.exists():
            bad_links.append({'file': str(p.relative_to(root)), 'target': href})

checks['markdown_links_exist'] = not bad_links
checks['markdown_fences_balanced'] = not bad_fences

spec = (specs / 'slices' / 'SL01-INTERNAL-WORK.md').read_text(encoding='utf8')
table = spec.split('## 9. Test applicability')[1].split('W-T18 đầy đủ')[0]
assigned = []
test_cells = '\n'.join(line.split('|')[2] for line in table.splitlines() if line.startswith('|') and len(line.split('|')) > 3)
for m in re.finditer(r'W-T(\d{2})((?:/\d{2})*)', test_cells):
    assigned += [int(m[1])] + [int(s) for s in m[2].split('/') if s]
checks['work_tests_01_40_classified_once'] = sorted(assigned) == list(range(1, 41))

manifest = json.loads((planning / 'agent' / 'active-task.json').read_text(encoding='utf8'))
checks['manifest_baseline_path_resolves'] = (planning / 'agent' / manifest['baseline_path']).resolve() == master.resolve()
checks['manifest_read_first_exists'] = all((planning / 'agent' / p).exists() for p in manifest['read_first'])

records = json.loads((planning / 'trace' / 'requirements.json').read_text(encoding='utf8'))['records']
checks['unique_registry_keys'] = len(records) == len({r['id'] for r in records})
checks['required_registry_fields'] = all(
    all(k in r for k in ['id', 'source', 'owner', 'consumers', 'slice', 'priority', 'applicability', 'implementation_status', 'tests', 'evidence'])
    for r in records
)
checks['no_claimed_application_pass'] = all(r['verification_status'] == 'Not Run' and not r['evidence'] for r in records)

required = [
    'README.md',
    'AGENTS.md',
    '00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md',
    '01-architecture/INDEX.md',
    '01-architecture/INVARIANTS.md',
    '01-architecture/decisions/ADR-001-BASELINE-AND-STACK.md',
    '02-specs/README.md',
    '02-specs/modules/M21-PARTNER-BUSINESS-RESULTS.md',
    '02-specs/modules/M22-HUMAN-RESOURCES.md',
    '02-specs/slices/SL01-INTERNAL-WORK.md',
    '02-specs/slices/SL08-PARTNER-RESULTS.md',
    '02-specs/slices/SL09-11-HRM.md',
    '02-specs/templates/MODULE-SPEC.md',
    '02-specs/templates/CONTRACT.md',
    '03-planning/README.md',
    '03-planning/GAPS.md',
    '03-planning/ROADMAP.md',
    '03-planning/agent/active-task.json',
    '03-planning/agent/PROGRESS.md',
]
checks['deliverables_exist'] = all((root / p).exists() for p in required)

result = {
    'run_at': datetime.now(timezone.utc).isoformat(),
    'kind': 'documentation-and-inventory validation only',
    'checks': checks,
    'bad_links': bad_links,
    'bad_fences': bad_fences,
    'json_files_loaded': sorted(loaded),
    'application_tests': 'Not Run',
    'mermaid_rendering': 'Not Run; fences only checked',
}
(planning / 'evidence' / 'package-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, ensure_ascii=False, indent=2))
if not all(checks.values()):
    raise SystemExit('Artifact validation failed')
