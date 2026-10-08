"""Literal role expectations and external RGBA observations for theme typography."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source/build'))
from check_text_runtime import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    exe,evidence=map(Path,sys.argv[1:3]);folder=evidence/('typography-'+uuid.uuid4().hex[:12]);folder.mkdir(parents=True)
    cases=json.loads((ROOT/'tests/scene/typography-cases.json').read_bytes())
    record=dict(family='THEME-TYPOGRAPHY',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),fixed_inputs_sha256=sha(ROOT/'tests/scene/typography-cases.json'),cases=[],outcome='fail')
    counter=0
    def run(theme,**options):
        nonlocal counter
        counter+=1;wire=json.dumps(dict(text=cases['native_text'],theme=theme,**options)).encode();target=folder/(str(counter)+'.rgba')
        p=subprocess.run([str(exe),str(target)],input=wire,capture_output=True,timeout=10)
        for suffix,data in [('input.json',wire),('stdout',p.stdout),('stderr',p.stderr)]: (folder/(str(counter)+'.'+suffix)).write_bytes(data)
        assert p.returncode==0,(p.returncode,p.stderr)
        result=json.loads(p.stdout)
        if 'error' in result:
            assert not target.exists(),'partial raster on rejection';return result,b''
        data=target.read_bytes();assert len(data)==result['width']*result['height']*4 and data
        assert result['theme_unchanged'] and result['missing_glyphs']==0
        assert all(max(data[n:n+3])<=data[n+3] for n in range(0,len(data),4))
        return result,data
    def equivalent(font,**options):
        t=copy.deepcopy(cases['theme']);t.pop('font_roles');t['font']=copy.deepcopy(font);return run(t,**options)
    def pass_case(name):record['cases'].append(dict(case=name,outcome='pass'))
    try:
        verify();record['runtime_identity_sha256']=sha(ROOT/'source/build/text-runtime.json')
        assert run(cases['legacy'])==equivalent(cases['expected_base']);pass_case('legacy-equivalence')
        for role,font in cases['expected_roles'].items():
            expected=equivalent(font);actual=run(cases['theme'],role=role);assert expected==actual,role
            if role!='body':assert run(cases['theme'],role=role,fault='ignore-role')[1]!=expected[1],('ignored role witness',role)
            pass_case('role-'+role)
        normal=copy.deepcopy(cases['expected_base']);bold={**normal,'weight':700};italic={**normal,'style':'italic'}
        assert equivalent(normal)[1]!=equivalent(bold)[1];assert equivalent(normal)[1]!=equivalent(italic)[1]
        assert equivalent(bold,fault='ignore-weight')[1]!=equivalent(bold)[1];pass_case('weight-style-and-fault')
        a,_=equivalent({**normal,'size_dip':17.25});b,_=equivalent({**normal,'size_dip':17.25},numerator=3,denominator=2)
        assert a['logical']==b['logical'] and a['baseline']==b['baseline'] and b['height']>a['height'];pass_case('fractional-size-scale')
        missing={**normal,'family':'SysPane Missing Family 72'};a,_=equivalent(missing)
        assert a['fonts'] and missing['family'] not in a['fonts'] and a['height']<60;pass_case('literal-family-fallback')
        for contrast in ('light','dark'):
            a,p=run(cases['theme'],role='diagnostic',contrast=contrast);assert all(p[n]==255 for n in range(3,len(p),4))
            assert all(p[n]==p[n+1]==p[n+2] for n in range(0,len(p),4));pass_case('contrast-'+contrast)
        for font in cases['invalid_fonts']:
            t=copy.deepcopy(cases['theme']);t['font']=font;assert 'error' in run(t)[0]
        for role in cases['invalid_roles']:assert 'error' in run(cases['legacy'],role=role)[0]
        pass_case('invalid-no-partial-output');record['outcome']='pass'
    except BaseException as e:
        record['error']=repr(e);raise
    finally:
        record['finished_at']=datetime.now(timezone.utc).isoformat();record['files']={p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.name!='result.json'}
        (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(folder/'result.json',record['outcome'],flush=True)
if __name__=='__main__':main()
