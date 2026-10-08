from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-native-visibility-';hp=e/'native-visibility-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
checks=[dict(name='Native all-kind visibility, groups, diagnostics, geometry, policy and retained work',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Independent owned-X11 pixels and explicit AT-SPI replies with inverted and retained-content fault controls',outcome='pass',evidence='build-support/evidence/'+prefix+'native-index.json'),
 dict(name='Full non-native suites: 331 Linux, 328 Windows GCC15, 325 v141_xp',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Fifteen native rendering regressions and editor lock/container integrations',outcome='pass',evidence='build-support/evidence/'+prefix+'attempts.json'),
 dict(name='Specification, fixtures, tooling and integrity',outcome='pass',evidence='build-support/evidence/'+prefix+'verification.json'),
 dict(name='Staged source/oracle/artifact identities',outcome='not_run',evidence='build-support/evidence/'+prefix+'staging.json'),
 dict(name='Native rule controls and ordinary editor/installed enablement',outcome='not_run',evidence=None),
 dict(name='Complete five editions and release qualification',outcome='not_run',evidence=None)]
h=dict(schema_version='0.1.0',work_id='W-09',source_ref=index['source_base'],objective='Implement and independently observe native conditional presentation under an explicit development opt-in.',changed_files=[],decisions=[
 'Keep layout from unconditioned authorized content and consume the existing borrowed hierarchy without a second cache.',
 'Erase hidden payloads and promote diagnostic descendants through hidden inspector groups.',
 'Preserve unresolved and mandatory status within existing leaf bounds; report an alternative for overflow or warning overlap.',
 'Retain authorized chart/image work while hidden and erase it on policy revocation.',
 'Paint warnings after ordinary content and independently compare exact native pixels and accessible names.',
 'Keep ordinary scene 0.5 refusal until native controls, selection/gestures and durable recovery integration pass.',
 'Preserve frozen contract/example bytes and failed attempts; correct only test geometry/source-state assumptions and harness import setup.'],checks=checks,
 open_questions=['Legacy OS/service-level and architecture floors and designated Windows/historical/Mac laboratories remain unresolved.'],
 next_step='Close the native visibility-controls work package, then implement private rule input, authored-list selection, held gestures, save/reopen, lost acknowledgement and restart before enabling ordinary conditional editing. Continue independent installed-ownership and complete-edition tracks.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Native rendering is enabled only by explicit trusted development configuration; authored capabilities alone do not enable it.',
 'Owned X11 synthetic component evidence does not establish installed desktop, Wayland, Windows or Mac visibility support.',
 'Historical-toolset execution on contemporary Windows does not qualify XP or other historical targets.',
 'Historical accessibility timeout causes remain unexplained; all five complete editions remain open.',
 'Two existing Windows symlink tooling assertions remain skipped.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/native-visibility-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Prepared reviewable handoff for',len(paths),'changed files.')
