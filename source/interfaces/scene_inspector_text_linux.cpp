#include "scene_inspector_text_linux.hpp"
#include <gtk/gtk-a11y.h>
#include <initializer_list>

namespace {
struct InspectorTextAccessible {GtkTextCellAccessible parent;};
struct InspectorTextAccessibleClass {GtkTextCellAccessibleClass parent;};
G_DEFINE_TYPE(InspectorTextAccessible,inspector_text_accessible,GTK_TYPE_TEXT_CELL_ACCESSIBLE)
bool cached_text_empty(GtkAccessible* accessible){
    auto* object=ATK_OBJECT(accessible);
    const auto* name=atk_object_get_name(object);
    // A null derived name also means the layout may not have been initialized.
    if(!name||name[0])return false;
    auto* text=ATK_TEXT(accessible);
    if(atk_text_get_character_count(text)!=0)return false;
    auto* value=atk_text_get_text(text,0,-1);
    const bool empty=value&&!value[0];g_free(value);
    if(!empty)return false;
    auto* api=ATK_TEXT_GET_IFACE(text);
    for(auto get:{api->get_text_before_offset,api->get_text_at_offset,api->get_text_after_offset}){
        if(!get)return false;
        gint start=0,end=0;
        value=get(text,0,ATK_TEXT_BOUNDARY_WORD_START,&start,&end);
        const bool word_empty=value&&!value[0];g_free(value);
        if(!word_empty)return false;
    }
    return true;
}
void clear_before_unset(GtkAccessible* accessible){
    if(!cached_text_empty(accessible)){
        GtkCellRenderer* renderer=nullptr;g_object_get(accessible,"renderer",&renderer,nullptr);
        if(renderer){
            gchar* previous=nullptr;g_object_get(renderer,"text",&previous,nullptr);
            g_object_set(renderer,"text","",nullptr);
            auto* cache=GTK_CELL_ACCESSIBLE_CLASS(inspector_text_accessible_parent_class);
            cache->update_cache(GTK_CELL_ACCESSIBLE(accessible),FALSE);
            g_object_set(renderer,"text",previous,nullptr);g_free(previous);g_object_unref(renderer);
        }
    }
    GTK_ACCESSIBLE_CLASS(inspector_text_accessible_parent_class)->widget_unset(accessible);
}
void inspector_text_accessible_class_init(InspectorTextAccessibleClass* type){GTK_ACCESSIBLE_CLASS(type)->widget_unset=clear_before_unset;}
void inspector_text_accessible_init(InspectorTextAccessible*){}
struct InspectorTextRenderer {GtkCellRendererText parent;};
struct InspectorTextRendererClass {GtkCellRendererTextClass parent;};
G_DEFINE_TYPE(InspectorTextRenderer,inspector_text_renderer,GTK_TYPE_CELL_RENDERER_TEXT)
void inspector_text_renderer_class_init(InspectorTextRendererClass* type){gtk_cell_renderer_class_set_accessible_type(GTK_CELL_RENDERER_CLASS(type),inspector_text_accessible_get_type());}
void inspector_text_renderer_init(InspectorTextRenderer*){}
}
namespace syspane::interfaces {
GtkCellRenderer* inspector_text_renderer(){return GTK_CELL_RENDERER(g_object_new(inspector_text_renderer_get_type(),nullptr));}
}
