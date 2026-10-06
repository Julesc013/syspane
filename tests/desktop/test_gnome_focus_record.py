"""Reject false candidate absence, native ownership, keyboard receipts and comparisons."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_focus import validate, compare
from gnome_focus_baseline import keyboard

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(9)]
BY_MODE={r['focus_baseline_mode']:r for r in REPORTS}


class FocusEvidence(unittest.TestCase):
    def reject(self, mutate, mode='ding'):
        value=copy.deepcopy(BY_MODE[mode])
        mutate(value,value['observation']['focus_baseline'])
        with self.assertRaises(ValueError):validate(value,BUILD)

    def test_all_native_repetitions(self):
        self.assertEqual(compare([validate(r,BUILD) for r in REPORTS])['outcome'],'stable')

    def test_candidate_cannot_be_hidden_in_baseline(self):
        self.reject(lambda r,c:r['enabled_extension_inputs'].update({'syspane-lab-marker@syspane.invalid/extension.js':{'bytes':1,'sha256':'0'*64}}))

    def test_candidate_cannot_be_enabled_in_baseline(self):
        self.reject(lambda r,c:c['extensions_before'].append('syspane-lab-marker@syspane.invalid'))

    def test_shell_only_cannot_include_icons(self):
        self.reject(lambda r,c:c.update(icon_manager=BY_MODE['ding']['observation']['focus_baseline']['icon_manager']),mode='shell')

    def test_changed_native_icon_extension(self):
        self.reject(lambda r,c:r['ding_inputs']['extension.js'].update(sha256='0'*64))

    def test_foreign_foreground_pid(self):
        self.reject(lambda r,c:c['foreground'].update(pid=1))

    def test_foreign_icon_pid(self):
        self.reject(lambda r,c:c['icon_manager'].update(pid=1))

    def test_foreground_wrong_geometry(self):
        self.reject(lambda r,c:c['foreground'].update(geometry=[0,0,200,120]))

    def test_unconfirmed_foreground_exit(self):
        self.reject(lambda r,c:next(x for x in r['cleanup'] if x['process']=='foreground').update(exit=None))

    def test_key_before_interval_end(self):
        self.reject(lambda r,c:c['unfocused_key'].update(started_ns=c['started_monotonic_ns']))

    def test_changed_event_file_identity(self):
        self.reject(lambda r,c:c['events_after_f9'].update(inode=0))

    def test_missing_positive_key(self):
        self.reject(lambda r,c:c['events_after_f10']['events'].clear())

    def test_receipt_from_another_process(self):
        self.reject(lambda r,c:c['events_after_f10']['events'][-1].update(pid=1))

    def test_late_keyboard_receipt(self):
        value=copy.deepcopy(BY_MODE['ding']['observation']['focus_baseline'])
        value['events_after_f10']['events'][-1]['received_ns']=value['focused_key']['finished_ns']+200000001
        with self.assertRaises(ValueError):keyboard(value)

    def test_false_keyboard_delivery_claim(self):
        self.reject(lambda r,c:c['keyboard'].update(f9_delivered=not c['keyboard']['f9_delivered']))

    def test_changed_raw_keyboard_journal(self):
        self.reject(lambda r,c:r['foreground_events'].update(sha256='0'*64))

    def test_changed_focus_journal(self):
        self.reject(lambda r,c:r['focus_journal'].update(sha256='0'*64))

    def test_native_acceptance_cannot_be_relabelled(self):
        self.reject(lambda r,c:c['evaluation'].update(focus='pass' if c['evaluation']['focus']=='fail' else 'fail'))

    def test_missing_capture(self):
        self.reject(lambda r,c:c['interval']['samples'].clear())

    def test_late_native_action(self):
        self.reject(lambda r,c:c['interval']['actions'][0].update(start_us=700000,end_us=700001))

    def test_candidate_original_oracle_kept(self):
        self.reject(lambda r,c:r['observation']['reveal']['evaluation'].update(outcome='pass'),mode='candidate')

    def test_comparison_requires_three_per_mode(self):
        rows=[{'mode':mode} for mode in ['shell','ding','candidate']]
        with self.assertRaises(ValueError):compare(rows)

    def test_disagreeing_repetition_is_inconclusive(self):
        rows=[{'mode':m,'visual_reveal':'pass','focus':'fail','phase_roles':[['foreground'],['icon'],['icon']],'f9_delivered':False}
              for m in ['shell','ding','candidate']*3]
        rows[-1]['f9_delivered']=True
        self.assertEqual(compare(rows)['outcome'],'inconclusive')

    def test_matching_all_modes_does_not_blame_ding(self):
        rows=[{'mode':m,'visual_reveal':'pass','focus':'fail','phase_roles':[['foreground'],['none'],['none']],'f9_delivered':False}
              for m in ['shell','ding','candidate']*3]
        result=compare(rows)
        self.assertTrue(result['focus_failure_without_bridge'])
        self.assertFalse(result['requires_ding_in_this_lab'])


if __name__=='__main__':unittest.main()
