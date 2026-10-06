#pragma once
#include <glib-object.h>

G_BEGIN_DECLS
#define SYSPANE_TYPE_NETWORK_VIEW (syspane_network_view_get_type())
G_DECLARE_FINAL_TYPE(SysPaneNetworkView, syspane_network_view, SYSPANE, NETWORK_VIEW, GObject)
SysPaneNetworkView* syspane_network_view_new_from_socket(gint fd, guint expected_pid,
    const gchar* revision, gboolean permit, GError** error);
GBytes* syspane_network_view_hello(SysPaneNetworkView* self, GError** error);
gchar* syspane_network_view_feed(SysPaneNetworkView* self, GBytes* bytes, GError** error);
gchar* syspane_network_view_project(SysPaneNetworkView* self, GError** error);
gchar* syspane_network_view_policy(SysPaneNetworkView* self, const gchar* revision,
    gboolean permit, GError** error);
GBytes* syspane_network_view_shutdown(SysPaneNetworkView* self, GError** error);
void syspane_network_view_close(SysPaneNetworkView* self);
G_END_DECLS
