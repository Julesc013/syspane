#include "native_visibility_fixture.hpp"
#include "scene_inspector_model.hpp"
#include "scene_text.hpp"
#include <iostream>
using namespace fixture;
namespace {
Json blocks(const std::vector<v::TextBlock>& parts){Json out=Json::array();for(const auto& b:parts)out.push_back({{"role",b.role},{"text",b.text}});return out;}
struct Run {
    v::SurfaceConfig cfg;std::unique_ptr<v::SceneSurface> surface;std::uint64_t now=0,token=0,revision=7,measured=100;unsigned clears=0;
    explicit Run(v::SurfaceConfig c):cfg(std::move(c)){
        surface=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},chart_policy(),cfg,std::vector<v::SurfaceProvider>{provider()},[&]{++clears;return true;},image_worker_path());}
    void full(Json d=document()){if(!token)token=surface->attach("P1",link(revision),++now).token;
        need(token!=0&&surface->receive("P1",token,revision,wire(d,link(revision)),++now,tick(100)).code==r::DataCode::accepted,"role probe delivery");}
    v::SurfaceFrame paint(){v::SurfaceFrame out;surface->paint(++now,{{"P1",tick(measured)}},[&](auto code,const auto* f){need(f&&(code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded),"role probe presentation");out=*f;});return out;}
    void replace(){surface->replace(cfg,++now);}
    void absent(const std::string& reason){surface->paint(++now,{{"P1",tick(measured)}},[&](auto,const auto* f){need(!f,"no partial frame");});need(surface->status().reason==reason,"exact refusal reason");need(!surface->status().widgets&&!surface->status().pixels,"no published buffers");}
};
v::SurfaceConfig setup(const std::string& root,const Json& fixed,const std::string& name){
    auto cfg=name=="table"?table_config(root,fixed["theme"]):name=="chart"||name=="chartgap"?chart_config(root,fixed["theme"]):config(root,fixed["theme"]);
    cfg.experimental_typography=true;cfg.capabilities.insert("theme.typography");
    if(name=="body"){content_config(cfg);auto& w=cfg.authored.scene["widgets"][0];w["kind"]="text";w["bindings"]=Json::array();w["content"]={{"body","Current\n<value> text"}};}
    if(name=="status")cfg.authored.scene["widgets"][0]["kind"]="status";
    if(name=="newline")cfg.authored.scene["widgets"][0]["title"]="Receive\nCurrent";
    if(name=="hidden"||name=="hiddenstale"||name=="empty"){
        visibility_config(cfg);auto& w=cfg.authored.scene["widgets"][0];w["visibility"]=visibility_rule(name=="empty"?0:123);
        if(name=="hidden")w["visibility"]["unit"]="1";}
    return cfg;
}
void contracts(const std::string& root,const Json& fixed){
    Run f(setup(root,fixed,"value"));f.full();need(!f.paint().widgets[0].blocks.empty(),"role blocks published");
    f.cfg.experimental_typography=false;f.replace();f.absent("surface.typography_unavailable");
    f.cfg.authored.settings["display"]["enabled"]=false;f.replace();f.absent("surface.typography_unavailable");
    f.cfg.experimental_typography=true;f.replace();f.absent("");
    f.cfg.capabilities.erase("theme.typography");f.replace();f.surface->paint(++f.now,{},[&](auto,const auto* frame){need(!frame,"disabled missing capability");});need(!f.surface->status().reason.empty(),"capability rejection explicit");
    f.cfg.capabilities.insert("theme.typography");f.cfg.authored.settings["display"]["enabled"]=true;f.replace();f.paint();
    const auto cleared=f.clears;auto denied=chart_policy(8);denied.denied_capabilities.insert("theme.typography");f.surface->policy(denied,++f.now);f.surface->paint(++f.now,{},[&](auto,const auto* frame){need(!frame,"policy erasure");});need(f.clears>cleared&&!f.surface->status().pixels,"native buffers erased");
    f.surface->policy(chart_policy(9),++f.now);f.revision=9;f.token=0;need(f.paint().widgets[0].text=="Receive\nWaiting","regrant waits");f.full();f.paint();
    f.cfg=config(root);f.replace();need(f.paint().widgets[0].blocks.empty(),"legacy replacement no role buffers");
    auto hidden=setup(root,fixed,"empty");Run h(hidden);h.full();auto frame=h.paint();need(frame.widgets[0].blocks.empty(),"hidden blocks erased");
    frame.widgets[0].blocks.push_back({"body","PRIVATE"});bool reject=false;try{syspane::interfaces::inspector_rows(frame);}catch(const p::Error&){reject=true;}need(reject,"inspector rejects retained hidden blocks");
    v::TextRequest q;q.theme=fixed["theme"];const auto fails=[&](std::vector<v::TextBlock> b,std::size_t pixels){bool rejected=false;try{v::render_blocks(q,b,pixels);}catch(const p::Error&){rejected=true;}need(rejected,"role budget must reject");};
    fails({},100000);fails(std::vector<v::TextBlock>(17,{"body","a"}),100000);fails({{"body",std::string(4096,'a')},{"label","b"}},100000);fails({{"body","Text"},{"value","Value"}},1);
    q.denominator=0;fails({{"body","Text"},{"value","Value"}},100000);q.denominator=1;
    auto tiny=setup(root,fixed,"hidden");tiny.authored.scene["widgets"][0]["kind"]="text";tiny.authored.scene["widgets"][0]["bindings"]=Json::array();tiny.authored.scene["widgets"][0]["content"]={{"body",""}};tiny.authored.scene["widgets"][0]["layout"]["base"]["width"]=32;tiny.authored.scene["widgets"][0]["layout"]["base"]["height"]=16;
    Run t(tiny);t.full();t.absent("surface.visibility_layout");
    auto group=visibility_group_config(root,fixed["theme"]);group.experimental_typography=true;group.capabilities.insert("theme.typography");
    for(auto& w:group.authored.scene["widgets"]){if(w["id"]=="g")w["visibility"]=visibility_rule(0);if(w["id"]=="b"){w["visibility"]=visibility_rule();w["visibility"]["unit"]="1";}}
    Run g(group);g.full();frame=g.paint();need(frame.widgets[0].blocks.empty()&&frame.widgets[1].blocks.empty()&&frame.widgets[2].blocks.size()==1&&frame.widgets[2].blocks[0].role=="diagnostic"&&frame.widgets[2].blocks[0].text=="Visibility (b): Unit mismatch","hidden group preserves child role");
    f.surface->close();need(!f.surface->status().widgets&&!f.surface->status().pixels,"close erases");
}
}
int main(int argc,char** argv){try{
    if(argc!=8)return 2;
    std::ifstream file(argv[2]);Json fixed;file>>fixed;const std::string name=argv[3];
    if(name=="contracts"){contracts(argv[1],fixed);std::cout<<Json({{"admission",true},{"erasure",true},{"limits",true},{"replacement",true},{"group",true}}).dump();return 0;}
    auto cfg=setup(argv[1],fixed,name);cfg.topology.displays[0].scale_numerator=static_cast<unsigned>(std::stoul(argv[5]));cfg.topology.displays[0].scale_denominator=static_cast<unsigned>(std::stoul(argv[6]));cfg.contrast=argv[7];
    Run run(cfg);
    if(name!="pending"){
        auto d=name=="table"?table_document():name=="chart"||name=="chartgap"?document(23):document();
        if(name=="failed")for(auto& o:d["observations"])if(o["field"]=="network.receive_bytes"){o["acquisition"]="failed";o["freshness"]="stale";o["error"]={{"code","provider.failed"},{"message","PRIVATE ERROR"},{"retryable",true}};}
        run.full(d);}
    if(name=="retained"||name=="hiddenstale"||name=="chartgap"){run.surface->disconnect("P1",run.token,7,++run.now);run.measured=3000000100ULL;}
    const auto frame=run.paint();const auto& out=frame.widgets[0];const auto& display=frame.displays[0];
    Json reply={{"width",display.width},{"height",display.height},{"blocks",blocks(out.blocks)},{"presented",out.presented},{"text",out.text},{"accessible",out.accessible}};
    if(out.chart)reply["plot_y"]=out.chart->pixels.y;
    if(out.table){reply["cells"]=Json::array();reply["rectangles"]=Json::array();for(const auto& row:out.table->rows){Json cells=Json::array(),rect=Json::array();for(const auto& c:row.cells){cells.push_back(blocks(c.blocks));rect.push_back({c.pixels.x,c.pixels.y,c.pixels.width,c.pixels.height});}reply["cells"].push_back(cells);reply["rectangles"].push_back(rect);}}
    std::ofstream pixels(argv[4],std::ios::binary);pixels.write(reinterpret_cast<const char*>(display.rgba.data()),static_cast<std::streamsize>(display.rgba.size()));need(pixels.good(),"raw frame output");std::cout<<reply.dump();return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
