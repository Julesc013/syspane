from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'build-support'))
import check_legacy_artifacts as audit
audit.EXECUTABLES += ('syspane_demand_tests.exe','syspane_demand_session_tests.exe','syspane_authored_tests.exe')
b=r/'out/build/windows-x86-v141-xp'
assert b.resolve().is_relative_to((r/'out/build').resolve())
assert json.loads((b/'.syspane-owner.json').read_text())['profile']=='windows-x86-v141-xp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v={'outcome':'pass','profile':'windows-x86-v141-xp','artifacts':{},'build_inputs':audit.build_inputs(b),
 'verification_inputs':{n:sha(r/n) for n in ('build-support/check_legacy_artifacts.py','build-support/targets/windows-x86-v141-xp.imports.json')},
 'helper_sha256':sha(Path(__file__)),
 'qualification':'PE/header/declared mandatory import closure and pinned actual linker inputs. Execution was on the modern Windows host; no XP, Windows 9x or old NT runtime qualification.'}
for name in audit.EXECUTABLES:
 p=b/'Release'/name;v['artifacts'][name]={'sha256':sha(p),'bytes':p.stat().st_size,**audit.verify(p.read_bytes())}
(r/'out/campaign/authored-legacy-audit.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Historical audit passed for',len(v['artifacts']),'executables; no historical runtime claim.')
