"""Run fixed native form request checks in a private display and session."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, signal, subprocess, sys, uuid
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tests/fault'), str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify

exe, evidence = map(Path, sys.argv[1:3])
history = True
prepared = len(sys.argv)==4 and sys.argv[3]=='--prepared'
initial = len(sys.argv)==4 and sys.argv[3]=='--initial-input'
assert os.geteuid() != 0 and evidence.resolve().is_relative_to(exe.parent.resolve())
verify()
folder = evidence/('reply-'+uuid.uuid4().hex[:12]); folder.mkdir(mode=0o700)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = dict(family='EDITOR-REQUEST' if history else 'EDITOR-INITIAL-INPUT' if initial else 'PREPARED-EDITOR' if prepared else 'EDITOR-REPLY-LIFECYCLE', outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
              executable_sha256=sha(exe), oracle_sha256=sha(Path(__file__)),
              component_checks_sha256=sha(Path(__file__).with_name('request_form.hpp' if history else 'initial_input.hpp' if initial else 'reply_lifecycle.hpp')), cases=[])
server = child = None
try:
    server, env = launch_xvfb(folder)
    child = subprocess.Popen(['dbus-run-session', '--', str(exe), '--request-form' if history else '--initial-input' if initial else '--prepared-editor' if prepared else '--reply-lifecycle', str(ROOT)],
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = child.communicate(timeout=90 if history else 30)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL); stdout, stderr = child.communicate(timeout=5)
        (folder/'stdout').write_bytes(stdout); (folder/'stderr').write_bytes(stderr)
        raise AssertionError('native reply check deadline')
    (folder/'stdout').write_bytes(stdout); (folder/'stderr').write_bytes(stderr)
    assert child.returncode == 0, stderr.decode(errors='replace')
    if history:assert b"Gtk-WARNING" not in stderr and b"Gtk-CRITICAL" not in stderr, stderr.decode(errors="replace")
    report['cases'] = [json.loads(line) for line in stdout.splitlines()]
    expected = json.loads((ROOT/'tests/editor/request-form-cases.json').read_bytes())['cases'] if history else ('tree','pointer','topology-tree','topology-pointer','reload','withdrawal','empty-click','no-selection-key','fallback') if initial else ('direct','reconciled','default','cancelled','unknown','ticket','epoch','revision','facts','query','withdrawn',*(('null',) if prepared else ()))
    assert [(v['case'],v['outcome']) for v in report['cases']] == [(c,'pass') for c in expected]
    for v in report['cases']:
        assert set(v)=={'case','outcome','capture_us','adopt_us'} and 0<=v['capture_us']<100000 and 0<=v['adopt_us']<100000
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
