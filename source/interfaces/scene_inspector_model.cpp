#include "scene_inspector_model.hpp"
#include <glib.h>
namespace syspane::interfaces {
namespace {
using configuration::Json;using rendering::SurfaceFrame;using rendering::SurfaceText;
void need(bool b,const char* why){if(!b)throw protocol::Error(why);}
std::string number(const scene::ChartNumber& n){return n.index()==1?std::to_string(std::get<std::uint64_t>(n)):Json(std::get<double>(n)).dump();}
struct Project {
    const SurfaceFrame& frame;std::map<std::string,const SurfaceText*> widgets;
    std::map<std::string,std::vector<const scene::Node*>> children;
    std::set<std::string> keys,visited;std::size_t count=0,bytes=0;
    InspectorRow row(Json key,std::string item,std::string info){
        InspectorRow out{key.dump(),std::move(item),std::move(info),{}};
        need(++count<=65536&&keys.insert(out.key).second,"inspector.capacity");
        for(const auto* text:{&out.key,&out.item,&out.information}){
            need(text->find('\0')==std::string::npos&&g_utf8_validate(text->data(),static_cast<gssize>(text->size()),nullptr),"inspector.text");
            need(text->size()<=2097152-bytes,"inspector.capacity");bytes+=text->size();}
        return out;
    }
    std::vector<InspectorRow> widget(const scene::Node& node,unsigned depth){
        need(depth<=256&&visited.insert(node.id).second,"inspector.hierarchy");
        const auto& w=*widgets.at(node.id);Json key={frame.layout.scene_id,w.id};
        std::vector<InspectorRow> descendants;for(const auto* child:children[node.id]){auto next=widget(*child,depth+1);for(auto& item:next)descendants.push_back(std::move(item));}
        if(!w.presented){need(w.title.empty()&&w.text.empty()&&w.accessible.empty()&&w.fonts.empty()&&!w.table&&!w.chart&&!w.image&&w.notices.empty()&&!w.diagnostic,"inspector.hidden_payload");return descendants;}
        auto out=row(key,w.title,w.table?w.table->summary:w.chart?w.chart->accessible_summary:w.accessible);out.children=std::move(descendants);
        if(w.table){need(w.kind=="table"&&w.table->columns.size()==w.table->labels.size(),"inspector.frame");const auto& table=*w.table;
            for(const auto& r:table.rows){need(r.cells.size()==table.columns.size(),"inspector.frame");auto rk=key;rk.push_back("row");rk.push_back(r.producer);rk.push_back(r.epoch);rk.push_back(r.entity);
                auto child=row(rk,r.entity,"Producer "+r.producer+" | Epoch "+r.epoch+" | Generation "+std::to_string(r.generation));
                for(std::size_t c=0;c<r.cells.size();++c){auto ck=rk;ck.push_back(table.columns[c]);child.children.push_back(row(ck,table.labels[c]==table.columns[c]?table.columns[c]:table.labels[c]+" ["+table.columns[c]+"]",r.cells[c].accessible));}
                out.children.push_back(std::move(child));}}
        if(w.chart){need(w.kind=="chart"&&(w.chart->points.empty()||w.chart->identity),"inspector.frame");
            if(w.chart->identity){const auto& id=*w.chart->identity;
                for(const auto& p:w.chart->points){auto pk=key;pk.push_back("point");pk.push_back(Json::array({id.producer,id.epoch,id.entity,id.field,id.source,id.unit,id.clock_id,id.clock_scope,static_cast<int>(id.origin),id.integer}));pk.push_back(std::to_string(p.measured_ns));
                    out.children.push_back(row(pk,"Point "+std::to_string(p.measured_ns)+" ns",number(p.value)+(id.unit.empty()||id.unit=="1"?"":" "+id.unit)+"; generation "+std::to_string(p.generation)+(p.joins_previous?"; join":"; start")));}}}
        std::vector<InspectorRow> result;result.push_back(std::move(out));return result;
    }
    std::vector<InspectorRow> run(){
        need(frame.widgets.size()==frame.layout.nodes.size()&&frame.widgets.size()<=256,"inspector.frame");
        for(const auto& w:frame.widgets)need(!w.id.empty()&&widgets.emplace(w.id,&w).second,"inspector.frame");
        std::set<std::string> ids;for(const auto& n:frame.layout.nodes){need(ids.insert(n.id).second&&widgets.count(n.id)&&widgets.at(n.id)->kind==n.kind,"inspector.frame");
            need(n.parent.empty()||(widgets.count(n.parent)&&widgets.at(n.parent)->kind=="group"),"inspector.hierarchy");children[n.parent].push_back(&n);}
        std::vector<InspectorRow> out;for(const auto* n:children[""]){auto next=widget(*n,1);for(auto& item:next)out.push_back(std::move(item));}
        need(visited.size()==widgets.size(),"inspector.hierarchy");return out;
    }
};
}
std::vector<InspectorRow> inspector_rows(const rendering::SurfaceFrame& frame){return Project{frame,{},{},{},{},0,0}.run();}
}
