#include "bundle_identity.hpp"
#include "editor_helpers_linux.hpp"
#include "local_ipc.hpp"
#include "editor_recovery_session.hpp"
#include "../scene/image_fixture.hpp"
#include "../editor/theme_history_fixture.hpp"
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <sys/syscall.h>
#include <thread>

namespace app=syspane::application;namespace os=syspane::platform;namespace v=syspane::rendering;namespace ui=syspane::interfaces;namespace c=syspane::configuration;
namespace {
using c::Json;using Clock=std::chrono::steady_clock;
struct TaskTimes {
    Json calls=Json::array();
    template<class F> auto measure(const char* op,F function)->decltype(function()){
        struct Record {TaskTimes& times;const char* op;Clock::time_point start=Clock::now();~Record(){times.calls.push_back({{"operation",op},{"elapsed_us",std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-start).count()}});}} record{*this,op};
        return function();
    }
};
struct TimedImage final:v::ImageTask {
    TaskTimes& times;std::unique_ptr<v::ImageTask> task;
    TimedImage(TaskTimes& t,std::unique_ptr<v::ImageTask> p):times(t),task(std::move(p)){}
    ~TimedImage() override{times.measure("image.destroy",[&]{task.reset();});}
    v::ImageJobStatus poll()override{return times.measure("image.poll",[&]{return task->poll();});}
    void cancel()override{times.measure("image.cancel",[&]{task->cancel();});}
    syspane::scene::Image take()override{return times.measure("image.take",[&]{return task->take();});}
    std::uint64_t process_id()const override{return times.measure("image.process",[&]{return task->process_id();});}
};
struct TimedRecovery final:os::RecoveryTask {
    TaskTimes& times;std::unique_ptr<os::RecoveryTask> task;
    TimedRecovery(TaskTimes& t,std::unique_ptr<os::RecoveryTask> p):times(t),task(std::move(p)){}
    ~TimedRecovery() override{times.measure("recovery.destroy",[&]{task.reset();});}
    std::uint64_t replace(std::string bytes)override{return times.measure("recovery.replace",[&]{return task->replace(std::move(bytes));});}
    std::uint64_t retire()override{return times.measure("recovery.retire",[&]{return task->retire();});}
    os::RecoveryQueueStatus poll()override{return times.measure("recovery.poll",[&]{return task->poll();});}
    os::RecoveryQueueStatus status()const override{return times.measure("recovery.status",[&]{return task->status();});}
    std::optional<os::RecoveryCompletion> take()override{return times.measure("recovery.take",[&]{return task->take();});}
    void close()override{times.measure("recovery.close",[&]{task->close();});}
};
struct TimedPreparation final:ui::RecoveryPreparationTask {
    TaskTimes& times;std::unique_ptr<ui::RecoveryPreparationTask> task;
    TimedPreparation(TaskTimes& t,std::unique_ptr<ui::RecoveryPreparationTask> p):times(t),task(std::move(p)){}
    ~TimedPreparation() override{times.measure("preparation.destroy",[&]{task.reset();});}
    ui::RecoveryPreparationStatus status()const override{return times.measure("preparation.status",[&]{return task->status();});}
    std::unique_ptr<ui::RecoveryPrepared> take()override{return times.measure("preparation.take",[&]{return task->take();});}
    void cancel()override{times.measure("preparation.cancel",[&]{task->cancel();});}
};
struct TimedHistory final:ui::HistoryPreparationTask {
    TaskTimes& times;std::unique_ptr<ui::HistoryPreparationTask> task;
    TimedHistory(TaskTimes& t,std::unique_ptr<ui::HistoryPreparationTask> p):times(t),task(std::move(p)){}
    ~TimedHistory() override{times.measure("history.destroy",[&]{task.reset();});}
    ui::HistoryPreparationStatus status()const override{return times.measure("history.status",[&]{return task->status();});}
    std::unique_ptr<ui::HistoryPrepared> take()override{return times.measure("history.take",[&]{return task->take();});}
    void cancel()override{times.measure("history.cancel",[&]{task->cancel();});}
};
void need(bool ok,const char* code){if(!ok)throw syspane::protocol::Error(code);}
struct TimedRequest final:ui::RequestPreparationTask {
    TaskTimes& times;std::unique_ptr<ui::RequestPreparationTask> task;
    TimedRequest(TaskTimes& t,std::unique_ptr<ui::RequestPreparationTask> p):times(t),task(std::move(p)){}
    ~TimedRequest() override{times.measure("request.destroy",[&]{task.reset();});}
    ui::RequestPreparationStatus status()const override{return times.measure("request.status",[&]{return task->status();});}
    std::unique_ptr<ui::RequestPrepared> take()override{return times.measure("request.take",[&]{return task->take();});}
    void cancel()override{times.measure("request.cancel",[&]{task->cancel();});}
};
std::string read(const std::string& path){std::ifstream f(path,std::ios::binary);need(static_cast<bool>(f),"probe.input");std::string bytes{std::istreambuf_iterator<char>(f),{}};need(bytes.size()<=8388609,"probe.capacity");return bytes;}
void emit(const Json& value){std::cout<<value.dump()<<std::endl;}
const char* image_state(v::ImageJobState s){switch(s){case v::ImageJobState::running:return "running";case v::ImageJobState::stopping:return "stopping";case v::ImageJobState::ready:return "ready";case v::ImageJobState::failed:return "failed";case v::ImageJobState::cancelled:return "cancelled";case v::ImageJobState::consumed:return "consumed";}return "invalid";}
const char* recovery_state(os::RecoveryQueueState s){switch(s){case os::RecoveryQueueState::loading:return "loading";case os::RecoveryQueueState::ready:return "ready";case os::RecoveryQueueState::busy:return "busy";case os::RecoveryQueueState::retiring:return "retiring";case os::RecoveryQueueState::retired:return "retired";case os::RecoveryQueueState::unavailable:return "unavailable";case os::RecoveryQueueState::closing:return "closing";case os::RecoveryQueueState::closed:return "closed";}return "invalid";}
const char* session_state(ui::EditorRecoveryState s){switch(s){case ui::EditorRecoveryState::disabled:return "disabled";case ui::EditorRecoveryState::loading:return "loading";case ui::EditorRecoveryState::offer:return "offer";case ui::EditorRecoveryState::ready:return "ready";case ui::EditorRecoveryState::capturing:return "capturing";case ui::EditorRecoveryState::retiring:return "retiring";case ui::EditorRecoveryState::kept:return "kept";case ui::EditorRecoveryState::unavailable:return "unavailable";}return "invalid";}
Json state(const os::RecoveryQueueStatus& s){return {{"state",recovery_state(s.state)},{"active",s.active},{"pending",s.pending},{"pid",s.process},{"bytes",s.retained_bytes},{"reaped",s.reaped},{"error",s.error}};}
Json state(const app::EditorHelperStatus& s){return {{"attached",s.attached},{"closing",s.closing},{"stopped",s.stopped},{"images",s.image_handles},{"recovery",s.recovery_handles},{"bytes",s.retained_bytes},{"processes",s.processes}};}
struct Worker {
    app::EditorHelperClient& client;std::mutex mutex;std::condition_variable condition;
    bool ready=false,quit=false;std::uint64_t requested=0,completed=0;long tid=0;std::string error;
    app::RecoveryAdmissionFactory admission;std::thread thread;
    explicit Worker(app::EditorHelperClient& c,app::RecoveryAdmissionFactory a={}):client(c),admission(std::move(a)),thread([this]{run();}){
        std::unique_lock<std::mutex> lock(mutex);
        if(!condition.wait_for(lock,std::chrono::seconds(10),[&]{return ready;})){
            quit=true;condition.notify_all();lock.unlock();thread.join();throw syspane::protocol::Error("probe.worker_timeout");
        }
        if(!error.empty()){lock.unlock();thread.join();throw std::runtime_error(error);}
    }
    void run(){try{
        auto installation=std::make_shared<os::LinuxInstallation>(os::built_helper_bundle_expectation());app::LinuxEditorHelperOwner owner(client,installation,admission);
        {std::lock_guard<std::mutex> lock(mutex);tid=::syscall(SYS_gettid);ready=true;condition.notify_all();}
        for(;;){
            {std::unique_lock<std::mutex> lock(mutex);condition.wait(lock,[&]{return quit||requested!=completed;});if(quit)break;}
            owner.poll();
            {std::lock_guard<std::mutex> lock(mutex);++completed;condition.notify_all();}
        }
    }catch(const std::exception& e){std::lock_guard<std::mutex> lock(mutex);error=e.what();ready=true;condition.notify_all();}}
    void step(){std::unique_lock<std::mutex> lock(mutex);++requested;condition.notify_all();need(condition.wait_for(lock,std::chrono::seconds(8),[&]{return completed==requested||!error.empty();})&&error.empty(),"probe.worker_timeout");}
    void start(){std::lock_guard<std::mutex> lock(mutex);need(requested==completed,"probe.worker_busy");++requested;condition.notify_all();}
    bool busy(){std::lock_guard<std::mutex> lock(mutex);need(error.empty(),"probe.worker_error");return completed!=requested;}
    void stop(){client.close();{std::lock_guard<std::mutex> lock(mutex);quit=true;condition.notify_all();}if(thread.joinable())thread.join();}
    ~Worker(){stop();}
};
}
int main(int argc,char** argv){try{
    need((argc==2||argc==3)&&os::unprivileged_context(),"probe.arguments");const std::string root=argv[1];app::EditorHelperClient client;
    app::RecoveryAdmissionFactory admission;
    if(argc==3){
        const std::string file=argv[2];const auto data=Json::parse(read(file));const auto& v=data.at("observation");const auto& d=v.at("directory");
        os::ProfileLocation location{data["location"]["profile"],"","","","",data["location"]["portable_root"].get<std::string>()};
        c::ProfileRecoveryView view{{v["profile"],v["generation"],{d["path"],d["uid"],d["state_device"],d["state_inode"],d["recovery_device"],d["recovery_inode"]},v["policy_revision"],v["erase"]},v["connection"],v["epoch"],v["session"],v["transfer"],v["revision"]};
        admission=[location,view,file,cached=std::shared_ptr<app::LinuxRecoveryAdmission>{}]()mutable{
            if(!cached)cached=std::make_shared<app::LinuxRecoveryAdmission>(location,view,[file]()->std::optional<app::RecoverySessionAuthority>{
                const auto a=Json::parse(read(file)).at("current");if(a.is_null())return {};
                return app::RecoverySessionAuthority{a["connection"],a["epoch"],a["profile"],a["session"],a["revision"],a["policy_revision"],a["retain"],a["erase"]};
            });return cached;
        };
    }
    std::string before;try{client.images()("image/png","x");}catch(const std::exception& e){before=e.what();}
    TaskTimes times;
    const v::ImageFactory image_factory=[&](std::string media,std::string bytes){auto task=times.measure("image.create",[&]{return client.images()(std::move(media),std::move(bytes));});return std::make_unique<TimedImage>(times,std::move(task));};
    auto recovery_factory=std::make_shared<const os::RecoveryFactory>([&](std::string path,os::RecoveryContext context){auto task=times.measure("recovery.create",[&]{return (*client.recovery())(std::move(path),std::move(context));});return std::make_unique<TimedRecovery>(times,std::move(task));});
    auto preparations=std::make_shared<const ui::RecoveryPreparationFactory>([&](std::unique_ptr<ui::RecoveryWork> input){auto task=times.measure("preparation.create",[&]{return (*client.preparations())(std::move(input));});return std::make_unique<TimedPreparation>(times,std::move(task));});
    const ui::HistoryPreparationFactory histories=[&](std::unique_ptr<ui::HistoryWork> input){auto task=times.measure("history.create",[&]{return (*client.history_preparations())(std::move(input));});return std::make_unique<TimedHistory>(times,std::move(task));};
    const ui::RequestPreparationFactory requests=[&](std::unique_ptr<ui::RequestWork> input){auto task=times.measure("request.create",[&]{return (*client.request_preparations())(std::move(input));});return std::make_unique<TimedRequest>(times,std::move(task));};
    Worker worker(client,std::move(admission));emit({{"event","ready"},{"worker",worker.tid},{"before_attach",before},{"status",state(client.status())}});
    std::map<std::uint64_t,std::unique_ptr<v::ImageTask>> images;std::uint64_t ids=0;
    std::unique_ptr<os::RecoveryTask> recovery;std::unique_ptr<v::SceneSurface> surface;
    std::unique_ptr<ui::EditorDraft> draft;std::unique_ptr<ui::EditorRecoverySession> session;std::uint64_t clock=0;
    std::unique_ptr<ui::RecoveryPreparationTask> preparation;std::unique_ptr<ui::RecoveryPrepared> prepared;bool capture=false,asynchronous=false;
    std::unique_ptr<ui::HistoryPreparationTask> history;std::unique_ptr<ui::HistoryPrepared> history_result;std::unique_ptr<ui::EditorDraft> capacity_draft;
    std::unique_ptr<ui::RequestPreparationTask> request;std::unique_ptr<ui::RequestPrepared> request_result;
    const auto recovery_cases=settings_fixture::read(root+"/tests/editor/recovery-draft-cases.json");
    const ui::RecoveryIdentity recovery_identity{recovery_cases["identity"]["profile"],recovery_cases["identity"]["generation"]};
    auto make_draft=[&]{
        need(!draft,"probe.active");settings_fixture::Fixture f(root);auto grant=theme_history_fixture::policy();grant.disclosure[{"desktop","history"}]={"sensitive"};
        auto resources=theme_history_fixture::context(f);resources.capabilities.insert("editor.recovery");draft=std::make_unique<ui::EditorDraft>(theme_history_fixture::authority(),grant,f.authored,"E1",resources,true);
    };
    auto history_snapshot=[&]()->Json{need(static_cast<bool>(draft),"probe.draft");return {{"scene",*draft->scene()},{"selection",draft->selection()},{"undo",draft->undo_count()},{"redo",draft->redo_count()}};};
    std::string line;
    while(std::getline(std::cin,line)){
        need(line.size()<=65536,"probe.capacity");const auto q=Json::parse(line);const std::string op=q.at("op");Json reply;std::string input;
        if(q.contains("file"))input=read(q.at("file"));
        times.calls=Json::array();const auto began=Clock::now();
        try{
            if(op=="pump"){worker.step();reply=state(client.status());}
            else if(op=="pump-start"){worker.start();reply={{"started",true}};}
            else if(op=="worker-state")reply={{"busy",worker.busy()}};
            else if(op=="worker-exit"){worker.stop();reply={{"stopped",true}};}
            else if(op=="status")reply=state(client.status());
            else if(op=="history-fixture"){
                make_draft();capacity_draft=std::make_unique<ui::EditorDraft>(*draft);
                capacity_draft->execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"Capacity"}});
                if(q.value("large",false)){
                    std::vector<ui::SceneEdit> edits;const auto initial=draft->scene()->at("widgets").size(),roots=draft->scene()->at("roots").size();
                    for(std::size_t n=initial;n<256;++n){
                        auto w=draft->scene()->at("widgets")[0];w["id"]="history:"+std::to_string(n);w["content"]["body"]=std::string(512,'x');edits.push_back(ui::InsertWidget{w,std::nullopt,roots+n-initial});
                        if(edits.size()==128){draft->execute(edits);edits.clear();}
                    }
                    if(!edits.empty())draft->execute(edits);
                }
                draft->select({"widget:text"});draft->execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"First"}});
                draft->select({});draft->execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,"Second"}});reply={{"created",true}};
            }else if(op=="history-create"||op=="history-consumed"){
                need(draft&&!history&&!history_result,"probe.active");auto work=times.measure("history.work",[&]{return draft->history_work(q.value("forward",false));});
                if(work&&op=="history-consumed"){
                    std::exception_ptr error;std::thread first([&]{try{(void)work->run();}catch(...){error=std::current_exception();}});first.join();if(error)std::rethrow_exception(error);
                }
                if(work){history=histories(std::move(work));reply={{"created",true}};}else reply={{"created",false}};
            }else if(op=="history-null"){auto extra=histories({});reply={{"created",true}};
            }else if(op=="history-capacity"){
                need(static_cast<bool>(capacity_draft),"probe.draft");auto extra=histories(capacity_draft->history_work(false));reply={{"created",true}};
            }else if(op=="history-poll"){
                need(static_cast<bool>(history),"probe.history");const auto s=history->status();reply={{"ready",s.ready},{"stopped",s.stopped},{"running",s.running},{"error",s.error},{"handles",client.status().history_handles}};
            }else if(op=="history-handles")reply={{"handles",client.status().history_handles}};
            else if(op=="history-take"){need(static_cast<bool>(history),"probe.history");history_result=history->take();reply={{"taken",true}};}
            else if(op=="history-adopt"){need(draft&&history_result,"probe.history");times.measure("history.adopt",[&]{draft->adopt_history(std::move(history_result));});reply=history_snapshot();}
            else if(op=="history-snapshot")reply=history_snapshot();
            else if(op=="history-select"){need(static_cast<bool>(draft),"probe.draft");draft->select({});reply={{"selected",true}};}
            else if(op=="history-cancel"){need(static_cast<bool>(history),"probe.history");history->cancel();reply={{"cancelled",true}};}
            else if(op=="history-drop"){history_result.reset();history.reset();reply={{"dropped",true},{"handles",client.status().history_handles}};}
            else if(op=="history-wrong-thread"){
                need(history&&capacity_draft,"probe.history");std::vector<std::string> errors;auto work=capacity_draft->history_work(false);const auto factory=client.history_preparations();
                std::thread other([&]{
                    try{history->status();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{history->take();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{history->cancel();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{(*factory)(std::move(work));}catch(const std::exception& e){errors.emplace_back(e.what());}
                });other.join();reply={{"errors",errors}};
            }
            else if(op=="request-create"||op=="request-consumed"||op=="request-reuse"){
                need(draft&&!request&&!request_result,"probe.active");
                auto& origin=op=="request-reuse"?*capacity_draft:*draft;
                auto work=times.measure("request.work",[&]{return origin.request_work(q.value("intent",std::string("commit")),"request:native");});
                if(work&&op=="request-consumed"){
                    std::exception_ptr error;std::thread first([&]{try{(void)work->run();}catch(...){error=std::current_exception();}});first.join();if(error)std::rethrow_exception(error);
                }
                if(work){request=requests(std::move(work));reply={{"created",true}};}else reply={{"created",false}};
            }else if(op=="request-null"){auto extra=requests({});reply={{"created",true}};
            }else if(op=="request-unattached"){
                need(static_cast<bool>(capacity_draft),"probe.draft");app::EditorHelperClient other;
                auto extra=(*other.request_preparations())(capacity_draft->request_work("commit","unattached"));reply={{"created",true}};
            }else if(op=="request-capacity"){
                need(static_cast<bool>(capacity_draft),"probe.draft");auto extra=requests(capacity_draft->request_work("commit","capacity"));reply={{"created",true}};
            }else if(op=="request-poll"){
                need(static_cast<bool>(request),"probe.request");const auto s=request->status();reply={{"ready",s.ready},{"stopped",s.stopped},{"running",s.running},{"error",s.error},{"handles",client.status().request_handles}};
            }else if(op=="request-handles")reply={{"handles",client.status().request_handles}};
            else if(op=="request-take"){need(static_cast<bool>(request),"probe.request");request_result=request->take();reply={{"taken",true}};}
            else if(op=="request-adopt"){
                need(draft&&request_result,"probe.request");auto value=times.measure("request.adopt",[&]{return draft->adopt_request(std::move(request_result));});
                reply={{"ticket",value.ticket},{"epoch",value.epoch},{"request",value.request},{"command",c::parse_command(value.body)}};
            }else if(op=="request-active"){need(static_cast<bool>(draft),"probe.draft");reply={{"active",draft->active_request().has_value()}};}
            else if(op=="request-cancel"){need(static_cast<bool>(request),"probe.request");request->cancel();reply={{"cancelled",true}};}
            else if(op=="request-drop"){request_result.reset();request.reset();reply={{"dropped",true},{"handles",client.status().request_handles}};}
            else if(op=="request-policy"){
                need(static_cast<bool>(draft),"probe.draft");auto p=theme_history_fixture::policy(q.value("deny",true)?8:9);
                p.disclosure[{"desktop","history"}]={"sensitive"};if(q.value("deny",true))p.denied_capabilities.insert("settings.commit");
                draft->policy(std::move(p));reply={{"changed",true}};
            }else if(op=="request-wrong-thread"){
                need(request&&capacity_draft,"probe.request");std::vector<std::string> errors;
                auto work=capacity_draft->request_work("commit","other");const auto factory=client.request_preparations();
                std::thread other([&]{
                    try{request->status();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{request->take();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{request->cancel();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{(*factory)(std::move(work));}catch(const std::exception& e){errors.emplace_back(e.what());}
                    try{client.request_preparations();}catch(const std::exception& e){errors.emplace_back(e.what());}
                });other.join();reply={{"errors",errors}};
            }
            else if(op=="draft"){make_draft();reply={{"created",true}};}
            else if(op=="prepare"){
                need(draft&&!preparation&&!prepared,"probe.active");capture=q.value("capture",false);
                auto work=times.measure("draft.work",[&]{return capture?draft->recovery_capture_work(recovery_identity):draft->recovery_restore_work(std::move(input),recovery_identity);});
                preparation=(*preparations)(std::move(work));reply={{"created",true}};
            }else if(op=="preparation-poll"){
                need(static_cast<bool>(preparation),"probe.preparation");const auto s=preparation->status();reply={{"ready",s.ready},{"stopped",s.stopped},{"running",s.running},{"error",s.error},{"handles",client.status().preparation_handles}};
            }else if(op=="preparation-capacity"){
                need(static_cast<bool>(draft),"probe.draft");auto work=times.measure("draft.work",[&]{return draft->recovery_capture_work(recovery_identity);});auto extra=(*preparations)(std::move(work));reply={{"created",true}};
            }else if(op=="preparation-take"){
                need(static_cast<bool>(preparation),"probe.preparation");prepared=preparation->take();
                if(capture){auto bytes=times.measure("draft.capture",[&]{return draft->recovery_capture(std::move(prepared),recovery_identity);});reply={{"bytes",bytes?Json(*bytes):Json()}};}
                else{const auto info=times.measure("draft.inspect",[&]{return draft->inspect_recovery(*prepared,recovery_identity);});reply={{"revision",info.revision},{"widgets",info.widgets},{"theme_changed",info.theme_changed}};}
            }else if(op=="preparation-restore"){
                need(draft&&prepared,"probe.preparation");const bool changed=times.measure("draft.restore",[&]{return draft->restore_recovery(std::move(prepared),recovery_identity);});reply={{"changed",changed},{"scene",*draft->scene()},{"undo",draft->undo_count()}};
            }else if(op=="preparation-cancel"){need(static_cast<bool>(preparation),"probe.preparation");preparation->cancel();prepared.reset();reply={{"cancelled",true}};}
            else if(op=="preparation-drop"){prepared.reset();preparation.reset();reply={{"dropped",true},{"handles",client.status().preparation_handles}};}
            else if(op=="draft-edit"){
                need(draft&&(!session||session->editing()),"probe.draft");
                if(q.contains("title"))draft->execute({ui::WidgetPropertyEdit{"widget:text",ui::WidgetProperty::title,q.at("title")}});
                else{std::vector<ui::SceneEdit> edits{ui::RemoveWidgets{draft->scene()->at("roots").get<std::vector<std::string>>()}};std::size_t index=0;
                    for(const auto& w:recovery_cases["scene"]["widgets"])edits.push_back(ui::InsertWidget{w,std::nullopt,index++});
                    draft->execute(edits);}
                if(session)times.measure("session.changed",[&]{session->changed();});
                reply={{"scene",*draft->scene()}};
            }else if(op=="draft-discard"){need(static_cast<bool>(draft),"probe.draft");draft->discard();if(session)times.measure("session.changed",[&]{session->changed();});reply={{"scene",*draft->scene()}};}
            else if(op=="image"){auto task=image_factory(q.at("media"),std::move(input));const auto id=++ids;images.emplace(id,std::move(task));reply={{"id",id}};}
            else if(op=="image-poll"){auto& image=*images.at(q.at("id"));const auto s=image.poll();reply={{"state",image_state(s.state)},{"reaped",s.reaped},{"reason",s.reason},{"pid",image.process_id()}};}
            else if(op=="image-take"){auto result=images.at(q.at("id"))->take();need(result.rgba.size()<=65536,"probe.capacity");reply={{"width",result.width},{"height",result.height},{"rgba",result.rgba}};}
            else if(op=="image-cancel"){images.at(q.at("id"))->cancel();reply={{"cancelled",true}};}
            else if(op=="image-drop"){need(images.erase(q.at("id"))==1,"probe.image");reply={{"dropped",true}};}
            else if(op=="recovery"){
                need(!recovery,"probe.active");const std::string grant=q.value("grants",std::string("rwe"));
                recovery=(*recovery_factory)(q.at("directory"),os::RecoveryContext{q.value("session",std::string("editor:worker")),q.value("profile",std::string("profile:primary")),q.value("generation",std::string(64,'4')),q.value("policy_revision",std::uint64_t{7}),grant.find('r')!=std::string::npos,grant.find('w')!=std::string::npos,grant.find('e')!=std::string::npos});reply=state(recovery->status());
            }else if(op=="recovery-poll"){need(static_cast<bool>(recovery),"probe.recovery");reply=state(recovery->poll());}
            else if(op=="replace"){need(static_cast<bool>(recovery),"probe.recovery");reply={{"ticket",recovery->replace(std::move(input))}};}
            else if(op=="retire"){need(static_cast<bool>(recovery),"probe.recovery");reply={{"ticket",recovery->retire()}};}
            else if(op=="recovery-take"){
                need(static_cast<bool>(recovery),"probe.recovery");auto result=recovery->take();reply=nullptr;
                if(result)reply={{"ticket",result->ticket},{"operation",result->operation},{"outcome",result->outcome},{"error",result->error},{"bytes",result->bytes?Json(*result->bytes):Json()},
                    {"digest",result->digest?Json(*result->digest):Json()},{"pending",result->pending},{"context",{{"session",result->context.session},{"profile",result->context.profile},{"generation",result->context.generation},{"revision",result->context.policy_revision}}}};
            }else if(op=="recovery-close"){need(static_cast<bool>(recovery),"probe.recovery");recovery->close();reply=state(recovery->status());}
            else if(op=="recovery-drop"){recovery.reset();reply={{"dropped",true}};}
            else if(op=="wrong-thread"){
                std::vector<std::string> errors;std::thread other([&]{
                    try{client.status();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    if(!images.empty())try{images.begin()->second->poll();}catch(const std::exception& e){errors.emplace_back(e.what());}
                    if(recovery)try{recovery->status();}catch(const std::exception& e){errors.emplace_back(e.what());}
                });other.join();reply={{"errors",errors}};
            }else if(op=="surface"){
                need(!surface,"probe.active");auto cfg=fixture::image_config(root+"/spec/fixtures/valid");
                surface=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},fixture::chart_policy(),std::move(cfg),std::vector<v::SurfaceProvider>{},[]{return true;},"",v::SurfaceAudience::desktop,image_factory);reply={{"created",true}};
            }else if(op=="surface-paint"){
                need(static_cast<bool>(surface),"probe.surface");surface->paint(++clock,{},[&](auto code,const v::SurfaceFrame* frame){
                    need(frame&&(code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded),"probe.surface");std::vector<unsigned char> pixels;
                    for(unsigned y=0;y<5;++y)for(unsigned x=0;x<9;++x)for(unsigned c=0;c<4;++c)pixels.push_back(frame->displays[0].rgba[(y*frame->displays[0].width+x)*4+c]);
                    reply={{"state",frame->widgets[0].image->state},{"width",9},{"height",5},{"rgba",pixels}};
                });
            }else if(op=="surface-close"){need(static_cast<bool>(surface),"probe.surface");surface->close();const bool done=surface->poll_image_jobs();if(done)surface.reset();reply={{"stopped",done}};
            }else if(op=="session"){
                need(!session&&!draft,"probe.active");make_draft();asynchronous=q.value("asynchronous",false);
                const auto& cases=recovery_cases;session=std::make_unique<ui::EditorRecoverySession>(*draft,recovery_factory,q.at("directory"),asynchronous?preparations:nullptr);
                session->bind({"editor:worker",cases["identity"]["profile"],cases["identity"]["generation"],7,true});reply={{"created",true}};
            }else if(op=="session-poll"){
                need(static_cast<bool>(session),"probe.session");if(asynchronous)times.measure("session.poll",[&]{session->poll();});else session->poll();
                reply={{"state",session_state(session->state())},{"editing",session->editing()},{"may_apply",session->may_apply()},{"restorable",session->restorable()},{"stopped",session->stopped()},{"scene",draft->scene()?*draft->scene():Json()},{"undo",draft->undo_count()},{"preparations",client.status().preparation_handles},{"cancelled",session->cancelled()}};
            }else if(op=="session-restore"){need(static_cast<bool>(session),"probe.session");if(asynchronous)times.measure("session.restore",[&]{session->restore();});else session->restore();reply={{"restored",true}};}
            else if(op=="session-keep"){need(static_cast<bool>(session),"probe.session");times.measure("session.keep",[&]{session->keep();});reply={{"kept",true}};}
            else if(op=="session-discard"){need(static_cast<bool>(session),"probe.session");times.measure("session.discard",[&]{session->discard();});reply={{"discarded",true}};}
            else if(op=="session-cancel"){need(static_cast<bool>(session),"probe.session");times.measure("session.cancel",[&]{session->cancel_session();});reply={{"cancelled",true}};}
            else if(op=="session-invalidate"){need(static_cast<bool>(session),"probe.session");times.measure("session.invalidate",[&]{session->invalidate();});draft->disconnected();reply={{"invalidated",true}};}
            else if(op=="session-close"){need(static_cast<bool>(session),"probe.session");session->close();session->poll();const bool done=session->stopped();if(done){session.reset();draft.reset();}reply={{"stopped",done}};}
            else if(op=="close"){client.close();reply=state(client.status());}
            else if(op=="quit"){need(client.status().stopped&&images.empty()&&!recovery&&!surface&&!session&&!preparation&&!prepared&&!history&&!history_result&&!request&&!request_result,"probe.active");emit({{"reply",{{"exit",true}}},{"elapsed_us",0},{"task_calls",times.calls}});return 0;}
            else throw syspane::protocol::Error("probe.operation");
        }catch(const std::exception& e){reply={{"error",e.what()}};}
        const auto elapsed=std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-began).count();emit({{"reply",reply},{"elapsed_us",elapsed},{"task_calls",times.calls}});
    }
    return 2;
}catch(const std::exception& e){emit({{"error",e.what()}});return 2;}}
