"""Installed image semantics and real logical-monitor changes, independently observed."""
import json
import fcntl
import os
import select
import signal
import time
from pathlib import Path
import native_installed_editor as h
import installed_image_fixture as fixture
from inspector_topology_fixture import Topology

CASES_PATH = 'tests/configuration/installed-inspector-assets-cases.json'
CASES = json.loads((h.ROOT / CASES_PATH).read_bytes())
h.CASES = CASES


def exercise(e):
    folder, mode, report = (e[k] for k in ('folder', 'mode', 'report'))
    wait, click, find, value, sensitive = (e[k] for k in ('wait', 'click', 'find', 'value', 'sensitive'))
    launch, quit = (e[k] for k in ('launch', 'quit'))
    def settings():
        wait(lambda: value('settings.value.sampling.resources_ms') == '1000' and sensitive(find('frontend.editor')), 62)
        e['child']()
    saved = fixture.recipe(h.ROOT, CASES, mode)
    report['fixture'] = dict(generation=saved[0], selector_sha256=h.sha(saved[1]),
                            files={name: h.sha(raw) for name, raw in saved[2].items()})
    report['observer_inputs'] = {name: h.sha((h.ROOT / 'tests/configuration' / name).read_bytes())
                                 for name in ('installed_image_fixture.py', 'inspector_topology_fixture.py')}

    def rows():
        tree = find('syspane.scene.inspector')
        if not tree: return None
        table = tree.get_table_iface(); assert table and table.get_n_columns() == 2
        return [[e['text'](table.get_accessible_at(r, c)) for c in range(2)] for r in range(table.get_n_rows())]

    def exact(expected):
        actual = rows(); assert actual == expected, (actual, expected)

    def ready(expected=None):
        expected = expected or CASES['ready_rows']
        wait(lambda: rows() == expected and sensitive(find('frontend.settings')), 62)
        assert not sensitive(find('frontend.inspector'))
        exact(expected); report['observations'].append(dict(rows=rows()))
        fixture.verify(e['generations'], saved)

    def open_view():
        wait(lambda: sensitive(find('frontend.inspector'))); click('frontend.inspector')

    def summary():
        keys = summary_keys
        if keys:
            tree = find('syspane.scene.inspector'); e['focus'](tree); keys.press(0xff57)
            wait(lambda: list(tree.get_table_iface().get_selected_rows()) == [0])
            button = next(o for o in e['objects']() if o.get_role() == e['Atspi'].Role.PUSH_BUTTON and o.get_name() == 'Summary')
            e['focus'](button); keys.press(0x20)
            wait(lambda: value('syspane.scene.requested-summary') == CASES['summary'])
            report['observations'].append(dict(summary=value('syspane.scene.requested-summary')))

    def erased():
        return rows() in (None, []) and value('syspane.scene.requested-summary') == ''

    launch(); settings(); e['documents'](); quit()
    fixture.install(e['generations'], saved)
    generation_names = sorted(p.name for p in e['generations'].iterdir())
    launch(); settings()
    summary_keys = h.Keys(e['process']().pid) if mode in ('SUMMARY', 'POLICY', 'TOPOLOGY') else None
    open_view()
    held = None
    if mode.startswith('HELD-'):
        installed = e['exe'].parent.parent / 'share/syspane/helpers.json'
        identities = {v['sha256'] for v in json.loads(installed.read_bytes())['helpers'].values()
                      if v['path'].endswith('/syspane-image-worker')}

        def live_image():
            for child in report.get('native_children', []):
                fd = e['helper_pidfds'][child['pid']]
                if child['argv'] == ['syspane-image-worker', 'image/png', str(e['process']().pid)] and not select.select([fd], [], [], 0)[0]:
                    if child['sha256'] is not None: assert child['sha256'] in identities
                    return child['pid'], fd
        held = wait(live_image, 62)
        signal.pidfd_send_signal(held[1], signal.SIGSTOP)
        wait(lambda: '\nState:\tT' in Path('/proc', str(held[0]), 'status').read_text(), .5)
        sealed = []
        for path in Path('/proc', str(e['process']().pid), 'fd').iterdir():
            try: target = os.readlink(path)
            except FileNotFoundError: continue
            if 'memfd:syspane-image-worker' not in target: continue
            with path.open('rb') as stream:
                seals = fcntl.fcntl(stream.fileno(), fcntl.F_GET_SEALS)
                digest = h.sha(stream.read())
            assert seals & 15 == 15 and digest in identities
            sealed.append(dict(sha256=digest, seals=seals))
        assert sealed, 'verified sealed image owner absent'
        exact(CASES['loading_rows']); report['held_image'] = dict(pid=held[0], stopped=True, rows=rows())
        report['held_image']['parent_sealed_images'] = sealed
        if mode == 'HELD-NAVIGATION':
            click('frontend.settings'); settings(); assert erased()
            assert select.select([held[1]], [], [], 0)[0], 'navigation completed before image exit'
        else:
            quit(); assert select.select([held[1]], [], [], 0)[0]
    else:
        ready(CASES['decode_failure_rows'] if mode == 'DECODE-FAILURE' else CASES['oversize_rows'] if mode == 'OVERSIZE' else None)
        if mode in ('SUMMARY', 'POLICY', 'TOPOLOGY'): summary()
        if mode == 'NAVIGATION':
            click('frontend.editor'); wait(lambda: find('editor.canvas') and sensitive(find('frontend.settings')))
            open_view(); ready(); click('frontend.settings'); settings(); open_view(); ready()
        elif mode == 'REOPEN':
            quit(); launch(); settings(); open_view(); ready()
        elif mode == 'POLICY':
            pid, fd = e['child'](); (folder / 'policy').write_text('deny\n')
            wait(lambda: select.select([fd], [], [], 0)[0], 4)
            start = time.monotonic(); wait(erased, CASES['erasure_after_observed_loss_ms'] / 1000)
            report['erasure_ms'] = (time.monotonic() - start) * 1000
        elif mode == 'TOPOLOGY':
            from gi.repository import Gdk
            topology = Topology()
            try:
                for narrow, width in ((True, 400), (False, 800)):
                    topology.change(narrow)
                    wait(lambda: Gdk.Display.get_default().get_n_monitors() == 1 and
                         Gdk.Display.get_default().get_monitor(0).get_geometry().width == width)
                    assert topology.geometry() == [[0, 0, width, 600]]
                    if narrow:
                        wait(lambda: erased() and value('frontend.status') == CASES['unavailable'])
                    else:
                        ready(); assert value('syspane.scene.requested-summary') == ''
                        assert value('frontend.status') != CASES['unavailable']
                    report['observations'].append(dict(randr=topology.geometry(), gdk_width=width, rows=rows(),
                                                       summary=value('syspane.scene.requested-summary'), status=value('frontend.status')))
            finally: topology.close()
        elif mode == 'ORACLE':
            wrong = [['Incorrect title', CASES['ready_rows'][0][1]]]
            try: exact(wrong)
            except AssertionError: report['wrong_row_rejected'] = True
            else: raise AssertionError('incorrect row accepted')
            exact(CASES['ready_rows'])
    if mode != 'HELD-CLOSE': e['screenshot']('inspector-assets'); quit()
    if summary_keys: summary_keys.close()
    fixture.verify(e['generations'], saved)
    assert sorted(p.name for p in e['generations'].iterdir()) == generation_names


exercise.continue_after_case_failure = True
if __name__ == '__main__': h.main(exercise, __file__, CASES_PATH, 'inspector-assets-')
