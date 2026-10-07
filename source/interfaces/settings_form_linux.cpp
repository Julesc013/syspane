#include "settings_form.hpp"
#include "private_text.hpp"
#include <gtk/gtk.h>
#include <gtk/gtk-a11y.h>
#include <thread>

namespace syspane::interfaces {
namespace {
namespace c=configuration;
std::string value_text(const Json& v){return v.is_string()?v.get<std::string>():v.is_null()?"":v.dump();}
std::string buffer_text(GtkWidget* w){auto* b=gtk_text_view_get_buffer(GTK_TEXT_VIEW(w));GtkTextIter a,z;gtk_text_buffer_get_bounds(b,&a,&z);auto* raw=gtk_text_buffer_get_text(b,&a,&z,FALSE);std::string out=raw;g_free(raw);return out;}
void buffer_set(GtkWidget* w,const std::string& text){if(buffer_text(w)!=text)gtk_text_buffer_set_text(gtk_text_view_get_buffer(GTK_TEXT_VIEW(w)),text.c_str(),static_cast<gint>(text.size()));}
void accessible(GtkWidget* w,const std::string& name,const std::string& id){atk_object_set_name(gtk_widget_get_accessible(w),name.c_str());atk_object_set_description(gtk_widget_get_accessible(w),id.c_str());}
std::string folded(const std::string& s){auto* p=g_utf8_casefold(s.c_str(),static_cast<gssize>(s.size()));std::string out=p;g_free(p);return out;}
}
struct SettingsForm::Impl {
    SettingsDraft draft;Actions actions;Translator translate;std::thread::id thread=std::this_thread::get_id();
    bool updating=false,closed=false,dispatching=false;GtkWidget *root=nullptr,*search=nullptr,*status=nullptr,*preview=nullptr,*apply=nullptr,*revert=nullptr,*cancel=nullptr,*reload=nullptr;
    std::vector<GtkWidget*> owned;
    struct Row {Impl* owner;SettingDescription descriptor;GtkWidget *box,*control,*detail,*error,*defaults;std::string invalid;};
    std::vector<std::unique_ptr<Row>> rows;
    Impl(c::Authority a,c::Policy p,c::Authored v,std::string e,Actions f,Translator t,std::optional<SettingsResources> resources):draft(std::move(a),std::move(p),std::move(v),std::move(e),std::move(resources)),actions(std::move(f)),translate(std::move(t)){}
    void owner()const{if(thread!=std::this_thread::get_id()||dispatching)throw std::logic_error("settings.owner");}
    GtkWidget* own(GtkWidget* w){g_object_ref_sink(w);owned.push_back(w);return w;}
    std::string tr(const std::string& id,const std::string& fallback)const{auto s=translate?translate(id,fallback):fallback;if(s.empty()||s.size()>4096||s.find('\0')!=std::string::npos||!g_utf8_validate(s.data(),static_cast<gssize>(s.size()),nullptr))throw protocol::Error("settings.translation");return s;}
    GtkWidget* label(const std::string& value){auto* w=own(gtk_label_new(value.c_str()));gtk_label_set_xalign(GTK_LABEL(w),0);gtk_label_set_line_wrap(GTK_LABEL(w),TRUE);return w;}
    GtkWidget* button(const std::string& id,const std::string& value){auto* w=own(gtk_button_new_with_label(tr("settings."+id,value).c_str()));accessible(w,tr("settings."+id,value),"settings."+id);return w;}
    void clear_errors(){for(auto& row:rows)row->invalid.clear();}
    void filter(){const auto query=folded(buffer_text(search));for(auto& row:rows){const auto hay=folded(row->descriptor.id+" "+tr(row->descriptor.label_id,row->descriptor.label)+" "+row->descriptor.page);gtk_widget_set_visible(row->box,query.empty()||hay.find(query)!=std::string::npos);}}
    void render(bool sync=false){
        updating=true;bool invalid=false;
        for(auto& item:rows){auto& row=*item;const auto v=draft.value(row.descriptor.id);const bool visible=draft.available();
            if(!visible){row.invalid.clear();sync=true;}
            if(sync||!v.editable){
                if(row.descriptor.kind==SettingKind::boolean)gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(row.control),visible&&v.effective==true);
                else buffer_set(row.control,visible?value_text(v.effective):"");
            }
            gtk_widget_set_sensitive(row.control,v.editable);gtk_widget_set_sensitive(row.defaults,v.editable);
            std::string detail;
            if(visible){detail=tr(row.descriptor.help_id,row.descriptor.help)+"\n"+row.descriptor.id+" | "+row.descriptor.units+" | "+row.descriptor.activation;
                if(v.reason=="policy.forced")detail+="\n"+tr("settings.policy_locked","Locked by policy")+" | "+tr("settings.requested","Requested")+": "+value_text(v.requested)+" | "+tr("settings.effective","Effective")+": "+value_text(v.effective);
                else if(v.reason=="policy.denied")detail+="\n"+tr("settings.policy_locked","Locked by policy");}
            gtk_label_set_text(GTK_LABEL(row.detail),detail.c_str());gtk_label_set_text(GTK_LABEL(row.error),row.invalid.c_str());invalid=invalid||!row.invalid.empty();
        }
        const auto state=draft.state();const bool pending=draft.active_request().has_value();const bool editing=draft.available()&&!pending&&state!=DraftState::conflict;
        gtk_widget_set_sensitive(preview,draft.may_submit("preview")&&!invalid);gtk_widget_set_sensitive(apply,draft.may_submit("commit")&&!invalid);
        gtk_widget_set_sensitive(revert,editing&&(draft.dirty()||invalid));gtk_widget_set_sensitive(cancel,pending&&draft.available());
        gtk_widget_set_sensitive(reload,!pending&&!closed);
        std::string message;
        if(state==DraftState::closed||state==DraftState::unavailable)message=tr("settings.unavailable","Settings unavailable");
        else if(state==DraftState::pending)message=tr("settings.pending","Request pending; storage outcome is not known.");
        else if(state==DraftState::unknown)message=tr("settings.unknown","Outcome unknown; retrieve the original request before continuing.");
        else if(state==DraftState::conflict)message=tr("settings.conflict","Configuration changed; reload current settings before applying.");
        else if(invalid)message=tr("settings.invalid","Correct invalid fields before applying.");
        else if(!draft.last_result().is_null()){
            const auto& result=draft.last_result();const auto outcome=result["outcome"].get<std::string>();
            if(outcome=="accepted")message=tr("settings.saved","Saved durably; activation pending. Visibility has not been confirmed.");
            else if(outcome=="preview")message=tr("settings.preview_ready","Preview validated; nothing has been saved.");
            else if(outcome=="cancelled")message=tr("settings.cancelled","Request cancelled; nothing has been saved.");
            else message=tr("settings.rejected","Request did not change stored settings.");
            if(!result["error"].is_null())message+=" "+result["error"]["code"].get<std::string>();
        }else message=tr(draft.dirty()?"settings.dirty":"settings.clean",draft.dirty()?"Draft changes have not been saved.":"No draft changes.");
        if(draft.revision())message+=" "+tr("settings.revision","Revision")+" "+std::to_string(*draft.revision());
        gtk_label_set_text(GTK_LABEL(status),message.c_str());updating=false;filter();
    }
    void changed(Row& row){if(updating||closed)return;try{
        if(row.descriptor.kind==SettingKind::boolean)draft.set(row.descriptor.id,gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(row.control))!=FALSE);
        else draft.set_text(row.descriptor.id,buffer_text(row.control));
        row.invalid.clear();
    }catch(const protocol::Error& e){row.invalid=tr("settings.field_invalid","Enter a valid value")+std::string(" (")+e.what()+")";}render();}
    void submit(const std::string& intent){
        for(const auto& row:rows)if(!row->invalid.empty())return;
        const auto request=draft.begin(intent,actions.request_id());render();if(!request)return;
        dispatching=true;try{actions.submit(*request);dispatching=false;}catch(...){dispatching=false;draft.disconnected();render();}
    }
    void shut(){if(closed)return;closed=true;draft.close();clear_errors();if(status&&preview&&reload)render(true);if(search)buffer_set(search,"");}
    template<class F> void event(F f)noexcept{try{if(!closed){f();}}catch(const protocol::Error& e){try{gtk_label_set_text(GTK_LABEL(status),e.what());}catch(...){shut();}}catch(...){try{shut();}catch(...){}}}
    ~Impl(){try{shut();}catch(...){}if(root)gtk_widget_destroy(root);for(auto it=owned.rbegin();it!=owned.rend();++it)g_object_unref(*it);}
};
SettingsForm::SettingsForm(c::Authority a,c::Policy p,c::Authored v,std::string e,Actions actions,Translator translate,std::optional<SettingsResources> resources):impl_(std::make_unique<Impl>(std::move(a),std::move(p),std::move(v),std::move(e),std::move(actions),std::move(translate),std::move(resources))){
    auto& i=*impl_;if(!i.actions.request_id||!i.actions.submit||!i.actions.cancel||!i.actions.reload)throw protocol::Error("settings.actions");
    i.root=i.own(gtk_box_new(GTK_ORIENTATION_VERTICAL,8));auto* search_label=i.label(i.tr("settings.search","Search settings"));gtk_box_pack_start(GTK_BOX(i.root),search_label,FALSE,FALSE,0);
    i.search=i.own(private_text());gtk_widget_set_size_request(i.search,-1,30);accessible(i.search,i.tr("settings.search","Search settings"),"settings.search");gtk_box_pack_start(GTK_BOX(i.root),i.search,FALSE,FALSE,0);
    auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_box_pack_start(GTK_BOX(i.root),scroll,TRUE,TRUE,0);auto* list=gtk_box_new(GTK_ORIENTATION_VERTICAL,12);gtk_container_add(GTK_CONTAINER(scroll),list);
    for(const auto& d:setting_descriptions()){
        auto row=std::make_unique<Impl::Row>();row->owner=&i;row->descriptor=d;row->box=i.own(gtk_box_new(GTK_ORIENTATION_VERTICAL,3));gtk_box_pack_start(GTK_BOX(list),row->box,FALSE,FALSE,0);
        auto* label=i.label(i.tr(d.label_id,d.label));gtk_box_pack_start(GTK_BOX(row->box),label,FALSE,FALSE,0);auto* line=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);gtk_box_pack_start(GTK_BOX(row->box),line,FALSE,FALSE,0);
        row->control=i.own(d.kind==SettingKind::boolean?gtk_check_button_new():private_text());gtk_widget_set_size_request(row->control,240,30);
        accessible(row->control,i.tr(d.label_id,d.label),"settings.value."+d.id);gtk_label_set_mnemonic_widget(GTK_LABEL(label),row->control);gtk_box_pack_start(GTK_BOX(line),row->control,TRUE,TRUE,0);
        row->defaults=i.button("default","Use built-in default");atk_object_set_description(gtk_widget_get_accessible(row->defaults),("settings.default."+d.id).c_str());gtk_box_pack_start(GTK_BOX(line),row->defaults,FALSE,FALSE,0);
        row->detail=i.label("");row->error=i.label("");accessible(row->detail,"", "settings.detail."+d.id);accessible(row->error,"", "settings.error."+d.id);
        gtk_box_pack_start(GTK_BOX(row->box),row->detail,FALSE,FALSE,0);gtk_box_pack_start(GTK_BOX(row->box),row->error,FALSE,FALSE,0);
        if(d.kind==SettingKind::boolean)g_signal_connect(row->control,"toggled",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& r=*static_cast<Impl::Row*>(p);r.owner->event([&]{r.owner->changed(r);});}),row.get());
        else g_signal_connect(gtk_text_view_get_buffer(GTK_TEXT_VIEW(row->control)),"changed",G_CALLBACK(+[](GtkTextBuffer*,gpointer p){auto& r=*static_cast<Impl::Row*>(p);r.owner->event([&]{r.owner->changed(r);});}),row.get());
        g_signal_connect(row->defaults,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& r=*static_cast<Impl::Row*>(p);r.owner->event([&]{r.owner->draft.use_default(r.descriptor.id);r.invalid.clear();r.owner->render(true);});}),row.get());
        i.rows.push_back(std::move(row));
    }
    i.status=i.label("");atk_object_set_description(gtk_widget_get_accessible(i.status),"settings.status");gtk_box_pack_start(GTK_BOX(i.root),i.status,FALSE,FALSE,0);
    auto* buttons=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);gtk_box_pack_start(GTK_BOX(i.root),buttons,FALSE,FALSE,0);
    i.preview=i.button("preview","Preview");i.apply=i.button("apply","Apply");i.revert=i.button("revert","Revert draft");i.cancel=i.button("cancel","Cancel request");
    i.reload=i.button("reload","Reload current settings");gtk_widget_set_tooltip_text(i.reload,i.tr("settings.reload_help","Discard the draft and load current settings.").c_str());
    for(auto* b:{i.preview,i.apply,i.revert,i.cancel,i.reload})gtk_box_pack_start(GTK_BOX(buttons),b,FALSE,FALSE,0);
    g_signal_connect(i.preview,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{x.submit("preview");});}),&i);
    g_signal_connect(i.apply,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{x.submit("commit");});}),&i);
    g_signal_connect(i.revert,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{x.draft.revert();x.clear_errors();x.render(true);});}),&i);
    g_signal_connect(i.cancel,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{auto q=x.draft.cancel_request();if(q){x.dispatching=true;try{x.actions.cancel(*q);x.dispatching=false;}catch(...){x.dispatching=false;x.draft.disconnected();x.render();}}});}),&i);
    g_signal_connect(i.reload,"clicked",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{x.dispatching=true;try{x.actions.reload();x.dispatching=false;}catch(...){x.dispatching=false;throw;}});}),&i);
    g_signal_connect(gtk_text_view_get_buffer(GTK_TEXT_VIEW(i.search)),"changed",G_CALLBACK(+[](GtkTextBuffer*,gpointer p){auto& x=*static_cast<Impl*>(p);x.event([&]{x.filter();});}),&i);
    g_signal_connect(i.root,"destroy",G_CALLBACK(+[](GtkWidget*,gpointer p){auto& x=*static_cast<Impl*>(p);try{x.shut();}catch(...){}}),&i);
    i.render(true);
}
SettingsForm::~SettingsForm()=default;
GtkWidget* SettingsForm::widget()const{impl_->owner();return impl_->root;}
void SettingsForm::complete(std::uint64_t ticket,const Json& result){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.complete(ticket,result))i.render(true);}catch(...){i.render();throw;}}
void SettingsForm::reconciled(std::uint64_t ticket,const std::string& query_id,const std::string& epoch,const Json& response){auto& i=*impl_;i.owner();if(i.closed)return;try{if(i.draft.reconciled(ticket,query_id,epoch,response))i.render(true);}catch(...){i.render();throw;}}
void SettingsForm::disconnected(){auto& i=*impl_;i.owner();if(i.closed)return;i.draft.disconnected();i.render();}
void SettingsForm::policy(c::Policy policy){auto& i=*impl_;i.owner();if(i.closed)return;i.draft.policy(std::move(policy));i.clear_errors();i.render(true);}
void SettingsForm::reload(c::Authored value,std::string epoch,std::optional<SettingsResources> resources){auto& i=*impl_;i.owner();if(i.closed)return;i.draft.reload(std::move(value),std::move(epoch),std::move(resources));i.clear_errors();i.render(true);}
void SettingsForm::close(){impl_->owner();impl_->shut();}
}
