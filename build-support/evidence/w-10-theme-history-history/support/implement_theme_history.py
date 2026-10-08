from pathlib import Path
r=Path.cwd()
def change(n,f):
 p=r/n;p.write_text(f(p.read_text()),encoding='utf-8',newline='\n')
def settings(s):
 s=s.replace('#include "reconciliation.hpp"','#include "reconciliation.hpp"\n#include "theme_command.hpp"')
 s=s.replace('Json one(const c::Authored&', '''bool versioned(const c::ResourceSnapshot& resource){return resource&&resource->selection().contains("schema_version");}
bool admitted(const std::optional<SettingsResources>& context,bool large){
    if(!large||!context)return false;
    for(const char* cap:{"configuration.theme-overrides","theme.typography","configuration.visibility","configuration.edit-locks","scene.content","scene.edit-locks","scene.visibility"})
        if(!context->capabilities.count(cap))return false;
    return true;
}
Json one(const c::Authored&''')
 s=s.replace('const std::optional<SettingsResources>& context){','const std::optional<SettingsResources>& context,const c::ResourceSnapshot& resource){')
 s=s.replace('if(context)command["content"]=context->selection;','if(context)command["content"]=resource->selection();\n    if(versioned(resource)){command["schema_version"]="0.8.0";command["theme_edit"]=nullptr;}')
 s=s.replace('id,requested,context_)','id,requested,context_,draft_resources_)').replace('id,std::move(v),context_)','id,std::move(v),context_,draft_resources_)')
 s=s.replace('void SettingsDraft::authorize_resources()const{if(context_)c::authorize_resources(*draft_resources_,policy_,context_->capabilities);}', '''bool SettingsDraft::theme_commands()const{return admitted(context_,large_commands_);}
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
    if(id!=draft_resources_->theme()["theme_id"])selection["theme_override"]=nullptr;
    return c::ContentCatalog::retained(*draft_resources_).theme_resources(selection,value);
}''')
 s=s.replace('auto resources=context_?context_->catalog->resources(context_->selection,next):c::ResourceSnapshot{};','auto resources=resolve_resources(next);',1)
 start=s.index('Json SettingsDraft::command(');end=s.index('void SettingsDraft::replace_scene',start)
 block=s[start:end];block=block.replace('Json SettingsDraft::command(const std::string& intent,const std::string& request)const{','Json SettingsDraft::command(const c::Authored& candidate,const c::ResourceSnapshot& resources,const std::string& intent,const std::string& request)const{')
 block=block.replace('*draft_','candidate').replace('draft_->','candidate.')
 block=block.replace('if(context_)result["content"]=context_->selection;','if(context_)result["content"]=resources->selection();')
 block=block.replace('    return result;', '''    if(versioned(base_resources_)||versioned(resources)){
        authorize_theme_resources();result["schema_version"]="0.8.0";result["content"]=resources->selection();
        if(!versioned(resources)){result["content"]["schema_version"]="0.2.0";result["content"]["theme_override"]=nullptr;}
        result["theme_edit"]=nullptr;
        if(!result["content"]["theme_override"].is_null()&&resources->theme_pin()!=base_resources_->theme_pin()){
            const auto& theme=resources->theme();result["theme_edit"]={{"source",base_resources_->theme_pin()},{"font",theme.at("font")},{"font_roles",theme.value("font_roles",Json())}};
        }
    }
    return result;''')
 s=s[:start]+'Json SettingsDraft::command(const std::string& intent,const std::string& request)const{return command(*draft_,draft_resources_,intent,request);}\n'+block+s[end:]
 start=s.index('void SettingsDraft::replace_scene');end=s.index('std::optional<EditRequest> SettingsDraft::begin',start)
 s=s[:start]+'''std::pair<c::Authored,c::ResourceSnapshot> SettingsDraft::prepare_scene(Json scene,c::ResourceSnapshot resources)const{
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
        (void)c::prepare_theme_command(*base_resources_,next,check,policy_,context_->capabilities);
    }
    // Legacy local previews retain their larger scene limit independently of the
    // old wire envelope. Versioned theme commands have the admitted full envelope.
    c::authorize_authored(check,authority_,policy_,*revision());return {std::move(next),std::move(resources)};
}
void SettingsDraft::adopt_scene(c::Authored next,c::ResourceSnapshot resources){draft_=std::move(next);draft_resources_=std::move(resources);result_=nullptr;state_=dirty()?DraftState::dirty:DraftState::clean;}
void SettingsDraft::replace_scene(Json scene){auto next=prepare_scene(std::move(scene));adopt_scene(std::move(next.first),std::move(next.second));}
'''+s[end:]
 s=s.replace('authorize_resources();need(tickets_', 'authorize_resources();if(body["schema_version"]=="0.8.0")(void)c::prepare_theme_command(*base_resources_,*draft_,body,policy_,context_->capabilities);need(tickets_')
 s=s.replace('policy_=std::move(next);if(!disclosure())erase();','''policy_=std::move(next);if(!disclosure())erase();
    else if(versioned(base_resources_)||versioned(draft_resources_)){try{authorize_resources();}catch(const p::Error&){erase();}}''')
 s=s.replace('if(resources){need(static_cast<bool>(resources->catalog),"resource.context");prepared=resources->catalog->resources(resources->selection,value);}', '''if(resources){need(static_cast<bool>(resources->catalog),"resource.context");
        if(resources->selection.contains("schema_version")){need(admitted(resources,large_commands_),"settings.theme_commands");prepared=resources->catalog->theme_resources(resources->selection,value);}
        else prepared=resources->catalog->resources(resources->selection,value);
    }''')
 s=s.replace('context_=std::move(resources);base_resources_', '''if(versioned(prepared)){need(policy_.available&&!policy_.denied_capabilities.count("configuration.theme-overrides")&&!policy_.denied_capabilities.count("theme.typography"),"policy.denied");c::authorize_resources(*prepared,policy_,resources->capabilities);}
    context_=std::move(resources);base_resources_''')
 return s
