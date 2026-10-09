"""Phase attribution alongside the unchanged, potentially failing GTK oracle."""
from pathlib import Path
import json, sys
import native_recovery_gui_limits as limits
from frontend_phases import decode, KINDS

h = limits.h
h.CASES = dict(limits.CASES, family='FRONTEND-PHASES')


def exercise(e):
    e['env']['SYSPANE_TEST_PHASES'] = '1'
    limits.exercise(e)


exercise.capture_timings = True
exercise.continue_after_case_failure = True


def analyze(folder):
    original = (folder/'result.json').read_bytes()
    report = json.loads(original)
    result = dict(diagnostic_only=True, original_outcome=report['outcome'],
                  original_report_sha256=h.sha(original), decoder_sha256=h.sha(Path(__file__).with_name('frontend_phases.py').read_bytes()), cases=[])
    for case in report['cases']:
        record = json.loads((folder/case['case']/'result.json').read_bytes())
        raw = (folder/case['case']/'stderr').read_bytes()
        blocks = decode(raw)
        timing_pids = {row['pid'] for row in record['timings']}
        assert {b['pid'] for b in blocks} == timing_pids, 'phase/timing lifetime mismatch'
        assert all(b['result'] == 0 for b in blocks), 'frontend failed before diagnostic completion'
        rows = [dict(pid=b['pid'], **row) for b in blocks for row in b['rows']]
        result['cases'].append(dict(case=case['case'], original_outcome=case['outcome'],
            stderr_sha256=h.sha(raw), blocks=blocks,
            maxima={kind:max((row['microseconds'] for row in rows if row['phase']==kind), default=0) for kind in KINDS},
            slow=[row for row in rows if row['microseconds'] > 100000]))
    (folder/'phases.json').write_bytes(h.encoded(result))
    print(json.dumps([dict(case=c['case'], maxima=c['maxima'], slow=c['slow']) for c in result['cases']], indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '--observe':
        h.main(exercise, __file__, limits.CASES_PATH, 'fp-')
    else:
        evidence = Path(sys.argv[4]).resolve(); before = set(evidence.glob('fp-*'))
        try:
            h.main(exercise, __file__, limits.CASES_PATH, 'fp-')
        finally:
            created = set(evidence.glob('fp-*')) - before
            assert len(created) == 1, 'ambiguous phase attempt'
            analyze(created.pop())  # Original oracle exceptions remain failures.
