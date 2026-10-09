"""Test-only callback attribution; original GUI failures remain failures."""
from pathlib import Path
import json,os,shlex,shutil,subprocess,sys,traceback,uuid
import native_recovery_gui_limits as limits
from editor_callback_trace import decode,correlate

h=limits.h
h.CASES=dict(limits.CASES,family='EDITOR-CALLBACK-TRACE')
ORACLE=(b'signals: arguments returns swapped after nested block disconnect destroy pass\n'
        b'timers: priority continue remove cancel self-remove data destroy pass\n')


def exercise(e):
    probe=Path(os.environ['SYSPANE_CALLBACK_TRACE_PATH']).resolve()
    assert probe.is_relative_to(h.ROOT/'out/campaign/editor-callback-trace') and probe.is_file()
    e['env']['LD_PRELOAD']=str(probe)
    e['report']['trace_library_sha256']=h.sha(probe.read_bytes())
    limits.exercise(e)


exercise.capture_timings=True
exercise.continue_after_case_failure=True


def build_probe():
    assert os.geteuid()!=0
    root=h.ROOT/'out/campaign/editor-callback-trace'/uuid.uuid4().hex[:12];root.mkdir(parents=True)
    source=Path(__file__).with_name('editor_callback_trace.c');fixture_source=source.with_name('editor_callback_fixture.c')
    probe=root/'trace.so';fixture=root/'fixture'
    compiler=Path(shutil.which('gcc')).resolve()
    flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gobject-2.0'],text=True))
    commands=[['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-fPIC','-shared',str(source),'-ldl','-pthread',*flags,'-o',str(probe)],
              ['gcc','-std=c11','-O0','-g','-Wall','-Wextra','-Werror',str(fixture_source),*flags,'-o',str(fixture)]]
    report=dict(compiler=dict(path=str(compiler),sha256=h.sha(compiler.read_bytes()),version=subprocess.check_output(['gcc','--version'],text=True)),
                gobject_version=subprocess.check_output(['pkg-config','--modversion','gobject-2.0'],text=True).strip(),
                sources={str(p.relative_to(h.ROOT)):h.sha(p.read_bytes()) for p in (source,fixture_source,Path(__file__),source.with_suffix('.py'),source.with_name('editor_callback_trace_tests.py'))},commands=[],outcome='fail')
    def run(command,name,env=None):
        q=subprocess.run(command,env=env,capture_output=True,timeout=60)
        (root/(name+'.stdout')).write_bytes(q.stdout);(root/(name+'.stderr')).write_bytes(q.stderr)
        report['commands'].append(dict(command=command,name=name,exit=q.returncode,stdout_sha256=h.sha(q.stdout),stderr_sha256=h.sha(q.stderr)))
        assert q.returncode==0,(name,q.returncode,q.stderr[-4000:]);return q
    try:
        for i,command in enumerate(commands):run(command,'build-'+str(i))
        report['artifacts']={p.name:h.sha(p.read_bytes()) for p in (probe,fixture)}
        report['linked_libraries']=subprocess.check_output(['ldd',str(probe)],text=True)
        libs=[Path(line.split(' => ')[1].split(' (')[0]) for line in report['linked_libraries'].splitlines() if ' => /' in line]
        report['runtime_sha256']={str(p):h.sha(p.read_bytes()) for p in libs}
        run([sys.executable,str(source.with_name('editor_callback_trace_tests.py'))],'decoder')
        env=dict(os.environ);env.pop('LD_PRELOAD',None)
        normal=run([str(fixture)],'normal',env);assert normal.stdout==ORACLE and not normal.stderr
        env['LD_PRELOAD']=str(probe)
        observed=run([str(fixture)],'observed',env);assert observed.stdout==ORACLE
        blocks=decode(observed.stderr);assert len(blocks)==1
        rows=blocks[0]['rows'];assert len(rows)==17,('missing fixture callback observations',len(rows))
        assert sum(v['parent']!=0 for v in rows)==4 and sum(v['label']=='apply' for v in rows)==1
        assert sum(v['kind']==2 for v in rows)==5
        report['fixture_rows']=rows;report['outcome']='pass'
    except Exception:
        report['failure']=traceback.format_exc();raise
    finally:
        (root/'build.json').write_bytes(h.encoded(report));print('Callback probe build:',root,flush=True)
    return probe,report


