"""Calibrate error reporting on owned native processes and a private denied RPC."""
from pathlib import Path
from datetime import datetime,timezone
from types import SimpleNamespace
import ctypes as C,json,os,signal,subprocess,sys,threading,time,uuid
from native_editor import Harness,ROOT,sha,launch_xvfb
from native_observation import PREFIX,Observations
from gi.repository import Gio,GLib
CASES=json.loads((ROOT/'tests/editor/observation-cases.json').read_text())

def denied_service():
    service=Observations({});path='/org/a11y/atspi/accessible/denied'
    info=Gio.DBusNodeInfo.new_for_xml('<node><interface name="org.a11y.atspi.Accessible"><method name="GetInterfaces"><arg type="as" direction="out"/></method><method name="GetState"><arg type="au" direction="out"/></method></interface></node>')
    def deny(connection,sender,path,interface,method,parameters,invocation):
        invocation.return_dbus_error('org.freedesktop.DBus.Error.AccessDenied','Calibration denied')
    service.bus.register_object(path,info.interfaces[0],deny,None,None)
    print(json.dumps([service.bus.get_unique_name(),path]),flush=True)
    GLib.timeout_add_seconds(30,lambda:os._exit(70));GLib.MainLoop().run()

def observe(exe,exit_exe,folder,mode):
    h=Harness(exe,exit_exe,folder,'drag');service=None
    h.report.update(family=CASES['family'],case=mode,oracle_sha256=sha(Path(__file__)),calibration_sha256=sha(ROOT/'tests/editor/observation-cases.json'))
    try:
        h.launch();h.point(60,60);h.wait(lambda:h.value('title')==CASES['expected_title']);h.focus('cancel')
        title=h.find('value.title');button=h.find('cancel');assert h.text(title)==CASES['expected_title'] and not h.erased(title)
        def capture(name,call):
            started=time.monotonic();row={'name':name}
            try:row['value']=call()
            except Exception as error:row['error']=str(error);row['remote']=Gio.DBusError.get_remote_error(error) if isinstance(error,GLib.GError) else None
            row['duration_ms']=(time.monotonic()-started)*1000;h.report.setdefault('calibrations',[]).append(row);return row
        if mode=='live':
            assert PREFIX+'Text' not in h.observer.interfaces(button)
            assert h.state(button,h.Atspi.StateType.FOCUSED);h.command('close');h.wait(lambda:h.erased(title))
        elif mode=='unfocused':
            h.focus('value.title');assert not h.state(button,h.Atspi.StateType.FOCUSED)
            row=capture('unfocused',lambda:h.wait(lambda:h.state(button,h.Atspi.StateType.FOCUSED),CASES['unfocused_wait_ms']/1000))
            assert 'observation deadline' in row['error'] and h.state(title,h.Atspi.StateType.FOCUSED)
        elif mode in ('short-stop','long-stop'):
            h.input.x.XGetInputFocus.argtypes=[C.c_void_p,C.POINTER(C.c_ulong),C.POINTER(C.c_int)]
            def xfocus():
                value=C.c_ulong();revert=C.c_int();h.input.x.XGetInputFocus(h.input.handle,C.byref(value),C.byref(revert));return value.value
            focus=xfocus();assert focus in h.input.windows(h.pid);h.report['x_focus']=focus
            reads=[('text',lambda:h.text(title)),('focus',lambda:h.state(button,h.Atspi.StateType.FOCUSED)),('erased',lambda:h.wait(lambda:h.erased(title),CASES['erase_ms']/1000))] if mode=='long-stop' else [('text',lambda:h.wait(lambda:h.text(title)==CASES['expected_title']))]
            for name,read in reads:
                stopped=time.monotonic();os.kill(h.pid,signal.SIGSTOP);resumed=[]
                def resume():
                    try:os.kill(h.pid,signal.SIGCONT)
                    except ProcessLookupError:pass
                    finally:resumed.append(time.monotonic())
                timer=threading.Timer(CASES[mode.replace('-','_')+'_ms']/1000,resume);timer.start()
                try:
                    assert Path('/proc/'+str(h.pid)+'/stat').read_text().split(') ')[1][0] in ('T','t')
                    row=capture(name,read);assert xfocus()==focus and h.proc.poll() is None
                    if mode=='long-stop':assert 'value' not in row and ('Timeout' in row['error'] or 'observation deadline' in row['error'])
                    else:assert row['value'] is True
                finally:
                    timer.join(timeout=1)
                    if not resumed:resume();timer.cancel();timer.join(timeout=1)
                    row['stop_ms']=(resumed[0]-stopped)*1000
                h.wait(lambda:h.text(title)==CASES['expected_title']);assert not h.erased(title)
        elif mode=='dead':
            h.command('quit');assert h.proc.wait(timeout=5)==0
            for name,call in [('text',lambda:h.text(title)),('focus',lambda:h.state(button,h.Atspi.StateType.FOCUSED)),('erased',lambda:h.erased(title))]:
                row=capture(name,call);assert row.get('remote') in ('org.freedesktop.DBus.Error.ServiceUnknown','org.freedesktop.DBus.Error.NameHasNoOwner') and 'value' not in row
        elif mode in ('removed','denied'):
            # Preserve the real object's address; only this calibration target uses
            # a deliberately absent path or an independent denied service.
            token=object()
            if mode=='removed':name=h.observer.identity(title)[0];path='/org/a11y/atspi/accessible/999999999'
            else:
                service=subprocess.Popen([sys.executable,str(Path(__file__)),'--denied'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                import select
                assert select.select([service.stdout],[],[],5)[0]
                name,path=json.loads(service.stdout.readline())
            h.observer.addresses[token]=(name,path)
            row=capture('text',lambda:h.text(token));assert 'value' not in row
            if mode=='removed':
                assert row['remote']=='org.freedesktop.DBus.Error.UnknownObject';assert h.erased(token)
            else:
                assert row['remote']=='org.freedesktop.DBus.Error.AccessDenied'
                for name,call in [('focus',lambda:h.state(token,h.Atspi.StateType.FOCUSED)),('erased',lambda:h.erased(token))]:
                    row=capture(name,call);assert row.get('remote')=='org.freedesktop.DBus.Error.AccessDenied' and 'value' not in row
        else:raise AssertionError(mode)
        if mode!='dead':h.command('quit');assert h.proc.wait(timeout=5)==0
        h.report['outcome']='pass'
    finally:
        if service:service.terminate();service.communicate(timeout=5)
        h.close()

def main():
    if sys.argv[1]=='--denied':denied_service();return
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('editor-observation-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),helper_sha256=sha(ROOT/'tests/editor/native_observation.py'),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/observation-cases.json'),executable_sha256=sha(exe),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=CASES['child_seconds'])
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err)
            result=json.loads((folder/mode/'result.json').read_text());report['cases'].append(dict(case=mode,outcome=result['outcome'],record_sha256=sha(folder/mode/'result.json')))
            assert child.returncode==0 and result['outcome']=='pass',(mode,err.decode(errors='replace'))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
