#include "frontend_linux.hpp"
#include "settings_form.hpp"
#include <gtk/gtk.h>
#include <cstdlib>
#include <iostream>

namespace syspane::application {
namespace {
void accessible(GtkWidget* widget,const char* description){atk_object_set_description(gtk_widget_get_accessible(widget),description);}
struct Window {
    LinuxFrontendBackend& backend;GtkWidget *window=nullptr,*box=nullptr,*status=nullptr,*retry=nullptr,*quit=nullptr;
    std::unique_ptr<interfaces::SettingsForm> form;
    std::uint64_t shown=0,withdrawal=0;bool erased=false,closing=false;int result=0;
    explicit Window(LinuxFrontendBackend& value):backend(value){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Settings");gtk_window_set_default_size(GTK_WINDOW(window),800,650);
        box=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);gtk_container_set_border_width(GTK_CONTAINER(box),12);gtk_container_add(GTK_CONTAINER(window),box);
        status=gtk_label_new("Starting configuration service.");gtk_label_set_xalign(GTK_LABEL(status),0);gtk_label_set_line_wrap(GTK_LABEL(status),TRUE);accessible(status,"frontend.status");gtk_box_pack_start(GTK_BOX(box),status,FALSE,FALSE,0);
        auto* actions=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);gtk_box_pack_end(GTK_BOX(box),actions,FALSE,FALSE,0);
        retry=gtk_button_new_with_label("Reconnect");accessible(retry,"frontend.retrieve");gtk_box_pack_start(GTK_BOX(actions),retry,FALSE,FALSE,0);
        quit=gtk_button_new_with_label("Quit");accessible(quit,"frontend.quit");gtk_box_pack_end(GTK_BOX(actions),quit,FALSE,FALSE,0);
        g_signal_connect(retry,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);try{s.backend.retrieve();}catch(...){s.stop();}}),this);
        g_signal_connect(quit,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Window*>(p)->stop();}),this);
        g_signal_connect(window,"delete-event",G_CALLBACK(+[](GtkWidget*,GdkEvent*,gpointer p)->gboolean{static_cast<Window*>(p)->stop();return TRUE;}),this);
        gtk_widget_show_all(window);
    }
    void stop()noexcept{
        if(closing)return;
        closing=true;
        try{if(form)form->close();backend.close();}catch(...){result=2;}
        gtk_widget_set_sensitive(retry,FALSE);gtk_widget_set_sensitive(quit,FALSE);
        gtk_label_set_text(GTK_LABEL(status),"Closing; waiting for configuration service to stop. Closing cannot undo a submitted change.");
    }
    gboolean tick()noexcept{
        try{
            auto state=backend.take();if(state.failed)result=2;
            if(state.withdrawal!=withdrawal){withdrawal=state.withdrawal;if(form)form->policy({});erased=true;}
            if(closing){if(state.stopped){gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;}
            gtk_label_set_text(GTK_LABEL(status),state.status.c_str());
            gtk_button_set_label(GTK_BUTTON(retry),state.pending?"Retrieve original request":"Reconnect");gtk_widget_set_sensitive(retry,state.pending||!state.profile);
            if(state.reply&&form){const auto& r=*state.reply;if(r.query.empty())form->complete(r.ticket,r.body);else form->reconciled(r.ticket,r.query,r.epoch,r.body);}
            if(state.profile&&!state.pending&&(shown!=state.profile->serial||erased)){
                if(form)form->close();
                form.reset();const auto& snapshot=*state.profile;
                interfaces::SettingsForm::Actions actions;
                actions.request_id=[this]{return backend.request_id();};actions.submit=[this](const auto& request){backend.submit(request);};
                actions.cancel=[this](const auto& request){backend.cancel(request);};actions.reload=[this]{backend.reload();};
                form=std::make_unique<interfaces::SettingsForm>(configuration::Authority{true,"console",{"console"}},snapshot.view.policy,snapshot.view.documents,snapshot.epoch,std::move(actions),interfaces::SettingsForm::Translator{},snapshot.resources,true);
                gtk_box_pack_start(GTK_BOX(box),form->widget(),TRUE,TRUE,0);gtk_widget_show_all(form->widget());shown=snapshot.serial;erased=false;
            }
            if(form)gtk_widget_set_sensitive(form->widget(),state.profile&&!state.loading);
            return G_SOURCE_CONTINUE;
        }catch(...){result=2;stop();return G_SOURCE_CONTINUE;}
    }
    ~Window(){form.reset();if(window)gtk_widget_destroy(window);}
};
}
int run_frontend(int argc,char** argv,platform::HelperExpectation expectation){
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
        Window window(backend);g_timeout_add_full(G_PRIORITY_DEFAULT,20,+[](gpointer value)->gboolean{return static_cast<Window*>(value)->tick();},&window,nullptr);
        gtk_main();return window.result;
    }catch(...){std::cerr<<"frontend.startup\n";return 2;}
}
}
