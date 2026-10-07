from pathlib import Path
import hashlib,json,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence').resolve()
assert str(b)=='/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence'
records=[]
for row in json.loads((r/'build-support/evidence/w-09-image-pipeline-native-index.json').read_text()):
    if row['family']!='IMAGE-DECODE':continue
    archive=r/row['archive']['path'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==row['archive']['sha256']
    directory=b/Path(row['path']).stem
    with zipfile.ZipFile(archive) as z:
        for name,digest in row['files'].items():
            if not name.endswith('.reply'):continue
            p=directory/name
            if not p.exists():continue
            assert not p.is_symlink() and p.resolve().is_relative_to(b) and p.parent.resolve()==directory.resolve()
            assert hashlib.sha256(p.read_bytes()).hexdigest()==digest==hashlib.sha256(z.read(name)).hexdigest()
            records.append(dict(removed=str(p),bytes=p.stat().st_size,sha256=digest,archive=row['archive'],member=name));p.unlink()
path=r/'out/campaign/image-reply-reclamation.json';prior=json.loads(path.read_text()) if path.exists() else []
path.write_text(json.dumps(prior+records,indent=2)+'\n');print('Reclaimed verified reply duplicates:',sum(v['bytes'] for v in records))
