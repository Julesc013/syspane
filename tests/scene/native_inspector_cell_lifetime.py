"""Real native inspector cache retirement across collapse/policy/regrant/destruction."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/fault'))
from native_diagnostic import launch_xvfb
sha=lambda raw:hashlib.sha256(raw).hexdigest()
exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
folder=evidence/('inspector-cell-lifetime-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
report=dict(started_at=datetime.now(timezone.utc).isoformat(),outcome='fail',scope='Small real SceneInspector native cache/lifecycle test, not maximum/installed/performance/edition qualification',executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/inspector_cell_lifetime.hpp',ROOT/'source/interfaces/scene_inspector_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.hpp')})
try:
    server,env=launch_xvfb(folder,(1600,2048));env.update(G_DEBUG='fatal-warnings',NO_AT_BRIDGE='1')
    result=subprocess.run([str(exe),str(ROOT/'spec/fixtures/valid'),'CELL-LIFETIME'],env=env,capture_output=True,timeout=15)
    (folder/'stdout').write_bytes(result.stdout);(folder/'stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr
    observed=json.loads(result.stdout);assert observed==dict(outcome='pass',initial_cells=8,collapsed_children=6,fresh_cells=4,renderer_columns=2,defunct_once=True,after_destroy_empty=True,native_modern_word_unsupported=True,original_points=['10 byte; generation 1; start','11 byte; generation 2; join','12 byte; generation 3; join'])
    report.update(outcome='pass',observed=observed)
finally:
    if server:server.terminate();server.communicate(timeout=5)
    report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
