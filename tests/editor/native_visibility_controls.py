"""Native private rule controls, conditional pixels and exact durable scenes."""
from pathlib import Path
from datetime import datetime, timezone
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
from native_observation import PREFIX

CASES = json.loads((ROOT/'tests/editor/visibility-controls-cases.json').read_text(encoding='utf-8'))


class VisibilityHarness(LayoutHarness):
    def __init__(self, *args):
        Harness.__init__(self, *args, visibility=True)


def canvas(h):
    return h.text(h.find('canvas'))


def field(h, id, value, prefix='visibility.'):
    obj = h.find(prefix+id)
    h.wait(lambda: h.sensitive(prefix+id))
    assert h.Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(), str(value))
    h.wait(lambda: h.text(obj) == str(value))


def chosen(h, id, prefix='visibility.'):
    return h.observer.selected_text(h.find(prefix+id))


def choose(h, id, index, value, prefix='visibility.'):
    obj = h.find(prefix+id)
    h.wait(lambda: h.state(obj, h.Atspi.StateType.SHOWING) and h.sensitive(prefix+id))
    assert h.Atspi.Action.do_action(obj.get_action_iface(), 0)
    h.wait(lambda: any(o.get_role() == h.Atspi.Role.MENU_ITEM and h.state(o, h.Atspi.StateType.SHOWING) and h.text(o) == value for o in h.objects()))
    h.input.press(0xff50)
    for _ in range(index):
        h.input.press(0xff54)
    h.input.press(0xff0d)
    h.wait(lambda: chosen(h, id, prefix) == value)


def select(h, index):
    widgets = CASES['authored']['scene']['widgets']
    end = time.monotonic()+3
    h.focus('objects')
    obj = h.find('objects')
    for key, row in [(0xff57, len(widgets)-1), (0xff50, 0)]+[(0xff54, n) for n in range(1, index+1)]:
        h.input.press(key)
        h.wait(lambda: h.observer.call(obj, PREFIX+'Table', 'GetSelectedRows', signature='(ai)')[0] == [row] and h.value('title') == widgets[row]['title'], max(.001, end-time.monotonic()))


def open_rule(h):
    h.click('visibility')
    h.wait(lambda: h.find('visibility.set') is not None and h.sensitive('visibility.set') and not h.sensitive('visibility') and not h.sensitive('apply'))


def set_rule(h):
    h.click('visibility.set')
    h.wait(lambda: h.sensitive('visibility'))
    h.input.focus(h.pid)


def source(h):
    h.click('visibility.source')
    h.wait(lambda: h.find('binding.set') is not None and h.sensitive('binding.set') and not h.sensitive('visibility.set'))


def hidden(h):
    return 'Move me' not in canvas(h) and 'Editable pane' not in canvas(h) and set(h.pixels(44, 44, 170, 68)) == {0}


def finish(h):
    h.command('quit')
    assert h.proc.wait(timeout=5) == 0
    h.report['outcome'] = 'pass'


