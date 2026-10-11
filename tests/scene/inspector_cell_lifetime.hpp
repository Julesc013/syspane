#pragma once
#include "inspector_admission_owner.hpp"
#include "inspector_delivery_chart_tests.hpp"
#include <gtk/gtk-a11y.h>
namespace inspector_cell_lifetime {
using namespace fixture;namespace ui=syspane::interfaces;
struct Held {
    std::vector<AtkObject*> cells;std::vector<unsigned> transitions;
    explicit Held(GtkWidget* tree){auto* table=ATK_TABLE(gtk_widget_get_accessible(tree));const auto rows=atk_table_get_n_rows(table);need(rows>0&&atk_table_get_n_columns(table)==2,"inspector lifetime shape");cells.reserve(rows*2);transitions.resize(rows*2);
        for(int row=0;row<rows;++row)for(int col=0;col<2;++col){auto* cell=atk_table_ref_at(table,row,col);need(cell&&ATK_IS_TEXT(cell)&&std::string(G_OBJECT_TYPE_NAME(cell))=="InspectorTextAccessible","real inspector lifetime accessible type");need(!ATK_TEXT_GET_IFACE(cell)->get_string_at_offset,"pinned native modern word slot absent before retirement");cells.push_back(cell);
            g_signal_connect(cell,"state-change",G_CALLBACK(+[](AtkObject*,const gchar* state,gboolean active,gpointer data){if(active&&std::string(state)=="defunct")++*static_cast<unsigned*>(data);}),&transitions[cells.size()-1]);}
    }
    ~Held(){for(std::size_t i=0;i<cells.size();++i){g_signal_handlers_disconnect_by_data(cells[i],&transitions[i]);g_object_unref(cells[i]);}}
    void empty(std::size_t begin=0){for(auto i=begin;i<cells.size();++i){auto* cell=cells[i];auto* value=atk_text_get_text(ATK_TEXT(cell),0,-1);need(value&&!value[0],"held inspector text cleared");g_free(value);const auto* name=atk_object_get_name(cell);need(!name||!name[0],"held inspector name cleared");need(atk_text_get_character_count(ATK_TEXT(cell))==0,"held inspector count cleared");
            auto* api=ATK_TEXT_GET_IFACE(cell);gint start=0,end=0;
            for(auto get:{api->get_text_before_offset,api->get_text_at_offset,api->get_text_after_offset}){value=get(ATK_TEXT(cell),0,ATK_TEXT_BOUNDARY_WORD_START,&start,&end);need(value&&!value[0],"held inspector layout cleared");g_free(value);}
            value=atk_text_get_string_at_offset(ATK_TEXT(cell),0,ATK_TEXT_GRANULARITY_WORD,&start,&end);need(!ATK_TEXT_GET_IFACE(cell)->get_string_at_offset&&!value&&start==-1&&end==-1,"held inspector native modern word explicitly unsupported");need(transitions[i]==1,"exactly one inspector defunct transition");
        }}
};
inline int run(const std::string& root){need(gtk_init_check(nullptr,nullptr),"inspector lifetime display");auto grant=inspector_admission_owner_test::grant();auto binding=inspector_admission_owner_test::binding();std::uint64_t now=1000;
    r::TelemetryReceiver receiver({11,4},grant,n::network_metrics(),binding,now);
    auto view=std::make_unique<ui::SceneInspector>(c::Authority{true,"console",{"console"}},grant,chart_config(root),std::vector<v::SurfaceProvider>{provider()});
    auto* window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_container_add(GTK_CONTAINER(window),view->widget());gtk_widget_show_all(window);auto* tree=inspector_delivery_test::tree(view->widget());need(tree,"real inspector tree");
    auto* columns=gtk_tree_view_get_columns(GTK_TREE_VIEW(tree));need(g_list_length(columns)==2,"two real columns");
    for(auto* at=columns;at;at=at->next){auto* cells=gtk_cell_layout_get_cells(GTK_CELL_LAYOUT(at->data));need(g_list_length(cells)==1&&std::string(G_OBJECT_TYPE_NAME(cells->data))=="InspectorTextRenderer","real inspector lifetime renderer type");g_list_free(cells);}g_list_free(columns);
    for(unsigned i=0;i<3;++i){need(receiver.receive(wire(chart_document(10+i,1+i,i*1000000),binding),++now,tick(i*1000000)).code==r::DataCode::accepted,"real inspector complete receipt");view->deliver(receiver.view(now),{11,4},now);}
    gtk_tree_view_expand_all(GTK_TREE_VIEW(tree));Held old(tree);need(old.cells.size()==8,"real inspector three-point cells");
    auto* model=gtk_tree_view_get_model(GTK_TREE_VIEW(tree));GtkTreeIter parent,point;need(gtk_tree_model_get_iter_first(model,&parent)&&gtk_tree_model_iter_children(model,&point,&parent),"real point row");unsigned generation=1;
    do{need(inspector_delivery_chart_test::cell(model,&point,1)=="Point "+std::to_string((generation-1)*1000000)+" ns","literal point item");need(inspector_delivery_chart_test::cell(model,&point,2)==std::to_string(9+generation)+" byte; generation "+std::to_string(generation)+"; "+(generation==1?"start":"join"),"literal point information");++generation;}while(gtk_tree_model_iter_next(model,&point));need(generation==4,"three exact points");
    auto* path=gtk_tree_model_get_path(model,&parent);gtk_tree_view_collapse_row(GTK_TREE_VIEW(tree),path);gtk_tree_path_free(path);old.empty(2);need(old.transitions[0]==0&&old.transitions[1]==0,"live root does not retire on collapse");
    auto* current=atk_text_get_text(ATK_TEXT(old.cells[1]),0,-1);need(current&&std::string(current).find("12 byte")!=std::string::npos,"active root preserved");g_free(current);
    auto denied=grant;denied.revision=8;denied.disclosure.erase({"console","inspector"});view->policy(denied,++now);old.empty();need(gtk_tree_model_iter_n_children(model,nullptr)==0,"denial erases native rows");
    grant.revision=9;binding.policy_revision=9;view->policy(grant,++now);r::TelemetryReceiver fresh({11,5},grant,n::network_metrics(),binding,now);need(fresh.receive(wire(chart_document(99,4,3000000),binding),++now,tick(3000000)).code==r::DataCode::accepted,"fresh inspector receipt");view->deliver(fresh.view(now),{11,5},now);gtk_tree_view_expand_all(GTK_TREE_VIEW(tree));Held new_cells(tree);need(new_cells.cells.size()==4,"one fresh point");
    need(gtk_tree_model_get_iter_first(model,&parent)&&gtk_tree_model_iter_children(model,&point,&parent)&&inspector_delivery_chart_test::cell(model,&point,2)=="99 byte; generation 4; start","fresh point has no old history");old.empty();
    view->close();need(view->poll_image_jobs(),"real inspector owner stopped");new_cells.empty();view.reset();gtk_widget_destroy(window);old.empty();new_cells.empty();
    std::cout<<Json({{"outcome","pass"},{"initial_cells",8},{"collapsed_children",6},{"fresh_cells",4},{"renderer_columns",2},{"defunct_once",true},{"after_destroy_empty",true},{"native_modern_word_unsupported",true},{"original_points",Json::array({"10 byte; generation 1; start","11 byte; generation 2; join","12 byte; generation 3; join"})}}).dump()<<std::endl;return 0;
}
}
