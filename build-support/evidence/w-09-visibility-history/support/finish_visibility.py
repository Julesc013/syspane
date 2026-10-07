from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-visibility-';hp=e/'visibility-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes())
assert all(c['exit']==0 for c in verification['checks'])
checks=[dict(name='Fixed comparisons, state/lifecycle/budget/grammar checks and existing bindings',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Full non-native suites: 317 Linux, 314 Windows GCC15, 311 v141_xp',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Fifteen existing native rendering regressions',outcome='pass',evidence='build-support/evidence/'+prefix+'native-index.json'),
 dict(name='Specification, fixtures, tooling and integrity',outcome='pass',evidence='build-support/evidence/'+prefix+'verification.json'),
 dict(name='Staged source/oracle/artifact identities',outcome='not_run',evidence='build-support/evidence/'+prefix+'staging.json'),
 dict(name='Scene/command visibility admission and native feature integration',outcome='not_run',evidence=None),
 dict(name='Complete five editions and release qualification',outcome='not_run',evidence=None)]
h=dict(schema_version='0.1.0',work_id='W-09',source_ref=index['source_base'],objective='Implement the policy-bound conditional-visibility evaluator and preserve exact acceptance before versioned scene/native feature integration.',changed_files=[],decisions=[
 'Use one existing singleton binding and one exact typed comparison; retain the current policy-bound synchronous borrow.',
 'Only shown/hidden represent valid decisions; missing, stale, denied, ambiguous and disconnected inputs remain explicit unresolved states.',
 'Reuse the existing exact numeric comparison without rounding uint64 to double; preserve fixed schema and expected examples.',
 'Keep scene admission, native controls/pixels/accessibility and full editions as required open gates.',
 'Preserve original schema-generator, warning and fixture-construction failures; reclaim only verified committed duplicates within the unchanged workspace maximum.'],checks=checks,
 open_questions=['Legacy OS/service-level and architecture floors and designated Windows/historical/Mac laboratories remain unresolved.'],
 next_step='Admit visibility through a new scene/command capability and coherent resources/persistence, then complete native editor controls and exact group/status/pixel/accessibility/erasure behavior from the visibility package. Continue other independent release tracks.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['This is an executable shared prerequisite; existing scene and command versions do not enable conditional visibility.',
 'Existing native rendering regressions do not test conditional native content.',
 'Historical-toolset execution on contemporary Windows does not qualify XP or other historical targets.',
 'Historical accessibility timeout causes remain unexplained; all five complete editions and full qualification stay open.',
 'Two existing Windows symlink tooling assertions remain skipped.'])
paths=set(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/visibility-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Prepared reviewable handoff for',len(paths),'changed files.')
