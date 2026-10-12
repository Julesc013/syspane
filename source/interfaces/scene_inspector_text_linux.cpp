#include "scene_inspector_text_linux.hpp"
#include <gtk/gtk-a11y.h>
#include <initializer_list>
#include <array>
#include <deque>
#include <thread>
#include <stdexcept>
#include <algorithm>

namespace syspane::interfaces {
struct InspectorRetirement::Impl {
    struct Operation {
        GObject* object=nullptr;AtkObject* parent=nullptr;guint count=0;
        std::array<GParamSpec*,8> properties{};
        void(*unset)(GtkAccessible*)=nullptr;void(*dispatch)(GObject*,guint,GParamSpec**)=nullptr;
        void release()noexcept{for(guint i=0;i<count;++i)g_param_spec_unref(properties[i]);if(parent)g_object_unref(parent);if(object)g_object_unref(object);}
        void invoke(){if(unset)unset(GTK_ACCESSIBLE(object));else dispatch(object,count,properties.data());}
    };
    static_assert(sizeof(Operation)<=128,"bounded native operation storage");
    std::thread::id thread=std::this_thread::get_id();std::deque<Operation> queue;State status;
    bool add(GObject* object,guint count,GParamSpec** properties,void(*unset)(GtkAccessible*),void(*dispatch)(GObject*,guint,GParamSpec**))noexcept{
        if(thread!=std::this_thread::get_id()||queue.size()>=262144||count>8){status.failed=true;return false;}
        Operation task;task.object=G_OBJECT(g_object_ref(object));auto* parent=atk_object_get_parent(ATK_OBJECT(object));if(parent)task.parent=ATK_OBJECT(g_object_ref(parent));
        task.count=count;task.unset=unset;task.dispatch=dispatch;for(guint i=0;i<count;++i)task.properties[i]=g_param_spec_ref(properties[i]);
        try{queue.push_back(task);++status.accepted;return true;}catch(...){task.release();status.failed=true;return false;}
    }
    void owner()const{if(thread!=std::this_thread::get_id())throw std::logic_error("inspector.retirement_owner");}
};
InspectorRetirement::InspectorRetirement():impl_(std::make_unique<Impl>()){}
InspectorRetirement::~InspectorRetirement(){finish();}
bool InspectorRetirement::unset(GtkAccessible* object,void(*operation)(GtkAccessible*))noexcept{return impl_->add(G_OBJECT(object),0,nullptr,operation,nullptr);}
bool InspectorRetirement::dispatch(GObject* object,guint count,GParamSpec** properties,void(*operation)(GObject*,guint,GParamSpec**))noexcept{return impl_->add(object,count,properties,nullptr,operation);}
void InspectorRetirement::poll(){auto& i=*impl_;i.owner();if(i.queue.empty())return;const auto begin=g_get_monotonic_time();unsigned count=0;
    do{auto task=i.queue.front();i.queue.pop_front();task.invoke();task.release();++i.status.delivered;++count;}while(!i.queue.empty()&&count<256&&g_get_monotonic_time()-begin<5000);
    const auto elapsed=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);++i.status.polls;i.status.total_us+=elapsed;i.status.max_us=std::max(i.status.max_us,elapsed);
}
void InspectorRetirement::finish(){while(!impl_->queue.empty())poll();}
InspectorRetirement::State InspectorRetirement::state()const{impl_->owner();auto result=impl_->status;result.pending=impl_->queue.size();return result;}
}

namespace {
constexpr auto retirement_key="syspane.inspector.retirement";
std::shared_ptr<syspane::interfaces::InspectorRetirement> retirement(GtkAccessible* accessible){
    GtkCellRenderer* renderer=nullptr;g_object_get(accessible,"renderer",&renderer,nullptr);if(!renderer)return {};
    auto* stored=static_cast<std::shared_ptr<syspane::interfaces::InspectorRetirement>*>(g_object_get_data(G_OBJECT(renderer),retirement_key));
    auto result=stored?*stored:std::shared_ptr<syspane::interfaces::InspectorRetirement>{};g_object_unref(renderer);return result;
}
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
    auto* parent=GTK_ACCESSIBLE_CLASS(inspector_text_accessible_parent_class);auto owner=retirement(accessible);
    if(!owner||!owner->unset(accessible,parent->widget_unset))parent->widget_unset(accessible);
}
void dispatch_properties(GObject* object,guint count,GParamSpec** properties){
    auto* parent=G_OBJECT_CLASS(inspector_text_accessible_parent_class);
    bool widget=false;for(guint i=0;i<count;++i)widget=widget||g_str_equal(g_param_spec_get_name(properties[i]),"widget");
    if(widget&&!gtk_accessible_get_widget(GTK_ACCESSIBLE(object))){auto owner=retirement(GTK_ACCESSIBLE(object));if(owner&&owner->dispatch(object,count,properties,parent->dispatch_properties_changed))return;}
    parent->dispatch_properties_changed(object,count,properties);
}
void inspector_text_accessible_class_init(InspectorTextAccessibleClass* type){GTK_ACCESSIBLE_CLASS(type)->widget_unset=clear_before_unset;G_OBJECT_CLASS(type)->dispatch_properties_changed=dispatch_properties;}
void inspector_text_accessible_init(InspectorTextAccessible*){}
struct InspectorTextRenderer {GtkCellRendererText parent;};
struct InspectorTextRendererClass {GtkCellRendererTextClass parent;};
G_DEFINE_TYPE(InspectorTextRenderer,inspector_text_renderer,GTK_TYPE_CELL_RENDERER_TEXT)
void inspector_text_renderer_class_init(InspectorTextRendererClass* type){gtk_cell_renderer_class_set_accessible_type(GTK_CELL_RENDERER_CLASS(type),inspector_text_accessible_get_type());}
void inspector_text_renderer_init(InspectorTextRenderer*){}
}
namespace syspane::interfaces {
GtkCellRenderer* inspector_text_renderer(const std::shared_ptr<InspectorRetirement>& owner){auto* renderer=GTK_CELL_RENDERER(g_object_new(inspector_text_renderer_get_type(),nullptr));
    if(owner)g_object_set_data_full(G_OBJECT(renderer),retirement_key,new std::shared_ptr<InspectorRetirement>(owner),+[](gpointer data){delete static_cast<std::shared_ptr<InspectorRetirement>*>(data);});
    return renderer;
}
}
