// Real form controls with held task completion; the native worker is verified
// independently by REQUEST-WORKER. Expected commands below are fixed inputs.
#include "editor_request_task.hpp"
namespace request_form_fixture {
using Request=history_form_fixture::Slot<ui::RequestWork,ui::RequestPrepared,ui::RequestPreparationStatus>;
struct Tasks:history_form_fixture::Tasks {
    std::shared_ptr<Request> request;unsigned requests_started=0;
    std::shared_ptr<const ui::RequestPreparationFactory> requests(){return std::make_shared<const ui::RequestPreparationFactory>([this](std::unique_ptr<ui::RequestWork> work)->std::unique_ptr<ui::RequestPreparationTask>{
        if(refuse)throw p::Error("helpers.capacity");
        need(!request||(request->released&&request->state.stopped),"request slot reused early");
        request=std::make_shared<Request>();request->input=std::move(work);++requests_started;
        return std::make_unique<history_form_fixture::Task<ui::RequestPreparationTask,Request>>(request);
    });}
};
struct Queue:history_form_fixture::Queue {
    bool& withdrawn;
    Queue(history_form_fixture::Store& s,os::RecoveryContext c,bool& w):history_form_fixture::Queue(s,std::move(c)),withdrawn(w){}
    os::RecoveryQueueStatus status()const override{auto value=history_form_fixture::Queue::status();if(withdrawn&&value.state!=os::RecoveryQueueState::closed)value.state=os::RecoveryQueueState::unavailable;return value;}
    os::RecoveryQueueStatus poll()override{return status();}
};
}
int request_form(const std::string& root){
    using namespace request_form_fixture;const auto cases=read(root+"/tests/editor/request-form-cases.json");
    for(const std::string mode:cases.at("cases")){
        settings_fixture::Fixture fixture(root);auto authored=fixture.authored;
        authored.scene=read(root+"/tests/editor/native-cases.json")["authored"]["scene"];
        authored.scene["widgets"].erase(authored.scene["widgets"].begin()+2);authored.scene["roots"].erase(authored.scene["roots"].begin()+2);
        authored.settings["revision"]=authored.scene["revision"]="40";auto expected=authored.scene;expected["widgets"][0]["title"]="Prepared form";
        const bool recover=mode.substr(0,9)=="recovery-";auto resources=fixture.resources();auto grant=policy();
        if(recover){resources.capabilities.insert("editor.recovery");grant.disclosure[{"desktop","history"}]={"sensitive"};}
        Tasks tasks;history_form_fixture::Store store;bool withdrawn=false;unsigned ids=0,exits=0,reloads=0,submissions=0,cancels=0;
        std::optional<ui::EditRequest> sent,cancelled;std::optional<std::string> digest;ui::EditorForm::Actions actions;
        actions.request_id=[&]{return "form:"+std::to_string(++ids);};actions.widget_id=[] {return "unexpected:widget";};
        actions.submit=[&](const auto&){throw std::runtime_error("unscoped request submission");};
        actions.submit_recovery=[&](const auto& q,auto d){++submissions;sent=q;digest=d;if(mode=="submit-failure")throw p::Error("test.transport");};
        actions.cancel=[&](const auto& q){++cancels;cancelled=q;};actions.reload=[&]{++reloads;};actions.exit=[&]{++exits;};
        ui::EditorForm form(authority(),grant,authored,"E1",resources,topology(),"D1",{},"",std::move(actions),true,{},tasks.histories(),tasks.requests());
        auto control=[&](const char* id){auto* w=editor_control(form.widget(),id);need(w!=nullptr,"missing request control");return w;};
        auto sensitive=[&](const char* id){return gtk_widget_get_sensitive(control(id))!=FALSE;};
        auto click=[&](const char* id){gtk_button_clicked(GTK_BUTTON(control(id)));};
        auto* tree=GTK_TREE_VIEW(control("editor.objects"));
        auto select=[&](int index){auto* selection=gtk_tree_view_get_selection(tree);gtk_tree_selection_unselect_all(selection);auto* path=gtk_tree_path_new_from_indices(index,-1);gtk_tree_selection_select_path(selection,path);gtk_tree_path_free(path);};
        auto field=[&]{auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title")));GtkTextIter a,z;gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;};
        auto title=[&](const char* value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title"))),value,-1);click("editor.properties");};
        auto flush=[&]{for(unsigned n=0;n<8;++n){form.stopped();if(tasks.capture&&tasks.capture->input&&!tasks.capture->state.stopped)tasks.capture->finish();}form.stopped();};
        auto queue=std::make_shared<const os::RecoveryFactory>([&](std::string,os::RecoveryContext context){return std::make_unique<Queue>(store,std::move(context),withdrawn);});
        const auto captures=tasks.captures();
        const ui::EditorRecoveryBinding binding{"request:session","profile:primary",std::string(64,'4'),7,true};
        if(recover){form.recovery(queue,"/controlled/recovery",binding,captures);flush();}
        select(0);title("Prepared form");if(recover){flush();need(store.bytes&&store.writes==1,"recovery capture not durable");}
        const auto retained=store.bytes;const auto saved_digest=retained?std::optional<std::string>(c::sha256(*retained)):std::nullopt;
        auto pending=[&]{need(tasks.request&&!tasks.request->released&&!form.can_leave()&&!sent,"request not pending");
            for(const char* id:{"editor.undo","editor.redo","editor.apply","editor.properties","editor.value.title","editor.objects","editor.canvas"})need(!sensitive(id),"pending authoring enabled");
            for(const char* id:{"editor.cancel","editor.reload","editor.cancel-request"})need(sensitive(id),"pending escape disabled");};
        auto exact=[&](unsigned identifier=1,std::optional<std::string> expected_digest=std::nullopt){
            need(sent&&submissions==1&&sent->ticket==1&&sent->request=="form:"+std::to_string(identifier)&&sent->epoch=="E1","request identity changed");
            Json want={{"schema_version","0.5.0"},{"request_id",sent->request},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},
                {"operations",Json::array({{{"op","scene.replace"},{"scene",expected}}})},{"content",fixture.document["selection"]}};
            need(Json::parse(sent->body)==want&&digest==expected_digest,"prepared command or digest differs from literal");
        };
        if(mode=="factory-failure")tasks.refuse=true;
        using Clock=std::chrono::steady_clock;auto before=Clock::now();click("editor.apply");auto capture_us=std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-before).count();long long adopt_us=0;
        if(mode=="factory-failure"){
            need(!tasks.request&&!sent&&sensitive("editor.apply")&&field()=="Prepared form","factory failure changed draft");tasks.refuse=false;click("editor.apply");tasks.request->finish();form.stopped();exact(2);
        }else{
            pending();const auto held=tasks.request;
            if(mode=="pending"){
                for(const char* id:{"editor.apply","editor.undo","editor.redo","editor.add","editor.delete","editor.revert-fields"})click(id);
                title("Injected");select(1);GdkEventKey key{};key.type=GDK_KEY_PRESS;key.keyval=GDK_KEY_Right;gboolean handled=FALSE;g_signal_emit_by_name(control("editor.canvas"),"key-press-event",&key,&handled);
                need(!handled&&ids==1&&tasks.requests_started==1&&field()=="Prepared form","pending input mutated form");pending();
            }
            if(mode=="trace"||mode=="pending"||mode=="recovery-digest"||mode=="submit-failure"||mode=="cancel-sent"){
                held->finish();before=Clock::now();form.stopped();adopt_us=std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-before).count();exact(1,saved_digest);
                need(held->released&&exits==0&&!sensitive("editor.apply"),"submitted form state differs");
                form.stopped();click("editor.apply");need(submissions==1&&ids==1,"request submitted twice");
                if(mode=="recovery-digest")need(store.bytes==retained&&store.writes==1,"submission rewrote retained draft");
                if(mode=="submit-failure")need(std::string(gtk_label_get_text(GTK_LABEL(control("editor.status")))).find("Outcome unknown")!=std::string::npos,"submit failure lost unknown state");
                if(mode=="cancel-sent"){click("editor.cancel-request");need(cancels==1&&cancelled->ticket==sent->ticket&&cancelled->body==sent->body,"transport cancellation identity changed");}
            }else if(mode=="run-failure"||mode=="cancel-preparation"||mode=="recovery-changed"){
                if(mode=="run-failure")held->finish(true);
                else if(mode=="cancel-preparation")click("editor.cancel-request");
                else{withdrawn=true;held->finish();}
                flush();need(held->released&&!sent&&cancels==0&&sensitive("editor.apply")&&field()=="Prepared form","pre-submit refusal changed draft");
                if(recover)need(store.bytes==retained&&store.writes==1,"withdrawal erased retained draft");
                click("editor.apply");tasks.request->finish();form.stopped();exact(2);
            }else{
                if(mode=="cancel-ready")held->finish();
                const bool running=mode!="cancel-queued"&&mode!="cancel-ready";if(running)held->state.running=true;
                if(mode.substr(0,7)=="cancel-"||mode=="recovery-cancel")click("editor.cancel");
                else if(mode=="reload-button")click("editor.reload");
                else if(mode=="reload")form.reload(authored,"E2",resources);
                else if(mode=="topology"||mode=="late-result")form.topology(topology(),"D1");
                else if(mode=="policy")form.policy(policy(8));
                else if(mode=="withdrawal"||mode=="recovery-withdrawal")form.policy({});
                else if(mode=="disconnect")form.disconnected();
                else if(mode=="close")form.close();
                else if(mode=="recovery-rebind")form.recovery(queue,"/controlled/recovery",binding,captures);
                need(held->cancelled,"context change did not cancel preparation");
                if(running){need(!form.stopped()&&!held->released&&exits==0,"running preparation released early");held->finish(false,true);}
                flush();need(held->released&&!sent&&cancels==0,"obsolete result submitted");
                if(mode.substr(0,7)=="cancel-"||mode=="recovery-cancel")need(exits==1&&field().empty(),"cancel did not erase and exit once");
                else if(mode=="close"||mode=="withdrawal"||mode=="recovery-withdrawal")need(exits==0&&field().empty(),"withdrawal revived private input");
                if(mode=="recovery-cancel")need(!store.bytes,"cancel retained owned recovery");
                if(mode=="recovery-withdrawal")need(store.bytes==retained,"withdrawal erased recovery without authority");
                need(reloads==(mode=="reload-button"?1U:0U),"reload callback mismatch");
            }
        }
        need(capture_us<cases.at("callback_limit_us").get<long long>()&&adopt_us<cases.at("callback_limit_us").get<long long>(),"request form callback exceeded fixed bound");
        form.close();if(tasks.request&&tasks.request->input)tasks.request->finish();if(tasks.capture&&tasks.capture->input)tasks.capture->finish();flush();need(form.stopped(),"request form did not drain");
        emit({{"case",mode},{"outcome","pass"},{"capture_us",capture_us},{"adopt_us",adopt_us}});
    }
    return 0;
}
