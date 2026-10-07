#include "layout.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <limits>
#include <tuple>

namespace s=syspane::scene;namespace c=syspane::configuration;using c::Json;
void check(bool ok,const char* what){if(!ok)throw std::runtime_error(what);}
s::Unit units(const Json& v){return static_cast<s::Unit>(v.get<double>()*s::dip);}
s::Rect rect(const Json& v){return {units(v[0]),units(v[1]),units(v[2]),units(v[3])};}
s::Topology topology(const Json& v){
    s::Topology result;result.fallback=v["fallback"];result.roles=v["roles"].get<std::map<std::string,std::vector<std::string>>>();
    for(const auto& d:v["displays"]){s::Display value;value.id=d["id"];value.bounds=rect(d["bounds"]);value.work=rect(d["work"]);
        const auto& in=d["safe"];value.safe={units(in[0]),units(in[1]),units(in[2]),units(in[3])};
        for(const auto& e:d["exclusions"])value.exclusions.push_back(rect(e));
        value.pixel_x=d["pixel_origin"][0];value.pixel_y=d["pixel_origin"][1];value.scale_numerator=d["scale"][0];value.scale_denominator=d["scale"][1];result.displays.push_back(std::move(value));}
    return result;
}
std::map<std::string,s::Metrics> metrics(const Json& v){
    std::map<std::string,s::Metrics> result;for(auto it=v.begin();it!=v.end();++it){const auto& m=it.value();result.emplace(it.key(),s::Metrics{{units(m["minimum"][0]),units(m["minimum"][1])},{units(m["preferred"][0]),units(m["preferred"][1])}});}return result;
}
Json box(const s::Rect& r){return Json::array({r.x,r.y,r.width,r.height});}
Json encoded(const s::Plan& p){
    Json result={{"scene_id",p.scene_id},{"revision",p.revision},{"state",p.state==s::State::ready?"ready":(p.state==s::State::degraded?"degraded":"alternative")},{"nodes",Json::array()},{"diagnostics",Json::array()}};
    for(const auto& n:p.nodes)result["nodes"].push_back({{"id",n.id},{"parent",n.parent},{"display",n.display},{"kind",n.kind},{"variant",n.variant},
        {"box",box(n.box)},{"visible",box(n.visible)},{"content",box(n.content)},{"pixels",box(n.pixels)},{"overflow",n.overflow},{"clipped",n.clipped}});
    for(const auto& d:p.diagnostics)result["diagnostics"].push_back({{"widget",d.widget},{"code",d.code},{"related",d.related}});
    return result;
}
Json read(const std::string& path){std::ifstream f(path);check(f.good(),"fixture absent");Json result;f>>result;return result;}
void rejection(const std::function<void()>& f,const char* code){bool failed=false;try{f();}catch(const syspane::protocol::Error& e){failed=true;check(std::string(e.what())==code,e.what());}check(failed,"expected rejection");}
void golden(const Json& input){
    const auto scene=input["scene"],original=scene;auto environment=topology(input["topology"]);const auto sizes=metrics(input["metrics"]);
    if(input.contains("error")){const auto code=input["error"].get<std::string>();rejection([&]{s::resolve(scene,environment,sizes);},code.c_str());return;}
    const auto result=encoded(s::resolve(scene,environment,sizes));
    if(result!=input["expected"]){std::cerr<<"Expected: "<<input["expected"].dump()<<"\nObserved: "<<result.dump()<<'\n';check(false,"geometry mismatch");}
    check(scene==original,"authored input mutated");
    auto shuffled=scene;std::reverse(shuffled["widgets"].begin(),shuffled["widgets"].end());std::reverse(environment.displays.begin(),environment.displays.end());
    for(auto& display:environment.displays)std::reverse(display.exclusions.begin(),display.exclusions.end());
    for(auto& role:environment.roles)std::reverse(role.second.begin(),role.second.end());
    check(encoded(s::resolve(shuffled,environment,sizes))==result,"input enumeration changed projection");
}
void limits(const Json& input){
    auto scene=input["scene"];auto env=topology(input["topology"]);auto m=metrics(input["metrics"]);const auto original=env;
    env.displays[0].bounds.width=std::numeric_limits<s::Unit>::max();rejection([&]{s::resolve(scene,env,m);},"layout.topology");env=original;
    env.displays[0].scale_denominator=0;rejection([&]{s::resolve(scene,env,m);},"layout.topology");env=original;
    env.displays.push_back(env.displays[0]);rejection([&]{s::resolve(scene,env,m);},"layout.topology");env=original;
    env.displays[0].exclusions.resize(17,{0,0,64,64});rejection([&]{s::resolve(scene,env,m);},"layout.topology");env=original;
    env.roles["primary"]={"main","main"};rejection([&]{s::resolve(scene,env,m);},"layout.topology");env=original;
    auto missing=m;m.begin()->second.preferred.width=std::numeric_limits<s::Unit>::max();rejection([&]{s::resolve(scene,env,m);},"layout.metrics");m=missing;
    scene["widgets"].push_back(scene["widgets"][0]);rejection([&]{s::resolve(scene,env,m);},"scene.duplicate");scene=input["scene"];
    scene["widgets"]=Json::array();scene["roots"]=Json::array();m.clear();
    check(s::resolve(scene,env,m).nodes.empty(),"empty scene");
    const auto prototype=input["scene"]["widgets"][0];
    for(unsigned i=0;i<256;++i){auto widget=prototype;const auto id="widget:"+std::to_string(i);widget["id"]=id;scene["widgets"].push_back(widget);scene["roots"].push_back(id);m.emplace(id,s::Metrics{{32*64,16*64},{32*64,16*64}});}
    auto result=s::resolve(scene,env,m);check(result.nodes.size()==256&&result.diagnostics.size()==32640,"maximum scene bounded overlap");
    scene["widgets"].push_back(prototype);rejection([&]{s::resolve(scene,env,m);},"authored.schema");
}
void exclusions(const Json& input){
    auto scene=input["scene"];auto& widget=scene["widgets"][0];widget["kind"]="group";widget["children"]=Json::array();
    widget["layout"]["base"]={{"kind","stack"},{"axis","vertical"},{"gap_dip",0},{"overflow","diagnose"}};
    auto env=topology(input["topology"]);env.displays[0].bounds=env.displays[0].work={0,0,6*64,6*64};
    const std::vector<std::pair<int,int>> cells{{0,0},{2,0},{4,1},{1,2},{3,3},{5,4},{0,5},{4,5}};
    for(unsigned mask=0;mask<256;++mask){bool occupied[6][6]{};env.displays[0].exclusions.clear();
        for(unsigned bit=0;bit<8;++bit)if(mask&(1u<<bit)){const auto cell=cells[bit];occupied[cell.second][cell.first]=true;env.displays[0].exclusions.push_back({cell.first*64,cell.second*64,64,64});}
        int bx=0,by=0,bw=0,bh=0;
        // Independent exhaustive cell occupancy oracle, not the engine's edge sweep.
        for(int y=0;y<6;++y)for(int x=0;x<6;++x)for(int h=1;y+h<=6;++h)for(int w=1;x+w<=6;++w){
            bool clear=true;for(int yy=y;yy<y+h;++yy)for(int xx=x;xx<x+w;++xx)if(occupied[yy][xx])clear=false;
            if(clear&&(w*h>bw*bh||(w*h==bw*bh&&std::make_tuple(y,x,-w,-h)<std::make_tuple(by,bx,-bw,-bh)))){bx=x;by=y;bw=w;bh=h;}
        }
        const auto result=s::resolve(scene,env,{});check(result.nodes.size()==1&&result.state==s::State::ready,"exclusion projection");
        check(box(result.nodes[0].box)==Json::array({bx*64,by*64,bw*64,bh*64}),"largest empty rectangle mismatch");
        std::reverse(env.displays[0].exclusions.begin(),env.displays[0].exclusions.end());check(encoded(s::resolve(scene,env,{}))==encoded(result),"exclusion order");
    }
}
int binding_test(const std::string& name);
int chart_plot_test(const std::string& name,const std::string& root);
int image_fit_test(const std::string& name,const std::string& root);
int chart_history_test(const std::string& name);
int main(int argc,char** argv){try{
    check(argc==3,"arguments");const std::string name=argv[1],root=argv[2];
    if(name.rfind("BIND-",0)==0)return binding_test(name);
    if(name.rfind("PLOT-",0)==0)return chart_plot_test(name,root);
    if(name.rfind("IMAGE-",0)==0)return image_fit_test(name,root);
    if(name.rfind("CHART-",0)==0)return chart_history_test(name);
    if(name=="LIMITS")limits(read(root+"/ROOT-FLOW.json"));else if(name=="EXCLUSION-EXHAUSTIVE")exclusions(read(root+"/ROOT-FLOW.json"));else golden(read(root+"/"+name+".json"));
    std::cout<<name<<" pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
