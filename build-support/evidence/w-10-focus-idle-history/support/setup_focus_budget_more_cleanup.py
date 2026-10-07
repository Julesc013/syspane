from pathlib import Path
out=Path.cwd()/'out/campaign'
s=(out/'prepare_focus_idle_budget_prune.py').read_text().replace("('w-10-content-properties','w-10-binding-authoring')","('w-10-widget-creation','w-10-native-editor')").replace('focus-idle-budget-prune-plan.json','focus-idle-budget-more-prune-plan.json')
(out/'prepare_focus_idle_budget_more_prune.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'prune_focus_idle_budget_attempts.ps1').read_text().replace('focus-idle-budget-prune-plan.json','focus-idle-budget-more-prune-plan.json').replace('focus-idle-budget-pruned-attempts.json','focus-idle-budget-more-pruned-attempts.json').replace("'w-10-content-properties'","'w-10-widget-creation'").replace("'w-10-binding-authoring'","'w-10-native-editor'")
(out/'prune_focus_idle_budget_more_attempts.ps1').write_text(s,encoding='utf-8',newline='\n')
