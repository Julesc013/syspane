"""Independent inputs/pixel assertions for the bounded native text backend."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'source/build'))
from check_text_runtime import verify
THEME = dict(schema_version='0.1.0', theme_id='test', name='Native text oracle',
             tokens=dict(foreground='#ffffffff', background='#00000000',
                         warning='#ff8000ff', error='#ff0000ff', muted='#808080ff'),
             font=dict(family='Noto Sans', size_dip=24), motion='none')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    exe, evidence = Path(sys.argv[1]), Path(sys.argv[2])
    folder = evidence / ('text-' + uuid.uuid4().hex[:12])
    folder.mkdir(parents=True)
    record = dict(family='TEXT-RASTER', started_at=datetime.now(timezone.utc).isoformat(),
                  executable_sha256=sha(exe), oracle_sha256=sha(Path(__file__)),
                  cases=[], outcome='fail')
    verify()
    record['runtime_identity_sha256'] = sha(ROOT/'source/build/text-runtime.json')
    counter = 0

    def run(text='SysPane', **options):
        nonlocal counter
        counter += 1
        request = dict(text=text, theme=copy.deepcopy(THEME), **options)
        raw = request.pop('raw', None)
        if 'theme_patch' in request:
            for key, value in request.pop('theme_patch').items():
                request['theme'][key] = value
        target = folder / (str(counter) + '.rgba')
        wire = raw if raw is not None else json.dumps(request, ensure_ascii=True).encode()
        p = subprocess.run([str(exe), str(target)], input=wire, capture_output=True, timeout=10)
        (folder / (str(counter) + '.input.json')).write_bytes(wire)
        (folder / (str(counter) + '.stdout')).write_bytes(p.stdout)
        (folder / (str(counter) + '.stderr')).write_bytes(p.stderr)
        assert p.returncode == 0, (p.returncode, p.stderr)
        result = json.loads(p.stdout)
        if 'error' in result:
            assert not target.exists(), 'partial raster on rejection'
            return result, b''
        data = target.read_bytes()
        assert len(data) == result['width'] * result['height'] * 4
        assert result['theme_unchanged'] is True
        assert all(max(data[i:i+3]) <= data[i+3] for i in range(0, len(data), 4))
        assert result['width'] <= 2048 and result['height'] <= 2048
        return result, data

    def case(name, check):
        check()
        record['cases'].append(dict(case=name, outcome='pass'))

    def require(value):
        assert value

    def reject(**kwargs):
        a, _ = run(**kwargs)
        assert 'error' in a, a

    def empty():
        a, p = run('')
        assert a['lines'] == 1 and a['extent'][3] > 0 and not any(p)
    def background():
        for color, expected in [('#204080ff', bytes([32, 64, 128, 255])),
                                ('#ff000080', bytes([128, 0, 0, 128]))]:
            _, p = run('', theme_patch={'tokens': dict(THEME['tokens'], background=color)})
            assert p == expected * (len(p) // 4)
    def ink():
        a, p = run('SysPane 0123456789')
        assert a['missing_glyphs'] == 0 and a['fonts'] == ['Noto Sans']
        assert 100 < sum(p[i+3] > 0 for i in range(0, len(p), 4))
        w, h = a['width'], a['height']
        assert not any(p[:w*4]) and not any(p[(h-1)*w*4:])
        assert all(not any(p[(y*w+x)*4:(y*w+x+1)*4]) for y in range(h) for x in (0, w-1))
    def alpha():
        _, p = run('MMMM', theme_patch={'tokens': dict(THEME['tokens'], foreground='#ff000080')})
        assert max(p[3::4]) == 128 and p[0::4] == p[3::4]
        assert not any(p[1::4]) and not any(p[2::4])
    def markup():
        a, _ = run('<b>Hi</b>')
        b, _ = run('Hi')
        assert a['extent'][2] > b['extent'][2] * 2
    def combining():
        a, p = run('caf\u00e9')
        b, q = run('cafe\u0301')
        assert a == b and p == q
    def bidi():
        for text in ['مرحبا بالعالم', 'SysPane مرحبا 123']:
            a, p = run(text, language='ar', wrap_units=240*64)
            assert a['missing_glyphs'] == 0 and a['lines'] == 1 and any(p)
            assert a['extent'][2] > 50*64
    def wrapping():
        a, _ = run('network throughput sample label')
        b, _ = run('network throughput sample label', wrap_units=100*64)
        c, _ = run('first\nsecond')
        assert a['lines'] == 1 and b['lines'] > 1 and c['lines'] == 2
        assert a['preferred'] == b['preferred'] and b['extent'][2] <= 101*64
    def scale():
        a, _ = run('Scale مرحبا')
        b, _ = run('Scale مرحبا', numerator=3, denominator=2)
        for name in ['extent', 'ink', 'logical', 'baseline', 'lines', 'fonts', 'preferred']:
            assert a[name] == b[name], name
        assert b['width'] == (b['extent'][2]*3+127)//128+2
        assert b['height'] == (b['extent'][3]*3+127)//128+2
    def fallback():
        a, p = run('fallback', theme_patch={'font': dict(family='SysPane Missing Family', size_dip=24)})
        assert a['missing_glyphs'] == 0 and a['fonts'] and 'SysPane Missing Family' not in a['fonts'] and any(p)
        a, p = run('\U0010ffff')
        assert a['missing_glyphs'] == 1 and any(p)
    def contrast():
        for mode, bg in [('light', 255), ('dark', 0)]:
            previous = None
            for token in ['foreground', 'warning', 'error', 'muted']:
                _, p = run('Status', token=token, contrast=mode)
                assert p[:4] == bytes([bg, bg, bg, 255]) and all(x == 255 for x in p[3::4])
                assert p[0::4] == p[1::4] == p[2::4]
                assert min(p[0::4]) == 0 and max(p[0::4]) == 255
                if previous is not None:
                    assert previous == p
                previous = p
    def tokens():
        for token, rgb in [('error',(255,0,0)), ('warning',(255,128,0)), ('muted',(128,128,128))]:
            _, p = run('MMMM', token=token)
            assert any(p[i:i+4] == bytes([*rgb,255]) for i in range(0,len(p),4))
    def color_font():
        _, p = run('\U0001f600', token='error')
        assert any(p) and not any(p[1::4]) and not any(p[2::4]) and p[0::4] == p[3::4]
    def invalid_utf8():
        a, _ = run(text_hex='f0808080')
        assert a == {'error':'text.input'}
    try:
        for name, check in [('EMPTY', empty), ('BACKGROUND', background), ('INK-BOUNDS', ink),
                            ('ALPHA', alpha), ('PLAIN-TEXT', markup), ('COMBINING', combining),
                            ('BIDI', bidi), ('WRAP', wrapping), ('SCALE', scale), ('FALLBACK', fallback),
                            ('CONTRAST', contrast), ('TOKENS', tokens),
                            ('COLOR-FONT', color_font), ('NATIVE-UTF8', invalid_utf8),
                            ('REPEAT', lambda: require(run('repeat') == run('repeat'))),
                            ('CONTROLS', lambda: [reject(text='a'+c+'b') for c in ['\x00','\t','\r','\x01','\x7f','\x85']]),
                            ('UTF8', lambda: reject(raw=b'{"text":"\xff"}')),
                            ('TEXT-LIMIT', lambda: reject(text='x'*1025)),
                            ('LINE-LIMIT', lambda: reject(text='x\n'*64)),
                            ('FONT-CONTROL', lambda: reject(theme_patch={'font':dict(family='bad\nfont',size_dip=24)})),
                            ('LANGUAGE', lambda: [reject(language=x) for x in ['', 'en_US', 'x'*36]]),
                            ('SCALE-LIMIT', lambda: [reject(numerator=n,denominator=d) for n,d in [(0,1),(17,1),(1,16),(16,1),(1,0)]]),
                            ('WRAP-LIMIT', lambda: [reject(wrap_units=x) for x in [0,63,32768*64+1]]),
                            ('RASTER-LIMIT', lambda: reject(text='W'*1024)),
                            ('BUDGET', lambda: [reject(pixel_budget=n) for n in [0,1,4194305]]),
                            ('TOKEN-LIMIT', lambda: reject(token='background')),
                            ('CONTRAST-LIMIT', lambda: reject(contrast='automatic'))]:
            case(name, check)
        verify()
        record['outcome'] = 'pass'
    except Exception as exc:
        record['error'] = repr(exc)
        raise
    finally:
        record['files'] = {p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        print(folder/'result.json', record['outcome'], len(record['cases']), flush=True)


if __name__ == '__main__':
    main()
