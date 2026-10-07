from pathlib import Path
import json
r=Path.cwd();d=r/'out/campaign'
base='1327296abae9e592ad6f20dd0334004c244c67c1'
for old,new in [('archive_observation.py','archive_keyboard.py'),('preserve_observation.py','preserve_keyboard.py'),('finish_observation_checks.py','finish_keyboard_checks.py'),('finish_observation.py','finish_keyboard.py'),('stage_observation.py','stage_keyboard.py')]:
    s=(d/old).read_text().replace('w-10-native-observation','w-10-modal-focus').replace('066657a89472b0476e3d30a1a1d51a944c88789b',base).replace('native-observation-handoff.json','keyboard-input-handoff.json').replace('observation-staging-paths.txt','keyboard-staging-paths.txt')
    if old=='archive_observation.py':
        s=s.replace("('NATIVE-OBSERVATION',", "('MODAL-FOCUS-DIAGNOSTIC','MODAL-FOCUS-MINIMAL-DIAGNOSTIC','MODAL-FOCUS-ORDERED-DIAGNOSTIC','EDITOR-LAYOUT','NATIVE-OBSERVATION',")
    if old=='preserve_observation.py':
        start=s.index('helpers=');end=s.index('\nfor p in [',start)
        helpers=['setup_modal_focus.py','prepare_modal_focus_minimal.py','prepare_modal_focus_ordered.py','modal_focus_probe.py','modal_focus_probe_minimal.py','modal_focus_probe_ordered.py','modal-focus-plan.json','modal-focus-plan-v2.json','modal-focus-plan-v3.json','modal_focus_step.py','modal_focus_flow.py','modal_focus_minimal_step.py','modal_focus_minimal_flow.py','modal_focus_ordered_step.py','modal_focus_ordered_flow.py','prune_modal_focus_duplicates.py','modal-focus-pruned-duplicates.json','freeze_keyboard_input.py','keyboard_step.py','keyboard_flow.py','document_keyboard.py','prepare_keyboard_evidence.py','archive_keyboard.py','preserve_keyboard.py','finish_keyboard_checks.py','finish_keyboard.py','stage_keyboard.py','fetch_keyboard_sources.py']
        s=s[:start]+'helpers='+repr(helpers)+s[end:]
        s=s.replace("*sorted((r/'out/campaign').glob('observation-execution-*.json'))", "*sorted((r/'out/campaign').glob('modal-focus*execution-*.json')),*sorted((r/'out/campaign').glob('keyboard-execution-*.json'))")
        s=s.replace("('fixed-inputs','calibration-inputs')", "('fixed-inputs',)")
        s=s.replace("('calibration','creation'", "('layout','calibration','creation'")
        s=s.replace('w-10-widget-creation-attempts.json','w-10-layout-authoring-attempts.json')
        s=s.replace("'HEAD','source','spec/contracts','spec/fixtures'", "'HEAD','source','spec/contracts','spec/fixtures','CMakeLists.txt','CMakePresets.json','build-support/components.json'")
        s=s.replace("families={'EDITOR-OBSERVATION'", "families={'EDITOR-LAYOUT':21,'EDITOR-OBSERVATION'")
        s=s.replace('Explicit native observations and seven calibrations with 129 existing native cases. Production source and binary unchanged. Original intermittent focus/interface cause remains unproven; no complete-edition or historical qualification.', 'Per-key navigation acknowledgement restores keyboard layout activation; alignment awaits fixed pixel completion before selection changes. All 157 native cases pass. Production source/binary and all existing product expectations remain unchanged; earlier unrelated failures and complete editions remain open.')
        marker="write(r/(prefix+'attempts.json'),dict("
        insert="""diagnostics=[]
for row in native:
    if row['family'] not in ('MODAL-FOCUS-DIAGNOSTIC','MODAL-FOCUS-MINIMAL-DIAGNOSTIC','MODAL-FOCUS-ORDERED-DIAGNOSTIC'):continue
    v=json.loads((r/row['path']).read_bytes());assert v['outcome']=='observed'
    diagnostics.append({**{k:row[k] for k in ('path','sha256','family')},'cases':len(v['cases'])})
assert len(diagnostics)==3 and sum(v['cases'] for v in diagnostics)==24
"""
        s=s.replace(marker,insert+marker).replace('final_native=final_native,scope=', 'final_native=final_native,diagnostics=diagnostics,scope=')
    if old=='finish_observation.py':
        s=s.replace("==136", "==157")
        s=s.replace('Distinguish unavailable native observations from absent text, state, interface and selection without weakening editor acceptance','Acknowledge native keyboard navigation and activation before moving focus, with fixed acceptance outcomes')
        a=s.index('    decisions=');b=s.index('    checks=',a)
        s=s[:a]+"    decisions=['Preserve the original keyboard oracle and three bounded diagnostic matrices, including failures and inconclusive passes.', 'Await each selected row/title within one three-second deadline and retain explicit focused-state assertions.', 'Restore keyboard button activation and await fixed aligned pixels before changing selection.', 'Keep production, product fixtures and all acceptance outcomes unchanged; do not generalize to unrelated historical failures.'],\n"+s[b:]
        s=s.replace('Seven observer calibrations and 129 fixed native regression cases','157 native cases across ten fixed regression matrices')
        s=s.replace("dict(name='Historical intermittent live focus/interface cause'", "dict(name='Specific layout input ordering experiment',outcome='not_run' if pending else 'pass',evidence=prefix+'native-index.json'),dict(name='Earlier unrelated live focus/interface causes'")
        s=s.replace('Close responsive/flow transforms','Close flow/container group transformations').replace('Responsive/flow transforms','Flow/container group transformations')
        s=s.replace("'Historical focus-failure cause and convenience-API delay duration remain unproven.', 'Denied RPC service calibrates observer error handling, not product authorization policy.',", "'The paired traces establish only this layout-navigation failure; earlier unrelated failures remain unproven.', 'An additional failed alignment run is retained; fixed pixels now acknowledge activation before focus moves.',")
        s=s.replace('Linux observer-only correction','Linux oracle-only correction')
    if old=='stage_observation.py':
        s=s.replace("'wrong-insert','retain-create'", "'wrong-layout','retain-layout','wrong-insert','retain-create'")
        s=s.replace('Fixed expected scenes, explicit native observer, calibration, original failures and source/binary-bound native evidence. Historical intermittent focus cause remains unproven and full editions remain open.', 'Fixed expected scenes, ordered native input, preserved diagnostic failures and source/binary-bound native evidence. Specific layout-navigation cause established; earlier unrelated failures and full editions remain open.')
    (d/new).write_text(s,encoding='utf-8',newline='\n')
print('Prepared five keyboard evidence helpers.')
