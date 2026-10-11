#pragma once
#include <gtk/gtk.h>
namespace syspane::interfaces {
// Internal GTK-thread factory. Every cell clears its cache before native retirement.
GtkCellRenderer* inspector_text_renderer();
}
