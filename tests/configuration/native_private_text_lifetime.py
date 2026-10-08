"""Independent lifetime/selection oracle for the shared native private text control."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes as C
import hashlib,json,os,resource,signal,subprocess,sys,time,traceback,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/configuration'),str(ROOT/'tests/editor'),str(ROOT/'tests/fault'),str(ROOT/'tests/desktop'),str(ROOT/'source/build')]
from native_settings import Keys
from native_diagnostic import launch_xvfb
from clipboard_peer import Peer,Event
from check_surface_runtime import verify
CASES=json.loads((ROOT/'tests/configuration/private-text-lifetime-cases.json').read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()

class Selections(Peer):
    def __init__(self):
        super().__init__();self.held={self.atom(n):self.own(selection=self.atom(n)) for n in CASES['selections']};self.cleared=0
    def check(self):
        self.sync()
        for _ in range(128):
            if not self.x.XPending(self.handle):break
            event=Event();self.x.XNextEvent(self.handle,C.byref(event))
            if event.type==29:self.cleared+=1
        assert not self.x.XPending(self.handle),'unbounded selection events'
        assert not self.cleared,'foreign selection ownership changed'
        assert all(self.owner(atom)==window for atom,window in self.held.items()),'foreign selection owner lost'

def observe(exe,folder,mode):
    import gi
    gi.require_version('Atspi','2.0');gi.require_version('Gtk','3.0')
    from gi.repository import Atspi,GLib,Gtk
    Gtk.init([]);Atspi.set_timeout(200,500);verify();folder.mkdir(mode=0o700)
    report=dict(case=mode,outcome='fail',observations=[],started_at=datetime.now(timezone.utc).isoformat());proc=None;keys=None;guard=Selections()
    error=(folder/'stderr').open('wb')
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
        guard.check()
    def wait(predicate):
        deadline=time.monotonic()+CASES['observation_timeout_seconds']
        while True:
            pump();assert proc.poll() is None,('consumer exit',proc.returncode)
            value=predicate()
            if value:return value
            assert time.monotonic()<deadline,'observation deadline'
            time.sleep(.005)
    def objects():
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];out=[]
        for n in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(n)
            if app and app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            obj,depth=pending.pop()
            if obj is None:continue
            obj.clear_cache();out.append(obj);assert len(out)<=128 and depth<=16
            for n in range(obj.get_child_count()):pending.append((obj.get_child_at_index(n),depth+1))
        return out
    def find(name):return next((o for o in objects() if o.get_description()==name),None)
    def text(obj):
        if not obj:return ''
        obj.clear_cache();interface=obj.get_text_iface();return Atspi.Text.get_text(interface,0,-1) if interface else obj.get_name() or ''
    def click(name):
        obj=find(name);assert obj and obj.get_state_set().contains(Atspi.StateType.SENSITIVE)
        assert obj.get_component_iface().grab_focus();keys.press(0x20)
    def selection():
        obj=find('private.text');interface=obj.get_text_iface();assert Atspi.Text.get_n_selections(interface)==1
        selected=Atspi.Text.get_selection(interface,0)
        assert selected.start_offset==0 and selected.end_offset==len(CASES['text'])
        assert text(obj)==CASES['text']
    try:
        if mode=='OBSERVER-CONTROL':
            other=Peer()
            try:
                for atom,window in guard.held.items():
                    other.own(selection=atom);guard.x.XSetSelectionOwner(guard.handle,atom,window,0);guard.sync()
                try:guard.check()
                except AssertionError as exc:assert str(exc)=='foreign selection ownership changed';report['detected']=str(exc)
                else:raise AssertionError('transient selection transfer was missed')
            finally:other.close()
            assert guard.cleared==2
        else:
            proc=subprocess.Popen([str(exe),mode,CASES['text']],cwd=folder,env=dict(os.environ,G_DEBUG='fatal-criticals'),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=error,
                preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
            if mode=='NEVER-REALIZED':assert proc.wait(timeout=5)==0;guard.check()
            else:
                wait(lambda:find('private.text'));keys=Keys(proc.pid);obj=find('private.text')
                assert obj.get_component_iface().grab_focus();keys.press(ord('a'),True)
                wait(lambda:Atspi.Text.get_n_selections(find('private.text').get_text_iface())==1);selection()
                keys.press(ord('c'),True);keys.press(ord('x'),True)
                Atspi.EditableText.copy_text(obj.get_editable_text_iface(),0,len(CASES['text']))
                Atspi.EditableText.cut_text(obj.get_editable_text_iface(),0,len(CASES['text']));pump();selection()
                if mode=='CYCLE':
                    for n in range(CASES['cycles']):
                        click('private.cycle');wait(lambda:text(find('private.status'))=='cycle '+str(n+1));selection();report['observations'].append(dict(cycle=n+1,text_and_selection_preserved=True))
                    obj=find('private.text');assert Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),CASES['replacement'])
                    wait(lambda:text(find('private.text'))==CASES['replacement']);pump()
                else:
                    click('private.destroy');wait(lambda:text(find('private.status'))=='destroyed');assert find('private.text') is None
                click('private.quit');assert proc.wait(timeout=5)==0;guard.check()
            error.flush();diagnostic=(folder/'stderr').read_text(errors='replace')
            assert 'CRITICAL' not in diagnostic and 'WARNING' not in diagnostic,diagnostic
            report['exit']=proc.returncode;report['selection_clear_events']=guard.cleared
        report['outcome']='pass'
    except Exception:
        report['failure']=traceback.format_exc();raise
    finally:
        if proc and proc.poll() is None:proc.kill();proc.wait(timeout=5)
        if keys:keys.close()
        guard.close();error.close();report['finished_at']=datetime.now(timezone.utc).isoformat()
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4]);return
    exe,evidence=map(Path,sys.argv[1:3]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('private-text-'+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700);server=None
    report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            proc=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:stdout,stderr=proc.communicate(timeout=CASES['case_timeout_seconds'])
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate(timeout=5);raise AssertionError('observer deadline')
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
            assert proc.returncode==0,(mode,stderr.decode(errors='replace'))
            case=folder/mode/'result.json';assert json.loads(case.read_bytes())['outcome']=='pass'
            report['cases'].append(dict(case=mode,outcome='pass',record_sha256=sha(case.read_bytes())))
        report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
