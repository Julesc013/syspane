from pathlib import Path
import hashlib,json
r=Path.cwd();o=r/'out/campaign';s=(o/'layout_step.py').read_text()
s=s.replace('w-10-layout-authoring','w-10-modal-focus').replace('spec/delivery/packages/w-10-modal-focus.md','spec/delivery/packages/w-10-native-observation.md')
s=s.replace("if action=='diagnostic':paths.append(r/'out/campaign/creation_focus_probe.py')", "if action=='diagnostic':paths.extend(r/n for n in ('out/campaign/modal_focus_probe.py','out/campaign/modal-focus-plan.json', 'build-support/evidence/w-10-layout-authoring-history/linux-x64-gcc13-layout-1901b24c42/source-inputs.zip'))")
needle="if profile=='linux-x64-gcc13':command="
s=s.replace(needle,"if action=='diagnostic':command=['python3',str(r/'out/campaign/modal_focus_probe.py'),'/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/syspane_editor_window','/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/SysPane.EditorExitProbe','/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence']\n"+needle)
(o/'modal_focus_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(o/'layout_flow.py').read_text().replace('layout_step.py','modal_focus_step.py').replace('layout-execution','modal-focus-execution')
(o/'modal_focus_flow.py').write_text(s,encoding='utf-8',newline='\n')
