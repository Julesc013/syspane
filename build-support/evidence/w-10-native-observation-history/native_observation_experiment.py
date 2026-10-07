"""Compare native API absence with explicit wire errors on owned GTK children."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes as C,hashlib,json,os,signal,subprocess,sys,threading,time,uuid
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tests/editor')]
from native_editor import Harness,launch_xvfb,sha
def observe(exe,exit_exe,folder,mode):
    from gi.repository import Gio,GLib
    h=Harness(exe,exit_exe,folder,'drag',large=mode=='large');rows=[]
    h.report.update(family='NATIVE-OBSERVATION',case=mode,probe_sha256=sha(Path(__file__)),queries=rows)
    try:
        h.launch();h.check();h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane')
        button=h.find('cancel');text=h.find('value.title')
        from check_surface_runtime import identify
        h.report['runtime']=identify();h.report['expected_text']='Editable pane'
        session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        address=session.call_sync('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress',None,GLib.VariantType.new('(s)'),Gio.DBusCallFlags.NONE,200,None).unpack()[0]
        bus=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
        identities={id:(obj.app.bus_name,obj.path) for id,obj in [('button',button),('text',text)]};h.report['objects']=identities
        def wire(id,interface,method,args=None,signature=None):
            name,path=identities[id]
            return bus.call_sync(name,path,'org.a11y.atspi.'+interface,method,args,GLib.VariantType.new(signature) if signature else None,Gio.DBusCallFlags.NONE,200,None).unpack()
        h.input.x.XGetInputFocus.argtypes=[C.c_void_p,C.POINTER(C.c_ulong),C.POINTER(C.c_int)]
        def xfocus():
            value=C.c_ulong();revert=C.c_int();h.input.x.XGetInputFocus(h.input.handle,C.byref(value),C.byref(revert));return value.value
        assert wire('button','Component','GrabFocus',signature='(b)')==(True,)
        bit=int(h.Atspi.StateType.FOCUSED)
        h.wait(lambda:bool(wire('button','Accessible','GetState',signature='(au)')[0][bit//32]&(1<<(bit%32))))
        h.report['x_focus']=xfocus();h.report['owner_windows']=list(h.input.windows(h.pid))
        def api_state():button.clear_cache();return [str(s) for s in button.get_state_set().get_states()]
        def api_interface():button.clear_cache();return button.get_component_iface() is not None
        def api_text():return h.text(text)
        calls=[('api.state',api_state),('api.component',api_interface),('api.text',api_text),('wire.state',lambda:wire('button','Accessible','GetState',signature='(au)')),('wire.interfaces',lambda:wire('button','Accessible','GetInterfaces',signature='(as)')),('wire.text',lambda:wire('text','Text','GetText',GLib.Variant('(ii)',(0,-1)),'(s)'))]
        if mode=='dead':h.command('quit');assert h.proc.wait(timeout=5)==0
        for name,call in calls:
            timer=None;resumed=threading.Event();stop_times={}
            def resume():
                try:os.kill(h.pid,signal.SIGCONT)
                except ProcessLookupError:pass
                finally:stop_times['resumed']=time.monotonic();resumed.set()
            try:
                if mode in ('short-stop','long-stop'):
                    stop_times['stopped']=time.monotonic();os.kill(h.pid,signal.SIGSTOP);timer=threading.Timer(.05 if mode=='short-stop' else .35,resume);timer.start()
                    assert Path('/proc/'+str(h.pid)+'/stat').read_text().split(') ')[1][0] in ('T','t')
                started=time.monotonic();row={'method':name,'started':started,'x_focus':xfocus()}
                try:row['value']=call()
                except Exception as error:row['error']={'type':type(error).__name__,'text':str(error)}
                row['duration_ms']=(time.monotonic()-started)*1000;row['process_exit']=h.proc.poll();rows.append(row)
            finally:
                if timer:
                    timer.join(timeout=1)
                    if not resumed.is_set():resume();timer.cancel();timer.join(timeout=1)
                    assert resumed.is_set();row['stop_times']=stop_times
            if mode!='dead':
                h.wait(lambda:bool(wire('button','Accessible','GetState',signature='(au)')[0][bit//32]&(1<<(bit%32))))
        if mode!='dead':h.command('quit');assert h.proc.wait(timeout=5)==0
        h.report['outcome']='observed'
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('observation-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='NATIVE-OBSERVATION',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),probe_sha256=sha(Path(__file__)),executable_sha256=sha(exe),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in ('live','large','short-stop','long-stop','dead'):
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err);assert child.returncode==0,(mode,err.decode(errors='replace'))
            report['cases'].append(dict(case=mode,record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='observed'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
