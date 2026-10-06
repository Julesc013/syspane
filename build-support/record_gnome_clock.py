"""Recompute native shell-clock acceptance from original public process/pixel evidence."""
import argparse
import json
from pathlib import Path
import sys
from record_gnome_host import ROOT, digest
from record_gnome_composition import validate as composition
sys.path.insert(0, str(ROOT/'tests/desktop'))
from gnome_clock_age import judge, MODES
from oracle import evaluate

def validate_raw(raw):
    result = judge(raw); mode = raw['mode']; pid = raw['peer']['pid']
    calls = raw['calls']; previous = raw['calibration']['end_ns']
    for call in calls:
        if not previous <= call['begin_ns'] <= call['end_ns'] <= call['begin_ns']+1_000_000_000:
            raise ValueError('native clock command order/deadline')
        previous = call['end_ns']
    expected = [('Start','starting')]
    if mode == 'peer-exit': expected += [('StopPeer','requested')]
    elif mode != 'wrong-peer': expected += [('Disable','closed')]
    expected += [('Start','closed'),('Disable','closed')]
    if [(c['method'],c['reply']) for c in calls if c['method']!='GetState'] != expected:
        raise ValueError('fixed native clock stimulus coverage')
    states = [json.loads(c['reply']) for c in calls if c['method']=='GetState']
    if raw['final'] not in states or ('ready' in raw and raw['ready'] not in states):
        raise ValueError('native diagnostic receipt differs')
    if raw['samples'] and any(raw['samples'][0]['begin_ns'] <= c['begin_ns'] <= raw['samples'][-1]['end_ns'] for c in calls):
        raise ValueError('diagnostic calls drove age observation')
    if raw['exit']['pid'] != pid or not calls[0]['end_ns'] <= raw['exit']['observed_ns'] <= raw['erasure']['samples'][-1]['end_ns']:
        raise ValueError('native held-peer exit interval')
    journal = raw['peer_journal']
    expected_events = ['waiting','stopped'] if mode in ('pending-disable','wrong-peer') else ['waiting','sample','stopped']
    if [r['event'] for r in journal] != expected_events or any(r['pid'] != pid or r['session'] != raw['peer']['session'] or r['parent'] != raw['peer']['session'] for r in journal):
        raise ValueError('native child sample/lifetime journal')
    if any(int(a['at_ns']) > int(b['at_ns']) for a,b in zip(journal,journal[1:])):
        raise ValueError('native child journal regressed')
    if mode not in ('pending-disable','wrong-peer'):
        stamp = journal[1]['sample_ns']
        if stamp != raw['ready']['sample'] or not int(journal[0]['at_ns']) <= int(stamp) <= int(journal[1]['at_ns']) <= int(raw['ready']['after']):
            raise ValueError('original native measurement was replaced')
    if evaluate(raw['post']['trace']) != raw['post']['evaluation'] or raw['post']['evaluation']['outcome'] != 'pass':
        raise ValueError('post-clock independent marker failed')
    if result != raw['evaluation']:
        raise ValueError('claimed clock result differs')
    return result

