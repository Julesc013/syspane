"""Observe only the owned window-manager restart; preserve all root frames."""
import ctypes as C
import json
import os
import select
import time

from oracle import decode, pack_frame, unpack_frame


class ClientSpec(C.Structure):
    _fields_ = [('client', C.c_ulong), ('mask', C.c_uint)]


class ClientValue(C.Structure):
    _fields_ = [('spec', ClientSpec), ('length', C.c_long), ('value', C.c_void_p)]


class Client(C.Structure):
    _fields_ = [('base', C.c_ulong), ('mask', C.c_ulong)]


class ErrorEvent(C.Structure):
    _fields_ = [('type', C.c_int), ('display', C.c_void_p), ('resource', C.c_ulong),
                ('serial', C.c_ulong), ('code', C.c_ubyte), ('request', C.c_ubyte), ('minor', C.c_ubyte)]


class ResourceOwner:
    def __init__(self, display):
        self.display = display
        self.library = C.CDLL('/usr/lib/x86_64-linux-gnu/libXRes.so.1')
        signatures = {
            'XResQueryExtension': ([C.c_void_p, C.POINTER(C.c_int), C.POINTER(C.c_int)], C.c_int),
            'XResQueryVersion': ([C.c_void_p, C.POINTER(C.c_int), C.POINTER(C.c_int)], C.c_int),
            'XResQueryClients': ([C.c_void_p, C.POINTER(C.c_int), C.POINTER(C.POINTER(Client))], C.c_int),
            'XResQueryClientIds': ([C.c_void_p, C.c_long, C.POINTER(ClientSpec), C.POINTER(C.c_long), C.POINTER(C.POINTER(ClientValue))], C.c_int),
            'XResGetClientPid': ([C.POINTER(ClientValue)], C.c_int),
            'XResClientIdsDestroy': ([C.c_long, C.POINTER(ClientValue)], None)}
        for name, (arguments, result) in signatures.items():
            function = getattr(self.library, name)
            function.argtypes, function.restype = arguments, result
        a, b = C.c_int(), C.c_int()
        if not self.library.XResQueryExtension(display.handle, C.byref(a), C.byref(b)) or not self.library.XResQueryVersion(display.handle, C.byref(a), C.byref(b)) or (a.value, b.value) < (1, 2):
            raise ValueError('X-Resource 1.2 unavailable')

    def pid(self, window):
        count_clients, clients = C.c_int(), C.POINTER(Client)()
        try:
            if not self.library.XResQueryClients(self.display.handle, C.byref(count_clients), C.byref(clients)) or not 1 <= count_clients.value <= 64:
                raise ValueError('native resource client bounds')
            owners = [(clients[i].base, clients[i].mask) for i in range(count_clients.value) if window & ~clients[i].mask == clients[i].base]
            if not owners:
                return None
            if len(owners) != 1:
                raise ValueError('ambiguous resource base')
            base, mask = owners[0]
        finally:
            if clients:
                self.display.x.XFree(clients)
        spec, count, values = ClientSpec(window, 2), C.c_long(), C.POINTER(ClientValue)()
        status = self.library.XResQueryClientIds(self.display.handle, 1, C.byref(spec), C.byref(count), C.byref(values))
        try:
            if status != 0 or count.value != 1 or not values or values[0].spec.client != base or values[0].spec.mask != 2:
                detail = {'status': status, 'count': count.value, 'requested': window,
                          'returned': [{'client': values[i].spec.client, 'mask': values[i].spec.mask, 'length': values[i].length} for i in range(max(0, min(count.value, 2)))] if values else []}
                raise ValueError('native resource owner unavailable or ambiguous: ' + json.dumps(detail))
            pid = self.library.XResGetClientPid(C.byref(values[0]))
            if pid <= 0:
                raise ValueError('native resource owner PID absent')
            return pid, base, mask
        finally:
            if values:
                self.library.XResClientIdsDestroy(count, values)


def manager_identity(display, owner):
    errors = []
    callback_type = C.CFUNCTYPE(C.c_int, C.c_void_p, C.POINTER(ErrorEvent))
    def error_callback(_display, event):
        errors.append(event.contents.code)
        return 0
    callback = callback_type(error_callback)
    display.x.XSetErrorHandler.argtypes = [C.c_void_p]
    display.x.XSetErrorHandler.restype = C.c_void_p
    display.x.XSync(display.handle, False)
    previous = display.x.XSetErrorHandler(C.cast(callback, C.c_void_p))
    try:
        check = display.property(display.root, '_NET_SUPPORTING_WM_CHECK')
        if len(check) != 1:
            return None
        binding = owner.pid(check[0])
        if binding is None:
            return None
        pid, base, mask = binding
        return {'window': check[0], 'self': display.property(check[0], '_NET_SUPPORTING_WM_CHECK'),
                'pid': [pid], 'pid_origin': 'XResQueryClientIds', 'resource_base': base, 'resource_mask': mask,
                'pid_property': display.property(check[0], '_NET_WM_PID')}
    except ValueError:
        if errors and all(code == 3 for code in errors):
            return None
        raise
    finally:
        display.x.XSync(display.handle, False)
        display.x.XSetErrorHandler(previous)
        if any(code != 3 for code in errors):
            raise ValueError('unexpected native manager-query error')


