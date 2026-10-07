from pathlib import Path
r=Path(__file__).resolve().parents[2];d=r/'out/campaign'
base='ce7731133431029d72d6d39f149d59f4663e66af'
def common(s):return s.replace('w-10-snap','w-10-content-properties').replace('01bea41e2123f69b1d71285b5ab944122efeace7',base).replace('snap-handoff.json','content-properties-handoff.json').replace('snap-execution','properties-execution').replace('snap-staging-paths','properties-staging-paths')
def write(name,s):(d/name).write_text(s,encoding='utf-8',newline='\n')
for name in ('archive','finish_snap_checks'):
 old='archive_snap.py' if name=='archive' else name+'.py';s=common((d/old).read_text())
 if name=='archive':s=s.replace("('EDITOR-SNAP',","('EDITOR-CONTENT-PROPERTIES','EDITOR-SNAP',")
 write('archive_properties.py' if name=='archive' else 'finish_properties_checks.py',s)
s=common((d/'preserve_snap.py').read_text());start=s.index('helpers=');end=s.index('\nfor p in ',start)
s=s[:start]+"helpers=['prepare_content_properties.py','setup_content_properties.py','fix_properties_buffers.py','properties_step.py','properties_flow.py','document_properties.py','archive_properties.py','preserve_properties.py','finish_properties_checks.py','setup_properties_evidence.py','finish_properties.py','stage_properties.py','prune_properties_duplicates.py','properties-pruned-duplicates.json']"+s[end:]
s=s.replace("latest('linux-x64-gcc13','snap')","latest('linux-x64-gcc13','properties')")
start=s.index('    for n in delta:');end=s.index('\nfinal={}',start)
s=s[:start]+'''    for n in delta:assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and v['action']!='arrange') or (v['profile'].startswith('windows') and n=='source/interfaces/editor_form_linux.cpp'),n
    if delta:input_differences[v['profile']+'-'+v['action']]=dict(files=delta,reason='Only documentation, the native arrangement observer for checks that do not invoke it, or the Linux-only form for Windows changed. Windows target graphs exclude the Linux form; Python observers are not compiler inputs. Final arrangement execution uses the current observer and final affected native checks use current product source.')
'''+s[end:]
s=s.replace('==105','==111').replace('105 affected','111 affected').replace("('snap','group','arrange','native','large')","('properties','snap','group','arrange','native','large')")
s=s.replace("families={'EDITOR-SNAP'","families={'EDITOR-CONTENT-PROPERTIES':('syspane_editor_window','tests/editor/native_content_properties.py',15),'EDITOR-SNAP'")
s=s.replace("    if family=='EDITOR-SNAP':", "    if family=='EDITOR-CONTENT-PROPERTIES':\n        assert v['fixture_sha256']==sha(r/'tests/editor/content-properties-cases.json') and v['resources_sha256']==sha(r/'tests/editor/content-properties-fixture.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='EDITOR-SNAP':")
s=s.replace('independent native snap,','independent native content properties, snap,');write('preserve_properties.py',s)
s=common((d/'stage_snap.py').read_text())
start=s.index('    for n in delta:');end=s.index('\n    if action',start);s=s[:start]+"    for n in delta:assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and action!='arrange') or (profile.startswith('windows') and n=='source/interfaces/editor_form_linux.cpp')"+s[end:]
s=s.replace("('EDITOR-SNAP',","('EDITOR-CONTENT-PROPERTIES','EDITOR-SNAP',")
s=s.replace("else 'tests/editor/snap-cases.json'", "else 'tests/editor/content-properties-cases.json' if family=='EDITOR-CONTENT-PROPERTIES' else 'tests/editor/snap-cases.json'")
s=s.replace("check('tests/editor/native_snap.py'", "check('tests/editor/native_content_properties.py' if family=='EDITOR-CONTENT-PROPERTIES' else 'tests/editor/native_snap.py'")
s=s.replace("'gui-wrong-commit')","'gui-wrong-commit','wrong-content','retain-content')")
s=s.replace('native snapping, exact','native content properties, exact');write('stage_properties.py',s)
s=common((d/'finish_snap.py').read_text()).replace('evidence/group-handoff.json','evidence/snap-handoff.json').replace('==105','==111').replace('105 affected','111 affected').replace('13 native snapping','15 native content, 13 snapping')
start=s.index("objective='");end=s.index("',changed_files=",start);s=s[:start]+"objective='Add bounded native content and scene-theme buffers through existing atomic draft, resource, policy and persistence owners"+s[end:]
start=s.index(' decisions=[');end=s.index('\n checks=[',start)
s=s[:start]+''' decisions=[
  'Freeze full authored scenes, resource bytes/pins and expected content outcomes before production changes.',
  'Preserve original bindings when reordering table labels; keep complete original-column permutations.',
  'Project strict finite numeric input and serialize only the active chart-axis mode.',
  'Enumerate exact immutable resource choices; retain theme resolver and current-policy validation.',
  'Keep modal input outside authored history; apply one atomic batch, preserve no-op/cancel previews, and erase native text/choice models on policy/owner changes.',
  'Preserve compilation, fixture-channel, native observation and any product failures. Final native checks retain original expected scenes and independently observe actual inputs, pixels, accessibility and storage.',
  'Record the native laboratory display as 640x560 logical DIP at 3/4 scale; maintain telemetry heartbeats at 500 ms.',
  'Preserve the isolated held-focus failure and diagnostic-only passing rerun; construct the modal window only on explicit Content entry and rerun the complete native matrix. The original focus failure cause was not established.',
  'Free only verified duplicates of committed native evidence within the unchanged 7 GiB workspace budget.'],'''+s[end:]
s=s.replace('Close responsive/flow container transforms and remaining authoring/property contracts','Close binding authoring, non-text insertion, responsive/flow container transforms and remaining property contracts')
s=s.replace('binding/content/theme panels','binding authoring and remaining property panels');write('finish_properties.py',s)
print('Prepared content-property evidence helpers.')
