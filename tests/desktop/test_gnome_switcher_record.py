"""Reject incomplete or false native switcher claims even with consistent journals."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_switcher import validate
from gnome_switcher import judge
from native_x11_host import rgb_record

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
BY_CONTROL={r['switcher_control']:r for r in REPORTS}


class SwitcherEvidence(unittest.TestCase):
    def reject(self,mutate,control='live',synchronize=True):
        value=copy.deepcopy(BY_CONTROL[control]);result=value['observation']['switcher']
        mutate(value,result)
        if not synchronize:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        try:
            result['evaluation']=judge(result,value['observation']['composition'])
            result['outcome']=value['outcome']=result['evaluation']['outcome']
        except ValueError:pass
        records=[json.loads(line) for line in Path(value['switcher_journal']['path']).read_text().splitlines()]
        rows={r['step']:r for r in result['observations']};actions={r['step']:r for r in result['actions']}
        samples=iter([{'marker':f,'observation':r} for f,r in zip(result.get('final_marker',{}).get('trace',{}).get('frames',[]),result.get('final_samples',[]))])
        for record in records:
            kind=record['kind']
            if kind=='completed':record['value']=result
            elif kind in ['accepted-observation','rejected-observation']:
                record['value']=rows.get(record['value']['step'],{})
            elif kind=='observation':record['value']={k:v for k,v in rows.get(record['value']['step'],{}).items() if k!='trigger_ns'}
            elif kind=='action':record['value']=actions.get(record['value']['step'],{})
            elif kind=='final-sample':record['value']=next(samples,{})
        raw=('\n'.join(json.dumps(r) for r in records)+'\n').encode()
        with patch('record_gnome_switcher.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_native_three_controls(self):
        self.assertEqual([validate(r,BUILD)['outcome'] for r in REPORTS],['pass','fail','fail'])

    def test_fixture_digest(self):self.reject(lambda r,c:c.update(fixture_sha256='0'*64))
    def test_wrong_control(self):self.reject(lambda r,c:c.update(control='ordinary-window'))
    def test_foreign_accessibility_bus(self):self.reject(lambda r,c:r['environment']['explicit'].update(AT_SPI_BUS_ADDRESS='unix:path=/tmp/foreign'))
    def test_missing_registry_exit(self):self.reject(lambda r,c:r['cleanup'].__setitem__(next(n for n,v in enumerate(r['cleanup']) if v['process']=='registry'),{'process':'registry','pid':0,'exit':0,'members_after_stop':[]}))
    def test_changed_favorites(self):self.reject(lambda r,c:c['settings_after'].update(**{'favorite-apps':"['unexpected.desktop']"}))
    def test_changed_background(self):self.reject(lambda r,c:c['background_after'].update(**{'picture-uri':"'file:///other'"}))
    def test_foreign_native_owner(self):self.reject(lambda r,c:c['applications']['alpha'].update(resource_base=0))
    def test_missing_retained_application(self):self.reject(lambda r,c:c['applications_after'].pop('alpha'))
    def test_incorrect_geometry(self):self.reject(lambda r,c:c['applications']['alpha'].update(geometry=[0,0,200,120]))
    def test_modified_launcher(self):self.reject(lambda r,c:r['switcher_launchers']['alpha'].update(desktop='[Desktop Entry]\n'))
    def test_foreign_shell_tree_pid(self):self.reject(lambda r,c:c['observations'][1]['tree']['rows'][-1].update(native_bus_pid=1))
    def test_duplicate_tree_node(self):self.reject(lambda r,c:c['observations'][1]['tree']['rows'].append(copy.deepcopy(c['observations'][1]['tree']['rows'][-1])))
    def test_missing_tree_child(self):self.reject(lambda r,c:c['observations'][1]['tree']['rows'].pop())
    def test_false_showing_claim(self):self.reject(lambda r,c:c['observations'][1]['tree']['rows'][-1].update(showing=False))
    def test_hide_visible_subtree(self):
        self.reject(lambda r,c:next(n for n in c['observations'][1]['tree']['rows'] if n['showing'] and n['children_count']).update(pruned_hidden=True))
    def test_missing_popup_does_not_pass_live(self):
        self.reject(lambda r,c:c['observations'][1].update(tree=copy.deepcopy(c['observations'][0]['tree'])))
    def test_names_without_rendered_icons(self):self.reject(lambda r,c:c['observations'][1].update(pixels=rgb_record(bytes(800*600*3))))
    def test_dash_names_without_rendered_icons(self):self.reject(lambda r,c:c['observations'][5].update(pixels=rgb_record(bytes(800*600*3))))
    def test_unexpected_application_name(self):
        self.reject(lambda r,c:next(n for n in c['observations'][1]['tree']['rows'] if n['name']=='SysPane Lab Beta').update(name='Unexpected application'))
    def test_fault_entry_cannot_be_relabelled_as_control(self):
        self.reject(lambda r,c:next(n for n in c['observations'][1]['tree']['rows'] if n['name']=='SysPane Surface Fault').update(name='SysPane Lab Beta'),control='ordinary-window')
    def test_native_switch_did_not_focus_beta(self):self.reject(lambda r,c:c['observations'][3]['native'].update(active_window=[c['applications']['alpha']['window']]))
    def test_unexpected_normal_client(self):
        self.reject(lambda r,c:c['observations'][0]['native']['clients'].append({'window':1,'type':[c['applications']['alpha']['normal_type_atom']]}))
    def test_late_transition(self):self.reject(lambda r,c:c['observations'][1].update(finished_ns=c['actions'][1]['issued_ns']+3000000001))
    def test_clicks_must_belong_to_declared_action(self):self.reject(lambda r,c:c['actions'][0].update(started_ns=c['actions'][0]['issued_ns']))
    def test_keys_must_belong_to_declared_action(self):self.reject(lambda r,c:c['actions'][1].update(started_ns=c['actions'][1]['issued_ns']))
    def test_missing_step(self):self.reject(lambda r,c:c['observations'].pop())
    def test_false_unexecuted_steps(self):self.reject(lambda r,c:c.update(not_run=[]),control='no-switcher')
    def test_omitted_action_control_did_issue_chord(self):self.reject(lambda r,c:c['actions'][1].update(performed=True),control='no-switcher')
    def test_missing_final_composition(self):self.reject(lambda r,c:c['final_samples'].clear())
    def test_focus_stolen_after_restoration(self):self.reject(lambda r,c:c['final_samples'][10]['native'].update(active_window=[0]))
    def test_final_observation_budget(self):self.reject(lambda r,c:c['final_samples'][10].update(end_us=c['final_marker']['trace']['frames'][10]['start_us']+50001))
    def test_late_final_generation(self):self.reject(lambda r,c:c['final_marker']['trace']['stimuli'][1].update(at_us=900001))
    def test_journal_digest(self):self.reject(lambda r,c:r['switcher_journal'].update(sha256='0'*64),synchronize=False)


if __name__=='__main__':unittest.main()
