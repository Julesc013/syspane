"""Every admitted controlled publication, then independent complete AT-SPI rows."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, re, select, signal, subprocess, sys, time, traceback, uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/scene'),str(ROOT/'tests/fault'),str(ROOT/'source/build')]
from native_inspector import Keys
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify
import chart_frame_oracle as oracle
import gtk_history_phases as history_phases
CASES_PATH=ROOT/'tests/scene/gtk-history-limits-cases.json'
CASES=json.loads(CASES_PATH.read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()

def expected(points,mixed,generation):
    chart=oracle.chart(points)[1];roots=[chart]
    if mixed:
        table=oracle.table()[1]
        for entity in table['children']:
            entity['information']=f'Producer P1 | Epoch E1 | Generation {generation}'
        roots.append(table)
    rows=[]
    def flatten(row):
        rows.append([row['item'],row['information']])
        for child in row['children']:flatten(child)
    for root in roots:flatten(root)
    return rows

def equal(actual,wanted):assert actual==wanted,'native rows differ from independent literal oracle'
def decode_timings(raw):
    assert len(raw)<=CASES['stderr_bytes'] and raw.endswith(b'\n'),'timing transcript bound/completion'
    lines=[line for line in raw.splitlines() if line.startswith(b'history-timing')]
    assert lines and re.fullmatch(rb'history-timing-begin [0-9]{1,5}',lines[0])
    count=int(lines[0].split()[1]);assert 0<count<=CASES['timing_records'] and lines[-1]==b'history-timing-end '+str(count).encode() and len(lines)==count+2
    samples=[]
    for line in lines[1:-1]:
        match=re.fullmatch(rb'history-timing ([0-9]{1,20}) ([0-9]{1,20})',line);assert match,'invalid timing record'
        values=list(map(int,match.groups()));assert all(v<2**64 for v in values)
        samples.append(dict(zip(('work_us','delay_us'),values)))
    return samples
def controls():
    wanted=expected(oracle.sequence(3),True,3)
    bad=copy.deepcopy(wanted);bad.pop(2)
    second=copy.deepcopy(wanted);second[2][1]=second[2][1].replace('join','start')
    third=copy.deepcopy(wanted);third[-1][1]='Wrong cell'
    for changed in (bad,second,third):
        try:equal(changed,wanted)
        except AssertionError:pass
        else:raise AssertionError('oracle accepted deliberate mutation')
    for name in CASES['cases']:assert oracle.boundary(name=='mixed')==CASES[name]
    literal=b'history-timing-begin 1\nhistory-timing 12 34\nhistory-timing-end 1\n'
    assert decode_timings(literal)==[dict(work_us=12,delay_us=34)]
    for bad in (literal[:-1],literal.replace(b'end 1',b'end 2'),literal.replace(b'12 34',b'-1 34'),literal.replace(b'12 34',b'18446744073709551616 34'),literal.replace(b'begin 1',b'begin 0'),literal.replace(b'begin 1',b'begin 32769'),literal.replace(b'history-timing 12 34\n',b'')):
        try:decode_timings(bad)
        except AssertionError:pass
        else:raise AssertionError('timing decoder accepted malformed journal')

def observe(exe,folder,mode):
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi, GLib
    Atspi.set_timeout(200,500);verify();folder.mkdir()
    report=dict(case=mode,outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),observations=[],progress=[])
    started=time.monotonic();deadline=started+CASES['child_seconds'];buffer=b'';records=0
    err=(folder/'stderr').open('wb');transcript=(folder/'stdout.jsonl').open('wb');keys=None
    env=dict(os.environ);diagnostic=env.get('SYSPANE_GTK_HISTORY_DIAGNOSTIC')=='1';phase_path=folder/'phases.journal'
    env.pop('SYSPANE_GTK_HISTORY_PHASE_FILE',None)
    if diagnostic:
        assert folder.resolve()==folder and folder.stat().st_uid==os.getuid() and not phase_path.exists()
        env['SYSPANE_GTK_HISTORY_PHASE_FILE']=str(phase_path)
    proc=subprocess.Popen([str(exe),str(ROOT/'spec/fixtures/valid'),'GTK-HISTORY-LIMITS',mode,str(CASES[mode]['points'])],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,env=env)
    def save():
        raw=encoded(report);assert len(raw)<=CASES['observation_bytes'];(folder/'result.json').write_bytes(raw)
    def reply():
        nonlocal buffer,records
        while b'\n' not in buffer:
            assert time.monotonic()<deadline,'native history deadline'
            ready=select.select([proc.stdout],[],[],.2)[0]
            if ready:
                block=os.read(proc.stdout.fileno(),4096);assert block,'native history exited before reply'
                buffer+=block;assert len(buffer)<=4096,'native reply buffer'
        line,buffer=buffer.split(b'\n',1);assert len(line)<=512
        transcript.write(line+b'\n');records+=1;assert records<=CASES['reply_records']
        return json.loads(line)
    def command(name):
        issued=time.monotonic();proc.stdin.write((name+'\n').encode());proc.stdin.flush()
        while True:
            value=reply()
            if 'progress' in value:
                report['progress'].append(value);save();print(mode+' progress '+str(value['progress']),flush=True);continue
            assert value['ack']==name and value['command_work_us']<=CASES['gui_limit_us'],value
            report['observations'].append(value);save();return issued,value
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(predicate,seconds=3):
        until=min(deadline,time.monotonic()+seconds)
        while True:
            pump();value=predicate()
            if value:
                assert time.monotonic()<=until,'native observation exceeded deadline';return value
            assert time.monotonic()<until,'native observation deadline';time.sleep(.005)
    def find(description=None,button=None):
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];visited=0
        for i in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(i)
            if app and app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            item,depth=pending.pop();item.clear_cache();visited+=1;assert visited<=512 and depth<=20
            if description and item.get_description()==description:return item
            if button and item.get_role()==Atspi.Role.PUSH_BUTTON and item.get_name()==button:return item
            if item.get_role() in (Atspi.Role.TABLE,Atspi.Role.TREE_TABLE):continue
            for i in range(item.get_child_count()):pending.append((item.get_child_at_index(i),depth+1))
        return None
    def text(item):
        item.clear_cache();interface=item.get_text_iface();return Atspi.Text.get_text(interface,0,-1) if interface else item.get_name() or ''
    def matrix():
        tree.clear_cache();table=tree.get_table_iface();assert table and table.get_n_columns()==2
        count=table.get_n_rows();assert count<=1+4096+321
        result=[[text(table.get_accessible_at(row,col)) for col in range(2)] for row in range(count)]
        assert len(encoded(result))<=CASES['observation_bytes'];return result
    def exact(points,generation):
        wanted=expected(points,mode=='mixed',generation);actual=matrix();equal(actual,wanted)
        report['observations'].append(dict(generation=generation,rows=len(actual),sha256=sha(encoded(actual))))
        (folder/('rows-'+str(generation)+'.json')).write_bytes(encoded(actual));save();return wanted
    try:
        assert reply()==dict(ready=True)
        tree=wait(lambda:find('syspane.scene.inspector'));keys=Keys(proc.pid)
        command('fill');count=CASES[mode]['points'];wanted=exact(oracle.sequence(count),count)
        assert tree.get_component_iface().grab_focus();keys.press(0xff57)
        wait(lambda:list(tree.get_table_iface().get_selected_rows())==[len(wanted)-1])
        summary=wait(lambda:find('syspane.scene.requested-summary'));button=wait(lambda:find(button='Summary'))
        assert button.get_component_iface().grab_focus();keys.press(0x20)
        wait(lambda:text(summary)=='\n'.join(wanted[-1]))
        _,value=command('over');assert value['reason']=='surface.capacity'
        assert matrix()==[] and text(summary)==''
        command('recover');exact([(20000000000,4098,False)],4098)
        issued,_=command('revoke');wait(lambda:matrix()==[] and text(summary)=='',CASES['erasure_ms']/1000)
        report['erasure_ms']=(time.monotonic()-issued)*1000;assert report['erasure_ms']<=CASES['erasure_ms']
        command('fresh');exact([(21000000000,4099,False)],4099);assert text(summary)==''
        command('close');assert matrix()==[] and text(summary)==''
        command('quit');assert proc.wait(timeout=3)==0
        report['actual_exit']=True;report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        if keys:keys.close()
        proc.stdin.close();proc.stdout.close();err.close();transcript.close()
        raw=(folder/'stderr').read_bytes()
        try:
            samples=decode_timings(raw)
            report['timing_max_us']={k:max(v[k] for v in samples) for k in ('work_us','delay_us')}
            report['timing_violations']=[dict(index=i,**v) for i,v in enumerate(samples) if max(v.values())>CASES['gui_limit_us']]
            if report['timing_violations']:report['outcome']='fail'
            report['timing_records']=len(samples)
            if diagnostic:
                phase_raw=phase_path.read_bytes();rows=history_phases.decode(phase_raw,samples)
                details=dict(diagnostic_only=True,original_outcome=report['outcome'],journal_sha256=sha(phase_raw),decoder_sha256=sha(Path(history_phases.__file__).read_bytes()),**history_phases.summarize(rows,CASES['gui_limit_us']))
                (folder/'phases.json').write_bytes(encoded(details));report['diagnostic_only']=True;report['phase_journal_sha256']=sha(phase_raw)
        except Exception:report['timing_failure']=traceback.format_exc();report['outcome']='fail'
        report['stderr_sha256']=sha(raw)
        report['finished_at']=datetime.now(timezone.utc).isoformat();report['elapsed_seconds']=time.monotonic()-started;save()
    assert report['outcome']=='pass',report.get('timing_violations')

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4]);return
    exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent
    controls();folder=evidence/('gtk-history-'+uuid.uuid4().hex[:12]);folder.mkdir()
    report=dict(family='GTK-HISTORY-LIMITS',outcome='fail',diagnostic_only=os.environ.get('SYSPANE_GTK_HISTORY_DIAGNOSTIC')=='1',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [Path(__file__),CASES_PATH,Path(oracle.__file__),ROOT/'tests/scene/gtk_history_limits.hpp',ROOT/'tests/scene/gtk_history_phases.hpp',Path(history_phases.__file__),ROOT/'source/build/surface-runtime.json']},oracle_mutations_rejected=3,cases=[])
    server=None
    try:
        server,env=launch_xvfb(folder,tuple(CASES['screen']));env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)), '--observe',str(exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=CASES['child_seconds'])
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err)
            path=folder/mode/'result.json';case=json.loads(path.read_bytes()) if path.exists() else dict(outcome='fail')
            report['cases'].append(dict(case=mode,outcome='pass' if child.returncode==0 and case['outcome']=='pass' else 'fail',exit=child.returncode,record_sha256=sha(path.read_bytes()) if path.exists() else None))
        assert all(c['outcome']=='pass' for c in report['cases']),report['cases'];report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_bytes(encoded(report));print(folder/'result.json',report['outcome'])

if __name__=='__main__':main()
