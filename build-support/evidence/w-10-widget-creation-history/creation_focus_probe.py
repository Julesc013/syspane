"""Bounded diagnostic wrapper: original checks plus read-only focus evidence."""
from pathlib import Path
import ctypes as C,hashlib,sys
r=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(r/'tests/editor'),str(r/'tests/configuration')]
import native_editor as editor
import native_large_commands as suite
original=editor.Harness.focus
def snapshot(h,id):
    h.input.x.XGetInputFocus.argtypes=[C.c_void_p,C.POINTER(C.c_ulong),C.POINTER(C.c_int)]
    focus=C.c_ulong();revert=C.c_int();h.input.x.XGetInputFocus(h.input.handle,C.byref(focus),C.byref(revert))
    obj=h.find(id);obj.clear_cache();state=obj.get_state_set()
    return dict(target=id,x_focus=focus.value,revert=revert.value,owner_windows=list(h.input.windows(h.pid)),component=obj.get_component_iface() is not None,states=[str(s) for s in state.get_states()],process_exit=h.proc.poll())
def focus(h,id):
    try:original(h,id)
    except Exception:
        h.report['focus_probe']=snapshot(h,id)
        h.report['focus_probe']['focused']=[dict(description=o.get_description(),name=h.text(o),role=str(o.get_role())) for o in h.objects() if o.get_state_set().contains(h.Atspi.StateType.FOCUSED)]
        h.report['focus_probe']['probe_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        raise
editor.Harness.focus=focus
start=suite.subprocess.Popen
def child(args,*a,**kw):
    args=[str(Path(__file__)) if x==str(Path(suite.__file__)) else x for x in args]
    return start(args,*a,**kw)
suite.subprocess.Popen=child
write=suite.write
def record(path,data):
    if path.name=='result.json' and path.parent.name.startswith('large-commands-'):
        import json
        v=json.loads(data);v['family']='LARGE-COMMANDS-DIAGNOSTIC';v['probe_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();data=suite.encoded(v)
    write(path,data)
suite.write=record
suite.main()
