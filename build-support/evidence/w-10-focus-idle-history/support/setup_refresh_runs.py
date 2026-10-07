from pathlib import Path
r=Path.cwd();out=r/'out/campaign'
s=(out/'locks_step.py').read_text().replace('w-10-edit-locks','w-10-focus-idle')
s=s.replace("('locks','containers'","('refresh','locks','containers'")
s=s.replace("command={'portable':", "command={'refresh':['ctest','--preset',profile,'-R','^native[.]EDITOR-REFRESH$','--output-on-failure'],'portable':")
s=s.replace("artifact_name={'locks':", "artifact_name={'refresh':'syspane_editor_window','locks':")
(out/'refresh_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'locks_flow.py').read_text().replace('locks-execution-','refresh-execution-').replace('locks_step.py','refresh_step.py').replace("('locks','containers'","('refresh','locks','containers'")
(out/'refresh_flow.py').write_text(s,encoding='utf-8',newline='\n')
