"""Generate the bounded native descriptor table from the canonical registry."""
import hashlib
import json
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
        rows.append(f'    Descriptor{{{json.dumps(name)}, Kind::{kind}, {low}ULL, {high}ULL}}')
    if not rows:
        raise ValueError('empty registry')
    text = '// Generated; input SHA256 ' + hashlib.sha256(source.read_bytes()).hexdigest() + '\n'
    text += '#pragma once\n#include <array>\n#include <cstdint>\nnamespace syspane::configuration {\n'
    text += 'enum class Kind { integer, boolean, identifier };\n'
    text += 'struct Descriptor { const char* path; Kind kind; std::uint64_t minimum, maximum; };\n'
    text += f'inline constexpr std::array<Descriptor, {len(rows)}> descriptors = {{\n' + ',\n'.join(rows) + '\n};\n}\n'
    destination = Path(sys.argv[1])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.read_text(encoding='utf-8') != text:
        destination.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
