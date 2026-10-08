#pragma once
#include "editor_draft.hpp"
#include "transaction.hpp"
#include "../configuration/settings_content_fixture.hpp"
namespace theme_history_fixture {
namespace c=syspane::configuration;namespace ui=syspane::interfaces;using c::Json;
inline c::Authority authority(){return {true,"desktop",{"desktop"}};}
inline c::Policy policy(std::uint64_t revision=7){c::Policy p;p.available=true;p.revision=revision;p.disclosure[{"desktop","inspector"}]={"operational"};p.disclosure[{"desktop","accessibility"}]={"operational"};return p;}
inline std::set<std::string> capabilities(){return {"scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides","configuration.edit-locks","configuration.visibility"};}
inline ui::SettingsResources context(const settings_fixture::Fixture& f){auto out=f.resources();out.capabilities=capabilities();return out;}
inline ui::SettingsResources context(const c::ResourceSet& r){return {std::make_shared<const c::ContentCatalog>(c::ContentCatalog::retained(r)),r.selection(),capabilities()};}
inline bool fonts(ui::EditorDraft& d,const Json& artifact){const auto& theme=artifact.at("theme");return d.set_theme_fonts(theme.at("font"),theme.value("font_roles",Json()));}
struct Store:c::GenerationStore {
    c::Committed current,previous;unsigned writes=0;
    explicit Store(const settings_fixture::Fixture& f):current{f.authored,{},f.catalog->resources(f.document["selection"],f.authored)}{}
    c::Committed load()const override{return current;}
    std::vector<c::CommitReceipt> receipts()const override{std::vector<c::CommitReceipt> out;for(const auto* v:{&current,&previous})if(v->identity)out.push_back({*v->identity,c::authored_revision(v->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string& principal,const std::string& epoch,const std::string& request)const override{for(const auto* v:{&current,&previous})if(v->identity&&v->identity->principal==principal&&v->identity->epoch==epoch&&v->identity->request==request)return *v;return {};}
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{guard();previous=current;current=next;++writes;return c::Publication::durable;}
    c::ResourceProvider provider(){return c::make_resource_provider(*this,capabilities(),[]()->std::vector<c::ContentPackage>{throw syspane::protocol::Error("test.unexpected_import");});}
};
}
