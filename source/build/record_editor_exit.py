"""Revalidate existing independent editor-exit evidence; never launch a desktop."""
import argparse
import hashlib
import json
from pathlib import Path

CASES = {'KEY-LIVE', 'KEY-FROZEN', 'BUTTON-FROZEN', 'LOCKS-FROZEN', 'DRAG-FROZEN',
         'MAPPING-LOSS', 'OWNER-LOSS', 'EDITOR-CRASH', 'GRAB-CONFLICT'}


def require(value, code):
    if not value:
        raise ValueError(code)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_facts(record):
    require(record['family'] == 'EDITOR-EXIT-01' and record['result'] == 'pass', 'family/outcome')
    rows = record['cases']
    require(len(rows) == len(CASES) and {r['case'] for r in rows} == CASES, 'case coverage')
    for row in rows:
        name = row['case']
        require(row['result'] == 'pass' and row['observer_exit'] == 0, 'observer outcome')
        require(row['display_exit'] == 0 and row['shortcut_released'] is True, 'native resource release')
        require(row['baseline_pixel'] == '116633', 'witness baseline')
        events = row['owner_events']
        if name == 'GRAB-CONFLICT':
            require(row['admission'] == 'denied_before_child' and not events and 'child_pid' not in row, 'admission denial')
            continue
        require(row['parent_verified'] is True and row['child_exit_at_cleanup'] is True, 'held native child')
        require(row['child_pid'] != row['owner_pid'] and row['child_executable_sha256'] == record['executable_sha256'], 'executable ownership')
        require(row['obstructed_pixel'] == 'cc2233' and row['input_obstructed'] is True and row['restored_pixel'] == '116633', 'external pixels/input')
        require(0 <= row['native_exit_ns'] - row['stimulus_ns'] <= row['input_restored_ns'] - row['stimulus_ns'] <= 1_500_000_000, 'independent recovery deadline')
        require(events and events[0]['event'] == 'child' and events[0]['value'] == row['child_pid'], 'child launch')
        require(all(a['at_ms'] <= b['at_ms'] for a, b in zip(events, events[1:])), 'event order')
        require(not any(e['event'] in ('deadline', 'unconfirmed') for e in events), 'confirmed exit only')
        if name == 'OWNER-LOSS':
            require(len(events) == 1, 'owner-loss trace')
            continue
        cooperative = name in ('KEY-LIVE', 'MAPPING-LOSS')
        require(events[-1]['event'] == ('child_exit' if cooperative else 'child_signal') and events[-1]['value'] == (0 if cooperative else 9), 'observed exit status')
        if name == 'EDITOR-CRASH':
            require(len(events) == 2, 'spontaneous child exit')
            continue
        reason = 'native_exit' if name == 'BUTTON-FROZEN' else 'mapping_lost' if name == 'MAPPING-LOSS' else 'keyboard_exit'
        require(events[1]['event'] == reason and events[1]['value'] == row['child_pid'], 'exit stimulus')
        if 'FROZEN' in name:
            require(row['stopped_before_stimulus'] is True, 'native stopped child')
            require(len(events) == 4 and events[2]['event'] == 'force_stop' and events[2]['value'] == row['child_pid'], 'bounded escalation')
            require(250 <= events[2]['at_ms'] - events[1]['at_ms'] < 1500, 'cooperative grace')
        else:
            require(len(events) == 3, 'cooperative trace')
        if name == 'KEY-LIVE':
            require(row['ordinary_and_shifted_ignored'] is True, 'ordinary keyboard input')
        if name == 'LOCKS-FROZEN':
            require(row['lock_state'] & 18 == 18, 'lock stimulus')
        if name == 'DRAG-FROZEN':
            require(row['drag_state'] & 256, 'held pointer stimulus')
        if name == 'BUTTON-FROZEN':
            button = row['native_button']
            require(100 <= button['width'] <= 800 and 20 <= button['height'] <= 100 and
                    0 <= button['root_x'] <= 800 - button['width'] and 0 <= button['root_y'] <= 100 - button['height'], 'reserved native recovery strip')
    return {'family': 'EDITOR-EXIT-01', 'outcome': 'pass', 'cases': len(rows), 'scope': 'owned-X11 editor lifetime experiment'}


def validate(path, root, executable):
    record = json.loads(path.read_text())
    result = validate_facts(record)
    require(sha(executable) == record['executable_sha256'], 'current executable identity')
    for name, digest in record['source_inputs'].items():
        target = (root / name).resolve()
        require(target.is_relative_to(root.resolve()) and sha(target) == digest, 'current source identity')
    for row in record['cases']:
        original = path.with_suffix('') / row['case']
        local = json.loads((original / 'result.json').read_text())
        require(all(row.get(key) == value for key, value in local.items()), 'original observer facts')
        out, err = original / 'owner.stdout', original / 'owner.stderr'
        require(sha(out) == row['owner_stdout_sha256'] and sha(err) == row['owner_stderr_sha256'], 'original native journals')
        require([json.loads(line) for line in out.read_text().splitlines()] == row['owner_events'], 'original native events')
        require(err.read_text() == ('editor.shortcut_unavailable\n' if row['case'] == 'GRAB-CONFLICT' else ''), 'native diagnostic')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('executable', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.report, Path(__file__).resolve().parents[2], args.executable)))
