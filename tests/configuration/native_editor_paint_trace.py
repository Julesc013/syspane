"""Independent native text-paint call stacks; does not qualify latency."""
from pathlib import Path
import json,os,shutil,subprocess,sys,uuid
import native_recovery_gui_limits as limits

h=limits.h
h.CASES=dict(limits.CASES,family='EDITOR-PAINT-TRACE')


def exercise(e):
    probe=Path(os.environ['SYSPANE_PAINT_TRACE_PATH']).resolve()
    assert probe.is_relative_to(h.ROOT/'out/campaign/editor-paint-trace')
    e['env']['LD_PRELOAD']=str(probe)
    e['report']['trace_library_sha256']=h.sha(probe.read_bytes())
    limits.exercise(e)


exercise.capture_timings=True
exercise.continue_after_case_failure=True


def decode(raw):
    assert len(raw)<=2*1024*1024,'trace transcript size'
    rows=[line.decode('ascii').split() for line in raw.splitlines() if line.startswith(b'paint-trace')]
    assert not raw.splitlines() or not raw.splitlines()[-1].startswith(b'paint-trace') or raw.endswith(b'\n'),'incomplete trace'
    result=[];seen=set();i=0
    while i<len(rows):
        row=rows[i];i+=1;assert len(row)==5 and row[0]=='paint-trace-begin'
        pid,count,total,overflow=map(int,row[1:]);assert 0<pid<2**31 and pid not in seen and 0<=count<=128 and 0<=total<2**64 and overflow==0
        seen.add(pid);stacks=[];calls=0
        for index in range(count):
            row=rows[i];i+=1;assert row[0]=='paint-trace' and len(row)>=7
            idx,n,first,last,depth=map(int,row[1:6]);assert idx==index and 0<n<=total and 0<first<=last<=total and 1<=depth<=32 and len(row)==depth+6
            offsets=[int(v,16) for v in row[6:]];assert all(0<v<2**64 for v in offsets)
            calls+=n;stacks.append(dict(calls=n,first=first,last=last,offsets=offsets))
        row=rows[i];i+=1;assert row==['paint-trace-end',str(pid),str(count),str(total)] and calls==total
        assert len({tuple(s['offsets']) for s in stacks})==len(stacks)
        result.append(dict(pid=pid,total=total,stacks=stacks))
    assert result,'missing trace';return result


def analyze(folder,fixture,compiler):
    raw=(folder/'result.json').read_bytes();report=json.loads(raw)
    symbolizer=Path(shutil.which('addr2line')).resolve();symbols={}
    result=dict(diagnostic_only=True,original_report_sha256=h.sha(raw),fixture_sha256=h.sha(fixture.read_bytes()),compiler=compiler,
                analyzer_sha256=h.sha(Path(__file__).read_bytes()),symbolizer=dict(path=str(symbolizer),sha256=h.sha(symbolizer.read_bytes())),cases=[])
    for case in report['cases']:
        record=json.loads((folder/case['case']/'result.json').read_bytes());transcript=(folder/case['case']/'stderr').read_bytes()
        blocks=decode(transcript);pids={v['pid'] for v in record['timings']}
        assert pids<={v['pid'] for v in blocks},'missing frontend lifetime trace'
        offsets=sorted({offset for block in blocks for stack in block['stacks'] for offset in stack['offsets']}-symbols.keys())
        if offsets:
            resolved=subprocess.check_output([str(symbolizer),'-C','-f','-e',str(fixture),*[hex(v-1) for v in offsets]],text=True,timeout=60).splitlines()
            assert len(resolved)==len(offsets)*2,'incomplete symbol resolution'
            assert all(resolved[i]!='??' and (not resolved[i+1].startswith('??:') or resolved[i]=='_start') for i in range(0,len(resolved),2)),'unresolved product stack'
            symbols.update({v:dict(function=resolved[i*2],source=resolved[i*2+1]) for i,v in enumerate(offsets)})
        for block in blocks:
            if block['pid'] not in pids:assert block['total']==0,'unexpected inherited product trace'
            for stack in block['stacks']:
                stack['frames']=[symbols[v] for v in stack['offsets']]
        result['cases'].append(dict(case=case['case'],original_outcome=case['outcome'],stderr_sha256=h.sha(transcript),blocks=blocks))
    (folder/'paint-trace.json').write_bytes(h.encoded(result))
    print(json.dumps([dict(case=c['case'],calls=sum(b['total'] for b in c['blocks']),stacks=sum(len(b['stacks']) for b in c['blocks'])) for c in result['cases']]))


if __name__=='__main__':
    if sys.argv[1]=='--observe':h.main(exercise,__file__,limits.CASES_PATH,'paint-trace-')
    else:
        assert os.geteuid()!=0
        root=h.ROOT/'out/campaign/editor-paint-trace'/uuid.uuid4().hex[:12];root.mkdir(parents=True)
        source=Path(__file__).with_name('editor_paint_trace.c');probe=root/'trace.so'
        command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-fPIC','-shared',str(source),'-ldl','-pthread','-o',str(probe)]
        subprocess.run(command,check=True)
        compiler_path=Path(shutil.which('gcc')).resolve()
        compiler=dict(command=command,version=subprocess.check_output(['gcc','--version'],text=True),compiler_sha256=h.sha(compiler_path.read_bytes()),source_sha256=h.sha(source.read_bytes()),library_sha256=h.sha(probe.read_bytes()))
        (root/'build.json').write_bytes(h.encoded(compiler));os.environ['SYSPANE_PAINT_TRACE_PATH']=str(probe)
        evidence=Path(sys.argv[4]).resolve();before=set(evidence.glob('paint-trace-*'))
        try:h.main(exercise,__file__,limits.CASES_PATH,'paint-trace-')
        finally:
            created=set(evidence.glob('paint-trace-*'))-before;assert len(created)==1
            analyze(created.pop(),Path(sys.argv[2]).resolve(),compiler)