def exercise(h):
    mode = h.mode
    h.launch()
    h.check()
    h.point(60, 60)
    h.wait(lambda: h.value('title') == 'Editable pane')
    baseline = h.pixels(44, 44, 170, 68)
    assert len(set(baseline)) > 2
    h.report['baseline_pixel_sha256'] = hashlib.sha256(baseline).hexdigest()
    (h.folder/'baseline.rgb.z').write_bytes(zlib.compress(baseline))
    h.screenshot('initial')
    if mode == 'frozen-preview':
        h.command('freeze-preview')
    h.stage = 'BUFFER'
    open_rule(h)
    assert chosen(h, 'mode') == 'Always show'
    choose(h, 'mode', 1, 'When condition matches')
    assert chosen(h, 'op') == 'gt' and h.text(h.find('visibility.value')) == '0'
    held = [h.find('visibility.value')]
    if mode in ('cancel-buffer', 'nested-cancel', 'revoke', 'nested-revoke', 'retain-visibility'):
        field(h, 'value', 'Private condition')
        if mode.startswith('nested-'):
            source(h)
            field(h, 'field', 'Private condition field', 'binding.')
            held += [h.find('binding.field'), h.find('binding.entity_type')]
        if mode.endswith('cancel') or mode == 'cancel-buffer':
            if mode == 'nested-cancel':
                h.click('binding.cancel')
                h.wait(lambda: h.sensitive('visibility.set') and h.erased(held[1]))
                assert 'network.receive_bytes' in h.text(h.find('visibility.source-summary'))
            h.click('visibility.cancel')
            h.wait(lambda: h.sensitive('visibility') and all(h.erased(o) for o in held))
            assert not h.sensitive('apply') and not h.sensitive('undo')
            h.check()
            finish(h)
            return
        h.stage = 'ERASE'
        issued = h.command('revoke')
        h.wait(lambda: all(h.erased(o) for o in held) and set(h.pixels(0, 0, 500, 420)) == {0}, max(.001, issued+.2-time.monotonic()))
        h.report['erase_ms'] = (time.monotonic()-issued)*1000
        assert h.report['erase_ms'] <= CASES['erase_ms']
        h.report['production_erased'] = True
        h.stage = 'RETAINED'
        assert not any('Private condition' in h.text(o) for o in h.objects()), 'retained visibility disclosed'
        h.check()
        h.command('regrant')
        assert not h.sensitive('visibility') and all(h.erased(o) for o in held)
        h.input.focus(h.pid)
        h.click('reload')
        h.event('event', 'reloaded')
        select(h, 0)
        open_rule(h)
        choose(h, 'mode', 1, 'When condition matches')
        assert h.text(h.find('visibility.value')) == '0'
        h.click('visibility.cancel')
        h.wait(lambda: h.sensitive('visibility'))
        finish(h)
        return
    expected = CASES['hidden']
    if mode == 'source':
        source(h)
        choose(h, 'kind', 1, 'direct', 'binding.')
        for key, value in dict(producer_id='P1', producer_epoch='E1', entity_id='network:interface:1', field='network.transmit_bytes').items():
            field(h, key, value, 'binding.')
        h.click('binding.set')
        h.wait(lambda: h.sensitive('visibility.set'))
        expected = CASES['source']
    elif mode == 'exact':
        field(h, 'value', '18446744073709551615')
        expected = CASES['exact']
    else:
        choose(h, 'op', 0, 'eq')
    if mode == 'invalid':
        field(h, 'value', '18446744073709551616')
        h.click('visibility.set')
        h.wait(lambda: '64-bit' in h.text(h.find('visibility.error')))
        assert h.text(h.find('visibility.value')) == '18446744073709551616'
        source(h)
        field(h, 'limit', '2', 'binding.')
        h.click('binding.set')
        h.wait(lambda: 'limit of 1' in h.text(h.find('binding.error')))
        h.check()
        h.click('binding.cancel')
        h.wait(lambda: h.sensitive('visibility.set'))
        field(h, 'value', '0')
    set_rule(h)
    h.stage = 'HIDDEN'
    if mode == 'frozen-preview':
        time.sleep(.22)
        assert 'Move me' not in canvas(h) and h.pixels(44, 44, 170, 68) == baseline, 'known retained preview absent'
        h.report['fault_detected'] = True
        h.screenshot('retained-preview')
        finish(h)
        return
    h.wait(lambda: hidden(h))
    assert 'hidden by condition' in h.status()
    h.screenshot('hidden')
    # Hidden objects cannot be selected through their old canvas pixels.
    h.point(60, 60)
    h.wait(lambda: h.value('title') == '')
    select(h, 0)
    h.wait(lambda: h.value('title') == 'Editable pane' and h.sensitive('visibility'))
    if mode == 'multi':
        h.point(300, 60, shift=True)
        h.wait(lambda: h.value('title') == '')
        open_rule(h)
        assert chosen(h, 'mode') == 'Keep unchanged'
        set_rule(h)
        open_rule(h)
        choose(h, 'mode', 1, 'When condition matches')
        choose(h, 'op', 0, 'eq')
        set_rule(h)
        h.wait(lambda: 'Second pane' not in canvas(h) and set(h.pixels(284, 44, 170, 68)) == {0})
        expected = CASES['multi']
    elif mode == 'clear':
        open_rule(h)
        choose(h, 'mode', 0, 'Always show')
        set_rule(h)
        h.wait(lambda: 'Move me' in canvas(h) and h.pixels(44, 44, 170, 68) == baseline)
        expected = CASES['cleared']
    elif mode in ('held-hide', 'held-diagnostic'):
        issued = h.command('condition-hide-select')  # eq 0, then selection before repaint.
        h.event('event', 'selected-before-paint')
        h.wait(lambda: 'Move me' in canvas(h) and h.pixels(44, 44, 170, 68) == baseline, max(.001, issued+.2-time.monotonic()))
        h.drag(60, 60, 20, 0, hold=True)
        h.wait(lambda: h.number('x') == 40 and 'Move me' in canvas(h))
        issued = h.command('condition-show' if mode == 'held-hide' else 'condition-loss')
        if mode == 'held-hide':
            h.wait(lambda: 'Move me' not in canvas(h) and set(h.pixels(64, 44, 170, 68)) == {0}, max(.001, issued+.2-time.monotonic()))
        else:
            h.wait(lambda: 'Visibility (widget:text): Source lost' in canvas(h) and 'Move me' not in canvas(h) and len(set(h.pixels(64, 44, 170, 68))) > 2, max(.001, issued+.2-time.monotonic()))
        assert h.number('x') == 40
        h.screenshot('held-current-condition')
        h.input.button(False)
        h.wait(lambda: h.number('x') == 60)
        expected = CASES['moved_hidden']
    h.stage = 'HISTORY'
    h.click('undo')
    h.wait(lambda: h.sensitive('redo'))
    h.click('redo')
    h.wait(lambda: not h.sensitive('redo'))
    h.check()
    h.stage = 'SUBMIT'
    h.click('apply')
    submitted = h.event('event', 'submitted')
    assert submitted['body']['schema_version'] == '0.7.0'
    if mode != 'wrong-visibility':
        assert submitted['body']['operations'][0]['scene'] == expected
    h.event('event', 'held')
    h.wait(lambda: not h.sensitive('visibility'))
    h.check()
    h.command('release')
    result = h.event('event', 'result')['result']
    assert result['outcome'] == 'accepted' and result['revision'] == '41' and result['durable'] and not result['visible']
    h.stage = 'STORE'
    h.check(expected, '41')
    if mode == 'restart':
        h.wait(lambda: 'Outcome unknown' in h.status())
        selector = (h.directory/'current.json').read_bytes()
        h.command('restart')
        h.event('event', 'reconciled')
        assert (h.directory/'current.json').read_bytes() == selector
    h.wait(lambda: 'Saved durably' in h.status())
    h.command('quit')
    assert h.proc.wait(timeout=5) == 0
    h.launch('reopen')
    h.check(expected, '41')
    select(h, 0)
    open_rule(h)
    assert chosen(h, 'mode') == ('Always show' if mode == 'clear' else 'When condition matches')
    if mode != 'clear':
        own = expected['widgets'][0]['visibility']
        assert chosen(h, 'op') == own['op'] and h.text(h.find('visibility.value')) == str(own['value']) and h.text(h.find('visibility.unit')) == own['unit']
    h.click('visibility.cancel')
    h.wait(lambda: h.sensitive('visibility'))
    finish(h)


