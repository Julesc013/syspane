"""Bridge-enabled real owner: immediate erasure, late events, replacement and shutdown."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/fault'))
from native_diagnostic import launch_xvfb
sha=lambda raw:hashlib.sha256(raw).hexdigest()
exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
folder=evidence/('inspector-retirement-owner-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
report=dict(started_at=datetime.now(timezone.utc).isoformat(),outcome='fail',scope='Bridge-enabled actual two-owner retirement and shutdown; external wire and maximum timing qualify separately',executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/inspector_retirement_owner.hpp',ROOT/'tests/scene/inspector_cell_lifetime.hpp',ROOT/'source/interfaces/scene_inspector_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.cpp')})
try:
    server,env=launch_xvfb(folder,(1600,2048));env.update(G_DEBUG='fatal-warnings',NO_AT_BRIDGE='0');env.pop('AT_SPI_BUS_ADDRESS',None)
    result=subprocess.run(['dbus-run-session','--',str(exe),str(ROOT/'spec/fixtures/valid'),'RETIREMENT-OWNER'],env=env,capture_output=True,timeout=15)
    (folder/'stdout').write_bytes(result.stdout);(folder/'stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr
    observed=json.loads(result.stdout);assert observed['outcome']=='pass' and observed['cells_per_projection']==646
    for key in ('immediate_empty','defunct_once','rapid_regrant','independent_owners','partial_expansion','pending_close','parent_destroy','after_destroy_empty'):assert observed[key] is True
    for owner in ('first','second'):
        s=observed[owner];assert s['pending']==0 and s['accepted']==s['delivered'] and s['accepted']>256 and s['polls']>1 and not s['failed'] and s['max_us']<=100000
    assert observed['calls'] and all(0<=call['work_us']<=100000 for call in observed['calls'])
    report.update(outcome='pass',observed=observed)
finally:
    if server:server.terminate();server.communicate(timeout=5)
    report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
