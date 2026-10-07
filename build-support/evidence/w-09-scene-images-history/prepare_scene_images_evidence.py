from pathlib import Path
r=Path.cwd()
p=r/'out/campaign/scene_images_step.py';t=p.read_text().replace("'chart','test')","'chart','resources','test')")
t=t.replace("command={'chart':", "command={'resources':['ctest','--preset',profile,'-R','^native[.](CONTENT-READER|RESOURCE-GENERATIONS|SCENE-CONTENT|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC)$','--output-on-failure'],'chart':")
t=t.replace("^(scene[.]|composition[.]|legacy[.]|native", "^(configuration[.]|scene[.]|composition[.]|legacy[.]|native")
t=t.replace("'content','chart')","'content','chart','resources')")
p.write_text(t,encoding='utf-8',newline='\n')
p=r/'out/campaign/scene_images_flow.py';t=p.read_text().replace("'content','chart')","'content','chart','resources')");p.write_text(t,encoding='utf-8',newline='\n')
for src,target in (('archive_native_chart.py','archive_scene_images.py'),('reclaim_native_chart_captures.py','reclaim_scene_images_captures.py')):
    t=(r/'out/campaign'/src).read_text().replace('w-09-native-chart','w-09-scene-images').replace("'CHART-ERASURE')", "'CHART-ERASURE','IMAGE-ERASURE','CONTENT-COMMANDS','CONTENT-READER','RESOURCE-GENERATIONS','CONFIG-STORE','COMMAND-IPC','TRANSACTION-SUPERVISION')")
    (r/'out/campaign'/target).write_text(t,encoding='utf-8',newline='\n')
