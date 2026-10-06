"""Verify installed GTK development identity; does not install or modify system packages."""
import hashlib
from pathlib import Path
import subprocess

EXPECTED = {
    'libgtk-3-dev': '3.24.41-4ubuntu1.3',
    'libgtk-3-0t64': '3.24.41-4ubuntu1.3',
    'libglib2.0-dev': '2.80.0-6ubuntu3.9',
    'libx11-dev': '2:1.8.7-1build1',
    'libx11-6': '2:1.8.7-1build1',
    'libxext-dev': '2:1.3.4-1build2',
    'libxext6': '2:1.3.4-1build2',
    'xvfb': '2:21.1.12-1ubuntu1.6',
}
for package, version in EXPECTED.items():
    actual = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', package], text=True).strip()
    if actual != version:
        raise ValueError('diagnostic package differs from pinned profile: ' + package)
runtime = Path('/usr/lib/x86_64-linux-gnu/libgtk-3.so.0').resolve(strict=True)
if hashlib.sha256(runtime.read_bytes()).hexdigest() != '0611fd19d1354a39a7cfafceffa3bdf4289d4c497c7f69ff337f86e99cf37d93':
    raise ValueError('diagnostic GTK runtime fingerprint differs')
if hashlib.sha256(Path('/usr/bin/Xvfb').read_bytes()).hexdigest() != '2c7f5a9534410fed5092d782a69ca7ffd9fce80e98b81ffe4944d703dd11d3b1':
    raise ValueError('diagnostic Xvfb test server fingerprint differs')
if hashlib.sha256(Path('/usr/lib/x86_64-linux-gnu/libX11.so.6').read_bytes()).hexdigest() != 'c5b5d782bd9cab3420a62df88f5c991507edf3331a89f98464ddbc538c37b879':
    raise ValueError('native UI/oracle X11 runtime fingerprint differs')
print('diagnostic toolkit verified: GTK 3.24.41 / Ubuntu 3.24.41-4ubuntu1.3')
if hashlib.sha256(Path('/usr/lib/x86_64-linux-gnu/libXext.so.6').read_bytes()).hexdigest() != '2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44':
    raise ValueError('X11 candidate Xext runtime fingerprint differs')
