// Included in the model fixture namespace; exact outcomes come from SP-W07-CONTINUOUS-REPLAY.
Publication reported(std::uint64_t sequence,std::uint64_t generation=0,std::uint64_t number=10) {
    if(!generation)generation=sequence;
    auto next=sample(generation,number);next.captured_at=UtcTime{1791158400,0};next.reported_document="document:"+std::to_string(generation);
    next.reported_version="0.2.0";next.clock_id="clock:1";next.clock_scope="scope:1";
    auto& observation=next.observations[0];observation.generation=generation;observation.measured_at=Tick{"E1",generation,"clock:1","scope:1"};
    return {"sample:"+std::to_string(sequence),{},std::move(next),"original-body:"+std::to_string(sequence)};
}
Store window_store(Limits limits={}) {return Store("P","E1",{{"throughput","B/s",ValueKind::uint64}},limits,ReplayPolicy::monotonic_window);}
void replay01() {
    auto s=window_store();
    for(std::uint64_t i=1;i<=4097;++i)CHECK(s.import_state(reported(i)).code==Code::accepted);
    CHECK(s.snapshot()->epoch=="E1"&&s.snapshot()->generation==4097&&value(s.snapshot())==10);
    CHECK(s.import_state(reported(4097)).code==Code::duplicate);
    CHECK(s.import_state(reported(3970)).code==Code::duplicate);
    CHECK(s.import_state(reported(3969)).code==Code::replay_expired);
    auto altered=reported(4097);altered.replay_bytes="altered";CHECK(s.import_state(altered).code==Code::conflict);
    CHECK(s.snapshot()->generation==4097);
}
void replay02() {
    Limits limits;limits.replay_records=3;auto s=window_store(limits);
    for(const auto i:{10ULL,20ULL,30ULL,40ULL})CHECK(s.import_state(reported(i)).code==Code::accepted);
    CHECK(s.import_state(reported(10)).code==Code::replay_expired);
    CHECK(s.import_state(reported(15)).code==Code::record_order);
    CHECK(s.import_state(reported(20)).code==Code::duplicate);
    auto bad=reported(50);bad.next.observations[0].unit="bad";CHECK(s.import_state(bad).code==Code::invalid_observation);
    CHECK(s.import_state(reported(20)).code==Code::duplicate);
    CHECK(s.import_state(reported(45)).code==Code::accepted);
    CHECK(s.import_state(reported(20)).code==Code::replay_expired);
}
void replay03() {
    auto s=window_store();auto first=reported(10,7);CHECK(s.import_state(first).code==Code::accepted);
    auto confirmation=reported(11,7);CHECK(s.import_state(confirmation).code==Code::accepted);
    auto altered=reported(12,7,11);CHECK(s.import_state(altered).code==Code::conflict);
    CHECK(s.import_state(reported(12,8)).code==Code::accepted);
    auto delta=reported(13,9);delta.expected_base=8;CHECK(s.import_state(delta).code==Code::invalid_mode);
    CHECK(s.publish(reported(13,9)).code==Code::invalid_mode);
    CHECK(s.import_state(reported(13,9)).code==Code::accepted);
}
void replay04() {
    Limits limits;limits.replay_records=2;auto s=window_store(limits);
    CHECK(s.import_state(reported(1)).code==Code::accepted);
    auto absent=reported(2);absent.next.observations.clear();CHECK(s.import_state(absent).code==Code::accepted);
    auto regressed=reported(3);regressed.next.observations[0].measured_at->nanoseconds=0;
    CHECK(s.import_state(regressed).code==Code::invalid_observation);
    CHECK(s.import_state(reported(3)).code==Code::accepted);
    auto gone=reported(4);gone.next.entities.clear();gone.next.observations.clear();CHECK(s.import_state(gone).code==Code::accepted);
    CHECK(s.import_state(reported(5)).code==Code::retired_identity);
    CHECK(s.retired_observations("A1").size()==1&&s.retired_observations("A1")[0].presence==Presence::absent);
    CHECK(s.import_state(reported(3)).code==Code::duplicate);
}
void replay05() {
    Limits limits;limits.retained_bytes=16384;limits.candidate_bytes=8192;auto s=window_store(limits);
    Publication last;
    for(std::uint64_t i=1;i<=100;++i){auto p=reported(i);p.replay_bytes=std::string(3000,'b');CHECK(s.import_state(p).code==Code::accepted);last=std::move(p);}
    auto old=reported(1);old.replay_bytes=std::string(3000,'b');CHECK(s.import_state(old).code==Code::replay_expired);
    auto oversized=reported(101);oversized.replay_bytes=std::string(8192,'x');CHECK(s.import_state(oversized).code==Code::capacity);
    CHECK(s.import_state(last).code==Code::duplicate&&s.snapshot()->generation==100);
    CHECK(s.import_state(reported(101)).code==Code::accepted);
}
void replay06() {
    auto s=window_store();
    for(const char* id:{"other:1","sample:0","sample:01","sample:+1","sample:18446744073709551616"}){auto p=reported(1);p.record_id=id;CHECK(s.import_state(p).code==Code::invalid_identity);}
    const auto maximum=std::numeric_limits<std::uint64_t>::max();CHECK(s.import_state(reported(maximum)).code==Code::accepted);
    CHECK(s.import_state(reported(maximum)).code==Code::duplicate);
    CHECK(s.import_state(reported(1)).code==Code::record_order);
    CHECK(s.snapshot()->generation==maximum);
}
