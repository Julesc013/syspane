from pathlib import Path
out=Path.cwd()/'out/campaign';step=out/'refresh_step.py';flow=out/'refresh_flow.py'
for path,name in [(step,'refresh_step_after_walk.py'),(flow,'refresh_flow_before_actions.py')]:
 target=out/name;assert not target.exists();target.write_bytes(path.read_bytes())
s=step.read_text().replace("('refresh','locks'","('graph','rendering','editors','refresh','locks'")
s=s.replace("command={'refresh':", "command={'graph':['ctest','--preset',profile,'-R','^composition[.]','--output-on-failure'],'rendering':['ctest','--preset',profile,'-R','^native[.](TEXT-RASTER|IMAGE-DECODE|IMAGE-JOB|SCENE-(SURFACE|IMAGE|CHART|TABLE|INSPECTOR|INSPECTOR-MODEL|ERASURE)|CHART-ERASURE|IMAGE-ERASURE|TABLE-ERASURE|CONTENT-ERASURE|SETTINGS-FORM)$','--output-on-failure'],'editors':['ctest','--preset',profile,'-R','^native[.](EDITOR-(LOCKS|CONTAINERS|LAYOUT|OBSERVATION|WIDGET-CREATION|BINDING-AUTHORING|CONTENT-PROPERTIES|SNAP|GROUP|ARRANGE|FORM)|LARGE-COMMANDS)$','--output-on-failure'],'refresh':")
s=s.replace("artifact_name={'refresh':", "artifact_name={'editors':'syspane_editor_window','rendering':'syspane_scene_surface_tests','refresh':")
step.write_text(s,encoding='utf-8',newline='\n')
s=flow.read_text().replace("('refresh','locks'","('graph','rendering','editors','refresh','locks'")
flow.write_text(s,encoding='utf-8',newline='\n')
