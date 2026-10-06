from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[2];python=str(r/'.venv/Scripts/python.exe')
for profile in ['linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp']:
 p=subprocess.run([python,'-X','utf8','out/campaign/surface_flow.py',profile,'configure','build','test'],cwd=r)
 if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run([python,'-X','utf8','out/campaign/audit_surface_legacy.py'],cwd=r);raise SystemExit(p.returncode)
