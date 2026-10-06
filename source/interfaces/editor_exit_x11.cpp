#include "editor_exit_x11.hpp"
#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <stdexcept>
#include <vector>

namespace syspane::interfaces {
namespace {
bool x_failed = false;
int note_error(Display*, XErrorEvent*) { x_failed = true; return 0; }
struct CheckedRequests {
    Display* display;
    XErrorHandler previous;
    explicit CheckedRequests(Display* value) : display(value), previous(XSetErrorHandler(note_error)) { x_failed = false; }
    ~CheckedRequests() { XSync(display, False); XSetErrorHandler(previous); }
    bool failed() { XSync(display, False); return x_failed; }
};
unsigned modifiers(Display* display, KeySym symbol) {
    const auto code = XKeysymToKeycode(display, symbol);
    if (!code) return 0;
    auto* map = XGetModifierMapping(display);
    if (!map) throw std::runtime_error("editor.keymap");
    unsigned result = 0;
    for (int slot = 0; slot < 8; ++slot)
        for (int key = 0; key < map->max_keypermod; ++key)
            if (map->modifiermap[slot * map->max_keypermod + key] == code) result |= 1u << slot;
    XFreeModifiermap(map);
    return result;
}
}
struct EditorExitKeys::Impl {
    Display* display = nullptr;
    Window root = 0;
    KeyCode code = 0;
    unsigned locks = 0;
    ~Impl() {
        if (display) {
            if (code) XUngrabKey(display, code, AnyModifier, root);
            XCloseDisplay(display);
        }
    }
};
EditorExitKeys::EditorExitKeys() : impl_(std::make_unique<Impl>()) {
    auto& state = *impl_;
    state.display = XOpenDisplay(nullptr);
    if (!state.display) throw std::runtime_error("editor.display");
    state.root = DefaultRootWindow(state.display);
    state.code = XKeysymToKeycode(state.display, XK_Escape);
    const auto num = modifiers(state.display, XK_Num_Lock);
    if (!state.code || modifiers(state.display, XK_Control_L) != ControlMask ||
        modifiers(state.display, XK_Alt_L) != Mod1Mask || modifiers(state.display, XK_Caps_Lock) != LockMask ||
        (num && ((num & (num - 1)) || (num & (ControlMask | Mod1Mask | ShiftMask | LockMask)))))
        throw std::runtime_error("editor.keymap");
    state.locks = LockMask | num;
    CheckedRequests requests(state.display);
    for (unsigned variant = 0; variant < 256; ++variant)
        if ((variant & ~state.locks) == 0)
            XGrabKey(state.display, state.code, ControlMask | Mod1Mask | variant, state.root,
                     False, GrabModeAsync, GrabModeAsync);
    if (requests.failed()) throw std::runtime_error("editor.shortcut_unavailable");
}
EditorExitKeys::~EditorExitKeys() = default;
EditorExitInput EditorExitKeys::poll() {
    auto& state = *impl_;
    for (unsigned count = 0; count < 32 && XPending(state.display); ++count) {
        XEvent event{};
        XNextEvent(state.display, &event);
        if (event.type == MappingNotify && event.xmapping.request != MappingPointer) {
            XRefreshKeyboardMapping(&event.xmapping);
            // XKB may announce a device switch with unchanged effective bindings.
            // Preserve the existing grab only when every relevant assignment agrees.
            if (XKeysymToKeycode(state.display, XK_Escape) != state.code ||
                modifiers(state.display, XK_Control_L) != ControlMask ||
                modifiers(state.display, XK_Alt_L) != Mod1Mask ||
                modifiers(state.display, XK_Caps_Lock) != LockMask ||
                (LockMask | modifiers(state.display, XK_Num_Lock)) != state.locks)
                return EditorExitInput::unavailable;
        }
        constexpr unsigned buttons = Button1Mask | Button2Mask | Button3Mask | Button4Mask | Button5Mask;
        if (event.type == KeyPress && !event.xkey.send_event && event.xkey.keycode == state.code &&
            (event.xkey.state & ~(state.locks | buttons)) == (ControlMask | Mod1Mask)) return EditorExitInput::requested;
    }
    return EditorExitInput::none;
}
}
