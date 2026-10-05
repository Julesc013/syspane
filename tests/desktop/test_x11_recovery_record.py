"""Reject altered native recovery claims even with a consistent replacement journal."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_x11_host import validate

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORT = json.loads(Path(sys.argv.pop(1)).read_text(encoding='utf-8'))


class RecoveryEvidenceChecks(unittest.TestCase):
    def altered(self, mutate, expected):
        value = copy.deepcopy(REPORT)
        row = value['cases'][0]
        mutate(row)
        observation = row['recovery_observation']
        entries = [json.loads(line) for line in row['recovery_journal']['raw_utf8'].splitlines()]
        iterators = {kind: iter(observation[key]) for kind, key in [('frame', 'frames'), ('sample', 'samples'), ('event', 'events')]}
        for entry in entries:
            if entry['kind'] in iterators:
                entry['value'] = next(iterators[entry['kind']])
            elif entry['kind'] == 'result':
                entry['value'] = {key: observation[key] for key in entry['value']}
            elif entry['kind'] == 'identity':
                entry['value'] = {key: observation[key] for key in entry['value']}
        raw = ''.join(json.dumps(entry, separators=(',', ':')) + '\n' for entry in entries)
        with tempfile.TemporaryDirectory(prefix='recovery-evidence-check-', dir=BUILD) as directory:
            path = Path(directory) / 'recovery.jsonl'
            path.write_text(raw, encoding='utf-8', newline='\n')
            row['recovery_journal'] = {'path': path.relative_to(BUILD).as_posix(), 'raw_utf8': raw,
                                       'bytes': len(raw.encode('utf-8')), 'sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest()}
            with self.assertRaisesRegex(ValueError, expected):
                validate(value, BUILD, True)

    def test_real_report(self):
        validate(REPORT, BUILD, True)

    def test_visibility_cannot_follow_manager_recovery(self):
        self.altered(lambda row: row['recovery_observation']['outcomes'].update(surface_recovery='pass'), 'outcomes do not reproduce')

    def test_parent_exit_claim_cannot_replace_pidfd(self):
        self.altered(lambda row: row['recovery_observation']['events'][2].update(observer='parent_claim'), 'independent exit')

    def test_new_supporting_window_needs_correct_owner(self):
        self.altered(lambda row: row['recovery_observation']['events'][5].update(pid=[123456789]), 'replacement native identity')

    def test_same_window_id_can_never_prove_same_process(self):
        def mutate(row):
            old = row['recovery_observation']['old_manager']['pid'][0]
            row['recovery_observation']['events'][4]['pid'] = old
        self.altered(mutate, 'independent exit')

    def test_candidate_buffer_cannot_replace_root_capture(self):
        self.altered(lambda row: row['recovery_observation']['frames'][0].update(origin='candidate_buffer'), 'frame time/origin')

    def test_coverage_claim_requires_observed_timing(self):
        self.altered(lambda row: row['recovery_observation'].update(maximum_gap_us=0), 'outcomes do not reproduce')

    def test_wallpaper_claim_requires_pixels(self):
        self.altered(lambda row: row['recovery_observation']['samples'][0].update(wallpaper_unchanged=False), 'wallpaper pixel claim')

    def test_client_mask_must_bind_supporting_resource(self):
        self.altered(lambda row: row['recovery_observation']['old_manager'].update(resource_base=12345), 'resource owner binding')


if __name__ == '__main__':
    unittest.main()
