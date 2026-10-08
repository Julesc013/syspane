"""Verify the pinned vendored inputs offline; never download during configure."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    record = json.loads((ROOT/'source/build/dependencies.json').read_text(encoding='utf-8'))
    for dependency in record['dependencies']:
        for name, expected in dependency['files'].items():
            path = (ROOT/name).resolve()
            if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('dependency digest mismatch: ' + name)
    print('vendored dependency digests: pass')


if __name__ == '__main__':
    main()
