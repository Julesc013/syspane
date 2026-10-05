"""Compare actual configured CMake targets with the declared component boundary."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def check(graph, manifest):
    owners = {row['target']: row for row in manifest['components']}
    errors = []
    if set(graph) != set(owners):
        errors.append('configured component set differs from manifest')
    installed = set()
    for name, (kind, dependencies, sources) in graph.items():
        if name not in owners:
            continue
        row = owners[name]
        if kind != row['type'] or set(sources) != set(row['sources']):
            errors.append(name + ': target type/source ownership differs')
        if not set(dependencies) <= set(row['allowed_dependencies']):
            errors.append(name + ': forbidden dependency')
        for source in sources:
            if not source.startswith(row['source_owner']) or not (ROOT / source).is_file():
                errors.append(name + ': unowned/missing source')
        for path in row['installed_files']:
            if path in installed:
                errors.append('duplicate installed-file owner: ' + path)
            installed.add(path)
    return errors

def main():
    graph = {}
    for line in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines():
        name, kind, dependencies, sources = line.split('|')
        if name in graph:
            raise ValueError('duplicate target')
        graph[name] = (kind, list(filter(None, dependencies.split(';'))), sources.split(';'))
    manifest = json.loads((ROOT / 'build-support/components.json').read_text(encoding='utf-8'))
    errors = check(graph, manifest)
    if errors:
        raise ValueError('; '.join(errors))
    if '--negative-test' in sys.argv:
        kind, dependencies, sources = graph['syspane_model']
        graph['syspane_model'] = (kind, dependencies + ['syspane_model_smoke'], sources)
        assert 'syspane_model: forbidden dependency' in check(graph, manifest), 'forbidden edge went undetected'
    print('component graph: pass')

if __name__ == '__main__':
    main()
