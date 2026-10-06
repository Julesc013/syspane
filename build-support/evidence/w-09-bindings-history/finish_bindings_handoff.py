from pathlib import Path
import hashlib,json,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-bindings-';hp='build-support/evidence/bindings-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_runs'])==3
h=json.loads((r/'build-support/evidence/layout-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Project authored selector and pin bindings over scoped, current-policy DataViews with exact comparison and bounded results.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Retain binding 0.1 and scene 0.2 identities; add the resolver to the existing scene component and use the existing compiled authored validator.',
 'Require a trusted complete routing catalog, explicit scope and persistent mappings; preserve exact producer/epoch/entity identity and never infer replacement hardware from a name or index.',
 'Check every relevant view permission before payload/support; no partial collections or operational values on denial, unknown selection or capacity.',
 'Nest distinct DataView borrows until the synchronous sink returns; no retained data/model pointers, acquisition, or reentry.',
 'Compare uint64 and binary64 by value without integer-to-double loss. Preserve typed null/zero, observation status, source identity, safe error code and qualified measurement freshness.',
 'Use a bounded heap, per-producer field index and explicit work/output/index admission budgets. Keep unavailable sort keys last and scoped identity as final tie break.',
 'Archive thirteen initial test families before implementation. Correct fixture grants/schema/formatting; preserve failed attempts. Honor existing wire duplicate-field rejection and verify the original ambiguous outcome through the typed retained path.',
 'Add restart/clock, signed real ordering, maximum collection and maximal Unicode descriptor cases. No expected output was changed to match resolver behavior.',
 'Record external GLib/glibc system update; explicitly revise installed development identities without installing or changing any packages.',
 'Preserve a native CONTENT-COMMANDS timeout after confirmed worker replacement, with its complete synthetic failure tree. The unchanged isolated oracle passed; cause remains undetermined. No deadline or acceptance assertion was relaxed.',
 'Preserve the failed 5 GiB workspace preflight and record the measured 6 GiB reversible development allocation; product limits/reservations unchanged.',
 'Keep W-09 and all complete release tracks open; native routing/measurement/drawing/cache ownership and actual visible activation remain required.'],
 checks=[
 {'name':'Original workspace reservation, Linux dependency mismatch, test compilation and fixture admission failures','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Preserved native CONTENT-COMMANDS receive timeout; unchanged isolated retry passed','outcome':'fail','evidence':prefix+'history/bindings-content-timeout-review.json'},
 {'name':'Full suites: 220 Linux, 202 contemporary Windows, 189 historical-toolset checks on modern Windows','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Seventeen binding families including measured wire admission and retained typed multi-source ambiguity','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Eighteen historical executable/header/import and actual linker-input audits','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Specification/schema/navigation/integrity and 56 passing tooling tests, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Exact staged input, archived original oracles and final test executable identities','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Native general scene routing, font measurement, drawing, editing, cache erasure and visible activation','outcome':'not_run','evidence':None},
 {'name':'Historical native OS execution and all complete platform releases','outcome':'not_run','evidence':None}],
 next_step='Connect immutable authored scene/resource generations, general bindings and shared geometry to native measurement/drawing; implement complete trusted routing and pin ownership plus retained native cache erasure, then editor/settings and visible activation/recovery. Continue all five release tracks.',
 limitations=['Synchronous component projection only; trusted routing completeness and explicit mapping provenance are caller obligations that native integration must implement.',
 'No new native scene visibility, text shaping, raster, accessibility or behind-icons qualification.',
 'Historical-toolset execution and artifact audits occur on the modern Windows host, not historical operating systems.',
 'Installed ownership/policy, media decoding, native editor/settings, lifecycle/packages and unresolved native labs remain open.',
 'One native content-command response exceeded the unchanged 1-second oracle timeout during regression; cause is undetermined and later passes do not erase this failure.',
 'Two existing Windows symlink tooling assertions remain skipped. No privileged or user desktop/VM operation and no public release occurred.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h);print('Bindings handoff validated; workspace inspection passed.')
