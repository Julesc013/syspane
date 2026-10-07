from pathlib import Path
import hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign'
s=(out/'refresh_step.py').read_text().replace('w-10-focus-idle','w-09-runtime-observation').replace("'test':['ctest','--preset',profile,'-R','^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'","'test':['ctest','--preset',profile,'-R','^(scene[.]IMAGE-|composition[.])'")
(out/'runtime_observation_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(out/'refresh_flow.py').read_text().replace('refresh-execution-','runtime-observation-execution-').replace('refresh_step.py','runtime_observation_step.py')
s=s.replace("started=datetime.now(timezone.utc).isoformat();p=subprocess.run(call", "started=datetime.now(timezone.utc).isoformat();p=subprocess.run(call")
# Full rendering has measured output growth above the ordinary reservation.
s=s.replace("rows.append({'step':step", "\n        if 'check_workspace_budget.py' in call and step=='rendering' and p.returncode==0:\n            budget=json.loads(p.stdout)\n            if budget['checkout_out_bytes']+budget['linux_campaign_bytes']+400*1024*1024>budget['maximum_bytes']:\n                p.returncode=1;p.stderr+='Measured rendering growth of 400 MiB does not fit the existing bound.'\n        rows.append({'step':step")
(out/'runtime_observation_flow.py').write_text(s,encoding='utf-8',newline='\n')
d=out/'runtime-observation';paths=['tests/scene/image_fit_tests.cpp','tests/scene/image-validation-cases.json','CMakeLists.txt']
with zipfile.ZipFile(d/'validation-oracle.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(d/'validation-oracle.json').write_text(json.dumps(dict(inputs={n:sha(r/n) for n in paths},archive_sha256=sha(d/'validation-oracle.zip')),indent=2)+'\n',encoding='utf-8',newline='\n')
