from pathlib import Path
import re
r=Path.cwd();src=r/'build-support/evidence/w-10-containers-history';out=r/'out/campaign';base='83da967d8a7311b8124c3beae304af103730eccd'
def read(n):return (src/n).read_text().replace('w-10-containers','w-10-edit-locks').replace('faba4663be62ff4790ea31b540d03c9f10bc2ce2',base).replace('containers-handoff.json','edit-locks-handoff.json')
def save(n,s):(out/n).write_text(s,encoding='utf-8',newline='\n')
s=read('archive_containers.py').replace("('EDITOR-CONTAINERS'","('EDITOR-LOCKS','EDITOR-CONTAINERS'");save('archive_edit_locks.py',s)
s=read('preserve_containers.py').replace('138','146').replace('container-execution-','locks-execution-')
helpers=['prepare_edit_locks.py','implement_lock_versions.py','resume_lock_versions.py','implement_native_locks.py','register_edit_locks.py','complete_lock_native_fixture.py','setup_lock_runs.py','prepare_locks_prune.py','prune_locks_attempts.ps1','locks-prune-plan.json','locks-pruned-attempts.json','prune_locks_duplicates.py','locks-pruned-duplicates.json','prepare_locks_more_cleanup.py','prune_locks_more_duplicates.py','fix_lock_schema_identity.py','correct_lock_numeric_oracle.py','document_edit_locks.py','add_locks_portable.py','locks_step.py','locks_flow.py','setup_edit_locks_evidence.py','archive_edit_locks.py','preserve_edit_locks.py','finish_edit_locks_checks.py','finish_edit_locks.py','stage_edit_locks.py']
s=re.sub(r'^helpers=.+$', 'helpers='+repr(helpers),s,flags=re.M)
s=s.replace("('fixed-inputs.json','fixed-inputs.zip','preview-inputs.json','preview-inputs.zip','oracle-correction.json','composite-calibration.json')","('fixed-inputs.json','fixed-inputs.zip','oracle-correction.json','schema-identity-failure.json','specctl-before-identity.py')")
a=s.index("preview=json.loads((history/");b=s.index('def latest(profile,action):',a);s=s[:a]+s[b:]
s=s.replace("preview_originals=dict(record=ref(history/'preview-inputs.json'),archive=ref(history/'preview-inputs.zip')),",'')
s=s.replace("[ref(history/'oracle-correction.json'),ref(history/'composite-calibration.json')]","[ref(history/'oracle-correction.json')]")
s=s.replace("for action in ('containers'","for action in ('locks','containers'")
s=s.replace("families={'EDITOR-CONTAINERS'","families={'EDITOR-LOCKS':('syspane_editor_window','tests/editor/native_edit_locks.py',7),'EDITOR-CONTAINERS'")
s=s.replace("if family=='EDITOR-CONTAINERS':assert", "if family=='EDITOR-LOCKS':assert v['fixture_sha256']==sha(r/'tests/editor/edit-lock-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='EDITOR-CONTAINERS':assert")
s=s.replace('final={};regressions={};artifacts={};graphs={}','final={};regressions={};artifacts={};graphs={};portable={}')
s=s.replace("row,v=latest(profile,'test');build,b=latest(profile,'build')","row,v=latest(profile,'test');build,b=latest(profile,'build')\n    pr,pv=latest(profile,'portable');assert not pv['exit'] and not pv['source_changed_during_execution'];compatible(pv);portable[profile]=dict(record={k:pr[k] for k in ('path','sha256')},log=pr['ctest_log'],cases=re.findall(r'Test\\s+#\\d+:\\s+(\\S+)\\s+\\.+\\s+Passed',pv['stdout']))\n    assert portable[profile]['cases'] and len(portable[profile]['cases'])==len(set(portable[profile]['cases']))")
s=s.replace('final_runs=final,regressions=regressions','final_runs=final,portable_runs=portable,regressions=regressions')
s=s.replace('native containers, layout','native edit locks, containers, layout')
save('preserve_edit_locks.py',s)
s=read('finish_containers_checks.py');save('finish_edit_locks_checks.py',s)
s=read('finish_containers.py').replace('138','146').replace('173','180').replace('eleven matrices','twelve matrices')
s=s.replace("'tests/configuration/settings_content_fixture.py')","'tests/configuration/settings_content_fixture.py','build-support/generate_authored_schemas.py')")
a=s.index('h.update(');s=s[:a]+'''h.update(source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),objective='Implement persistent own/inherited editor locks with negotiated scenes, native guards and durable recovery',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=['Freeze package, new schemas and full expected scenes before implementation; retain all old schemas.', 'Keep edit guards distinct from policy and live layout; explicit unlock and history remain available.', 'Require scene/content/edit-lock and command 0.6 negotiation through existing resource and transaction owners.', 'Preserve initial build/schema failures and numeric-label oracle correction without changing frozen expectations.', 'Retain the fixed workspace bound and all five release tracks.'],
 checks=[{'name':'146 affected checks on each of three toolchains','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'}, {'name':'All non-native CTest suites on three toolchains','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'}, {'name':'180 native cases across twelve matrices','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'}, {'name':'Schema, fixture, tooling and integrity checks','outcome':'not_run' if pending else 'pass','evidence':prefix+'verification.json'}, {'name':'Staged source/oracle/artifact/evidence identities','outcome':'not_run','evidence':prefix+'staging.json'}, {'name':'Complete native editions and historical/release qualification','outcome':'not_run','evidence':None}],
 next_step='Continue conditional visibility, typography, clipboard authority, recovery drafts and installed controller/catalog/policy ownership; retain all five complete-edition gates.',
 limitations=['Owned Linux ext4/Xvfb/DBus evidence does not qualify installed editing, historical platforms or physical power-loss durability.', 'Locks guard ordinary editor operations, not authorization, disclosure or dynamic layout.', 'Conditional visibility, typography, clipboard/recovery drafts, installed ownership and complete accessibility/performance remain required.', 'Windows builds run on contemporary Windows; two existing tooling symlink assertions remain skipped.', 'Earlier unrelated focus/interface causes and historical laboratory/release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and sealed handoff.')
'''
save('finish_edit_locks.py',s)
s=read('stage_containers.py').replace('container-staging-paths.txt','locks-staging-paths.txt')
a=s.index("preview=index['preview_originals']");b=s.index("native=json.loads(content(index['native_index']['path']));refs(native)",a);s=s[:a]+s[b:]
a=s.index("calibration=json.loads(");b=s.index('for row in native:',a);s=s[:a]+s[b:]
s=s.replace("for action,row in index['regressions'].items():", "for profile,row in index['portable_runs'].items():executed(row['record'],profile,'portable')\nfor action,row in index['regressions'].items():")
s=s.replace("if family=='EDITOR-CONTAINERS':check('tests/editor/container-cases.json',report['fixture_sha256'])", "if family=='EDITOR-LOCKS':check('tests/editor/edit-lock-cases.json',report['fixture_sha256'])\n    if family=='EDITOR-CONTAINERS':check('tests/editor/container-cases.json',report['fixture_sha256'])")
s=s.replace("('EDITOR-CONTAINERS','EDITOR-LAYOUT'","('EDITOR-LOCKS','EDITOR-CONTAINERS','EDITOR-LAYOUT'")
s=s.replace("if family=='EDITOR-CONTAINERS':check('tests/editor/native_layout_authoring.py'", "if family=='EDITOR-LOCKS':check('tests/editor/native_layout_authoring.py',detail['layout_helper_sha256'])\n                if family=='EDITOR-CONTAINERS':check('tests/editor/native_layout_authoring.py'")
s=s.replace("check('tests/editor/container-cases.json' if family", "check('tests/editor/edit-lock-cases.json' if family=='EDITOR-LOCKS' else 'tests/editor/container-cases.json' if family")
s=s.replace("check('tests/editor/native_containers.py' if family", "check('tests/editor/native_edit_locks.py' if family=='EDITOR-LOCKS' else 'tests/editor/native_containers.py' if family")
s=s.replace("('wrong-container','retain-container'","('wrong-lock','wrong-container','retain-container'")
s=s.replace('Staged shared and native reflowing container authoring','Staged shared and native persistent edit-lock authoring')
save('stage_edit_locks.py',s)
