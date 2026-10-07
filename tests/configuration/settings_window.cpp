#include "settings_form.hpp"
#include "async_commands.hpp"
#include "generation_store_linux.hpp"
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
    std::string root,path,mode,input,epoch="E1";c::Authored original;c::Policy current=policy();
    std::unique_ptr<os::LinuxGenerationStore> store;std::unique_ptr<c::AsyncCommands> owner;std::unique_ptr<ui::SettingsForm> form;
    GtkWidget *window=nullptr,*canary=nullptr;std::uint64_t serial=0;std::optional<ui::EditRequest> request;
    std::deque<std::pair<std::string,std::optional<ui::EditRequest>>> commands;
    std::thread worker;std::optional<c::AsyncCommands::Completion> completion;std::exception_ptr error;std::atomic<bool> done{false};
    std::mutex mutex;std::condition_variable condition;bool released=false,closed=false;int code=0;
    std::uint64_t now()const{return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
    void release(){std::lock_guard<std::mutex> lock(mutex);released=true;condition.notify_all();}
    void prepare(const c::Authored& value){
        need(value.settings["display"]["theme_id"]=="theme:native","unadmitted fixture theme");emit({{"event","held"}});
        std::unique_lock<std::mutex> lock(mutex);need(condition.wait_for(lock,std::chrono::seconds(12),[&]{return released;}),"preparation deadline");released=false;
    }
    void open_owner(){store=std::make_unique<os::LinuxGenerationStore>(path);owner=std::make_unique<c::AsyncCommands>(*store,epoch,[&](const auto& v){prepare(v);});owner->attach(epoch,c::authored_revision(store->load().documents),current);}
    void initialize(){
        original={read(root+"/spec/fixtures/valid/settings.json"),read(root+"/spec/fixtures/valid/scene-portable.json")};original.settings["revision"]=original.scene["revision"]="40";
        store=std::make_unique<os::LinuxGenerationStore>(path);
        if(mode!="reopen"){auto initial=original;if(mode=="conflict")initial.settings["revision"]=initial.scene["revision"]="41";store->initialize(initial);}
        else original=store->load().documents;
        if(mode=="locked")current.forced["sampling.max_workers"]=2;
        owner=std::make_unique<c::AsyncCommands>(*store,epoch,[&](const auto& v){prepare(v);});owner->attach(epoch,c::authored_revision(store->load().documents),current);
        ui::SettingsForm::Actions actions;
        actions.request_id=[&]{return "settings:"+std::to_string(++serial);};actions.submit=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"submit",q});if(mode=="callback")throw std::runtime_error("ambiguous callback delivery");};
        actions.cancel=[&](const auto& q){need(commands.size()<4,"fixture queue");commands.push_back({"cancel",q});};actions.reload=[&]{need(commands.size()<4,"fixture queue");commands.push_back({"reload",{}});};
        form=std::make_unique<ui::SettingsForm>(authority(),current,original,epoch,std::move(actions));
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane Settings");gtk_window_set_default_size(GTK_WINDOW(window),790,580);gtk_window_move(GTK_WINDOW(window),0,0);
        auto* box=gtk_box_new(GTK_ORIENTATION_VERTICAL,0);gtk_container_add(GTK_CONTAINER(window),box);gtk_box_pack_start(GTK_BOX(box),form->widget(),TRUE,TRUE,0);
        if(mode=="retain"||mode=="false-saved"){canary=gtk_label_new(mode=="retain"?"Retained settings canary 1500":"");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}
        g_signal_connect(window,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){static_cast<Window*>(p)->closed=true;gtk_main_quit();}),this);gtk_widget_show_all(window);
    }
    void tick(){
        if(done.load(std::memory_order_acquire)){
            worker.join();if(error)std::rethrow_exception(error);need(owner->finish(std::move(*completion),now(),true),"worker not finished");completion.reset();done.store(false,std::memory_order_relaxed);
            auto delivery=owner->delivery(now());need(delivery.has_value()&&request.has_value(),"missing command delivery");emit({{"event","result"},{"result",delivery->reply}});
            if((mode=="unknown"||mode=="restart"||mode=="callback")&&delivery->reply["outcome"]=="accepted")form->disconnected();else form->complete(request->ticket,delivery->reply);
        }
        while(!commands.empty()){
            auto command=commands.front();commands.pop_front();
            if(command.first=="reload"){need(!worker.joinable(),"reload while working");form->reload(store->load().documents,epoch);emit({{"event","reloaded"}});continue;}
            const auto& q=*command.second;
            if(command.first=="cancel"){auto result=owner->query("fixture:settings",authority(),q.request,true,now());emit({{"event","cancel-requested"},{"result",result}});continue;}
            request=q;auto admission=owner->submit("fixture:settings","settings",1,authority(),q.body,true,now());emit({{"event","submitted"},{"body",p::parse(q.body)}});
            if(!admission.ticket){form->complete(q.ticket,admission.reply);emit({{"event","result"},{"result",admission.reply}});continue;}
            const auto ticket=owner->take();need(ticket.has_value()&&!worker.joinable(),"worker admission");
            if(mode=="false-saved")gtk_label_set_text(GTK_LABEL(canary),"Saved durably; activation pending. Revision 41");
            worker=std::thread([&,ticket=*ticket]{try{completion.emplace(owner->run(ticket));}catch(...){error=std::current_exception();}done.store(true,std::memory_order_release);});
        }
    }
    void control(const std::string& value){
        if(value=="release")release();
        else if(value=="revoke"){current=policy(current.revision+1);current.disclosure.clear();owner->policy(current);form->policy(current);}
        else if(value=="regrant"){current=policy(current.revision+1);owner->policy(current);form->policy(current);}
        else if(value=="deny"){current=policy(current.revision+1);current.denied_capabilities.insert("settings.commit");owner->policy(current);form->policy(current);}
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
