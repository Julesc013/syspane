from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-theme-history-';hp=e/'theme-history-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=index['source_base'],objective='Connect immutable theme resources to bounded atomic editor history and durable Apply/reconcile/reload.',changed_files=[],
 decisions=['Retain scene, selection and matching resource snapshots together in existing history.',
 'Share internally owned validated package allocations; new package bytes enter by value and receive ordinary validation.',
 'Charge unique additional resource metadata and package bytes within the existing 64-entry/8-MiB history limits.',
 'Generate final command 0.8 from the accepted source and explicitly admitted context; reject unrepresentable edits atomically.',
 'Recheck binding/current policy, freeze pending state and erase private resource history on authority loss; preserve original failures.'],
 checks=[check('Eight theme-history families; 183 affected tests per profile','attempts'),check('Full portable suites: 360 Linux, 357 Windows GCC15, 354 v141_xp','attempts'),check('Independent editor/store save/reopen/reconciliation and five native regression families','native-index'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identity','staging','not_run'),check('Native base/role font controls and trusted editor rendering admission',None,'not_run'),check('Five complete editions and release qualification',None,'not_run')],
 open_questions=['Historical target floors and Mac laboratories remain unresolved.','Historical accessibility timeout causes remain unexplained.'],
 next_step='Implement native base/role font controls and matching borrowed-resource preview through the existing shared draft. Prove independent pixels/accessibility/save/reopen/lost-result/private-erasure behavior before trusted EditorForm typography admission.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['New native experiment exercises shared draft commands and owned Linux ext4 storage, not font-control UI.','Native font controls and trusted typography rendering remain required.','Historical toolset execution on contemporary Windows does not qualify XP.','Two existing Windows symlink tooling assertions remain skipped.','Installed ownership, full editions and release qualification remain open.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/theme-history-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h);print('Prepared handoff for',len(paths),'files.')
