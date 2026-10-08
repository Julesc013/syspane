"""Compare actual configured CMake targets with the declared component boundary."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

def check(graph, manifest, profile):
    profiles = {'windows-x64-gcc15', 'linux-x64-gcc13', 'windows-x86-v141-xp'}
    if profile not in profiles:
        raise ValueError('unknown component profile')
    for row in manifest['components']:
        if 'profiles' in row and (not row['profiles'] or not set(row['profiles']) <= profiles):
            raise ValueError('invalid component profile selector')
    owners = {row['target']: row for row in manifest['components']
              if profile in row.get('profiles', ['windows-x64-gcc15', 'linux-x64-gcc13'])}
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
    manifest = json.loads((ROOT / 'source/build/components.json').read_text(encoding='utf-8'))
    profile = json.loads((Path(sys.argv[1]).parent/'.syspane-owner.json').read_text(encoding='utf-8'))['profile']
    errors = check(graph, manifest, profile)
    if errors:
        raise ValueError('; '.join(errors))
    if '--negative-test' in sys.argv:
        kind, dependencies, sources = graph['syspane_model']
        graph['syspane_model'] = (kind, dependencies + ['syspane_model_smoke'], sources)
        assert 'syspane_model: forbidden dependency' in check(graph, manifest, profile), 'forbidden edge went undetected'
        wrong_profile = 'linux-x64-gcc13' if profile == 'windows-x64-gcc15' else 'windows-x64-gcc15'
        assert 'configured component set differs from manifest' in check(graph, manifest, wrong_profile), 'profile-specific component omission/addition went undetected'
    print('component graph: pass')

if __name__ == '__main__':
    main()
