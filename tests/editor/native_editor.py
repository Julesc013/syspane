"""Independent native input, pixels, accessibility, storage and held-child oracle."""
from pathlib import Path
from datetime import datetime,timezone
import copy,ctypes as C,hashlib,json,os,queue,select,signal,struct,subprocess,sys,threading,time,uuid,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/configuration'),str(ROOT/'tests/desktop'),str(ROOT/'tests/fault'),str(ROOT/'build-support')]
from native_settings import stored,check_resources
from native_diagnostic import launch_xvfb
from native_editor_exit import Observer
from check_surface_runtime import verify
from native_observation import Observations,Unavailable
CASES=json.loads((ROOT/'tests/editor/native-cases.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

class Input(Observer):
    def focus(self,pid):
        found=[]
        for win in self.windows(pid):
            name=C.c_void_p()
            if not self.x.XFetchName(self.handle,win,C.byref(name)):continue
            try:
                if C.string_at(name)==b'SysPane Editor':found.append(win)
            finally:self.x.XFree(name)
        assert len(found)==1,found
        self.x.XSetInputFocus(self.handle,found[0],1,0);self.sync()
    def press(self,symbol,control=False,shift=False,alt=False):
        keys=([0xffe3] if control else [])+([0xffe1] if shift else [])+([0xffe9] if alt else [])+[symbol]
        for key in keys:self.key(key,True)
        for key in reversed(keys):self.key(key,False)
        self.sync()
    def motion(self,x,y):assert self.xt.XTestFakeMotionEvent(self.handle,0,int(x),int(y),0);self.sync()
    def button(self,down):assert self.xt.XTestFakeButtonEvent(self.handle,1,down,0);self.sync()

class Harness:
    def __init__(self,exe,exit_exe,folder,mode,large=False,arrange=False,group=False,snap=False,properties=False,layout=False):
        import gi
        gi.require_version('Atspi','2.0');gi.require_version('Gtk','3.0')
        from gi.repository import Atspi,GLib,Gtk,Gdk
        self.Atspi,self.GLib,self.Gtk,self.Gdk=Atspi,GLib,Gtk,Gdk
        Gtk.init([]);Atspi.set_timeout(200,500);verify();folder.mkdir(mode=0o700)
        assert sum((large,arrange,group,snap,properties,layout))<=1
        self.layout=layout;self.large=large;self.arrange=arrange;self.group=group;self.snap=snap;self.properties=properties;self.case_path=ROOT/('tests/editor/layout-authoring-cases.json' if layout else 'tests/configuration/large-command-cases.json' if large else 'tests/editor/arrange-cases.json' if arrange else 'tests/editor/group-cases.json' if group else 'tests/editor/snap-cases.json' if snap else 'tests/editor/content-properties-cases.json' if properties else 'tests/editor/native-cases.json')
        self.cases=json.loads(self.case_path.read_text())
        if large:self.cases['drag']['expected']=self.cases['moved_scene']
        self.exe,self.exit_exe,self.folder,self.mode=exe,exit_exe,folder,mode
        self.directory=folder/'store';self.directory.mkdir(mode=0o700)
        assert subprocess.check_output(['findmnt','--target',str(self.directory),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
        self.proc=None;self.pid=None;self.fd=None;self.stage='startup';self.events=queue.Queue();self.inbox=[];self.input=Input();self.controls={}
        self.err=(folder/'stderr').open('wb')
        self.report=dict(outcome='fail',mode=mode,events=[],observations=[],executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),fixture_sha256=sha(self.case_path))
        self.observer=Observations(self.report);self.report['observation_helper_sha256']=sha(ROOT/'tests/editor/native_observation.py')
    def launch(self,mode=None,recovery=False):
        self.controls.clear();self.observer.addresses.clear()
        args=[str(self.exit_exe),'--owned-editor-lab',str(self.exe),str(ROOT),str(self.directory),'drag'] if recovery else [str(self.exe),str(ROOT),str(self.directory),("layout-" if self.layout else "large-" if self.large else "arrange-" if self.arrange else "group-" if self.group else "snap-" if self.snap else "properties-" if self.properties else "")+(mode or self.mode)]
        self.proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,bufsize=0)
        def collect(child):
            for line in child.stdout:
                item=json.loads(line);self.report['events'].append(item);self.events.put(item)
        threading.Thread(target=collect,args=(self.proc,),daemon=True).start()
        if recovery:
            self.pid=self.event('event','child')['value'];self.fd=os.pidfd_open(self.pid)
        else:self.event('ready',True);self.pid=self.proc.pid
        self.wait(lambda:self.find('status'));self.input.focus(self.pid)
        self.wait(lambda:'Move me' in self.text(self.find('canvas')) if mode!='reopen' else self.find('canvas'))
    def pump(self):
        context=self.GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(self,predicate,seconds=3):
        previous=self.observer.deadline;end=min(time.monotonic()+seconds,previous or float('inf'))
        self.observer.deadline=end
        try:
            while True:
                self.pump()
                try:value=predicate()
                except (self.GLib.GError,Unavailable) as error:
                    if not self.observer.retryable(error):raise
                    value=False
                assert time.monotonic()<end,self.stage+' observation deadline'
                if value:return value
                time.sleep(.005)
        finally:self.observer.deadline=previous
    def event(self,key,value):
        end=time.monotonic()+5
        while time.monotonic()<end:
            for n,item in enumerate(self.inbox):
                assert item.get('event')!='error',item
                if item.get(key)==value:return self.inbox.pop(n)
            try:self.inbox.append(self.events.get(timeout=.01))
            except queue.Empty:pass
        raise AssertionError((self.stage,'event deadline',key,value,self.inbox))
    def command(self,value):
        started=time.monotonic();self.proc.stdin.write((value+'\n').encode());self.event('ack',value);return started
    def objects(self):
        desktop=self.Atspi.get_desktop(0);desktop.clear_cache();pending=[];out=[]
        for n in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(n)
            if app.get_process_id()==self.pid:pending.append((app,0))
        while pending:
            obj,depth=pending.pop()
            # GTK can remove a list cell between count and indexed child reads.
            # Required controls/results are still independently awaited below.
            if obj is None:continue
            obj.clear_cache();self.observer.identity(obj);out.append(obj);assert len(out)<=512 and depth<=20
            for n in range(obj.get_child_count()):pending.append((obj.get_child_at_index(n),depth+1))
        return out
    def find(self,id):
        # These chrome objects live for the entire form. Cache references, never
        # text/state/geometry: each read still observes the live native interface.
        # Reopening starts a different process and discards every old reference.
        if id not in self.controls:
            for obj in self.objects():
                description=obj.get_description() or ''
                if description.startswith('editor.'):self.controls[description[7:]]=obj
            assert len(self.controls)<=64
        return self.controls.get(id)
    def text(self,obj):
        return self.observer.text(obj)
    def erased(self,obj):
        try:return self.text(obj)==''
        except self.GLib.GError as error:
            # A destroyed native cell may no longer have an exported object. This
            # is distinct from a timeout, disconnected application or stale text.
            if self.observer.removed(error):
                assert self.proc.poll() is None
                self.observer.interfaces(self.find('status'))
                return True
            raise
    def value(self,id):return self.text(self.find('value.'+id))
    def number(self,id):return float(self.value(id)) if self.value(id) else None
    def status(self):return self.text(self.find('status'))
    def sensitive(self,id):
        return self.state(self.find(id),self.Atspi.StateType.SENSITIVE)
    def state(self,obj,state):return self.observer.state(obj,state)
    def extents(self,obj):return self.observer.extents(obj)
    def focus_snapshot(self,id):
        self.input.x.XGetInputFocus.argtypes=[C.c_void_p,C.POINTER(C.c_ulong),C.POINTER(C.c_int)]
        value=C.c_ulong();revert=C.c_int();self.input.x.XGetInputFocus(self.input.handle,C.byref(value),C.byref(revert))
        result=dict(control=id,x_focus=value.value,owner_windows=list(self.input.windows(self.pid)),process_exit=self.proc.poll())
        try:
            obj=self.find(id);result['object']=self.observer.identity(obj)
            result['focused']=self.state(obj,self.Atspi.StateType.FOCUSED)
            result['sensitive']=self.sensitive(id)
        except Exception as error:result['observation_error']=str(error)
        return result
    def focus(self,id):
        try:
            obj=self.find(id);assert self.observer.focus(obj)
            self.wait(lambda:self.state(obj,self.Atspi.StateType.FOCUSED))
        except Exception:
            self.report['focus_failure']=self.focus_snapshot(id)
            raise
    def click(self,id):
        assert self.sensitive(id),(id,self.status());self.focus(id);self.input.press(0x20)
    def field(self,id,value):
        obj=self.find('value.'+id);assert self.sensitive('value.'+id)
        assert self.Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(value));self.wait(lambda:self.value(id)==str(value))
    def rect(self):return self.extents(self.find('canvas'))
    def point(self,x,y,shift=False):
        rect=self.rect()
        if shift:self.input.key(0xffe1,True)
        self.input.click(rect.x+x,rect.y+y)
        if shift:self.input.key(0xffe1,False);self.input.sync()
    def drag(self,x,y,dx,dy,hold=False):
        rect=self.rect();self.input.motion(rect.x+x,rect.y+y);self.input.button(True);time.sleep(.06)
        self.input.motion(rect.x+x+dx,rect.y+y+dy);time.sleep(.06)
        if not hold:self.input.button(False)
    def pixels(self,x,y,w,h):
        rect=self.rect();return self.input.capture(rect.x+x,rect.y+y,w,h)
    def screenshot(self,name):
        raw=self.input.capture(0,0,800,600)
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data))
        pixels=b''.join(b'\0'+raw[n*2400:(n+1)*2400] for n in range(600))
        (self.folder/(name+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',800,600,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
    def documents(self,scene=None,revision='40'):
        value=copy.deepcopy(self.cases['authored'])
        if scene is not None:value['scene']=copy.deepcopy(scene)
        for doc in value.values():doc['revision']=revision
        return value
    def check(self,scene=None,revision='40'):
        assert stored(self.directory)==self.documents(scene,revision),'stored documents differ';check_resources(self.directory,manifest_version="0.3.0" if self.large else "0.2.0")
    def note(self,name):self.report['observations'].append(dict(case=name,status=self.status(),documents=stored(self.directory)))
    def close(self):
        if self.proc and self.proc.poll() is None:self.proc.kill();self.proc.wait(timeout=5)
        if self.fd is not None:
            if not select.select([self.fd],[],[],0)[0]:signal.pidfd_send_signal(self.fd,signal.SIGKILL)
            assert select.select([self.fd],[],[],3)[0];os.close(self.fd)
        self.input.close();self.err.close();(self.folder/'result.json').write_text(json.dumps(self.report,indent=2)+'\n')

def exercise(h):
    CASES=h.cases
    mode=h.mode;h.launch()
    if mode=='conflict':
        other=copy.deepcopy(CASES['authored']['scene']);other['widgets'][0]['title']='Theirs';h.check(other,'41')
    else:h.check()
    h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane');h.screenshot('initial')
    expected=copy.deepcopy(CASES['drag']['expected']);baseline=h.pixels(44,44,170,68)
    assert len(set(baseline))>2,'text preview missing'
    if mode=='frozen-preview':h.command('freeze-preview')
    h.stage='EDIT'
    if mode=='keyboard':
        for _ in range(3):h.input.press(0xff53,shift=True)
        for _ in range(2):h.input.press(0xff54,shift=True)
    elif mode=='resize':
        h.drag(217,117,20,10);h.wait(lambda:h.number('width')==200 and h.number('height')==90)
        expected=copy.deepcopy(CASES['authored']['scene']);expected['widgets'][0]['layout']['base'].update(CASES['resize'])
    elif mode=='properties':
        expected=copy.deepcopy(CASES['properties']);h.field('title','Renamed pane');h.field('x','1e2');h.click('properties')
        h.wait(lambda:'Enter a number' in h.status());assert h.value('x')=='1e2' and not h.sensitive('apply');h.check()
        h.command('topology');assert h.value('x')=='1e2' and h.value('title')=='Renamed pane' and not h.sensitive('apply')
        for key,value in dict(title='Renamed pane',body='Updated body',x=125,y=135,width=210,height=90).items():h.field(key,value)
        obj=h.find('value.body');assert h.observer.focus(obj);h.input.press(ord('a'),control=True);h.input.press(ord('c'),control=True)
        h.Atspi.EditableText.copy_text(obj.get_editable_text_iface(),0,12);h.pump()
        assert h.Gtk.Clipboard.get(h.Gdk.SELECTION_PRIMARY).wait_for_text() is None
        assert h.Gtk.Clipboard.get(h.Gdk.SELECTION_CLIPBOARD).wait_for_text() is None
        h.click('properties');h.wait(lambda:h.number('x')==125 and h.sensitive('apply'))
        h.click('undo');h.wait(lambda:h.value('title')=='Editable pane');h.click('redo');h.wait(lambda:h.value('title')=='Renamed pane')
    elif mode=='multi':
        h.point(300,60,True);h.input.press(0xff53,shift=True);h.wait(lambda:'Draft changes' in h.status())
        expected=copy.deepcopy(CASES['authored']['scene'])
        for widget in expected['widgets'][:2]:widget['layout']['base']['x']+=CASES['multi_dx']
    elif mode=='structure':
        h.click('add');h.wait(lambda:h.value('title')=='Text');h.click('duplicate');h.wait(lambda:h.find('objects').get_table_iface().get_n_rows()==5);h.click('delete');h.wait(lambda:h.value('title')=='')
        # Add and duplicate allocate new1 and new2; duplicate selects the new copy.
        expected=copy.deepcopy(CASES['authored']['scene']);new=dict(id='widget:new1',kind='text',title='Text',content=dict(body='Text'),display=dict(local_id='D1'),layout=dict(base=dict(kind='fixed',x=20,y=20,width=180,height=80)),bindings=[],priority='normal')
        expected['widgets'].append(new);expected['roots'].append(new['id'])
    else:
        if mode=='topology':
            h.drag(60,60,15,5,True);h.command('topology');h.input.button(False);h.wait(lambda:h.number('x')==40);h.check()
        h.drag(60,60,30,20)
    if mode in ('drag','keyboard','cancel','conflict','deny','revoke','restart','topology','frozen-preview','wrong-commit','retain'):
        h.wait(lambda:h.number('x')==70 and h.number('y')==60);h.stage='PIXEL_MOVE'
        h.wait(lambda:h.pixels(74,64,170,68)==baseline)
        assert h.pixels(44,44,20,10)!=baseline[:600],'old preview remained'
        if mode=='drag':
            h.click('undo');h.wait(lambda:h.number('x')==40 and h.number('y')==40);assert not h.sensitive('undo')
            h.click('redo');h.wait(lambda:h.number('x')==70 and h.number('y')==60)
            # Escape cancels a held gesture, with no new history entry or save.
            h.drag(90,80,12,8,True);h.input.press(0xff1b);h.input.button(False);assert h.number('x')==70
    h.screenshot('edited');h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted')
    if mode!='wrong-commit':assert submitted['body']['operations'][0]['scene']==expected
    if mode=='conflict':
        assert h.event('event','result')['result']['outcome']=='conflict';h.wait(lambda:'Configuration changed' in h.status())
        other=copy.deepcopy(CASES['authored']['scene']);other['widgets'][0]['title']='Theirs';h.check(other,'41');h.click('reload');h.event('event','reloaded');h.point(60,60);h.wait(lambda:h.value('title')=='Theirs');h.note('CONFLICT')
    else:
        h.event('event','held');h.check();assert 'Request pending' in h.status() and not h.sensitive('cancel') and not h.sensitive('apply')
        if mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
        if mode=='deny':h.command('deny')
        if mode in ('revoke','retain'):
            h.stage='REVOKE';held=[h.find('value.'+id) for id in ('title','body','x','y','width','height')];held+= [o for o in h.objects() if 'Editable pane' in h.text(o) or 'Move me' in h.text(o)]
            issued=h.command('revoke')
            def erased():return all(h.erased(o) for o in held) and not any('Retained editor canary' in h.text(o) for o in h.objects()) and set(h.pixels(0,0,500,420))=={0}
            h.wait(erased,max(.001,issued+CASES['erase_ms']/1000-time.monotonic()));h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms']
        h.command('release');result=h.event('event','result')['result'];h.stage='RESULT'
        if mode in ('cancel','deny','revoke'):
            h.check()
            if mode=='deny':
                assert result['outcome']=='unknown' and result['error']['code']=='policy.denied'
                assert all(result[k] is None for k in ('revision','stored','durable','visible'))
                h.wait(lambda:'Outcome unknown' in h.status());h.command('regrant');h.command('retrieve');result=h.event('event','retrieved')['result']
            assert result['outcome']==('cancelled' if mode=='cancel' else 'conflict') and result['revision']=='40'
            if mode=='cancel':
                h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.check();h.report['outcome']='pass';return
            if mode=='revoke':
                h.command('regrant');assert all(h.erased(o) for o in held);assert h.text(h.find('canvas'))==''
            h.click('reload');h.event('event','reloaded');h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane')
        else:
            assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] is True and result['visible'] is False
            h.stage='STORE';h.check(expected,'41')
            if mode=='restart':
                h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
            h.wait(lambda:'Saved durably' in h.status() and 'Visibility unconfirmed' in h.status());h.note('DURABLE')
            if mode=='drag':
                h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.point(90,80);h.wait(lambda:h.number('x')==70);h.check(expected,'41');h.note('REOPEN')
    h.stage='CLOSE';held=h.find('value.title');h.command('close');h.wait(lambda:h.text(held)=='');h.command('quit');assert h.proc.wait(timeout=5)==0
    assert mode not in ('frozen-preview','wrong-commit','retain'),'deliberate fault escaped observer';h.report['outcome']='pass'

def recovery(h):
    CASES=h.cases
    mode=h.mode[9:];h.stage='RECOVERY';assert h.input.pixel()=='116633';h.input.click();assert h.input.clicks()==1
    if mode=='conflict':
        h.input.grab();h.proc=subprocess.Popen([str(h.exit_exe),'--owned-editor-lab',str(h.exe),str(ROOT),str(h.directory),'drag'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err=h.proc.communicate(timeout=5);assert h.proc.returncode==69 and not out and err.strip()==b'editor.shortcut_unavailable'
        assert not list(h.directory.iterdir());h.input.ungrab();h.report['outcome']='pass';return
    h.launch(recovery=True);assert sha(Path('/proc')/str(h.pid)/'exe')==sha(h.exe)
    status=(Path('/proc')/str(h.pid)/'status').read_text();assert int(next(line.split()[1] for line in status.splitlines() if line.startswith('PPid:')))==h.proc.pid
    h.check();h.point(60,60);h.wait(lambda:h.number('x')==40);h.drag(60,60,30,20);h.wait(lambda:h.number('x')==70);h.check()
    assert h.input.pixel()!='116633';h.input.clicks();h.input.click();assert h.input.clicks()==0
    if mode=='drag-frozen':h.drag(90,80,12,8,True);assert h.input.input_state()&256
    if mode!='owner-loss':
        signal.pidfd_send_signal(h.fd,signal.SIGSTOP);h.wait(lambda:'\nState:\tT' in (Path('/proc')/str(h.pid)/'status').read_text())
    started=time.monotonic()
    if mode=='owner-loss':h.proc.kill()
    elif mode=='button-frozen':
        button=h.input.recovery_button(h.proc.pid);assert button;h.input.click(button['root_x']+button['width']//2,button['root_y']+button['height']//2)
    else:h.input.chord()
    h.wait(lambda:select.select([h.fd],[],[],0)[0],1.5)
    if mode=='drag-frozen':h.input.button(False)
    h.wait(lambda:h.input.pixel()=='116633',1.5);h.input.clicks();h.input.click();assert h.input.clicks()==1
    h.report['recovery_ms']=(time.monotonic()-started)*1000;assert h.report['recovery_ms']<=CASES['recovery_ms']
    assert h.proc.wait(timeout=3)==(-9 if mode=='owner-loss' else 0);h.check();h.input.grab();h.input.ungrab()
    if mode!='owner-loss':h.event('event','child_signal');assert any(e['event']=='force_stop' for e in h.report['events'])
    h.report['outcome']='pass'

def observe(exe,exit_exe,folder,mode,large=False):
    h=Harness(exe,exit_exe,folder,mode,large)
    try:recovery(h) if mode.startswith('recovery-') else exercise(h)
    except AssertionError as exc:
        h.report.update(error=str(exc),stage=h.stage)
        if h.pid and h.proc.poll() is None and not mode.startswith('recovery-'):
            h.report['failure_status']=h.status();h.report['failure_fields']={k:h.value(k) for k in ('title','body','x','y','width','height')};h.screenshot('failure')
        frozen=mode=='frozen-preview' and h.stage=='PIXEL_MOVE' and str(exc)=='PIXEL_MOVE observation deadline' and h.number('x')==70 and stored(h.directory)==h.documents() and h.pixels(44,44,170,68)!=h.pixels(74,64,170,68)
        wrong=mode=='wrong-commit' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][0]['layout']['base']['x']==71 and h.number('x')==70
        retained=mode=='retain' and h.stage=='REVOKE' and str(exc)=='REVOKE observation deadline' and h.value('title')=='' and any('Retained editor canary' in h.text(o) for o in h.objects())
        if frozen or wrong or retained:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('editor-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-FORM',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in (*CASES['modes'],*('recovery-'+m for m in CASES['recovery_modes'])):
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:stdout,stderr=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5);raise AssertionError('observer deadline')
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
            assert child.returncode==0,(mode,stderr.decode(errors='replace'));case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass'
            report['cases'].append(dict(case=mode,outcome='pass',fault_detected=case.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
