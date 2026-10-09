"""Original installed oracles through the ordinary entry, without observer support."""
import os,sys

CONTROLS=dict(SYSPANE_TEST_TIMING='1',SYSPANE_TEST_PHASES='1',SYSPANE_TEST_PHASE_FAULT='invalid-for-observer-fixture')

if len(sys.argv)>1 and sys.argv[1]=='settings':
    sys.argv.pop(1)
    import native_installed_settings as settings
    os.environ.update(CONTROLS)
    settings.CASES=dict(settings.CASES,family='ADMITTED-SETTINGS')
    settings.main()
else:
    if len(sys.argv)>1 and sys.argv[1]=='recovery':sys.argv.pop(1)
    import native_installed_recovery as recovery
    recovery.h.CASES=dict(recovery.CASES,family='ADMITTED-RECOVERY')

    def exercise(e):
        e['env'].update(CONTROLS)
        recovery.exercise(e)
        e['timings']()
        assert not e['report'].get('timings'),'ordinary entry emitted timing records'
        raw=(e['folder']/'stderr').read_bytes()
        assert not any(line.startswith((b'phase-begin ',b'phase ',b'phase-end ')) for line in raw.splitlines()),'ordinary entry emitted phase records'
        e['report']['observer_controls_ignored']=True
        e['report']['latency_qualification']=False

    exercise.capture_timings=True  # Drain stdout and reject any emitted observations.
    recovery.h.main(exercise,__file__,recovery.CASES_PATH,'ar-')
