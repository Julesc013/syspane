"""Independent live proc/sysfs bounds and exact interval oracle; no system changes."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid


def ids(text):
    result = []
    for item in text.strip().split(','):
        endpoints = [int(n) for n in item.split('-')]
        result.extend(range(endpoints[0], endpoints[-1] + 1))
    assert len(result) == len(set(result)) and 0 < len(result) <= 8192
    return sorted(result)


def observation():
    start = time.monotonic_ns()
    online = ids(Path('/sys/devices/system/cpu/online').read_text())
    text = Path('/proc/stat').read_text()
    counters = {int(row[0][3:]): list(map(int, row[1:]))
                for row in (line.split() for line in text.splitlines())
                if row[0].startswith('cpu') and row[0] != 'cpu'}
    topology = {}
    for cpu in online:
        directory = Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
        topology[cpu] = dict(package=int((directory/'physical_package_id').read_text()),
                             core=int((directory/'core_id').read_text()),
                             peers=ids((directory/'core_cpus_list').read_text()))
    assert online == ids(Path('/sys/devices/system/cpu/online').read_text())
    return dict(start=start, end=time.monotonic_ns(), online=online,
                stat=text, counters=counters, topology=topology,
                hz=os.sysconf('SC_CLK_TCK'))


def verify(before, value, after):
    assert value['uid'] == os.getuid() != 0
    assert value['cancelled'] is True and value['timed_out'] is True
    assert value['definition'] == 'linux:execution-ticks-v1'
    assert before['online'] == after['online']
    captures = [value['first'], value['second']]
    assert before['end'] <= captures[0]['start'] <= captures[0]['end'] < captures[1]['start'] <= captures[1]['end'] <= after['start']
    for capture in captures:
        assert capture['hz'] == before['hz'] == after['hz'] > 0
        assert [r['index'] for r in capture['rows']] == before['online']
        for row in capture['rows']:
            cpu = row['index']
            assert {key: row[key] for key in ('package', 'core', 'peers')} == before['topology'][cpu] == after['topology'][cpu]
            raw = row['accounting'] + (row['guest'] or [])
            assert len(raw) == len(before['counters'][cpu]) == len(after['counters'][cpu])
            for low, measured, high in zip(before['counters'][cpu], raw, after['counters'][cpu]):
                assert low <= measured <= high, (cpu, low, measured, high)
    assert value['pending'] == 0, 'live interval pending: preserve evidence, no invented ratio'
    expected = {}
    for first, second in zip(captures[0]['rows'], captures[1]['rows']):
        delta = [b-a for a, b in zip(first['accounting'], second['accounting'])]
        assert all(n >= 0 for n in delta)
        total = sum(delta)
        busy = sum(delta[n] for n in (0, 1, 2, 5, 6))
        assert total > 0
        expected[f"linux:cpu:{first['index']}"] = dict(busy=busy, total=total)
    actual = {row['id']: dict(busy=row['busy'], total=row['total']) for row in value['ratios']}
    assert len(value['ratios']) == len(expected) and actual == expected
    assert value['aggregate'] == dict(busy=sum(r['busy'] for r in expected.values()),
                                     total=sum(r['total'] for r in expected.values()),
                                     interval_ns=captures[1]['start']-captures[0]['start'])


def main():
    executable, evidence_root = map(Path, sys.argv[1:])
    build = executable.resolve().parent
    assert (build/'.syspane-owner.json').is_file()
    assert evidence_root.resolve() == build/'native-evidence'
    folder = evidence_root/('linux-processor-'+uuid.uuid4().hex[:12])
    folder.mkdir(parents=True)
    result = dict(environment=dict(uid=os.getuid(), uname=list(platform.uname()),
                                  python=sys.version, clock=time.get_clock_info('monotonic').__dict__),
                  executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest())
    try:
        result['before'] = observation()
        run = subprocess.run([str(executable)], capture_output=True, timeout=30)
        (folder/'stdout.json').write_bytes(run.stdout)
        (folder/'stderr.txt').write_bytes(run.stderr)
        result['exit'] = run.returncode
        result['after'] = observation()
        assert run.returncode == 0, run.stderr.decode(errors='replace')
        result['probe'] = json.loads(run.stdout)
        verify(result['before'], result['probe'], result['after'])
        result['outcome'] = 'pass'
        print(f"Complete {len(result['before']['online'])}-CPU native accounting/topology and independent exact interval: pass; {folder}")
    except BaseException as error:
        result['outcome'] = 'fail'
        result['error'] = repr(error)
        raise
    finally:
        (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
