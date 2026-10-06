#include "health_link.hpp"
#include <iostream>
#include <stdexcept>

namespace r = syspane::recovery;
namespace w = syspane::protocol;
void check(bool value) { if (!value) throw std::runtime_error("health assertion"); }
template<class Call> void rejects(Call call, const std::string& code) {
    try { call(); } catch (const w::Error& error) { check(error.what() == code); return; }
    throw std::runtime_error("missing health rejection");
}
struct Pair {
    r::HealthLink client{false, "desktop", "client:1", "", 100};
    r::HealthLink server{true, "desktop", "server:1", "H", 100};
    Pair() {
        const auto hello = client.take_output();
        check(server.feed(hello.substr(0, 3), 101).empty());
        const auto ready = server.feed(hello.substr(3), 102);
        check(ready.size() == 1 && ready[0].kind == r::HealthKind::ready);
        const auto welcome = client.feed(server.take_output(), 103);
        check(welcome.size() == 1 && welcome[0].kind == r::HealthKind::ready);
        check(client.connection() == "H" && client.epoch() == "server:1");
    }
};
int main(int argc, char** argv) {
    try {
        check(argc == 2); const std::string name = argv[1];
        if (name == "HEALTH-ASYNC-01") {
            Pair pair; pair.client.heartbeat(0);
            const auto beat = pair.server.feed(pair.client.take_output(), 104);
            check(beat.size() == 1 && beat[0].kind == r::HealthKind::heartbeat && beat[0].value == 0);
            pair.server.challenge(18446744073709551615ULL);
            const auto challenge = pair.client.feed(pair.server.take_output(), 105);
            check(challenge.size() == 1 && challenge[0].kind == r::HealthKind::challenge && challenge[0].value == 18446744073709551615ULL);
            pair.client.progress(challenge[0].value);
            const auto progress = pair.server.feed(pair.client.take_output(), 106);
            check(progress.size() == 1 && progress[0].kind == r::HealthKind::progress && progress[0].value == challenge[0].value);
            pair.client.shutdown();
            const auto stopped = pair.server.feed(pair.client.take_output(), 107);
            check(stopped.size() == 1 && stopped[0].kind == r::HealthKind::shutdown);
            rejects([&] { pair.server.heartbeat(1); }, "health.not_ready");
        } else if (name == "HEALTH-ASYNC-02") {
            r::HealthLink silent(false, "desktop", "client:1", "", 100);
            silent.tick(5099); rejects([&] { silent.tick(5100); }, "health.handshake_timeout");
            check(silent.take_output().empty()); rejects([&] { silent.tick(5101); }, "health.closed");
            Pair pair; pair.server.challenge(1); pair.client.feed(pair.server.take_output(), 104);
            rejects([&] { pair.client.progress(2); }, "health.progress_order");
            rejects([&] { pair.client.heartbeat(1); }, "health.not_ready");
            Pair pending; pending.server.feed(std::string("\0", 1), 200);
            pending.server.tick(5199); rejects([&] { pending.server.tick(5200); }, "frame.timeout");
        } else if (name == "HEALTH-ASYNC-03") {
            Pair pair;
            for (unsigned i = 0; i < 16; ++i) pair.client.heartbeat(i);
            rejects([&] { pair.client.heartbeat(16); }, "health.outbox_capacity"); check(pair.client.take_output().empty());
            Pair big; rejects([&] { big.server.feed(std::string(4097, 'x'), 104); }, "health.read_capacity");
            Pair events; events.client.heartbeat(1); const auto frame = events.client.take_output(); std::string many;
            for (unsigned i = 0; i < 17; ++i) many += frame;
            check(many.size() <= 4096); rejects([&] { events.server.feed(many, 104); }, "health.event_limit");
        } else if(name=="HEALTH-TRANSACTION"){
            r::HealthLink client(false,"console","C","",100,true),server(true,"console","E","G",100,true);
            check(server.feed(client.take_output(),101)[0].kind==r::HealthKind::ready);client.feed(server.take_output(),102);
            client.transaction_started(1);check(server.feed(client.take_output(),103)[0].kind==r::HealthKind::transaction_started);
            server.transaction_armed(1);check(client.feed(server.take_output(),104)[0].kind==r::HealthKind::transaction_armed);
            client.heartbeat(1);check(server.feed(client.take_output(),105)[0].kind==r::HealthKind::heartbeat);
            client.transaction_finished(1);check(server.feed(client.take_output(),106)[0].kind==r::HealthKind::transaction_finished);
            client.transaction_started(2);server.feed(client.take_output(),107);server.transaction_armed(2);client.feed(server.take_output(),108);
            rejects([&]{client.transaction_finished(1);},"health.transaction_order");check(client.take_output().empty());
        } else if(name=="HEALTH-TRANSACTION-REJECT"){
            for(unsigned mode=0;mode<5;++mode){
                r::HealthLink client(false,"console","C","",100,true),server(true,"console","E","G",100,true);
                server.feed(client.take_output(),101);client.feed(server.take_output(),102);
                if(mode==0)rejects([&]{client.transaction_finished(1);},"health.transaction_order");
                if(mode==1)rejects([&]{server.transaction_started(1);},"health.transaction_order");
                if(mode==2){client.transaction_started(1);rejects([&]{client.transaction_finished(1);},"health.transaction_order");}
                if(mode==3){client.transaction_started(1);server.feed(client.take_output(),103);server.transaction_armed(1);rejects([&]{server.transaction_armed(1);},"health.transaction_order");}
                if(mode==4){client.transaction_started(1);server.feed(client.take_output(),103);rejects([&]{server.transaction_armed(2);},"health.transaction_order");}
            }
            r::HealthLink plain(true,"console","E","G",100),required(false,"console","C","",100,true);
            rejects([&]{plain.feed(required.take_output(),101);},"handshake.required_feature");
            for(const auto& ticket:{"0","01","18446744073709551616"})rejects([&]{w::decode(w::Json{{"type","transaction.started"},{"body",{{"ticket",ticket}}},{"connection_id","G"},{"producer_epoch","E"}}.dump());},"body.invalid");
        } else return 2;
        std::cout << name << ": pass\n"; return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
