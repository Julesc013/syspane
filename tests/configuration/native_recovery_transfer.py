"""Independent filesystem and authenticated-traffic oracle for profile transfer 0.2."""
from contextlib import contextmanager
from pathlib import Path
import copy, json, os, signal, stat, time
import native_profile_projection as base

FIXTURE = base.ROOT / 'tests/configuration/recovery-transfer-cases.json'
DEFINITIONS = json.loads(FIXTURE.read_bytes())


def exercise(h):
    parent, root, inspect, record = (h[n] for n in ('parent', 'root', 'inspect', 'record'))
    record['extension_sha256'] = base.sha(Path(__file__).read_bytes())
    record['fixture_sha256'] = base.sha(FIXTURE.read_bytes())

    class Client(h['Client']):
        def hello(self):
            docs = [dict(document=n, version=v) for n, v in [('profile-request', '0.2.0'), ('profile-result', '0.2.0'),
                ('command', '0.5.0'), ('command-result', '0.1.0'), ('reconciliation-request', '0.1.0'), ('reconciliation-result', '0.1.0')]]
            self.send('hello', dict(wire_major=0, wire_minor=1, role='console', producer_epoch='client', max_frame_bytes=328704,
                document_versions=docs, required_features=['configuration.transactions', 'result.reconcile', 'configuration.profile', 'configuration.recovery-context'],
                optional_features=['configuration.content', 'configuration.scene-content', 'configuration.large-commands', 'cancel', 'result.get']))

    def timeout(_s, _f):
        raise AssertionError('native case deadline')

    signal.signal(signal.SIGALRM, timeout)

    @contextmanager
    def case(name):
        start = time.monotonic(); signal.alarm(DEFINITIONS['native_case_timeout_seconds'])
        facts = {}
        try:
            yield facts
            elapsed = time.monotonic() - start
            assert elapsed < DEFINITIONS['native_case_timeout_seconds']
            h['passed'](name, elapsed_seconds=elapsed, **facts)
        finally:
            signal.alarm(0)

    def expected(p, transfer=1, revision='0', session='editor:S', mode='allow'):
        parts = h['expected_parts'](revision)
        header = json.loads(parts[0]); header['schema_version'] = '0.2.0'; parts[0] = base.encoded(header)
        policy = json.loads(parts[3])
        policy['disclosure'].insert(1, dict(channel='history', allow_classifications=['operational', 'public', 'sensitive']))
        if mode != 'allow':
            policy['denied_capabilities'] = ['editor.recovery' if mode == 'retention-denied' else 'editor.recovery.erase']
        context = copy.deepcopy(DEFINITIONS['expected_context'])
        context.update(producer_epoch=p.epoch, editor_session=session, transfer_id=str(transfer), revision=revision,
            generation=base.sha((h['generations'](p.data)/'current.json').read_bytes()), erase=mode != 'erase-denied')
        state = p.data / 'profile/syspane/state' / base.sha(base.CASES['profile'].encode())
        nodes = []
        for path in (state, state/'recovery'):
            observed = path.lstat(); fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                held = os.fstat(fd)
                assert (observed.st_dev, observed.st_ino) == (held.st_dev, held.st_ino)
                assert held.st_uid == os.geteuid() and stat.S_IMODE(held.st_mode) == 0o700
                nodes.append(held)
            finally:
                os.close(fd)
        a, b = nodes
        context['directory'].update(path=str(state/'recovery'), uid=str(os.geteuid()), state_device=str(a.st_dev), state_inode=str(a.st_ino),
            recovery_device=str(b.st_dev), recovery_inode=str(b.st_ino))
        parts[3] = base.encoded(dict(policy=policy, recovery=None if mode == 'retention-denied' else context))
        return parts

    def open_profile(client, session='editor:S'):
        client.send('profile.read', dict(schema_version='0.2.0', query_id='P0', op='open', profile=base.CASES['profile'], editor_session=session))
        reply = client.receive(); assert reply['type'] == 'profile.chunk'
        return reply['body']

    def next_query(reply, query='Pnext'):
        out = h['next_query'](reply, query); out['schema_version'] = '0.2.0'; return out

    def download(client, parts, first=None, transfer=1, session='editor:S'):
        received = [bytearray() for _ in parts]; reply = first or open_profile(client, session); query = 'P0'; index = 0
        while True:
            assert reply['schema_version'] == '0.2.0' and reply['outcome'] == 'chunk' and reply['query_id'] == query
            assert reply['transfer_id'] == str(transfer) and reply['part_count'] == str(len(parts)) and reply['part'] == str(index)
            assert reply['revision'] == json.loads(parts[1])['revision'] and reply['policy_generation'] == '7'
            assert reply['part_bytes'] == str(len(parts[index])) and reply['offset'] == str(len(received[index]))
            assert reply['sha256'] == base.sha(parts[index])
            raw = bytes.fromhex(reply['hex']); assert raw.hex() == reply['hex'] and len(raw) == min(4096, len(parts[index])-len(received[index]))
            received[index].extend(raw)
            finished = len(received[index]) == len(parts[index])
            assert reply['complete'] == (finished and index+1 == len(parts))
            if finished:
                assert bytes(received[index]) == parts[index]
                index += 1
            if reply['complete']:
                break
            query = 'P'+str(index)+'-'+str(sum(map(len, received)))
            client.send('profile.read', next_query(reply, query)); message = client.receive()
            assert message['type'] == 'profile.chunk' and message['connection_id'] == 'C' and message['producer_epoch'] == client.epoch
            reply = message['body']
        record.setdefault('transfers', []).append(dict(epoch=client.epoch, transfer_id=str(transfer), context=json.loads(parts[3]),
            parts=[dict(bytes=len(v), sha256=base.sha(v)) for v in parts]))
        h['save']()

    with case('exact-native-context'):
        with parent(root('exact')) as p:
            p.await_ready(); client = Client(p); download(client, expected(p)); inspect(p.data); client.close()
            assert p.shutdown() == 0
    with case('commit-and-pinned-generation'):
        with parent(root('commit')) as p:
            p.await_ready(); client = Client(p); old = expected(p); first = open_profile(client)
            client.send('command', base.command()); answer = client.receive()
            assert answer['type'] == 'result' and answer['body']['outcome'] == 'accepted' and answer['body']['revision'] == '1'
            inspect(p.data, '1'); download(client, old, first)
            new = expected(p, 2, '1'); assert json.loads(old[3])['recovery']['generation'] != json.loads(new[3])['recovery']['generation']
            download(client, new, transfer=2); client.close(); assert p.shutdown() == 0
    with case('reconnect-new-scope'):
        data = root('reconnect')
        with parent(data) as p:
            p.await_ready(); client = Client(p); first = open_profile(client); client.close(); time.sleep(.05)
            client = Client(p); client.send('profile.read', next_query(first)); assert client.socket.recv(4096) == b''; client.close(); time.sleep(.05)
            client = Client(p); download(client, expected(p, 2, session='editor:T'), transfer=2, session='editor:T'); client.close(); assert p.shutdown() == 0
        with parent(data, epoch=base.CASES['replacement_epoch']) as p:
            p.await_ready(); client = Client(p)
            client.socket.sendall(base.packet(dict(type='profile.read', body=next_query(first), connection_id='C', producer_epoch=base.CASES['epoch'])))
            assert client.socket.recv(4096) == b''; client.close(); time.sleep(.05)
            client = Client(p); download(client, expected(p, session='editor:U'), session='editor:U'); client.close(); assert p.shutdown() == 0
    with case('retention-and-erase'):
        for mode in ('retention-denied', 'erase-denied'):
            with parent(root(mode), phase=mode) as p:
                p.await_ready(); client = Client(p); download(client, expected(p, mode=mode)); inspect(p.data); client.close(); assert p.shutdown() == 0
    with case('policy-withdrawal'):
        with parent(root('revocation')) as p:
            p.await_ready(); client = Client(p); first = open_profile(client); p.set_policy('deny')
            client.send('profile.read', next_query(first)); assert p.process.wait(timeout=4) == 126
            assert client.socket.recv(4096) == b''; inspect(p.data); client.close()
    with case('wrong-generation-oracle') as facts:
        with parent(root('oracle')) as p:
            p.await_ready(); client = Client(p); parts = expected(p)
            context = json.loads(parts[3]); context['recovery']['generation'] = '0'*64; parts[3] = base.encoded(context)
            detected = False
            try:
                download(client, parts)
            except AssertionError:
                detected = True
            assert detected; facts['wrong_generation_detected'] = True
            client.close(); assert p.shutdown() == 0


if __name__ == '__main__':
    base.main(exercise, DEFINITIONS)
