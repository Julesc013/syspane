#include "editor_binding.hpp"
#include "editor_content.hpp"
#include <cmath>
#include <regex>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
const std::string& field(const BindingInput& in,const char* key){const auto it=in.fields.find(key);need(it!=in.fields.end(),"editor.binding_field");return it->second;}
Json scope(const BindingInput& in){Json out={{"kind",field(in,"scope")}};if(out["kind"]=="registered_asset")out["asset_id"]=field(in,"asset_id");return out;}
bool escaped(const std::string& value){for(unsigned char c:value)if((c<32&&c!='\n')||c==127)return true;return false;}
}
BindingInput binding_input(const Json& binding){
    configuration::validate_binding_document(binding);BindingInput out;
    for(auto it=binding.begin();it!=binding.end();++it){if(it.value().is_string())out.fields[it.key()]=it.value().get<std::string>();}
    if(binding.contains("scope")){out.fields["scope"]=binding["scope"]["kind"];if(binding["scope"].contains("asset_id"))out.fields["asset_id"]=binding["scope"]["asset_id"];}
    if(binding["kind"]=="persistent_pin"){const auto raw=binding["key"].get<std::string>();out.fields["key_encoding"]=escaped(raw)?"escaped":"literal";out.fields["key"]=escaped(raw)?binding["key"].dump():raw;}
    if(binding["kind"]=="selector"){
        out.fields["limit"]=binding["limit"].dump();
        for(const auto& p:binding["predicates"]){const auto& v=p["value"];const bool encode=v.is_string()&&escaped(v.get<std::string>());out.predicates.push_back({p["field"],p["op"],v.is_string()?"text":v.is_boolean()?"boolean":"number",v.is_string()&&!encode?v.get<std::string>():v.dump(),encode?"escaped":"literal"});}
        for(const auto& s:binding["sort"])out.sort.push_back({s["field"],s["direction"]});
    }return out;
}
Json binding_value(const PredicateInput& input){
    if(input.type=="text")return binding_text(input.value,input.encoding);
    if(input.type=="boolean"){need(input.value=="true"||input.value=="false","editor.binding_boolean");return input.value=="true";}
    need(input.type=="number","editor.binding_type");
    static const std::regex number("^-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?$");
    need(input.value.size()<=64&&std::regex_match(input.value,number),"editor.binding_number");Json out;
    try{out=Json::parse(input.value);}catch(const Json::exception&){throw protocol::Error("editor.binding_number");}
    if(input.value.find_first_of(".eE")==std::string::npos)need(out.is_number_integer(),"editor.binding_integer_range");
    need(out.is_number()&&(!out.is_number_float()||std::isfinite(out.get<double>())),"editor.binding_number");return out;
}
Json binding_text(const std::string& value,const std::string& encoding){
    if(encoding=="literal")return value;
    need(encoding=="escaped"&&value.size()>=2&&value.size()<=4096&&value.front()=='"'&&value.back()=='"',"editor.binding_text");
    try{auto out=Json::parse(value);need(out.is_string(),"editor.binding_text");return out;}catch(const Json::exception&){throw protocol::Error("editor.binding_text");}
}
Json binding_descriptor(const BindingInput& input,const Json& original,const std::string& mode){
    const auto& kind=field(input,"kind");Json out={{"kind",kind},{"field",field(input,"field")}};
    if(kind=="unresolved_pin"){
        need(original.is_object()&&original.value("kind","")=="unresolved_pin","editor.binding_legacy");
        need(field(input,"entity_id")==original.at("entity_id")&&out["field"]==original.at("field"),"editor.binding_legacy");out=original;
    }else if(kind=="direct")for(const char* key:{"producer_id","producer_epoch","entity_id"})out[key]=field(input,key);
    else if(kind=="persistent_pin"){
        out["scope"]=scope(input);for(const char* key:{"namespace","entity_type"})out[key]=field(input,key);
        out["key"]=binding_text(field(input,"key"),input.fields.count("key_encoding")?field(input,"key_encoding"):"literal");
    }else if(kind=="selector"){
        need(input.predicates.size()<=16&&input.sort.size()<=8,"editor.binding_rows");
        need(mode=="singleton"||mode=="collection","editor.binding_mode");out["mode"]=mode;out["scope"]=scope(input);out["entity_type"]=field(input,"entity_type");out["limit"]=content_integer(field(input,"limit"),1,256);
        out["predicates"]=Json::array();for(const auto& p:input.predicates)out["predicates"].push_back({{"field",p.field},{"op",p.op},{"value",binding_value(p)}});
        out["sort"]=Json::array();for(const auto& s:input.sort)out["sort"].push_back({{"field",s.field},{"direction",s.direction}});
    }else throw protocol::Error("editor.binding_kind");
    configuration::validate_binding_document(out);return out;
}
WidgetContentEdit binding_edit(const Json& widget,const BindingInput& input,const std::vector<std::string>& fields){
    const auto& kind=widget.at("kind");const bool table=kind=="table";
    need(table||kind=="value"||kind=="status"||kind=="chart","editor.binding_widget");
    need(!fields.empty()&&fields.size()<=256&&fields.size()==widget.at("bindings").size()&&(table||fields.size()==1),"editor.binding_fields");
    auto descriptor=binding_descriptor(input,widget.at("bindings")[0],table?"collection":"singleton");need(!table||descriptor["kind"]=="selector","editor.binding_table");
    WidgetContentEdit out{widget.at("id"),Json::array(),widget.at("content")};std::set<std::string> seen;
    for(const auto& name:fields){need(seen.insert(name).second,"editor.binding_duplicate");auto b=descriptor;b["field"]=name;
        need(b["kind"]!="unresolved_pin"||b==widget.at("bindings")[0],"editor.binding_legacy");configuration::validate_binding_document(b);out.bindings.push_back(std::move(b));}
    return out;
}
}
