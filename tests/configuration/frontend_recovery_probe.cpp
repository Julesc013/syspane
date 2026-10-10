#include "frontend_linux.hpp"
#include "bundle_identity.hpp"
#include "editor_draft.hpp"
#include "scene_surface.hpp"
#include <chrono>
#include <iostream>
#include <thread>

namespace app=syspane::application;namespace c=syspane::configuration;namespace ui=syspane::interfaces;namespace os=syspane::platform;
using J=c::Json;
void need(bool ok){if(!ok)throw syspane::protocol::Error("probe.state");}
J context(const c::ProfileRecoveryView& v){const auto& a=v.admission;const auto& d=a.directory;
    return {{"connection",v.connection},{"epoch",v.epoch},{"session",v.editor_session},{"profile",a.profile},{"generation",a.generation},
        {"transfer",v.transfer},{"revision",v.revision},{"policy",a.policy_revision},{"erase",a.erase},
        {"directory",{{"path",d.path},{"uid",d.uid},{"state_device",d.state_device},{"state_inode",d.state_inode},{"recovery_device",d.recovery_device},{"recovery_inode",d.recovery_inode}}}};
}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    try{
        app::LinuxFrontendBackend backend(os::built_helper_bundle_expectation(),argv[1],os::profile_environment("profile:default"));
        std::shared_ptr<const app::FrontendProfile> profile,remembered;
        std::unique_ptr<os::RecoveryTask> recovery;std::unique_ptr<ui::RecoveryPreparationTask> preparation;std::unique_ptr<ui::EditorDraft> draft;
        std::uint64_t tickets=0;bool ended=false;std::string line;
        while(std::getline(std::cin,line)){
            J answer;const auto started=std::chrono::steady_clock::now();
            try{
                const auto q=J::parse(line);const std::string op=q.at("op");
                if(op=="view"){
                    const auto v=backend.take();profile=v.profile;answer={{"pending",v.pending},{"loading",v.loading},{"stopped",v.stopped},{"failed",v.failed},{"withdrawal",v.withdrawal},{"status",v.status},{"profile",nullptr},{"reply",nullptr}};
                    if(profile)answer["profile"]={{"serial",profile->serial},{"epoch",profile->epoch},{"revision",c::authored_revision(profile->view.documents)},
                        {"recovery",profile->view.recovery?context(*profile->view.recovery):J()},{"retirement",profile->recovery_retirement?J(*profile->recovery_retirement):J()}};
                    if(v.reply)answer["reply"]={{"body",v.reply->body},{"query",v.reply->query},{"epoch",v.reply->epoch},{"ticket",v.reply->ticket}};
                }else if(op=="editor-ready"){
                    auto selected=q.value("old",false)?remembered:profile;
                    if(q.value("copied",false)&&selected)selected=std::make_shared<const app::FrontendProfile>(*selected);
                    answer={{"consumed",static_cast<bool>(backend.take_editor(selected))}};
                }else if(op=="remember"){need(static_cast<bool>(profile));remembered=profile;answer={{"remembered",true}};}
                else if(op=="load"){
                    const auto selected=q.value("old",false)?remembered:profile;need(selected&&selected->view.recovery&&!recovery);const auto& v=*selected->view.recovery;const auto& a=v.admission;
                    recovery=(*backend.recovery())(a.directory.path,{v.editor_session,a.profile,a.generation,a.policy_revision,true,true,a.erase});answer={{"created",true}};
                }else if(op=="poll"){
                    need(static_cast<bool>(recovery));const auto status=recovery->poll();auto done=recovery->take();
                    answer={{"state",static_cast<int>(status.state)},{"reaped",status.reaped},{"process",status.process},{"bytes",status.retained_bytes},{"completion",nullptr}};
                    if(done)answer["completion"]={{"operation",done->operation},{"outcome",done->outcome},{"digest",done->digest?J(*done->digest):J()},{"bytes",done->bytes?J(*done->bytes):J()}};
                }else if(op=="replace"){need(static_cast<bool>(recovery));answer={{"ticket",recovery->replace(q.at("bytes"))}};}
                else if(op=="retire"){need(static_cast<bool>(recovery));answer={{"ticket",recovery->retire()}};}
                else if(op=="stop"){if(recovery)recovery->close();answer={{"closed",true}};}
                else if(op=="drop"){need(!recovery||recovery->status().reaped);recovery.reset();answer={{"dropped",true}};}
                else if(op=="submit"){
                    need(static_cast<bool>(profile));auto command=q.at("command");const auto id=backend.request_id();command["request_id"]=id;
                    std::optional<std::string> digest;if(!q.at("digest").is_null())digest=q["digest"].get<std::string>();
                    backend.submit({++tickets,profile->epoch,id,command.dump()},std::move(digest));answer={{"request",id},{"ticket",tickets}};
                }else if(op=="reload"){backend.reload();answer={{"loading",true}};}
                else if(op=="ack"){backend.acknowledge_retirement(q.at("serial"));answer={{"acknowledged",true}};}
                else if(op=="retrieve"){backend.retrieve();answer={{"requested",true}};}
                else if(op=="prepare"){
                    need(profile&&profile->view.recovery&&!preparation);auto resources=profile->resources;resources.capabilities.insert("editor.recovery");
                    const auto begin=std::chrono::steady_clock::now();
                    draft=std::make_unique<ui::EditorDraft>(c::Authority{true,"console",{"console"}},profile->view.policy,profile->view.documents,profile->epoch,resources,true);
                    const auto initialized=std::chrono::steady_clock::now();const auto& a=profile->view.recovery->admission;
                    auto work=draft->recovery_restore_work(q.at("bytes"),{a.profile,a.generation});const auto copied=std::chrono::steady_clock::now();
                    preparation=(*backend.preparations())(std::move(work));const auto dispatched=std::chrono::steady_clock::now();
                    const auto us=[](auto a,auto b){return std::chrono::duration_cast<std::chrono::microseconds>(b-a).count();};
                    answer={{"created",true},{"timings_us",{{"draft",us(begin,initialized)},{"input",us(initialized,copied)},{"dispatch",us(copied,dispatched)}}}};
                }else if(op=="prepared"){
                    need(preparation&&profile&&profile->view.recovery);const auto status=preparation->status();answer={{"ready",status.ready},{"stopped",status.stopped},{"running",status.running},{"error",status.error}};
                    if(status.ready){const auto& a=profile->view.recovery->admission;auto prepared=preparation->take();const auto begin=std::chrono::steady_clock::now();
                        draft->restore_recovery(std::move(prepared),{a.profile,a.generation});const auto restored=std::chrono::steady_clock::now();answer["scene"]=*draft->scene();preparation.reset();draft.reset();
                        answer["restore_us"]=std::chrono::duration_cast<std::chrono::microseconds>(restored-begin).count();}
                }else if(op=="preview-cost"){
                    need(static_cast<bool>(profile));auto authored=profile->view.documents;authored.scene=q.at("scene");
                    auto previous=std::chrono::steady_clock::now();answer=J::object();
                    const auto mark=[&](const char* name){const auto next=std::chrono::steady_clock::now();answer[name]=std::chrono::duration_cast<std::chrono::microseconds>(next-previous).count();previous=next;};
                    ui::EditorDraft base({true,"console",{"console"}},profile->view.policy,profile->view.documents,profile->epoch,profile->resources,true);mark("base_us");
                    auto borrowed=base.resources();auto catalog=c::ContentCatalog::retained(*borrowed);mark("catalog_us");
                    auto resources=borrowed->selection().contains("schema_version")?catalog.theme_resources(borrowed->selection(),authored):catalog.resources(borrowed->selection(),authored);mark("resources_us");
                    c::validate_resource_binding(*resources,authored);mark("binding_us");
                    namespace s=syspane::scene;namespace v=syspane::rendering;
                    s::Display display;display.id="display:primary";display.bounds=display.work={0,0,800*s::dip,600*s::dip};
                    v::SurfaceConfig config;config.authored=authored;config.resources=resources;config.capabilities=profile->resources.capabilities;
                    config.topology.displays={display};config.topology.fallback=display.id;config.topology.roles["primary"]={display.id};
                    v::SceneSurface surface({true,"console",{"console"}},profile->view.policy,std::move(config),{},[]{return true;},"",v::SurfaceAudience::inspector,backend.images());mark("surface_us");
                    surface.paint(0,{},[](auto,const v::SurfaceFrame*){});mark("paint_us");
                    answer["surface_state"]=static_cast<int>(surface.status().code);surface.close();
                    mark("surface_close_us");
                    c::ValidatedAuthored snapshot(authored);mark("snapshot_prepare_us");
                    v::SurfaceConfig ready;ready.authored_snapshot=std::move(snapshot);ready.resources=resources;ready.capabilities=profile->resources.capabilities;
                    ready.topology.displays={display};ready.topology.fallback=display.id;ready.topology.roles["primary"]={display.id};
                    v::SceneSurface prepared_surface({true,"console",{"console"}},profile->view.policy,std::move(ready),{},[]{return true;},"",v::SurfaceAudience::inspector,backend.images());mark("prepared_surface_us");
                    prepared_surface.paint(0,{},[](auto,const v::SurfaceFrame*){});mark("prepared_paint_us");
                    answer["prepared_surface_state"]=static_cast<int>(prepared_surface.status().code);prepared_surface.close();mark("prepared_close_us");
                    ui::EditorDraft admitted({true,"console",{"console"}},profile->view.policy,authored,profile->epoch,profile->resources,true);mark("draft_us");
                    auto owned=admitted.resource_snapshot();answer["owns_current_resources"]=owned.get()==admitted.resources();mark("snapshot_us");
                    answer["clean_clipboard"]=admitted.clipboard_available();mark("clean_clipboard_us");
                    const auto& first=authored.scene.at("widgets").at(0);auto title=first.at("title").get<std::string>();need(!title.empty());title[0]=title[0]=='X'?'Y':'X';
                    admitted.execute({ui::WidgetPropertyEdit{first.at("id"),ui::WidgetProperty::title,title}});mark("edit_us");
                    answer["dirty_clipboard"]=admitted.clipboard_available();mark("dirty_clipboard_us");
                    answer["may_submit"]=admitted.may_submit("commit");mark("may_submit_us");
                    answer["may_submit_again"]=admitted.may_submit("commit");mark("may_submit_again_us");
                }else if(op=="close"){backend.close();if(preparation)preparation->cancel();answer={{"closing",true}};}
                else if(op=="end"){need(backend.take().stopped);recovery.reset();preparation.reset();draft.reset();ended=true;answer={{"ended",true}};}
                else need(false);
            }catch(const syspane::protocol::Error& e){answer={{"error",e.what()}};}
            const auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-started).count();
            std::cout<<J{{"result",answer},{"elapsed_us",us}}.dump()<<std::endl;if(ended)break;
        }
        if(!ended){backend.close();for(unsigned n=0;n<1000&&!backend.take().stopped;++n)std::this_thread::sleep_for(std::chrono::milliseconds(5));return 2;}
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
