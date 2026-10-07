from pathlib import Path
r=Path.cwd();p=r/'source/interfaces/settings_form_linux.cpp';s=p.read_text();start=s.index('// Distinct native accessible type:');end=s.index('namespace syspane::interfaces {',start)
part=s[start:end].replace('SpSettings','SpPrivate').replace('sp_settings','sp_private').replace('settings_editable_init','private_editable_init')
part=part.replace('typedef struct {GtkTextView parent;} SpPrivateText;','typedef struct {GtkTextView parent;guint limit;gboolean multiline;} SpPrivateText;')
part=part.replace('auto* view=GTK_TEXT_VIEW(self);','self->limit=256;self->multiline=FALSE;auto* view=GTK_TEXT_VIEW(self);')
part=part.replace('gchar* t,gint n,gpointer){','gchar* t,gint n,gpointer data){\n        const auto* options=static_cast<SpPrivateText*>(data);')
part=part.replace('n>1024','n>4096').replace('g_utf8_strlen(t,n)>256','g_utf8_strlen(t,n)>options->limit')
part=part.replace('find_first_of("\\r\\n\\t")','find_first_of(options->multiline?"\\r\\t":"\\r\\n\\t")').replace('by_name(b,"insert-text");}),nullptr);','by_name(b,"insert-text");}),self);')
part+='namespace syspane::interfaces {\nGtkWidget* private_text(unsigned limit,bool multiline){\n    if(!limit||limit>1024)throw std::invalid_argument("text.limit");\n    auto* value=static_cast<SpPrivateText*>(g_object_new(sp_private_text_get_type(),nullptr));value->limit=limit;value->multiline=multiline;\n    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(value),multiline?GTK_WRAP_WORD_CHAR:GTK_WRAP_NONE);return GTK_WIDGET(value);\n}\n}\n'
(r/'source/interfaces/private_text_linux.cpp').write_text('#include "private_text.hpp"\n#include <gtk/gtk.h>\n#include <gtk/gtk-a11y.h>\n#include <stdexcept>\n#include <string_view>\n'+part,encoding='utf-8',newline='\n')
s=s[:start]+s[end:];s=s.replace('#include "settings_form.hpp"','#include "settings_form.hpp"\n#include "private_text.hpp"').replace('GTK_WIDGET(g_object_new(sp_settings_text_get_type(),nullptr))','private_text()')
p.write_text(s,encoding='utf-8',newline='\n')
