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
static void sp_private_text_class_init(SpPrivateTextClass* cls){
    gtk_widget_class_set_accessible_type(GTK_WIDGET_CLASS(cls),sp_private_accessible_get_type());
    auto* text=GTK_TEXT_VIEW_CLASS(cls);text->copy_clipboard=+[](GtkTextView*){};text->cut_clipboard=+[](GtkTextView*){};
    GTK_WIDGET_CLASS(cls)->drag_data_get=+[](GtkWidget*,GdkDragContext*,GtkSelectionData*,guint,guint){};
}
static void sp_private_text_init(SpPrivateText* self){
    self->limit=256;self->multiline=FALSE;auto* view=GTK_TEXT_VIEW(self);gtk_text_view_set_accepts_tab(view,FALSE);gtk_text_view_set_wrap_mode(view,GTK_WRAP_NONE);
    auto* buffer=gtk_text_view_get_buffer(view);
    g_signal_connect_after(self,"realize",G_CALLBACK(+[](GtkWidget* w,gpointer){gtk_text_buffer_remove_selection_clipboard(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),gtk_widget_get_clipboard(w,GDK_SELECTION_PRIMARY));}),nullptr);
    g_signal_connect_object(buffer,"insert-text",G_CALLBACK(+[](GtkTextBuffer* b,GtkTextIter*,gchar* t,gint n,gpointer data){
        const auto* options=static_cast<SpPrivateText*>(data);
        if(n<0||n>4096||!g_utf8_validate(t,n,nullptr)||gtk_text_buffer_get_char_count(b)+g_utf8_strlen(t,n)>options->limit||
           std::string_view(t,static_cast<std::size_t>(n)).find_first_of(options->multiline?"\r\t":"\r\n\t")!=std::string_view::npos)
            g_signal_stop_emission_by_name(b,"insert-text");}),self,static_cast<GConnectFlags>(0));
}

namespace syspane::interfaces {
GtkWidget* private_text(unsigned limit,bool multiline){
    if(!limit||limit>1024)throw std::invalid_argument("text.limit");
    auto* value=static_cast<SpPrivateText*>(g_object_new(sp_private_text_get_type(),nullptr));value->limit=limit;value->multiline=multiline;
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(value),multiline?GTK_WRAP_WORD_CHAR:GTK_WRAP_NONE);return GTK_WIDGET(value);
}
}
