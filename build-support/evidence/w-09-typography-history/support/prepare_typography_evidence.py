from pathlib import Path
r=Path.cwd();out=r/'out/campaign'
s=(out/'typography_step.py').read_text();s=s.replace('EDITOR-(LOCKS|CONTAINERS|LAYOUT|OBSERVATION|WIDGET-CREATION|BINDING-AUTHORING|CONTENT-PROPERTIES|SNAP|GROUP|ARRANGE|FORM)|LARGE-COMMANDS','EDITOR-(CONTENT-PROPERTIES|VISIBILITY|FORM)')
(out/'typography_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'archive_visibility_controls.py').read_text().replace('w-10-visibility-controls','w-09-typography').replace("('EDITOR-VISIBILITY','VISIBILITY-PIXELS'","('THEME-TYPOGRAPHY','EDITOR-VISIBILITY','VISIBILITY-PIXELS'")
(out/'archive_typography.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'verify_visibility_controls.py').read_text().replace('w-10-visibility-controls','w-09-typography').replace('Native rule input and trusted EditorForm integration are verified; installed ownership and full editions remain open.','Versioned typography validation and native text roles are verified; scene composition, authoring controls and full editions remain open.')
s=s.replace("'spec/experience/scene-bindings.md','spec/experience/editor.md'","'spec/experience/scene-bindings.md','spec/experience/editor.md','spec/experience/scene-theme.md'")
(out/'verify_typography.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'stage_visibility_controls.py').read_text().replace('w-10-visibility-controls','w-09-typography').replace('visibility-controls-handoff','typography-handoff').replace('visibility-controls-staging','typography-staging')
begin=s.index("fixed=json.loads(content(");end=s.index("native=json.loads",begin)
s=s[:begin]+'''fixed=json.loads(content(index['support']['out/campaign/w-09-typography/fixed-inputs-v2.json']['path']))
for n,digest in fixed['inputs'].items():check(n,digest)
'''+s[end:]
s=s.replace('Installed ownership and full editions remain open.','Scene composition, native theme authoring and all complete editions remain open.')
(out/'stage_typography.py').write_text(s,encoding='utf-8',newline='\n')
print('Prepared evidence archive, verification and staged-byte audit.')
