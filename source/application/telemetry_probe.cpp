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
void clock_event(n::Stream& stream,const char* phase) {
    const auto clock=stream.measurement_clock();
    emit({{"event","clock"},{"phase",phase},{"clock_id",clock.clock_id},
        {"nanoseconds",std::to_string(clock.nanoseconds)},{"representation_unit_ns",clock.representation_unit_ns}});
}
bool clock_scenario(const std::string& scenario) { return scenario=="clock-roundtrip" || scenario=="clock-peer-exit"; }
bool measured_scenario(const std::string& scenario) { return scenario=="measured-fresh" || scenario=="measured-delayed" || scenario=="measured-future"; }
void observe_clock_exit(n::Stream& stream) {
    const auto started=n::monotonic_ms();
    for (;;) {
        need(n::monotonic_ms()-started<2000,"probe.clock_exit_timeout");
        try { stream.measurement_clock(); }
        catch (const n::IpcError& error) {
            need(std::string(error.what())=="clock.peer_exited","probe.clock_exit");
            emit({{"event","clock_rejected"},{"code",error.what()},{"peer_pid",stream.peer().process_id}});
            try { stream.measurement_clock(); throw p::Error("probe.clock_not_latched"); }
            catch (const n::IpcError& second) {
                need(std::string(second.what())=="clock.unavailable","probe.clock_latch");
                emit({{"event","clock_rejected"},{"code",second.what()},{"peer_pid",stream.peer().process_id}});
            }
            return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}
c::Policy policy(std::uint64_t revision=7) {
    c::Policy value; value.available=true; value.revision=revision;
    value.disclosure[{"desktop","desktop"}]={"operational"}; value.disclosure[{"desktop","accessibility"}]={"operational"}; return value;
}
Json hello(const std::string& version="0.1.0") {
    Json result{{"type","hello"},{"body",{{"wire_major",0},{"wire_minor",1},{"role","desktop"},{"producer_epoch","probe:client"},
    {"max_frame_bytes",p::frame_limit},{"document_versions",Json::array({{{"document","telemetry"},{"version",version}},
    {{"document","snapshot"},{"version",version}},{{"document","observation"},{"version",version}}})},
    {"required_features",{"telemetry.snapshot"}},{"optional_features",Json::array()}}}};
    if (version=="0.2.0") result["body"]["required_features"].push_back("telemetry.measured-time");
    return result;
}
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
    explicit Client(n::Stream stream,bool clock=false,bool measured=false):stream_(std::move(stream)),version_(measured?"0.2.0":"0.1.0") {
        emit({{"event","authenticated"},{"peer_pid",stream_.peer().process_id},{"user_session_verified",true}});
        if (clock) clock_event(stream_,"before");
        if (measured) local_clock_=stream_.measurement_clock();
        auto bytes=p::frame(hello(version_).dump()); stream_.write(std::string_view(bytes).substr(0,1));
        std::this_thread::sleep_for(std::chrono::milliseconds(20)); stream_.write(std::string_view(bytes).substr(1));
        auto welcome=p::decode(next()); need(welcome.type=="welcome","probe.welcome");
        if (clock) clock_event(stream_,"after");
        selected_=p::negotiate(p::handshake(hello(version_)["body"]),p::handshake(welcome.body),{"console"});
        id_=welcome.connection_id; epoch_=welcome.producer_epoch; decoder_.restrict_limit(selected_.max_frame_bytes);
    }
    p::TelemetryBinding binding() const { return {selected_,id_,epoch_,"producer:1","S","desktop","operational",7,p::TelemetryDirection::producer_to_consumer,
        version_,local_clock_?local_clock_->clock_id:"",local_clock_?local_clock_->local_scope:""}; }
    syspane::model::Tick tick() { const auto clock=stream_.measurement_clock(); return {epoch_,clock.nanoseconds,clock.clock_id,clock.local_scope}; }
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
    void subscribe(bool wrong=false) {
        Json body{{"schema_version",version_},{"subscription_id","S"},{"producer_id",wrong?"wrong":"producer:1"},
            {"policy_revision","7"},{"channel","desktop"},{"classification","operational"}};
        if (local_clock_) body["clock_id"]=local_clock_->clock_id;
        send("subscribe",std::move(body));
    }
    void beat(unsigned seq) { send("heartbeat",{{"sequence",std::to_string(seq)}}); }
private:
    n::Stream stream_; p::Framer decoder_; std::deque<std::string> pending_;
    p::Negotiated selected_{}; std::string id_,epoch_;
    std::string version_;
    std::optional<n::MeasurementClock> local_clock_;
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
        const bool measured=measured_scenario(scenario);
        Client client(n::Stream::connect(endpoint,expected),clock_scenario(scenario),measured);
        const auto attached=view.attach_wire(client.binding(),n::monotonic_ms()); need(attached.code==r::DataCode::accepted,"probe.attach");
        client.subscribe(scenario=="wrong-producer");
        if (scenario=="measured-future") {
            const auto bytes=client.next();
            need(view.receive(attached.token,7,bytes,n::monotonic_ms(),client.tick()).code==r::DataCode::invalid,"probe.future_rejection");
            const auto status=view.status(n::monotonic_ms());
            need(!status.payload_available && !status.alive,"probe.future_state");
            emit({{"event","measurement_rejected"},{"payload",status.payload_available},{"alive",status.alive}});
            client.send("shutdown",{{"reason","normal"}}); return;
        }
        const auto receive=[&] {
            const auto bytes=client.next();
            const auto tick=measured?std::optional<syspane::model::Tick>(client.tick()):std::nullopt;
            const auto result=view.receive(attached.token,7,bytes,n::monotonic_ms(),tick);
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
        if (measured) {
            const auto ttl=scenario=="measured-delayed"?100000000ULL:1000000000ULL;
            need(view.project_measured(n::monotonic_ms(),client.tick(),[&](const auto& snapshot,const auto& lease,const auto& now) {
                const auto& observation=snapshot.observations.at(0); need(observation.measured_at.has_value(),"probe.measurement_missing");
                const auto freshness=syspane::model::freshness_at(observation,now,ttl);
                need(lease.presentation==r::Presentation::active,"probe.measurement_lease");
                emit({{"event","measurement"},{"clock_id",now.clock_id},{"scope",now.clock_scope},
                    {"stamp",std::to_string(observation.measured_at->nanoseconds)},{"now",std::to_string(now.nanoseconds)},
                    {"ttl",std::to_string(ttl)},{"current",freshness==syspane::model::Freshness::current}});
            }),"probe.measurement_projection");
        }
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
    std::optional<c::Sessions> owner;
    std::uint64_t generation=1,record=0;
    for (unsigned ordinal=0;ordinal<(scenario=="journey"?2U:1U);++ordinal) {
        auto stream=listener.accept(expected); emit({{"event","authenticated"},{"peer_pid",stream.peer().process_id},{"user_session_verified",true}});
        if (!owner) {
            c::TelemetrySource source{"producer:1","desktop","operational"};
            if (measured_scenario(scenario)) {
                const auto clock=stream.measurement_clock(); source.document_version="0.2.0";
                source.clock_id=clock.clock_id; source.clock_scope=clock.local_scope;
            }
            owner.emplace("fixture:epoch-1",0,policy(),std::move(source));
        }
        auto& sessions=*owner;
        const auto id="C"+std::to_string(ordinal); sessions.open(id,stream.peer().principal,{true,"desktop",{"desktop"}},stream.connected_ms());
        p::Framer decoder; std::array<char,4096> buffer{}; std::uint64_t offered=0; bool advanced=false,overflowed=false; std::string reason;
        const auto started=n::monotonic_ms();
        try {
            while (!sessions.closed(id)) {
                need(n::monotonic_ms()-started<12000,"probe.deadline");
                const auto read=stream.read(buffer.data(),buffer.size());
                if (read.eof) { decoder.eof(); reason="peer.eof"; break; }
                if (read.bytes) decoder.feed(std::string_view(buffer.data(),read.bytes),read.observed_ms,[&](auto payload) {
                    const auto message=p::decode(payload);
                    if (clock_scenario(scenario) && message.type=="hello") clock_event(stream,"middle");
                    sessions.receive(id,payload,n::monotonic_ms()); decoder.restrict_limit(sessions.frame_bound(id));
                    const auto sub=sessions.subscription(id); if (!sub) return;
                    const auto offer=[&](std::optional<std::uint64_t> base) {
                        auto snapshot=state(fixture,generation);
                        if (measured_scenario(scenario)) {
                            const auto clock=stream.measurement_clock();
                            const auto stamp=clock.nanoseconds+(scenario=="measured-future"?60000000000ULL:0);
                            snapshot["schema_version"]="0.2.0";
                            for (auto& observation : snapshot["observations"]) {
                                observation["schema_version"]="0.2.0";
                                observation["measured_at"]={{"clock_id",clock.clock_id},{"nanoseconds",std::to_string(stamp)}};
                            }
                            emit({{"event","producer_measurement"},{"clock_id",clock.clock_id},{"stamp",std::to_string(stamp)},
                                {"sampled",std::to_string(clock.nanoseconds)}});
                            if (scenario=="measured-delayed") std::this_thread::sleep_for(std::chrono::milliseconds(200));
                        }
                        return sessions.offer(id,sub->ticket,"native:"+std::to_string(++record),snapshot,base,n::monotonic_ms());
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
        if (scenario=="clock-peer-exit") observe_clock_exit(stream);
    }
}
}
int main(int argc,char** argv) {
    try {
        if (argc!=6) return 2;
        need(n::unprivileged_context(),"probe.privileged_context");
        const auto expected=p::decimal(argv[4]); need(expected.has_value(),"probe.pid");
        const std::string role=argv[1],scenario=argv[3];
        need(scenario=="journey" || scenario=="overflow" || scenario=="revoke" || scenario=="expiry" || scenario=="wrong-producer" || clock_scenario(scenario) || measured_scenario(scenario),"probe.scenario");
        if (role=="server") server(argv[2],scenario,*expected,argv[5]);
        else if (role=="client") client(argv[2],scenario,*expected); else return 2;
        return 0;
    } catch (const std::exception& e) { emit({{"event","error"},{"code",e.what()}}); return 3; }
}
