from pathlib import Path
r=Path.cwd();p=r/'out/campaign/archive_scene_images.py';t=p.read_text()
t=t.replace("v=json.loads(p.read_text())\n", "v=json.loads(p.read_text())\n if p.parent.name.startswith('image-'):v['family']='IMAGE-DECODE'\n")
t=t.replace("'TRANSACTION-SUPERVISION')", "'TRANSACTION-SUPERVISION','IMAGE-DECODE')")
anchor="(e/(prefix+'native-index.json')).write_text"
insert="""flat=[p for p in b.iterdir() if p.is_file() and p.stat().st_mtime>=cutoff and (p.name.startswith('RECOVERY-01-') or p.name.startswith('failure-'))]
if flat:
 zp=d/'recovery-records.zip';files={}
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(flat):files[p.name]=sha(p);z.write(p,p.name)
 with zipfile.ZipFile(zp) as z:
  for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 records.append(dict(family='RECOVERY-01-records',archive=dict(path=zp.relative_to(r).as_posix(),sha256=sha(zp)),files=files))
"""
assert anchor in t;t=t.replace(anchor,insert+anchor);p.write_text(t,encoding='utf-8',newline='\n')
p=r/'out/campaign/reclaim_scene_images_captures.py';t=p.read_text();a=t.index(" if item['family'] not in");b=t.index('\n',a)
t=t[:a]+" if not (item['family'].endswith('-ERASURE') or item['family']=='IMAGE-DECODE'):continue"+t[b:]
t=t.replace("folder.name.startswith('surface-')", "(folder.name.startswith('surface-') or folder.name.startswith('image-'))").replace("if not name.endswith('.rgb'):continue", "if not name.endswith(('.rgb','.reply')):continue")
p.write_text(t,encoding='utf-8',newline='\n')
