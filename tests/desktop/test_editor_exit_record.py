"""Reject material corruption of the independent native recovery evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'source/build'))
from record_editor_exit import validate_facts

REPORT = json.loads(Path(sys.argv.pop(1)).read_text())


class Evidence(unittest.TestCase):
    def test_original(self):
        self.assertEqual(validate_facts(REPORT)['cases'], 9)

    def test_corruption(self):
        changes = [
            ('KEY-FROZEN', 'input_restored_ns', lambda r: r['stimulus_ns'] + 1_500_000_001),
            ('KEY-FROZEN', 'native_exit_ns', lambda r: r['stimulus_ns'] - 1),
            ('KEY-FROZEN', 'restored_pixel', lambda r: 'cc2233'),
            ('KEY-FROZEN', 'input_obstructed', lambda r: False),
            ('KEY-FROZEN', 'parent_verified', lambda r: False),
            ('KEY-FROZEN', 'child_executable_sha256', lambda r: '0' * 64),
            ('KEY-FROZEN', 'child_exit_at_cleanup', lambda r: False),
            ('KEY-FROZEN', 'stopped_before_stimulus', lambda r: False),
            ('KEY-FROZEN', 'shortcut_released', lambda r: False),
            ('KEY-FROZEN', 'owner_events', lambda r: r['owner_events'][:2] + r['owner_events'][3:]),
            ('LOCKS-FROZEN', 'lock_state', lambda r: 0),
            ('DRAG-FROZEN', 'drag_state', lambda r: 0),
            ('KEY-LIVE', 'ordinary_and_shifted_ignored', lambda r: False),
            ('BUTTON-FROZEN', 'native_button', lambda r: {**r['native_button'], 'root_y': 200}),
            ('GRAB-CONFLICT', 'owner_events', lambda r: [{'event': 'child', 'value': 1, 'at_ms': 0}]),
        ]
        for name, key, transform in changes:
            with self.subTest(case=name, corruption=key):
                changed = deepcopy(REPORT)
                row = next(row for row in changed['cases'] if row['case'] == name)
                row[key] = transform(row)
                with self.assertRaises(ValueError):
                    validate_facts(changed)

    def test_missing_case(self):
        changed = deepcopy(REPORT)
        changed['cases'].pop()
        with self.assertRaises(ValueError):
            validate_facts(changed)

    def test_premature_escalation(self):
        changed = deepcopy(REPORT)
        row = next(r for r in changed['cases'] if r['case'] == 'KEY-FROZEN')
        row['owner_events'][2]['at_ms'] = row['owner_events'][1]['at_ms'] + 249
        with self.assertRaises(ValueError):
            validate_facts(changed)


if __name__ == '__main__':
    unittest.main()
