"""Verify native selected/modal focus, closed targets and workspace invalidation."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import zipfile

from record_gnome_host import ROOT,digest,rgb
from record_gnome_focus import validate as focus,raw_file
from gnome_focus_scenarios import STEPS,RETURNS,judge_step
from oracle import evaluate


def validate(value,build):
    mode=value['focus_scenarios_mode'];result=value['observation']['focus_scenarios'];workspace=Path(value['workspace']).resolve(strict=True)
    env=value['environment']['explicit'];helper=result['helper_pid'];parent=value['focus_scenarios_parent']
    if mode not in ['restore','observe','helper-exit'] or result['mode']!=mode or result['version']!='0.1.0' or env.get('SYSPANE_GNOME_FOCUS_SCENARIOS')!=mode or env.get('SYSPANE_GNOME_FOCUS_INTEGRATION')!=('observe' if mode=='observe' else 'restore'):
        raise ValueError('explicit native scenario identity required')
    if value['family']!='GNOME-FOCUS-BASELINE-01' or workspace.parent!=build or not workspace.name.startswith('GNOME-FOCUS-BASELINE-01-') or env['HOME']!=str(workspace/'home') or value['focus_integration_mode'] is not None or value['focus_trace']:
        raise ValueError('owned untraced scenario environment')
    archive=raw_file(value,'source_archive',workspace,'source-inputs.zip',2*1024**2)
    import io
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        if len(source.namelist())!=len(value['source_inputs']) or set(source.namelist())!=set(value['source_inputs']) or any(digest(source.read(p))!=h for p,h in value['source_inputs'].items()):raise ValueError('source archive differs')
    command=['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_focus_controls.py')]
    launched=[r for r in value['commands'] if r['command']==command]
    retained=[r for r in value['cleanup'] if r['process']=='focus-controls']
    if len(launched)!=1 or launched[0]['pid']!=helper or len(retained)!=1 or retained[0]['pid']!=helper or retained[0]['members_after_stop']:
        raise ValueError('one retained native helper required')
    if parent['message']!={'focus_scenarios_request':'launch'} or parent['response']!={'focus_scenarios_pid':helper} or not result['launch_requested_ns']<=parent['received_ns']<=parent['responded_ns']<=result['launch_received_ns'] or result['launch_received_ns']-result['launch_requested_ns']>2000000000:
        raise ValueError('retained parent/observer launch ordering')
    journal=[json.loads(line) for line in raw_file(value,'focus_scenarios_journal',workspace,'focus-scenarios.jsonl',12*1024**2).splitlines()]
    selected=lambda kind:[r['value'] for r in journal if r['kind']==kind]
    if len(journal)>400 or selected('completed')!=[result]:raise ValueError('scenario completion differs from journal')
    prepared={k:result[k] for k in ['version','mode','initial_trace','started_monotonic_ns','workspace_settings_before','background_before','binding_before']}
    prepared['not_run']=STEPS+['final-marker']
    if selected('prepared')!=[prepared]:raise ValueError('scenario prerequisite journal differs')
    raw=raw_file(value,'focus_control_events',workspace,'focus-control-events.jsonl',32768)
    events=[json.loads(line) for line in raw.splitlines()]
    if not events or len(events)>128 or any(a['monotonic_ns']>=b['monotonic_ns'] for a,b in zip(events,events[1:])):raise ValueError('complete ordered native receipt journal')
    if mode=='helper-exit':
        if value['outcome']!='fail' or value.get('error')!='ValueError: retained focus helper not live' or result['outcome']!='inconclusive' or result.get('error')!='TimeoutError: native normal controls not ready':
            raise ValueError('startup failure must override earlier passed substeps')
        if retained[0]['exit']!=7 or retained[0]['members_before_stop'] or result['steps'] or result['roles'] or result['not_run']!=STEPS+['final-marker'] or 'final_marker' in result:
            raise ValueError('failed startup fabricated dependent completion')
        if [r['kind'] for r in journal]!=['prepared','error','completed'] or selected('error')!=[{'message':result['error']}]:raise ValueError('failed startup prefix differs')
        if len(events)!=1 or events[0]['event']!='exit-control' or events[0]['role']!='helper' or events[0]['native_time'] is not None:
            raise ValueError('native helper did not execute deliberate failure')
        for name in ['foreground','shell','bus','system-bus','observer','Xvfb']:
            rows=[r for r in value['cleanup'] if r['process']==name]
            if len(rows)!=1 or rows[0]['exit']!=0 or rows[0].get('members_after_stop'):raise ValueError('failed attempt cleanup unconfirmed')
        return {'mode':mode,'calibration':'pass','native_outcome':'fail','reason':'retained helper exited with code 7; outer attempt correctly failed','scenarios':'not_run'}
    original=focus(value,build);baseline=value['observation']['focus_baseline'];icon=baseline['icon_manager'];roles=result['roles'];steps=result['steps']
    if result.get('error') or value['outcome']!='pass' or result['outcome']!='pass' or result['not_run'] or set(roles)!=set(['alpha','beta','modal']) or [r['step'] for r in steps]!=STEPS:
        raise ValueError('complete native scenarios required')
    if original['focus']!=('pass' if mode=='restore' else 'fail') or original['f9_delivered']!=(mode=='restore') or not original['f10_delivered']:
        raise ValueError('original focus/key control changed')
    if retained[0]['exit']!=0 or helper not in [r['pid'] for r in retained[0]['members_before_stop'] if r['state']!='Z']:
        raise ValueError('native helper lifetime not retained')
    if selected('error') or selected('identity')!=[roles[r] for r in ['alpha','beta','modal']] or selected('launched')!=[{k:result[k] for k in ['helper_pid','launch_requested_ns','launch_received_ns']}]:
        raise ValueError('native identity/launch journal differs')
    if selected('step')!=[{k:v for k,v in r.items() if k not in ['evaluation','keyboard']} for r in steps] or selected('verdict')!=[r['evaluation'] for r in steps] or selected('sample')!=[{'step':r['step'],'sample':s} for r in steps for s in r['samples']]:
        raise ValueError('raw scenario samples/claims differ')
    if selected('keyboard')!=[{'step':r['step'],**r['keyboard']} for r in steps if r['step'] in RETURNS]:raise ValueError('raw keyboard observations differ')
    if any(r['kind'] not in ['prepared','identity','launched','sample','step','verdict','keyboard','completed'] for r in journal):raise ValueError('unknown journal record')
    expected_settings={'org.gnome.mutter/dynamic-workspaces':'false','org.gnome.desktop.wm.preferences/num-workspaces':'2',
                       'org.gnome.desktop.wm.keybindings/switch-to-workspace-1':"['<Control><Alt>1']",'org.gnome.desktop.wm.keybindings/switch-to-workspace-2':"['<Control><Alt>2']"}
    for suffix in ['before','after']:
        if result['workspace_settings_'+suffix]!=expected_settings or result['background_'+suffix]!=baseline['background_settings_after'] or result['binding_'+suffix]!=baseline['binding_after']:
            raise ValueError('private native settings changed')
    for role,owner in roles.items():
        if owner['role']!=role or owner['pid']!=helper or owner['arguments']!=command or owner['process_group']!=helper or owner['session']!=helper or owner['start_ticks']<=0 or owner['window']&~owner['resource_mask']!=owner['resource_base'] or owner['desktop']!=[0]:
            raise ValueError('native control resource/lifetime differs')
        x,y,w,h=owner['geometry']
        if not 0<=x<x+w<=800 or not 0<=y<y+h<=600 or w<128 or h<96:raise ValueError('native control geometry')
        expected_type=owner['dialog_type_atom'] if role=='modal' else owner['normal_type_atom']
        if owner['type']!=[expected_type] or owner['transient_for']!=([roles['beta']['window']] if role=='modal' else []):raise ValueError('normal/modal native role differs')
        if role=='modal' and owner['modal_atom'] not in owner['state']:raise ValueError('actual modal state absent')
        if role!='modal' and owner['geometry']!=({'alpha':[250,40,200,120],'beta':[250,380,200,160]}[role]):raise ValueError('normal control geometry differs')
    if len({r['window'] for r in roles.values()})!=3 or len({r['start_ticks'] for r in roles.values()})!=1:raise ValueError('distinct windows of one retained helper required')
    files=value['focus_helper_mapped_files']
    if roles['alpha']['executable'] not in files or any(digest(Path(p).read_bytes())!=h for p,h in files.items()):raise ValueError('native helper runtime differs')
    previous=result['launch_received_ns'];verdicts=[];keys=[]
    if result['started_monotonic_ns']<=baseline['focused_key']['finished_ns']+200000000:raise ValueError('new scenarios altered original acceptance interval')
    for row in steps:
        name=row['step'];start=row['started_monotonic_ns']
        if start<previous:raise ValueError('native scenario time order')
        expected_action=({'click':name.split('-')[0]} if name in ['beta-ready','alpha-ready','beta-for-dialog','beta-before-close','alpha-before-workspace','alpha-fresh'] else
                         {'click':'modal'} if name=='dialog-reselect' else {'keys':['F6']} if name=='dialog-open' else
                         {'keys':['Escape']} if name=='dialog-close' else {'close':roles['beta']['window']} if name=='close-target' else
                         {'keys':['Control_L','Alt_L','2' if name=='workspace-away' else '1']} if name in ['workspace-away','workspace-home'] else
                         {'show_desktop_if_active':steps[19]['samples'][-1]['native']['showing_desktop']==[1]} if name=='workspace-settle' else {'keys':['Super_L','d']})
        if row['action']['kind']!=expected_action:raise ValueError('native scenario stimulus changed')
        verdict=judge_step(row,roles,icon)
        if verdict!=row['evaluation'] or ((mode=='restore' or name not in RETURNS) and verdict['outcome']!='pass'):raise ValueError('fixed scenario outcome not established')
        verdicts.append(verdict)
        for sample in row['samples']:
            if sample['native'] is None:continue
            known={r['window']:r for r in roles.values()}|{baseline['foreground']['window']:baseline['foreground'],icon['window']:icon}
            clients=sample['native']['clients']
            if set(sample['native']['client_order_bottom_to_top'])!={c['window'] for c in clients} or len(clients)!=len({c['window'] for c in clients}):raise ValueError('native client list consistency')
            for client in clients:
                owner=known.get(client['window'])
                if owner is None or client['pid']!=[owner['pid']]:raise ValueError('unknown or foreign native scenario client')
                if owner is not icon and (client['type']!=owner['type'] or sample['memberships'].get(str(client['window']))!=[0]):raise ValueError('native role/workspace changed')
        previous=start+row['end_us']*1000
        if name in RETURNS:
            key=row['keyboard'];before=key['before'];after=key['after']
            for snapshot in [before,after]:
                prefix=snapshot['events'];encoded=b''.join((json.dumps(r,separators=(',',':'))+'\n').encode() for r in prefix)
                if snapshot['bytes']!=len(encoded) or snapshot['sha256']!=digest(encoded) or events[:len(prefix)]!=prefix or snapshot['mode']!=0o600 or snapshot['uid']!=value['environment']['uid']:
                    raise ValueError('actual native receipt prefix differs')
            if any(before[k]!=after[k] for k in ['device','inode','uid','mode']) or not previous<=key['started_ns']<=key['finished_ns']<=key['started_ns']+50000000:
                raise ValueError('receipt lifetime or stimulus timing differs')
            received=after['events'][len(before['events']):]
            actual=len(received)==1 and received[0]['event']=='key' and received[0]['role']==RETURNS[name] and received[0]['native_time']>0 and key['started_ns']<=received[0]['monotonic_ns']<=key['finished_ns']+200000000
            if key['delivered']!=actual or (mode=='restore' and not actual):raise ValueError('selected/modal window did not actually receive F9')
            keys.append({'step':name,'delivered':actual});previous=key['finished_ns']+150000000
    final=result['events_after']
    if final['events']!=events or final['bytes']!=len(raw) or final['sha256']!=digest(raw):raise ValueError('final receipt file differs')
    lifecycle=[(r['event'],r['role']) for r in events if r['event']!='key']
    if lifecycle!=[('created','alpha'),('created','beta'),('open-modal','beta'),('created','modal'),('close-modal','modal'),('destroy','modal'),('destroy','beta')]:raise ValueError('native fixture lifetime differs')
    decisions=result['final_trace'];rows=decisions['records'];initial=result['initial_trace']
    if decisions['version']!='0.1.0' or decisions['mode']!=mode or not decisions['enabled'] or rows[:len(initial['records'])]!=initial['records'] or len(rows)>256 or len(json.dumps(rows).encode())>65536:
        raise ValueError('bounded continuing native decision trace required')
    if any(a['monotonic_us']>=b['monotonic_us'] for a,b in zip(rows,rows[1:])):raise ValueError('native decision time order')
    expected=[(value['observation']['reveal']['started_monotonic_ns'],a,event,baseline['foreground']['pid']) for a,event in zip(value['observation']['reveal']['actions'],['entry','restore'])]
    expected += [(r['started_monotonic_ns'],r['action'],'entry' if r['step'].endswith('enter') else 'restore',helper) for r in steps if r['step'].endswith('enter') or r['step'] in RETURNS]
    transitions=[r for r in rows if r['event'] in ['entry','restore']]
    if len(transitions)!=len(expected):raise ValueError('missing or unsolicited native focus decision')
    for decision,(start,action,event,pid) in zip(transitions,expected):
        if decision['event']!=event or decision['target_pid']!=pid or decision['focus_pid']!=icon['pid'] or decision['workspace']!=0 or decision['showing']!=(event=='restore') or decision['event_type']!=1 or decision['key_symbol']!=100 or decision['state']!=64 or not decision['eligible_event'] or decision['native_time']<=0 or not start//1000+action['start_us']<=decision['monotonic_us']<=start//1000+action['end_us']+200000:
            raise ValueError('native focus decision not bound to actual selection/chord')
        if event=='restore' and decision['performed']!=(mode=='restore'):raise ValueError('named focus action differs')
    restored=[r for r in transitions if r['event']=='restore'][1:]
    if restored[0]['target_sequence']!=restored[2]['target_sequence'] or restored[1]['target_sequence']!=restored[3]['target_sequence'] or restored[0]['target_sequence']==restored[1]['target_sequence']:
        raise ValueError('distinct normal targets and modal parent required')
    def within(row):return [d for d in rows if row['started_monotonic_ns']//1000+row['action']['start_us']<=d['monotonic_us']<=row['started_monotonic_ns']//1000+row['action']['end_us']+200000]
    if not any(d['event']=='clear' and d['reason']=='unmanaging' for d in within(steps[14])) or not any(d['event']=='abstain' and d['target_pid'] is None for d in within(steps[15])):
        raise ValueError('closed native lifetime not invalidated')
    for index in [18,19]:
        if not any(d['event']=='clear' and d['reason']=='workspace' for d in within(steps[index])):raise ValueError('workspace transition did not invalidate pending target')
    marker=result['final_marker'];actual=evaluate(marker['trace'])
    if marker['evaluation']!=actual or actual['outcome']!='pass' or marker['started_monotonic_ns']<previous or marker['trace']['end_us']!=2400000 or [s['generation'] for s in marker['trace']['stimuli']]!=[1,2,3]:raise ValueError('final original changing-marker oracle failed')
    if any(rgb(marker[k],128*96*3)!=bytes([48,72,96])*128*96 for k in ['background_before','background_after']):raise ValueError('final background changed')
    if not marker['started_monotonic_ns']+2400000000<=result['finished_monotonic_ns']<=result['started_monotonic_ns']+20000000000:raise ValueError('bounded scenario completion clock')
    return {'mode':mode,'calibration':'pass','original_focus':original['focus'],'steps':verdicts,'keyboard':keys,
            'modal_focus':steps[9]['evaluation']['outcome'],'closed_target':'pass','workspace_invalidation':'pass','final_marker':'pass','cleanup':'confirmed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=3,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build=args.build_dir.resolve(strict=True);results=[];identities=[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:raise ValueError('owned bounded report required')
        raw=path.read_bytes();value=json.loads(raw);results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'os':value['environment']['os_release_sha256']}})
    if {r['mode'] for r in results}!={'restore','observe','helper-exit'} or any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):raise ValueError('source/runtime-identical controls required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned record required')
    scripts=['build-support/record_gnome_focus_scenarios.py','build-support/record_gnome_focus.py','build-support/record_gnome_host.py','build-support/record_gnome_reveal.py','build-support/record_gnome_composition.py','tests/desktop/gnome_focus_scenarios.py','tests/desktop/gnome_focus_baseline.py','tests/desktop/gnome_reveal.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    record={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass','scope':'Owned GNOME X11 selected/modal focus, target closure and workspace invalidation only',
            'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['moved windows','lock/session transitions','alternate reveal triggers','general enablement','wallpaper policy','other profiles','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
