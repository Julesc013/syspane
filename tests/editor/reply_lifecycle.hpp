// Native component assertions; installed tests separately observe persistence,
// helper retirement and pixels through external input/accessibility.
int reply_lifecycle(const std::string& root,bool prepared=false){
    const auto close=ui::EditorForm::ReplyView::close_on_accepted;
    for(const std::string mode:{"direct","reconciled","default","cancelled","unknown","ticket","epoch","revision","facts","query","withdrawn"}){
        settings_fixture::Fixture fixture(root);
        auto authored=fixture.authored;
        authored.scene=read(root+"/tests/editor/native-cases.json")["authored"]["scene"];
        authored.settings["revision"]=authored.scene["revision"]="40";
        std::optional<ui::EditRequest> request;ui::EditorForm::Actions actions;
        actions.request_id=[] {return "reply:request";};
        actions.submit=[&](const auto& q){request=q;};
        actions.widget_id=[] {throw std::runtime_error("unexpected widget creation");return std::string{};};
        actions.cancel=[](const auto&){throw std::runtime_error("unexpected cancellation callback");};
        actions.reload=actions.exit=[] {throw std::runtime_error("unexpected navigation callback");};
        std::unique_ptr<ui::EditorForm> owner;
        if(prepared){
            std::unique_ptr<ui::PreparedEditor> value;std::exception_ptr failure;
            std::thread worker([&]{try{value=std::make_unique<ui::PreparedEditor>(authority(),policy(),authored,"E1",fixture.resources());}catch(...){failure=std::current_exception();}});
            worker.join();if(failure)std::rethrow_exception(failure);
            authored.scene["widgets"][0]["title"]="Changed after preparation";
            owner=std::make_unique<ui::EditorForm>(std::move(value),topology(),"D1",std::vector<syspane::rendering::SurfaceProvider>{},"",std::move(actions));
            need(!value,"prepared owner not consumed");
        }else owner=std::make_unique<ui::EditorForm>(authority(),policy(),authored,"E1",fixture.resources(),topology(),"D1",std::vector<syspane::rendering::SurfaceProvider>{},"",std::move(actions));
        auto& form=*owner;
        auto control=[&](const char* name){auto* w=editor_control(form.widget(),name);need(w!=nullptr,"missing lifecycle control");return w;};
        auto* tree=GTK_TREE_VIEW(control("editor.objects"));
        const auto rows=[&]{return gtk_tree_model_iter_n_children(gtk_tree_view_get_model(tree),nullptr);};
        need(rows()>0,"empty initial editor");
        auto* path=gtk_tree_path_new_first();gtk_tree_selection_select_path(gtk_tree_view_get_selection(tree),path);gtk_tree_path_free(path);
        if(prepared){
            auto* buffer=gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title")));GtkTextIter first,last;gtk_text_buffer_get_bounds(buffer,&first,&last);
            auto* text=gtk_text_buffer_get_text(buffer,&first,&last,FALSE);const std::string title=text;g_free(text);
            need(title==read(root+"/tests/editor/native-cases.json")["authored"]["scene"]["widgets"][0]["title"],"prepared state retained mutable input");
        }
        gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(control("editor.value.title"))),"Reply lifecycle",-1);
        for(const char* name:{"editor.properties","editor.apply"}){auto* b=control(name);need(gtk_widget_get_sensitive(b),"submission disabled");gtk_button_clicked(GTK_BUTTON(b));}
        need(request.has_value(),"missing actual form request");
        auto result=c::committed_result(request->request,"E1",41);
        if(mode=="ticket"){
            need(!form.complete(request->ticket+1,result,close)&&rows()>0,"foreign ticket closed editor");
        }else if(mode=="epoch"||mode=="revision"||mode=="facts"){
            auto invalid=result;if(mode=="epoch")invalid["producer_epoch"]="foreign";
            else if(mode=="revision")invalid["revision"]="42";else invalid["durable"]=false;
            bool rejected=false;try{form.complete(request->ticket,invalid,close);}catch(const p::Error&){rejected=true;}
            need(rejected&&rows()>0,"invalid acceptance closed editor");
        }
        if(mode=="cancelled"||mode=="unknown"){
            auto other=c::result({mode,mode=="unknown"?"request.pending":"request.cancelled"},request->request,"E1",40);
            need(form.complete(request->ticket,other,close)&&rows()>0,"non-accepted result closed editor");
            need(gtk_widget_get_sensitive(control("editor.apply"))==(mode=="cancelled"),"non-accepted admission changed");
        }else if(mode=="default"){
            need(form.complete(request->ticket,result)&&rows()>0,"default refresh erased editor");
            need(std::string(gtk_label_get_text(GTK_LABEL(control("editor.status")))).find("Saved durably")!=std::string::npos,"default accepted status missing");
        }else{
            if(mode=="withdrawn")form.policy({});
            if(mode=="reconciled"||mode=="query"){
                form.disconnected();result["producer_epoch"]="E2";
                Json reply={{"schema_version","0.1.0"},{"query_id","Q"},{"original_producer_epoch","E1"},{"request_id",request->request},{"result",result}};
                if(mode=="query"){
                    bool rejected=false;try{form.reconciled(request->ticket,"foreign","E2",reply,close);}catch(const p::Error&){rejected=true;}
                    need(rejected&&rows()>0,"foreign query closed editor");
                }
                need(form.reconciled(request->ticket,"Q","E2",reply,close),"reconciled result ignored");
            }else need(form.complete(request->ticket,result,close),"accepted result ignored");
            need(rows()==0&&!gtk_widget_get_sensitive(control("editor.reload"))&&!gtk_widget_get_sensitive(control("editor.apply")),"closed form retained rows/controls");
            need(!form.complete(request->ticket,Json::object(),close),"closed form consumed duplicate");
        }
        form.close();need(form.stopped(),"component did not stop");
        emit({{"case",mode},{"outcome","pass"}});
    }
    if(prepared){
        bool refused=false;
        try{ui::EditorForm form(std::unique_ptr<ui::PreparedEditor>{},topology(),"D1",{},"",{});}catch(const p::Error& e){refused=std::string(e.what())=="editor.prepared";}
        need(refused,"null prepared state accepted");emit({{"case","null"},{"outcome","pass"}});
    }
    return 0;
}
