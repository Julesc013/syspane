#include "image_fixture.hpp"
#include "scene_inspector.hpp"
#include "inspector_delivery_tests.hpp"
#include "scene_inspector_model.hpp"
#include <gtk/gtk.h>
#include <glib-unix.h>
#include <fcntl.h>
#include <algorithm>
#include <iostream>
#include "inspector_image_owner.hpp"
using namespace fixture;
namespace ui=syspane::interfaces;
namespace {
c::Policy inspector_policy(std::uint64_t revision=7,std::string denied={}){auto p=chart_policy(revision);p.disclosure.erase({"desktop","desktop"});p.disclosure[{"desktop","inspector"}]={"operational"};
    if(denied=="resource")p.denied_capabilities.insert("scene.content");else if(!denied.empty())p.disclosure.erase({"desktop",denied});return p;}
p::TelemetryBinding inspector_link(std::uint64_t revision=7){auto l=link(revision);l.channel="inspector";return l;}
int component(const std::string& root){
    for(const std::string denied:{"","inspector","accessibility","history","resource"}){auto cfg=chart_config(root);v::SceneSurface surface({true,"desktop",{"desktop"}},inspector_policy(7,denied),cfg,{provider()},[]{return true;},{},v::SurfaceAudience::inspector);
        need(surface.attach("P1",link(),0).token==0,"desktop wire cannot enter inspector");const auto l=inspector_link();const auto t=surface.attach("P1",l,1).token;
        if(t)surface.receive("P1",t,7,wire(chart_document(10,1,0),l),2,tick(0));
        surface.paint(3,{{"P1",tick(0)}},[&](auto code,const auto* frame){if(!denied.empty()){need(code==v::SurfaceCode::restricted&&!frame,"independent inspector grants");return;}
            need(frame&&frame->widgets[0].chart->points.size()==1&&frame->widgets[0].chart->identity,"typed chart disclosure");
            auto rows=ui::inspector_rows(*frame);need(rows.size()==1&&rows[0].children.size()==1&&rows[0].children[0].information=="10 byte; generation 1; start","exact chart data view");});}
    v::SurfaceFrame frame;frame.layout.scene_id="scene:test";s::Node node;node.id="one";node.kind="text";frame.layout.nodes={node};v::SurfaceText text;text.id="one";text.kind="text";text.title="A";text.accessible="Public";frame.widgets={text};
    auto expect=[&](v::SurfaceFrame f,const char* code){bool rejected=false;try{ui::inspector_rows(f);}catch(const p::Error& e){rejected=std::string(e.what())==code;}need(rejected,"invalid semantic tree must reject");};
    auto bad=frame;bad.widgets[0].accessible=std::string(2097153,'x');expect(bad,"inspector.capacity");bad=frame;bad.widgets[0].accessible="\xff";expect(bad,"inspector.text");bad=frame;bad.layout.nodes[0].parent="missing";expect(bad,"inspector.hierarchy");bad=frame;bad.widgets.push_back(text);expect(bad,"inspector.frame");
    auto a=ui::inspector_rows(frame);frame.widgets[0].accessible="Next";auto b=ui::inspector_rows(frame);need(a[0].key==b[0].key&&b[0].information=="Next","content does not change identity");
    auto group=node;group.id="group";group.kind="group";auto group_text=text;group_text.id="group";group_text.kind="group";
    frame.layout.nodes[0].parent="group";frame.layout.nodes.insert(frame.layout.nodes.begin(),group);frame.widgets.insert(frame.widgets.begin(),group_text);
    auto nested=ui::inspector_rows(frame);need(nested.size()==1&&nested[0].children.size()==1&&nested[0].children[0].key==a[0].key,"authored group hierarchy");
    frame.layout.nodes[1].kind="chart";auto& chart_text=frame.widgets[1];chart_text.kind="chart";chart_text.chart.emplace();
    s::ChartIdentity identity;identity.producer="P1";identity.epoch="epoch:one";identity.entity="same";identity.field="value";identity.unit="byte";identity.integer=true;
    chart_text.chart->identity=identity;chart_text.chart->points={{42,1,UINT64_MAX,false}};
    auto point=ui::inspector_rows(frame)[0].children[0].children[0];need(point.information=="18446744073709551615 byte; generation 1; start","exact integer chart point");
    chart_text.chart->points[0].generation=2;need(ui::inspector_rows(frame)[0].children[0].children[0].key==point.key,"generation is chart content");
    chart_text.chart->identity->epoch="epoch:two";need(ui::inspector_rows(frame)[0].children[0].children[0].key!=point.key,"epoch resets chart identity");
    chart_text.chart->points.push_back(chart_text.chart->points[0]);expect(frame,"inspector.capacity");
    std::cout<<"CHANNEL TREE BOUNDS pass\n";return 0;
}
GtkWidget* tree_of(GtkWidget* widget){if(GTK_IS_TREE_VIEW(widget))return widget;if(!GTK_IS_CONTAINER(widget))return nullptr;auto* children=gtk_container_get_children(GTK_CONTAINER(widget));GtkWidget* found=nullptr;
    for(auto* item=children;item&&!found;item=item->next)found=tree_of(GTK_WIDGET(item->data));
    g_list_free(children);return found;}
struct Window {
    std::string root,mode,input;GtkWidget* window=nullptr;std::unique_ptr<ui::SceneInspector> view;
    gint64 start=g_get_monotonic_time();std::uint64_t revision=7,token=0,generation=0,sequence=0,measured=100;int exit=0;bool closed=false;
    std::uint64_t now()const{return static_cast<std::uint64_t>((g_get_monotonic_time()-start)/1000);}
    bool chart()const{return mode=="chart";}
    bool image()const{return mode=="image";}
    bool table()const{return mode=="table"||mode=="translated"||mode=="retain"||mode=="wrong-selection";}
    std::map<std::string,m::Tick> ticks()const{return {{"P1",tick(measured)}};}
    v::SurfaceConfig cfg(){auto result=image()?image_config(root):chart()?chart_config(root):table()?table_config(root):config(root);
        if(image())result.authored.scene["widgets"][0]["title"]="Public image";
        return result;}
    void full(std::uint64_t value,std::string change={}){auto l=inspector_link(revision);auto doc=chart()?chart_document(value,++generation,measured):table()?table_document(value,++generation):document(value,++generation);
        if(change=="insert"){auto e=doc["entities"][0];e["id"]="network:interface:0";doc["entities"].push_back(e);const auto old=doc["observations"];for(auto o:old)if(o["entity_id"]=="network:interface:1"){o["entity_id"]="network:interface:0";if(o["field"]=="network.receive_bytes")o["value"]["data"]="55";doc["observations"].push_back(o);}}
        if(change=="remove"){auto& entities=doc["entities"];entities.erase(std::remove_if(entities.begin(),entities.end(),[](const auto& e){return e["id"]=="network:interface:1";}),entities.end());auto& observations=doc["observations"];observations.erase(std::remove_if(observations.begin(),observations.end(),[](const auto& o){return o["entity_id"]=="network:interface:1";}),observations.end());}
        need(view->receive("P1",token,revision,wire(doc,l),now(),tick(measured)).code==r::DataCode::accepted,"inspector native delivery");}
    void command(const std::string& cmd){
        if(cmd=="update")full(987);else if(cmd=="insert"){full(987,"insert");if(mode=="wrong-selection"){auto* path=gtk_tree_path_new_from_indices(0,2,0,-1);gtk_tree_view_set_cursor(GTK_TREE_VIEW(tree_of(view->widget())),path,nullptr,FALSE);gtk_tree_path_free(path);}}
        else if(cmd=="remove")full(987,"remove");
        else if(cmd=="revoke"){revision=8;view->policy(inspector_policy(revision,"inspector"),now());}
        else if(cmd=="regrant"){revision=9;view->policy(inspector_policy(revision),now());}
        else if(cmd=="fresh"){token=view->attach("P1",inspector_link(revision),now(),ticks()).token;need(token!=0,"inspector fresh attachment");generation=0;full(456);}
        else if(cmd=="close"){view->close();closed=true;}
        else if(cmd=="quit"){view->close();closed=true;gtk_main_quit();}
        else throw std::runtime_error("inspector command");
        std::cout<<Json({{"ack",cmd}}).dump()<<std::endl;
    }
};
gboolean input(gint fd,GIOCondition cond,gpointer data){auto& w=*static_cast<Window*>(data);try{if(cond&(G_IO_HUP|G_IO_ERR)){w.view->close();gtk_main_quit();return G_SOURCE_REMOVE;}char bytes[1024];const auto n=::read(fd,bytes,sizeof(bytes));if(n<=0)return G_SOURCE_CONTINUE;
    w.input.append(bytes,static_cast<std::size_t>(n));need(w.input.size()<=4096,"inspector input bound");std::size_t at;while((at=w.input.find('\n'))!=std::string::npos){auto command=w.input.substr(0,at);w.input.erase(0,at+1);w.command(command);}}
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';w.exit=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;}
gboolean timer(gpointer data){auto& w=*static_cast<Window*>(data);try{w.view->poll_image_jobs();if(!w.closed){w.view->heartbeat("P1",w.token,w.revision,++w.sequence,w.now(),w.ticks());w.view->refresh(w.now(),w.ticks());}}
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';w.exit=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;}
int window(const std::string& root,const std::string& mode){g_set_prgname("syspane-scene-inspector");g_set_application_name("SysPane Scene Inspector");need(gtk_init_check(nullptr,nullptr),"native GTK unavailable");Window w;w.root=root;w.mode=mode;
    if(mode=="image")inspector_image_owner::run(root);
    if(mode=="scalar")inspector_delivery_test::run(root);
    w.window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(w.window),"SysPane Scene Inspector");gtk_window_set_default_size(GTK_WINDOW(w.window),740,540);gtk_window_move(GTK_WINDOW(w.window),0,0);
    ui::SceneInspector::Translator translate;if(mode=="translated"){const auto labels=read(root+"/../../../tests/scene","inspector-cases.json")["translation"];translate=[labels](const std::string& id){return labels.at(id).get<std::string>();};}
    w.view=std::make_unique<ui::SceneInspector>(c::Authority{true,"desktop",{"desktop"}},inspector_policy(),w.cfg(),std::vector<v::SurfaceProvider>{provider()},image_worker_path(),translate);
    auto* box=gtk_box_new(GTK_ORIENTATION_VERTICAL,0);gtk_container_add(GTK_CONTAINER(w.window),box);gtk_box_pack_start(GTK_BOX(box),w.view->widget(),TRUE,TRUE,0);
    if(mode=="retain")gtk_box_pack_start(GTK_BOX(box),gtk_label_new("Retained canary 123 byte"),FALSE,FALSE,0);
    w.token=w.view->attach("P1",inspector_link(),w.now(),w.ticks()).token;need(w.token!=0,"native inspector initial attachment");
    if(w.chart()){w.measured=0;w.full(10);w.measured=500000000;w.full(90);w.measured=1000000000;w.full(10);}else if(!w.image())w.full(123);
    gtk_widget_show_all(w.window);gtk_widget_grab_focus(tree_of(w.view->widget()));
    auto* bindings=gtk_binding_set_by_class(G_OBJECT_GET_CLASS(tree_of(w.view->widget())));
    for(auto* entry=bindings->entries;entry;entry=entry->set_next)if(entry->keyval==GDK_KEY_Left||entry->keyval==GDK_KEY_Right)for(auto* signal=entry->signals;signal;signal=signal->next)std::cerr<<"binding "<<entry->keyval<<" modifiers="<<entry->modifiers<<" signal="<<signal->signal_name<<'\n';
    g_signal_connect(tree_of(w.view->widget()),"key-press-event",G_CALLBACK(+[](GtkWidget* widget,GdkEventKey* event,gpointer)->gboolean{std::cerr<<"tree-key "<<event->keyval<<" focus="<<gtk_widget_has_focus(widget)<<" modifiers="<<event->state<<'\n';return FALSE;}),nullptr);
    g_signal_connect(w.window,"key-press-event",G_CALLBACK(+[](GtkWidget*,GdkEventKey* event,gpointer p)->gboolean{auto& owner=*static_cast<Window*>(p);GtkTreePath* path=nullptr;GtkTreeViewColumn* col=nullptr;auto* tree=GTK_TREE_VIEW(tree_of(owner.view->widget()));gtk_tree_view_get_cursor(tree,&path,&col);auto* value=path?gtk_tree_path_to_string(path):nullptr;std::cerr<<"native-key "<<event->keyval<<" column="<<(col?gtk_tree_view_column_get_title(col):"none")<<" path="<<(value?value:"none")<<" expanded="<<(path?gtk_tree_view_row_expanded(tree,path):false)<<'\n';g_free(value);if(path)gtk_tree_path_free(path);return FALSE;}),&w);
    g_signal_connect(tree_of(w.view->widget()),"row-collapsed",G_CALLBACK(+[](GtkTreeView*,GtkTreeIter*,GtkTreePath*,gpointer){std::cerr<<"native-row-collapsed\n";}),nullptr);
    g_signal_connect(w.window,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer){gtk_main_quit();}),nullptr);
    need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"inspector pipe");
    const auto input_id=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w),timer_id=g_timeout_add(50,timer,&w);
    const auto deadline=g_timeout_add_seconds(25,+[](gpointer p)->gboolean{static_cast<Window*>(p)->exit=1;gtk_main_quit();return G_SOURCE_REMOVE;},&w);
    std::cout<<"{\"ready\":true}"<<std::endl;gtk_main();
    for(auto id:{input_id,timer_id,deadline})if(g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);
    w.view->close();const auto until=g_get_monotonic_time()+2000000;while(!w.view->poll_image_jobs()){need(g_get_monotonic_time()<until,"inspector child drain");g_usleep(1000);}w.view.reset();gtk_widget_destroy(w.window);return w.exit;
}
}
int main(int argc,char** argv){try{need(argc>=2,"inspector arguments");return argc==2?component(argv[1]):window(argv[1],argv[2]);}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
