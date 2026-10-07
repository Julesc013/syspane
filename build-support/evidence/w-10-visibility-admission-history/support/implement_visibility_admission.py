from pathlib import Path
r=Path.cwd()
def edit(n,a,b):
 p=r/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
edit('build-support/generate_authored_schemas.py',"'scene-v0.4',","'scene-v0.4','scene-v0.5',")
edit('build-support/generate_authored_schemas.py',"'command-v0.6',","'command-v0.6','command-v0.7',")
edit('CMakeLists.txt','scene-v0.4','scene-v0.4 scene-v0.5')
edit('CMakeLists.txt','command-v0.6','command-v0.6 command-v0.7')
n='source/configuration/authored.cpp'
edit(n,'scene_v0_4_schema,','scene_v0_4_schema,scene_v0_5_schema,')
edit(n,'command_v0_6_schema,','command_v0_6_schema,command_v0_7_schema,')
edit(n,'if(scene["schema_version"]!="0.2.0")content_semantics(widget);','if(scene["schema_version"]!="0.2.0")content_semantics(widget);\n        if(widget.contains("visibility"))validate_visibility_document(widget["visibility"]);')
edit(n,'version=="0.4.0"?"0.4.0/scene":','version=="0.5.0"?"0.5.0/scene":version=="0.4.0"?"0.4.0/scene":')
edit(n,'version=="0.6.0"?"0.6.0/command":','version=="0.7.0"?"0.7.0/command":version=="0.6.0"?"0.6.0/command":')
edit(n,'version=="0.5.0"||version=="0.6.0"','version=="0.5.0"||version=="0.6.0"||version=="0.7.0"')
edit(n,'value.value("schema_version",Json())=="0.6.0"','value.value("schema_version",Json())=="0.6.0"||value.value("schema_version",Json())=="0.7.0"')
edit(n,'if(command.contains("content"))require','if(command.value("schema_version",Json())=="0.7.0")require(!policy.denied_capabilities.count("configuration.visibility"),"policy.denied");\n    if(command.contains("content"))require')
for n,expr in [('source/protocol/wire.cpp','root["body"].value("schema_version",Json())'),('source/platform/generation_store_linux.cpp','command["schema_version"]'),('source/platform/generation_store_linux.cpp','c::parse_command(next.identity->body)["schema_version"]')]:
 edit(n,expr+'=="0.6.0"',expr+'=="0.6.0"||'+expr+'=="0.7.0"')
for n in ['source/configuration/transaction.cpp','source/configuration/async_commands.cpp']:
 p=r/n;s=p.read_text();import re
 s,count=re.subn(r'(\w+\["schema_version"\])=="0.6.0"',r'\1=="0.6.0"||\1=="0.7.0"',s);assert count,(n,s)
 p.write_text(s,encoding='utf-8',newline='\n')
