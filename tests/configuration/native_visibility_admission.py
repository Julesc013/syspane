"""Owned ext4 experiment; inspect bytes independently of the configuration reader."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,os,select,signal,subprocess,sys,time,uuid
from native_large_commands import Store,ROOT,write,encoded,full_body,receipt,accepted,sha
CASES=json.loads((ROOT/'tests/editor/visibility-admission-cases.json').read_bytes())
COMMAND=json.loads((ROOT/'spec/fixtures/valid/command-visibility.json').read_bytes())
class VisibilityStore(Store):
    def __init__(self,exe,folder):
        super().__init__(exe,folder)
        self.body=full_body(COMMAND);write(folder/'command.json',self.body)
    def args(self,phase='-'):return [str(self.exe),str(self.path),'visibility-commit',str(self.folder/'command.json'),phase,*map(str,self.imports)]
    def commit(self,phase='-'):return self.call('visibility-commit',self.folder/'command.json',phase,*self.imports)['result']
    def inspect(self,revision,fallback=False):
        if revision==40:return super().inspect(revision,fallback)
        actual=self.call('read');scene=copy.deepcopy(CASES['conditional']);scene['revision']='41'
        settings=copy.deepcopy(CASES['authored']['settings']);settings['revision']='41'
        assert actual['scene']==scene and actual['settings']==settings and actual['recovered_previous']==fallback
        g,m=receipt(self.path,self.body,fallback)
        assert json.loads((g/'scene.json').read_bytes())==scene and json.loads((g/'settings.json').read_bytes())==settings
        return actual
def main():
    exe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('visibility-admission-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='VISIBILITY-ADMISSION',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),executable_sha256=sha(exe),fixture_sha256=sha(ROOT/'tests/editor/visibility-admission-cases.json'),cases=[])
    try:
        f=VisibilityStore(exe,folder/'success');accepted(f.commit());f.inspect(41);accepted(f.commit());f.inspect(41)
        for _ in range(2):accepted(f.call('reconcile','E1','visibility')['result'])
        report['cases'].append(dict(case='commit-exact-replay-reconcile',outcome='pass',revision=41))
        for phase,revision in CASES['faults'].items():
            f=VisibilityStore(exe,folder/('cut-'+phase));p=subprocess.Popen(f.args(phase),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                assert select.select([p.stdout],[],[],5)[0];assert json.loads(p.stdout.readline())==dict(transition=phase)
                end=time.monotonic()+3;stopped=None
                while time.monotonic()<end:
                    stopped=os.waitid(os.P_PID,p.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                    if stopped:break
                    time.sleep(.005)
                assert stopped and stopped.si_status==signal.SIGSTOP;p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
                f.inspect(revision);result=f.call('reconcile','E1','visibility')['result']
                if revision==41:accepted(result);accepted(f.commit());f.inspect(41)
                else:assert result['outcome']=='unknown' and result['stored'] is None
                report['cases'].append(dict(case='cut-'+phase,outcome='pass',revision=revision,stopped_signal=stopped.si_status,exit=p.returncode))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=3)
        for fault in ('revoke','deny-visibility','corrupt-request','corrupt-scene'):
            f=VisibilityStore(exe,folder/fault)
            if fault=='revoke':assert f.commit(fault)['outcome']=='conflict';f.inspect(40)
            elif fault=='deny-visibility':assert f.commit(fault)['error']['code']=='policy.denied';f.inspect(40)
            else:
                accepted(f.commit());g,m=receipt(f.path,f.body);path=g/('request.json' if fault=='corrupt-request' else 'scene.json');write(path,path.read_bytes()+b' ')
                f.inspect(40,True);assert f.call('reconcile','E1','visibility')['result']['outcome']=='unknown'
            report['cases'].append(dict(case=fault,outcome='pass'))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and not p.is_symlink()}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
