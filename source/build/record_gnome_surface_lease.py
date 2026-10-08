"""Recompute native surface lease outcomes from peer lifetimes, journals and pixels."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from record_gnome_host import ROOT, digest
from record_gnome_composition import validate as composition
from record_gnome_focus import raw_file
from gnome_surface_lease import CONTROLS, judge


def validate(value, build):
    if composition(value, build, family='GNOME-SURFACE-LEASE-01', outer_outcome=False)['outcome'] != 'pass':
        raise ValueError('live lease composition prerequisite')
    result = value['observation']['surface_lease']
    mode = result['control']
    workspace = Path(value['workspace'])
    env = value['environment']['explicit']
    if result['version'] != '0.1.0' or mode not in CONTROLS or value['surface_lease_control'] != mode or env.get('SYSPANE_GNOME_SURFACE_LEASE') != mode:
        raise ValueError('surface lease control identity')
    if result['icon_manager'] != value['observation']['composition']['icon_manager'] or result['unauthorized'] != 'unauthorized':
        raise ValueError('native ownership/admission proof differs')
    producers = result['producers']
    if set(producers) != {'first', 'second'} or json.loads(env['SYSPANE_GNOME_LEASE_PIDS']) != [producers[r]['pid'] for r in ['first', 'second']] or producers['first']['pid'] == producers['second']['pid']:
        raise ValueError('two distinct retained producer slots required')
    owners = {}
    for role in ['first', 'second']:
        identity = producers[role]
        command = ['/usr/bin/python3', str(ROOT / 'tests/desktop/gnome_lease_producer.py'), role]
        launched = [r for r in value['commands'] if r['command'] == command]
        cleanup = [r for r in value['cleanup'] if r['process'] == 'lease-' + role]
        pid = identity['pid']
        if len(launched) != 1 or launched[0]['pid'] != pid or identity['arguments'] != command or identity['process_group'] != pid or identity['session'] != pid or identity['start_ticks'] <= 0 or pid == result['icon_manager']['process_group']:
            raise ValueError('native retained producer identity differs')
        if len(cleanup) != 1 or cleanup[0]['pid'] != pid or cleanup[0]['exit'] != (73 if role == 'first' else 0) or cleanup[0]['members_after_stop']:
            raise ValueError('native producer cleanup/exit differs')
        if role == 'second' and not any(r['pid'] == pid and r['state'] != 'Z' for r in cleanup[0]['members_before_stop']):
            raise ValueError('replacement producer not retained')
        mapped = value['lease_producer_mapped_files'][role]
        if identity['executable'] not in mapped or not mapped or any(digest(Path(p).read_bytes()) != h for p, h in mapped.items()):
            raise ValueError('native producer mapped runtime differs')
        records = [json.loads(line) for line in raw_file(value, 'lease_' + role + '_journal', workspace, 'lease-producer-' + role + '.jsonl', 65536).splitlines()]
        selected = [r['native'] for r in result['calls'] if r['role'] == role]
        if not records or len(records) > 33 or records[1:] != selected:
            raise ValueError('native producer raw journal differs')
        ready = records[0]
        owner = ready.get('owner', '')
        if ready.get('event') != 'ready' or ready.get('pid') != pid or ready.get('role') != role or not re.fullmatch(r':[1-9][0-9]*\.[0-9]+', owner) or not 0 < ready['at_ns'] < selected[0]['started_ns']:
            raise ValueError('native producer connection readiness differs')
        owners[role] = owner
    if owners['first'] == owners['second']:
        raise ValueError('producer connections must be distinct')
    expected = [('second', 'Attach', 'lease:1', 'unauthorized'), ('first', 'Attach', 'lease:1', 'accepted'),
                ('first', 'Heartbeat', 0, 'accepted'), ('first', 'Snapshot', 4, 'accepted'),
                ('second', 'Attach', 'lease:2', 'busy'), ('second', 'Snapshot', 99, 'closed')]
    if mode != 'disconnect':
        late = 'accepted' if mode == 'ignore-expiry' else 'closed'
        expected += [('first', 'Heartbeat', 1, 'accepted'), ('first', 'Snapshot', 5, 'accepted'),
                     ('first', 'Heartbeat', 1, 'duplicate'), ('first', 'Snapshot', 6, 'accepted'),
                     ('first', 'Snapshot', 6, 'duplicate'), ('first', 'Heartbeat', 2, late), ('first', 'Snapshot', 7, late)]
    expected += [('first', 'Exit', 73, 'exiting'), ('second', 'Attach', 'lease:2', 'accepted'),
                 ('second', 'Heartbeat', 0, 'accepted'), ('second', 'Snapshot', 1, 'accepted')]
    calls = result['calls']
    if [(r['role'], r['request']['method'], r['request']['value'], r['reply']) for r in calls] != expected:
        raise ValueError('fixed native lease commands/replies differ')
    previous = value['observation']['composition']['marker']['started_monotonic_ns'] + 2400000000
    for row in calls:
        native = row['native']
        if row['peer_pid'] != producers[row['role']]['pid'] or native['event'] != 'call' or native['request'] != row['request'] or native['reply'] != row['reply'] or native['owner'] != owners[row['role']]:
            raise ValueError('native receipt/peer binding differs')
        if not previous <= row['started_ns'] <= native['started_ns'] <= native['finished_ns'] <= row['finished_ns'] <= row['started_ns'] + 50000000:
            raise ValueError('native call order/receipt bound differs')
        previous = row['finished_ns']
    origin = result['started_monotonic_ns']
    if not calls[5]['finished_ns'] <= origin <= calls[5]['finished_ns'] + 50000000:
        raise ValueError('lease interval must follow prelude')
    relative = lambda ns: (ns - origin) // 1000
    groups = [(6, 7, 800000)] if mode == 'disconnect' else [(6, 8, 800000), (8, 11, 1600000), (11, 13, 4100000), (13, 14, 4400000)]
    for begin, end, scheduled in groups:
        if not scheduled <= relative(calls[begin]['started_ns']) <= relative(calls[end - 1]['finished_ns']) <= scheduled + 50000:
            raise ValueError('fixed native lease scheduling differs')
    exiting, attach, heartbeat, full = calls[-4:]
    exit_record = result['exit']
    if exit_record != {'at_us': exit_record['at_us'], 'pid': producers['first']['pid'], 'observer': 'pidfd', 'readable': True} or not relative(exiting['finished_ns']) <= exit_record['at_us'] <= relative(exiting['finished_ns']) + 50000:
        raise ValueError('independently observed producer exit differs')
    if not exit_record['at_us'] + 1000000 <= relative(attach['started_ns']) <= relative(heartbeat['finished_ns']) <= result['reattached_us'] <= exit_record['at_us'] + 1050000:
        raise ValueError('new epoch must follow native exit and retained interval')
    if not result['reattached_us'] + 400000 <= relative(full['started_ns']) <= relative(full['finished_ns']) <= result['reattached_us'] + 450000 or not relative(full['finished_ns']) + 400000 <= result['end_us'] <= relative(full['finished_ns']) + 450000:
        raise ValueError('new epoch pending/fresh intervals differ')
    if not origin + result['end_us'] * 1000 <= result['disable_started_ns'] <= result['disable_finished_ns'] <= result['disable_started_ns'] + 50000000 or not result['disable_finished_ns'] + 250000000 <= result['post']['started_monotonic_ns'] <= result['disable_finished_ns'] + 500000000:
        raise ValueError('disable/post-regression ordering differs')

    def receipt(us, row):
        return row['native']['started_ns'] // 1000 <= us <= row['native']['finished_ns'] // 1000

    def state(name, role, snapshot, generation, data_role, data_call, renewal, alive=True, reason='none'):
        item = result[name]
        last = item['last']
        wanted = {'enabled': True, 'armed': True, 'alive': alive, 'snapshot_required': snapshot,
                  'epoch': 'lease:1' if role == 'first' else 'lease:2', 'owner': owners[role],
                  'last': last, 'reason': reason, 'renewed_us': item['renewed_us']}
        if item != wanted or last != {'epoch': 'lease:1' if data_role == 'first' else 'lease:2', 'generation': generation, 'accepted_us': last['accepted_us']} or not receipt(last['accepted_us'], data_call) or not receipt(item['renewed_us'], renewal):
            raise ValueError('auxiliary accepted identity/lease state differs')
    state('initial_state', 'first', False, 4, 'first', calls[3], calls[2])
    retained = calls[3] if mode == 'disconnect' else calls[12] if mode == 'ignore-expiry' else calls[9]
    generation = 4 if mode == 'disconnect' else 7 if mode == 'ignore-expiry' else 6
    if mode != 'disconnect':
        state('after_late', 'first', mode == 'live', generation, 'first', retained, calls[11] if mode == 'ignore-expiry' else calls[6], mode == 'ignore-expiry', 'none' if mode == 'ignore-expiry' else 'expired')
    elif 'after_late' in result:
        raise ValueError('disconnect mode cannot include late traffic')
    state('pending_state', 'second', True, generation, 'first', retained, heartbeat)
    state('before_disable', 'second', False, 1, 'second', full, heartbeat)
    prior = result['initial_state'] if mode == 'disconnect' else result['after_late']
    if result['pending_state']['last'] != prior['last'] or result['before_disable']['renewed_us'] != result['pending_state']['renewed_us']:
        raise ValueError('reattachment/full snapshot refreshed retained identity or heartbeat')
    actual = judge(result, value['observation']['composition'])
    wanted_outcome = 'fail' if mode == 'ignore-expiry' else 'pass'
    if result['evaluation'] != actual or value['outcome'] != actual['outcome'] or actual['outcome'] != wanted_outcome:
        raise ValueError('native surface lease claim differs from independent pixels')
    if mode != 'disconnect':
        # No diagnostic operation occurs here; these frames must witness the timer.
        timer = [r for r, sample in zip(actual['checks'], result['samples']) if r['settled'] and r['expected_state'] == 'retained' and sample['end_us'] < relative(calls[11]['started_ns'])]
        if not timer or any(r['matches'] != (mode == 'live') for r in timer):
            raise ValueError('independent timer/control coverage absent')
    for row in result['samples']:
        if not isinstance(row['first_exited'], bool) or (row['marker']['start_us'] >= exit_record['at_us'] and not row['first_exited']) or (row['end_us'] < relative(exiting['started_ns']) and row['first_exited']):
            raise ValueError('captured producer exit lifetime differs')
    for stimulus, scheduled in zip(result['post']['trace']['stimuli'], [0, 800000, 1600000]):
        if not scheduled <= stimulus['at_us'] <= scheduled + 50000:
            raise ValueError('post-disable marker stimulus schedule differs')
    records = [json.loads(line) for line in raw_file(value, 'surface_lease_journal', workspace, 'surface-lease.jsonl', 12 * 1024**2).splitlines()]
    initial_keys = ['version', 'control', 'producers', 'icon_manager', 'unauthorized', 'initial_state', 'started_monotonic_ns']
    required = {'call': calls, 'initial': [{k: result[k] for k in initial_keys}], 'sample': result['samples'],
                'exit': [exit_record], 'pending': [{'at_us': result['reattached_us'], 'state': result['pending_state']}],
                'completed': [{k: v for k, v in result.items() if k != 'samples'}]}
    if mode != 'disconnect':
        required['late-state'] = [result['after_late']]
    if len(records) > 260 or set(r['kind'] for r in records) != set(required) or any([r['value'] for r in records if r['kind'] == kind] != rows for kind, rows in required.items()):
        raise ValueError('observer raw lease journal differs')
    # Bind event ordering as well as each family's contents. Late-state follows its
    # commands, and the initial snapshot precedes every sampled pixel.
    order = [('call', c) for c in calls[:6]] + [('initial', required['initial'][0])]
    events = [(r['finished_ns'], 'call', r) for r in calls[6:]]
    events += [(origin + r['end_us'] * 1000, 'sample', r) for r in result['samples']]
    events += [(origin + exit_record['at_us'] * 1000, 'exit', exit_record), (origin + result['reattached_us'] * 1000, 'pending', required['pending'][0])]
    if mode != 'disconnect':
        events.append((calls[12]['finished_ns'] + 1, 'late-state', result['after_late']))
    order += [(kind, row) for _, kind, row in sorted(events, key=lambda e: e[0])]
    order.append(('completed', required['completed'][0]))
    if [(r['kind'], r['value']) for r in records] != order:
        raise ValueError('observer raw lease event order differs')
    return {'control': mode, 'outcome': actual['outcome'], 'lease_pixels': actual['lease_pixels'],
            'native_admission': 'pass', 'retained_identity': 'pass', 'composition': 'pass', 'post_marker': 'pass',
            'samples': len(result['samples']), 'max_gap_us': actual['max_gap_us'],
            'max_capture_us': actual['max_capture_us'], 'cleanup': 'confirmed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--reports', required=True, nargs=3, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    results, identities = [], []
    for path in args.reports:
        path = path.resolve(strict=True)
        if path.parent != build / 'native-evidence' or path.stat().st_size > 16 * 1024**2:
            raise ValueError('owned bounded lease report required')
        raw = path.read_bytes()
        value = json.loads(raw)
        results.append(validate(value, build))
        identities.append({'path': str(path), 'sha256': digest(raw), 'source_base': value['source_base'], 'source_inputs': value['source_inputs'],
                           'runtime': [value['lab_identity_sha256'], value['environment']['uid'], value['lease_producer_mapped_files']]})
    if sorted(r['control'] for r in results) != sorted(CONTROLS) or any(r['source_inputs'] != identities[0]['source_inputs'] or r['runtime'] != identities[0]['runtime'] for r in identities):
        raise ValueError('three source/runtime-identical lease controls required')
    if any(digest((ROOT / p).read_bytes()) != h for p, h in identities[0]['source_inputs'].items()):
        raise ValueError('current native source differs')
    output = args.output.resolve()
    if output.parent != build / 'native-evidence':
        raise ValueError('owned output required')
    scripts = ['source/build/record_gnome_surface_lease.py', 'source/build/record_gnome_composition.py', 'source/build/record_gnome_host.py',
               'source/build/record_gnome_focus.py', 'tests/desktop/gnome_surface_lease.py', 'tests/desktop/gnome_composition.py',
               'tests/desktop/gnome_shell_recovery.py', 'tests/desktop/native_x11_host.py', 'tests/desktop/oracle.py']
    record = {'version': '0.1.0', 'recorded_at': datetime.now(timezone.utc).isoformat(), 'outcome': 'pass',
              'scope': 'Owned GNOME surface expiry/disconnect, retained public marker and replacement full-snapshot admission',
              'reports': identities, 'results': results, 'recorder_inputs': {p: digest((ROOT / p).read_bytes()) for p in scripts},
              'not_run': ['real telemetry', 'full transport/policy', 'automatic restart', 'clock regression in native bridge', 'render watchdog', 'product editor/native exit', 'session lock/resume', 'other profiles', 'full host qualification']}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
