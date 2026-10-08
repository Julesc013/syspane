#include "settings_form.hpp"
#include "async_commands.hpp"
#include "generation_store_linux.hpp"
#include "settings_content_fixture.hpp"
#include <gtk/gtk.h>
#include <glib-unix.h>
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
struct Window {
    std::string root,path,mode,behavior,input,epoch="E1";bool content=false;Json alternate_selection;c::Authored original;c::Policy current=policy();
    std::unique_ptr<os::LinuxGenerationStore> store;std::unique_ptr<c::AsyncCommands> owner;std::unique_ptr<ui::SettingsForm> form;
    GtkWidget *window=nullptr,*canary=nullptr;std::uint64_t serial=0;std::optional<ui::EditRequest> request;
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
    std::optional<ui::SettingsResources> resource_context(){
        if(!content)return {};
        const auto saved=store->load();need(static_cast<bool>(saved.resources),"stored resource context absent");std::vector<c::ContentPackage> packages;
        for(const auto& package:saved.resources->packages())packages.push_back(*package);
        return ui::SettingsResources{std::make_shared<const c::ContentCatalog>(std::move(packages)),saved.resources->selection(),{"scene.content"}};
    }
    c::ResourceProvider provider(){
        auto base=c::make_resource_provider(*store,{"scene.content"},[]{throw p::Error("fixture.import_unavailable");return std::vector<c::ContentPackage>{};});
        auto fault_catalog=behavior=="wrong-selection"?resource_context()->catalog:std::shared_ptr<const c::ContentCatalog>{};
        return {base.capabilities,[this,base=std::move(base),fault_catalog](const c::Authored& v,const Json& s){prepare(v);return fault_catalog?fault_catalog->resources(s,v):base.prepare(v,s);}};
    }
    void attach_owner(){
        if(content)owner=std::make_unique<c::AsyncCommands>(*store,epoch,provider());else owner=std::make_unique<c::AsyncCommands>(*store,epoch,[&](const auto& v){prepare(v);});
        owner->attach(epoch,c::authored_revision(store->load().documents),current);
    }
    void open_owner(){store=std::make_unique<os::LinuxGenerationStore>(path);attach_owner();}
    void initialize(){
        content=mode.find("resource-")==0;behavior=content?mode.substr(9):mode;
        if(behavior=="reopen")epoch="E2";
        original={read(root+"/spec/fixtures/valid/settings.json"),read(root+"/spec/fixtures/valid/scene-portable.json")};original.settings["revision"]=original.scene["revision"]="40";
        store=std::make_unique<os::LinuxGenerationStore>(path);
        if(content&&behavior!="reopen"){
            settings_fixture::Fixture fixture(root);auto bare=original;bare.settings["revision"]=bare.scene["revision"]="39";store->initialize(bare);
            c::ResourceProvider imports{{"scene.content"},[&](const c::Authored& v,const Json& s){return fixture.catalog->resources(s,v);}};
            c::Transactions bootstrap(*store,"E0",imports);auto scene=fixture.authored.scene;scene["revision"]="39";
            Json q={{"schema_version","0.4.0"},{"request_id","bootstrap"},{"expected_revision","39"},{"policy_generation","7"},{"intent","commit"},{"content",fixture.document["selection"]},{"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})}};
            const auto result=bootstrap.submit("fixture:settings","bootstrap",q.dump(),authority(),[&]{return current;},0);need(result["outcome"]=="accepted"&&result["revision"]=="40","resource bootstrap");
            alternate_selection=fixture.document["alternate_selection"];original=store->load().documents;
        }
        else if(behavior!="reopen"){auto initial=original;if(behavior=="conflict")initial.settings["revision"]=initial.scene["revision"]="41";store->initialize(initial);}
        else original=store->load().documents;
        if(behavior=="locked")current.forced["sampling.max_workers"]=2;
        attach_owner();
        ui::SettingsForm::Actions actions;
        actions.request_id=[&]{return "settings:"+std::to_string(++serial);};actions.submit=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"submit",q});if(behavior=="callback")throw std::runtime_error("ambiguous callback delivery");};
        actions.cancel=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"cancel",q});};actions.reload=[&]{need(commands.size()<4,"fixture queue");commands.push_back({"reload",{}});};
        form=std::make_unique<ui::SettingsForm>(authority(),current,original,epoch,std::move(actions),ui::SettingsForm::Translator{},resource_context());
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Settings");gtk_window_set_default_size(GTK_WINDOW(window),790,580);gtk_window_move(GTK_WINDOW(window),0,0);
        auto* box=gtk_box_new(GTK_ORIENTATION_VERTICAL,0);gtk_container_add(GTK_CONTAINER(window),box);gtk_box_pack_start(GTK_BOX(box),form->widget(),TRUE,TRUE,0);
        if(behavior=="retain"||behavior=="false-saved"){canary=gtk_label_new(behavior=="retain"?"Retained settings canary 1500":"");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        g_signal_connect(window,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Window*>(p)->closed=true;if(gtk_main_level())gtk_main_quit();}),this);gtk_widget_show_all(window);
    }
    void tick(){
        if(done.load(std::memory_order_acquire)){
            worker.join();if(error)std::rethrow_exception(error);need(owner->finish(std::move(*completion),now(),true),"worker not finished");completion.reset();done.store(false,std::memory_order_relaxed);
            auto delivery=owner->delivery(now());need(delivery.has_value()&&request.has_value(),"missing command delivery");emit({{"event","result"},{"result",delivery->reply}});
            if((behavior=="unknown"||behavior=="restart"||behavior=="callback")&&delivery->reply["outcome"]=="accepted")form->disconnected();else form->complete(request->ticket,delivery->reply);
        }
        while(!commands.empty()){
            auto command=commands.front();commands.pop_front();
            if(command.first=="reload"){need(!worker.joinable(),"reload while working");form->reload(store->load().documents,epoch,resource_context());emit({{"event","reloaded"}});continue;}
            const auto& q=*command.second;
            if(command.first=="cancel"){auto result=owner->query("fixture:settings",authority(),q.request,true,now());emit({{"event","cancel-requested"},{"result",result}});continue;}
            request=q;auto body=q.body;if(behavior=="wrong-selection"){auto changed=p::parse(body);changed["content"]=alternate_selection;body=changed.dump();}
            auto admission=owner->submit("fixture:settings","settings",1,authority(),body,true,now());emit({{"event","submitted"},{"body",p::parse(body)}});
            if(!admission.ticket){form->complete(q.ticket,admission.reply);emit({{"event","result"},{"result",admission.reply}});continue;}
            const auto ticket=owner->take();need(ticket.has_value()&&!worker.joinable(),"worker admission");
            if(behavior=="false-saved")gtk_label_set_text(GTK_LABEL(canary),"Saved durably; activation pending. Revision 41");
            worker=std::thread([&,ticket=*ticket]{try{completion.emplace(owner->run(ticket));}catch(...){error=std::current_exception();}done.store(true,std::memory_order_release);});
        }
    }
    void control(const std::string& value){
        if(value=="release")release();
        else if(value=="revoke"){current=policy(current.revision+1);current.disclosure.clear();owner->policy(current);form->policy(current);}
        else if(value=="regrant"){current=policy(current.revision+1);owner->policy(current);form->policy(current);}
        else if(value=="deny"){current=policy(current.revision+1);current.denied_capabilities.insert(content?"content.select":"settings.commit");owner->policy(current);form->policy(current);}
        else if(value=="retrieve"){need(request.has_value()&&!worker.joinable(),"retrieve before stop");auto result=owner->query("fixture:settings",authority(),request->request,false,now());form->complete(request->ticket,result);emit({{"event","retrieved"},{"result",result}});}
        else if(value=="restart"){need(request.has_value()&&!worker.joinable(),"restart before stop");owner.reset();store.reset();epoch="E2";current=policy(8);open_owner();form->policy(current);
            Json query={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch",request->epoch},{"request_id",request->request}};
            auto result=owner->reconcile("fixture:settings",authority(),query,now());form->reconciled(request->ticket,"Q",epoch,result);emit({{"event","reconciled"},{"response",result}});}
        else if(value=="close"){form->close();}
        else if(value=="quit")gtk_main_quit();
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
int main(int argc,char** argv){try{need(argc==4&&geteuid()!=0,"unprivileged fixture arguments");g_set_prgname("syspane-settings");need(gtk_init_check(nullptr,nullptr),"GTK unavailable");
    Window w;w.root=argv[1];w.path=argv[2];w.mode=argv[3];w.initialize();need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"control pipe");
    const auto timer=g_timeout_add(10,tick,&w),reader=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w);
    const auto deadline=g_timeout_add_seconds(40,+[](gpointer p)->gboolean{static_cast<Window*>(p)->code=1;gtk_main_quit();return G_SOURCE_REMOVE;},&w);
    emit({{"ready",true}});gtk_main();for(auto id:{timer,reader,deadline})if(g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);return w.code;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
