#include "child.hpp"
#include "editor_exit_x11.hpp"
#include "local_ipc.hpp"
#include <gtk/gtk.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
#include <unistd.h>

namespace {
using syspane::platform::Child;
using syspane::platform::monotonic_ms;
volatile std::sig_atomic_t finish_child = 0;
void finish(int) { finish_child = 1; }
void event(const char* type, std::uint64_t value = 0) {
    std::cout << "{\"event\":\"" << type << "\",\"value\":" << value << ",\"at_ms\":" << monotonic_ms() << "}\n" << std::flush;
}
int managed_editor() {
    if (!gtk_init_check(nullptr, nullptr)) return 69;
    GtkWidget* window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "SysPane editor lifetime candidate");
    gtk_window_set_default_size(GTK_WINDOW(window), 800, 500);
    gtk_window_set_resizable(GTK_WINDOW(window), TRUE);
    g_signal_connect(window, "map-event", G_CALLBACK(+[](GtkWidget* widget, GdkEvent*, gpointer) -> gboolean {
        gtk_window_maximize(GTK_WINDOW(widget)); return FALSE;
    }), nullptr);
    GtkWidget* canvas = gtk_drawing_area_new();
    gtk_container_add(GTK_CONTAINER(window), canvas);
    g_signal_connect(canvas, "draw", G_CALLBACK(+[](GtkWidget*, cairo_t* context, gpointer) -> gboolean {
        cairo_set_source_rgb(context, 204.0/255.0, 34.0/255.0, 51.0/255.0);
        cairo_paint(context); return FALSE;
    }), nullptr);
    g_signal_connect(window, "delete-event", G_CALLBACK(+[](GtkWidget*, GdkEvent*, gpointer) -> gboolean {
        finish_child = 1; gtk_main_quit(); return TRUE;
    }), nullptr);
    auto started = monotonic_ms();
    const guint timer = g_timeout_add(10, +[](gpointer data) -> gboolean {
        if (finish_child || monotonic_ms() - *static_cast<const std::uint64_t*>(data) >= 17000) {
            gtk_main_quit(); return G_SOURCE_REMOVE;
        }
        return G_SOURCE_CONTINUE;
    }, &started);
    gtk_window_maximize(GTK_WINDOW(window));
    gtk_widget_show_all(window);
    gtk_main();
    if (g_main_context_find_source_by_id(nullptr, timer)) g_source_remove(timer);
    gtk_widget_destroy(window);
    return finish_child ? 0 : 70;
}
int editor(std::uint64_t parent, bool maximized) {
    syspane::platform::arm_parent_lifetime(parent);
    std::signal(SIGTERM, finish);
    if (maximized) return managed_editor();
    Display* display = XOpenDisplay(nullptr);
    if (!display) return 69;
    const auto root = DefaultRootWindow(display);
    const auto window = XCreateSimpleWindow(display, root, 0, 100, 800, 500, 0, 0, 0xcc2233);
    const unsigned long pid = syspane::platform::current_process_id();
    XChangeProperty(display, window, XInternAtom(display, "_NET_WM_PID", False), XA_CARDINAL, 32,
                    PropModeReplace, reinterpret_cast<const unsigned char*>(&pid), 1);
    XStoreName(display, window, "SysPane editor lifetime candidate");
    XSelectInput(display, window, KeyPressMask | ButtonPressMask);
    XMapRaised(display, window);
    XSync(display, False);
    XSetInputFocus(display, window, RevertToParent, CurrentTime);
    XFlush(display);
    const auto started = monotonic_ms();
    while (!finish_child && monotonic_ms() - started < 17000) {
        for (unsigned count = 0; count < 32 && XPending(display); ++count) { XEvent input{}; XNextEvent(display, &input); }
        ::usleep(10000);
    }
    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return finish_child ? 0 : 70;
}
struct Owner {
    syspane::interfaces::EditorExitKeys keys;
    Child child;
    std::uint64_t started = monotonic_ms(), stopping = 0;
    bool killed = false;
    int outcome = 0;
    explicit Owner(bool maximized) : child(Child::launch_self({maximized ? "--child-maximized" : "--child",
        std::to_string(syspane::platform::current_process_id())})) { event("child", child.id()); }
    void stop(const char* reason) {
        if (stopping) return;
        stopping = monotonic_ms();
        event(reason, child.id());
        child.request_terminate();
    }
    bool tick() {
        if (const auto exited = child.wait()) {
            event(exited->signaled ? "child_signal" : "child_exit", exited->code);
            gtk_main_quit();
            return false;
        }
        const auto input = keys.poll();
        if (input == syspane::interfaces::EditorExitInput::requested) stop("keyboard_exit");
        if (input == syspane::interfaces::EditorExitInput::unavailable) { outcome = 69; stop("mapping_lost"); }
        const auto now = monotonic_ms();
        if (now - started >= 15000) { outcome = 70; stop("deadline"); }
        if (stopping && now - stopping >= 250 && !killed) { child.request_stop(); killed = true; event("force_stop", child.id()); }
        if (stopping && now - stopping >= 2250) { outcome = 70; event("unconfirmed"); gtk_main_quit(); return false; }
        return true;
    }
};
gboolean tick(gpointer data) {
    auto& owner = *static_cast<Owner*>(data);
    try { return owner.tick(); }
    catch (...) { owner.outcome = 70; gtk_main_quit(); return G_SOURCE_REMOVE; }
}
void clicked(GtkButton*, gpointer data) {
    auto& owner = *static_cast<Owner*>(data);
    try { owner.stop("native_exit"); }
    catch (...) { owner.outcome = 70; gtk_main_quit(); }
}
gboolean closed(GtkWidget*, GdkEvent*, gpointer data) { clicked(nullptr, data); return TRUE; }
}
int main(int argc, char** argv) {
    try {
        if (argc == 3 && (std::string(argv[1]) == "--child" || std::string(argv[1]) == "--child-maximized")) {
            const std::string value = argv[2];
            if (value.empty() || value.size() > 10 || value.find_first_not_of("0123456789") != std::string::npos) return 64;
            return editor(std::stoull(value), std::string(argv[1]) == "--child-maximized");
        }
        if (argc != 2 || (std::string(argv[1]) != "--owned-x11-lab" && std::string(argv[1]) != "--owned-gnome-lab")) return 64;
        if (!gtk_init_check(nullptr, nullptr)) return 69;
        Owner owner(std::string(argv[1]) == "--owned-gnome-lab");
        GtkWidget* window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
        gtk_window_set_title(GTK_WINDOW(window), "SysPane independent editor exit");
        gtk_window_set_decorated(GTK_WINDOW(window), FALSE);
        gtk_window_set_default_size(GTK_WINDOW(window), 280, 80);
        gtk_window_move(GTK_WINDOW(window), 500, 0);
        gtk_window_set_keep_above(GTK_WINDOW(window), TRUE);
        GtkWidget* button = gtk_button_new_with_label("Close editor (Ctrl+Alt+Escape)");
        gtk_container_add(GTK_CONTAINER(window), button);
        g_signal_connect(button, "clicked", G_CALLBACK(clicked), &owner);
        g_signal_connect(window, "delete-event", G_CALLBACK(closed), &owner);
        gtk_widget_show_all(window);
        const guint timer = g_timeout_add(20, tick, &owner);
        gtk_main();
        if (g_main_context_find_source_by_id(nullptr, timer)) g_source_remove(timer);
        gtk_widget_destroy(window);
        return owner.outcome;
    } catch (const std::exception& error) {
        // Fixed local codes only. Neither keymap contents nor native paths escape.
        const std::string code = error.what();
        std::cerr << (code == "editor.shortcut_unavailable" ? "editor.shortcut_unavailable" : "editor.unavailable") << '\n';
        return 69;
    }
}
