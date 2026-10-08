#include "private_text.hpp"
#include <gtk/gtk.h>
#include <string>

namespace {
void describe(GtkWidget* widget,const char* id){atk_object_set_description(gtk_widget_get_accessible(widget),id);}
struct Window {
    GtkWidget *window=nullptr,*text=nullptr,*status=nullptr;unsigned cycles=0;
    explicit Window(const char* initial){
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Settings");gtk_window_set_default_size(GTK_WINDOW(window),480,200);
        auto* box=gtk_box_new(GTK_ORIENTATION_VERTICAL,8);gtk_container_add(GTK_CONTAINER(window),box);
        text=syspane::interfaces::private_text();g_object_ref_sink(text);describe(text,"private.text");
        gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(text)),initial,-1);gtk_box_pack_start(GTK_BOX(box),text,TRUE,TRUE,0);
        status=gtk_label_new("ready");describe(status,"private.status");gtk_box_pack_start(GTK_BOX(box),status,FALSE,FALSE,0);
        auto button=[&](const char* id,const char* label,GCallback callback){auto* value=gtk_button_new_with_label(label);describe(value,id);gtk_box_pack_start(GTK_BOX(box),value,FALSE,FALSE,0);g_signal_connect(value,"clicked",callback,this);};
        button("private.cycle","Cycle",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);
            gtk_widget_hide(s.text);gtk_widget_unrealize(s.text);gtk_widget_show(s.text);
            gtk_label_set_text(GTK_LABEL(s.status),("cycle "+std::to_string(++s.cycles)).c_str());}));
        button("private.destroy","Destroy text",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& s=*static_cast<Window*>(p);gtk_widget_destroy(s.text);gtk_label_set_text(GTK_LABEL(s.status),"destroyed");}));
        button("private.quit","Quit",G_CALLBACK(+[](GtkWidget*,gpointer){gtk_main_quit();}));
        gtk_widget_show_all(window);
    }
    ~Window(){gtk_widget_destroy(window);g_object_unref(text);}
};
}
int main(int argc,char** argv){
    if(argc!=3)return 2;
    const std::string mode=argv[1],initial=argv[2];
    if(!gtk_init_check(nullptr,nullptr))return 2;
    if(mode=="NEVER-REALIZED"){
        auto* text=syspane::interfaces::private_text();g_object_ref_sink(text);
        auto* buffer=gtk_text_view_get_buffer(GTK_TEXT_VIEW(text));gtk_text_buffer_set_text(buffer,initial.c_str(),-1);
        GtkTextIter first,last;gtk_text_buffer_get_bounds(buffer,&first,&last);gtk_text_buffer_select_range(buffer,&first,&last);
        gtk_widget_destroy(text);g_object_unref(text);return 0;
    }
    if(mode!="CYCLE"&&mode!="DESTROY")return 2;
    Window window(initial.c_str());gtk_main();return 0;
}
