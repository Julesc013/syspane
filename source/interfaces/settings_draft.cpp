#include "settings_draft.hpp"
#include "authored_equal.hpp"
#include "settings_descriptors.hpp"
#include "reconciliation.hpp"
#include "theme_command.hpp"
#include <algorithm>
#include <limits>
namespace syspane::interfaces {
namespace {
namespace c=configuration;namespace p=protocol;
void need(bool value,const char* code){if(!value)throw p::Error(code);}
const SettingDescription& descriptor(const std::string& id){const auto& rows=setting_descriptions();const auto it=std::find_if(rows.begin(),rows.end(),[&](const auto& r){return r.id==id;});need(it!=rows.end(),"settings.path");return *it;}
const Json& setting(const c::Authored& value,const std::string& id){const auto dot=id.find('.');return value.settings.at(id.substr(0,dot)).at(id.substr(dot+1));}
bool versioned(const c::ResourceSnapshot& resource){return resource&&resource->selection().contains("schema_version");}
bool admitted(const std::optional<SettingsResources>& context,bool large){
    if(!large||!context)return false;
    for(const char* cap:{"configuration.theme-overrides","theme.typography","configuration.visibility","configuration.edit-locks","scene.content","scene.edit-locks","scene.visibility"})
        if(!context->capabilities.count(cap))return false;
    return true;
}
Json one(const c::Authored& value,const c::Policy& policy,const std::string& id,Json v,const std::optional<SettingsResources>& context,const c::ResourceSnapshot& resource){
    Json command={{"schema_version",context?"0.3.0":"0.2.0"},{"request_id","draft.validation"},{"expected_revision",value.settings["revision"]},{"policy_generation",std::to_string(policy.revision)},{"intent","preview"},{"operations",Json::array({{{"op","settings.set"},{"path",id},{"value",std::move(v)}}})}};
    if(context)command["content"]=resource->selection();
    if(versioned(resource)){command["schema_version"]="0.8.0";command["theme_edit"]=nullptr;}
    return command;
}
}
const std::vector<SettingDescription>& setting_descriptions(){
    static const std::vector<SettingDescription> rows=[] {std::vector<SettingDescription> out;
        for(const auto& d:c::descriptors)out.push_back({d.path,d.page,d.units,d.activation,d.label_id,d.help_id,d.label,d.help,
            d.kind==c::Kind::boolean?SettingKind::boolean:d.kind==c::Kind::integer?SettingKind::integer:SettingKind::identifier,Json::parse(d.default_json)});
        return out;}();return rows;
}
SettingsDraft::SettingsDraft(c::Authority authority,c::Policy policy,c::Authored value,std::string epoch,std::optional<SettingsResources> resources,bool large_commands):authority_(std::move(authority)),policy_(std::move(policy)),large_commands_(large_commands){
    if(policy_.available)highest_policy_=policy_.revision;
    reload(std::move(value),std::move(epoch),std::move(resources));
}
PreparedSettings::PreparedSettings(c::Authority a,c::Policy p,c::Authored value,std::string epoch,std::optional<SettingsResources> resources,bool large)
    :draft_(std::move(a),std::move(p),std::move(value),std::move(epoch),std::move(resources),large){}
bool SettingsDraft::disclosure()const{return policy_.available&&c::permits(authority_,policy_,"inspector","operational")&&c::permits(authority_,policy_,"accessibility","operational");}
void SettingsDraft::erase(){submission_validation_.clear();base_.reset();draft_.reset();context_.reset();base_resources_.reset();draft_resources_.reset();result_=nullptr;if(active_)active_->request.body.clear();state_=DraftState::unavailable;}
bool SettingsDraft::theme_commands()const{return admitted(context_,large_commands_);}
void SettingsDraft::authorize_theme_resources()const{
    need(theme_commands(),"settings.theme_commands");need(policy_.available&&!policy_.denied_capabilities.count("configuration.theme-overrides")&&!policy_.denied_capabilities.count("theme.typography"),"policy.denied");
}
void SettingsDraft::authorize_resources()const{
    if(context_){c::authorize_resources(*draft_resources_,policy_,context_->capabilities);
        if(versioned(base_resources_)||versioned(draft_resources_)){authorize_theme_resources();c::authorize_resources(*base_resources_,policy_,context_->capabilities);}}
}
c::ResourceSnapshot SettingsDraft::resolve_resources(const c::Authored& value)const{
    if(!context_)return {};
    if(!versioned(draft_resources_))return context_->catalog->resources(context_->selection,value);
    auto selection=draft_resources_->selection();const auto id=value.scene["theme_id"].is_null()?value.settings["display"]["theme_id"]:value.scene["theme_id"];
    // Immutable resource identity does not change for ordinary edits within the
    // same scene version. The caller still validates the new candidate binding.
    if(id==draft_resources_->theme()["theme_id"]&&value.scene["schema_version"]==draft_->scene["schema_version"])return draft_resources_;
    if(id!=draft_resources_->theme()["theme_id"])selection["theme_override"]=nullptr;
    return c::ContentCatalog::retained(*draft_resources_).theme_resources(selection,value);
}
bool SettingsDraft::dirty()const{return available()&&(!c::authored_equal(draft_->settings,base_->settings)||!c::authored_equal(draft_->scene,base_->scene));}
std::optional<std::uint64_t> SettingsDraft::revision()const{return base_?std::optional<std::uint64_t>(c::authored_revision(*base_)):std::nullopt;}
void SettingsDraft::editable()const{need(available(),"settings.unavailable");need(!active_,"settings.pending");need(state_!=DraftState::conflict,"settings.reload_required");}
SettingValue SettingsDraft::value(const std::string& id)const{
    descriptor(id);if(!available())return {{},{},false,"settings.unavailable"};const auto requested=setting(*draft_,id);const auto forced=policy_.forced.find(id);
    SettingValue result{requested,forced==policy_.forced.end()?requested:forced->second,false,{}};
    try{editable();need(forced==policy_.forced.end(),"policy.forced");c::authorize_authored(one(*draft_,policy_,id,requested,context_,draft_resources_),authority_,policy_,*revision());authorize_resources();result.editable=true;}
    catch(const p::Error& e){result.reason=e.what();}return result;
}
void SettingsDraft::set(const std::string& id,Json v){
    submission_validation_.clear();
    descriptor(id);editable();need(value(id).editable,"settings.locked");auto next=c::prepare_authored(*draft_,one(*draft_,policy_,id,std::move(v),context_,draft_resources_),authority_,policy_);
    auto resources=resolve_resources(next);
    if(resources){c::validate_resource_binding(*resources,next);c::authorize_resources(*resources,policy_,context_->capabilities);}
    draft_=std::move(next);draft_resources_=std::move(resources);result_=nullptr;state_=dirty()?DraftState::dirty:DraftState::clean;
}
void SettingsDraft::set_text(const std::string& id,std::string_view text){
    const auto& d=descriptor(id);need(text.size()<=256,"settings.input_size");
    if(d.kind==SettingKind::integer){const auto number=p::decimal(text);need(number.has_value(),"settings.integer");set(id,*number);}
    else if(d.kind==SettingKind::boolean){need(text=="true"||text=="false","settings.boolean");set(id,text=="true");}
    else{need(p::identifier(text),"settings.identifier");set(id,std::string(text));}
}
void SettingsDraft::use_default(const std::string& id){set(id,descriptor(id).default_value);}
void SettingsDraft::revert(){submission_validation_.clear();editable();draft_=base_;draft_resources_=base_resources_;result_=nullptr;state_=DraftState::clean;}
Json SettingsDraft::command(const std::string& intent,const std::string& request)const{return command(*draft_,draft_resources_,intent,request);}
Json SettingsDraft::command(const c::Authored& candidate,const c::ResourceSnapshot& resources,const std::string& intent,const std::string& request)const{
    Json ops=Json::array();for(const auto& d:setting_descriptions())if(setting(*base_,d.id)!=setting(candidate,d.id))ops.push_back({{"op","settings.set"},{"path",d.id},{"value",setting(candidate,d.id)}});
    const bool scene_changed=!c::authored_equal(candidate.scene,base_->scene);
    if(scene_changed)ops.push_back({{"op","scene.replace"},{"scene",candidate.scene}});
    Json result={{"schema_version",large_commands_?"0.5.0":context_?(scene_changed&&candidate.scene["schema_version"]!="0.2.0"?"0.4.0":"0.3.0"):"0.2.0"},{"request_id",request},{"expected_revision",base_->settings["revision"]},{"policy_generation",std::to_string(policy_.revision)},{"intent",intent},{"operations",std::move(ops)}};
    if(context_)result["content"]=resources->selection();
    if(scene_changed&&candidate.scene["schema_version"]=="0.5.0"){need(large_commands_&&context_&&context_->capabilities.count("configuration.visibility")&&context_->capabilities.count("configuration.edit-locks"),"settings.visibility");result["schema_version"]="0.7.0";}
    if(scene_changed&&candidate.scene["schema_version"]=="0.4.0"){need(large_commands_&&context_&&context_->capabilities.count("configuration.edit-locks"),"settings.edit_locks");result["schema_version"]="0.6.0";}
    if(versioned(base_resources_)||versioned(resources)){
        authorize_theme_resources();result["schema_version"]="0.8.0";result["content"]=resources->selection();
        if(!versioned(resources)){result["content"]["schema_version"]="0.2.0";result["content"]["theme_override"]=nullptr;}
        result["theme_edit"]=nullptr;
        if(!result["content"]["theme_override"].is_null()&&resources->theme_pin()!=base_resources_->theme_pin()){
            const auto& theme=resources->theme();result["theme_edit"]={{"source",base_resources_->theme_pin()},{"font",theme.at("font")},{"font_roles",theme.value("font_roles",Json())}};
        }
    }
    return result;
}
std::pair<c::Authored,c::ResourceSnapshot> SettingsDraft::prepare_scene(Json scene,c::ResourceSnapshot resources)const{
    editable();authorize_resources();auto next=*draft_;next.scene=std::move(scene);c::validate_authored(next);
    if(next.scene["schema_version"]=="0.5.0"||draft_->scene["schema_version"]=="0.5.0"){
        need(large_commands_&&context_,"settings.visibility");
        for(const char* cap:{"configuration.visibility","configuration.edit-locks","scene.visibility","scene.edit-locks"})
            need(context_->capabilities.count(cap)&&!policy_.denied_capabilities.count(cap),"policy.denied");
    }
    if(!resources)resources=resolve_resources(next);
    if(resources){c::validate_resource_binding(*resources,next);c::authorize_resources(*resources,policy_,context_->capabilities);
        if(c::authored_equal(next.scene,base_->scene)&&c::authored_equal(next.settings,base_->settings)&&resources->theme_pin()==base_resources_->theme_pin())resources=base_resources_;}
    Json check={{"schema_version",next.scene["schema_version"]=="0.5.0"||draft_->scene["schema_version"]=="0.5.0"?"0.7.0":context_?"0.4.0":"0.2.0"},{"request_id","draft.scene"},{"expected_revision",base_->settings["revision"]},
        {"policy_generation",std::to_string(policy_.revision)},{"intent","preview"},{"operations",Json::array({{{"op","scene.replace"},{"scene",next.scene}}})}};
    if(context_)check["content"]=resources->selection();
    if(versioned(base_resources_)||versioned(resources)){
        check=command(next,resources,"preview","draft.scene");
        if(check["operations"].empty())check["operations"].push_back({{"op","scene.replace"},{"scene",next.scene}});
        if(resources->selection()!=draft_resources_->selection()||resources->theme_pin()!=draft_resources_->theme_pin())
            (void)c::prepare_theme_command(*base_resources_,next,check,policy_,context_->capabilities);
    }
    // Legacy local previews retain their larger scene limit independently of the
    // old wire envelope. Versioned theme commands have the admitted full envelope.
    c::authorize_authored(check,authority_,policy_,*revision());return {std::move(next),std::move(resources)};
}
void SettingsDraft::adopt_scene(c::Authored next,c::ResourceSnapshot resources){submission_validation_.clear();draft_=std::move(next);draft_resources_=std::move(resources);result_=nullptr;state_=dirty()?DraftState::dirty:DraftState::clean;}
void SettingsDraft::replace_scene(Json scene){auto next=prepare_scene(std::move(scene));adopt_scene(std::move(next.first),std::move(next.second));}
std::optional<EditRequest> SettingsDraft::begin(const std::string& intent,const std::string& request){
    submission_validation_.clear();
    editable();need(intent=="preview"||intent=="commit","settings.intent");need(p::identifier(request),"settings.request");if(!dirty())return {};
    const auto body=command(intent,request);(void)c::prepare_authored(*base_,body,authority_,policy_);authorize_resources();if(body["schema_version"]=="0.8.0")(void)c::prepare_theme_command(*base_resources_,*draft_,body,policy_,context_->capabilities);need(tickets_<std::numeric_limits<std::uint64_t>::max(),"settings.capacity");
    EditRequest q{++tickets_,epoch_,request,body.dump()};active_=Active{q,intent,*revision(),false};result_=nullptr;state_=DraftState::pending;return q;
}
bool SettingsDraft::may_submit(const std::string& intent)const{
    if(!available()||active_||state_==DraftState::conflict||!dirty()||(intent!="preview"&&intent!="commit"))return false;
    try{const auto body=command(intent,"draft.check");auto& structural=intent=="commit"?submission_validation_.commit:submission_validation_.preview;
        if(!structural){try{c::validate_command(body);structural=true;}catch(const p::Error&){structural=false;}}
        if(!*structural)return false;
        c::authorize_authored(body,authority_,policy_,*revision());authorize_resources();return true;}catch(const p::Error&){return false;}
}
std::optional<EditRequest> SettingsDraft::active_request()const{return active_?std::optional<EditRequest>(active_->request):std::nullopt;}
std::optional<EditRequest> SettingsDraft::cancel_request(){submission_validation_.clear();if(!active_||active_->cancelled||state_==DraftState::closed)return {};active_->cancelled=true;return active_->request;}
void SettingsDraft::disconnected(){submission_validation_.clear();if(active_&&available()){state_=DraftState::unknown;result_=nullptr;}}
bool SettingsDraft::complete(std::uint64_t ticket,const Json& result){return finish(ticket,result,active_?active_->request.epoch:std::string{});}
bool SettingsDraft::reconciled(std::uint64_t ticket,const std::string& query_id,const std::string& current_epoch,const Json& response){
    if(!active_||active_->request.ticket!=ticket||state_==DraftState::closed)return false;
    try{p::validate_reconciliation_result(response,current_epoch);
        need(response["query_id"]==query_id&&response["original_producer_epoch"]==active_->request.epoch&&response["request_id"]==active_->request.request,"settings.result_scope");
        return finish(ticket,response["result"],current_epoch);
    }catch(...){disconnected();throw;}
}
bool SettingsDraft::finish(std::uint64_t ticket,const Json& result,const std::string& expected_epoch){
    submission_validation_.clear();
    if(!active_||active_->request.ticket!=ticket||state_==DraftState::closed)return false;
    try{
        c::validate_command_result(result);need(result["request_id"]==active_->request.request&&result["producer_epoch"]==expected_epoch,"settings.result_scope");
        const auto outcome=result["outcome"].get<std::string>();
        if(outcome=="accepted"){
            need(active_->intent=="commit"&&active_->revision<std::numeric_limits<std::uint64_t>::max()&&result["revision"]==std::to_string(active_->revision+1),"settings.result_revision");
            Json wrapper={{"schema_version","0.1.0"},{"query_id","draft.check"},{"original_producer_epoch",active_->request.epoch},{"request_id",active_->request.request},{"result",result}};
            p::validate_reconciliation_result(wrapper,expected_epoch);
        }else if(outcome=="unknown"){
            need(result["revision"].is_null()&&result["activation"].empty(),"settings.result_facts");
            if(available()){result_=result;state_=DraftState::unknown;}return true;
        }else{
            need(result["stored"]==false&&result["durable"]==false&&result["visible"]==false&&result["activation"].empty(),"settings.result_facts");
            if(outcome=="preview")need(active_->intent=="preview"&&result["revision"]==std::to_string(active_->revision)&&result["error"].is_null(),"settings.result_preview");
        }
        std::optional<SettingsResources> accepted_context;
        if(outcome=="accepted"&&available()&&versioned(draft_resources_))
            accepted_context=SettingsResources{std::make_shared<const c::ContentCatalog>(c::ContentCatalog::retained(*draft_resources_)),draft_resources_->selection(),context_->capabilities};
        const auto next_epoch=expected_epoch;active_.reset();if(!available())return true;
        epoch_=next_epoch;
        result_=result;
        if(outcome=="accepted"){draft_->settings["revision"]=draft_->scene["revision"]=result["revision"];base_=draft_;base_resources_=draft_resources_;if(accepted_context)context_=std::move(accepted_context);state_=DraftState::clean;}
        else state_=outcome=="conflict"?DraftState::conflict:dirty()?DraftState::dirty:DraftState::clean;
        return true;
    }catch(...){disconnected();throw;}
}
void SettingsDraft::policy(c::Policy next){
    submission_validation_.clear();
    if(state_==DraftState::closed)return;
    if(next.available&&highest_policy_&&next.revision<=*highest_policy_)next.available=false;
    if(next.available)highest_policy_=next.revision;
    policy_=std::move(next);if(!disclosure())erase();
    else if(versioned(base_resources_)||versioned(draft_resources_)){try{authorize_resources();}catch(const p::Error&){erase();}}
}
void SettingsDraft::reload(c::Authored value,std::string epoch,std::optional<SettingsResources> resources){
    submission_validation_.clear();
    need(state_!=DraftState::closed,"settings.closed");need(!active_,"settings.pending");c::validate_authored(value);need(p::identifier(epoch),"settings.epoch");
    need(resources.has_value()||(!requires_resources_&&value.scene["schema_version"]=="0.2.0"),"resource.contract");
    c::ResourceSnapshot prepared;
    if(resources){need(static_cast<bool>(resources->catalog),"resource.context");
        if(resources->selection.contains("schema_version")){need(admitted(resources,large_commands_),"settings.theme_commands");prepared=resources->catalog->theme_resources(resources->selection,value);}
        else prepared=resources->catalog->resources(resources->selection,value);
    }
    requires_resources_=requires_resources_||resources.has_value();
    if(!disclosure()){erase();return;}
    if(versioned(prepared)){need(policy_.available&&!policy_.denied_capabilities.count("configuration.theme-overrides")&&!policy_.denied_capabilities.count("theme.typography"),"policy.denied");c::authorize_resources(*prepared,policy_,resources->capabilities);}
    context_=std::move(resources);base_resources_=draft_resources_=std::move(prepared);base_=std::move(value);draft_=base_;epoch_=std::move(epoch);result_=nullptr;state_=DraftState::clean;
}
void SettingsDraft::close(){erase();active_.reset();state_=DraftState::closed;}
}
