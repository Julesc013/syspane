#include "data_view.hpp"
#include "local_ipc.hpp"
#include "session.hpp"
#include <array>
#include <deque>
#include <fstream>
#include <iostream>
#include <iterator>
#include <thread>
#include <chrono>
namespace p=syspane::protocol;
namespace c=syspane::configuration;
namespace n=syspane::platform;
namespace r=syspane::recovery;
using p::Json;
namespace {
void emit(Json value) { std::cout<<value.dump()<<std::endl; }
void need(bool ok,const char* code) { if (!ok) throw p::Error(code); }
c::Policy policy(std::uint64_t revision=7) {
    c::Policy value; value.available=true; value.revision=revision;
    value.disclosure[{"desktop","desktop"}]={"operational"}; value.disclosure[{"desktop","accessibility"}]={"operational"}; return value;
}
Json hello() { return {{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","probe:client"},
    {"max_frame_bytes",p::frame_limit},{"document_versions",Json::array({{{"document","telemetry"},{"version","0.1.0"}},
    {{"document","snapshot"},{"version","0.1.0"}},{{"document","observation"},{"version","0.1.0"}}})},
    {"required_features",{"telemetry.snapshot"}},{"optional_features",Json::array()}}}}; }
Json read_fixture(const std::string& root) {
    std::ifstream stream(root+"/valid/snapshot.json",std::ios::binary); need(stream.good(),"probe.fixture");
    const std::string bytes{std::istreambuf_iterator<char>(stream),std::istreambuf_iterator<char>()};
    need(bytes.size()<16384,"probe.fixture_size"); return Json::parse(bytes);
}
Json state(Json fixture,std::uint64_t generation) {
    fixture["generation"]=std::to_string(generation);
    fixture["observations"][0]["generation"]=std::to_string(generation);
    fixture["observations"][0]["value"]["data"]="inventory-"+std::to_string(generation);
    return fixture;
}
class Client {
public:
    explicit Client(n::Stream stream):stream_(std::move(stream)) {
        emit({{"event","authenticated"},{"peer_pid",stream_.peer().process_id},{"user_session_verified",true}});
        auto bytes=p::frame(hello().dump()); stream_.write(std::string_view(bytes).substr(0,1));
        std::this_thread::sleep_for(std::chrono::milliseconds(20)); stream_.write(std::string_view(bytes).substr(1));
        auto welcome=p::decode(next()); need(welcome.type=="welcome","probe.welcome");
        selected_=p::negotiate(p::handshake(hello()["body"]),p::handshake(welcome.body),{"console"});
        id_=welcome.connection_id; epoch_=welcome.producer_epoch; decoder_.restrict_limit(selected_.max_frame_bytes);
    }
    p::TelemetryBinding binding() const { return {selected_,id_,epoch_,"producer:1","S","desktop","operational",7,p::TelemetryDirection::producer_to_consumer}; }
    std::string next() {
        const auto start=n::monotonic_ms(); std::array<char,4096> buffer{};
        while (pending_.empty()) {
            need(n::monotonic_ms()-start<6000,"probe.receive_timeout");
            const auto read=stream_.read(buffer.data(),buffer.size());
            if (read.eof) { decoder_.eof(); throw p::Error("probe.eof"); }
            if (read.bytes) decoder_.feed(std::string_view(buffer.data(),read.bytes),read.observed_ms,[&](auto payload) {
                p::decode(payload); need(pending_.size()<16,"probe.receive_capacity"); pending_.emplace_back(payload);
            });
            decoder_.tick(read.observed_ms);
        }
        auto payload=std::move(pending_.front()); pending_.pop_front(); emit({{"event","reply"},{"message",p::parse(payload)}}); return payload;
    }
    void send(const char* type,Json body) {
        stream_.write(p::frame(Json{{"type",type},{"connection_id",id_},{"producer_epoch",epoch_},{"body",std::move(body)}}.dump(),selected_.max_frame_bytes));
    }
    void subscribe(bool wrong=false) { send("subscribe",{{"schema_version","0.1.0"},{"subscription_id","S"},{"producer_id",wrong?"wrong":"producer:1"},
        {"policy_revision","7"},{"channel","desktop"},{"classification","operational"}}); }
    void beat(unsigned seq) { send("heartbeat",{{"sequence",std::to_string(seq)}}); }
private:
    n::Stream stream_; p::Framer decoder_; std::deque<std::string> pending_;
    p::Negotiated selected_{}; std::string id_,epoch_;
};
void projection(r::DataView& view,const char* event) {
    Json result{{"event",event},{"payload",false}};
    view.project(n::monotonic_ms(),[&](const auto& snapshot,const auto& lease) {
        result["payload"]=true; result["generation"]=std::to_string(snapshot.generation);
        result["value"]=std::get<std::string>(snapshot.observations[0].value);
        result["retained"]=lease.presentation==r::Presentation::retained;
        result["measured_tick"]=snapshot.observations[0].measured_at.has_value();
    }); emit(std::move(result));
}
void client(const std::string& endpoint,const std::string& scenario,std::uint64_t expected) {
    r::DataView view({true,"desktop",{"desktop"}},policy(),"desktop","operational",{{"network.media","none",syspane::model::ValueKind::string}});
    for (unsigned ordinal=0;ordinal<(scenario=="journey"?2U:1U);++ordinal) {
        Client client(n::Stream::connect(endpoint,expected));
        const auto attached=view.attach_wire(client.binding(),n::monotonic_ms()); need(attached.code==r::DataCode::accepted,"probe.attach");
        client.subscribe(scenario=="wrong-producer");
        const auto receive=[&] {
            const auto bytes=client.next(); const auto result=view.receive(attached.token,7,bytes,n::monotonic_ms());
            need(result.code==r::DataCode::accepted || result.code==r::DataCode::duplicate,"probe.import"); projection(view,"imported");
        };
        if (scenario=="wrong-producer") {
            try { client.next(); throw p::Error("probe.unexpected_reply"); }
            catch (const p::Error& e) { need(std::string(e.what())=="probe.eof","probe.expected_eof"); }
            projection(view,"rejected"); return;
        }
        if (scenario=="overflow") {
            need(p::decode(client.next()).body["reason"]=="queue_overflow","probe.gap");
            view.gap(attached.token,7,n::monotonic_ms()); client.subscribe(); receive();
        } else receive();
        if (scenario=="expiry") {
            try { client.next(); throw p::Error("probe.unexpected_reply"); }
            catch (const p::Error& e) { need(std::string(e.what())=="probe.eof","probe.expected_eof"); }
            view.disconnect(attached.token,7,n::monotonic_ms()); projection(view,"expired"); return;
        }
        if (scenario=="revoke") {
            client.beat(0); need(p::decode(client.next()).body["reason"]=="policy_changed","probe.policy_gap");
            auto revoked=policy(8); revoked.available=false; view.policy(revoked,n::monotonic_ms()); projection(view,"revoked");
        }
        if (scenario=="journey") {
            client.beat(0); need(p::decode(client.next()).type=="heartbeat","probe.heartbeat"); receive();
            if (ordinal==0) { client.subscribe(); receive(); }
            client.send("unsubscribe",{{"schema_version","0.1.0"},{"subscription_id","S"}});
            client.beat(1); need(p::decode(client.next()).type=="heartbeat","probe.unsubscribe");
        }
        client.send("shutdown",{{"reason","normal"}}); view.disconnect(attached.token,7,n::monotonic_ms());
    }
}
void server(const std::string& endpoint,const std::string& scenario,std::uint64_t expected,const std::string& root) {
    const auto fixture=read_fixture(root); n::Listener listener(endpoint);
    emit({{"event","ready"},{"access_controls_verified",listener.access_controls_verified()},{"unprivileged_context",true}});
    c::Sessions sessions("fixture:epoch-1",0,policy(),c::InventorySource{"producer:1","desktop","operational"});
    std::uint64_t generation=1,record=0;
    for (unsigned ordinal=0;ordinal<(scenario=="journey"?2U:1U);++ordinal) {
        auto stream=listener.accept(expected); emit({{"event","authenticated"},{"peer_pid",stream.peer().process_id},{"user_session_verified",true}});
        const auto id="C"+std::to_string(ordinal); sessions.open(id,stream.peer().principal,{true,"desktop",{"desktop"}},stream.connected_ms());
        p::Framer decoder; std::array<char,4096> buffer{}; std::uint64_t offered=0; bool advanced=false,overflowed=false; std::string reason;
        const auto started=n::monotonic_ms();
        try {
            while (!sessions.closed(id)) {
                need(n::monotonic_ms()-started<12000,"probe.deadline");
                const auto read=stream.read(buffer.data(),buffer.size());
                if (read.eof) { decoder.eof(); reason="peer.eof"; break; }
                if (read.bytes) decoder.feed(std::string_view(buffer.data(),read.bytes),read.observed_ms,[&](auto payload) {
                    const auto message=p::decode(payload); sessions.receive(id,payload,n::monotonic_ms()); decoder.restrict_limit(sessions.frame_bound(id));
                    const auto sub=sessions.subscription(id); if (!sub) return;
                    const auto offer=[&](std::optional<std::uint64_t> base) {
                        return sessions.offer(id,sub->ticket,"native:"+std::to_string(++record),state(fixture,generation),base,n::monotonic_ms());
                    };
                    if (sub->ticket!=offered) {
                        if (offered) ++generation;
                        offered=sub->ticket;
                        if (scenario=="overflow" && !overflowed) {
                            for (unsigned i=0;i<17;++i) { generation=i+1; const bool queued=offer({}); need(queued==(i<16),"probe.overflow"); }
                            overflowed=true;
                        } else need(offer({}),"probe.offer_full");
                        emit({{"event","demand"},{"count",sessions.demand_count()},{"ticket",offered}});
                    } else if (message.type=="heartbeat" && !advanced && (scenario=="journey" || scenario=="revoke")) {
                        const auto base=generation++; need(offer(base),"probe.offer_delta"); advanced=true;
                        if (scenario=="revoke") { auto denied=policy(8); denied.available=false; sessions.policy(denied,n::monotonic_ms()); }
                    }
                });
                sessions.tick(n::monotonic_ms()); decoder.tick(n::monotonic_ms());
                while (auto payload=sessions.pop(id,n::monotonic_ms())) stream.write(p::frame(*payload,sessions.frame_bound(id)));
            }
            if (reason.empty()) reason=sessions.close_reason(id);
        } catch (const p::Error& e) { reason=e.what(); }
          catch (const n::IpcError& e) { reason=e.what(); }
        sessions.disconnect(id); emit({{"event","closed"},{"reason",reason},{"demand",sessions.demand_count()},{"elapsed_ms",n::monotonic_ms()-started}});
    }
}
}
int main(int argc,char** argv) {
    try {
        if (argc!=6) return 2;
        need(n::unprivileged_context(),"probe.privileged_context");
        const auto expected=p::decimal(argv[4]); need(expected.has_value(),"probe.pid");
        const std::string role=argv[1],scenario=argv[3];
        need(scenario=="journey" || scenario=="overflow" || scenario=="revoke" || scenario=="expiry" || scenario=="wrong-producer","probe.scenario");
        if (role=="server") server(argv[2],scenario,*expected,argv[5]);
        else if (role=="client") client(argv[2],scenario,*expected); else return 2;
        return 0;
    } catch (const std::exception& e) { emit({{"event","error"},{"code",e.what()}}); return 3; }
}
