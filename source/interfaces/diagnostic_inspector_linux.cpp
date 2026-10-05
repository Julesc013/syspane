#ifndef _WIN32
#include "diagnostic_inspector.hpp"
#include <gtk/gtk.h>

namespace syspane::interfaces {
namespace {
struct View {
    GtkWidget *label, *window, *source, *destination, *preserve, *cancel, *status;
    const std::function<std::string()>* text;
    const PreservationControls* controls;
    int exit = 0;
};
gboolean refresh(gpointer data) {
    auto& view = *static_cast<View*>(data);
    try {
        gtk_label_set_text(GTK_LABEL(view.label), (*view.text)().c_str());
        const bool allowed = view.controls->permitted(), busy = view.controls->busy();
        if (!allowed) {
            view.controls->cancel();
            gtk_entry_set_text(GTK_ENTRY(view.source), ""); gtk_entry_set_text(GTK_ENTRY(view.destination), "");
        }
        for (const auto widget : {view.source, view.destination, view.preserve}) gtk_widget_set_sensitive(widget, allowed && !busy);
        gtk_widget_set_sensitive(view.cancel, busy);
        gtk_label_set_text(GTK_LABEL(view.status), allowed ? view.controls->status().c_str() : "Configuration preservation is restricted by policy.");
    }
    catch (...) { view.exit = 70; gtk_widget_destroy(view.window); return G_SOURCE_REMOVE; }
    return G_SOURCE_CONTINUE;
}
void preserve(GtkWidget*, gpointer data) {
    auto& view = *static_cast<View*>(data);
    try {
        if (view.controls->permitted() && !view.controls->busy()) view.controls->start(
            gtk_entry_get_text(GTK_ENTRY(view.source)), gtk_entry_get_text(GTK_ENTRY(view.destination)));
        refresh(data);
    } catch (...) { view.exit = 70; gtk_widget_destroy(view.window); }
}
void cancel(GtkWidget*, gpointer data) { static_cast<View*>(data)->controls->cancel(); }
void destroyed(GtkWidget*, gpointer data) { static_cast<View*>(data)->controls->cancel(); gtk_main_quit(); }
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
int diagnostic_inspector(const std::function<std::string()>& text, bool hidden, const PreservationControls& controls) {
    g_set_prgname("syspane-diag");
    if (!gtk_init_check(nullptr, nullptr)) return 69;
    auto window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "SysPane Diagnostic");
    gtk_window_set_default_size(GTK_WINDOW(window), 600, 460);
    gtk_container_set_border_width(GTK_CONTAINER(window), 16);
    auto box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 16);
    gtk_container_add(GTK_CONTAINER(window), box);
    auto label = gtk_label_new(nullptr);
    gtk_label_set_xalign(GTK_LABEL(label), 0);
    gtk_label_set_line_wrap(GTK_LABEL(label), TRUE);
    gtk_label_set_selectable(GTK_LABEL(label), FALSE);
    gtk_box_pack_start(GTK_BOX(box), label, TRUE, TRUE, 0);
    auto source = gtk_entry_new(), destination = gtk_entry_new();
    for (const auto& pair : {std::make_pair(source, "_Source file"), std::make_pair(destination, "_New copy")}) {
        auto caption = gtk_label_new_with_mnemonic(pair.second);
        gtk_label_set_mnemonic_widget(GTK_LABEL(caption), pair.first);
        gtk_label_set_xalign(GTK_LABEL(caption), 0);
        gtk_entry_set_max_length(GTK_ENTRY(pair.first), 4096);
        gtk_box_pack_start(GTK_BOX(box), caption, FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(box), pair.first, FALSE, FALSE, 0);
    }
    auto save = gtk_button_new_with_mnemonic("_Preserve copy"), stop = gtk_button_new_with_mnemonic("Cancel cop_y");
    auto status = gtk_label_new(nullptr);
    gtk_label_set_xalign(GTK_LABEL(status), 0); gtk_label_set_line_wrap(GTK_LABEL(status), TRUE);
    for (const auto widget : {save, stop, status}) gtk_box_pack_start(GTK_BOX(box), widget, FALSE, FALSE, 0);
    gtk_widget_set_name(source, "preserve-source"); gtk_widget_set_name(destination, "preserve-destination");
    gtk_widget_set_name(save, "preserve-start"); gtk_widget_set_name(stop, "preserve-cancel"); gtk_widget_set_name(status, "preserve-status");
    auto close = gtk_button_new_with_mnemonic("_Close");
    gtk_box_pack_end(GTK_BOX(box), close, FALSE, FALSE, 0);
    g_signal_connect_swapped(close, "clicked", G_CALLBACK(gtk_widget_destroy), window);
    g_signal_connect(window, "key-press-event", G_CALLBACK(key), nullptr);
    View view{label, window, source, destination, save, stop, status, &text, &controls, 0};
    g_signal_connect(save, "clicked", G_CALLBACK(preserve), &view);
    g_signal_connect(stop, "clicked", G_CALLBACK(cancel), &view);
    if (!refresh(&view)) return 70;
    g_signal_connect(window, "destroy", G_CALLBACK(destroyed), &view);
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
