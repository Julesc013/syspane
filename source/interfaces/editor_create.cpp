#include "editor_create.hpp"
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
const std::string& field(const CreateInput& input,const char* key){const auto it=input.fields.find(key);need(it!=input.fields.end(),"editor.create_field");return it->second;}
Json selector(const CreateInput& in,const std::string& field,bool table){return {{"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type",in.fields.at("entity_type")},{"field",field},
    {"mode",table?"collection":"singleton"},{"predicates",Json::array()},{"sort",Json::array()},{"limit",table?8:1}};}
}
CreateInput create_input(const std::string& kind){
    static const std::map<std::string,std::pair<unsigned,unsigned>> sizes={{"text",{180,80}},{"value",{240,100}},{"status",{240,120}},{"table",{420,180}},{"chart",{400,240}},{"image",{160,120}},{"group",{320,240}}};
    const auto it=sizes.find(kind);need(it!=sizes.end(),"editor.create_kind");CreateInput out;out.kind=kind;auto title=kind;title[0]=static_cast<char>(title[0]-'a'+'A');
    out.fields={{"title",title},{"x","20"},{"y","20"},{"width",std::to_string(it->second.first)},{"height",std::to_string(it->second.second)},
        {"body",kind=="image"?"Image":"Text"},{"entity_type","network.interface"},{"field","network.receive_bytes"},{"second_field","network.transmit_bytes"}};return out;
}
InsertWidget create_widget(const Json& scene,const CreateInput& in,const std::string& id,const Json& root_display,const ContentChoices& choices){
    need(scene.at("schema_version")=="0.3.0","editor.create_version");(void)create_input(in.kind);need(protocol::identifier(id),"editor.identity");
    Json display=root_display;std::size_t index=scene.at("roots").size();
    if(in.parent){bool found=false;for(const auto& w:scene.at("widgets"))if(w.at("id")==*in.parent){need(w.at("kind")=="group","editor.parent");display=w.at("display");index=w.at("children").size();found=true;break;}need(found,"editor.parent");}
    Json base={{"kind","fixed"}};for(const char* k:{"x","y","width","height"}){const double n=content_number(field(in,k));const bool position=std::string(k)=="x"||std::string(k)=="y";const double minimum=position?-100000:std::string(k)=="width"?32:16,maximum=position?100000:32768;need(n>=minimum&&n<=maximum,"editor.create_geometry");base[k]=n;}
    Json w={{"id",id},{"kind",in.kind},{"title",field(in,"title")},{"display",std::move(display)},{"layout",{{"base",std::move(base)}}},{"bindings",Json::array()},{"priority","normal"},{"content",Json::object()}};
    if(in.kind=="text")w["content"]={{"body",field(in,"body")}};
    else if(in.kind=="image"){
        bool found=false;for(const auto& c:choices.images)if(c.value==in.asset)found=true;need(found,"editor.create_asset");
        w["content"]={{"asset",in.asset},{"alt",field(in,"body")},{"width_dip",160},{"height_dip",120},{"fit","contain"}};
    }else if(in.kind=="group")w["children"]=Json::array();
    else{
        (void)field(in,"entity_type");const bool table=in.kind=="table";auto binding=selector(in,field(in,"field"),table);configuration::validate_binding_document(binding);w["bindings"].push_back(binding);
        if(table){need(field(in,"field")!=field(in,"second_field"),"editor.create_columns");binding=selector(in,field(in,"second_field"),true);configuration::validate_binding_document(binding);w["bindings"].push_back(binding);w["content"]={{"columns",Json::array({{{"label","Receive"}},{{"label","Sent"}}})}};}
        if(in.kind=="chart")w["content"]={{"window_ms",60000},{"max_points",256},{"interpolation","linear"},{"axis",{{"mode","auto"},{"include_zero",true}}}};
    }
    return {std::move(w),in.parent,index,true};
}
}
