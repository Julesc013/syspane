"""Independent GTK grouping, drawing-order, hierarchy and persistence oracle."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,stored,launch_xvfb
CASES=json.loads((ROOT/'tests/editor/group-cases.json').read_text())
OVERLAP=json.loads((ROOT/'tests/editor/group-overlap-cases.json').read_text())
def select_all(h):
    h.focus('objects');h.input.press(ord('a'),control=True);h.wait(lambda:h.sensitive('group') and h.value('title')=='')
def sample(h,scene):
    return [h.pixels(b['x']+10,b['y']+10,b['width']-20,b['height']-20) for b in (w['layout']['base'] for w in scene['widgets'][:3])]
def sample_second(h,position):return h.pixels(position[0]+OVERLAP['sample_offset'][0],position[1]+OVERLAP['sample_offset'][1],*OVERLAP['sample_extent'])

def foreground(pixels,indices):return all(pixels[n:n+3]==b'\xff\xff\xff' for n in indices)
def exercise(h):
    h.launch();h.check();h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane');assert not h.sensitive('group') and not h.sensitive('ungroup')
    original=h.cases['authored']['scene'];baseline=sample(h,original);assert all(len(set(p))>2 for p in baseline);second=sample_second(h,[200,170]);h.screenshot('initial')
    # The authored background is translucent. Only fully opaque foreground
    # pixels must equal the isolated glyph after another raster moves beneath it.
    # Derive these locations from the independent native baseline, never from
    # the grouped output, and require the opposite order to fail this probe.
    opaque=[n for n in range(0,len(second),3) if second[n:n+3]==b'\xff\xff\xff'];assert opaque
    h.stage='GROUP';expected=h.cases['grouped'];positions=original;group_id='widget:new1'
    if h.mode=='nested':
        h.point(220,180,True);h.wait(lambda:h.sensitive('group'));h.click('group');h.wait(lambda:h.value('title')=='Group' and h.number('width')==256)
        h.point(390,320,True);h.wait(lambda:h.sensitive('group') and h.value('title')=='');h.click('group');group_id='widget:new2';expected=h.cases['nested']
    elif h.mode=='overlap':
        h.point(220,180);h.wait(lambda:h.value('title')=='Second pane')
        for key,value in zip(('x','y'),OVERLAP['second_position']):h.field(key,value)
        h.click('properties');h.wait(lambda:h.number('x')==380 and h.number('y')==305 and h.sensitive('apply'))
        h.wait(lambda:not foreground(sample_second(h,[380,305]),opaque));h.report['overlap_opaque_samples']=len(opaque);h.screenshot('overlap-before');h.point(60,60);h.point(380,310,True)
        # The second point falls in the topmost Third pane before grouping.
        h.wait(lambda:h.sensitive('group'));h.click('group');expected=OVERLAP['expected']
    else:select_all(h);h.click('group')
    h.wait(lambda:h.value('title')=='Group' and h.number('x')==40 and h.number('y')==40 and h.number('width')==410 and h.sensitive('ungroup'))
    h.check();h.stage='PIXELS'
    if h.mode=='overlap':h.wait(lambda:foreground(sample_second(h,[380,305]),opaque))
    else:h.wait(lambda:sample(h,original)==baseline)
    if h.mode not in ('nested','overlap'):
        h.click('undo');h.wait(lambda:not h.sensitive('ungroup') and not h.sensitive('apply'));h.wait(lambda:sample(h,original)==baseline)
        h.click('redo');h.wait(lambda:h.sensitive('ungroup') and h.value('title')=='Group')
    if h.mode in ('move','ungroup','frozen-preview'):
        if h.mode=='frozen-preview':h.command('freeze-preview')
        h.stage='MOVE';h.drag(250,100,30,20);h.wait(lambda:h.number('x')==70 and h.number('y')==60);h.report['observed_group']={'x':70,'y':60}
        expected=h.cases['moved'];positions=h.cases['ungrouped'];h.stage='MOVED_PIXELS';h.wait(lambda:sample(h,positions)==baseline)
        if h.mode=='ungroup':
            h.click('ungroup');h.wait(lambda:not h.sensitive('ungroup') and h.sensitive('group') and h.value('title')=='');expected=h.cases['ungrouped']
            h.click('undo');h.wait(lambda:h.sensitive('ungroup') and h.number('x')==70);h.click('redo');h.wait(lambda:h.sensitive('group') and not h.sensitive('ungroup'))
    h.screenshot('grouped');h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted')
    if h.mode!='wrong-group':assert submitted['body']['operations'][0]['scene']==expected
    h.event('event','held');h.check();assert not h.sensitive('group') and not h.sensitive('ungroup') and not h.sensitive('undo')
    if h.mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
    if h.mode=='deny':h.command('deny')
    if h.mode=='revoke':
        held=[h.find('value.'+k) for k in ('title','body','x','y','width','height')]+[o for o in h.objects() if 'Move me' in h.text(o) or (o.get_role()==h.Atspi.Role.TABLE_CELL and h.text(o)=='Group')]
        issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:all(h.erased(o) for o in held) and set(h.pixels(0,0,500,420))=={0},max(.001,issued+.2-time.monotonic()))
        h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=h.cases['erase_ms']
    h.command('release');result=h.event('event','result')['result']
    if h.mode in ('cancel','deny','revoke'):
        h.check()
        if h.mode=='deny':
            assert result['outcome']=='unknown' and result['error']['code']=='policy.denied';h.command('regrant');h.command('retrieve');result=h.event('event','retrieved')['result']
        assert result['outcome']==('cancelled' if h.mode=='cancel' else 'conflict')
        if h.mode=='cancel':h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.check();h.report['outcome']='pass';return
        if h.mode=='revoke':h.command('regrant');assert all(h.erased(o) for o in held) and h.text(h.find('canvas'))==''
    else:
        assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
        if h.mode=='restart':
            h.wait(lambda:'Outcome unknown' in h.status());selector=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==selector
        h.wait(lambda:'Saved durably' in h.status());h.note('DURABLE');h.command('quit');assert h.proc.wait(timeout=5)==0
        h.launch('reopen');h.check(expected,'41')
        if h.mode=='overlap':h.wait(lambda:foreground(sample_second(h,[380,305]),opaque))
        else:h.wait(lambda:sample(h,positions)==baseline)
        if h.mode!='ungroup':
            h.point(340,120);h.wait(lambda:h.value('title')=='Group' and h.number('width')==410 and h.number('x')==(70 if h.mode=='move' else 40) and h.sensitive('ungroup'))
        h.note('REOPEN')
    h.command('quit');assert h.proc.wait(timeout=5)==0;assert h.mode not in ('wrong-group','frozen-preview');h.report['outcome']='pass'
def observe(exe,exit_exe,folder,mode):
    h=Harness(exe,exit_exe,folder,mode,group=True);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),overlap_fixture_sha256=sha(ROOT/'tests/editor/group-overlap-cases.json'))
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.report['fields']={k:h.value(k) for k in ('title','x','y','width','height')};h.screenshot('failure')
        wrong=mode=='wrong-group' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][3]['children']==list(reversed(h.cases['grouped']['widgets'][3]['children']))
        frozen=mode=='frozen-preview' and h.stage=='MOVED_PIXELS' and str(exc)=='MOVED_PIXELS observation deadline' and h.report.get('observed_group')=={'x':70,'y':60} and stored(h.directory)==h.documents() and sample(h,h.cases['authored']['scene'])!=sample(h,h.cases['ungrouped'])
        if wrong or frozen:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('group-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-GROUP',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),fixture_sha256=sha(ROOT/'tests/editor/group-cases.json'),overlap_fixture_sha256=sha(ROOT/'tests/editor/group-overlap-cases.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_modes']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
            assert not timed_out and child.returncode==0,(mode,stderr.decode(errors='replace'));case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass'
            report['cases'].append(dict(case=mode,outcome='pass',fault_detected=case.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
