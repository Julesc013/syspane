#include "editor_visibility.hpp"
#include "authored_equal.hpp"
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
void targets(const std::vector<std::string>& ids){need(!ids.empty()&&ids.size()<=256,"editor.targets");std::set<std::string> unique;for(const auto& id:ids)need(protocol::identifier(id)&&unique.insert(id).second,"editor.targets");}
}
void visibility_source(const Json& binding){
    try{configuration::validate_visibility_document({{"schema_version","0.1.0"},{"binding",binding},{"op","eq"},{"value",0},{"unit","1"}});}
    catch(const protocol::Error&){throw protocol::Error("editor.visibility_binding");}
}
VisibilityInput visibility_input(const Json& scene,const std::vector<std::string>& ids){
    configuration::validate_scene_document(scene);targets(ids);VisibilityInput out;
    out.binding={{"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type","network.interface"},{"field","network.receive_bytes"},{"predicates",Json::array()},{"mode","singleton"},{"sort",Json::array()},{"limit",1}};
    Json own;bool first=true,mixed=false;
    for(const auto& id:ids){const Json* widget=nullptr;for(const auto& w:scene.at("widgets"))if(w.at("id")==id)widget=&w;need(widget!=nullptr,"editor.target");const auto rule=widget->value("visibility",Json());if(first){own=rule;first=false;}else if(!configuration::authored_equal(own,rule))mixed=true;}
    if(mixed){out.mode="keep";return out;}if(own.is_null())return out;
    out.mode="conditional";out.binding=own.at("binding");out.unit=own.at("unit");out.comparison.op=own.at("op");const auto& value=own.at("value");
    out.comparison.type=value.is_string()?"text":value.is_boolean()?"boolean":"number";
    bool escaped=false;if(value.is_string())for(unsigned char c:value.get_ref<const std::string&>())if((c<32&&c!='\n')||c==127)escaped=true;
    out.comparison.encoding=escaped?"escaped":"literal";out.comparison.value=value.is_string()&&!escaped?value.get<std::string>():value.dump();return out;
}
std::optional<SetWidgetVisibility> visibility_edit(const std::vector<std::string>& ids,const VisibilityInput& input){
    targets(ids);if(input.mode=="keep")return {};if(input.mode=="always")return SetWidgetVisibility{ids,{}};
    need(input.mode=="conditional","editor.visibility_mode");need(input.comparison.value.size()<=4096&&input.unit.size()<=64,"editor.visibility_input");visibility_source(input.binding);
    Json rule={{"schema_version","0.1.0"},{"binding",input.binding},{"op",input.comparison.op},{"value",binding_value(input.comparison)},{"unit",input.unit}};
    configuration::validate_visibility_document(rule);return SetWidgetVisibility{ids,std::move(rule)};
}
}
