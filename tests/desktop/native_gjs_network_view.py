"""Native GJS consumer tests with independent literal model/clock expectations."""
import base64
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import time
import uuid
import zipfile
from native_gjs_clock import ROOT, sha, receive, descriptors, owned_build, inventory, verify

EPOCH = 'fixture:network'
SOURCES = ['CMakeLists.txt', 'source/build/components.json', 'source/build/targets/linux-x64-gcc13.json',
           'source/desktop/gnome/SysPaneClock-0.1.gir', 'tests/desktop/native_gjs_clock.py',
           'tests/desktop/native_gjs_network_view.py', 'tests/desktop/gjs_network_view.js',
           'spec/delivery/packages/w-25-gjs-network-view.md', 'source/build/prepare_gnome_lab.py',
           'source/build/check_gjs_clock_dependencies.py', 'source/build/gnome-lab-packages.json']
SOURCES += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'source').rglob('*') if p.suffix in ('.cpp', '.hpp'))


def packet(value):
    raw = json.dumps(value, separators=(',', ':')).encode()
    return len(raw).to_bytes(4, 'big') + raw


def envelope(kind, body):
    return {'type': kind, 'connection_id': 'D', 'producer_epoch': EPOCH, 'body': body}


def welcome(limit=1048576):
    return envelope('welcome', {'wire_major': 0, 'wire_minor': 1, 'role': 'console', 'producer_epoch': EPOCH,
        'max_frame_bytes': limit, 'document_versions': [{'document': name, 'version': '0.2.0'} for name in ('telemetry', 'snapshot', 'observation')],
        'required_features': [], 'optional_features': ['telemetry.snapshot', 'telemetry.measured-time']})


def snapshot(stamp, rates=False):
    generation = '2' if rates else '1'
    fields = ['network.receive_bytes', 'network.transmit_bytes', 'network.receive_bytes_per_second', 'network.transmit_bytes_per_second']
    observations = []
    for index, name in enumerate(fields):
        available = index < 2 or rates
        value = ({'kind': 'uint64', 'data': ['18446744073709551615', '0'][index]} if index < 2 else
                 {'kind': 'number', 'data': [.0625, 1.0625][index-2]} if rates else None)
        observations.append({'schema_version': '0.2.0', 'entity_id': 'network:interface:1', 'field': name,
            'value': value, 'unit': 'byte' if index < 2 else 'byte/second', 'origin': 'observed' if index < 2 else 'derived',
            'support': 'supported', 'acquisition': 'success' if available else 'pending',
            'freshness': 'current' if available else 'unknown', 'presence': 'present', 'source_id': 'provider:native-network',
            'observed_at': '2026-10-06T00:00:00Z' if available else None, 'attempted_at': '2026-10-06T00:00:01Z',
            'producer_epoch': EPOCH, 'generation': generation, 'sample_interval_ns': '1000000000' if index >= 2 and available else None,
            'error': None, 'measured_at': {'clock_id': 'linux.boottime', 'nanoseconds': str(stamp)} if available else None})
    document = {'schema_version': '0.2.0', 'producer_epoch': EPOCH, 'generation': generation,
        'captured_at': '2026-10-06T00:00:01Z', 'entities': [{'id': 'network:interface:1', 'kind': 'network.interface',
            'display_name': 'Synthetic interface', 'identity': {}, 'generation': generation}], 'relationships': [],
        'sources': [{'id': 'provider:native-network', 'kind': 'native.network.counters', 'scope': 'host:local'}],
        'observations': observations, 'completeness': 'complete'}
    return envelope('snapshot', {'schema_version': '0.2.0', 'subscription_id': 'S', 'producer_id': 'producer:network',
        'policy_revision': '7', 'record_id': 'fixture:'+generation, 'clock_id': 'linux.boottime', 'snapshot': document})


