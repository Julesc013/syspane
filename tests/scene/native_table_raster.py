"""Exact pre-change table raster metadata/pixels; no expectation regeneration."""
from pathlib import Path
import hashlib,json,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source/build'))
from check_text_runtime import verify
CASES=ROOT/'tests/scene/table-raster-cases.json'
EXPECTED=ROOT/'tests/scene/table-raster-expectations.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def invoke(exe,folder,case,mode):
    prefix=folder/(case['id']+'-'+mode)
    command=[str(exe),str(ROOT/'spec/fixtures/valid'),'TABLE-RASTER',case['id'],str(prefix),mode]
    run=subprocess.run(command,capture_output=True,timeout=10)
    prefix.with_suffix('.stdout').write_bytes(run.stdout);prefix.with_suffix('.stderr').write_bytes(run.stderr)
    assert run.returncode==0 and len(run.stdout)<=131072 and len(run.stderr)<=65536,(case['id'],run.returncode)
    value=json.loads(run.stdout);assert list(value)==['results']
    assert len(value['results'])==(2 if case.get('changed') else 1)
    for i,result in enumerate(value['results']):
        pixels=Path(str(prefix)+'.'+str(i))
        if 'error' in result:assert not pixels.exists(),'partial output after refusal'
        else:
            assert pixels.stat().st_size==result['pixel_bytes']==result['width']*result['height']*4
            result['rgba_sha256']=sha(pixels)
    return value

def main():
    exe,evidence=map(Path,sys.argv[1:3]);folder=evidence/('table-raster-'+uuid.uuid4().hex[:12]);folder.mkdir()
    verify();expected=json.loads(EXPECTED.read_bytes());assert expected['cases_sha256']==sha(CASES)
    report=dict(family='TABLE-RASTER',outcome='fail',executable_sha256=sha(exe),cases_sha256=sha(CASES),expectations_sha256=sha(EXPECTED),oracle_sha256=sha(Path(__file__)),cases=[])
    try:
        for case in json.loads(CASES.read_bytes())['cases']:
            for mode in ('isolated','session'):
                value=invoke(exe,folder,case,mode);assert value==expected['results'][case['id']],case['id']+' '+mode
                report['cases'].append(dict(case=case['id']+'-'+mode,outcome='pass'))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
