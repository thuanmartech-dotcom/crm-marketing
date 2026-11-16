"""Deterministic context-packet builder, cross-module registry generator,
and session token telemetry helper for CRM BA specs (Documentation-Only).
"""
from __future__ import annotations

import argparse
from context_integrity import context_issues, registry_stamp, write_receipt, verify_receipt
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / '00-master' / 'CRM_MASTER_BRD_SRS_HOP_NHAT.md'
ARCH_DECISIONS = ROOT / '01-architecture' / 'decisions'
SPECS = ROOT / '02-specs'
PLANNING = ROOT / '03-planning'
TRACE = PLANNING / 'trace'

YELLOW_THRESHOLD = 170_000
RED_THRESHOLD = 210_000
BRAIN_DIR = Path.home() / '.gemini' / 'antigravity' / 'brain'

# Extra domain keywords per module so 4-layer extraction catches unowned entities & rules.
MODULE_KEYWORDS: dict[str, list[str]] = {
    'M01': ['contact', 'account', 'contact_point', 'merge', 'identity', 'rfm', 'hồ sơ', 'định danh'],
    'M02': ['lead', 'deal', 'pipeline', 'qualif', 'convert', 'handover', 'today', 'activity', 'activities'],
    'M03': ['conversation', 'message', 'inbox', 'triage', 'thread', 'hội thoại'],
    'M04': ['journey', 'nhắc việc', 'chăm sóc tự động', 'cadence'],
    'M05': ['referral', 'loyalty', 'reward', 'điểm thưởng', 'giới thiệu'],
    'M06': ['ai ', 'copilot', 'co-pilot', 'draft', 'rag', 'provenance', 'prompt'],
    'M07': ['quote', 'catalog', 'báo giá', 'bảng giá', 'sow'],
    'M08': ['contract', 'hợp đồng', 'onboarding', 'renewal', 'amendment', 'start_auth'],
    'M09': ['receipt', 'payment', 'allocation', 'refund', 'invoice', 'thu tiền', 'đối soát', 'bank_account'],
    'M10': ['commission', 'payout', 'hoa hồng', 'chi trả', 'pool'],
    'M11': ['ticket', 'sla', 'entitlement', 'khiếu nại'],
    'M12': ['voc', 'feedback', 'survey', 'csat', 'nps', 'phục hồi cx'],
    'M13': ['appointment', 'booking', 'resource_booking', 'lịch hẹn'],
    'M14': ['principal', 'membership', 'role', 'grant', 'delegation', 'offboard', 'tenant', 'branch', 'legal_entity'],
    'M15': ['brief', 'imc', 'campaign', 'launch', 'media_plan'],
    'M16': ['task', 'project', 'deliverable', 'submission', 'review', 'acceptance', 'work_queue', 'time_entr'],
    'M17': ['budget', 'media funding', 'ngân sách', 'chi phí'],
    'M18': ['kpi', 'metric', 'bi ', 'p&l', 'attribution', 'report', 'forecast'],
    'M19': ['webhook', 'ingest', 'outbox', 'connection', 'adapter', 'replay', 'backfill'],
    'M20': ['consent', 'suppression', 'privacy', 'retention', 'erasure', 'legal_hold', 'deletion_ledger'],
    'M21': ['partner', 'pancake', 'đối tác', 'dataset'],
    'M22': ['employee', 'employment', 'leave', 'attendance', 'payroll', 'nhân sự', 'chấm công', 'lương'],
    'M23': ['policy', 'audit_log', 'approval_request', 'break_glass', 'asset', 'system_calendar', 'internal_outbox'],
    'M24': ['command_palette', 'split_view', 'bulk_command', 'quick_repl', 'notification', 'permission_cache', 'queue'],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def load_json(path: Path) -> dict | list:
    return json.loads(read_text(path))


def sanitize_cell(text: str, max_len: int = 180) -> str:
    """Keep table cells single-line, compact, and compliant with verify_module_spec."""
    # Preserve escaped pipes inside markdown cells as `/` before collapsing whitespace.
    cleaned = text.replace('\\|', '/').replace('|', '/')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'\b(pass|passed|verified)\b', lambda m: f'[{m.group(0)}]', cleaned, flags=re.I)
    if len(cleaned) > max_len:
        cut = cleaned[: max_len - 3].rstrip()
        # Avoid dangling unclosed backtick when truncating.
        if cut.count('`') % 2 == 1:
            cut += '`'
        return cut + '...'
    return cleaned


