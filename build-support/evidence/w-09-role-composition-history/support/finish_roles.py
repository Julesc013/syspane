from pathlib import Path
import json,subprocess,jsonschema
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-role-composition-';hp=e/'role-composition-handoff.json';sp=e/(prefix+'staging.json')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not sp.exists():write(sp,dict(outcome='not_run'))
index=json.loads((e/(prefix+'attempts.json')).read_bytes());verification=json.loads((e/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in verification['checks'])
def check(name,suffix,outcome='pass'):return dict(name=name,outcome=outcome,evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)
h=dict(schema_version='0.1.0',work_id='W-09',source_ref=index['source_bases'][-1],objective='Implement bounded role-aware development scene composition with mandatory diagnostics and legacy preservation.',changed_files=[],decisions=[
 'Assign roles at semantic construction; never infer them by parsing user text.',
 'Keep legacy native rendering and authored/pinned identities unchanged.',
 'Count owned block text and simultaneous raster buffers within existing bounds.',
 'Preserve whole-frame erasure and unsuppressed diagnostic rendering.',
 'Require explicit trusted development admission plus current resource capability and policy.',
 'Preserve two failed new expectations and their contract-derived corrections.',
 'Prove the two post-test CRLF-to-LF canonicalizations against exact archived tested inputs.'],checks=[check('Semantic roles, literal-font pixels, table geometry and diagnostic erasure','native-index'),check('Full portable suites: 339 Linux, 336 Windows GCC15, 333 v141_xp','attempts'),check('Six native font/visibility checks, three editor matrices and fifteen rendering regressions','attempts'),check('Specification, fixtures, tooling and integrity','verification'),check('Staged source/oracle/artifact identities and line-ending equivalence','staging','not_run'),check('Native theme-authoring controls and trusted editor integration',None,'not_run'),check('Five complete editions and release qualification',None,'not_run')],
 open_questions=['Historical OS floors and Mac laboratories remain unresolved.','Historical accessibility timeout causes remain unexplained.'],
 next_step='Specify and implement native font/theme authoring through existing private input, immutable resource publication and durable draft/transaction owners. Verify roles, reset, preview, undo, Apply/recovery and erasure before enabling trusted EditorForm typography. Continue clipboard/recovery drafts, installed ownership and all five native editions.',
 authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 release objective','User instruction to commit and sync main'],
 limitations=['Theme 0.2 requires explicit experimental_typography; ordinary native editor authoring remains pending.','Native composition evidence covers the pinned Linux development adapter only.','Historical compiler execution on contemporary Windows does not qualify XP.','Two existing Windows symlink tooling assertions remain skipped.','Full editions, installed ownership and release qualification remain open.'])
paths=set(subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())|{'build-support/evidence/role-composition-handoff.json'}
h['changed_files']=sorted(paths);jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h);print('Prepared handoff for',len(paths),'files.')
