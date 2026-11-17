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
from context_integrity import context_issues, find_inv27_erasure_issues, wave_guard_issues  # noqa: E402
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

REQUIRED_BEHAVIOR_SUBPARTS = [
    ('muc_tieu', r'^\s*-\s+\*\*Mục tiêu\s*&\s*Phạm vi\b'),
    ('tac_nhan', r'^\s*-\s+\*\*Tác nhân\s*&\s*Kích hoạt\b'),
    ('tien_dieu_kien', r'^\s*-\s+\*\*Tiền điều kiện\b'),
    ('mo_ta', r'^\s*-\s+\*\*Mô tả Nghiệp vụ\b'),
    ('dong_thoi', r'^\s*-\s+\*\*(?:Xử lý\s+)?Đồng thời\b'),
    ('ears', r'^\s*-\s+\*\*(?:Ngoại lệ\s*&\s*)?Quy tắc Hành vi\b'),
]

REQUIRED_APPROVAL_FIELDS = (
    'Approved_Scope',
    'Approved_By',
    'Decision_Ref',
    'Approved_At',
)

REQUIRED_ENVELOPE_FIELDS = (
    'event_id',
    'event_type',
    'schema_version',
    'tenant_id',
    'occurred_at',
    'correlation_id',
)

FORBIDDEN_IMMUTABLE_COLS = ('updated_at', 'updated_by', 'row_version', 'archived_at')
GAP_ID_TOKEN_RE = re.compile(r'\b(?:GAP-[A-Z0-9-]+|W-O\d{2}|P-O\d{2}|H-O\d{2}|O\d{2})\b')
PLACEHOLDER_VALUE_RE = re.compile(
    r'^(?:điền\b.*|tbd\b.*|todo\b.*|\.{3}|<[^>]+>|-\s*|\s*|n/a\s*\(draft\)|n/a)$',
    re.I,
)


def _display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def strip_html_comments(text: str) -> str:
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def extract_section(text: str, start_heading_re: str, level: int = 2) -> str:
    normalized = text.replace('\r\n', '\n')
    m = re.search(start_heading_re, normalized, re.M | re.I)
    if not m:
        return ''
    line_start = normalized.rfind('\n', 0, m.start()) + 1
    rest = normalized[line_start:]
    lines = rest.splitlines()
    out = [lines[0]]
    stop_higher = re.compile(rf'^#{{1,{level}}}\s+')
    in_fence = False
    for line in lines[1:]:
        if re.match(r'^\s*`{3,}', line):
            in_fence = not in_fence
        elif (not in_fence) and stop_higher.match(line):
            break
        out.append(line)
    return '\n'.join(out)


def _split_md_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', s)]


def iter_markdown_tables(section_text: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    lines = section_text.replace('\r\n', '\n').splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if re.match(r'^`{3,}', stripped):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        if (
            stripped.startswith('|')
            and i + 1 < len(lines)
            and re.match(r'^\|[\s:-]+(?:\|[\s:-]+)*\|?$', lines[i + 1].strip())
        ):
            headers = _split_md_row(lines[i])
            data_rows: list[list[str]] = []
            j = i + 2
            while j < len(lines):
                row_s = lines[j].strip()
                if not row_s.startswith('|') or re.match(r'^\|[\s:-]+(?:\|[\s:-]+)*\|?$', row_s):
                    break
                data_rows.append(_split_md_row(lines[j]))
                j += 1
            tables.append((headers, data_rows))
            i = j
            continue
        i += 1
    return tables


def _is_placeholder(val: str) -> bool:
    cleaned = val.strip().strip('`*"\' ').strip()
    return bool(PLACEHOLDER_VALUE_RE.match(cleaned))


def check_manifest_metadata(text: str) -> dict:
    """Validate Manifest Status and Approved_* fields when Reviewed/Ready."""
    manifest_sec = extract_section(text, r'^##\s+(?:\d+\.\s*)?Manifest\b', level=2)
    status_val = None
    m_bullet = re.search(r'(?im)^\s*-\s+\*\*Status:\*\*\s*(.+)$', manifest_sec)
    if m_bullet:
        status_val = m_bullet.group(1).strip()
    else:
        for _, rows in iter_markdown_tables(manifest_sec):
            for row in rows:
                if len(row) >= 2 and re.sub(r'[*` ]', '', row[0]).lower() == 'status':
                    status_val = row[1].strip()
                    break
            if status_val is not None:
                break

    has_status = bool(status_val and not _is_placeholder(status_val))
    status_stripped = (status_val or '').strip().strip('`*"\' ')
    is_approved_status = bool(re.match(r'^(?:Reviewed|Ready)\b', status_stripped, re.I))

    fields_found: dict[str, str] = {}
    for field in REQUIRED_APPROVAL_FIELDS:
        fb = re.search(rf'(?im)^\s*-\s+\*\*{re.escape(field)}:\*\*\s*(.+)$', manifest_sec)
        if fb:
            fields_found[field] = fb.group(1).strip()
            continue
        for _, rows in iter_markdown_tables(manifest_sec):
            for row in rows:
                if len(row) >= 2 and re.sub(r'[*` ]', '', row[0]).lower() == field.lower():
                    fields_found[field] = row[1].strip()
                    break
            if field in fields_found:
                break

    missing_or_empty_approval: list[str] = []
    if is_approved_status:
        for field in REQUIRED_APPROVAL_FIELDS:
            val = fields_found.get(field, '')
            if not val or _is_placeholder(val):
                missing_or_empty_approval.append(field)

    approval_ok = has_status and (not missing_or_empty_approval)
    return {
        'has_status': has_status,
        'status_value': status_val,
        'is_approved_status': is_approved_status,
        'missing_approval_fields': missing_or_empty_approval,
        'manifest_approval_ok': approval_ok,
    }


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


def load_owned_ids_by_module(req_path: Path | None = None) -> dict[str, list[str]]:
    path = req_path or (PLANNING / 'trace' / 'requirements.json')
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding='utf-8')).get('records', [])
    by_owner: dict[str, list[str]] = {}
    for rec in records:
        owner = rec.get('owner')
        if owner and re.match(r'^M\d{2}$', owner):
            by_owner.setdefault(owner, []).append(rec['id'])
    return {k: sorted(set(v)) for k, v in by_owner.items()}


