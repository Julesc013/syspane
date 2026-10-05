#pragma once
#include <X11/Xlib.h>

namespace syspane::desktop::x11 {
// Bounded EWMH investigation, not an admitted production desktop strategy.
bool configure_candidate(Display* display, Window window, bool below);
}
