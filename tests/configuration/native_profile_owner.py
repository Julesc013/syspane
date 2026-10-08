"""Independent profile layout, refusal, locking and process-interruption oracle."""
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
import copy, hashlib, json, os, select, signal, stat, subprocess, sys, time, uuid

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/configuration/profile-owner-cases.json'
CASES = json.loads(FIXTURE.read_bytes())
STAGE_FIXTURE = ROOT / 'tests/configuration/profile-owner-stage-cases.json'
STAGE_CASES = json.loads(STAGE_FIXTURE.read_bytes())
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()

def write(path, data):
    path.write_bytes(data)
    path.chmod(0o600)

def line(process):
    assert select.select([process.stdout], [], [], 8)[0], 'profile observation timeout'
    raw = process.stdout.readline()
    assert raw, 'profile EOF'
    return json.loads(raw)

def main():
    exe, config_exe, recovery_exe, evidence = [Path(v).resolve() for v in sys.argv[1:5]]
    assert os.geteuid() != 0 and evidence.is_relative_to(exe.parent)
    folder = evidence / ('profile-owner-' + uuid.uuid4().hex[:12])
    folder.mkdir(parents=True, mode=0o700)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    report = dict(family='PROFILE-OWNER', outcome='fail', uid=os.geteuid(), filesystem='ext4', kernel=list(os.uname()),
                  started_at=datetime.now(timezone.utc).isoformat(), executable_sha256=sha(exe.read_bytes()),
                  artifacts={p.name: sha(p.read_bytes()) for p in (exe, config_exe, recovery_exe)},
                  oracle_sha256=sha(Path(__file__).read_bytes()), fixture_sha256=sha(FIXTURE.read_bytes()),
                  stage_fixture_sha256=sha(STAGE_FIXTURE.read_bytes()), cases=[])
    def passed(name, **fields):
        report['cases'].append(dict(case=name, outcome='pass', **fields))
        write(folder / 'result.json', encoded(report))
    def request(v):
        p = folder / ('request-' + uuid.uuid4().hex[:10] + '.json')
        write(p, encoded(v))
        return p
    def args(v, op='open', phase='-', fault='-'):
        return [str(exe), str(request(v)), op, phase, fault]
    def call(v, op='open', phase='-', fault='-', good=True, env=None):
        q = subprocess.run(args(v, op, phase, fault), capture_output=True, timeout=8, env=env)
        reply = json.loads(q.stdout)
        assert (q.returncode == 0) == good, (v, op, q.returncode, reply, q.stderr)
        return reply
    def selection(name):
        return dict(profile=CASES['profile'], portable_root=str(folder / name))
    def expected(v):
        key = sha(v['profile'].encode())
        mode = 'portable' if 'portable_root' in v else 'xdg'
        bases = dict(zip(CASES['roles'], (v.get('config_home'), v.get('data_home'), v.get('state_home'))))
        suffixes = dict(zip(CASES['roles'], ('.config', '.local/share', '.local/state')))
        result = dict(profile=v['profile'], mode=mode)
        for role, child in CASES['roles'].items():
            base = v['portable_root'] if mode == 'portable' else bases[role] if bases[role] and bases[role].startswith('/') else v['home'].rstrip('/') + '/' + suffixes[role]
            result[role] = base.rstrip('/') + '/syspane/' + role + '/' + key
            result[child] = result[role] + '/' + child
        return result
    def marker(v, role):
        return encoded(dict(format=CASES['format'], schema_version=CASES['schema_version'], profile=v['profile'], kind=role, mode='portable' if 'portable_root' in v else 'xdg'))
    def inspect(v, roles=None, empty=True):
        paths = expected(v)
        for role, child in CASES['roles'].items():
            root = Path(paths[role])
            if roles is not None and role not in roles:
                assert not root.exists(), (role, root)
                continue
            assert {p.name for p in root.iterdir()} == set(CASES['entries'] + [child])
            for p in (root, root / child):
                s = p.lstat()
                assert stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode) == 0o700 and s.st_uid == os.geteuid()
            for name, content in (('.owner.json', marker(v, role)), ('.lease', b'')):
                p = root / name
                s = p.lstat()
                assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode) == 0o600 and s.st_nlink == 1 and s.st_uid == os.geteuid()
                assert p.read_bytes() == content
            if empty:
                assert not list((root / child).iterdir())
        return paths
    @contextmanager
    def held(v, phase='-', fault='-', op='session'):
        q = subprocess.Popen(args(v, op, phase, fault), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        try:
            yield q, line(q)
        finally:
            if q.poll() is None:
                q.kill()
                q.wait(timeout=3)
            write(folder / ('stderr-' + str(q.pid)), q.stderr.read())
            q.stdin.close(); q.stdout.close(); q.stderr.close()
    def send(q, op):
        q.stdin.write(encoded(dict(op=op)) + b'\n'); q.stdin.flush()
        return line(q)
    try:
        assert sha(CASES['profile'].encode()) == CASES['key']
        v = dict(profile=CASES['profile'], home='/home/tester')
        assert call(v, 'plan') == expected(v)
        for role, base in CASES['default_bases'].items():
            assert expected(v)[role] == base + '/syspane/' + role + '/' + CASES['key']
        passed('xdg-defaults')
        for overrides in ({'config_home':'', 'data_home':'relative', 'state_home':'relative'},
                          {'config_home':'/config/', 'data_home':'/content', 'state_home':'/state///'},
                          {'config_home':'/same', 'data_home':'/same', 'state_home':'/same'}):
            q = dict(v, **overrides)
            assert call(q, 'plan') == expected(q)
        q = dict(profile=CASES['profile'], config_home='/c', data_home='/d', state_home='/s')
        assert call(q, 'plan') == expected(q)
        env = dict(os.environ, HOME='/home/tester', XDG_CONFIG_HOME='/chosen', XDG_DATA_HOME='relative', XDG_STATE_HOME='')
        assert call(v, 'environment', env=env) == expected(dict(v, config_home='/chosen'))
        passed('xdg-overrides-and-environment')
        assert call(dict(v, portable_root='/chosen/'), 'plan') == expected(dict(v, portable_root='/chosen'))
        for value in CASES['invalid_bases'] + ['/a/'+'x'*256, '/'+'/'.join(['a']*64), '/'+'x'*4096]:
            assert call(dict(v, portable_root=value), 'plan', good=False)['error'] == 'profile.path'
        for bad in ('', 'bad id', '../bad', 'x'*257):
            assert call(dict(v, profile=bad), 'plan', good=False)['error'] == 'profile.identifier'
        for good_id in ('p/one', 'x'*256):
            assert call(dict(v, profile=good_id), 'plan') == expected(dict(v, profile=good_id))
        assert call(dict(profile=CASES['profile']), 'plan', good=False)['error'] == 'profile.path'
        overlap = dict(v, config_home='/c', data_home='/c/syspane/configuration/'+CASES['key'])
        assert call(overlap, 'plan', good=False)['error'] == 'profile.overlap'
        passed('planner-refusals-and-boundaries')
        v = selection('roundtrip')
        assert call(v) == expected(v)
        inspect(v)
        before = {p: p.stat().st_ino for p in Path(v['portable_root']).rglob('*')}
        assert call(dict(v, create=False)) == expected(v)
        assert before == {p:p.stat().st_ino for p in before}
        inspect(v); passed('exact-create-reopen')
        for name, fields in [('no-create', {'create':False}), ('denied', {})]:
            q = selection(name)
            assert call(dict(q, **fields), good=False, fault='deny' if name=='denied' else '-')['error'].startswith('profile.')
            assert not Path(q['portable_root']).exists()
        passed('no-authority-no-mutation')
        with held(v) as (q, reply):
            assert reply == expected(v)
            assert call(v, good=False)['error'] == 'profile.busy'
            assert send(q, 'thread')['error'] == 'profile.thread'
            assert send(q, 'reenter')['reentrant_rejected']
            assert send(q, 'verify')['profile'] == CASES['profile']
        assert call(v) == expected(v)
        passed('exclusive-owner-death-thread-reentry')
        # Only one role root shared; all three locks must independently exclude peers.
        for role, variable in zip(CASES['roles'], ('config_home','data_home','state_home')):
            first = dict(profile=CASES['profile'], config_home=str(folder/('lock-'+role)/'c'), data_home=str(folder/('lock-'+role)/'d'), state_home=str(folder/('lock-'+role)/'s'))
            second = dict(first, config_home=str(folder/('peer-'+role)/'c'), data_home=str(folder/('peer-'+role)/'d'), state_home=str(folder/('peer-'+role)/'s'))
            second[variable] = first[variable]
            with held(first):
                assert call(second, good=False)['error'] == 'profile.busy'
            assert call(second) == expected(second)
            passed('role-lock-'+role)
        for role in CASES['roles']:
            for phase, published in CASES['phases'].items():
                v = selection('cut-'+role+'-'+phase)
                with held(v, role+'.'+phase, 'stop', 'open') as (q, event):
                    assert event == dict(event='phase', phase=role+'.'+phase, pid=q.pid)
                    deadline = time.monotonic()+3
                    stopped = None
                    while time.monotonic()<deadline:
                        stopped = os.waitid(os.P_PID,q.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                        if stopped: break
                        time.sleep(.01)
                    assert stopped and stopped.si_code==os.CLD_STOPPED and stopped.si_status==signal.SIGSTOP
                    q.kill(); assert q.wait(timeout=3) == -signal.SIGKILL
                roles = list(CASES['roles']); visible = roles[:roles.index(role)+(1 if published else 0)]
                inspect(v, visible)
                assert call(v) == expected(v)
                inspect(v)
                passed('cut-'+role+'-'+phase, cut=event, exit=q.returncode)
        for phase, published in CASES['phases'].items():
            v=selection('deny-'+phase)
            assert call(v, phase='configuration.'+phase, fault='deny', good=False)['error']=='profile.denied'
            inspect(v, ['configuration'] if published else [])
            assert call(v)==expected(v)
            inspect(v); passed('denied-'+phase)
        v=selection('short-write')
        assert call(v, fault='file-size', good=False)['error']=='profile.write'
        inspect(v, []); assert call(v)==expected(v); inspect(v); passed('short-write')
        for fault in ('deny','throw'):
            v=selection('guard-'+fault)
            with held(v) as (q, _):
                assert send(q, fault)['error']=='profile.denied'
                assert send(q, 'verify')['error']=='profile.invalidated'
            assert call(v)==expected(v); passed('guard-'+fault)
        for role, child in CASES['roles'].items():
            for node in ('.owner.json','.lease'):
                for kind in CASES['unsafe_file_kinds']:
                    v=selection('unsafe-'+role+node+'-'+kind);call(v)
                    root=Path(expected(v)[role]); target=folder/('foreign-'+uuid.uuid4().hex[:8]);write(target,b'foreign preserved')
                    x=root/node; x.unlink()
                    if kind=='symlink': x.symlink_to(target)
                    elif kind=='hardlink': os.link(target,x)
                    elif kind=='directory': x.mkdir(mode=0o700)
                    elif kind=='fifo': os.mkfifo(x,0o600)
                    elif kind=='permissions': write(x,marker(v,role) if node=='.owner.json' else b''); x.chmod(0o644)
                    else: write(x,b'x'*(1025 if node=='.owner.json' else 1))
                    assert call(v,good=False)['error'].startswith('profile.')
                    assert target.read_bytes()==b'foreign preserved'
                    passed('unsafe-'+role+node+'-'+kind)
        for variant in ('profile','kind','mode','schema_version','extra','missing','unmarked','root-mode','child-mode','child-symlink','root-symlink','ancestor-symlink','foreign-entry'):
            v=selection('bad-'+variant);call(v); paths=expected(v);root=Path(paths['configuration']); child=root/'generations'
            if variant in ('profile','kind','mode','schema_version','extra'):
                m=json.loads(marker(v,'configuration'));m[variant]='wrong';write(root/'.owner.json',encoded(m))
            elif variant=='missing': (root/'.lease').unlink()
            elif variant=='unmarked': (root/'.owner.json').unlink()
            elif variant=='root-mode': root.chmod(0o755)
            elif variant=='child-mode': child.chmod(0o755)
            elif variant=='child-symlink': child.rmdir();child.symlink_to(Path(paths['packages']),target_is_directory=True)
            elif variant in ('root-symlink','ancestor-symlink'):
                original=root if variant=='root-symlink' else Path(v['portable_root'])/'syspane'
                moved=original.with_name(original.name+'-saved');original.rename(moved);original.symlink_to(moved,target_is_directory=True)
            else: write(root/'foreign',b'preserve')
            assert call(v,good=False)['error'].startswith('profile.')
            if variant=='foreign-entry': assert (root/'foreign').read_bytes()==b'preserve'
            passed('bad-'+variant)
        for kind in CASES['substitutions']:
            v=selection('substitute-'+kind);paths=expected(v);root=Path(paths['configuration'])
            with held(v) as (q, _):
                if kind=='root': root.rename(root.with_name(root.name+'-saved'));root.mkdir(mode=0o700)
                elif kind=='root_permissions': root.chmod(0o755)
                elif kind=='ancestor_permissions': Path(v['portable_root']).chmod(0o777)
                elif kind=='marker_bytes': write(root/'.owner.json',marker(v,'configuration').replace(b'portable',b'changed!'))
                else:
                    name={'marker':'.owner.json','lease':'.lease','child':'generations'}[kind];x=root/name;x.rename(root.parent/(kind+'-saved'))
                    if kind=='child': x.mkdir(mode=0o700)
                    else: write(x,marker(v,'configuration') if kind=='marker' else b'')
                assert send(q,'verify')['error'].startswith('profile.')
                assert send(q,'verify')['error']=='profile.invalidated'
            passed('substitute-'+kind)
        v=selection('collision')
        with held(v,'configuration.publish_ready','block','open') as (q, _):
            root=Path(expected(v)['configuration']);root.mkdir(mode=0o700);write(root/'foreign',b'untouched')
            q.stdin.write(b'resume\n');q.stdin.flush()
            assert line(q)['error']=='profile.publish' and q.wait(timeout=3)==1
            assert (root/'foreign').read_bytes()==b'untouched'
        passed('no-replace-publication-collision')
        for mutation in STAGE_CASES['mutations']:
            v=selection('stage-'+mutation);root=Path(expected(v)['configuration'])
            with held(v,STAGE_CASES['phase'],'block','open') as (q, _):
                stage=next(root.parent.glob('.'+CASES['key']+'.pending-*'))
                if mutation=='stage': stage.rename(stage.with_name(stage.name+'-saved'));stage.mkdir(mode=0o700)
                elif mutation=='parent': root.parent.rename(root.parent.with_name('saved-parent'));root.parent.mkdir(mode=0o700)
                elif mutation in ('marker','lease','child'):
                    name={'marker':'.owner.json','lease':'.lease','child':'generations'}[mutation]
                    x=stage/name;x.rename(stage.parent/(mutation+'-saved'))
                    if mutation=='child': x.mkdir(mode=0o700)
                    else: write(x,marker(v,'configuration') if mutation=='marker' else b'')
                elif mutation=='extra': write(stage/'foreign',b'preserve')
                elif mutation=='child_content': write(stage/'generations'/'foreign',b'preserve')
                else: (stage/'generations').chmod(0o755)
                q.stdin.write(b'resume\n');q.stdin.flush()
                assert line(q)['error'].startswith('profile.') and q.wait(timeout=3)==1
                assert root.exists()==STAGE_CASES['published_root_exists'],mutation
            passed('stage-'+mutation)
        v=selection('capacity')
        for i in range(CASES['maximum_pending']):
            assert call(v,phase='configuration.stage_created',fault='deny',good=False)['error']=='profile.denied'
        parent=Path(expected(v)['configuration']).parent
        names={p.name for p in parent.iterdir()}
        assert len(names)==CASES['maximum_pending']
        assert call(v,good=False)['error']=='profile.capacity' and names=={p.name for p in parent.iterdir()}
        passed('orphan-capacity-preserved')
        v=selection('scan-capacity');parent=Path(expected(v)['configuration']).parent;parent.mkdir(parents=True,mode=0o700)
        for i in range(CASES['maximum_parent_entries']+1): (parent/str(i)).mkdir(mode=0o700)
        assert call(v,good=False)['error']=='profile.capacity';passed('parent-scan-bound')
        v=selection('existing-orphans');call(v);parent=Path(expected(v)['configuration']).parent
        for i in range(8): (parent/('.'+CASES['key']+'.pending-'+str(i))).mkdir(mode=0o700)
        assert call(v)==expected(v);passed('valid-current-with-orphans')
        # Existing storage owners operate on the exact new children while profile locks remain held.
        v=selection('composed')
        settings=json.loads((ROOT/CASES['configuration_fixture']).read_bytes());scene=json.loads((ROOT/CASES['scene_fixture']).read_bytes())
        settings['revision']=scene['revision']='40'
        settings_file=folder/'settings.json';scene_file=folder/'scene.json';record=folder/'recovery.json'
        write(settings_file,encoded(settings));write(scene_file,encoded(scene));write(record,CASES['recovery_bytes'].encode())
        with held(v) as (q, paths):
            run=subprocess.run([str(config_exe),paths['generations'],'init',str(settings_file),str(scene_file)],capture_output=True,timeout=8)
            assert run.returncode==0,(run.stdout,run.stderr)
            actual=json.loads(run.stdout);assert actual['settings']==settings and actual['scene']==scene
            run=subprocess.run([str(recovery_exe),paths['recovery'],'replace',str(record),'-','-'],capture_output=True,timeout=8)
            assert run.returncode==0 and json.loads(run.stdout)['outcome']=='durable'
            assert send(q,'verify')['profile']==CASES['profile']
        assert call(dict(v,create=False))==expected(v);inspect(v,empty=False)
        run=subprocess.run([str(config_exe),paths['generations'],'read'],capture_output=True,timeout=8)
        actual=json.loads(run.stdout);assert run.returncode==0 and actual['settings']==settings and actual['scene']==scene
        assert (Path(paths['recovery'])/'draft.json').read_bytes()==CASES['recovery_bytes'].encode()
        passed('generation-recovery-composition-reopen')
        v=selection('oracle-control');call(v);root=Path(expected(v)['configuration']);write(root/'.owner.json',marker(v,'state'))
        detected=False
        try: inspect(v)
        except AssertionError: detected=True
        assert detected;passed('wrong-marker-oracle-control',fault_detected=True)
        report['outcome']='pass'
    except Exception as exc:
        report['error']=repr(exc)
        raise
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        report['files']={p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if stat.S_ISREG(p.lstat().st_mode) and p.name!='result.json'}
        report['nodes']={p.relative_to(folder).as_posix():dict(mode=p.lstat().st_mode,symlink=os.readlink(p) if p.is_symlink() else None) for p in folder.rglob('*')}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'],len(report['cases']))

if __name__=='__main__':main()
