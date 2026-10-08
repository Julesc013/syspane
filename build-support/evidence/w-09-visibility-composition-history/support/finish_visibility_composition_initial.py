from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-visibility-composition-';hp=e/'visibility-composition-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
checks=[dict(name='Bounded batch reads, borrowed hierarchy, limits, policy and callback lifetime',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Full non-native suites: 331 Linux, 328 Windows GCC15, 325 v141_xp',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Five native regression families; 26 archived scenarios',outcome='pass',evidence='build-support/evidence/'+prefix+'native-index.json'),
 dict(name='Specification, fixtures, tooling and integrity',outcome='pass',evidence='build-support/evidence/'+prefix+'verification.json'),
 dict(name='Staged source/oracle/artifact identities',outcome='not_run',evidence='build-support/evidence/'+prefix+'staging.json'),
 dict(name='Native conditional rendering, private editor controls and external feature qualification',outcome='not_run',evidence=None),
 dict(name='Complete five editions and release qualification',outcome='not_run',evidence=None)]
h=dict(schema_version='0.1.0',work_id='W-09',source_ref=index['source_base'],objective='Compose bounded visibility decisions through shared protected telemetry reads while keeping native presentation gated.',changed_files=[],decisions=[
 'Borrow each usable routed DataView once for an ordered batch of up to 512 queries.',
 'Bound aggregate work and output and erase partial results on capacity failure.',
 'Evaluate all own conditions in authored preorder; preserve unresolved diagnostics beneath hidden ancestors.',
 'Restrict the whole condition projection on denial, with no retained operational decision.',
 'Preserve the native refusal gate until layout/status/pixel/accessibility and private controls are verified.',
 'Preserve failed attempts and the original fixture; correct only schema-required empty group content and the test depth assumption.'],checks=checks,
 open_questions=['Legacy OS/service-level and architecture floors and designated Windows/historical/Mac laboratories remain unresolved.'],
 next_step='Freeze native visibility composition/dialog examples and implement condition inheritance, retained layout space, unresolved diagnostics, mandatory status, pixels/accessibility and revocation erasure. Continue independent installed-ownership and complete-edition tracks.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Borrowed shared decisions do not enable native conditional pixels, accessibility or private editor controls.',
 'Native regression evidence does not qualify unimplemented conditional presentation.',
 'Historical-toolset execution on contemporary Windows does not qualify XP or other historical targets.',
 'Historical accessibility timeout causes remain unexplained; all five complete editions remain open.',
 'Two existing Windows symlink tooling assertions remain skipped.'])
paths=set(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/visibility-composition-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Prepared reviewable handoff for',len(paths),'changed files.')
