#include "visibility.hpp"
#include "network_publication.hpp"
#include <algorithm>
#include <fstream>
#include <limits>
#include <stdexcept>

namespace {
namespace s=syspane::scene;namespace m=syspane::model;namespace r=syspane::recovery;
namespace p=syspane::protocol;namespace c=syspane::configuration;namespace n=syspane::runtime;
using p::Json;using Code=s::VisibilityCode;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
c::Policy policy(unsigned revision=7,bool allow=true){c::Policy v;v.available=allow;v.revision=revision;v.disclosure[{"desktop","desktop"}]={"operational"};v.disclosure[{"desktop","accessibility"}]={"operational"};return v;}
m::Tick tick(std::string epoch="E1",std::uint64_t now=100){return {std::move(epoch),now,"clock:1","scope:1"};}
m::ValueKind kind(const std::string& name){return name=="uint64"?m::ValueKind::uint64:name=="number"?m::ValueKind::number:name=="boolean"?m::ValueKind::boolean:m::ValueKind::string;}
Json direct(std::string epoch="E1"){return {{"kind","direct"},{"producer_id","P1"},{"producer_epoch",epoch},{"entity_id","a"},{"field","test.value"}};}
Json rule(){return {{"schema_version","0.1.0"},{"binding",direct()},{"op","eq"},{"value",3},{"unit","byte"}};}
Json selector(){return {{"kind","selector"},{"scope",{{"kind","local_host"}}},{"entity_type","fixture.entity"},{"mode","singleton"},{"predicates",Json::array()},{"sort",Json::array()},{"limit",1},{"field","test.value"}};}
struct Fixture {
    r::DataView view; p::TelemetryBinding link;std::uint64_t token=0;Json doc;
    Fixture(std::string type="uint64",Json value="3",std::string unit="byte",std::string producer="P1"):
      view({true,"desktop",{"desktop"}},policy(),"desktop","operational",{{"test.value",unit,kind(type)}}){
        link={{1,p::frame_limit,{{"telemetry","0.2.0"},{"snapshot","0.2.0"},{"observation","0.2.0"}},
            {"telemetry.snapshot","telemetry.measured-time"}},"D","E1",producer,"S","desktop","operational",7,
            p::TelemetryDirection::producer_to_consumer,"0.2.0","clock:1","scope:1"};
        token=view.attach_wire(link,0).token;need(token!=0,"fixture attachment");
        n::NetworkState state("E1","clock:1","scope:1");state.demand(1);
        need(state.commit(1,0,{syspane::platform::NetworkCode::success,0,{{9,9,6,syspane::platform::NetworkCounters{3,0}}}},tick(),tick())==n::NetworkStateCode::accepted,"fixture sample");
        doc=n::network_document(*state.sample(),1,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
        doc["entities"]=Json::array();doc["entities"].push_back({{"id","a"},{"kind","fixture.entity"},{"display_name","Alpha"},{"generation","1"},{"identity",Json::object()}});
        auto o=doc["observations"][0];o["entity_id"]="a";o["field"]="test.value";o["unit"]=unit;o["value"]={{"kind",type},{"data",value}};
        doc["observations"]=Json::array();doc["observations"].push_back(o);
    }
    void receive(unsigned now=1){Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id",link.producer},{"record_id","R"+doc["generation"].get<std::string>()},
        {"policy_revision",std::to_string(link.policy_revision)},{"clock_id","clock:1"},{"snapshot",doc}};
        const auto bytes=p::encode_telemetry({"snapshot","D",link.epoch,body.dump(),body},link);
        need(view.receive(token,link.policy_revision,bytes,now,tick(link.epoch)).code==r::DataCode::accepted,"visibility wire admission");}
    s::BindingInput input(){s::BindingInput v;v.view=&view;v.producer=link.producer;v.entity_types={"fixture.entity"};v.now=tick(link.epoch);v.fields["test.value"]=1000;return v;}
};
std::string code(Code v){
    switch(v){
    case Code::shown:return "shown";case Code::hidden:return "hidden";case Code::pending:return "pending";case Code::empty:return "empty";
    case Code::denied:return "denied";case Code::unsupported:return "unsupported";case Code::ambiguous:return "ambiguous";case Code::invalid:return "invalid";
    case Code::capacity:return "capacity";case Code::lease_lost:return "lease_lost";case Code::unavailable:return "unavailable";case Code::stale:return "stale";
    case Code::unit_mismatch:return "unit_mismatch";case Code::type_mismatch:return "type_mismatch";
    }throw std::runtime_error("unknown visibility outcome");
}
void check(const Json& q,const std::vector<s::BindingInput>& inputs,const std::string& expected,const std::string& id,unsigned now=2,s::BindingLimits limits={}){
    const auto original=q;unsigned calls=0;
    s::project_visibility(q,inputs,now,[&](const s::VisibilityResult& v){++calls;need(code(v.code)==expected,id+": expected "+expected+", got "+code(v.code));},limits);
    need(calls==1&&q==original,id+": callback/input lifetime");
}
void comparisons(const Json& cases){for(const auto& test:cases){
    Fixture f(test["kind"],test["observed"],test["unit"]);f.receive();auto q=rule();q["op"]=test["op"];q["value"]=test["literal"];q["unit"]=test["literal_unit"];
    check(q,{f.input()},test["expected"],test["id"]);
}}
void states(const Json& cases){for(const auto& test:cases){
    Fixture f;auto q=rule();auto& o=f.doc["observations"][0];const std::string id=test["id"];
    if(id=="denied"||id=="failed-retained"||id=="pending-retained"){
        o["acquisition"]=id=="denied"?"denied":id=="failed-retained"?"failed":"pending";o["freshness"]="stale";
        if(id!="pending-retained")o["error"]={{"code","fixture.failed"},{"message","private explanation"},{"retryable",true}};
    }
    if(id=="unsupported"||id=="disabled"||id=="support-unknown"||id=="no-value"){
        o["value"]=nullptr;o["observed_at"]=nullptr;o["measured_at"]=nullptr;o["acquisition"]=id=="disabled"?"disabled":"pending";
        o["freshness"]=id=="unsupported"?"not_applicable":"unknown";o["support"]=id=="unsupported"?"unsupported":id=="support-unknown"?"unknown":"supported";
    }
    if(id=="absent"){o["presence"]="absent";o["freshness"]="stale";}
    if(id=="missing-field")f.doc["observations"]=Json::array();
    if(id=="ambiguous"){auto e=f.doc["entities"][0],v=o;e["id"]="b";v["entity_id"]="b";f.doc["entities"].push_back(e);f.doc["observations"].push_back(v);q["binding"]=selector();}
    if(id!="no-snapshot")f.receive();
    auto in=f.input();unsigned now=2;
    if(id=="stale")in.now=tick("E1",1100);
    if(id=="clock-missing"||id=="clock-missing-retained")in.now.reset();
    if(id=="expired")now=3001;
    if(id=="disconnected"||id=="clock-missing-retained"){f.view.disconnect(f.token,7,2);now=3;}
    if(id=="missing-entity")q["binding"]["entity_id"]="missing";
    if(id=="unsupported-field")q["binding"]["field"]="unknown.value";
    if(id=="revoked"||id=="regranted"){f.view.policy(policy(8,false),2);now=3;}
    if(id=="regranted"){f.view.policy(policy(9),3);now=4;}
    check(q,{in},test["expected"],id,now);
}}
void lifecycle(){
    Fixture f;f.receive();auto q=rule();check(q,{f.input()},"shown","initial");
    f.view.disconnect(f.token,7,2);f.link.epoch="E2";f.token=f.view.attach_wire(f.link,3).token;need(f.token!=0,"restart attach");
    check(q,{f.input()},"lease_lost","restart retained",4);
    f.doc["producer_epoch"]="E2";for(auto& o:f.doc["observations"])o["producer_epoch"]="E2";f.receive(5);
    check(q,{f.input()},"empty","old epoch pin",6);q["binding"]=direct("E2");check(q,{f.input()},"shown","new epoch pin",6);
    f.view.policy(policy(8,false),7);check(q,{f.input()},"denied","revoked",8);
    f.view.policy(policy(9),9);check(q,{f.input()},"pending","fresh grant cannot restore",10);
    f.link.policy_revision=9;f.token=f.view.attach_wire(f.link,11).token;need(f.token!=0,"regrant attach");
    check(q,{f.input()},"pending","attachment without full",12);f.receive(13);check(q,{f.input()},"shown","new full",14);
    q["binding"]["field"]="entity.display_name";q["value"]="Alpha";q["unit"]="1";check(q,{f.input()},"shown","metadata",14);
    f.view.disconnect(f.token,9,15);check(q,{f.input()},"lease_lost","metadata after disconnect",16);
}
void limits(){
    Fixture f;f.receive();auto q=rule();
    for(unsigned i=0;i<3;++i){s::BindingLimits limit;if(i==0)limit.work_steps=0;if(i==1)limit.output_bytes=0;if(i==2)limit.index_bytes=0;check(q,{f.input()},"capacity","budget",2,limit);}
    unsigned calls=0;bool reentry=false;
    s::project_visibility(q,{f.input()},2,[&](const auto& v){++calls;need(v.code==Code::shown,"inside borrow");try{f.view.status(2);}catch(const std::logic_error&){reentry=true;}});
    need(calls==1&&reentry,"view must remain borrowed during decision");
    calls=0;bool raised=false;try{s::project_visibility(q,{f.input()},2,[&](const auto&){++calls;throw std::bad_alloc();});}catch(const std::bad_alloc&){raised=true;}
    need(raised&&calls==1,"throw once");check(q,{f.input()},"shown","owner released after exception",3);
    auto in=f.input();in.view=nullptr;calls=0;raised=false;try{s::project_visibility(q,{in},4,[&](const auto&){++calls;});}catch(const p::Error&){raised=true;}need(raised&&!calls,"bad context before callback");
    raised=false;try{s::project_visibility(q,{f.input()},4,{});}catch(const p::Error&){raised=true;}need(raised,"missing callback");
}
void grammar(){
    Fixture f;f.receive();const auto reject=[&](Json q){unsigned calls=0;bool threw=false;try{s::project_visibility(q,{f.input()},2,[&](const auto&){++calls;});}catch(const p::Error&){threw=true;}need(threw&&calls==0,"invalid rule before projection");};
    for(const char* field:{"schema_version","binding","op","value","unit"}){auto q=rule();q.erase(field);reject(q);}
    auto q=rule();q["schema_version"]="0.2.0";reject(q);q=rule();q["extra"]=true;reject(q);q=rule();q["op"]="eval";reject(q);
    q=rule();q["value"]=nullptr;reject(q);q["value"]=std::numeric_limits<double>::infinity();reject(q);q["value"]=std::numeric_limits<double>::quiet_NaN();reject(q);
    q=rule();q["unit"]="";reject(q);q["unit"]="byte per second";reject(q);q["unit"]=std::string(65,'a');reject(q);
    q=rule();q["value"]="text";reject(q);q["unit"]="1";q["op"]="gt";reject(q);q["op"]="eq";q["value"]=std::string(513,'a');reject(q);
    q=rule();q["binding"]=selector();q["binding"]["mode"]="collection";reject(q);q["binding"]["mode"]="singleton";q["binding"]["limit"]=2;reject(q);
    q=rule();q["binding"]={{"kind","unresolved_pin"},{"source_schema_version","0.1.0"},{"entity_id","a"},{"field","test.value"},{"reason","producer_context_required"}};check(q,{f.input()},"pending","legacy unresolved");
    q=rule();q["binding"]=selector();check(q,{f.input()},"shown","singleton selector");
    std::string unicode;for(unsigned i=0;i<512;++i)unicode+="\xf0\x9f\x98\x80";
    q["value"]=unicode;q["unit"]="1";c::validate_visibility_document(q);
    for(unsigned i=0;i<16;++i)q["binding"]["predicates"].push_back({{"field","entity.display_name"},{"op","eq"},{"value",unicode}});
    need(q.dump().size()>32768&&q.dump().size()<65536,"large valid rule");c::validate_visibility_document(q);
    q["value"]=std::string(65536,'a');reject(q);
}
void batch_order(){
    Fixture f;f.receive();auto absent=direct(),unsupported=direct(),missing=direct();absent["entity_id"]="missing";unsupported["field"]="other.field";missing["producer_id"]="missing";
    Json unresolved={{"kind","unresolved_pin"},{"source_schema_version","0.1.0"},{"entity_id","a"},{"field","test.value"},{"reason","producer_context_required"}};
    const std::vector<Json> queries{direct(),absent,direct(),unsupported,unresolved,missing};const auto original=queries;
    const std::vector<s::BindingCode> expected{s::BindingCode::matched,s::BindingCode::empty,s::BindingCode::matched,s::BindingCode::unsupported,s::BindingCode::pending,s::BindingCode::unsupported};unsigned calls=0;
    s::project_bindings(queries,{f.input()},2,[&](const auto& batch){++calls;need(batch.code==s::BindingBatchCode::ready&&batch.frames.size()==expected.size(),"batch order/count");
        for(std::size_t n=0;n<expected.size();++n){const auto& frame=batch.frames[n];need(frame.code==expected[n],"batch ordered outcome");
            if(frame.code==s::BindingCode::matched){need(frame.total==1&&frame.rows.size()==1&&!frame.truncated,"singleton batch");const auto& row=frame.rows[0];need(row.producer=="P1"&&row.epoch=="E1"&&row.entity=="a"&&std::get<std::uint64_t>(row.observation.value)==3,"same-view query result");}
            else need(frame.rows.empty(),"failed query has no payload");}
    });need(calls==1&&queries==original,"batch once/immutable");
    s::project_bindings(std::vector<Json>(512,direct()),{f.input()},3,[](const auto& batch){need(batch.code==s::BindingBatchCode::ready&&batch.frames.size()==512,"maximum duplicate queries");});
}
void batch_isolation(){
    Fixture a,b("uint64","4","byte","P2"),c("uint64","5","byte","P3");a.receive();c.receive();c.view.policy(policy(8,false),2);
    auto bq=direct(),cq=direct(),missing=direct();bq["producer_id"]="P2";cq["producer_id"]="P3";missing["producer_id"]="P4";
    const std::vector<s::BindingCode> expected{s::BindingCode::matched,s::BindingCode::pending,s::BindingCode::denied,s::BindingCode::unsupported,s::BindingCode::denied};
    s::project_bindings({direct(),bq,cq,missing,selector()},{a.input(),b.input(),c.input()},3,[&](const auto& batch){need(batch.code==s::BindingBatchCode::ready&&batch.frames.size()==expected.size(),"independent routes");for(std::size_t n=0;n<expected.size();++n)need(batch.frames[n].code==expected[n],"denied/waiting isolation and precedence");});
    b.receive(4);auto bad=b.input();bad.now=tick("wrong",100);
    s::project_bindings({direct(),bq},{a.input(),bad},5,[](const auto& batch){need(batch.code==s::BindingBatchCode::ready&&batch.frames[0].code==s::BindingCode::matched&&batch.frames[1].code==s::BindingCode::pending,"failed measured borrow only blocks its route");});
    a.view.disconnect(a.token,7,6);auto retained=a.input();retained.now.reset();
    s::project_bindings({direct(),direct()},{retained},7,[](const auto& batch){need(batch.code==s::BindingBatchCode::ready,"retained batch");for(const auto& f:batch.frames)need(f.code==s::BindingCode::matched&&f.rows[0].presentation==r::Presentation::retained&&f.rows[0].effective==m::Freshness::stale&&!f.rows[0].age_ns,"retained not current");});
}
void batch_bounds(){
    Fixture f;f.receive();const auto capacity=[&](const std::vector<Json>& q,s::BindingLimits limit){unsigned calls=0;s::project_bindings(q,{f.input()},2,[&](const auto& batch){++calls;need(batch.code==s::BindingBatchCode::capacity&&batch.frames.empty(),"atomic batch capacity");},limit);need(calls==1,"one capacity delivery");};
    s::BindingLimits limit;limit.output_bytes=0;capacity({direct()},limit);limit={};limit.index_bytes=0;capacity({direct()},limit);
    limit={};limit.work_steps=3;capacity({direct(),direct()},limit);limit.work_steps=4;
    s::project_bindings({direct(),direct()},{f.input()},2,[](const auto& b){need(b.code==s::BindingBatchCode::ready&&b.frames.size()==2,"exact aggregate work bound");},limit);
    limit={};limit.output_bytes=600;s::project_bindings({direct()},{f.input()},2,[](const auto& b){need(b.code==s::BindingBatchCode::ready,"one query fits output bound");},limit);capacity({direct(),direct()},limit);
    s::project_bindings({}, {f.input()},2,[](const auto& b){need(b.code==s::BindingBatchCode::ready&&b.frames.empty(),"empty batch needs no budget");},{0,0,0});
    const auto reject=[&](const std::vector<Json>& queries,const std::vector<s::BindingInput>& inputs,s::BindingLimits limits=s::BindingLimits{}){unsigned calls=0;bool rejected=false;try{s::project_bindings(queries,inputs,3000,[&](const auto&){++calls;},limits);}catch(const p::Error&){rejected=true;}need(rejected&&!calls,"batch invalid before delivery");need(f.view.status(2).payload_available,"invalid batch must not advance participating view");};
    auto invalid=direct();invalid.erase("field");reject({direct(),invalid},{f.input()});reject(std::vector<Json>(513,direct()),{f.input()});
    auto input=f.input();input.view=nullptr;reject({direct()},{input});limit={};limit.work_steps=4194305;reject({direct()},{f.input()},limit);
    auto large=selector();for(unsigned n=0;n<16;++n)large["predicates"].push_back({{"field","entity.display_name"},{"op","eq"},{"value",std::string(512,'x')}});
    c::validate_binding_document(large);need(large.dump().size()*32>262144,"aggregate document fixture");reject(std::vector<Json>(32,large),{f.input()});
    bool rejected=false;try{s::project_bindings({direct()},{f.input()},3,{});}catch(const p::Error&){rejected=true;}need(rejected,"missing batch sink");
}
void batch_lifetime(){
    std::vector<std::unique_ptr<Fixture>> owners;std::vector<s::BindingInput> inputs;std::vector<Json> queries;
    for(unsigned n=1;n<=16;++n){owners.push_back(std::make_unique<Fixture>("uint64",std::to_string(n),"byte","P"+std::to_string(n)));owners.back()->receive();inputs.push_back(owners.back()->input());auto q=direct();q["producer_id"]="P"+std::to_string(n);queries.push_back(q);}
    unsigned calls=0;s::project_bindings(queries,inputs,2,[&](const auto& batch){++calls;need(batch.code==s::BindingBatchCode::ready&&batch.frames.size()==16,"all providers");
        for(unsigned n=0;n<16;++n){need(std::get<std::uint64_t>(batch.frames[n].rows[0].observation.value)==n+1,"ordered multi-provider value");bool guarded=false;try{owners[n]->view.status(2);}catch(const std::logic_error&){guarded=true;}need(guarded,"every participating view borrowed");}
        bool guarded=false;try{s::project_bindings({direct()},inputs,2,[](const auto&){});}catch(const std::logic_error&){guarded=true;}need(guarded,"nested query cannot reenter");});need(calls==1,"one shared callback");
    for(bool allocation:{false,true}){calls=0;bool raised=false;try{s::project_bindings(queries,inputs,3,[&](const auto&){++calls;if(allocation)throw std::bad_alloc();throw std::runtime_error("sink");});}catch(const std::bad_alloc&){raised=allocation;}catch(const std::runtime_error&){raised=!allocation;}need(calls==1&&raised,"batch sink exception exactly once");for(const auto& f:owners)need(f->view.status(3).payload_available,"all borrows released after exception");}
}
Json scene_result(const s::VisibilityScene& view){Json out={{"state",view.code==s::VisibilitySceneCode::ready?"ready":view.code==s::VisibilitySceneCode::restricted?"restricted":"capacity"},{"nodes",Json::array()},{"diagnostics",Json::array()}};
    for(const auto& n:view.nodes)out["nodes"].push_back(Json::array({n.id,n.parent,code(n.own),n.show_content,n.blocker}));
    for(const auto& d:view.diagnostics)out["diagnostics"].push_back(Json::array({d.id,code(d.code)}));
    return out;
}
void tree_cases(const Json& fixture){for(const auto& test:fixture.at("cases")){
    Fixture f;f.receive();auto scene=fixture.at("scene");for(auto& w:scene["widgets"]){const auto id=w["id"].get<std::string>();if(test["rules"].contains(id))w["visibility"]=fixture["rules"][test["rules"][id].get<std::string>()];}
    unsigned now=2;if(test.contains("policy")){f.view.policy(policy(8,false),2);now=3;if(test["policy"]=="regranted"){f.view.policy(policy(9),3);now=4;}}
    s::BindingLimits limit;if(test.contains("output_bytes"))limit.output_bytes=test["output_bytes"];
    const Json expected={{"state",test.value("state",std::string("ready"))},{"nodes",test["nodes"]},{"diagnostics",test["diagnostics"]}};
    for(unsigned permutation=0;permutation<2;++permutation){const auto original=scene;unsigned calls=0;s::project_scene_visibility(scene,{f.input()},now,[&](const auto& view){++calls;need(scene_result(view)==expected,test["id"].get<std::string>()+": fixed hierarchy outcome");},limit);need(calls==1&&scene==original,"tree once/immutable");std::reverse(scene["widgets"].begin(),scene["widgets"].end());}
}}
void tree_lifetime(const Json& fixture){
    Fixture f;f.receive();auto scene=fixture.at("scene");for(auto& w:scene["widgets"])w["visibility"]=rule();unsigned calls=0;
    s::project_scene_visibility(scene,{f.input()},2,[&](const auto& v){++calls;need(v.code==s::VisibilitySceneCode::ready&&v.nodes.size()==5&&v.diagnostics.empty(),"nested same-source conditions");bool guarded=false;try{f.view.status(2);}catch(const std::logic_error&){guarded=true;}need(guarded,"all decisions inside source borrow");});need(calls==1,"one tree sink");
    calls=0;bool raised=false;try{s::project_scene_visibility(scene,{f.input()},3,[&](const auto&){++calls;throw std::bad_alloc();});}catch(const std::bad_alloc&){raised=true;}need(raised&&calls==1,"tree bad_alloc once");need(f.view.status(3).payload_available,"tree releases borrow");
    auto invalid=scene;invalid["widgets"][0]["visibility"]["value"]=nullptr;calls=0;raised=false;try{s::project_scene_visibility(invalid,{f.input()},3000,[&](const auto&){++calls;});}catch(const p::Error&){raised=true;}need(raised&&!calls&&f.view.status(3).payload_available,"invalid late scene before view access");
    scene["widgets"]=Json::array();scene["roots"]=Json::array();for(unsigned n=0;n<256;n+=16)scene["roots"].push_back("n"+std::to_string(n));auto prototype=fixture.at("scene")["widgets"][0];
    for(unsigned n=0;n<256;++n){auto w=prototype;w["id"]="n"+std::to_string(n);w["visibility"]=rule();if(n%16<15){w["kind"]="group";w["content"]=Json::object();w["children"]=Json::array({"n"+std::to_string(n+1)});w["layout"]["base"]={{"kind","stack"},{"axis","vertical"},{"gap_dip",0},{"overflow","diagnose"}};}scene["widgets"].push_back(w);}
    s::project_scene_visibility(scene,{f.input()},4,[](const auto& v){need(v.code==s::VisibilitySceneCode::ready&&v.nodes.size()==256,"maximum widget count at depth 16");for(std::size_t n=0;n<v.nodes.size();++n)need(v.nodes[n].id=="n"+std::to_string(n)&&v.nodes[n].show_content&&v.nodes[n].blocker.empty(),"preorder maximum widget count");});
    auto too_deep=scene;too_deep["roots"]=Json::array({"n0"});too_deep["widgets"]=Json::array();
    for(unsigned n=0;n<17;++n){auto w=scene["widgets"][n];if(n==15){w["kind"]="group";w["content"]=Json::object();w["children"]=Json::array({"n16"});w["layout"]=scene["widgets"][0]["layout"];}if(n==16){w=scene["widgets"][15];w["id"]="n16";}too_deep["widgets"].push_back(w);}
    raised=false;calls=0;try{s::project_scene_visibility(too_deep,{f.input()},3000,[&](const auto&){++calls;});}catch(const p::Error& e){raised=std::string(e.what())=="scene.depth";}need(raised&&!calls&&f.view.status(4).payload_available,"depth 17 rejects before source access");

}
}
int visibility_test(const std::string& name,const std::string& root){
    std::ifstream input(root+"/../visibility-cases.json");Json cases;input>>cases;
    if(name.rfind("VISIBILITY-TREE-",0)==0){std::ifstream file(root+"/../visibility-composition-cases.json");Json fixed;file>>fixed;if(name=="VISIBILITY-TREE-CASES")tree_cases(fixed);else if(name=="VISIBILITY-TREE-LIFETIME")tree_lifetime(fixed);else return 2;return 0;}
    if(name=="VISIBILITY-BATCH-ORDER"){batch_order();return 0;}if(name=="VISIBILITY-BATCH-ISOLATION"){batch_isolation();return 0;}
    if(name=="VISIBILITY-BATCH-BOUNDS"){batch_bounds();return 0;}if(name=="VISIBILITY-BATCH-LIFETIME"){batch_lifetime();return 0;}
    if(name=="VISIBILITY-COMPARE")comparisons(cases.at("comparisons"));
    else if(name=="VISIBILITY-STATES")states(cases.at("states"));
    else if(name=="VISIBILITY-LIFECYCLE")lifecycle();else if(name=="VISIBILITY-LIMITS")limits();else if(name=="VISIBILITY-GRAMMAR")grammar();else return 2;
    return 0;
}