def load_required_functions_by_module(
    catalog_path: Path | None = None,
    req_path: Path | None = None,
) -> dict[str, list[str]]:
    """Collect Mxx-Fyy (and W-F01..14 for M16) per module from FUNCTION-CATALOG.md and requirements.json."""
    by_mod: dict[str, set[str]] = {}
    cat = catalog_path or (SPECS / 'FUNCTION-CATALOG.md')
    if cat.exists():
        current_mod: str | None = None
        for line in cat.read_text(encoding='utf-8').splitlines():
            m_head = re.match(r'^##\s+(M\d{2})\b', line)
            if m_head:
                current_mod = m_head.group(1)
                continue
            if current_mod:
                m_row = re.match(r'^\|\s*\*\*(M\d{2}-F\d{2}|W-F\d{2})\*\*', line)
                if m_row:
                    by_mod.setdefault(current_mod, set()).add(m_row.group(1))
    owned = load_owned_ids_by_module(req_path)
    for mod, ids in owned.items():
        for rid in ids:
            if re.match(r'^(?:M\d{2}-F\d{2}|W-F\d{2})$', rid):
                by_mod.setdefault(mod, set()).add(rid)
    return {k: sorted(v) for k, v in by_mod.items()}


def load_registered_gap_ids(gaps_path: Path | None = None) -> set[str]:
    path = gaps_path or (PLANNING / 'GAPS.md')
    if not path.exists():
        return set()
    clean = strip_html_comments(path.read_text(encoding='utf-8'))
    ids: set[str] = set()
    for _, rows in iter_markdown_tables(clean):
        for row in rows:
            if row:
                ids.update(GAP_ID_TOKEN_RE.findall(row[0]))
    return ids


