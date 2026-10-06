"""Normal foreground control on the explicitly owned GNOME laboratory display."""
import json
from pathlib import Path
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk

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
window.connect('destroy', Gtk.main_quit)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (Gtk.main_quit(), False)[1])
window.show_all()
Gtk.main()