def extract_contract_summary(path: Path) -> dict:
    """Extract contract ID, version, ports/JSON fields, published/subscribed events."""
    text = read_text(path).replace('\r\n', '\n')
    lines = text.splitlines()
    title = lines[0].lstrip('# ').strip() if lines else path.stem
    ver_match = re.search(r'(?:schema_version|contract_version|Phiên bản)\s*[:=`"\s]+([0-9]+\.[0-9]+[^\s`",)]*)', text)
    version = ver_match.group(1) if ver_match else '1.0'

    # Extract Section 2 ports & JSON schema fields.
    sec2_match = re.search(r'^## 2\..*?(?=^## 3\.|\Z)', text, re.M | re.S)
    ports: list[dict] = []
    if sec2_match:
        sec2 = sec2_match.group(0)
        chunks = re.split(r'(?=^### 2\.\d+)', sec2, flags=re.M)
        for chunk in chunks:
            if not chunk.startswith('### 2.'):
                continue
            header_line = chunk.splitlines()[0]
            port_names = re.findall(r'`([A-Za-z0-9_.-]+)`', header_line)
            if not port_names:
                port_names = [re.sub(r'^###\s*2\.\d+\.?\s*', '', header_line).strip()]
            json_blocks = re.findall(r'```json\s*\n(.*?)\n```', chunk, re.S)
            key_fields: list[str] = []
            for blk in json_blocks[:2]:
                try:
                    data = json.loads(blk)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict):
                    props = data.get('properties') if isinstance(data.get('properties'), dict) else data
                    if isinstance(props, dict):
                        for k in props.keys():
                            if k not in key_fields and k not in ('$schema', 'type', 'title', 'required', 'additionalProperties'):
                                key_fields.append(k)
            ports.append({
                'heading': ' / '.join(port_names[:3]),
                'fields': key_fields[:10],
            })

    # Extract Section 3.2 Published Events & 3.3 Subscribed Events.
    pub_events: list[dict] = []
    sub_events: list[dict] = []
    sec32 = re.search(r'^### 3\.2\..*?(?=^### 3\.3\.|^## 4\.|\Z)', text, re.M | re.S)
    if sec32:
        for row in _parse_markdown_table_rows(sec32.group(0)):
            if len(row) >= 3:
                pub_events.append({
                    'event': row[0],
                    'payload': row[1],
                    'consumers': row[2],
                })
    sec33 = re.search(r'^### 3\.3\..*?(?=^## 4\.|\Z)', text, re.M | re.S)
    if sec33:
        for row in _parse_markdown_table_rows(sec33.group(0)):
            if len(row) >= 2:
                sub_events.append({'source_event': row[0], 'handling': row[1]})

    return {
        'file': path.name,
        'title': title,
        'version': version,
        'ports': ports,
        'published_events': pub_events,
        'subscribed_events': sub_events,
    }


def _parse_markdown_table_rows(section_text: str) -> list[list[str]]:
    """Return data rows (skipping header and separator) splitting only on unescaped pipes."""
    rows: list[list[str]] = []
    seen_header = False
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            seen_header = False
            continue
        if re.match(r'^\|[\s:-]+(?:\|[\s:-]+)*\|?$', stripped):
            seen_header = True
            continue
        if not seen_header:
            continue
        inner = stripped.strip('|')
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', inner)]
        rows.append(cells)
    return rows


def extract_module_entities(path: Path) -> list[dict]:
    """Extract owned tables, inheritance group, and frozen enums from Section 4.2."""
    text = read_text(path).replace('\r\n', '\n')
    mod_match = re.match(r'^(M\d{2})-', path.name)
    mod_id = mod_match.group(1) if mod_match else path.stem
    sec42 = re.search(r'^### 4\.2\..*?(?=^### 4\.3\.|^## 5\.|\Z)', text, re.M | re.S)
    if not sec42:
        return []

    # Stop before Section B referenced/external tables so we only capture owned entities.
    body = sec42.group(0)
    stop_match = re.search(r'^(?:####\s*B\.|>\s*\*\*Các Thực thể Tham chiếu)', body, re.M | re.I)
    if stop_match:
        body = body[: stop_match.start()]

    entities: list[dict] = []
    for cells in _parse_markdown_table_rows(body):
        if len(cells) < 4:
            continue
        # Handle both `| Table | ...` and `| # | Table | ...`
        idx = 1 if cells[0].isdigit() and len(cells) >= 5 else 0
        table_cell = cells[idx]
        trace_cell = cells[idx + 1] if idx + 1 < len(cells) else ''
        cols_cell = cells[idx + 2] if idx + 2 < len(cells) else ''
        rules_cell = cells[idx + 3] if idx + 3 < len(cells) else ''
        group_cell = cells[idx + 4] if idx + 4 < len(cells) else ''

        table_name_m = re.search(r'`([A-Za-z0-9_]+)`', table_cell)
        table_name = table_name_m.group(1) if table_name_m else sanitize_cell(table_cell, 50)
        combined = f'{table_cell} {group_cell} {rules_cell}'
        grp_m = re.search(r'Nhóm\s+(A|B-Governance-Sensitive|B-Catalog|B|C)', combined)
        group = f'Nhóm {grp_m.group(1)}' if grp_m else 'Theo Master 5.1'

        # Capture enum literals like (`VAL1 | VAL2 | VAL3`)
        enum_matches = re.findall(r'\(`([A-Z0-9_]+(?:\s*\\?\|\s*[A-Z0-9_]+)+)`\)', f'{cols_cell} {rules_cell}')
        enums_compact = '; '.join(sanitize_cell(e.replace('\\|', '|'), 70) for e in enum_matches[:3])
        entity_ids = sorted(set(re.findall(r'ENTITY-L\d+', f'{trace_cell} {rules_cell}')))
        entities.append({
            'module': mod_id,
            'table': table_name,
            'group': group,
            'entity_ids': ', '.join(entity_ids),
            'enums': enums_compact,
            'notes': sanitize_cell(rules_cell, 165),
        })
    return entities


