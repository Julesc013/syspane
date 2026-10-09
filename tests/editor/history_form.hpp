// Real GTK form tests with explicitly controlled task completion. Native worker
// execution and kernel-observed cancellation are covered by HISTORY-WORKER.
#include "editor_history_task.hpp"
#include "digest.hpp"
namespace history_form_fixture {
template<class Work,class Prepared,class Status>struct Slot {
    std::unique_ptr<Work> input;std::unique_ptr<Prepared> result;Status state;
    bool cancelled=false,released=false;
    void cancel(){cancelled=true;result.reset();state.ready=false;if(!state.running){input.reset();state.stopped=true;}}
    void finish(bool fail=false,bool late=false){
        need(input!=nullptr,"missing controlled input");state.running=true;std::exception_ptr error;
        std::thread worker([&]{try{if(!fail)result=input->run();}catch(...){error=std::current_exception();}input.reset();});worker.join();
        if(error)std::rethrow_exception(error);
        if(cancelled&&!late){result.reset();}state.running=false;state.stopped=true;state.ready=static_cast<bool>(result);state.error=fail?"history.preparation":"";
    }
};
using History=Slot<ui::HistoryWork,ui::HistoryPrepared,ui::HistoryPreparationStatus>;
using Capture=Slot<ui::RecoveryWork,ui::RecoveryPrepared,ui::RecoveryPreparationStatus>;
template<class Base,class Data>struct Task:Base {
    std::shared_ptr<Data> value;explicit Task(std::shared_ptr<Data> v):value(std::move(v)){}
    ~Task()override{value->released=true;value->cancel();}
    auto status()const->decltype(value->state)override{return value->state;}
    auto take()->decltype(value->result)override{
        if(!value->state.ready||!value->state.stopped){throw p::Error("test.not_ready");}value->state.ready=false;return std::move(value->result);
    }
    void cancel()override{value->cancel();}
};
struct Tasks {
    std::shared_ptr<History> history;std::shared_ptr<Capture> capture;bool refuse=false;unsigned admissions=0;
    std::shared_ptr<const ui::HistoryPreparationFactory> histories(){return std::make_shared<const ui::HistoryPreparationFactory>([this](std::unique_ptr<ui::HistoryWork> work)->std::unique_ptr<ui::HistoryPreparationTask>{
        if(refuse){throw p::Error("helpers.capacity");}need(!history||(history->released&&history->state.stopped),"history slot reused early");
        history=std::make_shared<History>();history->input=std::move(work);++admissions;return std::make_unique<Task<ui::HistoryPreparationTask,History>>(history);
    });}
    std::shared_ptr<const ui::RecoveryPreparationFactory> captures(){return std::make_shared<const ui::RecoveryPreparationFactory>([this](std::unique_ptr<ui::RecoveryWork> work)->std::unique_ptr<ui::RecoveryPreparationTask>{
        need(!capture||(capture->released&&capture->state.stopped),"capture slot reused early");capture=std::make_shared<Capture>();capture->input=std::move(work);return std::make_unique<Task<ui::RecoveryPreparationTask,Capture>>(capture);
    });}
};
struct Store {std::optional<std::string> bytes;unsigned writes=0;};
struct Queue:os::RecoveryTask {
    Store& store;os::RecoveryContext context;os::RecoveryQueueStatus state;std::optional<os::RecoveryCompletion> result;std::uint64_t ticket=1;
    Queue(Store& s,os::RecoveryContext c):store(s),context(std::move(c)){
        state.state=os::RecoveryQueueState::ready;state.reaped=true;
        result=os::RecoveryCompletion{context,1,"load","loaded","",store.bytes?std::optional<std::string>(c::sha256(*store.bytes)):std::nullopt,store.bytes,false};
    }
    std::uint64_t replace(std::string bytes)override{store.bytes=std::move(bytes);++store.writes;result=os::RecoveryCompletion{context,++ticket,"replace","durable","",c::sha256(*store.bytes),{},false};return ticket;}
    std::uint64_t retire()override{store.bytes.reset();state.state=os::RecoveryQueueState::retired;result=os::RecoveryCompletion{context,++ticket,"retire","durable","",{},{},false};return ticket;}
    os::RecoveryQueueStatus poll()override{return state;}
    os::RecoveryQueueStatus status()const override{return state;}
    std::optional<os::RecoveryCompletion> take()override{auto out=std::move(result);result.reset();return out;}
    void close()override{state.state=os::RecoveryQueueState::closed;state.reaped=true;result.reset();}
};
}
int history_form(const std::string& root){
    using namespace history_form_fixture;
    const auto cases=read(root+"/tests/editor/history-form-cases.json");
    for(const std::string mode:cases.at("cases")){
        settings_fixture::Fixture fixture(root);auto authored=fixture.authored;
        authored.scene=read(root+"/tests/editor/native-cases.json")["authored"]["scene"];
        authored.scene["widgets"].erase(authored.scene["widgets"].begin()+2);authored.scene["roots"].erase(authored.scene["roots"].begin()+2);
        authored.settings["revision"]=authored.scene["revision"]="40";
        auto first=authored.scene,second=authored.scene;first["widgets"][0]["title"]="First";second=first;second["widgets"][1]["title"]="Second";
        const bool recover=mode.substr(0,9)=="recovery-";auto resources=fixture.resources();auto grant=policy();
        if(recover){resources.capabilities.insert("editor.recovery");grant.disclosure[{"desktop","history"}]={"sensitive"};}
        Tasks tasks;Store store;unsigned exits=0,reloads=0;std::optional<ui::EditRequest> request;ui::EditorForm::Actions actions;
        actions.request_id=[] {return "history:form";};actions.widget_id=[] {return "unexpected:widget";};actions.submit=[&](const auto& q){request=q;};
        actions.cancel=[](const auto&){throw std::runtime_error("unexpected request cancellation");};actions.reload=[&]{++reloads;};actions.exit=[&]{++exits;};
        ui::EditorForm form(authority(),grant,authored,"E1",resources,topology(),"D1",{},"",std::move(actions),true,{},tasks.histories());
        auto control=[&](const char* id){auto* w=editor_control(form.widget(),id);need(w!=nullptr,"missing history control");return w;};
        auto sensitive=[&](const char* id){return gtk_widget_get_sensitive(control(id))!=FALSE;};
        auto click=[&](const char* id){gtk_button_clicked(GTK_BUTTON(control(id)));};
        auto* tree=GTK_TREE_VIEW(control("editor.objects"));
        auto select=[&](int index){auto* selection=gtk_tree_view_get_selection(tree);gtk_tree_selection_unselect_all(selection);auto* path=gtk_tree_path_new_from_indices(index,-1);gtk_tree_selection_select_path(selection,path);gtk_tree_path_free(path);};
        auto field=[&](const char* id){auto* buffer=gtk_text_view_get_buffer(GTK_TEXT_VIEW(control(id)));GtkTextIter a,z;gtk_text_buffer_get_bounds(buffer,&a,&z);auto* raw=gtk_text_buffer_get_text(buffer,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;};
        auto title=[&](const char* value){gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title"))),value,-1);click("editor.properties");};
        auto pending=[&]{need(tasks.history&&!tasks.history->released&&!form.can_leave(),"history not pending");for(const char* id:{"editor.undo","editor.redo","editor.apply","editor.properties","editor.value.title","editor.objects","editor.canvas"})need(!sensitive(id),"pending action enabled");need(sensitive("editor.cancel")&&sensitive("editor.reload"),"pending escape disabled");};
        auto flush=[&]{for(unsigned n=0;n<8;++n){form.stopped();if(tasks.capture&&tasks.capture->input&&!tasks.capture->state.stopped)tasks.capture->finish();}form.stopped();};
        auto exact=[&](const Json& expected){
            flush();request.reset();need(sensitive("editor.apply"),"history result cannot apply");click("editor.apply");need(request.has_value(),"history form did not submit");
            const auto q=Json::parse(request->body);need(q.at("operations")==Json::array({{{"op","scene.replace"},{"scene",expected}}}),"history command differs from literal scene");
            form.complete(request->ticket,c::result({"cancelled","request.cancelled"},request->request,request->epoch,40));request.reset();
        };
        auto saved=[&](const Json& expected){need(store.bytes.has_value(),"capture not durable");auto envelope=Json::parse(*store.bytes);auto q=Json::parse(envelope.at("command").get<std::string>());need(q.at("operations")==Json::array({{{"op","scene.replace"},{"scene",expected}}}),"capture scene differs from literal");};
        if(recover){auto queue=std::make_shared<const os::RecoveryFactory>([&](std::string,os::RecoveryContext context){return std::make_unique<Queue>(store,std::move(context));});form.recovery(queue,"/controlled/recovery",{"history:session","profile:primary",std::string(64,'4'),7,true},tasks.captures());flush();}
        select(0);title("First");if(recover){flush();saved(first);need(store.writes==1,"duplicate first capture");}
        select(1);title("Second");
        if(recover){form.stopped();need(tasks.capture&&tasks.capture->input,"second capture not admitted");tasks.capture->state.running=true;}
        if(mode=="factory-failure")tasks.refuse=true;
        click("editor.undo");
        if(mode=="factory-failure"){
            need(tasks.admissions==0&&sensitive("editor.undo")&&field("editor.value.title")=="Second","factory failure changed history");exact(second);
        }else{
            pending();const auto held=tasks.history;
            if(mode=="trace"||mode=="pending"){
                if(mode=="pending"){
                    for(const char* id:{"editor.undo","editor.redo","editor.apply","editor.add","editor.delete","editor.revert-fields"})click(id);
                    title("Injected");select(0);GdkEventKey key{};key.type=GDK_KEY_PRESS;key.keyval=GDK_KEY_Right;gboolean handled=FALSE;g_signal_emit_by_name(control("editor.canvas"),"key-press-event",&key,&handled);
                    need(!handled&&!request&&tasks.admissions==1&&field("editor.value.title")=="Second","pending input mutated form");pending();
                }
                held->finish();form.stopped();need(held->released&&field("editor.value.title")=="Second pane","undo selection or fields wrong");exact(first);
                click("editor.undo");tasks.history->finish();form.stopped();need(field("editor.value.title")=="Editable pane"&&!sensitive("editor.undo")&&!sensitive("editor.apply")&&sensitive("editor.redo"),"clean undo differs");
                click("editor.redo");tasks.history->finish();form.stopped();need(field("editor.value.title")=="First","redo selection differs");exact(first);
                click("editor.redo");tasks.history->finish();form.stopped();need(field("editor.value.title")=="Second"&&!sensitive("editor.redo"),"final redo differs");exact(second);
            }else if(mode=="run-failure"){
                held->finish(true);form.stopped();need(held->released&&field("editor.value.title")=="Second"&&sensitive("editor.undo"),"failed work mutated history");exact(second);
            }else if(recover){
                need(tasks.capture->cancelled,"history did not suspend obsolete capture");saved(first);held->state.running=true;
                if(mode=="recovery-capture"){
                    held->finish();need(!form.stopped()&&!sensitive("editor.apply"),"capture reused running slot or enabled apply");saved(first);
                    tasks.capture->finish();flush();saved(first);need(store.writes==1,"history captured obsolete second state");exact(first);
                    click("editor.redo");tasks.history->finish();flush();saved(second);need(store.writes==2,"redo capture count differs");exact(second);
                }else{
                    if(mode=="recovery-cancel")click("editor.cancel");else form.policy({});
                    need(!form.stopped()&&exits==0,"history closure acknowledged early");tasks.capture->finish();held->finish(false,true);flush();
                    if(mode=="recovery-cancel")need(exits==1&&!store.bytes,"cancel retained owned recovery or missed exit");else{need(exits==0&&!sensitive("editor.apply")&&field("editor.value.title").empty(),"withdrawal revived input");saved(first);}
                    need(store.writes==1,"cancel or withdrawal resumed capture");
                }
            }else{
                if(mode=="cancel-ready")held->finish();
                const bool running=mode!="cancel-queued"&&mode!="cancel-ready";if(running)held->state.running=true;
                if(mode.substr(0,7)=="cancel-")click("editor.cancel");
                else if(mode=="reload-button")click("editor.reload");
                else if(mode=="reload"){auto replacement=authored;replacement.scene["widgets"][0]["title"]="Reloaded";form.reload(replacement,"E2",resources);}
                else if(mode=="topology")form.topology(topology(),"D1");
                else if(mode=="policy")form.policy(policy(8));
                else if(mode=="disconnect")form.disconnected();
                else if(mode=="late-result")form.topology(topology(),"D1");
                else if(mode=="close")form.close();
                need(held->cancelled,"replacement did not cancel history");
                if(running){need(!form.stopped()&&!held->released&&exits==0,"running task released early");held->finish(false,mode=="late-result");}
                form.stopped();need(held->released,"stopped history handle retained");
                if(mode.substr(0,7)=="cancel-")need(exits==1&&field("editor.value.title").empty(),"cancel did not erase and exit");
                else if(mode=="close")need(exits==0&&field("editor.value.title").empty(),"close revived input");
                else if(mode=="reload")need(!sensitive("editor.undo")&&!sensitive("editor.apply"),"late history mutated reloaded draft");
                else if(mode=="disconnect")exact(second);
                else{need(reloads==(mode=="reload-button"?1U:0U),"reload callback mismatch");exact(second);}
            }
        }
        form.close();if(tasks.capture&&tasks.capture->input)tasks.capture->finish();if(tasks.history&&tasks.history->input)tasks.history->finish();flush();need(form.stopped(),"history form did not drain");
        emit({{"case",mode},{"outcome","pass"}});
    }
    return 0;
}
