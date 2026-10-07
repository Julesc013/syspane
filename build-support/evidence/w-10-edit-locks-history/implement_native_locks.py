from pathlib import Path
r=Path.cwd()
def edit(n,a,b):
 p=r/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
n='source/interfaces/editor_form_linux.cpp'
edit(n,'bool editing()const{','bool protected_selection()const{if(!draft.scene())return false;for(const auto& id:draft.selection())if(edit_protected(*draft.scene(),id))return true;return false;}\n    bool own_locks()const{if(!draft.scene()||draft.selection().empty())return false;for(const auto& id:draft.selection())if(!authored_widget(*draft.scene(),id).value("edit_locked",false))return false;return true;}\n    bool editing()const{')
edit(n,'const bool enabled=editing()&&!fields_dirty;','const bool protected_ids=protected_selection();const bool enabled=editing()&&!fields_dirty;')
edit(n,'gtk_widget_set_sensitive(row.second,editing()&&selected&&','gtk_widget_set_sensitive(row.second,editing()&&!protected_ids&&selected&&')
edit(n,'if((content&&content->opened())||(binding','if(id=="lock")active=enabled&&draft.locks_available()&&!draft.selection().empty();\n            if(protected_ids&&(id=="properties"||id=="duplicate"||id=="delete"||id=="group"||id=="ungroup"||id=="wrap"||id=="unwrap"||id=="layout"||id=="bindings"||id=="content"||id.substr(0,6)=="align-"||id.substr(0,6)=="space-"))active=false;\n            if((content&&content->opened())||(binding')
edit(n,'gtk_widget_set_sensitive(tree,enabled);','const char* lock_label=own_locks()?"Unlock":"Lock";if(std::string(gtk_button_get_label(GTK_BUTTON(buttons.at("lock"))))!=lock_label){gtk_button_set_label(GTK_BUTTON(buttons.at("lock")),lock_label);accessible(buttons.at("lock"),lock_label,"editor.lock");}\n        gtk_widget_set_sensitive(tree,enabled);')
edit(n,'message(value);guide_feedback();','if(selected&&edit_locked(*draft.scene(),draft.selection()[0]))value+=selected->value("edit_locked",false)?" Locked":" Locked by container";\n        else if(protected_ids)value+=" Contains locked objects";\n        message(value);guide_feedback();')
edit(n,'else if(id=="properties")properties();','else if(id=="lock"){ready();gesture.reset();execute({SetWidgetLocks{draft.selection(),!own_locks()}});}\n        else if(id=="properties")properties();')
edit(n,'Gesture g;g.x=x;g.y=y;','if(protected_selection()){gesture.reset();gtk_widget_queue_draw(canvas);return;}\n        Gesture g;g.x=x;g.y=y;')
edit(n,'button(containers,"unwrap","Unwrap...");','button(containers,"unwrap","Unwrap...");button(containers,"lock","Lock");')
