"""Attribute live-table costs with the unchanged full qualification observer."""
from pathlib import Path
import sys
from native_frontend_phases import analyze
import native_inspector_live_tables as limits

h=limits.h
h.CASES=dict(limits.CASES,family='INSPECTOR-LIVE-TABLE-PHASES')

def exercise(e):
    e['env']['SYSPANE_TEST_PHASES']='1'
    limits.exercise(e)

exercise.capture_timings=True
exercise.continue_after_case_failure=True

if __name__=='__main__':
    if sys.argv[1]=='--observe':h.main(exercise,__file__,limits.CASES_PATH,'inspector-table-phases-')
    else:
        evidence=Path(sys.argv[4]).resolve();before=set(evidence.glob('inspector-table-phases-*'))
        try:h.main(exercise,__file__,limits.CASES_PATH,'inspector-table-phases-')
        finally:
            created=set(evidence.glob('inspector-table-phases-*'))-before
            assert len(created)==1,'ambiguous phase attempt'
            analyze(created.pop())
