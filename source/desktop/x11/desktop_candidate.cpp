#include "desktop_candidate.hpp"
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <X11/extensions/shape.h>
#include <array>

namespace syspane::desktop::x11 {
bool configure_candidate(Display* display, Window window, bool below) {
    int event = 0, error = 0, major = 0, minor = 0;
    if (!XShapeQueryExtension(display, &event, &error) ||
        !XShapeQueryVersion(display, &major, &minor) || major < 1 || (major == 1 && minor < 1)) return false;
    const Atom type = XInternAtom(display, "_NET_WM_WINDOW_TYPE_DESKTOP", False);
    XChangeProperty(display, window, XInternAtom(display, "_NET_WM_WINDOW_TYPE", False),
                    XA_ATOM, 32, PropModeReplace, reinterpret_cast<const unsigned char*>(&type), 1);
    const std::array<Atom, 3> state{XInternAtom(display, "_NET_WM_STATE_SKIP_TASKBAR", False),
                                  XInternAtom(display, "_NET_WM_STATE_SKIP_PAGER", False),
                                  XInternAtom(display, "_NET_WM_STATE_BELOW", False)};
    XChangeProperty(display, window, XInternAtom(display, "_NET_WM_STATE", False), XA_ATOM, 32,
                    PropModeReplace, reinterpret_cast<const unsigned char*>(state.data()), below ? 3 : 2);
    XWMHints hints{};
    hints.flags = InputHint;
    hints.input = False;
    XSetWMHints(display, window, &hints);
    XShapeCombineRectangles(display, window, ShapeInput, 0, 0, nullptr, 0, ShapeSet, Unsorted);
    return true;
}
}
