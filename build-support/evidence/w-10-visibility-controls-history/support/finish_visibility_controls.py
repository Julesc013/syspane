from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-visibility-controls-';hp=e/'visibility-controls-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
checks=[check('Exact private visibility input, atomic history and policy admission','attempts'),check('Sixteen independent native control/pixel/storage/erasure/recovery scenarios and positive fault witnesses','native-index'),check('Full non-native suites: 336 Linux, 333 Windows GCC15, 330 v141_xp','attempts'),check('Twelve native editor matrices, fifteen rendering regressions and all-kind visibility','attempts'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identities','staging','not_run'),check('Installed controller/catalog/policy ownership and full native adapters',None,'not_run'),check('Complete five editions and release qualification',None,'not_run')]
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=index['source_bases'][-1],objective='Implement private native visibility editing and trusted EditorForm integration through existing typed and durable owners.',changed_files=[],decisions=[
 'Preserve visibility 0.1, scene 0.5, command 0.7 and existing ownership/history identities.',
 'Use exact authored numeric equality for mixed rules, no-op detection, dirty state and emitted scene replacements; preserve the failing pre-repair examples.',
 'Use exact typed private values and nest the existing binding dialog without early draft mutation.',
 'Distinguish all-absent, equal and mixed own rules; Clear and Keep ignore inactive private buffers.',
 'Keep hidden objects in the authored list and geometry while omitting canvas hits and payloads.',
 'Paint current conditional diagnostics during held scene 0.5 gestures without changing captured geometry.',
 'Rehydrate clean geometry fields after a resolved frame returns; preserve dirty inputs and the deterministic pre-repair selection-order failure.',
 'Enable only trusted EditorForm capability contexts and retain direct SceneSurface default refusal.',
 'Preserve failed compilation/registration attempts and frozen outcomes; use explicit independent native observations.'],checks=checks,
 open_questions=['Legacy OS/service-level and architecture floors and designated Windows/historical/Mac laboratories remain unresolved.','Historical native accessibility timeout causes remain unexplained.'],
 next_step='Close typography and remaining property contracts, clipboard authority and recovery drafts. Continue installed controller/catalog/policy ownership and scene-aligned entry/restoration, independent native adapters and complete-edition qualification.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Owned X11 component evidence does not establish installed desktop, Wayland, Windows or Mac visibility editing.',
 'The new restart fixture reconstructs the owner in the editor process; separate-process interruption is earlier admission evidence. Reopen starts a new editor process.',
 'Historical-toolset execution on contemporary Windows does not qualify XP or other historical targets.',
 'Full accessibility/performance and all five complete editions remain open.',
 'Two existing Windows symlink tooling assertions remain skipped.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/visibility-controls-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Prepared reviewable handoff for',len(paths),'changed files.')
