from pathlib import Path
r=Path.cwd();out=r/'out/campaign';base='6f753bf6cf4c49eded0134d9d7b63ce6d1b4f91a'
for old,new in [('preserve_theme_authoring.py','preserve_theme_overrides.py'),('verify_theme_authoring.py','verify_theme_overrides.py'),('stage_theme_authoring.py','stage_theme_overrides.py')]:
 s=(out/old).read_text().replace('w-10-theme-authoring','w-10-theme-overrides').replace('theme-authoring-handoff','theme-overrides-handoff').replace('theme-authoring-staging','theme-overrides-staging').replace('theme_authoring','theme_overrides').replace('theme-authoring','theme-overrides').replace('ed3adc07f6900846ec347e4019b822f44fce59d7',base).replace('fixed-inputs-v2.json','fixed-inputs.json')
 s=s.replace("('linux-x64-gcc13',343),('windows-x64-gcc15',340),('windows-x86-v141-xp',337)","('linux-x64-gcc13',347),('windows-x64-gcc15',344),('windows-x86-v141-xp',341)").replace("==166","==170")
 s=s.replace("a['family']=='THEME-TYPOGRAPHY'","a['family']=='RESOURCE-GENERATIONS'")
 s=s.replace('Shared theme input and immutable authored artifact construction; durable override/command/store and native UI integration remain required. Original fixed bytes and all execution attempts are preserved.','Bounded versioned theme selection and replacement; command/store and native integration remain required. Fixed inputs and all execution attempts preserved.')
 s=s.replace('Shared theme authoring input and artifact construction are verified; durable/native authoring integration and full editions remain open.','Versioned theme selection and replacement are verified; durable command/store and native integration remain open.')
 (out/new).write_text(s,encoding='utf-8',newline='\n')
