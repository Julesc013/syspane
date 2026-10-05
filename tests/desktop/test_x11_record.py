"""Adversarial evidence checks against an actual owned X11 experiment report."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_x11_host import validate

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORT = json.loads(Path(sys.argv.pop(1)).read_text(encoding='utf-8'))


class EvidenceChecks(unittest.TestCase):
    def test_recorded_observations(self):
        validate(REPORT, BUILD, True)

    def test_corrupt_pixel_bytes(self):
        value = copy.deepcopy(REPORT)
        value['cases'][0]['trace']['frames'][0]['rgb_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    def test_false_temporal_pass(self):
        value = copy.deepcopy(REPORT)
        value['cases'][0]['observation']['outcome'] = 'pass'
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    def test_false_placement_pass(self):
        value = copy.deepcopy(REPORT)
        value['cases'][1]['placement'] = 'pass'
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    def test_promoted_image_wallpaper(self):
        value = copy.deepcopy(REPORT)
        value['cases'][0]['wallpaper_preservation_scope'] = 'Configured image file and observed wallpaper region'
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    def test_unexecuted_input_claim(self):
        value = copy.deepcopy(REPORT)
        value['cases'][0]['icon_input'] = 'pass'
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)


if __name__ == '__main__':
    unittest.main()
