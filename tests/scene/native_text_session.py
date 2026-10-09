"""Compare session rendering with frozen original standalone bytes and errors."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys,uuid
import text_session_cases as inputs
ROOT=inputs.ROOT
sys.path.insert(0,str(ROOT/'source/build'))
from check_text_runtime import verify
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()


def main():
    exe,evidence=map(Path,sys.argv[1:3]);folder=evidence/('text-session-'+uuid.uuid4().hex[:12]);folder.mkdir(parents=True)
    expected_path=ROOT/'tests/scene/text-session-expectations.json';expected=json.loads(expected_path.read_bytes())
    rows=inputs.cases();assert [v['id'] for v in rows]==[v['id'] for v in expected['results']]
    record=dict(family='TEXT-SESSION',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),
                oracle_sha256=sha(Path(__file__).read_bytes()),expectations_sha256=sha(expected_path.read_bytes()),cases=[],outcome='fail')

    def compare(index,result,path):
        want=expected['results'][index];assert result==want['metadata'],(rows[index]['id'],result,want['metadata'])
        assert path.exists()==('error' not in result),('partial output',rows[index]['id'])
        raw=path.read_bytes() if path.exists() else b''
        assert len(raw)==want['rgba_bytes'] and sha(raw)==want['rgba_sha256'],('pixels',rows[index]['id'])

    def invoke(name,wire,session=False):
        prefix=folder/name;args=[str(exe),str(prefix)]+(['--session'] if session else [])
        assert len(wire)<=32768
        q=subprocess.run(args,input=wire,capture_output=True,timeout=10)
        for suffix,data in (('.input.json',wire),('.stdout',q.stdout),('.stderr',q.stderr)):(folder/(name+suffix)).write_bytes(data)
        assert q.returncode==0 and not q.stderr,(name,q.returncode,q.stderr)
        return json.loads(q.stdout),prefix

    try:
        verify();assert sha((ROOT/'source/build/text-runtime.json').read_bytes())==expected['runtime_identity_sha256']
        assert sha(Path(inputs.__file__).read_bytes())==expected['recipe_sha256']
        assert sha((ROOT/'tests/scene/typography-cases.json').read_bytes())==expected['typography_cases_sha256']
        for i,row in enumerate(rows):
            wire=encode(row['request']);assert sha(wire)==expected['results'][i]['request_sha256']
            result,path=invoke('single-'+row['id'],wire);compare(i,result,path)
        record['cases'].append(dict(case='STANDALONE',outcome='pass',requests=len(rows)))
        orders={'FORWARD':list(range(len(rows))),'REVERSE':list(reversed(range(len(rows))))}
        orders['ALTERNATING']=[i for pair in zip(range(15),range(29,14,-1)) for i in pair]
        for name,order in orders.items():
            result,path=invoke(name,encode([rows[i]['request'] for i in order]),True)
            assert result['owner_error']=='text.owner' and len(result['results'])==len(order)
            compare(order[0],result['seed'],Path(str(path)+'.seed'))
            for j,i in enumerate(order):compare(i,result['results'][j],Path(str(path)+'.'+str(j)))
            record['cases'].append(dict(case=name,outcome='pass',requests=len(order),wrong_thread_refused=True))
        record['outcome']='pass'
    except BaseException as error:
        record['error']=repr(error);raise
    finally:
        record['finished_at']=datetime.now(timezone.utc).isoformat()
        record['files']={p.name:sha(p.read_bytes()) for p in folder.iterdir() if p.is_file() and p.name!='result.json'}
        (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(folder/'result.json',record['outcome'],flush=True)


if __name__=='__main__':main()
