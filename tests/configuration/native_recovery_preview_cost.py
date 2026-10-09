"""Diagnostic stage costs, not a GUI responsiveness qualification."""
from pathlib import Path
import native_frontend_recovery as h
import recovery_limits_inputs as inputs

h.CASES['family']='RECOVERY-PREVIEW-COST'


def exercise(e):
    report=e['report'];report['diagnostic_only']=True
    report['extension_sha256']=h.sha(Path(__file__).read_bytes())
    report['recipe_sha256']=h.sha(Path(inputs.__file__).read_bytes())
    for name,maximum in [('MAX-WIDGETS',False),('MAX-SCENE',True)]:
        q=e['Run'](name,enforce_timing=False)
        try:
            q.ready();result=q.call('preview-cost',scene=inputs.scene(maximum))
            assert 'error' not in result,result
            report['cases'].append(dict(case=name,outcome='observed',measurements=result))
            q.close();e['documents'](q)
        finally:q.finish()


if __name__=='__main__':h.main(exercise)
