#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <gtk/gtk.h>
#include <dlfcn.h>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>

// Owned laboratory only. Observe both real GTK focus and its exported ATK state;
// add bounded paint work and optionally restore the old refresh priority.
namespace {
FILE* trace=nullptr;
gint64 start=0,pending=0;
guint paints=0;
bool target=false,slow=false;
thread_local bool own_state_read=false;
int refresh_priority=0;
const char* description(GtkWidget* w){if(!w)return "none";const auto* s=atk_object_get_description(gtk_widget_get_accessible(w));return s?s:G_OBJECT_TYPE_NAME(w);}
void emit(const char* kind,GtkWidget* w){
    if(!trace)return;
    gboolean focused=FALSE;
    if(w){own_state_read=true;auto* states=atk_object_ref_state_set(gtk_widget_get_accessible(w));own_state_read=false;focused=atk_state_set_contains_state(states,ATK_STATE_FOCUSED);g_object_unref(states);}
    std::fprintf(trace,"%s\t%lld\t%s\t%d\t%d\t%lld\t%u\t%d\n",kind,static_cast<long long>(g_get_monotonic_time()-start),description(w),w?gtk_widget_has_focus(w):0,focused,static_cast<long long>(pending?g_get_monotonic_time()-pending:0),paints,refresh_priority);std::fflush(trace);
}
gboolean idle(gpointer){emit("idle",nullptr);pending=0;return G_SOURCE_REMOVE;}
gboolean sample(gpointer){
    auto* rows=gtk_window_list_toplevels();
    for(auto* row=rows;row;row=row->next){auto* w=GTK_WINDOW(row->data);if(g_strcmp0(gtk_window_get_title(w),"SysPane Editor")==0)emit("sample",gtk_window_get_focus(w));}
    g_list_free(rows);if(!pending){pending=g_get_monotonic_time();g_idle_add_full(G_PRIORITY_DEFAULT_IDLE,idle,nullptr,nullptr);}return G_SOURCE_CONTINUE;
}
gboolean focus_hook(GSignalInvocationHint*,guint,const GValue* values,gpointer){
    auto* w=GTK_WIDGET(g_value_get_object(values));
    if(g_strcmp0(description(w),"editor.apply")==0||g_strcmp0(description(w),"editor.undo")==0){emit("focus-in",w);slow=true;}return TRUE;
}
gboolean draw_hook(GSignalInvocationHint*,guint,const GValue* values,gpointer){
    auto* w=GTK_WIDGET(g_value_get_object(values));
    if(g_strcmp0(description(w),"editor.canvas")==0){++paints;if(slow){emit("slow-paint",w);g_usleep(60000);}}return TRUE;
}
using Full=guint(*)(gint,guint,GSourceFunc,gpointer,GDestroyNotify);
Full full(){return reinterpret_cast<Full>(dlsym(RTLD_NEXT,"g_timeout_add_full"));}
bool editor_refresh(guint interval,void* caller){Dl_info info{};return target&&interval==40&&dladdr(caller,&info)&&g_str_has_suffix(info.dli_fname,"/syspane_editor_window");}
guint refresh(gint priority,guint interval,GSourceFunc function,gpointer data,GDestroyNotify notify){
    refresh_priority=std::getenv("SYSPANE_REFRESH_LEGACY")?G_PRIORITY_DEFAULT:priority;emit("refresh",nullptr);
    return full()(refresh_priority,interval,function,data,notify);
}
}
extern "C" AtkStateSet* atk_object_ref_state_set(AtkObject* object){
    using States=AtkStateSet*(*)(AtkObject*);auto* states=reinterpret_cast<States>(dlsym(RTLD_NEXT,"atk_object_ref_state_set"))(object);
    if(trace&&!own_state_read&&GTK_IS_ACCESSIBLE(object)){
        auto* w=gtk_accessible_get_widget(GTK_ACCESSIBLE(object));
        if(w){const auto* id=description(w);if(g_strcmp0(id,"editor.undo")==0||g_strcmp0(id,"editor.redo")==0||g_strcmp0(id,"editor.apply")==0){
            std::fprintf(trace,"focus-state\t%lld\t%s\t%d\t%d\t%lld\t%u\t%d\n",static_cast<long long>(g_get_monotonic_time()-start),id,gtk_widget_has_focus(w),atk_state_set_contains_state(states,ATK_STATE_FOCUSED),static_cast<long long>(pending?g_get_monotonic_time()-pending:0),paints,refresh_priority);std::fflush(trace);
        }}
    }return states;
}
extern "C" gboolean gtk_init_check(int* argc,char*** argv){
    using Init=gboolean(*)(int*,char***);const auto ok=reinterpret_cast<Init>(dlsym(RTLD_NEXT,"gtk_init_check"))(argc,argv);
    char exe[4096];const auto count=readlink("/proc/self/exe",exe,sizeof(exe)-1);if(count<=0)return ok;exe[count]=0;
    target=ok&&g_str_has_suffix(exe,"/syspane_editor_window");const auto* prefix=std::getenv("SYSPANE_REFRESH_TRACE");
    if(target&&prefix){
        char path[8192];std::snprintf(path,sizeof(path),"%s-%ld.tsv",prefix,static_cast<long>(getpid()));trace=std::fopen(path,"wx");if(!trace)std::abort();start=g_get_monotonic_time();
        g_signal_add_emission_hook(g_signal_lookup("focus-in-event",GTK_TYPE_WIDGET),0,focus_hook,nullptr,nullptr);
        g_signal_add_emission_hook(g_signal_lookup("draw",GTK_TYPE_WIDGET),0,draw_hook,nullptr,nullptr);
        full()(G_PRIORITY_DEFAULT,50,sample,nullptr,nullptr);emit("start",nullptr);
    }return ok;
}
extern "C" guint g_timeout_add(guint interval,GSourceFunc function,gpointer data){
    if(editor_refresh(interval,__builtin_return_address(0)))return refresh(G_PRIORITY_DEFAULT,interval,function,data,nullptr);
    using Timer=guint(*)(guint,GSourceFunc,gpointer);return reinterpret_cast<Timer>(dlsym(RTLD_NEXT,"g_timeout_add"))(interval,function,data);
}
extern "C" guint g_timeout_add_full(gint priority,guint interval,GSourceFunc function,gpointer data,GDestroyNotify notify){
    if(editor_refresh(interval,__builtin_return_address(0)))return refresh(priority,interval,function,data,notify);
    return full()(priority,interval,function,data,notify);
}
