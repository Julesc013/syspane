"""Independent native controls, X selections and coherent stored-document checks."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes as C
import copy,hashlib,json,os,queue,signal,struct,subprocess,sys,threading,time,uuid,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/fault'),str(ROOT/'tests/desktop'),str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from native_oracle import Display
from check_surface_runtime import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED=json.loads((ROOT/'tests/configuration/settings-cases.json').read_text())
CONTENT_CASES=json.loads((ROOT/'tests/configuration/settings-content-cases.json').read_text())
CONTENT_FIXTURE=json.loads((ROOT/'tests/configuration/settings-content-fixture.json').read_text())

class Keys(Display):
    def __init__(self,pid):
        super().__init__();p,w=C.c_void_p,C.c_ulong
        self.x.XQueryTree.argtypes=[p,w,C.POINTER(w),C.POINTER(w),C.POINTER(C.POINTER(w)),C.POINTER(C.c_uint)]
        self.x.XSetInputFocus.argtypes=[p,w,C.c_int,w];self.x.XGetInputFocus.argtypes=[p,C.POINTER(w),C.POINTER(C.c_int)]
        self.x.XGetGeometry.argtypes=[p,w,C.POINTER(w),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
        self.x.XKeysymToKeycode.argtypes=[p,w];self.x.XKeysymToKeycode.restype=C.c_ubyte
        self.xt=C.CDLL('libXtst.so.6');self.xt.XTestFakeKeyEvent.argtypes=[p,C.c_uint,C.c_int,w]
        root,parent,children,count=w(),w(),C.POINTER(w)(),C.c_uint();assert self.x.XQueryTree(self.handle,self.root,C.byref(root),C.byref(parent),C.byref(children),C.byref(count))
        found=[]
        try:
            for n in range(count.value):
                win=children[n]
                if self.property(win,'_NET_WM_PID')!=[pid]:continue
                name=C.c_void_p()
                if not self.x.XFetchName(self.handle,win,C.byref(name)):continue
                try:
                    if C.string_at(name)!=b'SysPane Settings':continue
                    root,x,y,width,height,border,depth=w(),C.c_int(),C.c_int(),C.c_uint(),C.c_uint(),C.c_uint(),C.c_uint()
                    assert self.x.XGetGeometry(self.handle,win,C.byref(root),C.byref(x),C.byref(y),C.byref(width),C.byref(height),C.byref(border),C.byref(depth))
                    if width.value>=100 and height.value>=100:found.append(win)
                finally:self.x.XFree(name)
        finally:
            if children:self.x.XFree(children)
        assert len(found)==1,found
        self.window=found[0];self.x.XSetInputFocus(self.handle,self.window,1,0);self.x.XSync(self.handle,False)
        focus,revert=w(),C.c_int();self.x.XGetInputFocus(self.handle,C.byref(focus),C.byref(revert));assert focus.value==self.window
    def press(self,symbol,control=False):
        key=self.x.XKeysymToKeycode(self.handle,symbol);modifier=self.x.XKeysymToKeycode(self.handle,0xffe3);assert key
        if control:assert self.xt.XTestFakeKeyEvent(self.handle,modifier,True,0)
        for down in (True,False):assert self.xt.XTestFakeKeyEvent(self.handle,key,down,0)
        if control:assert self.xt.XTestFakeKeyEvent(self.handle,modifier,False,0)
        self.x.XSync(self.handle,False)

def stored(directory):
    selector=json.loads((directory/'current.json').read_text());assert selector['version']=='0.1.0'
    generation=directory/selector['generation'];assert generation.parent==directory and generation.is_dir()
    assert sha(generation/'manifest.json')==selector['manifest'];manifest=json.loads((generation/'manifest.json').read_text())
    assert sha(generation/'settings.json')==manifest['settings'] and sha(generation/'scene.json')==manifest['scene']
    return {n:json.loads((generation/(n+'.json')).read_text()) for n in ('settings','scene')}

def documents(revision,edits=False):
    out={n:json.loads((ROOT/'spec/fixtures/valid'/(n+'.json' if n=='settings' else 'scene-portable.json')).read_text()) for n in ('settings','scene')}
    for n in out:out[n]['revision']=revision
    if edits:
        for setting in EXPECTED['settings']:
            group,key=setting['id'].split('.');out['settings'][group][key]=setting['edit']
    return out

def resource_index(directory,manifest_version="0.2.0"):
    selector=json.loads((directory/'current.json').read_text());generation=directory/selector['generation']
    assert generation.parent==directory and generation.is_dir()
    manifest=json.loads((generation/'manifest.json').read_text());assert manifest['version']==manifest_version and sha(generation/'manifest.json')==selector['manifest']
    assert sha(generation/'resources.json')==manifest['resources']
    return generation,json.loads((generation/'resources.json').read_text())

def check_resources(directory,theme='theme:native',manifest_version='0.2.0',fixture=CONTENT_FIXTURE):
    generation,index=resource_index(directory,manifest_version)
    assert index['selection']==fixture['selection'],'resource selection differs'
    expected={};pins=[]
    for package in fixture['packages']:
        raw=package['manifest'].encode();digest=hashlib.sha256(raw).hexdigest();pins.append(digest);expected['m-'+digest+'.json']=raw
        for raw in package['assets_hex'].values():
            raw=bytes.fromhex(raw);expected['a-'+hashlib.sha256(raw).hexdigest()+'.bin']=raw
    assert index==dict(version='0.1.0',selection=fixture['selection'],theme=fixture['themes'][theme],packages=sorted(pins))
    actual={p.name:p.read_bytes() for p in (generation/'resources').iterdir() if p.is_file() and not p.is_symlink()}
    assert actual==expected,'stored resource bytes differ'
    assert len(list((generation/'resources').iterdir()))==len(expected)

def observe(exe,folder,mode):
    import gi
    gi.require_version('Atspi','2.0');gi.require_version('Gtk','3.0')
    from gi.repository import Atspi,GLib,Gtk,Gdk
    Gtk.init([]);Atspi.set_timeout(200,500);verify();folder.mkdir(mode=0o700)
    resource=mode.startswith('resource-');behavior=mode[9:] if resource else mode
    directory=folder/'store';directory.mkdir(mode=0o700)
    assert subprocess.check_output(['findmnt','--target',str(directory),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(outcome='fail',mode=mode,events=[],observations=[],executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),fixture_sha256=sha(ROOT/'tests/configuration/settings-cases.json'),surface_runtime_sha256=sha(ROOT/'source/build/surface-runtime.json'),xtest_sha256=sha(Path('/usr/lib/x86_64-linux-gnu/libXtst.so.6')))
    if resource:report.update(resource_fixture_sha256=sha(ROOT/'tests/configuration/settings-content-fixture.json'),resource_cases_sha256=sha(ROOT/'tests/configuration/settings-content-cases.json'))
    err=(folder/'stderr').open('wb');proc=None;keys=None;stage='startup';events=queue.Queue();inbox=[]
    def launch(which):
        nonlocal proc,keys
        if resource and not which.startswith('resource-'):which='resource-'+which
        proc=subprocess.Popen([str(exe),str(ROOT),str(directory),which],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,bufsize=0)
        def collect(child):
            for line in child.stdout:
                item=json.loads(line);report['events'].append(item);events.put(item)
        threading.Thread(target=collect,args=(proc,),daemon=True).start();event('ready',True);keys=Keys(proc.pid)
    def event(key,value):
        end=time.monotonic()+5
        while time.monotonic()<end:
            for n,item in enumerate(inbox):
                assert item.get('event')!='error',item
                if item.get(key)==value:return inbox.pop(n)
            try:inbox.append(events.get(timeout=.02))
            except queue.Empty:pass
        raise AssertionError((stage,'event deadline',key,value,inbox))
    def command(value):
        issued=time.monotonic();proc.stdin.write((value+'\n').encode());event('ack',value);return issued
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(predicate,seconds=3):
        end=time.monotonic()+seconds
        while True:
            pump();answer=predicate()
            if answer:return answer
            assert time.monotonic()<end,stage+' observation deadline'
            time.sleep(.005)
    def objects():
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];out=[]
        for n in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(n)
            if app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            obj,depth=pending.pop()
            # GTK may destroy a child between child-count and indexed retrieval.
            # Required controls and their live values must still be observed below.
            if obj is None:continue
            obj.clear_cache();out.append(obj);assert len(out)<=512 and depth<=20
            for n in range(obj.get_child_count()):pending.append((obj.get_child_at_index(n),depth+1))
        return out
    def find(id):return next((o for o in objects() if o.get_description()==id),None)
    def text(o):
        o.clear_cache();interface=o.get_text_iface();return Atspi.Text.get_text(interface,0,-1) if interface else o.get_name() or ''
    def state(o,s):o.clear_cache();return o.get_state_set().contains(s)
    def status():return text(find('settings.status'))
    def control(id):return find('settings.value.'+id)
    def value(row):
        obj=control(row['id']);return state(obj,Atspi.StateType.CHECKED) if isinstance(row['initial'],bool) else text(obj)
    def set_value(row,v):
        obj=control(row['id'])
        if isinstance(v,bool):
            if state(obj,Atspi.StateType.CHECKED)!=v:assert obj.get_action_iface().do_action(0)
        else:assert Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(v))
        wait(lambda:value(row)==v if isinstance(v,bool) else value(row)==str(v))
    def click(id):
        obj=find('settings.'+id);assert obj and state(obj,Atspi.StateType.SENSITIVE),(id,status())
        assert obj.get_component_iface().grab_focus();keys.press(0x20)
    def check_values(edited=False):
        for row in EXPECTED['settings']:
            v=row['edit'] if edited else row['initial'];assert value(row)==(v if isinstance(v,bool) else str(v)),(row['id'],value(row),v)
    def expected_documents(revision,edited=False):
        if not resource:return documents(revision,edited)
        value=copy.deepcopy(CONTENT_FIXTURE['authored'])
        for n in value:value[n]['revision']=revision
        if edited:
            for setting in EXPECTED['settings']:
                group,key=setting['id'].split('.');value['settings'][group][key]=setting['edit']
        return value
    def note(name):
        item=dict(case=name,status=status(),documents=stored(directory))
        if resource:item['resources']=resource_index(directory)[1]
        report['observations'].append(item)
    def capture():
        raw=keys.capture(0,0,800,600)
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data))
        pixels=b''.join(b'\0'+raw[n*2400:(n+1)*2400] for n in range(600))
        (folder/'initial.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',800,600,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
    try:
        launch(mode);wait(lambda:find('settings.status'))
        for row in EXPECTED['settings']:
            obj=control(row['id']);assert obj and obj.get_name()==row['label'];assert obj.get_role() in (Atspi.Role.TEXT,Atspi.Role.CHECK_BOX)
        capture();stage='CONTROLS'
        if resource:check_resources(directory)
        if behavior=='locked':
            locked=EXPECTED['locked'];obj=control(locked['id']);assert text(obj)==str(locked['effective']) and not state(obj,Atspi.StateType.SENSITIVE)
            detail=text(find('settings.detail.'+locked['id']));assert 'Locked by policy' in detail and 'Requested: 4' in detail and 'Effective: 2' in detail
        else:check_values()
        row=EXPECTED['settings'][0];set_value(row,1500)
        if resource and behavior in ('theme','invalid'):
            theme=next(r for r in EXPECTED['settings'] if r['id']=='display.theme_id')
            if behavior=='invalid':
                stage='INVALID-THEME';set_value(theme,CONTENT_CASES['invalid_theme']);wait(lambda:'Correct invalid fields' in status())
                assert not state(find('settings.apply'),Atspi.StateType.SENSITIVE) and stored(directory)==expected_documents('40');check_resources(directory)
            set_value(theme,CONTENT_CASES['selected_theme'])
        if behavior=='save':
            stage='INVALID';set_value(row,99);wait(lambda:'Correct invalid fields' in status());assert not state(find('settings.apply'),Atspi.StateType.SENSITIVE);set_value(row,1500)
            stage='CLIPBOARD';obj=control(row['id']);assert obj.get_component_iface().grab_focus();keys.press(ord('a'),True);keys.press(ord('c'),True);pump()
            Atspi.EditableText.copy_text(obj.get_editable_text_iface(),0,4);pump()
            assert Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).wait_for_text() is None,'PRIMARY exported settings'
            assert Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text() is None,'CLIPBOARD exported settings'
            assert text(obj)=='1500';note('CLIPBOARD')
            stage='DEFAULT';click('default.'+row['id']);wait(lambda:value(row)=='1000');set_value(row,1500);click('revert');wait(lambda:value(row)=='1000');assert stored(directory)==expected_documents('40')
            stage='SEARCH';search=find('settings.search');assert Atspi.EditableText.set_text_contents(search.get_editable_text_iface(),'Resource sampling interval');wait(lambda:state(control(row['id']),Atspi.StateType.SHOWING));assert not state(control('display.enabled'),Atspi.StateType.SHOWING)
            assert Atspi.EditableText.set_text_contents(search.get_editable_text_iface(),'display.enabled');wait(lambda:state(control('display.enabled'),Atspi.StateType.SHOWING));assert Atspi.EditableText.set_text_contents(search.get_editable_text_iface(),'')
            for field in EXPECTED['settings']:set_value(field,field['edit'])
            stage='PREVIEW';click('preview');event('event','held');assert stored(directory)==expected_documents('40') and 'Request pending' in status();command('release');assert event('event','result')['result']['outcome']=='preview';wait(lambda:'Preview validated' in status());check_values(True)
        stage='SUBMIT';click('apply')
        submitted=event('event','submitted')
        # Save's preview submission was observed earlier through its held/result events.
        if behavior=='save':submitted=event('event','submitted')
        if resource:
            assert submitted['body']['schema_version']=='0.3.0'
            assert submitted['body']['content']==CONTENT_FIXTURE['alternate_selection' if behavior=='wrong-selection' else 'selection']
        if behavior=='conflict':
            assert event('event','result')['result']['outcome']=='conflict';wait(lambda:'Configuration changed' in status());assert stored(directory)==expected_documents('41');click('reload');event('event','reloaded');check_values();assert 'Revision 41' in status();note('CONFLICT')
        else:
            event('event','held');stage='PENDING';assert ('Outcome unknown' if behavior=='callback' else 'Request pending') in status() and not state(find('settings.apply'),Atspi.StateType.SENSITIVE)
            assert stored(directory)==expected_documents('40');assert not any('Saved durably' in text(o) for o in objects()),'premature saved claim'
            if resource:check_resources(directory)
            if behavior=='cancel':click('cancel');event('event','cancel-requested')
            if behavior=='deny':command('deny')
            if behavior in ('revoke','retain'):
                held=[control(r['id']) for r in EXPECTED['settings'] if not isinstance(r['initial'],bool)];stage='REVOKE';issued=command('revoke')
                def erased():return all(text(o)=='' for o in held) and not any('Retained settings canary' in text(o) for o in objects())
                wait(erased,max(.001,issued+EXPECTED['revocation_ms']/1000-time.monotonic()));assert time.monotonic()-issued<=EXPECTED['revocation_ms']/1000
                note('REVOKE')
            command('release');result=event('event','result')['result'];stage='RESULT'
            if behavior in ('cancel','deny','revoke'):
                assert stored(directory)==expected_documents('40')
                if behavior=='deny':
                    assert result['outcome']=='unknown' and result['error']['code']=='policy.denied' and result['activation']==[]
                    assert all(result[k] is None for k in ('revision','stored','durable','visible'))
                    wait(lambda:'Outcome unknown' in status());assert not state(find('settings.reload'),Atspi.StateType.SENSITIVE)
                    command('regrant');assert 'Outcome unknown' in status();command('retrieve');result=event('event','retrieved')['result']
                assert result['outcome']==('cancelled' if behavior=='cancel' else 'conflict')
                assert result['error']['code']==('request.cancelled' if behavior=='cancel' else 'policy.changed')
                assert result['revision']=='40' and all(result[k] is False for k in ('stored','durable','visible')) and result['activation']==[]
                assert stored(directory)==expected_documents('40')
                if resource:check_resources(directory)
                if behavior=='cancel':wait(lambda:'Request cancelled' in status());click('revert');wait(lambda:value(row)=='1000')
                if behavior=='deny':wait(lambda:'Configuration changed' in status());click('reload');event('event','reloaded');check_values();note('DENY-RETRIEVED')
                if behavior=='revoke':
                    assert all(text(o)=='' for o in held);command('regrant');assert all(text(o)=='' for o in held);click('reload');event('event','reloaded');check_values()
            else:
                assert result['outcome']=='accepted' and result['revision']=='41' and result['stored'] is True and result['durable'] is True and result['visible'] is False
                wanted=expected_documents('41',behavior=='save')
                if behavior!='save':wanted['settings']['sampling']['resources_ms']=1500
                if resource and behavior in ('theme','invalid'):wanted['settings']['display']['theme_id']=CONTENT_CASES['selected_theme']
                assert stored(directory)==wanted
                if resource:stage='RESOURCE';check_resources(directory,wanted['settings']['display']['theme_id'])
                if behavior in ('unknown','restart','callback'):
                    wait(lambda:'Outcome unknown' in status());assert not state(find('settings.apply'),Atspi.StateType.SENSITIVE);before=(directory/'current.json').read_bytes()
                    command('restart' if behavior=='restart' else 'retrieve');assert (directory/'current.json').read_bytes()==before
                wait(lambda:'Saved durably' in status() and 'activation pending' in status() and 'Visibility has not been confirmed' in status());note('DURABLE')
                if behavior=='save':
                    command('quit');assert proc.wait(timeout=5)==0;keys.close();keys=None;launch('reopen');wait(lambda:find('settings.status'));check_values(True);assert stored(directory)==wanted;note('REOPEN')
        stage='CLOSE';held=control(row['id']);command('close');wait(lambda:text(held)=='');command('quit');assert proc.wait(timeout=5)==0
        assert behavior not in ('retain','false-saved','wrong-selection'),'deliberate fault escaped observer';report['outcome']='pass'
    except AssertionError as exc:
        report.update(error=str(exc),stage=stage)
        retained=behavior=='retain' and stage=='REVOKE' and str(exc)=='REVOKE observation deadline' and all(text(o)=='' for o in held) and any('Retained settings canary' in text(o) for o in objects())
        premature=behavior=='false-saved' and stage=='PENDING' and str(exc)=='premature saved claim' and stored(directory)==expected_documents('40') and 'Request pending' in status()
        wrong=resource and behavior=='wrong-selection' and stage=='RESOURCE' and str(exc)=='resource selection differs' and resource_index(directory)[1]['selection']==CONTENT_FIXTURE['alternate_selection'] and stored(directory)==wanted
        if retained or premature or wrong:report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:
        if proc and proc.poll() is None:proc.kill();proc.wait(timeout=5)
        if keys:keys.close()
        err.close();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4]);return
    exe,evidence=map(Path,sys.argv[1:3]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('settings-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='SETTINGS-FORM',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in ('save','cancel','conflict','deny','revoke','unknown','callback','restart','locked','retain','false-saved',*CONTENT_CASES['native_modes']):
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:stdout,stderr=child.communicate(timeout=45)
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
