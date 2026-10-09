"""Run bounded native form reply checks in a private display and session."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, signal, subprocess, sys, uuid
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tests/fault'), str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify

exe, evidence = map(Path, sys.argv[1:3])
assert os.geteuid() != 0 and evidence.resolve().is_relative_to(exe.parent.resolve())
verify()
folder = evidence/('reply-'+uuid.uuid4().hex[:12]); folder.mkdir(mode=0o700)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = dict(family='EDITOR-REPLY-LIFECYCLE', outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
              executable_sha256=sha(exe), oracle_sha256=sha(Path(__file__)),
              component_checks_sha256=sha(Path(__file__).with_name('reply_lifecycle.hpp')), cases=[])
server = child = None
try:
    server, env = launch_xvfb(folder)
    child = subprocess.Popen(['dbus-run-session', '--', str(exe), '--reply-lifecycle', str(ROOT)],
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = child.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL); stdout, stderr = child.communicate(timeout=5)
        (folder/'stdout').write_bytes(stdout); (folder/'stderr').write_bytes(stderr)
        raise AssertionError('native reply check deadline')
    (folder/'stdout').write_bytes(stdout); (folder/'stderr').write_bytes(stderr)
    assert child.returncode == 0, stderr.decode(errors='replace')
    report['cases'] = [json.loads(line) for line in stdout.splitlines()]
    assert report['cases'] == [dict(case=c, outcome='pass') for c in
        ('direct','reconciled','default','cancelled','unknown','ticket','epoch','revision','facts','query','withdrawn')]
    report['outcome'] = 'pass'
except Exception as exc:
    report['error'] = repr(exc)
    raise
finally:
    if server:
        server.terminate(); server.communicate(timeout=5)
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report['files'] = {p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.name!='xauthority'}
    (folder/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(folder/'result.json', report['outcome'])
