"""Reject false wallpaper preservation even when report and raw-journal claims agree."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_wallpaper import validate
from gnome_wallpaper import judge,parse_settings,crop,FIXTURE
from native_x11_host import rgb_record

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(4)]
BY_CONTROL={r['wallpaper_control']:r for r in REPORTS}


def remove_key(record,key):
    record['stdout']='\n'.join(line for line in record['stdout'].splitlines() if line.split(' ',2)[1]!=key)+'\n'
    record['values']=parse_settings(record['stdout'])


class WallpaperEvidence(unittest.TestCase):
    def reject(self,mutate,control='live',synchronize=True):
        value=copy.deepcopy(BY_CONTROL[control]);result=value['observation']['wallpaper']
        mutate(value,result)
        if not synchronize:
            with self.assertRaises(ValueError):validate(value,BUILD)
            return
        # Mutated evidence may honestly claim its recomputed verdict. The control
        # contract and native meaning must still reject an invalid qualification.
        try:
            result['evaluation']=judge(result,value['observation']['composition'])
            value['outcome']=result['evaluation']['outcome']
        except ValueError:
            pass
        records=[json.loads(line) for line in Path(value['wallpaper_journal']['path']).read_text().splitlines()]
        bases=iter(result['baseline']);faults=iter(result['faults'])
        samples=iter([{'marker':f,'observation':r} for f,r in zip(result['marker']['trace']['frames'],result['samples'])])
        for row in records:
            if row['kind']=='completed':row['value']={k:v for k,v in result.items() if k not in ['samples','baseline']}
            elif row['kind']=='baseline':row['value']=next(bases,{})
            elif row['kind']=='sample':row['value']=next(samples,{})
            elif row['kind']=='fault':row['value']=next(faults,{})
            elif row['kind']=='scene-enabled':row['value']={'at_ns':result['scene_enabled_ns']}
        raw=('\n'.join(json.dumps(row) for row in records)+'\n').encode()
        with patch('record_gnome_wallpaper.raw_file',return_value=raw),self.assertRaises(ValueError):validate(value,BUILD)

    def test_four_native_controls(self):
        self.assertEqual([validate(r,BUILD)['outcome'] for r in REPORTS],['pass','fail','fail','fail'])

    def test_foreign_file_path(self):
        self.reject(lambda r,c:c.update(original_path='/tmp/foreign.png'))

    def test_wrong_native_uid(self):
        self.reject(lambda r,c:c['file_before']['path'].update(uid=0))

    def test_wrong_fixture_identity(self):
        self.reject(lambda r,c:c.update(fixture_sha256='0'*64))

    def test_writable_original(self):
        self.reject(lambda r,c:c['file_before']['path'].update(mode=0o644))

    def test_missing_image_baseline(self):
        self.reject(lambda r,c:c['baseline'].pop())

    def test_unspaced_image_baseline(self):
        self.reject(lambda r,c:c['baseline'][1].update(started_ns=c['baseline'][0]['finished_ns']))

    def test_baseline_wrong_image(self):
        self.reject(lambda r,c:c['baseline'][1]['witnesses'].__setitem__(0,rgb_record(bytes(128*96*3))))

    def test_pixels_cannot_stand_in_for_file_identity(self):
        self.reject(lambda r,c:c['samples'][10]['files']['path'].update(inode=c['samples'][10]['files']['path']['inode']+1))

    def test_matching_inode_cannot_stand_in_for_bytes(self):
        self.reject(lambda r,c:c['samples'][10]['files']['path'].update(sha256='0'*64))

    def test_path_cannot_stand_in_for_held_original(self):
        self.reject(lambda r,c:c['samples'][10]['files']['held'].update(links=0))

    def test_settings_claim_must_match_stdout(self):
        self.reject(lambda r,c:c['samples'][10]['settings']['values'].update(**{'picture-uri':"'file:///tmp/wrong'"}))

    def test_omitting_nonvisible_settings_everywhere(self):
        def change(r,c):
            for record in [c['settings_before'],c['settings_after']]+[b['settings'] for b in c['baseline']]+[s['settings'] for s in c['samples']]:remove_key(record,'picture-opacity')
        self.reject(change)

    def test_wrong_pixels_with_correct_file_settings(self):
        self.reject(lambda r,c:c['samples'][10]['witnesses'].__setitem__(0,rgb_record(bytes(128*96*3))))

    def test_missing_second_witness(self):
        self.reject(lambda r,c:c['samples'][10]['witnesses'].pop())

    def test_missing_marker_captures(self):
        self.reject(lambda r,c:c['marker']['trace']['frames'].clear())

    def test_late_generation_stimulus(self):
        self.reject(lambda r,c:c['marker']['trace']['stimuli'][1].update(at_us=900001))

    def test_observation_budget(self):
        self.reject(lambda r,c:c['samples'][10].update(end_us=c['marker']['trace']['frames'][10]['start_us']+50001))

    def test_missing_fault(self):
        self.reject(lambda r,c:c['faults'].clear(),control='redirect-setting')

    def test_late_fault(self):
        self.reject(lambda r,c:c['faults'][0].update(start_us=1100000,end_us=1100001),control='cover-wallpaper')

    def test_cover_cannot_be_an_unrelated_pixel_failure(self):
        self.reject(lambda r,c:c['samples'][-1]['witnesses'].__setitem__(0,rgb_record(bytes(128*96*3))),control='cover-wallpaper')

    def test_fault_must_persist_after_deadline(self):
        self.reject(lambda r,c:c['samples'][-1]['witnesses'].__setitem__(0,rgb_record(crop(FIXTURE['witnesses'][0]))),control='cover-wallpaper')

    def test_unrelated_file_failure_does_not_calibrate_cover(self):
        self.reject(lambda r,c:c['samples'][-1]['files']['path'].update(sha256='0'*64),control='cover-wallpaper')

    def test_replacement_must_preserve_held_original_bytes(self):
        self.reject(lambda r,c:c['samples'][-1]['files']['held'].update(sha256='0'*64),control='replace-file')

    def test_final_settings_cannot_silently_repair_fault(self):
        self.reject(lambda r,c:c.update(settings_after=copy.deepcopy(c['settings_before'])),control='redirect-setting')

    def test_artifact_digest(self):
        self.reject(lambda r,c:r['wallpaper_artifacts']['wallpaper.png'].update(sha256='0'*64))

    def test_raw_journal_digest(self):
        self.reject(lambda r,c:r['wallpaper_journal'].update(sha256='0'*64),synchronize=False)


if __name__=='__main__':unittest.main()
