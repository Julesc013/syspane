"""Native Show Desktop stimuli and independent, bounded root-pixel observations."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time

from native_oracle import ROOT
from native_x11_host import rgb_record
from x11_recovery import ResourceOwner
from oracle import evaluate, pack_frame
from gnome_composition import FIXTURE as COMPOSITION, judge_samples, settings

FIXTURE_PATH = ROOT / 'tests/desktop/fixtures/gnome-reveal.json'
FIXTURE = json.loads(FIXTURE_PATH.read_text())


def binding(environment):
    result = subprocess.run(['/usr/bin/gsettings', 'get', 'org.gnome.desktop.wm.keybindings', 'show-desktop'],
                            env=environment, capture_output=True, text=True, timeout=1, check=True)
    if result.stderr or len(result.stdout) > 128:
        raise ValueError('native binding observation invalid')
    return result.stdout.strip()


def issue(environment, method, argument):
    result = subprocess.run(['/usr/bin/gdbus', 'call', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
                             '--dest', 'org.gnome.Shell', '--object-path', '/org/syspane/LabMarker',
                             '--method', 'org.syspane.LabMarker.' + method, argument],
                            env=environment, capture_output=True, text=True, timeout=1, check=True)
    if result.stdout.strip() != '()':
        raise ValueError('laboratory stimulus reply differs')


def foreground_identity(display, pid):
    owner = ResourceOwner(display)
    matches = []
    for window in display.property(display.root, '_NET_CLIENT_LIST_STACKING'):
        binding = owner.pid(window)
        if not binding or binding[0] != pid:
            continue
        native_type = display.property(window, '_NET_WM_WINDOW_TYPE')
        if native_type != [display.atom('_NET_WM_WINDOW_TYPE_NORMAL')]:
            raise ValueError('foreground control is not a normal window')
        x, y, child = C.c_int(), C.c_int(), C.c_ulong()
        if not display.x.XTranslateCoordinates(display.handle, window, display.root, 0, 0, C.byref(x), C.byref(y), C.byref(child)):
            raise ValueError('foreground coordinates unavailable')
        # XGetGeometry on the client, independently of GTK's requested allocation.
        root, gx, gy, width, height, border, depth = C.c_ulong(), C.c_int(), C.c_int(), C.c_uint(), C.c_uint(), C.c_uint(), C.c_uint()
        display.x.XGetGeometry.argtypes = [C.c_void_p, C.c_ulong, C.POINTER(C.c_ulong), C.POINTER(C.c_int), C.POINTER(C.c_int),
                                           C.POINTER(C.c_uint), C.POINTER(C.c_uint), C.POINTER(C.c_uint), C.POINTER(C.c_uint)]
        if not display.x.XGetGeometry(display.handle, window, C.byref(root), C.byref(gx), C.byref(gy), C.byref(width), C.byref(height), C.byref(border), C.byref(depth)):
            raise ValueError('foreground geometry unavailable')
        geometry = [x.value, y.value, width.value, height.value]
        if geometry != FIXTURE['window']:
            raise ValueError('foreground geometry differs: ' + str(geometry))
        path = Path(f'/proc/{pid}')
        raw = (path / 'cmdline').read_bytes()
        if len(raw) > 16384:
            raise ValueError('foreground argument capacity')
        arguments = [x.decode() for x in raw.rstrip(b'\0').split(b'\0')]
        if str(ROOT / 'tests/desktop/gnome_foreground.py') not in arguments:
            raise ValueError('foreground script identity')
        stat = (path / 'stat').read_text().rsplit(')', 1)[1].split()
        if int(stat[2]) != pid or int(stat[3]) != pid:
            raise ValueError('foreground process group/session differs')
        matches.append({'window': window, 'pid': pid, 'pid_origin': 'XResQueryClientIds',
                        'resource_base': binding[1], 'resource_mask': binding[2], 'arguments': arguments,
                        'process_group': int(stat[2]), 'session': int(stat[3]), 'start_ticks': int(stat[19]),
                        'executable': str((path / 'exe').resolve(strict=True)),
                        'geometry': geometry, 'type': native_type, 'normal_type_atom': display.atom('_NET_WM_WINDOW_TYPE_NORMAL')})
    if len(matches) != 1:
        raise ValueError('one retained normal foreground window required')
    return matches[0]


def judge(result, composition):
    from record_gnome_host import rgb
    trace = result['trace']
    if trace['start_us'] != 0 or trace['end_us'] != FIXTURE['duration_us'] or [s['generation'] for s in trace['stimuli']] != [4, 5, 6]:
        raise ValueError('reveal marker scenario differs')
    for stimulus, scheduled in zip(trace['stimuli'], FIXTURE['generation_us']):
        if not scheduled <= stimulus['at_us'] <= scheduled + 50000:
            raise ValueError('generation stimulus scheduling budget')
    actions, faults = result['actions'], result['faults']
    if len(actions) != 2 or len(faults) != (2 if result['control'] == 'transient-blank' else 0):
        raise ValueError('native action/fault completeness')
    for rows, schedule in [(actions, FIXTURE['actions_us']), (faults, FIXTURE['blank_us'])]:
        for row, scheduled in zip(rows, schedule):
            if not scheduled <= row['start_us'] <= scheduled + 50000 or not row['start_us'] <= row['end_us'] <= row['start_us'] + 50000:
                raise ValueError('native action scheduling/duration budget')
    if any(row['performed'] != (result['control'] != 'no-action') for row in actions):
        raise ValueError('native action control differs')
    if faults and [row['enabled'] for row in faults] != [False, True]:
        raise ValueError('blank/restore fault ordering')
    marker = evaluate(trace)
    if any(reason.startswith('capture.') for reason in marker['uncertainty']):
        raise ValueError('marker capture coverage incomplete')
    samples = result['samples']
    if len(samples) != len(trace['frames']):
        raise ValueError('missing paired reveal capture')
    size = COMPOSITION['overlap'][2] * COMPOSITION['overlap'][3] * 3
    calibrated = [rgb(s['frames'][0]['pixels'], size) for s in composition['calibrations']]
    overlaps = []
    states, successes, joint_successes, focus_successes = [], [[], [], []], [[], [], []], [[], [], []]
    background_ok = True
    for frame, row in zip(trace['frames'], samples):
        if not frame['start_us'] <= frame['end_us'] <= row['overlap_start_us'] <= row['foreground_start_us'] <= row['background_start_us'] <= row['state_start_us'] <= row['end_us']:
            raise ValueError('reveal paired capture order')
        overlaps.append({'marker_start_us': frame['start_us'], 'start_us': row['overlap_start_us'], 'end_us': row['end_us'], 'pixels': row['overlap']})
        background_ok &= rgb(row['background'], 128*96*3) == bytes(COMPOSITION['background_rgb']) * (128*96)
        foreground = rgb(row['foreground'], 20*20*3)
        at = frame['start_us']
        phase = 0 if at < actions[0]['start_us'] else (1 if at < actions[1]['start_us'] else 2)
        expected_color = COMPOSITION['background_rgb'] if phase == 1 else FIXTURE['foreground_rgb']
        native = row['native']
        visible = native['showing_desktop'] == [int(phase == 1)] and foreground == bytes(expected_color) * (20*20)
        focused = phase == 1 or native['active_window'] == [result['foreground']['window']]
        if visible:
            successes[phase].append(row['end_us'])
        if focused:
            focus_successes[phase].append(row['end_us'])
        if visible and focused:
            joint_successes[phase].append(row['end_us'])
        required = phase == 0 or at >= actions[phase-1]['end_us'] + FIXTURE['transition_budget_us']
        states.append({'at_us': at, 'phase': phase, 'required': required,
                       'visible': visible, 'focused': focused, 'matches': visible and focused})
    composition_result = judge_samples(calibrated[2], overlaps, calibrated[:2])
    transitions = all(successes[p] and successes[p][0] <= actions[p-1]['end_us'] + FIXTURE['transition_budget_us'] for p in (1, 2))
    if any(sum(s['required'] and s['phase'] == phase for s in states) < 3 for phase in (0, 1, 2)):
        raise ValueError('native transition coverage incomplete')
    visual_reveal = transitions and all(s['visible'] for s in states if s['required'])
    focus = (all(s['focused'] for s in states if s['required']) and bool(focus_successes[2]) and
             focus_successes[2][0] <= actions[1]['end_us'] + FIXTURE['transition_budget_us'])
    joint_transitions = all(joint_successes[p] and joint_successes[p][0] <= actions[p-1]['end_us'] + FIXTURE['transition_budget_us'] for p in (1, 2))
    reveal = joint_transitions and all(s['matches'] for s in states if s['required'])
    return {'marker': marker, 'composition': composition_result,
            'background': 'pass' if background_ok else 'fail',
            'visual_reveal': 'pass' if visual_reveal else 'fail', 'focus': 'pass' if focus else 'fail',
            'reveal': 'pass' if reveal else 'fail', 'states': states,
            'transition_latency_us': [successes[p][0] - actions[p-1]['end_us'] if successes[p] else None for p in (1, 2)],
            'outcome': 'pass' if reveal and background_ok and marker['outcome'] == 'pass' and composition_result['icons'] == 'pass' and composition_result['rectangle'] == 'pass' else 'fail'}


def observe(display, environment, foreground_pid, workspace, composition):
    journal = (workspace / 'reveal.jsonl').open('x', encoding='utf-8', newline='\n')
    count, descriptor = 0, None
    def preserve(kind, value):
        nonlocal count
        count += 1
        if count > 180:
            raise ValueError('reveal journal record capacity')
        journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
        journal.flush()
        if journal.tell() > 8 * 1024**2:
            raise ValueError('reveal journal byte capacity')
    try:
        if composition['outcome'] != 'pass':
            raise ValueError('live composition prerequisite failed')
        identity = foreground_identity(display, foreground_pid)
        descriptor = os.pidfd_open(foreground_pid)
        poller = select.poll()
        poller.register(descriptor, select.POLLIN)
        result = {'version': '0.1.0', 'control': environment['SYSPANE_GNOME_REVEAL'],
                  'fixture_sha256': hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
                  'foreground': identity, 'binding_before': binding(environment),
                  'background_settings_before': settings(environment), 'actions': [], 'faults': [], 'samples': []}
        if result['binding_before'] != FIXTURE['binding']:
            raise ValueError('explicit Show Desktop binding differs')
        display.xtest.XTestFakeMotionEvent.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_ulong]
        display.xtest.XTestFakeButtonEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
        if not display.xtest.XTestFakeMotionEvent(display.handle, -1, 600, 110, 0):
            raise ValueError('foreground pointer motion failed')
        for pressed in (True, False):
            if not display.xtest.XTestFakeButtonEvent(display.handle, 1, pressed, 0):
                raise ValueError('foreground activation click failed')
        display.x.XFlush(display.handle)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            native = display.structure()
            pixels = display.capture(*FIXTURE['foreground_witness'])
            if native['active_window'] == [identity['window']] and native['showing_desktop'] == [0] and pixels == bytes(FIXTURE['foreground_rgb']) * (20*20):
                break
            time.sleep(.05)
        else:
            preserve('activation_failed', {'native': native, 'pixels': rgb_record(pixels)})
            raise ValueError('foreground activation/pixel prerequisite failed: ' + str(native))
        preserve('prepared', {**result, 'native': native, 'pixels': rgb_record(pixels)})
        issue(environment, 'SetGeneration', '4')
        time.sleep(.25)
        trace = {'version': '0.1.0', 'start_us': 0, 'end_us': FIXTURE['duration_us'],
                 'stimuli': [{'at_us': 0, 'generation': 4}], 'frames': []}
        result['trace'] = trace
        started = time.monotonic_ns()
        result['started_monotonic_ns'] = started
        now = lambda: (time.monotonic_ns() - started) // 1000
        next_frame, generation = 0, 5
        while now() < trace['end_us']:
            at = now()
            if generation <= 6 and at >= (generation - 4) * 800000:
                stimulus = {'at_us': at, 'generation': generation}
                trace['stimuli'].append(stimulus)
                issue(environment, 'SetGeneration', str(generation))
                preserve('generation', stimulus)
                generation += 1
            if len(result['actions']) < 2 and now() >= FIXTURE['actions_us'][len(result['actions'])]:
                action = {'start_us': now(), 'performed': result['control'] != 'no-action'}
                if action['performed']:
                    display.reveal_key()
                action['end_us'] = now()
                result['actions'].append(action)
                preserve('action', action)
            if result['control'] == 'transient-blank' and len(result['faults']) < 2 and now() >= FIXTURE['blank_us'][len(result['faults'])]:
                fault = {'start_us': now(), 'enabled': bool(result['faults'])}
                issue(environment, 'SetSceneEnabled', 'true' if fault['enabled'] else 'false')
                fault['end_us'] = now()
                result['faults'].append(fault)
                preserve('fault', fault)
            if now() >= next_frame and now() < trace['end_us'] - 10000:
                before = now()
                pixels = display.capture(300, 200, 128, 96)
                frame = pack_frame(pixels, before, now())
                row = {'overlap_start_us': now()}
                row['overlap'] = rgb_record(display.capture(*COMPOSITION['overlap']))
                row['foreground_start_us'] = now()
                row['foreground'] = rgb_record(display.capture(*FIXTURE['foreground_witness']))
                row['background_start_us'] = now()
                row['background'] = rgb_record(display.capture(*COMPOSITION['background_witness']))
                row['state_start_us'] = now()
                row['native'] = display.structure()
                row['end_us'] = now()
                trace['frames'].append(frame)
                result['samples'].append(row)
                preserve('sample', {'marker': frame, 'observation': row})
                if poller.poll(0):
                    raise ValueError('foreground process exited during trace')
                next_frame += 50000
            time.sleep(.002)
        result['binding_after'] = binding(environment)
        result['background_settings_after'] = settings(environment)
        if result['binding_after'] != result['binding_before'] or result['background_settings_after'] != result['background_settings_before']:
            raise ValueError('settings changed during reveal')
        if foreground_identity(display, foreground_pid) != identity or poller.poll(0):
            raise ValueError('foreground lifetime/geometry changed')
        result['evaluation'] = judge(result, composition)
        result['final_desktop'] = rgb_record(display.capture(0, 0, 800, 600))
        preserve('completed', {'evaluation': result['evaluation'], 'binding_after': result['binding_after'],
                               'background_settings_after': result['background_settings_after']})
        return result
    except Exception as error:
        preserve('error', {'message': type(error).__name__ + ': ' + str(error)})
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        journal.close()
