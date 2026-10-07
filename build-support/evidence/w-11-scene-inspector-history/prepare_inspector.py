from pathlib import Path
import hashlib,json,zipfile
r=Path.cwd();d=r/'out/campaign/scene-inspector-original';d.mkdir()
paths=['spec/delivery/packages/w-11-scene-inspector.md','tests/scene/inspector-cases.json','tests/scene/surface_fixture.hpp','tests/scene/table_fixture.hpp','tests/scene/chart_fixture.hpp','tests/scene/image_fixture.hpp']
(d/'original.json').write_text(json.dumps({n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths},indent=2)+'\n',encoding='utf-8',newline='\n')
with zipfile.ZipFile(d/'original.zip','x',zipfile.ZIP_DEFLATED) as z:
    for n in paths:z.write(r/n,n)
p=r/'out/campaign/reclaim_scene_images_inputs.ps1';s=p.read_text().replace('w-09-image-pipeline','w-09-scene-images').replace('scene-images-input-reclamation.json','scene-inspector-input-reclamation.json')
(r/'out/campaign/reclaim_inspector_inputs.ps1').write_text(s,encoding='utf-8',newline='\n')
print('Preserved inspector contract and fixed initial expectations.')
