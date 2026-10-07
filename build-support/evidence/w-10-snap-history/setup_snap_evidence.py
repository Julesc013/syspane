from pathlib import Path
r=Path(__file__).resolve().parents[2];d=r/'out/campaign'
base='01bea41e2123f69b1d71285b5ab944122efeace7'
def write(name,s):(d/name).write_text(s,encoding='utf-8',newline='\n')
def common(s):return s.replace('w-10-group','w-10-snap').replace('bd964bd465265a274dffe34b666994835cd3e643',base)
for name in ('archive','finish_group_checks'):
    old='archive_group.py' if name=='archive' else name+'.py';s=common((d/old).read_text())
    if name=='archive':s=s.replace("('EDITOR-GROUP','EDITOR-ARRANGE'", "('EDITOR-SNAP','EDITOR-GROUP','EDITOR-ARRANGE'")
    write(old.replace('group','snap'),s)
s=common((d/'preserve_group.py').read_text());start=s.index('helpers=');end=s.index('\nfor p in ',start)
s=s[:start]+"helpers=['prepare_snap.py','snap_step.py','snap_flow.py','document_snap.py','archive_snap.py','preserve_snap.py','finish_snap_checks.py','setup_snap_evidence.py','finish_snap.py','stage_snap.py']"+s[end:]
s=s.replace('group-execution-','snap-execution-').replace("'fixed-inputs.zip','overlap-input.json','overlap-input.zip'", "'fixed-inputs.zip'")
s=s.replace("latest('linux-x64-gcc13','group')", "latest('linux-x64-gcc13','snap')")
s=s.replace("(n=='tests/editor/native_group.py' and v['action']!='group')", "(n=='tests/editor/native_snap.py' and v['action']!='snap')")
s=s.replace("('group','arrange','native','large')", "('snap','group','arrange','native','large')")
s=s.replace("families={'EDITOR-GROUP'", "families={'EDITOR-SNAP':('syspane_editor_window','tests/editor/native_snap.py',13),'EDITOR-GROUP'")
s=s.replace("    if family=='EDITOR-GROUP':", "    if family=='EDITOR-SNAP':\n        assert v['fixture_sha256']==sha(r/'tests/editor/snap-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='EDITOR-GROUP':")
s=s.replace('==101','==105').replace('101 affected','105 affected').replace('native group, arrange','native snap, group, arrange')
s=s.replace(",overlap_record=ref(history/'overlap-input.json'),overlap_archive=ref(history/'overlap-input.zip')",'')
write('preserve_snap.py',s)
s=common((d/'stage_group.py').read_text()).replace('group-handoff.json','snap-handoff.json').replace('group-staging-paths','snap-staging-paths')
s=s.replace("(n=='tests/editor/native_group.py' and action!='group')", "(n=='tests/editor/native_snap.py' and action!='snap')")
s=s.replace("('EDITOR-GROUP','EDITOR-ARRANGE'", "('EDITOR-SNAP','EDITOR-GROUP','EDITOR-ARRANGE'")
s=s.replace("else 'tests/editor/group-cases.json'", "else 'tests/editor/snap-cases.json' if family=='EDITOR-SNAP' else 'tests/editor/group-cases.json'")
s=s.replace("check('tests/editor/native_group.py'", "check('tests/editor/native_snap.py' if family=='EDITOR-SNAP' else 'tests/editor/native_group.py'")
start=s.index("overlap=json.loads(content(original['overlap_record']['path']))");end=s.index('native=json.loads',start);s=s[:start]+s[end:]
s=s.replace('native grouping, exact','native snapping, exact')
write('stage_snap.py',s)
s=common((d/'finish_group.py').read_text()).replace('group-handoff.json','snap-handoff.json').replace('evidence/arrange-handoff.json','evidence/group-handoff.json').replace('==101','==105').replace('101 affected','105 affected').replace('11 native grouping, 14 arrangement','13 native snapping, 11 grouping, 14 arrangement')
start=s.index("objective='");end=s.index("',changed_files=",start);s=s[:start]+"objective='Add deterministic grid and alignment-guide snapping with bounded shared projection, captured native gestures and independent visible/stored outcomes"+s[end:]
start=s.index(' decisions=[');end=s.index('\n checks=[',start)
s=s[:start]+''' decisions=[
  'Freeze the package and literal geometry outcomes before production changes; use signed 1/64-DIP units and deterministic candidate ordering.',
  'Keep existing authored, renderer, policy and storage owners. Project captured pointer geometry into existing MoveWidgets/ResizeWidget operations.',
  'Capture siblings, parent/work area, grid origin, scale and options at press. Telemetry cannot retarget the gesture.',
  'Keep snap/grid preferences local to the session; numeric and keyboard edits remain precise. Ctrl at release bypasses snapping.',
  'Expose guide lines and accessible coordinates while held; erase feedback on cancellation, focus/topology/policy changes and close.',
  'Preserve the checkbox-observation failure; await actual native checked state before moving focus.',
  'Preserve the original frozen-preview calibration failure. Detect its earlier held-guide pixel failure only with correct live guide text, unchanged original scene pixels and unchanged durable documents.'],'''+s[end:]
s=s.replace('Close snap/grid/guides, responsive/flow container transforms', 'Close responsive/flow container transforms').replace('Responsive arrangement/container transforms, snap/grid/guides,','Responsive arrangement/container transforms,')
write('finish_snap.py',s)
print('Prepared snapshot, native archive, handoff and staged-identity helpers.')
