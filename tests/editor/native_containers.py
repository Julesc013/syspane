"""Independent native rule-preserving container input, pixels and persistence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
from native_layout_authoring import LayoutHarness,field,kind,choose,selected,value
CASES=json.loads((ROOT/'tests/editor/container-cases.json').read_bytes())
PREVIEW=json.loads((ROOT/'tests/editor/container-preview-cases.json').read_bytes())
class ContainerHarness(LayoutHarness):
    def __init__(self,*args):Harness.__init__(self,*args,container=True)
def caption(h,position):return h.pixels(position[0]+4,position[1]+4,160,28)
def composite(bottom,top):
    # White text over the pinned #14345acc native theme, rendered onto black.
    # Recover unique alpha from each isolated premultiplied RGB sample, then use
    # ordinary source-over. No pixel from the result under test is an input.
    multiply=lambda a,b:(a*b+127)//255
    background=tuple(c*204//255 for c in (20,52,90));lookup={(0,0,0):{0}}
    for coverage in range(256):
        rgb=tuple(coverage+multiply(c,255-coverage) for c in background)
        lookup.setdefault(rgb,set()).add(coverage+multiply(204,255-coverage))
    result=bytearray();assert len(bottom)==len(top)
    for i in range(0,len(top),3):
        rgb=tuple(top[i:i+3]);alpha=lookup.get(rgb,set());assert len(alpha)==1,'unavailable or ambiguous caption alpha'
        result.extend(rgb[c]+multiply(bottom[i+c],255-next(iter(alpha))) for c in range(3))
    return bytes(result)
def open_form(h,action):
    h.click(action);h.wait(lambda:h.find('layout.set') is not None and h.state(h.find('layout.set'),h.Atspi.StateType.SHOWING) and not h.sensitive('apply') and not h.sensitive('wrap'))
def set_form(h):h.click('layout.set');h.wait(lambda:h.sensitive('wrap'))
def setup(h,key):
    if key in ('stack-horizontal','stack-vertical','responsive'):
        field(h,'gap_dip',8 if key=='responsive' else 20)
        if key=='stack-horizontal':choose(h,'axis',0,'horizontal')
        if key=='responsive':
            h.click('layout.add');h.wait(lambda:selected(h,'variant')=='Breakpoint 1');field(h,'threshold',400);field(h,'gap_dip',20);choose(h,'axis',0,'horizontal')
    else:
        kind(h,key,True)
        if key=='grid':field(h,'columns',2);field(h,'gap_dip',20)
        elif key=='canvas':field(h,'width',400);field(h,'height',180)
        else:
            for k,v in dict(x=30,y=40,width=400,height=200).items():field(h,k,v)
def exercise(h):
    mode=h.mode;h.launch();h.check();initial=CASES['geometry']['initial'];baseline=[caption(h,p) for p in initial];assert all(len(set(p))>2 for p in baseline);h.screenshot('initial')
    h.report['baseline_pixel_sha256']=[hashlib.sha256(p).hexdigest() for p in baseline]
    if mode=='frozen-preview':h.command('freeze-preview')
    if mode=='unwrap':h.point(420,330);h.wait(lambda:h.value('title')=='Layout group');action='unwrap'
    else:h.point(30,30);h.wait(lambda:h.value('title')=='Editable pane');h.point(30,110,True);h.wait(lambda:h.value('title')=='');action='wrap'
    h.stage='BUFFER';open_form(h,action);assert 'layout rules' in h.text(h.find('layout.note'))
    if mode in ('cancel-buffer','revoke','retain-container','topology'):
        field(h,'title','Private container');held=h.find('layout.title')
        if mode=='cancel-buffer':h.click('layout.cancel');h.wait(lambda:h.erased(held) and h.sensitive('wrap'));assert not h.sensitive('apply');h.check()
        elif mode=='topology':h.command('layout-narrow');h.wait(lambda:h.erased(held) and h.sensitive('wrap'));assert not h.sensitive('apply');h.check()
        else:
            issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:h.erased(held) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-__import__('time').monotonic()));h.report['erase_ms']=(__import__('time').monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms'];h.report['production_erased']=True
            h.stage='RETAINED';assert not any('Private container' in h.text(o) for o in h.objects()),'retained container disclosed';h.check();h.command('regrant');assert h.erased(held) and not h.sensitive('wrap');h.click('reload');h.event('event','reloaded');assert h.erased(held)
        h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    key='canvas' if mode=='overflow' else mode if mode in CASES['layouts'] else 'stack-horizontal'
    if mode=='unwrap':expected=CASES['unwrapped'];positions=[[0,0,180,80]];samples=[composite(baseline[0],baseline[1])];h.report['expected_composite_sha256']=hashlib.sha256(samples[0]).hexdigest()
    else:
        if mode=='invalid':field(h,'gap_dip','NaN');h.click('layout.set');h.wait(lambda:bool(value(h,'error')));assert value(h,'gap_dip')=='NaN' and not h.sensitive('apply');h.check()
        setup(h,key);expected=CASES['expected'][key];positions=CASES['geometry'][key];samples=baseline
        if mode=='overflow':field(h,'width',180);field(h,'height',80)
    def pixels_match():
        return [caption(h,p) for p in positions]==samples and (mode!='unwrap' or set(caption(h,initial[1]))=={0})
    set_form(h);h.wait(lambda:h.value('title')==('' if mode=='unwrap' else 'Container'));h.report['expected_key']='unwrapped' if mode=='unwrap' else key
    def unavailable():return PREVIEW['required_status'] in h.status() and PREVIEW['forbidden_status'] not in h.status() and set(h.pixels(0,0,500,420))=={0}
    if mode=='overflow':
        h.stage='UNAVAILABLE';h.wait(unavailable);h.check();h.screenshot('unavailable');assert h.value('title')=='Container' and h.sensitive('layout') and h.sensitive('undo')
        h.click('undo');h.wait(lambda:not h.sensitive('undo'));h.wait(lambda:[caption(h,p) for p in initial]==baseline)
        h.click('redo');h.wait(unavailable);open_form(h,'layout');field(h,'width',400);field(h,'height',180);set_form(h)
        expected=PREVIEW['repaired_scene'];h.report['recovered_preview']=True
    h.stage='PIXELS';h.wait(pixels_match);h.check();h.screenshot('draft')
    h.click('undo')
    if mode=='overflow':h.wait(unavailable);h.click('undo')
    h.wait(lambda:not h.sensitive('undo') and h.sensitive('redo'));h.wait(lambda:[caption(h,p) for p in initial]==baseline)
    h.click('redo')
    if mode=='overflow':h.wait(unavailable);h.click('redo')
    h.wait(lambda:not h.sensitive('redo') and h.sensitive('apply'));h.wait(pixels_match)
    if mode=='responsive':
        h.command('layout-narrow');h.wait(lambda:[caption(h,p) for p in CASES['geometry']['responsive-narrow']]==baseline);h.command('layout-wide');h.wait(lambda:[caption(h,p) for p in positions]==samples)
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');h.check()
    if mode!='wrong-container':assert submitted['body']['operations'][0]['scene']==expected
    h.command('release');result=h.event('event','result')['result'];assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.wait(pixels_match);h.command('quit');assert h.proc.wait(timeout=5)==0
    assert mode not in ('wrong-container','retain-container','frozen-preview');h.report['outcome']='pass'
def observe(exe,exit_exe,folder,mode):
    h=ContainerHarness(exe,exit_exe,folder,mode);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),layout_helper_sha256=sha(ROOT/'tests/editor/native_layout_authoring.py'),preview_fixture_sha256=sha(ROOT/'tests/editor/container-preview-cases.json'))
    try:exercise(h)
    except AssertionError as error:
        h.report.update(stage=h.stage,error=str(error));h.screenshot('failure')
        wrong=mode=='wrong-container' and h.stage=='STORE' and str(error)=='stored documents differ' and stored(h.directory)['scene']['widgets'][-1]['children']==['widget:second','widget:text']
        retained=mode=='retain-container' and h.stage=='RETAINED' and str(error)=='retained container disclosed' and h.report.get('production_erased') and any('Private container' in h.text(o) for o in h.objects()) and stored(h.directory)==h.documents()
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(error)=='PIXELS observation deadline' and h.value('title')=='Container' and stored(h.directory)==h.documents() and [hashlib.sha256(caption(h,p)).hexdigest() for p in CASES['geometry']['initial']]==h.report['baseline_pixel_sha256'] and caption(h,CASES['geometry']['initial'][1])!=caption(h,CASES['geometry']['stack-horizontal'][1])
        if wrong or retained or frozen:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve());folder=evidence/('containers-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-CONTAINERS',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/container-cases.json'),preview_fixture_sha256=sha(ROOT/'tests/editor/container-preview-cases.json'),executable_sha256=sha(exe),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_cases']+PREVIEW['native_cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err);detail=json.loads((folder/mode/'result.json').read_text());report['cases'].append(dict(case=mode,outcome=detail['outcome'],fault_detected=detail.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')));assert child.returncode==0 and detail['outcome']=='pass',(mode,err.decode(errors='replace'))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
