"""Independent, deterministic package bytes and exact pins for settings integration."""
from pathlib import Path
import copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
encoded=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture():
    read=lambda n:json.loads((ROOT/'spec/fixtures/valid'/n).read_text())
    settings,scene,theme=read('settings.json'),read('scene-content.json'),read('theme.json')
    settings['revision']=scene['revision']='40';scene['theme_id']=None
    packages=[]
    def pack(id,kind,doc,deps=(),extras=None):
        assets={kind+'.json':encoded(doc),**(extras or {})}
        manifest=dict(schema_version='0.1.0',package_id='package:'+id,version='0.1.0',kind=kind,license='MIT',dependencies=list(deps),
            assets=[dict(path=n,media_type='image/png' if n.endswith('.png') else 'application/json',sha256=sha(b),bytes=len(b)) for n,b in sorted(assets.items())],
            total_unpacked_bytes=sum(map(len,assets.values())),required_capabilities=[],optional_capabilities=[])
        raw=encoded(manifest);packages.append(dict(manifest=raw.decode(),assets_hex={n:b.hex() for n,b in assets.items()}))
        return dict(id=manifest['package_id'],version='0.1.0',sha256=sha(raw)),dict(id=doc[kind+'_id'],version='0.1.0',sha256=sha(assets[kind+'.json']))
    png=(ROOT/'tests/scene/image-cases/rgb.png').read_bytes()
    native,nt=pack('settings-native','theme',theme,extras={'images/pixel.png':png})
    contrast=copy.deepcopy(theme);contrast['theme_id']='theme:contrast';contrast['name']='Settings contrast';contrast['tokens']['background']='#000000ff'
    other,ot=pack('settings-contrast','theme',contrast)
    scene['widgets'][6]['content']['asset']=dict(package=native,path='images/pixel.png',sha256=sha(png))
    scene_package,scene_pin=pack('settings-scene','scene',scene)
    preset=dict(schema_version='0.1.0',preset_id='preset:settings-alternate',version='0.1.0',parent=None,scene=scene_pin,theme=None,settings=[],required_capabilities=[],optional_capabilities=[])
    alternate,alternate_pin=pack('settings-alternate','preset',preset,[native,other,scene_package])
    preset['preset_id']='preset:settings';selected,preset_pin=pack('settings','preset',preset,[native,other,scene_package,alternate])
    return dict(authored=dict(settings=settings,scene=scene),packages=packages,selection=dict(package=selected,preset=preset_pin),
        alternate_selection=dict(package=alternate,preset=alternate_pin),themes={'theme:native':nt,'theme:contrast':ot})
if __name__=='__main__':
    p=ROOT/'tests/configuration/settings-content-fixture.json';raw=encoded(fixture())
    if sys.argv[1:] == ['--check']:assert p.read_bytes()==raw,'fixed resource fixture differs'
    else:
        assert not p.exists(),'do not overwrite a preserved fixture';p.write_bytes(raw)
    print('Settings resource fixture:',sha(raw))