def extract_adr_summaries() -> list[dict]:
    """Extract all top-level decision clauses from ADR-001..NNN without truncating later items."""
    summaries: list[dict] = []
    for path in sorted(ARCH_DECISIONS.glob('ADR-*.md')):
        text = read_text(path).replace('\r\n', '\n')
        lines = text.splitlines()
        title = lines[0].lstrip('# ').strip() if lines else path.stem
        dec_match = re.search(r'^## Đề nghị.*?(?=^## So sánh|^## Hệ quả|\Z)', text, re.M | re.S)
        bullets: list[str] = []
        if dec_match:
            for raw in dec_match.group(0).splitlines():
                # Only match top-level numbered clauses or ### headings so sub-bullets don't crowd out clauses 2..5.
                if re.match(r'^(?:\d+\.\s+|###\s+\d+\.)', raw):
                    cleaned = re.sub(r'^(?:\d+\.|###\s*\d+\.?)\s*', '', raw.strip())
                    bullets.append(sanitize_cell(cleaned, 115))
                if len(bullets) >= 6:
                    break
            if not bullets:
                for raw in dec_match.group(0).splitlines():
                    s = raw.strip()
                    if re.match(r'^-\s+', s):
                        bullets.append(sanitize_cell(s.lstrip('- '), 115))
                    if len(bullets) >= 5:
                        break
            if not bullets:
                paras = [
                    sanitize_cell(raw.strip(), 160)
                    for raw in dec_match.group(0).splitlines()[1:]
                    if raw.strip() and not raw.strip().startswith('#')
                ]
                bullets.extend(paras[:3])
        summaries.append({
            'file': path.name,
            'title': sanitize_cell(title, 110),
            'rules': bullets,
        })
    return summaries


def extract_extended_invariants() -> list[dict]:
    """Extract INV-22+ architectural & distributed-system guardrails from 01-architecture/INVARIANTS.md."""
    inv_path = ROOT / '01-architecture' / 'INVARIANTS.md'
    if not inv_path.exists():
        return []
    rows: list[dict] = []
    for raw in read_text(inv_path).splitlines():
        stripped = raw.strip()
        if not stripped.startswith('| INV-'):
            continue
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', stripped.strip('|'))]
        if len(cells) >= 3:
            num_m = re.match(r'INV-(\d+)', cells[0])
            if num_m and int(num_m.group(1)) >= 22:
                rows.append({
                    'id': cells[0],
                    'rule': sanitize_cell(cells[1], len(cells[1]) + 1),
                    'verify': sanitize_cell(cells[2], len(cells[2]) + 1),
                })
    return rows


def extract_pending_backsync() -> list[str]:
    """Collect active bullet items starting with [PENDING-BACKSYNC]: from PROGRESS.md."""
    progress_path = PLANNING / 'agent' / 'PROGRESS.md'
    if not progress_path.exists():
        return []
    lines = []
    for raw in read_text(progress_path).splitlines():
        stripped = raw.strip()
        if re.match(r'^[-*]\s+(?:\*\*)?\[PENDING-BACKSYNC\](?:\*\*)?:', stripped):
            # Strip relative links resolved from PROGRESS.md so CONTRACTS-REGISTRY.md keeps clean links.
            text_only = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'`\1`', stripped.lstrip('-* ').strip())
            lines.append(sanitize_cell(text_only, len(text_only) + 1))
    return lines


