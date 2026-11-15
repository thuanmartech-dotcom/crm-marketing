"""Validate documentation integrity and HRM trace, never application behavior."""
from pathlib import Path
import json, re, hashlib, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf8')
root = Path(__file__).resolve().parents[1]
master = root / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
specs = root / '02-specs'
planning = root / '03-planning'
archive = root / '99-archive'

text = master.read_text(encoding='utf8')
sha = hashlib.sha256(master.read_bytes()).hexdigest()
records = {r['id']: r for r in json.loads((planning / 'trace' / 'requirements.json').read_text(encoding='utf8'))['records']}
trace = json.loads((planning / 'trace' / 'hrm-trace.json').read_text(encoding='utf8'))

prefixes = {'M22-F': 28, 'UC-H': 16, 'BR-H': 24, 'H-T': 48, 'H-NFR': 8, 'H-O': 10}
expected = {f'{p}{i:02}' for p, end in prefixes.items() for i in range(1, end + 1)}
checks = {
    'all_hrm_ids_defined_once': all(rid in records and len(records[rid]['definition_lines']) == 1 for rid in expected),
    'all_hrm_ids_owned_by_M22': all(records[rid]['owner'] == 'M22' for rid in expected),
    'feature_trace_covers_28': len(trace['feature_matrix']) == 28,
    'all_features_link_uc_rule_tests': all(r['use_cases'] and r['rules'] and r['tests'] for r in trace['feature_matrix']),
    'trace_references_resolve': all(ref in records for r in trace['feature_matrix'] for k in ['use_cases', 'rules', 'tests'] for ref in r[k]),
    'every_test_covered_by_feature': {t for r in trace['feature_matrix'] for t in r['tests']} == {f'H-T{i:02}' for i in range(1, 49)},
    'uc_rules_nfr_have_test_links': all(records[rid]['tests'] for rid in expected if rid.startswith(('UC-H', 'BR-H', 'H-NFR'))),
    'no_hrm_app_pass_claim': all(records[rid]['verification_status'] == 'Not Run' for rid in expected),
    'trace_hash_current': trace['source_sha256'] == sha,
    'manifest_hash_current': json.loads((planning / 'agent' / 'active-task.json').read_text(encoding='utf8'))['baseline_sha256'] == sha,
    'readme_hash_current': sha in (planning / 'README.md').read_text(encoding='utf8'),
    'archive_baseline_preserved': (archive / 'master-versions' / 'CRM_MASTER_v1.8_BEFORE_HRM_2026-10-18.md').exists(),
    'no_crcrlf': b'\r\r\n' not in master.read_bytes(),
}
source = (archive / 'legacy-working-drafts' / 'hrm_sections.md').read_text(encoding='utf8')
parts = re.split(r'<!-- SECTION:([3456789A]) -->\s*', source)
module = (specs / 'modules' / 'M22-HUMAN-RESOURCES.md').read_text(encoding='utf8')
checks['all_reviewed_sections_in_master_and_module'] = all(s.strip() in text and s.strip() in module for s in parts[2::2])
checks['module_anchor_unique'] = text.count('<a id="module-m22"></a>') == 1

result = {
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'baseline': '1.9',
    'sha256': sha,
    'kind': 'documentation structural validation only',
    'counts': prefixes,
    'checks': checks,
    'application_tests': 'Not Run',
    'limitations': [
        'Policy parameters, actual Excel data and physical schema remain unconfirmed.',
        'Legacy registry unresolved owners are preserved, not claimed fixed by M22.',
    ],
}
(planning / 'evidence' / 'hrm-integration-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert all(checks.values()), 'HRM validation failed'
