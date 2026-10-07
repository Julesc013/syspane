#include "settings_draft.hpp"
#include "settings_descriptors.hpp"
#include "reconciliation.hpp"
#include <algorithm>
#include <limits>
namespace syspane::interfaces {
namespace {
namespace c=configuration;namespace p=protocol;
void need(bool value,const char* code){if(!value)throw p::Error(code);}
const SettingDescription& descriptor(const std::string& id){const auto& rows=setting_descriptions();const auto it=std::find_if(rows.begin(),rows.end(),[&](const auto& r){return r.id==id;});need(it!=rows.end(),"settings.path");return *it;}
const Json& setting(const c::Authored& value,const std::string& id){const auto dot=id.find('.');return value.settings.at(id.substr(0,dot)).at(id.substr(dot+1));}
Json one(const c::Authored& value,const c::Policy& policy,const std::string& id,Json v){return {{"schema_version","0.2.0"},{"request_id","draft.validation"},{"expected_revision",value.settings["revision"]},{"policy_generation",std::to_string(policy.revision)},{"intent","preview"},{"operations",Json::array({{{"op","settings.set"},{"path",id},{"value",std::move(v)}}})}};}
}
const std::vector<SettingDescription>& setting_descriptions(){
    static const std::vector<SettingDescription> rows=[] {std::vector<SettingDescription> out;
        for(const auto& d:c::descriptors)out.push_back({d.path,d.page,d.units,d.activation,d.label_id,d.help_id,d.label,d.help,
            d.kind==c::Kind::boolean?SettingKind::boolean:d.kind==c::Kind::integer?SettingKind::integer:SettingKind::identifier,Json::parse(d.default_json)});
        return out;}();return rows;
}
SettingsDraft::SettingsDraft(c::Authority authority,c::Policy policy,c::Authored value,std::string epoch):authority_(std::move(authority)),policy_(std::move(policy)){
    if(policy_.available)highest_policy_=policy_.revision;
    reload(std::move(value),std::move(epoch));
}
bool SettingsDraft::disclosure()const{return policy_.available&&c::permits(authority_,policy_,"inspector","operational")&&c::permits(authority_,policy_,"accessibility","operational");}
void SettingsDraft::erase(){base_.reset();draft_.reset();result_=nullptr;if(active_)active_->request.body.clear();state_=DraftState::unavailable;}
bool SettingsDraft::dirty()const{return available()&&draft_->settings!=base_->settings;}
std::optional<std::uint64_t> SettingsDraft::revision()const{return base_?std::optional<std::uint64_t>(c::authored_revision(*base_)):std::nullopt;}
void SettingsDraft::editable()const{need(available(),"settings.unavailable");need(!active_,"settings.pending");need(state_!=DraftState::conflict,"settings.reload_required");}
SettingValue SettingsDraft::value(const std::string& id)const{
    descriptor(id);if(!available())return {{},{},false,"settings.unavailable"};const auto requested=setting(*draft_,id);const auto forced=policy_.forced.find(id);
    SettingValue result{requested,forced==policy_.forced.end()?requested:forced->second,false,{}};
    try{editable();need(forced==policy_.forced.end(),"policy.forced");c::authorize_authored(one(*draft_,policy_,id,requested),authority_,policy_,*revision());result.editable=true;}
    catch(const p::Error& e){result.reason=e.what();}return result;
}
void SettingsDraft::set(const std::string& id,Json v){
    descriptor(id);editable();need(value(id).editable,"settings.locked");auto next=c::prepare_authored(*draft_,one(*draft_,policy_,id,std::move(v)),authority_,policy_);
    draft_=std::move(next);result_=nullptr;state_=dirty()?DraftState::dirty:DraftState::clean;
}
void SettingsDraft::set_text(const std::string& id,std::string_view text){
    const auto& d=descriptor(id);need(text.size()<=256,"settings.input_size");
    if(d.kind==SettingKind::integer){const auto number=p::decimal(text);need(number.has_value(),"settings.integer");set(id,*number);}
    else if(d.kind==SettingKind::boolean){need(text=="true"||text=="false","settings.boolean");set(id,text=="true");}
    else{need(p::identifier(text),"settings.identifier");set(id,std::string(text));}
}
void SettingsDraft::use_default(const std::string& id){set(id,descriptor(id).default_value);}
void SettingsDraft::revert(){editable();draft_=base_;result_=nullptr;state_=DraftState::clean;}
Json SettingsDraft::command(const std::string& intent,const std::string& request)const{
    Json ops=Json::array();for(const auto& d:setting_descriptions())if(setting(*base_,d.id)!=setting(*draft_,d.id))ops.push_back({{"op","settings.set"},{"path",d.id},{"value",setting(*draft_,d.id)}});
    return {{"schema_version","0.2.0"},{"request_id",request},{"expected_revision",base_->settings["revision"]},{"policy_generation",std::to_string(policy_.revision)},{"intent",intent},{"operations",std::move(ops)}};
}
std::optional<EditRequest> SettingsDraft::begin(const std::string& intent,const std::string& request){
    editable();need(intent=="preview"||intent=="commit","settings.intent");need(p::identifier(request),"settings.request");if(!dirty())return {};
    const auto body=command(intent,request);(void)c::prepare_authored(*base_,body,authority_,policy_);need(tickets_<std::numeric_limits<std::uint64_t>::max(),"settings.capacity");
    EditRequest q{++tickets_,epoch_,request,body.dump()};active_=Active{q,intent,*revision(),false};result_=nullptr;state_=DraftState::pending;return q;
}
bool SettingsDraft::may_submit(const std::string& intent)const{
    if(!available()||active_||state_==DraftState::conflict||!dirty()||(intent!="preview"&&intent!="commit"))return false;
    try{c::authorize_authored(command(intent,"draft.check"),authority_,policy_,*revision());return true;}catch(const p::Error&){return false;}
}
std::optional<EditRequest> SettingsDraft::active_request()const{return active_?std::optional<EditRequest>(active_->request):std::nullopt;}
std::optional<EditRequest> SettingsDraft::cancel_request(){if(!active_||active_->cancelled||state_==DraftState::closed)return {};active_->cancelled=true;return active_->request;}
void SettingsDraft::disconnected(){if(active_&&available()){state_=DraftState::unknown;result_=nullptr;}}
bool SettingsDraft::complete(std::uint64_t ticket,const Json& result){return finish(ticket,result,active_?active_->request.epoch:std::string{});}
bool SettingsDraft::reconciled(std::uint64_t ticket,const std::string& query_id,const std::string& current_epoch,const Json& response){
    if(!active_||active_->request.ticket!=ticket||state_==DraftState::closed)return false;
    try{p::validate_reconciliation_result(response,current_epoch);
        need(response["query_id"]==query_id&&response["original_producer_epoch"]==active_->request.epoch&&response["request_id"]==active_->request.request,"settings.result_scope");
        return finish(ticket,response["result"],current_epoch);
    }catch(...){disconnected();throw;}
}
bool SettingsDraft::finish(std::uint64_t ticket,const Json& result,const std::string& expected_epoch){
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
        const auto next_epoch=expected_epoch;active_.reset();if(!available())return true;
        epoch_=next_epoch;
        result_=result;
        if(outcome=="accepted"){draft_->settings["revision"]=draft_->scene["revision"]=result["revision"];base_=draft_;state_=DraftState::clean;}
        else state_=outcome=="conflict"?DraftState::conflict:dirty()?DraftState::dirty:DraftState::clean;
        return true;
    }catch(...){disconnected();throw;}
}
void SettingsDraft::policy(c::Policy next){
    if(state_==DraftState::closed)return;
    if(next.available&&highest_policy_&&next.revision<=*highest_policy_)next.available=false;
    if(next.available)highest_policy_=next.revision;
    policy_=std::move(next);if(!disclosure())erase();
}
void SettingsDraft::reload(c::Authored value,std::string epoch){
    need(state_!=DraftState::closed,"settings.closed");need(!active_,"settings.pending");c::validate_authored(value);need(p::identifier(epoch),"settings.epoch");
    if(!disclosure()){erase();return;}base_=std::move(value);draft_=base_;epoch_=std::move(epoch);result_=nullptr;state_=DraftState::clean;
}
void SettingsDraft::close(){erase();active_.reset();state_=DraftState::closed;}
}
