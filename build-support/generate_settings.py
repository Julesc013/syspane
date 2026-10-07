"""Generate the bounded native descriptor table from the canonical registry."""
import hashlib
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'spec/experience/settings-registry.json'
    registry = json.loads(source.read_text(encoding='utf-8'))
    rows = []
    seen = set()
    for setting in registry['settings']:
        name, c = setting['id'], setting['constraints']
        if name in seen or not setting['user_editable'] or not setting['preview'] or setting['command'] != 'settings.set':
            raise ValueError('unsupported descriptor metadata; close native semantics before generation')
        seen.add(name)
        if c['type'] == 'integer' and set(c) == {'type', 'minimum', 'maximum'}:
            if not 0 <= c['minimum'] <= c['maximum'] <= 2**53 - 1:
                raise ValueError('unsupported descriptor bounds')
            kind, low, high = 'integer', c['minimum'], c['maximum']
        elif c == {'type': 'boolean'}:
            kind, low, high = 'boolean', 0, 0
        elif c == {'type': 'string', 'minLength': 1, 'maxLength': 256, 'pattern': '^[A-Za-z0-9][A-Za-z0-9:._/-]*$'}:
            kind, low, high = 'identifier', 0, 0
        else:
            raise ValueError('unsupported descriptor constraint; do not silently weaken it')
        metadata = [setting[k] for k in ('native_page','units','activation','label_id','help_id','label','help')]
        if any(not isinstance(v,str) or not v or len(v.encode('utf-8'))>2048 or any(ord(c)<32 for c in v) for v in metadata):
            raise ValueError('unsupported native descriptor text')
        default = setting['default']
        if ((kind=='boolean' and type(default) is not bool) or
            (kind=='integer' and (type(default) is not int or not low<=default<=high)) or
            (kind=='identifier' and (not isinstance(default,str) or not 1<=len(default)<=256 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:._/-]*',default)))):
            raise ValueError('invalid native descriptor default')
        extra = ', '.join(json.dumps(v) for v in [json.dumps(default,separators=(',',':')),*metadata])
        rows.append(f'    Descriptor{{{json.dumps(name)}, Kind::{kind}, {low}ULL, {high}ULL, {extra}}}')
    if not rows:
        raise ValueError('empty registry')
    text = '// Generated; input SHA256 ' + hashlib.sha256(source.read_bytes()).hexdigest() + '\n'
    text += '#pragma once\n#include <array>\n#include <cstdint>\nnamespace syspane::configuration {\n'
    text += 'enum class Kind { integer, boolean, identifier };\n'
    text += 'struct Descriptor { const char* path; Kind kind; std::uint64_t minimum, maximum; const char* default_json; const char* page; const char* units; const char* activation; const char* label_id; const char* help_id; const char* label; const char* help; };\n'
    text += f'inline constexpr std::array<Descriptor, {len(rows)}> descriptors = {{\n' + ',\n'.join(rows) + '\n};\n}\n'
    destination = Path(sys.argv[1])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.read_text(encoding='utf-8') != text:
        destination.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
