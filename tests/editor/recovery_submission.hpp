// Literal submission behavior, frozen before recovery hint preparation changes.
void recovery_submission(const settings_fixture::Fixture& f,const Json& cases,const ui::RecoveryIdentity& id){
    const auto make=[&](const c::Policy& p){return ui::EditorDraft(authority(),p,f.authored,"E1",admitted(f),true);};
    for(bool prepared:{false,true}){
        const auto restore=[&](ui::EditorDraft& d,const std::string& bytes){
            return prepared?d.restore_recovery(d.recovery_restore_work(bytes,id)->run(),id):d.restore_recovery(bytes,id);
        };
        const auto bytes=cases.at("wire").get<std::string>();
        auto d=make(grant());d.select({"widget:text"});
        CHECK(restore(d,bytes)&&*d.scene()==cases["scene"]&&d.selection().empty());
        CHECK(d.undo_count()==1&&d.redo_count()==0&&!d.active_request());
        for(unsigned n=0;n<3;++n)CHECK(d.may_submit("preview")&&d.may_submit("commit")&&!d.may_submit("invalid"));
        CHECK(d.undo()&&*d.scene()==f.authored.scene&&d.selection()==std::vector<std::string>{"widget:text"});
        CHECK(!d.may_submit("preview")&&!d.may_submit("commit"));
        CHECK(d.redo()&&*d.scene()==cases["scene"]&&d.may_submit("commit"));
        auto q=*d.begin("preview","recovery:preview");auto expected=cases["command"];
        expected["request_id"]="recovery:preview";CHECK(c::parse_command(q.body)==expected);
        CHECK(q.ticket==1&&q.epoch=="E1"&&!d.may_submit("preview")&&!d.may_submit("commit"));
        CHECK(d.complete(q.ticket,c::result({"preview",""},"recovery:preview","E1",40))&&d.may_submit("commit"));
        q=*d.begin("commit","recovery:commit");expected["request_id"]="recovery:commit";expected["intent"]="commit";
        CHECK(q.ticket==2&&c::parse_command(q.body)==expected);
        Store store(f);c::Transactions tx(store,"E1",store.provider());
        auto accepted=tx.submit("p","C",q.body,authority(),[]{return grant();},0);
        CHECK(accepted["outcome"]=="accepted"&&d.complete(q.ticket,accepted)&&d.revision()==41&&store.writes==1);
        auto saved=cases["scene"];saved["revision"]="41";CHECK(store.current.documents.scene==saved&&!d.may_submit("commit"));
        auto clean=make(grant());clean.select({"widget:text"});auto noop=cases["command"];noop["operations"][0]["scene"]=f.authored.scene;
        CHECK(!restore(clean,wrap(cases,noop))&&!clean.dirty()&&clean.undo_count()==0&&clean.selection()==std::vector<std::string>{"widget:text"});
        CHECK(!clean.may_submit("preview")&&!clean.may_submit("commit"));
        auto denied=grant();denied.denied_capabilities.insert("settings.commit");auto local=make(denied);
        CHECK(restore(local,bytes)&&local.may_submit("preview")&&!local.may_submit("commit"));
        rejects([&]{local.begin("commit","denied:commit");},"policy.denied");CHECK(!local.active_request());
        local.policy(grant(8));CHECK(local.may_submit("commit"));
        auto revoked=grant(9);revoked.denied_capabilities.insert("settings.commit");local.policy(revoked);
        CHECK(local.may_submit("preview")&&!local.may_submit("commit"));local.policy(grant(10));CHECK(local.may_submit("commit"));
        local.reload(f.authored,"E2",admitted(f));CHECK(!local.may_submit("preview")&&!local.may_submit("commit"));
        for(const char* name:{"first","second"}){
            auto themed=make(grant());CHECK(restore(themed,wrap(cases,cases["theme_commands"][name])));
            CHECK(*themed.scene()==cases["theme_scenes"][name]&&themed.resources()->selection()==cases["theme_selections"][name]);
            CHECK(themed.may_submit("preview")&&themed.may_submit("commit"));
            auto command=*themed.begin("commit","recovery:theme");auto expected_theme=cases["theme_commands"][name];
            expected_theme["request_id"]="recovery:theme";expected_theme["intent"]="commit";CHECK(c::parse_command(command.body)==expected_theme);
        }
    }
}
