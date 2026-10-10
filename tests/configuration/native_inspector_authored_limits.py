"""Exact installed authored limits with the original bounded GTK-loop observer."""
import json
import select
import time
import native_installed_editor as h
import inspector_authored_inputs as inputs

CASES_PATH = 'tests/configuration/inspector-authored-limits-cases.json'
CASES = json.loads((h.ROOT / CASES_PATH).read_bytes()); h.CASES = CASES


def exercise(e):
    folder, mode, report = (e[k] for k in ('folder', 'mode', 'report'))
    wait, click, find, value, sensitive = (e[k] for k in ('wait', 'click', 'find', 'value', 'sensitive'))
    launch, settings, quit = (e[k] for k in ('launch', 'settings_ready', 'quit'))
    fixture, expected = inputs.generation(h.ROOT, mode)
    identity = dict(scene_bytes=len(fixture[2]['scene.json']), scene_sha256=h.sha(fixture[2]['scene.json']),
                    widgets=len(json.loads(fixture[2]['scene.json'])['widgets']), rows=len(expected), rows_sha256=h.sha(h.encoded(expected)))
    assert identity == json.loads((h.ROOT / 'tests/configuration/inspector-authored-inputs.json').read_bytes())[mode]
    report['recipe_sha256'] = h.sha((h.ROOT / 'tests/configuration/inspector_authored_inputs.py').read_bytes())
    report['input'] = dict(scene_bytes=len(fixture[2]['scene.json']), scene_sha256=h.sha(fixture[2]['scene.json']),
                          expected_rows=len(expected), expected_sha256=h.sha(h.encoded(expected)),
                          files={k: h.sha(v) for k, v in fixture[2].items()})
    e['env']['SYSPANE_TEST_TIMING'] = '1'

    def rows():
        tree = find('syspane.scene.inspector')
        if not tree: return None
        table = tree.get_table_iface(); assert table and table.get_n_columns() == 2
        return [[e['text'](table.get_accessible_at(r, c)) for c in range(2)] for r in range(table.get_n_rows())]

    def exact(wanted=None):
        wanted = expected if wanted is None else wanted
        actual = rows()
        assert actual == wanted, (mode, 'rows differ', len(actual) if actual is not None else None,
                                  h.sha(h.encoded(actual)), h.sha(h.encoded(wanted)))

    def ready():
        wait(lambda: rows() == expected and sensitive(find('frontend.settings')), 12)
        if not expected: assert value('frontend.status') == CASES['unavailable']
        else: assert value('frontend.status') != CASES['unavailable']
        exact(); inputs.verify(e['generations'], fixture)
        report['observations'].append(dict(rows=len(expected), sha256=h.sha(h.encoded(rows()))))

    def open_view():
        click('frontend.inspector'); ready()

    def erased():
        return rows() in (None, []) and value('syspane.scene.requested-summary') == ''

    launch(); settings(); e['documents'](); quit()
    inputs.install(e['generations'], fixture)
    generations = sorted(p.name for p in e['generations'].iterdir())
    launch(); settings()
    keys = h.Keys(e['process']().pid)
    try:
        open_view()
        if mode == 'MAX-WIDGETS':
            wrong = [list(row) for row in expected]; wrong[0][0] = 'Incorrect title'
            try: exact(wrong)
            except AssertionError: report['wrong_row_rejected'] = True
            else: raise AssertionError('incorrect title accepted')
        if mode == 'MAX-DEPTH':
            tree = find('syspane.scene.inspector'); e['focus'](tree); keys.press(0xff50)
            wait(lambda: list(tree.get_table_iface().get_selected_rows()) == [0])
            shift = keys.x.XKeysymToKeycode(keys.handle, 0xffe1); assert shift
            for key, wanted in ((0xff51, expected[:1] + expected[16:]), (0xff53, expected)):
                assert keys.xt.XTestFakeKeyEvent(keys.handle, shift, True, 0)
                try: keys.press(key)
                finally:
                    assert keys.xt.XTestFakeKeyEvent(keys.handle, shift, False, 0)
                    keys.x.XSync(keys.handle, False)
                wait(lambda: rows() == wanted)
                exact(wanted)
                assert list(tree.get_table_iface().get_selected_rows()) == [0]
                report['observations'].append(dict(hierarchy_rows=len(wanted)))
        if expected:
            tree = find('syspane.scene.inspector'); e['focus'](tree); keys.press(0xff57)
            wait(lambda: list(tree.get_table_iface().get_selected_rows()) == [255])
            button = next(o for o in e['objects']() if o.get_role() == e['Atspi'].Role.PUSH_BUTTON and o.get_name() == 'Summary')
            e['focus'](button); keys.press(0x20)
            wait(lambda: value('syspane.scene.requested-summary') == '\n'.join(expected[-1]))
        start = time.monotonic(); sample = len(report.get('timings', [])); observations = 0
        while time.monotonic() - start < CASES['steady_seconds']:
            e['pump'](); exact(); observations += 1; time.sleep(.01)
        e['timings'](); report['steady'] = dict(seconds=time.monotonic() - start, samples=len(report.get('timings', [])) - sample, observations=observations)
        assert report['steady']['samples'] >= CASES['steady_samples']
        if mode == 'NAVIGATION':
            click('frontend.editor'); wait(lambda: find('editor.canvas') and sensitive(find('frontend.settings')), 12)
            open_view(); click('frontend.settings'); settings(); open_view()
        elif mode == 'REOPEN':
            quit(); launch(); settings(); open_view()
        elif mode == 'POLICY':
            pid, fd = e['child'](); (folder / 'policy').write_text('deny\n')
            wait(lambda: select.select([fd], [], [], 0)[0], 4)
            start = time.monotonic(); wait(erased, CASES['erasure_after_observed_loss_ms'] / 1000)
            report['erasure_ms'] = (time.monotonic() - start) * 1000
        e['screenshot']('inspector-authored'); quit()
    finally: keys.close()
    inputs.verify(e['generations'], fixture)
    assert sorted(p.name for p in e['generations'].iterdir()) == generations
    e['timings'](); samples = report.get('timings', []); assert samples
    violations = [dict(index=i, **v) for i, v in enumerate(samples) if max(v['work_us'], v['delay_us']) > CASES['gui_operation_limit_ms'] * 1000]
    report['timing_violations'] = violations
    assert not violations, ('GUI timing limit exceeded', violations)


exercise.capture_timings = True
exercise.continue_after_case_failure = True
if __name__ == '__main__': h.main(exercise, __file__, CASES_PATH, 'inspector-authored-')
