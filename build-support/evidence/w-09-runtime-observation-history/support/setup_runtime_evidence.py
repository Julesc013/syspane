from pathlib import Path
r=Path.cwd();out=r/'out/campaign'
s=(out/'archive_focus_idle.py').read_text().replace('w-10-focus-idle','w-09-runtime-observation')
s=s.replace("p.parent.name!='editor-idle-788c47e77043'","p.parent.name!='query-probe-8a2c130673c1'")
s=s.replace("('EDITOR-IDLE-DIAGNOSTIC'","('NATIVE-QUERY-DIAGNOSTIC','EDITOR-IDLE-DIAGNOSTIC'")
(out/'archive_runtime_observation.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'finish_focus_idle_checks.py').read_text().replace('w-10-focus-idle-','w-09-runtime-observation-').replace('9c1757de6a8227b2a4235f8be7b727a9d3f55d7d','330c9772c73928d83a974b051c599190006d60f8')
(out/'finish_runtime_observation_checks.py').write_text(s,encoding='utf-8',newline='\n')
