#include "async_commands.hpp"
#include "session.hpp"
#include "digest.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>

namespace c=syspane::configuration;namespace p=syspane::protocol;using p::Json;
void check(bool value,int line){if(!value)throw std::runtime_error("check:"+std::to_string(line));}
#define CHECK(x) check(static_cast<bool>(x),__LINE__)
std::string root;
Json read(const std::string& path){std::ifstream input(root+"/"+path);CHECK(input.good());Json value;input>>value;return value;}
const std::set<std::string> caps={"scene.selector","scene.content","scene.edit-locks","scene.visibility","theme.typography","configuration.theme-overrides"};
c::Authority authority(){return {true,"console",{"console"}};}
c::Policy policy(){c::Policy value;value.available=true;value.revision=7;for(const auto* channel:{"inspector","accessibility"})value.disclosure[{"console",channel}]={"public","operational","sensitive"};return value;}
std::string binary(){std::string bytes(1048832,'\0');for(std::size_t i=0;i<bytes.size();++i)bytes[i]=static_cast<char>(i%256);return bytes;}
c::Committed initial(bool large=false){
    const auto fixture=read("tests/configuration/profile-startup-cases.json");c::Authored documents{fixture["documents"]["settings"],fixture["documents"]["scene"]};
    auto selection=fixture["selection"];std::vector<c::ContentPackage> packages;
    for(const auto& item:fixture["packages"]){
        c::ContentPackage package{item["manifest"],item["assets"].get<std::map<std::string,std::string>>()};
        auto manifest=p::parse(package.manifest);
        if(large&&manifest["kind"]=="preset"){
            for(const auto& asset:std::map<std::string,std::string>{{"binary.png",binary()},{"empty.png",{}}}){
                package.assets.emplace(asset);manifest["assets"].push_back({{"path",asset.first},{"media_type","image/png"},{"sha256",c::content_sha256(asset.second)},{"bytes",asset.second.size()}});
                manifest["total_unpacked_bytes"]=manifest["total_unpacked_bytes"].get<std::size_t>()+asset.second.size();
            }
            package.manifest=manifest.dump();selection["package"]["sha256"]=c::sha256(package.manifest);
        }
        packages.push_back(std::move(package));
    }
    c::ContentCatalog catalog(std::move(packages));auto resources=catalog.resources(selection,documents);return {std::move(documents),{},std::move(resources)};
}
struct Store:c::GenerationStore{
    c::Committed current,previous;mutable unsigned reads=0;bool unknown=false;
    explicit Store(bool large=false):current(initial(large)){}
    c::Committed load()const override{++reads;return current;}
    std::vector<c::CommitReceipt> receipts()const override{++reads;std::vector<c::CommitReceipt> out;for(const auto* item:{&current,&previous})if(item->identity)out.push_back({*item->identity,c::authored_revision(item->documents)});return out;}
    std::optional<c::Committed> reconcile(const std::string&,const std::string&,const std::string&)const override{return {};}
    c::Publication publish(const c::Committed& next,const std::function<void()>& guard)override{guard();previous=current;current=next;return unknown?c::Publication::unknown:c::Publication::durable;}
};
std::string envelope(const std::string& kind,const Json& body,const std::string& id="C",const std::string& epoch="E"){
    Json value{{"type",kind},{"body",body}};if(kind!="hello"){value["connection_id"]=id;value["producer_epoch"]=epoch;}return value.dump();
}
Json hello(){
    Json docs=Json::array();for(const auto* name:{"profile-request","profile-result","command-result"})docs.push_back({{"document",name},{"version","0.1.0"}});docs.push_back({{"document","command"},{"version","0.5.0"}});
    return {{"wire_major",0},{"wire_minor",1},{"role","console"},{"producer_epoch","client"},{"max_frame_bytes",p::large_command_frame_floor},
        {"document_versions",docs},{"required_features",Json::array({"configuration.profile"})},
        {"optional_features",Json::array({"configuration.transactions","configuration.content","configuration.scene-content","configuration.large-commands"})}};
}
Json open_request(const std::string& id="Q"){return {{"schema_version","0.1.0"},{"query_id",id},{"op","open"}};}
Json next_request(const Json& result){
    const auto length=result["hex"].get<std::string>().size()/2;auto part=*p::decimal(result["part"].get<std::string>()),offset=*p::decimal(result["offset"].get<std::string>())+length;
    if(offset==*p::decimal(result["part_bytes"].get<std::string>())){++part;offset=0;}
    return {{"schema_version","0.1.0"},{"query_id","Qnext"},{"op","read"},{"transfer_id",result["transfer_id"]},{"part",std::to_string(part)},{"offset",std::to_string(offset)}};
}
struct Harness{
    Store store;std::shared_ptr<c::AsyncCommands> owner; c::Sessions sessions;std::uint64_t now=0;
    explicit Harness(c::Policy effective=policy(),bool large=false,c::AsyncCommands::RecoveryProvider recovery={}):store(large),owner(std::make_shared<c::AsyncCommands>(store,"E",c::make_resource_provider(store,caps),std::move(recovery))),sessions("E",0,std::move(effective),{},owner){}
    void connect(const std::string& id="C",Json greeting=hello(),c::Authority granted=authority()){
        sessions.open(id,"principal",std::move(granted),now);sessions.receive(id,envelope("hello",greeting),now);
    }
    Json pop(const std::string& id="C"){const auto bytes=sessions.pop(id,now);CHECK(bytes);return p::decode(*bytes,true).body;}
    void open(const std::string& id="C"){connect(id);CHECK(pop(id)["role"]=="console");}
    void send(const Json& request,const std::string& id="C"){sessions.receive(id,envelope("profile.read",request,id),now);}
    Json exchange(const Json& request,const std::string& id="C"){send(request,id);return pop(id);}
    c::ProfileView download(const std::string& id="C"){
        c::ProfileDownload reader(id,"E",caps);const auto reads=store.reads;
        for(unsigned i=0;!reader.complete();++i){CHECK(i<20000);send(reader.request("Q"+std::to_string(i)),id);const auto bytes=sessions.pop(id,now);CHECK(bytes);reader.receive(p::decode(*bytes));}
        CHECK(store.reads==reads);return reader.view();
    }
    void submit(){sessions.receive("C",envelope("command",read("tests/configuration/profile-startup-command-case.json")["command"]),now);CHECK(!sessions.closed("C"));}
    void execute(){auto ticket=owner->take();CHECK(ticket);auto done=owner->run(*ticket);CHECK(owner->finish(std::move(done),now,true));CHECK(pop()["outcome"]=="accepted");}
};
template<class F>void rejects(F&& action){try{action();}catch(const p::Error&){return;}throw std::runtime_error("expected refusal");}
void exact(){
    Harness h;h.open();auto view=h.download();const auto expected=initial();CHECK(view.documents.settings==expected.documents.settings&&view.documents.scene==expected.documents.scene);
    CHECK(view.resources->selection()==expected.resources->selection()&&view.resources->theme_pin()==expected.resources->theme_pin());
    std::map<std::string,std::map<std::string,std::string>> a,b;for(const auto& x:view.resources->packages())a[x->manifest]=x->assets;for(const auto& x:expected.resources->packages())b[x->manifest]=x->assets;CHECK(a==b);CHECK(view.policy.revision==7&&view.policy.available);
}
void read_only(){auto value=policy();value.forced["display.enabled"]=false;value.denied_capabilities.insert("settings.commit");value.disclosure[{"saver","saver"}]={"public"};Harness h(value);h.open();auto view=h.download();CHECK(view.policy.forced==value.forced&&view.policy.denied_capabilities==value.denied_capabilities);CHECK(view.policy.disclosure.size()==2&&view.documents.settings==h.store.current.documents.settings);}
void denied(){
    for(int kind=0;kind<7;++kind){auto value=policy();if(kind==0)value.available=false;if(kind==1)value.disclosure[{"console","inspector"}]={"operational"};if(kind==2)value.disclosure.erase({"console","accessibility"});if(kind==3)value.denied_capabilities.insert("profile.open");if(kind==4)value.denied_capabilities.insert("profile.read");if(kind==5)value.denied_capabilities.insert("scene.content");if(kind==6)value.denied_capabilities.insert("projection.inspector");Harness h(value);h.open();CHECK(h.exchange(open_request())==Json({{"schema_version","0.1.0"},{"query_id","Q"},{"outcome","denied"}}));}
    Harness h;auto greeting=hello();greeting["role"]="desktop";h.connect("C",greeting,{true,"desktop",{"desktop"}});(void)h.pop();CHECK(h.exchange(open_request())["outcome"]=="denied");
}
void negotiate(){
    for(int kind=0;kind<2;++kind)for(bool required:{false,true}){Harness h;auto greeting=hello();if(kind==0)greeting["document_versions"].erase(greeting["document_versions"].begin());else greeting["max_frame_bytes"]=12287;
        if(!required){greeting["required_features"]=Json::array();greeting["optional_features"].push_back("configuration.profile");}
        h.connect("C",greeting);CHECK(h.sessions.closed("C")==required);if(!required){auto welcome=h.pop();for(const auto& feature:welcome["optional_features"])CHECK(feature!="configuration.profile");}}
    Harness h;auto greeting=hello();greeting["max_frame_bytes"]=12288;greeting["document_versions"].erase(greeting["document_versions"].begin()+2,greeting["document_versions"].end());h.connect("C",greeting);CHECK(!h.sessions.closed("C"));(void)h.pop();CHECK(h.exchange(open_request())["outcome"]=="chunk");
}
void busy(){Harness h;h.open();h.open("B");const auto first=h.exchange(open_request());CHECK(h.exchange(open_request(),"B")["outcome"]=="busy");auto close=open_request();close["op"]="close";close["transfer_id"]=first["transfer_id"];CHECK(h.exchange(close)["outcome"]=="closed");CHECK(h.exchange(open_request(),"B")["transfer_id"]=="2");}
void foreign(){Harness h;h.open();h.open("B");auto first=h.exchange(open_request());h.send(next_request(first),"B");CHECK(h.sessions.closed("B"));CHECK(h.exchange(next_request(first))["outcome"]=="chunk");h.sessions.disconnect("C");h.open();h.send(next_request(first));CHECK(h.sessions.closed("C"));h.sessions.disconnect("C");h.open();CHECK(h.exchange(open_request())["transfer_id"]=="2");}
void cursors(){for(const auto* field:{"part","offset","transfer_id"}){Harness h;h.open();auto query=next_request(h.exchange(open_request()));query[field]="999";h.send(query);CHECK(h.sessions.closed("C"));h.open("B");CHECK(h.exchange(open_request(),"B")["outcome"]=="chunk");}}
void expiry(){
    {Harness h;h.open();h.exchange(open_request());h.now=4999;h.sessions.receive("C",envelope("heartbeat",{{"sequence","1"}}),h.now);(void)h.pop();h.now=5000;h.sessions.tick(h.now);CHECK(h.sessions.closed("C"));h.open("B");CHECK(h.exchange(open_request(),"B")["outcome"]=="chunk");}
    {Harness h(policy(),true);h.open();auto reply=h.exchange(open_request());for(unsigned i=1;i<=12;++i){h.now=i*4999;reply=h.exchange(next_request(reply));}h.now=60000;h.sessions.tick(h.now);CHECK(h.sessions.closed("C")&&h.sessions.close_reason("C")=="profile.expired");}
}
void revocation(){for(bool same:{false,true}){Harness h;h.open();h.send(open_request());auto next=policy();next.revision=same?7:8;next.available=false;if(same)rejects([&]{h.sessions.policy(next,1);});else h.sessions.policy(next,1);CHECK(!h.sessions.pop("C",1));CHECK(h.sessions.closed("C"));}}
void pinned(){Harness h;h.open();auto reply=h.exchange(open_request());h.submit();h.execute();do{CHECK(reply["revision"]=="0");reply=h.exchange(next_request(reply));}while(!reply["complete"].get<bool>());CHECK(reply["revision"]=="0");auto view=h.download();CHECK(view.documents.settings["revision"]=="1"&&view.documents.settings["sampling"]["resources_ms"]==1500);}
void joined(){
    {Harness h;h.open();h.submit();auto ticket=h.owner->take();CHECK(ticket);auto done=h.owner->run(*ticket);CHECK(!h.owner->finish(std::move(done),0,false));CHECK(h.download().documents.settings["revision"]=="0");CHECK(h.owner->finish(std::move(done),0,true));CHECK(h.pop()["outcome"]=="accepted");CHECK(h.download().documents.settings["revision"]=="1");}
    {Harness h;h.store.unknown=true;h.open();h.submit();auto ticket=h.owner->take();CHECK(ticket);auto done=h.owner->run(*ticket);CHECK(h.owner->finish(std::move(done),0,true));CHECK(h.pop()["outcome"]=="unknown");CHECK(h.exchange(open_request())["outcome"]=="unavailable");}
}
void queue(){Harness h;h.open();h.exchange(open_request());for(int i=0;i<17&&!h.sessions.closed("C");++i)h.sessions.receive("C",envelope("heartbeat",{{"sequence",std::to_string(i)}}),0);CHECK(h.sessions.closed("C"));h.open("B");CHECK(h.exchange(open_request(),"B")["outcome"]=="chunk");}
void large(){Harness h(policy(),true);h.open();auto view=h.download();bool found=false;for(const auto& package:view.resources->packages())if(package->assets.count("binary.png")){CHECK(package->assets.at("binary.png")==binary()&&package->assets.at("empty.png").empty());found=true;}CHECK(found);}
void corruption(){
    for(int kind=0;kind<8;++kind){Harness h;h.open();c::ProfileDownload reader("C","E",caps);auto query=reader.request("Q");h.send(query);auto raw=h.sessions.pop("C",0);CHECK(raw);auto message=p::decode(*raw);
        if(kind==0)message.producer_epoch="different";
        if(kind==1)message.connection_id="B";
        if(kind==2)message.body["query_id"]="different";
        if(kind==3)message.body["hex"].get_ref<std::string&>()[0]='0';
        if(kind==4)message.body["sha256"]=std::string(64,'0');
        if(kind==5)message.body["part_count"]="1093";
        if(kind==6)message.body["offset"]="1";
        if(kind==7)message.body["complete"]=true;
        rejects([&]{reader.receive(message);});rejects([&]{(void)reader.view();});rejects([&]{reader.request("again");});}
    // A self-consistent chunk digest cannot make a malformed semantic header valid.
    Harness h;h.open();c::ProfileDownload reader("C","E",caps);bool refused=false;
    for(unsigned i=0;i<100&&!refused;++i){
        h.send(reader.request("Q"+std::to_string(i)));auto message=p::decode(*h.sessions.pop("C",0));
        if(i==0){
            std::string raw;const auto hex=message.body["hex"].get<std::string>();
            for(std::size_t at=0;at<hex.size();at+=2)raw.push_back(static_cast<char>(std::stoul(hex.substr(at,2),nullptr,16)));
            auto header=p::parse(raw);std::reverse(header["capabilities"].begin(),header["capabilities"].end());raw=header.dump();
            CHECK(raw.size()==hex.size()/2);std::string changed;const std::string digits="0123456789abcdef";
            for(unsigned char byte:raw){changed.push_back(digits[byte>>4]);changed.push_back(digits[byte&15]);}
            message.body["hex"]=changed;message.body["sha256"]=c::sha256(raw);
        }
        try{reader.receive(message);}catch(const p::Error& error){CHECK(std::string(error.what())=="profile.capabilities");refused=true;}
    }
    CHECK(refused&&!reader.complete());
}
void invalidation(){Harness h;h.open();c::ProfileDownload reader("C","E",caps);rejects([&]{(void)reader.view();});h.send(reader.request("Q"));reader.receive(p::decode(*h.sessions.pop("C",0)));reader.invalidate();rejects([&]{reader.request("Q2");});rejects([&]{(void)reader.view();});
    h.sessions.disconnect("C");h.open();c::ProfileDownload complete("C","E",caps);for(unsigned i=0;!complete.complete();++i){h.send(complete.request("Q"+std::to_string(i)));complete.receive(p::decode(*h.sessions.pop("C",0)));}complete.invalidate();CHECK(!complete.complete());rejects([&]{(void)complete.view();});}
