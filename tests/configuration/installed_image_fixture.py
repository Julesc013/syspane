"""Independent deterministic saved-generation recipe; never reads product output."""
import copy
import hashlib
import json
import struct
import zlib

encode = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def recipe(root, cases, mode):
    initial = json.loads((root / cases['initial_documents']).read_bytes())
    image = (root / 'tests/scene/image-cases/rgba.png').read_bytes()
    if mode == 'DECODE-FAILURE':
        image = image[:-1]
    elif mode in ('MAXIMUM', 'OVERSIZE', 'HELD-NAVIGATION', 'HELD-CLOSE'):
        size = cases['encoded_limit'] + (mode == 'OVERSIZE')
        data = b'pad\0' + b'x' * (size - len(image) - 16)
        chunk = b'tEXt' + data
        image = image[:33] + struct.pack('!I', len(data)) + chunk + struct.pack('!I', zlib.crc32(chunk) & 0xffffffff) + image[33:]
        assert len(image) == size
    resources = {}

    def package(kind, document, dependencies=(), extra=None):
        assets = {kind + '.json': encode(document)}
        if extra: assets.update(extra)
        manifest = dict(schema_version='0.1.0', package_id='package:installed-' + kind,
                        version='0.1.0', kind=kind, license='LicenseRef-SysPane-Pending',
                        dependencies=list(dependencies), required_capabilities=[], optional_capabilities=[],
                        assets=[dict(path=name, media_type='image/png' if name == 'image.data' else 'application/json',
                                     sha256=sha(raw), bytes=len(raw)) for name, raw in sorted(assets.items())],
                        total_unpacked_bytes=sum(map(len, assets.values())))
        raw = encode(manifest)
        resources['m-' + sha(raw) + '.json'] = raw
        for data in assets.values(): resources['a-' + sha(data) + '.bin'] = data
        return (dict(id=manifest['package_id'], version='0.1.0', sha256=sha(raw)),
                dict(id=document[kind + '_id'], version='0.1.0', sha256=sha(assets[kind + '.json'])))

    theme = next(json.loads(p['assets']['theme.json']) for p in initial['packages'] if 'theme.json' in p['assets'])
    theme_package, theme_pin = package('theme', theme, extra={'image.data': image})
    x, y, width, height = cases['rectangle']
    scene = dict(schema_version='0.3.0', revision='0', scene_id='scene:installed-image', theme_id=theme['theme_id'],
                 roots=[cases['widget']], widgets=[dict(id=cases['widget'], kind='image', title=cases['title'],
                 display=dict(role='primary'), layout=dict(base=dict(kind='fixed', x=x, y=y, width=width, height=height)),
                 bindings=[], priority='essential', content=dict(asset=dict(package=theme_package, path='image.data', sha256=sha(image)),
                 alt=cases['alt'], width_dip=cases['content_extent'][0], height_dip=cases['content_extent'][1], fit='contain'))])
    scene_package, scene_pin = package('scene', scene)
    preset = dict(schema_version='0.1.0', preset_id='preset:installed-image', version='0.1.0', parent=None,
                  scene=scene_pin, theme=theme_pin, settings=[], required_capabilities=[], optional_capabilities=[])
    preset_package, preset_pin = package('preset', preset, [theme_package, scene_package])
    index = dict(version='0.1.0', selection=dict(package=preset_package, preset=preset_pin), theme=theme_pin,
                 packages=sorted(p['sha256'] for p in (theme_package, scene_package, preset_package)))
    files = {'settings.json': encode(copy.deepcopy(initial['documents']['settings'])),
             'scene.json': encode(scene), 'resources.json': encode(index)}
    files['manifest.json'] = encode(dict(version='0.5.0', revision='0', identity=None,
                                        **{key: sha(files[key + '.json']) for key in ('settings', 'scene', 'resources')}))
    files.update({'resources/' + name: raw for name, raw in resources.items()})
    generation = 'g-' + sha(files['manifest.json'])[:32]
    selector = encode(dict(version='0.1.0', generation=generation, manifest=sha(files['manifest.json'])))
    return generation, selector, files


def install(generations, fixture):
    generation, selector, files = fixture
    target = generations / generation
    target.mkdir(mode=0o700)
    (target / 'resources').mkdir(mode=0o700)
    for name, raw in files.items():
        path = target / name
        path.write_bytes(raw)
        path.chmod(0o600)
    (generations / 'current.json').write_bytes(selector)
    (generations / 'current.json').chmod(0o600)


def verify(generations, fixture):
    generation, selector, files = fixture
    assert (generations / 'current.json').read_bytes() == selector
    target = generations / generation
    assert {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob('*') if p.is_file()} == files
