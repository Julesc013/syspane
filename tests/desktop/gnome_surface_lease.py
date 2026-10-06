"""Independent native pixels and held producer exits for surface lease recovery."""
import json
import os
from pathlib import Path
import select
import socket
import struct
import time

import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib
from gnome_composition import FIXTURE, masks, bind_icon_window
from gnome_shell_recovery import process_identity
from native_x11_host import rgb_record
from oracle import decode, pack_frame, unpack_frame, evaluate

CONTROLS = ['live', 'ignore-expiry', 'disconnect']
COLORS = {'active': (32, 160, 64), 'retained': (208, 144, 32)}


def native_call(connection, method, value=None):
    arguments = None if value is None else GLib.Variant('(s)', (value,))
    reply = connection.call_sync('org.gnome.Shell', '/org/syspane/SurfaceLease', 'org.syspane.SurfaceLease',
        method, arguments, None, Gio.DBusCallFlags.NO_AUTO_START, 1000, None)
    return reply.unpack()


def judge(result, composition):
    from record_gnome_host import rgb
    mode = result['control']
    calls = result['calls']
    find = lambda role, method, value: next(c for c in calls if c['role'] == role and c['request'] == {'method': method, 'value': value})
    initial = find('first', 'Snapshot', 4)
    first_exit = result['exit']
    attach = find('second', 'Attach', 'lease:2')
    replacement = find('second', 'Snapshot', 1)
    # A prelude busy attempt is intentionally earlier than the admitted attach.
    attach = next(c for c in calls if c['role'] == 'second' and c['request']['method'] == 'Attach' and c['reply'] == 'accepted')
    origin = result['started_monotonic_ns']
    at = lambda value: (value - origin) // 1000
    if mode not in CONTROLS or not 0 < result['end_us'] < 9000000 or first_exit['observer'] != 'pidfd' or first_exit['readable'] is not True:
        raise ValueError('surface lease control/interval/exit proof')
    calibrations = [rgb(s['frames'][0]['pixels'], 180 * 220 * 3) for s in composition['calibrations']]
    anchors, clean = masks(calibrations[2], calibrations[:2])
    background = bytes(FIXTURE['background_rgb']) * 128 * 96
    last = gap = duration = 0
    lease_ok = True
    checks = []
    for row in result['samples']:
        frame = row['marker']
        begin, end = frame['start_us'], row['end_us']
        if frame['origin'] != 'display_server_root' or not last <= begin <= frame['end_us'] <= row['start_us'] <= end <= result['end_us']:
            raise ValueError('surface lease capture order')
        gap = max(gap, begin - last)
        duration = max(duration, end - begin)
        last = end
        if rgb(row['background'], len(background)) != background:
            raise ValueError('surface lease background changed')
        overlap = rgb(row['overlap'], 180 * 220 * 3)
        if any(overlap[n*3:n*3+3] != calibrations[2][n*3:n*3+3] for group in anchors for n in group) or any(overlap[n*3:n*3+3] != bytes(FIXTURE['overlap_rgb']) for n in clean):
            raise ValueError('surface lease icon composition changed')
        generation = decode(unpack_frame(frame))
        status = rgb(row['badge'], 16 * 16 * 3)
        expected_generation, expected_state, settled = 4, 'active', begin >= at(initial['finished_ns']) + 200000
        if mode != 'disconnect':
            for value in [5, 6]:
                update = find('first', 'Snapshot', value)
                if begin >= at(update['finished_ns']) + 200000:
                    expected_generation = value
                elif end >= at(update['started_ns']):
                    settled = False
            heartbeat = find('first', 'Heartbeat', 1)
            if begin >= at(heartbeat['finished_ns']) + 3200000:
                expected_state = 'retained'
            elif end >= at(heartbeat['started_ns']) + 3000000:
                settled = False
        else:
            exiting = find('first', 'Exit', 73)
            if begin >= first_exit['at_us'] + 200000:
                expected_state = 'retained'
            elif end >= at(exiting['started_ns']):
                settled = False
        # Disconnect after expiry also leaves the same old accepted identity.
        if begin >= first_exit['at_us'] + 200000:
            expected_state = 'retained'
        if begin >= at(replacement['finished_ns']) + 200000:
            expected_generation, expected_state = 1, 'active'
        elif end >= at(replacement['started_ns']):
            settled = False
        ok = generation == expected_generation and status == bytes(COLORS[expected_state]) * 16 * 16
        checks.append({'at_us': begin, 'settled': settled, 'expected_generation': expected_generation, 'expected_state': expected_state, 'matches': ok})
        if settled and not ok:
            lease_ok = False
    gap = max(gap, result['end_us'] - last)
    if len(checks) < 20 or gap > 150000 or duration > 50000:
        raise ValueError('surface lease capture coverage')
    phases = [c for c in checks if c['settled'] and c['expected_state'] == 'retained' and c['at_us'] < at(attach['started_ns'])]
    pending = [c for c in checks if at(attach['finished_ns']) + 200000 <= c['at_us'] < at(replacement['started_ns'])]
    fresh = [c for c in checks if c['settled'] and c['expected_generation'] == 1]
    if min(len(phases), len(pending), len(fresh)) < 3:
        raise ValueError('surface lease retained/pending/fresh coverage')
    post = result['post']
    progress = evaluate(post['trace'])
    if progress != post['evaluation'] or progress['outcome'] != 'pass' or post['trace']['end_us'] != 2400000 or [s['generation'] for s in post['trace']['stimuli']] != [1, 2, 3]:
        raise ValueError('disabled adapter original marker regression')
    if rgb(result['badge_after_disable'], 16 * 16 * 3) != bytes(FIXTURE['background_rgb']) * 16 * 16:
        raise ValueError('lease badge survived disable')
    return {'outcome': 'pass' if lease_ok else 'fail', 'lease_pixels': 'pass' if lease_ok else 'fail',
            'composition': 'pass', 'post_marker': 'pass', 'max_gap_us': gap, 'max_capture_us': duration, 'checks': checks}


