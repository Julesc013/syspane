from pathlib import Path
r=Path.cwd()
p=r/'out/campaign/preserve_image_pipeline.py'
s=p.read_text().replace('w-09-image-pipeline-','w-09-scene-images-').replace('w-09-image-pipeline','w-09-scene-images').replace('image-pipeline','scene-images').replace('e503d290a2c905918abf04e71d85a38642458d1d','ab2642454d562704bf5fac9666b4362ef3370b79')
a=s.index('helpers=');b=s.index('for p in [*sorted',a)
s=s[:a]+'''helpers=['scene_images_step.py','scene_images_flow.py','archive_scene_images.py','reclaim_scene_images_captures.py',
 'reclaim_scene_images_inputs.ps1','reclaim_scene_images_prior_inputs.ps1','scene-images-input-reclamation.json',
 'scene-images-prior-input-reclamation.json','setup_scene_images_flow.py','implement_scene_images.py',
 'extend_scene_images_native.py','prepare_scene_images_evidence.py','extend_scene_images_archive.py',
 'fix_content_digest.py','create_large_image_input.py','fix_scene_image_terminal.py','prepare_scene_images_preservation.py']
'''+s[b:]
s=s.replace("('linux-x64-gcc13',77),('windows-x64-gcc15',71),('windows-x86-v141-xp',72)","('linux-x64-gcc13',114),('windows-x64-gcc15',107),('windows-x86-v141-xp',108)")
s=s.replace("'SysPane.ConfigProbe','libsyspane_scene.a'","'SysPane.ConfigProbe','SysPane.ContentProbe','SysPane.TextProbe','syspane_authored_tests','libsyspane_authored.a','libsyspane_generation_store.a','libsyspane_scene_surface.a','libsyspane_scene.a'")
s=s.replace("names=['syspane_scene_tests.exe',","names=['syspane_authored_tests.exe','syspane_authored.lib' if profile.endswith('xp') else 'libsyspane_authored.a','syspane_scene_tests.exe',")
a=s.index('for family,artifact in ');b=s.index('cutoff=min(',a)
s=s[:a]+'''families={
 'IMAGE-DECODE':('SysPane.ImageWorker','tests/scene/image_native.py'),
 'TRANSACTION-SUPERVISION':('SysPane.CommandProbe','tests/configuration/native_supervision.py'),
 'CONTENT-READER':('SysPane.ContentProbe','tests/configuration/native_content.py'),
 'RESOURCE-GENERATIONS':('SysPane.ConfigProbe','tests/configuration/native_resources.py'),
 'SCENE-CONTENT':('SysPane.ConfigProbe','tests/configuration/native_scene_content.py'),
 'CONTENT-COMMANDS':('SysPane.CommandProbe','tests/configuration/native_content_commands.py'),
 'CONFIG-STORE':('SysPane.ConfigProbe','tests/configuration/native_store.py'),
 'COMMAND-IPC':('SysPane.CommandProbe','tests/configuration/native_command.py'),
 **{n+'-ERASURE':('syspane_scene_surface_tests','tests/scene/native_surface.py') for n in ('SCENE','TABLE','CONTENT','CHART','IMAGE')}}
for family,(artifact,oracle) in families.items():
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);report=json.loads((r/row['path']).read_text());assert report['outcome']=='pass'
    assert report['worker_sha256' if family=='IMAGE-DECODE' else 'executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'],family
    assert report['oracle_sha256']==sha(r/oracle),(family,oracle)
    if 'store_executable_sha256' in report:assert report['store_executable_sha256']==artifacts['linux-x64-gcc13']['SysPane.ConfigProbe']['sha256']
    assert all(c['outcome']=='pass' for c in report['cases'])
    if family=='IMAGE-DECODE':assert len(report['cases'])==54
    if family=='CONTENT-COMMANDS':assert any(c['case']=='LARGE-RESOURCE' for c in report['cases'])
    if family.endswith('-ERASURE'):
        assert len(report['cases'])==3
        with zipfile.ZipFile(r/row['archive']['path']) as z:
            for c in report['cases']:
                raw=z.read(c['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==c['record_sha256']
                detail=json.loads(raw);assert detail['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256']
                assert detail['text_probe_sha256']==artifacts['linux-x64-gcc13']['SysPane.TextProbe']['sha256']
                assert detail['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json')
                if family=='IMAGE-ERASURE':
                    assert detail['image_worker_sha256']==artifacts['linux-x64-gcc13']['SysPane.ImageWorker']['sha256']
                    assert detail['image_oracle_sha256']==sha(r/'tests/scene/image-cases/surface.json')
    final_native[family]={**{k:row[k] for k in ('path','sha256')},'artifact':artifact,'oracle':oracle,'cases':len(report['cases'])}
'''+s[b:]
s=s.replace("('fit-original','native-original')","('original','native-original','digest-original','resource-native-original','large-original')")
s=s.replace('Affected three-toolchain image/scene/dependency checks and native Linux codec/job/child-supervision evidence; modern Windows child recovery. No operational image scene or historical OS/release qualification.','Affected three-toolchain configuration/image/scene/dependency checks and owned Linux image scene, external erasure, content recovery, codec/job/child-supervision evidence; modern Windows child recovery. No installed desktop, historical OS or release qualification.')
(r/'out/campaign/preserve_scene_images.py').write_text(s,encoding='utf-8',newline='\n')
print('Prepared preservation helper; execution follows final checks.')