change('source/interfaces/settings_draft.cpp',settings)
def editor(s):
 s=s.replace('#include "authored_equal.hpp"','#include "authored_equal.hpp"\n#include "theme_resources.hpp"')
 start=s.index('std::size_t EditorDraft::history_bytes()const');end=s.index('void EditorDraft::clear_history()',start)
 s=s[:start]+'''bool EditorDraft::theme_fonts_available()const{
    if(!available()||!resources()||!transaction_.theme_commands())return false;
    try{transaction_.editable();transaction_.authorize_resources();transaction_.authorize_theme_resources();
        c::authorize_authored({{"schema_version","0.8.0"},{"theme_edit",Json::object()},{"intent","preview"},{"policy_generation",std::to_string(transaction_.policy_.revision)},{"expected_revision",std::to_string(*revision())},{"operations",Json::array({{{"op","scene.replace"}}})}},transaction_.authority_,transaction_.policy_,*revision());return true;
    }catch(const protocol::Error&){return false;}
}
bool EditorDraft::set_theme_fonts(const Json& font,const Json& roles){
    transaction_.editable();need(theme_fonts_available(),"editor.theme_unavailable");auto proposed=resources()->theme();proposed["schema_version"]="0.2.0";proposed["font"]=font;
    if(roles.is_null())proposed.erase("font_roles");else proposed["font_roles"]=roles;
    const auto artifact=c::author_theme(*resources(),proposed,transaction_.policy_,transaction_.context_->capabilities);if(!artifact)return false;
    auto candidate=*transaction_.draft_;candidate.scene["theme_id"]=artifact->theme["theme_id"];
    auto retained=c::replace_theme_resources(*resources(),candidate,artifact,transaction_.policy_,transaction_.context_->capabilities);
    return record(std::move(candidate.scene),selected_,std::move(retained));
}
std::size_t EditorDraft::history_bytes(const std::deque<Change>& undo,const std::deque<Change>& redo)const{
    std::size_t bytes=0;std::set<const c::ResourceSet*> snapshots;std::set<const c::ContentPackage*> packages;
    if(transaction_.base_resources_){snapshots.insert(transaction_.base_resources_.get());for(const auto& p:transaction_.base_resources_->packages())packages.insert(p.get());}
    const auto charge=[&](const State& state){
        if(!state.resources||!snapshots.insert(state.resources.get()).second)return;
        const auto& resources=*state.resources;bytes+=resources.selection().dump().size()+resources.theme().dump().size()+resources.theme_pin().dump().size()+Json(resources.required()).dump().size();
        for(const auto& p:resources.packages())if(packages.insert(p.get()).second){bytes+=p->manifest.size();for(const auto& asset:p->assets)bytes+=asset.first.size()+asset.second.size();}
    };
    for(const auto* stack:{&undo,&redo})for(const auto& entry:*stack){bytes+=entry.bytes;charge(entry.before);charge(entry.after);}
    return bytes;
}
std::size_t EditorDraft::history_bytes()const{return history_bytes(undo_,redo_);}
'''+s[end:]
 start=s.index('    if(c::authored_equal(candidate,*scene()))return false;',s.index('bool EditorDraft::execute'));end=s.index('bool EditorDraft::travel',start)
 s=s[:start]+'''    if(c::authored_equal(candidate,*scene()))return false;
    return record(std::move(candidate),std::move(selected));
}
bool EditorDraft::record(Json candidate,std::vector<std::string> selected,c::ResourceSnapshot resources){
    auto prepared=transaction_.prepare_scene(std::move(candidate),std::move(resources));
    if(c::authored_equal(prepared.first.scene,*scene())&&(!prepared.second||prepared.second->selection()==transaction_.draft_resources_->selection()))return false;
    Change change{{*scene(),selected_,transaction_.draft_resources_},{prepared.first.scene,surviving(prepared.first.scene,selected),prepared.second},0};
    change.bytes=change.before.scene.dump().size()+change.after.scene.dump().size()+Json(change.before.selection).dump().size()+Json(change.after.selection).dump().size();
    auto next=undo_;next.push_back(change);const std::deque<Change> empty;
    while(next.size()>64||history_bytes(next,empty)>8*1024*1024)next.pop_front();
    auto selection=change.after.selection;transaction_.adopt_scene(std::move(prepared.first),std::move(prepared.second));
    selected_.swap(selection);undo_.swap(next);redo_.clear();return true;
}
'''+s[end:]
 s=s.replace('transaction_.replace_scene(target.scene);selected_.swap(selection);','auto prepared=transaction_.prepare_scene(target.scene,target.resources);transaction_.adopt_scene(std::move(prepared.first),std::move(prepared.second));selected_.swap(selection);')
 return s
change('source/interfaces/editor_draft.cpp',editor)
print('Connected shared immutable resources, history and source-bound theme Apply.')
