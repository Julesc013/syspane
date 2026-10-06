from pathlib import Path
import hashlib,json,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-surface-';hp='build-support/evidence/surface-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_runs'])==3 and index['final_focus']
h=json.loads((r/'build-support/evidence/text-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Compose policy-owned scalar scenes from pinned resources, live DataViews, shared geometry and native text; independently verify native pixel and accessible-name erasure.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Preserve authored scene/theme identities and full release ambition. Add a Linux-only scalar integration capability with explicit whole-scene alternatives for unsupported widgets.',
 'Give one serialized SceneSurface exclusive ownership of its DataViews, policy high-water mark and frame. Mutations clear native caches before new presentation; clear failure permanently closes the owner.',
 'Require both operational desktop and accessibility disclosure, telemetry admission and current resource capabilities. Policy regrant requires new attachment and full state.',
 'Render exact scalar values and explicit acquisition/freshness/lease meaning. Measure bounded native text before shared layout and premultiplied OVER composition.',
 'Preserve the original sixteen independent component families. Their exact-zero-age assertion exposed a shared binding defect, corrected without changing the positive-interval rate contract.',
 'Extend to twenty-two families; preserve the forced-enable failure before fixing mandatory true precedence over authored false.',
 'Observe public synthetic pixels through XGetImage and actual GTK names through AT-SPI on an owned authenticated Xvfb server/private bus. Deliberate retained-pixel and retained-name controls must fail their corresponding erasure observations.',
 'Pin selected installed accessibility and observer dependencies; exclude ephemeral X authorization cookies from retained evidence. No dependencies were installed or redistributed.',
 'Bind all three full suites to archived source inputs. The final delta is confined to the Linux forced-enable branch and its test, followed by passing focused component/native checks.',
 'Keep W-09, installed ownership, complete widgets, native host activation and all full release tracks open.'],
 checks=[
 {'name':'Original zero-age and forced-enable failures; preserved before correction without weakening expectations','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Full suites on archived inputs: 223 Linux, 202 modern Windows, 189 historical-toolset checks on the modern host','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Final Linux-only correction: 22 component families and three independent native erasure modes, including negative controls','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'18 historical executable/header/import and actual linker-input audits','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Specification/schema/navigation/integrity and 56 passing tooling assertions, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Exact staged final inputs, declared full-run deltas, original oracles, every native capture archive and final artifact identities','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Full widget set, installed policy/catalog ownership, complete accessibility navigation, independently supervised desktop activation and real-network scene vertical','outcome':'not_run','evidence':None},
 {'name':'Other native text adapters, historical native OS execution and all complete editions','outcome':'not_run','evidence':None}],
 next_step='Close and implement remaining primitive content contracts, then connect the owned scene surface to authenticated producer discovery, persistent pins, committed configuration, native controls/direct editing and independent desktop supervision. Continue other adapters and all five platform/package/lifecycle tracks.',
 limitations=[
 'Finite synthetic GTK/X11 scalar window experiment. No behind-icons placement, installed ownership or complete native accessibility-tree qualification.',
 'Component clear failure closes permanently, but an unresponsive native surface still requires independent host teardown; suspend and hard-failure erasure remain open.',
 'The final native forced-enable correction received focused component and native checks; full-suite source differences are explicitly archived and limited to two Linux-only files.',
 'Selected runtime/font identities do not prove complete transitive reproduction, portable glyph equality or font redistribution rights.',
 'Historical-toolset tests run on the modern Windows host, not historical operating systems.',
 'The earlier binding checkpoint content-command receive timeout remains undetermined and preserved; later passes do not erase it.',
 'Two existing Windows symlink tool assertions remain skipped. Full product implementation, native labs and release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Scalar scene handoff validated; workspace inspection passed.')
