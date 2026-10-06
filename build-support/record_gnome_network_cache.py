"""Validate retained network glyphs, policy erasure and bound private native evidence."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import stat
import sys
from types import SimpleNamespace

from record_gnome_host import ROOT,digest,rgb
from record_gnome_composition import validate as composition
from gnome_network_cache import judge,CONTROLS,CALIBRATION
from native_collector import verify_documents,verify_presentation
from oracle import evaluate

def private_file(record,workspace,name,maximum):
    path=Path(record['path'])
    if path!=workspace/name or path.is_symlink() or path.resolve(strict=True)!=path:raise ValueError('owned private path')
    info=path.stat()
    data=path.read_bytes()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or len(data)>maximum or len(data)!=record['bytes'] or digest(data)!=record['sha256']:raise ValueError('bound private file identity/mode')
    return data

def validate(value,build):
    if composition(value,build,family='GNOME-NETWORK-CACHE-01',outer_outcome=False)['outcome']!='pass':raise ValueError('live cache composition prerequisite')
    result=value['observation']['network_cache'];workspace=Path(value['workspace']);mode=result['control']
    if mode not in CONTROLS or value['network_cache_control']!=mode or value['environment']['explicit']['SYSPANE_GNOME_NETWORK_CACHE']!=mode:raise ValueError('native cache control identity')
    raw=json.loads(private_file(result['private'],workspace,'network-cache.private.json',16*1024**2))
    if raw['control']!=mode or raw['version']!='0.1.0' or raw['relay']!=result['relay'] or raw['unauthorized']!=['unauthorized']*3:raise ValueError('cache identity/admission')
    relay=result['relay'];pid=relay['pid'];command=['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_network_relay.py')]
    launched=[r for r in value['commands'] if r['command']==command]
    cleanup=[r for r in value['cleanup'] if r['process']=='network-relay']
    if len(launched)!=1 or launched[0]['pid']!=pid or relay['arguments']!=command or relay['process_group']!=pid or relay['session']!=pid or relay['start_ticks']<=0 or value['environment']['explicit']['SYSPANE_GNOME_NETWORK_PID']!=str(pid):raise ValueError('retained relay PID/connection authority')
    if len(cleanup)!=1 or cleanup[0]['pid']!=pid or cleanup[0]['exit']!=(73 if mode=='owner-loss' else 0) or cleanup[0]['members_after_stop']:raise ValueError('relay exit/cleanup')
    runtime=value['network_relay_mapped_files']
    if relay['executable'] not in runtime or any(digest(Path(p).read_bytes())!=h for p,h in runtime.items()):raise ValueError('relay runtime identity')
    artifacts=value['network_private_artifacts']
    expected_names={'network-cache.private.json','network-relay.private.jsonl','network-collector-1.private.json'}
    if mode!='owner-loss':expected_names.add('network-collector-2.private.json')
    if set(artifacts)!=expected_names or artifacts['network-cache.private.json']!=result['private']:raise ValueError('private evidence closure')
    journal=[json.loads(line) for line in private_file(artifacts['network-relay.private.jsonl'],workspace,'network-relay.private.jsonl',1024**2).splitlines()]
    calls=raw['calls'];ready=journal[0]
    if journal[1:]!=[c['native'] for c in calls] or ready.get('event')!='ready' or ready['pid']!=pid or not ready['owner'].startswith(':'):raise ValueError('relay raw receipt journal')
    last=value['observation']['composition']['marker']['started_monotonic_ns']+2400000000
    for call in calls:
        native=call['native']
        if call['peer_pid']!=pid or native['owner']!=ready['owner'] or native['request']!={'method':call['method'],'args':call['args']}:raise ValueError('native call peer/payload')
        limit=6_000_000_000 if call['method']=='Collect' else 1_000_000_000
        if not last<=call['started_ns']<=native['started_ns']<=native['finished_ns']<=call['finished_ns']<=call['started_ns']+limit:raise ValueError('native call order/deadline')
        last=call['finished_ns']
    # Exact fixed commands leave no room to drop the revoked replay or regrant gap.
    expected=[('Attach',[],'accepted'),('Heartbeat',[0],'accepted'),('Frame',['0','1',CALIBRATION],'restricted'),
        ('Policy',['7',True],'cleared'),('Frame',['7','1',CALIBRATION],'accepted'),
        ('Policy',['7',True],'duplicate'),('Policy',['6',False],'invalid'),
        ('Frame',['7','2',dict(CALIBRATION,generation='00')],'invalid'),
        ('Frame',['7','2',dict(CALIBRATION,extra='forbidden')],'invalid'),
        ('Frame',['7','0',CALIBRATION],'invalid'),
        ('Frame',['7','2',dict(CALIBRATION,values=['1234567890',None,'1'*33+'.000',None])],'capacity')]
    if raw['capacity_state']!={'enabled':True,'closed':False,'permitted':True,'revision':'7','sequence':'1','entries':0,'labels':0}:raise ValueError('capacity did not clear complete native cache')
    counter=1
    frames=[];collect_index=0
    for grant,sequence in [('7','2')]+([] if mode=='owner-loss' else [('9','1')]):
        expected.extend([('Heartbeat',[counter],'accepted'),('Collect',[],None),('Heartbeat',[counter+1],'accepted')]);counter+=2
        collect_call=[c for c in calls if c['method']=='Collect'][collect_index];collect_index+=1
        frame=collect_call['native']['reply']['frame'];frames.append(frame)
        expected.append(('Frame',[grant,sequence,frame],'accepted'))
        if grant=='7':
            if mode=='owner-loss':expected.append(('Exit',[73],'exiting'))
            else:expected.extend([('Policy',['8',False],'cleared'),('Frame',['7','3',frame],'restricted'),('Policy',['8',True],'invalid'),('Policy',['9',True],'cleared')])
        else:expected.extend([('Frame',['9','1',frame],'invalid'),('Policy',['10',False],'cleared'),('Disable',[],'cleared')])
    if len(calls)!=len(expected):raise ValueError('fixed command coverage')
    for row,(method,args,reply) in zip(calls,expected):
        if row['method']!=method or row['args']!=args or (reply is not None and row['native']['reply']!=reply):raise ValueError('fixed native command/result')
    if [row['frame'] for row in raw['displayed']]!=frames:raise ValueError('displayed full identity/values changed')
    frame_calls=[c for c in calls if c['method']=='Frame' and c['native']['reply']=='accepted'][1:]
    for row,call in zip(raw['displayed'],frame_calls):
        if not call['finished_ns']+200_000_000<=row['capture_start_ns']<=row['capture_end_ns']<=call['finished_ns']+350_000_000:raise ValueError('native display deadline')
    cal=raw['calibration'];cal_call=calls[4]
    if not cal_call['finished_ns']+200_000_000<=cal['started_ns']<=cal['finished_ns']<=cal_call['finished_ns']+350_000_000:raise ValueError('independent public calibration deadline')
    if mode=='owner-loss':
        exit=raw['exit']
        if exit['pid']!=pid or exit['observer']!='pidfd' or not calls[-1]['finished_ns']<=exit['observed_ns']<=calls[-1]['finished_ns']+1_000_000_000:raise ValueError('independent native relay exit')
        origins=[exit['observed_ns']]
        state=raw['closed_state']
        if not state['closed'] or state['permitted'] or state['entries'] or state['labels']:raise ValueError('closed cache state')
    else:origins=[c['finished_ns'] for c in calls if c['method']=='Policy' and c['args'][0] in ('8','9','10') and c['native']['reply']=='cleared']
    if [r['start_ns'] for r in raw['erasure']]!=origins:raise ValueError('erasure not bound to native acknowledgement/exit')
    if result['collectors']!=raw['collectors'] or len(raw['collectors'])!=len(frames):raise ValueError('collector evidence coverage')
    build_record=ROOT/'build-support/evidence/w-25-controller-render-recovery-linux-x64-gcc13.json'
    prior=json.loads(build_record.read_text());artifact=prior['artifacts']['SysPane.CollectorProbe']['sha256']
    if value['collector_build_record_sha256']!=digest(build_record.read_bytes()) or digest((build/'SysPane.CollectorProbe').read_bytes())!=artifact:raise ValueError('tested collector artifact identity')
    for index,(record,frame) in enumerate(zip(raw['collectors'],frames),1):
        name=f'network-collector-{index}.private.json';data=json.loads(private_file(artifacts[name],workspace,name,4*1024**2))
        if record['path']!=str(workspace/name) or record['sha256']!=artifacts[name]['sha256'] or data['artifact_sha256']!=artifact or record['artifact_sha256']!=artifact or data['build_record_sha256']!=digest(build_record.read_bytes()):raise ValueError('collector source/artifact binding')
        process=SimpleNamespace(lines=data['events'])
        rows=verify_documents(process,data['before'],data['after'],data['lower'],data['upper'],'live')
        fields=verify_presentation(process,data['lower'],data['upper'])
        selected=[r for r in data['events'] if r['event']=='presentation'][-1]
        actual={'producer':'producer:network','epoch':selected['epoch'],'entity':selected['entity'],'generation':selected['generation'],'values':[f['value'] for f in selected['fields']]}
        if frame!=actual or record['rows_compared']!=rows or record['fields_compared']!=fields:raise ValueError('native field oracle or relay mutation')
        spawned=[e['pid'] for e in data['events'] if e['event']=='spawned'];stopped=[e['pid'] for e in data['events'] if e['event']=='stopped' and e['os_confirmed'] and e['code']==0]
        if len(spawned)!=1 or spawned!=stopped or data['children']!=[{'pid':spawned[0],'observed_alive':True,'observed_exited':True,'observer':'pidfd'}]:raise ValueError('held native collector exit')
    if len(frames)==2 and frames[0]['epoch']==frames[1]['epoch']:raise ValueError('new grant reused collector lifetime')
    evaluated=judge(raw);wanted='fail' if mode in ('ignore-clear','wrong-value') else 'pass'
    if evaluated!=raw['evaluation'] or evaluated!=result['evaluation'] or value['outcome']!=evaluated['outcome'] or evaluated['outcome']!=wanted:raise ValueError('native cache acceptance differs')
    if (mode=='ignore-clear' and evaluated['values']!='pass') or (mode=='wrong-value' and evaluated['erasure']!='pass'):raise ValueError('negative control did not isolate its defect')
    post=evaluate(raw['post']['trace'])
    if post!=raw['post']['evaluation'] or post['outcome']!='pass' or raw['post']['trace']['end_us']!=2400000:raise ValueError('post-disable marker regression')
    return {'control':mode,'outcome':'pass','candidate':evaluated,'private_evidence_sha256':result['private']['sha256'],
        'collector_runs':len(frames),'operational_fields_compared':evaluated['fields_compared']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-dir',type=Path,required=True)
    parser.add_argument('--reports',nargs=4,type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    records=[json.loads(p.read_text()) for p in args.reports]
    if {r['network_cache_control'] for r in records}!=set(CONTROLS) or any(r['source_inputs']!=records[0]['source_inputs'] for r in records):raise ValueError('four source-identical native modes required')
    build=args.build_dir.resolve(strict=True)
    if args.output.resolve().parent!=build/'native-evidence' or args.output.exists() or any(p.resolve().parent!=build/'native-evidence' or p.stat().st_size>16*1024**2 for p in args.reports):raise ValueError('fresh bounded owned native records required')
    if any(digest((ROOT/p).read_bytes())!=sha for p,sha in records[0]['source_inputs'].items()):raise ValueError('current native source differs')
    results=[validate(r,args.build_dir.resolve(strict=True)) for r in records]
    scripts=['build-support/record_gnome_network_cache.py','build-support/record_gnome_host.py','build-support/record_gnome_composition.py',
        'tests/desktop/gnome_network_cache.py','tests/desktop/test_gnome_network_cache_record.py','tests/protocol/native_collector.py']
    args.output.write_text(json.dumps({'family':'GNOME-NETWORK-CACHE','outcome':'pass','recorded_at':datetime.now(timezone.utc).isoformat(),
        'source_inputs':records[0]['source_inputs'],'reports':[{'path':str(p),'sha256':digest(p.read_bytes())} for p in args.reports],
        'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
        'cases':results,'scope':'Named retained real-network cache and revision/owner clearing; live freshness, installed policy and full product remain open.'},indent=2)+'\n')
    print('Four native cache modes independently verified; private operational records were not copied.')
if __name__=='__main__':main()