def build_contracts_registry() -> Path:
    """Generate 02-specs/CONTRACTS-REGISTRY.md from contracts, modules, and ADRs."""
    contract_files = sorted((SPECS / 'contracts').glob('*.md'))
    module_files = sorted((SPECS / 'modules').glob('*.md'))
    contracts = [extract_contract_summary(p) for p in contract_files]
    adrs = extract_adr_summaries()
    pending = extract_pending_backsync()

    out: list[str] = [
        '# Sổ Tra cứu Bề mặt Hợp đồng & Thực thể Toàn Hệ thống (`CONTRACTS-REGISTRY`)',
        '',
        '> **Tệp tự sinh bởi [build_module_context.py](../05-tools/build_module_context.py) — không sửa tay trực tiếp.**  ',
        f'> **Mục đích:** Chỉ mục tóm tắt Command, Event, Bảng SSoT, Enum và ADR; kích thước thay đổi theo nguồn. Các ô có `...` phải đọc tiếp tại file nguồn; không thay thế contract/ADR đầy đủ cho các phiên Wave 2–6 mà không cần đọc lại toàn văn `~944 KB` file `modules/` cũ. Khi cần sửa ngược (*Backward Drift*), cập nhật additive vào `contracts/*.md`, ghi `[PENDING-BACKSYNC]` vào [PROGRESS.md](../03-planning/agent/PROGRESS.md) và chạy lại `--build-registry`.',
        '',
        '---',
        '',
        '## 1. Danh mục Public Contracts & Ports (`02-specs/contracts/`)',
        '',
        '| Contract | Phiên bản | Ports / Schemas Chính | Trường Trọng yếu (`Top Properties`) |',
        '|---|---|---|---|',
    ]

    for c in contracts:
        link = f'[{c["file"].replace(".md", "")}](contracts/{c["file"]})'
        if not c['ports']:
            out.append(f'| {link} | `{c["version"]}` | *(xem file)* | — |')
            continue
        for idx, p in enumerate(c['ports']):
            c_col = link if idx == 0 else '↳'
            v_col = f'`{c["version"]}`' if idx == 0 else ''
            fields_str = ', '.join(f'`{f}`' for f in p['fields']) if p['fields'] else '—'
            out.append(f'| {c_col} | {v_col} | {sanitize_cell(p["heading"], 90)} | {sanitize_cell(fields_str, 130)} |')

    out.extend([
        '',
        '---',
        '',
        '## 2. Ma trận Domain Events (Published & Subscribed)',
        '',
        '| Producer | Event Name | Payload Trọng yếu | Consumers Bắt buộc |',
        '|---|---|---|---|',
    ])
    for c in contracts:
        mod = c['file'].split('-')[0]
        for ev in c['published_events']:
            out.append(
                f'| `{mod}` | {sanitize_cell(ev["event"], 75)} | '
                f'{sanitize_cell(ev["payload"], 115)} | {sanitize_cell(ev["consumers"], 90)} |'
            )

    out.extend([
        '',
        '### Subscribed Events theo từng Contract',
        '',
        '| Consumer Contract | Nguồn & Event Tiêu thụ | Hành vi Bắt buộc |',
        '|---|---|---|',
    ])
    for c in contracts:
        mod = c['file'].split('-')[0]
        for ev in c['subscribed_events']:
            out.append(
                f'| `{mod}` | {sanitize_cell(ev["source_event"], 95)} | {sanitize_cell(ev["handling"], 125)} |'
            )

    out.extend([
        '',
        '---',
        '',
        '## 3. Từ điển Bảng SSoT & Enum Khóa Cứng (`02-specs/modules/` Đã Khóa)',
        '',
        '| Module SSoT | Bảng Logic | Nhóm Kế thừa | Mã `ENTITY` | Enum / Giá trị Khóa & Bất biến |',
        '|---|---|---|---|---|',
    ])
    for mp in module_files:
        entities = extract_module_entities(mp)
        if not entities:
            continue
        mod_link = f'[{mp.name.split("-")[0]}](modules/{mp.name})'
        for idx, e in enumerate(entities):
            m_col = mod_link if idx == 0 else f'`{e["module"]}`'
            ent_col = f'`{e["entity_ids"]}`' if e['entity_ids'] else '—'
            detail = f'Enums: {e["enums"]}. {e["notes"]}' if e['enums'] else e['notes']
            out.append(
                f'| {m_col} | `{e["table"]}` | `{e["group"]}` | {ent_col} | {sanitize_cell(detail, 190)} |'
            )

    out.extend([
        '',
        '---',
        '',
        '## 4. Tóm tắt Quy tắc Bắt buộc từ `ADR-001..NNN`',
        '',
        '| ADR | Tiêu đề | Quy tắc Kiến trúc Bắt buộc |',
        '|---|---|---|',
    ])
    for a in adrs:
        adr_id = a['file'].split('-')[0] + '-' + a['file'].split('-')[1]
        link = f'[{adr_id}](../01-architecture/decisions/{a["file"]})'
        rules_str = ' ; '.join(a['rules']) if a['rules'] else '*(đọc trực tiếp ADR)*'
        out.append(f'| {link} | {sanitize_cell(a["title"], 80)} | {sanitize_cell(rules_str, 420)} |')

    ext_invariants = extract_extended_invariants()
    out.extend([
        '',
        '### 4b. Bất biến Mở rộng & Mẫu Phân tán Bắt buộc Kế thừa (`INV-22..28`)',
        '',
        '| ID | Quy chuẩn Kiến trúc / Phân tán Bắt buộc | Cách kiểm chứng |',
        '|---|---|---|',
    ])
    for inv in ext_invariants:
        out.append(f'| `{inv["id"]}` | {inv["rule"]} | {inv["verify"]} |')

    out.extend([
        '',
        '---',
        '',
        '## 5. Hàng đợi Đồng bộ Ngược (`[PENDING-BACKSYNC]`)',
        '',
    ])
    if pending:
        for item in pending:
            out.append(f'- {item}')
    else:
        out.append('- Không có mục `[PENDING-BACKSYNC]` đang chờ xử lý.')

    target = SPECS / 'CONTRACTS-REGISTRY.md'
    out.insert(2, f'<!-- source-sha256: {registry_stamp()} -->')
    target.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return target


