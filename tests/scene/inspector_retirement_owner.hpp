#pragma once
#include "inspector_cell_lifetime.hpp"
#include "gtk_history_limits.hpp"
namespace inspector_retirement_owner {
using namespace fixture;namespace ui=syspane::interfaces;
inline Json state(const ui::SceneInspector& view){const auto s=view.native_retirement();return {{"pending",s.pending},{"accepted",s.accepted},{"delivered",s.delivered},{"polls",s.polls},{"total_us",s.total_us},{"max_us",s.max_us},{"failed",s.failed}};}
inline Json packet(unsigned generation,bool partial=false){n::NetworkState source("E1","clock:1","scope:1");source.demand(1);syspane::platform::NetworkResult input{syspane::platform::NetworkCode::success,0,{}};
    for(unsigned i=1;i<=64;++i){const auto id=partial&&i==64?65U:i;input.rows.push_back({id,id,6,syspane::platform::NetworkCounters{10,7}});}
    if(partial){auto previous=input;previous.rows.back()={64,64,6,syspane::platform::NetworkCounters{10,7}};need(source.commit(1,0,previous,tick(0),tick(0))==n::NetworkStateCode::accepted,"partial original lifetime acquisition");}
    const auto time=partial?1000000U:0U;need(source.commit(1,0,std::move(input),tick(time),tick(time))==n::NetworkStateCode::accepted,"retirement complete acquisition");
    return n::network_document(*source.sample(),generation,"2026-10-06T00:00:00Z","2026-10-06T00:00:01Z",true);
}
inline int run(const std::string& root){need(gtk_init_check(nullptr,nullptr),"retirement owner display");auto grant=inspector_admission_owner_test::grant();auto binding=inspector_admission_owner_test::binding();std::uint64_t now=1000;
    auto make=[&]{return std::make_unique<ui::SceneInspector>(c::Authority{true,"console",{"console"}},grant,gtk_history_limits::configuration(root,true),std::vector<v::SurfaceProvider>{provider()});};
    auto first=make(),second=make();auto* a=gtk_window_new(GTK_WINDOW_TOPLEVEL);auto* b=gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_container_add(GTK_CONTAINER(a),first->widget());gtk_container_add(GTK_CONTAINER(b),second->widget());gtk_widget_show_all(a);gtk_widget_show_all(b);
    auto* at=gtk_history_limits::tree_of(first->widget());auto* bt=gtk_history_limits::tree_of(second->widget());r::TelemetryReceiver receiver({11,4},grant,n::network_metrics(),binding,now);
    need(receiver.receive(wire(packet(1),binding),++now,tick(0)).code==r::DataCode::accepted,"retirement complete receipt");
    first->deliver(receiver.view(now),{11,4},now);second->deliver(receiver.view(now),{11,4},now);gtk_tree_view_expand_all(GTK_TREE_VIEW(at));gtk_tree_view_expand_all(GTK_TREE_VIEW(bt));
    inspector_cell_lifetime::Held old_a(at),old_b(bt);need(old_a.cells.size()==646&&old_b.cells.size()==646,"literal 323-row two-owner projection");
    auto denied=grant;denied.revision=8;denied.disclosure.erase({"console","inspector"});Json calls=Json::array();
    const auto timed=[&](const char* label,const auto& action){const auto begin=g_get_monotonic_time();action();const auto us=g_get_monotonic_time()-begin;need(us<=100000,"retirement actual caller 100-ms limit");calls.push_back({{"call",label},{"work_us",us}});};
    timed("revoke-first",[&]{first->policy(denied,++now);});old_a.empty(0,false);need(first->native_retirement().pending>256,"large owner remains pending");need(!second->native_retirement().accepted,"second owner remains independent");
    const auto* active=atk_object_get_name(old_b.cells[0]);need(active&&*active,"independent active projection preserved");
    grant.revision=9;binding.policy_revision=9;timed("regrant-first",[&]{first->policy(grant,++now);});r::TelemetryReceiver fresh({11,5},grant,n::network_metrics(),binding,now);
    need(fresh.receive(wire(packet(2),binding),++now,tick(0)).code==r::DataCode::accepted,"retirement fresh receipt");
    timed("deliver-while-pending",[&]{first->deliver(fresh.view(now),{11,5},now);});need(first->native_retirement().pending&&gtk_tree_model_iter_n_children(gtk_tree_view_get_model(GTK_TREE_VIEW(at)),nullptr)==0,"fresh adoption waits for native retirement");old_a.empty(0,false);
    unsigned polls=0;while(first->native_retirement().pending){need(++polls<=16,"bounded real owner drain");timed("refresh-first",[&]{++now;first->deliver(fresh.view(now),{11,5},now);});}old_a.empty();
    need(gtk_tree_model_iter_n_children(gtk_tree_view_get_model(GTK_TREE_VIEW(at)),nullptr)==2,"fresh projection adopted after drain");inspector_cell_lifetime::Held new_a(at);need(new_a.cells.size()==646,"fresh complete projection");
    for(auto* cell:new_a.cells)need(std::find(old_a.cells.begin(),old_a.cells.end(),cell)==old_a.cells.end(),"fresh objects never rebind old cells");
    need(fresh.receive(wire(packet(3,true),binding),++now,tick(1000000)).code==r::DataCode::accepted,"partial retirement complete receipt");
    timed("partial-first",[&]{first->deliver(fresh.view(now),{11,5},now);});
    auto* partial_model=gtk_tree_view_get_model(GTK_TREE_VIEW(at));GtkTreeIter table,entity;
    need(gtk_tree_model_get_iter_first(partial_model,&table)&&gtk_tree_model_iter_next(partial_model,&table)&&gtk_tree_model_iter_children(partial_model,&entity,&table),"partial table shape");
    unsigned entities=0;bool replacement=false;
    do{++entities;const auto name=inspector_delivery_chart_test::cell(partial_model,&entity,1);need(name!="network:interface:64","old partial entity removed");
        if(name=="network:interface:65"){auto* path=gtk_tree_model_get_path(partial_model,&entity);replacement=gtk_tree_view_row_expanded(GTK_TREE_VIEW(at),path);gtk_tree_path_free(path);need(gtk_tree_model_iter_n_children(partial_model,&entity)==4,"four exact replacement fields");}
    }while(gtk_tree_model_iter_next(partial_model,&entity));
    need(entities==64&&replacement,"partial new entity retains default expansion while original notifications drain");
    timed("close-first",[&]{first->close();});bool stopped=true;timed("pending-stop-first",[&]{stopped=first->poll_image_jobs();});need(first->native_retirement().pending&&!stopped,"closed owner is not stopped while pending");new_a.empty(0,false);
    timed("revoke-second",[&]{second->policy(denied,++now);});old_b.empty(0,false);need(second->native_retirement().pending,"second retirement pending before parent destruction");
    timed("destroy-parent-second",[&]{gtk_widget_destroy(b);});unsigned shutdown=0;
    while(first->native_retirement().pending||second->native_retirement().pending){need(++shutdown<=16,"two-owner shutdown bound");timed("poll-first",[&]{first->poll_image_jobs();});timed("poll-second",[&]{second->poll_image_jobs();});}
    need(first->poll_image_jobs()&&second->poll_image_jobs(),"actual two-owner stop");old_a.empty();new_a.empty();old_b.empty();
    const auto first_state=state(*first),second_state=state(*second);for(const auto& s:{first_state,second_state})need(s["accepted"]==s["delivered"]&&s["pending"]==0&&!s["failed"].get<bool>()&&s["max_us"]<=100000,"all original operations delivered within measured polls");
    first.reset();second.reset();gtk_widget_destroy(a);old_a.empty();new_a.empty();old_b.empty();
    std::cout<<Json({{"outcome","pass"},{"cells_per_projection",646},{"first",first_state},{"second",second_state},{"calls",calls},{"immediate_empty",true},{"defunct_once",true},{"rapid_regrant",true},{"independent_owners",true},{"partial_expansion",true},{"pending_close",true},{"parent_destroy",true},{"after_destroy_empty",true}}).dump()<<std::endl;return 0;
}
}