def find_unregistered_open_gaps(text: str, registered_gaps: set[str]) -> list[str]:
    """Ensure every [OPEN-GAP: ...] tag (outside comments/fences) resolves to registered GAPS.md IDs."""
    clean = strip_html_comments(text)
    lines = []
    in_fence = False
    for line in clean.replace('\r\n', '\n').splitlines():
        if re.match(r'^\s*`{3,}', line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    body = '\n'.join(lines)
    # Ignore literal backticked rubric placeholder `[OPEN-GAP]` (no ID),
    # while still validating every concrete `[OPEN-GAP: ...]` tag even inside inline code ticks.
    body_no_inline = re.sub(r'`\[OPEN-GAP\]`', '', body)

    bad: list[str] = []
    for m in re.finditer(r'\[OPEN-GAP(?::([^\]]*))?\]', body_no_inline):
        inner = (m.group(1) or '').strip()
        if not inner:
            bad.append(m.group(0))
            continue
        # Expand any GAP-05..07 or W-O01..04 range inside [OPEN-GAP: ...]
        expanded = re.sub(
            r'(GAP-|W-O|P-O|H-O|O)(\d{2})(?:\.\.|–)(\d{2})',
            lambda rm: ', '.join(
                f'{rm.group(1)}{n:0{len(rm.group(2))}d}'
                for n in range(int(rm.group(2)), int(rm.group(3)) + 1)
            ) if int(rm.group(2)) <= int(rm.group(3)) else rm.group(0),
            inner,
        )
        tokens = GAP_ID_TOKEN_RE.findall(expanded)
        if not tokens:
            bad.append(m.group(0))
            continue
        for tok in tokens:
            if tok not in registered_gaps:
                bad.append(tok)
    return sorted(set(bad))


def missing_owned_ids(mod_id: str, combined_text: str, owned_map: dict[str, list[str]]) -> list[str]:
    ids = owned_map.get(mod_id, [])
    return [
        rid for rid in ids
        if not re.search(rf'(?<![A-Za-z0-9_-]){re.escape(rid)}(?![A-Za-z0-9_-])', combined_text)
    ]


def expand_test_tokens(cell: str) -> tuple[list[str], bool]:
    """Return (expanded_test_ids, has_valid_na_or_gap) from a Requirement trace Test cell or 6.2 Mã Test cell."""
    had_na = bool(re.search(r'\bN/A\b', cell, re.I))
    had_gap = bool(re.search(r'\[OPEN-GAP:', cell))

    work = re.sub(r'\[OPEN-GAP(?::[^\]]*)?\]', ' ', cell)
    work = re.sub(r'\*\([^)]*\)\*', ' ', work)
    work = re.sub(r'\bN/A\b\s*(?:\([^)]*\))?', ' ', work, flags=re.I)
    work = work.replace('`', '')

    # Same-prefix ranges e.g. SL01-T01..SL01-T11
    def _rep_same(m: re.Match) -> str:
        prefix, s_num, e_num = m.group(1), m.group(2), m.group(3)
        start, end = int(s_num), int(e_num)
        if start <= end and (end - start) <= 200:
            width = max(len(s_num), len(e_num))
            return ' '.join(f'{prefix}{n:0{width}d}' for n in range(start, end + 1))
        return m.group(0)

    work = re.sub(r'([A-Z](?:[A-Z0-9-]*[A-Z-])?)(\d+)(?:\.\.|–)\1(\d+)', _rep_same, work)

    # Short-end ranges e.g. W-T01..40, ONFR01..06, M14-AC01..03
    def _rep_short(m: re.Match) -> str:
        prefix, s_num, e_num = m.group(1), m.group(2), m.group(3)
        start, end = int(s_num), int(e_num)
        if start <= end and (end - start) <= 200:
            width = max(len(s_num), len(e_num))
            return ' '.join(f'{prefix}{n:0{width}d}' for n in range(start, end + 1))
        return m.group(0)

    work = re.sub(r'([A-Z](?:[A-Z0-9-]*[A-Z-])?)(\d+)(?:\.\.|–)(\d+)', _rep_short, work)

    # Slash shorthand e.g. W-T01/02/07/29/36 or H-T35/40/41
    def _rep_slash(m: re.Match) -> str:
        prefix, nums = m.group(1), m.group(2)
        return ' '.join(f'{prefix}{n}' for n in nums.split('/'))

    work = re.sub(r'([A-Z](?:[A-Z0-9-]*[A-Z-])?)(\d+(?:/\d+)+)', _rep_slash, work)

    tokens = [
        tok for tok in re.findall(r'\b[A-Z](?:[A-Z0-9-]*[A-Z-])?\d+[A-Z0-9-]*\b', work)
        if not re.match(r'^(?:M\d{2}|ADR-\d+|SL\d{2}|L\d+|P[012]|Q\d+|GAP-[A-Z0-9-]+|W-O\d{2}|P-O\d{2}|H-O\d{2}|O\d{2})$', tok)
    ]
    return tokens, (had_na or had_gap)


def load_known_contract_surface(specs_dir: Path | None = None) -> dict[str, set[str]]:
    """Collect published events, contract port names, and owned tables per contracted module."""
    sdir = specs_dir or SPECS
    known: dict[str, set[str]] = {}
    contract_dir = sdir / 'contracts'
    if contract_dir.exists():
        for cpath in contract_dir.glob('*.md'):
            mod = cpath.name.split('-')[0]
            txt = cpath.read_text(encoding='utf-8')
            syms = set(re.findall(rf'\b{re.escape(mod)}\.([A-Z][A-Za-z0-9_]+)\b', txt))
            for h in re.findall(r'^###\s+2\.\d+.*', txt, re.M):
                for tok in re.findall(r'`([A-Z][A-Za-z0-9_]+)`', h):
                    syms.add(tok)
                    base = re.sub(r'(?:Input|Output|Decision|Result|Note|Ack)$', '', tok)
                    if base:
                        syms.add(base)
            known.setdefault(mod, set()).update(syms)
    module_dir = sdir / 'modules'
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
                    row_match = re.search(rf'\|\s*`{re.escape(key)}[^`]*`\s*[^\n]*\n', plan_txt)
                    if row_match and ('Reviewed' not in row_match.group(0)):
                        issues.append(f'DECOMPOSITION-PLAN.md row for {key} does not report Reviewed')
                if key.startswith('M') and readme_txt:
                    row_match = re.search(rf'\|\s*{re.escape(key)}\s*\|[^\n]+\n', readme_txt)
                    if row_match and ('Reviewed' not in row_match.group(0)):
                        issues.append(f'02-specs/README.md row for {key} does not report Reviewed')

    # INV-27 / W1-01 single-shot erasure checks and cross-doc privacy_erasure_system_role
    # alignment are enforced in wave_guard_issues() (`context_integrity.py`).

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

    c16_path = SPECS / 'contracts' / 'M16-TASK-CORE-COMMANDS.md'
    if c16_path.exists():
        c16_txt = c16_path.read_text(encoding='utf-8')
        if 'rút submission (WithdrawSubmission) hay sửa khi đang duyệt trả 409' in c16_txt:
            issues.append('C16 still has contradictory W-T15 summary stating WithdrawSubmission returns 409 (W1-04)')

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


def _check_function_subsections(
    behavior_sec: str,
    required_funcs: list[str],
) -> tuple[list[str], dict[str, list[str]]]:
    """Verify every required Mxx-Fyy / W-Fzz has a ### 3.x subsection with all 6 substantive sub-parts + provenance."""
    lines = behavior_sec.replace('\r\n', '\n').splitlines()
    blocks: list[tuple[str, str]] = []
    cur_head: str | None = None
    cur_body: list[str] = []
    for line in lines:
        if line.startswith('### '):
            if cur_head is not None:
                blocks.append((cur_head, '\n'.join(cur_body)))
            if re.match(r'^###\s+3\.([1-9]\d*)\b', line):
                cur_head = line
                cur_body = []
            else:
                cur_head = None
                cur_body = []
        elif cur_head is not None:
            cur_body.append(line)
    if cur_head is not None:
        blocks.append((cur_head, '\n'.join(cur_body)))

    missing_funcs: list[str] = []
    incomplete_subparts: dict[str, list[str]] = {}

    def _validate_block(label: str, body: str) -> list[str]:
        issues: list[str] = []
        if not re.search(r'\[(MASTER|PROPOSED|OPEN-GAP(?::[^\]]+)?)\]', body):
            issues.append('missing_provenance_tag')
        b_lines = body.splitlines()
        for key, pat in REQUIRED_BEHAVIOR_SUBPARTS:
            matched_idx = None
            for idx, ln in enumerate(b_lines):
                if re.match(pat, ln):
                    matched_idx = idx
                    break
            if matched_idx is None:
                issues.append(f'missing_{key}')
                continue
            head_line = b_lines[matched_idx]
            after_colon = head_line.split(':', 1)[1].strip() if ':' in head_line else ''
            sub_lines: list[str] = []
            for j in range(matched_idx + 1, len(b_lines)):
                if re.match(r'^-\s+\*\*', b_lines[j]) or b_lines[j].startswith('### '):
                    break
                if b_lines[j].strip():
                    sub_lines.append(b_lines[j].strip())
            combined_val = ' '.join([after_colon] + sub_lines).strip()
            if not combined_val or _is_placeholder(combined_val):
                issues.append(f'empty_{key}')
        return issues

    if required_funcs:
        for fid in required_funcs:
            pat = re.compile(rf'(?<![A-Za-z0-9_-]){re.escape(fid)}(?![A-Za-z0-9_-])')
            match_blk = next(((h, b) for h, b in blocks if pat.search(h)), None)
            if match_blk is None:
                missing_funcs.append(fid)
            else:
                sub_issues = _validate_block(fid, match_blk[1])
                if sub_issues:
                    incomplete_subparts[fid] = sub_issues
    else:
        if not blocks:
            missing_funcs.append('### 3.x')
        for idx, (h, b) in enumerate(blocks, 1):
            sub_issues = _validate_block(f'3.{idx}', b)
            if sub_issues:
                incomplete_subparts[h[:50]] = sub_issues

    return missing_funcs, incomplete_subparts


def _check_42_table_dictionary(data_sec: str) -> dict:
    """Verify every owned entity table row in ### 4.2 declares ADR-004 group and Nhóm C avoids mutable audit cols."""
    sec_42 = extract_section(data_sec, r'^###\s+4\.2\b', level=3)
    if not sec_42:
        return {
            'has_42_section': False,
            'owned_rows_count': 0,
            'missing_group_rows': ['### 4.2 section missing'],
            'forbidden_immutable_columns': [],
        }

    missing_group_rows: list[str] = []
    forbidden_cols: list[str] = []
    owned_rows = 0
    group_re = re.compile(r'Nhóm\s+(?:A|B-Catalog|B-Governance-Sensitive|B-Gov|C)\b')

    for headers, rows in iter_markdown_tables(sec_42):
        h_joined = ' | '.join(headers)
        if 'SSoT' in h_joined and 'Tên bảng độc lập' not in h_joined:
            continue
        if not re.search(r'Tên bảng', h_joined):
            continue

        fields_idx = next(
            (i for i, h in enumerate(headers) if re.search(r'Cột|Trường|Columns|Fields', h, re.I)),
            len(headers) - 2 if len(headers) >= 3 else 0,
        )
        name_idx = next(
            (i for i, h in enumerate(headers) if 'Tên bảng' in h),
            0,
        )
        for row in rows:
            if not row:
                continue
            owned_rows += 1
            row_joined = ' | '.join(row)
            table_label = row[name_idx] if name_idx < len(row) else row[0]
            groups_found = group_re.findall(row_joined)
            if not groups_found:
                missing_group_rows.append(table_label[:60])
                continue
            is_nhom_c = ('Nhóm C' in group_re.findall(table_label)) or (
                'Nhóm C' in groups_found and len(set(groups_found)) == 1
            ) or bool(re.search(r'(?:\*\*|`)Nhóm C\b', row_joined))
            if is_nhom_c:
                fields_text = row[fields_idx] if fields_idx < len(row) else ''
                for col in FORBIDDEN_IMMUTABLE_COLS:
                    if re.search(rf'(?<![A-Za-z0-9_]){col}(?![A-Za-z0-9_])', fields_text):
                        forbidden_cols.append(f'{table_label}: {col}')

    return {
        'has_42_section': True,
        'owned_rows_count': owned_rows,
        'missing_group_rows': missing_group_rows,
        'forbidden_immutable_columns': forbidden_cols,
    }


def check_module_file(
    path: Path,
    baseline_sha: str,
    owned_map: dict[str, list[str]],
    strict_all: bool = False,
    known_surface: dict[str, set[str]] | None = None,
    required_funcs_map: dict[str, list[str]] | None = None,
    registered_gaps: set[str] | None = None,
    root: Path = ROOT,
) -> dict:
    raw_text = path.read_text(encoding='utf-8')
    clean_text = strip_html_comments(raw_text)
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    is_legacy = (path.name in LEGACY_EXEMPT_MODULES) and not strict_all

    missing_sections: list[str] = []
    if not is_legacy:
        for key, pattern in REQUIRED_MODULE_SECTIONS:
            if not re.search(pattern, clean_text, re.M | re.I):
                missing_sections.append(key)

    has_provenance_tags = bool(re.search(r'\[(MASTER|PROPOSED|OPEN-GAP(?::[^\]]+)?)\]', clean_text))
    has_baseline_ref = baseline_sha in clean_text
    manifest_info = check_manifest_metadata(clean_text)

    trace_sec = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?Requirement\s+trace\b', level=2)
    trace_tables = iter_markdown_tables(trace_sec) if trace_sec else []
    trace_data_text_parts: list[str] = []
    trace_9col_ok = len(trace_tables) >= 1
    empty_contract_col_rows: list[str] = []
    invalid_test_trace_cells: list[str] = []
    trace_test_ids: set[str] = set()

    for headers, rows in trace_tables:
        if len(headers) < 9 or not rows:
            trace_9col_ok = False
        contract_idx = next(
            (i for i, h in enumerate(headers) if ('hành vi' in h.lower() and 'contract' in h.lower())),
            None,
        )
        test_idx = next((i for i, h in enumerate(headers) if h.strip().lower() == 'test'), None)
        if contract_idx is None or test_idx is None:
            trace_9col_ok = False
        for row in rows:
            if len(row) != len(headers):
                trace_9col_ok = False
            trace_data_text_parts.append(' | '.join(row))
            row_id = row[0] if row else '?'
            if contract_idx is not None:
                cval = row[contract_idx] if contract_idx < len(row) else ''
                if not cval or _is_placeholder(cval):
                    empty_contract_col_rows.append(row_id[:40])
            if test_idx is not None and test_idx < len(row):
                tval = row[test_idx]
                toks, has_na_or_gap = expand_test_tokens(tval)
                if not toks and not has_na_or_gap:
                    invalid_test_trace_cells.append(f'{row_id}: {tval[:40]}')
                trace_test_ids.update(toks)

    mod_match = re.match(r'^(M\d{2})-', path.name)
    mod_id = mod_match[1] if mod_match else None
    trace_scan_text = '\n'.join(trace_data_text_parts) if not is_legacy else clean_text
    missing_ids = missing_owned_ids(mod_id, trace_scan_text, owned_map) if mod_id else []
    trace_ids_complete = (len(missing_ids) == 0)

    behavior_sec = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?Hành\s+vi\b', level=2)
    req_map = required_funcs_map if required_funcs_map is not None else load_required_functions_by_module()
    req_funcs = req_map.get(mod_id, []) if mod_id else []
    missing_funcs, incomplete_subparts = _check_function_subsections(behavior_sec, req_funcs)
    has_precondition_blocks = bool(re.search(r'^\s*-\s+\*\*Tiền điều kiện', behavior_sec, re.M))

    data_sec = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?Data/API\b', level=2)
    has_base_scope_columns = all(col in clean_text for col in ('branch_id', 'legal_entity_id', 'business_line_id'))
    tdict_info = _check_42_table_dictionary(data_sec) if data_sec else {
        'has_42_section': False,
        'owned_rows_count': 0,
        'missing_group_rows': ['Data/API section missing'],
        'forbidden_immutable_columns': [],
    }

    mig_sec = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?Migration\b', level=2)
    test_matrix_ids: set[str] = set()
    has_10col_test_matrix = False
    test_matrix_rows_valid = False
    for headers, rows in iter_markdown_tables(mig_sec):
        if headers and headers[0].strip().lower() == 'mã test':
            header_joined = ' | '.join(headers)
            has_10col_test_matrix = (
                len(headers) == 10
                and all(req in header_joined for req in ('Severity', 'Fixture', 'Build', 'Actual'))
                and (('Status' in header_joined) or ('Evidence' in header_joined))
            )
            valid_rows = 0
            all_not_run = True
            for row in rows:
                if len(row) != len(headers) or any(not c.strip() for c in row):
                    all_not_run = False
                    continue
                if 'not run' not in ' | '.join(row).lower():
                    all_not_run = False
                toks, _ = expand_test_tokens(row[0])
                test_matrix_ids.update(toks)
                valid_rows += 1
            test_matrix_rows_valid = (valid_rows >= 1) and all_not_run
            break

    missing_test_matrix_ids = sorted(trace_test_ids - test_matrix_ids)
    reg_gaps = registered_gaps if registered_gaps is not None else load_registered_gap_ids()
    unregistered_open_gaps = find_unregistered_open_gaps(clean_text, reg_gaps)
    unknown_cross_refs = find_unknown_cross_module_refs(mod_id, clean_text, known_surface or {})
    inv27_issues = find_inv27_erasure_issues(clean_text, _display_path(path, root))

    passed = (
        fences_ok
        and (not bad_links)
        and no_fake_pass
        and (not missing_sections)
        and (not unregistered_open_gaps)
        and (not inv27_issues)
    )
    if not is_legacy:
        passed = (
            passed
            and has_provenance_tags
            and has_baseline_ref
            and manifest_info['manifest_approval_ok']
            and trace_9col_ok
            and (not empty_contract_col_rows)
            and (not invalid_test_trace_cells)
            and (not missing_test_matrix_ids)
            and has_precondition_blocks
            and (not missing_funcs)
            and (not incomplete_subparts)
            and has_base_scope_columns
            and tdict_info['has_42_section']
            and (tdict_info['owned_rows_count'] >= 1)
            and (not tdict_info['missing_group_rows'])
            and (not tdict_info['forbidden_immutable_columns'])
            and has_10col_test_matrix
            and test_matrix_rows_valid
            and trace_ids_complete
            and (not unknown_cross_refs)
        )

    return {
        'file': _display_path(path, root),
        'mode': 'legacy_or_extension' if is_legacy else 'standard_module_spec',
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_sections': missing_sections,
        'has_provenance_tags': has_provenance_tags,
        'has_baseline_ref': has_baseline_ref,
        'manifest_approval_ok': manifest_info['manifest_approval_ok'],
        'missing_approval_fields': manifest_info['missing_approval_fields'],
        'trace_9col_ok': trace_9col_ok,
        'empty_contract_col_rows': empty_contract_col_rows[:15],
        'invalid_test_trace_cells': invalid_test_trace_cells[:15],
        'missing_test_matrix_ids': missing_test_matrix_ids[:25],
        'missing_function_subsections': missing_funcs,
        'incomplete_function_subparts': incomplete_subparts,
        'has_precondition_blocks': has_precondition_blocks,
        'has_base_scope_columns': has_base_scope_columns,
        'table_42_missing_group_rows': tdict_info['missing_group_rows'],
        'forbidden_immutable_columns': tdict_info['forbidden_immutable_columns'],
        'has_10col_test_matrix': has_10col_test_matrix,
        'test_matrix_rows_valid': test_matrix_rows_valid,
        'trace_ids_complete': trace_ids_complete,
        'missing_ids_count': len(missing_ids),
        'missing_ids_sample': missing_ids[:25],
        'unregistered_open_gaps': unregistered_open_gaps,
        'unknown_cross_module_refs': unknown_cross_refs,
        'inv27_erasure_issues': inv27_issues,
        'passed': passed,
    }


def check_slice_file(
    path: Path,
    baseline_sha: str,
    strict_all: bool = False,
    registered_gaps: set[str] | None = None,
    root: Path = ROOT,
) -> dict:
    raw_text = path.read_text(encoding='utf-8')
    clean_text = strip_html_comments(raw_text)
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    is_legacy = (path.name in LEGACY_EXEMPT_SLICES) and not strict_all

    missing_sections: list[str] = []
    if not is_legacy:
        for key, pattern in REQUIRED_SLICE_SECTIONS:
            if not re.search(pattern, clean_text, re.M | re.I):
                missing_sections.append(key)

    has_baseline_ref = baseline_sha in clean_text
    manifest_info = check_manifest_metadata(clean_text)

    test_sec = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?Test\b', level=2)
    test_tables = iter_markdown_tables(test_sec) if test_sec else []
    has_valid_test_matrix = False
    if test_tables:
        all_rows_ok = True
        row_count = 0
        for headers, rows in test_tables:
            if not rows:
                all_rows_ok = False
                continue
            status_idx = next((i for i, h in enumerate(headers) if 'status' in h.lower() or 'evidence' in h.lower()), None)
            for row in rows:
                row_count += 1
                if len(row) != len(headers) or any(not c.strip() for c in row):
                    all_rows_ok = False
                elif status_idx is not None and 'not run' not in row[status_idx].lower():
                    all_rows_ok = False
        has_valid_test_matrix = (row_count >= 1) and all_rows_ok

    reg_gaps = registered_gaps if registered_gaps is not None else load_registered_gap_ids()
    unregistered_open_gaps = find_unregistered_open_gaps(clean_text, reg_gaps)
    inv27_issues = find_inv27_erasure_issues(clean_text, _display_path(path, root))

    passed = (
        fences_ok
        and (not bad_links)
        and no_fake_pass
        and (not missing_sections)
        and (not unregistered_open_gaps)
        and (not inv27_issues)
    )
    if not is_legacy:
        passed = (
            passed
            and has_baseline_ref
            and manifest_info['manifest_approval_ok']
            and has_valid_test_matrix
        )

    return {
        'file': _display_path(path, root),
        'mode': 'legacy_slice' if is_legacy else 'standard_slice_spec',
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_sections': missing_sections,
        'has_baseline_ref': has_baseline_ref,
        'manifest_approval_ok': manifest_info['manifest_approval_ok'],
        'missing_approval_fields': manifest_info['missing_approval_fields'],
        'has_valid_test_matrix': has_valid_test_matrix,
        'unregistered_open_gaps': unregistered_open_gaps,
        'inv27_erasure_issues': inv27_issues,
        'passed': passed,
    }


def _find_empty_json_nodes(obj, depth: int = 0, allow_empty_list: bool = False, loc: str = 'root') -> list[str]:
    """Check depth 0/1/2 objects & values to forbid empty {} and empty strings."""
    errors: list[str] = []
    if depth > 2:
        return errors
    if isinstance(obj, dict):
        if len(obj) == 0:
            errors.append(f'{loc}: empty JSON object {{}}')
            return errors
        for k, v in obj.items():
            if not str(k).strip():
                errors.append(f'{loc}: empty key')
            child_loc = f'{loc}.{k}'
            if isinstance(v, str) and not v.strip():
                errors.append(f'{child_loc}: empty string value')
            elif isinstance(v, (dict, list)):
                errors.extend(_find_empty_json_nodes(v, depth + 1, allow_empty_list, child_loc))
    elif isinstance(obj, list):
        if len(obj) == 0:
            if depth == 0 or not allow_empty_list:
                errors.append(f'{loc}: empty JSON array []')
        else:
            for idx, item in enumerate(obj[:5]):
                if isinstance(item, (dict, list)):
                    errors.extend(_find_empty_json_nodes(item, depth + 1, allow_empty_list, f'{loc}[{idx}]'))
    return errors


def _collect_all_dict_keys(obj) -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(str(k))
            keys.update(_collect_all_dict_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(_collect_all_dict_keys(item))
    return keys


def _extract_schema_field_names(obj) -> set[str]:
    """Collect concrete declared field names from Input/Output Schema JSON blocks."""
    wrapper_suffixes = ('Input', 'Output', 'Decision', 'Result', 'Ack', 'Note', 'Request', 'Response')
    fields: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and (k.endswith(wrapper_suffixes) or k.lower() in {'input', 'output', 'schema'}):
                for fk, fv in v.items():
                    fields.add(fk)
                    if isinstance(fv, dict):
                        fields.update(fv.keys())
            else:
                fields.add(k)
                if isinstance(v, dict):
                    fields.update(v.keys())
    return fields


def check_contract_file(
    path: Path,
    registered_gaps: set[str] | None = None,
    root: Path = ROOT,
) -> dict:
    raw_text = path.read_text(encoding='utf-8')
    clean_text = strip_html_comments(raw_text)
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)

    # Check ## 1 table has all 12 standard parts with substantive descriptions (no blank/Điền/TBD)
    sec1 = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?', level=2)
    sec1_tables = iter_markdown_tables(sec1) if sec1 else []
    part_values: dict[str, str] = {}
    for _, rows in sec1_tables:
        for row in rows:
            if len(row) >= 2:
                key_cell = row[0]
                val_cell = row[1]
                for part in REQUIRED_CONTRACT_PARTS:
                    if part.lower() in key_cell.lower():
                        part_values[part] = val_cell

    missing_parts: list[str] = []
    empty_contract_parts: list[str] = []
    for part in REQUIRED_CONTRACT_PARTS:
        if part not in part_values:
            if not re.search(re.escape(part), clean_text, re.I):
                missing_parts.append(part)
            else:
                # Part appeared outside a valid 2-col table -> still missing structured row
                empty_contract_parts.append(part)
        elif _is_placeholder(part_values[part]):
            empty_contract_parts.append(part)

    normalized = clean_text.replace('\r\n', '\n')
    lines = normalized.splitlines()

    # Locate section boundaries for ## 2 and ## 3
    sec2_match = re.search(r'^##\s+2\b', normalized, re.M)
    sec3_match = re.search(r'^##\s+3\b', normalized, re.M)
    sec2_start = sec2_match.start() if sec2_match else -1
    sec2_end = sec3_match.start() if sec3_match else len(normalized)

    json_matches = list(re.finditer(r'```json\s*\n(.*?)\n```', normalized, re.S))
    invalid_json_blocks: list[str] = []
    empty_json_nodes: list[str] = []
    declared_schema_fields: set[str] = set()
    port_schema_count = 0
    example_blocks: list[tuple[int, dict | list]] = []

    for idx, jm in enumerate(json_matches):
        block_str = jm.group(1)
        try:
            parsed = json.loads(block_str)
        except json.JSONDecodeError as exc:
            invalid_json_blocks.append(f'block#{idx}: {exc.msg} (line {exc.lineno})')
            continue

        # Grab context heading/lines before this code block
        prefix_lines = [ln.strip() for ln in normalized[:jm.start()].splitlines() if ln.strip()]
        nearby_ctx = ' '.join(prefix_lines[-4:])
        last_h3 = next((ln for ln in reversed(prefix_lines) if ln.startswith('### ')), '')

        top_keys = list(parsed.keys()) if isinstance(parsed, dict) else []
        is_example = bool(re.search(r'\b(Example|Sample|Ví dụ)\b', nearby_ctx, re.I)) or any(
            k.lower().startswith(('example', 'sample')) for k in top_keys
        )
        is_envelope = isinstance(parsed, dict) and {'event_id', 'event_type', 'correlation_id'}.issubset(parsed.keys()) and not is_example

        node_errs = _find_empty_json_nodes(parsed, depth=0, allow_empty_list=is_example, loc=f'block#{idx}')
        empty_json_nodes.extend(node_errs)

        if is_example:
            example_blocks.append((idx, parsed))
        elif (not is_envelope) and sec2_start != -1 and sec2_start <= jm.start() < sec2_end:
            has_port_hint = bool(last_h3 and re.search(r'`?[A-Za-z][A-Za-z0-9_]+`?', last_h3)) or any(
                re.search(r'(Input|Output|Decision|Result|Ack|Request|Response)$', k) or isinstance(v, dict)
                for k, v in (parsed.items() if isinstance(parsed, dict) else [])
            )
            if has_port_hint:
                port_schema_count += 1
                declared_schema_fields.update(_extract_schema_field_names(parsed))

    has_port_schema = (port_schema_count >= 1) and (len(declared_schema_fields) >= 1)

    matching_examples = 0
    for _, ex_obj in example_blocks:
        ex_keys = _collect_all_dict_keys(ex_obj)
        overlap = ex_keys & declared_schema_fields
        min_needed = 2 if len(declared_schema_fields) >= 2 else 1
        if len(overlap) >= min_needed:
            matching_examples += 1
    has_matching_example = (len(example_blocks) >= 1) and (matching_examples >= 1)

    has_published_events = bool(re.search(r'Published\s+Events|Sự\s+kiện\s+Phát\s+hành', clean_text, re.I))
    sec3 = extract_section(clean_text, r'^##\s+(?:\d+\.\s*)?(?:Domain\s+Events|Published|Event)', level=2) or clean_text
    missing_envelope_fields = [f for f in REQUIRED_ENVELOPE_FIELDS if f not in sec3] if has_published_events else []
    has_event_envelope_fields = len(missing_envelope_fields) == 0

    reg_gaps = registered_gaps if registered_gaps is not None else load_registered_gap_ids()
    unregistered_open_gaps = find_unregistered_open_gaps(clean_text, reg_gaps)
    inv27_issues = find_inv27_erasure_issues(clean_text, _display_path(path, root))

    passed = (
        fences_ok
        and (not bad_links)
        and no_fake_pass
        and (not missing_parts)
        and (not empty_contract_parts)
        and (not invalid_json_blocks)
        and (not empty_json_nodes)
        and has_port_schema
        and has_matching_example
        and has_event_envelope_fields
        and (not unregistered_open_gaps)
        and (not inv27_issues)
    )
    return {
        'file': _display_path(path, root),
        'fences_balanced': fences_ok,
        'bad_links': bad_links,
        'no_fake_pass': no_fake_pass,
        'missing_contract_parts': missing_parts,
        'empty_contract_parts': empty_contract_parts,
        'json_schema_count': port_schema_count,
        'example_count': len(example_blocks),
        'matching_example_count': matching_examples,
        'has_port_schema': has_port_schema,
        'has_matching_example': has_matching_example,
        'invalid_json_blocks': invalid_json_blocks,
        'empty_json_nodes': empty_json_nodes,
        'has_event_envelope_fields': has_event_envelope_fields,
        'missing_envelope_fields': missing_envelope_fields,
        'unregistered_open_gaps': unregistered_open_gaps,
        'inv27_erasure_issues': inv27_issues,
        'passed': passed,
    }


def check_basic_doc_file(path: Path, root: Path = ROOT) -> dict:
    fences_ok, bad_links, no_fake_pass = check_markdown_basics(path)
    return {
        'file': _display_path(path, root),
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
        scan_chunks: list[str] = []
        for p in files_by_mod[mod]:
            clean = strip_html_comments(p.read_text(encoding='utf-8'))
            if p.name in LEGACY_EXEMPT_MODULES:
                scan_chunks.append(clean)
            else:
                tsec = extract_section(clean, r'^##\s+(?:\d+\.\s*)?Requirement\s+trace\b', level=2)
                for _, rows in iter_markdown_tables(tsec):
                    for r in rows:
                        scan_chunks.append(' | '.join(r))
        combined = '\n'.join(scan_chunks)
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
    parser.add_argument('--transcript', help='Optional explicit transcript JSONL path of THIS session for token telemetry.')
    args = parser.parse_args()

    baseline_sha = hashlib.sha256(MASTER.read_bytes()).hexdigest()
    owned_map = load_owned_ids_by_module()
    required_funcs_map = load_required_functions_by_module()
    registered_gaps = load_registered_gap_ids()
    known_surface = load_known_contract_surface()
    token_telemetry = check_session_tokens(Path(args.transcript) if args.transcript else None)

    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = (ROOT / target).resolve()
        if not target.exists():
            print(json.dumps({'error': f'File not found: {args.file}'}, ensure_ascii=False, indent=2))
            return 1
        if 'contracts' in target.parts:
            res = check_contract_file(target, registered_gaps=registered_gaps)
        elif 'changes' in target.parts or '.agents' in target.parts or target.name == 'CONTRACTS-REGISTRY.md':
            res = check_basic_doc_file(target)
        elif 'slices' in target.parts:
            res = check_slice_file(target, baseline_sha, strict_all=args.strict_all, registered_gaps=registered_gaps)
        else:
            res = check_module_file(
                target,
                baseline_sha,
                owned_map,
                strict_all=args.strict_all,
                known_surface=known_surface,
                required_funcs_map=required_funcs_map,
                registered_gaps=registered_gaps,
            )
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
        check_module_file(
            p,
            baseline_sha,
            owned_map,
            strict_all=args.strict_all,
            known_surface=known_surface,
            required_funcs_map=required_funcs_map,
            registered_gaps=registered_gaps,
        )
        for p in module_files
    ]
    slice_results = [
        check_slice_file(p, baseline_sha, strict_all=args.strict_all, registered_gaps=registered_gaps)
        for p in slice_files
    ]
    contract_results = [check_contract_file(p, registered_gaps=registered_gaps) for p in contract_files]
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
