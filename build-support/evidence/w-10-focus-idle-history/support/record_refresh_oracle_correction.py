from pathlib import Path
import hashlib,json
r=Path.cwd();out=r/'out/campaign/focus-idle';fixed=json.loads((out/'fixed-regression.json').read_bytes())
paths=['tests/editor/native_refresh.py','tests/editor/refresh_probe_linux.cpp'];record=out/'oracle-correction.json';assert not record.exists()
v=dict(original_failure='editor-refresh-84cbbd11f7d7',old={p:fixed['inputs'][p] for p in paths},new={p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in paths},unchanged_fixture_sha256=fixed['inputs']['tests/editor/refresh-cases.json'],reason='The unchanged native keyboard/scene/pixel/history/storage oracle passed, but the new auxiliary 50 ms sampler missed the short focused state before Undo disabled itself. Record the actual ATK state query and simultaneous real GTK focus instead of requiring a timed sample to coincide. Preserve the original failure. The required focused-state conjunction, deadlines, fixed scenes, workload and production source do not change.')
record.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
