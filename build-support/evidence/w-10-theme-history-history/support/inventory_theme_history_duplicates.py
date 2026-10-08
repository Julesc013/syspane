from pathlib import Path
import json
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
rows=[];seen=set()
for p in (r/'build-support/evidence').glob('*-native-index.json'):
 if 'w-10-theme-history' in p.name:continue
 values=json.loads(p.read_bytes())
 if not isinstance(values,list):continue
 for item in values:
  if 'archive' not in item:continue
  d=b/Path(item['archive']['path']).stem
  if d in seen or not d.is_dir():continue
  seen.add(d);rows.append((sum(x.lstat().st_size for x in d.rglob('*') if x.is_file() or x.is_symlink()),str(d),str(p)))
print(json.dumps(sorted(rows,reverse=True)[:25],indent=2))
