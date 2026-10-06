from pathlib import Path
import hashlib,json,subprocess
import jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-layout-';hp='build-support/evidence/layout-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_runs'])==3
h=json.loads((r/'build-support/evidence/content-resolution-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Resolve all admitted scene layouts into deterministic readable geometry using explicit topology and native metric inputs.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Keep scene 0.2/layout 0.1 identities and all admitted kinds. Add one shared source/scene component and dedicated test target to the existing component graph.',
 'Use explicit display identities, role candidates and fallback, with exact maximum safe rectangles after work areas/insets/exclusions. Reject cross-display hierarchy without rewriting authored ownership.',
 'Select breakpoints against display safe width before allocation; use bounded native minimum/preferred metric inputs and integer 1/64 DIP geometry.',
 'Define stack/grid/canvas/fixed/flow placement, priority-aware fair shrinking and readable minima. Preserve clipped content and require an alternative presentation instead of inventing visibility.',
 'Convert clipped edges to device pixels through explicit rational scale and pixel origin, preserving negative origins and sub-DIP coverage.',
 'Keep resolution pure and bounded, with deterministic diagnostics and enumeration-invariant output. Font lookup, bindings, native drawing and activation remain separate integration requirements.',
 'Record 26 original exact oracles before implementation; preserve their original archive and unchanged final hashes. Add five fixed cases and independent exhaustive/limit checks.',
 'Preserve the initial compiler rejection for three misleadingly indented statements; correct formatting without changing expected geometry.',
 'Preserve the historical configuration preflight stop at the workspace reservation. Reclaim only completed cached attempts whose bytes match unchanged committed evidence; retain the unexpected empty attempt. Resume after the reservation passes.',
 'Keep W-09, W-08 and all five full release tracks open. Shared geometry is a prerequisite for the complete native renderer/editor.'],
 checks=[
 {'name':'Initial warnings-as-errors compiler failure','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Initial historical configuration workspace reservation stop, followed by verified cache reclamation and a passing reservation','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Full suites: 203 Linux, 185 Windows, 172 historical-toolset entries on the modern host','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'33 scene cases per profile, including 31 exact fixtures and 256 independently enumerated obstacle arrangements','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Eighteen historical PE/header/import and actual linker-input audits','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Specification/schema/generation/integrity and 56 passing tooling tests, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Original geometry oracle preservation, staged byte identity, archived attempts and artifact bindings','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Native font measurement/shaping, primitive drawing, direct editing and visible activation','outcome':'not_run','evidence':None},
 {'name':'Historical guest execution and all complete native desktop releases','outcome':'not_run','evidence':None}],
 next_step='Connect native text measurement and drawing to immutable scene/resource generations and this layout plan, with current-policy erasure, live bindings and actual activation/recovery; then integrate native settings/direct editing through common commands. Continue all five release tracks.',
 limitations=['Shared scene geometry and explicit premeasured metric inputs only. No native font, raster, accessibility, behind-icons or visible activation qualification follows.',
 'Clipped nodes and unavailable safe regions require an exposed alternative presentation; a returned plan is not a successful drawing result.',
 'Installed ownership, admitted media decoding, bindings, native editor/settings integration and complete package/lifecycle evidence remain open.',
 'Historical-toolset execution and binary audits on the modern Windows host do not qualify historical Windows behavior. Other native platform laboratories remain unresolved.',
 'Two existing Windows symlink assertions remain skipped. No privileged operation, user desktop/VM operation or public release occurred.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h);print('Layout handoff schema validated; workspace inspection passed.')
