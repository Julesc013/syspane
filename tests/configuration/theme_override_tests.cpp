#include "theme_resources.hpp"
#include "digest.hpp"
#include "settings_content_fixture.hpp"
#include <algorithm>
#include <iostream>
namespace {
namespace c=syspane::configuration;using c::Json;
void check(bool b,int line){if(!b)throw std::runtime_error("theme override assertion:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
template<class F>void rejects(F f,const std::string& code=""){bool caught=false;try{f();}catch(const syspane::protocol::Error& e){caught=true;CHECK(code.empty()||code==e.what());}CHECK(caught);}
c::Policy policy(){c::Policy p;p.available=true;p.revision=7;return p;}
const std::set<std::string> caps={"scene.content","theme.typography","configuration.theme-overrides"};
c::AuthoredTheme artifact(const Json& value){return {value.at("theme"),value.at("package_pin"),value.at("theme_pin"),{value.at("manifest"),{{"theme.json",value.at("asset")}}}};}
std::map<std::string,c::ContentPackage> inventory(const std::vector<std::shared_ptr<const c::ContentPackage>>& packages){
    std::map<std::string,c::ContentPackage> out;for(const auto& p:packages)CHECK(out.emplace(c::sha256(p->manifest),*p).second);return out;
}
Json hashes(const std::vector<std::shared_ptr<const c::ContentPackage>>& packages){Json out=Json::array();for(const auto& p:inventory(packages))out.push_back(p.first);return out;}
void same(const std::vector<std::shared_ptr<const c::ContentPackage>>& a,const std::vector<std::shared_ptr<const c::ContentPackage>>& b){
    const auto left=inventory(a),right=inventory(b);CHECK(left.size()==right.size());for(const auto& p:left){const auto& q=right.at(p.first);CHECK(p.second.manifest==q.manifest&&p.second.assets==q.assets);}
}
Json package_pin(const c::ContentPackage& p){const auto m=Json::parse(p.manifest);return {{"id",m["package_id"]},{"version",m["version"]},{"sha256",c::sha256(p.manifest)}};}
c::ContentPackage dummy(const Json& source,unsigned n){
    auto doc=source;doc["theme_id"]="theme:capacity:"+std::to_string(n);const auto bytes=doc.dump()+"\n";
    const Json m={{"schema_version","0.1.0"},{"package_id","package:capacity:"+std::to_string(n)},{"version","0.1.0"},{"kind","theme"},{"license","MIT"},{"dependencies",Json::array()},
        {"required_capabilities",Json::array()},{"optional_capabilities",Json::array()},{"assets",Json::array({{{"path","theme.json"},{"media_type","application/json"},{"bytes",bytes.size()},{"sha256",c::sha256(bytes)}}})},{"total_unpacked_bytes",bytes.size()}};
    return {m.dump()+"\n",{{"theme.json",bytes}}};
}
void asset(c::ContentPackage& p,const std::string& name,std::size_t size){
    std::string bytes(size,'x');auto m=Json::parse(p.manifest);m["assets"].push_back({{"path",name},{"media_type","image/png"},{"bytes",size},{"sha256",c::content_sha256(bytes)}});
    m["total_unpacked_bytes"]=m["total_unpacked_bytes"].get<std::size_t>()+size;p.manifest=m.dump()+"\n";p.assets.emplace(name,std::move(bytes));
}
c::ResourceSnapshot expanded(const c::ResourceSet& source,const c::Authored& authored,std::vector<c::ContentPackage> extra){
    std::vector<c::ContentPackage> packages;for(const auto& p:source.base_packages())packages.push_back(*p);
    auto selection=source.selection();auto root=std::find_if(packages.begin(),packages.end(),[&](const auto& p){return c::sha256(p.manifest)==selection["package"]["sha256"];});CHECK(root!=packages.end());
    auto m=Json::parse(root->manifest);for(const auto& p:extra)m["dependencies"].push_back(package_pin(p));root->manifest=m.dump()+"\n";selection["package"]=package_pin(*root);
    packages.insert(packages.end(),std::make_move_iterator(extra.begin()),std::make_move_iterator(extra.end()));return c::ContentCatalog(std::move(packages)).resources(selection,authored);
}
void run(const std::string& name,const std::string& root){
    settings_fixture::Fixture f(root);const auto cases=settings_fixture::read(root+"/tests/configuration/theme-override-cases.json");
    const auto inputs=settings_fixture::read(root+"/tests/editor/theme-authoring-cases.json");const auto art=artifact(inputs["expected"]);
    const auto source=f.catalog->resources(f.document["selection"],f.authored);auto candidate=f.authored;candidate.scene["theme_id"]=art.theme.at("theme_id");
    const auto before=candidate.scene.dump();
    if(name=="RESOLVE"){
        auto result=c::replace_theme_resources(*source,candidate,art,policy(),caps);
        CHECK(result->selection()==cases["selection"]&&result->theme().dump()==cases["expected_theme"].dump()&&result->theme_pin()==art.theme_pin);
        CHECK(hashes(result->packages())==cases["selected_manifests"]&&hashes(result->base_packages())==cases["base_manifests"]);same(source->packages(),result->base_packages());
        CHECK(result->required()==caps);Json images=Json::array();for(const auto& w:candidate.scene["widgets"])if(w["kind"]=="image")images.push_back(w["content"]["asset"]);CHECK(images==cases["image_refs"]);
        c::validate_resource_binding(*result,candidate);auto reset=c::replace_theme_resources(*result,f.authored,{},policy(),caps);CHECK(reset->selection()==cases["reset"]&&reset->theme()==source->theme());same(reset->packages(),source->packages());
        CHECK(!reset->required().count("theme.typography")&&reset->required().count("configuration.theme-overrides"));
        auto reused=expanded(*source,f.authored,{art.package});auto selected=c::replace_theme_resources(*reused,candidate,art,policy(),caps);CHECK(selected->packages().size()==reused->packages().size());same(selected->base_packages(),reused->packages());
        std::vector<c::ContentPackage> packages;for(const auto& p:result->packages())packages.push_back(*p);std::reverse(packages.begin(),packages.end());auto shuffled=c::ContentCatalog(std::move(packages)).theme_resources(cases["selection"],candidate);same(shuffled->packages(),result->packages());CHECK(shuffled->theme_pin()==result->theme_pin());
    }else if(name=="REPLACE"){
        auto current=c::replace_theme_resources(*source,candidate,art,policy(),caps);const auto first=current;
        for(unsigned n=0;n<cases["replacements"].get<unsigned>();++n){auto edit=current->theme();edit["font"]["size_dip"]=(n%2)?17.25:21.25;
            auto changed=c::author_theme(*current,edit,policy(),caps);CHECK(changed);candidate.scene["theme_id"]=changed->theme["theme_id"];
            current=c::replace_theme_resources(*current,candidate,changed,policy(),caps);CHECK(current->packages().size()==source->packages().size()+1);same(current->base_packages(),source->packages());}
        CHECK(current->selection()==cases["selection"]&&current->theme()==art.theme);same(current->packages(),first->packages());
        auto identical=c::replace_theme_resources(*current,candidate,art,policy(),caps);same(identical->packages(),current->packages());CHECK(identical->selection()==current->selection());
        auto reset=c::replace_theme_resources(*current,f.authored,{},policy(),caps);same(reset->packages(),source->packages());CHECK(source->selection()==f.document["selection"]&&first->selection()==cases["selection"]);
    }else if(name=="INVALID"){
        rejects([&]{f.catalog->resources(cases["selection"],candidate);},"content.selection");rejects([&]{f.catalog->theme_resources(source->selection(),candidate);});
        for(const auto* fixture:{"missing","digest","many","version"}){auto invalid=settings_fixture::read(root+"/spec/fixtures/invalid/resource-selection-"+fixture+".json");rejects([&]{f.catalog->theme_resources(invalid,candidate);});}
        std::vector<c::ContentPackage> packages;for(const auto& p:source->packages())packages.push_back(*p);packages.push_back(art.package);c::ContentCatalog catalog(packages);
        for(const char* field:{"id","version","sha256"})for(const char* kind:{"package","theme"}){auto bad=cases["selection"];bad["theme_override"][kind][field]=field==std::string("sha256")?std::string(64,'0'):(field==std::string("version")?"0.2.0":"unknown");rejects([&]{catalog.theme_resources(bad,candidate);},"content.reference");}
        rejects([&]{catalog.theme_resources(cases["selection"],f.authored);},"content.theme");rejects([&]{c::replace_theme_resources(*source,candidate,{},policy(),caps);},"content.theme");
        for(unsigned i=0;i<7;++i){auto bad=art;if(i==0)bad.theme["name"]="changed";if(i==1)bad.package_pin["sha256"]=std::string(64,'0');if(i==2)bad.theme_pin["id"]="wrong";if(i==3)bad.package.manifest+=" ";if(i==4)bad.package.assets["theme.json"]+=" ";if(i==5)bad.package.assets["extra.png"]="x";if(i==6){auto m=Json::parse(bad.package.manifest);m["dependencies"].push_back(source->selection()["package"]);bad.package.manifest=m.dump()+"\n";}rejects([&]{c::replace_theme_resources(*source,candidate,bad,policy(),caps);},"theme.artifact");}
        auto changed=candidate;changed.scene["widgets"].back()["content"]["asset"]["sha256"]=std::string(64,'0');rejects([&]{c::replace_theme_resources(*source,changed,art,policy(),caps);},"content.asset");
        for(const auto& cap:caps){auto reduced=caps;reduced.erase(cap);rejects([&]{c::replace_theme_resources(*source,candidate,art,policy(),reduced);},"policy.denied");auto denied=policy();denied.denied_capabilities.insert(cap);rejects([&]{c::replace_theme_resources(*source,candidate,art,denied,caps);},"policy.denied");}
        auto unavailable=policy();unavailable.available=false;rejects([&]{c::replace_theme_resources(*source,candidate,art,unavailable,caps);},"policy.denied");
        auto active=c::replace_theme_resources(*source,candidate,art,policy(),caps);auto denied=policy();denied.denied_capabilities.insert("theme.typography");rejects([&]{c::replace_theme_resources(*active,f.authored,{},denied,caps);},"policy.denied");
        auto collision=dummy(source->theme(),0);auto m=Json::parse(collision.manifest);m["package_id"]=art.package_pin["id"];collision.manifest=m.dump()+"\n";auto conflicting=expanded(*source,f.authored,{collision});rejects([&]{c::replace_theme_resources(*conflicting,candidate,art,policy(),caps);},"content.duplicate_package");
        collision=art.package;m=Json::parse(collision.manifest);m["package_id"]="package:duplicate-document";collision.manifest=m.dump()+"\n";conflicting=expanded(*source,f.authored,{collision});rejects([&]{c::replace_theme_resources(*conflicting,candidate,art,policy(),caps);},"content.ambiguous");
        for(const char* version:{"0.2.0","0.3.0","0.4.0","0.5.0","0.6.0","0.7.0"}){Json command={{"schema_version",version},{"request_id","override:refused"},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},{"content",cases["selection"]},{"operations",Json::array({{{"op","settings.set"},{"path","display.enabled"},{"value",true}}})}};rejects([&]{c::validate_command(command);});}
        CHECK(candidate.scene.dump()==before&&source->selection()==f.document["selection"]&&hashes(source->packages())==cases["base_manifests"]);
    }else if(name=="CAPACITY"){
        for(unsigned count:{63u,64u}){std::vector<c::ContentPackage> extra;for(unsigned n=static_cast<unsigned>(source->packages().size());n<count;++n)extra.push_back(dummy(source->theme(),n));auto full=expanded(*source,f.authored,std::move(extra));CHECK(full->packages().size()==count);
            if(count==63)CHECK(c::replace_theme_resources(*full,candidate,art,policy(),caps)->packages().size()==64);else rejects([&]{c::replace_theme_resources(*full,candidate,art,policy(),caps);},"content.capacity");CHECK(full->packages().size()==count);}
        std::vector<c::ContentPackage> chain;for(unsigned n=0;n<7;++n){auto p=dummy(source->theme(),n);if(n){auto m=Json::parse(p.manifest);m["dependencies"].push_back(package_pin(chain.back()));p.manifest=m.dump()+"\n";}chain.push_back(std::move(p));}
        auto deep=expanded(*source,f.authored,std::move(chain));CHECK(c::replace_theme_resources(*deep,candidate,art,policy(),caps)->packages().size()==13);
        std::vector<c::ContentPackage> extra;std::size_t assets=0;for(const auto& p:source->packages())assets+=p->assets.size();for(unsigned n=0;n<5;++n){extra.push_back(dummy(source->theme(),n));++assets;}
        for(unsigned n=0;assets<1024;++assets,++n)asset(extra[n%extra.size()],"padding-"+std::to_string(n)+".png",0);
        auto full=expanded(*source,f.authored,std::move(extra));rejects([&]{c::replace_theme_resources(*full,candidate,art,policy(),caps);},"content.capacity");
        std::size_t bytes=0;for(const auto& p:source->packages())for(const auto& a:p->assets)bytes+=a.second.size();extra.clear();for(unsigned n=0;n<4;++n){extra.push_back(dummy(source->theme(),n));bytes+=extra.back().assets.at("theme.json").size();}
        auto remaining=67108864-bytes;for(unsigned n=0;n<4;++n){const auto size=std::min<std::size_t>(remaining,16777216);asset(extra[n],"padding.png",size);remaining-=size;}CHECK(remaining==0);
        full=expanded(*source,f.authored,std::move(extra));rejects([&]{c::replace_theme_resources(*full,candidate,art,policy(),caps);},"content.capacity");
    }else throw std::runtime_error("unknown theme override test");
}
}
int main(int argc,char** argv){try{CHECK(argc==3);run(argv[1],argv[2]);std::cout<<argv[1]<<" pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
