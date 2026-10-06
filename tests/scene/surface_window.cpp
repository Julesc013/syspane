#include "table_fixture.hpp"
#include <gtk/gtk.h>
#include <glib-unix.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
using namespace fixture;
namespace {
struct Window {
    GtkWidget* area=nullptr;std::unique_ptr<v::SceneSurface> owner;
    gint64 start=g_get_monotonic_time();std::string input,mode;
    std::uint64_t revision=7,token=0,sequence=0,generation=0;bool connected=true,drawing=false,table=false;int exit=0;
    std::vector<unsigned char> fault_pixels;
    std::uint64_t now()const{return static_cast<std::uint64_t>((g_get_monotonic_time()-start)/1000);}
    m::Tick measured()const{return tick(100+now()*1000000);}
    bool clear(){if(mode!="ignore-accessible")atk_object_set_name(gtk_widget_get_accessible(area),"");if(!drawing)gtk_widget_queue_draw(area);return true;}
    void full(std::uint64_t number){++generation;auto d=table?table_document(number,generation):document(number,generation);const auto code=owner->receive("P1",token,revision,wire(d,link(revision)),now(),measured()).code;need(code==r::DataCode::accepted,"native full");}
    void command(const std::string& name){
        if(name=="revoke"){revision=8;owner->policy(policy(revision,false),now());}
        else if(name=="regrant"){revision=9;owner->policy(policy(revision),now());}
        else if(name=="fresh"){token=owner->attach("P1",link(revision),now()).token;need(token!=0,"native attach");generation=0;connected=true;full(456);}
        else if(name=="replace")full(987);
        else if(name=="stale"){auto result=owner->receive("P1",token,7,wire(document(999,99),link()),now(),measured());need(result.code!=r::DataCode::accepted,"stale native frame accepted");}
        else if(name=="disconnect"){connected=false;owner->disconnect("P1",token,revision,now());}
        else if(name=="close"){owner->close();gtk_main_quit();}
        else throw std::runtime_error("native command");
        gtk_widget_queue_draw(area);std::cout<<Json({{"ack",name}}).dump()<<std::endl;
    }
};
void pixels(cairo_t* cr,const std::vector<unsigned char>& rgba){
    if(rgba.empty())return;
    std::vector<std::uint32_t> argb(800*600);
    for(std::size_t i=0;i<argb.size();++i)argb[i]=(static_cast<std::uint32_t>(rgba[i*4+3])<<24)|(static_cast<std::uint32_t>(rgba[i*4])<<16)|(static_cast<std::uint32_t>(rgba[i*4+1])<<8)|rgba[i*4+2];
    auto* surface=cairo_image_surface_create_for_data(reinterpret_cast<unsigned char*>(argb.data()),CAIRO_FORMAT_ARGB32,800,600,800*4);
    cairo_set_source_surface(cr,surface,0,0);cairo_paint(cr);cairo_surface_destroy(surface);
}
gboolean draw(GtkWidget*,cairo_t* cr,gpointer data){auto& w=*static_cast<Window*>(data);w.drawing=true;
    try{
        w.owner->paint(w.now(),{{"P1",w.measured()}},[&](auto,const v::SurfaceFrame* f){
            cairo_set_source_rgb(cr,0,0,0);cairo_paint(cr);
            if(f){std::string accessible;for(const auto& row:f->widgets){if(!accessible.empty())accessible+='\n';accessible+=row.accessible;}
                atk_object_set_name(gtk_widget_get_accessible(w.area),accessible.c_str());
                if(w.mode=="ignore-pixels")w.fault_pixels=f->displays[0].rgba;
                pixels(cr,f->displays[0].rgba);
            }else if(w.mode=="ignore-pixels")pixels(cr,w.fault_pixels);
        });
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';w.exit=1;gtk_main_quit();}
    w.drawing=false;return TRUE;
}
gboolean timer(gpointer data){auto& w=*static_cast<Window*>(data);
    try{if(w.connected)w.owner->heartbeat("P1",w.token,w.revision,++w.sequence,w.now());gtk_widget_queue_draw(w.area);}
    catch(...){w.exit=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;
}
gboolean input(gint fd,GIOCondition condition,gpointer data){auto& w=*static_cast<Window*>(data);
    if(condition&(G_IO_HUP|G_IO_ERR)){w.owner->close();gtk_main_quit();return G_SOURCE_REMOVE;}
    char buf[1024];const auto n=::read(fd,buf,sizeof(buf));if(n<=0)return G_SOURCE_CONTINUE;
    try{w.input.append(buf,static_cast<std::size_t>(n));need(w.input.size()<=4096,"native input bound");std::size_t end;
        while((end=w.input.find('\n'))!=std::string::npos){auto cmd=w.input.substr(0,end);w.input.erase(0,end+1);w.command(cmd);}
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';w.exit=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;
}
gboolean deadline(gpointer data){auto& w=*static_cast<Window*>(data);w.exit=1;w.owner->close();gtk_main_quit();return G_SOURCE_REMOVE;}
}
int surface_window(const std::string& root,const std::string& mode){
    const bool table=mode.find("table-")==0;const auto fault=table?mode.substr(6):mode;
    need(fault=="normal"||fault=="ignore-pixels"||fault=="ignore-accessible","native mode");
    g_set_prgname("syspane-scene-surface");g_set_application_name("SysPane Scene Surface");if(!gtk_init_check(nullptr,nullptr))return 69;
    Window w;w.mode=fault;w.table=table;auto* window=gtk_window_new(GTK_WINDOW_TOPLEVEL);w.area=gtk_drawing_area_new();
    gtk_window_set_title(GTK_WINDOW(window),"SysPane Scene Surface");gtk_window_set_decorated(GTK_WINDOW(window),FALSE);
    gtk_window_set_default_size(GTK_WINDOW(window),800,600);gtk_window_move(GTK_WINDOW(window),0,0);gtk_container_add(GTK_CONTAINER(window),w.area);
    atk_object_set_description(gtk_widget_get_accessible(w.area),"syspane.scene.surface");
    auto provider_spec=provider();for(auto& field:provider_spec.fields)field.second=5000000000000ULL;
    w.owner=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},policy(),table?table_config(root):config(root),std::vector<v::SurfaceProvider>{provider_spec},[&]{return w.clear();});
    w.token=w.owner->attach("P1",link(),w.now()).token;need(w.token!=0,"native initial attach");w.full(123);
    g_signal_connect(w.area,"draw",G_CALLBACK(draw),&w);gtk_widget_show_all(window);
    need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"native stdin");
    const auto input_id=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w);
    const auto timer_id=g_timeout_add(50,timer,&w),deadline_id=g_timeout_add_seconds(25,deadline,&w);
    std::cout<<"{\"ready\":true}"<<std::endl;gtk_main();
    for(auto id:{input_id,timer_id,deadline_id})if(g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);
    w.owner.reset();gtk_widget_destroy(window);return w.exit;
}
