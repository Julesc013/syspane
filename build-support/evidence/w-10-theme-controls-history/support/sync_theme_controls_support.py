from pathlib import Path
import hashlib,json,shutil
r=Path.cwd();out=r/'out/campaign';p=r/'build-support/evidence/w-10-theme-controls-attempts.json';index=json.loads(p.read_bytes());h=r/'build-support/evidence/w-10-theme-controls-history/support'
files=[x for x in out.iterdir() if x.is_file() and ('theme_controls' in x.name or 'theme-controls' in x.name or x.name=='prepare_theme_controls_evidence.py')]
files += [x for x in (out/'w-10-theme-controls').iterdir() if x.is_file()]
for x in files:
 target=h/x.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(x,target);index['support'][x.relative_to(r).as_posix()]={'path':target.relative_to(r).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
p.write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(files),'current helper/receipt files.')
