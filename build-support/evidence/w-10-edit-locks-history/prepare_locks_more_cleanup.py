from pathlib import Path
r=Path.cwd();s=(r/'out/campaign/prune_locks_duplicates.py').read_text().replace("('w-10-containers',)","('w-10-layout-authoring','w-10-native-observation','w-10-widget-creation','w-10-binding-authoring')").replace('locks-pruned-duplicates.json','locks-more-pruned-duplicates.json')
(r/'out/campaign/prune_locks_more_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