def _module_keywords(mod_id: str, mod_entry: dict) -> list[str]:
    kws = list(MODULE_KEYWORDS.get(mod_id, []))
    owned_src = mod_entry.get('owned_data_source') or ''
    for part in re.split(r'[/,;()]+', owned_src):
        tok = part.strip().lower()
        if len(tok) >= 3 and tok not in kws:
            kws.append(tok)
    return kws


def _find_master_sections(mod_id: str, mod_entry: dict, catalog_text: str) -> list[dict]:
    """Identify Master v1.9 headings relevant to mod_id via source-sections.json."""
    sections = load_json(TRACE / 'source-sections.json')
    # Check Master section ref in FUNCTION-CATALOG.md, e.g. `Nguồn Master: Mục 3.1`
    cat_block = _extract_catalog_block(mod_id, catalog_text)
    sec_refs = set(re.findall(r'Mục\s+`?(\d+(?:\.\d+)*)`?', cat_block))
    matched: list[dict] = []
    kws = _module_keywords(mod_id, mod_entry)
    for idx, sec in enumerate(sections):
        heading = sec.get('heading', '')
        line_start = sec['line']
        line_end = sections[idx + 1]['line'] - 1 if idx + 1 < len(sections) else line_start + 120
        hit_ref = any(heading.startswith(ref + ' ') or heading.startswith(ref + '.') or heading == ref for ref in sec_refs)
        hit_kw = (mod_id in heading) or (sec.get('level', 0) >= 3 and any(k in heading.lower() for k in kws[:6]))
        if hit_ref or hit_kw:
            matched.append({'heading': heading, 'start': line_start, 'end': line_end})
    return matched


def _extract_catalog_block(mod_id: str, catalog_text: str) -> str:
    anchor = f'<a id="{mod_id.lower()}"></a>'
    if anchor in catalog_text:
        part = catalog_text.split(anchor, 1)[1]
        return part.split('\n---', 1)[0].strip()
    m = re.search(rf'^##\s+{re.escape(mod_id)}\b.*?(?=^##\s+M\d{{2}}|\Z)', catalog_text, re.M | re.S)
    return m.group(0).strip() if m else ''


def _pick_primary_occurrence(rec: dict) -> str:
    occs = rec.get('occurrences') or []
    def_lines = set(rec.get('definition_lines') or [])
    for occ in occs:
        if occ.get('line') in def_lines or occ.get('classification') == 'definition_candidate':
            return occ.get('text', '')
    return occs[-1].get('text', '') if occs else ''


def _text_matches(text: str, mod_id: str, kws: list[str]) -> bool:
    if re.search(rf'(?<![A-Za-z0-9_-]){re.escape(mod_id)}(?![A-Za-z0-9_-])', text):
        return True
    low = text.lower()
    return any(k in low for k in kws)


