from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import zipfile
r = Path.cwd()
source = 'source/interfaces/editor_theme_form_linux.cpp'
report = r/'build-support/evidence/w-10-theme-controls-normalization.json'
assert not report.exists()
index = json.loads((r/'build-support/evidence/w-10-theme-controls-attempts.json').read_bytes())
archive=next(v['source_archive']['path'] for v in index['attempts'] if v['profile']=='linux-x64-gcc13' and v['action']=='native')
with zipfile.ZipFile(r/archive) as z:old=z.read(source)
new = old.replace(b'\r\n', b'\n')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert sha(old) == index['current_inputs'][source] and old != new and b'\r' not in new
assert subprocess.check_output(['git', 'show', ':'+source]) == new
capture = ['wsl', '-d', 'Ubuntu-24.04', '-u', 'ir4runner', '--', 'python3', '/mnt/d/Projects/SysPane/syspane/out/campaign/capture_lock_artifacts.py', 'linux-x64-gcc13']
before = json.loads(subprocess.check_output(capture, text=True))
record = dict(source_base=index['source_base'], source=source, original_sha256=sha(old), normalized_sha256=sha(new),
              transformation='Replace every CRLF with LF; no other byte changes.',
              reason='The initial staged-byte audit rejected Git line-ending normalization of this one new C++ file.',
              started_at=datetime.now(timezone.utc).isoformat(), outcome='fail', before_artifacts=before)
(r/source).write_bytes(new)
record['source_bytes'] = len(new)
command = ['wsl', '-d', 'Ubuntu-24.04', '-u', 'ir4runner', '--', 'env', 'SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498', 'cmake', '--build', '--preset', 'linux-x64-gcc13']
try:
    # The small normalization rebuild uses the existing build reservation.
    budget = subprocess.run([str(r/'.venv/Scripts/python.exe'), 'build-support/check_workspace_budget.py', '--action', 'build'], capture_output=True, text=True)
    record['preflight'] = dict(exit=budget.returncode, stdout=budget.stdout, stderr=budget.stderr)
    if budget.returncode:
        raise RuntimeError('Normalization rebuild workspace preflight failed')
    result = subprocess.run(command, cwd=r, capture_output=True, text=True, encoding='utf-8', errors='replace')
    record['build'] = dict(command=command, exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    assert result.returncode == 0
    record['after_artifacts'] = json.loads(subprocess.check_output(capture, text=True))
    assert record['after_artifacts'] == before, 'Normalized rebuild changed an executable'
    assert (r/source).read_bytes() == new
    record['outcome'] = 'pass'
finally:
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    report.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(report, record['outcome'])
