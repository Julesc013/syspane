#pragma once
typedef struct _GtkWidget GtkWidget;
namespace syspane::interfaces {
// Bounded plain text without implicit PRIMARY/CLIPBOARD/drag/AT-SPI copy export.
GtkWidget* private_text(unsigned characters=256,bool multiline=false);
}
