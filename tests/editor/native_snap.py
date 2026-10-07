"""Independent native snapping, held guide pixels, history and durable scene oracle."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
CASES=json.loads((ROOT/'tests/editor/snap-cases.json').read_text())
def checked(h,id):
    obj=h.find(id);obj.clear_cache();return obj.get_state_set().contains(h.Atspi.StateType.CHECKED)
def samples(h,scene,count):
    return [h.pixels(b['x']+10,b['y']+10,b['width']-20,b['height']-20) for b in (w['layout']['base'] for w in scene['widgets'][:count])]
def guide(h):return h.text(h.find('guidance'))
def held(h,resize=False,guides=False):
    x,y,dx,dy=(156,116,7,7) if resize else (60,60,37,45) if guides else (60,60,29,21)
    h.drag(x,y,dx,dy,hold=True)
    gx,gy=(168,128) if resize else (200,170) if guides else (72,64)
    h.wait(lambda:guide(h)==f'X guide: {gx} DIP; Y guide: {gy} DIP')
    h.stage='GUIDE_PIXELS'
    h.wait(lambda:h.pixels(gx,10,1,1)==b'\xff\x00\xff' and h.pixels(10,gy,1,1)==b'\xff\x00\xff')
    h.stage='HELD'
    assert not h.sensitive('undo') and not h.sensitive('apply');h.check();h.screenshot('held')

def exercise(h):
    h.launch();h.check();h.point(60,60);h.wait(lambda:h.number('x')==40);h.stage='OPTIONS'
    assert all(not checked(h,id) for id in ('snap-grid','snap-guides','show-grid')) and guide(h)==''
    original=h.cases['authored']['scene'];count=2 if h.mode=='multi' else 1;baseline=samples(h,original,count);assert all(len(set(p))>2 for p in baseline)
    h.report['baseline_pixel_sha256']=hashlib.sha256(b''.join(baseline)).hexdigest()
    option='snap-guides' if h.mode=='guides' else 'snap-grid';h.click(option);h.wait(lambda:checked(h,option))
    if h.mode=='grid':
        h.click('show-grid');h.wait(lambda:h.pixels(16,300,1,1)==b'333' and h.pixels(17,300,1,1)==b'\0\0\0')
        for spacing in (16,32,4,8):h.click('grid-spacing');h.wait(lambda:h.text(h.find('grid-spacing'))==f'Grid {spacing} DIP')
        h.click('show-grid');h.wait(lambda:h.pixels(16,300,1,1)==b'\0\0\0')
    assert not h.sensitive('undo') and not h.sensitive('apply')
    if h.mode=='multi':h.point(220,180,True);h.wait(lambda:h.value('title')=='' and h.sensitive('group'))
    if h.mode=='frozen-preview':h.command('freeze-preview')
    if h.mode=='keyboard':h.focus('canvas');h.input.press(0xff53)
    else:
        h.stage='HELD';held(h,h.mode=='resize',h.mode=='guides')
        if h.mode=='revoke':
            ref=h.find('guidance');assert guide(h);issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:h.erased(ref) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-time.monotonic()))
            h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=h.cases['erase_ms'];h.input.button(False);h.check();h.command('regrant');assert h.erased(ref) and guide(h)=='' and not h.sensitive('snap-grid');h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
        if h.mode in ('escape','options'):
            if h.mode=='escape':h.input.press(0xff1b)
            else:h.click('snap-grid');h.wait(lambda:not checked(h,'snap-grid'))
            h.input.button(False);h.wait(lambda:guide(h)=='' and not h.sensitive('undo') and not h.sensitive('apply'));h.wait(lambda:samples(h,original,count)==baseline);h.check()
            if h.mode=='options':h.click('snap-grid');h.wait(lambda:checked(h,'snap-grid'))
            held(h)
        if h.mode=='bypass':h.input.key(0xffe3,True)
        h.input.button(False)
        if h.mode=='bypass':h.input.key(0xffe3,False);h.input.sync()
    key=h.mode if h.mode in h.cases['expected'] else 'grid';expected=h.cases['expected'][key];b=expected['widgets'][0]['layout']['base']
    h.wait(lambda:h.sensitive('apply') and guide(h)=='')
    if h.mode=='multi':h.point(490,410);h.point(b['x']+10,b['y']+10)
    h.wait(lambda:all(h.number(k)==b[k] for k in ('x','y','width','height')));h.report['observed_geometry']={k:h.number(k) for k in ('x','y','width','height')};h.stage='PIXELS'
    # Resizing retains the same independently sampled text region; movement
    # compares identical-size regions at independently specified new locations.
    positions=original if h.mode=='resize' else expected
    h.wait(lambda:samples(h,positions,count)==baseline);h.screenshot('snapped')
    h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:samples(h,original,count)==baseline)
    h.click('redo');h.wait(lambda:h.sensitive('apply'));h.wait(lambda:samples(h,positions,count)==baseline)
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');h.check();assert not h.sensitive('snap-grid') and not h.sensitive('snap-guides') and not h.sensitive('show-grid')
    if h.mode!='wrong-commit':assert submitted['body']['operations'][0]['scene']==expected
    if h.mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
    h.command('release');result=h.event('event','result')['result']
    if h.mode=='cancel':assert result['outcome']=='cancelled';h.check();h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if h.mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
    h.wait(lambda:'Saved durably' in h.status());h.note('DURABLE');h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.wait(lambda:samples(h,positions,count)==baseline)
    assert not checked(h,'snap-grid') and not checked(h,'snap-guides') and not checked(h,'show-grid') and guide(h)=='';h.note('REOPEN');h.command('quit');assert h.proc.wait(timeout=5)==0
    assert h.mode not in ('wrong-commit','frozen-preview');h.report['outcome']='pass'

def observe(exe,exit_exe,folder,mode):
    h=Harness(exe,exit_exe,folder,mode,snap=True);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'))
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.report['fields']={k:h.value(k) for k in ('title','x','y','width','height')};h.screenshot('failure')
        wrong=mode=='wrong-commit' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][0]['layout']['base']['x']==71
        frozen=mode=='frozen-preview' and h.stage=='GUIDE_PIXELS' and str(exc)=='GUIDE_PIXELS observation deadline' and guide(h)=='X guide: 72 DIP; Y guide: 64 DIP' and stored(h.directory)==h.documents() and hashlib.sha256(b''.join(samples(h,h.cases['authored']['scene'],1))).hexdigest()==h.report['baseline_pixel_sha256'] and h.pixels(72,10,1,1)!=b'\xff\x00\xff'
        if wrong or frozen:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('snap-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-SNAP',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/snap-cases.json'),cases=[])
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
