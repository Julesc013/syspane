"""Independent native arrange controls, pixels and exact persistent documents."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
CASES=json.loads((ROOT/'tests/editor/arrange-cases.json').read_text())
def all_selected(h):
    h.focus('objects');h.input.press(ord('a'),control=True)
    h.wait(lambda:h.sensitive('space-horizontal') and h.value('title')=='')
def pixels(h,scene):
    return [h.pixels(b['x']+4,b['y']+4,b['width']-8,b['height']-8) for b in (w['layout']['base'] for w in scene['widgets'])]
def pixel_match(h,scene,expected):
    try:return pixels(h,scene)==expected
    except h.GLib.GError as error:
        # Missing read-only geometry is no pixel observation. Retry only inside
        # the caller's original deadline; fault calibration below requires fresh
        # positive observations and never accepts a timeout as its pixel witness.
        if error.domain!='atspi_error' or 'timeout from dbind' not in str(error):raise
        assert h.proc.poll() is None
        h.report['pixel_rpc_timeouts']=h.report.get('pixel_rpc_timeouts',0)+1
        assert h.report['pixel_rpc_timeouts']<=64
        return False
def selected_frame(h,scene):
    # Await an externally painted multiselection before recording its pixels.
    # AT-SPI state can change before GTK paints; a single-selection resize handle
    # must not accidentally become part of the reference image.
    return all(h.pixels(b['x']+1,b['y']+1,1,1)==bytes((0,153,255)) for b in (w['layout']['base'] for w in scene['widgets']))
def held_activation(h,id):
    h.focus(id);obj=h.find(id);until=time.monotonic()+.16
    h.input.key(0x20,True);h.input.sync()
    try:
        while time.monotonic()<until:
            h.pump();obj.clear_cache()
            if not obj.get_state_set().contains(h.Atspi.StateType.FOCUSED):
                h.report['focus_failure']={'control':id,'sensitive':h.sensitive(id),'focused':[{'name':h.text(o),'description':o.get_description(),'role':str(o.get_role())} for o in h.objects() if o.get_state_set().contains(h.Atspi.StateType.FOCUSED)]}
                raise AssertionError('repaint stole native button focus')
            time.sleep(.005)
    finally:h.input.key(0x20,False);h.input.sync()
def exercise(h):
    h.launch();h.check();h.stage='CONTROLS';h.point(60,60);h.wait(lambda:h.number('x')==40)
    assert not h.sensitive('align-left') and not h.sensitive('space-horizontal')
    h.field('title','Buffered');assert not h.sensitive('align-left');h.stage='FOCUS';held_activation(h,'revert-fields');h.wait(lambda:h.value('title')=='Editable pane');h.stage='CONTROLS'
    if h.mode=='left':
        h.field('width',32);h.field('height',16);h.click('properties');h.wait(lambda:h.number('width')==32 and h.sensitive('undo'));all_selected(h)
        h.click('align-left');h.wait(lambda:'Arrange needs fixed widgets' in h.status());h.click('undo');h.wait(lambda:not h.sensitive('undo') and not h.sensitive('apply'));h.check()
    all_selected(h);original=h.cases['authored']['scene'];h.wait(lambda:selected_frame(h,original));baseline=pixels(h,original);assert all(len(set(p))>2 for p in baseline)
    action=next((c for c in h.cases['cases'] if c['action']==h.mode),h.cases['cases'][6]);expected=action['expected'];name=action['action']
    button=('space-' if name in ('horizontal','vertical') else 'align-')+name
    h.screenshot('initial')
    if h.mode=='frozen-preview':h.command('freeze-preview')
    h.click(button);h.wait(lambda:h.sensitive('apply'))
    # Inspect an independently known changed box before checking pixels. The
    # frozen-preview control must really mutate the draft and retain old pixels.
    b=expected['widgets'][1]['layout']['base'];h.point(490,410);h.point(b['x']+8,b['y']+8);h.wait(lambda:h.number('x')==b['x'] and h.number('y')==b['y']);all_selected(h)
    h.report['observed_second']={'x':b['x'],'y':b['y']};h.stage='PIXELS';h.wait(lambda:pixel_match(h,expected,baseline))
    if h.mode=='left':h.click('space-horizontal');h.wait(lambda:'not enough room' in h.status());assert pixels(h,expected)==baseline
    h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:pixels(h,original)==baseline)
    h.click('redo');h.wait(lambda:h.sensitive('apply'));h.wait(lambda:pixels(h,expected)==baseline);h.check();h.screenshot('arranged')
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted')
    if h.mode!='wrong-commit':assert submitted['body']['operations'][0]['scene']==expected
    h.event('event','held');h.check();assert not h.sensitive(button) and not h.sensitive('undo')
    if h.mode=='cancel':held_activation(h,'cancel-request');h.event('event','cancel-requested')
    if h.mode=='deny':h.command('deny')
    if h.mode=='revoke':
        held=[h.find('value.'+k) for k in ('title','body','x','y','width','height')]+[o for o in h.objects() if 'Move me' in h.text(o)]
        issued=h.command('revoke');h.stage='ERASE'
        h.wait(lambda:all(h.erased(o) for o in held) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-time.monotonic()))
        h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=h.cases['erase_ms']
    h.command('release');result=h.event('event','result')['result']
    if h.mode in ('cancel','deny','revoke'):
        h.check()
        if h.mode=='deny':
            assert result['outcome']=='unknown' and result['error']['code']=='policy.denied'
            h.command('regrant');h.command('retrieve');result=h.event('event','retrieved')['result']
        assert result['outcome']==('cancelled' if h.mode=='cancel' else 'conflict')
        if h.mode=='cancel':h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.check();h.report['outcome']='pass';return
        if h.mode=='revoke':h.command('regrant');assert all(h.erased(o) for o in held) and h.text(h.find('canvas'))==''
    else:
        assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible']
        h.stage='STORE';h.check(expected,'41')
        if h.mode=='restart':
            h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
        h.wait(lambda:'Saved durably' in h.status());h.note('DURABLE')
        h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');all_selected(h);h.wait(lambda:pixels(h,expected)==baseline);h.note('REOPEN')
    h.command('quit');assert h.proc.wait(timeout=5)==0;assert h.mode not in ('wrong-commit','frozen-preview');h.report['outcome']='pass'
def observe(exe,exit_exe,folder,mode):
    h=Harness(exe,exit_exe,folder,mode,arrange=True);h.report['oracle_sha256']=sha(Path(__file__));h.report['harness_sha256']=sha(ROOT/'tests/editor/native_editor.py')
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.screenshot('failure')
        wrong=mode=='wrong-commit' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][0]['layout']['base']['x']==71
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(exc)=='PIXELS observation deadline' and h.report.get('observed_second')=={'x':217,'y':170} and h.sensitive('apply') and stored(h.directory)==h.documents() and pixels(h,h.cases['authored']['scene'])!=pixels(h,h.cases['cases'][6]['expected'])
        if wrong or frozen:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('arrange-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-ARRANGE',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/arrange-cases.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_modes']:
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