void bounds(){auto query=open_request();query["path"]="/etc/shadow";rejects([&]{p::validate_profile_request(query);});query=open_request();query["op"]="read";query["transfer_id"]="01";query["part"]="0";query["offset"]="0";rejects([&]{p::validate_profile_request(query);});Harness h;h.open();const auto original=h.exchange(open_request());for(int i=0;i<4;++i){auto reply=original;if(i==0)reply["hex"]=std::string(8194,'0');if(i==1)reply["part_bytes"]="16777217";if(i==2)reply["part_count"]="1093";if(i==3)reply["transfer_id"]="0";rejects([&]{p::validate_profile_result(reply);});}}
Json recovery_cases(){return read("tests/configuration/recovery-transfer-cases.json");}
c::Policy recovery_policy(){auto value=policy();value.disclosure[{"console","history"}]={"sensitive"};return value;}
c::AsyncCommands::RecoveryProvider recovery_provider(){return [](const c::Committed& value)->std::optional<c::ProfileRecoveryData>{
    return c::ProfileRecoveryData{"profile:default",value.documents.settings["revision"]=="0"?recovery_cases()["expected_context"]["generation"].get<std::string>():recovery_cases()["next_generation"].get<std::string>(),
        {"/fixture/state/recovery",1000,2096,101,2096,102},7,true};
};}
Json recovery_hello(){auto value=hello();value["required_features"].push_back("configuration.recovery-context");
    for(const char* name:{"profile-request","profile-result"})value["document_versions"].push_back({{"document",name},{"version","0.2.0"}});
    return value;}
