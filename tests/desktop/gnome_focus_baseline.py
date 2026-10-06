"""Independent native focus baselines and real keyboard receipt on an owned desktop."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import time

from gnome_composition import FIXTURE as SCENE, bind_icon_window, masks, settings
from gnome_reveal import FIXTURE, binding, foreground_identity
from native_x11_host import rgb_record
from record_gnome_host import rgb

MODES = {'shell': [], 'ding': ['ding@rastersoft.com'],
         'candidate': ['ding@rastersoft.com', 'syspane-lab-marker@syspane.invalid']}


def extensions(environment):
    value = subprocess.run(['/usr/bin/gsettings', 'get', 'org.gnome.shell', 'enabled-extensions'],
                           env=environment, capture_output=True, text=True, timeout=1, check=True)
    if value.stderr or len(value.stdout) > 512:
        raise ValueError('extension settings observation invalid')
    # GVariant prints this string array using the same quoted string grammar as JSON
    # after single-quote substitution; only the three fixed extension identities are valid.
    encoded = value.stdout.strip().removeprefix('@as ')
    return json.loads(encoded.replace("'", '"'))


def activate(display, identity):
    display.xtest.XTestFakeMotionEvent.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_ulong]
    display.xtest.XTestFakeButtonEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
    if not display.xtest.XTestFakeMotionEvent(display.handle, -1, 600, 110, 0):
        raise ValueError('foreground motion failed')
    for pressed in (True, False):
        if not display.xtest.XTestFakeButtonEvent(display.handle, 1, pressed, 0):
            raise ValueError('foreground click failed')
    display.x.XFlush(display.handle)
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        native = display.structure()
        pixels = display.capture(*FIXTURE['foreground_witness'])
        if native['active_window'] == [identity['window']] and native['showing_desktop'] == [0] and pixels == bytes(FIXTURE['foreground_rgb']) * 400:
            return {'native': native, 'pixels': rgb_record(pixels), 'at_ns': time.monotonic_ns()}
        time.sleep(.05)
    raise ValueError('foreground activation prerequisite failed')


def key(display, name):
    code = display.x.XKeysymToKeycode(display.handle, display.x.XStringToKeysym(name.encode()))
    if not code:
        raise ValueError('native key unavailable')
    started = time.monotonic_ns()
    for pressed in (True, False):
        if not display.xtest.XTestFakeKeyEvent(display.handle, code, pressed, 0):
            raise ValueError('native key injection failed')
    display.x.XFlush(display.handle)
    return {'key': name, 'hardware_keycode': code, 'started_ns': started, 'finished_ns': time.monotonic_ns()}


def event_file(workspace):
    path = workspace / 'foreground-events.jsonl'
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        if not stat.S_ISREG(identity.st_mode) or stat.S_IMODE(identity.st_mode) != 0o600 or identity.st_uid != os.geteuid() or identity.st_size > 16384:
            raise ValueError('private bounded key journal required')
        raw = os.read(descriptor, 16385)
        if len(raw) != identity.st_size or (raw and not raw.endswith(b'\n')):
            raise ValueError('incomplete key journal')
        events = [json.loads(line) for line in raw.splitlines()]
        if len(events) > 16:
            raise ValueError('key journal event capacity')
        return {'device': identity.st_dev, 'inode': identity.st_ino, 'uid': identity.st_uid,
                'mode': stat.S_IMODE(identity.st_mode), 'bytes': len(raw),
                'sha256': hashlib.sha256(raw).hexdigest(), 'events': events}
    finally:
        os.close(descriptor)


def role(native, foreground, icon):
    active = native['active_window']
    return 'foreground' if active == [foreground] else ('icon' if icon and active == [icon] else ('none' if active in ([], [0]) else 'other'))


def keyboard(result):
    before, first, last = [result[k] for k in ['event_file_before', 'events_after_f9', 'events_after_f10']]
    identity = lambda value: [value[k] for k in ['device','inode','uid','mode']]
    if before['events'] or identity(before) != identity(first) or identity(first) != identity(last) or last['events'][:len(first['events'])] != first['events']:
        raise ValueError('keyboard journal lifetime/prefix changed')
    events, previous = last['events'], 0
    if len(events) not in (1,2) or [e['key'] for e in events] not in (['F10'], ['F9','F10']):
        raise ValueError('keyboard controls incomplete or repeated')
    for event in events:
        stimulus = result['unfocused_key'] if event['key']=='F9' else result['focused_key']
        if (event['pid'] != result['foreground']['pid'] or event['hardware_keycode'] != stimulus['hardware_keycode'] or
            not previous < event['received_ns'] or not stimulus['started_ns'] <= event['received_ns'] <= stimulus['finished_ns']+200000000):
            raise ValueError('keyboard receipt identity/time differs')
        previous = event['received_ns']
    if first['events'] != [e for e in events if e['key']=='F9'] or not events[-1]['active'] or not events[-1]['toplevel_focus']:
        raise ValueError('native keyboard positive control invalid')
    if not result['unfocused_key']['finished_ns'] < result['positive_activation']['at_ns'] < result['focused_key']['started_ns']:
        raise ValueError('keyboard control ordering')
    return {'f9_delivered': bool(first['events']), 'f10_delivered': True,
            'f9_latency_us': (first['events'][0]['received_ns']-result['unfocused_key']['finished_ns'])//1000 if first['events'] else None,
            'f10_latency_us': (events[-1]['received_ns']-result['focused_key']['finished_ns'])//1000}


def judge(interval, foreground, icon):
    actions, samples = interval['actions'], interval['samples']
    if len(actions) != 2 or not 3 <= len(samples) <= 100:
        raise ValueError('native interval completeness')
    for action, scheduled in zip(actions, FIXTURE['actions_us']):
        if not action['performed'] or not scheduled <= action['start_us'] <= scheduled + 50000 or not action['start_us'] <= action['end_us'] <= action['start_us'] + 50000:
            raise ValueError('native action schedule')
    last_end, max_gap, max_duration = 0, 0, 0
    phase_roles, visible_successes, focus_successes = [set(), set(), set()], [[], [], []], [[], [], []]
    states, background_ok = [], True
    for row in samples:
        begin, end = row['start_us'], row['end_us']
        if not last_end <= begin <= row['foreground_start_us'] <= row['background_start_us'] <= row['state_start_us'] <= end <= 2400000:
            raise ValueError('native capture order')
        max_gap, max_duration = max(max_gap, begin-last_end), max(max_duration, end-begin)
        last_end = end
        pixels = rgb(row['foreground'], 20*20*3)
        background_ok &= rgb(row['background'], 128*96*3) == bytes(SCENE['background_rgb'])*128*96
        phase = 0 if begin < actions[0]['start_us'] else (1 if begin < actions[1]['start_us'] else 2)
        required = phase == 0 or begin >= actions[phase-1]['end_us'] + 200000
        current_role = role(row['native'], foreground, icon)
        expected = SCENE['background_rgb'] if phase == 1 else FIXTURE['foreground_rgb']
        visible = row['native']['showing_desktop'] == [int(phase == 1)] and pixels == bytes(expected)*400
        focused = phase == 1 or current_role == 'foreground'
        if visible: visible_successes[phase].append(end)
        if focused: focus_successes[phase].append(end)
        if required: phase_roles[phase].add(current_role)
        states.append({'at_us': begin, 'phase': phase, 'required': required, 'visible': visible, 'focused': focused})
    max_gap = max(max_gap, 2400000-last_end)
    if max_gap > 150000 or max_duration > 50000 or any(sum(s['phase']==p and s['required'] for s in states)<3 for p in (0,1,2)):
        raise ValueError('native capture coverage')
    visible = (all(s['visible'] for s in states if s['required']) and
               all(visible_successes[p] and visible_successes[p][0] <= actions[p-1]['end_us']+200000 for p in (1,2)))
    focused = (all(s['focused'] for s in states if s['required']) and bool(focus_successes[2]) and
               focus_successes[2][0] <= actions[1]['end_us']+200000)
    return {'visual_reveal': 'pass' if visible else 'fail', 'focus': 'pass' if focused else 'fail',
            'background': 'pass' if background_ok else 'fail', 'phase_roles': [sorted(p) for p in phase_roles],
            'max_gap_us': max_gap, 'max_capture_us': max_duration, 'samples': len(samples)}


def observe(display, environment, shell_pid, foreground_pid, workspace, reveal=None, composition=None):
    mode = environment['SYSPANE_GNOME_FOCUS_BASELINE']
    journal = (workspace / 'focus-baseline.jsonl').open('x', encoding='utf-8', newline='\n')
    descriptors, count = [], 0
    def preserve(kind, value):
        nonlocal count
        count += 1
        if count > 180:
            raise ValueError('focus journal record capacity')
        journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
        journal.flush()
        if journal.tell() > 8*1024**2:
            raise ValueError('focus journal byte capacity')
    try:
        foreground = foreground_identity(display, foreground_pid)
        poller = select.poll()
        descriptors.append(os.pidfd_open(foreground_pid))
        poller.register(descriptors[-1], select.POLLIN)
        if reveal is None:
            key(display, 'Escape')
            time.sleep(.3)
        deadline, icon = time.monotonic()+5, None
        while mode != 'shell' and time.monotonic() < deadline:
            icon = bind_icon_window(display, shell_pid, workspace)
            if icon: break
            time.sleep(.05)
        if mode != 'shell':
            if not icon: raise ValueError('native DING prerequisite missing')
            descriptors.append(os.pidfd_open(icon['pid']))
            poller.register(descriptors[-1], select.POLLIN)
        else:
            for window in display.property(display.root, '_NET_CLIENT_LIST_STACKING'):
                if display.atom('_NET_WM_WINDOW_TYPE_DESKTOP') in display.property(window, '_NET_WM_WINDOW_TYPE'):
                    raise ValueError('shell-only baseline has a desktop client')
        result = {'mode': mode, 'version': '0.1.0', 'foreground': foreground, 'icon_manager': icon,
                  'extensions_before': extensions(environment), 'binding_before': binding(environment),
                  'background_settings_before': settings(environment), 'event_file_before': event_file(workspace)}
        if result['extensions_before'] != MODES[mode] or result['binding_before'] != FIXTURE['binding'] or result['event_file_before']['events']:
            raise ValueError('baseline settings/keyboard preconditions')
        preserve('prepared', result)
        if reveal is None:
            result['activation'] = activate(display, foreground)
            result['baseline'] = []
            for index in range(3):
                if index: time.sleep(.1)
                row = {name: rgb_record(display.capture(*region)) for name, region in [('overlap', SCENE['overlap']), ('marker', [300,200,128,96]), ('background', SCENE['background_witness'])]}
                result['baseline'].append(row)
                preserve('baseline', row)
                if index and row != result['baseline'][0]: raise ValueError('baseline pixels unstable')
                if rgb(row['marker'],128*96*3) != bytes(SCENE['background_rgb'])*128*96 or rgb(row['background'],128*96*3) != bytes(SCENE['background_rgb'])*128*96:
                    raise ValueError('baseline marker/background not absent/unchanged')
            if icon: masks(rgb(result['baseline'][0]['overlap'], SCENE['overlap'][2]*SCENE['overlap'][3]*3))
            interval = {'actions': [], 'samples': []}
            started, next_frame = time.monotonic_ns(), 0
            result['started_monotonic_ns'] = started
            now = lambda: (time.monotonic_ns()-started)//1000
            while now() < 2400000:
                if len(interval['actions']) < 2 and now() >= FIXTURE['actions_us'][len(interval['actions'])]:
                    action = {'start_us': now(), 'performed': True}
                    display.reveal_key()
                    action['end_us'] = now()
                    interval['actions'].append(action)
                    preserve('action', action)
                if now() >= next_frame and now() < 2390000:
                    row = {'start_us': now()}
                    row['overlap'] = rgb_record(display.capture(*SCENE['overlap']))
                    row['foreground_start_us'] = now()
                    row['foreground'] = rgb_record(display.capture(*FIXTURE['foreground_witness']))
                    row['background_start_us'] = now()
                    row['background'] = rgb_record(display.capture(*SCENE['background_witness']))
                    row['state_start_us'] = now()
                    row['native'] = display.structure()
                    row['end_us'] = now()
                    interval['samples'].append(row)
                    preserve('sample', row)
                    if poller.poll(0): raise ValueError('native fixture exited during focus trace')
                    next_frame += 50000
                time.sleep(.002)
            result['interval'] = interval
        else:
            result['started_monotonic_ns'] = reveal['started_monotonic_ns']
            result['interval'] = {'actions': reveal['actions'], 'samples': [
                {'start_us': frame['start_us'], **row} for frame,row in zip(reveal['trace']['frames'], reveal['samples'])]}
            preserve('candidate_interval', result['interval'])
        result['evaluation'] = judge(result['interval'], foreground['window'], icon['window'] if icon else None)
        result['before_keyboard'] = display.structure()
        result['unfocused_key'] = key(display, 'F9')
        time.sleep(.2)
        result['events_after_f9'] = event_file(workspace)
        preserve('after_f9', {k: result[k] for k in ['before_keyboard', 'unfocused_key', 'events_after_f9']})
        result['positive_activation'] = activate(display, foreground)
        result['focused_key'] = key(display, 'F10')
        time.sleep(.2)
        result['events_after_f10'] = event_file(workspace)
        result['after_keyboard'] = display.structure()
        result['extensions_after'] = extensions(environment)
        result['binding_after'] = binding(environment)
        result['background_settings_after'] = settings(environment)
        for name in ('extensions', 'binding', 'background_settings'):
            if result[name+'_before'] != result[name+'_after']:
                raise ValueError('native focus settings changed')
        if poller.poll(0) or foreground_identity(display, foreground_pid) != foreground or (icon and bind_icon_window(display, shell_pid, workspace) != icon):
            raise ValueError('native focus fixture lifetime changed')
        result['keyboard'] = keyboard(result)
        preserve('completed', {k:v for k,v in result.items() if k not in ['interval','baseline']})
        return result
    except Exception as error:
        preserve('error', {'message': type(error).__name__ + ': ' + str(error)})
        raise
    finally:
        for descriptor in descriptors: os.close(descriptor)
        journal.close()
