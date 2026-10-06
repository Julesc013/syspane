"""Normal foreground control on the explicitly owned GNOME laboratory display."""
import json
import os
from pathlib import Path
import signal
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk

fixture = json.loads((Path(__file__).parent / 'fixtures/gnome-reveal.json').read_text())
window = Gtk.Window(title='SysPane owned reveal control')
window.set_wmclass('syspane-reveal-control', 'SysPaneRevealControl')
window.set_decorated(False)
window.set_resizable(False)
x, y, width, height = fixture['window']
window.set_default_size(width, height)
window.move(x, y)
provider = Gtk.CssProvider()
color = ','.join(str(c) for c in fixture['foreground_rgb'])
provider.load_from_data(('window { background-image: none; background-color: rgb(' + color + '); }').encode())
window.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
content = Gtk.Box()
content.set_size_request(width, height)
window.add(content)
event_path = os.environ.get('SYSPANE_FOREGROUND_EVENTS')
event_descriptor, event_count, event_bytes = None, 0, 0
if event_path:
    workspace = Path(os.environ['HOME']).parent.resolve(strict=True)
    path = Path(event_path)
    if not workspace.name.startswith('GNOME-FOCUS-BASELINE-01-') or path != workspace / 'foreground-events.jsonl':
        raise ValueError('owned foreground event path required')
    event_descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)

    def key_press(widget, event):
        global event_count, event_bytes
        key = Gdk.keyval_name(event.keyval)
        if key not in ('F9', 'F10'):
            return False
        record = {'key': key, 'pid': os.getpid(), 'received_ns': time.monotonic_ns(),
                  'hardware_keycode': event.hardware_keycode, 'state': int(event.state), 'native_time': event.time,
                  'active': window.is_active(), 'toplevel_focus': window.has_toplevel_focus()}
        raw = (json.dumps(record, separators=(',', ':')) + '\n').encode()
        event_count += 1
        event_bytes += len(raw)
        if event_count > 16 or event_bytes > 16384 or os.write(event_descriptor, raw) != len(raw):
            os._exit(2)
        return False

    window.connect('key-press-event', key_press)
window.connect('destroy', Gtk.main_quit)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (Gtk.main_quit(), False)[1])
window.show_all()
Gtk.main()
if event_descriptor is not None:
    os.close(event_descriptor)
