#include "editor_draft.hpp"
#include "authored_equal.hpp"
#include "theme_command.hpp"

namespace syspane::interfaces {
namespace {
namespace c=configuration;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
constexpr const char* request="editor:recovery";
void identity(const RecoveryIdentity& value){
    need(protocol::identifier(value.profile)&&value.generation.size()==64&&
        value.generation.find_first_not_of("0123456789abcdef")==std::string::npos,"recovery.identity");
}
Json envelope(const RecoveryIdentity& value,const Json& command){
    return {{"format","syspane.editor-recovery"},{"schema_version","0.1.0"},
        {"identity",{{"profile",value.profile},{"generation",value.generation}}},{"command",command.dump()}};
}
Json decode(std::string_view bytes,const RecoveryIdentity& expected){
    identity(expected);const auto value=c::parse_content_json(bytes,recovery_record_limit);
    need(protocol::members(value,{"format","schema_version","identity","command"})&&
        value["format"]=="syspane.editor-recovery"&&value["schema_version"]=="0.1.0"&&
        protocol::members(value["identity"],{"profile","generation"})&&value["command"].is_string(),"recovery.format");
    need(value["identity"]["profile"]==expected.profile&&value["identity"]["generation"]==expected.generation,"recovery.baseline");
    auto command=c::parse_command(value["command"].get_ref<const std::string&>());c::validate_command(command);
    need(command["intent"]=="preview"&&command["request_id"]==request&&command.contains("content")&&
        command["operations"].size()==1&&command["operations"][0]["op"]=="scene.replace","recovery.command");
    return command;
}
Json metadata(Json scene){for(const char* name:{"schema_version","theme_id","roots","widgets"})scene.erase(name);return scene;}
}
void EditorDraft::authorize_recovery()const{
    transaction_.editable();
    need(transaction_.large_commands_&&transaction_.context_&&transaction_.base_resources_&&
        transaction_.context_->capabilities.count("editor.recovery"),"recovery.unavailable");
    const auto& a=transaction_.authority_;const auto& p=transaction_.policy_;
    need((a.role=="desktop"||a.role=="console")&&p.available&&!p.denied_capabilities.count("editor.recovery")&&
        c::permits(a,p,"history","sensitive"),"recovery.denied");
    if(scene()->at("schema_version")!="0.2.0")admit_fragment_version(scene()->at("schema_version"));
    transaction_.authorize_resources();
    auto check=transaction_.command("preview",request);
    if(check["operations"].empty())check["operations"].push_back({{"op","scene.replace"}});
    c::authorize_authored(check,a,p,*revision());
}
bool EditorDraft::recovery_available()const{
    try{authorize_recovery();return true;}catch(const protocol::Error&){return false;}
}
void EditorDraft::recovery_destination()const{
    need(!dirty()&&undo_.empty()&&redo_.empty(),"recovery.local_changes");
}
std::pair<c::Authored,c::ResourceSnapshot> EditorDraft::prepare_recovery(std::string_view bytes,const RecoveryIdentity& expected)const{
    authorize_recovery();auto command=decode(bytes,expected);
    const auto& base=*transaction_.base_;const auto& incoming=command["operations"][0]["scene"];
    need(c::authored_equal(metadata(base.scene),metadata(incoming)),"recovery.metadata");
    const auto from=base.scene.at("schema_version").get<std::string>(),to=incoming.at("schema_version").get<std::string>();
    need(from=="0.2.0"?to==from:to>=from,"recovery.version");
    if(to!="0.2.0")admit_fragment_version(to);
    for(const char* key:{"package","preset"})need(command["content"].at(key)==transaction_.base_resources_->selection().at(key),"recovery.resources");
    // The recorded policy generation is audit data. It was structurally validated above;
    // current authorization alone controls this local preview and later Apply.
    command["policy_generation"]=std::to_string(transaction_.policy_.revision);
    auto candidate=c::prepare_authored(base,command,transaction_.authority_,transaction_.policy_);
    c::ResourceSnapshot resources;
    if(command["schema_version"]=="0.8.0")resources=c::prepare_theme_command(*transaction_.base_resources_,candidate,command,transaction_.policy_,transaction_.context_->capabilities);
    else resources=c::ContentCatalog::retained(*transaction_.base_resources_).resources(command["content"],candidate);
    c::authorize_resources(*resources,transaction_.policy_,transaction_.context_->capabilities);
    auto prepared=transaction_.prepare_scene(std::move(candidate.scene),std::move(resources));
    auto normal=transaction_.command(prepared.first,prepared.second,"preview",request);
    if(normal["operations"].empty())normal["operations"].push_back({{"op","scene.replace"},{"scene",prepared.first.scene}});
    need(c::authored_equal(command,normal),"recovery.command");
    return prepared;
}
std::optional<std::string> EditorDraft::recovery_snapshot(const RecoveryIdentity& expected)const{
    authorize_recovery();identity(expected);if(!dirty())return {};
    const auto command=transaction_.command("preview",request);c::validate_command(command);
    auto bytes=envelope(expected,command).dump();need(bytes.size()<=recovery_record_limit,"recovery.size");
    const auto prepared=prepare_recovery(bytes,expected);
    need(c::authored_equal(prepared.first.scene,*scene())&&prepared.second->selection()==resources()->selection()&&
        prepared.second->theme_pin()==resources()->theme_pin(),"recovery.reconstruction");
    return bytes;
}
RecoveryDescription EditorDraft::inspect_recovery(std::string_view bytes,const RecoveryIdentity& expected)const{
    authorize_recovery();recovery_destination();const auto prepared=prepare_recovery(bytes,expected);
    return {prepared.first.scene.at("scene_id").get<std::string>(),c::authored_revision(prepared.first),
        prepared.first.scene.at("widgets").size(),prepared.second->theme_pin()!=transaction_.base_resources_->theme_pin()};
}
bool EditorDraft::restore_recovery(std::string_view bytes,const RecoveryIdentity& expected){
    invalidate_recovery();
    authorize_recovery();recovery_destination();auto prepared=prepare_recovery(bytes,expected);
    return record(std::move(prepared.first.scene),{},std::move(prepared.second));
}
struct RecoveryWork::Impl {
    std::unique_ptr<EditorDraft> draft;std::weak_ptr<const char> validity;RecoveryIdentity identity;
    bool capture=false;std::string bytes;
};
struct RecoveryPrepared::Impl {
    std::weak_ptr<const char> validity;RecoveryIdentity identity;bool capture=false;
    std::optional<std::string> bytes;std::pair<c::Authored,c::ResourceSnapshot> candidate;RecoveryDescription description;
};
RecoveryWork::RecoveryWork(std::unique_ptr<Impl> value):impl_(std::move(value)){}
RecoveryWork::~RecoveryWork()=default;
RecoveryPrepared::RecoveryPrepared(std::unique_ptr<Impl> value):impl_(std::move(value)){}
RecoveryPrepared::~RecoveryPrepared()=default;
std::unique_ptr<RecoveryPrepared> RecoveryWork::run(){
    auto input=std::move(impl_);need(input&&input->draft,"recovery.work_consumed");
    auto result=std::make_unique<RecoveryPrepared::Impl>();result->validity=input->validity;result->identity=input->identity;result->capture=input->capture;
    if(input->capture)result->bytes=input->draft->recovery_snapshot(input->identity);
    else{
        input->draft->recovery_destination();result->candidate=input->draft->prepare_recovery(input->bytes,input->identity);
        const auto& value=result->candidate;result->description={value.first.scene.at("scene_id").get<std::string>(),c::authored_revision(value.first),
            value.first.scene.at("widgets").size(),value.second->theme_pin()!=input->draft->resources()->theme_pin()};
    }
    return std::unique_ptr<RecoveryPrepared>(new RecoveryPrepared(std::move(result)));
}
std::unique_ptr<RecoveryWork> EditorDraft::recovery_capture_work(const RecoveryIdentity& expected)const{
    authorize_recovery();identity(expected);auto value=std::make_unique<RecoveryWork::Impl>();
    value->draft=std::unique_ptr<EditorDraft>(new EditorDraft(transaction_,0));
    value->validity=recovery_validity_.value;value->identity=expected;value->capture=true;
    return std::unique_ptr<RecoveryWork>(new RecoveryWork(std::move(value)));
}
std::unique_ptr<RecoveryWork> EditorDraft::recovery_restore_work(std::string bytes,const RecoveryIdentity& expected)const{
    authorize_recovery();identity(expected);recovery_destination();need(bytes.size()<=recovery_record_limit,"recovery.size");
    auto value=std::make_unique<RecoveryWork::Impl>();value->draft=std::unique_ptr<EditorDraft>(new EditorDraft(transaction_,0));
    value->validity=recovery_validity_.value;value->identity=expected;value->bytes=std::move(bytes);
    return std::unique_ptr<RecoveryWork>(new RecoveryWork(std::move(value)));
}
void EditorDraft::check_recovery(const RecoveryPrepared& prepared,const RecoveryIdentity& expected,bool capture)const{
    authorize_recovery();identity(expected);need(prepared.impl_&&prepared.impl_->capture==capture,"recovery.prepared_kind");const auto& value=*prepared.impl_;
    need(value.identity.profile==expected.profile&&value.identity.generation==expected.generation&&value.validity.lock()==recovery_validity_.value,"recovery.prepared_stale");
    if(!capture)recovery_destination();
}
std::optional<std::string> EditorDraft::recovery_capture(std::unique_ptr<RecoveryPrepared> prepared,const RecoveryIdentity& expected)const{
    need(static_cast<bool>(prepared),"recovery.prepared");check_recovery(*prepared,expected,true);return std::move(prepared->impl_->bytes);
}
RecoveryDescription EditorDraft::inspect_recovery(const RecoveryPrepared& prepared,const RecoveryIdentity& expected)const{
    check_recovery(prepared,expected,false);return prepared.impl_->description;
}
bool EditorDraft::restore_recovery(std::unique_ptr<RecoveryPrepared> prepared,const RecoveryIdentity& expected){
    try{need(static_cast<bool>(prepared),"recovery.prepared");check_recovery(*prepared,expected,false);}
    catch(...){invalidate_recovery();throw;}
    invalidate_recovery();
    return record_prepared(std::move(prepared->impl_->candidate),{});
}
}
