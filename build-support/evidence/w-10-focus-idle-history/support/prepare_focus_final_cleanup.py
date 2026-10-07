from pathlib import Path
r=Path.cwd();source=r/'out/campaign/prune_focus_idle_duplicates.py';s=source.read_text()
s=s.replace("for prefix in ('w-10-edit-locks',):", "for prefix in ('w-10-containers','w-10-modal-focus','w-10-layout-authoring','w-10-native-observation','w-09-scene-images','w-09-image-pipeline'):")
s=s.replace("data=git(index);assert data==(r/index).read_bytes()", "\n if not (r/index).exists():continue\n data=git(index);assert data==(r/index).read_bytes()")
s=s.replace("archive=entry['archive'];zp=r/archive['path'];assert sha(git(archive['path']))==sha(zp.read_bytes())==archive['sha256']", "archive=entry['archive'];zp=r/archive['path']")
s=s.replace("seen.add(folder);assert folder.resolve().parent==base and not folder.is_symlink()", "seen.add(folder);assert folder.resolve().parent==base and not folder.is_symlink()\n  assert sha(git(archive['path']))==sha(zp.read_bytes())==archive['sha256']")
s=s.replace('focus-idle-pruned-duplicates.json','focus-idle-final-pruned-duplicates.json')
s=s.replace('assert rows\nrecord=', 'assert rows\nchosen=[]\nfor row in sorted(rows,key=lambda x:-x["bytes"]):\n chosen.append(row)\n if sum(x["bytes"] for x in chosen)>=512*1024*1024:break\nrows=chosen\nrecord=')
(r/'out/campaign/prune_focus_idle_final_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
