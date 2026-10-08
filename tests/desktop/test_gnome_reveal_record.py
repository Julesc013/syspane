"""Adversarial checks for native reveal evidence and temporary-disappearance rejection."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'source/build'))
from record_gnome_reveal import validate
from gnome_reveal import judge
from native_x11_host import rgb_record

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS = [json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
REPORT = next(r for r in REPORTS if r['reveal_control'] == 'live')


class RevealEvidence(unittest.TestCase):
    def reject(self, mutate):
        value = copy.deepcopy(REPORT)
        mutate(value, value['observation']['reveal'])
        with self.assertRaises(ValueError):
            validate(value, BUILD)

    def test_native_controls(self):
        self.assertEqual(sorted(validate(r, BUILD)['control'] for r in REPORTS), ['live', 'no-action', 'transient-blank'])

    def test_foreign_foreground_pid(self):
        self.reject(lambda r,c: c['foreground'].update(pid=1))

    def test_foreground_wrong_group(self):
        self.reject(lambda r,c: c['foreground'].update(process_group=1))

    def test_wrong_window_geometry(self):
        self.reject(lambda r,c: c['foreground'].update(geometry=[0,0,200,120]))

    def test_changed_native_window_type(self):
        self.reject(lambda r,c: c['foreground'].update(type=[0]))

    def test_unconfirmed_foreground_exit(self):
        self.reject(lambda r,c: next(x for x in r['cleanup'] if x['process'] == 'foreground').update(exit=None))

    def test_wrong_binding(self):
        self.reject(lambda r,c: c.update(binding_after='[]'))

    def test_missing_action(self):
        self.reject(lambda r,c: c['actions'].pop())

    def test_late_action(self):
        self.reject(lambda r,c: c['actions'][0].update(start_us=600000, end_us=600001))

    def test_relabelled_omitted_action(self):
        self.reject(lambda r,c: c['actions'][0].update(performed=False))

    def test_missing_paired_sample(self):
        self.reject(lambda r,c: c['samples'].pop())

    def test_reversed_capture_order(self):
        self.reject(lambda r,c: c['samples'][0].update(foreground_start_us=0))

    def test_missing_foreground_native_client(self):
        self.reject(lambda r,c: c['samples'][0]['native'].update(clients=[]))

    def test_changed_background_settings(self):
        self.reject(lambda r,c: c['background_settings_after'].update(**{'primary-color': "'#000000'"}))

    def test_changed_background_pixels_with_valid_hash(self):
        self.reject(lambda r,c: c['samples'][0].update(background=rgb_record(bytes(128*96*3))))

    def test_forged_transition_claim(self):
        self.reject(lambda r,c: c['evaluation'].update(transition_latency_us=[0,0]))

    def test_changed_journal(self):
        self.reject(lambda r,c: r['reveal_journal'].update(sha256='0'*64))

    def test_native_flag_without_visible_disappearance_fails(self):
        c = copy.deepcopy(REPORT['observation']['reveal'])
        for row in c['samples']:
            row['foreground'] = rgb_record(bytes((24,160,192))*400)
        self.assertEqual(judge(c, REPORT['observation']['composition'])['visual_reveal'], 'fail')

    def test_visible_disappearance_without_native_state_fails(self):
        c = copy.deepcopy(REPORT['observation']['reveal'])
        for row in c['samples']:
            row['native']['showing_desktop'] = [0]
        self.assertEqual(judge(c, REPORT['observation']['composition'])['visual_reveal'], 'fail')

    def test_false_focus_pass(self):
        self.reject(lambda r,c: c['evaluation'].update(focus='pass' if c['evaluation']['focus'] == 'fail' else 'fail'))

    def test_focus_first_observed_after_deadline_fails(self):
        c = copy.deepcopy(REPORT['observation']['reveal'])
        deadline = c['actions'][1]['end_us'] + 200000
        for frame, row in zip(c['trace']['frames'], c['samples']):
            if frame['start_us'] >= deadline:
                row['native']['active_window'] = [c['foreground']['window']]
        result = judge(c, REPORT['observation']['composition'])
        self.assertEqual(result['focus'], 'fail')
        self.assertEqual(result['reveal'], 'fail')

    def test_temporary_failure_is_not_repaired_into_pass(self):
        record = next(r for r in REPORTS if r['reveal_control'] == 'transient-blank')
        result = judge(record['observation']['reveal'], record['observation']['composition'])
        self.assertEqual(result['outcome'], 'fail')
        self.assertIn('marker.absent_or_invalid', result['marker']['failures'])
        self.assertTrue(result['composition']['samples'][-1]['rectangle'])


if __name__ == '__main__':
    unittest.main()
