#pragma once
#include <glib-object.h>

G_BEGIN_DECLS
#define SYSPANE_TYPE_CLOCK (syspane_clock_get_type())
G_DECLARE_FINAL_TYPE(SysPaneClock, syspane_clock, SYSPANE, CLOCK, GObject)
SysPaneClock* syspane_clock_new_from_socket(gint fd, guint expected_pid, GError** error);
gchar* syspane_clock_sample(SysPaneClock* self, GError** error);
void syspane_clock_close(SysPaneClock* self);
G_END_DECLS
