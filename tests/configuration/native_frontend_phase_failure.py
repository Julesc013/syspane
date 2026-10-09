"""Observer refusal/exception must close the host without undoing an accepted write."""
import copy, json, select
import native_installed_editor as h
from frontend_phases import decode

CASES_PATH = 'tests/configuration/frontend-phase-failure-cases.json'
h.CASES = json.loads((h.ROOT/CASES_PATH).read_bytes())


def exercise(e):
    e['env'].update(SYSPANE_TEST_TIMING='1', SYSPANE_TEST_PHASES='1', SYSPANE_TEST_PHASE_FAULT=e['mode'].lower())
    e['launch'](); e['settings_ready']()
    e['enter']('settings.value.sampling.resources_ms', '1500')
    e['wait'](lambda:e['sensitive'](e['find']('settings.apply')))
    e['click']('settings.apply')
    e['wait'](lambda:e['process']().poll() is not None, 8)
    assert e['process']().returncode == 2, 'observer failure did not fail frontend'
    assert set(e['runtime'].glob('sp-*')) == e['roots'], 'runtime not retired'
    for fd in [*e['pidfds'].values(), *e['helper_pidfds'].values()]:
        assert select.select([fd], [], [], 1)[0], 'native child not exited'
    expected = copy.deepcopy(h.INITIAL['documents'])
    expected['settings']['sampling']['resources_ms'] = 1500
    expected['settings']['revision'] = expected['scene']['revision'] = '1'
    assert h.stored(e['generations']) == expected, 'observer failure changed committed documents'
    blocks = decode((e['folder']/'stderr').read_bytes())
    assert len(blocks) == 1 and blocks[0]['pid'] == e['process']().pid and blocks[0]['result'] == 2
    assert blocks[0]['rows'] and not any(row['phase'] == 'reply' for row in blocks[0]['rows'])
    e['report']['phase_records'] = len(blocks[0]['rows'])


exercise.capture_timings = True
if __name__ == '__main__':
    h.main(exercise, __file__, CASES_PATH, 'pff-')
