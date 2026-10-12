#pragma once
#include <gtk/gtk-a11y.h>
#include <numeric>
namespace gtk_history_limits {
struct PolicyHeld {
    std::vector<AtkObject*> cells;std::vector<unsigned> transitions;const std::size_t expected;
    unsigned checks=0;
    bool erased=false;
    explicit PolicyHeld(std::size_t count):expected(count){fixture::need(count&&count<=6278,"maximum policy native hold bound");cells.reserve(count);transitions.resize(count);}
    ~PolicyHeld(){for(std::size_t i=0;i<cells.size();++i){g_signal_handlers_disconnect_by_data(cells[i],&transitions[i]);g_object_unref(cells[i]);}}
    bool advance(GtkWidget* tree){auto* table=ATK_TABLE(gtk_widget_get_accessible(tree));fixture::need(atk_table_get_n_columns(table)==2&&static_cast<std::size_t>(atk_table_get_n_rows(table))*2==expected,"maximum policy exact native cell count");const auto begin=g_get_monotonic_time();unsigned captured=0;
        while(cells.size()<expected&&captured<128&&g_get_monotonic_time()-begin<5000){const auto index=cells.size();auto* cell=atk_table_ref_at(table,static_cast<gint>(index/2),static_cast<gint>(index%2));fixture::need(cell&&ATK_IS_TEXT(cell)&&std::string(G_OBJECT_TYPE_NAME(cell))=="InspectorTextAccessible","maximum policy actual native cell");cells.push_back(cell);
            g_signal_connect(cell,"state-change",G_CALLBACK(+[](AtkObject*,const gchar* state,gboolean active,gpointer data){if(active&&std::string(state)=="defunct")++*static_cast<unsigned*>(data);}),&transitions[index]);
            fixture::need(!ATK_TEXT_GET_IFACE(cell)->get_string_at_offset,"maximum policy native modern word unsupported before");
            auto* value=atk_text_get_text(ATK_TEXT(cell),0,-1);fixture::need(value&&*value,"maximum policy initial native text");g_free(value);
            const auto* name=atk_object_get_name(cell);fixture::need(name&&*name&&atk_text_get_character_count(ATK_TEXT(cell))>0,"maximum policy initial name/count");
            auto* api=ATK_TEXT_GET_IFACE(cell);gint start=0,end=0;
            for(auto get:{api->get_text_before_offset,api->get_text_at_offset,api->get_text_after_offset}){value=get(ATK_TEXT(cell),0,ATK_TEXT_BOUNDARY_WORD_START,&start,&end);fixture::need(value,"maximum policy prime implemented native word slot");g_free(value);}
            ++captured;
        }return cells.size()==expected;
    }
    void check(bool complete){fixture::need(cells.size()==expected,"maximum policy complete native holds");
        for(std::size_t i=0;i<cells.size();++i){auto* cell=cells[i];auto* value=atk_text_get_text(ATK_TEXT(cell),0,-1);fixture::need(value&&!value[0],"maximum policy held text erased");g_free(value);const auto* name=atk_object_get_name(cell);fixture::need(!name||!name[0],"maximum policy held name erased");fixture::need(atk_text_get_character_count(ATK_TEXT(cell))==0,"maximum policy held count erased");
            auto* api=ATK_TEXT_GET_IFACE(cell);gint start=0,end=0;
            for(auto get:{api->get_text_before_offset,api->get_text_at_offset,api->get_text_after_offset}){value=get(ATK_TEXT(cell),0,ATK_TEXT_BOUNDARY_WORD_START,&start,&end);fixture::need(value&&!value[0],"maximum policy held word layout erased");g_free(value);}
            value=atk_text_get_string_at_offset(ATK_TEXT(cell),0,ATK_TEXT_GRANULARITY_WORD,&start,&end);fixture::need(!api->get_string_at_offset&&!value&&start==-1&&end==-1,"maximum policy native modern word unsupported after");fixture::need(complete?transitions[i]==1:transitions[i]<=1,"maximum policy exactly one normal defunct");
        }++checks;erased=true;
    }
    fixture::Json report()const{return {{"cells",cells.size()},{"checks",checks},{"empty",erased},{"defunct",std::accumulate(transitions.begin(),transitions.end(),std::uint64_t{0})},{"modern_unsupported",true}};}
};
}
