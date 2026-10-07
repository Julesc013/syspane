from pathlib import Path
out=Path.cwd()/'out/campaign'
s=(out/'prepare_focus_idle_prune.py').read_text().replace("('w-10-edit-locks','w-10-group')","('w-10-snap','w-10-arrange')").replace('focus-idle-prune-plan.json','focus-idle-more-prune-plan.json')
(out/'prepare_focus_idle_more_prune.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'prune_focus_idle_attempts.ps1').read_text().replace('focus-idle-prune-plan.json','focus-idle-more-prune-plan.json').replace('focus-idle-pruned-attempts.json','focus-idle-more-pruned-attempts.json').replace("'w-10-edit-locks'","'w-10-snap'").replace("'w-10-group'","'w-10-arrange'")
(out/'prune_focus_idle_more_attempts.ps1').write_text(s,encoding='utf-8',newline='\n')
