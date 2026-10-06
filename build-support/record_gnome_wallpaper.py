"""Verify independent wallpaper bytes, native settings, pixels and fault isolation."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path

from record_gnome_host import ROOT,digest,rgb
from record_gnome_composition import validate as composition
from record_gnome_focus import raw_file
from gnome_wallpaper import CONTROLS,FIXTURE,FIXTURE_PATH,judge,png,crop,parse_settings

SETTINGS_KEYS={'color-shading-type','picture-opacity','picture-options','picture-uri',
               'picture-uri-dark','primary-color','secondary-color','show-desktop-icons'}


def validate(value,build):
    prerequisite=composition(value,build,family='GNOME-WALLPAPER-01',outer_outcome=False)
    result=value['observation']['wallpaper'];workspace=Path(value['workspace']);control=result['control']
    if prerequisite['outcome']!='pass' or control not in CONTROLS or value['wallpaper_control']!=control or value['environment']['explicit']['SYSPANE_GNOME_WALLPAPER_CONTROL']!=control:
        raise ValueError('wallpaper prerequisite/control identity')
    if result['version']!='0.1.0' or result['fixture_sha256']!=digest(FIXTURE_PATH.read_bytes()) or result['icon_manager']!=value['observation']['composition']['icon_manager']:
        raise ValueError('wallpaper fixture/native ownership')
    if result['original_path']!=str(workspace/'wallpaper.png') or result['alternate_path']!=str(workspace/'wallpaper-alternate.png'):
        raise ValueError('owned wallpaper paths required')
    if result['file_before']['path']['uid']!=value['environment']['uid']:
        raise ValueError('wallpaper native owner differs')
    if set(parse_settings(result['settings_before']['stdout']))!=SETTINGS_KEYS:
        raise ValueError('complete pinned native background settings required')
    for stimulus,scheduled in zip(result['marker']['trace']['stimuli'],[0,800000,1600000]):
        if not scheduled<=stimulus['at_us']<=scheduled+50000:
            raise ValueError('wallpaper generation schedule differs')
    actual=judge(result,value['observation']['composition'])
    if result['evaluation']!=actual or value['outcome']!=actual['outcome']:
        raise ValueError('wallpaper claim differs from raw evidence')
    if actual['marker']['outcome']!='pass' or actual['composition']['icons']!=actual['composition']['rectangle'] or actual['composition']['icons']!='pass':
        raise ValueError('control must retain live native composition')
    first=result['baseline'][0]
    for previous,frame in zip(result['baseline'],result['baseline'][1:]):
        if frame['started_ns']-previous['finished_ns']<100000000 or frame['overlap']!=first['overlap'] or frame['witnesses']!=first['witnesses']:
            raise ValueError('native image baseline not stable/spaced')
    raw=raw_file(value,'wallpaper_journal',workspace,'wallpaper.jsonl',8*1024**2)
    records=[json.loads(line) for line in raw.splitlines()]
    if len(records)>180 or any(r['kind']=='error' for r in records):raise ValueError('wallpaper journal incomplete')
    selected=lambda kind:[r['value'] for r in records if r['kind']==kind]
    if selected('baseline')!=result['baseline'] or selected('fault')!=result['faults'] or selected('scene-enabled')!=[{'at_ns':result['scene_enabled_ns']}]:
        raise ValueError('wallpaper setup/fault differs from raw journal')
    if selected('sample')!=[{'marker':frame,'observation':row} for frame,row in zip(result['marker']['trace']['frames'],result['samples'])] or selected('completed')!=[{k:v for k,v in result.items() if k not in ['samples','baseline']}]:
        raise ValueError('wallpaper samples/completion differ from raw journal')
    expected_files={'wallpaper-original.png':png(),'wallpaper-alternate.png':png(),'wallpaper.png':png(control=='replace-file')}
    if set(value['wallpaper_artifacts'])!=set(expected_files):raise ValueError('wallpaper artifact set differs')
    for name,expected in expected_files.items():
        entry=value['wallpaper_artifacts'][name];path=Path(entry['path']).resolve(strict=True)
        if path!=workspace/name or entry['bytes']!=len(expected) or entry['sha256']!=digest(expected) or path.read_bytes()!=expected:
            raise ValueError('wallpaper artifact bytes/path differ')
    guards=['files','settings','pixels']
    target={'replace-file':'files','redirect-setting':'settings','cover-wallpaper':'pixels'}.get(control)
    expected={key:'fail' if key==target else 'pass' for key in guards}
    if any(actual[key]!=verdict for key,verdict in expected.items()):raise ValueError('wallpaper fault is not isolated to its intended dimension')
    before=result['file_before'];settings_before=result['settings_before']['values']
    after_settings=parse_settings(result['settings_after']['stdout'])
    if result['settings_after']['values']!=after_settings:raise ValueError('final settings differ from raw output')
    changed_settings={**settings_before,'picture-uri':repr((workspace/'wallpaper-alternate.png').as_uri())}
    required_settings=changed_settings if control=='redirect-setting' else settings_before
    if after_settings!=required_settings:raise ValueError('final native settings differ from control')
    if control!='replace-file' and result['file_after']!=before:raise ValueError('final original file changed unexpectedly')
    rows=list(zip(result['samples'],actual['checks']))
    if target:
        fault=result['faults'][0]
        prior=[check for _,check in rows if check['end_us']<fault['start_us']]
        later=[(row,check) for row,check in rows if check['at_us']>=fault['end_us']+200000]
        if len(prior)<3 or len(later)<3 or any(not all(check[k] for k in guards) for check in prior) or any(check[target] for _,check in later):
            raise ValueError('native fault transition coverage/deadline')
    else:
        later=rows
    for row,_ in later:
        if parse_settings(row['settings']['stdout'])!=required_settings:raise ValueError('native settings transition differs')
        if control=='cover-wallpaper':
            if rgb(row['witnesses'][0],128*96*3)!=bytes(FIXTURE['cover_rgb'])*128*96 or rgb(row['witnesses'][1],96*96*3)!=crop(FIXTURE['witnesses'][1]):
                raise ValueError('native cover pixels differ from the explicit fault')
        if control=='replace-file':
            pair=row['files'];old=before['held'];held=pair['held'];path=pair['path']
            stable=['device','inode','mode','uid','bytes','mtime_ns','sha256']
            if any(held[k]!=old[k] for k in stable) or held['links']!=0:
                raise ValueError('held original identity/content not preserved across replacement')
            if path['device']!=old['device'] or path['inode']==old['inode'] or path['mode']!=0o444 or path['uid']!=old['uid'] or path['links']!=1 or path['sha256']!=digest(png(True)) or path['bytes']!=len(png(True)):
                raise ValueError('native replacement identity/bytes differ')
    if control=='replace-file' and result['file_after']!=later[-1][0]['files']:
        raise ValueError('replacement changed after the interval')
    for key,expected_pixels in [('background_before',crop(FIXTURE['witnesses'][0])),
                               ('background_after',bytes(FIXTURE['cover_rgb'])*128*96 if control=='cover-wallpaper' else crop(FIXTURE['witnesses'][0]))]:
        if rgb(result['marker'][key],128*96*3)!=expected_pixels:raise ValueError('marker background witness differs')
    return {'control':control,'outcome':actual['outcome'],**{k:actual[k] for k in guards},
            'marker':'pass','icons':'pass','rectangle':'pass','samples':len(result['samples']),
            'max_gap_us':actual['composition']['max_gap_us'],'max_observation_us':actual['composition']['max_capture_us'],
            'fault_duration_us':result['faults'][0]['end_us']-result['faults'][0]['start_us'] if target else None,
            'cleanup':'confirmed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=4,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build=args.build_dir.resolve(strict=True)
    results,identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:raise ValueError('owned bounded report required')
        raw=path.read_bytes();value=json.loads(raw);results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'os_release':value['environment']['os_release_sha256']}})
    if sorted(r['control'] for r in results)!=sorted(CONTROLS) or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('complete source/runtime-identical wallpaper controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned output required')
    scripts=['build-support/record_gnome_wallpaper.py','build-support/record_gnome_composition.py','build-support/record_gnome_host.py',
             'build-support/record_gnome_focus.py','tests/desktop/gnome_wallpaper.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned GNOME/DING single-display PNG file/settings/pixel preservation only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['wallpaper policy','other formats/scaling/topologies','color-managed/GPU presentation','Show Desktop focus integration fix','taskbar/task-switcher qualification','shell/icon-manager recovery','Wayland','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
