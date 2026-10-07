from pathlib import Path
r=Path.cwd();p=r/'tests/scene/native_surface.py';t=p.read_text()
t=t.replace('chart=False):','chart=False,image=False):')
t=t.replace("report['surface_runtime_sha256']=", "if image:\n        report['image_worker_sha256']=sha(exe.with_name('SysPane.ImageWorker'))\n        report['image_oracle_sha256']=sha(ROOT/'tests/scene/image-cases/surface.json')\n        report['image_runtime_sha256']=sha(ROOT/'build-support/image-runtime.json')\n    report['surface_runtime_sha256']=")
t=t.replace("('chart-' if chart", "('image-' if image else 'chart-' if chart")
t=t.replace("        if chart:\n", """        if image:
            canvas=bytearray(800*600*3)
            if number in (987,None):raw=[0,255,0,255]*45
            else:
                mode={123:'contain',456:'contain','cover':'cover','stretch':'stretch'}[number]
                raw=next(c['rgba'] for c in json.loads((ROOT/'tests/scene/image-cases/surface.json').read_text()) if c['width']==9 and c['fit']==mode)
            for y in range(5):
                for x in range(9):canvas[(y*800+x)*3:(y*800+x)*3+3]=bytes(raw[(y*9+x)*4:(y*9+x)*4+3])
            return bytes(canvas),'Public image\\nImage ready'
        if chart:
""",1)
t=t.replace('if table or chart else label.startswith(prefix)','if table or chart or image else label.startswith(prefix)')
t=t.replace("        if mode=='normal':\n            command('replace');check", "        if mode=='normal':\n            if image:\n                for fit in ('cover','stretch'):\n                    command('fit-'+fit);check('FIT-'+fit,*view(fit),timeout=3)\n            command('replace');check")
t=t.replace("check('REPLACE',*references[(987,False)])", "check('REPLACE',*references[(987,False)],timeout=3 if image else .2)")
t=t.replace("check('REGRANT',*references[(None,False)])", "check('REGRANT',*references[(None,False)],timeout=3 if image else .2)")
t=t.replace("check('FRESH',*references[(456,False)])", "check('FRESH',*references[(456,False)],timeout=3 if image else .2)")
t=t.replace("len(sys.argv)>6 and 'CHART' not in sys.argv,'CONTENT' in sys.argv,'CHART' in sys.argv", "len(sys.argv)>6 and 'CHART' not in sys.argv and 'IMAGE' not in sys.argv,'CONTENT' in sys.argv,'CHART' in sys.argv,'IMAGE' in sys.argv")
t=t.replace("chart='CHART' in sys.argv;table=len(sys.argv)>4 and not chart", "image='IMAGE' in sys.argv;chart='CHART' in sys.argv;table=len(sys.argv)>4 and not chart and not image")
t=t.replace("family='CHART-ERASURE' if chart", "family='IMAGE-ERASURE' if image else 'CHART-ERASURE' if chart")
t=t.replace("+(['CHART'] if chart", "+(['IMAGE'] if image else ['CHART'] if chart")
p.write_text(t,encoding='utf-8',newline='\n')
# Preserve the independent observer before adding the native-window trace.
import zipfile,hashlib,json
d=r/'out/campaign/scene-images-original';n='tests/scene/native_surface.py'
with zipfile.ZipFile(d/'native-original.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(r/n,n)
(d/'native-original.json').write_text(json.dumps({n:hashlib.sha256((r/n).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'tests/scene/surface_window.cpp';t=p.read_text().replace('#include "chart_fixture.hpp"','#include "image_fixture.hpp"')
t=t.replace('std::string input,mode;', 'std::string input,mode,root;')
t=t.replace('table=false,chart=false;', 'table=false,chart=false,image=false,closing=false;')
t=t.replace('if(name=="revoke")', 'if(image&&(name=="replace"||name=="fresh"||name=="fit-cover"||name=="fit-stretch")){auto cfg=name=="replace"?image_config(root,green_image(),"image/svg+xml"):image_config(root);if(name=="fit-cover"||name=="fit-stretch")cfg.authored.scene["widgets"][0]["content"]["fit"]=name.substr(4);owner->replace(std::move(cfg),now());}\n        else if(name=="revoke")')
t=t.replace('else if(name=="close"){owner->close();gtk_main_quit();}', 'else if(name=="close"){owner->close();closing=true;}')
t=t.replace('try{if(w.connected)w.owner->heartbeat', 'try{const bool stopped=w.owner->poll_image_jobs();if(w.closing){if(stopped)gtk_main_quit();return G_SOURCE_CONTINUE;}if(w.connected)w.owner->heartbeat')
t=t.replace('const bool chart=mode.find("chart-")==0,', 'const bool image=mode.find("image-")==0,chart=mode.find("chart-")==0,')
t=t.replace('(chart||table)?mode.substr(6)', '(chart||table||image)?mode.substr(6)')
t=t.replace('w.chart=chart;auto* window', 'w.chart=chart;w.image=image;w.root=root;auto* window')
t=t.replace('auto cfg=chart?chart_config(root)', 'auto cfg=image?image_config(root):chart?chart_config(root)')
t=t.replace('[&]{return w.clear();});', '[&]{return w.clear();},image?image_worker_path():std::string());')
t=t.replace('}else w.full(123);', '}else if(!image)w.full(123);')
p.write_text(t,encoding='utf-8',newline='\n')
