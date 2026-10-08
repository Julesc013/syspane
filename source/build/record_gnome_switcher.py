"""Verify complete native application lists, ownership, pixels and fault controls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest, rgb
from record_gnome_composition import validate as composition
from record_gnome_focus import raw_file
from gnome_switcher import FIXTURE, FIXTURE_PATH, STEPS, judge, focused


def validate_tree(tree, shell_pid):
    rows=tree['rows'];paths=[tuple(r['path']) for r in rows]
    if not 1<=len(rows)<=512 or len(set(paths))!=len(paths) or paths[0]!=() or rows[0]['name']!='gnome-shell' or rows[0]['role']!='application':
        raise ValueError('complete native shell root required')
    if tree['native_bus_pid']!=shell_pid or not 0<=tree['finished_ns']-tree['started_ns']<=3000000000:
        raise ValueError('native shell peer/time identity')
    lookup=dict(zip(paths,rows))
    for row,path in zip(rows,paths):
        if len(path)>24 or len(row['name'])>256 or row['native_bus_pid']!=shell_pid or row['bus_name']!=tree['bus_name']:
            raise ValueError('native shell subtree identity/capacity')
        if len(row['states'])!=2 or row['showing']!=bool(row['states'][0]&(1<<25)) or row['selected']!=bool(row['states'][0]&(1<<23)):
            raise ValueError('native accessibility states differ')
        count=row['children_count']
        if not isinstance(count,int) or not 0<=count<=64 or row['pruned_hidden']!=bool(path and not row['showing'] and count):
            raise ValueError('hidden subtree pruning differs')
        children=[p for p in paths if p and p[:-1]==path]
        expected=[] if row['pruned_hidden'] else [path+(n,) for n in range(count)]
        if children!=expected:raise ValueError('visible native tree has missing or unordered children')
        if path and (path[:-1] not in lookup or path[-1]<0 or path[-1]>=lookup[path[:-1]]['children_count']):
            raise ValueError('orphaned accessibility node')


def validate(value,build):
    prerequisite=composition(value,build,family='GNOME-SWITCHER-01',outer_outcome=False)
    result=value['observation']['switcher'];control=result['control'];env=value['environment']['explicit']
    workspace=Path(value['workspace']);shell_pid=value['observation']['manager']['pid'][0]
    if prerequisite['outcome']!='pass' or control not in FIXTURE['controls'] or value['switcher_control']!=control or env['SYSPANE_GNOME_SWITCHER_CONTROL']!=control:
        raise ValueError('switcher prerequisite/control identity')
    if result['version']!='0.1.0' or result['fixture_sha256']!=digest(FIXTURE_PATH.read_bytes()):raise ValueError('switcher fixture identity')
    expected_settings={'favorite-apps':FIXTURE['favorites'],'switch-applications':FIXTURE['switch_binding']}
    if result['settings_before']!=expected_settings or result['settings_after']!=expected_settings:
        raise ValueError('native favorites/switch binding differs')
    if result['background_before']!=result['background_after'] or result['background_before']!=value['observation']['composition']['background_settings_after']:
        raise ValueError('background changed during native UI sequence')
    if 'NO_AT_BRIDGE' in env or env.get('GTK_MODULES')!='atk-bridge' or env['AT_SPI_BUS_ADDRESS']!=env['DBUS_SESSION_BUS_ADDRESS']:
        raise ValueError('private native accessibility environment')
    runtime=json.loads((ROOT/'source/build/x11-input-runtime.json').read_text())
    if value['input_runtime_files']!=runtime['files'] or any(digest(Path(p).read_bytes())!=h for p,h in runtime['files'].items()):raise ValueError('pinned accessibility runtime')
    registry=[r for r in value['commands'] if r['command']==['/usr/libexec/at-spi2-registryd']]
    cleanup=[r for r in value['cleanup'] if r['process']=='registry']
    if len(registry)!=1 or registry[0]['pid']!=value['registry_pid'] or len(cleanup)!=1 or cleanup[0]['pid']!=value['registry_pid'] or cleanup[0]['exit'] not in [0,-15] or cleanup[0]['members_after_stop']:
        raise ValueError('native accessibility registry lifetime')
    roles=['alpha','beta']+(['fault'] if control=='ordinary-window' else [])
    apps=result['applications']
    if set(apps)!=set(roles) or result['applications_after']!=apps or json.loads(env['SYSPANE_GNOME_SWITCHER_PIDS'])!={k:v['pid'] for k,v in apps.items()}:
        raise ValueError('held application set/lifetime differs')
    if len({a['pid'] for a in apps.values()})!=len(roles) or len({a['window'] for a in apps.values()})!=len(roles):raise ValueError('application identities alias')
    for role,app in apps.items():
        pid=app['pid'];command=['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_switcher_app.py'),role]
        starts=[r for r in value['commands'] if r['command']==command]
        ends=[r for r in value['cleanup'] if r['process']=='switcher-'+role]
        if len(starts)!=1 or starts[0]['pid']!=pid or len(ends)!=1 or ends[0]['pid']!=pid or ends[0]['exit']!=0 or ends[0]['members_after_stop']:
            raise ValueError('held native application start/cleanup')
        if app['role']!=role or app['arguments']!=command or app['process_group']!=pid or app['session']!=pid or app['start_ticks']<=0 or app['window']&~app['resource_mask']!=app['resource_base']:
            raise ValueError('native application ownership differs')
        if app['executable']!=str(Path('/usr/bin/python3').resolve()) or app['executable'] not in value['switcher_mapped_files'][role] or value['switcher_mapped_files'][role][app['executable']]!=digest(Path(app['executable']).read_bytes()):
            raise ValueError('native application executable identity')
        if app['geometry']!=FIXTURE['applications'][role]['window'] or app['type']!=[app['normal_type_atom']]:raise ValueError('normal application geometry/type')
    launchers=value['switcher_launchers'];expected_files={}
    if set(launchers)!=set(FIXTURE['applications']):raise ValueError('private launcher set')
    for role,item in FIXTURE['applications'].items():
        icon=workspace/'data/icons'/(item['id']+'.svg');name=item['id']+'.desktop'
        text=('[Desktop Entry]\nType=Application\nName='+item['name']+'\nExec=/usr/bin/python3 '+str(ROOT/'tests/desktop/gnome_switcher_app.py')+' '+role+'\nIcon='+str(icon)+'\nStartupWMClass='+item['id']+'\nTerminal=false\nDBusActivatable=false\n')
        icon_text='<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" fill="rgb('+','.join(map(str,item['icon_rgb']))+')"/></svg>\n'
        if launchers[role]!={'desktop':text,'icon':icon_text} or (workspace/'data/applications'/name).read_text()!=text or icon.read_text()!=icon_text:
            raise ValueError('private launcher/icon contents differ')
        expected_files[name]={'bytes':len(text.encode()),'sha256':digest(text.encode())}
    if value['switcher_launcher_inputs_after']!=expected_files:raise ValueError('private launcher inventory changed')
    raw=raw_file(value,'switcher_journal',workspace,'switcher.jsonl',8*1024**2)
    records=[json.loads(line) for line in raw.splitlines()]
    if len(records)>180 or any(r['kind'] in ['error','tree-incomplete'] for r in records):raise ValueError('switcher journal incomplete')
    selected=lambda kind:[r['value'] for r in records if r['kind']==kind]
    if selected('completed')!=[result] or selected('action')!=result['actions']:raise ValueError('switcher claims differ from journal')
    rows=result['observations'];expected_steps=STEPS[:2] if control=='no-switcher' else STEPS
    if [r['step'] for r in rows]!=expected_steps or [r['step'] for r in result['actions']]!=expected_steps:
        raise ValueError('native application sequence incomplete')
    not_run=STEPS[2:]+['final-composition'] if control=='no-switcher' else []
    if result['not_run']!=not_run:raise ValueError('unexecuted steps differ')
    if selected('accepted-observation')!=rows:raise ValueError('native accepted observations differ')
    normal_atom=apps['alpha']['normal_type_atom'];previous=0
    for row,action in zip(rows,result['actions']):
        if action['performed']!=(control!='no-switcher' or row['step']!='switcher'):raise ValueError('native action control differs')
        if not previous<=action['started_ns']<=action['issued_ns']==row['trigger_ns']<=row['started_ns']<=row['tree']['started_ns']<=row['tree']['finished_ns']<=row['finished_ns']<=action['issued_ns']+3000000000:
            raise ValueError('native action/observation timing differs')
        previous=row['finished_ns'];validate_tree(row['tree'],shell_pid)
        rgb(row['pixels'],800*600*3)
        if {c['window'] for c in row['native']['clients'] if c['type']==[normal_atom]}!={a['window'] for a in apps.values()}:
            raise ValueError('unexpected ordinary application client')
        if not any(r=={k:v for k,v in row.items() if k!='trigger_ns'} for r in selected('observation')):raise ValueError('native observation missing from raw journal')
    if selected('click') and [(r['role'],r['point']) for r in selected('click')]!=[(role,[FIXTURE['applications'][role]['window'][0]+100,FIXTURE['applications'][role]['window'][1]+60]) for role in ['beta','alpha']]:raise ValueError('native activation click sequence')
    if len(selected('click'))!=2:raise ValueError('native activation click completeness')
    initial_action=result['actions'][0]
    if any(not initial_action['started_ns']<=r['at_ns']<=initial_action['issued_ns'] for r in selected('click')):
        raise ValueError('native clicks fall outside their action')
    key_sequence=[]
    for key in ['Alt_L','Tab'] if control!='no-switcher' else []:
        key_sequence.extend([(key,True)]+([(key,False)] if key=='Tab' else []))
    if control!='no-switcher':
        key_sequence += [('Escape',True),('Escape',False),('Alt_L',False)]
        key_sequence += [('Alt_L',True),('Tab',True),('Tab',False),('Alt_L',False)]*2
        key_sequence += [('Super_L',True),('Super_L',False),('Escape',True),('Escape',False)]
    if [(r['name'],r['pressed']) for r in selected('key')]!=key_sequence:raise ValueError('native switcher key sequence')
    if control!='no-switcher':
        keys=selected('key');offset=0
        for action,count in zip(result['actions'][1:],[3,3,4,4,2,2]):
            group=keys[offset:offset+count];offset+=count
            if any(not action['started_ns']<=r['at_ns']<=action['issued_ns'] for r in group) or any(a['at_ns']>b['at_ns'] for a,b in zip(group,group[1:])):
                raise ValueError('native keys fall outside their action')
    actual=judge(result,value['observation']['composition'])
    if result['evaluation']!=actual or result['outcome']!=actual['outcome'] or value['outcome']!=actual['outcome']:raise ValueError('switcher verdict differs from native evidence')
    if actual['focus']!='pass':raise ValueError('native focus prerequisite/continuity failed')
    if control=='no-switcher':
        if actual['switcher']!={'visible':False,'entries':[]} or not focused(rows[1],'alpha',apps) or actual['outcome']!='fail':raise ValueError('missing-popup control did not expose absence')
    else:
        expected_names={FIXTURE['applications'][r]['name'] for r in roles}
        for name in ['switcher','overview']:
            items=actual[name]['entries']
            if not actual[name]['visible'] or len(items)!=len(roles) or {r['name'] for r in items}!=expected_names or not all(r['icon_matches'] for r in items):raise ValueError('native application-list control is not calibrated')
        if any(actual['final'][k]!='pass' for k in ['marker','icons','rectangle']):raise ValueError('final live composition failed')
        expected_outcome='pass' if control=='live' else 'fail'
        if actual['outcome']!=expected_outcome or actual['switcher_absence']!=expected_outcome or actual['dash_absence']!=expected_outcome:raise ValueError('ordinary-entry control did not expose both lists')
        trace=result['final_marker']['trace']
        if result['final_marker']['started_monotonic_ns']<=rows[-1]['finished_ns']:raise ValueError('final trace precedes restoration')
        for stimulus,scheduled in zip(trace['stimuli'],[0,800000,1600000]):
            if not scheduled<=stimulus['at_us']<=scheduled+50000:raise ValueError('final generation schedule')
        if selected('final-sample')!=[{'marker':f,'observation':s} for f,s in zip(trace['frames'],result['final_samples'])]:raise ValueError('final samples differ from journal')
    return {'control':control,'outcome':actual['outcome'],'switcher_absence':actual['switcher_absence'],'dash_absence':actual['dash_absence'],
            'switcher_entries':[r['name'] for r in actual['switcher']['entries']],
            'dash_entries':[r['name'] for r in actual['overview']['entries']] if actual['overview'] else None,
            'focus':actual['focus'],'final':actual['final'],'observations':len(rows),'max_tree_nodes':max(len(r['tree']['rows']) for r in rows),
            'max_transition_us':max((r['finished_ns']-r['trigger_ns'])//1000 for r in rows),'cleanup':'confirmed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=3,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build=args.build_dir.resolve(strict=True)
    results,identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:raise ValueError('owned bounded report')
        raw=path.read_bytes();value=json.loads(raw);results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'accessibility':value['input_runtime_files']}})
    if sorted(r['control'] for r in results)!=sorted(FIXTURE['controls']) or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):raise ValueError('complete source/runtime-identical controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    scripts=['source/build/record_gnome_switcher.py','source/build/record_gnome_host.py','source/build/record_gnome_composition.py','source/build/record_gnome_focus.py','tests/desktop/gnome_switcher.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned output required')
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Named GNOME/DING Alt+Tab and running-app overview dash absence only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['other shell/taskbar profiles','Show Desktop focus integration fix','wallpaper policy','shell/icon-manager recovery','Wayland/GPU','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
