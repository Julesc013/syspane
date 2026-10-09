#include "frontend_linux.hpp"
#include "settings_form.hpp"
#include "editor_form.hpp"
#include "editor_recovery_session.hpp"
#include <gtk/gtk.h>
#include <algorithm>
#include <cstdlib>
#include <iostream>

namespace syspane::application {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
void accessible(GtkWidget* widget,const char* description){atk_object_set_description(gtk_widget_get_accessible(widget),description);}
struct Window {
    LinuxFrontendBackend& backend;GtkWidget *window=nullptr,*box=nullptr,*forms=nullptr,*status=nullptr,*retry=nullptr,*quit=nullptr,*settings_button=nullptr,*editor_button=nullptr,*recovery_notice=nullptr;
    std::unique_ptr<interfaces::SettingsForm> form;std::unique_ptr<interfaces::EditorForm> editor;
    std::vector<GdkMonitor*> monitors;GdkDisplay* display=nullptr;bool topology_dirty=true;
    std::uint64_t shown=0,withdrawal=0;bool erased=false,closing=false,editor_mode=false,transition=false,exit_requested=false,editor_unavailable=false;int result=0;
    bool experimental_recovery=false,recovery_enabled=false;std::optional<std::uint64_t> retirement_serial;
    std::string saved_notice;
    FrontendTimingObserver timing;gint64 previous_tick=0;
    scene::Topology topology(){
        scene::Topology out;const auto count=gdk_display_get_n_monitors(display);need(count>0&&count<=16,"frontend.topology");
        auto* primary=gdk_display_get_primary_monitor(display);if(!primary)primary=gdk_display_get_monitor(display,0);
        for(int n=0;n<count;++n){
            auto* monitor=gdk_display_get_monitor(display,n);auto at=std::find(monitors.begin(),monitors.end(),monitor);
            if(at==monitors.end()){
                need(monitors.size()<64,"frontend.topology_capacity");g_object_ref(monitor);monitors.push_back(monitor);at=monitors.end()-1;
                g_signal_connect(monitor,"notify",G_CALLBACK(+[](GObject*,GParamSpec*,gpointer p){static_cast<Window*>(p)->topology_dirty=true;}),this);
            }
            GdkRectangle bounds{},work{};gdk_monitor_get_geometry(monitor,&bounds);gdk_monitor_get_workarea(monitor,&work);
            const auto scale=gdk_monitor_get_scale_factor(monitor);need(scale>=1&&scale<=8,"frontend.topology");
            const auto valid=[](const GdkRectangle& r){return r.x>=-100000&&r.x<=100000&&r.y>=-100000&&r.y<=100000&&r.width>0&&r.width<=32768&&r.height>0&&r.height<=32768;};
            need(valid(bounds)&&valid(work)&&work.x>=bounds.x&&work.y>=bounds.y&&
                 static_cast<scene::Unit>(work.x)+work.width<=static_cast<scene::Unit>(bounds.x)+bounds.width&&
                 static_cast<scene::Unit>(work.y)+work.height<=static_cast<scene::Unit>(bounds.y)+bounds.height,"frontend.topology");
            scene::Display d;d.id="display:session:"+std::to_string(at-monitors.begin()+1);
            const auto rect=[](const GdkRectangle& r){return scene::Rect{static_cast<scene::Unit>(r.x)*scene::dip,static_cast<scene::Unit>(r.y)*scene::dip,static_cast<scene::Unit>(r.width)*scene::dip,static_cast<scene::Unit>(r.height)*scene::dip};};
            d.bounds=rect(bounds);d.work=rect(work);d.scale_numerator=static_cast<unsigned>(scale);d.pixel_x=static_cast<scene::Unit>(bounds.x)*scale;d.pixel_y=static_cast<scene::Unit>(bounds.y)*scale;
            if(monitor==primary){out.fallback=d.id;out.roles["primary"]={d.id};}out.displays.push_back(std::move(d));
        }
        need(!out.fallback.empty(),"frontend.topology");topology_dirty=false;return out;
    }
    explicit Window(LinuxFrontendBackend& value,bool recover,FrontendTimingObserver observer):backend(value),experimental_recovery(recover),timing(std::move(observer)){
        display=gdk_display_get_default();need(display!=nullptr,"frontend.display");
        for(const char* event:{"monitor-added","monitor-removed"})g_signal_connect(display,event,G_CALLBACK(+[](GdkDisplay*,GdkMonitor*,gpointer p){static_cast<Window*>(p)->topology_dirty=true;}),this);
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Settings");
        GdkRectangle area{0,0,800,600};auto* monitor=gdk_display_get_primary_monitor(display);
        if(!monitor&&gdk_display_get_n_monitors(display)>0)monitor=gdk_display_get_monitor(display,0);
        if(monitor)gdk_monitor_get_workarea(monitor,&area);
        gtk_window_set_default_size(GTK_WINDOW(window),std::min(1000,std::max(1,area.width)),std::min(720,std::max(1,area.height)));
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);gtk_container_set_border_width(GTK_CONTAINER(box),12);gtk_container_add(GTK_CONTAINER(window),box);
        auto* navigation=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);gtk_box_pack_start(GTK_BOX(box),navigation,FALSE,FALSE,0);
        settings_button=gtk_button_new_with_label("Settings");accessible(settings_button,"frontend.settings");gtk_box_pack_start(GTK_BOX(navigation),settings_button,FALSE,FALSE,0);
        editor_button=gtk_button_new_with_label("Edit scene");accessible(editor_button,"frontend.editor");gtk_box_pack_start(GTK_BOX(navigation),editor_button,FALSE,FALSE,0);
        g_signal_connect(settings_button,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);try{s.select(false);}catch(...){s.stop();}}),this);
        g_signal_connect(editor_button,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);try{s.select(true);}catch(...){s.stop();}}),this);
        recovery_notice=gtk_label_new("Draft recovery unavailable. Apply saves the configuration.");accessible(recovery_notice,"frontend.recovery");gtk_label_set_xalign(GTK_LABEL(recovery_notice),0);gtk_box_pack_start(GTK_BOX(box),recovery_notice,FALSE,FALSE,0);
        gtk_widget_set_no_show_all(recovery_notice,TRUE);
        status=gtk_label_new("Starting configuration service.");gtk_label_set_xalign(GTK_LABEL(status),0);gtk_label_set_line_wrap(GTK_LABEL(status),TRUE);accessible(status,"frontend.status");gtk_box_pack_start(GTK_BOX(box),status,FALSE,FALSE,0);
        gtk_label_set_max_width_chars(GTK_LABEL(status),72);
        auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scroll),GTK_POLICY_AUTOMATIC,GTK_POLICY_AUTOMATIC);
        gtk_box_pack_start(GTK_BOX(box),scroll,TRUE,TRUE,0);forms=gtk_box_new(GTK_ORIENTATION_VERTICAL,0);gtk_container_add(GTK_CONTAINER(scroll),forms);
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);gtk_box_pack_end(GTK_BOX(box),actions,FALSE,FALSE,0);
        retry=gtk_button_new_with_label("Reconnect");accessible(retry,"frontend.retrieve");gtk_box_pack_start(GTK_BOX(actions),retry,FALSE,FALSE,0);
        quit=gtk_button_new_with_label("Quit");accessible(quit,"frontend.quit");gtk_box_pack_end(GTK_BOX(actions),quit,FALSE,FALSE,0);
        g_signal_connect(retry,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);try{s.backend.retrieve();}catch(...){s.stop();}}),this);
        g_signal_connect(quit,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Window*>(p)->stop();}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{static_cast<Window*>(p)->stop();return TRUE;}),this);
        gtk_widget_set_sensitive(settings_button,FALSE);gtk_widget_set_sensitive(editor_button,FALSE);gtk_widget_show_all(window);
    }
    bool can_leave()const{return editor?editor->can_leave():editor_unavailable||(form&&form->can_leave());}
    void close_forms(){if(form)form->close();if(editor)editor->close();}
    void select(bool next){
        if(closing||transition||next==editor_mode||!can_leave())return;
        saved_notice.clear();retirement_serial.reset();backend.reload();close_forms();editor_mode=next;transition=true;
        gtk_widget_set_sensitive(settings_button,FALSE);gtk_widget_set_sensitive(editor_button,FALSE);
    }
    void stop()noexcept{
        if(closing)return;
        closing=true;
        try{close_forms();backend.close();}catch(...){result=2;}
        for(auto* button:{retry,quit,settings_button,editor_button})gtk_widget_set_sensitive(button,FALSE);
        gtk_label_set_text(GTK_LABEL(status),"Closing; waiting for configuration service to stop. Closing cannot undo a submitted change.");
    }
    void populate(const FrontendProfile& snapshot){
        const configuration::Authority authority{true,"console",{"console"}};
        editor_unavailable=false;retirement_serial.reset();recovery_enabled=editor_mode&&experimental_recovery&&snapshot.view.recovery.has_value();
        if(editor_mode){
            scene::Topology current;
            try{current=topology();}
            catch(const protocol::Error&){editor_unavailable=true;topology_dirty=false;shown=snapshot.serial;erased=false;transition=false;gtk_widget_hide(recovery_notice);return;}
            const auto selected=current.fallback;interfaces::EditorForm::Actions actions;
            actions.request_id=[this]{return backend.request_id();};actions.widget_id=actions.request_id;
            actions.submit=[this](const auto& request){backend.submit(request);};actions.cancel=[this](const auto& request){backend.cancel(request);};
            actions.submit_recovery=[this](const auto& request,auto digest){saved_notice.clear();retirement_serial.reset();backend.submit(request,std::move(digest));};
            actions.reload=[this]{saved_notice.clear();retirement_serial.reset();backend.reload();};actions.exit=[this]{exit_requested=true;};
            auto resources=snapshot.resources;if(recovery_enabled)resources.capabilities.insert("editor.recovery");
            editor=std::make_unique<interfaces::EditorForm>(authority,snapshot.view.policy,snapshot.view.documents,snapshot.epoch,std::move(resources),std::move(current),selected,std::vector<rendering::SurfaceProvider>{},"",std::move(actions),true,backend.images());
            if(recovery_enabled){const auto& v=*snapshot.view.recovery;const auto& a=v.admission;
                editor->recovery(backend.recovery(),a.directory.path,{v.editor_session,a.profile,a.generation,a.policy_revision,a.erase},backend.preparations(),snapshot.recovery_retirement);
                if(snapshot.recovery_retirement)retirement_serial=snapshot.serial;
            }
            gtk_box_pack_start(GTK_BOX(forms),editor->widget(),TRUE,TRUE,0);gtk_widget_show_all(editor->widget());
        }else{
            interfaces::SettingsForm::Actions actions;
            actions.request_id=[this]{return backend.request_id();};actions.submit=[this](const auto& request){backend.submit(request);};
            actions.cancel=[this](const auto& request){backend.cancel(request);};actions.reload=[this]{backend.reload();};
            form=std::make_unique<interfaces::SettingsForm>(authority,snapshot.view.policy,snapshot.view.documents,snapshot.epoch,std::move(actions),interfaces::SettingsForm::Translator{},snapshot.resources,true);
            gtk_box_pack_start(GTK_BOX(forms),form->widget(),TRUE,TRUE,0);gtk_widget_show_all(form->widget());
        }
        gtk_widget_set_visible(recovery_notice,editor_mode&&!recovery_enabled);gtk_window_set_title(GTK_WINDOW(window),editor_mode?"SysPane Scene Editor":"SysPane Settings");
        shown=snapshot.serial;erased=false;transition=false;
    }
    gboolean observed_tick()noexcept{
        if(!timing)return tick();
        const auto begin=g_get_monotonic_time();
        const auto delay=previous_tick?std::max<gint64>(0,begin-previous_tick-20000):0;
        const auto keep=tick();const auto end=g_get_monotonic_time();
        try{if(!timing(static_cast<std::uint64_t>(end-begin),static_cast<std::uint64_t>(delay))){result=2;stop();}}
        catch(...){result=2;stop();}
        previous_tick=g_get_monotonic_time();return keep;
    }
    gboolean tick()noexcept{
        try{
            auto state=backend.take();if(state.failed)result=2;
            if(state.withdrawal!=withdrawal){withdrawal=state.withdrawal;saved_notice.clear();retirement_serial.reset();if(form)form->policy({});if(editor)editor->policy({});erased=true;}
            if(closing){if(state.stopped&&(!editor||editor->stopped())){gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;}
            const auto notice=state.status+(saved_notice.empty()?"":" "+saved_notice);
            gtk_label_set_text(GTK_LABEL(status),editor_unavailable?"Scene editor unavailable for the current displays.":notice.c_str());
            gtk_button_set_label(GTK_BUTTON(retry),state.pending?"Retrieve original request":"Reconnect");gtk_widget_set_sensitive(retry,state.pending||!state.profile);
            if(state.reply){const auto& r=*state.reply;
                if(form){if(r.query.empty())form->complete(r.ticket,r.body);else form->reconciled(r.ticket,r.query,r.epoch,r.body);}
                if(editor){if(r.query.empty())editor->complete(r.ticket,r.body);else editor->reconciled(r.ticket,r.query,r.epoch,r.body);}
                const auto& result=r.query.empty()?r.body:r.body.at("result");
                if(editor&&recovery_enabled&&result.at("outcome")=="accepted"){
                    saved_notice="Configuration saved durably at revision "+result.at("revision").get<std::string>()+". Activation and visibility remain unconfirmed.";
                    if(!state.loading&&state.profile&&std::to_string(configuration::authored_revision(state.profile->view.documents))!=result.at("revision")){
                        backend.reload();close_forms();transition=true;state.loading=true;
                    }
                }
            }
            if(exit_requested){exit_requested=false;saved_notice.clear();retirement_serial.reset();backend.reload();close_forms();editor_mode=false;transition=true;state.loading=true;}
            if(state.profile&&!state.loading&&!state.pending&&(shown!=state.profile->serial||erased||transition||(!editor&&editor_unavailable&&topology_dirty))){
                close_forms();
                if(!editor||editor->stopped()){editor.reset();form.reset();populate(*state.profile);}
            }
            const bool current=state.profile&&!state.loading&&!state.pending&&!transition&&!erased;
            if(editor&&current&&retirement_serial&&*retirement_serial==state.profile->serial&&editor->retirement_decided()){
                backend.acknowledge_retirement(*retirement_serial);retirement_serial.reset();
            }
            if(editor&&current&&topology_dirty){
                scene::Topology next;
                try{next=topology();editor_unavailable=false;}
                catch(const protocol::Error&){editor_unavailable=true;topology_dirty=false;}
                if(!editor_unavailable){const auto selected=next.fallback;editor->topology(std::move(next),selected);}
            }
            const bool navigate=current&&can_leave();gtk_widget_set_sensitive(settings_button,navigate&&editor_mode);gtk_widget_set_sensitive(editor_button,navigate&&!editor_mode);
            if(form)gtk_widget_set_sensitive(form->widget(),state.profile&&!state.loading&&!transition);
            if(editor)gtk_widget_set_sensitive(editor->widget(),state.profile&&!state.loading&&!transition&&!editor_unavailable);
            return G_SOURCE_CONTINUE;
        }catch(...){result=2;stop();return G_SOURCE_CONTINUE;}
    }
    ~Window(){editor.reset();form.reset();if(window)gtk_widget_destroy(window);if(display)g_signal_handlers_disconnect_by_data(display,this);for(auto* monitor:monitors){g_signal_handlers_disconnect_by_data(monitor,this);g_object_unref(monitor);}}
};
}
int run_frontend(int argc,char** argv,platform::HelperBundleExpectation expectation,bool experimental_recovery,FrontendTimingObserver timing){
    try{
        std::string profile="profile:default";
        for(int i=1;i<argc;++i){const std::string option=argv[i];
            if(option=="--help"&&argc==2){std::cout<<"SysPane development frontend\nUsage: syspane [--profile ID]\nUses native XDG profile and runtime directories.\n";return 0;}
            if(option!="--profile"||i+1>=argc||!protocol::identifier(argv[i+1]))return 2;
            profile=argv[++i];
        }
        if(!gtk_init_check(nullptr,nullptr)){std::cerr<<"frontend.display_unavailable\n";return 2;}
        const char* selected=std::getenv("XDG_RUNTIME_DIR");
        LinuxFrontendBackend backend(std::move(expectation),selected?selected:"",platform::profile_environment(profile));
        Window window(backend,experimental_recovery,std::move(timing));g_timeout_add_full(G_PRIORITY_DEFAULT,20,+[](gpointer value)->gboolean{return static_cast<Window*>(value)->observed_tick();},&window,nullptr);
        gtk_main();return window.result;
    }catch(...){std::cerr<<"frontend.startup\n";return 2;}
}
}
