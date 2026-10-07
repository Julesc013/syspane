from pathlib import Path
import hashlib,json
r=Path('/mnt/d/Projects/SysPane/syspane');p=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence/editor-idle-788c47e77043')
v=json.loads((p/'result.json').read_bytes());rows=[]
for case in v['cases']:
 detail=json.loads((p/case['case']/'result.json').read_bytes());capture=[]
 for n in case['traces']:
  raw=(p/n).read_bytes();data=[x.split('\t') for x in raw.decode().splitlines()]
  refresh=[x for x in data if x[0].startswith('refresh-')];assert len(refresh)==1
  mismatch=[x for x in data if x[0]=='sample' and x[3:5]==['1','0']]
  capture.append(dict(path=n,sha256=hashlib.sha256(raw).hexdigest(),max_idle_us=max(int(x[5]) for x in data),paints=int(data[-1][6]),mismatches=len(mismatch),rows=data))
 if case['slow'] and case['priority']=='default':
  assert case['exit']!=0 and detail['outcome']=='fail' and detail['error'].endswith('observation deadline')
  target='editor.'+detail['focus_failure']['control'];matching=[x for c in capture for x in c['rows'] if x[0]=='sample' and x[2]==target and x[3:5]==['1','0']]
  assert int(matching[-1][1])-int(matching[0][1])>=2000000 and int(matching[-1][6])>int(matching[0][6]) and max(int(x[5]) for x in matching)>3000000
 else:assert case['exit']==0 and detail['outcome']=='pass'
 rows.append(dict(case=case['case'],observed=case['outcome'],traces=[{k:v for k,v in c.items() if k!='rows'} for c in capture]))
out=r/'out/campaign/focus-idle/diagnostic-analysis.json'
out.write_text(json.dumps(dict(outcome='supported',source_ref=v['source_ref'],record=str(p/'result.json'),record_sha256=hashlib.sha256((p/'result.json').read_bytes()).hexdigest(),cases=rows,conclusion='Bounded drawing cost reproduces real GTK focus with stale ATK focus and multi-second normal-idle starvation while drawing continues. Changing only the periodic refresh priority permits the same existing keyboard/scene/pixel/storage checks to pass. This isolates a scheduling defect; it does not prove every earlier interface/focus failure had the same cause.',sources=['https://docs.gtk.org/glib/main-loop.html','https://docs.gtk.org/glib/func.timeout_add_full.html','https://docs.gtk.org/gdk3/func.threads_add_idle.html']),indent=2)+'\n')
print(out)
