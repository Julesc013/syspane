"""Independent native editor obstruction/release on the owned measured desktop."""
import ctypes as C
import json
import os
from pathlib import Path
import select
import signal
import time
from gi.repository import Gio
from gnome_controller_recovery import (identity, controller_rows, lines, now, templates, visible,
                                      RECT, BACKGROUND_RECT, rgb_record, linux_rows, verify_source)
from gnome_composition import FIXTURE, settings, masks
from gnome_input import Observer, icon_center, clipboard_names
from x11_recovery import ResourceOwner
from record_gnome_host import rgb

MODES = ('editor-key', 'editor-button', 'editor-owner-loss', 'editor-controller-freeze', 'editor-no-exit')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def judge(raw, composition):
    mode = raw['mode']
    require(mode in MODES, 'editor control')
    ids = raw['identities']
    require(set(raw['held_live']) == set(ids) == {'controller', 'source', 'old_shell', 'old_icon', 'exit_owner', 'editor'}, 'complete held identities')
    require(all(raw['held_live'].values()), 'held native lifetimes')
    root = ids['controller']['pid']
    require(ids['controller']['session'] == root == ids['controller']['process_group'], 'controller session')
    for name in ('source', 'old_shell'):
        require(ids[name]['parent'] == root == ids[name]['session'] == ids[name]['process_group'], 'original native child')
    require(ids['editor']['parent'] == ids['exit_owner']['pid'] and ids['exit_owner']['pid'] != root and
            ids['editor']['process_group'] == ids['exit_owner']['pid'] == ids['exit_owner']['session'], 'independent exit ownership')
    require(all(raw['final_live'][k] for k in ('controller', 'source', 'old_shell', 'old_icon')), 'desktop lifetime survived')
    rows = raw['controller']
    launched = [r for r in rows if r['event'] == 'consumer_spawned']
    source = [r for r in rows if r['event'] == 'source_spawned']
    require(len(launched) == len(source) == 1 and launched[0]['pid'] == ids['old_shell']['pid'] and
            source[0]['pid'] == ids['source']['pid'], 'no source/desktop replacement')
    require(not any(r['event'] in ('consumer_fault', 'render_fault', 'error') for r in rows), 'no unrelated native fault')
    verify_source(raw['source'], raw['bracket']['before'], raw['after'], raw['bracket']['lower_ns'], raw['upper_ns'])
    originals = {json.loads(r['payload'])['body']['snapshot']['generation']: json.loads(r['payload'])['body'] for r in raw['source']}
    require(all(v['snapshot']['producer_epoch'] == source[0]['epoch'] for v in originals.values()), 'unchanged source epoch')
    for row in raw['delivery']:
        message = json.loads(row['payload'])
        require(message['producer_epoch'] == source[0]['epoch'], 'delivery epoch')
        if message['type'] == 'snapshot':
            require(message['body'] == originals.get(message['body']['snapshot']['generation']), 'original measured delivery')
    require(visible(raw['baseline'], raw['calibration'], raw['delivery'], launched[0]['connection']), 'baseline original pixels')
    begin, fault = raw['obstructed_at_ns'], raw['fault']['begin_ns']
    require(raw['fault']['pid'] == ids['editor']['pid'] and raw['fault']['method'] == mode and
            raw['baseline'][-1]['end_ns'] <= begin <= fault <= raw['fault']['end_ns'], 'fault identity and ordering')
    require(raw['identities']['old_icon']['pid'] == composition['icon_manager']['pid'] and not raw['old_icon_exited'], 'retained icon identity')
    for name, pid in [('editor_window', ids['editor']['pid']), *([('button', ids['exit_owner']['pid'])] if mode == 'editor-button' else [])]:
        window = raw[name]
        require(window['pid'] == pid and window['window'] & ~window['resource_mask'] == window['resource_base'] and
                window['width'] > 0 and window['height'] > 0, 'native window resource binding')
    x, y = icon_center(composition); window = raw['editor_window']
    require(raw['icon_center'] == [x, y] and window['x'] <= x < window['x'] + window['width'] and
            window['y'] <= y < window['y'] + window['height'], 'native obstruction geometry')
    events = raw['exit_owner_events']
    require([e['value'] for e in events if e['event'] == 'child'] == [ids['editor']['pid']] and
            not any(e['event'] in ('deadline', 'mapping_lost', 'unconfirmed', 'child_exit') for e in events), 'bounded independent exit events')
    requests = [e for e in events if e['event'] in ('keyboard_exit', 'native_exit')]
    expected_request = 'native_exit' if mode == 'editor-button' else 'keyboard_exit'
    if mode in ('editor-owner-loss', 'editor-no-exit'):
        require(not requests, 'owner unavailable control must not acknowledge exit')
    else:
        require(len(requests) == 1 and requests[0]['event'] == expected_request and requests[0]['value'] == ids['editor']['pid'] and
                [e['value'] for e in events if e['event'] == 'force_stop'] == [ids['editor']['pid']] and
                [e['value'] for e in events if e['event'] == 'child_signal'] == [signal.SIGKILL], 'requested native escalation')
    require(not any(c['begin_ns'] >= raw['baseline'][0]['begin_ns'] for c in raw['calls']), 'observer must not drive operational recovery')
    require(any(int(r['now_ns']) < begin for r in raw['source']) and any(begin <= int(r['now_ns']) <= fault for r in raw['source']), 'acquisition during obstruction')
    require(raw['before_input']['names'] == ['Probe Folder'] and raw['blocked_input']['owner_changed'] is False and
            raw['blocked_active'] == [raw['editor_window']['window']], 'independent blocked icon input')
    require(raw['obstructed_pixel'] == 'cc2233' and raw['stopped']['editor'] in ('T', 't'), 'real stopped obstruction')
    require(raw['settings_after'] == composition['background_settings_before'], 'background settings preserved')
    if mode == 'editor-no-exit':
        require(raw['stopped']['exit_owner'] in ('T', 't') and not raw.get('editor_exit') and
                raw['negative_end_ns'] - raw['fault']['end_ns'] >= 2_000_000_000 and raw['negative_alive'] and
                raw['negative_pixel'] == 'cc2233' and not raw['negative_input']['owner_changed'], 'calibrated failure missing')
        return {'outcome': 'fail', 'collection': 'pass', 'native_release': 'fail', 'input': 'fail', 'pixels': 'obstructed'}
    require(raw['editor_exit']['pidfd_exit'] and raw['editor_exit']['pid'] == ids['editor']['pid'], 'exact child exit')
    require(0 <= raw['editor_exit']['observed_ns'] - fault <= raw['pixel_restored_ns'] - fault <= 1_500_000_000, 'native/pixel release deadline')
    require(raw['after_input']['names'] == ['Probe Folder'] and raw['after_active'] == [composition['icon_manager']['window']] and
            raw['pixel_restored_ns'] <= raw['input_restored_ns'] <= fault + 2_500_000_000 and
            raw['input_restored_ns'] <= raw['post'][0]['begin_ns'], 'native icon recovery deadline')
    if mode == 'editor-controller-freeze':
        require(raw['stopped']['controller'] in ('T', 't') and raw['controller_resumed_ns'] >= raw['pixel_restored_ns'], 'independent controller-frozen release')
    require(any(int(r['now_ns']) > raw['pixel_restored_ns'] for r in raw['source']), 'post-release acquisition')
    require(visible(raw['post'], raw['calibration'], raw['delivery'], launched[0]['connection']), 'post-release original pixels')
    require(any(r['event'] == 'render_progress' and r['observed_ms'] >= raw['post_start_mono_ms'] for r in rows), 'post-release render progress')
    stages = [rgb(s['frames'][0]['pixels'], 180 * 220 * 3) for s in composition['calibrations']]
    anchors, _ = masks(stages[2], stages[:2])
    for row in raw['post']:
        pixels = rgb(row['icons'], 180 * 220 * 3)
        require(all(pixels[n*3:n*3+3] == stages[2][n*3:n*3+3] for group in anchors for n in group), 'original icon anchors')
        require(rgb(row['background'], 128*96*3) == bytes(FIXTURE['background_rgb'])*128*96, 'background pixels')
    return {'outcome': 'pass', 'collection': 'pass', 'native_release': 'pass', 'input': 'pass', 'pixels': 'pass'}


