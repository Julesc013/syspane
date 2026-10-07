#pragma once
#include "content.hpp"
#include <vector>
namespace syspane::interfaces {
using configuration::Json;
enum class SettingKind {integer,boolean,identifier};
struct SettingDescription {
    std::string id,page,units,activation,label_id,help_id,label,help;
    SettingKind kind;Json default_value;
};
const std::vector<SettingDescription>& setting_descriptions();
struct SettingValue {Json requested,effective;bool editable=false;std::string reason;};
struct EditRequest {std::uint64_t ticket;std::string epoch,request,body;};
enum class DraftState {clean,dirty,pending,unknown,conflict,unavailable,closed};
// Trusted host prepares the immutable catalog off the UI loop from the admitted
// generation. Selection is an exact package/preset pin, never a path or fallback.
struct SettingsResources {
    std::shared_ptr<const configuration::ContentCatalog> catalog;
    Json selection;
    std::set<std::string> capabilities;
};
// Serialized native owner; immutable snapshots enter only through construction/reload.
class SettingsDraft {
public:
    SettingsDraft(configuration::Authority,configuration::Policy,configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={});
    SettingValue value(const std::string&)const;
    void set(const std::string&,Json);
    void set_text(const std::string&,std::string_view);
    void use_default(const std::string&);
    void revert();
    std::optional<EditRequest> begin(const std::string& intent,const std::string& request);
    std::optional<EditRequest> active_request()const;
    std::optional<EditRequest> cancel_request();
    bool complete(std::uint64_t ticket,const Json& result);
    bool reconciled(std::uint64_t ticket,const std::string& query_id,const std::string& current_epoch,const Json& response);
    void disconnected();
    void policy(configuration::Policy);
    void reload(configuration::Authored,std::string epoch,std::optional<SettingsResources> resources={});
    void close();
    DraftState state()const{return state_;}
    bool available()const{return base_.has_value()&&state_!=DraftState::closed;}
    bool dirty()const;
    bool may_submit(const std::string& intent)const;
    const Json& last_result()const{return result_;}
    std::optional<std::uint64_t> revision()const;
private:
    friend class EditorDraft;
    // Shared scene staging for the editor; publication still uses begin/complete.
    void replace_scene(Json);
    void editable()const;
    bool disclosure()const;
    void erase();
    void authorize_resources()const;
    Json command(const std::string&,const std::string&)const;
    bool finish(std::uint64_t,const Json&,const std::string& expected_epoch);
    configuration::Authority authority_;configuration::Policy policy_;
    std::optional<configuration::Authored> base_,draft_;
    std::optional<SettingsResources> context_;
    configuration::ResourceSnapshot base_resources_,draft_resources_;
    bool requires_resources_=false;
    std::string epoch_;std::uint64_t tickets_=0;std::optional<std::uint64_t> highest_policy_;
    struct Active {EditRequest request;std::string intent;std::uint64_t revision;bool cancelled=false;};
    std::optional<Active> active_;DraftState state_=DraftState::unavailable;Json result_;
};
}