def observe(display, environment, shell_pid, workspace, composition, trace_function):
    journal = (workspace / 'surface-lease.jsonl').open('x', encoding='utf-8', newline='\n')
    count = 0
    descriptors = {}
    connection = Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],
        Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
    def preserve(kind, value):
        nonlocal count
        count += 1
        if count > 260:
            raise ValueError('lease journal record capacity')
        journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
        journal.flush()
        if journal.tell() > 12 * 1024**2:
            raise ValueError('lease journal byte capacity')
    pids = dict(zip(['first', 'second'], json.loads(environment['SYSPANE_GNOME_LEASE_PIDS'])))
    result = {'version': '0.1.0', 'control': environment['SYSPANE_GNOME_SURFACE_LEASE'],
              'producers': {role: process_identity(pid) for role, pid in pids.items()},
              'icon_manager': composition['icon_manager'], 'calls': [], 'samples': []}
    def call(role, method, value):
        request = {'method': method, 'value': value}
        begin = time.monotonic_ns()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2)
            client.connect('\0syspane-lease-' + workspace.name.rsplit('-', 1)[1] + '-' + role)
            peer = struct.unpack('3i', client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if peer[0] != pids[role] or peer[1] != os.geteuid():
                raise ValueError('native fixture control peer differs')
            client.sendall((json.dumps(request) + '\n').encode())
            raw = bytearray()
            while not raw.endswith(b'\n'):
                part = client.recv(4097 - len(raw))
                if not part or len(raw) + len(part) > 4096:
                    raise ValueError('bounded control response required')
                raw.extend(part)
        row = {'role': role, 'request': request, 'started_ns': begin, 'finished_ns': time.monotonic_ns(),
               'peer_pid': peer[0], 'native': json.loads(raw)}
        row['reply'] = row['native']['reply']
        result['calls'].append(row)
        preserve('call', row)
        return row
    try:
        if composition['outcome'] != 'pass':
            raise ValueError('lease live composition prerequisite')
        for role, pid in pids.items():
            descriptors[role] = os.pidfd_open(pid)
        pollers = {}
        for role, descriptor in descriptors.items():
            pollers[role] = select.poll()
            pollers[role].register(descriptor, select.POLLIN)
        result['unauthorized'] = native_call(connection, 'Attach', 'lease:1')[0]
        call('second', 'Attach', 'lease:1')
        call('first', 'Attach', 'lease:1')
        call('first', 'Heartbeat', 0)
        call('first', 'Snapshot', 4)
        call('second', 'Attach', 'lease:2')
        call('second', 'Snapshot', 99)
        result['initial_state'] = json.loads(native_call(connection, 'GetState')[0])
        result['started_monotonic_ns'] = started = time.monotonic_ns()
        now = lambda: (time.monotonic_ns() - started) // 1000
        preserve('initial', {k: v for k, v in result.items() if k not in ['calls', 'samples']})
        actions = set()
        next_frame = 0
        final_at = None
        while now() < 9000000:
            at = now()
            if pollers['second'].poll(0):
                raise ValueError('second retained fixture exited')
            if at >= 800000 and 'first-transition' not in actions:
                actions.add('first-transition')
                if result['control'] == 'disconnect':
                    call('first', 'Exit', 73)
                else:
                    call('first', 'Heartbeat', 1)
                    call('first', 'Snapshot', 5)
            if result['control'] != 'disconnect':
                if at >= 1600000 and 'data-only' not in actions:
                    actions.add('data-only')
                    call('first', 'Heartbeat', 1)
                    call('first', 'Snapshot', 6)
                    call('first', 'Snapshot', 6)
                if at >= 4100000 and 'late' not in actions:
                    actions.add('late')
                    call('first', 'Heartbeat', 2)
                    call('first', 'Snapshot', 7)
                    result['after_late'] = json.loads(native_call(connection, 'GetState')[0])
                    preserve('late-state', result['after_late'])
                if at >= 4400000 and 'exit-requested' not in actions:
                    actions.add('exit-requested')
                    call('first', 'Exit', 73)
            if 'exit' not in result and pollers['first'].poll(0):
                result['exit'] = {'at_us': now(), 'pid': pids['first'], 'observer': 'pidfd', 'readable': True}
                preserve('exit', result['exit'])
            if 'exit' in result and now() >= result['exit']['at_us'] + 1000000 and 'reattach' not in actions:
                actions.add('reattach')
                call('second', 'Attach', 'lease:2')
                call('second', 'Heartbeat', 0)
                result['reattached_us'] = now()
                result['pending_state'] = json.loads(native_call(connection, 'GetState')[0])
                preserve('pending', {'at_us': result['reattached_us'], 'state': result['pending_state']})
            if 'reattached_us' in result and now() >= result['reattached_us'] + 400000 and final_at is None:
                call('second', 'Snapshot', 1)
                final_at = now() + 400000
            if at >= next_frame:
                before = now()
                marker = pack_frame(display.capture(*FIXTURE['marker']), before, now())
                row = {'marker': marker, 'start_us': now(), 'overlap': rgb_record(display.capture(*FIXTURE['overlap'])),
                       'background': rgb_record(display.capture(600, 400, 128, 96)),
                       'badge': rgb_record(display.capture(462, 202, 16, 16))}
                row['first_exited'] = bool(pollers['first'].poll(0))
                row['end_us'] = now()
                result['samples'].append(row)
                preserve('sample', row)
                next_frame += 50000
            if final_at is not None and now() >= final_at:
                break
            time.sleep(.002)
        else:
            raise TimeoutError('bounded surface lease scenario')
        result['end_us'] = now()
        result['before_disable'] = json.loads(native_call(connection, 'GetState')[0])
        result['disable_started_ns'] = time.monotonic_ns()
        native_call(connection, 'Disable')
        result['disable_finished_ns'] = time.monotonic_ns()
        result['post'] = trace_function(display, environment, dismiss=False)
        result['badge_after_disable'] = rgb_record(display.capture(462, 202, 16, 16))
        if bind_icon_window(display, shell_pid, workspace) != result['icon_manager']:
            raise ValueError('lease icon manager lifetime changed')
        result['evaluation'] = judge(result, composition)
        preserve('completed', {k: v for k, v in result.items() if k != 'samples'})
        return result
    except Exception as error:
        preserve('error', {'message': type(error).__name__ + ': ' + str(error)})
        raise
    finally:
        for descriptor in descriptors.values():
            os.close(descriptor)
        connection.close_sync(None)
        journal.close()
