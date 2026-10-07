from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile,subprocess
r=Path.cwd();d=r/'out/campaign/runtime-observation';d.mkdir(exist_ok=True)
paths=['spec/delivery/packages/w-09-runtime-observation.md','source/rendering/image_job_linux.cpp','source/rendering/image_job.hpp','source/rendering/scene_image.cpp','source/rendering/scene_image.hpp','source/rendering/scene_surface.cpp','source/scene/image.cpp','source/scene/image.hpp','tests/scene/image_surface_tests.cpp','tests/scene/image_job_tests.cpp','tests/scene/inspector-cases.json','tests/scene/native_inspector.py','tests/editor/native_binding_authoring.py','tests/editor/native_observation.py','tests/editor/native_editor.py','tests/editor/observation-cases.json','tests/editor/binding-authoring-cases.json','tests/editor/binding-text-cases.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (d/'fixed-inputs.zip').exists()
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'fixed-inputs.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs={p:sha(r/p) for p in paths},archive_sha256=sha(d/'fixed-inputs.zip')),indent=2)+'\n',encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_focus_idle_final_duplicates.py').read_text()
s=s.replace("('w-10-containers','w-10-modal-focus','w-10-layout-authoring','w-10-native-observation','w-09-scene-images','w-09-image-pipeline')","('w-10-focus-idle',)")
s=s.replace('focus-idle-final-pruned-duplicates.json','runtime-observation-pruned-duplicates.json')
(r/'out/campaign/prune_runtime_observation_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
