#include "native_visibility_fixture.hpp"
#include "scene_inspector_model.hpp"
#include <algorithm>
#include <iostream>
#include <thread>
#include <chrono>
using namespace fixture;
namespace {
namespace ui=syspane::interfaces;
bool clear_pixels(const v::SurfaceFrame& f){for(const auto& d:f.displays)for(auto c:d.rgba)if(c)return false;return true;}
Json boxes(const v::SurfaceFrame& f){Json out=Json::array();for(const auto& n:f.layout.nodes)out.push_back(Json::array({n.id,n.pixels.x,n.pixels.y,n.pixels.width,n.pixels.height}));return out;}
struct Visible {
    v::SurfaceConfig cfg;std::unique_ptr<v::SceneSurface> surface;std::uint64_t token=0,now=0,revision=7,measured=100;unsigned clears=0;
    explicit Visible(v::SurfaceConfig config):cfg(std::move(config)){
        surface=std::make_unique<v::SceneSurface>(c::Authority{true,"desktop",{"desktop"}},chart_policy(),cfg,std::vector<v::SurfaceProvider>{provider()},[&]{++clears;return true;},image_worker_path());
        attach();full(document(cfg.authored.scene["widgets"][0]["kind"]=="chart"?10:123));
    }
    void attach(){token=surface->attach("P1",link(revision),++now).token;need(token!=0,"visibility attach");}
    void full(Json d){need(surface->receive("P1",token,revision,wire(std::move(d),link(revision)),++now,tick(measured)).code==r::DataCode::accepted,"visibility receive");}
    v::SurfaceFrame paint(){v::SurfaceFrame out;surface->paint(++now,{{"P1",tick(measured)}},[&](auto code,const auto* f){need(f&&(code==v::SurfaceCode::ready||code==v::SurfaceCode::degraded),"visibility presentation");out=*f;});return out;}
    void empty(v::SurfaceCode expected,const char* reason){surface->paint(++now,{{"P1",tick(measured)}},[&](auto code,const auto* f){need(!f&&code==expected,"visibility empty result");});need(surface->status().reason==reason,"visibility reason");}
    void replace(){surface->replace(cfg,++now);}
};
void hidden(const v::SurfaceFrame& frame){need(clear_pixels(frame)&&ui::inspector_rows(frame).empty(),"hidden native pixels and inspector rows");for(const auto& w:frame.widgets)need(!w.presented&&!w.diagnostic&&w.title.empty()&&w.text.empty()&&w.accessible.empty()&&w.fonts.empty()&&!w.table&&!w.chart&&!w.image&&w.notices.empty(),"hidden derived payload erased");}
void examples(const std::string& root,const Json& fixed){for(const auto& test:fixed["cases"]){
    std::cerr<<"visibility example "<<test["id"]<<'\n';
    auto cfg=config(root);visibility_config(cfg);auto q=visibility_rule(test["rule_value"]);if(test.contains("unit"))q["unit"]=test["unit"];if(test.contains("field"))q["binding"]["field"]=test["field"];if(test.contains("entity"))q["binding"]["entity_id"]=test["entity"];
    cfg.authored.scene["widgets"][0]["visibility"]=q;Visible f(cfg);
    const auto initial=f.paint();const auto& first=initial.layout.nodes[0];need(Json::array({first.pixels.x,first.pixels.y,first.pixels.width,first.pixels.height})==fixed["bounds"],"fixed initial bounds");
    if(test.value("failed",false)){auto d=document(123,2);for(auto& o:d["observations"])if(o["field"]=="network.receive_bytes"){o["acquisition"]="failed";o["freshness"]="stale";o["error"]={{"code","provider.failed"},{"message","PRIVATE ERROR"},{"retryable",true}};}f.full(d);}
    if(test.value("disconnect",false))f.surface->disconnect("P1",f.token,7,++f.now);
    // Compare identical underlying content. Source failure can independently
    // enlarge the existing readable minimum; a condition must not change it.
    f.cfg.authored.scene["widgets"][0].erase("visibility");f.replace();const auto unconditioned=f.paint();
    f.cfg.authored.scene["widgets"][0]["visibility"]=q;f.replace();
    const auto frame=f.paint();need(frame.widgets.size()==1,"one conditional widget");const auto& w=frame.widgets[0];
    need(w.text==test["text"]&&w.presented==test["presented"]&&w.diagnostic==test["diagnostic"],test["id"].get_ref<const std::string&>().c_str());
    if(test.contains("accessible"))need(w.accessible==test["accessible"],"exact conditional accessible text");
    need(boxes(frame)==boxes(unconditioned),"condition preserves identical-content layout");
    if(!w.presented)hidden(frame);else{const auto rows=ui::inspector_rows(frame);need(rows.size()==1&&rows[0].information==w.accessible,"inspector diagnostic semantic text");}
    if(w.diagnostic)need(!w.table&&!w.chart&&!w.image&&f.surface->status().code==v::SurfaceCode::degraded&&f.surface->status().reason=="visibility.diagnostic","status-only diagnostic publication");
}}
void groups(const std::string& root,const Json& fixed){
    auto cfg=visibility_group_config(root);Visible f(cfg);const auto baseline=f.paint();const auto bounds=boxes(baseline);need(bounds[1]==Json::array({"a",0,0,320,180})&&bounds[2]==Json::array({"b",330,0,320,180}),"fixed independent child rectangles");
    for(auto& w:f.cfg.authored.scene["widgets"])if(w["id"]=="g")w["visibility"]=visibility_rule(0);
    f.replace();auto frame=f.paint();hidden(frame);need(boxes(frame)==bounds,"false group keeps children geometry");
    for(auto& w:f.cfg.authored.scene["widgets"])if(w["id"]=="b"){w["visibility"]=visibility_rule();w["visibility"]["unit"]="1";}
    f.replace();frame=f.paint();
    need(!frame.widgets[0].presented&&!frame.widgets[1].presented&&frame.widgets[2].diagnostic&&frame.widgets[2].text==fixed["group"]["child_diagnostic"],"false ancestor preserves child diagnostic");
    auto rows=ui::inspector_rows(frame);need(rows.size()==1&&rows[0].key==Json::array({"scene:surface","b"}).dump()&&rows[0].item=="Second","promote diagnostic out of hidden group");need(boxes(frame)==bounds,"diagnostic retains layout");
    for(auto& w:f.cfg.authored.scene["widgets"]){w.erase("visibility");if(w["id"]=="g"){w["visibility"]=visibility_rule();w["visibility"]["binding"]["entity_id"]="missing";}}
    f.replace();frame=f.paint();
    for(const auto& w:frame.widgets)need(w.diagnostic&&w.text==fixed["group"]["parent_diagnostic"],"group diagnostic relay");
    need(boxes(frame)==bounds,"group relay retains layout");
    // Empty groups have their own retained rectangle instead of an invented child.
    auto group=f.cfg.authored.scene["widgets"][1];group["children"]=Json::array();f.cfg.authored.scene["widgets"]=Json::array({group});
    f.replace();frame=f.paint();need(frame.widgets.size()==1&&frame.widgets[0].diagnostic&&!clear_pixels(frame),"empty group diagnostic raster");
}
void policy_cases(const std::string& root){
    auto cfg=visibility_text_config(root);Visible f(cfg);need(!clear_pixels(f.paint()),"initial native content");const auto before=f.clears;
    f.surface->policy(chart_policy(8,false),++f.now);need(f.clears>before&&f.surface->status().widgets==0,"erase before policy publication");f.empty(v::SurfaceCode::restricted,"policy.denied");
    f.surface->policy(chart_policy(9),++f.now);f.revision=9;auto frame=f.paint();need(frame.widgets[0].text=="Visibility (value): Waiting"&&frame.widgets[0].accessible.find("Secret body")==std::string::npos,"regrant cannot restore condition");
    f.attach();f.full(document(123));need(f.paint().widgets[0].text=="Secret body","fresh grant state reveals content");
    auto denied=document(123,2);for(auto& o:denied["observations"])if(o["field"]=="network.receive_bytes"){o["acquisition"]="denied";o["freshness"]="stale";o["error"]={{"code","provider.denied"},{"message","PRIVATE"},{"retryable",false}};}f.full(denied);f.empty(v::SurfaceCode::restricted,"policy.denied");
}
void geometry(const std::string& root){
    // Use the existing schema's smallest valid fixed rectangle (32 by 16 DIP).
    auto cfg=visibility_text_config(root);cfg.authored.scene["widgets"][0]["visibility"]["unit"]="1";cfg.authored.scene["widgets"][0]["content"]["body"]="";cfg.authored.scene["widgets"][0]["layout"]["base"]["width"]=32;cfg.authored.scene["widgets"][0]["layout"]["base"]["height"]=16;
    Visible f(cfg);f.empty(v::SurfaceCode::alternative,"surface.visibility_layout");
    auto tokens=f.cfg.resources->theme()["tokens"];tokens["background"]="#000000ff";f.cfg=visibility_group_config(root,{{"tokens",tokens}});for(auto& w:f.cfg.authored.scene["widgets"])if(w["id"]!="g"){w["layout"]["base"]["x"]=0;w["visibility"]=visibility_rule();w["visibility"]["unit"]="1";}
    f.replace();f.empty(v::SurfaceCode::alternative,"surface.visibility_layout");
    // A later ordinary leaf must not overpaint an earlier diagnostic.
    for(auto& w:f.cfg.authored.scene["widgets"])if(w["id"]=="b")w.erase("visibility");
    f.replace();const auto overlap=f.paint();const auto expected=overlap.displays[0].rgba;
    for(auto& w:f.cfg.authored.scene["widgets"])if(w["id"]=="b")w["visibility"]=visibility_rule(0);
    f.replace();const auto only_warning=f.paint();const auto& node=only_warning.layout.nodes[1];
    // Compare actual warning footprint against the same warning on transparent pixels.
    const auto& raster=only_warning.displays[0];for(s::Unit y=node.pixels.y;y<node.pixels.y+node.pixels.height;++y)for(s::Unit x=node.pixels.x;x<node.pixels.x+node.pixels.width;++x){const auto n=(static_cast<std::size_t>(y)*raster.width+x)*4;if(raster.rgba[n+3]==255)need(std::equal(raster.rgba.begin()+n,raster.rgba.begin()+n+4,expected.begin()+n),"diagnostic painted after ordinary content");}
}
void kinds(const std::string& root){
    for(const std::string kind:{"text","value","status","table","chart"}){std::cerr<<"visibility kind "<<kind<<'\n';auto cfg=kind=="table"?table_config(root):kind=="chart"?chart_config(root):config(root);visibility_config(cfg);auto& w=cfg.authored.scene["widgets"][0];
        if(kind=="text"){w["kind"]=kind;w["bindings"]=Json::array();w["content"]={{"body","Secret body"}};}else if(kind=="status")w["kind"]=kind;
        w["visibility"]=visibility_rule(1);w["visibility"]["binding"]["field"]="network.transmit_bytes";Visible f(cfg);
        if(kind=="chart")f.full(document(10,2));
        hidden(f.paint());
    }
    auto cfg=image_config(root);cfg.authored.scene["widgets"][0]["layout"]["base"]["width"]=320;cfg.authored.scene["widgets"][0]["layout"]["base"]["height"]=180;visibility_config(cfg);cfg.authored.scene["widgets"][0]["visibility"]=visibility_rule(0);Visible image(cfg);
    auto frame=image.paint();for(unsigned n=0;n<200&&frame.widgets[0].presented;++n){need(frame.widgets[0].text=="Image loading","hidden image keeps safe worker status");std::this_thread::sleep_for(std::chrono::milliseconds(5));image.surface->poll_image_jobs();frame=image.paint();}hidden(frame);
    image.full(document(0,2));frame=image.paint();need(frame.widgets[0].image&&frame.widgets[0].image->state=="ready"&&!clear_pixels(frame),"hidden image work survives and reveals");
    auto bad=frame;bad.widgets[0].presented=false;bool rejected=false;try{ui::inspector_rows(bad);}catch(const p::Error& e){rejected=std::string(e.what())=="inspector.hidden_payload";}need(rejected,"inspector rejects retained hidden image payload");
    cfg=chart_config(root);visibility_config(cfg);cfg.authored.scene["widgets"][0]["visibility"]=visibility_rule(1);cfg.authored.scene["widgets"][0]["visibility"]["binding"]["field"]="network.transmit_bytes";Visible chart(cfg);
    chart.full(chart_document(10,2,100));chart.measured=200;chart.full(chart_document(20,3,200));auto reveal=chart_document(30,4,300);for(auto& o:reveal["observations"])if(o["field"]=="network.transmit_bytes")o["value"]["data"]="1";chart.measured=300;chart.full(reveal);frame=chart.paint();need(frame.widgets[0].chart&&frame.widgets[0].chart->points.size()>=3,"authorized hidden chart history continues");
}
}
int native_visibility_tests(const std::string& root){const auto fixed=read(root+"/../../../tests/scene","native-visibility-cases.json");examples(root,fixed);std::cerr<<"visibility groups\n";groups(root,fixed);std::cerr<<"visibility policy\n";policy_cases(root);std::cerr<<"visibility geometry\n";geometry(root);std::cerr<<"visibility kinds\n";kinds(root);std::cout<<"NATIVE VISIBILITY EXAMPLES GROUPS POLICY GEOMETRY KINDS pass\n";return 0;}
