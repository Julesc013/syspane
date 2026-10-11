#include <gtk/gtk.h>
#include <gtk/gtk-a11y.h>
#include <glib-unix.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
void need(bool okay,const char* reason){if(!okay)throw std::runtime_error(reason);}
struct Probe {
    GtkTreeStore* store=nullptr;GtkWidget *window=nullptr,*tree=nullptr;
    GtkTreeIter chart,retired;std::vector<GtkCellRenderer*> renderers;std::vector<AtkObject*> held;
    std::string strategy,input;bool collapsed=false,retirement_done=false,erased=false,recovered=false;int result=0;
    void row(GtkTreeIter& at,GtkTreeIter* parent,const std::string& item,const std::string& info){gtk_tree_store_append(store,&at,parent);gtk_tree_store_set(store,&at,0,item.c_str(),1,info.c_str(),-1);}
    void blank(GtkTreeIter* parent=nullptr){GtkTreeIter at;auto* model=GTK_TREE_MODEL(store);if(!gtk_tree_model_iter_children(model,&at,parent))return;
        do{blank(&at);gtk_tree_store_set(store,&at,0,"",1,"",-1);}while(gtk_tree_model_iter_next(model,&at));}
    Probe(std::string mode,bool collapse):strategy(std::move(mode)),collapsed(collapse){
        need(strategy=="blank"||strategy=="detach"||strategy=="scrub","cache probe strategy");
        store=gtk_tree_store_new(2,G_TYPE_STRING,G_TYPE_STRING);
        row(chart,nullptr,"ITEM_CHART_ROOT","ERASURE_CANARY_CHART_ROOT");
        for(unsigned i=0;i<3138;++i){GtkTreeIter at;row(at,&chart,"ITEM_POINT_"+std::to_string(i),"ERASURE_CANARY_POINT_"+std::to_string(i));}
        row(retired,nullptr,"ITEM_RETIRED_ROOT","ERASURE_CANARY_RETIRED_ROOT");
        for(unsigned i=0;i<32;++i){GtkTreeIter at;row(at,&retired,"ITEM_RETIRED_"+std::to_string(i),"ERASURE_CANARY_RETIRED_"+std::to_string(i));}
        window=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(window),"SysPane accessibility cache probe");gtk_window_set_default_size(GTK_WINDOW(window),740,540);
        auto* scroll=gtk_scrolled_window_new(nullptr,nullptr);gtk_container_add(GTK_CONTAINER(window),scroll);tree=gtk_tree_view_new_with_model(GTK_TREE_MODEL(store));gtk_container_add(GTK_CONTAINER(scroll),tree);
        for(int col=0;col<2;++col){auto* renderer=gtk_cell_renderer_text_new();g_object_set(renderer,"font","Noto Sans 9",nullptr);renderers.push_back(renderer);
            auto* column=gtk_tree_view_column_new_with_attributes(col?"Information":"Item",renderer,"text",col,nullptr);gtk_tree_view_column_set_sizing(column,GTK_TREE_VIEW_COLUMN_GROW_ONLY);gtk_tree_view_column_set_resizable(column,TRUE);gtk_tree_view_append_column(GTK_TREE_VIEW(tree),column);}
        atk_object_set_description(gtk_widget_get_accessible(tree),"syspane.cache.erasure.probe");gtk_widget_show_all(window);gtk_tree_view_expand_all(GTK_TREE_VIEW(tree));
        auto* table=ATK_TABLE(gtk_widget_get_accessible(tree));need(atk_table_get_n_rows(table)==3172&&atk_table_get_n_columns(table)==2,"cache probe initial shape");held.reserve(6344);
        for(int r=0;r<3172;++r)for(int col=0;col<2;++col){auto* cell=atk_table_ref_at(table,r,col);need(cell&&GTK_IS_CELL_ACCESSIBLE(cell)&&ATK_IS_TEXT(cell),"cache probe actual text object");auto* text=atk_text_get_text(ATK_TEXT(cell),0,-1);need(text&&*text,"cache probe initial text");g_free(text);held.push_back(cell);}
    }
    ~Probe(){for(auto* cell:held)g_object_unref(cell);if(window)gtk_widget_destroy(window);if(store)g_object_unref(store);}
    struct Leaks {unsigned text=0,name=0,count=0,word=0;};
    Leaks inspect(){Leaks leaks;
        for(auto* cell:held){auto* text=atk_text_get_text(ATK_TEXT(cell),0,-1);leaks.text+=text&&*text;g_free(text);const auto* name=atk_object_get_name(cell);leaks.name+=name&&*name;leaks.count+=atk_text_get_character_count(ATK_TEXT(cell))!=0;
            gint start=0,end=0;bool word=false;
            auto* api=ATK_TEXT_GET_IFACE(cell);
            for(auto get:{api->get_text_before_offset,api->get_text_at_offset,api->get_text_after_offset}){need(get,"cache probe public word slot");auto* value=get(ATK_TEXT(cell),0,ATK_TEXT_BOUNDARY_WORD_START,&start,&end);word=word||(value&&*value);g_free(value);}
            auto* value=atk_text_get_string_at_offset(ATK_TEXT(cell),0,ATK_TEXT_GRANULARITY_WORD,&start,&end);word=word||(value&&*value);g_free(value);leaks.word+=word;
        }return leaks;
    }
    void command(const std::string& name){const auto begin=g_get_monotonic_time();std::uint64_t mutation=0;Leaks leaks;
        if(name=="retire"){
            need(!retirement_done&&!erased,"cache probe retire order");auto* path=gtk_tree_model_get_path(GTK_TREE_MODEL(store),&retired);gtk_tree_view_collapse_row(GTK_TREE_VIEW(tree),path);gtk_tree_path_free(path);
            blank(&retired);gtk_tree_store_set(store,&retired,0,"",1,"",-1);gtk_tree_store_remove(store,&retired);
            if(collapsed){path=gtk_tree_model_get_path(GTK_TREE_MODEL(store),&chart);gtk_tree_view_collapse_row(GTK_TREE_VIEW(tree),path);gtk_tree_path_free(path);}retirement_done=true;
        }else if(name=="erase"){
            need(retirement_done&&!erased,"cache probe erase order");
            if(strategy!="blank")gtk_tree_view_set_model(GTK_TREE_VIEW(tree),nullptr);
            blank();gtk_tree_store_clear(store);
            if(strategy=="scrub"){
                for(auto* renderer:renderers)g_object_set(renderer,"text","",nullptr);
                for(auto* cell:held){auto* type=GTK_CELL_ACCESSIBLE_GET_CLASS(cell);need(type->update_cache,"cache probe public cache slot");type->update_cache(GTK_CELL_ACCESSIBLE(cell),FALSE);}
            }
            if(strategy!="blank"){gtk_tree_view_set_model(GTK_TREE_VIEW(tree),GTK_TREE_MODEL(store));}
            erased=true;mutation=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);leaks=inspect();
        }else if(name=="recover"){
            need(erased&&!recovered,"cache probe recovery order");GtkTreeIter parent,child;row(parent,nullptr,"FRESH_ROOT","FRESH_VALUE");row(child,&parent,"FRESH_POINT","FRESH_POINT_VALUE");gtk_tree_view_expand_all(GTK_TREE_VIEW(tree));recovered=true;leaks=inspect();
        }else if(name=="quit"){need(recovered,"cache probe quit order");gtk_main_quit();}
        else throw std::runtime_error("cache probe command");
        const auto callback=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);
        std::cout<<"{\"ack\":\""<<name<<"\",\"local_checked\":"<<((name=="erase"||name=="recover")?"true":"false")<<",\"callback_us\":"<<callback<<",\"mutation_us\":"<<mutation<<",\"held_cells\":"<<held.size()<<",\"text_leaks\":"<<leaks.text<<",\"name_leaks\":"<<leaks.name<<",\"count_leaks\":"<<leaks.count<<",\"word_leaks\":"<<leaks.word<<"}"<<std::endl;
    }
};
}
int main(int argc,char** argv){try{
    need(argc==3,"cache probe arguments");need(std::string(argv[2])=="collapsed"||std::string(argv[2])=="expanded","cache probe cohort");g_set_prgname("syspane-cache-erasure-probe");need(gtk_init_check(nullptr,nullptr),"cache probe display");Probe p(argv[1],std::string(argv[2])=="collapsed");
    need(fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK)==0,"cache probe stdin");
    const auto input=g_unix_fd_add(STDIN_FILENO,static_cast<GIOCondition>(G_IO_IN|G_IO_HUP|G_IO_ERR),+[](gint fd,GIOCondition flags,gpointer data)->gboolean{auto& p=*static_cast<Probe*>(data);try{
        need(!(flags&(G_IO_HUP|G_IO_ERR)),"cache probe unexpected EOF");char bytes[1024];const auto count=::read(fd,bytes,sizeof(bytes));if(count>0)p.input.append(bytes,static_cast<std::size_t>(count));need(p.input.size()<=4096,"cache probe input bound");std::size_t at;
        while((at=p.input.find('\n'))!=std::string::npos){const auto name=p.input.substr(0,at);p.input.erase(0,at+1);p.command(name);}
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';p.result=1;gtk_main_quit();return G_SOURCE_REMOVE;}return G_SOURCE_CONTINUE;},&p);
    const auto deadline=g_timeout_add_seconds(120,+[](gpointer data)->gboolean{static_cast<Probe*>(data)->result=1;gtk_main_quit();return G_SOURCE_REMOVE;},&p);
    std::cout<<"{\"ready\":true,\"rows\":3172,\"columns\":2,\"held_cells\":6344}"<<std::endl;gtk_main();
    for(auto id:{input,deadline}){if(g_main_context_find_source_by_id(nullptr,id))g_source_remove(id);}
    return p.result;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
