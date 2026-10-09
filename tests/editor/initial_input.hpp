// Fixed observable first-input expectations, exercised before changing scheduling.
int initial_input(const std::string& root){
    for(const std::string mode:{"tree","pointer","topology-tree","topology-pointer","reload","withdrawal","empty-click","no-selection-key","fallback"}){
        settings_fixture::Fixture fixture(root);auto authored=fixture.authored;
        authored.scene=read(root+"/tests/editor/native-cases.json")["authored"]["scene"];
        authored.scene["widgets"].erase(authored.scene["widgets"].begin()+2);authored.scene["roots"].erase(authored.scene["roots"].begin()+2);
        authored.settings["revision"]=authored.scene["revision"]="40";
        if(mode.substr(0,9)=="topology-"){
            auto responsive=authored.scene["widgets"][0]["layout"]["base"];responsive["x"]=100;
            authored.scene["widgets"][0]["layout"]["breakpoints"]=Json::array({{{"min_width_dip",600},{"layout",responsive}}});
        }
        if(mode=="fallback")authored.scene["widgets"][0]["content"]["body"]=std::string(1024,'W');
        auto expected=authored.scene;std::optional<ui::EditRequest> request;ui::EditorForm::Actions actions;
        actions.request_id=[] {return "initial:request";};actions.submit=[&](const auto& q){request=q;};
        actions.widget_id=[] {throw std::runtime_error("unexpected creation");return std::string{};};
        actions.cancel=[](const auto&){throw std::runtime_error("unexpected cancellation");};
        actions.reload=actions.exit=[] {throw std::runtime_error("unexpected navigation");};
        ui::EditorForm form(authority(),policy(),authored,"E1",fixture.resources(),topology(),"D1",{},"",std::move(actions));
        auto control=[&](const char* id){auto* w=editor_control(form.widget(),id);need(w!=nullptr,"missing initial control");return w;};
        auto* canvas=control("editor.canvas");auto* tree=GTK_TREE_VIEW(control("editor.objects"));
        auto field=[&](const char* id){auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(control(id)));GtkTextIter a,z;gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string result=raw;g_free(raw);return result;};
        auto choose=[&]{auto* path=gtk_tree_path_new_first();gtk_tree_selection_select_path(gtk_tree_view_get_selection(tree),path);gtk_tree_path_free(path);};
        auto point=[&](double x,double y){GdkEventButton event{};event.button=1;event.x=x;event.y=y;gboolean handled=FALSE;event.type=GDK_BUTTON_PRESS;g_signal_emit_by_name(canvas,"button-press-event",&event,&handled);need(handled,"initial press not consumed");event.type=GDK_BUTTON_RELEASE;g_signal_emit_by_name(canvas,"button-release-event",&event,&handled);need(handled,"initial release not consumed");};
        auto key=[&]{GdkEventKey event{};event.type=GDK_KEY_PRESS;event.keyval=GDK_KEY_Right;gboolean handled=FALSE;g_signal_emit_by_name(canvas,"key-press-event",&event,&handled);return handled!=FALSE;};
        need(!gtk_widget_get_realized(canvas),"fixture drew before input");
        double x=40;
        if(mode.substr(0,9)=="topology-"){auto changed=topology();changed.displays[0].bounds.width=changed.displays[0].work.width=800*64;form.topology(changed,"D1");x=100;}
        if(mode=="reload"){authored.scene["widgets"][0]["layout"]["base"]["x"]=70;expected=authored.scene;form.reload(authored,"E2",fixture.resources());x=70;}
        if(mode=="withdrawal"){
            form.policy({});need(gtk_tree_model_iter_n_children(gtk_tree_view_get_model(tree),nullptr)==0,"withdrawal retained rows");
            need(field("editor.value.title").empty()&&field("editor.value.x").empty()&&!gtk_widget_get_sensitive(canvas),"withdrawal retained input");
            need(!key()&&!request,"withdrawn key mutated");
        }else{
            if(mode=="empty-click"){point(490,400);need(field("editor.value.title").empty()&&!key()&&!request,"empty click selected or mutated");}
            if(mode=="no-selection-key")need(!key()&&!request,"unselected key mutated");
            if(mode=="pointer"||mode=="topology-pointer")point(x+10,50);else choose();
            need(field("editor.value.title")=="Editable pane","wrong initial selection");
            if(mode=="fallback"){
                need(field("editor.value.x").empty()&&!gtk_widget_get_sensitive(control("editor.value.x")),"fallback exposed geometry");
                need(std::string(gtk_label_get_text(GTK_LABEL(control("editor.status")))).find("Preview unavailable")!=std::string::npos,"native fallback missing");
                need(!request,"fallback submitted");
            }else{
                need(std::stod(field("editor.value.x"))==x&&gtk_widget_get_sensitive(control("editor.value.x")),"initial geometry was not hydrated");
                need(key()&&std::stod(field("editor.value.x"))==x+1,"queued key used stale geometry");
                auto& layout=expected["widgets"][0]["layout"];(mode.substr(0,9)=="topology-"?layout["breakpoints"][0]["layout"]:layout["base"])["x"]=x+1;
                auto* apply=control("editor.apply");need(gtk_widget_get_sensitive(apply),"initial movement not admissible");gtk_button_clicked(GTK_BUTTON(apply));
                need(request.has_value(),"initial movement not submitted");const auto command=Json::parse(request->body);
                need(command.at("operations").size()==1&&command.at("operations")[0].at("scene")==expected,"first input changed unexpected authored content");
            }
        }
        need(!gtk_widget_get_realized(canvas),"fixture processed a draw");form.close();need(form.stopped(),"initial fixture did not close");
        emit({{"case",mode},{"outcome","pass"}});
    }
    return 0;
}
