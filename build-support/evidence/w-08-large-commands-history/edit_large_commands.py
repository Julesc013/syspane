from pathlib import Path
r=Path(__file__).resolve().parents[2]
def edit(name,pairs):
    p=r/name;s=p.read_text(encoding='utf-8')
    for old,new in pairs:
        assert old in s,(name,old);s=s.replace(old,new)
    p.write_text(s,encoding='utf-8',newline='\n')
edit('build-support/generate_authored_schemas.py',[("'command-v0.4',","'command-v0.4','command-v0.5',"),("'items','minimum'","'items','contains','minimum'"),("'not','items','propertyNames'","'not','items','contains','propertyNames'")])
edit('CMakeLists.txt',[('command-v0.4 command-result','command-v0.4 command-v0.5 command-result')])
for f in ['spec/tools/specctl.py','spec/tools/tests/test_specctl.py']:
    edit(f,[("'command-v0.4')","'command-v0.4','command-v0.5')")])
edit('source/configuration/transaction.cpp',[
    ('id.body.size()<=16384','id.body.size()<=protocol::large_command_limit'),
    ('protocol::parse(id.body)','parse_command(id.body)'),
    ('    require(!body.empty()&&body.size()<=16384,"command.size");\n',''),
    ('protocol::parse(body)','parse_command(body)'),
    ('ledger_.admit(principal,connection,request,body,now)','ledger_.admit(principal,connection,request,body,now,command["schema_version"]=="0.5.0")'),
    ('protocol::parse(record->identity->body)','parse_command(record->identity->body)')])
edit('source/configuration/async_commands.cpp',[
    ('auto command=protocol::parse(body);validate_command(command)','auto command=parse_command(body);validate_command(command)'),
    ('const auto command=protocol::parse(body);','const auto command=protocol::parse(body,protocol::ParseProfile::large_command);'),
    ('    if(body.size()>16384)return {0,reply(request,"invalid","command.size")};\n    try{validate_command(command);}',
     '    try{(void)parse_command(body);validate_command(command);}'),
    ('ledger_.admit(principal,connection,request,job->body,now)','ledger_.admit(principal,connection,request,job->body,now,command["schema_version"]=="0.5.0")'),
    ('authorize_authored(protocol::parse(job->body)','authorize_authored(parse_command(job->body)')])
edit('source/configuration/session.cpp',[
    ('bool commands=false,bool resources=false)','bool commands=false,bool resources=false,bool large=false)'),
    ('    if (source) {','    if(large){hello.documents.insert({"command","0.5.0"});hello.optional.insert("configuration.large-commands");}\n    if (source) {'),
    ('protocol::decode(payload)','protocol::decode(payload,c.negotiated&&c.selection.features.count("configuration.large-commands"))'),
    ('commands_&&commands_->supports_resources())','commands_&&commands_->supports_resources(),commands_&&commands_->supports_large_commands())'),
    ('c.selection.documents.count({"command", "0.4.0"}))','c.selection.documents.count({"command", "0.4.0"})||c.selection.documents.count({"command", "0.5.0"}))'),
    ('!c.selection.documents.count({"command","0.4.0"}))','!c.selection.documents.count({"command","0.4.0"})&&!c.selection.documents.count({"command","0.5.0"}))'),
    ('if(!c.selection.documents.count({"command","0.4.0"})||','if((!c.selection.documents.count({"command","0.4.0"})&&!c.selection.documents.count({"command","0.5.0"}))||'),
    ('        const auto version = source_ ? source_->document_version : "0.1.0";',
     '        if(!c.selection.documents.count({"command","0.5.0"})||!c.selection.documents.count({"command-result","0.1.0"})||\n           !c.selection.features.count("configuration.transactions")||c.selection.max_frame_bytes<protocol::large_command_frame_floor){\n            if(client.required.count("configuration.large-commands"))throw Error("handshake.large_commands");\n            c.selection.features.erase("configuration.large-commands");\n        }\n        const auto version = source_ ? source_->document_version : "0.1.0";'),
    ('        if(commands_){\n            // Even legacy',
     '        if(body.value("schema_version",Json())=="0.5.0"){\n            bool scene_content=false;if(body.contains("operations")&&body["operations"].is_array())for(const auto& op:body["operations"])\n                if(op.is_object()&&op.value("op",Json())=="scene.replace"&&op.contains("scene")&&op["scene"].is_object()&&op["scene"].value("schema_version",Json())=="0.3.0")scene_content=true;\n            if(!c.selection.features.count("configuration.large-commands")||\n               (body.contains("content")&&!c.selection.features.count("configuration.content"))||\n               (scene_content&&!c.selection.features.count("configuration.scene-content"))){\n                queue(c,"result",result({"invalid","feature.unsupported"},request,epoch_,revision_));return;\n            }\n        }\n        if(commands_){\n            // Even legacy')])
for name in ['settings_draft','editor_draft']:
    edit('source/interfaces/'+name+'.hpp',[('std::optional<SettingsResources> resources={});','std::optional<SettingsResources> resources={},bool large_commands=false);')])
edit('source/interfaces/settings_draft.hpp',[('bool requires_resources_=false;','bool requires_resources_=false,large_commands_=false;')])
edit('source/interfaces/settings_draft.cpp',[
    ('std::optional<SettingsResources> resources):authority_','std::optional<SettingsResources> resources,bool large_commands):authority_'),
    ('policy_(std::move(policy)){','policy_(std::move(policy)),large_commands_(large_commands){'),
    ('{"schema_version",context_?(scene_changed','{"schema_version",large_commands_?"0.5.0":context_?(scene_changed')])
edit('source/interfaces/editor_draft.cpp',[
    ('std::optional<SettingsResources> resources)\n','std::optional<SettingsResources> resources,bool large_commands)\n'),
    ('std::move(epoch),std::move(resources)){}','std::move(epoch),std::move(resources),large_commands){}')])
edit('source/interfaces/editor_form.hpp',[('std::string image_worker,Actions);','std::string image_worker,Actions,bool large_commands=false);')])
edit('source/interfaces/editor_form_linux.cpp',[
    ('std::string w,Actions callbacks)','std::string w,Actions callbacks,bool large_commands)'),
    (':draft(a,p,value,std::move(epoch),r)',':draft(a,p,value,std::move(epoch),r,large_commands)'),
    ('std::string worker,Actions actions)','std::string worker,Actions actions,bool large_commands)'),
    ('std::move(worker),std::move(actions)))','std::move(worker),std::move(actions),large_commands))')])
edit('source/configuration/content.cpp',[
    ('    if(scene["schema_version"]=="0.3.0"){result.command',
     '    if(capabilities.count("configuration.large-commands")||scene["schema_version"]=="0.3.0"){result.command'),
    ('result.command["schema_version"]="0.4.0"','result.command["schema_version"]=capabilities.count("configuration.large-commands")?"0.5.0":"0.4.0"'),
    ('if(scene["schema_version"]=="0.3.0")authorize_resources','if(result.command.contains("content"))authorize_resources')])
edit('source/application/configuration_probe.cpp',[
    ('std::string read(const char* path)','std::string read(const char* path,std::size_t maximum=262144)'),
    ('value.size()>262144','value.size()>maximum'),
    ('"fixture:connection",read(argv[3])','"fixture:connection",read(argv[3],syspane::protocol::large_command_limit)')])
print('Updated shared parsing, negotiation, command ownership and opt-in draft paths.')
