#include "editor_layout.hpp"
#include <algorithm>
namespace syspane::interfaces {
namespace {
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
const Json& widget(const Json& scene,const std::string& id){for(const auto& w:scene.at("widgets"))if(w.at("id")==id)return w;throw protocol::Error("editor.target");}
std::optional<std::string> parent(const Json& scene,const std::string& id){for(const auto& w:scene.at("widgets"))if(w.contains("children"))for(const auto& child:w.at("children"))if(child==id)return w.at("id").get<std::string>();return {};}
const Json& siblings(const Json& scene,const std::string& id){const auto p=parent(scene,id);return p?widget(scene,*p).at("children"):scene.at("roots");}
LayoutVariantInput input(const Json& value){
    LayoutVariantInput out;out.kind=value.at("kind");out.by_kind={
        {"fixed",{{"x","0"},{"y","0"},{"width","180"},{"height","80"}}},
        {"flow",{{"width_min","32"},{"width_preferred","180"},{"width_max","32768"},{"height_min","16"},{"height_preferred","80"},{"height_max","32768"},{"anchor","start"}}},
        {"canvas",{{"width","180"},{"height","80"},{"overflow","diagnose"}}},
        {"stack",{{"axis","vertical"},{"gap_dip","8"},{"overflow","diagnose"}}},
        {"grid",{{"columns","2"},{"gap_dip","8"},{"overflow","diagnose"}}}};
    auto& fields=out.by_kind.at(out.kind);
    for(auto& f:fields){const auto split=f.first.find('_');
        const auto& v=out.kind=="flow"&&split!=std::string::npos?value.at(f.first.substr(0,split)).at(f.first.substr(split+1)):value.at(f.first);
        f.second=v.is_string()?v.get<std::string>():v.dump();}
    return out;
}
Json variant(const LayoutVariantInput& in,bool group){
    need(group?(in.kind=="fixed"||in.kind=="canvas"||in.kind=="stack"||in.kind=="grid"):(in.kind=="fixed"||in.kind=="flow"),"editor.layout_kind");
    const auto found=in.by_kind.find(in.kind);need(found!=in.by_kind.end(),"editor.layout_fields");const auto& f=found->second;
    auto field=[&](const char* key)->const std::string&{const auto at=f.find(key);need(at!=f.end(),"editor.layout_fields");return at->second;};
    auto number=[&](const char* key,double minimum,double maximum){const double value=content_number(field(key));need(value>=minimum&&value<=maximum,"editor.layout_bounds");return value;};
    auto choice=[&](const char* key,std::initializer_list<const char*> options){const auto& v=field(key);need(std::find(options.begin(),options.end(),v)!=options.end(),"editor.layout_choice");return v;};
    Json value={{"kind",in.kind}};
    if(in.kind=="fixed"){value["x"]=number("x",-100000,100000);value["y"]=number("y",-100000,100000);}
    if(in.kind=="fixed"||in.kind=="canvas"){value["width"]=number("width",32,32768);value["height"]=number("height",16,32768);}
    if(in.kind=="flow"){
        for(const std::string axis:{"width","height"}){
            const double lo=number((axis+"_min").c_str(),0,32768),preferred=number((axis+"_preferred").c_str(),0,32768),hi=number((axis+"_max").c_str(),0,32768);
            need(lo<=preferred&&preferred<=hi,"editor.layout_bounds");value[axis]={{"min",lo},{"preferred",preferred},{"max",hi}};
        }value["anchor"]=choice("anchor",{"start","center","end","stretch"});
    }
    if(in.kind=="stack")value["axis"]=choice("axis",{"horizontal","vertical"});
    if(in.kind=="grid")value["columns"]=content_integer(field("columns"),1,32);
    if(in.kind=="stack"||in.kind=="grid")value["gap_dip"]=number("gap_dip",0,256);
    if(in.kind=="canvas"||in.kind=="stack"||in.kind=="grid")value["overflow"]=choice("overflow",{"scroll","diagnose"});
    return value;
}
}
LayoutInput layout_input(const Json& scene,const std::string& id){
    const auto& w=widget(scene,id);const auto& layout=w.at("layout");LayoutInput out;out.variants.push_back(input(layout.at("base")));out.breakpoints_present=layout.contains("breakpoints");
    if(out.breakpoints_present)for(const auto& row:layout.at("breakpoints")){out.thresholds.push_back(row.at("min_width_dip").dump());out.variants.push_back(input(row.at("layout")));}
    const auto& display=w.at("display");out.display_kind=display.contains("local_id")?"local_id":"role";out.display_value=display.at(out.display_kind);out.priority=w.at("priority");
    const auto& list=siblings(scene,id);out.sibling=std::to_string(std::distance(list.begin(),std::find(list.begin(),list.end(),id)));return out;
}
std::vector<SceneEdit> layout_edits(const Json& scene,const std::string& id,const LayoutInput& in){
    const auto& w=widget(scene,id);need(!in.variants.empty()&&in.variants.size()<=9&&in.thresholds.size()+1==in.variants.size(),"editor.layout_variants");
    Json layout={{"base",variant(in.variants[0],w.at("kind")=="group")}};double previous=-1;
    if(in.breakpoints_present||!in.thresholds.empty())layout["breakpoints"]=Json::array();
    for(std::size_t n=0;n<in.thresholds.size();++n){const double width=content_number(in.thresholds[n]);need(width>=0&&width<=32768&&width>previous,"editor.layout_threshold");previous=width;
        layout["breakpoints"].push_back({{"min_width_dip",width},{"layout",variant(in.variants[n+1],w.at("kind")=="group")}});}
    need(in.priority=="essential"||in.priority=="normal"||in.priority=="secondary","editor.layout_priority");
    need((in.display_kind=="local_id"||in.display_kind=="role")&&protocol::identifier(in.display_value),"editor.layout_display");
    std::vector<SceneEdit> edits{WidgetPropertyEdit{id,WidgetProperty::layout,std::move(layout)},WidgetPropertyEdit{id,WidgetProperty::priority,in.priority}};
    const Json display={{in.display_kind,in.display_value}};
    if(display!=w.at("display")){std::string root=id;for(unsigned depth=0;;++depth){need(depth<16,"editor.layout_depth");const auto p=parent(scene,root);if(!p)break;root=*p;}edits.push_back(RootDisplayEdit{root,display});}
    const auto& list=siblings(scene,id);const auto index=content_integer(in.sibling,0,static_cast<unsigned>(list.size()-1));
    if(list.at(index)!=id)edits.push_back(ReparentWidgets{{id},parent(scene,id),index});
    return edits;
}
}
