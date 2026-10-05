#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <string>
#include <poll.h>
#include <unistd.h>
#include "../desktop/x11/desktop_candidate.hpp"

namespace {
std::array<unsigned char, 17> payload(std::uint64_t generation) {
    std::array<unsigned char, 17> result{'S', 'Y', 'P', 'N', 1};
    for (unsigned n = 0; n < 8; ++n) result[5+n] = static_cast<unsigned char>(generation >> ((7-n)*8));
    std::uint32_t crc = 0xffffffffu;
    for (unsigned n = 0; n < 13; ++n) {
        crc ^= result[n];
        for (unsigned bit = 0; bit < 8; ++bit) crc = (crc >> 1) ^ ((crc & 1) ? 0xedb88320u : 0u);
    }
    crc ^= 0xffffffffu;
    for (unsigned n = 0; n < 4; ++n) result[13+n] = static_cast<unsigned char>(crc >> ((3-n)*8));
    return result;
}
void paint(Display* display, Window window, Pixmap buffer, GC gc, std::uint64_t generation) {
    const auto bytes = payload(generation);
    unsigned bit = 0;
    for (unsigned row = 0; row < 12; ++row) for (unsigned column = 0; column < 16; ++column) {
        unsigned long color;
        if (row == 0 || row == 11 || column == 0 || column == 15) {
            color = (column + row) % 2 ? 0xf0a010 : 0x1060e0;
            if (row == 11 && column == 0) color = 0xa020c0;
        } else {
            const bool one = bit < 136 && (bytes[bit/8] & (1u << (7 - bit%8)));
            color = one ? 0xe0e0e0 : 0x202020;
            ++bit;
        }
        XSetForeground(display, gc, color);
        XFillRectangle(display, buffer, gc, static_cast<int>(column*8), static_cast<int>(row*8), 8, 8);
    }
    XCopyArea(display, buffer, window, gc, 0, 0, 128, 96, 0, 0);
    XFlush(display);
}
}
int main(int argc, char** argv) {
    if (argc != 2 || (std::string(argv[1]) != "live" && std::string(argv[1]) != "hide" && std::string(argv[1]) != "freeze" &&
                      std::string(argv[1]) != "desktop" && std::string(argv[1]) != "desktop-below")) return 64;
    const std::string mode = argv[1];
    auto display = XOpenDisplay(nullptr);
    if (!display) return 69;
    const auto screen = DefaultScreen(display);
    const auto visual = DefaultVisual(display, screen);
    if (DefaultDepth(display, screen) != 24 || visual->red_mask != 0xff0000 || visual->green_mask != 0xff00 || visual->blue_mask != 0xff) {
        XCloseDisplay(display); return 69;
    }
    const auto window = XCreateSimpleWindow(display, RootWindow(display, screen), 32, 32, 128, 96, 0, 0, 0);
    if (!window) { XCloseDisplay(display); return 70; }
    XStoreName(display, window, "SysPane Oracle Probe");
    char name[] = "syspane-oracle-probe", kind[] = "SysPaneOracleProbe";
    XClassHint hint{name, kind};
    XSetClassHint(display, window, &hint);
    const unsigned long pid = static_cast<unsigned long>(getpid());
    XChangeProperty(display, window, XInternAtom(display, "_NET_WM_PID", False), XA_CARDINAL, 32, PropModeReplace,
                    reinterpret_cast<const unsigned char*>(&pid), 1);
    const auto message = XInternAtom(display, "_SYSPANE_ORACLE_GENERATION", False);
    const auto accepted = XInternAtom(display, "_SYSPANE_ORACLE_ACCEPTED", False);
    const auto protocols = XInternAtom(display, "WM_PROTOCOLS", False);
    auto close = XInternAtom(display, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(display, window, &close, 1);
    if ((mode == "desktop" || mode == "desktop-below") &&
        !syspane::desktop::x11::configure_candidate(display, window, mode == "desktop-below")) {
        XDestroyWindow(display, window); XCloseDisplay(display); return 69;
    }
    XSelectInput(display, window, ExposureMask | StructureNotifyMask);
    const auto gc = XCreateGC(display, window, 0, nullptr);
    const auto buffer = XCreatePixmap(display, window, 128, 96, 24);
    XMapWindow(display, window);
    if (mode == "desktop-below") XLowerWindow(display, window);
    XFlush(display);
    std::cout << "{\"window\":" << window << ",\"pid\":" << getpid() << ",\"claims_visible\":true}\n" << std::flush;
    const auto start = std::chrono::steady_clock::now();
    bool running = true, has_generation = false;
    std::uint64_t generation = 0, drawn = 0;
    unsigned updates = 0;
    int result = 0;
    while (running) {
        if (std::chrono::steady_clock::now() - start >= std::chrono::seconds(15)) { result = 70; break; }
        if (!XPending(display)) {
            pollfd fd{ConnectionNumber(display), POLLIN, 0};
            (void)::poll(&fd, 1, 50);
            continue;
        }
        XEvent event{};
        XNextEvent(display, &event);
        if (event.type == Expose && has_generation) paint(display, window, buffer, gc, drawn);
        if (event.type != ClientMessage || event.xclient.window != window || event.xclient.format != 32) continue;
        if (event.xclient.message_type == protocols && static_cast<Atom>(event.xclient.data.l[0]) == close) { running = false; continue; }
        if (event.xclient.message_type != message || event.xclient.data.l[2] || event.xclient.data.l[3] || event.xclient.data.l[4]) { result = 64; break; }
        const auto next = (static_cast<std::uint64_t>(static_cast<std::uint32_t>(event.xclient.data.l[0])) << 32) |
                          static_cast<std::uint32_t>(event.xclient.data.l[1]);
        if ((has_generation && next <= generation) || ++updates > 128) { result = 64; break; }
        generation = next;
        const std::array<unsigned long, 2> words{static_cast<std::uint32_t>(next >> 32), static_cast<std::uint32_t>(next)};
        XChangeProperty(display, window, accepted, XA_CARDINAL, 32, PropModeReplace,
                        reinterpret_cast<const unsigned char*>(words.data()), 2);
        if (mode == "hide" && updates == 2) XUnmapWindow(display, window);
        else {
            if (mode == "hide" && updates == 3) XMapWindow(display, window);
            if (mode != "freeze" || !has_generation) drawn = next;
            paint(display, window, buffer, gc, drawn);
        }
        has_generation = true;
        XFlush(display);
    }
    XFreeGC(display, gc);
    XFreePixmap(display, buffer);
    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return result;
}
