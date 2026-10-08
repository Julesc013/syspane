"""Reject plausible but incorrect native icon-input evidence, beyond journal mismatch."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source/build'))
from record_gnome_input import validate

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
BY_CONTROL={r['icon_input_control']:r for r in REPORTS}


class InputEvidence(unittest.TestCase):
    def reject(self,mutate,control='live',synchronize=True):
        value=copy.deepcopy(BY_CONTROL[control]);result=value['observation']['icon_input']
        mutate(value,result)
        if not synchronize:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        # Keep the step/raw-journal copies mutually consistent so semantic checks,
        # rather than an easy report/journal mismatch, must reject these fixtures.
        records=[json.loads(line) for line in Path(value['input_journal']['path']).read_text().splitlines()]
        steps=iter(result['steps']); clips=[r['clipboard'] for r in result['steps'] if r['clipboard']]
        copies=iter(clips);raws=iter(clips)
        for row in records:
            if row['kind']=='completed':row['value']=result
            elif row['kind']=='step':row['value']=next(steps,{'step':'missing'})
            elif row['kind']=='clipboard':row['value']=next(copies,{})
            elif row['kind']=='clipboard-raw':row['value']={k:v for k,v in next(raws,{}).items() if k!='names'}
        raw=('\n'.join(json.dumps(r) for r in records)+'\n').encode()
        with patch('record_gnome_input.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_three_native_controls(self):
        self.assertEqual([validate(r,BUILD)['outcome'] for r in REPORTS],['pass','fail','fail'])

    def test_wrong_icon_coordinate(self):
        self.reject(lambda r,c:c.update(icon_center=[700,550]))

    def test_wrong_clipboard_file(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard'].update(raw_utf8='copy\nfile:///tmp/other'))

    def test_cut_is_not_copy(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard'].update(raw_utf8=c['steps'][1]['clipboard']['raw_utf8'].replace('copy','cut',1)))

    def test_clear_requires_fresh_native_reply(self):
        self.reject(lambda r,c:c['steps'][0]['clipboard'].update(owner_changed=False))

    def test_stale_owner(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard'].update(owner=c['steps'][1]['clipboard']['requestor']))

    def test_foreign_clipboard_pid(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard']['owner_binding'].update(pid=1))

    def test_wrong_clipboard_target(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard'].update(target_name='text/plain'))

    def test_late_clipboard_reply(self):
        self.reject(lambda r,c:c['steps'][1]['clipboard'].update(finished_ns=c['steps'][1]['clipboard']['owner_observed_ns']+500000001))

    def test_accessibility_foreign_pid(self):
        self.reject(lambda r,c:c['steps'][0]['tree'][0].update(native_bus_pid=1))

    def test_accessibility_foreign_bus(self):
        self.reject(lambda r,c:c['steps'][0]['tree'][0].update(bus_name=':999.1'))

    def test_hidden_menu_does_not_pass(self):
        self.reject(lambda r,c:[row.update(showing=False) for row in c['steps'][4]['tree'] if row['name']=='Open'])

    def test_menu_must_dismiss(self):
        self.reject(lambda r,c:c['steps'][5].update(tree=copy.deepcopy(c['steps'][4]['tree'])))

    def test_selection_requires_native_focus(self):
        self.reject(lambda r,c:c['steps'][1]['native'].update(active_window=[]))

    def test_wrong_folder_executable(self):
        self.reject(lambda r,c:c['folder'].update(executable='/usr/bin/false'))

    def test_unretained_folder_group(self):
        self.reject(lambda r,c:c['folder'].update(process_group=1))

    def test_folder_title_without_contents(self):
        self.reject(lambda r,c:c['steps'][6]['clipboard'].update(raw_utf8='file:///tmp/Sentinel.txt\0'))

    def test_folder_native_client_pid(self):
        self.reject(lambda r,c:next(x for x in c['steps'][6]['native']['clients'] if x['window']==c['folder']['window']).update(pid=[1]))

    def test_folder_must_close(self):
        self.reject(lambda r,c:c['steps'][-1]['native']['client_order_bottom_to_top'].append(c['folder']['window']))

    def test_final_marker_claim_cannot_replace_frames(self):
        self.reject(lambda r,c:c['final_composition']['marker']['trace']['frames'].clear())

    def test_final_composition_must_follow_input(self):
        self.reject(lambda r,c:c['final_composition']['marker'].update(started_monotonic_ns=1))

    def test_background_must_remain_unchanged(self):
        self.reject(lambda r,c:c['background_after'].update(**{'primary-color':"'#000000'"}))

    def test_negative_control_cannot_be_relabelled(self):
        self.reject(lambda r,c:c['steps'][-1].update(outcome='pass'),control='block-pointer')

    def test_missing_native_step(self):
        self.reject(lambda r,c:c['steps'].pop())

    def test_registry_owner(self):
        self.reject(lambda r,c:r.update(registry_pid=1))

    def test_registry_cleanup(self):
        self.reject(lambda r,c:next(x for x in r['cleanup'] if x['process']=='registry').update(members_after_stop=[{'pid':1,'state':'S'}]))

    def test_raw_journal_identity(self):
        self.reject(lambda r,c:r['input_journal'].update(sha256='0'*64),synchronize=False)


if __name__=='__main__':unittest.main()
