from pathlib import Path
for name in ('locks_step.py','locks_flow.py'):
 p=Path('out/campaign')/name;s=p.read_text().replace("'focus','oracle'","'portable','focus','oracle'")
 if name=='locks_step.py':s=s.replace("command={'locks':","command={'portable':['ctest','--preset',profile,'-E','^native[.]','--output-on-failure'],'locks':")
 p.write_text(s,encoding='utf-8',newline='\n')
