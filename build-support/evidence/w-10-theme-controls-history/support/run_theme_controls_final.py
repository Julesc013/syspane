from pathlib import Path
import subprocess,sys
r=Path.cwd();python=str(r/'.venv/Scripts/python.exe')
for profile,steps in [('windows-x64-gcc15',['configure','build','test','portable']),('windows-x86-v141-xp',['configure','build','test','portable']),('linux-x64-gcc13',['build','test','portable','native'])]:
 p=subprocess.run([python,'-X','utf8','out/campaign/theme_controls_flow.py',profile,*steps],cwd=r)
 if p.returncode:sys.exit(p.returncode)
