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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from context_integrity import context_issues, wave_guard_issues
from build_module_context import check_session_tokens  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
SPECS = ROOT / '02-specs'
PLANNING = ROOT / '03-planning'
SKILLS = ROOT / '.agents' / 'skills'

# Keep only un-decomposed baseline / prior-wave specs exempt until their scheduled upgrade wave.
LEGACY_EXEMPT_MODULES = {
    'M18-BI-REPORTING-EXPANSION.md',
    'M21-PARTNER-BUSINESS-RESULTS.md',
    'M22-HUMAN-RESOURCES.md',
}

LEGACY_EXEMPT_SLICES = {
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


def load_known_contract_surface() -> dict[str, set[str]]:
    """Collect published events, contract port names, and owned tables per contracted module."""
    known: dict[str, set[str]] = {}
    contract_dir = SPECS / 'contracts'
    if contract_dir.exists():
        for cpath in contract_dir.glob('*.md'):
            mod = cpath.name.split('-')[0]
            txt = cpath.read_text(encoding='utf-8')
            syms = set(re.findall(rf'\b{re.escape(mod)}\.([A-Z][A-Za-z0-9_]+)\b', txt))
            for h in re.findall(r'^###\s+2\.\d+.*', txt, re.M):
                for tok in re.findall(r'`([A-Z][A-Za-z0-9_]+)`', h):
                    syms.add(tok)
                    base = re.sub(r'(?:Input|Output|Decision|Result|Note)$', '', tok)
                    if base:
                        syms.add(base)
            known.setdefault(mod, set()).update(syms)
    module_dir = SPECS / 'modules'
    if module_dir.exists():
        for mpath in module_dir.glob('*.md'):
            mod = mpath.name.split('-')[0]
            if mod in known:
                txt = mpath.read_text(encoding='utf-8')
                syms = set(re.findall(r'\|\s*(?:\d+\s*\|\s*)?`([A-Z][A-Za-z0-9_]+)`', txt))
                known[mod].update(syms)
    return known


def find_unknown_cross_module_refs(mod_id: str | None, text: str, known_surface: dict[str, set[str]]) -> list[str]:
    if not mod_id:
        return []
    unknown: set[str] = set()
    for target_mod, sym in re.findall(r'`(M\d{2})\.([A-Z][A-Za-z0-9_]+)`', text):
        if target_mod != mod_id and target_mod in known_surface:
            if sym not in known_surface[target_mod]:
                unknown.add(f'{target_mod}.{sym}')
    return sorted(unknown)


def check_cross_doc_consistency(baseline_sha: str) -> dict:
    """Check manifest status sync and cross-document semantic invariants (W1-01..W1-05)."""
    issues: list[str] = context_issues() + wave_guard_issues()
    manifest_path = PLANNING / 'agent' / 'active-task.json'
    plan_path = PLANNING / 'DECOMPOSITION-PLAN.md'
    specs_readme_path = SPECS / 'README.md'

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('baseline_sha256') != baseline_sha:
            issues.append('active-task.json baseline_sha256 does not match Master v1.9')
        next_actions_joined = ' '.join(manifest.get('next_actions', []))
        if 'M01-M20' in next_actions_joined and 'Wave 2' not in next_actions_joined:
            issues.append('active-task.json next_actions contains stale M01-M20 text after Wave 1')
        if manifest.get('application_write_scope') is not None:
            issues.append('active-task.json application_write_scope must remain null in Documentation-Only phase')

        wave1_specs = manifest.get('wave1_specs', {})
        if not wave1_specs:
            issues.append('active-task.json missing wave1_specs status map')
        else:
            plan_txt = plan_path.read_text(encoding='utf-8') if plan_path.exists() else ''
            readme_txt = specs_readme_path.read_text(encoding='utf-8') if specs_readme_path.exists() else ''
            for key, status_val in wave1_specs.items():
                if status_val != 'Reviewed':
                    issues.append(f'wave1_specs[{key}] expected Reviewed, got {status_val}')
                if key.startswith('M') and f'`{key}`' in plan_txt:
                    # Verify DECOMPOSITION-PLAN row does not revert to Draft/Chờ
                    row_match = re.search(rf'\|\s*`{re.escape(key)}[^`]*`\s*[^\n]*\n', plan_txt)
                    if row_match and ('Reviewed' not in row_match.group(0)):
                        issues.append(f'DECOMPOSITION-PLAN.md row for {key} does not report Reviewed')
                if key.startswith('M') and readme_txt:
                    row_match = re.search(rf'\|\s*{re.escape(key)}\s*\|[^\n]+\n', readme_txt)
                    if row_match and ('Reviewed' not in row_match.group(0)):
                        issues.append(f'02-specs/README.md row for {key} does not report Reviewed')

    # Check W1-01 globally across all modules, contracts, slices & ADR-004
    m16_path = SPECS / 'modules' / 'M16-WORK-PROJECTS-TASK-CORE.md'
    adr004_path = ROOT / '01-architecture' / 'decisions' / 'ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md'
    for p in (m16_path, adr004_path):
        if p.exists():
            txt = p.read_text(encoding='utf-8')
            if 'WHERE privacy_redacted_at IS NULL' in txt or 'CHECK / WHERE privacy_redacted_at IS NULL' in txt:
                issues.append(f'{p.relative_to(ROOT)} still contains single-shot privacy_redacted_at IS NULL lock (W1-01)')
            if 'redacted_deletion_ledger_ids' not in txt or 'redacted_content_sha256' not in txt:
                issues.append(f'{p.relative_to(ROOT)} missing multi-subject redaction tracking fields (W1-01)')
    for folder in (SPECS / 'modules', SPECS / 'contracts', SPECS / 'slices'):
        if folder.exists():
            for p in folder.glob('*.md'):
                txt = p.read_text(encoding='utf-8')
                if re.search(r'(?:WHERE|CHECK(?:\s*/\s*WHERE)?)\s+privacy_redacted_at\s+IS\s+NULL', txt, re.I):
                    issues.append(f'{p.relative_to(ROOT)} uses forbidden single-shot privacy_redacted_at IS NULL lock (INV-27 / W1-01)')

    # Check W1-02 & W1-03: M19, C19, ADR-005 must share lease_token CAS fencing and 8-branch reaper rule
    m19_path = SPECS / 'modules' / 'M19-INTEGRATION-ADAPTERS-OUTBOX.md'
    c19_path = SPECS / 'contracts' / 'M19-DURABLE-INGEST-OUTBOX.md'
    adr005_path = ROOT / '01-architecture' / 'decisions' / 'ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md'
    for p in (m19_path, c19_path, adr005_path):
        if p.exists():
            txt = p.read_text(encoding='utf-8')
            if 'lease_token' not in txt:
                issues.append(f'{p.relative_to(ROOT)} missing lease_token fencing specification (W1-02)')
            if 'EXPIRED_CANCELLED' not in txt or 'RETRY_WAITING' not in txt or 'QUEUED' not in txt or 'UNKNOWN_OUTCOME' not in txt:
                issues.append(f'{p.relative_to(ROOT)} missing full 8-branch reaper state transitions (W1-03)')

    # Check W1-04: C16 W-T15 summary must not state WithdrawSubmission returns 409
    c16_path = SPECS / 'contracts' / 'M16-TASK-CORE-COMMANDS.md'
    if c16_path.exists():
        c16_txt = c16_path.read_text(encoding='utf-8')
        if 'rút submission (WithdrawSubmission) hay sửa khi đang duyệt trả 409' in c16_txt:
            issues.append('C16 still has contradictory W-T15 summary stating WithdrawSubmission returns 409 (W1-04)')

    # Check Anti-Loss Context Persistence across Wave 2-6
    inv_path = ROOT / '01-architecture' / 'INVARIANTS.md'
    if inv_path.exists():
        inv_txt = inv_path.read_text(encoding='utf-8')
        for inv_id in ('INV-26', 'INV-27', 'INV-28'):
            if inv_id not in inv_txt:
                issues.append(f'01-architecture/INVARIANTS.md missing {inv_id}')

    progress_path = PLANNING / 'agent' / 'PROGRESS.md'
    if progress_path.exists():
        prog_txt = progress_path.read_text(encoding='utf-8')
        if '## 0. Sticky Wave Context' not in prog_txt:
            issues.append('03-planning/agent/PROGRESS.md missing "## 0. Sticky Wave Context" top anchor')

    reg_path = SPECS / 'CONTRACTS-REGISTRY.md'
    if reg_path.exists():
        reg_txt = reg_path.read_text(encoding='utf-8')
        for cp in sorted((SPECS / 'contracts').glob('*.md')):
            if cp.name not in reg_txt:
                issues.append(f'02-specs/CONTRACTS-REGISTRY.md missing contract {cp.name} (re-run --build-registry)')
        for adrp in sorted((ROOT / '01-architecture' / 'decisions').glob('ADR-*.md')):
            if adrp.name not in reg_txt:
                issues.append(f'02-specs/CONTRACTS-REGISTRY.md missing ADR {adrp.name} (re-run --build-registry)')
        if 'INV-26' not in reg_txt or 'INV-27' not in reg_txt or 'INV-28' not in reg_txt:
            issues.append('02-specs/CONTRACTS-REGISTRY.md missing INV-26..28 section 4b (re-run --build-registry)')

    return {
        'passed': len(issues) == 0,
        'issues': issues,
    }


def check_module_file(
    path: Path,
    baseline_sha: str,
    owned_map: dict[str, list[str]],
    strict_all: bool = False,
    known_surface: dict[str, set[str]] | None = None,
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
    has_precondition_blocks = bool(re.search(r'^\s*-\s+\*\*Tiền điều kiện', text, re.M))
    has_base_scope_columns = all(col in text for col in ('branch_id', 'legal_entity_id', 'business_line_id'))
    test_header_match = re.search(r'^(\|\s*Mã Test\s*\|[^\r\n]+)$', text, re.M)
    if test_header_match:
        cols = [c.strip() for c in test_header_match.group(1).strip().strip('|').split('|')]
        header_joined = ' | '.join(cols)
        has_10col_test_matrix = (
            len(cols) == 10
            and all(req in header_joined for req in ('Severity', 'Fixture', 'Build', 'Actual'))
            and (('Status' in header_joined) or ('Evidence' in header_joined))
        )
    else:
        has_10col_test_matrix = False

    mod_match = re.match(r'^(M\d{2})-', path.name)
    mod_id = mod_match[1] if mod_match else None
    missing_ids = missing_owned_ids(mod_id, text, owned_map) if mod_id else []
    trace_ids_complete = (len(missing_ids) == 0)
    unknown_cross_refs = find_unknown_cross_module_refs(mod_id, text, known_surface or {})

    passed = fences_ok and (not bad_links) and no_fake_pass and (not missing_sections)
    if not is_legacy:
        passed = (
            passed
            and has_provenance_tags
            and has_baseline_ref
            and has_precondition_blocks
            and has_base_scope_columns
            and has_10col_test_matrix
            and trace_ids_complete
            and (not unknown_cross_refs)
        )

    return {
        'file': str(path.relative_to(ROOT)),
        'mode': 'legacy_or_extension' if is_legacy else 'standard_module_spec',
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_sections': missing_sections,
        'has_provenance_tags': has_provenance_tags,
        'has_baseline_ref': has_baseline_ref,
        'has_precondition_blocks': has_precondition_blocks,
        'has_base_scope_columns': has_base_scope_columns,
        'has_10col_test_matrix': has_10col_test_matrix,
        'trace_ids_complete': trace_ids_complete,
        'missing_ids_count': len(missing_ids),
        'missing_ids_sample': missing_ids[:25],
        'unknown_cross_module_refs': unknown_cross_refs,
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
    import json

    text = path.read_text(encoding='utf-8')
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    missing_parts = [p for p in REQUIRED_CONTRACT_PARTS if not re.search(re.escape(p), text, re.I)]
    normalized = text.replace('\r\n', '\n')
    json_blocks = re.findall(r'```json\s*\n(.*?)\n```', normalized, re.S)
    invalid_json_blocks = []
    for idx, block in enumerate(json_blocks):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            invalid_json_blocks.append(f'block#{idx}: {exc.msg} (line {exc.lineno})')
    has_json_schemas = len(json_blocks) >= 2
    has_event_envelope_fields = ('correlation_id' in text) and ('schema_version' in text)
    passed = (
        fences_ok
        and (not bad_links)
        and no_fake_pass
        and (not missing_parts)
        and has_json_schemas
        and (not invalid_json_blocks)
        and has_event_envelope_fields
    )
    return {
        'file': str(path.relative_to(ROOT)),
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_contract_parts': missing_parts,
        'json_schema_count': len(json_blocks),
        'invalid_json_blocks': invalid_json_blocks,
        'has_event_envelope_fields': has_event_envelope_fields,
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
    known_surface = load_known_contract_surface()
    token_telemetry = check_session_tokens()

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = (ROOT / target).resolve()
        if not target.exists():
            print(json.dumps({'error': f'File not found: {args.file}'}, ensure_ascii=False, indent=2))
            return 1
        if 'contracts' in target.parts:
            res = check_contract_file(target)
        elif 'changes' in target.parts or '.agents' in target.parts or target.name == 'CONTRACTS-REGISTRY.md':
            res = check_basic_doc_file(target)
        elif 'slices' in target.parts:
            res = check_slice_file(target, baseline_sha, strict_all=args.strict_all)
        else:
            res = check_module_file(target, baseline_sha, owned_map, strict_all=args.strict_all, known_surface=known_surface)
        res['session_token_telemetry'] = token_telemetry
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res['passed'] else 1

    module_files = sorted((SPECS / 'modules').glob('*.md')) if (SPECS / 'modules').exists() else []
    slice_files = sorted((SPECS / 'slices').glob('*.md')) if (SPECS / 'slices').exists() else []
    contract_files = sorted((SPECS / 'contracts').glob('*.md')) if (SPECS / 'contracts').exists() else []
    change_files = sorted((SPECS / 'changes').rglob('*.md')) if (SPECS / 'changes').exists() else []
    skill_files = sorted(SKILLS.rglob('*.md')) if SKILLS.exists() else []
    registry_file = SPECS / 'CONTRACTS-REGISTRY.md'

    module_results = [
        check_module_file(p, baseline_sha, owned_map, strict_all=args.strict_all, known_surface=known_surface)
        for p in module_files
    ]
    slice_results = [check_slice_file(p, baseline_sha, strict_all=args.strict_all) for p in slice_files]
    contract_results = [check_contract_file(p) for p in contract_files]
    change_results = [check_basic_doc_file(p) for p in change_files]
    skill_results = [check_basic_doc_file(p) for p in skill_files]
    registry_results = [check_basic_doc_file(registry_file)] if registry_file.exists() else []
    coverage = compute_trace_coverage(module_files, owned_map)
    cross_doc_consistency = check_cross_doc_consistency(baseline_sha)

    all_results = module_results + slice_results + contract_results + change_results + skill_results + registry_results
    all_passed = all(r['passed'] for r in all_results) and cross_doc_consistency['passed']
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
        'registry_checked': len(registry_results),
        'partial_trace_warnings': partial_modules,
        'cross_doc_consistency': cross_doc_consistency,
        'module_results': module_results,
        'slice_results': slice_results,
        'contract_results': contract_results,
        'change_results': change_results,
        'skill_results': skill_results,
        'registry_results': registry_results,
        'trace_coverage': coverage,
        'session_token_telemetry': token_telemetry,
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
        'registry_checked': len(registry_results),
        'partial_trace_warnings': partial_modules,
        'cross_doc_consistency': cross_doc_consistency,
        'evidence': str(evidence_file.relative_to(ROOT)),
        'session_token_telemetry': token_telemetry,
        'application_tests': 'Not Run',
    }, ensure_ascii=False, indent=2))
    return 0 if all_passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
