// Hold image acknowledgement independently of request completion.
#include "../scene/image_fixture.hpp"
namespace request_exit_fixture {
namespace v=syspane::rendering;
struct Image {bool cancelled=false,stopped=false;};
struct Task:v::ImageTask {
    std::shared_ptr<Image> value;explicit Task(std::shared_ptr<Image> i):value(std::move(i)){}
    v::ImageJobStatus poll()override{return {value->cancelled?v::ImageJobState::cancelled:v::ImageJobState::running,"",value->stopped};}
    void cancel()override{value->cancelled=true;}
    syspane::scene::Image take()override{throw std::runtime_error("held image was taken");}
    std::uint64_t process_id()const override{return 0;}
};
}
int request_exit(const std::string& root){
    using namespace request_exit_fixture;
    for(const bool prepare:{false,true}){
        const auto cfg=fixture::image_config(root+"/spec/fixtures/valid");
        ui::SettingsResources resources{std::make_shared<const c::ContentCatalog>(c::ContentCatalog::retained(*cfg.resources)),cfg.resources->selection(),cfg.capabilities};
        std::vector<std::shared_ptr<Image>> images;
        const v::ImageFactory factory=[&](std::string,std::string){auto value=std::make_shared<Image>();images.push_back(value);return std::make_unique<Task>(value);};
        request_form_fixture::Tasks tasks;unsigned exits=0,sends=0;ui::EditorForm::Actions actions;
        actions.request_id=[] {return "request:exit";};actions.widget_id=actions.request_id;actions.submit=[&](const auto&){++sends;};
        actions.cancel=[](const auto&){throw std::runtime_error("unexpected transport cancellation");};actions.reload=[]{};actions.exit=[&]{++exits;};
        ui::EditorForm form(authority(),policy(),cfg.authored,"E1",resources,cfg.topology,cfg.topology.fallback,{},"",std::move(actions),true,factory,{},tasks.requests());
        auto control=[&](const char* id){auto* w=editor_control(form.widget(),id);need(w!=nullptr,"missing exit control");return w;};
        auto click=[&](const char* id){gtk_button_clicked(GTK_BUTTON(control(id)));};
        auto* path=gtk_tree_path_new_first();gtk_tree_selection_select_path(gtk_tree_view_get_selection(GTK_TREE_VIEW(control("editor.objects"))),path);gtk_tree_path_free(path);
        gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title"))),"Exit draft",-1);click("editor.properties");
        need(!images.empty(),"no image work was held");
        if(prepare){click("editor.apply");need(tasks.request&&tasks.request->input,"no request work was held");tasks.request->state.running=true;}
        click("editor.cancel");need(exits==0&&!form.stopped()&&sends==0,"exit preceded outstanding work");
        if(prepare){tasks.request->finish(false,true);need(!form.stopped()&&exits==0&&sends==0,"request acknowledgement bypassed held image");}
        for(const auto& image:images){need(image->cancelled,"image work not cancelled");image->stopped=true;}
        need(form.stopped()&&exits==1&&sends==0,"exit did not follow complete drain");form.stopped();need(exits==1,"duplicate exit callback");
        emit({{"case",prepare?"request-and-image":"image"},{"outcome","pass"}});
    }
    return 0;
}
