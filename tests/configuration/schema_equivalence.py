"""Fixed public-validator corpus; expected outcomes come from the archived baseline.

This comparison supplements the independent schema fixtures and semantic tests.
It cannot establish correctness by itself or update its own expected results.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = Path(__file__).with_name('schema-equivalence.json')
KINDS = {'settings', 'binding', 'visibility', 'command-result', 'content-package',
         'content-catalog', 'preset', 'theme', 'theme-v0.2', 'resource-selection-v0.2'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def paths(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for key in sorted(value):
            yield from paths(value[key], path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value[:2]):
            yield from paths(child, path + (index,))


def replacement(value, path, item, remove=False):
    result = copy.deepcopy(value)
    if not path:
        return item
    parent = result
    for key in path[:-1]:
        parent = parent[key]
    if remove:
        del parent[path[-1]]
    else:
        parent[path[-1]] = copy.deepcopy(item)
    return result


def corpus():
    catalog = json.loads((ROOT / 'spec/fixtures/catalog.json').read_text())['fixtures']
    scene = json.loads((ROOT / 'spec/fixtures/valid/scene-portable.json').read_text())
    for fixture in sorted(catalog, key=lambda row: row['path']):
        schema = fixture['schema']
        if schema not in KINDS and not schema.startswith(('scene-v0.', 'command-v0.')):
            continue
        kind = schema.split('-v0.')[0]
        value = json.loads((ROOT / 'spec' / fixture['path']).read_text())
        extra = {}
        if kind == 'settings':
            extra['scene'] = copy.deepcopy(scene)
            extra['scene']['revision'] = value['revision']

        def case(label, item):
            return dict(id=fixture['path'] + ':' + label, kind=kind, value=item, **extra)

        yield case('original', value)
        if fixture['expected'] != 'valid':
            continue
        for index, (path, child) in enumerate(list(paths(value))[:32]):
            variants = [None, True, 0, [], {}, '']
            if isinstance(child, dict):
                variants += [dict(child, **{'unexpected key': 1})]
            elif isinstance(child, list):
                variants += [child + child, [None]]
            elif isinstance(child, str):
                variants += ['a' * 513, '\u00e9' * 512, '\n\t\u0000', '18446744073709551616']
            elif isinstance(child, (int, float)) and not isinstance(child, bool):
                variants += [-1, 1.5, 65536, 4294967296]
            for mutation, item in enumerate(variants):
                yield case(f'{index}/{mutation}', replacement(value, path, item))
            if path:
                yield case(f'{index}/remove', replacement(value, path, None, remove=True))


def execute(executable):
    rows = list(corpus())
    data = b''.join(encoded(row) + b'\n' for row in rows)
    assert 0 < len(rows) <= 12000 and len(data) <= 134217728
    assert all(len(encoded(row)) <= 1048576 for row in rows)
    q = subprocess.run([str(executable), '--schema-stream'], input=data,
                       capture_output=True, timeout=180)
    if q.returncode:
        raise RuntimeError(f'validator exit {q.returncode}: {q.stderr[-4096:]!r}')
    outcomes = [json.loads(line) for line in q.stdout.splitlines()]
    assert [r['id'] for r in rows] == [r['id'] for r in outcomes]
    groups = {}
    for row in outcomes:
        groups.setdefault(row['id'].split(':')[0], []).append(row)
    return dict(cases=len(rows), input_bytes=len(data), input_sha256=digest(data),
                output_sha256=digest(encoded(outcomes)),
                groups={name: dict(cases=len(items), accepted=sum(r['outcome'] == 'accepted' for r in items),
                                   sha256=digest(encoded(items))) for name, items in groups.items()}), data, q.stdout


def main():
    actual, _, _ = execute(Path(sys.argv[1]))
    expected = json.loads(EXPECTED.read_text())['results']
    if actual != expected:
        differing = [name for name in set(actual['groups']) | set(expected['groups'])
                     if actual['groups'].get(name) != expected['groups'].get(name)]
        raise AssertionError(f'frozen schema outcomes changed: {differing}')
    print(f"{actual['cases']} frozen public-validator outcomes match")


if __name__ == '__main__':
    main()
