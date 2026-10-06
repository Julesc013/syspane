from pathlib import Path
import json,subprocess
r=Path.cwd(); py=str(r/'.venv/Scripts/python.exe')
# Sequence the remaining profiles so native deadline laboratories do not compete.
for profile in ['windows-x64-gcc15','windows-x86-v141-xp']:
 p=subprocess.run([py,'-X','utf8','out/campaign/text_flow.py',profile,'configure','build','test'],cwd=r)
 if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run([py,'-X','utf8','out/campaign/audit_text_legacy.py'],cwd=r);raise SystemExit(p.returncode)
