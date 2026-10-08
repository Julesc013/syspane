"""Literal bytes, held native process cuts and refused private-filesystem entries."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,select,signal,socket,stat,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'tests/editor/recovery-store-cases.json').read_bytes())
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def read_line(p):
    assert select.select([p.stdout],[],[],8)[0],'store observation timeout'
    raw=p.stdout.readline();assert raw,'store EOF';return json.loads(raw)

def main():
    exe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('recovery-store-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='RECOVERY-STORE',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),uid=os.geteuid(),filesystem='ext4',kernel=list(os.uname()),executable_sha256=sha(exe.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),fixture_sha256=sha((ROOT/'tests/editor/recovery-store-cases.json').read_bytes()),cases=[])
    records={k:v.encode() for k,v in CASES['records'].items()};inputs={}
    for k,b in records.items():inputs[k]=folder/(k+'.json');write(inputs[k],b)
    def root(name,initial='old',pending=False):
        p=folder/name;p.mkdir(mode=0o700)
        if initial is not None:write(p/'draft.json',records[initial])
        if pending:write(p/'.pending',records['new'][:100])
        return p
    def call(p,op='read',file='-',phase='-',fault='-',good=True):
        q=subprocess.run([str(exe),str(p),op,str(file),phase,fault],capture_output=True,timeout=8)
        v=json.loads(q.stdout);assert (q.returncode==0)==good,(p,op,q.returncode,v,q.stderr)
        return v
    def check(p,want):
        data=None if want is None else records.get(want,want)
        v=call(p);assert v['bytes']==(len(data) if data is not None else None) and v['sha256']==(sha(data) if data is not None else None)
        assert v['version']['digest']==v['sha256'] and len(v['version']['instance'])==32
        assert (p/'draft.json').read_bytes()==data if data is not None else not (p/'draft.json').exists()
        assert set(x.name for x in p.iterdir())<=set(CASES['allowed_entries'])
        for x in p.iterdir():assert stat.S_ISREG(x.lstat().st_mode) and stat.S_IMODE(x.stat().st_mode)==0o600 and x.stat().st_uid==os.geteuid() and x.stat().st_nlink==1
        return v
    def passed(name,**fields):report['cases'].append(dict(case=name,outcome='pass',**fields))
    try:
        p=root('roundtrip',None);a=check(p,None)
        assert call(p,'replace',inputs['old'])['outcome']=='durable';b=check(p,'old');assert a['version']['instance']!=b['version']['instance']
        for i in range(12):
            key='new' if i%2==0 else 'old';assert call(p,'replace',inputs[key])['outcome']=='durable';check(p,key);assert len(list(p.iterdir()))==2
        assert call(p,'retire')['outcome']=='durable';check(p,None);passed('roundtrip')
        for initial in ('old',None):
            for phase,after in CASES['replace_phases'].items():
                p=root(('replace-' if initial else 'create-')+phase,initial)
                q=subprocess.Popen([str(exe),str(p),'replace',str(inputs['new']),phase,'stop'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
                try:
                    event=read_line(q);assert event==dict(event='phase',phase=phase,pid=q.pid)
                    q.kill();assert q.wait(timeout=3)==-signal.SIGKILL
                    want='new' if after=='new' else initial;v=check(p,want)
                    assert v['pending']==(phase in ('pending_created','pending_partial','pending_written','pending_flushed','publish_ready'))
                    if v['pending']:
                        assert call(p,'replace',inputs['new'])['outcome']=='durable';check(p,'new');assert not (p/'.pending').exists()
                    passed(p.name,cut=event,exit=q.returncode,reopened=v)
                finally:
                    if q.poll() is None:q.kill();q.wait(timeout=3)
                    write(folder/(p.name+'.stderr'),q.stderr.read())
        for phase,after in CASES['retire_phases'].items():
            p=root('retire-'+phase,pending=True);q=subprocess.Popen([str(exe),str(p),'retire','-',phase,'stop'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
            try:
                event=read_line(q);assert event['phase']==phase and event['pid']==q.pid;q.kill();assert q.wait(timeout=3)==-signal.SIGKILL
                v=check(p,None if after=='absent' else 'old');assert v['pending']==(phase=='admitted');passed(p.name,cut=event,exit=q.returncode,reopened=v)
            finally:
                if q.poll() is None:q.kill();q.wait(timeout=3)
        for phase in CASES['replace_phases']:
            p=root('failure-'+phase);v=call(p,'replace',inputs['new'],phase,'throw');published=phase in ('published','durable')
            assert v['outcome']==('unknown' if published else 'unchanged')
            if published:assert v['snapshot_error']=='recovery_store.unknown'
            check(p,'new' if published else 'old');passed(p.name,result=v)
        for phase in CASES['retire_phases']:
            p=root('retire-failure-'+phase,pending=True);v=call(p,'retire','-',phase,'throw');removed=phase in ('retired','durable')
            assert v['outcome']==('unknown' if removed else 'unchanged')
            if removed:assert v['snapshot_error']=='recovery_store.unknown'
            check(p,None if removed else 'old');passed(p.name,result=v)
        p=root('actual-short-write');v=call(p,'replace',inputs['new'],'-','file-size');assert v['outcome']=='unchanged' and v['error']=='recovery_store.write'
        check(p,'old');assert (p/'.pending').stat().st_size==1024
        assert call(p,'replace',inputs['new'])['outcome']=='durable';check(p,'new');passed('actual-short-write',result=v)
        for op,phase in [('replace','publish_ready'),('retire','retire_ready')]:
            p=root('revoke-'+op);v=call(p,op,inputs['new'],phase,'deny');assert v['outcome']=='unchanged' and v['error']=='recovery_store.denied';check(p,'old');passed(p.name,result=v)
        p=root('bounds',None);maximum=CASES['maximum_bytes'];large=records['new']+b' '*(maximum-len(records['new']));payload=folder/'maximum.json';write(payload,large)
        assert call(p,'replace',payload)['outcome']=='durable';check(p,large)
        write(payload,large+b' ');v=call(p,'replace',payload);assert v['outcome']=='unchanged' and v['error']=='recovery_store.size';check(p,large)
        write(payload,b'');assert call(p,'replace',payload)['outcome']=='unchanged';check(p,large);passed('bounds')
        p=root('malformed',None);write(p/'draft.json',b'not a recovery command');check(p,b'not a recovery command');assert call(p,'retire')['outcome']=='durable';check(p,None);passed('malformed')
        p=root('session',None);q=subprocess.Popen([str(exe),str(p),'session','-','-','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        try:
            original=read_line(q)
            def exchange(op,version=None):
                request=dict(op=op,file=str(inputs['new']));
                if version is not None:request['version']=version
                q.stdin.write(encoded(request)+b'\n');q.stdin.flush();return read_line(q)
            assert call(p,good=False)['error']=='recovery_store.busy'
            retired=exchange('retire',original['version']);assert retired['outcome']=='durable' and retired['snapshot']['bytes'] is None
            stale=exchange('replace',original['version']);assert stale['outcome']=='unchanged' and stale['error']=='recovery_store.conflict' and not (p/'draft.json').exists()
            current=retired['snapshot']['version']
            for op in ('deny','guard-throw'):
                v=exchange(op,current);assert v['outcome']=='unchanged' and v['error']=='recovery_store.denied' and v['snapshot']['version']==current
            for op in ('deny-read','deny-read-late'):assert exchange(op)['error']=='recovery_store.denied'
            assert exchange('wrong-thread')['error']=='recovery_store.owner'
            v=exchange('reenter',current);assert v['outcome']=='durable' and v['reentrant_rejected'];current=v['snapshot']['version']
            forged=copy.deepcopy(current);forged['digest']='0'*64
            v=exchange('replace',forged);assert v['error']=='recovery_store.conflict' and v['snapshot']['version']==current
            q.stdin.write(encoded(dict(op='exit'))+b'\n');q.stdin.flush();assert q.wait(timeout=3)==0;old_instance=current['instance']
        finally:
            if q.poll() is None:q.kill();q.wait(timeout=3)
        q=subprocess.Popen([str(exe),str(p),'session','-','-','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        try:
            fresh=read_line(q);forged=copy.deepcopy(fresh['version']);forged['instance']=old_instance
            q.stdin.write(encoded(dict(op='replace',file=str(inputs['old']),version=forged))+b'\n');q.stdin.flush();v=read_line(q);assert v['error']=='recovery_store.conflict'
            q.stdin.write(encoded(dict(op='exit'))+b'\n');q.stdin.flush();assert q.wait(timeout=3)==0
        finally:
            if q.poll() is None:q.kill();q.wait(timeout=3)
        check(p,'new');passed('stale-versions-guards-and-owner')
        for node in ('draft.json','.pending','.writer'):
            for kind in ('symlink','hardlink','directory','fifo','socket','permissions','oversized'):
                p=root('unsafe-'+node.replace('.','_')+'-'+kind,None);target=folder/(p.name+'-foreign');write(target,b'' if node=='.writer' else records['old']);before=target.read_bytes();x=p/node;sock=None
                if kind=='symlink':x.symlink_to(target)
                elif kind=='hardlink':os.link(target,x)
                elif kind=='directory':x.mkdir(mode=0o700)
                elif kind=='fifo':os.mkfifo(x,0o600)
                elif kind=='socket':
                    sock=socket.socket(socket.AF_UNIX);prior=Path.cwd()
                    try:os.chdir(p);sock.bind(node)
                    finally:os.chdir(prior)
                    x.chmod(0o600)
                elif kind=='permissions':write(x,b'');x.chmod(0o644)
                else:
                    write(x,b'');os.truncate(x,(1 if node=='.writer' else maximum+1))
                try:assert call(p,good=False)['error'].startswith('recovery_store.');assert target.read_bytes()==before
                finally:
                    if sock:sock.close()
                passed(p.name)
        p=root('foreign-entry');write(p/'foreign',b'untouched');assert call(p,good=False)['error']=='recovery_store.layout';assert (p/'foreign').read_bytes()==b'untouched';passed(p.name)
        p=root('root-permissions');p.chmod(0o755);assert call(p,good=False)['error']=='recovery_store.permissions';p.chmod(0o700);passed(p.name)
        p=root('root-target');link=folder/'root-link';link.symlink_to(p,target_is_directory=True);assert call(link,good=False)['error']=='recovery_store.path';passed('root-symlink')
        for kind in ('root','lock','current','same-current','staging'):
            p=root('substitute-'+kind);q=subprocess.Popen([str(exe),str(p),'replace',str(inputs['new']),'publish_ready','block'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
            try:
                assert read_line(q)['phase']=='publish_ready'
                if kind=='root':
                    saved=folder/(p.name+'-original');p.rename(saved);p.mkdir(mode=0o700);write(p/'draft.json',b'foreign root')
                else:
                    name={'lock':'.writer','current':'draft.json','same-current':'draft.json','staging':'.pending'}[kind]
                    raw=b'' if kind=='lock' else records['old'] if kind=='same-current' else records['new'] if kind=='staging' else b'foreign current'
                    replacement=folder/(p.name+'-replacement');write(replacement,raw);os.replace(replacement,p/name)
                q.stdin.write(b'resume\n');q.stdin.flush();v=read_line(q);assert q.wait(timeout=3)==0 and v['outcome']=='unchanged'
                if kind=='root':assert (saved/'draft.json').read_bytes()==records['old'] and (p/'draft.json').read_bytes()==b'foreign root'
                else:assert (p/'draft.json').read_bytes()==(b'foreign current' if kind=='current' else records['old'])
                passed(p.name,result=v)
            finally:
                if q.poll() is None:q.kill();q.wait(timeout=3)
        assert records['old']!=records['new'];p=root('wrong-byte-control');detected=False
        try:check(p,'new')
        except AssertionError:detected=True
        assert detected;check(p,'old');passed('wrong-byte-control',fault_detected=True)
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if stat.S_ISREG(p.lstat().st_mode)}
        report['nodes']={p.relative_to(folder).as_posix():dict(mode=p.lstat().st_mode,symlink=os.readlink(p) if p.is_symlink() else None) for p in folder.rglob('*')}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
