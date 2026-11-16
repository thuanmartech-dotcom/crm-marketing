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


if __name__ == '__main__':
    unittest.main()
