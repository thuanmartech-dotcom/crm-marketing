"""Integrity gates for documentation context; no application execution."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def source_hashes(root=ROOT):
    paths = [root / '00-master/CRM_MASTER_BRD_SRS_HOP_NHAT.md',
             root / '01-architecture/INVARIANTS.md',
             root / '05-tools/build_module_context.py', root / '05-tools/context_integrity.py']
    for folder, pattern in [('02-specs/contracts', '*.md'), ('02-specs/modules', '*.md'),
                            ('01-architecture/decisions', 'ADR-*.md')]:
        paths.extend((root / folder).glob(pattern))
    result = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(paths)}
    progress = (root / '03-planning/agent/PROGRESS.md').read_text(encoding='utf-8')
    pending = '\n'.join(line.strip() for line in progress.splitlines()
                        if re.match(r'^[-*]\s+(?:\*\*)?\[PENDING-BACKSYNC\](?:\*\*)?:', line.strip()))
    result['pending_backsync'] = hashlib.sha256(pending.encode()).hexdigest()
    return result


def registry_stamp(root=ROOT):
    return hashlib.sha256(json.dumps(source_hashes(root), sort_keys=True).encode()).hexdigest()


def context_issues(root=ROOT, check_registry=True):
    required = ['AGENTS.md', '03-planning/agent/active-task.json',
                '03-planning/agent/PROGRESS.md', '03-planning/GAPS.md',
                '03-planning/DECOMPOSITION-PLAN.md', '02-specs/README.md',
                '01-architecture/INVARIANTS.md', '01-architecture/INDEX.md',
                '02-specs/CONTRACTS-REGISTRY.md']
    for folder, prefix in [('02-specs/modules', 'M16-'), ('02-specs/modules', 'M19-'),
                           ('02-specs/contracts', 'M16-'), ('02-specs/contracts', 'M19-'),
                           ('01-architecture/decisions', 'ADR-004-'),
                           ('01-architecture/decisions', 'ADR-005-')]:
        matches = list((root / folder).glob(prefix + '*.md'))
        if len(matches) != 1:
            required.append(folder + '/' + prefix + '*.md')
    issues = ['Missing required context: ' + name for name in required if not (root / name).is_file()]
    if issues:
        return issues
    manifest_path = root / '03-planning/agent/active-task.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for key in manifest.get('wave1_specs', {}):
        folder = 'contracts' if key.startswith('C') else ('slices' if key.startswith('SL') else 'modules')
        prefix = 'M' + key[1:] if key.startswith('C') else key
        if not list((root / '02-specs' / folder).glob(prefix + '-*.md')):
            issues.append('Missing reviewed source: ' + key)
    for name in manifest.get('read_first', []):
        if not (manifest_path.parent / name).is_file():
            issues.append('Missing read_first source: ' + name)
    if check_registry:
        registry = (root / '02-specs/CONTRACTS-REGISTRY.md').read_text(encoding='utf-8')
        if f'<!-- source-sha256: {registry_stamp(root)} -->' not in registry:
            issues.append('Registry stale: run --build-registry after source changes')
    return issues


_CLAUSE_SPLIT_RE = re.compile(r'\s*\|\s*|\s+—\s+|;\s+|\.\s+|,\s+')
_SINGLE_SHOT_SCRUB_RE = re.compile(
    r'(?:'
    r'chỉ\s+(?:được\s+)?(?:scrub|redact|xóa\s+PII)\s+(?:1|một)\s+lần'
    r'|scrub\s+(?:PII\s+)?(?:duy\s+nhất\s+)?(?:1|một)\s+lần'
    r'|(?:1|one)[-\s]?time\s+(?:pii\s+)?(?:scrub|redact(?:ion)?|erasure)'
    r'|single[-\s]?shot\s+(?:pii\s+)?(?:scrub|redact(?:ion)?|erasure|lock)'
    r'|khóa\s+(?:(?:scrub|redact|xóa(?:\s+PII)?)\s+)?(?:1|một)\s+lần'
    r'|cơ\s+chế\s+(?:scrub|redact|xóa\s+PII)\s+(?:1|một)\s+lần'
    r'|(?:privacy_erasure_system_role|Task_Submissions|privacy_redacted_at)[^.;|\n]{0,80}?\b(?:1|một)\s+lần'
    r')',
    re.I,
)
_PRIVACY_NULL_GATE_RE = re.compile(r'\bprivacy_redacted_at\s+IS\s+NULL\b', re.I)
_PRE_NEGATION_RE = re.compile(
    r'(?:'
    r'nghiêm\s+cấm|cấm\s+dùng|cấm\s+sử\s+dụng|cấm|tuyệt\s+đối\s+không|không\s+dùng|không\s+sử\s+dụng'
    r'|không\s+áp\s+dụng|không\s+được\s+dùng|không\s+cho\s+phép|không\s+còn'
    r'|bãi\s+bỏ|gỡ\s+bỏ|loại\s+bỏ|bỏ\s+(?:điều\s+kiện|khóa|cờ)|thay\s+(?:thế(?:\s+cho)?|cho)'
    r'|khắc\s+phục|sửa\s+(?:mô\s+tả|lỗi)|trích\s+dẫn\s+lỗi|thiết\s+kế\s+cũ|mô\s+tả\s+cũ|lỗi\s+cũ|bản\s+cũ|trước\s+đây'
    r'|forbid(?:den|s)?|prohibit(?:ed|s)?|must\s+not|do\s+not\s+use|never(?:\s+use)?'
    r'|no\s+longer|remov(?:e|ed)|replac(?:e|ed)|supersed(?:e|ed)|deprecated|legacy'
    r')',
    re.I,
)
_POST_DEPRECATED_RE = re.compile(
    r'(?:'
    r'bị\s+(?:cấm|bãi\s+bỏ|loại\s+bỏ|thay\s+thế)|đã\s+(?:bỏ|bị\s+bỏ|loại\s+bỏ|thay\s+thế)'
    r'|(?:là\s+)?(?:sai|lỗi\s+(?:cũ|thời)|thiết\s+kế\s+cũ)'
    r'|is\s+(?:forbidden|prohibited|deprecated|removed|superseded)|deprecated|legacy'
    r')',
    re.I,
)


def _extract_heading_section(text: str, heading_pattern: str, level: int) -> str:
    """Return body of the first markdown section matching `#*level heading_pattern`."""
    lines = text.replace('\r\n', '\n').splitlines()
    start_re = re.compile(rf'^#{{{level}}}\s+{heading_pattern}')
    stop_re = re.compile(rf'^#{{1,{level}}}\s+')
    capturing = False
    collected: list[str] = []
    for line in lines:
        if not capturing:
            if start_re.match(line):
                capturing = True
                collected.append(line)
        else:
            if stop_re.match(line):
                break
            collected.append(line)
    return '\n'.join(collected)


def find_inv27_erasure_issues(text: str, label: str = '<doc>') -> list[str]:
    """Detect active single-shot PII scrub / privacy_redacted_at IS NULL rules.

    Clause-local negation/replacement exemptions avoid false positives on
    prohibitions or replaced-design notes, while still catching mixed clauses.
    Does not replace human semantic review across all cross-module flows.
    """
    norm_label = label.replace('\\', '/')
    if '/changes/' in f'/{norm_label}' or norm_label.startswith('02-specs/changes/'):
        return []
    clean = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    issues: list[str] = []
    for lineno, line in enumerate(clean.replace('\r\n', '\n').splitlines(), 1):
        for clause in _CLAUSE_SPLIT_RE.split(line):
            for kind, pat in (
                ('single-shot PII scrub phrasing', _SINGLE_SHOT_SCRUB_RE),
                ('privacy_redacted_at IS NULL gate', _PRIVACY_NULL_GATE_RE),
            ):
                for m in pat.finditer(clause):
                    before = clause[max(0, m.start() - 100):m.start()]
                    after = clause[m.end():m.end() + 60]
                    if _PRE_NEGATION_RE.search(before) or _POST_DEPRECATED_RE.search(after):
                        continue
                    issues.append(f'{label}:{lineno}: active doc contains disallowed {kind} (INV-27/ADR-004): {m.group(0).strip()}')
    return issues


def wave_guard_issues(root=ROOT):
    """Check branch-local evidence, not just words appearing anywhere in a file.

    Structural and clause-local regression guard only; human semantic review remains required.
    """
    issues = []
    expected = {
        '1–4': ('http_attempted_at IS NOT NULL', 'UNKNOWN_OUTCOME'),
        '5–6': ('http_attempted_at IS NULL', 'now() >= expires_at', 'EXPIRED_CANCELLED'),
        '7': ('http_attempted_at IS NULL', 'now() < expires_at', 'allow_auto_retry = true', 'RETRY_WAITING', 'PRE_SOCKET_WORKER_CRASH_LIMIT'),
        '8': ('http_attempted_at IS NULL', 'now() < expires_at', 'allow_auto_retry = false', 'QUEUED', 'PRE_SOCKET_WORKER_CRASH_LIMIT'),
    }
    for folder, prefix in [('01-architecture/decisions', 'ADR-005-'),
                           ('02-specs/modules', 'M19-'), ('02-specs/contracts', 'M19-')]:
        for path in (root / folder).glob(prefix + '*.md'):
            text = path.read_text(encoding='utf-8')
            for branch, tokens in expected.items():
                lines = [line for line in text.splitlines() if re.search(r'Nhánh ' + branch + r'\s*\(', line)]
                if len(lines) != 1 or not all(token in lines[0] for token in tokens):
                    issues.append(f'{path.name}: incomplete Reaper branch {branch}')
            for label in ('Micro-commit', 'Pha 3'):
                lines = [line for line in text.splitlines() if label.lower() in line.lower()]
                if not any('lease_token' in line and ('CAS' in line or 'WHERE' in line) for line in lines):
                    issues.append(f'{path.name}: missing local fencing evidence for {label}')
    for folder, pattern in [('02-specs/contracts', 'M16-*.md'),
                            ('02-specs/modules', 'M16-*.md'), ('02-specs/slices', 'SL01-*.md')]:
        for path in (root / folder).glob(pattern):
            rows = [line for line in path.read_text(encoding='utf-8').splitlines()
                    if line.startswith('|') and ('W-T15' in line or 'SL01-T07' in line)]
            if not any(all(token in row for token in ('200', '409', 'IN_PROGRESS')) for row in rows):
                issues.append(f'{path.name}: W-T15 must retain success, withdrawal and conflict cases')

    # INV-27 / ADR-004: Scan active architecture + spec docs (exclude CRs/logs) for single-shot PII scrub gates.
    normative_docs: list[Path] = []
    for rel in ('01-architecture/INVARIANTS.md', '01-architecture/INDEX.md'):
        p = root / rel
        if p.is_file():
            normative_docs.append(p)
    for folder, pattern in [('01-architecture/decisions', 'ADR-*.md'),
                            ('02-specs/modules', '*.md'),
                            ('02-specs/contracts', '*.md'),
                            ('02-specs/slices', '*.md')]:
        d = root / folder
        if d.is_dir():
            normative_docs.extend(sorted(d.glob(pattern)))
    for p in normative_docs:
        issues.extend(find_inv27_erasure_issues(p.read_text(encoding='utf-8'), p.relative_to(root).as_posix()))

    # INV-27 / ADR-004: Validate section-scoped privacy_erasure_system_role alignment.
    erasure_section_specs = [
        ('01-architecture/decisions/ADR-004-SHARED-PLATFORM-TABLES-AND-BASE-SCHEMA.md', r'Đề nghị\b', 2, True),
        ('01-architecture/decisions/ADR-005-DUAL-OUTBOX-3LANE-ISOLATION-AND-VAULT.md', r'Đề nghị\b', 2, False),
        ('02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md', r'3\.14\b', 3, True),
        ('02-specs/modules/M16-WORK-PROJECTS-TASK-CORE.md', r'4\.2\b', 3, True),
        ('02-specs/contracts/M16-TASK-CORE-COMMANDS.md', r'1\.\s', 2, True),
        ('02-specs/contracts/M16-TASK-CORE-COMMANDS.md', r'3\.\s', 2, True),
        ('02-specs/modules/M20-PRIVACY-CONSENT-RETENTION.md', r'3\.6\b', 3, True),
        ('02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md', r'6\.1\b', 3, True),
    ]
    for rel_path, heading_pat, lvl, require_orig_hash in erasure_section_specs:
        fpath = root / rel_path
        if not fpath.is_file():
            continue
        sec_text = _extract_heading_section(fpath.read_text(encoding='utf-8'), heading_pat, lvl)
        role_lines = [ln for ln in sec_text.splitlines() if 'privacy_erasure_system_role' in ln]
        if not role_lines:
            issues.append(f'{fpath.name} ({heading_pat}): missing privacy_erasure_system_role specification (INV-27/ADR-004)')
            continue
        combined = '\n'.join(role_lines)
        for req_tok in ('redacted_deletion_ledger_ids', 'redacted_content_sha256', 'deletion_ledger_id'):
            if req_tok not in combined:
                issues.append(f'{fpath.name} ({heading_pat}): privacy_erasure_system_role missing {req_tok} (INV-27/ADR-004)')
        if 'legal_hold' not in combined.lower() and 'active_legal_hold_ids' not in combined and 'ngoài hold' not in combined.lower():
            issues.append(f'{fpath.name} ({heading_pat}): privacy_erasure_system_role missing Legal_Hold gate (INV-27/ADR-004)')
        if require_orig_hash and not re.search(r'(?<![A-Za-z0-9_])content_sha256(?![A-Za-z0-9_])', combined):
            issues.append(f'{fpath.name} ({heading_pat}): privacy_erasure_system_role missing immutable original content_sha256 preservation (INV-27/ADR-004)')
        if fpath.name.startswith('M23-'):
            if 'NOBYPASSRLS' not in combined or 'NOSUPERUSER' not in combined:
                issues.append(f'{fpath.name} ({heading_pat}): privacy_erasure_system_role missing NOBYPASSRLS/NOSUPERUSER isolation (ADR-005)')
            if 'Nhóm C' not in combined or 'Audit_Logs' not in combined:
                issues.append(f'{fpath.name} ({heading_pat}): privacy_erasure_system_role must explicitly exclude Nhóm C / Audit_Logs (ADR-004)')
    return issues


def write_receipt(packet_path, root=ROOT):
    paths = set()
    for folder in ['00-master', '01-architecture', '02-specs', '03-planning/agent',
                   '03-planning/trace', '05-tools', '.agents/skills/crm-ba-spec']:
        paths.update(p for p in (root / folder).rglob('*') if p.suffix in {'.md', '.json', '.py'})
    paths.update([root / 'AGENTS.md', root / '03-planning/GAPS.md', root / '03-planning/DECOMPOSITION-PLAN.md'])
    receipt = {'kind': 'generated-context-not-proof-of-reading',
               'packet_sha256': hashlib.sha256(packet_path.read_bytes()).hexdigest(),
               'sources': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(paths)}}
    packet_path.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


def verify_receipt(packet_path, root=ROOT):
    receipt = json.loads(packet_path.with_suffix('.receipt.json').read_text(encoding='utf-8'))
    issues = context_issues(root)
    if receipt['packet_sha256'] != hashlib.sha256(packet_path.read_bytes()).hexdigest():
        issues.append('Context packet changed')
    for name, digest in receipt['sources'].items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            issues.append('Context source changed: ' + name)
    return issues
