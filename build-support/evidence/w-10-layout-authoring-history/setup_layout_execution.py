from pathlib import Path
r=Path(__file__).resolve().parents[2]
for old,new in [('creation_step.py','layout_step.py'),('creation_flow.py','layout_flow.py')]:
    s=(r/'out/campaign'/old).read_text().replace('w-10-widget-creation','w-10-layout-authoring').replace('creation-execution-','layout-execution-').replace('creation_step.py','layout_step.py')
    if new=='layout_step.py':
        s=s.replace("'diagnostic','configure'","'layout','calibration','diagnostic','configure'").replace("command={'diagnostic':","command={'layout':['ctest','--preset',profile,'-R','^native[.]EDITOR-LAYOUT$','--output-on-failure'],'calibration':['ctest','--preset',profile,'-R','^native[.]EDITOR-OBSERVATION$','--output-on-failure'],'diagnostic':").replace('^editor[.]CREATE-','^editor[.]LAYOUT-').replace("{'diagnostic':'syspane_editor_window'","{'layout':'syspane_editor_window','calibration':'syspane_editor_window','diagnostic':'syspane_editor_window'").replace("if action in ('test',","if action in ('layout','calibration','test',")
    else:s=s.replace("('diagnostic','test'","('layout','calibration','diagnostic','test'")
    (r/'out/campaign'/new).write_text(s,encoding='utf-8',newline='\n')
print('Prepared source-bound ordinary build and native layout runners.')
