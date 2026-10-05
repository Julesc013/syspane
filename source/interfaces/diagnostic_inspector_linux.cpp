#ifndef _WIN32
#include "diagnostic_inspector.hpp"
#include <gtk/gtk.h>

namespace syspane::interfaces {
namespace {
struct View { GtkWidget* label; GtkWidget* window; const std::function<std::string()>* text; int exit = 0; };
gboolean refresh(gpointer data) {
    auto& view = *static_cast<View*>(data);
    try { gtk_label_set_text(GTK_LABEL(view.label), (*view.text)().c_str()); }
    catch (...) { view.exit = 70; gtk_widget_destroy(view.window); return G_SOURCE_REMOVE; }
    return G_SOURCE_CONTINUE;
}
gboolean timeout(gpointer data) {
    auto& view = *static_cast<View*>(data);
    view.exit = 70;
    gtk_widget_destroy(view.window);
    return G_SOURCE_REMOVE;
}
gboolean key(GtkWidget* widget, GdkEventKey* event, gpointer) {
    if (event->keyval != GDK_KEY_Escape) return FALSE;
    gtk_widget_destroy(widget);
    return TRUE;
}
}
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden) {
    g_set_prgname("syspane-diag");
    if (!gtk_init_check(nullptr, nullptr)) return 69;
    auto window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "SysPane Diagnostic");
    gtk_window_set_default_size(GTK_WINDOW(window), 540, 240);
    gtk_container_set_border_width(GTK_CONTAINER(window), 16);
    auto box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 16);
    gtk_container_add(GTK_CONTAINER(window), box);
    auto label = gtk_label_new(nullptr);
    gtk_label_set_xalign(GTK_LABEL(label), 0);
    gtk_label_set_line_wrap(GTK_LABEL(label), TRUE);
    gtk_label_set_selectable(GTK_LABEL(label), FALSE);
    gtk_box_pack_start(GTK_BOX(box), label, TRUE, TRUE, 0);
    auto close = gtk_button_new_with_mnemonic("_Close");
    gtk_box_pack_end(GTK_BOX(box), close, FALSE, FALSE, 0);
    g_signal_connect_swapped(close, "clicked", G_CALLBACK(gtk_widget_destroy), window);
    g_signal_connect(window, "key-press-event", G_CALLBACK(key), nullptr);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), nullptr);
    View view{label, window, &text, 0};
    try { gtk_label_set_text(GTK_LABEL(label), text().c_str()); }
    catch (...) { gtk_widget_destroy(window); return 70; }
    gtk_widget_show_all(box);
    // Realize supplies a native owned window for external close tests, without mapping it.
    if (hidden) gtk_widget_realize(window); else gtk_widget_show(window);
    const auto poll = g_timeout_add(1000, refresh, &view);
    const auto limit = hidden ? g_timeout_add(20000, timeout, &view) : 0;
    gtk_main();
    if (g_main_context_find_source_by_id(nullptr, poll)) g_source_remove(poll);
    if (limit && g_main_context_find_source_by_id(nullptr, limit)) g_source_remove(limit);
    return view.exit;
}
}
#endif
