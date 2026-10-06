from pathlib import Path
import subprocess,sys
r=Path.cwd()
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
 p=subprocess.run([sys.executable,'-X','utf8','out/campaign/bindings_flow.py',profile,'configure','build','test'],cwd=r)
 if p.returncode:sys.exit(p.returncode)
