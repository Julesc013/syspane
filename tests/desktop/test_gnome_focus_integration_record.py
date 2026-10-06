"""Reject false focus, guard, ownership and disabled-callback evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_focus_integration import validate
from gnome_focus_integration import judge_step, STEPS
from native_x11_host import rgb_record

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS = [json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(2)]
MODES = {r['focus_integration_mode']:r for r in REPORTS}
SNAPSHOTS = ['initial_trace','before_folder_trace','after_folder_trace','before_disable_trace','after_disable_trace','final_trace']


def traces(result, change):
    for name in SNAPSHOTS:
        for row in result[name]['records']:change(row)


class FocusIntegrationEvidence(unittest.TestCase):
    def reject(self, mutate, mode='restore', sync=True):
        value = copy.deepcopy(MODES[mode]); result = value['observation']['focus_integration']; mutate(value,result)
        if not sync:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        owners = value['observation']['focus_baseline']
        for row in result['steps']:
            try:row['evaluation'] = judge_step(row,mode,owners['foreground']['window'],owners['icon_manager']['window'])
            except ValueError:pass
        rows = [json.loads(line) for line in Path(value['focus_integration_journal']['path']).read_text().splitlines()]
        steps = iter(result['steps']); verdicts = iter(result['steps'])
        for row in rows:
            kind = row['kind']
            if kind == 'completed':row['value'] = result
            elif kind == 'step':row['value'] = {k:v for k,v in next(steps,{}).items() if k != 'evaluation'}
            elif kind == 'verdict':row['value'] = next(verdicts,{}).get('evaluation',{})
            elif kind == 'prepared':row['value'] = {k:result[k] for k in ['version','mode','initial_trace','started_monotonic_ns']} | {'not_run':STEPS+['folder-input','disable']}
            elif kind == 'folder-input':row['value'] = {k:result[k] for k in ['before_folder_trace','folder_started_ns','folder_input','folder_finished_ns','after_folder_trace']}
            elif kind == 'disabled':row['value'] = {k:result[k] for k in ['before_disable_trace','disable_started_ns','disable_finished_ns','after_disable_trace']}
        raw = ('\n'.join(json.dumps(r) for r in rows)+'\n').encode()
        with patch('record_gnome_focus_integration.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_native_observe_and_restore(self):
        results = [validate(r,BUILD) for r in REPORTS]
        self.assertEqual([r['original_focus'] for r in results],['fail','pass'])
        self.assertEqual([r['f9_delivered'] for r in results],[False,True])
        self.assertTrue(all(len(r['guards']) == 15 for r in results))
    def test_wrong_environment_mode(self):self.reject(lambda v,r:v['environment']['explicit'].update(SYSPANE_GNOME_FOCUS_INTEGRATION='observe'))
    def test_traced_experiment_not_admitted(self):self.reject(lambda v,r:v.update(focus_trace=True))
    def test_missing_guard(self):self.reject(lambda v,r:r['steps'].pop(1))
    def test_guard_before_original_keyboard(self):self.reject(lambda v,r:r.update(started_monotonic_ns=1))
    def test_later_click_substituted_for_restore(self):self.reject(lambda v,r:r['steps'][5]['action'].update(kind={'click':[600,110]}))
    def test_guard_minimizes_another_window(self):self.reject(lambda v,r:r['steps'][10]['action'].update(kind={'minimize':1}))
    def test_guard_order(self):self.reject(lambda v,r:r['steps'][2].update(started_monotonic_ns=1))
    def test_guard_has_no_settled_coverage(self):self.reject(lambda v,r:r['steps'][5].update(samples=r['steps'][5]['samples'][:3]))
    def test_capture_too_slow(self):self.reject(lambda v,r:r['steps'][5]['samples'][-1].update(end_us=r['steps'][5]['samples'][-1]['start_us']+50001))
    def test_guard_duration(self):self.reject(lambda v,r:r['steps'][5].update(end_us=700000))
    def test_stale_marker(self):self.reject(lambda v,r:r['steps'][5]['samples'][-1].update(marker=rgb_record(bytes(128*96*3))))
    def test_hidden_foreground_claimed_visible(self):self.reject(lambda v,r:r['steps'][5]['samples'][-1].update(foreground=rgb_record(bytes([48,72,96])*400)))
    def test_changed_background(self):self.reject(lambda v,r:r['steps'][5]['samples'][-1].update(background=rgb_record(bytes(128*96*3))))
    def test_late_focus(self):self.reject(lambda v,r:r['steps'][5]['samples'][-3]['native'].update(active_window=[v['observation']['focus_baseline']['icon_manager']['window']]))
    def test_wrong_native_pid(self):
        def change(v,r):
            owner = v['observation']['focus_baseline']['foreground']['window']
            next(c for c in r['steps'][0]['samples'][-1]['native']['clients'] if c['window'] == owner)['pid'] = [1]
        self.reject(change)
    def test_wrong_native_type(self):self.reject(lambda v,r:r['steps'][0]['samples'][-1]['native']['clients'][0].update(type=[0]))
    def test_unexpected_native_client(self):self.reject(lambda v,r:r['steps'][0]['samples'][-1]['native']['client_order_bottom_to_top'].append(1))
    def test_icon_focus_stolen(self):self.reject(lambda v,r:r['steps'][0]['samples'][-1]['native'].update(active_window=[v['observation']['focus_baseline']['foreground']['window']]))
    def test_unrelated_key_restores_focus(self):self.reject(lambda v,r:r['steps'][1]['samples'][-1]['native'].update(active_window=[v['observation']['focus_baseline']['foreground']['window']]))
    def test_minimized_window_unminimized(self):self.reject(lambda v,r:r['steps'][11]['samples'][-1].update(wm_state=[1,0]))
    def test_disabled_controller_restores_focus(self):self.reject(lambda v,r:r['steps'][14]['samples'][-1]['native'].update(active_window=[v['observation']['focus_baseline']['foreground']['window']]))
    def test_changed_final_binding(self):self.reject(lambda v,r:r.update(binding_after="['<Super>x']"))
    def test_changed_final_wallpaper(self):self.reject(lambda v,r:r['background_after'].update(**{'picture-uri':"'file:///foreign'"}))
    def test_folder_before_desktop_entry(self):self.reject(lambda v,r:r.update(folder_started_ns=r['started_monotonic_ns']))
    def test_disable_after_observation(self):self.reject(lambda v,r:r.update(disable_finished_ns=r['finished_monotonic_ns']))
    def test_disabled_flag_not_cleared(self):self.reject(lambda v,r:r['after_disable_trace'].update(enabled=True))
    def test_trace_rewritten_after_disable(self):self.reject(lambda v,r:r['final_trace']['records'][-1].update(pid=1))
    def test_stale_target_sequence(self):self.reject(lambda v,r:traces(r,lambda row:row.update(target_sequence=999) if row['event'] == 'restore' else None))
    def test_foreign_focus_target(self):self.reject(lambda v,r:traces(r,lambda row:row.update(target_pid=1) if row['event'] == 'restore' else None))
    def test_non_key_restore(self):self.reject(lambda v,r:traces(r,lambda row:row.update(event_type=None,eligible_event=False) if row['event'] == 'restore' else None))
    def test_wrong_modifier(self):self.reject(lambda v,r:traces(r,lambda row:row.update(state=4) if row['event'] == 'restore' else None))
    def test_zero_native_time(self):self.reject(lambda v,r:traces(r,lambda row:row.update(native_time=0) if row['event'] == 'restore' else None))
    def test_foreign_workspace(self):self.reject(lambda v,r:traces(r,lambda row:row.update(workspace=1) if row['event'] == 'restore' else None))
    def test_restore_without_call(self):self.reject(lambda v,r:traces(r,lambda row:row.update(performed=False) if row['event'] == 'restore' else None))
    def test_observe_cannot_call_focus(self):self.reject(lambda v,r:traces(r,lambda row:row.update(performed=True) if row['event'] == 'restore' else None),mode='observe')
    def test_minimized_target_retained(self):self.reject(lambda v,r:traces(r,lambda row:row.update(target_pid=v['observation']['focus_baseline']['foreground']['pid']) if row['event'] == 'abstain' else None))
    def test_native_folder_misidentified(self):self.reject(lambda v,r:traces(r,lambda row:row.update(pid=1) if row['event'] == 'remember' and row['pid'] == r['folder_input']['folder']['pid'] else None))
    def test_folder_key_event_invented(self):self.reject(lambda v,r:traces(r,lambda row:row.update(eligible_event=True) if row['event'] == 'abstain' and row['event_type'] is None else None))
    def test_callback_after_disable(self):self.reject(lambda v,r:traces(r,lambda row:row.update(monotonic_us=r['disable_finished_ns']//1000) if row['event'] == 'remember' else None))
    def test_original_f9_claim(self):self.reject(lambda v,r:v['observation']['focus_baseline']['keyboard'].update(f9_delivered=False))
    def test_owned_foreground_not_retained(self):self.reject(lambda v,r:next(c for c in v['cleanup'] if c['process'] == 'foreground').update(members_before_stop=[]))
    def test_raw_journal_identity(self):self.reject(lambda v,r:v['focus_integration_journal'].update(sha256='0'*64),sync=False)
    def test_missing_cleanup(self):self.reject(lambda v,r:v['cleanup'][0].update(members_after_stop=[{'pid':1}]))


if __name__ == '__main__':unittest.main()
