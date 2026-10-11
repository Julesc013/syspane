"""Actual native collector with manual public callback traces, not GUI qualification."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,uuid
from gtk_history_phases import decode
ROOT=Path(__file__).resolve().parents[2]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
exe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
folder=evidence/('gtk-history-phases-probe-'+uuid.uuid4().hex[:12]);folder.mkdir()
env=dict(os.environ,SYSPANE_GTK_HISTORY_PHASE_FILE=str(folder/'phases.journal'))
report=dict(started_at=datetime.now(timezone.utc).isoformat(),outcome='fail',diagnostic_only=True,scope='Native collector fixture with manually invoked public observer traces; not product/native GUI qualification',executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/gtk_history_phases.py',ROOT/'tests/scene/gtk_history_phases.hpp')})
try:
    result=subprocess.run([str(exe),str(ROOT/'spec/fixtures/valid'),'PHASE-COLLECTOR'],env=env,capture_output=True,timeout=20)
    (folder/'stdout').write_bytes(result.stdout);(folder/'stderr').write_bytes(result.stderr)
    assert result.returncode==0,result.stderr;value=json.loads(result.stdout)
    assert value['delay_us']==34 and value['exclusive_output'] and value['record_capacity'] and value['observer_controls']==3
    raw=(folder/'phases.journal').read_bytes();rows=decode(raw,[{k:value[k] for k in ('work_us','delay_us')}])
    assert len(rows)==1 and all(rows[0][k]==v for k,v in dict(index=0,stage=1,generation_before=1,generation_after=2,points=1,phase_mask=7).items())
    assert (folder/'phases.journal').stat().st_mode&0o777==0o600
    report.update(outcome='pass',observed=value,journal_sha256=sha(raw),rows=rows)
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
