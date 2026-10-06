"""Owned native normal/modal fixtures; only real key events produce receipts."""
import json
import os
from pathlib import Path
import signal
import time
import gi
gi.require_version('Gtk','3.0')
gi.require_version('Gdk','3.0')
from gi.repository import Gdk, GLib, Gtk

workspace = Path(os.environ['HOME']).parent.resolve(strict=True)
if not workspace.name.startswith('GNOME-FOCUS-BASELINE-01-') or not os.environ.get('SYSPANE_GNOME_FOCUS_SCENARIOS'):
    raise ValueError('owned focus-scenario workspace required')
descriptor = os.open(workspace/'focus-control-events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
count = 0
windows = {}


def record(kind,role,event=None):
    global count
    count += 1
    if count > 128:raise ValueError('native control event capacity')
    row = {'event':kind,'role':role,'monotonic_ns':time.monotonic_ns(),'native_time':event.time if event else None}
    raw = (json.dumps(row,separators=(',',':'))+'\n').encode()
    if os.lseek(descriptor,0,os.SEEK_CUR)+len(raw)>32768:raise ValueError('native control journal capacity')
    if os.write(descriptor,raw)!=len(raw):raise ValueError('complete native control event required')


def create(role):
    geometry,color = {'alpha':([250,40,200,120],[32,160,64]),'beta':([250,380,200,160],[176,64,160]),
                      'modal':([260,390,180,120],[208,144,32])}[role]
    window = Gtk.Window(title='SysPane focus '+role)
    window.set_wmclass('syspane-focus-'+role,'SysPaneFocus'+role.title())
    window.set_decorated(False);window.set_resizable(False)
    window.set_default_size(*geometry[2:]);window.move(*geometry[:2])
    if role=='modal':
        window.set_transient_for(windows['beta']);window.set_modal(True);window.set_type_hint(Gdk.WindowTypeHint.DIALOG)
    provider = Gtk.CssProvider()
    provider.load_from_data(('window { background-image:none; background-color:rgb('+','.join(map(str,color))+'); }').encode())
    window.get_style_context().add_provider(provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    content=Gtk.Box();content.set_size_request(*geometry[2:]);window.add(content)
    def key(widget,event):
        name=Gdk.keyval_name(event.keyval)
        if name=='F9':record('key',role,event)
        elif name=='F6' and role=='beta' and 'modal' not in windows:record('open-modal',role,event);create('modal')
        elif name=='Escape' and role=='modal':record('close-modal',role,event);widget.destroy()
        return False
    def closed(widget):
        windows.pop(role,None);record('destroy',role)
        if not windows:Gtk.main_quit()
    window.connect('key-press-event',key);window.connect('destroy',closed)
    windows[role]=window;window.show_all();record('created',role)


if os.environ['SYSPANE_GNOME_FOCUS_SCENARIOS']=='helper-exit':
    record('exit-control','helper');os.close(descriptor);raise SystemExit(7)

GLib.set_prgname('syspane-focus-controls')
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,lambda:(Gtk.main_quit(),False)[1])
try:
    create('alpha');create('beta');Gtk.main()
finally:os.close(descriptor)
