"""Owned X11/AT-SPI oracle for conditional pixels, independent of scene decisions."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import select
import signal
import subprocess
import sys
import time
import uuid
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tests/desktop'), str(ROOT/'tests/fault'), str(ROOT/'tests/scene'), str(ROOT/'build-support')]
from native_diagnostic import launch_xvfb
from native_oracle import Display
from check_text_runtime import verify
from check_surface_runtime import verify as verify_surface
from native_text import THEME


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe(exe, probe, folder, mode):
    import gi
    gi.require_version('Atspi', '2.0')
    from gi.repository import Atspi, GLib
    Atspi.set_timeout(500, 1000)
    verify()
    verify_surface()
    folder.mkdir()
    report = dict(mode=mode, outcome='fail', observations=[], executable_sha256=sha(exe),
                  text_probe_sha256=sha(probe), oracle_sha256=sha(Path(__file__)),
                  runtime_identity_sha256=sha(ROOT/'build-support/text-runtime.json'),
                  surface_runtime_sha256=sha(ROOT/'build-support/surface-runtime.json'))
    stderr = (folder/'stderr').open('wb')
    proc = subprocess.Popen([str(exe), str(ROOT/'spec/fixtures/valid'), 'WINDOW', 'visibility-'+mode],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
    display = None
    last_ack = None

    def read():
        assert select.select([proc.stdout], [], [], 5)[0], 'native reply timeout'
        line = proc.stdout.readline()
        assert line, 'native exited before reply'
        return json.loads(line)

    def command(name):
        nonlocal last_ack
        proc.stdin.write((name+'\n').encode('utf-8'))
        proc.stdin.flush()
        assert read() == {'ack': name}
        last_ack = time.monotonic()

    def pump():
        context = GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():
                break
            context.iteration(False)

    def find_surface():
        desktop = Atspi.get_desktop(0)
        if desktop is None:
            return None
        desktop.clear_cache()
        count = desktop.get_child_count()
        assert 0 <= count <= 64, 'desktop traversal bound'
        pending = []
        for i in range(count):
            app = desktop.get_child_at_index(i)
            assert app is not None, 'missing application reply'
            if app.get_process_id() == proc.pid:
                pending.append((app, 0))
        for _ in range(256):
            if not pending:
                return None
            item, depth = pending.pop()
            item.clear_cache()
            if item.get_description() == 'syspane.scene.surface':
                assert item.get_process_id() == proc.pid
                return item
            count = item.get_child_count()
            assert 0 <= count <= 64, 'child traversal bound'
            if depth < 8:
                for i in range(count):
                    child = item.get_child_at_index(i)
                    assert child is not None, 'missing child reply'
                    pending.append((child, depth+1))
        raise AssertionError('accessibility traversal bound')

    def expected(text, diagnostic=False):
        request = dict(text=text, theme=dict(THEME, theme_id='theme:native'))
        if diagnostic:
            request['wrap_units'] = 318*64  # Frozen 320-pixel rectangle, two guard pixels.
        key = hashlib.sha256(json.dumps(request, sort_keys=True).encode('utf-8')).hexdigest()[:16]
        path = folder/('expected-'+key+'.rgba')
        p = subprocess.run([str(probe), str(path)], input=json.dumps(request).encode('utf-8'),
                           capture_output=True, timeout=5)
        assert p.returncode == 0, p.stderr
        meta = json.loads(p.stdout)
        assert 'error' not in meta and meta['missing_glyphs'] == 0, meta
        assert meta['width'] <= 320 and meta['height'] <= 180, meta
        raw = path.read_bytes()
        canvas = bytearray(800*600*3)
        for y in range(meta['height']):
            for x in range(meta['width']):
                src = (y*meta['width']+x)*4
                dst = (y*800+x)*3
                canvas[dst:dst+3] = raw[src:src+3]
        return bytes(canvas), ('Private label\n'+text if diagnostic else text)

    def check(name, target, timeout=.2, hold=0, ordinary=None):
        start = last_ack if last_ack is not None else time.monotonic()
        for _ in range(64):
            assert proc.poll() is None, 'native owner exited'
            pump()
            actual = display.capture(0, 0, 800, 600)
            accessible.clear_cache()
            assert accessible.get_process_id() == proc.pid, 'accessible owner changed'
            label = accessible.get_name()
            assert isinstance(label, str), 'missing name reply is not empty content'
            elapsed = time.monotonic()-start
            matches = dict(pixels=actual == target[0], accessible=label == target[1])
            sequence = len(report['observations'])+1
            assert sequence <= 256, 'observation storage bound'
            path = folder/(str(sequence)+'.rgb.z')
            compressed = zlib.compress(actual, 9)
            path.write_bytes(compressed)
            assert zlib.decompress(compressed) == actual
            item = dict(case=name, elapsed=elapsed, artifact=path.name,
                        pixels_sha256=hashlib.sha256(actual).hexdigest(),
                        artifact_sha256=sha(path), name=label, **matches)
            if ordinary is not None:
                item['ordinary_pixels_match'] = actual == ordinary[0]
                item['ordinary_accessible_match'] = label == ordinary[1]
            report['observations'].append(item)
            if all(matches.values()) and elapsed >= hold:
                assert elapsed <= timeout, (name, 'deadline exceeded', elapsed)
                if ordinary is not None:
                    assert not item['ordinary_pixels_match'] and not item['ordinary_accessible_match'], name
                return
            assert elapsed < timeout, (name, matches, elapsed)
            time.sleep(.015)
        raise AssertionError('observation attempt bound')

    try:
        assert read() == {'ready': True}
        report['pid'] = proc.pid
        display = Display()
        deadline = time.monotonic()+5
        accessible = None
        while accessible is None and time.monotonic() < deadline:
            pump()
            accessible = find_surface()
            if accessible is None:
                time.sleep(.025)
        assert accessible is not None, 'owned AT-SPI surface absent'
        blank = (bytes(800*600*3), '')
        body = expected('Secret body')
        mismatch = expected('Visibility (value): Unit mismatch', True)
        waiting = expected('Visibility (value): Waiting', True)
        lost = expected('Visibility (value): Source lost', True)
        if mode == 'invert':
            check('INVERT-INITIAL', blank, timeout=2, hold=.2, ordinary=body)
            command('hide')
            check('INVERT-REVEALS', body, timeout=.5, hold=.2, ordinary=blank)
        else:
            check('INITIAL', body, timeout=2)
            command('hide')
            if mode == 'retain-hidden':
                check('RETAINED-HIDDEN', body, timeout=.5, hold=.2, ordinary=blank)
            else:
                check('HIDDEN', blank)
                command('show')
                check('SHOWN', body)
                command('mismatch')
                check('UNRESOLVED', mismatch)
                command('reset')
                check('RESET', body)
                command('revoke')
                check('REVOKED', blank)
                command('regrant')
                check('REGRANTED', waiting)
                command('fresh')
                check('FRESH', body)
                command('disconnect')
                check('LOST', lost)
        command('close')
        assert proc.wait(timeout=5) == 0
        report['outcome'] = 'pass'
        report['negative_control'] = mode != 'normal'
    except Exception as exc:
        report['error'] = repr(exc)
        raise
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        stderr.close()
        if display is not None:
            display.close()
        report['files'] = {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        (folder/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


def main():
    if sys.argv[1] == '--observe':
        observe(*map(Path, sys.argv[2:5]), sys.argv[5])
        return
    exe, probe, evidence = map(Path, sys.argv[1:4])
    folder = evidence/('visibility-'+uuid.uuid4().hex[:12])
    folder.mkdir()
    report = dict(family='VISIBILITY-PIXELS', outcome='fail', cases=[],
                  started_at=datetime.now(timezone.utc).isoformat(), executable_sha256=sha(exe),
                  oracle_sha256=sha(Path(__file__)))
    server = None
    try:
        server, env = launch_xvfb(folder)
        env['NO_AT_BRIDGE'] = '0'
        env.pop('AT_SPI_BUS_ADDRESS', None)
        for mode in ('normal', 'invert', 'retain-hidden'):
            child = subprocess.Popen(['dbus-run-session', '--', sys.executable, str(Path(__file__)),
                                      '--observe', str(exe), str(probe), str(folder/mode), mode],
                                     env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     start_new_session=True)
            timed_out = False
            try:
                stdout, stderr = child.communicate(timeout=35)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                stdout, stderr = child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout)
            (folder/(mode+'.stderr')).write_bytes(stderr)
            assert not timed_out and child.returncode == 0, (mode, 'observer deadline' if timed_out else stderr.decode(errors='replace'))
            record = folder/mode/'result.json'
            assert json.loads(record.read_text(encoding='utf-8'))['outcome'] == 'pass'
            report['cases'].append(dict(case=mode, outcome='pass', record_sha256=sha(record)))
        report['outcome'] = 'pass'
    except Exception as exc:
        report['error'] = repr(exc)
        raise
    finally:
        if server is not None:
            server.terminate()
            server.communicate(timeout=5)
        report['files'] = {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*')
                           if p.is_file() and p.name != 'xauthority'}
        (folder/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(folder/'result.json', report['outcome'])


if __name__ == '__main__':
    main()
