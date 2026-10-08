from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-08-theme-commands-';hp=e/'theme-commands-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
h=dict(schema_version='0.1.0',work_id='W-08',source_ref=index['source_base'],objective='Implement negotiated source-bound authored theme commands and exact Linux durable publication/recovery.',changed_files=[],
 decisions=['Use command 0.8 with exact resource selection 0.2 and current theme pin; carry only complete base/role font intent.',
 'Construct and validate canonical artifacts on the existing transaction worker without imports; retain original base/image closure and one override.',
 'Require explicit feature dependencies and current policy at admission, publication, result retrieval and reconciliation.',
 'Write Linux manifest 0.4/resource index 0.2; bind exact request bytes and fulfilled font intent without changing old formats or limits.',
 'Preserve fixed expectations, all failed attempts and source/artifact identities.'],
 checks=[check('Five portable theme-command families; 175 affected tests per profile','attempts'),check('Full portable suites: 352 Linux, 349 Windows GCC15, 346 v141_xp','attempts'),check('25 independent theme-command scenarios and five native regression families','native-index'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identity','staging','not_run'),check('Atomic editor resource history and native theme controls',None,'not_run'),check('Five complete editions and release qualification',None,'not_run')],
 open_questions=['Historical target floors and Mac laboratories remain unresolved.','Historical accessibility timeout causes remain unexplained.'],
 next_step='Carry resources atomically through editor base/draft/history, Apply/cancel/unknown-result reconciliation and reload with bounded retained resource storage. Then complete native base/role font controls, independent preview/save/reopen/accessibility and private-buffer erasure before trusted EditorForm typography admission.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Native durable theme qualification is scoped to the owned Linux ext4/IPC laboratory.','Atomic editor resource history and native font controls remain unimplemented.','Historical toolset execution on contemporary Windows does not qualify XP.','Two existing Windows symlink tooling assertions remain skipped.','Installed ownership, full editions and release qualification remain open.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/theme-commands-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h);print('Prepared handoff for',len(paths),'files.')
