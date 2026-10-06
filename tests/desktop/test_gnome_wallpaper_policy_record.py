"""Reject consistent false policy evidence using actual native calibration records."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_gnome_wallpaper_policy import validate
from gnome_wallpaper_policy import judge
from native_x11_host import rgb_record

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS = [json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
BY_CONTROL = {r['wallpaper_policy_control']: r for r in REPORTS}


class PolicyEvidence(unittest.TestCase):
    def reject(self, mutate, mode='locked'):
        value = copy.deepcopy(BY_CONTROL[mode])
        result = value['observation']['wallpaper_policy']
        mutate(value, result)
        try:
            result['evaluation'] = judge(result, value['observation']['composition'])
            value['outcome'] = result['evaluation']['outcome']
        except (ValueError, KeyError):
            pass
        records = [json.loads(line) for line in Path(value['wallpaper_policy_journal']['path']).read_text().splitlines()]
        samples = iter([{'marker': f, 'observation': r} for f, r in zip(result['marker']['trace']['frames'], result['samples'])])
        faults = iter(result['faults'])
        for row in records:
            if row['kind'] == 'initial':
                row['value'] = {k: result[k] for k in ['version', 'control', 'icon_manager', 'files_before', 'settings_before', 'writable_before']}
            elif row['kind'] == 'writes':
                row['value'] = {k: result[k] for k in ['writer_get_before', 'writer_set', 'writer_get_after', 'write', 'settings_after_write']}
            elif row['kind'] == 'sample':
                row['value'] = next(samples, {})
            elif row['kind'] == 'fault':
                row['value'] = next(faults, {})
            elif row['kind'] == 'completed':
                row['value'] = {k: v for k, v in result.items() if k != 'samples'}
        raw = ('\n'.join(json.dumps(r) for r in records) + '\n').encode()
        with patch('record_gnome_wallpaper_policy.raw_file', return_value=raw), self.assertRaises(ValueError):
            validate(value, BUILD)

    def test_native_matrix(self):
        self.assertEqual([validate(r, BUILD)['outcome'] for r in REPORTS], ['pass', 'fail', 'fail'])

    def test_keyfile_cannot_qualify_native_dconf(self):
        self.reject(lambda v, r: v['environment']['explicit'].update(GSETTINGS_BACKEND='keyfile'))

    def test_foreign_profile(self):
        self.reject(lambda v, r: v['environment']['explicit'].update(DCONF_PROFILE='/etc/dconf/profile/user'))

    def test_wrong_runtime(self):
        self.reject(lambda v, r: v['wallpaper_policy_setup'].update(lock_sha256='0' * 64))

    def test_compile_failure(self):
        self.reject(lambda v, r: v['wallpaper_policy_setup']['commands'][0].update(exit=1))

    def test_foreign_compile_target(self):
        self.reject(lambda v, r: v['wallpaper_policy_setup']['commands'][0]['command'].__setitem__(2, '/tmp/foreign'))

    def test_wrong_native_writer(self):
        self.reject(lambda v, r: v.update(wallpaper_policy_writer_pid=1))

    def test_writer_exit(self):
        self.reject(lambda v, r: next(c for c in v['cleanup'] if c['process'] == 'dconf-writer').update(exit=7))

    def test_writer_survivor(self):
        self.reject(lambda v, r: next(c for c in v['cleanup'] if c['process'] == 'dconf-writer')['members_after_stop'].append({'pid': 1, 'state': 'S'}))

    def test_unavailable_writer_is_not_policy(self):
        self.reject(lambda v, r: r['writer_set'].update(exit=1, stderr='No writer\n'))

    def test_writer_readback_must_change(self):
        self.reject(lambda v, r: r['writer_get_after'].update(stdout=r['writer_get_before']['stdout']))

    def test_write_denial_must_be_native_policy_reason(self):
        self.reject(lambda v, r: r['write'].update(stderr='Failed to connect\n'))

    def test_wrong_write_target(self):
        self.reject(lambda v, r: r['write']['command'].__setitem__(3, 'picture-uri-dark'))

    def test_write_must_precede_interval(self):
        self.reject(lambda v, r: r['write'].update(started_ns=r['marker']['started_monotonic_ns'] + 1, finished_ns=r['marker']['started_monotonic_ns'] + 2))

    def test_no_perpetual_command(self):
        self.reject(lambda v, r: r['write'].update(finished_ns=r['write']['started_ns'] + 2000000001))

    def test_missing_locked_key(self):
        self.reject(lambda v, r: r['writable_after'].pop('picture-uri-dark'))

    def test_lost_lock(self):
        self.reject(lambda v, r: r['writable_after']['picture-options'].update(stdout='true\n'))

    def test_unlocked_control_cannot_report_denial(self):
        self.reject(lambda v, r: r['write'].update(exit=1, stderr='The key is not writable\n'), 'unlocked')

    def test_native_stdout_must_match_values(self):
        self.reject(lambda v, r: r['settings_after']['values'].update(**{'picture-uri': "'wrong'"}))

    def test_omit_nonvisible_key_consistently(self):
        def mutate(v, r):
            for phase in ['settings_before', 'settings_after_write', 'settings_after']:
                r[phase]['values'].pop('picture-opacity')
                r[phase]['stdout'] = ''.join(line for line in r[phase]['stdout'].splitlines(True) if ' picture-opacity ' not in line)
        self.reject(mutate)

    def test_foreign_owner_consistently(self):
        def mutate(v, r):
            for files in [r['files_before'], r['files_after'], *[s['files'] for s in r['samples']]]:
                for side in ['path', 'held']:
                    files['policy'][side]['uid'] = 0
        self.reject(mutate)

    def test_mutable_policy_consistently(self):
        def mutate(v, r):
            for files in [r['files_before'], r['files_after'], *[s['files'] for s in r['samples']]]:
                for side in ['path', 'held']:
                    files['policy'][side]['mode'] = 0o644
        self.reject(mutate)

    def test_equal_hash_does_not_hide_inode_change(self):
        self.reject(lambda v, r: r['samples'][8]['files']['policy']['path'].update(inode=99999999))

    def test_path_does_not_replace_held_identity(self):
        self.reject(lambda v, r: r['samples'][8]['files']['policy']['held'].update(links=0))

    def test_wrong_policy_bytes(self):
        self.reject(lambda v, r: r['samples'][8]['files']['policy']['path'].update(sha256='0' * 64))

    def test_missing_capture(self):
        self.reject(lambda v, r: r['samples'].clear())

    def test_background_corruption(self):
        self.reject(lambda v, r: r['samples'][8].update(background=rgb_record(bytes(128 * 96 * 3))))

    def test_icon_corruption(self):
        self.reject(lambda v, r: r['samples'][8].update(overlap=rgb_record(bytes(180 * 220 * 3))))

    def test_late_capture(self):
        self.reject(lambda v, r: r['samples'][8].update(end_us=r['samples'][8]['start_us'] + 50001))

    def test_late_generation(self):
        self.reject(lambda v, r: r['marker']['trace']['stimuli'][1].update(at_us=900000))

    def test_missing_replacement(self):
        self.reject(lambda v, r: r['faults'].clear(), 'replace-policy')

    def test_late_replacement(self):
        self.reject(lambda v, r: r['faults'][0].update(start_us=1100000, end_us=1100100), 'replace-policy')

    def test_replacement_must_unlink_held_original(self):
        def mutate(v, r):
            for files in [r['files_after'], *[s['files'] for s in r['samples']]]:
                files['policy']['held']['links'] = 1
        self.reject(mutate, 'replace-policy')

    def test_replacement_cannot_change_content(self):
        self.reject(lambda v, r: r['files_after']['policy']['path'].update(sha256='0' * 64), 'replace-policy')

    def test_foreign_icon_owner(self):
        self.reject(lambda v, r: r['icon_manager'].update(pid=1))


if __name__ == '__main__':
    unittest.main()