void recovery_connect(Harness& h){h.connect("C",recovery_hello());CHECK(h.pop()["role"]=="console");}
std::set<std::string> recovery_caps(){auto value=caps;value.insert("editor.recovery");return value;}
struct RecoveryTransfer {c::ProfileView view;std::vector<std::string> parts;};
RecoveryTransfer receive_profile(Harness& h,bool recovery=true,std::function<void(p::Message&)> mutate={},bool capability=true){
    std::optional<c::ProfileRecoveryScope> scope;if(recovery)scope=c::ProfileRecoveryScope{"profile:default","editor:S"};
    c::ProfileDownload reader("C","E",capability?recovery_caps():caps,scope);std::vector<std::string> parts;
    for(unsigned i=0;!reader.complete();++i){CHECK(i<100);h.send(reader.request("R"+std::to_string(i)));auto raw=h.sessions.pop("C",h.now);CHECK(raw);auto message=p::decode(*raw);
        if(mutate)mutate(message);
        const auto part=std::stoul(message.body["part"].get<std::string>());if(parts.size()<=part)parts.resize(part+1);
        const auto hex=message.body["hex"].get<std::string>();for(std::size_t at=0;at<hex.size();at+=2)parts[part].push_back(static_cast<char>(std::stoul(hex.substr(at,2),nullptr,16)));
        reader.receive(message);
    }return {reader.view(),std::move(parts)};
}
void rewrite_part(p::Message& message,const std::function<void(Json&)>& mutate){
    if(message.body["part"]!="3")return;
    CHECK(message.body["offset"]=="0");const auto hex=message.body["hex"].get<std::string>();std::string raw;
    for(std::size_t at=0;at<hex.size();at+=2)raw.push_back(static_cast<char>(std::stoul(hex.substr(at,2),nullptr,16)));
    auto context=p::parse(raw);mutate(context);raw=context.dump();CHECK(raw.size()<=4096);std::string next;const std::string digits="0123456789abcdef";
    for(unsigned char byte:raw){next.push_back(digits[byte>>4]);next.push_back(digits[byte&15]);}
    message.body["hex"]=next;message.body["sha256"]=c::sha256(raw);message.body["part_bytes"]=std::to_string(raw.size());
}
void recovery_exact(){
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);auto value=receive_profile(h);
    CHECK(p::parse(value.parts[3])["recovery"]==recovery_cases()["expected_context"]);
    CHECK(value.view.recovery&&value.view.recovery->admission.directory.path=="/fixture/state/recovery");
    CHECK(value.view.documents.settings==initial().documents.settings&&value.view.documents.scene==initial().documents.scene);
    auto legacy=receive_profile(h,false);CHECK(!legacy.view.recovery);auto first=p::parse(value.parts[0]);first["schema_version"]="0.1.0";CHECK(first.dump()==legacy.parts[0]);
    CHECK(p::parse(value.parts[3])["policy"].dump()==legacy.parts[3]);
    for(std::size_t i=1;i<value.parts.size();++i)if(i!=3)CHECK(value.parts[i]==legacy.parts[i]);
}
void recovery_permission(){
    for(unsigned kind=0;kind<6;++kind){auto effective=recovery_policy();auto provider=recovery_provider();
        if(kind==0)effective.denied_capabilities.insert("editor.recovery");
        if(kind==1)effective.disclosure.erase({"console","history"});
        if(kind==2)effective.denied_capabilities.insert("projection.history");
        if(kind==3)provider=[](const c::Committed&)->std::optional<c::ProfileRecoveryData>{return {};};
        if(kind==4)effective.revision=8;
        if(kind==5)effective.denied_capabilities.insert("editor.recovery.erase");
        Harness h(effective,false,provider);recovery_connect(h);auto v=receive_profile(h);
        if(kind<5)CHECK(!v.view.recovery&&p::parse(v.parts[3])["recovery"].is_null());else CHECK(v.view.recovery&&!v.view.recovery->admission.erase);
    }
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);rejects([&]{receive_profile(h,true,{},false);});
    auto initial_value=initial();c::ProfileImage image(initial_value,caps,recovery_provider()(initial_value));
    auto effective=recovery_policy();effective.disclosure[{"desktop","history"}]={"sensitive"};
    rejects([&]{image.context({true,"desktop",{"desktop"}},effective,"C","E",{"profile:default","editor:S"},1);});
}
void recovery_negotiate(){
    for(unsigned kind=0;kind<4;++kind)for(bool required:{false,true}){
        Harness h(recovery_policy(),false,kind==0?c::AsyncCommands::RecoveryProvider{}:recovery_provider());auto greeting=recovery_hello();
        if(kind==1)greeting["document_versions"].erase(greeting["document_versions"].end()-1);
        if(kind==2)greeting["max_frame_bytes"]=12287;
        if(kind==3){greeting["required_features"]=Json::array({"configuration.recovery-context"});}
        if(!required){greeting["required_features"]=Json::array();greeting["optional_features"].push_back("configuration.recovery-context");if(kind!=3)greeting["optional_features"].push_back("configuration.profile");}
        h.connect("C",greeting);CHECK(h.sessions.closed("C")==required);
        if(!required){auto welcome=h.pop();for(const auto& feature:welcome["optional_features"])CHECK(feature!="configuration.recovery-context");
            h.send({{"schema_version","0.2.0"},{"query_id","Q"},{"op","open"},{"profile","profile:default"},{"editor_session","editor:S"}});CHECK(h.sessions.closed("C"));}
    }
    Harness h(recovery_policy(),false,recovery_provider());auto greeting=recovery_hello();
    greeting["document_versions"].erase(greeting["document_versions"].begin(),greeting["document_versions"].begin()+2);
    h.connect("C",greeting);CHECK(!h.sessions.closed("C"));(void)h.pop();CHECK(receive_profile(h).view.recovery);
}
void recovery_version(){
    for(bool initial2:{false,true}){Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);auto query=open_request();
        if(initial2){query["schema_version"]="0.2.0";query["profile"]="profile:default";query["editor_session"]="editor:S";}
        auto next=next_request(h.exchange(query));next["schema_version"]=initial2?"0.1.0":"0.2.0";h.send(next);CHECK(h.sessions.closed("C"));}
    for(bool mode:{false,true}){Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);rejects([&]{receive_profile(h,mode,[&](p::Message& message){message.body["schema_version"]=mode?"0.1.0":"0.2.0";});});}
}
void recovery_corruption(){
    for(const char* field:{"connection_id","producer_epoch","profile","editor_session","transfer_id","revision","policy_generation","generation","erase","directory","extra"}){
        Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);
        rejects([&]{receive_profile(h,true,[&](p::Message& message){rewrite_part(message,[&](Json& ctx){auto& v=ctx["recovery"];const std::string key=field;
            if(key=="erase")v[key]="true";else if(key=="directory")v[key]["path"]="/fixture/../recovery";
            else if(key=="generation")v[key]=std::string(64,'A');else if(key=="transfer_id"||key=="revision"||key=="policy_generation")v[key]="999";else v[key]="wrong";});});});
    }
    for(const char* field:{"kind","uid","state_device","state_inode","recovery_inode","path","extra"}){
        Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);
        rejects([&]{receive_profile(h,true,[&](p::Message& message){rewrite_part(message,[&](Json& ctx){auto& d=ctx["recovery"]["directory"];const std::string key=field;
            d[key]=key=="uid"?"4294967296":key=="state_device"?"2097":key=="state_inode"||key=="recovery_inode"?"0":key=="path"?"/fixture//recovery":"wrong";});});});
    }
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);
    rejects([&]{receive_profile(h,true,[&](p::Message& message){rewrite_part(message,[](Json& ctx){ctx["policy"]["denied_capabilities"].push_back("editor.recovery.erase");});});});
}
void recovery_join(){
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);h.submit();auto ticket=h.owner->take();CHECK(ticket);auto done=h.owner->run(*ticket);
    CHECK(!h.owner->finish(std::move(done),0,false));CHECK(receive_profile(h).view.recovery->admission.generation==recovery_cases()["expected_context"]["generation"]);
    CHECK(h.owner->finish(std::move(done),0,true));CHECK(h.pop()["outcome"]=="accepted");CHECK(receive_profile(h).view.recovery->admission.generation==recovery_cases()["next_generation"]);
    auto provider=recovery_provider();Harness failed(recovery_policy(),false,[&](const c::Committed& value){if(value.documents.settings["revision"]!="0")throw p::Error("fixture.provider");return provider(value);});
    recovery_connect(failed);failed.submit();ticket=failed.owner->take();CHECK(ticket);auto fault=failed.owner->run(*ticket);CHECK(failed.owner->finish(std::move(fault),0,true));
    CHECK(failed.pop()["outcome"]=="unknown"&&failed.owner->storage_faulted()&&failed.store.current.documents.settings["revision"]=="1");
    rejects([&]{Harness startup(recovery_policy(),false,[](const c::Committed&)->std::optional<c::ProfileRecoveryData>{throw p::Error("fixture.provider");});});
}
void recovery_pinned(){
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);bool committed=false;
    auto old=receive_profile(h,true,[&](p::Message& message){if(message.body["part"]=="0"&&!committed){h.submit();h.execute();committed=true;}});
    CHECK(old.view.documents.settings["revision"]=="0"&&old.view.recovery->admission.generation==recovery_cases()["expected_context"]["generation"]);
    auto current=receive_profile(h);CHECK(current.view.documents.settings["revision"]=="1"&&current.view.recovery->admission.generation==recovery_cases()["next_generation"]);
}
void recovery_invalidation(){
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);c::ProfileDownload reader("C","E",recovery_caps(),c::ProfileRecoveryScope{"profile:default","editor:S"});
    for(unsigned i=0;!reader.complete();++i){h.send(reader.request("Q"+std::to_string(i)));reader.receive(p::decode(*h.sessions.pop("C",0)));}
    CHECK(reader.view().recovery);reader.invalidate();CHECK(!reader.complete());rejects([&]{reader.view();});
    auto query=reader; // invalidation remains latched on an ordinary value copy.
    rejects([&]{query.request("again");});
    Harness revoked(recovery_policy(),false,recovery_provider());recovery_connect(revoked);
    c::ProfileDownload partial("C","E",recovery_caps(),c::ProfileRecoveryScope{"profile:default","editor:S"});revoked.send(partial.request("Q"));
    auto next=recovery_policy();next.revision=8;next.available=false;revoked.sessions.policy(next,1);CHECK(!revoked.sessions.pop("C",1));partial.invalidate();rejects([&]{partial.view();});
}
void recovery_bounds(){
    for(const char* field:{"profile","editor_session"}){auto query=Json{{"schema_version","0.2.0"},{"query_id","Q"},{"op","open"},{"profile","profile:default"},{"editor_session","editor:S"}};
        query.erase(field);rejects([&]{p::validate_profile_request(query);});query[field]=std::string(257,'x');rejects([&]{p::validate_profile_request(query);});}
    Harness h(recovery_policy(),false,recovery_provider());recovery_connect(h);auto got=receive_profile(h);auto wrong=recovery_cases()["expected_context"];wrong["generation"]=std::string(64,'0');
    CHECK(p::parse(got.parts[3])["recovery"]!=wrong);
}
int main(int argc,char** argv){
    try{CHECK(argc==3);root=argv[2];const std::string name=argv[1];const std::map<std::string,void(*)()> cases={
        {"exact-profile-and-resources",exact},{"read-only-forced-policy",read_only},{"disclosure-denials",denied},{"negotiation-and-frame-floor",negotiate},
        {"global-transfer-busy-close",busy},{"foreign-transfer-and-lifetime",foreign},{"invalid-cursors",cursors},{"idle-and-absolute-expiry",expiry},
        {"policy-clears-queued-bytes",revocation},{"current-and-pinned-revision",pinned},{"join-and-unknown-outcome",joined},{"bounded-control-queue",queue},
        {"binary-large-empty-parts",large},{"receiver-corruption-and-identity",corruption},{"receiver-invalidation",invalidation},{"schema-and-size-bounds",bounds},
        {"recovery-exact-and-legacy",recovery_exact},{"recovery-permission-and-null",recovery_permission},{"recovery-negotiation",recovery_negotiate},
        {"recovery-version-lifetime",recovery_version},{"recovery-scope-and-corruption",recovery_corruption},{"recovery-provider-and-join",recovery_join},
        {"recovery-pinned-generation",recovery_pinned},{"recovery-invalidation",recovery_invalidation},{"recovery-bounds-and-oracle",recovery_bounds}};
        CHECK(cases.count(name));cases.at(name)();std::cout<<name<<": pass\n";return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
