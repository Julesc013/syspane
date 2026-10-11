#pragma once
#include "scene_inspector.hpp"
#include "inspector_admission_owner.hpp"
#include <gtk/gtk.h>
#include <glib-unix.h>
#include <fcntl.h>
#include <unistd.h>

namespace gtk_history_limits {
using namespace fixture;namespace ui=syspane::interfaces;
inline GtkWidget* tree_of(GtkWidget* widget){
    if(GTK_IS_TREE_VIEW(widget))return widget;
    if(!GTK_IS_CONTAINER(widget))return nullptr;
    auto* children=gtk_container_get_children(GTK_CONTAINER(widget));GtkWidget* found=nullptr;
    for(auto* i=children;i&&!found;i=i->next)found=tree_of(GTK_WIDGET(i->data));
    g_list_free(children);return found;
}
inline v::SurfaceConfig configuration(const std::string& root,bool mixed){
    auto cfg=chart_config(root,{{"font",{{"family","Noto Sans"},{"size_dip",9}}}});
    auto& chart=cfg.authored.scene["widgets"][0];chart["content"]["window_ms"]=10000;chart["content"]["max_points"]=4096;
    chart["layout"]["base"]["x"]=1280;chart["layout"]["base"]["width"]=320;
    cfg.topology.displays[0].bounds=cfg.topology.displays[0].work={0,0,1600*64,2048*64};
    if(mixed){auto table=widget("table","table","Interfaces");table["bindings"]=Json::array();table["content"]={{"columns",Json::array()}};
        for(const auto& pair:std::vector<std::pair<std::string,std::string>>{{"network.receive_bytes","Rx"},{"network.transmit_bytes","Tx"},{"entity.id","Identity"},{"entity.kind","Kind"}}){
            table["bindings"].push_back(collection(pair.first,64));table["content"]["columns"].push_back({{"label",pair.second}});
        }
        table["layout"]["base"]["width"]=1280;table["layout"]["base"]["height"]=2048;
        cfg.authored.scene["widgets"].push_back(table);cfg.authored.scene["roots"].push_back("table");
    }
    return cfg;
}
struct Window {
    struct Timing {std::uint64_t work,delay;};
    bool mixed;unsigned fitting,sent=0;std::uint64_t revision=7,sequence=0,measured=0;
    GtkWidget* window=nullptr;std::unique_ptr<ui::SceneInspector> view;std::unique_ptr<r::TelemetryReceiver> receiver;
    std::vector<Timing> journal;gint64 previous=0;std::string input,pending;std::uint64_t command_work=0;int result=0;
    std::uint64_t now()const{return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
    c::Policy grant()const{auto p=inspector_admission_owner_test::grant();p.revision=revision;return p;}
    p::TelemetryBinding binding()const{auto b=inspector_admission_owner_test::binding();b.policy_revision=revision;b.negotiated.features.insert("telemetry.monotonic-replay");return b;}
    explicit Window(const std::string& root,bool table,unsigned count):mixed(table),fitting(count){
        static_assert(sizeof(s::ChartPoint)==40,"Pinned Linux chart ABI");need(count>1&&count<4096,"fitting argument");
        journal.reserve(32768);auto renders=std::make_shared<const ui::InspectorRenderFactory>(ui::threaded_inspector_renderer());
        view=std::make_unique<ui::SceneInspector>(c::Authority{true,"console",{"console"}},grant(),configuration(root,mixed),std::vector<v::SurfaceProvider>{provider()},"",ui::SceneInspector::Translator{},v::ImageFactory{},renders,11);
        receiver=std::make_unique<r::TelemetryReceiver>(r::DeliveryScope{11,4},grant(),n::network_metrics(),binding(),now());
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Scene Inspector");gtk_window_set_default_size(GTK_WINDOW(window),740,540);
        gtk_container_add(GTK_CONTAINER(window),view->widget());gtk_widget_show_all(window);gtk_widget_grab_focus(tree_of(view->widget()));
    }
    unsigned points(){auto* model=gtk_tree_view_get_model(GTK_TREE_VIEW(tree_of(view->widget())));GtkTreeIter root;
        return gtk_tree_model_get_iter_first(model,&root)?static_cast<unsigned>(gtk_tree_model_iter_n_children(model,&root)):0;}
    void publish(unsigned generation,std::uint64_t ns){
        n::NetworkState state("E1","clock:1","scope:1");state.demand(1);syspane::platform::NetworkResult input{syspane::platform::NetworkCode::success,0,{}};
        for(unsigned i=1;i<=(mixed?64U:1U);++i)input.rows.push_back({i,i,6,syspane::platform::NetworkCounters{10,7}});
        need(state.commit(1,0,std::move(input),tick(ns),tick(ns))==n::NetworkStateCode::accepted,"GTK history acquisition");
        auto doc=n::network_document(*state.sample(),generation,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id","P1"},{"record_id","sample:"+std::to_string(generation)},{"policy_revision",std::to_string(revision)},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D","E1",body.dump(),body},binding());
        need(receiver->receive(bytes,now(),tick(ns)).code==r::DataCode::accepted,"GTK history complete receipt");sent=generation;measured=ns;
    }
    void reply(const std::string& name,std::uint64_t work=0){std::cout<<Json({{"ack",name},{"command_work_us",work},{"generation",sent},{"reason",view->status().reason}}).dump()<<std::endl;}
    void command(const std::string& name){
        need(pending.empty(),"GTK history outstanding command");const auto begin=g_get_monotonic_time();
        if(name=="fill")pending=name;
        else if(name=="over"){publish(fitting+1,static_cast<std::uint64_t>(fitting)*1000000);pending=name;}
        else if(name=="recover"){publish(4098,20000000000ULL);pending=name;}
        else if(name=="revoke"){revision=8;auto denied=grant();denied.disclosure.erase({"console","history"});view->policy(std::move(denied),now());}
        else if(name=="fresh"){revision=9;view->policy(grant(),now());sequence=0;receiver=std::make_unique<r::TelemetryReceiver>(r::DeliveryScope{11,5},grant(),n::network_metrics(),binding(),now());publish(4099,21000000000ULL);pending=name;}
        else if(name=="close"){view->close();pending=name;}
        else if(name=="quit"){need(view->poll_image_jobs(),"quit before real renderer destruction");gtk_main_quit();}
        else throw std::runtime_error("GTK history command");
        command_work=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);need(command_work<=100000,"GTK history native command timing");
        if(pending.empty())reply(name,command_work);
    }
    void pulse(){
        const auto begin=g_get_monotonic_time();const auto delay=previous?std::max<gint64>(0,begin-previous-20000):0;
        if(pending=="close"){if(view->poll_image_jobs()){reply(pending,command_work);pending.clear();}}
        else{
            if(receiver->view(now()).connected){need(receiver->heartbeat(++sequence,now())==r::DataCode::accepted,"GTK history heartbeat");receiver->sample(tick(measured),now());}
            view->deliver(receiver->view(now()),{11,revision==9?5U:4U},now());
            const auto count=points();
            if(pending=="fill"){
                if(count==fitting){reply(pending,command_work);pending.clear();}
                else if(count==sent){publish(sent+1,static_cast<std::uint64_t>(sent)*1000000);if(sent%250==0)std::cout<<Json({{"progress",sent}}).dump()<<std::endl;}
            }else if(pending=="over"&&view->status().code==v::SurfaceCode::alternative&&count==0){reply(pending,command_work);pending.clear();}
            else if((pending=="recover"||pending=="fresh")&&count==1){reply(pending,command_work);pending.clear();}
        }
        const auto end=g_get_monotonic_time();need(journal.size()<32768,"GTK history timing capacity");journal.push_back({static_cast<std::uint64_t>(end-begin),static_cast<std::uint64_t>(delay)});previous=g_get_monotonic_time();
    }
};
inline int run(const std::string& root,bool mixed,unsigned fitting){
    g_set_prgname("syspane-scene-inspector");g_set_application_name("SysPane Scene Inspector");need(gtk_init_check(nullptr,nullptr),"GTK history display");Window w(root,mixed,fitting);
    need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"GTK history pipe");
    const auto source=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),+[](gint fd,GIOCondition cond,gpointer p)->gboolean{auto& s=*static_cast<Window*>(p);
        try{if(cond&(G_IO_HUP|G_IO_ERR))throw std::runtime_error("GTK history unexpected EOF");char raw[1024];const auto n=::read(fd,raw,sizeof(raw));if(n>0)s.input.append(raw,static_cast<std::size_t>(n));need(s.input.size()<=4096,"GTK history input limit");std::size_t at;
            while((at=s.input.find('\n'))!=std::string::npos){const auto line=s.input.substr(0,at);s.input.erase(0,at+1);s.command(line);}}
        catch(const std::exception& e){std::cerr<<e.what()<<'\n';s.result=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;},&w);
    const auto timer=g_timeout_add(20,+[](gpointer p)->gboolean{auto& s=*static_cast<Window*>(p);try{s.pulse();}catch(const std::exception& e){std::cerr<<e.what()<<'\n';s.result=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;},&w);
    const auto deadline=g_timeout_add_seconds(600,+[](gpointer p)->gboolean{static_cast<Window*>(p)->result=1;gtk_main_quit();return G_SOURCE_REMOVE;},&w);
    std::cout<<"{\"ready\":true}"<<std::endl;gtk_main();
    for(auto id:{source,timer,deadline})if(g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);
    w.view->close();const auto until=g_get_monotonic_time()+2500000;while(!w.view->poll_image_jobs()){need(g_get_monotonic_time()<until,"GTK history actual owner drain");g_usleep(1000);}
    w.view.reset();gtk_widget_destroy(w.window);
    std::cerr<<"history-timing-begin "<<w.journal.size()<<'\n';for(const auto& row:w.journal)std::cerr<<"history-timing "<<row.work<<' '<<row.delay<<'\n';std::cerr<<"history-timing-end "<<w.journal.size()<<'\n';
    return w.result;
}
}
