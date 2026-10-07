"""Independent native content buffers, telemetry/pixels, storage and erasure oracle."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb,check_resources
CASES=json.loads((ROOT/'tests/editor/content-properties-cases.json').read_text())
RESOURCES=json.loads((ROOT/'tests/editor/content-properties-fixture.json').read_text())
class ContentHarness(Harness):
    def point(self,x,y,shift=False):return super().point(int(x*3/4),int(y*3/4),shift)
    def pixels(self,x,y,w,h):return super().pixels(int(x*3/4),int(y*3/4),max(1,int(w*3/4)),max(1,int(h*3/4)))
    def cleared_canvas(self):return set(super().pixels(0,0,500,420))=={0}
    def erased(self,obj):
        try:return super().erased(obj)
        except self.GLib.GError as error:
            # A removed GTK menu item can lose its application association. Require
            # its defunct state AND a live, accessible owner; disconnection is no pass.
            if error.domain!='atspi_error' or str(error)!='atspi_error: The application no longer exists (0)':raise
            assert self.proc.poll() is None and obj.get_state_set().contains(self.Atspi.StateType.DEFUNCT)
            assert 'Editor unavailable' in self.status() and self.sensitive('reload')
            return True
    def check(self,scene=None,revision='40'):
        expected=self.documents(scene,revision);assert stored(self.directory)==expected,'stored documents differ'
        check_resources(self.directory,expected['scene']['theme_id'] or expected['settings']['display']['theme_id'],fixture=RESOURCES)

def value(h,id):return h.text(h.find('content.'+id))
def field(h,id,text):
    obj=h.find('content.'+id);assert h.sensitive('content.'+id)
    assert h.Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(text));h.wait(lambda:value(h,id)==str(text))
def selected(h,id):
    obj=h.find('content.'+id);obj.clear_cache();selection=obj.get_selection_iface()
    try:
        if selection and selection.get_n_selected_children():return h.text(selection.get_selected_child(0))
    except h.GLib.GError as error:
        if error.domain!='atspi_error' or 'does not exist' not in str(error):raise
    return ''
def choose(h,id,index,expected):
    obj=h.find('content.'+id);rect=obj.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN);h.input.click(rect.x+rect.width-12,rect.y+rect.height//2)
    def option():
        matches=[o for o in h.objects() if o.get_role()==h.Atspi.Role.MENU_ITEM and o.get_state_set().contains(h.Atspi.StateType.SHOWING) and h.text(o)==expected]
        bounds=[o.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN) for o in matches]
        # GTK exports its popup through both the combo and application hierarchy.
        positions={(b.x,b.y,b.width,b.height) for b in bounds if b.x>=0 and b.width>0}
        assert len(positions)<=1
        return next(iter(positions)) if positions else None
    x,y,width,height=h.wait(option);h.input.click(x+width//2,y+height//2)
    h.wait(lambda:selected(h,id)==expected)
def opened(h):return h.find('content.set') is not None and h.sensitive('content.set') and not h.sensitive('content')
def open_content(h):h.click('content');h.wait(lambda:opened(h))
def set_content(h):h.click('content.set');h.wait(lambda:h.sensitive('content'));h.input.focus(h.pid)
def canvas(h):return h.text(h.find('canvas'))
def region(h,kind):
    x,y,w,ht={'table':(25,95,450,75),'chart':(25,200,280,110),'image':(365,260,80,40),'theme':(25,25,100,35)}[kind]
    return h.pixels(x,y,w,ht)
def select_widget(h,kind):
    if kind=='theme':h.point(490,405);h.wait(lambda:h.value('title')=='');return
    x,y={'table':(30,100),'chart':(30,205),'image':(365,240)}[kind];h.point(x,y);h.wait(lambda:h.value('title')==kind.capitalize())
def populate(h,kind,mode):
    if kind=='table':
        field(h,'label','Received\nbytes');choose(h,'column',1,'network.transmit_bytes');field(h,'label','Sent bytes')
        choose(h,'column',0,'network.receive_bytes');assert value(h,'label')=='Received\nbytes'
        if mode=='order':h.click('content.down');h.wait(lambda:selected(h,'column')=='network.receive_bytes' and not h.sensitive('content.down'))
    elif kind=='chart':
        field(h,'window_ms','1000' if mode=='chart-auto' else '2000');field(h,'max_points','2' if mode=='chart-auto' else '32')
        if mode=='chart-auto':
            choose(h,'axis',1,'fixed');field(h,'minimum','invalid inactive');field(h,'maximum','invalid inactive');choose(h,'axis',0,'auto');choose(h,'include_zero',1,'false')
        else:
            choose(h,'interpolation',1,'step');choose(h,'axis',1,'fixed');field(h,'minimum','-5.5');field(h,'maximum','1e2')
    elif kind=='image':
        choose(h,'asset',1,'package:properties-native / 0.1.0 / images/b-gray.png');field(h,'alt','Gray replacement');field(h,'width_dip','9.6e1');field(h,'height_dip','80');choose(h,'fit',2,'stretch')
    else:choose(h,'theme',1,'Content contrast (theme:contrast)')
def preview(h,kind,mode,baseline=None):
    label=canvas(h)
    if kind=='table':
        a='Received\nbytes [network.receive_bytes]: 80 byte';b='Sent bytes [network.transmit_bytes]: 0 byte'
        if a not in label or b not in label:return False
        if (label.index(a)<label.index(b))!=(mode!='order'):return False
    elif kind=='chart':
        if ('Window 1000 ms | linear' if mode=='chart-auto' else 'Window 2000 ms | step') not in label:return False
        if mode!='chart-auto' and 'Range -5.5 .. 100.0 byte' not in label:return False
        if 'Point 2000000000: 80' not in label:return False
    elif kind=='image':
        if 'Gray replacement\nImage ready' not in label:return False
        # Bilinear stretch clamps the outer source-pixel centres to black/gray 137.
        if h.pixels(441,270,1,1)!=b'\x89\x89\x89' or h.pixels(365,270,1,1)!=b'\0\0\0':return False
    elif kind=='theme':
        raw=region(h,'theme')
        colors=list(zip(raw[0::3],raw[1::3],raw[2::3]))
        # Grayscale glyph coverage over black must preserve equal cyan channels.
        if not all(r==0 and g==b for r,g,b in colors) or not any(g>=128 for _,g,_ in colors):return False
    return baseline is None or region(h,kind)!=baseline

def exercise(h):
    h.launch();h.check();h.stage='SOURCE';h.wait(lambda:'Showing 1 of 1 rows' in canvas(h) and '80 byte' in canvas(h) and 'Initial color image\nImage ready' in canvas(h))
    mode=h.mode;kind='table' if mode in ('table','order') else 'chart' if mode in ('chart','chart-auto') else 'theme' if mode in ('theme','inherit') else 'image'
    select_widget(h,kind);baseline=region(h,kind);h.report['baseline_pixel_sha256']=hashlib.sha256(baseline).hexdigest();h.report['initial_accessible']=canvas(h)
    if mode=='frozen-preview':h.command('freeze-preview')
    h.stage='BUFFER';open_content(h);assert not h.sensitive('apply') and not h.sensitive('undo') and not h.sensitive('value.title');h.check()
    if mode in ('revoke','retain-content'):
        field(h,'alt','Private buffered alternative');held=[h.find('content.alt'),h.find('content.width_dip')]
        for obj in h.objects():
            if h.text(obj).startswith('package:properties-native /'):held.append(obj)
        issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:all(h.erased(obj) for obj in held) and h.cleared_canvas(),max(.001,issued+.2-time.monotonic()))
        h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=h.cases['erase_ms'];h.report['production_erased']=True
        h.stage='RETAINED';assert not any('Initial color image' in h.text(obj) or 'Private buffered alternative' in h.text(obj) for obj in h.objects()),'retained content disclosed'
        h.check();h.command('regrant');assert not h.sensitive('content') and all(h.erased(obj) for obj in held);h.input.focus(h.pid);h.click('reload');h.event('event','reloaded');h.wait(lambda:'Move me' in canvas(h));h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode=='invalid':
        field(h,'width_dip','NaN');choose(h,'theme',1,'Content contrast (theme:contrast)');h.click('content.set');h.wait(lambda:bool(value(h,'error')));assert opened(h) and value(h,'width_dip')=='NaN';h.check();choose(h,'theme',0,'Inherit settings')
    populate(h,kind,mode);h.check()
    if mode=='cancel-buffer':
        held=h.find('content.alt');h.click('content.cancel');h.wait(lambda:h.sensitive('content') and h.erased(held));h.input.focus(h.pid);assert not h.sensitive('undo') and not h.sensitive('apply');h.wait(lambda:region(h,kind)==baseline);h.check();open_content(h);assert value(h,'alt')=='Initial color image';populate(h,kind,mode)
    h.stage='SET';set_content(h)
    if mode=='inherit':
        h.wait(lambda:preview(h,'theme','theme',baseline));open_content(h);choose(h,'theme',0,'Inherit settings');set_content(h);h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:region(h,kind)==baseline);assert h.sensitive('undo');h.check();h.click('undo');h.wait(lambda:h.sensitive('apply'));h.click('redo');h.wait(lambda:not h.sensitive('apply'));h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    h.wait(lambda:h.sensitive('apply'));h.stage='PIXELS';h.wait(lambda:preview(h,kind,mode,baseline));h.screenshot('draft');h.report['edited_accessible']=canvas(h);h.report['edited_pixel_sha256']=hashlib.sha256(region(h,kind)).hexdigest()
    expected=h.cases['expected'][mode if mode in h.cases['expected'] else 'image']
    h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:'Window 60000 ms | linear' in canvas(h) if kind=='chart' else region(h,kind)==baseline);h.click('redo');h.wait(lambda:h.sensitive('apply'));h.wait(lambda:preview(h,kind,mode,baseline));h.check()
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');assert not h.sensitive('content');h.check()
    if mode!='wrong-content':assert submitted['body']['operations'][0]['scene']==expected
    if mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
    h.command('release');result=h.event('event','result')['result']
    if mode=='cancel':assert result['outcome']=='cancelled';h.check();h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());record=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==record
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.stage='REOPEN';h.wait(lambda:preview(h,kind,mode));h.command('quit');assert h.proc.wait(timeout=5)==0
    assert mode not in ('wrong-content','frozen-preview','retain-content');h.report['outcome']='pass'

def observe(exe,exit_exe,folder,mode):
    h=ContentHarness(exe,exit_exe,folder,mode,properties=True);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),display=dict(logical_dip=[640,560],scale=[3,4],pixels=[480,420]))
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.report['accessible']=canvas(h);h.screenshot('failure')
        wrong=mode=='wrong-content' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][3]['content']['alt']=='Wrong replacement'
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(exc)=='PIXELS observation deadline' and 'Gray replacement\nImage ready' in canvas(h) and stored(h.directory)==h.documents() and hashlib.sha256(region(h,'image')).hexdigest()==h.report['baseline_pixel_sha256']
        retained=mode=='retain-content' and h.stage=='RETAINED' and str(exc)=='retained content disclosed' and h.report.get('production_erased') and any(h.text(obj)=='Retained content canary Initial color image' for obj in h.objects())
        if wrong or frozen or retained:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('properties-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-CONTENT-PROPERTIES',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/content-properties-cases.json'),resources_sha256=sha(ROOT/'tests/editor/content-properties-fixture.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_modes']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
            assert not timed_out and child.returncode==0,(mode,stderr.decode(errors='replace'));case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass';report['cases'].append(dict(case=mode,outcome='pass',fault_detected=case.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
