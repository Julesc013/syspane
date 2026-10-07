from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=(r/'out/campaign/preserve_large_commands.py').read_text().replace('w-08-large-commands','w-10-arrange').replace('c7c2f32489caec1c1cba143ec3c48cef707a86e5','62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1')
start=s.index('helpers=');end=s.index("for n in ('fixed-inputs.json'",start)
s=s[:start]+'''helpers=['prepare_arrange.py','arrange_step.py','arrange_flow.py','document_arrange.py','archive_arrange.py','preserve_arrange.py','finish_arrange_checks.py','setup_arrange_evidence.py','finish_arrange.py','stage_arrange.py','diagnose_arrange_native.py']
for p in [*sorted((r/'out/campaign').glob('arrange-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
'''+s[end:]
s=s.replace("latest('linux-x64-gcc13','large')[1]","latest('linux-x64-gcc13','arrange')[1]")
s=s.replace("or (n=='tests/configuration/native_large_commands.py' and v['action']!='large')", "or (n=='tests/editor/native_arrange.py' and v['action']!='arrange')")
s=s.replace("assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and v['action']!='arrange'),n","assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and v['action']!='arrange') or (n=='tests/editor/native_editor.py' and v['action'] not in ('native','arrange','large')),n")
s=s.replace('the independent native large-command Python oracle','the independent native arrangement Python oracle').replace('final large-command native execution','final arrangement native execution')
s=s.replace('==88','==94').replace("for action in ('large','resources','native','oracle'):","for action in ('arrange','native','large'):")
start=s.index("families={'LARGE-COMMANDS'");end=s.index('for family,',start)
s=s[:start]+'''families={'EDITOR-ARRANGE':('syspane_editor_window','tests/editor/native_arrange.py',14),'LARGE-COMMANDS':('SysPane.CommandProbe','tests/configuration/native_large_commands.py',24),'EDITOR-FORM':('syspane_editor_window','tests/editor/native_editor.py',20)}
'''+s[end:]
s=s.replace("    if family=='LARGE-COMMANDS':", "    if family=='EDITOR-ARRANGE':\n        assert v['fixture_sha256']==sha(r/'tests/editor/arrange-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='LARGE-COMMANDS':")
s=s.replace('88 affected checks on each development profile and independent native large-command/store/IPC/editor cases.','94 affected checks on each development profile and independent native arrange, editor and large-command/store/IPC cases.')
(r/'out/campaign/preserve_arrange.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/stage_large_commands.py').read_text().replace('w-08-large-commands','w-10-arrange').replace('large-commands-handoff.json','arrange-handoff.json').replace('large-commands-staging-paths.txt','arrange-staging-paths.txt')
s=s.replace("or (n=='tests/configuration/native_large_commands.py' and action!='large')", "or (n=='tests/editor/native_arrange.py' and action!='arrange')")
s=s.replace("assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and action!='arrange')","assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and action!='arrange') or (n=='tests/editor/native_editor.py' and action not in ('native','arrange','large'))")
s=s.replace("if family in ('LARGE-COMMANDS','EDITOR-FORM'):","if family in ('EDITOR-ARRANGE','LARGE-COMMANDS','EDITOR-FORM'):")
s=s.replace("else 'tests/editor/native-cases.json',detail['fixture_sha256'])", "else 'tests/editor/arrange-cases.json' if family=='EDITOR-ARRANGE' else 'tests/editor/native-cases.json',detail['fixture_sha256'])")
s=s.replace("check('tests/editor/native_editor.py',detail['oracle_sha256'])", "check('tests/editor/native_arrange.py' if family=='EDITOR-ARRANGE' else 'tests/editor/native_editor.py',detail['oracle_sha256'])\n                if family=='EDITOR-ARRANGE':check('tests/editor/native_editor.py',detail['harness_sha256'])")
s=s.replace('Staged complete-scene commands','Staged shared and native arrangement')
(r/'out/campaign/stage_arrange.py').write_text(s,encoding='utf-8',newline='\n')
print('Prepared bounded source/evidence preservation and staged identity checks.')
