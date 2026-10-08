"""Independent AT-SPI and real-key acceptance in an owned Xvfb/private D-Bus session."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes as C
import hashlib,json,os,select,signal,struct,subprocess,sys,time,uuid,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/fault'),str(ROOT/'tests/desktop'),str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from native_oracle import Display
from check_surface_runtime import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED=json.loads((ROOT/'tests/scene/inspector-cases.json').read_text())

class Keys(Display):
    def __init__(self,pid):
        super().__init__();p,w=C.c_void_p,C.c_ulong
        self.x.XQueryTree.argtypes=[p,w,C.POINTER(w),C.POINTER(w),C.POINTER(C.POINTER(w)),C.POINTER(C.c_uint)]
        self.x.XSetInputFocus.argtypes=[p,w,C.c_int,w]
        self.x.XGetInputFocus.argtypes=[p,C.POINTER(w),C.POINTER(C.c_int)]
        self.x.XGetGeometry.argtypes=[p,w,C.POINTER(w),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
        self.x.XKeysymToKeycode.argtypes=[p,w];self.x.XKeysymToKeycode.restype=C.c_ubyte
        self.xt=C.CDLL('libXtst.so.6');self.xt.XTestFakeKeyEvent.argtypes=[p,C.c_uint,C.c_int,w]
        root,parent,children,count=w(),w(),C.POINTER(w)(),C.c_uint()
        assert self.x.XQueryTree(self.handle,self.root,C.byref(root),C.byref(parent),C.byref(children),C.byref(count))
        found=[]
        try:
            for n in range(count.value):
                win=children[n]
                if self.property(win,'_NET_WM_PID')!=[pid]:continue
                name=C.c_void_p()
                if self.x.XFetchName(self.handle,win,C.byref(name)):
                    try:
                        if C.string_at(name)==b'SysPane Scene Inspector':
                            root,x,y,width,height,border,depth=w(),C.c_int(),C.c_int(),C.c_uint(),C.c_uint(),C.c_uint(),C.c_uint()
                            assert self.x.XGetGeometry(self.handle,win,C.byref(root),C.byref(x),C.byref(y),C.byref(width),C.byref(height),C.byref(border),C.byref(depth))
                            if width.value>=100 and height.value>=100:found.append(win)
                    finally:self.x.XFree(name)
        finally:
            if children:self.x.XFree(children)
        assert len(found)==1,found
        self.window=found[0];self.x.XSetInputFocus(self.handle,self.window,1,0);self.x.XSync(self.handle,False)
    def press(self,symbol,shift=False):
        code=self.x.XKeysymToKeycode(self.handle,symbol);assert code
        modifier=self.x.XKeysymToKeycode(self.handle,0xffe1)
        if shift:assert modifier and self.xt.XTestFakeKeyEvent(self.handle,modifier,True,0)
        for down in (True,False):assert self.xt.XTestFakeKeyEvent(self.handle,code,down,0)
        if shift:assert self.xt.XTestFakeKeyEvent(self.handle,modifier,False,0)
        self.x.XSync(self.handle,False)

def observe(exe,folder,mode):
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi,GLib
    Atspi.set_timeout(200,500);verify();folder.mkdir()
    report=dict(outcome='fail',mode=mode,observations=[],executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),
        fixture_sha256=sha(ROOT/'tests/scene/inspector-cases.json'),surface_runtime_sha256=sha(ROOT/'source/build/surface-runtime.json'),
        xtest_sha256=sha(Path('/usr/lib/x86_64-linux-gnu/libXtst.so.6')),worker_sha256=sha(exe.with_name('SysPane.ImageWorker')))
    err=(folder/'stderr').open('wb');proc=subprocess.Popen([str(exe),str(ROOT/'spec/fixtures/valid'),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
    keys=None;stage='startup';started=time.monotonic()
    def reply():
        assert select.select([proc.stdout],[],[],5)[0],'native reply deadline'
        line=proc.stdout.readline();assert line,'native exited before reply';return json.loads(line)
    def command(cmd):
        issued=time.monotonic();proc.stdin.write((cmd+'\n').encode());proc.stdin.flush();assert reply()=={'ack':cmd};return issued
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(predicate,seconds=3):
        end=time.monotonic()+seconds
        while True:
            pump();value=predicate()
            if value:return value
            assert time.monotonic()<end,stage+' observation deadline'
            time.sleep(.005)
    def objects():
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];out=[]
        for n in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(n)
            if app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            item,depth=pending.pop();item.clear_cache();out.append(item)
            assert len(out)<=512 and depth<=20,'accessibility traversal bound'
            for n in range(item.get_child_count()):pending.append((item.get_child_at_index(n),depth+1))
        return out
    def find(description):return next((x for x in objects() if x.get_description()==description),None)
    def text(item):
        item.clear_cache();interface=item.get_text_iface()
        return Atspi.Text.get_text(interface,0,-1) if interface else item.get_name()
    def matrix():
        tree.clear_cache();table=tree.get_table_iface();return [[text(table.get_accessible_at(r,c)) for c in range(table.get_n_columns())] for r in range(table.get_n_rows())]
    def selected():
        tree.clear_cache();table=tree.get_table_iface();rows=table.get_selected_rows();return [matrix()[n] for n in rows]
    def note(name):
        report['observations'].append(dict(case=name,rows=matrix(),selection=selected(),at_ms=(time.monotonic()-started)*1000))
        if not (folder/'initial.png').exists():
            raw=keys.capture(0,0,800,600)
            def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data))
            pixels=b''.join(b'\0'+raw[row*2400:(row+1)*2400] for row in range(600))
            (folder/'initial.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',800,600,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
    def summary():
        item=find('syspane.scene.requested-summary');return text(item) if item else ''
    try:
        assert reply()=={'ready':True};tree=wait(lambda:find('syspane.scene.inspector'));assert tree.get_role()==Atspi.Role.TREE_TABLE,tree.get_role_name()
        keys=Keys(proc.pid);assert tree.get_component_iface().grab_focus()
        focus,revert=C.c_ulong(),C.c_int();keys.x.XGetInputFocus(keys.handle,C.byref(focus),C.byref(revert));report['native_focus']={'expected':keys.window,'actual':focus.value}
        assert focus.value==keys.window,'native input focus differs'
        table=tree.get_table_iface();assert table.get_n_columns()==2
        columns=EXPECTED['columns'] if mode!='translated' else [EXPECTED['translation']['inspector.item'],EXPECTED['translation']['inspector.information']]
        assert [table.get_column_description(c) for c in range(2)]==columns
        if mode=='image':
            stage='IMAGE';wait(lambda:matrix()==[[EXPECTED['image']['item'],EXPECTED['image']['information']]])
        elif mode=='chart':
            stage='CHART';rows=wait(lambda:matrix() if len(matrix())==4 else None)
            for row,point in zip(rows[1:],EXPECTED['chart']['points']):assert row==['Point '+point['time']+' ns',point['value']+' byte; generation '+point['generation']+'; '+point['segment']]
        elif mode=='scalar':
            stage='TREE';rows=wait(lambda:matrix() if len(matrix())==1 else None);assert rows[0][0]==EXPECTED['scalar']['item']
            assert all(value in rows[0][1] for value in EXPECTED['scalar']['contains'])
        else:
            stage='TABLE';rows=wait(lambda:matrix() if len(matrix())==7 else None);expected=EXPECTED['table'];assert rows[0]==[expected['item'],expected['summary']]
            assert [rows[n][0] for n in (1,4)]==expected['entities']
            assert [rows[n][0] for n in (2,3,5,6)]==expected['columns']*2
            assert all(value in rows[n][1] for n,value in zip((2,3,5,6),expected['values']))
            note('TABLE');stage='KEYBOARD';keys.press(0xff50);wait(lambda:len(selected())==1 and selected()[0][0]==expected['item'])
            keys.press(0xff51,True);wait(lambda:table.get_n_rows()==1);keys.press(0xff53,True);wait(lambda:table.get_n_rows()==7)
            keys.press(0xff54);keys.press(0xff54);wait(lambda:selected() and '123 byte' in selected()[0][1]);note('KEYBOARD')
            stage='SUMMARY'
            for _ in range(5):
                keys.press(0xff09);pump();time.sleep(.01)
                focused=[o for o in objects() if o.get_role()==Atspi.Role.PUSH_BUTTON and o.get_state_set().contains(Atspi.StateType.FOCUSED)]
                if focused:break
            assert focused,'Summary keyboard focus';keys.press(0x20);wait(lambda:'123 byte' in summary());old_summary=summary()
            command('update');wait(lambda:any('987 byte' in r[1] for r in matrix()));assert summary()==old_summary,'summary changed without request'
            assert tree.get_component_iface().grab_focus();stage='IDENTITY';command('insert');wait(lambda:table.get_n_rows()==10)
            assert selected() and '987 byte' in selected()[0][1],'selected entity changed after insertion';note('IDENTITY')
            command('remove');wait(lambda:table.get_n_rows()==4);assert selected() and selected()[0][0]==expected['item'],'removed selection did not fall back to ancestor'
            assert summary()=='';note('REMOVAL')
        note(stage);old_cells=[tree.get_table_iface().get_accessible_at(n,1) for n in range(tree.get_table_iface().get_n_rows())]
        stage='REVOKE';issued=command('revoke');deadline=issued+EXPECTED['revocation_ms']/1000
        def erased():
            if tree.get_table_iface().get_n_rows()!=0 or summary():return False
            if any('Retained canary' in (o.get_name() or '') for o in objects()):return False
            for cell in old_cells:
                try:
                    if text(cell) or cell.get_name():return False
                except GLib.Error as e:
                    if not any(s in str(e).lower() for s in ('unknownobject','does not exist','defunct','no longer exists')):raise
            return True
        wait(erased,max(.001,deadline-time.monotonic()));assert time.monotonic()<=deadline,'revocation exceeded bound';note('OLD-REFERENCE')
        stage='REGRANT';command('regrant');assert not any('987 byte' in row[1] for row in matrix())
        if mode not in ('image','chart'):
            command('fresh');wait(lambda:any('456 byte' in row[1] for row in matrix()))
        stage='CLOSE';command('close');wait(lambda:tree.get_table_iface().get_n_rows()==0 and summary()=='');note('CLOSE');command('quit');assert proc.wait(timeout=5)==0
        assert mode not in ('retain','wrong-selection'),'deliberate fault escaped observer';report['outcome']='pass'
    except AssertionError as exc:
        report.update(error=str(exc),stage=stage)
        if 'tree' in locals() and proc.poll() is None:report['last_rows']=matrix();report['last_selection']=selected()
        retained=mode=='retain' and stage=='REVOKE' and str(exc)=='REVOKE observation deadline' and not matrix() and any('Retained canary' in (o.get_name() or '') for o in objects())
        displaced=mode=='wrong-selection' and stage=='IDENTITY' and str(exc)=='selected entity changed after insertion' and any(EXPECTED['wrong_selection_value'] in row[1] for row in selected())
        if retained or displaced:report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        if keys:keys.close()
        err.close();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4]);return
    exe,evidence=map(Path,sys.argv[1:3]);folder=evidence/('inspector-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
    report=dict(family='SCENE-INSPECTOR',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in ('scalar','table','chart','image','translated','retain','wrong-selection'):
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:stdout,stderr=child.communicate(timeout=30)
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