def observe_recovery(display, channel, workspace, command, baseline, icon_mask, wallpaper):
    old_pid, window = command['window_manager_pid'], command['window']
    owner = ResourceOwner(display)
    old = manager_identity(display, owner)
    if old is None or old['pid'] != [old_pid] or old['self'] != [old['window']]:
        raise ValueError('original window manager identity')
    descriptor = os.pidfd_open(old_pid)
    poller = select.poll()
    poller.register(descriptor, select.POLLIN)
    if poller.poll(0):
        os.close(descriptor)
        raise ValueError('original window manager already exited')
    result = {'old_manager': old, 'candidate_pid': command['pid'], 'candidate_window': window,
              'start_us': 0, 'frames': [], 'samples': [], 'events': []}
    started = time.monotonic_ns()
    now = lambda: (time.monotonic_ns() - started) // 1000
    requested = False
    replacement_pid = ready_time = None
    with (workspace / 'recovery.jsonl').open('x', encoding='utf-8', newline='\n') as journal:
        def preserve(kind, value):
            journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
            journal.flush()
            if journal.tell() > 8 * 1024**2:
                raise ValueError('recovery journal capacity')

        def event(kind, **values):
            value = {'event': kind, 'at_us': now(), **values}
            result['events'].append(value)
            preserve('event', value)
            return value['at_us']

        def stimulus(generation):
            event('stimulus', generation=generation)
            display.send(window, generation)

        try:
            preserve('identity', {key: value for key, value in result.items() if key not in ('frames', 'samples', 'events')})
            stimulus(4)
            next_capture = 0
            while now() < 8_000_000:
                elapsed = now()
                if not requested and elapsed >= 250_000:
                    event('stop_requested', pid=old_pid)
                    channel.send({'restart_requested': 'openbox', 'pid': old_pid})
                    requested = True
                if channel.poll():
                    message = channel.recv()
                    if set(message) == {'manager_stopped', 'exit'} and message['manager_stopped'] == old_pid:
                        if message['exit'] != -9 or not poller.poll(0):
                            raise ValueError('independent manager exit not confirmed')
                        event('exit_observed', pid=old_pid, exit=-9, observer='pidfd')
                        stimulus(5)
                        channel.send({'exit_observed': old_pid})
                    elif set(message) == {'replacement_started'} and replacement_pid is None:
                        replacement_pid = message['replacement_started']
                        if replacement_pid == old_pid:
                            raise ValueError('replacement process identity reused')
                        event('replacement_started', pid=replacement_pid)
                    else:
                        raise ValueError('recovery parent message')
                if replacement_pid and ready_time is None:
                    identity = manager_identity(display, owner)
                    if identity is not None and identity['pid'] == [replacement_pid] and identity['self'] == [identity['window']]:
                        display.verify(window, command['pid'])
                        ready_time = event('manager_ready', **identity)
                        stimulus(6)
                if ready_time is not None and elapsed >= ready_time + 750_000:
                    break
                if elapsed >= 5_250_000 and ready_time is None:
                    raise TimeoutError('replacement manager readiness exceeded five seconds')
                if elapsed < next_capture:
                    time.sleep(min(.01, (next_capture - elapsed) / 1_000_000))
                    continue
                if len(result['frames']) >= 160:
                    raise ValueError('recovery frame capacity')
                begin = now()
                pixels = display.capture()
                finish = now()
                frame = pack_frame(pixels, begin, finish)
                result['frames'].append(frame)
                preserve('frame', frame)
                words = display.property(window, '_SYSPANE_ORACLE_ACCEPTED')
                wallpaper_start = now()
                wallpaper_pixels = display.capture(600, 400, 128, 96)
                sample = {'at_us': now(), 'accepted': (words[0] << 32) | words[1] if len(words) == 2 else None,
                          'wallpaper_frame': pack_frame(wallpaper_pixels, wallpaper_start, now()),
                          'wallpaper_unchanged': wallpaper_pixels == wallpaper}
                result['samples'].append(sample)
                preserve('sample', sample)
                next_capture = finish + 50_000
            if ready_time is None:
                raise TimeoutError('window manager recovery deadline')
            result['end_us'] = now()
            frames = result['frames']
            gaps = [frames[0]['start_us'], result['end_us'] - frames[-1]['end_us']]
            gaps.extend(b['start_us'] - a['end_us'] for a, b in zip(frames, frames[1:]))
            maximum_capture = max(frame['end_us'] - frame['start_us'] for frame in frames + [s['wallpaper_frame'] for s in result['samples']])
            complete = max(gaps) <= 150_000 and maximum_capture <= 50_000
            final_stimulus = next(e['at_us'] for e in result['events'] if e['event'] == 'stimulus' and e['generation'] == 6)
            post = [frame for frame in frames if frame['start_us'] >= final_stimulus + 200_000]
            decoded_post = [unpack_frame(frame) for frame in post]
            defects = any(decode(pixels) != 6 or any(pixels[n:n+3] != baseline[n:n+3] for n in icon_mask) for pixels in decoded_post)
            continuity = any(s['accepted'] == 5 and s['at_us'] < ready_time for s in result['samples']) and any(s['accepted'] == 6 for s in result['samples'])
            result['outcomes'] = {'manager_recovery': 'pass', 'candidate_progress': 'pass' if continuity else 'fail',
                                  'coverage': 'pass' if complete else 'inconclusive',
                                  'surface_recovery': 'fail' if defects else ('pass' if complete and len(post) >= 3 else 'inconclusive'),
                                  'wallpaper_pixels': 'pass' if all(s['wallpaper_unchanged'] for s in result['samples']) else 'fail'}
            result['maximum_gap_us'] = max(gaps)
            result['maximum_capture_us'] = maximum_capture
            result['first_final_generation_us'] = next((f['end_us'] for f in frames if decode(unpack_frame(f)) == 6), None)
            preserve('result', {key: value for key, value in result.items() if key not in ('frames', 'samples', 'events', 'old_manager', 'candidate_pid', 'candidate_window', 'start_us')})
            return result
        finally:
            os.close(descriptor)
