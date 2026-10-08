from pathlib import Path
r=Path.cwd();out=r/'out/campaign'
for name in ('preserve','verify','stage','sync'):
 suffix='_support' if name=='sync' else ''
 s=(out/(name+'_theme_commands'+suffix+'.py')).read_text().replace('w-08-theme-commands','w-10-theme-history').replace('theme_commands','theme_history').replace('theme-commands','theme-history').replace('cba00af8d6dd2fcd09d2a363e3d08cf2bae0d406','5e043779be1734d13e65e533d0d4b2789a713107')
 if name=='preserve':
  s=s.replace("('linux-x64-gcc13',352),('windows-x64-gcc15',349),('windows-x86-v141-xp',346)","('linux-x64-gcc13',360),('windows-x64-gcc15',357),('windows-x86-v141-xp',354)").replace('==175 and','==183 and')
  s=s.replace("a['family']=='THEME-COMMANDS'","a['family']=='THEME-HISTORY'")
  s=s.replace('Negotiated theme commands and Linux durable generations; atomic editor history and native controls remain required.','Shared immutable editor resource history and durable Apply/reload; native font controls remain required.')
 if name=='verify':s=s.replace('Theme commands and Linux durable recovery are verified; atomic editor history and native controls remain open.','Shared editor resource history and durable Apply/reload are verified; native font controls remain open.')
 if name=='stage':s=s.replace('Atomic editor history, native theme controls and all complete editions remain open.','Native theme controls and all complete editions remain open.')
 (out/(name+'_theme_history'+suffix+'.py')).write_text(s,encoding='utf-8',newline='\n')
print('Prepared theme history preservation/verification/staging helpers.')
