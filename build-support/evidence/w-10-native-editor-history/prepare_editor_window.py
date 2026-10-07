from pathlib import Path
r=Path.cwd();s=(r/'tests/configuration/settings_window.cpp').read_text()
s=s.replace('"settings_form.hpp"','"editor_form.hpp"\n#include "child.hpp"').replace('"settings_content_fixture.hpp"','"../configuration/settings_content_fixture.hpp"')
s=s.replace('SettingsForm','EditorForm').replace('fixture:settings','fixture:editor').replace('settings:', 'editor:').replace('syspane-settings','syspane-editor').replace('SysPane Settings','SysPane Editor')
s=s.replace('GtkWidget *window=nullptr,*canary=nullptr;','GtkWidget *window=nullptr,*canary=nullptr,*overlay=nullptr;bool recovery=false;')
s=s.replace('content=mode.find("resource-")==0;behavior=content?mode.substr(9):mode;','content=true;behavior=mode;')
s=s.replace('auto scene=fixture.authored.scene;scene["revision"]="39";', 'auto scene=read(root+"/tests/editor/native-cases.json")["authored"]["scene"];scene["revision"]="39";')
s=s.replace('attach_owner();\n        ui::EditorForm::Actions actions;', '''if(behavior=="conflict"){
            c::Transactions external(*store,"EX",c::make_resource_provider(*store,{"scene.content"},[]{return std::vector<c::ContentPackage>{};}));
            auto scene=original.scene;scene["widgets"][0]["title"]="Theirs";
            Json q={{"schema_version","0.4.0"},{"request_id","other"},{"expected_revision","40"},{"policy_generation","7"},{"intent","commit"},{"content",store->load().resources->selection()},{"operations",Json::array({{{"op","scene.replace"},{"scene",scene}}})}};
            need(external.submit("fixture:editor","other",q.dump(),authority(),[&]{return current;},0)["outcome"]=="accepted","conflict fixture");
        }
        attach_owner();
        ui::EditorForm::Actions actions;''')
s=s.replace('actions.request_id=[&]', 'actions.widget_id=[&]{return "widget:new"+std::to_string(++serial);};actions.exit=[&]{commands.push_back({"exit",{}});};actions.request_id=[&]')
s=s.replace('epoch,std::move(actions),ui::EditorForm::Translator{},resource_context()', 'epoch,*resource_context(),topology(),"D1",std::vector<syspane::rendering::SurfaceProvider>{},image_worker(),std::move(actions)')
s=s.replace('gtk_window_move(GTK_WINDOW(window),0,0);','gtk_window_move(GTK_WINDOW(window),0,recovery?100:0);')
s=s.replace('gtk_container_add(GTK_CONTAINER(window),box);','overlay=gtk_overlay_new();gtk_container_add(GTK_CONTAINER(window),overlay);gtk_container_add(GTK_CONTAINER(overlay),box);')
s=s.replace('Retained settings canary 1500','Retained editor canary Move me')
s=s.replace('if(command.first=="reload")','if(command.first=="exit"){emit({{"event","closed"}});gtk_main_quit();continue;}\n            if(command.first=="reload")')
s=s.replace('form->reload(store->load().documents,epoch,resource_context())','form->reload(store->load().documents,epoch,*resource_context())')
s=s.replace('if(behavior=="wrong-selection"){auto changed=p::parse(body);changed["content"]=alternate_selection;body=changed.dump();}', 'if(behavior=="wrong-commit"){auto changed=p::parse(body);changed["operations"][0]["scene"]["widgets"][0]["layout"]["base"]["x"]=71;body=changed.dump();}')
s=s.replace('if(value=="release")release();','''if(value=="freeze-preview"){
            need(behavior=="frozen-preview","unadmitted frozen preview");
            auto* pixels=gdk_pixbuf_get_from_window(gtk_widget_get_window(window),0,0,gtk_widget_get_allocated_width(window),gtk_widget_get_allocated_height(window));need(pixels!=nullptr,"capture fixture");
            auto* image=gtk_image_new_from_pixbuf(pixels);g_object_unref(pixels);gtk_widget_set_halign(image,GTK_ALIGN_START);gtk_widget_set_valign(image,GTK_ALIGN_START);gtk_overlay_add_overlay(GTK_OVERLAY(overlay),image);gtk_overlay_set_overlay_pass_through(GTK_OVERLAY(overlay),image,TRUE);gtk_widget_show(image);
        }
        else if(value=="topology"){form->topology(topology("D2"),"D2");}
        else if(value=="release")release();''')
s=s.replace('struct Window {','''std::string image_worker(){char path[4096];const auto n=readlink("/proc/self/exe",path,sizeof(path)-1);need(n>0,"native path");std::string value(path,static_cast<std::size_t>(n));return value.substr(0,value.rfind('/'))+"/SysPane.ImageWorker";}
syspane::scene::Topology topology(const std::string& id="D1"){syspane::scene::Display d;d.id=id;d.bounds=d.work={0,0,500*64,420*64};return {{d},{},id};}
struct Window {''')
s=s.replace('need(argc==4&&geteuid()!=0,"unprivileged fixture arguments");','const bool recovery=argc==6&&std::string(argv[1])=="--recovery-child";need((argc==4||recovery)&&geteuid()!=0,"unprivileged fixture arguments");if(recovery)os::arm_parent_lifetime(std::stoull(argv[2]));')
s=s.replace('w.root=argv[1];w.path=argv[2];w.mode=argv[3];','w.recovery=recovery;const int offset=recovery?2:0;w.root=argv[1+offset];w.path=argv[2+offset];w.mode=argv[3+offset];')
s=s.replace('reader=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w)', 'reader=recovery?0:g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),input,&w)')
s=s.replace('if(g_main_context_find_source_by_id(nullptr,id))','if(id&&g_main_context_find_source_by_id(nullptr,id))')
(r/'tests/editor/editor_window.cpp').write_text(s,encoding='utf-8',newline='\n')

