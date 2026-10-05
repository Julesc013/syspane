"""Adversarial evidence checks against an actual owned X11 experiment report."""
import copy
import base64
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_x11_host import validate, pixels

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORT = json.loads(Path(sys.argv.pop(1)).read_text(encoding='utf-8'))


def rebind_journal(row):
    """Keep journal stages consistent so tampering reaches semantic checks."""
    journal = row['input_journal']
    entries = [json.loads(line) for line in journal['raw_utf8'].splitlines()]
    stages = iter(row['input_observation']['steps'])
    entries = [{**e, 'value': next(stages)} if e['kind'] == 'check-finish' else e for e in entries]
    raw = ''.join(json.dumps(e, separators=(',', ':')) + '\n' for e in entries)
    journal.update(raw_utf8=raw, bytes=len(raw.encode('utf-8')), sha256=hashlib.sha256(raw.encode('utf-8')).hexdigest())


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
        if value['wallpaper_mode'] == 'color':
            value['cases'][0]['wallpaper_preservation_scope'] = 'Configured image file and observed wallpaper region'
        else:
            image = value['cases'][0]['wallpaper_region']
            rgb = bytes((48, 72, 96)) * 128 * 96
            image.update(sha256=hashlib.sha256(rgb).hexdigest(), rgb_zlib_base64=base64.b64encode(zlib.compress(rgb)).decode('ascii'))
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    def test_unexecuted_input_claim(self):
        value = copy.deepcopy(REPORT)
        value['cases'][0]['icon_input'] = 'pass'
        with self.assertRaises(ValueError):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_clipboard_names_require_matching_uri_bytes(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        row['input_observation']['steps'][1]['clipboard']['names'] = ['Second Folder']
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'names differ'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_uri_must_name_exact_fixture(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        clip = row['input_observation']['steps'][1]['clipboard']
        clip['uris'] = ['file:///unexpected/Probe%20Folder']
        clip['raw_utf8'] = clip['uris'][0] + '\0'
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'outside exact fixture'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_stale_clipboard_is_not_a_selection(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        row['input_observation']['steps'][1]['clipboard']['owner_changed'] = False
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'empty clipboard'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_hidden_menu_does_not_pass(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        for node in row['input_observation']['steps'][4]['tree']:
            node['showing'] = False
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'input verdict'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_folder_title_alone_does_not_pass(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        row['input_observation']['steps'][5]['clipboard'] = None
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'input verdict'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_candidate_focus_invalidates_input(self):
        value = copy.deepcopy(REPORT)
        row = value['cases'][2]
        state = row['input_observation']['steps'][1]['structure']
        state['active_window'] = [state['candidate']]
        rebind_journal(row)
        with self.assertRaisesRegex(ValueError, 'focus claim'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_journal_corruption_rejected(self):
        value = copy.deepcopy(REPORT)
        value['cases'][2]['input_journal']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'journal identity'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_fixture_mutation_rejected(self):
        value = copy.deepcopy(REPORT)
        value['cases'][2]['fixture_after']['Probe Folder/Sentinel.txt']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'fixture was changed'):
            validate(value, BUILD, True)

    @unittest.skipUnless(REPORT.get('icon_input_requested'), 'historical report has no native input')
    def test_registry_identity_rejected(self):
        value = copy.deepcopy(REPORT)
        value['cases'][2]['registry_identity_confirmed'] += 1
        with self.assertRaisesRegex(ValueError, 'registry identity'):
            validate(value, BUILD, True)


if __name__ == '__main__':
    unittest.main()
