#pragma once
#include <glib-object.h>

G_BEGIN_DECLS
#define SYSPANE_TYPE_HEALTH_VIEW (syspane_health_view_get_type())
G_DECLARE_FINAL_TYPE(SysPaneHealthView, syspane_health_view, SYSPANE, HEALTH_VIEW, GObject)
SysPaneHealthView* syspane_health_view_new_from_socket(gint fd, guint expected_pid, GError** error);
GBytes* syspane_health_view_hello(SysPaneHealthView* self, GError** error);
gchar* syspane_health_view_feed(SysPaneHealthView* self, GBytes* bytes, GError** error);
GBytes* syspane_health_view_heartbeat(SysPaneHealthView* self, const gchar* sequence, GError** error);
GBytes* syspane_health_view_progress(SysPaneHealthView* self, const gchar* generation, GError** error);
GBytes* syspane_health_view_shutdown(SysPaneHealthView* self, GError** error);
gboolean syspane_health_view_tick(SysPaneHealthView* self, GError** error);
void syspane_health_view_close(SysPaneHealthView* self);
G_END_DECLS
