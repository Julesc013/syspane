"""Recompute persistent-controller recovery from original native/private evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/desktop'))
from gnome_controller_recovery import judge, MODES, RENDER_MODES, REVOKED, NO_REPLACEMENT

BUILD_RECORD='build-support/evidence/w-25-controller-render-recovery-linux-x64-gcc13.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def controller_lifetimes(value, build):
    workspace=Path(value['workspace']);mode=value['controller_recovery_control']
    if value['family']!='GNOME-CONTROLLER-RECOVERY-01' or mode not in MODES:
        raise ValueError('explicit persistent-controller family required')
    environment=value['environment']['explicit'];artifacts=value['network_private_artifacts'];contents={}
    names={'network-controller-recovery.private.json':16*1024**2,
           'network-controller-source.private.jsonl':4*1024**2,
           'network-controller-delivery.private.jsonl':4*1024**2,
           'network-controller-bracket.private.json':1024**2}
    if set(artifacts)!=set(names):raise ValueError('private controller evidence coverage')
    for name,maximum in names.items():
        entry=artifacts[name];path=Path(entry['path'])
        if path!=workspace/name or path.resolve(strict=True)!=path or path.is_symlink() or path.stat().st_mode&0o777!=0o600:
            raise ValueError('private evidence ownership/path')
        data=path.read_bytes()
        if len(data)>maximum or len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('private original identity differs')
        contents[name]=data
    raw=json.loads(contents['network-controller-recovery.private.json'])
    if raw.get('error') or raw['mode']!=mode or environment['SYSPANE_GNOME_CONTROLLER_CONTROL']!=mode:
        raise ValueError('native observation incomplete')
    for key in ('source','delivery'):
        original=[json.loads(r) for r in contents['network-controller-'+key+'.private.jsonl'].splitlines()]
        if raw[key]!=original[:len(raw[key])]:raise ValueError('original operational journal prefix differs')
    if raw['bracket']!=json.loads(contents['network-controller-bracket.private.json']):
        raise ValueError('independent native counter bracket differs')
    log=workspace/'controller.log';data=log.read_bytes()
    if len(data)>1024**2 or value['logs']['controller.log']!=data.decode():raise ValueError('native controller log differs')
    events=[json.loads(r) for r in data.splitlines()]
    if events[:len(raw['controller'])]!=raw['controller'] or any(r['event']=='error' for r in events):
        raise ValueError('original controller lifecycle differs')
    complete=[r for r in events if r['event']=='complete']
    if len(complete)!=1 or complete[0]['requested'] is not True:raise ValueError('controller shutdown was not acknowledged')
    controller=raw['identities']['controller']['pid']
    command=[r for r in value['commands'] if r.get('pid')==controller]
    expected=[str(build/'SysPane.CollectorProbe'),'desktop-watch' if mode in RENDER_MODES else 'desktop',environment['SYSPANE_GNOME_NETWORK_ROOT'],
              'revoke-on-exit' if mode in REVOKED else 'no-reattach' if mode=='no-reattach' else 'allow',str(build/'gnome-lab/sysroot/usr/bin/gnome-shell')]
    if len(command)!=1 or command[0]['command']!=expected or controller!=value['controller_pid'] or str(controller)!=environment['SYSPANE_GNOME_CONTROLLER_PID']:
        raise ValueError('admitted controller launch differs')
    if (environment.get('SYSPANE_GNOME_CONTROLLER_RENDER')=='1')!=(mode in RENDER_MODES):raise ValueError('native rendering mode differs')
    shells=[raw['identities']['old_shell']]+([raw['identities']['new_shell']] if mode not in NO_REPLACEMENT else [])
    for shell in shells:
        if shell['arguments']!=[expected[-1],'--x11','--mode=user'] or shell['executable']!=expected[-1]:
            raise ValueError('native ELF replacement differs')
    stopped=[r for r in events if r['event']=='stopped']
    expected_pids={raw['identities']['source']['pid'],*[r['pid'] for r in shells]}
    if {r['pid'] for r in stopped}!=expected_pids or len(stopped)!=len(expected_pids) or not all(r['os_confirmed'] for r in stopped):
        raise ValueError('held native exit coverage differs')
    for row in stopped:
        old=row['pid']==shells[0]['pid'] and mode!='false-progress'
        if row['code']!=(9 if old else 0) or row['signaled']!=old or (not old and row['forced']):
            raise ValueError('unexpected native exit or forced graceful cleanup')
    record=ROOT/BUILD_RECORD;compiled=json.loads(record.read_text())
    if sha(record)!=value['network_build_record_sha256']:raise ValueError('native build record differs')
    for name in ('SysPane.CollectorProbe','libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if sha(build/name)!=compiled['artifacts'][name]['sha256']:raise ValueError('native tested artifact differs')
    for name in ('libsyspane_gjs_clock.so','SysPaneClock-0.1.typelib'):
        if value['mapped_files'].get(str(build/name))!=compiled['artifacts'][name]['sha256']:raise ValueError('original shell native mapping differs')
        if mode not in NO_REPLACEMENT+('no-reattach',) and raw['new_shell_mapped_files'].get(str(build/name))!=compiled['artifacts'][name]['sha256']:
            raise ValueError('replacement shell native mapping differs')
    result=judge(raw,value['observation']['composition'])
    if result!=raw['evaluation'] or result!=value['observation']['controller_recovery']['evaluation'] or result['outcome']!=value['outcome']:
        raise ValueError('recomputed native/pixel outcome differs')
    expected_outcome='fail' if mode in ('no-reattach','false-progress') else 'pass'
    if result['outcome']!=expected_outcome:raise ValueError('control missed its fixed expected outcome')
    return raw, result


def validate(value,build):
    from record_gnome_composition import validate as composition
    raw,result=controller_lifetimes(value,build)
    icon_exit={'event':'exit-observed','pid':raw['identities']['old_icon']['pid'],'observer':'pidfd','readable':raw['old_icon_exited']}
    composition(value,build,family='GNOME-CONTROLLER-RECOVERY-01',outer_outcome=False,
                icon_exit=icon_exit if raw['mode'] not in NO_REPLACEMENT else None)
    return {'mode':raw['mode'],**result,'scope':'Automatic same-session native reattachment and operational pixels after native overview dismissal; no complete edition qualification.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('reports',type=Path,nargs='+');args=parser.parse_args()
    values=[json.loads(p.read_text()) for p in args.reports]
    if len(values)!=len(MODES) or {v['controller_recovery_control'] for v in values}!=set(MODES):
        raise ValueError('eight explicit controls required')
    if any(v['source_inputs']!=values[0]['source_inputs'] for v in values):raise ValueError('control source identities differ')
    for name,h in values[0]['source_inputs'].items():
        if sha(ROOT/name)!=h:raise ValueError('current source identity differs: '+name)
    result={'outcome':'pass','source_inputs':values[0]['source_inputs'],
            'results':[validate(v,args.build_dir.resolve(strict=True)) for v in values],
            'reports':[{'path':str(p),'sha256':sha(p)} for p in args.reports]}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Eight persistent-controller controls recomputed from original evidence.')


if __name__=='__main__':main()
