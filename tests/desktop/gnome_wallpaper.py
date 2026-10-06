"""Independent file, settings and native-pixel evidence for owned GNOME wallpaper."""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import select
import stat
import struct
import subprocess
import time
import zlib

from native_oracle import ROOT
from native_x11_host import rgb_record
from gnome_composition import FIXTURE as SCENE, masks, judge_samples, bind_icon_window
from gnome_reveal import issue
from oracle import evaluate

FIXTURE_PATH=ROOT/'tests/desktop/fixtures/gnome-wallpaper.json'
FIXTURE=json.loads(FIXTURE_PATH.read_text())
CONTROLS=['live','replace-file','redirect-setting','cover-wallpaper']
SETTINGS_COMMAND=['/usr/bin/gsettings','list-recursively','org.gnome.desktop.background']


@lru_cache(maxsize=1)
def raster():
    width,height=FIXTURE['size'];tw,th=FIXTURE['tile'];colors=FIXTURE['palette']
    return b''.join(bytes(colors[(x//tw+FIXTURE['row_multiplier']*(y//th))%len(colors)])
                    for y in range(height) for x in range(width))


def crop(region):
    x,y,width,height=region;row_bytes=FIXTURE['size'][0]*3;pixels=raster()
    return b''.join(pixels[(y+n)*row_bytes+x*3:(y+n)*row_bytes+(x+width)*3] for n in range(height))


@lru_cache(maxsize=2)
def png(annotated=False):
    width,height=FIXTURE['size'];pixels=raster()
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data))
    raw=b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(raw))+(chunk(b'tEXt',b'SysPane\0owned replacement control') if annotated else b'')+chunk(b'IEND',b''))


def parse_settings(raw):
    if not raw or len(raw.encode())>8192:raise ValueError('native settings response capacity')
    values={}
    for line in raw.splitlines():
        schema,key,value=line.split(' ',2)
        if schema!='org.gnome.desktop.background' or key in values or not value:raise ValueError('native settings response shape')
        values[key]=value
    if not {'picture-uri','picture-uri-dark','picture-options','primary-color','color-shading-type'}<=set(values):
        raise ValueError('native background settings incomplete')
    return values


def settings(environment):
    response=subprocess.run(SETTINGS_COMMAND,env=environment,capture_output=True,text=True,timeout=1,check=True)
    if response.stderr:raise ValueError('native background settings warning')
    return {'stdout':response.stdout,'values':parse_settings(response.stdout)}


def metadata(value):
    if not stat.S_ISREG(value.st_mode) or value.st_size>FIXTURE['maximum_file_bytes']:
        raise ValueError('bounded regular wallpaper file required')
    return {'device':value.st_dev,'inode':value.st_ino,'mode':stat.S_IMODE(value.st_mode),'uid':value.st_uid,
            'links':value.st_nlink,'bytes':value.st_size,'mtime_ns':value.st_mtime_ns,'ctime_ns':value.st_ctime_ns}


def descriptor_snapshot(descriptor):
    before=metadata(os.fstat(descriptor))
    raw=os.pread(descriptor,FIXTURE['maximum_file_bytes']+1,0)
    after=metadata(os.fstat(descriptor))
    if before!=after or len(raw)!=before['bytes']:raise ValueError('wallpaper changed during snapshot')
    return {**before,'sha256':hashlib.sha256(raw).hexdigest()}


def file_pair(path,held):
    descriptor=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:return {'path':descriptor_snapshot(descriptor),'held':descriptor_snapshot(held)}
    finally:os.close(descriptor)


def write_image(path,annotated=False):
    with path.open('xb') as stream:
        stream.write(png(annotated));stream.flush();os.fsync(stream.fileno())
    path.chmod(0o444)


def expected_settings(original):
    return {'picture-uri':repr(original.as_uri()),'picture-uri-dark':repr(original.as_uri()),
            'picture-options':"'centered'",'primary-color':"'#304860'",'color-shading-type':"'solid'"}