def validate(value, build):
    if composition(value,build,family='GNOME-CLOCK-01',outer_outcome=False)['outcome']!='pass':
        raise ValueError('clock composition prerequisite')
    result=value['observation']['clock_age']; workspace=Path(value['workspace']); mode=result['control']
    environment=value['environment']['explicit']
    if mode not in MODES or mode!=value['clock_age_control'] or mode!=environment['SYSPANE_GNOME_CLOCK_AGE']:
        raise ValueError('clock control identity')
    artifacts=value['clock_artifacts']
    if set(artifacts)!={'clock-age.json','clock-peer.jsonl'}:
        raise ValueError('clock artifact coverage')
    data={}
    for name,record in artifacts.items():
        path=Path(record['path'])
        if path!=workspace/name or path.resolve(strict=True)!=path or path.is_symlink():raise ValueError('owned clock evidence path')
        raw=path.read_bytes()
        if len(raw)!=record['bytes'] or digest(raw)!=record['sha256'] or len(raw)>(8*1024**2 if name=='clock-age.json' else 65536):raise ValueError('clock evidence identity/capacity')
        data[name]=raw
    raw=json.loads(data['clock-age.json'])
    if raw['peer_journal']!=[json.loads(line) for line in data['clock-peer.jsonl'].splitlines()]:raise ValueError('original child journal differs')
    if result['journal']!=str(workspace/'clock-age.json') or result['peer']!=raw['peer']:raise ValueError('clock observation identity')
    shell_pid=value['observation']['manager']['pid'][0]
    peer=raw['peer']
    if peer['session']!=shell_pid or peer['process_group']!=shell_pid or peer['start_ticks']<=0 or peer['pid']==shell_pid:raise ValueError('clock peer native session differs')
    expected=['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_clock_peer.py'),environment['SYSPANE_GNOME_CLOCK_SOCKET'],'slow-ready' if mode=='pending-disable' else 'normal']
    if peer['arguments']!=expected or environment['SYSPANE_GNOME_CLOCK_HELPER']!=expected[1]:raise ValueError('clock peer executable arguments differ')
    if raw['final']['exitStatus']!=0:raise ValueError('clock peer did not exit normally')
    prior_path=ROOT/'build-support/evidence/w-25-gnome-controller-recovery-linux-x64-gcc13.json';prior=json.loads(prior_path.read_text())
    if digest(prior_path.read_bytes())!=value['clock_build_record_sha256']:raise ValueError('native clock build identity')
    for name in ['libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib']:
        if digest((build/name).read_bytes())!=prior['artifacts'][name]['sha256']:raise ValueError('clock native artifact differs')
    library=str(build/'libsyspane_gjs_clock.so')
    # GI loads the native library lazily when the Clock class is first accessed.
    # Pending-disable intentionally cancels before native socket adoption.
    if (mode!='pending-disable' or library in value['mapped_files']) and value['mapped_files'].get(library)!=prior['artifacts']['libsyspane_gjs_clock.so']['sha256']:
        raise ValueError('native clock library was not mapped in the shell')
    if value['mapped_files'].get(str(build/'SysPaneClock-0.1.typelib'))!=prior['artifacts']['SysPaneClock-0.1.typelib']['sha256']:
        raise ValueError('native clock introspection identity differs')
    evaluated=validate_raw(raw)
    if evaluated!=result['evaluation'] or evaluated['outcome']!=value['outcome']:raise ValueError('outer clock outcome differs')
    expected_age='fail' if mode=='freeze-age' else 'pass'
    expected_expiry='fail' if mode=='ignore-expiry' else 'pass'
    if evaluated['age']!=expected_age or evaluated['expiry']!=expected_expiry:raise ValueError('native clock control missed its intended failure')
    return {'control':mode,**evaluated,'peer_exit':'confirmed','scope':'public clock age only; no operational field freshness'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('reports',nargs='+',type=Path);args=parser.parse_args();build=args.build_dir.resolve(strict=True)
    values=[json.loads(p.read_text()) for p in args.reports]
    if len(values)!=len(MODES) or {r['clock_age_control'] for r in values}!=set(MODES) or any(r['source_inputs']!=values[0]['source_inputs'] for r in values):raise ValueError('six source-identical clock modes required')
    if any(digest((ROOT/p).read_bytes())!=h for p,h in values[0]['source_inputs'].items()):raise ValueError('current clock source differs')
    report={'outcome':'pass','source_inputs':values[0]['source_inputs'],'cases':[validate(v,build) for v in values],
        'reports':[{'path':str(p),'sha256':digest(p.read_bytes())} for p in args.reports]}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Native shell clock controls verified:',len(values))

if __name__=='__main__':main()
