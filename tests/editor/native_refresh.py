"""Native refresh fairness under bounded paint cost; the old priority is a fault."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/editor'),str(ROOT/'tests/configuration')]
from native_editor import observe,launch_xvfb
from native_settings import stored
CASES=json.loads((ROOT/'tests/editor/refresh-cases.json').read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def traces(folder,name):
    paths=sorted(folder.glob(name+'-*.tsv'));assert paths,'missing native trace'
    result=[]
    for path in paths:
        rows=[line.split('\t') for line in path.read_text().splitlines()]
        assert rows and all(len(row)==8 for row in rows)
        refresh=[row for row in rows if row[0]=='refresh'];assert len(refresh)==1,'refresh source not uniquely observed'
        result.append((path,rows))
    return result

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5],True);return
    exe,exit_exe,probe,evidence=map(Path,sys.argv[1:5]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('editor-refresh-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-REFRESH',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),fixture_sha256=sha(ROOT/'tests/editor/refresh-cases.json'),executable_sha256=sha(exe),probe_sha256=sha(probe),probe_source_sha256=sha(ROOT/'tests/editor/refresh_probe_linux.cpp'),preserved_oracles={p:sha(ROOT/p) for p in CASES['preserved_oracles']},cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for case in CASES['cases']:
            name=case['id'];childenv=dict(env,LD_PRELOAD=str(probe),SYSPANE_REFRESH_TRACE=str(folder/name));childenv.pop('SYSPANE_REFRESH_LEGACY',None)
            if case['legacy_priority']:childenv['SYSPANE_REFRESH_LEGACY']='1'
            command=['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/name),case['mode']]
            child=subprocess.Popen(command,env=childenv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err)
            detail_path=folder/name/'result.json';detail=json.loads(detail_path.read_bytes());captures=traces(folder,name);rows=[row for _,data in captures for row in data]
            assert max(int(row[6]) for row in rows)>=CASES['minimum_paints'] and any(row[0]=='slow-paint' for row in rows)
            if case['expected']=='pass':
                assert child.returncode==0 and detail['outcome']=='pass',(name,detail.get('error'),err.decode(errors='replace'))
                assert any(row[0]=='focus-state' and row[2] in ('editor.undo','editor.redo','editor.apply') and row[3:5]==['1','1'] for row in rows),'no matching real/accessibility focus'
                assert any(row[0]=='idle' for row in rows),'no normal-idle progress'
            else:
                assert child.returncode!=0 and detail['outcome']=='fail' and detail['stage'] in ('PIXEL_MOVE','SUBMIT') and detail['error'].endswith('observation deadline')
                failure=detail['focus_failure'];assert failure['control'] in ('undo','redo','apply') and not failure['focused'] and failure['sensitive'] and failure['process_exit'] is None and failure['x_focus'] in failure['owner_windows']
                samples=[row for row in rows if row[0]=='sample' and row[2]=='editor.'+failure['control'] and row[3:5]==['1','0']]
                assert samples and int(samples[-1][1])-int(samples[0][1])>=CASES['minimum_starved_focus_us'] and int(samples[-1][6])>int(samples[0][6])
                assert max(int(row[5]) for row in samples)>=CASES['minimum_starved_focus_us']
                assert stored(folder/name/'store')==json.loads((ROOT/'tests/configuration/large-command-cases.json').read_bytes())['authored']
                assert not any(e.get('event')=='submitted' for e in detail['events'])
            report['cases'].append(dict(case=name,outcome='pass',fault_detected=case['legacy_priority'],observed_outcome=detail['outcome'],record_sha256=sha(detail_path),traces={p.name:sha(p) for p,_ in captures}))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
