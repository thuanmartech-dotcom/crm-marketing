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


def wave_guard_issues(root=ROOT):
    """Check branch-local evidence, not just words appearing anywhere in a file.

    Structural regression guard only; human semantic review remains required.
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