def analyze(folder,fixture,compiler):
    raw=(folder/'result.json').read_bytes();report=json.loads(raw)
    symbolizer=Path(shutil.which('addr2line')).resolve();symbols={}
    result=dict(diagnostic_only=True,outcome='fail',original_report_sha256=h.sha(raw),fixture_sha256=h.sha(fixture.read_bytes()),build=compiler,
                analyzer_sha256=h.sha(Path(__file__).read_bytes()),symbolizer=dict(path=str(symbolizer),sha256=h.sha(symbolizer.read_bytes())),cases=[])
    try:
        for case in report['cases']:
            record=json.loads((folder/case['case']/'result.json').read_bytes());transcript=(folder/case['case']/'stderr').read_bytes()
            blocks=decode(transcript);timings=record['timings'];pids={v['pid'] for v in timings}
            assert pids<={v['pid'] for v in blocks},'missing frontend lifetime trace'
            offsets=sorted({v['offset'] for block in blocks for v in block['rows']}-symbols.keys())
            if offsets:
                resolved=subprocess.check_output([str(symbolizer),'-C','-f','-e',str(fixture),*[hex(v) for v in offsets]],text=True,timeout=60).splitlines()
                assert len(resolved)==len(offsets)*2 and all(resolved[i]!='??' and not resolved[i+1].startswith('??:') for i in range(0,len(resolved),2)),'unresolved callback'
                symbols.update({v:dict(function=resolved[i*2],source=resolved[i*2+1]) for i,v in enumerate(offsets)})
            for block in blocks:
                if block['pid'] in pids:
                    block['gaps']=correlate(block,[v for v in timings if v['pid']==block['pid']])
                else:assert not block['rows'],'unexpected inherited product trace'
                for row in block['rows']:row['symbol']=symbols[row['offset']]
            case_result=dict(case=case['case'],original_outcome=case['outcome'],stderr_sha256=h.sha(transcript),blocks=blocks)
            all_rows=[dict(pid=b['pid'],**v) for b in blocks for v in b['rows']]
            case_result['longest_callbacks']=sorted(all_rows,key=lambda v:v['wall_ns'],reverse=True)[:12]
            case_result['longest_gaps']=sorted([dict(pid=b['pid'],**v) for b in blocks for v in b.get('gaps',[])],key=lambda v:v['gap_ns'],reverse=True)[:12]
            result['cases'].append(case_result)
        result['outcome']='pass'
    except Exception:
        result['failure']=traceback.format_exc();raise
    finally:(folder/'callback-trace.json').write_bytes(h.encoded(result))
    print(json.dumps([dict(case=c['case'],original_outcome=c['original_outcome'],longest_wall_us=c['longest_callbacks'][0]['wall_ns']/1000,longest_label=c['longest_callbacks'][0]['label']) for c in result['cases']]))


if __name__=='__main__':
    if sys.argv[1]=='--observe':h.main(exercise,__file__,limits.CASES_PATH,'callback-trace-')
    else:
        probe,compiler=build_probe()
        if sys.argv[1]=='--self-test':sys.exit(0)
        os.environ['SYSPANE_CALLBACK_TRACE_PATH']=str(probe)
        evidence=Path(sys.argv[4]).resolve();before=set(evidence.glob('callback-trace-*'))
        try:h.main(exercise,__file__,limits.CASES_PATH,'callback-trace-')
        finally:
            created=set(evidence.glob('callback-trace-*'))-before;assert len(created)==1
            analyze(created.pop(),Path(sys.argv[2]).resolve(),compiler)
