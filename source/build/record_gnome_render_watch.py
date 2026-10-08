"""Recompute render supervision from original native health and private pixels."""
import argparse
import json
from pathlib import Path
import sys
from record_gnome_host import ROOT, digest
from record_gnome_composition import validate as composition
sys.path.insert(0,str(ROOT/'tests/desktop'))
from gnome_render_watch import judge, MODES

BUILD_RECORD = 'out/evidence/w-25-controller-render-recovery-linux-x64-gcc13.json'


def validate_raw(raw):
    result = judge(raw); mode = raw['mode']; calls = raw['calls']; previous = 0
    for call in calls:
        if not previous <= call['begin_ns'] <= call['end_ns'] <= call['begin_ns']+1_000_000_000:
            raise ValueError('command order/deadline')
        previous = call['end_ns']
    expected = [('Calibrate','calibrated'),('Start','starting')]
    if mode in ('render-stall','false-progress','hidden'): expected.append(('Fault','faulted'))
    if mode == 'revoke': expected.append(('Revoke','cleared'))
    if mode in ('live','false-progress'): expected.append(('Stop','stopping'))
    expected += [('Cleanup','cleared'),('Start','closed')]
    if [(c['method'],c['reply']) for c in calls if c['method']!='GetState'] != expected:
        raise ValueError('fixed stimulus coverage')
    states = [json.loads(c['reply']) for c in calls if c['method']=='GetState']
    if raw['final'] not in states: raise ValueError('final diagnostic receipt differs')
    start = next(c for c in calls if c['method']=='Start')
    if not calls[0]['end_ns'] <= raw['calibration']['begin_ns'] <= raw['calibration']['end_ns'] <= raw['lower_ns'] <= start['begin_ns'] <= raw['baseline'][0]['begin_ns']:
        raise ValueError('calibration/source order')
    if not raw['baseline'][-1]['end_ns'] <= raw['stimulus']['begin_ns'] <= raw['stimulus']['end_ns'] <= raw['samples'][0]['begin_ns']:
        raise ValueError('native stimulus order')
    if not raw['erasure']['samples'][-1]['end_ns'] <= raw['post_clear']['begin_ns'] <= raw['post_clear']['end_ns'] <= raw['upper_ns']:
        raise ValueError('final erasure order')
    for role in ('supervisor','worker','watcher'):
        peer, exited = raw['peers'][role], raw['exits'][role]
        if peer['pid'] != exited['pid'] or peer['start_ticks'] <= 0 or not start['end_ns'] <= exited['observed_ns'] <= raw['post_clear']['begin_ns']:
            raise ValueError('held native identity/exit')
        if peer['session'] != peer['process_group'] or peer['session'] != raw['shell_before']['pid'] or peer['session'] == peer['pid']:
            raise ValueError('inherited shell session')
    if len({p['pid'] for p in raw['peers'].values()}) != 3:
        raise ValueError('independent native processes required')
    if raw['peers']['supervisor']['pid'] != raw['final']['session']['pid'] or raw['peers']['watcher']['pid'] != raw['final']['watch']['pid']:
        raise ValueError('retained native supervisors differ')
    events = raw['final']['session']['events']
    spawned = [r for r in events if r['event']=='spawned']; stopped = [r for r in events if r['event']=='stopped']
    if len(spawned)!=1 or spawned[0]['pid']!=raw['peers']['worker']['pid'] or len(stopped)!=1 or not stopped[0]['os_confirmed'] or stopped[0]['forced']:
        raise ValueError('source worker lifetime differs')
    if stopped[0]['pid']!=raw['peers']['worker']['pid'] or stopped[0]['code']!=0 or stopped[0]['signaled']:
        raise ValueError('source worker normal exit differs')
    journal = raw['watch_journal']
    if journal[0]['pid'] != raw['peers']['watcher']['pid'] or journal[0]['parent'] != raw['shell_before']['pid']:
        raise ValueError('watcher parent binding')
    authenticated = [r for r in journal if r['event']=='authenticated']
    if len(authenticated)!=1 or authenticated[0]['pid']!=raw['shell_before']['pid']:
        raise ValueError('native parent authentication missing')
    # GJS's bounded stdout copy must agree with the independent native journal.
    recorded = [r for r in raw['final']['watch']['events'] if r['event']!='error']
    if recorded != journal: raise ValueError('original independent journal differs from child receipts')
    beats = {'sent':-1,'received':-1}
    for row in journal:
        if row['event']=='heartbeat':
            direction=row['direction']
            if row['sequence'] != beats[direction]+1: raise ValueError('health sequence continuity')
            beats[direction]=row['sequence']
    signals = raw['signals']; expected_signals = []
    if mode=='watch-exit': expected_signals=[('watcher','SIGKILL')]
    if mode=='watch-hang': expected_signals=[('watcher','SIGSTOP')]
    if mode=='shell-freeze': expected_signals=[('shell','SIGSTOP'),('shell','SIGCONT')]
    if [(r['role'],r['signal']) for r in signals] != expected_signals:
        raise ValueError('held-process stimulus differs')
    for row in signals:
        pid = raw['shell_before']['pid'] if row['role']=='shell' else raw['peers'][row['role']]['pid']
        if row['pid']!=pid or not row['confirmed'] or not row['mono_begin_ms']<=row['mono_end_ms']<=row['mono_begin_ms']+500:
            raise ValueError('held-process signal proof')
    if expected_signals and raw['stimulus']!=signals[0]: raise ValueError('signal stimulus differs')
    if mode in ('render-stall','false-progress','hidden','revoke') and raw['stimulus'] not in calls:
        raise ValueError('private interface stimulus differs')
    if mode in ('watch-exit','revoke') and raw['erasure']['mono_begin_ms']!=raw['stimulus']['mono_end_ms']:
        raise ValueError('native erasure start rebased')
    if mode in ('live','false-progress') and raw['erasure']['mono_begin_ms']!=next(c for c in calls if c['method']=='Stop')['mono_end_ms']:
        raise ValueError('stop erasure start rebased')
    previous = raw['lower_ns']
    for row in raw['producer']:
        stamp = int(row['now_ns'])
        if not previous <= stamp <= raw['upper_ns']: raise ValueError('original source clock order')
        previous = stamp
    if result != raw['evaluation']: raise ValueError('claimed render outcome differs')
    if result['outcome'] != ('fail' if mode=='false-progress' else 'pass'):
        raise ValueError('control missed its intended outcome')
    if mode=='false-progress' and (result['age']!='fail' or any(result[k]!='pass' for k in ('values','lease','erasure'))):
        raise ValueError('false progress must expose frozen age with intact source and cleanup')
    return result


