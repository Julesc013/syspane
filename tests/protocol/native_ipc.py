"""Independent fixed-oracle process harness for the local IPC development adapter."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import stat
import subprocess
import threading
import time
import uuid


class Process:
    def __init__(self, command, new_session=False):
        self.lines = []
        self.events = queue.Queue()
        kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': new_session}
        self.process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, encoding='utf-8', bufsize=1, **kwargs)
        def collect():
            for line in self.process.stdout:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    value = {'event': 'unparsed_output', 'text': line.rstrip()}
                self.lines.append(value)
                self.events.put(value)
        self.reader = threading.Thread(target=collect, daemon=True)
        self.reader.start()

    def event(self, name, timeout=7):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                value = self.events.get(timeout=min(.1, max(.001, end-time.monotonic())))
                if value.get('event') == name:
                    return value
                if value.get('event') == 'error':
                    raise AssertionError(f'{name} replaced by {value}')
            except queue.Empty:
                if self.process.poll() is not None and not self.reader.is_alive():
                    raise AssertionError(f'process exited before {name}: {self.lines}')
        raise AssertionError(f'timeout waiting for {name}: {self.lines}')

    def finish(self, timeout=10):
        result = self.process.wait(timeout=timeout)
        self.reader.join(timeout=1)
        assert not self.reader.is_alive(), 'stdout collector did not finish'
        return result

    def stop(self):
        if self.process.poll() is None:
            self.process.kill()  # Only the exact finite probe process we launched.
        self.process.wait(timeout=3)
        self.reader.join(timeout=1)

    def record(self):
        return {'pid': self.process.pid, 'exit_code': self.process.poll(), 'events': self.lines}


class Harness:
    def __init__(self, executable):
        self.executable = str(executable)
        self.cases = []

    def endpoint(self):
        tag = uuid.uuid4().hex
        if os.name == 'nt':
            return '\\\\.\\pipe\\SysPane.Dev.' + tag, None
        root = Path.home()/'.cache/syspane/ipc-w24'
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = root.lstat()
        assert stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700
        assert root.resolve() == root, 'runtime root must be canonical'
        owned = root/('case-'+tag[:12])
        owned.mkdir(mode=0o700)
        return str(owned/'s'), owned

    def scenario(self, case, client_mode, *, server_mode='normal', server_expected=0, client_expected=None,
                 collision=False, new_session=False, check=None, clients=None):
        endpoint, owned = self.endpoint()
        processes = []
        record = {'case': case, 'outcome': 'fail', 'started_at': datetime.now(timezone.utc).isoformat()}
        self.cases.append(record)
        start = time.monotonic()
        try:
            server = Process([self.executable, 'server', endpoint, server_mode, str(server_expected)])
            processes.append(server)
            ready = server.event('ready')
            assert ready['access_controls_verified'] is True, 'endpoint ACL/mode verification failed'
            assert ready['unprivileged_context'] is True, 'native proof requires unelevated processes'
            if collision:
                duplicate = Process([self.executable, 'collision', endpoint, 'normal', '0'])
                processes.append(duplicate)
                assert duplicate.finish() == 0 and duplicate.lines == [{'event': 'collision_rejected'}], 'existing endpoint replaced'
            modes = clients or [client_mode]
            client_processes = []
            for ordinal, mode in enumerate(modes):
                listening = server.event('listening')
                assert listening['ordinal'] == ordinal
                expected = server.process.pid if client_expected is None else client_expected
                client = Process([self.executable, 'client', endpoint, mode, str(expected)], new_session=new_session)
                client_processes.append(client)
                processes.append(client)
                client.finish(timeout=10)
            server.finish(timeout=10)
            if check:
                check(server, client_processes)
            record['outcome'] = 'pass'
        except Exception as error:
            record['failure'] = str(error)
            raise
        finally:
            for process in processes:
                process.stop()
            record['processes'] = [process.record() for process in processes]
            record['elapsed_seconds'] = round(time.monotonic()-start, 3)
            if owned is not None:
                # Native listener must remove only its owned socket. Do not delete
                # an unexpected entry or recursively clean a failed endpoint.
                if list(owned.iterdir()):
                    record['remaining_runtime_directory'] = str(owned)
                    if record['outcome'] == 'pass':
                        record['outcome'] = 'fail'
                        raise AssertionError('native listener left endpoint entries behind')
                else:
                    owned.rmdir()
            print(json.dumps({'case': case, 'outcome': record['outcome'], 'elapsed_seconds': record['elapsed_seconds']}), flush=True)


def events(process, name):
    return [row for row in process.lines if row.get('event') == name]


def native_identity(server, client):
    server_rows = events(server, 'authenticated')
    client_rows = events(client, 'authenticated')
    assert any(row['peer_pid'] == client.process.pid and row['user_session_verified'] is True for row in server_rows)
    assert client_rows == [{'event': 'authenticated', 'peer_pid': server.process.pid, 'user_session_verified': True}]


def preview_body(request='R'):
    return {'schema_version': '0.1.0', 'request_id': request, 'producer_epoch': 'probe:epoch-1', 'outcome': 'preview',
            'revision': '40', 'stored': False, 'durable': False, 'visible': False, 'activation': [], 'error': None}


def journey(server, clients):
    assert server.process.returncode == 0
    assert all(client.process.returncode == 0 for client in clients)
    for client in clients:
        native_identity(server, client)
    first = events(clients[0], 'reply')
    second = events(clients[1], 'reply')
    assert len(first) == 3 and len(second) == 5
    assert first[0]['message']['type'] == 'welcome' and first[0]['message']['connection_id'] == 'C0'
    assert second[0]['message']['connection_id'] == 'C1'
    assert [row['message']['body'] for row in first[1:]] == [preview_body(), preview_body()]
    assert second[1]['message']['body'] == preview_body(), 'reconnect lost or reran preview'
    rejected, conflict, unknown = [row['message']['body'] for row in second[2:]]
    assert rejected['outcome'] == 'invalid' and rejected['error']['code'] == 'feature.unsupported'
    assert rejected['stored'] is False and rejected['durable'] is False and rejected['revision'] == '40'
    assert conflict['outcome'] == 'conflict' and conflict['error']['code'] == 'request.changed'
    assert unknown['outcome'] == 'unknown' and all(unknown[name] is None for name in ('revision', 'stored', 'durable', 'visible'))
    closed = events(server, 'closed')
    assert len(closed) == 2 and all(row['requests'] == 1 and row['reason'] == 'peer.shutdown' for row in closed)
    assert closed[0]['reads'] >= 2 and closed[0]['frames'] == 4, 'fragmented/coalesced journey not observed'


def lost_ack(server, clients):
    assert server.process.returncode == 0 and all(client.process.returncode == 0 for client in clients)
    for client in clients:
        native_identity(server, client)
    assert len(events(clients[0], 'reply')) == 1, 'first client must not read a command result'
    replies = events(clients[1], 'reply')
    assert len(replies) == 5 and replies[1]['message']['body'] == preview_body(), 'unacknowledged request lost on reconnect'
    closed = events(server, 'closed')
    assert len(closed) == 2 and all(row['requests'] == 1 for row in closed), 'lost acknowledgement reran request'
    assert closed[0]['reason'] in ('peer.eof', 'io.write') and closed[1]['reason'] == 'peer.shutdown'


def saturation(server, clients):
    normal(server, clients)
    replies = [row['message'] for row in events(clients[0], 'reply')]
    assert len(replies) == 133 and replies[0]['type'] == 'welcome'
    for index, reply in enumerate(replies[1:129]):
        assert reply['type'] == 'result' and reply['body'] == preview_body('R'+str(index))
    busy = replies[129]['body']
    assert busy['outcome'] == 'busy' and busy['error']['code'] == 'request.capacity'
    assert busy['stored'] is False and busy['durable'] is False and busy['revision'] == '40'
    assert replies[130]['body'] == preview_body('R0') and replies[131]['body'] == preview_body('R0'), 'control retrieval/cancel blocked under saturation'
    assert replies[132]['type'] == 'heartbeat' and replies[132]['body'] == {'sequence': '9'}, 'health traffic blocked under saturation'
    assert events(server, 'closed')[0]['requests'] == 128, 'busy/control traffic changed reservations'


def closed_as(reason, *, timed=False, buffered=None):
    def check(server, clients):
        assert server.process.returncode == 0
        rows = events(server, 'closed')
        assert len(rows) == 1 and rows[0]['reason'] == reason, rows
        assert rows[0]['requests'] == 0, 'invalid stream admitted a request'
        if timed:
            assert 4500 <= rows[0]['elapsed_ms'] <= 8000, rows
        if buffered is not None:
            assert rows[0]['buffered'] <= buffered, rows
        native_identity(server, clients[0])
    return check


def server_denial(code):
    def check(server, clients):
        assert server.process.returncode == 3
        assert events(server, 'error') == [{'event': 'error', 'code': code}], server.lines
        assert not events(server, 'authenticated') and not events(clients[0], 'reply'), 'denied peer reached protocol'
    return check


def client_denial(server, clients):
    assert clients[0].process.returncode == 3
    assert events(clients[0], 'error') == [{'event': 'error', 'code': 'peer.process'}]
    assert not events(clients[0], 'reply')
    assert all(row.get('requests', 0) == 0 for row in events(server, 'closed'))


def normal(server, clients):
    assert server.process.returncode == 0 and clients[0].process.returncode == 0
    native_identity(server, clients[0])
    assert events(server, 'closed')[0]['reason'] == 'peer.shutdown'


def forged(server, clients):
    normal(server, clients)
    replies = events(clients[0], 'reply')
    assert len(replies) == 2
    result = replies[1]['message']['body']
    assert result['outcome'] == 'invalid' and result['error']['code'] == 'command.shape'
    assert result['stored'] is False and result['durable'] is False
    assert events(server, 'closed')[0]['requests'] == 0


def new_session_denial(server, clients):
    server_denial('peer.session')(server, clients)
    assert events(clients[0], 'error') == [{'event': 'error', 'code': 'peer.session'}], clients[0].lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    parser.add_argument('family', choices=('NATIVE-01', 'NATIVE-02'))
    parser.add_argument('output_root', type=Path)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    harness = Harness(args.executable.resolve())
    report = {'family': args.family, 'profile_os': os.name, 'cases': harness.cases, 'outcome': 'fail',
              'qualification': {'cross_user': 'blocked: no admitted second-user laboratory',
                                'cross_logon_or_desktop_session': 'blocked: no admitted Windows second logon or Linux desktop-session laboratory'}}
    destination = args.output_root/(args.family+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    try:
        if args.family == 'NATIVE-01':
            harness.scenario('NATIVE-01.JOURNEY', 'journey', server_mode='journey', clients=['journey', 'retrieve'], check=journey)
            harness.scenario('NATIVE-01.LOST-ACK', 'drop-reply', server_mode='journey', clients=['drop-reply', 'retrieve'], check=lost_ack)
            harness.scenario('NATIVE-01.SATURATION', 'saturation', check=saturation)
            harness.scenario('NATIVE-01.PARTIAL-EOF', 'partial-eof', check=closed_as('frame.truncated'))
            harness.scenario('NATIVE-01.MALFORMED', 'malformed', check=closed_as('frame.length', buffered=4))
            harness.scenario('NATIVE-01.NEGOTIATED-LIMIT', 'over-limit', check=closed_as('frame.length', buffered=4))
            harness.scenario('NATIVE-01.HELLO-TIMEOUT', 'hello-timeout', check=closed_as('handshake.timeout', timed=True))
            harness.scenario('NATIVE-01.FRAME-TIMEOUT', 'frame-timeout', check=closed_as('frame.timeout', timed=True))
            harness.scenario('NATIVE-01.WRITE-TIMEOUT', 'write-stall', server_mode='write-stall', check=closed_as('io.timeout', timed=True))
        else:
            harness.scenario('NATIVE-02.COLLISION', 'normal', collision=True, check=normal)
            harness.scenario('NATIVE-02.SERVER-PROCESS-DENIAL', 'normal', server_expected=os.getpid(), check=server_denial('peer.process'))
            harness.scenario('NATIVE-02.CLIENT-PROCESS-DENIAL', 'normal', client_expected=os.getpid(), check=client_denial)
            harness.scenario('NATIVE-02.ROLE-SPOOF', 'role-spoof', check=closed_as('handshake.role_denied'))
            harness.scenario('NATIVE-02.FORGED-AUTHORITY', 'forged', check=forged)
            harness.scenario('NATIVE-02.OLD-EPOCH', 'old-epoch', check=closed_as('session.identity'))
            if os.name != 'nt':
                harness.scenario('NATIVE-02.POSIX-SESSION-DENIAL', 'normal', new_session=True, check=new_session_denial)
        report['outcome'] = 'pass'
    finally:
        destination.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        print('Native evidence: '+str(destination), flush=True)


if __name__ == '__main__':
    main()
