"""Extract the pinned GNOME laboratory without installing packages or services."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'build-support/gnome-lab-packages.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix():
            {'symlink': os.readlink(p)} if p.is_symlink() else {'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(root.rglob('*')) if p.is_symlink() or p.is_file()}


def owned_build(path):
    build = path.resolve(strict=True)
    if os.name != 'posix' or os.geteuid() == 0:
        raise ValueError('unprivileged Linux account required')
    if json.loads((build / '.syspane-owner.json').read_text())['profile'] != 'linux-x64-gcc13':
        raise ValueError('owned Linux development build required')
    if build != Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13'):
        raise ValueError('only the admitted campaign build is allowed')
    return build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_dir', type=Path)
    args = parser.parse_args()
    build = owned_build(args.build_dir)
    lock = json.loads(LOCK.read_text(encoding='utf-8'))
    rows = lock['packages']
    if sum(r['bytes'] for r in rows) > 128 * 1024**2 or sum(r['installed_bytes'] for r in rows) > 512 * 1024**2:
        raise ValueError('pinned package budget exceeded')
    lab = build / 'gnome-lab'
    lab.mkdir(mode=0o700, exist_ok=True)
    if lab.is_symlink():
        raise ValueError('lab may not be a symlink')
    identity = lab / 'identity.json'
    sysroot = lab / 'sysroot'
    if identity.exists():
        record = json.loads(identity.read_text())
        if record['lock_sha256'] != sha(LOCK) or record['files'] != inventory(sysroot):
            raise ValueError('existing laboratory identity changed; preserve it')
        print('Verified pinned GNOME laboratory:', lab)
        return
    packages = lab / 'packages'
    packages.mkdir(mode=0o700, exist_ok=True)
    if packages.is_symlink():
        raise ValueError('package directory may not be a symlink')
    def fetch(row):
        if Path(row['filename']).name != row['filename']:
            raise ValueError('archive must be a basename')
        parsed = urllib.parse.urlparse(row['url'])
        if parsed.scheme != 'https' or parsed.hostname not in {'archive.ubuntu.com', 'security.ubuntu.com'}:
            raise ValueError('unexpected package origin')
        archive = packages / row['filename']
        if not archive.exists():
            print('Fetching', row['package'], row['version'], flush=True)
            partial = archive.with_suffix('.partial')
            with urllib.request.urlopen(row['url'], timeout=30) as incoming, partial.open('xb') as outgoing:
                count = 0
                while chunk := incoming.read(1024 * 1024):
                    count += len(chunk)
                    if count > row['bytes']:
                        raise ValueError('download exceeds pinned size')
                    outgoing.write(chunk)
            if partial.stat().st_size != row['bytes'] or sha(partial) != row['sha256']:
                raise ValueError('download differs from pinned archive: ' + row['package'])
            partial.rename(archive)
        if archive.is_symlink() or archive.stat().st_size != row['bytes'] or sha(archive) != row['sha256']:
            raise ValueError('archive identity differs: ' + row['package'])
    if len({row['filename'] for row in rows}) != len(rows):
        raise ValueError('duplicate archive filenames')
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(fetch, rows))
    # Never overwrite a partially extracted tree. All archive checks precede this.
    sysroot.mkdir(mode=0o700)
    for row in rows:
        subprocess.run(['dpkg-deb', '--extract', str(packages / row['filename']), str(sysroot)],
                       stdin=subprocess.DEVNULL, check=True, timeout=30)
    files = inventory(sysroot)
    size = sum(r.get('bytes', 0) for r in files.values())
    if size > 512 * 1024**2:
        raise ValueError('extracted laboratory exceeds 512 MiB')
    record = {'version': '0.1.0', 'lock_sha256': sha(LOCK), 'uid': os.geteuid(),
              'extracted_bytes': size, 'files': files,
              'qualification': 'Extracted runtime only; no desktop experiment has run.'}
    with identity.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print('Prepared pinned GNOME laboratory:', lab, '; extracted bytes:', size)


if __name__ == '__main__':
    main()
