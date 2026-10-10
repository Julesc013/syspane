"""RandR stimuli confined to the installed harness's authenticated private Xvfb."""
import ctypes as C


class Monitor(C.Structure):
    _fields_ = [('name', C.c_ulong), ('primary', C.c_int), ('automatic', C.c_int), ('noutput', C.c_int),
                ('x', C.c_int), ('y', C.c_int), ('width', C.c_int), ('height', C.c_int),
                ('mwidth', C.c_int), ('mheight', C.c_int), ('outputs', C.POINTER(C.c_ulong))]


class Topology:
    def __init__(self):
        self.x = C.CDLL('libX11.so.6'); self.rr = C.CDLL('libXrandr.so.2')
        for lib, name, args, result in [
            (self.x, 'XOpenDisplay', [C.c_char_p], C.c_void_p),
            (self.x, 'XDefaultRootWindow', [C.c_void_p], C.c_ulong),
            (self.x, 'XInternAtom', [C.c_void_p, C.c_char_p, C.c_int], C.c_ulong),
            (self.x, 'XSync', [C.c_void_p, C.c_int], C.c_int),
            (self.x, 'XCloseDisplay', [C.c_void_p], C.c_int),
            (self.rr, 'XRRGetMonitors', [C.c_void_p, C.c_ulong, C.c_int, C.POINTER(C.c_int)], C.POINTER(Monitor)),
            (self.rr, 'XRRFreeMonitors', [C.POINTER(Monitor)], None),
            (self.rr, 'XRRSetMonitor', [C.c_void_p, C.c_ulong, C.POINTER(Monitor)], None),
            (self.rr, 'XRRDeleteMonitor', [C.c_void_p, C.c_ulong, C.c_ulong], None),
            (self.rr, 'XRRSetScreenSize', [C.c_void_p, C.c_ulong, C.c_int, C.c_int, C.c_int, C.c_int], None)]:
            function = getattr(lib, name); function.argtypes = args; function.restype = result
        self.display = self.x.XOpenDisplay(None); assert self.display
        self.root = self.x.XDefaultRootWindow(self.display)
        n = C.c_int(); monitors = self.rr.XRRGetMonitors(self.display, self.root, 1, C.byref(n))
        assert n.value == 1 and monitors[0].width == 800 and monitors[0].height == 600
        original = monitors[0]
        self.values = {name: getattr(original, name) for name, _ in Monitor._fields_ if name != 'outputs'}
        self.outputs = (C.c_ulong * original.noutput)(*[original.outputs[i] for i in range(original.noutput)])
        self.rr.XRRFreeMonitors(monitors)
        self.values['name'] = self.x.XInternAtom(self.display, b'SysPaneFixture', False)
        self.narrowed = False

    def change(self, narrow):
        if narrow:
            monitor = Monitor(**dict(self.values, width=400, automatic=0), outputs=self.outputs)
            self.rr.XRRSetMonitor(self.display, self.root, C.byref(monitor))
        else:
            self.rr.XRRDeleteMonitor(self.display, self.root, self.values['name'])
        self.narrowed = narrow
        self.rr.XRRSetScreenSize(self.display, self.root, 800, 600, 212 if narrow else 211, 159)
        self.x.XSync(self.display, False)

    def geometry(self):
        n = C.c_int(); monitors = self.rr.XRRGetMonitors(self.display, self.root, 1, C.byref(n))
        result = [[monitors[i].x, monitors[i].y, monitors[i].width, monitors[i].height] for i in range(n.value)]
        self.rr.XRRFreeMonitors(monitors)
        return result

    def close(self):
        if self.narrowed: self.change(False)
        self.x.XCloseDisplay(self.display)
