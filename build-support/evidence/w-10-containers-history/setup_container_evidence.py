from pathlib import Path
r=Path.cwd();o=r/'out/campaign';base='faba4663be62ff4790ea31b540d03c9f10bc2ce2'
for old,new in [('archive_layout.py','archive_containers.py'),('preserve_layout.py','preserve_containers.py'),('finish_layout_checks.py','finish_containers_checks.py'),('finish_layout.py','finish_containers.py'),('stage_layout.py','stage_containers.py')]:
 s=(o/old).read_text().replace('w-10-layout-authoring','w-10-containers').replace('layout-authoring-handoff.json','containers-handoff.json').replace('321a11e67d28582b5c03c4f0b4c89ecc4c6b550c',base).replace('layout-execution-','container-execution-').replace('layout-staging-paths.txt','container-staging-paths.txt').replace('==132','==138').replace('==157','==172').replace('132 affected','138 affected').replace('157 native cases across ten matrices','172 native cases across eleven matrices')
 if old=='archive_layout.py':s=s.replace("('EDITOR-LAYOUT',", "('EDITOR-CONTAINERS','EDITOR-LAYOUT',")
 if old=='preserve_layout.py':
  start=s.index('helpers=');end=s.index('\nfor p in [',start)
  helpers=['prune_container_duplicates.py','container-pruned-duplicates.json','prepare_container_prune.py','prune_container_attempts.ps1','container-prune-plan.json','container-pruned-attempts.json','prepare_container_inputs.py','register_containers.py','correct_container_oracle.py','inspect_container_composite.py','container_step.py','container_flow.py','document_containers.py','archive_containers.py','preserve_containers.py','setup_container_evidence.py','finish_containers_checks.py','finish_containers.py','stage_containers.py']
  s=s[:start]+'helpers='+repr(helpers)+s[end:]
  s=s.replace("for n in ('fixed-inputs.json','fixed-inputs.zip')", "for n in ('fixed-inputs.json','fixed-inputs.zip','oracle-correction.json','composite-calibration.json')")
  s=s.replace("for action in ('layout',", "for action in ('containers','layout',")
  s=s.replace("families={'EDITOR-LAYOUT'", "families={'EDITOR-CONTAINERS':('syspane_editor_window','tests/editor/native_containers.py',15),'EDITOR-LAYOUT'")
  s=s.replace("    if family=='EDITOR-LAYOUT':", "    if family=='EDITOR-CONTAINERS':assert v['fixture_sha256']==sha(r/'tests/editor/container-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='EDITOR-LAYOUT':")
  s=s.replace('independent native layout, observation', 'independent native containers, layout, observation')
  s=s.replace('validation_attempts=[],', "validation_attempts=[],oracle_corrections=[ref(history/'oracle-correction.json'),ref(history/'composite-calibration.json')],")
 if old=='finish_layout.py':
  s=s.replace('Add native layout and active fixed variants through existing atomic draft, resource, policy and persistence owners','Add explicit reflowing Wrap/Unwrap through existing atomic draft and native modal owners')
  a=s.index(' decisions=');b=s.index(' checks=',a)
  s=s[:a]+" decisions=['Freeze complete input/expected scenes, geometry and package before production changes.', 'Retain every surviving authored child value and make reflow explicit; preserve fixed-geometry Group/Ungroup.', 'Reuse native private variant buffers and atomic scene/selection history; Apply remains separate.', 'Preserve both composite-oracle failures and independently derived exact source-over correction without changing frozen scenes or production.', 'Keep the existing workspace limit and all five release tracks.'],\n"+s[b:]
  s=s.replace('132 affected checks','138 affected checks')
  a=s.index(' next_step=');b=s.index('\njsonschema.validate',a)
  s=s[:a]+" next_step='Close lock/visibility/typography, clipboard authority and recovery drafts, then installed controller/catalog/policy ownership and scene-aligned entry/restoration with independent escape. Continue all five release tracks.',\n limitations=['Owned Linux ext4/Xvfb/DBus evidence does not qualify installed editing, historical platforms or physical power-loss durability.', 'Explicit container reflow preserves authored rules; it is not an automatic appearance-preserving conversion for arbitrary responsive layouts.', 'Lock/visibility/typography, clipboard/recovery drafts and installed ownership remain required.', 'Full accessibility/performance, other adapters, historical labs and complete-edition release gates remain open.', 'Windows builds run on contemporary Windows; two existing symlink tooling assertions remain skipped.', 'Earlier unrelated native focus/interface causes remain unproven.'])"+s[b:]
 if old=='stage_layout.py':
  s=s.replace("    if family=='EDITOR-LAYOUT':", "    if family=='EDITOR-CONTAINERS':check('tests/editor/container-cases.json',report['fixture_sha256'])\n    if family=='EDITOR-LAYOUT':")
  s=s.replace("('EDITOR-LAYOUT',", "('EDITOR-CONTAINERS','EDITOR-LAYOUT',")
  s=s.replace("check('tests/editor/layout-authoring-cases.json' if family", "check('tests/editor/container-cases.json' if family=='EDITOR-CONTAINERS' else 'tests/editor/layout-authoring-cases.json' if family")
  s=s.replace("check('tests/editor/native_layout_authoring.py' if family", "check('tests/editor/native_containers.py' if family=='EDITOR-CONTAINERS' else 'tests/editor/native_layout_authoring.py' if family")
  s=s.replace("('wrong-layout','retain-layout'", "('wrong-container','retain-container','wrong-layout','retain-layout'")
  s=s.replace('Staged shared and native layout authoring', 'Staged shared and native reflowing container authoring')
 (o/new).write_text(s,encoding='utf-8',newline='\n')
print('Prepared container preservation and verification helpers.')
