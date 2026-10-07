from pathlib import Path
r=Path.cwd();old='w-11-settings-resources';new='w-10-editor-draft';base='10765b6a65b9fe3e13e7e255fba2b91758107d0b'
def read(n):return (r/'out/campaign'/n).read_text().replace(old,new).replace('252647623e2d56cbc6f2797fb9325d788d9a21d5',base)
def write(n,s):(r/'out/campaign'/n).write_text(s,encoding='utf-8',newline='\n')
write('archive_editor.py',read('archive_resource_settings.py'))
s=read('preserve_resource_settings.py')
s=s.replace("helpers=['resource_settings_step.py','resource_settings_flow.py','archive_resource_settings.py','preserve_resource_settings.py','setup_resource_settings_evidence.py','reclaim_resource_settings_prior.ps1','resource-settings-prior-reclamation.json']","helpers=['editor_step.py','editor_flow.py','archive_editor.py','preserve_editor.py','setup_editor_run.py','setup_editor_evidence.py','prepare_editor_inputs.py','reclaim_editor_prior.ps1','editor-prior-reclamation.json']")
s=s.replace('resource-settings-execution-','editor-execution-').replace('out/campaign/resource-settings-original','out/campaign/editor-original')
s=s.replace('==58','==69').replace("assert sum(c.startswith('settings.') for c in cases)==17","assert sum(c.startswith('settings.') for c in cases)==17 and sum(c.startswith('editor.') for c in cases)==11")
s=s.replace("('syspane_settings_tests','syspane_settings_window'","('syspane_editor_tests','libsyspane_editor_draft.a','syspane_settings_tests','syspane_settings_window'")
s=s.replace("names=['syspane_settings_tests.exe'","names=['syspane_editor_tests.exe','syspane_settings_tests.exe'")
start=s.index("original=json.loads((history/'original.json').read_text())")
end=s.index('write(r/(prefix+',start)
s=s[:start]+"original=json.loads((history/'original.json').read_text())\nfor n,digest in original.items():assert sha(r/n)==digest,('fixed input changed',n)\n"+s[end:]
s=s.replace("for n in ('original','resource-fixture','native-original')","for n in ('original',)")
s=s.replace('58 affected settings/authored/policy/dependency checks','69 affected editor/settings/authored/policy/dependency checks').replace('18 owned native settings modes including exact resource selection/bytes and deliberate faults.','18 existing owned native settings regression modes; these do not qualify a native editor.')
write('preserve_editor.py',s)
s=read('finish_resource_settings_checks.py').replace('finish_resource_settings','finish_editor');write('finish_editor_checks.py',s)
s=read('stage_resource_settings.py').replace('settings-resources-handoff.json','editor-draft-handoff.json').replace('resource-settings-staging-paths.txt','editor-staging-paths.txt')
start=s.index("  if name=='original':");end=s.index('native=json.loads',start)
s=s[:start]+"  for n,digest in inputs.items():\n   if not n.startswith('out/'):check(n,digest)\n"+s[end:]
s=s.replace('Staged source, original fixed settings values','Staged source, independently prepared expected scenes').replace('Owned Linux settings controls, resource identity/bytes and storage outcomes are verified; installed controls','Portable editor operations/history and native settings regression are verified; native editor, installed controls')
write('stage_editor.py',s)
print('Prepared editor evidence helpers.')
