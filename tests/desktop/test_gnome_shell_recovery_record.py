"""Reject inconsistent and semantically false shell recovery evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source/build'))
from record_gnome_shell_recovery import validate
from record_gnome_host import validate_runtime
from gnome_shell_recovery import judge
from native_x11_host import rgb_record
from oracle import pack_frame, unpack_frame

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
CONTROLS={r['shell_recovery_control']:r for r in REPORTS}


class ShellRecoveryEvidence(unittest.TestCase):
    def reject(self,mutate,control='live',sync=True):
        value=copy.deepcopy(CONTROLS[control]);result=value['observation']['shell_recovery'];mutate(value,result)
        if not sync:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        try:result['evaluation']=judge(result,value['observation']['composition'])
        except (ValueError,StopIteration):pass
        records=[json.loads(line) for line in Path(value['shell_recovery_journal']['path']).read_text().splitlines()]
        events=iter(result['events']);samples=iter(result['samples'])
        generations=iter(result.get('post',{}).get('trace',{}).get('stimuli',[])[1:])
        for row in records:
            if row['kind']=='completed':row['value']=result
            elif row['kind']=='sample':row['value']=next(samples,{})
            elif row['kind']=='event':row['value']=next(events,{})
            elif row['kind']=='generation':row['value']=next(generations,{})
            elif row['kind']=='recovery-completed':
                row['value']={k:v for k,v in result.items() if k not in ['samples','post','post_input','new_shell_mapped_files','new_icon_mapped_files','outcome']}
                row['value']['not_run']=['post-recovery-input']
            elif row['kind']=='identity':
                keys=['version','control','old_shell','old_process','old_icon','old_shell_mapped_files','old_icon_mapped_files','settings_before','held_before_ns']
                row['value']={k:result[k] for k in keys}|{'events':[],'samples':[],'not_run':['post-recovery-input']}
        raw=('\n'.join(json.dumps(r) for r in records)+'\n').encode()
        with patch('record_gnome_shell_recovery.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_three_native_controls(self):self.assertEqual([validate(r,BUILD)['outcome'] for r in REPORTS],['pass','fail','fail'])
    def test_default_runtime_cannot_waive_old_shell_exit(self):
        with self.assertRaises(ValueError):validate_runtime(CONTROLS['live'],BUILD,'GNOME-SHELL-RECOVERY-01','GNOME-SHELL-RECOVERY-01-')
    def test_fake_exit_observer(self):self.reject(lambda v,r:r['events'][1].update(observer='candidate-ack'))
    def test_exit_not_readable(self):self.reject(lambda v,r:r['events'][1].update(readable=False))
    def test_exit_before_fault(self):self.reject(lambda v,r:r['events'][1].update(at_us=1))
    def test_late_shell_exit(self):self.reject(lambda v,r:r['events'][1].update(at_us=3000000))
    def test_wrong_fault_pid(self):self.reject(lambda v,r:r['events'][0].update(pid=1))
    def test_unheld_fault(self):self.reject(lambda v,r:r['events'][0].update(held_live=False))
    def test_wrong_fault_resource(self):self.reject(lambda v,r:r['events'][0]['binding'].update(window=1))
    def test_original_process_command(self):self.reject(lambda v,r:r['old_process'].update(arguments=['foreign']))
    def test_original_not_in_own_group(self):self.reject(lambda v,r:r['old_process'].update(process_group=1))
    def test_missing_absence_interval(self):self.reject(lambda v,r:r['events'][2].update(at_us=r['events'][1]['at_us']))
    def test_launch_after_readiness(self):self.reject(lambda v,r:r['events'][3].update(at_us=r['events'][4]['at_us']+1))
    def test_replacement_is_original_lifetime(self):self.reject(lambda v,r:r.update(new_process=copy.deepcopy(r['old_process'])))
    def test_replacement_start_time(self):self.reject(lambda v,r:r['new_process'].update(start_ticks=r['old_process']['start_ticks']))
    def test_replacement_command_changed(self):self.reject(lambda v,r:r['new_process'].update(arguments=['foreign']))
    def test_replacement_foreign_group(self):self.reject(lambda v,r:r['new_process'].update(process_group=1))
    def test_replacement_wrong_native_resource(self):self.reject(lambda v,r:r['new_shell'].update(resource_base=0))
    def test_old_icon_used_as_replacement(self):self.reject(lambda v,r:r.update(new_icon=copy.deepcopy(r['old_icon'])))
    def test_original_icon_exit_not_observed(self):self.reject(lambda v,r:[s.update(old_icon_exited=False) for s in r['samples']])
    def test_original_shell_resurrection(self):self.reject(lambda v,r:r['samples'][-1].update(old_shell_exited=False))
    def test_new_shell_died(self):self.reject(lambda v,r:r['samples'][-1].update(new_shell_live=False))
    def test_new_icon_died(self):self.reject(lambda v,r:r['samples'][-1].update(new_icon_live=False))
    def test_foreign_bus_peer(self):self.reject(lambda v,r:r['events'][4]['peer'].update(pid=1))
    def test_missing_bridge_interface(self):self.reject(lambda v,r:r['events'][4]['peer'].update(interface_xml='<node/>'))
    def test_false_reattach(self):self.reject(lambda v,r:r['events'][5].update(performed=False))
    def test_no_reattach_control_cannot_enable_scene(self):self.reject(lambda v,r:r['events'][5].update(performed=True),control='no-reattach')
    def test_early_settling(self):self.reject(lambda v,r:r['post'].update(started_monotonic_ns=r['started_monotonic_ns']))
    def test_incomplete_post_frames(self):self.reject(lambda v,r:r['post']['trace']['frames'].pop())
    def test_consistent_stale_pixels_cannot_claim_progress(self):
        def freeze(value,result):
            pixels=unpack_frame(result['post']['trace']['frames'][0])
            for row,frame in zip([s for s in result['samples'] if 'post_frame' in s],result['post']['trace']['frames']):
                frame.update(pack_frame(pixels,frame['start_us'],frame['end_us']))
                row['post_frame']=copy.deepcopy(frame)
                row['marker'].update(pack_frame(pixels,row['marker']['start_us'],row['marker']['end_us']))
        self.reject(freeze)
    def test_mutable_cache_exception_cannot_cover_executable(self):
        def change(value,result):
            path=result['old_process']['executable']
            result['old_shell_mapped_files'][path]='0'*64
            value['mapped_files'][path]='0'*64
        self.reject(change)
    def test_raw_and_post_pixels_disagree(self):self.reject(lambda v,r:r['samples'][-1].update(overlap=rgb_record(bytes(180*220*3))))
    def test_post_background_changed(self):self.reject(lambda v,r:r['samples'][-1].update(background=rgb_record(bytes(128*96*3))))
    def test_capture_duration_exceeded(self):self.reject(lambda v,r:r['samples'][5].update(end_us=r['samples'][5]['marker']['start_us']+50001))
    def test_changed_settings(self):self.reject(lambda v,r:r['settings_after'].update(**{'primary-color':"'#000000'"}))
    def test_parent_armed_wrong_pid(self):self.reject(lambda v,r:v['shell_recovery_parent'][0]['message'].update(pid=1))
    def test_parent_launch_before_request(self):self.reject(lambda v,r:v['shell_recovery_parent'][1].update(received_ns=r['started_monotonic_ns']))
    def test_parent_did_not_confirm_signal_exit(self):self.reject(lambda v,r:v['shell_recovery_parent'][1]['response'].update(old_exit=0))
    def test_replacement_not_retained(self):self.reject(lambda v,r:next(s for s in v['cleanup'] if s['process']=='shell-replacement').update(members_before_stop=[]))
    def test_old_owner_cannot_supply_input(self):self.reject(lambda v,r:r['post_input'].update(icon_manager=copy.deepcopy(r['old_icon'])))
    def test_input_precedes_recovery(self):self.reject(lambda v,r:r['post_input']['accessibility_registration'].update(started_ns=r['started_monotonic_ns']))
    def test_missing_required_input(self):self.reject(lambda v,r:r.pop('post_input'))
    def test_failed_control_invents_input(self):self.reject(lambda v,r:r.update(post_input={}),control='no-reattach')
    def test_no_restart_invents_native_shell(self):self.reject(lambda v,r:r.update(new_shell=r['old_shell']),control='no-restart')
    def test_raw_journal_digest(self):self.reject(lambda v,r:v['shell_recovery_journal'].update(sha256='0'*64),sync=False)


if __name__=='__main__':unittest.main()