def build_module_context_packet(mod_id: str, out_path: Path | None = None) -> str:
    """Build 4-layer, 2-way context packet for mod_id from traces, Master, and Contracts."""
    mod_id = mod_id.upper()
    if mod_id not in MODULE_KEYWORDS:
        raise ValueError(f'Unsupported module: {mod_id}')
    issues = context_issues()
    if issues:
        raise ValueError('; '.join(issues))
    modules = load_json(TRACE / 'modules.json')
    mod_entry = next((m for m in modules if m['id'] == mod_id), {})
    req_data = load_json(TRACE / 'requirements.json')['records']
    ec_data = load_json(TRACE / 'entities-contracts.json')
    ur_data = load_json(TRACE / 'unnumbered-rules.json')['candidates']
    catalog_text = read_text(SPECS / 'FUNCTION-CATALOG.md')
    gaps_text = read_text(PLANNING / 'GAPS.md')

    kws = _module_keywords(mod_id, mod_entry)
    cat_block = _extract_catalog_block(mod_id, catalog_text)
    master_secs = _find_master_sections(mod_id, mod_entry, catalog_text)
    master_ranges = [(s['start'], s['end']) for s in master_secs]

    def in_master_range(line_no: int) -> bool:
        return any(s <= line_no <= e for s, e in master_ranges)

    # Layer 1: Owned IDs
    owned_recs = [r for r in req_data if r.get('owner') == mod_id]

    # Layer 2: Upstream contracts & ADRs
    upstream_mods: set[str] = set()
    for token in re.findall(r'M\d{2}', (mod_entry.get('dependencies_source') or '') + ' ' + cat_block):
        if token != mod_id:
            upstream_mods.add(token)
    # Core cross-cutting contracts always relevant when upstream mentions M14/M19/M20 or core ops
    core_contracts = sorted((SPECS / 'contracts').glob('*.md'))
    upstream_contracts = [c for c in core_contracts if c.name.split('-')[0] in upstream_mods | {'M14', 'M20', 'M23'}]
    upstream_contracts = sorted(set(upstream_contracts))

    # Layer 3: Multi-source unowned IDs, entities, contracts, unnumbered rules, GAPS
    matched_entities = [
        e for e in ec_data.get('entities', [])
        if in_master_range(e.get('source_line', -1)) or _text_matches(f"{e.get('section', '')} {e.get('text', '')}", mod_id, kws)
    ]
    matched_master_contracts = [
        c for c in ec_data.get('contracts', [])
        if in_master_range(c.get('source_line', -1)) or _text_matches(f"{c.get('section', '')} {c.get('text', '')}", mod_id, kws)
    ]
    unowned_reqs = [
        r for r in req_data
        if not r.get('owner') and (
            any(in_master_range(ln) for ln in (r.get('definition_lines') or r.get('source', {}).get('lines', [])))
            or _text_matches(_pick_primary_occurrence(r), mod_id, kws)
        )
    ]
    matched_unnumbered = [
        u for u in ur_data
        if in_master_range(u.get('source_line', -1)) or _text_matches(f"{u.get('section', '')} {u.get('text', '')}", mod_id, kws)
    ]
    matched_gaps = [
        line.strip() for line in gaps_text.splitlines()
        if line.strip().startswith('| GAP-') and _text_matches(line, mod_id, kws)
    ]

    # Layer 4: Downstream & sibling cross-module links (who depends on mod_id)
    downstream_modules = [
        m for m in modules
        if m['id'] != mod_id and mod_id in (m.get('dependencies_source') or '')
    ]
    catalog_cross_refs: list[str] = []
    current_heading = ''
    for line in catalog_text.splitlines():
        if line.startswith('## M'):
            current_heading = line.lstrip('# ').strip()
        elif line.startswith('| **') and not current_heading.startswith(mod_id):
            cols = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip('|'))]
            if len(cols) >= 3 and re.search(rf'(?<![A-Za-z0-9_-]){re.escape(mod_id)}(?![A-Za-z0-9_-])', cols[2]):
                catalog_cross_refs.append(f'- {cols[0]} ({current_heading.split("—")[0].strip()}): liên quan {cols[2]}')

    contract_cross_refs: list[str] = []
    for c in core_contracts:
        for line in read_text(c).splitlines():
            if line.startswith('|') and re.search(rf'(?<![A-Za-z0-9_-]){re.escape(mod_id)}(?![A-Za-z0-9_-])', line):
                contract_cross_refs.append(f'- `{c.name}`: {sanitize_cell(line, 170)}')

    # Build Master read ranges from source sections + owned occurrences
    occ_lines = sorted({ln for r in owned_recs for ln in r.get('source', {}).get('lines', [])})
    active_task_path = PLANNING / 'agent' / 'active-task.json'
    active_task = load_json(active_task_path) if active_task_path.exists() else {}
    pending_backsync = extract_pending_backsync()
    ext_invariants = extract_extended_invariants()

    lines_out: list[str] = [
        f'# Gói Ngữ cảnh 4 Lớp — `{mod_id}` ({mod_entry.get("name", "N/A")})',
        '',
        f'> **Tạo tự động bởi `05-tools/build_module_context.py` lúc {datetime.now(timezone.utc).isoformat()}**  ',
        '> Lưu ý: Đặt file này trong `scratch/` ngoài kho để không ảnh hưởng `verify_delivery_plan.py`.',
        '',
        f'## 0. Chốt Chặn Ngữ cảnh Xuyên Wave & Bài học Kiến trúc Cần Áp dụng cho `{mod_id}`',
        f'- **Trạng thái Manifest (`active-task.json`):** `{active_task.get("spec_review_status", "N/A")}` | Readiness: `{active_task.get("implementation_readiness", "N/A")}` | Next: `{active_task.get("proposed_next_slice", "N/A")}`',
        '- **Tài liệu Thay đổi Wave 1 đã Khóa (`Read-on-Demand`):** [CR-20261116-WAVE1-REVIEW-FIXES.md](file:///d:/AI%20Agent/CRM/02-specs/changes/archive/CR-20261116-WAVE1-REVIEW-FIXES.md) & [CR-20261116-WAVE1-5-HARDENING.md](file:///d:/AI%20Agent/CRM/02-specs/changes/archive/CR-20261116-WAVE1-5-HARDENING.md).',
        '- **Bất biến Bắt buộc từ Wave 1 (`INV-22..28` — Không được làm mất ở Wave 2–6):**',
    ]
    for inv in ext_invariants:
        lines_out.append(f'  - **`{inv["id"]}`:** {inv["rule"]}')
    if mod_id in {'M01', 'M02', 'M03', 'M06', 'M08', 'M11', 'M12', 'M15', 'M18', 'M21', 'M22'}:
        lines_out.append(
            f'  - **Lưu ý đặc thù `{mod_id}` (`INV-27` / `W1-01`):** Nếu phát sinh bảng lưu trữ bất biến chứa dữ liệu khách hàng/nhân sự (hội thoại, ghi chú, draft AI, ticket, hồ sơ), áp dụng `redacted_deletion_ledger_ids uuid[]` (xóa đa chủ thể nối tiếp) + tách đôi `content_sha256` vs `redacted_content_sha256` + truy tìm đa nguồn với `M20.SubjectErasureExecuted`.'
        )
    if mod_id in {'M01', 'M03', 'M04', 'M06', 'M09', 'M10', 'M11', 'M12', 'M13', 'M15', 'M17', 'M21', 'M22'}:
        lines_out.append(
            f'  - **Lưu ý đặc thù `{mod_id}` (`INV-26` / `W1-02..03`):** Tích hợp ngoài dùng `M19` (`C19` — đã khóa `lease_token` fencing CAS 3 pha + Bảng Reaper 8 nhánh); sự kiện nội bộ dùng `M23-F12` (`C23` `Lane 2`). Bất kỳ worker/scheduler riêng nào của `{mod_id}` nhả DB lock phải tuân thủ `lease_token` CAS.'
        )
    lines_out.append('- **Hàng đợi Đồng bộ Ngược (`[PENDING-BACKSYNC]`):**')
    if pending_backsync:
        lines_out.extend(f'  - {item}' for item in pending_backsync)
    else:
        lines_out.append('  - Không có mục `[PENDING-BACKSYNC]` đang mở.')

    lines_out.extend([
        '',
        '## 1. Hồ sơ Module & Dải dòng Master cần đọc (`Read-Targeted`)',
        f'- **Actors:** {mod_entry.get("actors", "N/A")}',
        f'- **Owned Data (Master):** `{mod_entry.get("owned_data_source", "N/A")}`',
        f'- **Dependencies (Master):** `{mod_entry.get("dependencies_source", "N/A")}`',
        f'- **Priority:** {mod_entry.get("priority_source", "N/A")} (Master dòng `{mod_entry.get("source_line", "?")}`)',
        f'- **Dòng xuất hiện của IDs `owner == {mod_id}` trong Master v1.9:** `{occ_lines}`',
        '- **Các mục Master v1.9 liên quan (dùng `read_file` theo đúng `StartLine..EndLine`):**',
    ])
    for s in master_secs:
        lines_out.append(f'  - `{s["heading"]}`: `L{s["start"]}–L{s["end"]}`')

    lines_out.extend(['', '## 2. Danh mục Chức năng (`FUNCTION-CATALOG.md`)', '', cat_block or '*(Không tìm thấy trong catalog)*'])

    lines_out.extend([
        '',
        f'## 3. Lớp 1 — Toàn bộ {len(owned_recs)} IDs `owner == {mod_id}` (`requirements.json`)',
        '',
        '| ID | Kind | Master Lines | Tóm tắt định nghĩa / tham chiếu | Tests |',
        '|---|---|---|---|---|',
    ])
    for r in sorted(owned_recs, key=lambda x: x['id']):
        occ_txt = _pick_primary_occurrence(r)
        lines_out.append(
            f'| `{r["id"]}` | `{r.get("kind", "")}` | `{r.get("source", {}).get("lines", [])}` | '
            f'{sanitize_cell(occ_txt, 140)} | `{", ".join(r.get("tests", [])) or "—"}` |'
        )

    lines_out.extend([
        '',
        '## 4. Lớp 2 — Hợp đồng Upstream cần đọc (`02-specs/contracts/`)',
        '- Luôn đọc [CONTRACTS-REGISTRY.md](file:///d:/AI%20Agent/CRM/02-specs/CONTRACTS-REGISTRY.md) trước, sau đó đọc trực tiếp các Contract phụ thuộc:',
    ])
    for c in upstream_contracts:
        lines_out.append(f'  - `02-specs/contracts/{c.name}`')

    lines_out.extend([
        '',
        f'## 5. Lớp 3 — Thực thể, Hợp đồng gốc, ID chưa gán Owner & Rule chưa đánh số (`4-Layer Harvest`)',
        f'- **`ENTITY-Lxxxx` khớp ({len(matched_entities)}):**',
    ])
    for e in matched_entities:
        lines_out.append(f'  - `{e["id"]}` (`L{e["source_line"]}`): {sanitize_cell(e.get("text", ""), 130)}')
    lines_out.append(f'- **`CONTRACT-Lxxxx` khớp ({len(matched_master_contracts)}):**')
    for c in matched_master_contracts:
        lines_out.append(f'  - `{c["id"]}` (`L{c["source_line"]}`): {sanitize_cell(c.get("text", ""), 130)}')
    lines_out.append(f'- **ID `missing_owner` liên quan ({len(unowned_reqs)} — review đưa vào Trace nếu là Consumer/Owner):**')
    for r in unowned_reqs:
        occ_txt = _pick_primary_occurrence(r)
        lines_out.append(f'  - `{r["id"]}` (`L{r.get("source", {}).get("lines", [])}`): {sanitize_cell(occ_txt, 125)}')
    lines_out.append(f'- **Unnumbered rules liên quan ({len(matched_unnumbered)}):**')
    for u in matched_unnumbered:
        lines_out.append(f'  - `{u["id"]}` (`L{u["source_line"]}`): {sanitize_cell(u.get("text", ""), 130)}')
    lines_out.append(f'- **GAP đang mở liên quan (`03-planning/GAPS.md`, {len(matched_gaps)}):**')
    for g in matched_gaps:
        lines_out.append(f'  - {sanitize_cell(g, 190)}')

    lines_out.extend([
        '',
        f'## 6. Lớp 4 — Liên kết Chiều ra & Ngang hàng (`Downstream & Sibling Touchpoints` cho `{mod_id}`)',
        '- **Các module phụ thuộc vào `' + mod_id + '` theo `modules.json`:** '
        + (', '.join(f'`{m["id"]}` ({m["name"]})' for m in downstream_modules) or '*(không có)*'),
        '- **Điểm nối chéo từ `FUNCTION-CATALOG.md` (cả module chưa bóc tách):**',
    ])
    lines_out.extend(catalog_cross_refs or ['  - *(không có)*'])
    lines_out.append('- **Tham chiếu từ `02-specs/contracts/` đã phát hành:**')
    lines_out.extend(contract_cross_refs or ['  - *(không có)*'])

    packet = '\n'.join(lines_out) + '\n'
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(packet, encoding='utf-8')
        write_receipt(out_path)
    return packet


