"""Analyze & traceability check for 02-specs/ modules, slices, contracts, changes, and skills.
Artifact checks only; never executes or certifies application code.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
SPECS = ROOT / '02-specs'
PLANNING = ROOT / '03-planning'
SKILLS = ROOT / '.agents' / 'skills'

# Remove M18-BI-REPORTING-EXPANSION.md once M18-F01..07 baseline is fully decomposed into it.
LEGACY_EXEMPT_MODULES = {
    'M18-BI-REPORTING-EXPANSION.md',
    'M21-PARTNER-BUSINESS-RESULTS.md',
    'M22-HUMAN-RESOURCES.md',
    'M23-SYSTEM-ADMIN-SECURITY-OPS.md',
    'M24-PERFORMANCE-AND-PRODUCTIVITY.md',
}

LEGACY_EXEMPT_SLICES = {
    'SL01-INTERNAL-WORK.md',
    'SL08-PARTNER-RESULTS.md',
    'SL09-11-HRM.md',
}

REQUIRED_MODULE_SECTIONS = [
    ('manifest', r'^##\s+(?:\d+\.\s*)?Manifest\b'),
    ('requirement_trace', r'^##\s+(?:\d+\.\s*)?Requirement\s+trace\b'),
    ('hanh_vi', r'^##\s+(?:\d+\.\s*)?Hành\s+vi\b'),
    ('data_api', r'^##\s+(?:\d+\.\s*)?Data/API\b'),
    ('ui_operations', r'^##\s+(?:\d+\.\s*)?UI/operations\b'),
    ('migration_gate', r'^##\s+(?:\d+\.\s*)?Migration\b'),
]

REQUIRED_SLICE_SECTIONS = [
    ('manifest', r'^##\s+(?:\d+\.\s*)?Manifest\b'),
    ('scope', r'^##\s+(?:\d+\.\s*)?(?:Phạm\s+vi|Scope)\b'),
    ('flow', r'^##\s+(?:\d+\.\s*)?Luồng\b'),
    ('test_matrix', r'^##\s+(?:\d+\.\s*)?Test\b'),
    ('gates_gaps', r'^##\s+(?:\d+\.\s*)?(?:Danh\s+sách\s+Gate|Gate|Gap)\b'),
]

REQUIRED_CONTRACT_PARTS = [
    'Meaning', 'Actor/scope', 'Preconditions', 'Input', 'Output',
    'Errors', 'Concurrency', 'Idempotency', 'Transaction',
    'Compatibility', 'Audit/privacy', 'Tests',
]


def check_markdown_basics(path: Path) -> tuple[bool, list[str], bool]:
    text = path.read_text(encoding='utf-8')
    fences_balanced = (len(re.findall(r'^`{3,}', text, re.M)) % 2) == 0
    bad_links: list[str] = []
    for href in re.findall(r'\]\(([^)]+)\)', text):
        if href.startswith(('http://', 'https://', '#')):
            continue
        target = (path.parent / href.split('#')[0]).resolve()
        if not target.exists():
            bad_links.append(href)
    fake_pass = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|') or re.match(r'^\|[\s:-]+\|$', stripped):
            continue
        cells = [c.strip().strip('`*_ ').lower() for c in stripped.strip('|').split('|')]
        if any(c in {'pass', 'passed', 'verified'} for c in cells):
            fake_pass = True
            break
    return fences_balanced, bad_links, not fake_pass


def load_owned_ids_by_module() -> dict[str, list[str]]:
    req_path = PLANNING / 'trace' / 'requirements.json'
    if not req_path.exists():
        return {}
    records = json.loads(req_path.read_text(encoding='utf-8')).get('records', [])
    by_owner: dict[str, list[str]] = {}
    for rec in records:
        owner = rec.get('owner')
        if owner and re.match(r'^M\d{2}$', owner):
            by_owner.setdefault(owner, []).append(rec['id'])
    return {k: sorted(set(v)) for k, v in by_owner.items()}


def missing_owned_ids(mod_id: str, combined_text: str, owned_map: dict[str, list[str]]) -> list[str]:
    ids = owned_map.get(mod_id, [])
    return [
        rid for rid in ids
        if not re.search(rf'(?<![A-Za-z0-9_-]){re.escape(rid)}(?![A-Za-z0-9_-])', combined_text)
    ]


def check_module_file(
    path: Path,
    baseline_sha: str,
    owned_map: dict[str, list[str]],
    strict_all: bool = False,
) -> dict:
    text = path.read_text(encoding='utf-8')
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    is_legacy = (path.name in LEGACY_EXEMPT_MODULES) and not strict_all

    missing_sections: list[str] = []
    if not is_legacy:
        for key, pattern in REQUIRED_MODULE_SECTIONS:
            if not re.search(pattern, text, re.M | re.I):
                missing_sections.append(key)

    has_provenance_tags = bool(re.search(r'\[(MASTER|PROPOSED|OPEN-GAP(?::[^\]]+)?)\]', text))
    has_baseline_ref = (baseline_sha in text) or ('1.9' in text)

    mod_match = re.match(r'^(M\d{2})-', path.name)
    mod_id = mod_match[1] if mod_match else None
    missing_ids = missing_owned_ids(mod_id, text, owned_map) if mod_id else []
    trace_ids_complete = (len(missing_ids) == 0)

    passed = fences_ok and (not bad_links) and no_fake_pass and (not missing_sections)
    if not is_legacy:
        passed = passed and has_provenance_tags and has_baseline_ref and trace_ids_complete

    return {
        'file': str(path.relative_to(ROOT)),
        'mode': 'legacy_or_extension' if is_legacy else 'standard_module_spec',
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_sections': missing_sections,
        'has_provenance_tags': has_provenance_tags,
        'has_baseline_ref': has_baseline_ref,
        'trace_ids_complete': trace_ids_complete,
        'missing_ids_count': len(missing_ids),
        'missing_ids_sample': missing_ids[:25],
        'passed': passed,
    }


def check_slice_file(path: Path, baseline_sha: str, strict_all: bool = False) -> dict:
    text = path.read_text(encoding='utf-8')
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    is_legacy = (path.name in LEGACY_EXEMPT_SLICES) and not strict_all

    missing_sections: list[str] = []
    if not is_legacy:
        for key, pattern in REQUIRED_SLICE_SECTIONS:
            if not re.search(pattern, text, re.M | re.I):
                missing_sections.append(key)

    has_baseline_ref = (baseline_sha in text) or ('1.9' in text)
    passed = fences_ok and (not bad_links) and no_fake_pass and (not missing_sections)
    if not is_legacy:
        passed = passed and has_baseline_ref

    return {
        'file': str(path.relative_to(ROOT)),
        'mode': 'legacy_slice' if is_legacy else 'standard_slice_spec',
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_sections': missing_sections,
        'has_baseline_ref': has_baseline_ref,
        'passed': passed,
    }


def check_contract_file(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    missing_parts = [p for p in REQUIRED_CONTRACT_PARTS if not re.search(re.escape(p), text, re.I)]
    passed = fences_ok and (not bad_links) and no_fake_pass and (not missing_parts)
    return {
        'file': str(path.relative_to(ROOT)),
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_contract_parts': missing_parts,
        'passed': passed,
    }


def check_basic_doc_file(path: Path) -> dict:
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    return {
        'file': str(path.relative_to(ROOT)),
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'passed': fences_ok and (not bad_links) and no_fake_pass,
    }


def compute_trace_coverage(module_files: list[Path], owned_map: dict[str, list[str]]) -> dict:
    files_by_mod: dict[str, list[Path]] = {}
    for mf in module_files:
        m = re.match(r'^(M\d{2})-', mf.name)
        if m:
            files_by_mod.setdefault(m[1], []).append(mf)

    coverage: dict[str, dict] = {}
    for mod in sorted(owned_map):
        ids = owned_map[mod]
        if mod not in files_by_mod:
            coverage[mod] = {
                'spec_files': [],
                'total_owned_ids': len(ids),
                'covered_ids': 0,
                'missing_ids_count': len(ids),
                'status': 'not_decomposed_yet',
            }
            continue
        combined = '\n'.join(p.read_text(encoding='utf-8') for p in files_by_mod[mod])
        missing = missing_owned_ids(mod, combined, owned_map)
        coverage[mod] = {
            'spec_files': [str(p.relative_to(ROOT)) for p in files_by_mod[mod]],
            'total_owned_ids': len(ids),
            'covered_ids': len(ids) - len(missing),
            'missing_ids_count': len(missing),
            'missing_ids_sample': missing[:25],
            'status': 'complete_id_mentions' if not missing else 'partial_id_mentions',
        }
    return coverage


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate CRM BA specs, slices, contracts, skills, and traceability.')
    parser.add_argument('--file', help='Optional single spec file path (relative to repo root or absolute).')
    parser.add_argument('--strict-all', action='store_true', help='Enforce standard spec sections on legacy/CR modules & slices too.')
    args = parser.parse_args()

    baseline_sha = hashlib.sha256(MASTER.read_bytes()).hexdigest()
    owned_map = load_owned_ids_by_module()

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = (ROOT / target).resolve()
        if not target.exists():
            print(json.dumps({'error': f'File not found: {args.file}'}, ensure_ascii=False, indent=2))
            return 1
        if 'contracts' in target.parts:
            res = check_contract_file(target)
        elif 'changes' in target.parts or '.agents' in target.parts:
            res = check_basic_doc_file(target)
        elif 'slices' in target.parts:
            res = check_slice_file(target, baseline_sha, strict_all=args.strict_all)
        else:
            res = check_module_file(target, baseline_sha, owned_map, strict_all=args.strict_all)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res['passed'] else 1

    module_files = sorted((SPECS / 'modules').glob('*.md')) if (SPECS / 'modules').exists() else []
    slice_files = sorted((SPECS / 'slices').glob('*.md')) if (SPECS / 'slices').exists() else []
    contract_files = sorted((SPECS / 'contracts').glob('*.md')) if (SPECS / 'contracts').exists() else []
    change_files = sorted((SPECS / 'changes').rglob('*.md')) if (SPECS / 'changes').exists() else []
    skill_files = sorted(SKILLS.rglob('*.md')) if SKILLS.exists() else []

    module_results = [check_module_file(p, baseline_sha, owned_map, strict_all=args.strict_all) for p in module_files]
    slice_results = [check_slice_file(p, baseline_sha, strict_all=args.strict_all) for p in slice_files]
    contract_results = [check_contract_file(p) for p in contract_files]
    change_results = [check_basic_doc_file(p) for p in change_files]
    skill_results = [check_basic_doc_file(p) for p in skill_files]
    coverage = compute_trace_coverage(module_files, owned_map)

    all_results = module_results + slice_results + contract_results + change_results + skill_results
    all_passed = all(r['passed'] for r in all_results)
    partial_modules = {
        mod: info['missing_ids_count']
        for mod, info in coverage.items()
        if info['status'] == 'partial_id_mentions'
    }

    report = {
        'run_at': datetime.now(timezone.utc).isoformat(),
        'kind': 'spec-analyze-and-traceability validation only',
        'baseline_sha256': baseline_sha,
        'all_passed': all_passed,
        'modules_checked': len(module_results),
        'slices_checked': len(slice_results),
        'contracts_checked': len(contract_results),
        'changes_checked': len(change_results),
        'skills_checked': len(skill_results),
        'partial_trace_warnings': partial_modules,
        'module_results': module_results,
        'slice_results': slice_results,
        'contract_results': contract_results,
        'change_results': change_results,
        'skill_results': skill_results,
        'trace_coverage': coverage,
        'application_tests': 'Not Run',
    }
    evidence_file = PLANNING / 'evidence' / 'module-spec-validation.json'
    evidence_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'all_passed': all_passed,
        'modules_checked': len(module_results),
        'slices_checked': len(slice_results),
        'contracts_checked': len(contract_results),
        'changes_checked': len(change_results),
        'skills_checked': len(skill_results),
        'partial_trace_warnings': partial_modules,
        'evidence': str(evidence_file.relative_to(ROOT)),
        'application_tests': 'Not Run',
    }, ensure_ascii=False, indent=2))
    return 0 if all_passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
