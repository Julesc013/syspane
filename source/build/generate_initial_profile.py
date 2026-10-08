"""Embed authored product defaults; generated output stays in the owned build root."""
from pathlib import Path
import hashlib, json, sys

root = Path(__file__).resolve().parents[2]
source = root / 'configuration/defaults/profile.json'
raw = source.read_bytes()
assert len(raw) <= 32768
value = json.loads(raw)
assert set(value) == {'scene', 'theme'}
body = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
text = '// Generated from configuration/defaults/profile.json; SHA256 ' + hashlib.sha256(raw).hexdigest() + '\n'
text += '#pragma once\nnamespace syspane::configuration {\n'
text += 'inline constexpr const char* initial_profile_json = ' + json.dumps(body) + ';\n}\n'
destination = Path(sys.argv[1])
destination.parent.mkdir(parents=True, exist_ok=True)
if not destination.exists() or destination.read_text(encoding='utf-8') != text:
    destination.write_text(text, encoding='utf-8', newline='\n')
