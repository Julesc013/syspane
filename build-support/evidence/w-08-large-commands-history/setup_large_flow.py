from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=(r/'out/campaign/native_editor_step.py').read_text().replace('w-10-native-editor','w-08-large-commands')
s=s.replace('syspane_editor_tests','syspane_large_command_tests').replace("'^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.](POLICY-|DISCLOSURE-))'","'^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'")
s=s.replace("'^(editor[.]|settings[.]|composition[.])'","'^configuration[.]LARGE-'")
(r/'out/campaign/large_commands_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/native_editor_flow.py').read_text().replace('native_editor_step.py','large_commands_step.py').replace('native-editor-execution-','large-commands-execution-')
(r/'out/campaign/large_commands_flow.py').write_text(s,encoding='utf-8',newline='\n')
