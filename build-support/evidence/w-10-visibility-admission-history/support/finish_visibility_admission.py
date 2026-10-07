from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-visibility-admission-';hp=e/'visibility-admission-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
checks=[dict(name='Versioned schemas, protected draft/history, resource/preset admission, negotiation and replay',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Full non-native suites: 325 Linux, 322 Windows GCC15, 319 v141_xp',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Nine native visibility durability scenarios and ten native regression families',outcome='pass',evidence='build-support/evidence/'+prefix+'native-index.json'),
 dict(name='Specification, fixtures, tooling and integrity',outcome='pass',evidence='build-support/evidence/'+prefix+'verification.json'),
 dict(name='Staged source/oracle/artifact identities',outcome='not_run',evidence='build-support/evidence/'+prefix+'staging.json'),
 dict(name='Native conditional rendering, private editor controls and external feature qualification',outcome='not_run',evidence=None),
 dict(name='Complete five editions and release qualification',outcome='not_run',evidence=None)]
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=index['source_base'],objective='Admit authored visibility through versioned scene/command contracts, protected typed edits, coherent resources and durable recovery while preserving the native rendering gate.',changed_files=[],decisions=[
 'Append scene 0.5 and command 0.7 without rewriting existing schemas or fixture bytes.',
 'Require explicit capability dependencies and current policy for typed visibility edits, including Clear/no-op and history travel.',
 'Preserve rule/version/selection/history exactly; never silently discard a conditional parent during Ungroup/Unwrap.',
 'Keep original request bytes and existing publication/reconciliation owners; durable storage does not imply activation.',
 'Refuse unsupported scene 0.5 rendering even for a disabled display; policy denial retains priority.',
 'Preserve configure and test-harness failures, unchanged frozen expectations and the fixed workspace maximum.'],checks=checks,
 open_questions=['Legacy OS/service-level and architecture floors and designated Windows/historical/Mac laboratories remain unresolved.'],
 next_step='Freeze native visibility composition/dialog examples and implement condition inheritance, retained layout space, unresolved diagnostics, mandatory status, pixels/accessibility and revocation erasure. Continue independent installed-ownership and complete-edition tracks.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Shared typed drafts and stored rules do not enable native conditional widgets or a visibility dialog.',
 'Owned ext4 process-interruption evidence does not establish hardware power-loss or other filesystem/OS qualification.',
 'Historical-toolset execution on contemporary Windows does not qualify XP or other historical targets.',
 'Historical accessibility timeout causes remain unexplained; all five complete editions remain open.',
 'Two existing Windows symlink tooling assertions remain skipped.'])
paths=set(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/visibility-admission-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Prepared reviewable handoff for',len(paths),'changed files.')
