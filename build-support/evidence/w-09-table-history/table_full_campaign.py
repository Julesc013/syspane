from pathlib import Path
import subprocess
r=Path.cwd();python=str(r/'.venv/Scripts/python.exe')
for profile,steps in [('linux-x64-gcc13',['configure','build','test']),('windows-x64-gcc15',['configure']),('windows-x86-v141-xp',['configure'])]:
 subprocess.run([python,'-X','utf8','out/campaign/table_flow.py',profile,*steps],check=True)
