"""Extract the pinned dconf CLI; never install packages or start services."""
import argparse
import json
from pathlib import Path
import subprocess
import urllib.request

from prepare_gnome_lab import ROOT, inventory, owned_build, sha

LOCK = ROOT / 'source/build/gnome-policy-runtime.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_dir', type=Path)
    build = owned_build(parser.parse_args().build_dir)
    lock = json.loads(LOCK.read_text())
    if any(sha(Path(name)) != digest for name, digest in lock['system_files'].items()):
        raise ValueError('installed dconf runtime differs')
    root = build / 'gnome-policy-runtime'
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise ValueError('owned runtime cannot be a symlink')
    record = root / 'identity.json'
    if record.exists():
        value = json.loads(record.read_text())
        if value['lock_sha256'] != sha(LOCK) or value['files'] != inventory(root / 'sysroot'):
            raise ValueError('existing runtime differs; preserve it')
        print('Verified', root)
        return
    row = lock['archive']
    expected_url = 'https://archive.ubuntu.com/ubuntu/pool/main/d/dconf/dconf-cli_0.40.0-4ubuntu0.1_amd64.deb'
    if row['url'] != expected_url or row['bytes'] != 28022:
        raise ValueError('bounded pinned archive required')
    archive = root / 'dconf-cli.deb'
    if not archive.exists():
        with urllib.request.urlopen(expected_url, timeout=30) as incoming:
            raw = incoming.read(row['bytes'] + 1)
        with archive.open('xb') as stream:
            stream.write(raw)
    if archive.is_symlink() or archive.stat().st_size != row['bytes'] or sha(archive) != row['sha256']:
        raise ValueError('archive identity differs')
    target = root / 'sysroot'
    target.mkdir(mode=0o700)
    subprocess.run(['dpkg-deb', '--extract', str(archive), str(target)], check=True, timeout=10)
    files = inventory(target)
    if sum(v.get('bytes', 0) for v in files.values()) > 256 * 1024:
        raise ValueError('extraction capacity exceeded')
    with record.open('x') as stream:
        json.dump({'lock_sha256': sha(LOCK), 'files': files}, stream, indent=2)
        stream.write('\n')
    print('Prepared', root)


if __name__ == '__main__':
    main()
