"""Independent native collection/consumer lifetime and original-measurement oracle."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import signal
import stat
import sys
import time
import uuid
from native_ipc import Process, Harness, events
from native_network import linux_rows
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/fault'))
from native_recovery import ObservedChild


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    if not path.exists():
        return []
    data = path.read_bytes()
    assert len(data) <= 4*1024*1024, 'private journal bound'
    return [json.loads(line) for line in data.split(b'\n')[:-1]]


def verify_source(records, before, after, lower, upper):
    assert len(records) >= 10 and set(before) == set(after), 'continuous source inventory'
    previous = None
    for index, row in enumerate(records):
        message = json.loads(row['payload'])
        doc = message['body']['snapshot']
        assert int(doc['generation']) == index+1, 'continuous generation'
        assert message['type'] == 'snapshot' and doc['completeness'] == 'complete'
        entities = {e['id']: e for e in doc['entities']}
        assert {e['identity']['native_index'] for e in entities.values()} == set(before)
        observations = {(o['entity_id'], o['field']): o for o in doc['observations']}
        for identity, entity in entities.items():
            native = entity['identity']['native_index']
            for direction in ('receive', 'transmit'):
                field = 'network.'+direction+'_bytes'
                counter, rate = observations[identity, field], observations[identity, field+'_per_second']
                assert counter['acquisition'] == 'success', 'real successful acquisition'
                value, stamp = int(counter['value']['data']), int(counter['measured_at']['nanoseconds'])
                assert before[native][direction] <= value <= after[native][direction], 'independent counter bracket'
                assert lower <= stamp <= int(row['now_ns']) <= upper, 'original clock bracket'
                if previous:
                    old = previous[identity, field]
                    elapsed = stamp-int(old['measured_at']['nanoseconds'])
                    delta = value-int(old['value']['data'])
                    assert elapsed > 0 and delta >= 0, 'advancing real acquisition'
                    expected = float(Fraction(delta*1_000_000_000, elapsed))
                    assert rate['sample_interval_ns'] == str(elapsed)
                    assert math.isclose(rate['value']['data'], expected, rel_tol=4e-15, abs_tol=1e-9), 'independent interval rate'
                else:
                    assert rate['value'] is None and rate['acquisition'] == 'pending'
        previous = observations


def run(executable, output, case):
    _, root = Harness(executable).endpoint()
    for name in ('h', 'd', 'v'):
        (root/name).mkdir(mode=0o700)
    record = {'case': 'CONSUMER-CONTINUITY.'+case, 'outcome': 'fail', 'started_at': datetime.now(timezone.utc).isoformat()}
    process = None
    held = {}
    faults = []
    source_pid = None
    killed = set()
    try:
        before = linux_rows()
        lower = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        process = Process([str(executable), 'continuity', str(root), 'revoke-on-exit' if case == 'REVOKE' else 'allow'])
        deadline = time.monotonic()+22
        current = None
        while process.process.poll() is None or process.reader.is_alive():
            assert time.monotonic() < deadline, 'bounded experiment'
            try:
                event = process.events.get(timeout=.025)
                kind = event.get('event')
                assert kind != 'error', 'native failure: '+str(event)
                if kind in ('source_spawned', 'consumer_spawned'):
                    pid = event['pid']
                    held[pid] = ObservedChild(pid)
                    assert os.getsid(pid) == os.getsid(process.process.pid), 'native session continuity'
                    if kind == 'source_spawned':
                        assert source_pid is None, 'collector restarted'
                        source_pid = pid
                    else:
                        assert source_pid == event['source_pid'] and not held[source_pid].exited(0)
                        for old in events(process, 'consumer_spawned')[:-1]:
                            assert held[old['pid']].exited(0), 'replacement overlaps old child'
                        current = event
            except queue.Empty:
                pass
            if current and current['pid'] not in killed:
                should_fault = case == 'CIRCUIT' or (case in ('CRASH', 'HANG', 'REVOKE') and not killed)
                received = rows(root/('consumer-'+current['connection']+'.jsonl'))
                if should_fault and received:
                    assert not held[source_pid].exited(0), 'collector lifetime before fault'
                    sig = signal.SIGSTOP if case == 'HANG' else signal.SIGKILL
                    signal.pidfd_send_signal(held[current['pid']].handle, sig)
                    killed.add(current['pid'])
                    faults.append({'pid': current['pid'], 'signal': int(sig), 'observed_ms': time.monotonic_ns()//1_000_000,
                                   'last_generation': json.loads(received[-1]['payload'])['body']['snapshot']['generation']})
        assert process.finish() == 0, 'native completion'
        after = linux_rows()
        upper = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        assert all(child.exited(2000) for child in held.values()), 'held descendant exit'
        spawned, stopped = events(process, 'consumer_spawned'), events(process, 'stopped')
        expected = {'LIVE': 1, 'CRASH': 2, 'HANG': 2, 'REVOKE': 1, 'CIRCUIT': 4}[case]
        assert len(spawned) == expected and len(stopped) == expected+1, 'bounded launches/exits'
        assert {e['pid'] for e in stopped} == set(held) and all(e['os_confirmed'] for e in stopped)
        records = rows(root/'source.jsonl')
        verify_source(records, before, after, lower, upper)
        originals = {json.loads(row['payload'])['body']['snapshot']['generation']: row for row in records}
        epoch = events(process, 'source_spawned')[0]['epoch']
        journals = []
        for child in spawned:
            path = root/('consumer-'+child['connection']+'.jsonl')
            received = rows(path)
            assert received, 'actual native import before outcome'
            for row in received:
                message = json.loads(row['payload'])
                original = originals[message['body']['snapshot']['generation']]
                body = json.loads(original['payload'])['body']
                assert message['connection_id'] == child['connection'] and message['producer_epoch'] == epoch
                assert message['body'] == body and row['projection'] == body['snapshot'], 'unaltered original snapshot/measurement'
                assert int(row['now_ns']) >= int(original['now_ns']), 'causal original delivery'
            info = path.stat()
            assert stat.S_IMODE(info.st_mode) == 0o600 and info.st_uid == os.geteuid()
            journals.append({'path': str(path), 'sha256': sha(path), 'samples': len(received)})
        failures = events(process, 'consumer_fault')
        assert len(failures) == len(faults), 'one retained failure per injected fault'
        for index, failure in enumerate(failures):
            assert failure['pid'] == faults[index]['pid'] and failure['backoff_ms'] == [1000, 2000, 4000, 4000][index]
            stop = next(e for e in stopped if e['pid'] == failure['pid'])
            assert stop['observed_ms'] >= failure['observed_ms']
            if index+1 < len(spawned):
                replacement = spawned[index+1]
                assert replacement['observed_ms'] >= stop['observed_ms']
                assert replacement['observed_ms']-failure['observed_ms'] >= failure['backoff_ms']
                assert replacement['last_failure'] == failure['reason']
                during = [r for r in records if stop['observed_ms'] <= r['observed_ms'] <= replacement['observed_ms']]
                assert during, 'new real source acquisition while no consumer exists'
        complete = events(process, 'complete')
        assert len(complete) == 1 and complete[0]['launches'] == expected
        if case == 'HANG':
            assert failures[0]['reason'] == 'subscription.expired', 'independent consumer lease'
            assert 2900 <= failures[0]['observed_ms']-faults[0]['observed_ms'] <= 3400, 'native lease deadline'
        if case == 'REVOKE':
            changed = events(process, 'consumer_policy')
            assert len(changed) == 1 and changed[0]['revision'] == 8 and not changed[0]['permitted']
            assert complete[0]['consumer_policy_revision'] == 8
            assert sum(r['observed_ms'] > changed[0]['observed_ms'] for r in records) >= 5, 'independent authorized collection continues'
        assert complete[0]['circuit_open'] == (case == 'CIRCUIT')
        if case == 'CIRCUIT':
            opened = events(process, 'consumer_circuit_open')
            assert len(opened) == 1 and complete[0]['observed_ms']-opened[0]['observed_ms'] >= 2000
        record.update(outcome='pass', source_journal={'path': str(root/'source.jsonl'), 'sha256': sha(root/'source.jsonl'),
                      'samples': len(records)}, consumer_journals=journals, held_exits=True)
    except Exception as error:
        record['error'] = str(error)
    finally:
        if process:
            process.stop()
            record['process'] = process.record()
        for child in held.values():
            record.setdefault('cleanup_exits', {})[str(child.pid)] = child.exited(2000)
            child.close()
        record['faults'] = faults
        record['private_root'] = str(root)
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    return record


def main():
    executable, output = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    directory = output/('consumer-continuity-'+uuid.uuid4().hex[:10])
    directory.mkdir(parents=True)
    result = {'family': 'CONSUMER-CONTINUITY', 'artifact_sha256': sha(executable), 'cases': []}
    for case in sys.argv[3:] or ('LIVE', 'CRASH', 'HANG', 'REVOKE', 'CIRCUIT'):
        record = run(executable, directory/(case+'.json'), case)
        result['cases'].append(record)
        print(case, record['outcome'], record.get('error', ''), flush=True)
    result['outcome'] = 'pass' if all(r['outcome'] == 'pass' for r in result['cases']) else 'fail'
    (directory/'result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (output/'CONSUMER-CONTINUITY.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Native evidence:', directory/'result.json', flush=True)
    raise SystemExit(result['outcome'] != 'pass')


if __name__ == '__main__':
    main()
