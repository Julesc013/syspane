"""Recompute measured GNOME network acceptance from original private evidence."""
import argparse
import json
from pathlib import Path
import sys
from record_gnome_host import ROOT, digest
from record_gnome_composition import validate as composition
sys.path.insert(0,str(ROOT/'tests/desktop'))
from gnome_live_network import judge, MODES

BUILD_RECORD='build-support/evidence/w-25-live-network-session-linux-x64-gcc13.json'

def validate_raw(raw):
    result=judge(raw);mode=raw['mode'];calls=raw['calls'];previous=0
    for call in calls:
        if not previous<=call['begin_ns']<=call['end_ns']<=call['begin_ns']+1_000_000_000:raise ValueError('command order/deadline')
        previous=call['end_ns']
    expected=[('Calibrate','calibrated'),('Start','starting')]
    if mode in ('revoke','ignore-clear'):expected.append(('Revoke','cleared'))
    elif mode not in ('hang','peer-exit'):expected.append(('Stop','stopping'))
    expected += [('Cleanup','cleared'),('Start','closed')]
    if [(c['method'],c['reply']) for c in calls if c['method']!='GetState']!=expected:raise ValueError('fixed stimulus coverage')
    states=[json.loads(c['reply']) for c in calls if c['method']=='GetState']
    if raw['final'] not in states:raise ValueError('final diagnostic receipt differs')
    start=next(c for c in calls if c['method']=='Start')
    if not calls[0]['end_ns']<=raw['calibration']['begin_ns']<=raw['calibration']['end_ns']<=raw['lower_ns']<=start['begin_ns']<=raw['samples'][0]['begin_ns']:raise ValueError('calibration/source order')
    if not raw['erasure']['samples'][-1]['end_ns']<=raw['post_clear']['begin_ns']<=raw['post_clear']['end_ns']<=raw['upper_ns']:raise ValueError('final erasure order')
    for role in ('supervisor','worker'):
        peer=raw['peers'][role];exited=raw['exits'][role]
        if peer['pid']!=exited['pid'] or peer['start_ticks']<=0 or not start['end_ns']<=exited['observed_ns']<=raw['post_clear']['begin_ns']:raise ValueError('held descendant identity/exit')
        if peer['session']!=peer['process_group'] or peer['session']==peer['pid']:raise ValueError('native inherited session')
    if raw['peers']['supervisor']['pid']!=raw['final']['session']['pid']:raise ValueError('retained native supervisor')
    spawned=[r for r in raw['final']['session']['events'] if r['event']=='spawned']
    if len(spawned)!=1 or spawned[0]['pid']!=raw['peers']['worker']['pid']:raise ValueError('retained native worker')
    previous=raw['lower_ns']
    for row in raw['producer']:
        stamp=int(row['now_ns'])
        if not previous<=stamp<=raw['upper_ns']:raise ValueError('original source clock order')
        previous=stamp
    if result!=raw['evaluation']:raise ValueError('claimed network outcome differs')
    failures={'freeze-age':'age','ignore-expiry':'freshness','wrong-value':'values','ignore-clear':'erasure'}
    for key in ('values','age','freshness','lease','erasure'):
        if result[key]!=('fail' if failures.get(mode)==key else 'pass'):raise ValueError('control missed its intended failure')
    return result

def validate(value,build):
    if composition(value,build,family='GNOME-NETWORK-LIVE-01',outer_outcome=False)['outcome']!='pass':raise ValueError('composition prerequisite')
    result=value['observation']['network_live'];workspace=Path(value['workspace']);environment=value['environment']['explicit'];mode=result['control']
    if mode not in MODES or mode!=value['network_live_control'] or mode!=environment['SYSPANE_GNOME_NETWORK_LIVE']:raise ValueError('network mode identity')
    artifacts=value['network_private_artifacts']
    if set(artifacts)!={'network-live.private.json','network-live-producer.private.jsonl'}:raise ValueError('private artifact coverage')
    data={}
    for name,record in artifacts.items():
        path=Path(record['path'])
        if path!=workspace/name or path.resolve(strict=True)!=path or path.is_symlink() or path.stat().st_mode & 0o777 != 0o600:raise ValueError('private evidence path/mode')
        content=path.read_bytes();maximum=4*1024**2 if name.endswith('jsonl') else 16*1024**2
        if len(content)>maximum or len(content)!=record['bytes'] or digest(content)!=record['sha256']:raise ValueError('private evidence identity/capacity')
        data[name]=content
    raw=json.loads(data['network-live.private.json'])
    if raw['producer']!=[json.loads(line) for line in data['network-live-producer.private.jsonl'].splitlines()]:raise ValueError('original source journal differs')
    if result['journal']!=str(workspace/'network-live.private.json') or result['peers']!=raw['peers']:raise ValueError('public observation identity')
    shell=value['observation']['manager']['pid'][0]
    for peer in raw['peers'].values():
        if peer['session']!=shell:raise ValueError('native shell session differs')
    expected=[str(build/'SysPane.CollectorProbe'),'stream',environment['SYSPANE_GNOME_NETWORK_ROOT'],mode if mode in ('lease-loss','hang') else 'hold',str(workspace/'network-live-producer.private.jsonl')]
    if raw['peers']['supervisor']['arguments']!=expected or environment['SYSPANE_GNOME_NETWORK_EXECUTABLE']!=expected[0] or environment['SYSPANE_GNOME_NETWORK_JOURNAL']!=expected[-1]:raise ValueError('native supervisor invocation differs')
    record=ROOT/BUILD_RECORD;prior=json.loads(record.read_text())
    if digest(record.read_bytes())!=value['network_build_record_sha256']:raise ValueError('native build record differs')
    for name in ('SysPane.CollectorProbe','libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if digest((build/name).read_bytes())!=prior['artifacts'][name]['sha256']:raise ValueError('tested native artifact differs')
    for name in ('libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if value['mapped_files'].get(str(build/name))!=prior['artifacts'][name]['sha256']:raise ValueError('shell native library mapping differs')
    actual=validate_raw(raw)
    if actual!=result['evaluation'] or actual['outcome']!=value['outcome']:raise ValueError('outer network outcome differs')
    return {'control':mode,**actual,'native_exit':'confirmed','scope':'measured network pixels in owned GNOME X11 laboratory'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('reports',type=Path,nargs='+');args=parser.parse_args()
    values=[json.loads(p.read_text()) for p in args.reports];build=args.build_dir.resolve(strict=True)
    if len(values)!=len(MODES) or {r['network_live_control'] for r in values}!=set(MODES) or any(r['source_inputs']!=values[0]['source_inputs'] for r in values):raise ValueError('nine source-identical network cases required')
    if any(digest((ROOT/p).read_bytes())!=h for p,h in values[0]['source_inputs'].items()):raise ValueError('current network source differs')
    report={'outcome':'pass','source_inputs':values[0]['source_inputs'],'cases':[validate(v,build) for v in values],
        'reports':[{'path':str(p),'sha256':digest(p.read_bytes())} for p in args.reports]}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print('Native measured network controls verified:',len(values))

if __name__=='__main__':main()
