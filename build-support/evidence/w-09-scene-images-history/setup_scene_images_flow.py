from pathlib import Path
r=Path.cwd()
for name in ('image_pipeline_step.py','image_pipeline_flow.py'):
    t=(r/'out/campaign'/name).read_text().replace('image-pipeline','scene-images').replace('image_pipeline','scene_images').replace('w-09-image-pipeline.md','w-09-scene-images.md')
    if name.endswith('step.py'):
        t=t.replace("('configure','build','focus','oracle','scalar','table','content','test')","('configure','build','focus','oracle','scalar','table','content','chart','test')")
        t=t.replace("command={'scalar':", "command={'chart':['ctest','--preset',profile,'-R','^native[.]CHART-ERASURE$','--output-on-failure'],'scalar':")
        t=t.replace("^(scene[.]IMAGE-|native[.]IMAGE-(DECODE|JOB)$|composition[.])", "^(native[.](SCENE-IMAGE|IMAGE-JOB)$|composition[.])")
        t=t.replace("^native[.]IMAGE-(DECODE|JOB)$","^native[.]IMAGE-ERASURE$")
        t=t.replace("SCENE-(SURFACE|TABLE|CHART)","SCENE-(SURFACE|TABLE|CHART|IMAGE)")
        t=t.replace("'scalar','table','content')","'scalar','table','content','chart')")
    else:t=t.replace("'scalar','table','content')","'scalar','table','content','chart')")
    (r/'out/campaign'/name.replace('image_pipeline','scene_images')).write_text(t,encoding='utf-8',newline='\n')
# Existing committed image-pipeline archives are safe duplicates in ignored output.
p=r/'out/campaign/reclaim_scene_images_inputs.ps1';t=(r/'out/campaign/reclaim_image_table_inputs.ps1').read_text().replace('w-09-table-history','w-09-image-pipeline-history').replace('w-09-table','w-09-image-pipeline').replace('image-table-reclamation','scene-images-input-reclamation')
t=t.replace("preflight=@{ maximum_bytes=6442450944; checkout_out_bytes=1908686429; linux_campaign_bytes=4266538210; reserved_growth_bytes=268435456; status='stop' };", "reason='Reclaim verified committed duplicate inputs before the next admitted native scene build';")
p.write_text(t,encoding='utf-8',newline='\n')
