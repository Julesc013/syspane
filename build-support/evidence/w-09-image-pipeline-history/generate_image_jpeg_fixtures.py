from pathlib import Path
import hashlib,json,subprocess
r=Path('/mnt/d/Projects/SysPane/syspane');out=Path('/home/ir4runner/.cache/syspane/campaign-229a498/image-fixtures');out.mkdir(exist_ok=True)
commands=[['g++','-std=c++17','-Wall','-Wextra','-Werror',str(r/'out/campaign/image_jpeg_fixture.cpp'),'-ljpeg','-o',str(out/'fixture')]]
commands += [[str(out/'fixture'),str(r/'tests/scene/image-cases'/name),mode] for name,mode in [('pattern.jpg','baseline'),('progressive.jpg','progressive')]]
records=[]
for command in commands:
    p=subprocess.run(command,capture_output=True,text=True);records.append(dict(command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,records[-1]
(r/'out/campaign/image-jpeg-fixture-generation.json').write_text(json.dumps(dict(commands=records,source_sha256=hashlib.sha256((r/'out/campaign/image_jpeg_fixture.cpp').read_bytes()).hexdigest(),purpose='Independent public JPEG fixtures; exact grayscale DC block input at quality 100.'),indent=2)+'\n')
