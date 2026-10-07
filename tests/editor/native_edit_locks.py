"""Independent native lock guards, exact authored scenes and durable reopen."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
from native_layout_authoring import LayoutHarness,field,kind
CASES=json.loads((ROOT/'tests/editor/edit-lock-cases.json').read_bytes())
class LockHarness(LayoutHarness):
    def __init__(self,*args):Harness.__init__(self,*args,locks=True)

def locked(h):return h.text(h.find('lock'))=='Unlock'
def protected(h):
    assert all(not h.sensitive(n) for n in ('value.title','value.x','value.body','properties','layout','content','delete','duplicate','wrap','group'))
    assert h.sensitive('objects') and h.sensitive('lock') and h.sensitive('undo')

def exercise(h):
    mode=h.mode;h.launch();h.check();h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane');baseline=h.pixels(44,44,170,68);assert len(set(baseline))>2;h.screenshot('initial')
    h.report['baseline_pixel_sha256']=hashlib.sha256(baseline).hexdigest();expected=CASES['locked']
    if mode=='nested':
        h.point(300,60,True);h.wait(lambda:h.value('title')=='');h.click('wrap');h.wait(lambda:h.find('layout.set') is not None and h.state(h.find('layout.set'),h.Atspi.StateType.SHOWING));kind(h,'fixed',True)
        for k,v in dict(x=0,y=0,width=480,height=140,title='Locked group').items():field(h,k,v)
        h.click('layout.set');h.wait(lambda:h.value('title')=='Locked group' and h.sensitive('lock'));expected=CASES['grouped']
    elif mode=='multi':h.point(300,60,True);h.wait(lambda:h.value('title')=='');expected=CASES['multi']
    h.stage='LOCK';h.click('lock');h.wait(lambda:locked(h));h.check();protected(h);h.wait(lambda:h.pixels(44,44,170,68)==baseline)
    if mode=='revoke':
        held=h.find('value.title');issued=h.command('revoke');h.wait(lambda:h.erased(held) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-time.monotonic()));h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms'];assert not h.sensitive('lock');h.check();h.command('regrant');assert not h.sensitive('lock') and h.erased(held);h.click('reload');h.event('event','reloaded');h.wait(lambda:'Move me' in h.text(h.find('canvas')));h.check();h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode=='nested':
        h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane' and 'Locked by container' in h.status());protected(h)
        h.click('lock');h.wait(lambda:locked(h));h.click('lock');h.wait(lambda:not locked(h) and 'Locked by container' in h.status());protected(h)
        h.point(470,130);h.wait(lambda:h.value('title')=='Locked group');h.click('lock');h.wait(lambda:not locked(h) and h.sensitive('layout'));h.click('undo');h.wait(lambda:locked(h));protected(h)
        h.point(60,60);h.wait(lambda:'Locked by container' in h.status());h.drag(60,60,20,0);h.input.press(0xff53,shift=True);h.input.press(0xffff);h.wait(lambda:h.number('x')==40 and 'Locked by container' in h.status());h.check()
    elif mode!='multi':
        h.stage='GUARD';h.drag(60,60,20,0);h.input.press(0xff53,shift=True);h.input.press(0xffff);h.wait(lambda:h.number('x')==40 and 'Locked' in h.status());protected(h);h.check();assert h.pixels(44,44,170,68)==baseline
        if mode=='unlock-move':
            h.click('lock');h.wait(lambda:not locked(h) and h.sensitive('value.x'));h.drag(60,60,20,0);h.wait(lambda:h.number('x')==60);expected=CASES['moved']
            h.click('undo');h.wait(lambda:h.number('x')==40);h.click('undo');h.wait(lambda:locked(h));h.click('undo');h.wait(lambda:not h.sensitive('undo'));h.click('redo');h.wait(lambda:locked(h));h.click('redo');h.wait(lambda:not locked(h));h.click('redo');h.wait(lambda:h.number('x')==60 and not h.sensitive('redo'));h.wait(lambda:h.pixels(64,44,170,68)==baseline)
        else:h.click('undo');h.wait(lambda:not h.sensitive('undo') and h.sensitive('value.x'));h.click('redo');h.wait(lambda:locked(h));protected(h)
    h.screenshot('draft');h.check();h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');assert submitted['body']['schema_version']=='0.6.0'
    if mode!='wrong-lock':assert submitted['body']['operations'][0]['scene']==expected
    h.check();h.command('release');result=h.event('event','result')['result'];assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.point(80 if mode=='unlock-move' else 60,60);h.wait(lambda:h.value('title')=='Editable pane')
    if mode=='unlock-move':h.wait(lambda:h.number('x')==60 and h.sensitive('value.x') and h.pixels(64,44,170,68)==baseline)
    else:h.wait(lambda:'Locked' in h.status());assert not h.sensitive('value.x') and h.pixels(44,44,170,68)==baseline
    h.command('quit');assert h.proc.wait(timeout=5)==0;assert mode!='wrong-lock';h.report['outcome']='pass'

def observe(exe,exit_exe,folder,mode):
    h=LockHarness(exe,exit_exe,folder,mode);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),layout_helper_sha256=sha(ROOT/'tests/editor/native_layout_authoring.py'))
    try:exercise(h)
    except AssertionError as error:
        h.report.update(stage=h.stage,error=str(error));h.screenshot('failure')
        if mode=='wrong-lock' and h.stage=='STORE' and str(error)=='stored documents differ' and stored(h.directory)==h.documents(CASES['unlocked'],'41'):h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve());folder=evidence/('edit-locks-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-LOCKS',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/edit-lock-cases.json'),executable_sha256=sha(exe),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err);detail=json.loads((folder/mode/'result.json').read_bytes());report['cases'].append(dict(case=mode,outcome=detail['outcome'],fault_detected=detail.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')));assert child.returncode==0 and detail['outcome']=='pass',(mode,err.decode(errors='replace'))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
