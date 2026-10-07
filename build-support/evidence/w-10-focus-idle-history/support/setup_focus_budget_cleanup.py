from pathlib import Path
out=Path.cwd()/'out/campaign'
s=(out/'prepare_focus_idle_more_prune.py').read_text().replace("('w-10-snap','w-10-arrange')","('w-10-content-properties','w-10-binding-authoring')").replace('focus-idle-more-prune-plan.json','focus-idle-budget-prune-plan.json')
(out/'prepare_focus_idle_budget_prune.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'prune_focus_idle_more_attempts.ps1').read_text().replace('focus-idle-more-prune-plan.json','focus-idle-budget-prune-plan.json').replace('focus-idle-more-pruned-attempts.json','focus-idle-budget-pruned-attempts.json').replace("'w-10-snap'","'w-10-content-properties'").replace("'w-10-arrange'","'w-10-binding-authoring'")
(out/'prune_focus_idle_budget_attempts.ps1').write_text(s,encoding='utf-8',newline='\n')
