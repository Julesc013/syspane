from pathlib import Path
r=Path.cwd()
p=r/'out/campaign/archive_edit_locks.py'
s=p.read_text().replace('w-10-edit-locks','w-10-focus-idle')
s=s.replace("if p.stat().st_mtime<cutoff:continue", "if p.stat().st_mtime<cutoff and p.parent.name!='editor-idle-788c47e77043':continue")
s=s.replace("if v.get('family') not in (", "if v.get('family') not in ('EDITOR-IDLE-DIAGNOSTIC','EDITOR-REFRESH','EDITOR-REFRESH-ANIMATION-DIAGNOSTIC','TEXT-RASTER','IMAGE-JOB','SCENE-SURFACE','SCENE-IMAGE','SCENE-CHART','SCENE-TABLE','SCENE-INSPECTOR-MODEL',")
(r/'out/campaign/archive_focus_idle.py').write_text(s,encoding='utf-8',newline='\n')
