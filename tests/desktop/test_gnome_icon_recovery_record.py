"""Reject false native replacement/progress claims with consistent recovery records."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_icon_recovery import validate
from record_gnome_composition import validate as composition
from gnome_icon_recovery import judge
from native_x11_host import rgb_record
from oracle import unpack_frame,pack_frame

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
BY_CONTROL={r['icon_recovery_control']:r for r in REPORTS}


class RecoveryEvidence(unittest.TestCase):
    def reject(self,mutate,control='live',synchronize=True):
        value=copy.deepcopy(BY_CONTROL[control]);result=value['observation']['icon_recovery'];mutate(value,result)
        if not synchronize:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        try:result['evaluation']=judge(result,value['observation']['composition'])
        except ValueError:pass
        records=[json.loads(line) for line in Path(value['icon_recovery_journal']['path']).read_text().splitlines()]
        events=iter(result['events']);generations=iter(result['trace']['stimuli'][1:])
        samples=iter([{'marker':f,'observation':s} for f,s in zip(result['trace']['frames'],result['samples'])])
        for row in records:
            if row['kind']=='completed':row['value']=result
            elif row['kind']=='recovery-completed':
                row['value']={k:v for k,v in result.items() if k not in ['samples','trace','post_input','new_icon_mapped_files','shell_after','outcome']}
                row['value']['not_run']=['post-recovery-input']
            elif row['kind']=='event':row['value']=next(events,{})
            elif row['kind']=='generation':row['value']=next(generations,{})
            elif row['kind']=='sample':row['value']=next(samples,{})
            elif row['kind']=='identity':
                row['value']={k:result[k] for k in ['version','control','old_icon','old_icon_mapped_files','old_shell','settings_before','held_before']}|{'events':[],'samples':[],'not_run':['post-recovery-input']}
        raw=('\n'.join(json.dumps(r) for r in records)+'\n').encode()
        with patch('record_gnome_icon_recovery.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_three_native_controls(self):self.assertEqual([validate(r,BUILD)['outcome'] for r in REPORTS],['pass','fail','fail'])
    def test_original_lifetime_cannot_be_silently_waived(self):
        with self.assertRaises(ValueError):composition(BY_CONTROL['live'],BUILD,family='GNOME-ICON-RECOVERY-01',outer_outcome=False)
    def test_fake_exit_observer_cannot_waive_initial_retention(self):
        self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='exit-observed').update(observer='candidate-ack'))
    def test_wrong_control(self):self.reject(lambda r,c:c.update(control='no-stop'))
    def test_original_descriptor_already_exited(self):self.reject(lambda r,c:c['held_before'].update(old_live=False))
    def test_shell_descriptor_already_exited(self):self.reject(lambda r,c:c['held_before'].update(shell_live=False))
    def test_stop_wrong_process(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='stop').update(pid=1))
    def test_stop_without_revalidated_handle(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='stop').update(held_live=False))
    def test_missing_actual_stop(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='stop').update(performed=False))
    def test_exit_before_stop(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='exit-observed').update(at_us=1))
    def test_late_exit(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='exit-observed').update(at_us=3000000))
    def test_unreadable_exit_handle(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='exit-observed').update(readable=False))
    def test_old_lifetime_cannot_be_replacement(self):self.reject(lambda r,c:c.update(new_icon=copy.deepcopy(c['old_icon'])))
    def test_foreign_replacement_group(self):self.reject(lambda r,c:c['new_icon'].update(process_group=1))
    def test_foreign_replacement_resource(self):self.reject(lambda r,c:c['new_icon'].update(resource_base=0))
    def test_replacement_readiness_not_observed(self):self.reject(lambda r,c:next(e for e in c['events'] if e['event']=='replacement-ready').update(at_us=next(e for e in c['events'] if e['event']=='replacement-ready')['at_us']+1))
    def test_old_process_resurrection(self):self.reject(lambda r,c:c['samples'][-1].update(old_exited=False))
    def test_replacement_died_during_interval(self):self.reject(lambda r,c:c['samples'][-1].update(new_live=False))
    def test_shell_died_during_icon_fault(self):self.reject(lambda r,c:c['samples'][10].update(shell_live=False))
    def test_shell_resource_changed(self):self.reject(lambda r,c:c['samples'][10]['shell'].update(window=1))
    def test_replacement_missing_from_native_sample(self):self.reject(lambda r,c:c['samples'][-1].update(icon=None))
    def test_background_changed(self):self.reject(lambda r,c:c['samples'][-1].update(background=rgb_record(bytes(128*96*3))))
    def test_native_icons_not_restored(self):self.reject(lambda r,c:c['samples'][-1].update(overlap=rgb_record(bytes(180*220*3))))
    def test_replacement_ack_cannot_replace_live_pixels(self):
        def freeze(r,c):
            pixels=unpack_frame(c['trace']['frames'][0])
            c['trace']['frames']=[pack_frame(pixels,f['start_us'],f['end_us']) for f in c['trace']['frames']]
        self.reject(freeze)
    def test_missing_paired_frame(self):self.reject(lambda r,c:c['samples'].pop())
    def test_capture_duration_limit(self):self.reject(lambda r,c:c['samples'][10].update(end_us=c['trace']['frames'][10]['start_us']+50001))
    def test_generation_six_before_replacement(self):self.reject(lambda r,c:c['trace']['stimuli'][2].update(at_us=1))
    def test_configuration_changed(self):self.reject(lambda r,c:c['settings_after'].update(**{'picture-options':"'zoom'"}))
    def test_original_process_cannot_supply_recovered_input(self):self.reject(lambda r,c:c['post_input'].update(icon_manager=copy.deepcopy(c['old_icon'])))
    def test_input_before_recovery_completed(self):self.reject(lambda r,c:c['post_input']['accessibility_registration'].update(started_ns=c['started_monotonic_ns']))
    def test_missing_required_input(self):self.reject(lambda r,c:c.pop('post_input'))
    def test_unexecuted_input_marked_complete(self):self.reject(lambda r,c:c.update(not_run=[]),control='frozen-surface')
    def test_frozen_control_cannot_omit_the_fault(self):self.reject(lambda r,c:c['events'].pop(0),control='frozen-surface')
    def test_no_stop_cannot_invent_replacement(self):self.reject(lambda r,c:c.update(new_icon=copy.deepcopy(c['old_icon'])),control='no-stop')
    def test_no_stop_requires_actual_live_progress(self):self.reject(lambda r,c:c['trace']['stimuli'][1].update(at_us=1000000),control='no-stop')
    def test_raw_journal_digest(self):self.reject(lambda r,c:r['icon_recovery_journal'].update(sha256='0'*64),synchronize=False)


if __name__=='__main__':unittest.main()