def observe(display, environment, shell_pid, workspace, composition, channel):
    from native_gnome_bootstrap import mapped_files
    mode = environment['SYSPANE_GNOME_CONTROLLER_CONTROL']
    raw = {'version': '0.1.0', 'mode': mode, 'identities': {}, 'held_live': {}, 'final_live': {},
           'calls': [], 'baseline': [], 'post': [], 'stopped': {}}
    path = workspace/'network-controller-recovery.private.json'
    fds = {}; input_observer = None; owner = ResourceOwner(display); frozen_controller = False
    connection = Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],
        Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
    def alive(name):
        return not bool(select.select([fds[name]], [], [], 0)[0])
    def hold(name, pid):
        fds[name] = os.pidfd_open(pid); raw['identities'][name] = identity(pid); raw['held_live'][name] = alive(name)
        require(raw['held_live'][name], 'already exited native process')
    def until(predicate, seconds=2):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if predicate(): return
            time.sleep(.01)
        raise TimeoutError('editor native observation deadline')
    def call(method):
        begin = now()
        reply = connection.call_sync('org.gnome.Shell', '/org/syspane/NetworkLive', 'org.syspane.NetworkLive', method,
            None, None, Gio.DBusCallFlags.NO_AUTO_START, 1000, None).unpack()[0]
        raw['calls'].append({'method': method, 'begin_ns': begin, 'end_ns': now(), 'reply': reply})
        return reply
    def capture(extra=False):
        row = {'begin_ns': now(), 'pixels': rgb_record(display.capture(*RECT))}
        if extra:
            row.update(icons=rgb_record(display.capture(*FIXTURE['overlap'])), background=rgb_record(display.capture(*BACKGROUND_RECT)))
        row['end_ns'] = now(); return row
    def freeze(name):
        signal.pidfd_send_signal(fds[name], signal.SIGSTOP)
        def stopped():
            state = Path(f"/proc/{raw['identities'][name]['pid']}/stat").read_text().rsplit(')', 1)[1].split()[0]
            raw['stopped'][name] = state; return state in ('T', 't')
        until(stopped, .1)
    def window(pid, title):
        found = []
        for candidate in display.property(display.root, '_NET_CLIENT_LIST'):
            binding = owner.pid(candidate)
            if not binding or binding[0] != pid: continue
            text = C.c_void_p()
            if not display.x.XFetchName(display.handle, candidate, C.byref(text)): continue
            try:
                if C.string_at(text).decode() == title:
                    root, child = C.c_ulong(), C.c_ulong()
                    x, y, rx, ry = (C.c_int() for _ in range(4))
                    width, height, border, depth = (C.c_uint() for _ in range(4))
                    require(display.x.XGetGeometry(display.handle, candidate, C.byref(root), C.byref(x), C.byref(y), C.byref(width), C.byref(height), C.byref(border), C.byref(depth)), 'native geometry')
                    require(display.x.XTranslateCoordinates(display.handle, candidate, display.root, 0, 0, C.byref(rx), C.byref(ry), C.byref(child)), 'native root geometry')
                    found.append({'window': candidate, 'pid': pid, 'resource_base': binding[1], 'resource_mask': binding[2],
                                  'x': rx.value, 'y': ry.value, 'width': width.value, 'height': height.value})
            finally: display.x.XFree(text)
        require(len(found) <= 1, 'ambiguous owned native control')
        return found[0] if found else None
    p, w, i = C.c_void_p, C.c_ulong, C.c_int
    display.x.XGetGeometry.argtypes = [p,w,C.POINTER(w),C.POINTER(i),C.POINTER(i),*[C.POINTER(C.c_uint)]*4]
    display.x.XTranslateCoordinates.argtypes = [p,w,w,i,i,C.POINTER(i),C.POINTER(i),C.POINTER(w)]
    try:
        hold('controller', int(environment['SYSPANE_GNOME_CONTROLLER_PID'])); hold('old_shell', shell_pid)
        hold('old_icon', composition['icon_manager']['pid'])
        spawned = [r for r in controller_rows(workspace) if r['event'] == 'source_spawned']; require(len(spawned) == 1, 'one collector')
        hold('source', spawned[0]['pid'])
        raw['bracket'] = json.loads((workspace/'network-controller-bracket.private.json').read_text())
        input_observer = Observer(display, composition['icon_manager'], workspace, shell_pid)
        x, y = icon_center(composition); raw['icon_center'] = [x, y]
        input_observer.click(x, y); raw['before_input'] = input_observer.copy_selection()
        require(raw['before_input']['names'] == ['Probe Folder'], 'initial native icon input')
        input_observer.click(700, 550); time.sleep(.1)
        require(call('Calibrate') == 'calibrated', 'glyph calibration'); time.sleep(.2)
        raw['calibration'] = capture(); templates(raw['calibration']['pixels'])
        require(call('Start') == 'starting', 'live attachment')
        until(lambda: (json.loads(call('GetState')).get('session') or {}).get('phase') == 'live')
        until(lambda: len([r for r in controller_rows(workspace) if r['event'] == 'render_progress']) >= 2, 4)
        time.sleep(.25); end = now() + 2_200_000_000
        while now() < end: raw['baseline'].append(capture()); time.sleep(.05)
        raw['old_shell_mapped_files'] = mapped_files(shell_pid); raw['old_icon_mapped_files'] = mapped_files(composition['icon_manager']['pid'])
        channel.send({'editor_exit_request': 'launch'})
        require(channel.poll(3), 'native exit owner launch reply'); reply = channel.recv()
        require(set(reply) == {'editor_exit_pid'}, 'native launch response')
        hold('exit_owner', reply['editor_exit_pid'])
        until(lambda: any(r['event'] == 'child' for r in lines(workspace/'editor-exit.log', 65536)))
        child = next(r['value'] for r in lines(workspace/'editor-exit.log', 65536) if r['event'] == 'child')
        hold('editor', child)
        def candidate_ready():
            raw['candidate_probe'] = {'window': window(child, 'SysPane editor lifetime candidate'),
                                      'icon_pixel': display.capture(x, y, 1, 1).hex(), 'alive': alive('editor'),
                                      'workarea': display.property(display.root, '_NET_WORKAREA'),
                                      'maximized_atoms': [display.atom('_NET_WM_STATE_MAXIMIZED_HORZ'), display.atom('_NET_WM_STATE_MAXIMIZED_VERT')]}
            if raw['candidate_probe']['window']:
                raw['candidate_probe']['state'] = display.property(raw['candidate_probe']['window']['window'], '_NET_WM_STATE')
            return raw['candidate_probe']['window'] and raw['candidate_probe']['icon_pixel'] == 'cc2233'
        until(candidate_ready)
        raw['editor_window'] = window(child, 'SysPane editor lifetime candidate')
        raw['obstructed_pixel'] = display.capture(x, y, 1, 1).hex(); raw['obstructed_at_ns'] = now()
        time.sleep(.4); input_observer.click(x, y)
        raw['blocked_input'] = input_observer.copy_selection(); raw['blocked_active'] = display.structure()['active_window']
        freeze('editor')
        if mode == 'editor-controller-freeze': freeze('controller'); frozen_controller = True
        if mode == 'editor-no-exit': freeze('exit_owner')
        if mode == 'editor-button':
            until(lambda: window(reply['editor_exit_pid'], 'SysPane independent editor exit'))
            raw['button'] = window(reply['editor_exit_pid'], 'SysPane independent editor exit')
        raw['fault'] = {'begin_ns': now(), 'pid': child, 'method': mode}
        if mode == 'editor-owner-loss': signal.pidfd_send_signal(fds['exit_owner'], signal.SIGKILL)
        elif mode == 'editor-button':
            button = raw['button']; input_observer.click(button['x'] + button['width']//2, button['y'] + button['height']//2)
        else:
            keys = [display.x.XKeysymToKeycode(display.handle, display.x.XStringToKeysym(n)) for n in (b'Control_L', b'Alt_L', b'Escape')]
            require(all(keys), 'native recovery chord')
            for key in keys: require(display.xtest.XTestFakeKeyEvent(display.handle, key, True, 0), 'native key press')
            for key in reversed(keys): require(display.xtest.XTestFakeKeyEvent(display.handle, key, False, 0), 'native key release')
            display.x.XFlush(display.handle)
        raw['fault']['end_ns'] = now()
        if mode == 'editor-no-exit':
            time.sleep(2); raw['negative_end_ns'] = now(); raw['negative_alive'] = alive('editor') and alive('exit_owner')
            raw['negative_pixel'] = display.capture(x, y, 1, 1).hex()
            input_observer.click(x, y); raw['negative_input'] = input_observer.copy_selection()
        else:
            until(lambda: not alive('editor'), 1.5)
            raw['editor_exit'] = {'pid': child, 'pidfd_exit': True, 'observed_ns': now()}
            until(lambda: display.capture(x, y, 1, 1).hex() != 'cc2233', 1.5); raw['pixel_restored_ns'] = now()
            if frozen_controller:
                signal.pidfd_send_signal(fds['controller'], signal.SIGCONT); frozen_controller = False; raw['controller_resumed_ns'] = now()
            input_observer.click(x, y); raw['after_input'] = input_observer.copy_selection()
            raw['after_active'] = display.structure()['active_window']; raw['input_restored_ns'] = now()
            input_observer.click(700, 550); time.sleep(.2)
            raw['post_start_mono_ms'] = time.monotonic_ns()//1_000_000; end = now() + 2_200_000_000
            while now() < end: raw['post'].append(capture(True)); time.sleep(.045)
        raw['controller'] = controller_rows(workspace)
        raw['source'] = lines(Path(environment['SYSPANE_GNOME_CONTROLLER_SOURCE']), 4*1024**2)
        raw['delivery'] = lines(Path(environment['SYSPANE_GNOME_CONTROLLER_DELIVERY']), 4*1024**2)
        raw['after'] = linux_rows(); raw['upper_ns'] = now(); raw['settings_after'] = settings(environment)
        raw['exit_owner_events'] = lines(workspace/'editor-exit.log', 65536)
        raw['old_icon_exited'] = not alive('old_icon')
        raw['final_live'] = {name: alive(name) for name in fds}; raw['evaluation'] = judge(raw, composition)
        return {'outcome': raw['evaluation']['outcome'], 'evaluation': raw['evaluation'], 'journal': str(path),
                'old_shell_mapped_files': raw['old_shell_mapped_files'], 'old_icon_mapped_files': raw['old_icon_mapped_files']}
    except Exception as error:
        raw['error'] = type(error).__name__ + ': ' + str(error); raise
    finally:
        if frozen_controller and alive('controller'): signal.pidfd_send_signal(fds['controller'], signal.SIGCONT)
        # Only cleanup after acceptance/failure capture; never counted as recovery.
        for name in ('exit_owner', 'editor'):
            if name in fds and alive(name): signal.pidfd_send_signal(fds[name], signal.SIGKILL)
        if input_observer: input_observer.close()
        connection.close_sync(None)
        data = json.dumps(raw, indent=2) + '\n'; require(len(data.encode()) <= 16*1024**2, 'private editor evidence capacity')
        with path.open('x') as target: path.chmod(0o600); target.write(data)
        for fd in fds.values(): os.close(fd)
