#include "theme_command.hpp"
namespace syspane::configuration {
namespace {void need(bool b,const char* code){if(!b)throw protocol::Error(code);}}
void validate_theme_command_binding(const Json& command,const ResourceSet& resources){
    need(command.at("schema_version")=="0.8.0"&&command.at("content")==resources.selection(),"resource.selection");
    const auto& edit=command.at("theme_edit");if(edit.is_null())return;
    need(!resources.selection().at("theme_override").is_null(),"theme.binding");
    const auto& theme=resources.theme();need(theme.at("font").dump()==edit.at("font").dump(),"theme.binding");
    if(edit.at("font_roles").is_null())need(!theme.contains("font_roles"),"theme.binding");
    else need(theme.contains("font_roles")&&theme.at("font_roles").dump()==edit.at("font_roles").dump(),"theme.binding");
}
ResourceSnapshot prepare_theme_command(const ResourceSet& source,const Authored& candidate,const Json& command,
    const Policy& policy,const std::set<std::string>& capabilities){
    validate_command(command);need(command.at("schema_version")=="0.8.0","resource.contract");
    authorize_resources(source,policy,capabilities);
    need(capabilities.count("configuration.theme-overrides")&&capabilities.count("theme.typography")&&
        !policy.denied_capabilities.count("configuration.theme-overrides")&&!policy.denied_capabilities.count("theme.typography"),"policy.denied");
    const auto& selection=command.at("content");
    for(const char* key:{"package","preset"})need(source.selection().at(key)==selection.at(key),"resource.selection");
    ResourceSnapshot result;const auto& edit=command.at("theme_edit");
    if(!edit.is_null()){
        need(edit.at("source")==source.theme_pin(),"theme.source");auto proposed=source.theme();proposed["schema_version"]="0.2.0";proposed["font"]=edit.at("font");
        if(edit.at("font_roles").is_null())proposed.erase("font_roles");else proposed["font_roles"]=edit.at("font_roles");
        auto artifact=author_theme(source,proposed,policy,capabilities);need(artifact.has_value(),"theme.no_change");
        result=replace_theme_resources(source,candidate,artifact,policy,capabilities);
    }else{
        result=ContentCatalog::retained(source).theme_resources(selection,candidate);authorize_resources(*result,policy,capabilities);
    }
    validate_theme_command_binding(command,*result);return result;
}
}
