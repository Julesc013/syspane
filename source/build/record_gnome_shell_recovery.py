"""Verify owned shell exit, native replacement and independently observed reattachment."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest
from record_gnome_composition import validate as composition
from record_gnome_input import validate_observations as input_observations
from record_gnome_focus import raw_file
from gnome_shell_recovery import CONTROLS, judge


def validate(value, build):
    result = value['observation']['shell_recovery']; control = result['control']
    events = result['events']; samples = result['samples']; workspace = Path(value['workspace'])
    if result.get('error') or result['version'] != '0.1.0' or control not in CONTROLS or value['shell_recovery_control'] != control or value['environment']['explicit']['SYSPANE_GNOME_SHELL_RECOVERY'] != control:
        raise ValueError('complete native shell recovery control required')
    exits = [e for e in events if e['event'] == 'shell-exit']
    if len(exits) != 1:raise ValueError('exactly one independent shell exit required')
    old_icon_exit = next((s for s in samples if s['old_icon_exited']), None)
    icon_exit = None if old_icon_exit is None else {'event':'exit-observed','pid':result['old_icon']['pid'],'observer':'pidfd','readable':True}
    initial = composition(value,build,family='GNOME-SHELL-RECOVERY-01',outer_outcome=False,icon_exit=icon_exit,shell_exit=exits[0])
    old = result['old_process']; old_pid = old['pid']; started = result['started_monotonic_ns']
    shell_commands = [r for r in value['commands'] if r['command'][0].endswith('/usr/bin/gnome-shell')]
    if initial['outcome'] != 'pass' or result['old_shell'] != value['observation']['manager'] or result['old_icon'] != value['observation']['composition']['icon_manager']:
        raise ValueError('original composition or ownership differs')
    if old_pid != shell_commands[0]['pid'] or old['arguments'] != shell_commands[0]['command'] or old['executable'] != shell_commands[0]['command'][0] or old['process_group'] != old_pid or old['session'] != old_pid or old['start_ticks'] <= 0:
        raise ValueError('original shell native process binding')
    if not value['observation']['composition']['marker']['started_monotonic_ns'] < result['held_before_ns'] < started:
        raise ValueError('original held descriptors predate composition or follow fault clock')
    if result['old_shell_mapped_files'] != value['mapped_files'] or result['old_icon_mapped_files'] != value['icon_manager_mapped_files']:
        raise ValueError('original mapped runtime identity differs')
    for name, process in [('old_shell',old),('old_icon',result['old_icon'])] + ([] if control=='no-restart' else [('new_shell',result['new_process']),('new_icon',result['new_icon'])]):
        files = result[name+'_mapped_files']
        # Mesa maps this owned writable data index. A replacement legitimately
        # updates it; its original digest remains an observation, not a claim
        # that mutable cache bytes are an immutable executable dependency.
        mutable_index = str(workspace/'cache/mesa_shader_cache/index')
        immutable = {p:h for p,h in files.items() if not (name=='old_shell' and p==mutable_index)}
        if process['executable'] not in immutable or any(digest(Path(p).read_bytes()) != expected for p,expected in immutable.items()):
            raise ValueError('mapped native runtime differs')
    if result['settings_before'] != value['observation']['composition']['background_settings_after'] or result['settings_after'] != result['settings_before']:
        raise ValueError('original wallpaper settings changed')
    raw = raw_file(value,'shell_recovery_journal',workspace,'shell-recovery.jsonl',12*1024**2)
    records = [json.loads(line) for line in raw.splitlines()]
    if len(records)>240 or any(r['kind']=='error' for r in records):raise ValueError('recovery journal incomplete')
    selected = lambda kind:[r['value'] for r in records if r['kind']==kind]
    if selected('completed') != [result] or selected('sample') != samples or selected('event') != events:
        raise ValueError('recovery report differs from raw journal')
    identity_keys = ['version','control','old_shell','old_process','old_icon','old_shell_mapped_files','old_icon_mapped_files','settings_before','held_before_ns']
    if selected('identity') != [{k:result[k] for k in identity_keys}|{'events':[],'samples':[],'not_run':['post-recovery-input']}]:
        raise ValueError('original held identity journal differs')
    interim = {k:v for k,v in result.items() if k not in ['samples','post','post_input','new_shell_mapped_files','new_icon_mapped_files','outcome']}
    interim['not_run'] = ['post-recovery-input']
    if selected('recovery-completed') != [interim]:raise ValueError('independent recovery result must precede dependent input')
    stimuli = [] if control=='no-restart' else result['post']['trace']['stimuli'][1:]
    if selected('generation') != stimuli:raise ValueError('post-recovery generation journal differs')
    actual = judge(result,value['observation']['composition'])
    if actual != result['evaluation']:raise ValueError('native recovery verdict differs')
    parent = value['shell_recovery_parent']
    if len(parent) != (1 if control=='no-restart' else 2):raise ValueError('parent recovery message count')
    armed = parent[0]
    if armed['message'] != {'shell_recovery_request':'arm','pid':old_pid} or armed['response'] != {'armed':old_pid} or not result['held_before_ns'] <= armed['received_ns'] <= armed['responded_ns'] < started:
        raise ValueError('parent did not arm original held lifetime')
    if control=='no-restart':
        if result['not_run'] != ['post-recovery-input'] or 'post_input' in result or 'new_shell' in result or 'new_icon' in result:
            raise ValueError('omitted restart invented a replacement or input')
        if any(s['shell'] is not None for s in samples if s['native_at_us'] >= exits[0]['at_us']+150000):
            raise ValueError('omitted restart unexpectedly retained native manager')
    else:
        request, launch, ready, attach = events[2:]
        replacement = result['new_process']; new_pid = replacement['pid']
        if shell_commands[1]['pid'] != new_pid or shell_commands[1]['command'] != replacement['arguments']:
            raise ValueError('replacement not the retained native child')
        response = parent[1]
        if response['message'] != {'shell_recovery_request':'restart','pid':old_pid} or response['response'] != {'replacement_started':new_pid,'old_exit':-9} or not started+request['at_us']*1000 <= response['received_ns'] <= response['responded_ns'] <= started+(launch['at_us']+1)*1000:
            raise ValueError('replacement parent/observer ordering differs')
        absent = [s for s in samples if exits[0]['at_us']+50000 <= s['native_at_us'] < request['at_us']]
        if len(absent)<3 or any(s['shell'] is not None for s in absent):raise ValueError('required native manager absence unobserved')
        if old_icon_exit is None or old_icon_exit['native_at_us'] > ready['at_us'] or any(not s['old_icon_exited'] for s in samples if s['native_at_us'] >= old_icon_exit['native_at_us']):
            raise ValueError('original DING exit not independently retained')
        before = [s for s in samples if s['end_us'] <= ready['at_us']]
        if not before or ready['at_us']-before[-1]['end_us']>50000 or before[-1]['shell'] != result['new_shell'] or before[-1]['icon'] != result['new_icon'] or not before[-1]['new_shell_live']:
            raise ValueError('readiness does not follow observed native replacement')
        xml = ready['peer']['interface_xml']
        if len(xml)>16384 or 'name="org.syspane.LabMarker"' not in xml or 'name="SetGeneration"' not in xml or 'name="SetSceneEnabled"' not in xml:
            raise ValueError('replacement bridge interface absent')
        retained = next(r for r in value['cleanup'] if r['process']=='shell-replacement')
        if retained['pid'] != new_pid or any(pid not in [p['pid'] for p in retained['members_before_stop'] if p['state']!='Z'] for pid in [new_pid,result['new_icon']['pid']]):
            raise ValueError('replacement native lifetimes not retained through cleanup')
        if control=='live':
            if result['not_run'] or 'post_input' not in result or result['post_input']['accessibility_registration']['started_ns'] < started+result['end_us']*1000:
                raise ValueError('replacement input missing or precedes recovery gate')
            input_observations(value,build,initial,result['post_input'],result['new_icon'],expected_shell_pid=new_pid)
        elif 'post_input' in result or result['not_run'] != ['post-recovery-input']:
            raise ValueError('failed reattachment claims dependent input')
    expected = 'pass' if control=='live' else 'fail'
    if result['outcome'] != expected or value['outcome'] != expected:raise ValueError('native shell outcome differs')
    return {'control':control,**actual,'post_recovery_input':'pass' if control=='live' else 'not_run',
            'old_shell_pid':old_pid,'new_shell_pid':result.get('new_process',{}).get('pid'),
            'supporting_window_id_reused':result.get('new_shell',{}).get('window')==result['old_shell']['window'] if control!='no-restart' else None,
            'native_ready_after_request_us':events[4]['at_us']-events[2]['at_us'] if control!='no-restart' else None,
            'samples':len(samples),'cleanup':'confirmed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=3,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build=args.build_dir.resolve(strict=True);results=[];identities=[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:raise ValueError('owned bounded report required')
        raw=path.read_bytes();value=json.loads(raw);results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'folder':value['folder_runtime_identity']['sha256'],'accessibility':value['input_runtime_files']}})
    if sorted(r['control'] for r in results)!=sorted(CONTROLS) or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('complete source/runtime-identical shell recovery controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    scripts=['source/build/record_gnome_shell_recovery.py','source/build/record_gnome_composition.py','source/build/record_gnome_input.py','source/build/record_gnome_host.py','source/build/record_gnome_focus.py','tests/desktop/gnome_shell_recovery.py','tests/desktop/gnome_input.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned output required')
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned GNOME X11 shell/compositor replacement, bridge reattachment and new-desktop input only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['user session-manager recovery','Show Desktop focus integration fix','wallpaper policy','other native profiles','Wayland/GPU','product controller/renderer/collector continuity','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
