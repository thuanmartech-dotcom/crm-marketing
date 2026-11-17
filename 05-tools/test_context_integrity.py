"""Regression tests for documentation tooling only."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import context_integrity as ci
import build_module_context as loader


class ContextIntegrityTests(unittest.TestCase):
    def test_unbound_telemetry_is_unknown(self):
        self.assertEqual(loader.check_session_tokens()['status'], 'UNKNOWN')

    def test_required_source_missing_is_error(self):
        original = Path.is_file
        with patch.object(Path, 'is_file', lambda p: False if p.name == 'INVARIANTS.md' else original(p)):
            self.assertTrue(any('INVARIANTS' in s for s in ci.context_issues()))

    def test_registry_detects_content_change(self):
        original = Path.read_bytes
        with patch.object(Path, 'read_bytes', lambda p: original(p) + b'changed' if p.name.startswith('M20-') else original(p)):
            self.assertTrue(any('Registry stale' in s for s in ci.context_issues()))

    def test_reaper_wrong_destination_is_error(self):
        original = Path.read_text
        def changed(p, *a, **kw):
            text = original(p, *a, **kw)
            if p.name.startswith('M19-DURABLE'):
                text = '\n'.join(line.replace('RETRY_WAITING', 'QUEUED') if 'Nhánh 7 (' in line else line
                                 for line in text.splitlines())
            return text
        with patch.object(Path, 'read_text', changed):
            self.assertTrue(any('branch 7' in s for s in ci.wave_guard_issues()))

    def test_receipt_rejects_packet_and_source_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / 'context.md'
            packet.write_text('context', encoding='utf-8')
            ci.write_receipt(packet)
            self.assertEqual(ci.verify_receipt(packet), [])
            packet.write_text('tampered', encoding='utf-8')
            self.assertIn('Context packet changed', ci.verify_receipt(packet))
            original = Path.read_bytes
            with patch.object(Path, 'read_bytes', lambda p: original(p) + b'changed' if p.name == 'active-task.json' else original(p)):
                self.assertTrue(any('active-task.json' in s for s in ci.verify_receipt(packet)))

    def test_full_invariant_and_harvest(self):
        packet = loader.build_module_context_packet('M01')
        inv = next(item for item in loader.extract_extended_invariants() if item['id'] == 'INV-26')
        self.assertNotIn('...', inv['rule'])
        self.assertIn(inv['rule'], packet)
        import re
        count = int(re.search(r'Unnumbered rules liên quan \((\d+)\)', packet)[1])
        self.assertEqual(count, len(re.findall(r'  - `UNNUMBERED-', packet)))

    def test_wave_guard_inv27_aligned_repo_passes(self):
        self.assertEqual(ci.wave_guard_issues(), [])

    def test_inv27_mutated_m23_and_is_null_gate_caught_without_false_positives(self):
        original_read_text = Path.read_text

        def mutated_m23_single_shot(p, *a, **kw):
            text = original_read_text(p, *a, **kw)
            if p.name == 'M23-SYSTEM-ADMIN-SECURITY-OPS.md':
                lines = [
                    '   - `privacy_erasure_system_role` (chỉ scrub 1 lần `M16.Task_Submissions.privacy_redacted_at` ngoài `Legal_Hold` theo `ADR-004`).'
                    if '**`privacy_erasure_system_role`**' in ln
                    else ln
                    for ln in text.splitlines()
                ]
                return '\n'.join(lines) + '\n'
            return text

        with patch.object(Path, 'read_text', mutated_m23_single_shot):
            issues = ci.wave_guard_issues()
        self.assertTrue(any('M23-SYSTEM-ADMIN-SECURITY-OPS.md' in s and 'single-shot PII scrub' in s for s in issues), issues)
        self.assertTrue(any('M23-SYSTEM-ADMIN-SECURITY-OPS.md' in s and 'redacted_deletion_ledger_ids' in s for s in issues), issues)

        def mutated_m16_is_null(p, *a, **kw):
            text = original_read_text(p, *a, **kw)
            if p.name == 'M16-WORK-PROJECTS-TASK-CORE.md':
                return text.replace(
                    'cardinality(active_legal_hold_ids) = 0 AND NOT (redacted_deletion_ledger_ids @> ARRAY[$deletion_ledger_id]::uuid[])',
                    'cardinality(active_legal_hold_ids) = 0 AND privacy_redacted_at IS NULL',
                )
            return text

        with patch.object(Path, 'read_text', mutated_m16_is_null):
            issues_null = ci.wave_guard_issues()
        self.assertTrue(any('M16-WORK-PROJECTS-TASK-CORE.md' in s and 'privacy_redacted_at IS NULL gate' in s for s in issues_null), issues_null)

        # Valid prohibitions, deprecated replaced-design notes, and CR history quotes must pass.
        self.assertEqual(
            ci.find_inv27_erasure_issues('Cấm dùng khóa một lần `privacy_redacted_at IS NULL` trên `Task_Submissions`.', '02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md'),
            [],
        )
        self.assertEqual(
            ci.find_inv27_erasure_issues("Thiết kế cũ 'chỉ scrub 1 lần' (1-time scrub) đã bị loại bỏ.", '02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md'),
            [],
        )
        self.assertEqual(
            ci.find_inv27_erasure_issues("Mô tả lỗi gốc trước khi sửa: chỉ scrub 1 lần `M16.Task_Submissions`.", '02-specs/changes/CR-20261117-TEST.md'),
            [],
        )
        # Mixed clause: prior negation does NOT exempt an independent disallowed clause.
        mixed = ci.find_inv27_erasure_issues(
            'Cấm admin tự xóa; `privacy_erasure_system_role` chỉ scrub 1 lần `M16.Task_Submissions`.',
            '02-specs/modules/M23-SYSTEM-ADMIN-SECURITY-OPS.md',
        )
        self.assertTrue(len(mixed) >= 1, mixed)


if __name__ == '__main__':
    unittest.main()
