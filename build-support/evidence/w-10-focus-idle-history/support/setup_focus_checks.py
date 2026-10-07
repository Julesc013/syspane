from pathlib import Path
r=Path.cwd()
s=(r/'out/campaign/finish_edit_locks_checks.py').read_text().replace('w-10-edit-locks-','w-10-focus-idle-').replace('83da967d8a7311b8124c3beae304af103730eccd','9c1757de6a8227b2a4235f8be7b727a9d3f55d7d')
(r/'out/campaign/finish_focus_idle_checks.py').write_text(s,encoding='utf-8',newline='\n')
