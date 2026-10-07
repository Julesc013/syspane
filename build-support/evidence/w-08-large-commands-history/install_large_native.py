from pathlib import Path
r=Path(__file__).resolve().parents[2]
(r/'tests/configuration/native_large_commands.py').write_bytes((r/'out/campaign/native_large_commands.py').read_bytes())
p=r/'out/campaign/large_commands_step.py';s=p.read_text()
s=s.replace("'surface','test'","'surface','large','test'").replace("command={","command={'large':['ctest','--preset',profile,'-R','^native[.]LARGE-COMMANDS$','--output-on-failure'],")
s=s.replace("'native':'syspane_editor_window'","'large':'SysPane.CommandProbe','native':'syspane_editor_window'")
s=s.replace("'exit','surface'):","'exit','surface','large'):")
p.write_text(s,encoding='utf-8',newline='\n')
p=r/'out/campaign/large_commands_flow.py';s=p.read_text().replace("'exit','surface')","'exit','surface','large')");p.write_text(s,encoding='utf-8',newline='\n')
