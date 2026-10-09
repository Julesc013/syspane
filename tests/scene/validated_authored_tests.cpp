#include "layout.hpp"
#include "initial_profile.hpp"
#include <iostream>
#include <memory>
#include <type_traits>

namespace s=syspane::scene;namespace c=syspane::configuration;using c::Json;
void check(bool,const char*);
Json read(const std::string&);
Json encoded(const s::Plan&);
s::Topology topology(const Json&);
std::map<std::string,s::Metrics> metrics(const Json&);
void rejection(const std::function<void()>&,const char*);

namespace {
#ifdef SYSPANE_VALIDATED_AUTHORED_TEST
using Snapshot=c::ValidatedAuthored;
s::Plan project(const Snapshot& v,const s::Topology& t,const std::map<std::string,s::Metrics>& m){return s::resolve(v,t,m);}
void bind(const c::ResourceSet& r,const Snapshot& v){c::validate_resource_binding(r,v);}
#else
// Pre-change reference adapter: expectations below are identical in both runs.
class Snapshot {
public:
    explicit Snapshot(const c::Authored& v):value_(std::make_shared<const c::Authored>(v)){c::validate_authored(*value_);}
    const c::Authored& documents()const{if(!value_)throw syspane::protocol::Error("authored.snapshot");return *value_;}
private:
    std::shared_ptr<const c::Authored> value_;
};
s::Plan project(const Snapshot& v,const s::Topology& t,const std::map<std::string,s::Metrics>& m){return s::resolve(v.documents().scene,t,m);}
void bind(const c::ResourceSet& r,const Snapshot& v){c::validate_resource_binding(r,v.documents());}
#endif
static_assert(!std::is_default_constructible<Snapshot>::value,"unvalidated owner");
static_assert(std::is_same<decltype(std::declval<Snapshot>().documents()),const c::Authored&>::value,"mutable documents");
}

int validated_authored_test(const std::string& root){
    const auto settings=read(root+"/spec/fixtures/valid/settings.json");
    const std::vector<std::string> cases={"ROOT-FLOW","STACK-V","STACK-H","PRIORITY","FAIR-SHRINK","OVERFLOW","FIXED-GROUP","CANVAS","GRID","GRID-OVERFLOW","NESTED","BREAKPOINT-EQUAL","BREAKPOINT-BELOW","DISPLAY-MISSING","DISPLAY-AMBIGUOUS","DISPLAY-REMOVED","SAFE-REGION","EXCLUSION-TIE","NO-REGION","PIXELS","PIXEL-CLIP","READABLE-FIXED","READABLE-FLOW","OVERLAP","DISPLAY-CONFLICT","MISSING-METRICS","EXCLUSION-ORDER","QUANTIZED-FIXED","QUANTIZED-GAP","NESTED-BREAKPOINT","NATIVE-METRICS"};
    for(const auto& name:cases){
        const auto input=read(root+"/tests/scene/cases/"+name+".json");
        c::Authored raw{settings,input["scene"]};raw.settings["revision"]=raw.scene["revision"];
        Snapshot value(raw);const auto env=topology(input["topology"]);const auto sizes=metrics(input["metrics"]);
        raw.scene=Json();raw.settings=Json();
        if(input.contains("error")){const auto error=input["error"].get<std::string>();rejection([&]{project(value,env,sizes);},error.c_str());}
        else check(encoded(project(value,env,sizes))==input["expected"],"snapshot literal geometry mismatch");
    }
    const auto input=read(root+"/tests/scene/cases/ROOT-FLOW.json");
    c::Authored raw{settings,input["scene"]};raw.settings["revision"]=raw.scene["revision"];
    const auto original=raw;auto& retained=raw.scene["widgets"][0]["title"];
    Snapshot owner(std::move(raw));retained="changed through retained input reference";
    check(owner.documents().scene==original.scene&&owner.documents().settings==original.settings,"caller aliases snapshot");
    auto copy=owner;auto moved=std::move(owner);
    rejection([&]{(void)owner.documents();},"authored.snapshot");
    owner=copy;copy=std::move(moved);rejection([&]{(void)moved.documents();},"authored.snapshot");
    const auto env=topology(input["topology"]);const auto sizes=metrics(input["metrics"]);
    check(encoded(project(copy,env,sizes))==input["expected"],"copy/move changed geometry");
    auto bad=env;bad.displays[0].scale_denominator=0;
    rejection([&]{project(copy,bad,sizes);},"layout.topology");
    auto bad_metrics=sizes;bad_metrics.begin()->second.minimum.width=0;
    rejection([&]{project(copy,env,bad_metrics);},"layout.metrics");
    auto changed=input;changed["topology"]["displays"][0]["pixel_origin"][0]=100;
    auto expected=input["expected"];for(auto& node:expected["nodes"])node["pixels"][0]=node["pixels"][0].get<s::Unit>()+100;
    check(encoded(project(copy,topology(changed["topology"]),sizes))==expected,"new topology ignored");
    auto invalid=original;invalid.settings["revision"]="999999";
    rejection([&]{Snapshot v(invalid);},"authored.mixed_revision");
    invalid=original;invalid.scene["schema_version"]="9.9.9";
    rejection([&]{Snapshot v(invalid);},"authored.schema");
    invalid=original;invalid.scene["widgets"].push_back(invalid.scene["widgets"][0]);
    rejection([&]{Snapshot v(invalid);},"scene.duplicate");
    invalid=original;invalid.scene["widgets"][0]["title"]=std::string(262145,'x');
    rejection([&]{Snapshot v(invalid);},"authored.size");
    invalid=original;invalid.settings["annotations"]=std::string(16385,'x');
    rejection([&]{Snapshot v(invalid);},"authored.size");
    c::Policy policy;policy.available=true;policy.revision=7;
    const std::set<std::string> caps={"scene.selector","scene.content"};
    const auto initial=c::initial_profile(policy,caps);Snapshot selected(initial.documents);
    bind(*initial.resources,selected);c::authorize_resources(*initial.resources,policy,caps);
    auto mismatch=initial.documents;mismatch.scene["theme_id"]="theme:absent";Snapshot wrong(mismatch);
    rejection([&]{bind(*initial.resources,wrong);},"content.theme");
    policy.denied_capabilities.insert("scene.content");
    rejection([&]{c::authorize_resources(*initial.resources,policy,caps);},"policy.denied");
    bind(*initial.resources,selected); // Structural proof has never conferred authority.
    std::cout<<"AUTHORED-SNAPSHOT: 31 literal layouts, ownership, refusal and current inputs passed\n";return 0;
}
