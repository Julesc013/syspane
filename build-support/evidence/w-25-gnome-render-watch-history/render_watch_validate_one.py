from pathlib import Path
import json,sys
root=Path('/mnt/d/Projects/SysPane/syspane');sys.path.insert(0,str(root/'build-support'))
from record_gnome_render_watch import validate
build=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
print(validate(json.loads(Path(sys.argv[1]).read_text()),build))
