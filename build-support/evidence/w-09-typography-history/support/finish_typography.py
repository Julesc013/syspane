from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-typography-';hp=e/'typography-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
h=dict(schema_version='0.1.0',work_id='W-09',source_ref=index['source_bases'][-1],objective='Implement versioned theme font roles, current-policy resource admission and bounded native text rendering.',changed_files=[],decisions=[
 'Keep typography in versioned theme documents and preserve every legacy schema/fixture byte.',
 'Return owned complete font values with explicit role fallback; preserve authored family and exact fractional size.',
 'Require theme.typography from resolved theme meaning even when the manifest omitted it.',
 'Use native family/size/weight/style setters and preserve current text, alpha, contrast and resource limits.',
 'Keep scene composition explicitly unavailable until all roles and mandatory diagnostics have independent evidence.',
 'Preserve original failures, initial and revised freezes and the precise schema-refinement sequence.'],checks=[check('Literal font resolution, invalid inputs and resource authority','attempts'),check('Native pixels, font roles and positive ignored-role/weight witnesses','native-index'),check('Full portable suites: 339 Linux, 336 Windows GCC15, 333 v141_xp','attempts'),check('Three native editor matrices and fifteen rendering regressions','attempts'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identities','staging','not_run'),check('Role-aware scene composition and native theme-authoring controls',None,'not_run'),check('Five complete editions and release qualification',None,'not_run')],
 open_questions=['Legacy OS floors and historical/Mac laboratories remain unresolved.','Historical accessibility timeout causes remain unexplained.'],
 next_step='Close role mapping and mandatory diagnostic rendering for every scene primitive, prove native composition, then implement native theme authoring through exact resource publication and existing draft/transaction owners. Continue clipboard/recovery drafts, installed ownership and all five native editions.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Theme 0.2 is deliberately not enabled in SceneSurface until role-aware composition is verified.','Native font editing and immutable theme publication remain required.','Native raster tests qualify the pinned Linux development adapter only.','Historical compiler execution on contemporary Windows does not qualify XP.','Two existing Windows symlink tooling assertions remain skipped.','Full editions, installed ownership and release qualification remain open.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/typography-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h);print('Prepared handoff for',len(paths),'files.')
