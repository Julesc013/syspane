from pathlib import Path
from datetime import datetime
import hashlib,json,os,stat,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence');e=r/'build-support/evidence'
assert os.geteuid()==1000 and b.resolve()==b
prefix='w-09-image-pipeline-';d=e/(prefix+'native');d.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
attempts=[json.loads(p.read_text()) for p in (r/'out/campaign/w-09-image-pipeline').glob('*/result.json')]
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
records=[]
index_path=e/(prefix+'native-index.json')
previous={v.get('path'):v for v in json.loads(index_path.read_text())} if index_path.exists() else {}
for p in sorted(b.glob('*/result.json')):
    if p.stat().st_mtime<cutoff:continue
    v=json.loads(p.read_text());family=v.get('family','IMAGE-DECODE' if p.parent.name.startswith('image-') else '')
    if family not in ('IMAGE-DECODE','TRANSACTION-SUPERVISION') or v.get('outcome') in ('running','pending'):continue
    name=p.parent.name;rp=d/(name+'.json');zp=d/(name+'.zip');files={};links={}
    if rp.relative_to(r).as_posix() in previous:
        row=previous[rp.relative_to(r).as_posix()];assert sha(p)==row['sha256'] and sha(zp)==row['archive']['sha256'];records.append(row);continue
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for q in sorted(p.parent.rglob('*')):
            if q.is_dir() and not q.is_symlink():continue
            relative=q.relative_to(p.parent).as_posix();assert 'xauthority' not in relative
            if q.is_symlink():
                target=os.readlink(q);links[relative]=target;info=zipfile.ZipInfo(relative);info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,target)
            else:
                assert stat.S_ISREG(q.lstat().st_mode);files[relative]=sha(q);z.write(q,relative)
    with zipfile.ZipFile(zp) as z:
        for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
        for n,target in links.items():assert z.read(n).decode()==target
    rp.write_bytes(p.read_bytes());records.append(dict(path=rp.relative_to(r).as_posix(),sha256=sha(rp),family=family,outcome=v['outcome'],finished_mtime=p.stat().st_mtime,archive=dict(path=zp.relative_to(r).as_posix(),sha256=sha(zp)),files=files,links=links))
# The existing recovery runner uses flat reports and public failure journals.
flat=[p for p in b.iterdir() if p.is_file() and p.stat().st_mtime>=cutoff and (p.name.startswith('RECOVERY-01-') or p.name.startswith('failure-'))]
if flat:
    zp=d/'recovery-records.zip';files={}
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(flat):files[p.name]=sha(p);z.write(p,p.name)
    with zipfile.ZipFile(zp) as z:
        for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
    records.append(dict(family='RECOVERY-01-records',archive=dict(path=zp.relative_to(r).as_posix(),sha256=sha(zp)),files=files))
(e/(prefix+'native-index.json')).write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('Preserved',len(records),'native record groups')
