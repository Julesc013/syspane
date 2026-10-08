"""Literal font requests, native private controls and independent stored bytes."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import uuid
import zlib
from native_editor import Harness, ROOT, sha, stored, launch_xvfb
from native_layout_authoring import LayoutHarness
from native_visibility_controls import field as input_field, choose as input_choose, chosen as input_chosen
from native_large_commands import generation
from native_theme_commands import BASE, FIXTURE
from native_observation import PREFIX

CASES = json.loads((ROOT/'tests/editor/theme-controls-cases.json').read_bytes())
TARGETS = ['Base', 'Body', 'Label', 'Value', 'Diagnostic']
MODES = ['Use base font for all roles', 'Customize roles']


class FontHarness(LayoutHarness):
    def __init__(self, exe, exit_exe, text_exe, folder, mode):
        Harness.__init__(self, exe, exit_exe, folder, mode, fonts=True)
        self.text_exe = text_exe
        self.rasters = {}


def field(h, key, value):
    input_field(h, key, value, 'theme.')


def choose(h, key, index, label):
    input_choose(h, key, index, label, 'theme.')


def chosen(h, key):
    return input_chosen(h, key, 'theme.')


def open_fonts(h):
    h.click('fonts')
    h.wait(lambda: h.find('theme.set') and h.state(h.find('theme.set'), h.Atspi.StateType.SHOWING) and h.sensitive('theme.set') and not h.sensitive('fonts'))
    assert not h.sensitive('fonts') and not h.sensitive('apply')


def finish_modal(h, action='set'):
    held = [h.find('theme.'+key) for key in ('family', 'size', 'weight', 'error', 'note')]
    for obj in held:
        assert PREFIX+'Text' in h.observer.interfaces(obj)
    h.focus('theme.'+action)
    issued = time.monotonic()
    h.input.press(0x20)
    await_erasure(h, held, issued)
    h.report.setdefault('modal_erasure_ms', []).append((time.monotonic()-issued)*1000)
    h.wait(lambda: h.sensitive('fonts'))
    h.input.focus(h.pid)


def await_erasure(h, held, issued):
    # These live text objects were positively identified before the stimulus.
    # Dispatch independent reads together, so intervening paints do not turn five
    # observations into five render intervals. Every explicit reply shares 200 ms.
    from gi.repository import Gio, GLib
    end = issued+.2
    while True:
        replies = {}
        errors = []
        def complete(connection, result, index):
            try:
                replies[index] = connection.call_finish(result).unpack()[0]
            except GLib.GError as error:
                errors.append(str(error))
                replies[index] = None
        for index, obj in enumerate(held):
            name, path = h.observer.identity(obj)
            remaining = int((end-time.monotonic())*1000)
            assert remaining > 0, 'private erasure deadline before query'
            h.observer.bus.call(name, path, PREFIX+'Text', 'GetText', GLib.Variant('(ii)', (0, -1)), GLib.VariantType.new('(s)'), Gio.DBusCallFlags.NONE, remaining, None, complete, index)
        h.wait(lambda: len(replies) == len(held), max(.001, end-time.monotonic()))
        assert not errors, errors
        if all(value == '' for value in replies.values()):
            assert time.monotonic() <= end
            return


def populate(h, font):
    for key, value in [('family', font['family']), ('size', font['size_dip']), ('weight', font['weight'])]:
        field(h, key, value)
    styles = ['normal', 'italic', 'oblique']
    if chosen(h, 'style') != font['style']:
        choose(h, 'style', styles.index(font['style']), font['style'])


def stage(h, key):
    open_fonts(h)
    theme = CASES['artifacts'][key]['theme']
    populate(h, theme['font'])
    if 'font_roles' in theme:
        choose(h, 'mode', 1, MODES[1])
        for role, font in theme['font_roles'].items():
            choose(h, 'target', TARGETS.index(role.title()), role.title())
            h.click('theme.enabled')
            h.wait(lambda: h.sensitive('theme.family'))
            populate(h, font)
    finish_modal(h)


def literal_raster(h, key, kind):
    cache_key = (key, kind)
    if cache_key in h.rasters:
        return h.rasters[cache_key]
    theme = CASES['artifacts'][key]['theme']
    blocks = [dict(role='body', text=CASES['body_text'])] if kind == 'body' else CASES['value_blocks']
    parts = []
    for index, block in enumerate(blocks):
        expected = copy.deepcopy(theme)
        expected['font'] = theme.get('font_roles', {}).get(block['role'], theme['font'])
        expected.pop('font_roles', None)
        if kind != 'body':
            expected['tokens']['background'] = '#00000000'
        stem = h.folder/(key+'-'+kind+'-'+str(index))
        wire = json.dumps(dict(text=block['text'], theme=expected, numerator=1, denominator=1)).encode()
        stem.with_suffix('.input.json').write_bytes(wire)
        result = subprocess.run([str(h.text_exe), str(stem.with_suffix('.rgba'))], input=wire, capture_output=True, timeout=10)
        stem.with_suffix('.stdout').write_bytes(result.stdout)
        stem.with_suffix('.stderr').write_bytes(result.stderr)
        assert result.returncode == 0, result.stderr
        info = json.loads(result.stdout)
        assert 'error' not in info and info['missing_glyphs'] == 0
        parts.append((info['width'], info['height'], stem.with_suffix('.rgba').read_bytes()))
    if kind == 'body':
        w, height, data = parts[0]
        rgb = b''.join(data[n:n+3] for n in range(0, len(data), 4))
        h.rasters[cache_key] = (w, height, rgb)
        return w, height, rgb
    width = max(p[0] for p in parts)
    height = sum(p[1] for p in parts)+4*(len(parts)-1)
    rgba = bytes.fromhex(theme['tokens']['background'][1:])
    bg = bytes([(c*rgba[3]+127)//255 for c in rgba[:3]]+[rgba[3]])
    data = bytearray(bg*width*height)
    y = 0
    for w, rows, src in parts:
        for row in range(rows):
            for col in range(w):
                a = (row*w+col)*4
                b = ((y+row)*width+col)*4
                for channel in range(4):
                    data[b+channel] = src[a+channel]+(data[b+channel]*(255-src[a+3])+127)//255
        y += rows+4
    rgb = b''.join(data[n:n+3] for n in range(0, len(data), 4))
    h.rasters[cache_key] = (width, height, rgb)
    return width, height, rgb


def pixels(h, key):
    for kind, x, y in [('body', 40, 40), ('value', 280, 180)]:
        w, height, expected = literal_raster(h, key, kind)
        h.wait(lambda: h.pixels(x, y, w, height) == expected)
        (h.folder/(key+'-'+kind+'.rgb.z')).write_bytes(zlib.compress(expected))
    h.wait(lambda: '80 byte' in h.text(h.find('canvas')) and 'Current' in h.text(h.find('canvas')))


def exact_store(h, key, revision='41'):
    scene = CASES['authored']['scene'] if key is None else CASES['scenes'][key]
    assert stored(h.directory) == h.documents(scene, revision), 'stored documents differ'
    g, m = generation(h.directory)
    assert m['version'] == '0.4.0' and m['revision'] == revision
    assert sha(g/'request.json') == m['identity']['body_sha256']
    assert sha(g/'resources.json') == m['resources']
    index = json.loads((g/'resources.json').read_bytes())
    files = {}
    for digest, package in BASE.items():
        files['m-'+digest+'.json'] = package['manifest'].encode()
        for raw in package['assets_hex'].values():
            raw = bytes.fromhex(raw)
            files['a-'+hashlib.sha256(raw).hexdigest()+'.bin'] = raw
    artifact = None if key is None else CASES['artifacts'][key]
    if artifact:
        files['m-'+artifact['package_pin']['sha256']+'.json'] = artifact['manifest'].encode()
        files['a-'+artifact['theme_pin']['sha256']+'.bin'] = artifact['asset'].encode()
    assert index == dict(version='0.2.0', selection=CASES['base_selection'] if key is None else CASES['selections'][key], theme=FIXTURE['themes']['theme:native'] if key is None else artifact['theme_pin'], packages=sorted([*BASE]+([] if key is None else [artifact['package_pin']['sha256']])))
    assert {p.name: p.read_bytes() for p in (g/'resources').iterdir()} == files, 'stored resource bytes differ'
    body = json.loads((g/'request.json').read_bytes())
    assert body['schema_version'] == '0.8.0'
    if key is None:
        assert body['theme_edit'] is None
    else:
        assert body['theme_edit']['font'] == artifact['theme']['font']
        assert body['theme_edit']['font_roles'] == artifact['theme'].get('font_roles')
    h.report['observations'].append(dict(revision=revision, selection=index['selection'], manifest_sha256=sha(g/'manifest.json')))


def submit(h, key, revision='41'):
    h.stage = 'SUBMIT'
    h.click('apply')
    submitted = h.event('event', 'submitted')['body']
    assert submitted['schema_version'] == '0.8.0'
    h.event('event', 'held')
    assert not h.sensitive('fonts') and not h.sensitive('apply')
    if h.mode == 'cancel-request':
        h.click('cancel-request')
        h.event('event', 'cancel-requested')
    if h.mode == 'deny':
        h.command('deny-font')
    h.command('release')
    result = h.event('event', 'result')['result']
    if h.mode in ('cancel-request', 'deny'):
        h.check()
        if h.mode == 'deny':
            assert result['outcome'] == 'unknown' and result['error']['code'] == 'policy.denied'
            assert all(result[k] is None for k in ('revision', 'stored', 'durable', 'visible'))
            assert not h.sensitive('fonts')
            w, height, expected = literal_raster(h, key, 'body')
            h.wait(lambda: h.pixels(40, 40, w, height) == expected)
            h.command('regrant')
            h.command('retrieve')
            result = h.event('event', 'retrieved')['result']
        assert result['outcome'] == ('cancelled' if h.mode == 'cancel-request' else 'conflict') and result['revision'] == '40'
        return False
    assert result['outcome'] == 'accepted' and result['revision'] == revision and result['durable'] and not result['visible']
    h.stage = 'STORE'
    if h.mode == 'wrong-font':
        g, m = generation(h.directory)
        actual = json.loads((g/'request.json').read_bytes())
        assert m['revision'] == '41' and actual['theme_edit']['font']['weight'] == 900
        assert actual['theme_edit']['font'] != CASES['artifacts']['base']['theme']['font']
        detected = False
        try:
            exact_store(h, 'base')
        except AssertionError:
            detected = True
        assert detected
        h.report['fault_detected'] = True
        return False
    exact_store(h, key, revision)
    if h.mode == 'restart':
        h.wait(lambda: 'Outcome unknown' in h.status())
        selector = (h.directory/'current.json').read_bytes()
        h.command('restart')
        h.event('event', 'reconciled')
        assert (h.directory/'current.json').read_bytes() == selector
    h.wait(lambda: 'Saved durably' in h.status())
    return True


def reopen(h, key, revision='41'):
    h.command('quit')
    assert h.proc.wait(timeout=5) == 0
    h.launch('reopen')
    exact_store(h, key, revision)
    if key:
        pixels(h, key)
    open_fonts(h)
    theme = CASES['source'] if key is None else CASES['artifacts'][key]['theme']
    assert chosen(h, 'mode') == MODES[int('font_roles' in theme)]
    for index, target in enumerate(TARGETS):
        if index:
            choose(h, 'target', index, target)
        expected = theme.get('font_roles', {}).get(target.lower(), theme['font'])
        assert h.text(h.find('theme.family')) == expected['family']
        assert float(h.text(h.find('theme.size'))) == expected['size_dip']
        assert int(h.text(h.find('theme.weight'))) == expected.get('weight', 400)
        assert chosen(h, 'style') == expected.get('style', 'normal')
        assert h.state(h.find('theme.enabled'), h.Atspi.StateType.CHECKED) == (target.lower() in theme.get('font_roles', {}))
    finish_modal(h, 'cancel')


def erasure(h):
    if h.mode == 'capability-loss':
        stage(h, 'base')
        pixels(h, 'base')
    open_fonts(h)
    field(h, 'family', 'Private font family')
    field(h, 'size', 'invalid private size')
    h.click('theme.set')
    h.wait(lambda: 'Fonts could not be set' in h.text(h.find('theme.error')))
    held = [h.find('theme.'+key) for key in ('family', 'size', 'weight', 'error', 'note')]
    for obj in held:
        assert PREFIX+'Text' in h.observer.interfaces(obj)
    h.Atspi.EditableText.copy_text(held[0].get_editable_text_iface(), 0, 7)
    assert h.Gtk.Clipboard.get(h.Gdk.SELECTION_PRIMARY).wait_for_text() is None
    assert h.Gtk.Clipboard.get(h.Gdk.SELECTION_CLIPBOARD).wait_for_text() is None
    h.stage = 'ERASE'
    issued = h.command('revoke' if h.mode == 'retain-font' else h.mode)
    await_erasure(h, held, issued)
    h.report['erase_ms'] = (time.monotonic()-issued)*1000
    assert h.report['erase_ms'] <= CASES['erase_ms']
    exposed = [h.text(o) for o in h.objects() if 'Private font family' in h.text(o)]
    if h.mode == 'retain-font':
        assert exposed == ['Retained font canary Private font family']
        h.report['fault_detected'] = True
    else:
        assert not exposed
    h.check()
    if h.mode in ('revoke', 'capability-loss', 'retain-font'):
        h.wait(lambda: set(h.pixels(0, 0, 500, 420)) == {0})
        h.command('regrant')
        assert not h.sensitive('fonts') and all(h.erased(o) for o in held)
    elif h.mode in ('policy', 'topology'):
        open_fonts(h)
        assert h.text(h.find('theme.family')) == CASES['source']['font']['family']
        finish_modal(h, 'cancel')


def exercise(h):
    h.launch()
    h.check()
    h.wait(lambda: '80 byte' in h.text(h.find('canvas')))
    baseline = h.pixels(40, 40, 180, 80)
    assert len(set(baseline)) > 2 and h.sensitive('fonts')
    h.screenshot('initial')
    if h.mode in ('revoke', 'capability-loss', 'policy', 'disconnect', 'topology', 'close', 'retain-font'):
        erasure(h)
    elif h.mode == 'noop':
        open_fonts(h)
        finish_modal(h)
        assert not h.sensitive('apply') and not h.sensitive('undo')
        open_fonts(h)
        field(h, 'family', 'Private cancelled font')
        finish_modal(h, 'cancel')
        h.check()
    else:
        key = h.mode if h.mode in ('base', 'roles', 'empty') else 'base'
        if h.mode == 'frozen-preview':
            h.command('freeze-preview')
        h.stage = 'BUFFER'
        if h.mode == 'invalid':
            open_fonts(h)
            field(h, 'size', 'NaN')
            h.click('theme.set')
            h.wait(lambda: 'Fonts could not be set' in h.text(h.find('theme.error')))
            assert h.text(h.find('theme.size')) == 'NaN' and not h.sensitive('apply')
            choose(h, 'mode', 1, MODES[1])
            choose(h, 'target', 1, 'Body')
            h.click('theme.enabled')
            field(h, 'family', '')
            choose(h, 'target', 0, 'Base')
            assert h.text(h.find('theme.size')) == 'NaN'
            populate(h, CASES['artifacts']['base']['theme']['font'])
            choose(h, 'mode', 0, MODES[0])
            finish_modal(h)
        else:
            stage(h, 'roles' if h.mode == 'inherit' else key)
        if h.mode == 'inherit':
            open_fonts(h)
            choose(h, 'mode', 0, MODES[0])
            finish_modal(h)
        h.stage = 'PIXELS'
        if h.mode == 'frozen-preview':
            w, height, expected = literal_raster(h, key, 'body')
            h.wait(lambda: h.sensitive('apply') and h.sensitive('undo'))
            assert h.pixels(40, 40, 180, 80) == baseline
            assert h.pixels(40, 40, w, height) != expected
            h.report['fault_detected'] = True
        else:
            pixels(h, key)
            if h.mode == 'base':
                h.click('undo')
                h.wait(lambda: h.pixels(40, 40, 180, 80) == baseline and not h.sensitive('undo'))
                h.click('redo')
                pixels(h, key)
            h.screenshot('edited')
            if submit(h, key):
                if h.mode == 'reset':
                    open_fonts(h)
                    field(h, 'size', 'invalid ignored reset')
                    finish_modal(h, 'reset')
                    assert submit(h, None, '42')
                    reopen(h, None, '42')
                else:
                    reopen(h, key)
    h.command('quit')
    assert h.proc.wait(timeout=5) == 0
    h.report['outcome'] = 'pass'


def observe(exe, exit_exe, text_exe, folder, mode):
    h = FontHarness(exe, exit_exe, text_exe, folder, mode)
    h.report.update(oracle_sha256=sha(Path(__file__)), text_executable_sha256=sha(text_exe))
    try:
        exercise(h)
    except BaseException as error:
        h.report.update(stage=h.stage, error=repr(error))
        try:
            h.report['failure_status'] = h.status()
            h.report['failure_canvas'] = h.text(h.find('canvas'))
            h.screenshot('failure')
        except BaseException as diagnostic:
            h.report['diagnostic_error'] = repr(diagnostic)
        raise
    finally:
        h.close()


def main():
    if sys.argv[1] == '--observe':
        observe(*map(Path, sys.argv[2:6]), sys.argv[6])
        return
    exe, exit_exe, text_exe, evidence = map(Path, sys.argv[1:5])
    assert os.geteuid() != 0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder = evidence/('theme-controls-'+uuid.uuid4().hex[:12])
    folder.mkdir(mode=0o700)
    server = None
    report = dict(family='EDITOR-FONTS', outcome='fail', started_at=datetime.now(timezone.utc).isoformat(), oracle_sha256=sha(Path(__file__)), harness_sha256=sha(ROOT/'tests/editor/native_editor.py'), fixture_sha256=sha(ROOT/'tests/editor/theme-controls-cases.json'), executable_sha256=sha(exe), text_executable_sha256=sha(text_exe), cases=[])
    try:
        server, env = launch_xvfb(folder)
        env['NO_AT_BRIDGE'] = '0'
        env.pop('AT_SPI_BUS_ADDRESS', None)
        for mode in CASES['native_cases']:
            child = subprocess.Popen(['dbus-run-session', '--', sys.executable, str(Path(__file__)), '--observe', str(exe), str(exit_exe), str(text_exe), str(folder/mode), mode], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            try:
                out, err = child.communicate(timeout=50)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGCONT)
                os.killpg(child.pid, signal.SIGKILL)
                out, err = child.communicate(timeout=5)
                (folder/(mode+'.stderr')).write_bytes(err)
                raise
            (folder/(mode+'.stdout')).write_bytes(out)
            (folder/(mode+'.stderr')).write_bytes(err)
            detail_path = folder/mode/'result.json'
            assert detail_path.is_file(), (mode, err.decode(errors='replace'))
            detail = json.loads(detail_path.read_bytes())
            report['cases'].append(dict(case=mode, outcome=detail['outcome'], fault_detected=detail.get('fault_detected', False), record_sha256=sha(detail_path)))
            assert child.returncode == 0 and detail['outcome'] == 'pass', (mode, err.decode(errors='replace'))
        report['outcome'] = 'pass'
    finally:
        if server is not None:
            server.terminate()
            server.communicate(timeout=5)
        report['files'] = {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*') if p.is_file() and p.name != 'xauthority'}
        (folder/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(folder/'result.json', report['outcome'])


if __name__ == '__main__':
    main()
