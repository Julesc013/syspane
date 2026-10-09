#include "editor_form.hpp"
#include "editor_recovery_session.hpp"
#include "child.hpp"
#include "async_commands.hpp"
#include "authored_theme.hpp"
#include "generation_store_linux.hpp"
#include "../configuration/settings_content_fixture.hpp"
#include "../scene/chart_fixture.hpp"
#include <gtk/gtk.h>
#include <glib-unix.h>
#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <deque>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <thread>
#include <unistd.h>
namespace c=syspane::configuration;namespace p=syspane::protocol;namespace os=syspane::platform;namespace ui=syspane::interfaces;using p::Json;
void need(bool v,const char* why){if(!v)throw std::runtime_error(why);}
std::mutex output;void emit(Json v){std::lock_guard<std::mutex> lock(output);std::cout<<v.dump()<<std::endl;}
Json read(const std::string& path){std::ifstream f(path);need(f.good(),"fixture unavailable");Json v;f>>v;return v;}
c::Authority authority(){return {true,"desktop",{"desktop"}};}
c::Policy policy(std::uint64_t revision=7){c::Policy v;v.available=true;v.revision=revision;v.disclosure[{"desktop","inspector"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
std::string image_worker(){char path[4096];const auto n=readlink("/proc/self/exe",path,sizeof(path)-1);need(n>0,"native path");std::string value(path,static_cast<std::size_t>(n));return value.substr(0,value.rfind('/'))+"/SysPane.ImageWorker";}
syspane::scene::Topology topology(const std::string& id="D1"){syspane::scene::Display d;d.id=id;d.bounds=d.work={0,0,500*64,420*64};return {{d},{},id};}
GtkWidget* editor_control(GtkWidget* root,const char* description){
    const auto* actual=atk_object_get_description(gtk_widget_get_accessible(root));if(actual&&std::string(actual)==description)return root;
    if(!GTK_IS_CONTAINER(root))return nullptr;
    auto* children=gtk_container_get_children(GTK_CONTAINER(root));GtkWidget* found=nullptr;
    for(auto* child=children;child&&!found;child=child->next)found=editor_control(GTK_WIDGET(child->data),description);
    g_list_free(children);return found;
}
struct Window {
    std::string root,path,mode,behavior,input,epoch="E1";bool content=false,large=false,arrange=false,group=false,snap=false,properties=false,layout_mode=false,container_mode=false,locks_mode=false,visibility_mode=false,theme_mode=false,clipboard_mode=false,recovery_mode=false,quitting=false;Json alternate_selection;c::Authored original;c::Policy current=policy();
    std::uint64_t data_token=0,data_sequence=0,last_heartbeat=0,data_generation=2;
    std::unique_ptr<os::LinuxGenerationStore> store;std::unique_ptr<c::AsyncCommands> owner;std::unique_ptr<ui::EditorForm> form;
    GtkWidget *window=nullptr,*canary=nullptr,*overlay=nullptr;bool recovery=false;std::uint64_t serial=0;std::optional<ui::EditRequest> request;
    std::deque<std::pair<std::string,std::optional<ui::EditRequest>>> commands;
    std::thread worker;std::optional<c::AsyncCommands::Completion> completion;std::exception_ptr error;std::atomic<bool> done{false};
    std::mutex mutex;std::condition_variable condition;bool released=false,closed=false;int code=0;
    std::uint64_t now()const{return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
    void release(){std::lock_guard<std::mutex> lock(mutex);released=true;condition.notify_all();}
    void prepare(const c::Authored& value){
        if(!content)need(value.settings["display"]["theme_id"]=="theme:native","unadmitted fixture theme");
        emit({{"event","held"}});
        std::unique_lock<std::mutex> lock(mutex);need(condition.wait_for(lock,std::chrono::seconds(12),[&]{return released;}),"preparation deadline");released=false;
    }
    std::set<std::string> capabilities()const{return recovery_mode?std::set<std::string>{"scene.content","editor.recovery"}:clipboard_mode?std::set<std::string>{"scene.content","editor.clipboard"}:theme_mode?std::set<std::string>{"scene.content","scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility","theme.typography","configuration.theme-overrides"}:visibility_mode?std::set<std::string>{"scene.content","scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility"}:locks_mode?std::set<std::string>{"scene.content","scene.edit-locks","configuration.edit-locks"}:std::set<std::string>{"scene.content"};}
    std::optional<ui::SettingsResources> resource_context(){
        if(!content)return {};
        const auto saved=store->load();need(static_cast<bool>(saved.resources),"stored resource context absent");std::vector<c::ContentPackage> packages;
        for(const auto& package:saved.resources->packages())packages.push_back(*package);
        return ui::SettingsResources{std::make_shared<const c::ContentCatalog>(std::move(packages)),saved.resources->selection(),capabilities()};
    }
    c::ResourceProvider provider(){
        auto base=c::make_resource_provider(*store,capabilities(),[]{throw p::Error("fixture.import_unavailable");return std::vector<c::ContentPackage>{};});
        if(theme_mode){base.after_prepare=[this]{prepare(original);};return base;}
        auto fault_catalog=behavior=="wrong-selection"?resource_context()->catalog:std::shared_ptr<const c::ContentCatalog>{};
        return {base.capabilities,[this,base=std::move(base),fault_catalog](const c::Authored& v,const Json& s){prepare(v);return fault_catalog?fault_catalog->resources(s,v):base.prepare(v,s);}};
    }
    void attach_owner(){
        if(content)owner=std::make_unique<c::AsyncCommands>(*store,epoch,provider());else owner=std::make_unique<c::AsyncCommands>(*store,epoch,[&](const auto& v){prepare(v);});
        owner->attach(epoch,c::authored_revision(store->load().documents),current);
    }
    void open_owner(){store=std::make_unique<os::LinuxGenerationStore>(path);attach_owner();}
    c::Policy local_policy(std::uint64_t revision){auto p=policy(revision);if(recovery_mode)p.disclosure[{"desktop","history"}]={"sensitive"};if(clipboard_mode)p.disclosure[{"desktop","clipboard"}]={"sensitive"};return p;}
    void initialize(){
        content=true;recovery_mode=mode.substr(0,9)=="recovery-";clipboard_mode=mode.substr(0,10)=="clipboard-";theme_mode=mode.substr(0,6)=="fonts-";visibility_mode=mode.substr(0,11)=="visibility-";locks_mode=mode.substr(0,6)=="locks-";container_mode=mode.substr(0,10)=="container-";layout_mode=mode.substr(0,7)=="layout-";large=recovery_mode||clipboard_mode||theme_mode||visibility_mode||locks_mode||mode.substr(0,6)=="large-";arrange=mode.substr(0,8)=="arrange-";group=mode.substr(0,6)=="group-";snap=mode.substr(0,5)=="snap-";properties=mode.substr(0,11)=="properties-";behavior=recovery_mode?mode.substr(9):clipboard_mode?mode.substr(10):theme_mode?mode.substr(6):visibility_mode?mode.substr(11):locks_mode?mode.substr(6):container_mode?mode.substr(10):layout_mode?mode.substr(7):large?mode.substr(6):arrange?mode.substr(8):group?mode.substr(6):snap?mode.substr(5):properties?mode.substr(11):mode;
        if(clipboard_mode||recovery_mode)current=local_policy(7);
        if(properties)current.disclosure[{"desktop","history"}]={"operational"};
        if(behavior=="reopen")epoch="E2";
        original={read(root+"/spec/fixtures/valid/settings.json"),read(root+"/spec/fixtures/valid/scene-portable.json")};original.settings["revision"]=original.scene["revision"]="40";
        store=std::make_unique<os::LinuxGenerationStore>(path);
        if(content&&behavior!="reopen"){
            settings_fixture::Fixture fixture(root,properties?"tests/editor/content-properties-fixture.json":"tests/configuration/settings-content-fixture.json");auto bare=original;bare.settings["revision"]=bare.scene["revision"]="39";store->initialize(bare);
            c::ResourceProvider imports{capabilities(),[&](const c::Authored& v,const Json& s){return fixture.catalog->resources(s,v);}};
            c::Transactions bootstrap(*store,"E0",imports);auto scene=read(root+(recovery_mode?"/tests/editor/recovery-controls-cases.json":clipboard_mode?"/tests/editor/native-clipboard-cases.json":theme_mode?"/tests/editor/theme-controls-cases.json":visibility_mode?"/tests/editor/visibility-controls-cases.json":locks_mode?"/tests/editor/edit-lock-cases.json":container_mode?"/tests/editor/container-cases.json":layout_mode?"/tests/editor/layout-authoring-cases.json":large?"/tests/configuration/large-command-cases.json":arrange?"/tests/editor/arrange-cases.json":group?"/tests/editor/group-cases.json":snap?"/tests/editor/snap-cases.json":properties?"/tests/editor/content-properties-cases.json":"/tests/editor/native-cases.json"))["authored"]["scene"];scene["revision"]="39";
            Json q={{"schema_version",visibility_mode?"0.7.0":locks_mode?"0.6.0":large?"0.5.0":"0.4.0"},{"request_id","bootstrap"},{"expected_revision","39"},{"policy_generation","7"},{"intent","commit"},{"content",fixture.document["selection"]},{"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})}};
            const auto result=bootstrap.submit("fixture:editor","bootstrap",q.dump(),authority(),[&]{return current;},0);need(result["outcome"]=="accepted"&&result["revision"]=="40","resource bootstrap");
            alternate_selection=fixture.document["alternate_selection"];original=store->load().documents;
        }
        else if(behavior!="reopen"){auto initial=original;if(behavior=="conflict")initial.settings["revision"]=initial.scene["revision"]="41";store->initialize(initial);}
        else original=store->load().documents;
        if(behavior=="locked")current.forced["sampling.max_workers"]=2;
        if(behavior=="conflict"){
            c::Transactions external(*store,"EX",c::make_resource_provider(*store,capabilities(),[]{return std::vector<c::ContentPackage>{};}));
            auto scene=original.scene;scene["widgets"][0]["title"]="Theirs";
            Json q={{"schema_version",visibility_mode?"0.7.0":locks_mode?"0.6.0":large?"0.5.0":"0.4.0"},{"request_id","other"},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},{"content",store->load().resources->selection()},{"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})}};
            need(external.submit("fixture:editor","other",q.dump(),authority(),[&]{return current;},0)["outcome"]=="accepted","conflict fixture");
        }
        attach_owner();
        ui::EditorForm::Actions actions;
        actions.widget_id=[&]{if(clipboard_mode)return "native:"+std::to_string(++serial);if(locks_mode&&behavior=="nested"&&!serial){++serial;return std::string("widget:group");}return "widget:new"+std::to_string(++serial);};actions.exit=[&]{commands.push_back({"exit",{}});};actions.request_id=[&]{return "editor:"+std::to_string(++serial);};actions.submit=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"submit",q});if(behavior=="callback")throw std::runtime_error("ambiguous callback delivery");};
        actions.cancel=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"cancel",q});};actions.reload=[&]{need(commands.size()<4,"fixture queue");commands.push_back({"reload",{}});};
        auto display=topology();if(properties){display.displays[0].bounds=display.displays[0].work={0,0,640*64,560*64};display.displays[0].scale_numerator=3;display.displays[0].scale_denominator=4;}
        form=std::make_unique<ui::EditorForm>(authority(),current,original,epoch,*resource_context(),display,"D1",(properties||visibility_mode||theme_mode)?std::vector<syspane::rendering::SurfaceProvider>{fixture::provider()}:std::vector<syspane::rendering::SurfaceProvider>{},image_worker(),std::move(actions),large);
        if(recovery_mode)bind_recovery();
        if(properties||visibility_mode||theme_mode){auto link=fixture::link();link.channel="inspector";data_token=form->attach("P1",link,now()).token;need(data_token!=0,"properties provider attach");
            for(unsigned i=1;i<=2;++i){auto document=fixture::document(i==1?20:80,i);for(auto& o:document["observations"])if(!o["measured_at"].is_null())o["measured_at"]["nanoseconds"]=std::to_string(i*1000000000ULL);
                need(form->receive("P1",data_token,7,fixture::wire(document,link),now(),fixture::tick(i*1000000000ULL)).code==fixture::r::DataCode::accepted,"properties sample");}}
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Editor");gtk_window_set_default_size(GTK_WINDOW(window),790,580);gtk_window_move(GTK_WINDOW(window),0,recovery?100:0);
        auto* box=gtk_box_new(GTK_ORIENTATION_VERTICAL,0);overlay=gtk_overlay_new();gtk_container_add(GTK_CONTAINER(window),overlay);gtk_container_add(GTK_CONTAINER(overlay),box);gtk_box_pack_start(GTK_BOX(box),form->widget(),TRUE,TRUE,0);
        if(behavior=="retain"||behavior=="false-saved"){canary=gtk_label_new(behavior=="retain"?"Retained editor canary Move me":"");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-container"){canary=gtk_label_new("Retained container canary Private container");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-layout"){canary=gtk_label_new("Retained layout canary Private layout role");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-create"){canary=gtk_label_new("Retained creation canary Private creation");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-font"){canary=gtk_label_new("Retained font canary Private font family");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-visibility"){canary=gtk_label_new("Retained visibility canary Private condition");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-binding"){canary=gtk_label_new("Retained binding canary Private filter");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        if(behavior=="retain-content"){canary=gtk_label_new("Retained content canary Initial color image");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        g_signal_connect(window,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& w=*static_cast<Window*>(p);w.closed=true;if(w.form)w.form->close();w.quitting=true;}),this);gtk_widget_show_all(window);
    }
    void bind_recovery(){
        auto worker=image_worker();worker=worker.substr(0,worker.rfind('/'))+"/SysPane.RecoveryWorker";
        if(behavior=="worker-failure")worker+="-missing";
        if(behavior=="held-close")worker=path+"-worker/worker-stop-pending_created";
        const auto profile=behavior=="scope-change"&&c::authored_revision(store->load().documents)==41?"profile:other":"profile:primary";
        form->recovery(worker,path+"-recovery",{"editor:session",profile,store->generation_token(),current.revision,true});
    }
    void quit(){form->close();quitting=true;}
    void tick(){
        if(quitting&&form->stopped()){gtk_main_quit();return;}
        if(data_token&&current.revision==7&&now()-last_heartbeat>=500){last_heartbeat=now();form->heartbeat("P1",data_token,7,++data_sequence,last_heartbeat);}
        if(done.load(std::memory_order_acquire)){
            worker.join();if(error)std::rethrow_exception(error);need(owner->finish(std::move(*completion),now(),true),"worker not finished");completion.reset();done.store(false,std::memory_order_relaxed);
            auto delivery=owner->delivery(now());need(delivery.has_value()&&request.has_value(),"missing command delivery");emit({{"event","result"},{"result",delivery->reply}});
            if((behavior=="unknown"||behavior=="restart"||behavior=="callback")&&delivery->reply["outcome"]=="accepted")form->disconnected();else {form->complete(request->ticket,delivery->reply);if(recovery_mode&&delivery->reply["outcome"]=="accepted")bind_recovery();}
        }
        while(!commands.empty()){
            auto command=commands.front();commands.pop_front();
            if(command.first=="exit"){emit({{"event","closed"}});quit();continue;}
            if(command.first=="reload"){need(!worker.joinable(),"reload while working");form->reload(store->load().documents,epoch,*resource_context());if(recovery_mode)bind_recovery();emit({{"event","reloaded"}});continue;}
            const auto& q=*command.second;
            if(command.first=="cancel"){auto result=owner->query("fixture:editor",authority(),q.request,true,now());emit({{"event","cancel-requested"},{"result",result}});continue;}
            request=q;auto body=q.body;if(behavior=="wrong-commit"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][0]["layout"]["base"]["x"]=71;body=changed.dump();}
            if(behavior=="wrong-font"){auto changed=c::parse_command(body);changed["theme_edit"]["font"]["weight"]=900;auto source=store->load().resources;auto proposed=source->theme();proposed["schema_version"]="0.2.0";proposed["font"]=changed["theme_edit"]["font"];
                if(changed["theme_edit"]["font_roles"].is_null())proposed.erase("font_roles");else proposed["font_roles"]=changed["theme_edit"]["font_roles"];
                auto artifact=c::author_theme(*source,proposed,current,capabilities());need(artifact.has_value(),"wrong font witness");changed["content"]["theme_override"]={{"package",artifact->package_pin},{"theme",artifact->theme_pin}};changed["operations"][0]["scene"]["theme_id"]=artifact->theme["theme_id"];body=changed.dump();}
            if(behavior=="wrong-visibility"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][0]["visibility"]["op"]="gt";body=changed.dump();}
            if(behavior=="wrong-lock"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][0].erase("edit_locked");body=changed.dump();}
            if(behavior=="wrong-container"){auto changed=c::parse_command(body);auto& children=changed["operations"][0]["scene"]["widgets"].back()["children"];std::reverse(children.begin(),children.end());body=changed.dump();}
            if(behavior=="wrong-layout"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][0]["layout"]["base"]["x"]=71;body=changed.dump();}
            if(behavior=="wrong-group"){auto changed=c::parse_command(body);auto& children=changed["operations"][0]["scene"]["widgets"][3]["children"];std::reverse(children.begin(),children.end());body=changed.dump();}
            if(behavior=="wrong-insert"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"].back()["title"]="Wrong insertion";body=changed.dump();}
            if(behavior=="wrong-binding"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][2]["bindings"][0]["field"]="network.receive_bytes";body=changed.dump();}
            if(behavior=="wrong-content"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][3]["content"]["alt"]="Wrong replacement";body=changed.dump();}
            auto admission=owner->submit("fixture:editor","settings",1,authority(),body,true,now());emit({{"event","submitted"},{"body",c::parse_command(body)}});
            if(!admission.ticket){form->complete(q.ticket,admission.reply);emit({{"event","result"},{"result",admission.reply}});continue;}
            const auto ticket=owner->take();need(ticket.has_value()&&!worker.joinable(),"worker admission");
            if(behavior=="false-saved")gtk_label_set_text(GTK_LABEL(canary),"Saved durably; activation pending. Revision 41");
            worker=std::thread([&,ticket=*ticket]{try{completion.emplace(owner->run(ticket));}catch(...){error=std::current_exception();}done.store(true,std::memory_order_release);});
        }
    }
    void control(const std::string& value){
        if(value=="freeze-preview"){
            need(behavior=="frozen-preview","unadmitted frozen preview");
            auto* pixels=gdk_pixbuf_get_from_window(gtk_widget_get_window(window),0,0,gtk_widget_get_allocated_width(window),gtk_widget_get_allocated_height(window));need(pixels!=nullptr,"capture fixture");
            auto* image=gtk_image_new_from_pixbuf(pixels);g_object_unref(pixels);gtk_widget_set_halign(image,GTK_ALIGN_START);gtk_widget_set_valign(image,GTK_ALIGN_START);gtk_overlay_add_overlay(GTK_OVERLAY(overlay),image);gtk_overlay_set_overlay_pass_through(GTK_OVERLAY(overlay),image,TRUE);gtk_widget_show(image);
        }
        else if(value=="condition-hide"||value=="condition-hide-select"||value=="condition-show"){need(visibility_mode&&data_token,"visibility laboratory control");auto link=fixture::link(current.revision);link.channel="inspector";const auto measured=++data_generation*1000000000ULL;auto doc=fixture::document(value=="condition-show"?80:0,data_generation);for(auto& o:doc["observations"])if(!o["measured_at"].is_null())o["measured_at"]["nanoseconds"]=std::to_string(measured);need(form->receive("P1",data_token,current.revision,fixture::wire(doc,link),now(),fixture::tick(measured)).code==fixture::r::DataCode::accepted,"visibility sample");
            if(value=="condition-hide-select"){auto* tree=editor_control(form->widget(),"editor.objects");need(tree&&GTK_IS_TREE_VIEW(tree),"native authored list");auto* selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree));gtk_tree_selection_unselect_all(selection);auto* path=gtk_tree_path_new_first();gtk_tree_selection_select_path(selection,path);gtk_tree_path_free(path);emit({{"event","selected-before-paint"}});}}
        else if(value=="condition-loss"){need(visibility_mode&&data_token,"visibility laboratory control");form->disconnect("P1",data_token,current.revision,now());data_token=0;}
        else if(value=="layout-narrow"||value=="layout-wide"){need(layout_mode||container_mode,"layout laboratory control");auto t=topology();t.displays[0].bounds.width=t.displays[0].work.width=(value=="layout-narrow"?399:500)*64;form->topology(t,"D1");}
        else if(value=="deny-clipboard"){current=local_policy(current.revision+1);current.disclosure.erase({"desktop","clipboard"});owner->policy(current);form->policy(current);}
        else if(value=="bind-recovery"){need(recovery_mode,"unadmitted recovery");bind_recovery();}
        else if(value=="disconnect"){form->disconnected();}
        else if(value=="policy"){current=local_policy(current.revision+1);owner->policy(current);form->policy(current);}
        else if(value=="deny-font"||value=="capability-loss"){current=local_policy(current.revision+1);current.denied_capabilities.insert(value=="deny-font"?"theme.edit":"theme.typography");owner->policy(current);form->policy(current);}
        else if(value=="topology"){form->topology(topology("D2"),"D2");}
        else if(value=="release")release();
        else if(value=="revoke"){current=local_policy(current.revision+1);current.disclosure.clear();owner->policy(current);form->policy(current);}
        else if(value=="regrant"){current=local_policy(current.revision+1);if(properties)current.disclosure[{"desktop","history"}]={"operational"};owner->policy(current);form->policy(current);}
        else if(value=="deny"){current=local_policy(current.revision+1);current.denied_capabilities.insert(content?"content.select":"settings.commit");owner->policy(current);form->policy(current);}
        else if(value=="retrieve"){need(request.has_value()&&!worker.joinable(),"retrieve before stop");auto result=owner->query("fixture:editor",authority(),request->request,false,now());form->complete(request->ticket,result);if(recovery_mode&&result["outcome"]=="accepted")bind_recovery();emit({{"event","retrieved"},{"result",result}});}
        else if(value=="restart"){need(request.has_value()&&!worker.joinable(),"restart before stop");owner.reset();store.reset();epoch="E2";current=local_policy(8);if(properties)current.disclosure[{"desktop","history"}]={"operational"};open_owner();form->policy(current);
            Json query={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch",request->epoch},{"request_id",request->request}};
            auto result=owner->reconcile("fixture:editor",authority(),query,now());form->reconciled(request->ticket,"Q",epoch,result);if(recovery_mode)bind_recovery();emit({{"event","reconciled"},{"response",result}});}
        else if(value=="close"){form->close();}
        else if(value=="quit")quit();
        else throw std::runtime_error("unknown fixture control");
        emit({{"ack",value}});
    }
    ~Window(){try{if(form)form->close();if(owner)owner->invalidate();release();if(worker.joinable())worker.join();form.reset();if(window&&!closed)gtk_widget_destroy(window);}catch(...){std::terminate();}}
};
gboolean tick(gpointer data){auto& w=*static_cast<Window*>(data);try{w.tick();return G_SOURCE_CONTINUE;}catch(const std::exception& e){emit({{"event","error"},{"reason",e.what()}});w.code=1;gtk_main_quit();return G_SOURCE_REMOVE;}}
gboolean input(gint fd,GIOCondition cond,gpointer data){auto& w=*static_cast<Window*>(data);try{
    if(cond&(G_IO_HUP|G_IO_ERR)){gtk_main_quit();return G_SOURCE_REMOVE;}char bytes[1024];const auto n=::read(fd,bytes,sizeof(bytes));if(n<=0)return G_SOURCE_CONTINUE;
    w.input.append(bytes,static_cast<std::size_t>(n));need(w.input.size()<=4096,"control bound");std::size_t at;
    while((at=w.input.find('\n'))!=std::string::npos){const auto line=w.input.substr(0,at);w.input.erase(0,at+1);w.control(line);}
    return G_SOURCE_CONTINUE;
}catch(const std::exception& e){emit({{"event","error"},{"reason",e.what()}});w.code=1;gtk_main_quit();return G_SOURCE_REMOVE;}}
#include "reply_lifecycle.hpp"
#include "initial_input.hpp"
#include "history_form.hpp"
int main(int argc,char** argv){try{const bool history=argc==3&&std::string(argv[1])=="--history-form";const bool initial=argc==3&&std::string(argv[1])=="--initial-input";const bool prepared=argc==3&&std::string(argv[1])=="--prepared-editor";const bool lifecycle=argc==3&&std::string(argv[1])=="--reply-lifecycle";const bool recovery=argc==6&&std::string(argv[1])=="--recovery-child";need((argc==4||recovery||lifecycle||prepared||initial||history)&&geteuid()!=0,"unprivileged fixture arguments");if(recovery)os::arm_parent_lifetime(std::stoull(argv[2]));g_set_prgname("syspane-editor");need(gtk_init_check(nullptr,nullptr),"GTK unavailable");
    if(history)return history_form(argv[2]);
    if(initial)return initial_input(argv[2]);
    if(lifecycle||prepared)return reply_lifecycle(argv[2],prepared);
    Window w;w.recovery=recovery;const int offset=recovery?2:0;w.root=argv[1+offset];w.path=argv[2+offset];w.mode=argv[3+offset];w.initialize();need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"control pipe");
    const auto timer=g_timeout_add(10,tick,&w),reader=recovery?0:g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w);
    const auto deadline=g_timeout_add_seconds(40,+[](gpointer p)->gboolean{static_cast<Window*>(p)->code=1;gtk_main_quit();return G_SOURCE_REMOVE;},&w);
    emit({{"ready",true}});gtk_main();for(auto id:{timer,reader,deadline})if(id&&g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);return w.code;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
