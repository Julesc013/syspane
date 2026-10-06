"""Validate the candidate-absent native focus comparison without changing acceptance."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest, rgb, validate_runtime
from record_gnome_reveal import validate as validate_reveal
from gnome_focus_baseline import MODES, FIXTURE, SCENE, judge, keyboard
from gnome_composition import masks, png_icon


def raw_file(value, key, workspace, name, maximum):
    record = value[key]
    path = Path(record['path']).resolve(strict=True)
    if path != workspace / name:
        raise ValueError('owned evidence path required')
    raw = path.read_bytes()
    if len(raw)>maximum or len(raw)!=record['bytes'] or digest(raw)!=record['sha256']:
        raise ValueError('raw evidence identity differs')
    return raw


def validate(value, build):
    observation = validate_runtime(value, build, 'GNOME-FOCUS-BASELINE-01', 'GNOME-FOCUS-BASELINE-01-')
    result = observation['focus_baseline']
    mode = result['mode']
    environment = value['environment']['explicit']
    workspace = Path(value['workspace'])
    if mode not in MODES or value['focus_baseline_mode'] != mode or environment['SYSPANE_GNOME_FOCUS_BASELINE'] != mode or value['outcome'] != 'pass':
        raise ValueError('completed named focus comparison required')
    if result['version'] != '0.1.0' or environment['SYSPANE_FOREGROUND_EVENTS'] != str(workspace/'foreground-events.jsonl'):
        raise ValueError('foreground event identity')
    for suffix in ['before','after']:
        if result['extensions_'+suffix] != MODES[mode] or result['binding_'+suffix] != FIXTURE['binding']:
            raise ValueError('native baseline settings differ')
    expected_background = {'picture-uri': "''", 'picture-uri-dark': "''", 'picture-options': "'none'",
                           'primary-color': "'#304860'", 'color-shading-type': "'solid'"}
    if result['background_settings_before'] != expected_background or result['background_settings_after'] != expected_background:
        raise ValueError('native background settings differ')
    owner = result['foreground']
    command = ['/usr/bin/python3', str(ROOT/'tests/desktop/gnome_foreground.py')]
    processes = [r for r in value['commands'] if r['command']==command]
    if len(processes)!=1 or processes[0]['pid']!=owner['pid'] or owner['arguments']!=command or owner['pid_origin']!='XResQueryClientIds':
        raise ValueError('foreground native ownership')
    if owner['process_group']!=owner['pid'] or owner['session']!=owner['pid'] or owner['start_ticks']<=0 or owner['executable'] not in value['foreground_mapped_files']:
        raise ValueError('foreground retained lifetime')
    if owner['window'] & ~owner['resource_mask'] != owner['resource_base'] or owner['geometry']!=FIXTURE['window'] or owner['type'] != [owner['normal_type_atom']]:
        raise ValueError('foreground normal geometry/type')
    cleanup = [r for r in value['cleanup'] if r['process']=='foreground']
    if len(cleanup)!=1 or cleanup[0]['pid']!=owner['pid'] or cleanup[0]['exit']!=0 or cleanup[0]['members_after_stop'] or owner['pid'] not in [r['pid'] for r in cleanup[0]['members_before_stop'] if r['state']!='Z']:
        raise ValueError('foreground cleanup/lifetime')
    identity = json.loads((build/'gnome-lab/identity.json').read_text())
    prefix = 'usr/share/gnome-shell/extensions/ding@rastersoft.com/'
    ding = {key[len(prefix):]:row for key,row in identity['files'].items() if key.startswith(prefix)}
    expected_extensions = {}
    icon = result['icon_manager']
    if mode != 'shell':
        if value['ding_inputs']!=ding or not icon:
            raise ValueError('exact native DING required')
        expected_extensions.update({'ding@rastersoft.com/'+key:row for key,row in ding.items()})
        script = str(workspace/'data/gnome-shell/extensions/ding@rastersoft.com/app/ding.js')
        shell_pid = observation['manager']['pid'][0]
        if icon['pid_origin']!='XResQueryClientIds' or icon['window'] & ~icon['resource_mask'] != icon['resource_base'] or script not in icon['arguments'] or icon['process_group']!=shell_pid or icon['session']!=shell_pid or icon['start_ticks']<=0:
            raise ValueError('DING native ownership')
        retained = next(r for r in value['cleanup'] if r['process']=='shell')['members_before_stop']
        if icon['pid'] not in [r['pid'] for r in retained if r['state']!='Z'] or icon['executable'] not in value['icon_manager_mapped_files']:
            raise ValueError('DING retained lifetime')
        if value['fixture_inputs']!=value['fixture_after'] or value['desktop_entries']!=['Probe Folder','Probe Folder/Sentinel.txt'] or value['desktop_entries_after']!=value['desktop_entries']:
            raise ValueError('owned icon fixture changed')
        if value['fixture_inputs']['data/icons']['SysPaneFixture/64x64/places/folder.png'] != {'bytes':len(png_icon()),'sha256':digest(png_icon())}:
            raise ValueError('native icon pixels differ')
    elif icon is not None or 'ding_inputs' in value:
        raise ValueError('shell-only baseline includes DING')
    if mode=='candidate':
        candidate = validate_reveal(value, build, family='GNOME-FOCUS-BASELINE-01', outer_outcome=False)
        for name in ['extension.js','metadata.json','surfaceLease.js','networkCache.js']:
            raw = (ROOT/'source/desktop/gnome/lab-marker'/name).read_bytes()
            expected_extensions['syspane-lab-marker@syspane.invalid/'+name] = {'bytes':len(raw),'sha256':digest(raw)}
        source = observation['reveal']
        expected_interval = {'actions':source['actions'],'samples':[{'start_us':f['start_us'],**r} for f,r in zip(source['trace']['frames'],source['samples'])]}
        if result['interval']!=expected_interval or result['foreground']!=source['foreground'] or result['icon_manager']!=observation['composition']['icon_manager']:
            raise ValueError('candidate interval differs from original reveal evidence')
    else:
        candidate = None
        if 'reveal' in observation or 'composition' in observation or value['composition_control'] is not None or value['reveal_control'] is not None:
            raise ValueError('candidate must be absent in the native baseline')
        frames = result['baseline']
        if len(frames)!=3 or any(frame!=frames[0] for frame in frames):
            raise ValueError('native baseline stability')
        for frame in frames:
            for key in ['marker','background']:
                if rgb(frame[key],128*96*3)!=bytes(SCENE['background_rgb'])*128*96:
                    raise ValueError('native baseline contains candidate/changed background')
            overlap = rgb(frame['overlap'],SCENE['overlap'][2]*SCENE['overlap'][3]*3)
            if icon: masks(overlap)
        if result['activation']['native']['active_window'] != [owner['window']] or rgb(result['activation']['pixels'],1200)!=bytes(FIXTURE['foreground_rgb'])*400:
            raise ValueError('native baseline activation differs')
    if value['enabled_extension_inputs']!=expected_extensions or value['enabled_extension_inputs_after']!=expected_extensions:
        raise ValueError('candidate absence/extension inventory differs')
    for row in result['interval']['samples']:
        rgb(row['overlap'],SCENE['overlap'][2]*SCENE['overlap'][3]*3)
        clients = row['native']['clients']
        foreground = [r for r in clients if r['window']==owner['window']]
        if len(foreground)!=1 or foreground[0]['pid']!=[owner['pid']] or foreground[0]['type']!=owner['type']:
            raise ValueError('foreground client changed during interval')
        if mode=='shell' and len(clients)!=1:
            raise ValueError('shell-only native client set differs')
    actual = judge(result['interval'], owner['window'], icon['window'] if icon else None)
    if actual != result['evaluation'] or actual['visual_reveal']!='pass' or actual['background']!='pass':
        raise ValueError('native visible/state observations differ or are incomplete')
    if candidate and (candidate['visual_reveal']!=actual['visual_reveal'] or candidate['focus']!=actual['focus']):
        raise ValueError('candidate focus classification disagrees with original oracle')
    for point in [result['positive_activation']['native'], result['after_keyboard']]:
        if point['active_window'] != [owner['window']] or point['showing_desktop'] != [0]:
            raise ValueError('keyboard positive-control focus unavailable')
    if result['unfocused_key']['started_ns'] < result['started_monotonic_ns']+2400000000:
        raise ValueError('keyboard probe alters fixed native interval')
    keys = keyboard(result)
    if keys != result['keyboard']:
        raise ValueError('keyboard claim differs from receipt evidence')
    raw = raw_file(value,'foreground_events',workspace,'foreground-events.jsonl',16384)
    events = [json.loads(line) for line in raw.splitlines()]
    if events != result['events_after_f10']['events'] or digest(raw)!=result['events_after_f10']['sha256'] or len(raw)!=result['events_after_f10']['bytes']:
        raise ValueError('keyboard journal differs from raw helper output')
    raw = raw_file(value,'focus_journal',workspace,'focus-baseline.jsonl',8*1024**2)
    records = [json.loads(line) for line in raw.splitlines()]
    if len(records)>180 or any(r['kind']=='error' for r in records):
        raise ValueError('focus journal incomplete')
    selected = lambda kind: [r['value'] for r in records if r['kind']==kind]
    if selected('completed') != [{k:v for k,v in result.items() if k not in ['interval','baseline']}]:
        raise ValueError('focus completion differs from preserved journal')
    if mode=='candidate':
        if selected('candidate_interval') != [result['interval']]: raise ValueError('candidate journal interval differs')
    elif selected('sample')!=result['interval']['samples'] or selected('action')!=result['interval']['actions'] or selected('baseline')!=result['baseline']:
        raise ValueError('baseline journal samples/actions differ')
    return {'mode':mode, **actual, **keys, 'candidate_acceptance':candidate['outcome'] if candidate else 'not_applicable', 'cleanup':'confirmed'}


def compare(results):
    if len(results)!=9 or any(sum(r['mode']==m for r in results)!=3 for m in MODES):
        raise ValueError('three repetitions per native mode required')
    fields = ['visual_reveal','focus','phase_roles','f9_delivered']
    signatures = {mode:[{k:r[k] for k in fields} for r in results if r['mode']==mode] for mode in MODES}
    if any(any(s!=group[0] for s in group) for group in signatures.values()):
        return {'outcome':'inconclusive','reason':'native repetitions differ'}
    stable = {mode:group[0] for mode,group in signatures.items()}
    equal = stable['ding']==stable['candidate']
    failure_without_bridge = equal and stable['ding']['focus']=='fail'
    return {'outcome':'stable','signatures':stable,'ding_and_candidate_equal':equal,
            'focus_failure_without_bridge':failure_without_bridge,
            'requires_ding_in_this_lab':failure_without_bridge and stable['shell']['focus']=='pass'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=9,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    build=args.build_dir.resolve(strict=True)
    results,identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2: raise ValueError('owned bounded report required')
        raw=path.read_bytes(); value=json.loads(raw)
        results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'os_release':value['environment']['os_release_sha256']}})
    if any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('source/runtime-identical comparison required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected: raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence': raise ValueError('owned output required')
    result={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned native focus comparison only',
            'reports':identities,'results':results,'comparison':compare(results),
            'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in ['build-support/record_gnome_focus.py','build-support/record_gnome_reveal.py','build-support/record_gnome_composition.py','build-support/record_gnome_host.py','tests/desktop/gnome_focus_baseline.py','tests/desktop/gnome_reveal.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']},
            'not_run':['specific upstream root cause','native integration fix','full focus/input/taskbar qualification','image wallpaper/policy','shell/icon-manager recovery','Wayland','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream: json.dump(result,stream,indent=2); stream.write('\n')
    print(json.dumps(result['comparison'],indent=2))


if __name__=='__main__':main()
