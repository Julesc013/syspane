"""Independent native layout input, active-variant pixels and persistent scenes."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
CASES=json.loads((ROOT/'tests/editor/layout-authoring-cases.json').read_text())
class LayoutHarness(Harness):
    def __init__(self,*args):super().__init__(*args,layout=True)
    def find(self,id):
        if id not in self.controls:
            for obj in self.objects():
                description=obj.get_description() or ''
                if description.startswith('editor.'):self.controls[description[7:]]=obj
            assert len(self.controls)<=128
        return self.controls.get(id)
    def click(self,id):
        obj=self.find(id);assert self.sensitive(id) and self.state(obj,self.Atspi.StateType.SHOWING)
        rect=self.extents(obj);assert rect.x>=0 and rect.y>=0 and rect.width>0 and rect.height>0
        self.input.click(rect.x+rect.width//2,rect.y+rect.height//2)

def value(h,id):return h.text(h.find('layout.'+id))
def field(h,id,text):
    obj=h.find('layout.'+id);h.wait(lambda:h.state(obj,h.Atspi.StateType.SENSITIVE))
    assert h.Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(text));h.wait(lambda:value(h,id)==str(text))
def selected(h,id):return h.observer.selected_text(h.find('layout.'+id))
def choose(h,id,index,expected):
    obj=h.find('layout.'+id);h.wait(lambda:h.state(obj,h.Atspi.StateType.SHOWING) and h.state(obj,h.Atspi.StateType.SENSITIVE))
    # Changing layout kind resizes/repositions the modal window. Activate the
    # native combo itself, without interpreting a pre-allocation rectangle.
    assert h.Atspi.Action.do_action(obj.get_action_iface(),0)
    h.wait(lambda:any(o.get_role()==h.Atspi.Role.MENU_ITEM and h.state(o,h.Atspi.StateType.SHOWING) and h.text(o)==expected for o in h.objects()))
    h.input.press(0xff50)
    for _ in range(index):h.input.press(0xff54)
    h.input.press(0xff0d);h.wait(lambda:selected(h,id)==expected)
def tab(h,title):
    matches=[o for o in h.objects() if o.get_role()==h.Atspi.Role.PAGE_TAB and h.text(o)==title];assert len(matches)==1
    rect=h.extents(matches[0]);h.input.click(rect.x+rect.width//2,rect.y+rect.height//2);h.wait(lambda:h.state(matches[0],h.Atspi.StateType.SELECTED))
def select(h,index):
    # Focusing an unselected GTK tree can place its cursor on row zero. Home is
    # then a no-op; first move to End so Home performs a real selection change.
    h.focus('objects');h.input.press(0xff57);h.input.press(0xff50)
    for _ in range(index):h.input.press(0xff54)
    title=CASES['authored']['scene']['widgets'][index]['title']
    try:h.wait(lambda:h.value('title')==title)
    except Exception:
        h.report['selection_failure']=dict(index=index,title=h.value('title'),status=h.status(),focus=h.focus_snapshot('objects'),rows=list(h.find('objects').get_table_iface().get_selected_rows()))
        h.screenshot('selection-failure');raise
def open_layout(h):h.click('layout');h.wait(lambda:h.find('layout.set') is not None and h.state(h.find('layout.set'),h.Atspi.StateType.SHOWING) and h.sensitive('layout.set') and not h.sensitive('layout') and not h.sensitive('apply'))
def set_layout(h):h.click('layout.set');h.wait(lambda:h.sensitive('layout'));h.input.focus(h.pid)
def kind(h,k,group=False):choose(h,'kind',(['fixed','canvas','stack','grid'] if group else ['fixed','flow']).index(k),k)
def fixed(h):
    for key,v in dict(x=70,y=60,width=210,height=90).items():field(h,key,v)
def breakpoint_input(h):
    h.click('layout.add');h.wait(lambda:selected(h,'variant')=='Breakpoint 1');field(h,'threshold',400)
    for key,v in dict(x=80,y=60,width=220,height=90).items():field(h,key,v)
    h.click('layout.add');h.wait(lambda:selected(h,'variant')=='Breakpoint 2');field(h,'threshold',800);kind(h,'flow');choose(h,'anchor',2,'end')
def body(h,x,y,height=60):return h.pixels(x+4,y+4,160,height)

def exercise(h):
    mode=h.mode;h.launch();h.check();select(h,0);h.wait(lambda:h.number('x')==20);baseline=body(h,40,40);second=body(h,270,40);assert len(set(baseline))>2;h.screenshot('initial')
    h.report['baseline_pixel_sha256']=__import__('hashlib').sha256(baseline).hexdigest()
    if mode=='frozen-preview':h.command('freeze-preview')
    h.stage='BUFFER';open_layout(h)
    if mode=='cancel-buffer':
        field(h,'x','invalid private');held=h.find('layout.x');h.click('layout.cancel');h.wait(lambda:h.erased(held) and h.sensitive('layout'));assert not h.sensitive('apply');h.check();h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode in ('revoke','retain-layout'):
        tab(h,'Assignment');field(h,'display_value','Private layout role');held=[h.find('layout.display_value')];tab(h,'Geometry');field(h,'x',12345);held.append(h.find('layout.x'));h.click('layout.add');h.wait(lambda:selected(h,'variant')=='Breakpoint 1');field(h,'threshold',400);held.append(h.find('layout.threshold'));kind(h,'flow');field(h,'width_min',123);held.append(h.find('layout.width_min'))
        issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:all(h.erased(o) for o in held) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-time.monotonic()));h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms'];h.report['production_erased']=True
        h.stage='RETAINED';assert not any('Private layout role' in h.text(o) for o in h.objects()),'retained layout disclosed';h.check();h.command('regrant');assert not h.sensitive('layout') and all(h.erased(o) for o in held);h.click('reload');h.event('event','reloaded');select(h,0);open_layout(h);tab(h,'Assignment');assert value(h,'display_value')=='D1';h.click('layout.cancel');h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode=='topology':
        field(h,'x',123);held=h.find('layout.x');h.command('layout-narrow');h.wait(lambda:h.erased(held) and h.sensitive('layout'));assert not h.sensitive('apply');h.check()
        # The original root and second child exceed a 399-DIP display; clipped
        # leaves require the surface alternative. Temporarily fit both through
        # native controls and restore their frozen geometry before saving.
        select(h,1);open_layout(h);field(h,'x',150);set_layout(h)
        select(h,3);open_layout(h);field(h,'width',360);set_layout(h);select(h,0);open_layout(h)
    key='fixed';expected=CASES['expected'][key];location=(90,80);sample=baseline;sample_height=60
    if mode in ('breakpoints','variant-drag','variant-keyboard','variant-resize','variant-align','topology'):
        breakpoint_input(h);key='breakpoints';set_layout(h);h.wait(lambda:h.number('x')==(20 if mode=='topology' else 80))
        if mode=='topology':
            h.field('x',123);h.command('layout-wide');assert h.value('x')=='123';h.click('properties');h.wait(lambda:'Layout changed' in h.status());h.click('revert-fields');h.wait(lambda:h.number('x')==80)
            select(h,3);open_layout(h);field(h,'width',460);set_layout(h)
            select(h,1);open_layout(h);field(h,'x',250);set_layout(h);select(h,0);h.wait(lambda:h.number('x')==80)
        h.wait(lambda:'Active layout: Breakpoint 1' in h.status());location=(100,80)
        if mode=='variant-drag':h.drag(110,90,30,20);key='variant-move';location=(130,100);h.wait(lambda:h.number('x')==110 and h.number('y')==80)
        elif mode=='variant-keyboard':
            h.focus('canvas')
            for _ in range(3):h.input.press(0xff53,shift=True)
            for _ in range(2):h.input.press(0xff54,shift=True)
            key='variant-move';location=(130,100);h.wait(lambda:h.number('x')==110 and h.number('y')==80)
        elif mode=='variant-resize':h.drag(317,167,20,10);key='variant-resize';h.wait(lambda:h.number('width')==240 and h.number('height')==100)
        elif mode=='variant-align':
            h.point(110,90);h.point(280,50,True);h.wait(lambda:h.value('title')=='');h.click('align-left');select(h,1);h.wait(lambda:h.number('x')==80);key='variant-align';location=(100,40)
            # These fixed expected boxes overlap below y=80. Compare the second
            # caption above that overlap, not transparent pixels over the first.
            sample_height=28;sample=second[:160*sample_height*3]
    elif mode in ('canvas','stack-horizontal','stack-vertical','grid'):
        h.click('layout.cancel');h.wait(lambda:h.sensitive('layout'));h.input.focus(h.pid)
        if mode!='canvas':
            for index in (0,1):select(h,index);open_layout(h);kind(h,'flow');choose(h,'anchor',3,'stretch') if mode=='grid' else None;set_layout(h)
        select(h,3);open_layout(h);kind(h,'canvas' if mode=='canvas' else 'grid' if mode=='grid' else 'stack',True)
        if mode=='canvas':field(h,'width',460);field(h,'height',260)
        else:
            field(h,'gap_dip',20)
            if mode=='stack-horizontal':choose(h,'axis',0,'horizontal')
            if mode=='stack-vertical':choose(h,'overflow',0,'scroll')
        set_layout(h);select(h,0);key=mode;location=(20,20) if mode=='canvas' else (0,0)
    elif mode=='flow':kind(h,'flow');set_layout(h);key='flow-start';location=(20,20);assert not h.sensitive('value.x')
    elif mode in ('order-priority','display'):
        tab(h,'Assignment')
        if mode=='display':choose(h,'display_kind',1,'role');field(h,'display_value','work')
        else:choose(h,'priority',0,'essential');field(h,'sibling',1)
        set_layout(h);key=mode;location=(40,40)
    else:
        if mode=='invalid':
            field(h,'width','NaN');h.click('layout.set');h.wait(lambda:bool(value(h,'error')));assert value(h,'width')=='NaN' and not h.sensitive('apply');h.check()
        fixed(h)
        set_layout(h);h.wait(lambda:h.number('x')==70 and h.number('width')==210)
    expected=CASES['expected'][key];h.report['expected_key']=key;h.stage='PIXELS';h.wait(lambda:body(h,*location,sample_height)==sample);h.check();h.screenshot('draft')
    # One Set layout is one history entry; direct gestures append exactly one.
    h.click('undo');h.wait(lambda:h.sensitive('redo'));h.click('redo');h.wait(lambda:h.sensitive('apply'));h.wait(lambda:body(h,*location,sample_height)==sample)
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');h.check()
    if mode!='wrong-layout':assert submitted['body']['operations'][0]['scene']==expected
    h.command('release');result=h.event('event','result')['result'];assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] is True and result['visible'] is False
    h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');select(h,1 if mode=='variant-align' else 0);h.wait(lambda:body(h,*location,sample_height)==sample)
    h.command('quit');assert h.proc.wait(timeout=5)==0;assert mode not in ('wrong-layout','retain-layout','frozen-preview');h.report['outcome']='pass'

def observe(exe,exit_exe,folder,mode):
    h=LayoutHarness(exe,exit_exe,folder,mode);h.report['oracle_sha256']=sha(Path(__file__));h.report['harness_sha256']=sha(ROOT/'tests/editor/native_editor.py')
    try:exercise(h)
    except AssertionError as error:
        h.report.update(stage=h.stage,error=str(error))
        h.screenshot('failure')
        wrong=mode=='wrong-layout' and h.stage=='STORE' and str(error)=='stored documents differ' and stored(h.directory)['scene']['widgets'][0]['layout']['base']['x']==71
        retained=mode=='retain-layout' and h.stage=='RETAINED' and str(error)=='retained layout disclosed' and h.report.get('production_erased') and any('Private layout role' in h.text(o) for o in h.objects()) and stored(h.directory)==h.documents()
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(error)=='PIXELS observation deadline' and h.number('x')==70 and stored(h.directory)==h.documents() and __import__('hashlib').sha256(body(h,40,40)).hexdigest()==h.report.get('baseline_pixel_sha256') and body(h,40,40)!=body(h,90,80)
        if wrong or retained or frozen:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('layout-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-LAYOUT',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/layout-authoring-cases.json'),executable_sha256=sha(exe),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err);detail=json.loads((folder/mode/'result.json').read_text());report['cases'].append(dict(case=mode,outcome=detail['outcome'],fault_detected=detail.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
            assert child.returncode==0 and detail['outcome']=='pass',(mode,err.decode(errors='replace'))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
