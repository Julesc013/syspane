from pathlib import Path
import json
r=Path.cwd();out=r/'out/campaign'
s=(out/'prune_locks_duplicates.py').read_text().replace("('w-10-containers',)","('w-10-edit-locks',)").replace('locks-pruned-duplicates.json','focus-idle-pruned-duplicates.json')
(out/'prune_focus_idle_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'prepare_locks_prune.py').read_text().replace("('w-10-containers',)","('w-10-edit-locks','w-10-group')").replace('locks-prune-plan.json','focus-idle-prune-plan.json')
(out/'prepare_focus_idle_prune.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'prune_locks_attempts.ps1').read_text().replace('locks-prune-plan.json','focus-idle-prune-plan.json').replace('locks-pruned-attempts.json','focus-idle-pruned-attempts.json')
s=s.replace("(Join-Path $taskRoot 'w-10-containers')", "(Join-Path $taskRoot 'w-10-edit-locks')",1).replace("(Join-Path $taskRoot 'w-10-containers')", "(Join-Path $taskRoot 'w-10-group')",1)
(out/'prune_focus_idle_attempts.ps1').write_text(s,encoding='utf-8',newline='\n')