def judge(result,composition):
    from record_gnome_host import rgb
    if result['control'] not in CONTROLS:raise ValueError('wallpaper control')
    original=Path(result['original_path']);expected=expected_settings(original)
    baseline_settings=parse_settings(result['settings_before']['stdout'])
    if result['settings_before']['values']!=baseline_settings or any(baseline_settings[k]!=v for k,v in expected.items()):
        raise ValueError('original native image configuration differs')
    before=result['file_before']
    if before['path']!=before['held'] or before['path']['mode']!=0o444 or before['path']['links']!=1 or before['path']['sha256']!=hashlib.sha256(png()).hexdigest() or before['path']['bytes']!=len(png()):
        raise ValueError('original immutable image identity differs')
    calibration=[rgb(s['frames'][0]['pixels'],180*220*3) for s in composition['calibrations']]
    anchors,clean=masks(calibration[2],calibration[:2]);image_overlap=crop(SCENE['overlap'])
    baseline=result['baseline'];previous=0
    if len(baseline)!=3:raise ValueError('image baseline completeness')
    for frame in baseline:
        if not previous<=frame['started_ns']<=frame['finished_ns']<result['scene_enabled_ns']:raise ValueError('image baseline timing')
        previous=frame['finished_ns']
        overlap=rgb(frame['overlap'],180*220*3)
        if any(overlap[n*3:n*3+3]!=calibration[2][n*3:n*3+3] for group in anchors for n in group) or any(overlap[n*3:n*3+3]!=image_overlap[n*3:n*3+3] for n in clean):
            raise ValueError('image baseline icon/transparent witnesses differ')
        for data,region in zip(frame['witnesses'],FIXTURE['witnesses']):
            if rgb(data,region[2]*region[3]*3)!=crop(region):raise ValueError('image baseline pixels differ')
        if len(frame['witnesses'])!=2 or frame['files']!=before or parse_settings(frame['settings']['stdout'])!=baseline_settings or frame['settings']['values']!=baseline_settings:
            raise ValueError('image baseline file/settings differ')
    marker=result['marker'];trace=marker['trace'];mark=evaluate(trace)
    if marker['evaluation']!=mark or marker['started_monotonic_ns']<=result['scene_enabled_ns'] or trace['end_us']!=2400000 or [s['generation'] for s in trace['stimuli']]!=[1,2,3]:
        raise ValueError('fixed wallpaper marker interval differs')
    if any(x.startswith('capture.') for x in mark['uncertainty']):raise ValueError('marker coverage incomplete')
    samples=result['samples'];faults=result['faults'];control=result['control']
    if len(faults)!=(0 if control=='live' else 1) or len(samples)!=len(trace['frames']):raise ValueError('wallpaper observation/fault completeness')
    if faults:
        fault=faults[0]
        if fault['kind']!=control or not 1000000<=fault['start_us']<=1050000 or not fault['start_us']<=fault['end_us']<=fault['start_us']+50000:
            raise ValueError('wallpaper fault scheduling/duration')
    overlaps=[];checks=[]
    for frame,row in zip(trace['frames'],samples):
        if not frame['start_us']<=frame['end_us']<=row['start_us']<=row['files_started_us']<=row['settings_started_us']<=row['end_us']:
            raise ValueError('paired wallpaper observation order')
        overlaps.append({'marker_start_us':frame['start_us'],'start_us':row['start_us'],'end_us':row['end_us'],'pixels':row['overlap']})
        native_settings=parse_settings(row['settings']['stdout'])
        if row['settings']['values']!=native_settings or len(row['witnesses'])!=2:raise ValueError('native wallpaper observation shape')
        pixels=[rgb(data,region[2]*region[3]*3) for data,region in zip(row['witnesses'],FIXTURE['witnesses'])]
        checks.append({'at_us':frame['start_us'],'end_us':row['end_us'],'files':row['files']==before,
                       'settings':native_settings==baseline_settings,'pixels':all(data==crop(region) for data,region in zip(pixels,FIXTURE['witnesses']))})
    comp=judge_samples(calibration[2],overlaps,calibration[:2])
    guards={key:'pass' if all(row[key] for row in checks) else 'fail' for key in ['files','settings','pixels']}
    return {'marker':mark,'composition':comp,**guards,'checks':checks,
            'outcome':'pass' if mark['outcome']=='pass' and comp['icons']==comp['rectangle']=='pass' and all(v=='pass' for v in guards.values()) else 'fail'}


