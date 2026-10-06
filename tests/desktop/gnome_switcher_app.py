"""Normal application fixture on the owned GNOME switcher display."""
import json
import os
from pathlib import Path
import signal
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk

workspace = Path(os.environ['HOME']).parent.resolve(strict=True)
if not workspace.name.startswith('GNOME-SWITCHER-01-'):
    raise ValueError('owned switcher application workspace required')
role = sys.argv[1]
fixture = json.loads((Path(__file__).parent/'fixtures/gnome-switcher.json').read_text())['applications'][role]
GLib.set_prgname(fixture['id'])
GLib.set_application_name(fixture['name'])
window = Gtk.Window(title=fixture['name'])
window.set_wmclass(fixture['id'], fixture['id'])
window.set_decorated(False)
window.set_resizable(False)
x, y, width, height = fixture['window']
window.set_default_size(width, height)
window.move(x, y)
provider = Gtk.CssProvider()
color = ','.join(str(c) for c in fixture['rgb'])
provider.load_from_data(('window { background-image: none; background-color: rgb('+color+'); }').encode())
window.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
window.set_icon_from_file(str(workspace/'data/icons'/ (fixture['id']+'.svg')))
content = Gtk.Box(); content.set_size_request(width, height); window.add(content)
window.connect('destroy', Gtk.main_quit)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (Gtk.main_quit(), False)[1])
window.show_all()
Gtk.main()
