from pathlib import Path
import hashlib,json,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-text-';hp='build-support/evidence/text-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_runs'])==3
h=json.loads((r/'build-support/evidence/bindings-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Measure and rasterize bounded native Linux text with exact pixel ownership, explicit font fallback, wrapping and semantic/contrast colors.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Preserve scene/theme identities and full release ambition; add a Linux-only native text component to the existing component inventory.',
 'Measure plain UTF-8 with explicit language, absolute DIP font size, native ink/logical bounds and actual font families. Preserve nonzero origins and measure separately from rational raster scale.',
 'Reject malformed encoding, controls and text/raster capacity rather than truncating or silently clipping. Return explicit premultiplied RGBA8 bytes owned by the caller.',
 'Use an alpha glyph coverage mask so embedded color-font layers cannot bypass semantic or contrast colors.',
 'Archive 25 original independent test families before implementation. Add two cases for native malformed UTF-8 and color-font behavior; preserve the failing color-font raster and unchanged assertion.',
 'Pin selected installed text libraries/packages plus 358 font/configuration/library files. No dependencies were installed or redistributed.',
 'Restrict initial use to public/authored or synthetic text until a current-policy native cache/accessibility owner is implemented.',
 'Keep W-09 and every full release track open; native text raster alone is not complete scene rendering or visible host activation.'],
 checks=[
 {'name':'Original embedded color-font foreground bypass; preserved and corrected without relaxing the assertion','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Full suites: 221 Linux, 202 modern Windows, 189 historical-toolset checks on the modern host','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'27 native text input/pixel families and selected installed library/font identity','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'18 historical executable/header/import and actual linker-input audits','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Specification/schema/navigation/integrity and 56 passing tooling assertions, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Exact staged inputs, original oracles, every native raster archive and final artifact identities','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Live widget composition, policy cache/accessibility erasure and independent native host activation','outcome':'not_run','evidence':None},
 {'name':'Windows/Mac text adapters, historical native OS execution and all complete editions','outcome':'not_run','evidence':None}],
 next_step='Close missing primitive content semantics and compose immutable scene/resources, live bindings and shared geometry with native metrics; implement retained text/pixel/accessibility erasure ownership and externally verified native activation/editor integration. Continue Windows/Mac text adapters and all five full release tracks.',
 limitations=['Linux offscreen raster only. No new desktop visibility, behind-icons or accessibility qualification.',
 'Native font caches belong to the external dependency; application cache erasure/live payload retention is not admitted by this adapter.',
 'Selected runtime/font identities do not prove complete transitive reproduction, portable glyph equality or font redistribution rights.',
 'Historical-toolset tests run on the modern Windows host, not historical operating systems.',
 'The earlier binding checkpoint content-command receive timeout remains undetermined and preserved; later full passes do not erase it.',
 'Two existing Windows symlink tool assertions remain skipped. Full product implementation, installed ownership/policy, native labs and release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Native text handoff validated; workspace inspection passed.')
