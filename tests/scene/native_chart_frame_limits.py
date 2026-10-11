"""Bounded wire-to-native-frame and semantic projection checks; not GUI timing qualification."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import selectors
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'source/build'))
from check_text_runtime import verify as verify_text
from check_surface_runtime import verify as verify_surface
import chart_frame_oracle as oracle

CASES = ROOT/'tests/scene/chart-frame-limits-cases.json'
EXPECTED = json.loads(CASES.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def fitting_frame(points, mixed):
    widget, row = oracle.chart(points)
    widgets, rows = [widget], [row]
    if mixed:
        table, table_row = oracle.table()
        widgets.append(table)
        rows.append(table_row)
    return dict(widgets=widgets, rows=rows, display_pixels=1600*2048)

def verify(record, expected):
    assert record == expected, 'frame differs from independent literal oracle'

def controls():
    expected = fitting_frame(oracle.sequence(3), True)
    mutations = []
    bad = copy.deepcopy(expected); bad['widgets'][0]['points'].pop(); mutations.append(bad)
    bad = copy.deepcopy(expected); bad['widgets'][0]['points'][1]['joins_previous'] = False; mutations.append(bad)
    bad = copy.deepcopy(expected); bad['rows'][1]['children'][0]['children'][0]['information'] = 'Wrong'; mutations.append(bad)
    for bad in mutations:
        try: verify(bad, expected)
        except AssertionError: pass
        else: raise AssertionError('oracle accepted a deliberate mutation')
    return len(mutations)

def execute(command, folder):
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    selector = selectors.DefaultSelector()
    files = [folder/'stdout.jsonl', folder/'stderr.txt']
    streams = [p.open('wb') for p in files]
    counts = [0, 0]
    limits = [EXPECTED['stdout_bytes'], EXPECTED['stderr_bytes']]
    try:
        for index, pipe in enumerate((proc.stdout, proc.stderr)):
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ, index)
        while selector.get_map():
            assert time.monotonic()-started < EXPECTED['child_seconds'], 'child deadline'
            for key, _ in selector.select(.1):
                block = os.read(key.fd, 65536)
                if not block:
                    selector.unregister(key.fileobj)
                    continue
                index = key.data
                streams[index].write(block[:limits[index]-counts[index]])
                counts[index] += len(block)
                assert counts[index] <= limits[index], 'child output bound'
        assert proc.wait(timeout=max(.001, EXPECTED['child_seconds']-(time.monotonic()-started))) == 0, 'native child failure'
    finally:
        if proc.poll() is None: proc.kill(); proc.wait(timeout=5)
        selector.close()
        for stream in streams: stream.close()
        for pipe in (proc.stdout, proc.stderr): pipe.close()
        (folder/'process.json').write_text(json.dumps(dict(command=command, exit=proc.returncode,
            elapsed_ms=(time.monotonic()-started)*1000, bytes=counts), indent=2)+'\n')

def check(folder, mixed, threshold, group):
    records = [json.loads(line) for line in (folder/'stdout.jsonl').read_bytes().splitlines()]
    assert [r['case'] for r in records] == EXPECTED['groups'][group], 'missing or extra case'
    cleared = 0
    outcomes = []
    for record in records:
        name = record['case']
        assert record['point_bytes'] == EXPECTED['point_bytes'], 'ABI differs'
        assert record['clears'] > cleared, 'owner did not clear prior presentation'
        cleared = record['clears']
        if name in ('FIT', 'RECOVER', 'FRESH'):
            assert record['code'] == 'ready', (name, record['code'], record['reason'])
            points = oracle.sequence(threshold['points']) if name == 'FIT' else [(20000000000,4098,False)] if name == 'RECOVER' else [(21000000000,4099,False)]
            expected = fitting_frame(points, mixed)
            verify(record['frame'], expected)
            if name == 'FIT': assert sum(w['bytes'] for w in record['frame']['widgets']) == threshold['fitting_bytes']
        elif name == 'REGRANT':
            assert record['code'] in ('ready','degraded') and record['frame'] is not None
            assert all(not r['children'] for r in record['frame']['rows']), 'old semantic rows survived regrant'
            assert not record['frame']['widgets'][0]['points'], 'old points survived regrant'
            assert '10 byte' not in json.dumps(record['frame']), 'old value survived regrant'
        else:
            assert record['frame'] is None, 'partial disclosure on refusal'
            expected_code = 'restricted' if name == 'REVOKE' else 'closed' if name == 'CLOSE' else 'alternative'
            assert record['code'] == expected_code, (name, record['code'], record['reason'])
            if expected_code == 'alternative': assert record['reason'] == 'surface.capacity'
        outcomes.append(dict(case=name, outcome='pass', code=record['code'], clears=cleared))
    return outcomes

def main():
    exe, evidence = map(Path, sys.argv[1:3])
    folder = evidence/('chart-frame-limits-'+uuid.uuid4().hex[:12]); folder.mkdir()
    report = dict(family='CHART-FRAME-LIMITS', outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
                  executable_sha256=sha(exe), inputs={p.relative_to(ROOT).as_posix():sha(p) for p in
                  [Path(__file__), CASES, Path(oracle.__file__), ROOT/'tests/scene/chart_frame_limits.hpp',
                   ROOT/'source/build/text-runtime.json', ROOT/'source/build/surface-runtime.json']}, cases=[])
    try:
        verify_text(); verify_surface()
        report['oracle_mutations_rejected'] = controls()
        failures = []
        for mode, mixed in [('chart',False), ('mixed',True)]:
            threshold = oracle.boundary(mixed)
            assert threshold == EXPECTED[mode], 'frozen arithmetic boundary differs'
            for group in EXPECTED['groups']:
                child = folder/(mode+'-'+group); child.mkdir()
                case = dict(scene=mode, group=group, boundary=threshold, outcome='fail')
                try:
                    execute([str(exe), str(ROOT/'spec/fixtures/valid'), 'HISTORY-LIMITS', mode, str(threshold['points']), group], child)
                    case['checks'] = check(child, mixed, threshold, group)
                    case['outcome'] = 'pass'
                except Exception as exc:
                    case['error'] = repr(exc)
                    failures.append(mode+'-'+group)
                report['cases'].append(case)
        assert not failures, 'failed scenes: '+', '.join(failures)
        report['outcome'] = 'pass'
    except Exception as exc:
        report['error'] = repr(exc)
        raise
    finally:
        report['files'] = {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
        (folder/'result.json').write_text(json.dumps(report, indent=2)+'\n')
        print(folder/'result.json', report['outcome'])

if __name__ == '__main__': main()