def validate(value, build):
    if composition(value,build,family='GNOME-RENDER-WATCH-01',outer_outcome=False)['outcome']!='pass':
        raise ValueError('composition prerequisite')
    result=value['observation']['render_watch']; workspace=Path(value['workspace']); environment=value['environment']['explicit']; mode=result['control']
    if mode not in MODES or mode!=value['render_watch_control'] or mode!=environment['SYSPANE_GNOME_RENDER_WATCH'] or environment['SYSPANE_GNOME_NETWORK_LIVE']!='live':
        raise ValueError('mode identity')
    artifacts=value['network_private_artifacts']
    if set(artifacts)!={'network-render-watch.private.json','network-live-producer.private.jsonl'}:
        raise ValueError('private artifact coverage')
    data={}
    for name,record in {**artifacts,'render-watch.jsonl':value['render_watch_journal']}.items():
        path=Path(record['path']); maximum=65536 if name=='render-watch.jsonl' else 4*1024**2 if name.endswith('jsonl') else 16*1024**2
        if path!=workspace/name or path.resolve(strict=True)!=path or path.is_symlink() or path.stat().st_mode & 0o777 != 0o600:
            raise ValueError('evidence path/mode')
        content=path.read_bytes()
        if len(content)>maximum or len(content)!=record['bytes'] or digest(content)!=record['sha256']:
            raise ValueError('evidence identity/capacity')
        data[name]=content
    raw=json.loads(data['network-render-watch.private.json'])
    for key,name in [('producer','network-live-producer.private.jsonl'),('watch_journal','render-watch.jsonl')]:
        if raw[key]!=[json.loads(line) for line in data[name].splitlines()]: raise ValueError('original journal differs')
    if result['journal']!=str(workspace/'network-render-watch.private.json') or result['peers']!=raw['peers'] or raw['mode']!=mode:
        raise ValueError('public observation identity')
    shell=value['observation']['manager']['pid'][0]
    if raw['shell_before']['pid']!=shell: raise ValueError('native shell lifetime differs')
    expected=[str(build/'SysPane.CollectorProbe'),'stream',environment['SYSPANE_GNOME_NETWORK_ROOT'],'hold',str(workspace/'network-live-producer.private.jsonl')]
    if raw['peers']['supervisor']['arguments']!=expected or environment['SYSPANE_GNOME_NETWORK_EXECUTABLE']!=expected[0] or environment['SYSPANE_GNOME_NETWORK_JOURNAL']!=expected[-1]:
        raise ValueError('source invocation differs')
    expected=[str(build/'SysPane.RecoveryProbe'),'render-watch',environment['SYSPANE_GNOME_NETWORK_ROOT']+'/r/s',str(workspace/'render-watch.jsonl')]
    if raw['peers']['watcher']['arguments']!=expected or environment['SYSPANE_GNOME_WATCH_EXECUTABLE']!=expected[0] or environment['SYSPANE_GNOME_WATCH_JOURNAL']!=expected[-1]:
        raise ValueError('watcher invocation differs')
    record=ROOT/BUILD_RECORD; prior=json.loads(record.read_text())
    if digest(record.read_bytes())!=value['network_build_record_sha256']: raise ValueError('native build record differs')
    for name in ('SysPane.CollectorProbe','SysPane.RecoveryProbe','libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if digest((build/name).read_bytes())!=prior['artifacts'][name]['sha256']: raise ValueError('tested native artifact differs')
    for name in ('libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if value['mapped_files'].get(str(build/name))!=prior['artifacts'][name]['sha256']: raise ValueError('native mapping differs')
    actual=validate_raw(raw)
    if actual!=result['evaluation'] or actual['outcome']!=value['outcome']: raise ValueError('outer outcome differs')
    return {'control':mode,**actual,'native_exit':'confirmed','scope':'owned GNOME X11 render supervision; no automatic replacement qualification'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',type=Path,required=True); parser.add_argument('--output',type=Path,required=True); parser.add_argument('reports',type=Path,nargs='+')
    args=parser.parse_args(); values=[json.loads(p.read_text()) for p in args.reports]; build=args.build_dir.resolve(strict=True)
    if len(values)!=len(MODES) or {r['render_watch_control'] for r in values}!=set(MODES) or any(r['source_inputs']!=values[0]['source_inputs'] for r in values):
        raise ValueError('eight source-identical render-watch cases required')
    if any(digest((ROOT/p).read_bytes())!=h for p,h in values[0]['source_inputs'].items()): raise ValueError('current sources differ')
    report={'outcome':'pass','source_inputs':values[0]['source_inputs'],'cases':[validate(v,build) for v in values],
            'reports':[{'path':str(p),'sha256':digest(p.read_bytes())} for p in args.reports]}
    args.output.write_text(json.dumps(report,indent=2)+'\n'); print('Native render-watch controls verified:',len(values))


if __name__=='__main__': main()