def observe(display,environment,shell_pid,workspace,composition,trace_function):
    journal=(workspace/'wallpaper.jsonl').open('x',encoding='utf-8',newline='\n')
    count=0;held=icon_descriptor=None
    def preserve(kind,value):
        nonlocal count
        count+=1
        if count>180:raise ValueError('wallpaper journal record capacity')
        journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        if journal.tell()>8*1024**2:raise ValueError('wallpaper journal byte capacity')
    def set_key(key,value):
        response=subprocess.run(['/usr/bin/gsettings','set','org.gnome.desktop.background',key,value],
            env=environment,capture_output=True,text=True,timeout=1,check=True)
        if response.stdout or response.stderr:raise ValueError('native background setter output')
    try:
        if composition['outcome']!='pass':raise ValueError('live composition prerequisite')
        control=environment['SYSPANE_GNOME_WALLPAPER_CONTROL'];original=workspace/'wallpaper.png';alternate=workspace/'wallpaper-alternate.png'
        write_image(original);write_image(alternate)
        (workspace/'wallpaper-original.png').write_bytes(png())
        held=os.open(original,os.O_RDONLY|os.O_NOFOLLOW)
        owner=composition['icon_manager'];icon_descriptor=os.pidfd_open(owner['pid'])
        poller=select.poll();poller.register(icon_descriptor,select.POLLIN)
        issue(environment,'SetSceneEnabled','false')
        for key,value in expected_settings(original).items():set_key(key,value)
        result={'version':'0.1.0','fixture_sha256':hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
                'control':control,'icon_manager':owner,'original_path':str(original),'alternate_path':str(alternate),
                'file_before':file_pair(original,held),'settings_before':settings(environment),'baseline':[],'faults':[],'samples':[]}
        preserve('identity',{k:v for k,v in result.items() if k not in ['baseline','faults','samples']})
        from record_gnome_host import rgb
        calibration=[rgb(s['frames'][0]['pixels'],180*220*3) for s in composition['calibrations']]
        anchors,clean=masks(calibration[2],calibration[:2]);image_overlap=crop(SCENE['overlap'])
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            witnesses=[display.capture(*region) for region in FIXTURE['witnesses']];overlap=display.capture(*SCENE['overlap'])
            if all(data==crop(region) for data,region in zip(witnesses,FIXTURE['witnesses'])) and all(overlap[n*3:n*3+3]==image_overlap[n*3:n*3+3] for n in clean) and all(overlap[n*3:n*3+3]==calibration[2][n*3:n*3+3] for group in anchors for n in group):break
            time.sleep(.05)
        else:
            preserve('baseline-failed',{'witnesses':[rgb_record(data) for data in witnesses],'overlap':rgb_record(overlap)})
            raise TimeoutError('native image wallpaper baseline did not match fixture')
        for index in range(3):
            if index:time.sleep(.1)
            started=time.monotonic_ns()
            frame={'started_ns':started,'overlap':rgb_record(display.capture(*SCENE['overlap'])),
                   'witnesses':[rgb_record(display.capture(*region)) for region in FIXTURE['witnesses']],
                   'files':file_pair(original,held),'settings':settings(environment),'finished_ns':time.monotonic_ns()}
            result['baseline'].append(frame);preserve('baseline',frame)
        issue(environment,'SetSceneEnabled','true');result['scene_enabled_ns']=time.monotonic_ns()
        preserve('scene-enabled',{'at_ns':result['scene_enabled_ns']})
        def sample(frame,now):
            if control!='live' and not result['faults'] and now()>=FIXTURE['fault_at_us']:
                fault={'kind':control,'start_us':now()}
                if control=='replace-file':
                    replacement=workspace/'wallpaper-replacement.png';write_image(replacement,True);os.replace(replacement,original)
                elif control=='redirect-setting':set_key('picture-uri',repr(alternate.as_uri()))
                elif control=='cover-wallpaper':issue(environment,'SetWallpaperOccluded','true')
                else:raise ValueError('unknown wallpaper control')
                fault['end_us']=now();result['faults'].append(fault);preserve('fault',fault)
            row={'start_us':now(),'overlap':rgb_record(display.capture(*SCENE['overlap'])),
                 'witnesses':[rgb_record(display.capture(*region)) for region in FIXTURE['witnesses']]}
            row['files_started_us']=now();row['files']=file_pair(original,held)
            row['settings_started_us']=now();row['settings']=settings(environment);row['end_us']=now()
            result['samples'].append(row);preserve('sample',{'marker':frame,'observation':row})
            if poller.poll(0):raise ValueError('icon manager exited during wallpaper observation')
        result['marker']=trace_function(display,environment,sample=sample,dismiss=False)
        result['file_after']=file_pair(original,held);result['settings_after']=settings(environment)
        if poller.poll(0) or bind_icon_window(display,shell_pid,workspace)!=owner:raise ValueError('native icon-manager lifetime changed')
        result['evaluation']=judge(result,composition)
        preserve('completed',{k:v for k,v in result.items() if k not in ['samples','baseline']})
        return result
    except Exception as error:
        preserve('error',{'message':type(error).__name__+': '+str(error)})
        raise
    finally:
        for descriptor in [held,icon_descriptor]:
            if descriptor is not None:os.close(descriptor)
        journal.close()