def check_session_tokens(transcript_path: Path | None = None, max_age_minutes: int = 20) -> dict:
    """Inspect latest PLANNER_RESPONSE token usage from Antigravity transcript.jsonl (read-only)."""
    target = transcript_path
    if target is None or not target.exists():
        return {
            'status': 'UNKNOWN',
            'reason': 'No explicitly bound transcript; current session usage is UNKNOWN',
            'yellow_threshold': YELLOW_THRESHOLD,
            'red_threshold': RED_THRESHOLD,
        }

    if datetime.now(timezone.utc).timestamp() - target.stat().st_mtime > max_age_minutes * 60:
        return {'status': 'UNKNOWN', 'reason': 'Explicit transcript is stale'}

    latest_usage: dict | None = None
    for raw in target.read_text(encoding='utf-8', errors='replace').splitlines():
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get('type') == 'PLANNER_RESPONSE' and (
            obj.get('input_tokens') is not None or obj.get('cache_read_tokens') is not None
        ):
            latest_usage = obj

    if not latest_usage:
        return {
            'status': 'UNKNOWN',
            'transcript': str(target),
            'reason': 'No PLANNER_RESPONSE token metrics recorded yet',
            'yellow_threshold': YELLOW_THRESHOLD,
            'red_threshold': RED_THRESHOLD,
        }

    in_tok = int(latest_usage.get('input_tokens') or 0)
    cache_tok = int(latest_usage.get('cache_read_tokens') or 0)
    total_ctx = in_tok + cache_tok
    if total_ctx > RED_THRESHOLD:
        light = 'RED'
        guidance = 'RED ALERT (>210k): Stop expanding scope, save files + PROGRESS.md Handoff, and start a fresh session.'
    elif total_ctx >= YELLOW_THRESHOLD:
        light = 'YELLOW'
        guidance = 'YELLOW WARNING (170k-210k): Do NOT spawn long-running subagents (>3m); finish edits & verify inline.'
    else:
        light = 'GREEN'
        guidance = 'GREEN (<170k): Safe to proceed and delegate to subagents.'

    session_id = target.parent.parent.parent.name if len(target.parents) >= 3 else 'unknown'
    return {
        'status': light,
        'session_id': session_id,
        'step_index': latest_usage.get('step_index'),
        'recorded_at': latest_usage.get('created_at'),
        'input_tokens': in_tok,
        'cache_read_tokens': cache_tok,
        'total_context_tokens': total_ctx,
        'yellow_threshold': YELLOW_THRESHOLD,
        'red_threshold': RED_THRESHOLD,
        'guidance': guidance,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='CRM spec context optimizer, registry builder & token guard.')
    parser.add_argument('--build-registry', action='store_true', help='Regenerate 02-specs/CONTRACTS-REGISTRY.md')
    parser.add_argument('--module', help='Build 4-layer, 2-way context packet for module ID (e.g. M01)')
    parser.add_argument('--out', help='Optional output file path (recommended outside repo under scratch/)')
    parser.add_argument('--check-tokens', action='store_true', help='Report current session token status (GREEN/YELLOW/RED)')
    parser.add_argument('--verify-packet', help='Verify a generated packet and its source receipt before use')
    parser.add_argument('--transcript', help='Optional explicit transcript.jsonl path for --check-tokens')
    args = parser.parse_args()

    if not (args.build_registry or args.module or args.check_tokens or args.verify_packet):
        parser.print_help()
        return 1

    result: dict = {}
    if args.verify_packet:
        issues = verify_receipt(Path(args.verify_packet).resolve())
        print(json.dumps({'context_valid': not issues, 'issues': issues}, ensure_ascii=False))
        return 1 if issues else 0
    if args.build_registry:
        reg_path = build_contracts_registry()
        result['registry_written'] = str(reg_path.relative_to(ROOT))
        result['registry_bytes'] = reg_path.stat().st_size

    if args.module:
        out_p = Path(args.out).resolve() if args.out else None
        packet = build_module_context_packet(args.module, out_p)
        if out_p:
            result['context_packet_written'] = str(out_p)
            result['context_packet_bytes'] = out_p.stat().st_size
        else:
            print(packet)

    if args.check_tokens:
        t_path = Path(args.transcript) if args.transcript else None
        result['token_telemetry'] = check_session_tokens(t_path)

    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({'context_error': str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
