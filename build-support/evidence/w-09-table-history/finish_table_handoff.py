from pathlib import Path
import hashlib,json,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-table-';hp='build-support/evidence/table-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_run']['cases'])==225
h=json.loads((r/'build-support/evidence/surface-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Render collection tables with scoped row identity, explicit incomplete/truncated states and bounded native cell geometry under the existing policy-erasing owner.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Keep existing scene/binding identities. Ordered selectors differing only in field define columns; never infer a join from names or arrival order.',
 'Retain typed producer/epoch/entity keys, snapshot generation and relative cell rectangles inside the synchronous policy-owned frame.',
 'Show selected/total counts and mandatory cell state; suppress partial rows when any column is incomplete. Whole-scene alternatives preserve unsupported/capacity outcomes.',
 'Measure every cell/header, use explicitly scaled grid gaps, compose one background and preserve all existing frame/text/pixel budgets.',
 'Archive fourteen original component families and independent grid expectations before implementation. Add rational-scale and cell-budget cases; retain all twenty-two scalar families.',
 'Preserve the original table failure and two observer timeouts from the application-cache experiment. Remove optional cache-mask changes, retain explicit fresh reads and acknowledgement-based deadlines.',
 'Use independent owned Xvfb/AT-SPI checks for both scalar and table scenes, with deliberate pixel and accessible-name retention controls.',
 'Verify and archive the original failed synthetic capture before releasing 149760000 redundant raw native-cache bytes; preserve every captured byte and hash in the retained archive.',
 'Keep Linux implementation and Windows configure evidence distinct. Installed ownership, complete native accessibility, remaining primitives and all full editions remain open.'],
 checks=[
 {'name':'Original table failure and observer cache-mode timeouts preserved before correction','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'225 complete Linux regression tests against final source inputs','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'16 table and 22 scalar component families; two independent native experiments with three modes each','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'All three development configure/inventory checks; Windows runtime suites not rerun','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Specification/schema/navigation/integrity and 56 passing tooling assertions, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Exact staged final inputs, original oracles, attempt/native archives and artifact identities','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Complete widget content, installed ownership, native accessible table navigation, desktop/editor integration and full editions','outcome':'not_run','evidence':None}],
 next_step='Close chart/image and richer formatting contracts; connect typed scene rows to native accessible table navigation and stable editing. Integrate authenticated producer discovery, persistent configuration, native controls and independent desktop supervision while continuing all five release tracks.',
 limitations=[
 'Finite synthetic GTK/X11 table and scalar window experiments. No behind-icons placement, installed ownership or native accessibility table-interface qualification.',
 'Historical and other-platform runtime results remain historical; this checkpoint runs Windows configure/inventory checks only.',
 'Observer cache-mode timeouts remain preserved failures; removing that optional setting restored passing checks without extending observation limits.',
 'Selected runtime/font identities do not prove complete transitive reproduction, portable glyph equality or font redistribution rights.',
 'The earlier content-command receive timeout remains undetermined and preserved; later passes do not erase it.',
 'Two existing Windows symlink tool assertions remain skipped. Historical/Mac labs, full product implementation and release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Collection table handoff validated; workspace inspection passed.')
