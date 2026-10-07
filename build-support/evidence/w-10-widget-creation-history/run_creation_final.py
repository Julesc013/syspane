from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[2];python=str(r/'.venv/Scripts/python.exe')
for profile,steps in (
    ('windows-x64-gcc15',['configure','build','test']),
    ('windows-x86-v141-xp',['configure','build','test']),
    ('linux-x64-gcc13',['build','test','creation','bindings','properties','snap','group','arrange','native','large'])):
    subprocess.run([python,'-X','utf8','out/campaign/creation_flow.py',profile,*steps],cwd=r,check=True)
