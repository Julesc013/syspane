"""Download pinned Ubuntu lab packages and extract them inside an owned build.

No apt installation, maintainer script, service, system configuration or privilege
change is performed. Configure/build/test remain offline and never call this tool.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / 'source/build/x11-lab-packages.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_dir', type=Path)
    parser.add_argument('--refresh-metadata', action='store_true', help='Refresh Ubuntu metadata only in this owned lab cache')
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    if os.name != 'posix' or os.geteuid() == 0:
        raise ValueError('unprivileged Linux account required')
    if json.loads((build / '.syspane-owner.json').read_text())['profile'] != 'linux-x64-gcc13':
        raise ValueError('owned Linux development build required')
    lock = json.loads(LOCK.read_text(encoding='utf-8'))
    lab = build / 'x11-lab'
    lab.mkdir(mode=0o700, exist_ok=True)
    if lab.is_symlink():
        raise ValueError('lab must be an owned directory')
    record = lab / 'identity.json'
    if record.exists():
        value = json.loads(record.read_text(encoding='utf-8'))
        if value['lock_sha256'] != sha(LOCK):
            raise ValueError('existing lab uses another lock; preserve it')
        for name, digest in value['files'].items():
            if sha(lab / 'sysroot' / name) != digest:
                raise ValueError('extracted lab file changed: ' + name)
        print('Verified existing pinned X11 lab:', lab)
        return
    packages = lab / 'packages'
    packages.mkdir(exist_ok=True)
    if packages.is_symlink():
        raise ValueError('package directory must not be a symlink')
    if args.refresh_metadata:
        lists = lab / 'apt-lists'
        (lists / 'partial').mkdir(parents=True, exist_ok=True)
        subprocess.run(['apt-get', '-o', 'Dir::State::lists=' + str(lists), '-o', 'Acquire::Languages=none',
                        '-o', 'Debug::NoLocking=1', 'update'], stdin=subprocess.DEVNULL, check=True, timeout=120)
    if sum(row['bytes'] for row in lock['packages']) > 64 * 1024**2:
        raise ValueError('package download exceeds 64 MiB budget')
    for row in lock['packages']:
        archive = packages / row['filename']
        if not archive.exists():
            print('Fetching', row['package'], row['version'], flush=True)
            options = ['-o', 'Dir::State::lists=' + str(lab / 'apt-lists')] if (lab / 'apt-lists').is_dir() else []
            subprocess.run(['apt-get', *options, 'download', row['package'] + '=' + row['version']],
                           cwd=packages, stdin=subprocess.DEVNULL, check=True, timeout=60)
        if not archive.exists():
            # apt includes a URL-escaped epoch in its output name; the repository
            # Filename field omits it. Match validated content, not that spelling.
            matches = [p for p in packages.glob('*.deb') if not p.is_symlink()
                       and p.stat().st_size == row['bytes'] and sha(p) == row['sha256']]
            if len(matches) != 1:
                raise ValueError('download did not produce one matching archive')
            matches[0].rename(archive)
        if archive.is_symlink() or archive.stat().st_size != row['bytes'] or sha(archive) != row['sha256']:
            raise ValueError('package identity differs: ' + row['package'])
    sysroot = lab / 'sysroot'
    # Preserve partial extraction on interruption; never recursively replace a tree.
    sysroot.mkdir(mode=0o700)
    for row in lock['packages']:
        subprocess.run(['dpkg-deb', '--extract', str(packages / row['filename']), str(sysroot)],
                       stdin=subprocess.DEVNULL, check=True, timeout=15)
    size = sum(p.stat().st_size for p in build.rglob('*') if p.is_file() and not p.is_symlink())
    if size > 1024**3:
        raise ValueError('owned build exceeded campaign 1 GiB budget')
    files = {p.relative_to(sysroot).as_posix(): sha(p) for p in sorted(sysroot.rglob('*'))
             if p.is_file() and not p.is_symlink()}
    value = {'version': '0.1.0', 'lock_sha256': sha(LOCK), 'uid': os.geteuid(),
             'build_bytes_after_prepare': size, 'files': files,
             'qualification': 'Extracted lab dependencies only; no desktop experiment has run.'}
    with record.open('x', encoding='utf-8', newline='\n') as file:
        json.dump(value, file, indent=2)
        file.write('\n')
    print('Prepared pinned X11 lab:', lab, '; owned build bytes:', size)


if __name__ == '__main__':
    main()
