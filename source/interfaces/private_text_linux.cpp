#include "private_text.hpp"
#include <gtk/gtk.h>
#include <gtk/gtk-a11y.h>
#include <stdexcept>
#include <string_view>
// Distinct native accessible type: reading/editing remains standard; this component
// has no clipboard export owner, including AT-SPI EditableText copy/cut entry points.
typedef struct {GtkTextViewAccessible parent;} SpPrivateAccessible;
typedef struct {GtkTextViewAccessibleClass parent;} SpPrivateAccessibleClass;
static void private_editable_init(AtkEditableTextIface* iface){
    iface->copy_text=+[](AtkEditableText*,gint,gint){};
    iface->cut_text=+[](AtkEditableText*,gint,gint){};
}
G_DEFINE_TYPE_WITH_CODE(SpPrivateAccessible,sp_private_accessible,GTK_TYPE_TEXT_VIEW_ACCESSIBLE,
    G_IMPLEMENT_INTERFACE(ATK_TYPE_EDITABLE_TEXT,private_editable_init))
static void sp_private_accessible_init(SpPrivateAccessible*){}
static void sp_private_accessible_class_init(SpPrivateAccessibleClass*){}
typedef struct {GtkTextView parent;guint limit;gboolean multiline;} SpPrivateText;
typedef struct {GtkTextViewClass parent;} SpPrivateTextClass;
G_DEFINE_TYPE(SpPrivateText,sp_private_text,GTK_TYPE_TEXT_VIEW)
static void private_realize(GtkWidget* widget){
    GTK_WIDGET_CLASS(sp_private_text_parent_class)->realize(widget);
    gtk_text_buffer_remove_selection_clipboard(gtk_text_view_get_buffer(GTK_TEXT_VIEW(widget)),
        gtk_widget_get_clipboard(widget,GDK_SELECTION_PRIMARY));
}
static void private_unrealize(GtkWidget* widget){
    // Restore only GTK's bookkeeping reference. Adding it does not publish the
    // selection. The parent's first buffer action removes it synchronously;
    // there is no event dispatch or buffer mutation in this handoff.
    gtk_text_buffer_add_selection_clipboard(gtk_text_view_get_buffer(GTK_TEXT_VIEW(widget)),
        gtk_widget_get_clipboard(widget,GDK_SELECTION_PRIMARY));
    GTK_WIDGET_CLASS(sp_private_text_parent_class)->unrealize(widget);
}
static void private_destroy(GtkWidget* widget){
    // GtkTextView destruction replaces its buffer. Finish the balanced native
    // unrealize first so buffer removal cannot consume the reference again.
    if(gtk_widget_get_realized(widget))gtk_widget_unrealize(widget);
    GTK_WIDGET_CLASS(sp_private_text_parent_class)->destroy(widget);
}
static void sp_private_text_class_init(SpPrivateTextClass* cls){
    gtk_widget_class_set_accessible_type(GTK_WIDGET_CLASS(cls),sp_private_accessible_get_type());
    auto* widget=GTK_WIDGET_CLASS(cls);widget->realize=private_realize;widget->unrealize=private_unrealize;widget->destroy=private_destroy;
    auto* text=GTK_TEXT_VIEW_CLASS(cls);text->copy_clipboard=+[](GtkTextView*){};text->cut_clipboard=+[](GtkTextView*){};
    GTK_WIDGET_CLASS(cls)->drag_data_get=+[](GtkWidget*,GdkDragContext*,GtkSelectionData*,guint,guint){};
}
static void sp_private_text_init(SpPrivateText* self){
    self->limit=256;self->multiline=FALSE;auto* view=GTK_TEXT_VIEW(self);gtk_text_view_set_accepts_tab(view,FALSE);gtk_text_view_set_wrap_mode(view,GTK_WRAP_NONE);
    auto* buffer=gtk_text_view_get_buffer(view);
    g_signal_connect_object(buffer,"insert-text",G_CALLBACK(+[](GtkTextBuffer* b,GtkTextIter*,gchar* t,gint n,gpointer data){
        const auto* options=static_cast<SpPrivateText*>(data);
        if(n<0||n>4096||!g_utf8_validate(t,n,nullptr)||gtk_text_buffer_get_char_count(b)+g_utf8_strlen(t,n)>options->limit||
           std::string_view(t,static_cast<std::size_t>(n)).find_first_of(options->multiline?"\r\t":"\r\n\t")!=std::string_view::npos)
            g_signal_stop_emission_by_name(b,"insert-text");}),self,static_cast<GConnectFlags>(0));
}

namespace syspane::interfaces {
GtkWidget* private_text(unsigned limit,bool multiline){
    if(!limit||limit>4096)throw std::invalid_argument("text.limit");
    auto* value=static_cast<SpPrivateText*>(g_object_new(sp_private_text_get_type(),nullptr));value->limit=limit;value->multiline=multiline;
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(value),multiline?GTK_WRAP_WORD_CHAR:GTK_WRAP_NONE);return GTK_WIDGET(value);
}
}
