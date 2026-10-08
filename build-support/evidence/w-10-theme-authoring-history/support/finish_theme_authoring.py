from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-theme-authoring-';hp=e/'theme-authoring-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=index['source_bases'][-1],objective='Implement shared lossless theme input and immutable authored theme artifacts for the durable/native authoring boundary.',changed_files=[],decisions=[
 'Preserve exact no-op documents, explicit role membership and source packages.',
 'Validate complete font input with existing numeric/theme rules and locale-independent hydration.',
 'Construct immutable artifacts without I/O, catalog mutation or publication claims.',
 'Bind identity to both edited content and exact preserved source license.',
 'Preserve the original theme-only seed contract/examples and preliminary executions.',
 'Keep durable override, command/store, draft/history and native control integration required.'],checks=[check('Input/no-op/negative/artifact families and exact independent bytes','attempts'),check('Full portable suites: 343 Linux, 340 Windows GCC15, 337 v141_xp','attempts'),check('Native theme and semantic typography regressions','native-index'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identity','staging','not_run'),check('Durable theme override and command/store integration',None,'not_run'),check('Native theme controls and trusted editor admission',None,'not_run'),check('Five complete editions and release qualification',None,'not_run')],
 open_questions=['Historical target floors and Mac laboratories remain unresolved.','Historical accessibility timeout causes remain unexplained.'],
 next_step='Close versioned exact theme resource override, command/store publication and restart/reconciliation. Preserve the base preset/image closure and bound repeated edits to one override. Then connect atomic draft/resource history and native font controls with independent preview, save/reopen and private-buffer erasure evidence before trusted EditorForm admission.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Pure input/artifact helpers do not save edits, mutate draft history or enable native theme controls.','Existing command/generation versions cannot carry this new authored artifact boundary.','Native font checks cover the pinned Linux development adapter only.','Historical compiler execution on contemporary Windows does not qualify XP.','Two existing Windows symlink tooling assertions remain skipped.','Installed ownership, full editions and release qualification remain open.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/theme-authoring-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h);print('Prepared handoff for',len(paths),'files.')
