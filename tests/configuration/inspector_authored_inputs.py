"""Independent maximum authored scene, exact row and coherent-generation recipes."""
import copy
import json
from installed_image_fixture import encode, sha, install, verify


def scene(mode):
    maximum = mode in ('MAX-FRAME', 'MAX-SCENE', 'OVER-FRAME', 'REOPEN', 'POLICY')
    deep = mode == 'MAX-DEPTH'
    value = dict(schema_version='0.3.0', revision='0', scene_id='scene:inspector-limits',
                 theme_id='theme:native', roots=[], widgets=[])
    expected = []
    for i in range(256):
        name = 'w' + format(i, '03d')
        group = maximum or (deep and i % 16 != 15)
        title = 'Widget ' + format(i, '03d')
        if maximum: title += 'L' * ((507 if i < 128 else 508) - len(title))
        x, y = (i % 16) * 50, (i // 16) * 32
        if deep: x, y = ((i // 16) * 50 if i % 16 == 0 else 0), 0
        widget = dict(id=name, kind='group' if group else 'text', title=title,
                      display=dict(role='primary'), layout=dict(base=dict(kind='fixed', x=x, y=y, width=50, height=32)),
                      bindings=[], priority='essential', content={} if group else dict(body='L'))
        if group: widget['children'] = ['w' + format(i + 1, '03d')] if deep else []
        if not deep or i % 16 == 0: value['roots'].append(name)
        value['widgets'].append(widget)
        expected.append([title, title if group else 'L'])
    if mode == 'OVER-FRAME':
        value['widgets'][0]['title'] += 'X'
        expected = []
    if mode in ('MAX-SCENE', 'REOPEN', 'POLICY'):
        padding = [''] * 64
        value['extensions'] = {'experiment.padding': padding}
        remaining = 262144 - len(encode(value))
        assert 0 < remaining <= 64 * 4096
        for i in range(64):
            size = min(remaining, 4096); padding[i] = 'P' * size; remaining -= size
        assert remaining == 0 and len(encode(value)) == 262144
    if maximum:
        frame_bytes = sum(len(w['id']) + len(w['kind']) + 2 * len(w['title']) for w in value['widgets'])
        assert frame_bytes == (262146 if mode == 'OVER-FRAME' else 262144)
    return value, expected


def generation(root, mode):
    initial = json.loads((root / 'tests/configuration/profile-startup-cases.json').read_bytes())
    document, expected = scene(mode)
    packages = copy.deepcopy(initial['packages'])
    theme = next(p for p in packages if 'theme.json' in p['assets'])
    scene_package = next(p for p in packages if 'scene.json' in p['assets'])
    preset_package = next(p for p in packages if 'preset.json' in p['assets'])

    def pin(package):
        manifest = json.loads(package['manifest'])
        return dict(id=manifest['package_id'], version=manifest['version'], sha256=sha(package['manifest'].encode()))

    def replace(package, kind, value, dependencies=None):
        raw = encode(value); manifest = json.loads(package['manifest'])
        manifest['assets'] = [dict(path=kind + '.json', media_type='application/json', bytes=len(raw), sha256=sha(raw))]
        manifest['total_unpacked_bytes'] = len(raw)
        if dependencies is not None: manifest['dependencies'] = dependencies
        package['assets'] = {kind + '.json': raw.decode()}; package['manifest'] = encode(manifest).decode()
        return dict(id=value[kind + '_id'], version='0.1.0', sha256=sha(raw))

    scene_pin = replace(scene_package, 'scene', document)
    preset = json.loads(preset_package['assets']['preset.json'])
    preset['scene'] = scene_pin; preset['theme'] = initial['theme_pin']
    preset_pin = replace(preset_package, 'preset', preset, [pin(theme), pin(scene_package)])
    index = dict(version='0.1.0', selection=dict(package=pin(preset_package), preset=preset_pin),
                 theme=initial['theme_pin'], packages=sorted(pin(p)['sha256'] for p in packages))
    files = {'settings.json': encode(initial['documents']['settings']), 'scene.json': encode(document), 'resources.json': encode(index)}
    files['manifest.json'] = encode(dict(version='0.5.0', revision='0', identity=None,
                                        **{name: sha(files[name + '.json']) for name in ('settings', 'scene', 'resources')}))
    for package in packages:
        raw = package['manifest'].encode(); files['resources/m-' + sha(raw) + '.json'] = raw
        for text in package['assets'].values():
            raw = text.encode(); files['resources/a-' + sha(raw) + '.bin'] = raw
    name = 'g-' + sha(files['manifest.json'])[:32]
    selector = encode(dict(version='0.1.0', generation=name, manifest=sha(files['manifest.json'])))
    return (name, selector, files), expected
