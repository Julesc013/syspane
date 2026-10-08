"""Verify owned icon-manager replacement separately from marker and input recovery."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path

from record_gnome_host import ROOT,digest,rgb
from record_gnome_composition import validate as composition
from record_gnome_input import validate_observations as input_observations
from record_gnome_focus import raw_file
from gnome_icon_recovery import CONTROLS,judge


def validate(value,build):
    result=value['observation']['icon_recovery'];control=result['control'];workspace=Path(value['workspace'])
    events=result['events'];exits=[r for r in events if r['event']=='exit-observed']
    initial=composition(value,build,family='GNOME-ICON-RECOVERY-01',outer_outcome=False,icon_exit=exits[0] if len(exits)==1 else None)
    env=value['environment']['explicit'];old=result['old_icon'];shell=value['observation']['manager'];shell_pid=shell['pid'][0]
    if result['version']!='0.1.0' or control not in CONTROLS or value['icon_recovery_control']!=control or env['SYSPANE_GNOME_ICON_RECOVERY']!=control:
        raise ValueError('native recovery control identity')
    if initial['outcome']!='pass' or old!=value['observation']['composition']['icon_manager'] or result['old_shell']!=shell or result['shell_after']!=shell:
        raise ValueError('original native composition/lifetime differs')
    if result.get('error') or result['old_icon_mapped_files']!=value['icon_manager_mapped_files'] or not result['old_icon_mapped_files']:
        raise ValueError('original mapped files or completed recovery missing')
    for path,expected in result['old_icon_mapped_files'].items():
        if digest(Path(path).read_bytes())!=expected:raise ValueError('original mapped runtime differs')
    before=result['held_before']
    if before['old_live'] is not True or before['shell_live'] is not True or not value['observation']['composition']['marker']['started_monotonic_ns']<before['at_ns']<result['started_monotonic_ns']:
        raise ValueError('held native handles were not established after composition')
    if result['settings_before']!=value['observation']['composition']['background_settings_after'] or result['settings_after']!=result['settings_before']:
        raise ValueError('background changed during recovery')
    raw=raw_file(value,'icon_recovery_journal',workspace,'icon-recovery.jsonl',8*1024**2)
    records=[json.loads(line) for line in raw.splitlines()]
    if len(records)>180 or any(r['kind']=='error' for r in records):raise ValueError('native recovery journal incomplete')
    selected=lambda kind:[r['value'] for r in records if r['kind']==kind]
    if selected('completed')!=[result] or selected('event')!=events or selected('sample')!=[{'marker':f,'observation':s} for f,s in zip(result['trace']['frames'],result['samples'])]:
        raise ValueError('recovery claims differ from raw journal')
    if selected('generation')!=result['trace']['stimuli'][1:]:raise ValueError('native generation stimuli differ from journal')
    identities=selected('identity')
    if len(identities)!=1 or identities[0]!={k:result[k] for k in ['version','control','old_icon','old_icon_mapped_files','old_shell','settings_before','held_before']}|{'events':[],'samples':[],'not_run':['post-recovery-input']}:
        raise ValueError('initial held identity record differs')
    interim={k:v for k,v in result.items() if k not in ['samples','trace','post_input','new_icon_mapped_files','shell_after','outcome']}
    interim['not_run']=['post-recovery-input']
    if selected('recovery-completed')!=[interim]:raise ValueError('recovery result must precede dependent input')
    expected_events=(['freeze'] if control=='frozen-surface' else [])+['stop']+([] if control=='no-stop' else ['exit-observed','replacement-ready'])
    if [r['event'] for r in events]!=expected_events:raise ValueError('native recovery event sequence')
    if control=='frozen-surface':
        freeze=events[0];stop=events[1]
        if not 250000<=freeze['start_us']<=freeze['end_us']<=stop['start_us'] or freeze['end_us']-freeze['start_us']>50000:
            raise ValueError('one-way marker freeze timing')
    actual=judge(result,value['observation']['composition'])
    if actual!=result['evaluation']:raise ValueError('recovery verdict differs from native evidence')
    if actual['rectangle']!='pass' or actual['background']!='pass':raise ValueError('unrelated native composition changed')
    if control=='no-stop':
        if 'new_icon' in result or 'post_input' in result or actual['replacement']!='fail' or actual['post_ready_icons'] is not None or result['not_run']!=['post-recovery-input']:
            raise ValueError('no-stop control invented a new lifetime or dependent input')
        if not 2500000<=result['trace']['end_us']<=2600000 or actual['marker']['outcome']!='pass' or actual['marker']['observed_generations']!=['4','5'] or any(not r['icons'] for r in actual['checks']):
            raise ValueError('no-stop control must retain the live original desktop')
    else:
        new=result['new_icon']
        if new['pid_origin']!='XResQueryClientIds' or new['window']&~new['resource_mask']!=new['resource_base'] or new['process_group']!=shell_pid or new['session']!=shell_pid or new['start_ticks']<=old['start_ticks']:
            raise ValueError('new native process/resource identity')
        retained=next(row for row in value['cleanup'] if row['process']=='shell')['members_before_stop']
        if new['pid'] not in [r['pid'] for r in retained if r['state']!='Z'] or new['executable'] not in result['new_icon_mapped_files']:
            raise ValueError('replacement not retained through cleanup')
        if any(digest(Path(p).read_bytes())!=h for p,h in result['new_icon_mapped_files'].items()):raise ValueError('replacement mapped runtime differs')
        if actual['replacement']!='pass' or actual['post_ready_icons']!='pass':raise ValueError('native replacement/composition prerequisite failed')
        ready=next(r for r in events if r['event']=='replacement-ready')
        matches=[s for s in result['samples'] if s['native_at_us']==ready['at_us']]
        if len(matches)!=1 or matches[0]['icon']!=new or not matches[0]['new_live']:raise ValueError('readiness is not a native sample with a held replacement')
        if control=='frozen-surface':
            if actual['marker']['outcome']!='fail' or 'generation.deadline' not in actual['marker']['failures'] or actual['marker']['observed_generations']!=['4'] or 'post_input' in result or result['not_run']!=['post-recovery-input']:
                raise ValueError('frozen marker did not fail independently of native replacement')
        else:
            if actual['marker']['outcome']!='pass' or actual['marker']['observed_generations']!=['4','5','6'] or result['not_run'] or 'post_input' not in result:
                raise ValueError('live recovery failed progress or dependent work')
            post=result['post_input']
            if post['accessibility_registration']['started_ns']<result['started_monotonic_ns']+result['trace']['end_us']*1000:
                raise ValueError('post-recovery input began before measured recovery ended')
            input_observations(value,build,initial,post,new)
    expected='pass' if control=='live' else 'fail'
    if result['outcome']!=expected or value['outcome']!=expected:raise ValueError('native recovery outcome differs')
    stop=next(r for r in events if r['event']=='stop')
    ready=next((r for r in events if r['event']=='replacement-ready'),None)
    return {'control':control,'outcome':expected,'replacement':actual['replacement'],'marker':actual['marker']['outcome'],
            'observed_generations':actual['marker']['observed_generations'],'post_ready_icons':actual['post_ready_icons'],
            'rectangle':actual['rectangle'],'background':actual['background'],'post_recovery_input':'pass' if control=='live' else 'not_run',
            'same_window_id_reused':result.get('new_icon',{}).get('window')==old['window'] if ready else None,
            'old_pid':old['pid'],'new_pid':result.get('new_icon',{}).get('pid'),
            'replacement_ready_after_stop_us':ready['at_us']-stop['start_us'] if ready else None,
            'first_icon_absence_us':actual['first_icon_absence_us'],'samples':len(result['samples']),
            'max_gap_us':actual['max_gap_us'],'max_capture_us':actual['max_capture_us'],'cleanup':'confirmed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=3,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build=args.build_dir.resolve(strict=True)
    results,identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:raise ValueError('owned bounded report required')
        raw=path.read_bytes();value=json.loads(raw);results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'folder':value['folder_runtime_identity']['sha256'],'accessibility':value['input_runtime_files']}})
    if sorted(r['control'] for r in results)!=sorted(CONTROLS) or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('complete source/runtime-identical recovery controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    scripts=['source/build/record_gnome_icon_recovery.py','source/build/record_gnome_composition.py','source/build/record_gnome_input.py','source/build/record_gnome_host.py','source/build/record_gnome_focus.py','tests/desktop/gnome_icon_recovery.py','tests/desktop/gnome_input.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned output required')
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned DING exit/replacement, live composition and replacement-bound input only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['shell/compositor replacement','Show Desktop focus integration fix','wallpaper policy','other native profiles','Wayland/GPU','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
