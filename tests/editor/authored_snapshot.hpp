#pragma once
// Included in the existing portable recovery-preparation fixture.
void authored_snapshot(const settings_fixture::Fixture& f,const Json& cases,const ui::RecoveryIdentity& id){
    auto fresh=[&]{return ui::EditorDraft(authority(),grant(),f.authored,"E1",admitted(f),true);};
    const auto bytes=cases["wire"].get<std::string>();auto d=fresh();
    CHECK(!d.authored_snapshot());auto work=d.recovery_restore_work(bytes,id);auto result=work->run();
    CHECK(!d.authored_snapshot()&&*d.scene()==f.authored.scene);
    CHECK(d.restore_recovery(std::move(result),id));auto held=d.authored_snapshot();CHECK(held);
    CHECK(held->documents().scene==cases["scene"]&&held->documents().settings==f.authored.settings);
    const auto* identity=&held->documents();d.select({});CHECK(&d.authored_snapshot()->documents()==identity);
    auto mutable_copy=held->documents();mutable_copy.scene["widgets"][0]["title"]="Caller mutation";
    CHECK(held->documents().scene==cases["scene"]);
    CHECK(d.execute({ui::WidgetPropertyEdit{d.scene()->at("widgets")[0]["id"],ui::WidgetProperty::title,"Edited"}}));
    CHECK(!d.authored_snapshot()&&held->documents().scene==cases["scene"]);
    CHECK(d.adopt_history(d.history_work(false)->run()));CHECK(d.authored_snapshot()->documents().scene==cases["scene"]);
    CHECK(d.adopt_history(d.history_work(false)->run()));CHECK(d.authored_snapshot()->documents().scene==f.authored.scene);
    d.policy(grant(8));CHECK(!d.authored_snapshot());
    CHECK(d.adopt_history(d.history_work(true)->run()));CHECK(d.authored_snapshot()->documents().scene==cases["scene"]);
    d.discard();CHECK(!d.authored_snapshot()&&*d.scene()==f.authored.scene);
    auto stale=d.recovery_restore_work(bytes,id)->run();d.policy(grant(9));
    rejects([&]{d.restore_recovery(std::move(stale),id);},"recovery.prepared_stale");CHECK(!d.authored_snapshot());
    CHECK(d.restore_recovery(d.recovery_restore_work(bytes,id)->run(),id));d.disconnected();CHECK(!d.authored_snapshot());
    d=fresh();CHECK(d.restore_recovery(d.recovery_restore_work(bytes,id)->run(),id));d.close();CHECK(!d.authored_snapshot());
    d=fresh();CHECK(d.restore_recovery(d.recovery_restore_work(bytes,id)->run(),id));d.policy({});CHECK(!d.authored_snapshot()&&!d.available());
}
