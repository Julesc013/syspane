"""Recompute native DING input, native ownership and calibrated negative controls."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path

from record_gnome_host import ROOT,digest,rgb
from record_gnome_composition import validate as composition
from record_gnome_focus import raw_file
from gnome_input import STEPS,clipboard_names,icon_center
from gnome_composition import FIXTURE,judge_samples
from oracle import evaluate


def validate(value,build):
    initial=composition(value,build,family='GNOME-INPUT-01',outer_outcome=False)
    return validate_observations(value,build,initial,value['observation']['icon_input'],value['observation']['composition']['icon_manager'])


def validate_observations(value,build,initial,result,expected_owner,expected_shell_pid=None):
    """Check input against a caller-validated composition gate and native lifetime."""
    env=value['environment']['explicit'];workspace=Path(value['workspace'])
    control=result['control'];owner=result['icon_manager'];shell_pid=value['observation']['manager']['pid'][0] if expected_shell_pid is None else expected_shell_pid
    if result['version']!='0.1.0' or control not in ['live','block-pointer','no-selection'] or value['icon_input_control']!=control or env['SYSPANE_GNOME_INPUT_CONTROL']!=control:
        raise ValueError('native input identity/control')
    if initial['outcome']!='pass' or owner!=expected_owner or result['icon_center']!=icon_center(value['observation']['composition']):
        raise ValueError('independent input prerequisite/coordinates')
    if result['background_before']!=value['observation']['composition']['background_settings_after']:
        raise ValueError('input background differs from composition prerequisite')
    if 'NO_AT_BRIDGE' in env or env.get('GTK_MODULES')!='atk-bridge' or env['AT_SPI_BUS_ADDRESS']!=env['DBUS_SESSION_BUS_ADDRESS']:
        raise ValueError('private native accessibility environment')
    runtime=json.loads((ROOT/'build-support/x11-input-runtime.json').read_text())
    if value['input_runtime_files']!=runtime['files'] or any(digest(Path(p).read_bytes())!=h for p,h in runtime['files'].items()):
        raise ValueError('pinned accessibility inputs')
    registry=[r for r in value['commands'] if r['command']==['/usr/libexec/at-spi2-registryd']]
    cleanup=[r for r in value['cleanup'] if r['process']=='registry']
    if len(registry)!=1 or registry[0]['pid']!=value['registry_pid'] or len(cleanup)!=1 or cleanup[0]['pid']!=value['registry_pid'] or cleanup[0]['exit'] not in [0,-15] or cleanup[0]['members_after_stop']:
        raise ValueError('owned accessibility registry identity/exit')
    identity=build/'x11-lab/identity.json'
    if value['folder_runtime_identity']!={'path':str(identity),'sha256':digest(identity.read_bytes())}:
        raise ValueError('pinned folder runtime')
    association=value['folder_association']
    if value['folder_association_after']!={k:association[k] for k in ['inputs','mimeapps_sha256']}:
        raise ValueError('private file association changed')
    launcher=(workspace/'data/applications/syspane-owned-folder.desktop').read_bytes()
    if launcher.decode()!=association['launcher'] or association['inputs']['syspane-owned-folder.desktop']!={'bytes':len(launcher),'sha256':digest(launcher)}:
        raise ValueError('private launcher identity')
    if association['mimeapps_sha256']!=digest(b'[Default Applications]\ninode/directory=syspane-owned-folder.desktop;\n') or digest((workspace/'config/mimeapps.list').read_bytes())!=association['mimeapps_sha256']:
        raise ValueError('private MIME association differs')
    raw=raw_file(value,'input_journal',workspace,'input.jsonl',8*1024**2)
    records=[json.loads(line) for line in raw.splitlines()]
    if len(records)>256 or any(r['kind']=='error' for r in records) or any(a['at_us']>b['at_us'] for a,b in zip(records,records[1:])):
        raise ValueError('input journal incomplete/order')
    selected=lambda kind:[r['value'] for r in records if r['kind']==kind]
    if selected('completed')!=[result] or selected('step')!=result['steps']:
        raise ValueError('input claims differ from raw journal')
    expected_steps=STEPS if control=='live' else STEPS[:2]
    if [r['step'] for r in result['steps']]!=expected_steps or result['not_run']!=STEPS[len(expected_steps):]:
        raise ValueError('input step sequence/completeness')
    x,y=result['icon_center']
    clicks=[{'x':700,'y':550,'button':1}]
    if control!='no-selection':clicks.append({'x':x,'y':y,'button':1})
    if control=='live':clicks += [{'x':700,'y':550,'button':1},{'x':700,'y':550,'button':1},
        {'x':x,'y':y,'button':3},{'x':700,'y':550,'button':1},{'x':x,'y':y,'button':1},
        {'x':x,'y':y,'button':1},{'x':700,'y':550,'button':1}]
    if selected('click')!=clicks or selected('selection-stimulus')!=[{'point':[x,y],'performed':control!='no-selection'}]:
        raise ValueError('native input stimuli differ')
    if selected('drag')!=([{'from':[1,33],'to':[179,251],'steps':12}] if control=='live' else []):
        raise ValueError('native drag stimulus differs')
    registrations=[result['accessibility_registration']]
    if control=='live':registrations.append(result['folder']['accessibility_registration'])
    if selected('accessibility-ready')!=registrations:
        raise ValueError('native accessibility registration record differs')
    for registration,pid in zip(registrations,[owner['pid']]+([result['folder']['pid']] if control=='live' else [])):
        if registration['pid']!=pid or not 0<=registration['finished_ns']-registration['started_ns']<=3000000000:
            raise ValueError('native accessibility registration identity/deadline')
    expected_names={'baseline-clear':[],'select':['Probe Folder'],'clear':[],'drag-select':['Probe Folder'],
                    'double-click-open':['Sentinel.txt'],'restore-clear':[]}
    previous=0;requestors=set();clipboards=[];outcomes=[]
    for row in result['steps']:
        name=row['step'];contents=name=='double-click-open';tree=row['tree'];native=row['native']
        if row['at_ns']<=previous:raise ValueError('input step time order')
        previous=row['at_ns']
        rgb(row['desktop_pixels'],800*600*3);rgb(row['marker_pixels'],128*96*3)
        pid=result['folder']['pid'] if contents else owner['pid']
        registration=registrations[1] if contents else registrations[0]
        if not tree or any(r['native_bus_pid']!=pid or r['bus_name']!=registration['bus_name'] for r in tree):
            raise ValueError('accessible tree is not the held native application')
        if len(tree)>256 or any(len(r['name'])>256 or len(r['path'])>12 for r in tree):
            raise ValueError('native accessibility tree capacity')
        if name in expected_names:
            clipboard=row['clipboard'];clipboards.append(clipboard)
            if clipboard['requestor'] in requestors:raise ValueError('fresh clipboard requestor required')
            requestors.add(clipboard['requestor'])
            if not clipboard['started_ns']<=clipboard['issued_ns']<=clipboard['owner_observed_ns']<=clipboard['finished_ns']<=row['at_ns']:
                raise ValueError('clipboard observation time order')
            if clipboard['target_name']!=('text/uri-list' if contents else 'x-special/gnome-copied-files'):
                raise ValueError('native clipboard target')
            names=clipboard_names(clipboard,workspace,contents)
            if names!=clipboard['names']:raise ValueError('clipboard names differ from raw bytes')
            changed=clipboard['owner_changed']
            if changed:
                binding=clipboard['owner_binding']
                if clipboard['owner']==clipboard['requestor'] or binding['pid']!=(pid if contents else shell_pid) or clipboard['owner'] & ~binding['resource_mask']!=binding['resource_base']:
                    raise ValueError('native clipboard resource owner')
                if clipboard['owner_observed_ns']-clipboard['issued_ns']>500000000 or clipboard['finished_ns']-clipboard['owner_observed_ns']>500000000 or len(clipboard['raw_utf8'].encode())>4096:
                    raise ValueError('native clipboard response budget')
            expected_window=result['folder']['window'] if contents else owner['window']
            actual=changed and names==expected_names[name] and native['active_window']==[expected_window]
            if contents:
                actual &= any(r['role']=='frame' and r['name']=='Probe Folder' and r['showing'] for r in tree)
        else:
            if row['clipboard'] is not None:raise ValueError('unexpected menu clipboard')
            shown=any(r['role']=='menu item' and r['name']=='Open' and r['showing'] for r in tree)
            actual=shown==(name=='context-menu')
        verdict='pass' if actual else 'fail'
        if row['outcome']!=verdict:raise ValueError('input step verdict differs from observations')
        outcomes.append(verdict)
    if selected('clipboard')!=clipboards or selected('clipboard-raw')!=[{k:v for k,v in c.items() if k!='names'} for c in clipboards]:
        raise ValueError('clipboard raw journal differs')
    expected_outcomes=['pass']*len(STEPS) if control=='live' else ['pass','fail']
    if outcomes!=expected_outcomes:raise ValueError('input control produced unexpected result')
    if control=='live':
        folder=result['folder'];executable=str(build/'x11-lab/sysroot/usr/bin/pcmanfm')
        if folder['executable']!=executable or env['SYSPANE_GNOME_FOLDER_EXECUTABLE']!=executable or folder['arguments']!=[executable,'--new-win',str(workspace/'home/Desktop/Probe Folder')]:
            raise ValueError('native folder executable/arguments')
        if folder['process_group']!=shell_pid or folder['session']!=shell_pid or folder['start_ticks']<=0 or folder['window'] & ~folder['resource_mask']!=folder['resource_base']:
            raise ValueError('native folder resource/lifetime')
        if folder['type']!=[folder['normal_type_atom']] or not result['folder_closed'] or selected('close-folder')!=[{'window':folder['window']}]:
            raise ValueError('native folder role/close')
        before=result['steps'][5]['native']['client_order_bottom_to_top']
        opened=result['steps'][6]['native']
        if set(opened['client_order_bottom_to_top'])-set(before)!={folder['window']}:
            raise ValueError('one new native folder client required')
        client=[c for c in opened['clients'] if c['window']==folder['window']]
        if len(client)!=1 or client[0]['pid']!=[folder['pid']] or client[0]['type']!=folder['type'] or folder['window'] in result['steps'][-1]['native']['client_order_bottom_to_top']:
            raise ValueError('native folder client identity/closure')
        if executable not in folder['mapped_files'] or any(digest(Path(p).read_bytes())!=h for p,h in folder['mapped_files'].items()):
            raise ValueError('native folder mapped artifact identity')
        final=result['final_composition'];marker=final['marker'];evaluation=evaluate(marker['trace'])
        if evaluation!=marker['evaluation'] or evaluation['outcome']!='pass' or [s['generation'] for s in marker['trace']['stimuli']]!=[1,2,3] or marker['trace']['end_us']!=2400000:
            raise ValueError('final changing marker differs')
        if marker['started_monotonic_ns']<=result['steps'][-1]['at_ns'] or len(marker['trace']['frames'])!=len(final['overlap_samples']):
            raise ValueError('final composition interval/coverage')
        for frame,overlap in zip(marker['trace']['frames'],final['overlap_samples']):
            if frame['start_us']!=overlap['marker_start_us'] or frame['end_us']>overlap['start_us']:raise ValueError('final paired capture order')
        calibration=[rgb(s['frames'][0]['pixels'],180*220*3) for s in value['observation']['composition']['calibrations']]
        final_result=judge_samples(calibration[2],final['overlap_samples'],calibration[:2])
        if final_result!=final['evaluation'] or final_result['icons']!=final_result['rectangle'] or final_result['icons']!='pass':
            raise ValueError('final native composition failed')
        for key in ['background_before','background_after']:
            if rgb(marker[key],128*96*3)!=bytes(FIXTURE['background_rgb'])*128*96:raise ValueError('final background pixels changed')
        if result['background_before']!=result['background_after']:raise ValueError('input background settings changed')
    expected='pass' if control=='live' else 'fail'
    if result['outcome']!=expected or value['outcome']!=expected:raise ValueError('native input outcome differs')
    return {'control':control,'outcome':expected,'steps':[{'step':r['step'],'outcome':r['outcome']} for r in result['steps']],
            'not_run':result['not_run'],'initial_composition':initial['outcome'],'final_composition':'pass' if control=='live' else 'not_run','cleanup':'confirmed'}


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
                           'runtime':{'gnome':value['lab_identity_sha256'],'folder':value['folder_runtime_identity']['sha256'],'accessibility':value['input_runtime_files']}})
    if sorted(r['control'] for r in results)!=['block-pointer','live','no-selection'] or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('complete source/runtime-identical input controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned output required')
    scripts=['build-support/record_gnome_input.py','build-support/record_gnome_composition.py','build-support/record_gnome_host.py',
             'build-support/record_gnome_focus.py','tests/desktop/gnome_input.py','tests/desktop/x11_input.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned GNOME/DING/PCManFM native icon input only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['Show Desktop focus integration fix','taskbar/task-switcher qualification','image wallpaper/policy','shell/icon-manager recovery','Wayland','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
