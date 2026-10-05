#include "telemetry.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
using namespace syspane::protocol;
void check(bool value, const char* code, int line) { if (!value) throw std::runtime_error(std::string(code)+":"+std::to_string(line)); }
#define CHECK(x) check(static_cast<bool>(x), #x, __LINE__)
Json fixture(const std::string& path) {
    std::ifstream input(path, std::ios::binary); CHECK(input.good());
    const std::string data{std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
    return Json::parse(data);
}
TelemetryBinding binding(bool consumer = false) {
    return {{1,frame_limit,{{"telemetry","0.1.0"},{"snapshot","0.1.0"},{"observation","0.1.0"}},{"telemetry.snapshot"}},
        "connection:1","fixture:epoch-1","producer:1","subscription:1","desktop","operational",7,
        consumer ? TelemetryDirection::consumer_to_producer : TelemetryDirection::producer_to_consumer};
}
Json envelope(const std::string& root, std::string type = "snapshot") {
    Json body = {{"schema_version","0.1.0"},{"subscription_id","subscription:1"}};
    if (type != "unsubscribe") { body["producer_id"]="producer:1"; body["policy_revision"]="7"; }
    if (type == "subscribe") { body["channel"]="desktop"; body["classification"]="operational"; }
    if (type == "snapshot" || type == "delta") {
        body["record_id"]="publication:1"; body["snapshot"]=fixture(root+"/valid/snapshot.json");
        if (type == "delta") body["base_generation"]="0";
    }
    return {{"type",type},{"connection_id","connection:1"},{"producer_epoch","fixture:epoch-1"},{"body",body}};
}
void reject(const std::string& bytes, const TelemetryBinding& b, const std::string& code = "") {
    bool rejected = false;
    try { (void)decode_telemetry(bytes, b); }
    catch (const Error& e) { rejected = true; if (!code.empty()) CHECK(e.what() == code); }
    CHECK(rejected);
}
void snapshots(const std::string& root) {
    auto wire = envelope(root); const auto decoded = decode_telemetry(wire.dump(), binding());
    CHECK(decoded.body["snapshot"] == fixture(root+"/valid/snapshot.json"));
    CHECK(decoded.body["snapshot"]["entities"][0]["identity"]["fixture"] == "true");
    for (const auto name : {"observation-large-counter","observation-retained-denied","observation-unsupported"}) {
        auto observation = fixture(root+"/valid/"+name+".json");
        wire["body"]["snapshot"]["observations"] = Json::array({observation});
        const auto result = decode_telemetry(wire.dump(), binding());
        CHECK(result.body["snapshot"]["observations"][0] == observation);
    }
    wire = envelope(root); auto& o = wire["body"]["snapshot"]["observations"][0];
    o["value"]={{"kind","uint64"},{"data","18446744073709551615"}};
    CHECK(decode_telemetry(wire.dump(),binding()).body["snapshot"]["observations"][0]["value"]["data"] == "18446744073709551615");
    o["value"]["data"]="18446744073709551616"; reject(wire.dump(),binding());
}
void messages(const std::string& root) {
    for (const auto type : {"subscribe","unsubscribe","snapshot","delta"}) {
        const bool consumer = std::string(type)=="subscribe" || std::string(type)=="unsubscribe";
        const auto wire = envelope(root,type); auto b = binding(consumer);
        CHECK(decode_telemetry(wire.dump(),b).type == type);
        reject(wire.dump(),binding(!consumer),"telemetry.direction");
        b.negotiated.features.clear(); reject(wire.dump(),b,"telemetry.feature"); b=binding(consumer);
        b.negotiated.documents.erase({"observation","0.1.0"}); reject(wire.dump(),b,"telemetry.feature");
        for (auto field : {"connection_id","producer_epoch"}) { auto wrong=wire; wrong[field]="wrong"; reject(wrong.dump(),binding(consumer),"telemetry.binding"); }
        auto wrong=wire; wrong["body"]["subscription_id"]="old"; reject(wrong.dump(),binding(consumer),"telemetry.binding");
        wrong=wire; wrong["body"]["schema_version"]="0.2.0"; reject(wrong.dump(),binding(consumer));
        wrong=wire; wrong["body"]["approval"]=true; reject(wrong.dump(),binding(consumer));
    }
    for (const auto type : {"subscribe","snapshot","delta"}) {
        auto wire=envelope(root,type); const auto b=binding(std::string(type)=="subscribe");
        wire["body"]["policy_revision"]="6"; reject(wire.dump(),b,"telemetry.binding");
        wire["body"]["policy_revision"]="7"; wire["body"]["producer_id"]="other"; reject(wire.dump(),b,"telemetry.binding");
    }
    auto wire=envelope(root,"subscribe"); wire["body"]["classification"]="public"; reject(wire.dump(),binding(true),"telemetry.binding");
    wire=envelope(root,"subscribe"); wire["body"]["channel"]="preview"; reject(wire.dump(),binding(true),"telemetry.binding");
    wire=envelope(root,"delta"); wire["body"]["base_generation"]="1"; reject(wire.dump(),binding(),"telemetry.generation");
    wire["body"]["base_generation"]="2"; reject(wire.dump(),binding(),"telemetry.generation");
    wire["body"]["base_generation"]=0; reject(wire.dump(),binding());
    wire=envelope(root); wire["type"]="command"; reject(wire.dump(),binding(),"telemetry.direction");
}
void graph(const std::string& root) {
    for (unsigned variant=0; variant<9; ++variant) {
        auto wire=envelope(root); auto& s=wire["body"]["snapshot"];
        if (variant==0) s["entities"].push_back(s["entities"][0]);
        if (variant==1) s["sources"].push_back(s["sources"][0]);
        if (variant==2) s["observations"].push_back(s["observations"][0]);
        if (variant==3) s["relationships"].push_back({{"source","missing"},{"target","host:demo/nic:1"},{"kind","owns"}});
        if (variant==4) s["observations"][0]["source_id"]="missing";
        if (variant==5) s["observations"][0]["entity_id"]="missing";
        if (variant==6) { s["sources"].push_back({{"id","other"},{"kind","fixture"},{"scope","host:demo"}}); auto o=s["observations"][0]; o["source_id"]="other"; s["observations"].push_back(o); }
        if (variant==7) s["entities"][0]["generation"]="2";
        if (variant==8) s["observations"][0]["generation"]="2";
        reject(wire.dump(),binding(),variant>=7 ? "telemetry.generation" : "telemetry.graph");
    }
    auto wire=envelope(root); wire["body"]["snapshot"]["observations"][0]["producer_epoch"]="other";
    reject(wire.dump(),binding(),"telemetry.generation");
    wire=envelope(root); wire["body"]["snapshot"]["producer_epoch"]="other"; reject(wire.dump(),binding(),"telemetry.binding");
    wire=envelope(root); wire["body"]["snapshot"]["observations"][0]["generation"]="0";
    CHECK(decode_telemetry(wire.dump(),binding()).body["snapshot"]["observations"][0]["generation"] == "0");
}
void times(const std::string& root) {
    for (const auto time : {"2000-02-29T23:59:59.1234567890123456789+23:59","0001-01-01t00:00:00z","9999-12-31T23:59:59-23:59","2026-10-06T00:00:00.0Z"}) {
        auto wire=envelope(root); wire["body"]["snapshot"]["captured_at"]=time;
        CHECK(decode_telemetry(wire.dump(),binding()).body["snapshot"]["captured_at"] == time);
    }
    for (const auto time : {"1900-02-29T00:00:00Z","2000-02-30T00:00:00Z","0000-01-01T00:00:00Z","2026-04-31T00:00:00Z",
         "2026-13-01T00:00:00Z","2026-01-00T00:00:00Z","2026-01-01T24:00:00Z","2026-01-01T00:60:00Z","2026-01-01T00:00:60Z",
         "2026-01-01T00:00:00","2026-01-01T00:00:00.Z","2026-01-01T00:00:00+24:00","2026-01-01T00:00:00+00:60",
         "2026-01-01T00:00:00Ztail","2026-01-01 00:00:00Z","2026-01-01T00:00:00.123"}) {
        auto wire=envelope(root); wire["body"]["snapshot"]["captured_at"]=time; reject(wire.dump(),binding());
    }
    for (const auto field : {"observed_at","attempted_at"}) {
        auto wire=envelope(root); wire["body"]["snapshot"]["observations"][0][field]="bad"; reject(wire.dump(),binding());
    }
}
void bounds(const std::string& root) {
    auto wire=envelope(root); auto bytes=wire.dump(); auto small=binding(); small.negotiated.max_frame_bytes=1024;
    wire["body"]["snapshot"]["entities"][0]["display_name"]=std::string(2048,'x'); reject(wire.dump(),small,"telemetry.capacity");
    CHECK(decode_telemetry(wire.dump(),binding()).type == "snapshot");
    wire["body"]["snapshot"]["entities"][0]["display_name"]=std::string(2049,'x'); reject(wire.dump(),binding());
    for (const auto bad : {"00","-1","18446744073709551616","1.0","+1"}) {
        wire=envelope(root); wire["body"]["snapshot"]["generation"]=bad; reject(wire.dump(),binding());
    }
    for (unsigned variant=0; variant<13; ++variant) {
        wire=envelope(root); auto& s=wire["body"]["snapshot"]; auto& o=s["observations"][0];
        if (variant==0) s["entities"][0]["identity"]={{"x",true}};
        if (variant==1) s["entities"][0]["identity"]={{std::string(257,'a'),"x"}};
        if (variant==2) for (unsigned i=0;i<65;++i) s["entities"][0]["identity"][std::to_string(i)]="x";
        if (variant==3) s["extensions"]={{"Bad",true}};
        if (variant==4) { s["extensions"]=Json::object(); for (unsigned i=0;i<65;++i) s["extensions"]["x"+std::to_string(i)]=true; }
        if (variant==5) o["value"]={{"kind","uint64"},{"data",42}};
        if (variant==6) o["value"]={{"kind","boolean"},{"data",1}};
        if (variant==7) o["value"]={{"kind","string"},{"data",std::string(16385,'x')}};
        if (variant==8) o["acquisition"]="unknown";
        if (variant==9) { o["acquisition"]="denied"; o["error"]=nullptr; }
        if (variant==10) o["error"]={{"code","bad code"},{"message","safe"},{"retryable",true}};
        if (variant==11) s["sources"]=Json::array();
        if (variant==12) o["unknown"]=true;
        reject(wire.dump(),binding());
    }
    bytes=envelope(root).dump(); auto pos=bytes.find("\"generation\":\"1\""); CHECK(pos!=std::string::npos);
    bytes.insert(pos,"\"gener\\u0061tion\":\"1\","); reject(bytes,binding(),"json.duplicate_key");
    reject(std::string(frame_limit+1,' '),binding(),"telemetry.capacity");
    reject(envelope(root).dump()+"\n",binding(),"json.encoding");
    auto nested=Json::array(); for (unsigned i=0;i<33;++i) nested=Json::array({nested});
    wire=envelope(root); wire["body"]["snapshot"]["extensions"]={{"nested",nested}}; reject(wire.dump(),binding(),"json.depth");
    wire=envelope(root); wire["body"]["snapshot"]["extensions"]={{"nodes",std::vector<int>(16384,0)}}; reject(wire.dump(),binding(),"json.nodes");
    wire=envelope(root);
    for (unsigned i=1;i<1024;++i) wire["body"]["snapshot"]["sources"].push_back({{"id","source:"+std::to_string(i)},{"kind","fixture"},{"scope","host:demo"}});
    CHECK(decode_telemetry(wire.dump(),binding()).body["snapshot"]["sources"].size()==1024);
    wire["body"]["snapshot"]["sources"].push_back({{"id","source:1024"},{"kind","fixture"},{"scope","host:demo"}});
    reject(wire.dump(),binding());
    wire=envelope(root); wire["body"]["snapshot"]["entities"]=std::vector<int>(8193,0); reject(wire.dump(),binding());
    wire=envelope(root); wire["body"]["snapshot"]["observations"][0]["value"]={{"kind","string"},{"data",std::string(16384,'x')}};
    CHECK(decode_telemetry(wire.dump(),binding()).body["snapshot"]["observations"][0]["value"]["data"].get<std::string>().size()==16384);
}
void preserve(const std::string& root) {
    for (const auto completeness : {"complete","partial","gap"}) {
        auto wire=envelope(root); auto& s=wire["body"]["snapshot"]; s["completeness"]=completeness;
        s["extensions"]={{"inert",{{"approval",true},{"nested",Json::array({nullptr,123,"x"})}}}};
        s["entities"][0]["extensions"]={{"future",true}};
        s["observations"][0]["extensions"]={{"future",false}};
        const auto bytes=wire.dump(2); auto decoded=decode_telemetry(bytes,binding());
        CHECK(decoded.body == wire["body"]);
        auto again=decode_telemetry(encode_telemetry(decoded,binding()),binding());
        CHECK(again.body_bytes == decoded.body_bytes && again.body["snapshot"]["completeness"] == completeness);
        decoded.body["record_id"]="changed";
        bool rejected=false; try { (void)encode_telemetry(decoded,binding()); } catch (const Error&) { rejected=true; } CHECK(rejected);
    }
}
int main(int argc,char** argv) {
    try {
        if (argc!=3) return 2;
        const std::string name=argv[1], root=argv[2];
        if (name=="TELEMETRY-SNAPSHOT") snapshots(root); else if (name=="TELEMETRY-MESSAGES") messages(root);
        else if (name=="TELEMETRY-GRAPH") graph(root); else if (name=="TELEMETRY-TIME") times(root);
        else if (name=="TELEMETRY-BOUNDS") bounds(root); else if (name=="TELEMETRY-PRESERVE") preserve(root); else return 2;
        std::cout<<name<<": pass\n"; return 0;
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
