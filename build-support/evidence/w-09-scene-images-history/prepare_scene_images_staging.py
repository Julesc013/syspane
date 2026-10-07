from pathlib import Path
r=Path.cwd();s=(r/'out/campaign/stage_image_pipeline.py').read_text().replace('w-09-image-pipeline-','w-09-scene-images-').replace('image-pipeline','scene-images').replace('audit_image_pipeline_legacy.py','audit_scene_images_legacy.py')
a=s.index("        if name=='fit-original':");b=s.index("native=json.loads",a)
s=s[:a]+'''        fixed={'tests/scene/image_surface_oracle.py','tests/scene/image-cases/surface.json','tests/configuration/content-digests.json','tests/scene/image-cases/large-encoded.png'}
        for n,digest in inputs.items():
            if n in fixed:check(n,digest)
        if name=='resource-native-original':
            for n,digest in inputs.items():check(n,digest)
'''+s[b:]
a=s.index("    artifact='SysPane.ImageWorker'");b=s.index("windows=index['windows_recovery']",a)
s=s[:a]+'''    artifact=row['artifact'];key='worker_sha256' if family=='IMAGE-DECODE' else 'executable_sha256'
    assert report[key]==index['artifacts']['linux-x64-gcc13'][artifact]['sha256']
    check(row['oracle'],report['oracle_sha256']);assert all(c['outcome']=='pass' for c in report['cases']) and len(report['cases'])==row['cases']
    if 'store_executable_sha256' in report:assert report['store_executable_sha256']==index['artifacts']['linux-x64-gcc13']['SysPane.ConfigProbe']['sha256']
    if family=='IMAGE-DECODE':assert len(report['cases'])==54
    if family=='CONTENT-COMMANDS':assert any(c['case']=='LARGE-RESOURCE' for c in report['cases'])
    if family.endswith('-ERASURE'):
        assert len(report['cases'])==3
        archived=next(n for n in native if n.get('path')==row['path'])
        with zipfile.ZipFile(io.BytesIO(content(archived['archive']['path']))) as z:
            for c in report['cases']:
                raw=z.read(c['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==c['record_sha256'];detail=json.loads(raw)
                assert detail['executable_sha256']==report[key] and detail['text_probe_sha256']==index['artifacts']['linux-x64-gcc13']['SysPane.TextProbe']['sha256']
                check('build-support/text-runtime.json',detail['runtime_identity_sha256'])
                if family=='IMAGE-ERASURE':
                    assert detail['image_worker_sha256']==index['artifacts']['linux-x64-gcc13']['SysPane.ImageWorker']['sha256']
                    check('tests/scene/image-cases/surface.json',detail['image_oracle_sha256'])
'''+s[b:]
s=s.replace('Staged source, fixed geometry/native oracles and attempt/reply archives match executed affected checks. Operational scene images, installed desktop, historical runtime and release qualification remain open.','Staged source, fixed image/digest expectations and attempt/native archives match affected checks. Owned Linux component images are verified; installed desktop, historical runtime and release qualification remain open.')
(r/'out/campaign/stage_scene_images.py').write_text(s,encoding='utf-8',newline='\n')
print('Prepared staged identity verifier.')
