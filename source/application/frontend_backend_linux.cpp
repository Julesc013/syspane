#include "frontend_linux.hpp"
#include "profile_supervisor_linux.hpp"
#include "runtime_directory_linux.hpp"
#include "editor_helpers_linux.hpp"
#include "local_ipc.hpp"
#include "reconciliation.hpp"
#include "digest.hpp"
#include <atomic>
#include <deque>
#include <limits>
#include <mutex>
#include <thread>
#include <utility>
#include <unistd.h>

namespace syspane::application {
namespace c=configuration;namespace p=protocol;namespace os=platform;namespace ui=interfaces;
namespace {
void need(bool ok,const char* code){if(!ok)throw p::Error(code);}
void increment(std::uint64_t& n){need(n<std::numeric_limits<std::uint64_t>::max(),"frontend.capacity");++n;}
void pause(){std::this_thread::sleep_for(std::chrono::milliseconds(10));}
const std::set<std::string> capabilities={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides","editor.recovery"};
bool same_directory(const c::ProfileRecoveryDirectory& a,const c::ProfileRecoveryDirectory& b){
    return a.path==b.path&&a.uid==b.uid&&a.state_device==b.state_device&&a.state_inode==b.state_inode&&a.recovery_device==b.recovery_device&&a.recovery_inode==b.recovery_inode;
}
p::Handshake offer(){
    p::Handshake h;h.role="console";h.epoch="frontend";h.max_frame_bytes=p::large_command_frame_floor;
    for(const char* version:{"0.2.0","0.3.0","0.4.0","0.5.0","0.6.0","0.7.0","0.8.0"})h.documents.emplace("command",version);
    for(const char* document:{"command-result","profile-request","profile-result","reconciliation-request","reconciliation-result"})h.documents.emplace(document,"0.1.0");
    for(const char* document:{"profile-request","profile-result"})h.documents.emplace(document,"0.2.0");
    h.required={"configuration.transactions","configuration.content","configuration.scene-content","configuration.large-commands","configuration.edit-locks",
        "configuration.visibility","configuration.theme-overrides","configuration.profile","configuration.recovery-context","settings.preview","result.get","cancel","result.reconcile"};return h;
}
c::Json hello(const p::Handshake& h){
    c::Json docs=c::Json::array();for(const auto& d:h.documents)docs.push_back({{"document",d.first},{"version",d.second}});
    return {{"wire_major",0},{"wire_minor",1},{"role",h.role},{"producer_epoch",h.epoch},{"max_frame_bytes",h.max_frame_bytes},
        {"document_versions",docs},{"required_features",h.required},{"optional_features",c::Json::array()}};
}
}
struct LinuxFrontendBackend::Impl {
    struct Capture {c::ProfileRecoveryView source;std::string digest;};
    struct Pending {ui::EditRequest request;std::string intent;std::uint64_t revision=0;bool dispatched=false,cancel=false,retrieve=false;std::optional<Capture> capture;};
    os::HelperBundleExpectation expectation;std::string runtime_base;os::ProfileLocation location;
    EditorHelperClient helpers;
    std::mutex mutex;std::thread supervisor_worker,client_worker;
    std::atomic<bool> closing{false},supervisor_done{false},client_done{false};
    ProfileSupervisorView controller;std::uint64_t generation=0,requests=0,profiles=0,sessions=0,retries=0,last_retry=0;
    FrontendView view;std::optional<Pending> pending;bool reload_requested=false;
    std::unique_ptr<ui::PreparedEditor> prepared_editor;const bool recovery_admitted;
    std::optional<RecoverySessionAuthority> recovery_authority;
    std::optional<Capture> retirement;
    Impl(os::HelperBundleExpectation e,std::string base,os::ProfileLocation l,bool recovery):expectation(std::move(e)),runtime_base(std::move(base)),location(std::move(l)),recovery_admitted(recovery){
        view.status="Starting configuration service.";
    }
    bool valid_unlocked(std::uint64_t token)const{return !closing&&generation==token&&controller.state==ProfileSupervisorState::ready;}
    void valid(std::uint64_t token){std::lock_guard<std::mutex> lock(mutex);need(valid_unlocked(token),"frontend.withdrawn");}
    void withdraw(const char* status){
        prepared_editor.reset();
        recovery_authority.reset();
        view.profile.reset();view.reply.reset();view.loading=true;view.status=status;increment(view.withdrawal);
        if(pending){pending->request.body.clear();if(!pending->dispatched)pending.reset();}
    }
    std::optional<RecoverySessionAuthority> authority(){
        std::lock_guard<std::mutex> lock(mutex);
        if(closing||view.loading||!view.profile||controller.state!=ProfileSupervisorState::ready)return {};
        return recovery_authority;
    }
    std::shared_ptr<LinuxRecoveryAdmission> admit_recovery(){
        std::optional<c::ProfileRecoveryView> context;
        {std::lock_guard<std::mutex> lock(mutex);if(view.profile)context=view.profile->view.recovery;}
        need(context.has_value(),"frontend.recovery_unavailable");
        return std::make_shared<LinuxRecoveryAdmission>(location,std::move(*context),[this]{return authority();});
    }
    void supervise(){
        try{
            auto installation=std::make_shared<os::LinuxInstallation>(expectation);
            os::LinuxRuntimeDirectory runtime(runtime_base);
            {
                LinuxEditorHelperOwner helper(helpers,installation,[this]{return admit_recovery();});
                LinuxProfileSupervisor owner(installation,runtime.path(),location,true,static_cast<std::uint64_t>(::getpid()));
                bool stopped=false;
                while(!stopped){
                    if(closing){owner.close();helper.close();}
                    auto next=owner.poll();owner.take();
                    const bool helpers_stopped=helper.poll();
                    {
                        std::lock_guard<std::mutex> lock(mutex);
                        if(next.epoch!=controller.epoch||next.process!=controller.process||
                           (next.state==ProfileSupervisorState::ready)!=(controller.state==ProfileSupervisorState::ready)){
                            increment(generation);withdraw(closing?"Closing; waiting for configuration service to stop.":"Configuration connection unavailable.");
                        }
                        controller=std::move(next);stopped=controller.state==ProfileSupervisorState::closed&&helpers_stopped;
                        if(controller.state==ProfileSupervisorState::circuit_open||controller.state==ProfileSupervisorState::unavailable)
                            view.status="Configuration service unavailable. Close and restart after checking installation and policy.";
                    }
                    if(!stopped)pause();
                }
            }
            runtime.cleanup();
        }catch(...){std::lock_guard<std::mutex> lock(mutex);withdraw("Settings unavailable. Check installation, runtime and policy configuration.");view.failed=true;}
        supervisor_done=true;
    }
    struct Connection {
        Impl& owner;std::uint64_t token;ProfileSupervisorView controller;
        os::Stream stream;p::Framer framer{p::large_command_frame_floor};p::Negotiated selected{};
        std::deque<std::pair<p::Message,std::size_t>> incoming;std::size_t queued=0;std::string id;
        std::uint64_t sequence=0,sent=0,echo=0,last_sent=0,query_counter=0;
        std::string query,editor_session;bool recovering=false,profile_reading=false,retrieval_wait=false;
        std::uint64_t profile_started=0,profile_last=0,retrieval_started=0;
        std::unique_ptr<c::ProfileDownload> download;
        std::string terminal_id,terminal_hash;
        Connection(Impl& o,std::uint64_t t,ProfileSupervisorView v):owner(o),token(t),controller(std::move(v)),stream(os::Stream::connect(controller.endpoint,controller.process)){owner.valid(token);}
        void send(const std::string& type,const c::Json& body){
            owner.valid(token);c::Json value={{"type",type},{"body",body}};
            if(type!="hello"){value["connection_id"]=id;value["producer_epoch"]=controller.epoch;}
            stream.write(p::frame(value.dump(),p::large_command_frame_floor),100);owner.valid(token);
        }
        std::string query_id(){increment(query_counter);return "query:"+std::to_string(query_counter);}
        void input(){
            owner.valid(token);char bytes[4096];const auto got=stream.read(bytes,sizeof bytes,10);need(!got.eof,"frontend.eof");
            framer.feed({bytes,got.bytes},got.observed_ms,[&](auto raw){
                need(incoming.size()<16&&raw.size()<=65536-queued,"frontend.queue");queued+=raw.size();
                incoming.emplace_back(p::decode(raw),raw.size());
            });framer.tick(os::monotonic_ms());
        }
        p::Message pop(){auto m=std::move(incoming.front().first);queued-=incoming.front().second;incoming.pop_front();return m;
        }
        void deadlines(){
            owner.valid(token);const auto now=os::monotonic_ms();framer.tick(now);
            if(sent!=echo)need(now-last_sent<3000,"frontend.heartbeat_timeout");
            if(profile_reading)need(now-profile_last<5000&&now-profile_started<60000,"frontend.profile_timeout");
            if(retrieval_wait)need(now-retrieval_started<5000,"frontend.result_timeout");
        }
        void handshake(){
            const auto offered=offer();send("hello",hello(offered));const auto started=os::monotonic_ms();
            while(incoming.empty()){need(os::monotonic_ms()-started<5000,"frontend.handshake_timeout");input();}
            need(os::monotonic_ms()-started<5000,"frontend.handshake_timeout");auto welcome=pop();
            need(welcome.type=="welcome"&&welcome.producer_epoch==controller.epoch,"frontend.welcome");const auto h=p::handshake(welcome.body);
            need(h.role=="console"&&h.epoch==controller.epoch&&h.minor==1&&h.max_frame_bytes==offered.max_frame_bytes&&h.required.empty()&&
                 h.optional==offered.required&&h.documents==offered.documents,"frontend.negotiation");
            id=welcome.connection_id;selected={h.minor,h.max_frame_bytes,h.documents,h.optional};framer.restrict_limit(selected.max_frame_bytes);
            std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token),"frontend.withdrawn");
            recovering=owner.pending.has_value();if(owner.pending)owner.pending->retrieve=true;else owner.reload_requested=true;
            owner.view.status=recovering?"Retrieving the original request.":"Loading saved settings.";
        }
        void profile(){
            {std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token),"frontend.withdrawn");
                owner.prepared_editor.reset();
                owner.recovery_authority.reset();increment(owner.sessions);editor_session=controller.epoch+":editor:"+std::to_string(owner.sessions);}
            download=std::make_unique<c::ProfileDownload>(id,controller.epoch,capabilities,c::ProfileRecoveryScope{owner.location.profile,editor_session});profile_reading=true;
            profile_started=profile_last=os::monotonic_ms();
            send("profile.read",download->request(query_id()));
        }
        void result(const p::Message& message){
            const bool reconciliation=message.type=="result.reconciled";
            const auto& body=reconciliation?message.body.at("result"):message.body;c::validate_command_result(body);
            need(body["producer_epoch"]==controller.epoch,"frontend.result_epoch");
            const auto request=body.at("request_id").get<std::string>(),digest=c::payload_sha256(body.dump());
            std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token),"frontend.withdrawn");
            if(request==terminal_id&&digest==terminal_hash)return;
            need(owner.pending&&owner.pending->dispatched&&request==owner.pending->request.request,"frontend.result_scope");auto& active=*owner.pending;
            if(reconciliation){
                c::Json expected={{"schema_version","0.1.0"},{"query_id",query},{"original_producer_epoch",active.request.epoch},{"request_id",request}};
                (void)p::consume_reconciliation(message,selected,expected,id,controller.epoch);
            }else need(active.request.epoch==controller.epoch,"frontend.result_epoch");
            const std::string outcome=body["outcome"];
            if(outcome=="accepted"){
                need(active.intent=="commit"&&active.revision<std::numeric_limits<std::uint64_t>::max()&&body["revision"]==std::to_string(active.revision+1),"frontend.result_revision");
                p::validate_reconciliation_result({{"schema_version","0.1.0"},{"query_id","check"},{"original_producer_epoch",active.request.epoch},{"request_id",request},{"result",body}},controller.epoch);
                owner.retirement=active.capture;owner.recovery_authority.reset();
            }else if(outcome=="unknown"){
                p::validate_reconciliation_result({{"schema_version","0.1.0"},{"query_id","check"},{"original_producer_epoch",active.request.epoch},{"request_id",request},{"result",body}},controller.epoch);
            }else{
                need(body["stored"]==false&&body["durable"]==false&&body["visible"]==false&&body["activation"].empty(),"frontend.result_facts");
                if(outcome=="preview")need(active.intent=="preview"&&body["revision"]==std::to_string(active.revision)&&body["error"].is_null(),"frontend.result_preview");
            }
            owner.view.reply=FrontendReply{active.request.ticket,reconciliation?query:std::string{},controller.epoch,message.body};
            retrieval_wait=false;
            if(outcome=="unknown")owner.view.status="Outcome unknown. Retrieve the original request before continuing.";
            else{terminal_id=request;terminal_hash=digest;owner.pending.reset();
                if(recovering){owner.reload_requested=true;owner.view.loading=true;owner.view.status="Loading saved settings.";}
                else owner.view.status="Settings connected.";
            }
        }
        void message(p::Message value){
            deadlines();need(value.connection_id==id&&value.producer_epoch==controller.epoch,"frontend.scope");
            if(value.type=="heartbeat"){
                const auto n=p::decimal(value.body.at("sequence").get<std::string>());
                need(n&&*n==sent&&sent!=echo,"frontend.heartbeat_scope");echo=*n;return;
            }
            if(value.type=="result"||value.type=="result.reconciled"){result(value);return;}
            need(value.type=="profile.chunk"&&profile_reading&&download,"frontend.direction");download->receive(value);
            profile_last=os::monotonic_ms();
            if(!download->complete()){send("profile.read",download->request(query_id()));return;}
            auto profile=std::make_shared<FrontendProfile>();profile->view=download->view();profile->epoch=controller.epoch;
            auto caps=profile->view.capabilities;caps.insert(selected.features.begin(),selected.features.end());
            profile->resources={std::make_shared<const c::ContentCatalog>(c::ContentCatalog::retained(*profile->view.resources)),profile->view.resources->selection(),std::move(caps)};
            auto resources=profile->resources;
            if(owner.recovery_admitted&&profile->view.recovery)resources.capabilities.insert("editor.recovery");
            auto prepared=std::make_unique<ui::PreparedEditor>(c::Authority{true,"console",{"console"}},profile->view.policy,profile->view.documents,profile->epoch,std::move(resources),true);
            deadlines();
            {std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token)&&!owner.pending,"frontend.withdrawn");
                if(owner.reload_requested){download.reset();profile_reading=false;return;}
                const auto revision=c::authored_revision(profile->view.documents);const auto& policy=profile->view.policy;
                if(profile->view.recovery){
                    const bool retain=policy.available&&!policy.denied_capabilities.count("editor.recovery")&&c::permits({true,"console",{"console"}},policy,"history","sensitive");
                    owner.recovery_authority=RecoverySessionAuthority{id,controller.epoch,owner.location.profile,editor_session,revision,policy.revision,retain,retain&&!policy.denied_capabilities.count("editor.recovery.erase")};
                    const auto& fresh=*profile->view.recovery;
                    if(owner.retirement){const auto& previous=*owner.retirement;const auto& old=previous.source;
                        if(old.revision<std::numeric_limits<std::uint64_t>::max()&&revision==old.revision+1&&old.admission.profile==fresh.admission.profile&&
                           old.admission.generation!=fresh.admission.generation&&same_directory(old.admission.directory,fresh.admission.directory)){
                            if(retain&&owner.recovery_authority->erase&&fresh.admission.erase)profile->recovery_retirement=previous.digest;
                        }else owner.retirement.reset();
                    }
                }
                increment(owner.profiles);profile->serial=owner.profiles;owner.view.profile=std::move(profile);owner.prepared_editor=std::move(prepared);owner.view.loading=false;owner.view.status="Settings connected.";}
            download.reset();profile_reading=false;recovering=false;
        }
        void actions(){
            std::optional<ui::EditRequest> dispatch;std::optional<Capture> capture;bool cancel=false,retrieve=false,reload=false;std::string original,request;
            {
                std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token),"frontend.withdrawn");
                if(owner.pending){auto& active=*owner.pending;request=active.request.request;original=active.request.epoch;
                    if(!active.dispatched){dispatch=active.request;capture=active.capture;}
                    else{cancel=std::exchange(active.cancel,false);if(!retrieval_wait)retrieve=std::exchange(active.retrieve,false);}
                }else if(!profile_reading)reload=std::exchange(owner.reload_requested,false);
            }
            if(dispatch){
                need(dispatch->epoch==controller.epoch,"frontend.command_epoch");const auto command=c::parse_command(dispatch->body);c::validate_command(command);
                const auto revision=p::decimal(command.at("expected_revision").get<std::string>());need(revision&&command["request_id"]==dispatch->request,"frontend.command_scope");
                if(capture){
                    const auto& source=capture->source;
                    need(command["intent"]=="commit"&&command["operations"].size()==1&&command["operations"][0]["op"]=="scene.replace"&&command.contains("content")&&
                         *revision==source.revision&&command["policy_generation"]==std::to_string(source.admission.policy_revision),"frontend.recovery_command");
                    auto preview=command;preview["intent"]="preview";preview["request_id"]="editor:recovery";
                    const c::Json envelope={{"format","syspane.editor-recovery"},{"schema_version","0.1.0"},
                        {"identity",{{"profile",source.admission.profile},{"generation",source.admission.generation}}},{"command",preview.dump()}};
                    need(c::sha256(envelope.dump())==capture->digest,"frontend.recovery_digest");
                }
                {
                    std::lock_guard<std::mutex> lock(owner.mutex);need(owner.valid_unlocked(token)&&owner.pending&&owner.pending->request.request==dispatch->request,"frontend.withdrawn");
                    owner.pending->intent=command.at("intent");owner.pending->revision=*revision;owner.pending->dispatched=true;owner.pending->request.body.clear();
                }
                const auto envelope="{\"type\":\"command\",\"body\":"+dispatch->body+",\"connection_id\":"+c::Json(id).dump()+",\"producer_epoch\":"+c::Json(controller.epoch).dump()+"}";
                owner.valid(token);stream.write(p::frame(envelope,selected.max_frame_bytes),100);owner.valid(token);
            }
            if(cancel&&original==controller.epoch)send("cancel",{{"request_id",request}});
            if(retrieve){
                retrieval_wait=true;retrieval_started=os::monotonic_ms();
                if(original==controller.epoch)send("result.get",{{"request_id",request}});
                else{query=query_id();send("result.reconcile",{{"schema_version","0.1.0"},{"query_id",query},{"original_producer_epoch",original},{"request_id",request}});}
            }
            if(reload)profile();
        }
        void run(){
            handshake();
            for(;;){
                deadlines();const auto now=os::monotonic_ms();
                if(sent==echo&&(!sent||now-last_sent>=1000)){increment(sequence);sent=sequence;last_sent=now;send("heartbeat",{{"sequence",std::to_string(sequence)}});}
                actions();input();for(unsigned i=0;i<8&&!incoming.empty();++i)message(pop());
            }
        }
    };
    void client(){
        std::uint64_t token=0,retry=0,next=0;unsigned attempts=0;
        try{
            while(!closing){
                ProfileSupervisorView current;std::uint64_t selected=0;
                {std::lock_guard<std::mutex> lock(mutex);selected=generation;current=controller;
                    if(selected!=token||retry!=retries){token=selected;retry=retries;attempts=0;next=0;}}
                if(current.state!=ProfileSupervisorState::ready||attempts>=3||os::monotonic_ms()<next){pause();continue;}
                ++attempts;
                try{Connection connection(*this,token,std::move(current));connection.run();}
                catch(...){std::lock_guard<std::mutex> lock(mutex);if(generation==token)withdraw(pending?"Outcome unknown. Retrieve the original request before continuing.":"Settings connection unavailable. Reconnect to try again.");}
                next=os::monotonic_ms()+1000;
            }
        }catch(...){std::lock_guard<std::mutex> lock(mutex);withdraw("Settings connection unavailable.");view.failed=true;}
        client_done=true;
    }
};
LinuxFrontendBackend::LinuxFrontendBackend(os::HelperBundleExpectation expectation,std::string base,os::ProfileLocation location,bool recovery)
    :impl_(std::make_unique<Impl>(std::move(expectation),std::move(base),std::move(location),recovery)){
    auto& s=*impl_;s.supervisor_worker=std::thread([&s]{s.supervise();});
    try{s.client_worker=std::thread([&s]{s.client();});}catch(...){s.closing=true;s.supervisor_worker.join();throw;}
}
LinuxFrontendBackend::~LinuxFrontendBackend(){close();if(impl_->client_worker.joinable())impl_->client_worker.join();if(impl_->supervisor_worker.joinable())impl_->supervisor_worker.join();}
FrontendView LinuxFrontendBackend::take(){auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);auto out=s.view;s.view.reply.reset();out.pending=s.pending.has_value();out.closing=s.closing;out.stopped=s.supervisor_done&&s.client_done;return out;}
std::unique_ptr<ui::PreparedEditor> LinuxFrontendBackend::take_editor(const std::shared_ptr<const FrontendProfile>& profile){
    auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);
    if(!profile||s.closing||s.pending||s.view.loading||s.controller.state!=ProfileSupervisorState::ready||s.view.profile!=profile)return {};
    return std::move(s.prepared_editor);
}
rendering::ImageFactory LinuxFrontendBackend::images()const{return impl_->helpers.images();}
std::shared_ptr<const os::RecoveryFactory> LinuxFrontendBackend::recovery()const{return impl_->helpers.recovery();}
std::shared_ptr<const ui::RecoveryPreparationFactory> LinuxFrontendBackend::preparations()const{return impl_->helpers.preparations();}
std::shared_ptr<const ui::HistoryPreparationFactory> LinuxFrontendBackend::history_preparations()const{return impl_->helpers.history_preparations();}
std::string LinuxFrontendBackend::request_id(){auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);need(!s.closing&&s.view.profile&&!s.view.loading&&!s.pending,"frontend.unavailable");increment(s.requests);return s.controller.epoch+":request:"+std::to_string(s.requests);}
void LinuxFrontendBackend::submit(const ui::EditRequest& request,std::optional<std::string> digest){
    auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);
    need(!s.closing&&s.view.profile&&!s.view.loading&&!s.pending&&request.epoch==s.controller.epoch&&request.body.size()<=p::large_command_limit,"frontend.admission");
    need(request.ticket&&p::identifier(request.request),"frontend.request");std::optional<Impl::Capture> capture;
    if(digest){need(digest->size()==64&&digest->find_first_not_of("0123456789abcdef")==std::string::npos&&s.recovery_authority&&s.recovery_authority->retain&&s.view.profile->view.recovery,"frontend.recovery_capture");
        capture=Impl::Capture{*s.view.profile->view.recovery,std::move(*digest)};}
    s.pending=Impl::Pending{request,"",0,false,false,false,std::move(capture)};s.prepared_editor.reset();s.view.reply.reset();s.retirement.reset();s.recovery_authority.reset();
}
void LinuxFrontendBackend::acknowledge_retirement(std::uint64_t serial){
    auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);
    need(!s.closing&&s.view.profile&&!s.view.loading&&!s.pending&&s.view.profile->serial==serial&&s.retirement&&
         s.view.profile->recovery_retirement==std::optional<std::string>{s.retirement->digest},"frontend.retirement_scope");s.retirement.reset();
}
void LinuxFrontendBackend::cancel(const ui::EditRequest& request){auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);if(!s.closing&&s.pending&&s.pending->request.request==request.request&&s.pending->request.epoch==request.epoch)s.pending->cancel=true;}
void LinuxFrontendBackend::reload(){auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);need(!s.closing&&!s.pending&&s.view.profile,"frontend.pending");s.prepared_editor.reset();s.recovery_authority.reset();s.reload_requested=true;s.view.loading=true;s.view.status="Loading saved settings.";}
void LinuxFrontendBackend::retrieve(){const auto now=os::monotonic_ms();auto& s=*impl_;std::lock_guard<std::mutex> lock(s.mutex);if(s.closing)return;if(s.last_retry&&now-s.last_retry<1000)return;s.last_retry=now;increment(s.retries);if(s.pending)s.pending->retrieve=true;}
void LinuxFrontendBackend::close(){auto& s=*impl_;s.helpers.close();std::lock_guard<std::mutex> lock(s.mutex);if(s.closing.exchange(true))return;s.withdraw("Closing; waiting for configuration service to stop.");}
}
