"""Adversarial checks against original private desktop/editor observations."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'source/build'))
from record_gnome_editor_exit import judge, MODES

ORIGINALS = {}


class EditorDesktopEvidence(unittest.TestCase):
    def reject(self, change, mode='editor-key'):
        raw, composition = copy.deepcopy(ORIGINALS[mode])
        change(raw)
        with self.assertRaises((ValueError, AssertionError, KeyError, IndexError, TypeError)):
            judge(raw, composition)

    def test_originals(self):
        for mode, (raw, composition) in ORIGINALS.items():
            self.assertEqual(judge(raw, composition), raw['evaluation'])
            self.assertEqual(raw['evaluation']['outcome'], 'fail' if mode == 'editor-no-exit' else 'pass')

    def test_unheld_editor(self): self.reject(lambda r: r['held_live'].pop('editor'))
    def test_wrong_parent(self): self.reject(lambda r: r['identities']['editor'].update(parent=0))
    def test_shared_controller_group(self): self.reject(lambda r: r['identities']['editor'].update(process_group=r['identities']['controller']['pid']))
    def test_dead_collector(self): self.reject(lambda r: r['final_live'].update(source=False))
    def test_replaced_shell(self): self.reject(lambda r: r['controller'].append(next(e for e in r['controller'] if e['event'] == 'consumer_spawned')))
    def test_unrelated_render_fault(self): self.reject(lambda r: r['controller'].append({'event': 'render_fault'}))
    def test_wrong_fault(self): self.reject(lambda r: r['fault'].update(pid=r['identities']['source']['pid']))
    def test_undiscovered_icon(self): self.reject(lambda r: r.update(icon_center=[0, 0]))
    def test_wrong_window_owner(self): self.reject(lambda r: r['editor_window'].update(pid=0))
    def test_wrong_resource(self): self.reject(lambda r: r['editor_window'].update(resource_base=0))
    def test_nonobstructing_geometry(self): self.reject(lambda r: r['editor_window'].update(x=500))
    def test_wrong_button_owner(self): self.reject(lambda r: r['button'].update(pid=0), 'editor-button')
    def test_shortcut_without_request(self): self.reject(lambda r: r.update(exit_owner_events=[e for e in r['exit_owner_events'] if e['event'] != 'keyboard_exit']))
    def test_safety_timer_exit(self): self.reject(lambda r: r['exit_owner_events'].append({'event': 'deadline'}))
    def test_missing_escalation(self): self.reject(lambda r: r.update(exit_owner_events=[e for e in r['exit_owner_events'] if e['event'] != 'force_stop']))
    def test_icon_not_blocked(self): self.reject(lambda r: r['blocked_input'].update(owner_changed=True))
    def test_editor_not_stopped(self): self.reject(lambda r: r['stopped'].update(editor='R'))
    def test_unconfirmed_exit(self): self.reject(lambda r: r['editor_exit'].update(pidfd_exit=False))
    def test_late_release(self): self.reject(lambda r: r.update(pixel_restored_ns=r['fault']['begin_ns'] + 1_500_000_001))
    def test_late_input(self): self.reject(lambda r: r.update(input_restored_ns=r['fault']['begin_ns'] + 2_500_000_001))
    def test_controller_resumed_first(self): self.reject(lambda r: r.update(controller_resumed_ns=r['pixel_restored_ns'] - 1), 'editor-controller-freeze')
    def test_short_post_observation(self): self.reject(lambda r: r.update(post=r['post'][:5]))
    def test_replayed_operational_pixels(self): self.reject(lambda r: [s.update(pixels=r['baseline'][-1]['pixels']) for s in r['post']])
    def test_observer_drove_recovery(self): self.reject(lambda r: r['calls'].append({'begin_ns': r['post'][0]['begin_ns']}))
    def test_collection_paused(self): self.reject(lambda r: r.update(source=r['source'][:2]))
    def test_replaced_epoch(self):
        def change(raw):
            message = json.loads(raw['source'][-1]['payload'])
            message['body']['snapshot']['producer_epoch'] = 'replacement'
            raw['source'][-1]['payload'] = json.dumps(message)
        self.reject(change)
    def test_negative_too_short(self): self.reject(lambda r: r.update(negative_end_ns=r['fault']['end_ns'] + 1), 'editor-no-exit')
    def test_negative_released(self): self.reject(lambda r: r.update(negative_alive=False), 'editor-no-exit')
    def test_negative_owner_running(self): self.reject(lambda r: r['stopped'].update(exit_owner='R'), 'editor-no-exit')


if __name__ == '__main__':
    for name in sys.argv[1:]:
        report = json.loads(Path(name).read_text())
        raw = json.loads(Path(report['network_private_artifacts']['network-controller-recovery.private.json']['path']).read_text())
        ORIGINALS[raw['mode']] = (raw, report['observation']['composition'])
    if set(ORIGINALS) != set(MODES): raise ValueError('five original native editor controls required')
    sys.argv = [sys.argv[0], '-v']
    unittest.main()
