"""Selected installed native accessibility/observer identities; no installation."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
def identify():
    packages=['at-spi2-core','libatspi2.0-0t64','libatk1.0-0t64','libatk-bridge2.0-0t64',
              'gir1.2-atspi-2.0','python3-gi','dbus-daemon']
    files=['/usr/lib/x86_64-linux-gnu/libatspi.so.0','/usr/lib/x86_64-linux-gnu/libatk-1.0.so.0',
           '/usr/lib/x86_64-linux-gnu/libatk-bridge-2.0.so.0','/usr/bin/dbus-run-session',
           '/usr/bin/dbus-daemon','/usr/libexec/at-spi-bus-launcher','/usr/libexec/at-spi2-registryd']
    return dict(packages=subprocess.check_output(['dpkg-query','-W',*packages],text=True),
                files={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files})
def verify():
    actual=identify()
    if actual!=json.loads((ROOT/'surface-runtime.json').read_text()):raise ValueError('native scene observer runtime differs from pinned identity')
    return actual
if __name__=='__main__':verify();print('Native scene accessibility/observer identity verified')
