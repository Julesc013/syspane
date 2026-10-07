from pathlib import Path
import hashlib,json
r=Path.cwd()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
path='build-support/components.json';v=json.loads((r/path).read_text());parts={p['target']:p for p in v['components']}
parts['syspane_scene']['public_interfaces'].append('source/scene/image.hpp');parts['syspane_scene']['sources'].append('source/scene/image.cpp')
parts['syspane_scene_tests']['sources'].append('tests/scene/image_fit_tests.cpp')
for ident,target,kind,owner,headers,sources,deps in [
 ('native-image','syspane_native_image','STATIC_LIBRARY','source/rendering/',['source/rendering/image_decode.hpp'],['source/rendering/image_decode_linux.cpp','source/rendering/image_sandbox_linux.cpp'],['syspane_scene','PkgConfig::PIXBUF']),
 ('image-worker','syspane_image_worker','EXECUTABLE','source/application/',[],['source/application/image_worker.cpp'],['syspane_native_image','syspane_child'])]:
    v['components'].append(dict(id=ident,target=target,type=kind,source_owner=owner,public_interfaces=headers,private_interfaces=[],sources=sources,allowed_dependencies=deps,target_requirements=['cxx17','native_image'],roles=['development_test'],installed_files=[],profiles=['linux-x64-gcc13']))
write(path,v)
path='build-support/targets/linux-x64-gcc13.json';v=json.loads((r/path).read_text());v['revision']=str(int(v['revision'])+1)
v['dependencies'].append(dict(id='native-image-development-runtime',version='GdkPixbuf 2.42.10 / librsvg 2.58.0; Linux Landlock ABI >= 3',sha256=hashlib.sha256((r/'build-support/image-runtime.json').read_bytes()).hexdigest(),license='Installed system libraries; package copyright files apply; no redistribution claim'))
v['limitations'].append('Image decoding and fit are bounded worker/component experiments. Operational image widgets require asynchronous policy-bound scene integration and independent native erasure; historical/native release qualification remains open.')
write(path,v)
for name in ('native_chart_step.py','native_chart_flow.py'):
    text=(r/'out/campaign'/name).read_text().replace('native-chart','image-pipeline').replace('native_chart','image_pipeline')
    text=text.replace("^(scene[.](CHART-|PLOT-)|native[.]SCENE-(CHART|SURFACE|TABLE)$|composition[.])","^(scene[.]IMAGE-|native[.]IMAGE-DECODE$|composition[.])")
    text=text.replace("^(scene[.]|composition[.]|legacy[.]|native[.]SCENE-(SURFACE|TABLE|CHART)$)","^(scene[.]|composition[.]|legacy[.]|native[.](IMAGE-DECODE|SCENE-(SURFACE|TABLE|CHART))$)")
    text=text.replace("^native[.]CHART-ERASURE$","^native[.]IMAGE-DECODE$")
    (r/'out/campaign'/name.replace('native_chart','image_pipeline')).write_text(text,encoding='utf-8',newline='\n')
