from pathlib import Path
r=Path.cwd();old='w-10-editor-draft';new='w-10-native-editor';base='c225a32823682b904e624d295b694d233accb773'
def write(n,s):(r/'out/campaign'/n).write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/archive_editor.py').read_text().replace(old,new).replace("('SETTINGS-FORM','SCENE-INSPECTOR'","('EDITOR-FORM','SETTINGS-FORM','SCENE-INSPECTOR'")
at=s.index('flat=[p for p in b.iterdir()')
s=s[:at]+'''for p in sorted(b.glob('EDITOR-EXIT-01-*.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());folder=p.with_suffix('');zp=d/(folder.name+'.zip');rp=d/p.name;meta=d/(folder.name+'.index.json')
 if meta.exists():
  item=json.loads(meta.read_text());assert sha(zp)==item['archive']['sha256'] and sha(p)==item['record_sha256'];records.append(item);continue
 files={};modes={}
 with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
  for q in sorted(folder.rglob('*')):
   if not q.is_file() or q.name=='xauthority':continue
   assert not q.is_symlink();n=q.relative_to(folder).as_posix();files[n]=sha(q);modes[n]=stat.S_IMODE(q.stat().st_mode);z.write(q,n)
  files['result.json']=sha(p);z.write(p,'result.json')
 with zipfile.ZipFile(zp) as z:
  for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 rp.write_bytes(p.read_bytes());item={'path':rp.relative_to(r).as_posix(),'sha256':sha(rp),'record_sha256':sha(p),'family':'EDITOR-EXIT-01','outcome':v['result'],
  'finished_mtime':p.stat().st_mtime,'archive':{'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},'files':files,'links':{},'modes':modes,'post_report_differences':{}}
 meta.write_text(json.dumps(item,indent=2)+'\\n',encoding='utf-8');records.append(item)
(e/(prefix+'native-index.json')).write_text(json.dumps(records,indent=2)+'\\n',encoding='utf-8')
print('Archived and verified',len(records),'completed native records.')
'''
write('archive_native_editor.py',s)
s=(r/'out/campaign/finish_editor_checks.py').read_text().replace(old,new).replace('10765b6a65b9fe3e13e7e255fba2b91758107d0b',base)
write('finish_native_editor_checks.py',s)
