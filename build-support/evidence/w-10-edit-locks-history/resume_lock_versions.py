from pathlib import Path
s=Path('out/campaign/implement_lock_versions.py').read_text()
exec(s[:s.index("edit('CMakeLists.txt'")]+s[s.index('for subject in '):].replace("('value.documents','next.documents')","('next.documents',)",1))
