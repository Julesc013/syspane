"""External native input and read-only AT-SPI observations on the owned X11 lab."""
import ctypes as C
import json
import os
import time
from urllib.parse import unquote, urlsplit


class SelectionEvent(C.Structure):
    _fields_ = [('type', C.c_int), ('serial', C.c_ulong), ('send_event', C.c_int),
                ('display', C.c_void_p), ('requestor', C.c_ulong), ('selection', C.c_ulong),
                ('target', C.c_ulong), ('property', C.c_ulong), ('time', C.c_ulong)]


class NativeEvent(C.Union):
    _fields_ = [('selection', SelectionEvent), ('padding', C.c_long * 24)]


class InputObserver:
    def __init__(self, display, manager_pid, workspace, desktop):
        self.journal = (workspace / 'input.jsonl').open('x', encoding='utf-8', newline='\n')
        self.started = time.monotonic_ns()
        self.preserve('initialize', {'manager_pid': manager_pid, 'desktop': desktop})
        import gi
        from gi.repository import Gio, GLib
        self.api, self.glib = Gio, GLib
        self.display, self.manager_pid = display, manager_pid
        self.workspace, self.desktop = workspace, desktop
        self.bus = Gio.DBusConnection.new_for_address_sync(
            os.environ['AT_SPI_BUS_ADDRESS'], Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
            Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
        display.xtest.XTestFakeMotionEvent.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_ulong]
        display.xtest.XTestFakeButtonEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
        p, w, i = C.c_void_p, C.c_ulong, C.c_int
        signatures = {
            'XSetSelectionOwner': ([p, w, w, w], i), 'XGetSelectionOwner': ([p, w], w),
            'XConvertSelection': ([p, w, w, w, w, w], i),
            'XPending': ([p], i), 'XNextEvent': ([p, C.POINTER(NativeEvent)], i),
        }
        for name, (arguments, result) in signatures.items():
            getattr(display.x, name).argtypes = arguments
            getattr(display.x, name).restype = result
        self.clipboard_window = display.x.XCreateSimpleWindow(display.handle, display.root, 0, 0, 1, 1, 0, 0, 0)
        self.preserve('ready', {'clipboard_window': self.clipboard_window})

    def preserve(self, kind, value):
        self.journal.write(json.dumps({'kind': kind, 'at_us': (time.monotonic_ns() - self.started)//1000,
                                      'value': value}, separators=(',', ':')) + '\n')
        self.journal.flush()

    def close(self):
        self.display.x.XDestroyWindow(self.display.handle, self.clipboard_window)
        self.bus.close_sync(None)
        self.journal.close()

    def tree(self):
        self.preserve('tree-start', {})
        deadline = time.monotonic() + 3
        def call(destination, path, interface, method, parameters=None):
            if time.monotonic() >= deadline:
                raise TimeoutError('accessibility tree observation deadline')
            return self.bus.call_sync(destination, path, interface, method, parameters, None,
                                      self.api.DBusCallFlags.NO_AUTO_START, 250, None).unpack()
        accessible = 'org.a11y.atspi.Accessible'
        children = call('org.a11y.atspi.Registry', '/org/a11y/atspi/accessible/root', accessible, 'GetChildren')[0]
        apps = []
        if len(children) > 8:
            raise RuntimeError('unexpected private accessibility application count')
        for app in children:
            pid = call('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus',
                       'GetConnectionUnixProcessID', self.glib.Variant('(s)', (app[0],)))[0]
            if pid == self.manager_pid:
                apps.append(app)
        if len(apps) != 1:
            raise RuntimeError('native icon manager accessibility identity unavailable or ambiguous')
        rows, queue = [], [(apps[0], [], 0)]
        while queue:
            if len(rows) >= 256 or time.monotonic() >= deadline:
                raise RuntimeError('accessibility tree observation exceeded budget')
            obj, path, depth = queue.pop(0)
            if depth > 12:
                raise RuntimeError('accessibility depth limit')
            destination, object_path = obj
            name = call(destination, object_path, 'org.freedesktop.DBus.Properties', 'Get',
                        self.glib.Variant('(ss)', (accessible, 'Name')))[0] or ''
            if len(name) > 256:
                raise RuntimeError('accessibility name limit')
            states = call(destination, object_path, accessible, 'GetState')[0]
            if len(states) != 2:
                raise ValueError('accessibility state bitmap shape')
            role = call(destination, object_path, accessible, 'GetRoleName')[0]
            row = {'path': path, 'name': name, 'role': role,
                   'selected': bool(states[0] & (1 << 23)), 'showing': bool(states[0] & (1 << 25)),
                   'focused': bool(states[0] & (1 << 12)), 'bus_name': destination, 'object_path': object_path}
            rows.append(row)
            children = call(destination, object_path, accessible, 'GetChildren')[0]
            if len(children) > 32:
                raise RuntimeError('accessibility child-count limit')
            queue.extend((child, path + [n], depth + 1) for n, child in enumerate(children))
        self.preserve('tree-finish', {'nodes': len(rows)})
        return rows

    def move(self, x, y):
        if not 0 <= x < 800 or not 0 <= y < 600:
            raise ValueError('private-display input bounds')
        if not self.display.xtest.XTestFakeMotionEvent(self.display.handle, -1, x, y, 0):
            raise RuntimeError('native pointer motion failed')
        self.display.x.XFlush(self.display.handle)

    def button(self, number, pressed):
        if not self.display.xtest.XTestFakeButtonEvent(self.display.handle, number, pressed, 0):
            raise RuntimeError('native pointer button failed')
        self.display.x.XFlush(self.display.handle)

    def click(self, x, y, number=1):
        self.preserve('click', {'x': x, 'y': y, 'button': number})
        self.move(x, y)
        self.button(number, True)
        time.sleep(.03)
        self.button(number, False)

    def escape(self):
        self.preserve('key', {'name': 'Escape'})
        key = self.display.x.XKeysymToKeycode(self.display.handle, self.display.x.XStringToKeysym(b'Escape'))
        if not key:
            raise RuntimeError('native Escape key unavailable')
        for pressed in (True, False):
            self.display.xtest.XTestFakeKeyEvent(self.display.handle, key, pressed, 0)
        self.display.x.XFlush(self.display.handle)

    def control_key(self, letter):
        self.preserve('control-key', {'name': letter.decode('ascii')})
        d = self.display
        keys = [d.x.XKeysymToKeycode(d.handle, d.x.XStringToKeysym(n)) for n in (b'Control_L', letter)]
        if not all(keys):
            raise RuntimeError('native control key map unavailable')
        for key, pressed in ((keys[0], True), (keys[1], True), (keys[1], False), (keys[0], False)):
            if not d.xtest.XTestFakeKeyEvent(d.handle, key, pressed, 0):
                raise RuntimeError('native control key stimulus failed')
        d.x.XFlush(d.handle)

    def copy_selection(self, folder_contents=False):
        self.preserve('copy', {})
        d = self.display
        selection, target, prop = (d.atom(n) for n in ('CLIPBOARD', 'text/uri-list', '_SYSPANE_INPUT_SELECTION'))
        d.x.XSetSelectionOwner(d.handle, selection, self.clipboard_window, 0)
        d.x.XSync(d.handle, False)
        if d.x.XGetSelectionOwner(d.handle, selection) != self.clipboard_window:
            raise RuntimeError('private clipboard initialization failed')
        self.control_key(b'c')
        deadline = time.monotonic() + .5
        owner = self.clipboard_window
        while time.monotonic() < deadline:
            owner = d.x.XGetSelectionOwner(d.handle, selection)
            if owner != self.clipboard_window:
                break
            time.sleep(.01)
        if owner == self.clipboard_window:
            return {'names': [], 'uris': [], 'owner_changed': False, 'owner': owner}
        if not owner:
            raise RuntimeError('private clipboard lost its owner')
        d.x.XConvertSelection(d.handle, selection, target, prop, self.clipboard_window, 0)
        d.x.XFlush(d.handle)
        deadline = time.monotonic() + .5
        received = False
        while time.monotonic() < deadline and not received:
            for _ in range(256):
                if not d.x.XPending(d.handle):
                    break
                event = NativeEvent()
                d.x.XNextEvent(d.handle, C.byref(event))
                reply = event.selection
                if reply.type == 31 and reply.requestor == self.clipboard_window and reply.selection == selection:
                    if reply.target != target or reply.property != prop:
                        raise RuntimeError('private clipboard URI conversion refused')
                    received = True
                    break
            else:
                raise RuntimeError('private clipboard event budget')
            if not received:
                time.sleep(.01)
        if not received:
            raise TimeoutError('private clipboard URI response deadline')
        kind, form, count, remaining, data = C.c_ulong(), C.c_int(), C.c_ulong(), C.c_ulong(), C.c_void_p()
        status = d.x.XGetWindowProperty(d.handle, self.clipboard_window, prop, 0, 1024, True, 0,
                                       C.byref(kind), C.byref(form), C.byref(count), C.byref(remaining), C.byref(data))
        try:
            if status or kind.value != target or form.value != 8 or not 0 < count.value <= 4096 or remaining.value:
                raise ValueError('private clipboard URI shape or budget')
            raw = C.string_at(data, count.value)
        finally:
            if data:
                d.x.XFree(data)
        # GTK's selection buffer includes one terminating NUL; URI content may not.
        content = raw[:-1] if raw.endswith(b'\x00') else raw
        if b'\x00' in content:
            raise ValueError('embedded private clipboard NUL')
        uris = content.decode('utf-8').splitlines()
        self.preserve('clipboard-reply', {'raw_utf8': raw.decode('utf-8'), 'owner': owner})
        allowed = {str(self.workspace / 'Desktop' / name): name for name in ('Probe Folder', 'Second Folder')}
        if folder_contents:
            allowed = {str(self.workspace / 'Desktop/Probe Folder/Sentinel.txt'): 'Sentinel.txt'}
        names = []
        if not 1 <= len(uris) <= 2 or len(set(uris)) != len(uris):
            raise ValueError('private clipboard URI count')
        for uri in uris:
            parsed = urlsplit(uri)
            path = unquote(parsed.path, errors='strict')
            if parsed.scheme != 'file' or parsed.netloc or parsed.query or parsed.fragment or path not in allowed:
                raise ValueError('private clipboard names an unexpected file')
            names.append(allowed[path])
        return {'names': sorted(names), 'uris': uris, 'owner_changed': True, 'owner': owner,
                'raw_utf8': raw.decode('utf-8')}

    def wait(self, predicate):
        deadline = time.monotonic() + 3
        latest = None
        while time.monotonic() < deadline:
            latest = self.tree()
            if predicate(latest):
                return latest, True
            time.sleep(.05)
        return latest, False

    def run(self, candidate, capture_record):
        rows = []
        def check(name, predicate=None, selected=None, folder_before=None):
            self.preserve('check-start', {'step': name})
            clipboard = None
            if selected is not None:
                clipboard = self.copy_selection()
                tree, matched = self.tree(), clipboard['names'] == selected
            else:
                tree, matched = self.wait(predicate)
            structure = self.display.structure(candidate)
            opened_window = None
            if folder_before is not None and matched:
                new = [c for c in structure['clients'] if c['window'] not in folder_before and c['pid'] == [self.manager_pid]
                       and c['type'] == [self.display.atom('_NET_WM_WINDOW_TYPE_NORMAL')]]
                matched = len(new) == 1 and structure['active_window'] == [new[0]['window']]
                if matched:
                    opened_window = new[0]['window']
                    self.preserve('select-folder-contents', {'window': opened_window})
                    self.control_key(b'a')
                    clipboard = self.copy_selection(folder_contents=True)
                    matched = clipboard['names'] == ['Sentinel.txt']
            candidate_clear = structure['focus'] != candidate and structure['active_window'] != [candidate]
            focus_clear = candidate_clear
            if selected is not None:
                focus_clear = focus_clear and structure['active_window'] == [self.desktop]
            row = {'step': name, 'outcome': 'pass' if matched and focus_clear else 'fail',
                   'tree': tree, 'clipboard': clipboard, 'structure': structure,
                   'opened_window': opened_window,
                   'candidate_did_not_own_focus': candidate_clear, 'native_focus_expected': focus_clear,
                   'desktop_pixels': capture_record(self.display.capture(0, 0, 800, 600))}
            rows.append(row)
            self.preserve('check-finish', row)
            return row['outcome'] == 'pass'
        try:
            self.click(700, 550)
            if not check('baseline-clear', selected=[]):
                return {'outcome': 'fail', 'steps': rows}
            self.click(60, 40)
            if not check('select', selected=['Probe Folder']):
                return {'outcome': 'fail', 'steps': rows}
            self.click(700, 550)
            if not check('clear', selected=[]):
                return {'outcome': 'fail', 'steps': rows}
            self.move(10, 5)
            self.preserve('drag', {'from': [10, 5], 'to': [115, 200], 'steps': 12})
            self.button(1, True)
            for n in range(1, 13):
                self.move(10 + 105*n//12, 5 + 195*n//12)
                time.sleep(.02)
            self.button(1, False)
            if not check('drag-select', selected=['Probe Folder', 'Second Folder']):
                return {'outcome': 'fail', 'steps': rows}
            self.click(700, 550)
            self.click(60, 40, 3)
            if not check('context-menu', lambda t: any(r['role'] == 'menu item' and r['name'] == 'Open in New Window' and r['showing'] for r in t)):
                return {'outcome': 'fail', 'steps': rows}
            self.escape()
            time.sleep(.1)
            self.click(700, 550)
            before = set(self.display.property(self.display.root, '_NET_CLIENT_LIST_STACKING'))
            self.click(60, 40)
            time.sleep(.05)
            self.click(60, 40)
            if not check('double-click-open', lambda t: any(r['name'] == 'Probe Folder' and r['role'] == 'frame' and r['showing'] for r in t),
                         folder_before=before):
                return {'outcome': 'fail', 'steps': rows}
            structure = rows[-1]['structure']
            new = [c for c in structure['clients'] if c['window'] not in before and c['pid'] == [self.manager_pid]]
            if len(new) != 1 or structure['active_window'] != [new[0]['window']]:
                rows[-1]['outcome'] = 'fail'
                return {'outcome': 'fail', 'steps': rows, 'error': 'opened folder lacks unambiguous native focus/identity'}
            self.preserve('close-folder', {'window': new[0]['window']})
            self.display.send(new[0]['window'])
            deadline = time.monotonic() + 3
            while new[0]['window'] in self.display.property(self.display.root, '_NET_CLIENT_LIST_STACKING'):
                if time.monotonic() >= deadline:
                    raise TimeoutError('owned folder did not close')
                time.sleep(.05)
            self.click(700, 550)
            if not check('restore-clear', selected=[]):
                return {'outcome': 'fail', 'steps': rows}
            return {'outcome': 'pass', 'steps': rows}
        except Exception as error:
            return {'outcome': 'inconclusive', 'steps': rows, 'error': type(error).__name__ + ': ' + str(error)}
        finally:
            self.escape()
            self.button(1, False)
            self.click(700, 550)