edit('source/configuration/command_service.hpp','virtual bool supports_edit_locks()const{return false;}','virtual bool supports_edit_locks()const{return false;}\n    virtual bool supports_visibility()const{return false;}')
edit('source/configuration/transaction.hpp','bool supports_edit_locks()const','bool supports_visibility()const{return supports_edit_locks()&&resource_provider_.capabilities.count("scene.visibility");}\n    bool supports_edit_locks()const')
edit('source/configuration/async_commands.hpp','bool supports_edit_locks()const','bool supports_visibility()const override{return transactions_.supports_visibility();}\n    bool supports_edit_locks()const')
n='source/configuration/content.cpp'
edit(n,'candidate.scene["schema_version"]=="0.4.0"','(candidate.scene["schema_version"]=="0.4.0"||candidate.scene["schema_version"]=="0.5.0")')
edit(n,'result->required_.insert("scene.edit-locks");','result->required_.insert("scene.edit-locks");\n    if(candidate.scene["schema_version"]=="0.5.0")result->required_.insert("scene.visibility");')
edit(n,'need(resources.required().count("scene.edit-locks")!=0,"resource.contract");','need(resources.required().count("scene.edit-locks")!=0,"resource.contract");\n    if(candidate.scene["schema_version"]=="0.5.0")need(resources.required().count("scene.visibility")!=0,"resource.contract");')
edit(n,'if(scene["schema_version"]=="0.4.0")','if(scene["schema_version"]=="0.5.0"){need(capabilities.count("configuration.visibility")&&capabilities.count("configuration.edit-locks")&&capabilities.count("configuration.large-commands"),"resource.capability");result.command["schema_version"]="0.7.0";}\n    if(scene["schema_version"]=="0.4.0")')
n='source/configuration/session.cpp'
edit(n,'bool locks=false)','bool locks=false,bool visibility=false)')
edit(n,'if (source) {','if(visibility&&locks&&resources&&large){hello.documents.insert({"command","0.7.0"});hello.optional.insert("configuration.visibility");}\n    if (source) {')
edit(n,'commands_&&commands_->supports_edit_locks())','commands_&&commands_->supports_edit_locks(),commands_&&commands_->supports_visibility())')
edit(n,'c.selection.documents.count({"command", "0.6.0"})','c.selection.documents.count({"command", "0.6.0"})||c.selection.documents.count({"command", "0.7.0"})')
edit(n,'!c.selection.documents.count({"command","0.6.0"})','(!c.selection.documents.count({"command","0.6.0"})&&!c.selection.documents.count({"command","0.7.0"}))')
edit(n,'const auto version = source_ ?','if(!c.selection.documents.count({"command","0.7.0"})||!c.selection.features.count("configuration.edit-locks")){\n            if(client.required.count("configuration.visibility"))throw Error("handshake.visibility");\n            c.selection.features.erase("configuration.visibility");\n        }\n        const auto version = source_ ?')
edit(n,'message.body.value("schema_version",Json())!="0.6.0"','message.body.value("schema_version",Json())!="0.6.0"&&message.body.value("schema_version",Json())!="0.7.0"')
edit(n,'if(body.value("schema_version",Json())=="0.6.0"&&!','if((body.value("schema_version",Json())=="0.6.0"||body.value("schema_version",Json())=="0.7.0")&&!')
edit(n,'if(body.value("schema_version",Json())=="0.5.0"||body.value("schema_version",Json())=="0.6.0"){','if(body.value("schema_version",Json())=="0.7.0"&&!c.selection.features.count("configuration.visibility")){queue(c,"result",result({"invalid","feature.unsupported"},request,epoch_,revision_));return;}\n        if(body.value("schema_version",Json())=="0.5.0"||body.value("schema_version",Json())=="0.6.0"||body.value("schema_version",Json())=="0.7.0"){')
edit(n,'op["scene"].value("schema_version",Json())=="0.4.0"','op["scene"].value("schema_version",Json())=="0.4.0"||op["scene"].value("schema_version",Json())=="0.5.0"')
n='source/interfaces/editor_draft.hpp'
edit(n,'struct SetWidgetLocks','struct SetWidgetVisibility {std::vector<std::string> ids;std::optional<Json> rule;};\nstruct SetWidgetLocks')
edit(n,'UnwrapWidget,SetWidgetLocks>','UnwrapWidget,SetWidgetLocks,SetWidgetVisibility>')
edit(n,'bool locks_available()const;','bool locks_available()const;\n    bool visibility_available()const;')
n='source/interfaces/editor_draft.cpp'
edit(n,'need(group.at("kind")=="group","editor.group");','need(group.at("kind")=="group","editor.group");need(!group.contains("visibility"),"editor.visibility_container");')
edit(n,'if(edit.locked)scene["schema_version"]="0.4.0";','if(edit.locked&&scene["schema_version"]=="0.3.0")scene["schema_version"]="0.4.0";')
edit(n,'template<class T>std::vector<std::string> targets','void apply(Json& scene,const SetWidgetVisibility& edit){\n    need(scene.at("schema_version")!="0.2.0","editor.visibility_version");need(!edit.ids.empty()&&edit.ids.size()<=256,"editor.targets");std::set<std::string> ids;\n    for(const auto& id:edit.ids){need(ids.insert(id).second,"editor.targets");(void)widget(scene,id);}\n    if(edit.rule){c::validate_visibility_document(*edit.rule);scene["schema_version"]="0.5.0";}\n    for(const auto& id:edit.ids){auto& w=widget(scene,id);if(edit.rule)w["visibility"]=*edit.rule;else w.erase("visibility");}\n}\n\ntemplate<class T>std::vector<std::string> targets')
edit(n,'void EditorDraft::select','bool EditorDraft::visibility_available()const{\n    return locks_available()&&transaction_.context_->capabilities.count("configuration.visibility")&&\n        transaction_.context_->capabilities.count("scene.visibility")&&!transaction_.policy_.denied_capabilities.count("configuration.visibility");\n}\nvoid EditorDraft::select')
edit(n,'if(std::holds_alternative<SetWidgetLocks>(edit))','if(std::holds_alternative<SetWidgetVisibility>(edit))need(visibility_available(),"editor.visibility_unavailable");if(std::holds_alternative<SetWidgetLocks>(edit))')
n='source/interfaces/settings_draft.cpp'
edit(n,'if(scene_changed&&draft_->scene["schema_version"]=="0.4.0")','if(scene_changed&&draft_->scene["schema_version"]=="0.5.0"){need(large_commands_&&context_&&context_->capabilities.count("configuration.visibility")&&context_->capabilities.count("configuration.edit-locks"),"settings.visibility");result["schema_version"]="0.7.0";}\n    if(scene_changed&&draft_->scene["schema_version"]=="0.4.0")')
edit(n,'{"schema_version",context_?"0.4.0":"0.2.0"}','{"schema_version",scene["schema_version"]=="0.5.0"?"0.7.0":context_?"0.4.0":"0.2.0"}')
edit('source/rendering/scene_surface.cpp','c::authorize_resources(*config.resources,policy,config.capabilities);','c::authorize_resources(*config.resources,policy,config.capabilities);\n        need(config.authored.scene["schema_version"]!="0.5.0","surface.visibility_unavailable");')
n='spec/tools/specctl.py'
edit(n,'"command-v0.6"','"command-v0.6", "command-v0.7"')
edit(n,'"scene-v0.4"','"scene-v0.4", "scene-v0.5"')
print('Visibility admission production integration applied.')
