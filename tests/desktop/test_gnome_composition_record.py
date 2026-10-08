"""Reject altered native composition evidence without changing the fixed pixel oracle."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source/build'))
from record_gnome_composition import validate
from native_x11_host import rgb_record

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORT=json.loads(Path(sys.argv.pop(1)).read_text())


class CompositionEvidence(unittest.TestCase):
    def reject(self, mutate):
        value=copy.deepcopy(REPORT)
        mutate(value, value['observation']['composition'])
        with self.assertRaises(ValueError):validate(value,BUILD)

    def test_native_record(self):
        self.assertEqual(validate(REPORT,BUILD)['outcome'],'pass')

    def test_foreign_icon_pid(self):
        self.reject(lambda r,c:c['icon_manager'].update(pid=1))

    def test_changed_icon_script(self):
        self.reject(lambda r,c:c['icon_manager'].update(arguments=['gjs','/tmp/fake.js']))

    def test_calibration_after_enable(self):
        self.reject(lambda r,c:c.update(scene_enabled_ns=1))

    def test_missing_white_control(self):
        self.reject(lambda r,c:c['calibrations'].pop(1))

    def test_false_calibration_pixels(self):
        self.reject(lambda r,c:c['calibrations'][1]['frames'][0]['pixels'].update(sha256='0'*64))

    def test_invented_mask_count(self):
        self.reject(lambda r,c:c['evaluation'].update(anchor_counts=[1,1,1,1]))

    def test_missing_overlap_sample(self):
        self.reject(lambda r,c:c['overlap_samples'].pop())

    def test_overlapping_capture_times(self):
        self.reject(lambda r,c:c['overlap_samples'][0].update(start_us=0))

    def test_background_change(self):
        self.reject(lambda r,c:c['background_settings_after'].update(**{'primary-color':"'#ffffff'"}))

    def test_moved_fixture(self):
        self.reject(lambda r,c:r['desktop_entries_after'].append('Other Folder'))

    def test_unconfirmed_exit(self):
        self.reject(lambda r,c:r['cleanup'][0].update(exit=None))

    def test_relabelled_negative_control(self):
        self.reject(lambda r,c:c.update(control='above-icons'))

    def test_changed_journal(self):
        self.reject(lambda r,c:r['composition_journal'].update(sha256='0'*64))

    def test_empty_icon_mask_with_valid_pixel_hashes(self):
        value=copy.deepcopy(REPORT)
        c=value['observation']['composition']
        for stage in c['calibrations']:
            for frame in stage['frames']:
                frame['pixels']=rgb_record(bytes(stage['background'])*(180*220))
        for frame in c['baseline']:
            frame['pixels']=rgb_record(bytes((48,72,96))*(180*220))
        with self.assertRaisesRegex(ValueError,'native fixture anchors unavailable'):
            validate(value,BUILD)


if __name__=='__main__':unittest.main()
