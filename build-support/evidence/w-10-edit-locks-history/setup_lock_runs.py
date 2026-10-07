from pathlib import Path
import json
r=Path.cwd();base='83da967d8a7311b8124c3beae304af103730eccd'
def save(n,s):(r/'out/campaign'/n).write_text(s,encoding='utf-8',newline='\n')
for target,source in [('locks_step.py','container_step.py'),('locks_flow.py','container_flow.py')]:
 s=(r/'out/campaign'/source).read_text().replace('w-10-containers','w-10-edit-locks').replace('container_step.py','locks_step.py').replace('container-execution-','locks-execution-').replace("r/'spec/delivery/packages/w-10-container-preview.md'","r/'spec/delivery/packages/w-10-edit-locks.md'")
 s=s.replace("('containers','layout'","('locks','containers','layout'").replace("{'containers':","{'locks':['ctest','--preset',profile,'-R','^native[.]EDITOR-LOCKS$','--output-on-failure'],'containers':",1)
 s=s.replace("{'containers':'syspane_editor_window'","{'locks':'syspane_editor_window','containers':'syspane_editor_window'").replace("'^editor[.]CONTAINER-'","'^editor[.]LOCK-'")
 save(target,s)
# Only previously committed duplicate evidence is eligible for cleanup.
s=(r/'out/campaign/prepare_container_prune.py').read_text().replace("('w-10-modal-focus','w-10-layout-authoring')","('w-10-containers',)").replace('container-prune-plan.json','locks-prune-plan.json');save('prepare_locks_prune.py',s)
s=(r/'out/campaign/prune_container_attempts.ps1').read_text().replace("'w-10-modal-focus'","'w-10-containers'").replace("'w-10-layout-authoring'","'w-10-containers'").replace('container-prune-plan.json','locks-prune-plan.json').replace('container-pruned-attempts.json','locks-pruned-attempts.json');save('prune_locks_attempts.ps1',s)
s=(r/'out/campaign/prune_container_duplicates.py').read_text().replace('w-10-modal-focus','w-10-containers').replace('container-pruned-duplicates.json','locks-pruned-duplicates.json');save('prune_locks_duplicates.py',s)
