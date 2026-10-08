#pragma once
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
// Bounded plain text without implicit PRIMARY/CLIPBOARD/drag/AT-SPI copy export.
// Owns one buffer for its entire lifetime. Edit its contents; do not replace or
// share the buffer, or change its clipboard registrations outside this control.
GtkWidget* private_text(unsigned characters=256,bool multiline=false);
}