def server(endpoint):
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(endpoint); os.chmod(endpoint, 0o600); listener.listen(2)
    held = []
    print(json.dumps({'event': 'listening'}), flush=True)
    end = time.monotonic() + 35
    try:
        while time.monotonic() < end:
            ready = select.select([listener, sys.stdin], [], [], max(0, end-time.monotonic()))[0]
            if sys.stdin in ready:
                assert sys.stdin.read(1) == 'x'
                return
            if listener in ready:
                assert len(held) < 2
                held.append(listener.accept()[0])
        raise TimeoutError('Synthetic peer deadline')
    finally:
        for connection in held:
            connection.close()
        listener.close()


def main():
    build = owned_build(Path(sys.argv[1])); output = build/'native-evidence'; output.mkdir(exist_ok=True)
    attempt = 'GJS-NETWORK-'+uuid.uuid4().hex
    report = {'family': 'GJS-NETWORK', 'outcome': 'fail', 'executed_at': datetime.now(timezone.utc).isoformat(),
              'source_inputs': {p: sha(ROOT/p) for p in SOURCES}, 'cases': [], 'calls': [],
              'qualification': 'Native model consumer with synthetic inputs injected by its serialized fixture owner. No operational delivery, shell pixels or installed-policy qualification.'}
    archive = output/(attempt+'-sources.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as bundle:
        for name in SOURCES:
            bundle.write(ROOT/name, name)
    report['source_archive_sha256'] = sha(archive)
    runtime = Path.home()/'.cache/syspane/ipc-w24'
    assert runtime.resolve(strict=True) == runtime and runtime.stat().st_uid == os.getuid() and runtime.stat().st_mode & 0o777 == 0o700
    workspace = runtime/('case-'+uuid.uuid4().hex); workspace.mkdir(mode=0o700); endpoint = str(workspace/'s')
    processes, handles = [], []
    try:
        report['build_dependencies'] = verify()
        lab = build/'gnome-lab'; identity = json.loads((lab/'identity.json').read_text())
        assert identity['lock_sha256'] == sha(ROOT/'source/build/gnome-lab-packages.json') and identity['files'] == inventory(lab/'sysroot')
        executable = lab/'sysroot/usr/bin/gjs'; lib = lab/'sysroot/usr/lib/x86_64-linux-gnu'
        report['artifacts'] = {str(p): sha(p) for p in [build/'libsyspane_gjs_clock.so', build/'SysPaneClock-0.1.typelib', executable, lab/'identity.json']}
        peer = subprocess.Popen(['/usr/bin/python3', str(Path(__file__).resolve()), '--server', endpoint],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append(peer); peer_fd = os.pidfd_open(peer.pid); handles.append(peer_fd)
        assert receive(peer) == {'event': 'listening'}
        env = {k: v for k, v in os.environ.items() if k not in ('DISPLAY', 'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'GI_TYPELIB_PATH', 'LD_LIBRARY_PATH')}
        env.update(LD_LIBRARY_PATH=str(build)+':'+str(lib),
            GI_TYPELIB_PATH=':'.join(map(str, [build, lib/'gjs/girepository-1.0', lib/'girepository-1.0'])))
        command = [str(executable), '-m', str(ROOT/'tests/desktop/gjs_network_view.js'), endpoint, str(peer.pid)]
        child = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append(child); handles.append(os.pidfd_open(child.pid)); report['command'] = command
        ready = receive(child)
        assert ready == {'event': 'ready', 'invalid': [{'error': e} for e in ['peer.handle', 'peer.process', 'network.policy', 'network.closed']]}
        report['cases'].append({'case': 'GJS-NETWORK.ADMISSION', 'outcome': 'pass', 'observation': ready})
        baseline = descriptors(child.pid)
        namespace = lambda pid: (os.stat(f'/proc/{pid}/ns/time').st_dev, os.stat(f'/proc/{pid}/ns/time').st_ino)
        assert namespace(os.getpid()) == namespace(peer.pid) == namespace(child.pid)
        report['time_namespace'] = {'observer': namespace(os.getpid()), 'peer': namespace(peer.pid), 'gjs': namespace(child.pid)}

        def ask(op, owner='main', **args):
            request = {'op': op, 'id': owner, **args}; before = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            child.stdin.write(json.dumps(request)+'\n'); child.stdin.flush(); response = receive(child)
            after = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            report['calls'].append({'request': request, 'before_ns': str(before), 'after_ns': str(after), 'reply': response})
            assert response['event'] == op
            return response

        def value(op, owner='main', **args):
            response = ask(op, owner, **args)
            assert 'error' not in response, response
            return response['value']

        def feed(data, owner='main', expected='accepted'):
            assert value('feed', owner, data=base64.b64encode(data).decode()) == expected

        def project(owner='main'):
            frame = value('project', owner)
            call = report['calls'][-1]
            for field in frame.get('fields', []):
                if field['age_ns'] is not None:
                    stamp = int(field['measured_ns']); age = int(field['age_ns'])
                    assert int(call['before_ns'])-stamp <= age <= int(call['after_ns'])-stamp
            return frame

        value('open'); assert project() == {'code': 'waiting', 'fields': []}
        raw = base64.b64decode(value('hello')); assert len(raw)-4 == int.from_bytes(raw[:4], 'big')
        assert json.loads(raw[4:])['body']['required_features'] == ['telemetry.snapshot', 'telemetry.measured-time']
        first_stamp = time.clock_gettime_ns(time.CLOCK_BOOTTIME); first = packet(snapshot(first_stamp)); greeting = packet(welcome())
        feed(greeting[:3], expected='buffered'); feed(greeting[3:]+first)
        frame = project(); assert frame['code'] == 'ready' and frame['lease'] == 2 and frame['reason'] == 0
        assert (frame['producer'], frame['epoch'], frame['entity'], frame['generation']) == ('producer:network', EPOCH, 'network:interface:1', '1')
        assert 'clock_scope' not in json.dumps(frame)
        assert [f['value'] for f in frame['fields']] == ['18446744073709551615', '0', None, None]
        for index, field in enumerate(frame['fields']):
            assert field['support'] == field['presence'] == 0 and field['origin'] == (0 if index < 2 else 1)
            assert field['acquisition'] == (0 if index < 2 else 1) and field['effective'] == (0 if index < 2 else 2)
            assert field['measured_ns'] == (str(first_stamp) if index < 2 else None)
            assert field['observed_at'] == ({'seconds': '1791244800', 'nanoseconds': 0, 'subnanoseconds': ''} if index < 2 else None)
            assert field['attempted_at'] == {'seconds': '1791244801', 'nanoseconds': 0, 'subnanoseconds': ''}
            assert field['unit'] == ('byte' if index < 2 else 'byte/second') and field['error_code'] == ''
        report['cases'].append({'case': 'GJS-NETWORK.VALUES', 'outcome': 'pass'})
        feed(first, expected='duplicate'); assert int(project()['fields'][0]['age_ns']) >= int(frame['fields'][0]['age_ns'])
        stamp = time.clock_gettime_ns(time.CLOCK_BOOTTIME); second = packet(snapshot(stamp, True)); feed(second)
        frame = project(); assert [f['value'] for f in frame['fields']] == ['18446744073709551615', '0', '0.063', '1.063']
        assert [f['interval_ns'] for f in frame['fields']] == [None, None, '1000000000', '1000000000']
        sequence = 0
        while time.clock_gettime_ns(time.CLOCK_BOOTTIME)-stamp < 3_100_000_000:
            heartbeat = packet(envelope('heartbeat', {'sequence': str(sequence)})); feed(heartbeat); feed(heartbeat, expected='duplicate')
            sequence += 1; time.sleep(.45); project()
        frame = project(); assert frame['lease'] == 2 and all(f['reported'] == 0 and f['effective'] == 1 and f['measured_ns'] == str(stamp) for f in frame['fields'])
        feed(second, expected='duplicate'); assert all(f['measured_ns'] == str(stamp) for f in project()['fields'])
        report['cases'].append({'case': 'GJS-NETWORK.AGE-REPLAY', 'outcome': 'pass'})
        time.sleep(3.1); frame = project(); assert frame['lease'] == 3 and frame['reason'] == 2
        feed(packet(envelope('heartbeat', {'sequence': str(sequence)})), expected='closed')
        assert project()['lease'] == 3
        assert value('policy', revision='6', permit=False) == 'invalid' and project()['code'] == 'ready'
        assert value('policy', revision='7', permit=False) == 'invalid' and project()['code'] == 'ready'
        assert value('policy', revision='7', permit=True) == 'duplicate' and project()['code'] == 'ready'
        assert value('policy', revision='8', permit=False) == 'cleared' and project() == {'code': 'restricted', 'fields': []}
        feed(b'invalid payload', expected='restricted')
        assert value('policy', revision='9', permit=True) == 'cleared' and project() == {'code': 'waiting', 'fields': []}
        feed(second, expected='policy_changed')
        shutdown = base64.b64decode(value('shutdown')); assert json.loads(shutdown[4:]) == envelope('shutdown', {'reason': 'normal'})
        value('close'); report['cases'].append({'case': 'GJS-NETWORK.LEASE-POLICY', 'outcome': 'pass'})
        value('open', 'gap'); feed(greeting+first, 'gap'); feed(packet(envelope('gap', {'reason': 'resync_required'})), 'gap')
        assert project('gap')['lease'] == 3 and project('gap')['reason'] == 3
        value('close', 'gap'); report['cases'].append({'case': 'GJS-NETWORK.GAP', 'outcome': 'pass'})

        retained = snapshot(stamp, True)
        for field in retained['body']['snapshot']['observations']:
            field.update(acquisition='failed', freshness='stale', attempted_at='2026-10-06T00:00:02Z',
                error={'code': 'network.read', 'message': 'Synthetic read failure.', 'retryable': True})
        value('open', 'retained'); feed(greeting+packet(retained), 'retained')
        frame = project('retained')
        assert [f['value'] for f in frame['fields']] == ['18446744073709551615', '0', '0.063', '1.063']
        assert all(f['acquisition'] == 3 and f['reported'] == f['effective'] == 1 and f['error_code'] == 'network.read'
            and f['measured_ns'] == str(stamp) and f['observed_at']['seconds'] == '1791244800'
            and f['attempted_at']['seconds'] == '1791244802' for f in frame['fields'])
        value('close', 'retained'); report['cases'].append({'case': 'GJS-NETWORK.RETAIN', 'outcome': 'pass'})

        conflict = snapshot(first_stamp); conflict['body']['snapshot']['observations'][0]['value']['data'] = '12'
        value('open', 'conflict'); feed(greeting+first, 'conflict')
        assert ask('feed', 'conflict', data=base64.b64encode(packet(conflict)).decode()) == {'event': 'feed', 'error': 'network.receive'}
        assert ask('project', 'conflict') == {'event': 'project', 'error': 'network.closed'}
        value('close', 'conflict'); report['cases'].append({'case': 'GJS-NETWORK.REPLAY-CONFLICT', 'outcome': 'pass'})

        wrong_role = welcome(); wrong_role['body']['role'] = 'desktop'
        for name, data, expected in [('direction', packet(wrong_role), 'network.welcome'),
            ('negotiated-limit', packet(welcome(1024))+(1025).to_bytes(4, 'big'), 'frame.length')]:
            value('open', name)
            assert ask('feed', name, data=base64.b64encode(data).decode()) == {'event': 'feed', 'error': expected}
            assert ask('project', name) == {'event': 'project', 'error': 'network.closed'}
            value('close', name)
        report['cases'].append({'case': 'GJS-NETWORK.NEGOTIATION', 'outcome': 'pass'})

        wrong = snapshot(first_stamp); wrong['producer_epoch'] = 'wrong:epoch'
        future = snapshot(time.clock_gettime_ns(time.CLOCK_BOOTTIME)+60_000_000_000)
        for name, data, expected in [('epoch', packet(wrong), 'network.envelope'), ('future', packet(future), 'network.receive'),
            ('length', b'\x00\x10\x00\x01', 'frame.length'), ('batch', packet(envelope('heartbeat', {'sequence': '0'}))*17, 'network.batch'),
            ('input', b'x'*16385, 'network.input')]:
            value('open', name); feed(greeting, name)
            assert ask('feed', name, data=base64.b64encode(data).decode()) == {'event': 'feed', 'error': expected}
            assert ask('project', name) == {'event': 'project', 'error': 'network.closed'}
            value('close', name)
        report['cases'].append({'case': 'GJS-NETWORK.REJECT', 'outcome': 'pass'})
        value('open', 'deadline'); feed(greeting[:10], 'deadline', expected='buffered')
        value('open', 'silent')
        assert project('deadline') == {'code': 'waiting', 'fields': []}
        time.sleep(5.1)
        assert ask('project', 'deadline') == {'event': 'project', 'error': 'frame.timeout'}
        assert ask('project', 'silent') == {'event': 'project', 'error': 'network.welcome_timeout'}
        value('close', 'silent')
        value('close', 'deadline'); report['cases'].append({'case': 'GJS-NETWORK.DEADLINE', 'outcome': 'pass'})
        assert descriptors(child.pid) == baseline
        assert value('cycles') == 64 and descriptors(child.pid) == baseline
        report['cases'].append({'case': 'GJS-NETWORK.CLEANUP', 'outcome': 'pass', 'cycles': 64,
            'baseline_descriptors': baseline, 'after_close_descriptors': descriptors(child.pid)})
        value('open', 'exit'); feed(greeting+first, 'exit')
        peer.stdin.write('x'); peer.stdin.flush(); assert peer.wait(timeout=3) == 0
        assert select.select([peer_fd], [], [], 0)[0]
        assert ask('project', 'exit') == {'event': 'project', 'error': 'clock.peer_exited'}
        assert ask('project', 'exit') == {'event': 'project', 'error': 'network.closed'}
        value('close', 'exit'); child.stdin.write('{"op":"exit"}\n'); child.stdin.flush(); assert child.wait(timeout=3) == 0
        report['cases'].append({'case': 'GJS-NETWORK.PEER-EXIT', 'outcome': 'pass', 'native_pid': peer.pid,
            'native_exit': peer.returncode, 'pidfd_exit': True})
        report['outcome'] = 'pass'
    except Exception as error:
        report['failure'] = type(error).__name__+': '+str(error)
        raise
    finally:
        report['processes'] = []
        for process in processes:
            forced = process.poll() is None
            if forced: process.kill()
            process.wait(timeout=5)
            report['processes'].append({'pid': process.pid, 'exit': process.returncode, 'forced_cleanup': forced,
                'remaining_stdout': process.stdout.read(), 'stderr': process.stderr.read()})
        for fd in handles: os.close(fd)
        if Path(endpoint).is_socket(): Path(endpoint).unlink()
        workspace.rmdir()
        if report['outcome'] == 'pass' and any(r['exit'] or r['forced_cleanup'] or r['remaining_stdout'] or r['stderr'] for r in report['processes']):
            report['outcome'] = 'fail'; report['failure'] = 'Unexpected native exit/output/cleanup'
        raw = json.dumps(report, indent=2)+'\n'; assert len(raw.encode()) <= 4*1024**2
        path = output/(attempt+'.json'); path.write_text(raw)
        print('Native evidence:', path, flush=True); print('GJS-NETWORK:', report['outcome'], flush=True)
    if report['outcome'] != 'pass': raise AssertionError(report.get('failure', 'Native consumer failed'))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--server': server(sys.argv[2])
    else: main()
