from pathlib import Path
r=Path.cwd();out=r/'out/campaign'
def write(name,value):(out/name).write_text(value,encoding='utf-8',newline='\n')
def adapted(name):
 s=(out/(name+'_theme_overrides'+('_support' if name=='sync' else '')+'.py')).read_text()
 return s.replace('w-10-theme-overrides','w-08-theme-commands').replace('theme_overrides','theme_commands').replace('theme-overrides','theme-commands').replace('6f753bf6cf4c49eded0134d9d7b63ce6d1b4f91a','cba00af8d6dd2fcd09d2a363e3d08cf2bae0d406')
s=adapted('preserve').replace("('linux-x64-gcc13',347),('windows-x64-gcc15',344),('windows-x86-v141-xp',341)","('linux-x64-gcc13',352),('windows-x64-gcc15',349),('windows-x86-v141-xp',346)")
s=s.replace("==170 and", "==175 and").replace("['native']['cases'])==2","['native']['cases'])==6")
s=s.replace("list((out/'w-08-theme-commands').glob('original-*'))","[p for p in (out/'w-08-theme-commands').iterdir() if p.is_file()]")
s=s.replace("+list((out/'w-08-theme-commands').glob('fixed-inputs*'))","")
s=s.replace("any(a['family']=='RESOURCE-GENERATIONS' and a['outcome']=='pass' for a in native)","any(a['family']=='THEME-COMMANDS' and a['outcome']=='pass' for a in native)")
s=s.replace('Bounded versioned theme selection and replacement; command/store and native integration remain required.','Negotiated theme commands and Linux durable generations; atomic editor history and native controls remain required.')
write('preserve_theme_commands.py',s)
s=adapted('verify').replace('Versioned theme selection and replacement are verified; durable command/store and native integration remain open.','Theme commands and Linux durable recovery are verified; atomic editor history and native controls remain open.')
write('verify_theme_commands.py',s)
s=adapted('stage');start=s.index("for n,digest in fixed['inputs'].items():");end=s.index("native=json.loads",start)
s=s[:start]+"for n,digest in fixed['inputs'].items():check(n,digest)\n"+s[end:]
s=s.replace('Durable/native theme authoring integration and all complete editions remain open.','Atomic editor history, native theme controls and all complete editions remain open.')
write('stage_theme_commands.py',s)
write('sync_theme_commands_support.py',adapted('sync').replace('prepare_theme_override_evidence.py','prepare_theme_commands_evidence.py'))