def observe(exe, exit_exe, folder, mode):
    h = VisibilityHarness(exe, exit_exe, folder, mode)
    h.report.update(oracle_sha256=sha(Path(__file__)), harness_sha256=sha(ROOT/'tests/editor/native_editor.py'))
    try:
        exercise(h)
    except AssertionError as error:
        h.report.update(stage=h.stage, error=str(error))
        h.report['failure_status'] = h.status()
        h.report['failure_fields'] = {k: h.value(k) for k in ('title', 'body', 'x', 'y', 'width', 'height')}
        h.report['failure_canvas'] = canvas(h)
        h.screenshot('failure')
        if mode == 'wrong-visibility' and h.stage == 'STORE' and str(error) == 'stored documents differ' and stored(h.directory) == h.documents(CASES['conditional'], '41'):
            h.report.update(outcome='pass', fault_detected=True)
        elif mode == 'retain-visibility' and h.stage == 'RETAINED' and str(error) == 'retained visibility disclosed' and h.report.get('production_erased') and any('Retained visibility canary Private condition' in h.text(o) for o in h.objects()):
            h.report.update(outcome='pass', fault_detected=True)
        else:
            raise
    finally:
        h.close()


def main():
    if sys.argv[1] == '--observe':
        observe(*map(Path, sys.argv[2:5]), sys.argv[5])
        return
    exe, exit_exe, evidence = map(Path, sys.argv[1:4])
    assert os.geteuid() != 0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder = evidence/('visibility-controls-'+uuid.uuid4().hex[:12])
    folder.mkdir(mode=0o700)
    server = None
    report = dict(family='EDITOR-VISIBILITY', outcome='fail', started_at=datetime.now(timezone.utc).isoformat(), oracle_sha256=sha(Path(__file__)), harness_sha256=sha(ROOT/'tests/editor/native_editor.py'), fixture_sha256=sha(ROOT/'tests/editor/visibility-controls-cases.json'), executable_sha256=sha(exe), cases=[])
    try:
        server, env = launch_xvfb(folder)
        env['NO_AT_BRIDGE'] = '0'
        env.pop('AT_SPI_BUS_ADDRESS', None)
        for mode in CASES['native_cases']:
            child = subprocess.Popen(['dbus-run-session', '--', sys.executable, str(Path(__file__)), '--observe', str(exe), str(exit_exe), str(folder/mode), mode], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
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
            detail = json.loads((folder/mode/'result.json').read_bytes())
            report['cases'].append(dict(case=mode, outcome=detail['outcome'], fault_detected=detail.get('fault_detected', False), record_sha256=sha(folder/mode/'result.json')))
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
