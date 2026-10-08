"""Identify the existing image loader and native containment development inputs."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def identify():
    packages=subprocess.check_output(['dpkg-query','-W','libgdk-pixbuf-2.0-dev','libgdk-pixbuf-2.0-0','librsvg2-2','librsvg2-common','libpng16-16t64','libjpeg-turbo8'],text=True)
    paths={Path('/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders.cache'),Path('/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.so')}
    for initial in ('/usr/lib/x86_64-linux-gnu/libgdk_pixbuf-2.0.so.0','/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.so'):
        paths.add(Path(initial))
        for line in subprocess.check_output(['ldd',initial],text=True).splitlines():
            for word in line.split():
                if word.startswith('/') and Path(word).is_file():paths.add(Path(word))
    for directory in ('/usr/include/gdk-pixbuf-2.0','/usr/include/glib-2.0'):
        paths.update(p for p in Path(directory).rglob('*.h'))
    for name in ('linux/landlock.h','linux/seccomp.h','linux/filter.h','linux/audit.h','x86_64-linux-gnu/sys/resource.h'):
        paths.add(Path('/usr/include')/name)
    paths.add(Path('/usr/lib/x86_64-linux-gnu/glib-2.0/include/glibconfig.h'))
    return dict(packages=packages,kernel=os.uname().release,files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
def verify():
    value=identify();assert value==json.loads((ROOT/'image-runtime.json').read_text()),'Image runtime/header/kernel identity differs; revise the development profile explicitly'
    return value
if __name__=='__main__':print('native image dependencies verified:',len(verify()['files']),'files')
