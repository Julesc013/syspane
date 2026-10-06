"""Check native choice/lifetime evidence, including consistently rewritten journals."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'build-support'))
import record_gnome_focus_scenarios as recorder
from gnome_focus_scenarios import judge_step
from native_x11_host import rgb_record
from record_gnome_host import digest

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
MODES={r['focus_scenarios_mode']:r for r in REPORTS}


def native_race(result,index,resource=None):
    sample=result['steps'][11]['samples'][index]
    sample['native']=None;sample['memberships']={}
    sample['native_errors']=[{'code':3,'request':20,'resource':resource or result['roles']['modal']['window'],'serial':1}]


class FocusScenarioEvidence(unittest.TestCase):
    def check_mutation(self,mutate,mode='restore',accept=False,sync=True,receipts=False):
        value=copy.deepcopy(MODES[mode]);result=value['observation']['focus_scenarios'];mutate(value,result)
        if not sync:
            with self.assertRaises(ValueError):recorder.validate(value,BUILD)
            return
        for row in result['steps']:
            try:row['evaluation']=judge_step(row,result['roles'],value['observation']['focus_baseline']['icon_manager'])
            except (ValueError,KeyError):pass
        rows=[json.loads(line) for line in Path(value['focus_scenarios_journal']['path']).read_text().splitlines()]
        steps=iter(result['steps']);verdicts=iter(result['steps']);samples=iter([{'step':r['step'],'sample':s} for r in result['steps'] for s in r['samples']])
        keys=iter([{'step':r['step'],**r['keyboard']} for r in result['steps'] if 'keyboard' in r]);identities=iter(result['roles'].values())
        for row in rows:
            kind=row['kind']
            if kind=='completed':row['value']=result
            elif kind=='sample':row['value']=next(samples,{})
            elif kind=='step':row['value']={k:v for k,v in next(steps,{}).items() if k not in ['evaluation','keyboard']}
            elif kind=='verdict':row['value']=next(verdicts,{}).get('evaluation',{})
            elif kind=='keyboard':row['value']=next(keys,{})
            elif kind=='identity':row['value']=next(identities,{})
        raw=('\n'.join(json.dumps(r) for r in rows)+'\n').encode();original=recorder.raw_file
        def file(v,key,*args):
            if key=='focus_scenarios_journal':return raw
            if receipts and key=='focus_control_events':return b''.join((json.dumps(r,separators=(',',':'))+'\n').encode() for r in result['events_after']['events'])
            return original(v,key,*args)
        with patch('record_gnome_focus_scenarios.raw_file',side_effect=file):
            if accept:self.assertEqual(recorder.validate(value,BUILD)['calibration'],'pass')
            else:
                with self.assertRaises(ValueError):recorder.validate(value,BUILD)
    def reject(self,*args,**kwargs):self.check_mutation(*args,**kwargs)
    def test_native_controls(self):
        values=[recorder.validate(v,BUILD) for v in REPORTS]
        self.assertTrue(all(v['calibration']=='pass' for v in values))
        self.assertTrue(all(k['delivered'] for k in values[0]['keyboard']))
        self.assertEqual(values[2]['native_outcome'],'fail')
    def test_intentional_failure_cannot_retain_pass(self):self.reject(lambda v,r:v.update(outcome='pass'),mode='helper-exit')
    def test_wrong_helper_exit(self):self.reject(lambda v,r:next(c for c in v['cleanup'] if c['process']=='focus-controls').update(exit=0),mode='helper-exit')
    def test_failed_startup_invents_marker(self):self.reject(lambda v,r:r.update(final_marker={}),mode='helper-exit')
    def test_failed_startup_invents_window(self):self.reject(lambda v,r:r['roles'].update(alpha={}),mode='helper-exit')
    def test_parent_wrong_reply(self):self.reject(lambda v,r:v['focus_scenarios_parent']['response'].update(focus_scenarios_pid=1))
    def test_parent_reply_before_request(self):self.reject(lambda v,r:v['focus_scenarios_parent'].update(responded_ns=1))
    def test_duplicate_helper_launch(self):self.reject(lambda v,r:v['commands'].append(next(c for c in v['commands'] if c.get('pid')==r['helper_pid'])))
    def test_missing_retained_helper(self):self.reject(lambda v,r:next(c for c in v['cleanup'] if c['process']=='focus-controls').update(members_before_stop=[]))
    def test_surviving_helper(self):self.reject(lambda v,r:next(c for c in v['cleanup'] if c['process']=='focus-controls').update(members_after_stop=[{'pid':1}]))
    def test_foreign_native_pid(self):self.reject(lambda v,r:r['roles']['alpha'].update(pid=1))
    def test_wrong_group(self):self.reject(lambda v,r:r['roles']['beta'].update(process_group=1))
    def test_wrong_resource_base(self):self.reject(lambda v,r:r['roles']['alpha'].update(resource_base=0))
    def test_modal_uses_parent_identity(self):self.reject(lambda v,r:r['roles']['modal'].update(window=r['roles']['beta']['window']))
    def test_modal_state_missing(self):self.reject(lambda v,r:r['roles']['modal'].update(state=[]))
    def test_modal_has_wrong_parent(self):self.reject(lambda v,r:r['roles']['modal'].update(transient_for=[r['roles']['alpha']['window']]))
    def test_modal_native_type_is_normal(self):self.reject(lambda v,r:r['roles']['modal'].update(type=[r['roles']['modal']['normal_type_atom']]))
    def test_wrong_normal_selected(self):self.reject(lambda v,r:r['steps'][2]['samples'][-1]['native'].update(active_window=[r['roles']['alpha']['window']]))
    def test_parent_instead_of_modal(self):self.reject(lambda v,r:r['steps'][9]['samples'][-1]['native'].update(active_window=[r['roles']['beta']['window']]))
    def test_dead_target_focused(self):self.reject(lambda v,r:r['steps'][15]['samples'][-1]['native'].update(active_window=[r['roles']['beta']['window']]))
    def test_cross_workspace_focus(self):self.reject(lambda v,r:r['steps'][18]['samples'][-1]['native'].update(active_window=[r['roles']['alpha']['window']]))
    def test_workspace_action_not_executed(self):self.reject(lambda v,r:r['steps'][18]['samples'][-1].update(workspace=[0]))
    def test_native_membership_changed(self):self.reject(lambda v,r:r['steps'][18]['samples'][-1]['memberships'].update({str(r['roles']['alpha']['window']):[1]}))
    def test_return_repaired_by_click(self):self.reject(lambda v,r:r['steps'][2]['action'].update(kind={'click':'beta'}))
    def test_changed_workspace_settings(self):self.reject(lambda v,r:r['workspace_settings_after'].update({'org.gnome.mutter/dynamic-workspaces':'true'}))
    def test_missing_required_step(self):self.reject(lambda v,r:r['steps'].pop())
    def test_slow_capture(self):self.reject(lambda v,r:r['steps'][2]['samples'][-1].update(end_us=r['steps'][2]['samples'][-1]['start_us']+50001))
    def test_missing_settled_samples(self):self.reject(lambda v,r:r['steps'][2].update(samples=r['steps'][2]['samples'][:3]))
    def test_wrong_marker(self):self.reject(lambda v,r:r['steps'][2]['samples'][-1].update(marker=rgb_record(bytes(128*96*3))))
    def test_wrong_visible_modal_pixels(self):self.reject(lambda v,r:r['steps'][9]['samples'][-1]['witnesses'].update(modal=rgb_record(bytes([176,64,160])*400)))
    def test_owned_closing_race_is_recorded(self):self.check_mutation(lambda v,r:native_race(r,0),accept=True)
    def test_foreign_closing_race_rejected(self):self.reject(lambda v,r:native_race(r,0,1))
    def test_settled_closing_race_rejected(self):self.reject(lambda v,r:native_race(r,-1))
    def test_no_error_record_cannot_hide_native_state(self):self.reject(lambda v,r:r['steps'][11]['samples'][0].update(native=None,native_errors=[]))
    def test_false_key_receipt(self):self.reject(lambda v,r:r['steps'][2]['keyboard'].update(delivered=False))
    def test_consistent_key_reattribution(self):
        def change(v,r):
            timestamp=next(e['monotonic_ns'] for e in r['events_after']['events'] if e['event']=='key')
            snapshots=[r['events_after']]+[s for row in r['steps'] if 'keyboard' in row for s in [row['keyboard']['before'],row['keyboard']['after']]]
            for snapshot in snapshots:
                for event in snapshot['events']:
                    if event['monotonic_ns']==timestamp:event['role']='alpha'
                raw=b''.join((json.dumps(e,separators=(',',':'))+'\n').encode() for e in snapshot['events'])
                snapshot.update(bytes=len(raw),sha256=digest(raw))
        self.check_mutation(change,receipts=True)
    def test_key_predates_focus_interval(self):self.reject(lambda v,r:r['steps'][2]['keyboard'].update(started_ns=1))
    def test_foreign_receipt_inode(self):self.reject(lambda v,r:r['steps'][2]['keyboard']['after'].update(inode=0))
    def test_wrong_focus_sequence(self):self.reject(lambda v,r:[d.update(target_sequence=999) for d in r['final_trace']['records'] if d['event']=='restore'])
    def test_missing_closed_target_clear(self):self.reject(lambda v,r:[d.update(reason='other') for d in r['final_trace']['records'] if d['event']=='clear' and d['reason']=='unmanaging'])
    def test_missing_workspace_invalidation(self):self.reject(lambda v,r:[d.update(reason='other') for d in r['final_trace']['records'] if d['event']=='clear' and d['reason']=='workspace'])
    def test_unsolicited_restore(self):self.reject(lambda v,r:next(d for d in r['final_trace']['records'] if d['event']=='abstain').update(event='restore'))
    def test_observation_control_performed_restore(self):self.reject(lambda v,r:[d.update(performed=True) for d in r['final_trace']['records'] if d['event']=='restore'],mode='observe')
    def test_final_marker_not_executed(self):self.reject(lambda v,r:r['final_marker']['trace'].update(frames=[]))
    def test_journal_digest(self):self.reject(lambda v,r:v['focus_scenarios_journal'].update(sha256='0'*64),sync=False)


if __name__=='__main__':unittest.main()
