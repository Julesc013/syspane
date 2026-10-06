"""Reject consistent false lease evidence against the preserved native fixtures."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_gnome_surface_lease import validate
from gnome_surface_lease import judge
from native_x11_host import rgb_record

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS = [json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(3)]
BY_CONTROL = {r['surface_lease_control']: r for r in REPORTS}


class LeaseEvidence(unittest.TestCase):
    def reject(self, mutate, mode='live'):
        value = copy.deepcopy(BY_CONTROL[mode])
        result = value['observation']['surface_lease']
        mutate(value, result)
        try:
            result['evaluation'] = judge(result, value['observation']['composition'])
            value['outcome'] = result['evaluation']['outcome']
        except (ValueError, KeyError):
            pass
        journals = {}
        for role in ['first', 'second']:
            key = 'lease_' + role + '_journal'
            records = [json.loads(line) for line in Path(value[key]['path']).read_text().splitlines()]
            records[1:] = [c['native'] for c in result['calls'] if c['role'] == role]
            journals[key] = ('\n'.join(json.dumps(r) for r in records) + '\n').encode()
        records = [json.loads(line) for line in Path(value['surface_lease_journal']['path']).read_text().splitlines()]
        calls, samples = iter(result['calls']), iter(result['samples'])
        for row in records:
            kind = row['kind']
            if kind == 'initial':
                row['value'] = {k: result[k] for k in ['version', 'control', 'producers', 'icon_manager', 'unauthorized', 'initial_state', 'started_monotonic_ns']}
            elif kind == 'call':
                row['value'] = next(calls, {})
            elif kind == 'sample':
                row['value'] = next(samples, {})
            elif kind == 'late-state':
                row['value'] = result['after_late']
            elif kind == 'exit':
                row['value'] = result['exit']
            elif kind == 'pending':
                row['value'] = {'at_us': result['reattached_us'], 'state': result['pending_state']}
            elif kind == 'completed':
                row['value'] = {k: v for k, v in result.items() if k != 'samples'}
        journals['surface_lease_journal'] = ('\n'.join(json.dumps(r) for r in records) + '\n').encode()
        with patch('record_gnome_surface_lease.raw_file', side_effect=lambda v, key, *args: journals[key]), self.assertRaises(ValueError):
            validate(value, BUILD)

    def test_native_matrix(self):
        self.assertEqual([validate(r, BUILD)['outcome'] for r in REPORTS], ['pass', 'fail', 'pass'])

    def test_native_journal_hash(self):
        value = copy.deepcopy(BY_CONTROL['live'])
        value['surface_lease_journal']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            validate(value, BUILD)

    def test_wrong_reply_consistent_with_receipt(self):
        def mutate(v, r):
            r['calls'][8]['reply'] = r['calls'][8]['native']['reply'] = 'accepted'
        self.reject(mutate)

    def test_late_heartbeat_cannot_resurrect(self):
        def mutate(v, r):
            r['calls'][11]['reply'] = r['calls'][11]['native']['reply'] = 'accepted'
        self.reject(mutate)

    def test_pending_heartbeat_cannot_relabel_retained_epoch(self):
        self.reject(lambda v, r: r['pending_state']['last'].update(epoch='lease:2'))

    def test_duplicate_cannot_refresh_accepted_time(self):
        def mutate(v, r):
            for key in ['after_late', 'pending_state']:
                r[key]['last']['accepted_us'] = r['calls'][10]['native']['started_ns'] // 1000 + 1
        self.reject(mutate)

    def test_data_cannot_renew_lease(self):
        self.reject(lambda v, r: r['after_late'].update(renewed_us=r['calls'][9]['native']['started_ns'] // 1000 + 1))

    def test_old_pixels_cannot_be_active(self):
        def mutate(v, r):
            for row, check in zip(r['samples'], r['evaluation']['checks']):
                if check['settled'] and check['expected_state'] == 'retained':
                    row['badge'] = rgb_record(bytes([32, 160, 64]) * 16 * 16)
        self.reject(mutate)

    def test_expiry_fault_must_be_visible(self):
        def mutate(v, r):
            live = BY_CONTROL['live']['observation']['surface_lease']
            for row, check in zip(r['samples'], r['evaluation']['checks']):
                if check['settled'] and check['expected_state'] == 'retained':
                    row['badge'] = rgb_record(bytes([208, 144, 32]) * 16 * 16)
                    source = next(s for s, c in zip(live['samples'], live['evaluation']['checks']) if c['settled'] and c['expected_generation'] == 6)
                    for key in ['bytes', 'sha256', 'rgb_zlib_base64']:
                        if key in source['marker']:
                            row['marker'][key] = source['marker'][key]
        # The untouched native timer/control frames must expose the intended fault.
        self.reject(mutate, 'ignore-expiry')


CASES = {
    'wrong_mode': lambda v, r: v['environment']['explicit'].update(SYSPANE_GNOME_SURFACE_LEASE='disconnect'),
    'foreign_native_producer': lambda v, r: r['producers']['first'].update(pid=1),
    'wrong_process_start': lambda v, r: r['producers']['first'].update(start_ticks=0),
    'shared_process_group': lambda v, r: r['producers']['second'].update(process_group=r['producers']['first']['pid']),
    'wrong_peer': lambda v, r: r['calls'][0].update(peer_pid=r['producers']['first']['pid']),
    'foreign_connection': lambda v, r: r['calls'][2]['native'].update(owner=':1.99999'),
    'receipt_before_send': lambda v, r: r['calls'][2]['native'].update(started_ns=r['calls'][2]['started_ns'] - 1),
    'late_call': lambda v, r: r['calls'][6].update(finished_ns=r['calls'][6]['started_ns'] + 50000001),
    'missed_schedule': lambda v, r: r.update(started_monotonic_ns=r['started_monotonic_ns'] - 100000000),
    'unobserved_exit': lambda v, r: r['exit'].update(observer='timeout'),
    'wrong_exit_pid': lambda v, r: r['exit'].update(pid=r['producers']['second']['pid']),
    'false_exit_sample': lambda v, r: r['samples'][0].update(first_exited=True),
    'no_real_exit': lambda v, r: next(c for c in v['cleanup'] if c['process'] == 'lease-first').update(exit=0),
    'replacement_died': lambda v, r: next(c for c in v['cleanup'] if c['process'] == 'lease-second').update(exit=73),
    'producer_survived': lambda v, r: next(c for c in v['cleanup'] if c['process'] == 'lease-second')['members_after_stop'].append({'pid': 1, 'state': 'S'}),
    'observer_admitted': lambda v, r: r.update(unauthorized='accepted'),
    'pending_without_full': lambda v, r: r['pending_state'].update(snapshot_required=False),
    'new_full_old_generation': lambda v, r: r['before_disable']['last'].update(generation=6),
    'expired_still_alive': lambda v, r: r['after_late'].update(alive=True),
    'wrong_icon_owner': lambda v, r: r['icon_manager'].update(pid=1),
    'missing_frames': lambda v, r: r['samples'].clear(),
    'late_capture': lambda v, r: r['samples'][8].update(end_us=r['samples'][8]['marker']['start_us'] + 50001),
    'changed_background': lambda v, r: r['samples'][8].update(background=rgb_record(bytes(128 * 96 * 3))),
    'changed_icons': lambda v, r: r['samples'][8].update(overlap=rgb_record(bytes(180 * 220 * 3))),
    'badge_survives_disable': lambda v, r: r.update(badge_after_disable=rgb_record(bytes([32, 160, 64]) * 16 * 16)),
    'late_disable': lambda v, r: r.update(disable_finished_ns=r['disable_started_ns'] + 50000001),
    'post_marker_missing_stimulus': lambda v, r: r['post']['trace']['stimuli'].pop(),
    'too_short_retained_interval': lambda v, r: r.update(reattached_us=r['exit']['at_us'] + 500000),
    'missing_runtime_mapping': lambda v, r: v['lease_producer_mapped_files']['first'].clear(),
}


def negative_case(mutation):
    def test(self):
        self.reject(mutation)
    return test


for name, mutation in CASES.items():
    setattr(LeaseEvidence, 'test_' + name, negative_case(mutation))


if __name__ == '__main__':
    unittest.main()
