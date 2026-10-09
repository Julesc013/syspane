#include "layout.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <numeric>
#include <tuple>

namespace syspane::scene {
namespace {
using configuration::Json;
constexpr Unit limit=32768*dip,origin_limit=100000*dip;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
Unit right(const Rect& r){return r.x+r.width;}
Unit bottom(const Rect& r){return r.y+r.height;}
bool positive(const Rect& r){return r.width>0&&r.height>0;}
bool same(const Rect& a,const Rect& b){return std::tie(a.x,a.y,a.width,a.height)==std::tie(b.x,b.y,b.width,b.height);}
bool contains(const Rect& a,const Rect& b){return b.x>=a.x&&b.y>=a.y&&right(b)<=right(a)&&bottom(b)<=bottom(a);}
Rect intersection(const Rect& a,const Rect& b){
    const Unit x=std::max(a.x,b.x),y=std::max(a.y,b.y),r=std::min(right(a),right(b)),d=std::min(bottom(a),bottom(b));
    if(r<=x||d<=y)return {std::clamp(a.x,b.x,right(b)),std::clamp(a.y,b.y,bottom(b)),0,0};
    return {x,y,r-x,d-y};
}
Rect united(const Rect& a,const Rect& b){
    if(!positive(a))return b;
    if(!positive(b))return a;
    const auto x=std::min(a.x,b.x),y=std::min(a.y,b.y);
    return {x,y,std::max(right(a),right(b))-x,std::max(bottom(a),bottom(b))-y};
}
bool valid_rect(const Rect& r){return r.x>=-origin_limit&&r.x<=origin_limit&&r.y>=-origin_limit&&r.y<=origin_limit&&
    r.width>0&&r.width<=limit&&r.height>0&&r.height<=limit;}
Rect safe_region(const Display& d){
    const auto& w=d.work;const auto& s=d.safe;
    Rect work{w.x+std::min(s.left,w.width),w.y+std::min(s.top,w.height),std::max(Unit{0},w.width-s.left-s.right),std::max(Unit{0},w.height-s.top-s.bottom)};
    if(!positive(work))return {work.x,work.y,0,0};
    std::vector<Rect> obstacles;std::vector<Unit> ys{work.y,bottom(work)};
    for(const auto& input:d.exclusions){const auto e=intersection(input,work);if(positive(e)){obstacles.push_back(e);ys.push_back(e.y);ys.push_back(bottom(e));}}
    std::sort(ys.begin(),ys.end());ys.erase(std::unique(ys.begin(),ys.end()),ys.end());Rect best{work.x,work.y,0,0};
    const auto choose=[&](const Rect& v){
        const auto area=v.width*v.height,old=best.width*best.height;
        if(area>old||(area==old&&std::make_tuple(v.y,v.x,-v.width,-v.height)<std::make_tuple(best.y,best.x,-best.width,-best.height)))best=v;
    };
    for(std::size_t a=0;a+1<ys.size();++a)for(std::size_t b=a+1;b<ys.size();++b){
        std::vector<std::pair<Unit,Unit>> blocked;
        for(const auto& e:obstacles)if(e.y<ys[b]&&bottom(e)>ys[a])blocked.emplace_back(e.x,right(e));
        std::sort(blocked.begin(),blocked.end());auto cursor=work.x;
        for(const auto& span:blocked){if(span.first>cursor)choose({cursor,ys[a],span.first-cursor,ys[b]-ys[a]});cursor=std::max(cursor,span.second);}
        if(cursor<right(work))choose({cursor,ys[a],right(work)-cursor,ys[b]-ys[a]});
    }
    return best;
}
Unit nearest(const Json& v){return static_cast<Unit>(std::round(v.get<double>()*dip));}
Unit up(const Json& v){return static_cast<Unit>(std::ceil(v.get<double>()*dip));}
Unit down(const Json& v){return static_cast<Unit>(std::floor(v.get<double>()*dip));}
Unit floor_div(Unit n,Unit d){return n/d-(n%d<0?1:0);}
Unit ceil_div(Unit n,Unit d){return -floor_div(-n,d);}
Rect pixels(const Rect& v,const Display& d){
    const Unit den=static_cast<Unit>(d.scale_denominator)*dip,num=d.scale_numerator;
    const auto x=d.pixel_x+floor_div((v.x-d.bounds.x)*num,den),y=d.pixel_y+floor_div((v.y-d.bounds.y)*num,den);
    if(!positive(v))return {x,y,0,0};
    return {x,y,d.pixel_x+ceil_div((right(v)-d.bounds.x)*num,den)-x,d.pixel_y+ceil_div((bottom(v)-d.bounds.y)*num,den)-y};
}
int priority(const Json& widget){const auto& p=widget["priority"];return p=="essential"?0:(p=="normal"?1:2);}
std::vector<Unit> fit(std::vector<Unit> sizes,const std::vector<Unit>& minima,const std::vector<int>& priorities,Unit available){
    auto deficit=std::accumulate(sizes.begin(),sizes.end(),Unit{0})-std::max(Unit{0},available);
    for(int p=2;p>=0&&deficit>0;--p)for(;;){
        std::vector<std::size_t> active;for(std::size_t i=0;i<sizes.size();++i)if(priorities[i]==p&&sizes[i]>minima[i])active.push_back(i);
        if(active.empty()||deficit<=0)break;
        const auto count=static_cast<Unit>(active.size()),share=deficit/count,extra=deficit%count;
        for(std::size_t j=0;j<active.size();++j){const auto i=active[j];const auto take=std::min(sizes[i]-minima[i],share+(static_cast<Unit>(j)<extra?1:0));sizes[i]-=take;deficit-=take;}
    }
    return sizes;
}
struct Item {
    const Json* widget=nullptr;const Json* layout=nullptr;const Display* display=nullptr;
    std::string id,parent,kind;int variant=-1;bool group=false,fixed=false;
    std::array<Unit,2> minimum{},preferred{},maximum{};
    std::vector<std::string> children;
};
class Engine {
    struct Checked {};
    static const Json& checked(const Json& scene){configuration::validate_scene_document(scene);return scene;}
    Engine(const Json& scene,const Topology& topology,const std::map<std::string,Metrics>& metrics,Checked):scene_(scene),topology_(topology),metrics_(metrics){
        validate_environment();
        for(const auto& widget:scene_["widgets"])widgets_.emplace(widget["id"].get<std::string>(),&widget);
        std::size_t leaves=0;for(const auto& row:widgets_)if((*row.second)["kind"]!="group")++leaves;
        need(metrics_.size()==leaves,"layout.metrics");
        for(const auto& row:metrics_){const auto found=widgets_.find(row.first);need(found!=widgets_.end()&&(*found->second)["kind"]!="group","layout.metrics");
            const auto& m=row.second;need(m.minimum.width>0&&m.minimum.height>0&&m.preferred.width>=m.minimum.width&&m.preferred.height>=m.minimum.height&&
                m.preferred.width<=limit&&m.preferred.height<=limit,"layout.metrics");}
        plan_.scene_id=scene_["scene_id"];plan_.revision=scene_["revision"];plan_.nodes.reserve(widgets_.size());
        for(const auto& root:scene_["roots"])select(root.get<std::string>(),"","");
        for(const auto& root:scene_["roots"])measure(items_.at(root.get<std::string>()));
    }
public:
    Engine(const Json& scene,const Topology& topology,const std::map<std::string,Metrics>& metrics):Engine(checked(scene),topology,metrics,Checked{}){}
    Engine(const configuration::ValidatedAuthored& value,const Topology& topology,const std::map<std::string,Metrics>& metrics):Engine(value.documents().scene,topology,metrics,Checked{}){}
    Plan run(){
        for(const auto& root:scene_["roots"]){auto& item=items_.at(root.get<std::string>());const auto area=regions_.at(item.display->id);place(item,box_in(item,area,true),area);}
        for(std::size_t a=0;a<plan_.nodes.size();++a)for(std::size_t b=a+1;b<plan_.nodes.size();++b){
            const auto& x=plan_.nodes[a];const auto& y=plan_.nodes[b];
            if(x.parent==y.parent&&x.display==y.display&&positive(intersection(x.visible,y.visible)))diagnose(std::min(x.id,y.id),"layout.overlap",std::max(x.id,y.id));
        }
        auto& d=plan_.diagnostics;std::sort(d.begin(),d.end(),[](const auto& a,const auto& b){return std::tie(a.widget,a.code,a.related)<std::tie(b.widget,b.code,b.related);});
        d.erase(std::unique(d.begin(),d.end(),[](const auto& a,const auto& b){return std::tie(a.widget,a.code,a.related)==std::tie(b.widget,b.code,b.related);}),d.end());
        if(plan_.state!=State::alternative&&!d.empty())plan_.state=State::degraded;
        return std::move(plan_);
    }
private:
    void diagnose(const std::string& id,const char* code,const std::string& related=""){
        need(plan_.diagnostics.size()<65536,"layout.capacity");plan_.diagnostics.push_back({id,code,related});
    }
    void validate_environment(){
        need(!topology_.displays.empty()&&topology_.displays.size()<=16&&topology_.roles.size()<=256,"layout.topology");
        for(const auto& d:topology_.displays){
            need(protocol::identifier(d.id)&&displays_.emplace(d.id,&d).second&&valid_rect(d.bounds)&&valid_rect(d.work)&&contains(d.bounds,d.work)&&
                d.exclusions.size()<=16&&d.pixel_x>=-16777216&&d.pixel_x<=16777216&&d.pixel_y>=-16777216&&d.pixel_y<=16777216&&
                d.scale_numerator>=1&&d.scale_numerator<=16&&d.scale_denominator>=1&&d.scale_denominator<=16&&
                d.scale_numerator*4>=d.scale_denominator&&d.scale_numerator<=d.scale_denominator*8,"layout.topology");
            for(const auto v:{d.safe.left,d.safe.top,d.safe.right,d.safe.bottom})need(v>=0&&v<=limit,"layout.topology");
            for(const auto& e:d.exclusions)need(valid_rect(e)&&contains(d.bounds,e),"layout.topology");
            regions_.emplace(d.id,safe_region(d));
        }
        need(displays_.count(topology_.fallback)!=0,"layout.topology");
        for(const auto& row:topology_.roles){need(protocol::identifier(row.first)&&row.second.size()<=16,"layout.topology");std::set<std::string> unique;
            for(const auto& id:row.second)need(protocol::identifier(id)&&unique.insert(id).second,"layout.topology");}
    }
    const Display* assignment(const Json& widget){
        std::vector<const Display*> candidates;const auto& value=widget["display"];
        if(value.contains("local_id")){const auto found=displays_.find(value["local_id"].get<std::string>());if(found!=displays_.end())candidates.push_back(found->second);}
        else {const auto role=topology_.roles.find(value["role"].get<std::string>());if(role!=topology_.roles.end())for(const auto& id:role->second){const auto found=displays_.find(id);if(found!=displays_.end())candidates.push_back(found->second);}}
        if(candidates.size()==1)return candidates.front();
        diagnose(widget["id"],candidates.empty()?"display.missing":"display.ambiguous");return displays_.at(topology_.fallback);
    }
    void select(const std::string& id,const std::string& parent,const std::string& root_display){
        Item item;item.id=id;item.parent=parent;item.widget=widgets_.at(id);item.group=(*item.widget)["kind"]=="group";item.display=assignment(*item.widget);
        need(root_display.empty()||root_display==item.display->id,"layout.display_conflict");const auto area=regions_.at(item.display->id);
        if(!positive(area)){diagnose(id,"layout.no_region");plan_.state=State::alternative;}
        const auto& layouts=(*item.widget)["layout"];item.layout=&layouts["base"];
        if(layouts.contains("breakpoints")){int index=0;for(const auto& point:layouts["breakpoints"]){if(area.width>=up(point["min_width_dip"])){item.layout=&point["layout"];item.variant=index;}++index;}}
        item.kind=(*item.layout)["kind"];item.fixed=item.kind=="fixed";
        if(item.group)for(const auto& child:(*item.widget)["children"])item.children.push_back(child.get<std::string>());
        auto& inserted=items_.emplace(id,std::move(item)).first->second;
        for(const auto& child:inserted.children)select(child,id,inserted.display->id);
    }
    std::vector<Item*> flowing(Item& item){std::vector<Item*> result;for(const auto& id:item.children)if(!items_.at(id).fixed)result.push_back(&items_.at(id));return result;}
    void measure(Item& item){
        for(const auto& child:item.children)measure(items_.at(child));
        const auto& layout=*item.layout;
        if(item.kind=="fixed"||item.kind=="canvas"){
            item.minimum=item.preferred={up(layout["width"]),up(layout["height"])};
            if(!item.group){const auto& m=metrics_.at(item.id);item.minimum[0]=std::max(item.minimum[0],m.minimum.width);item.minimum[1]=std::max(item.minimum[1],m.minimum.height);
                if(item.minimum!=item.preferred)diagnose(item.id,"layout.fixed_size");
                item.preferred=item.minimum;}
            item.maximum=item.preferred;return;
        }
        if(item.kind=="flow"){
            const auto& m=metrics_.at(item.id);const std::array<Unit,2> mn{m.minimum.width,m.minimum.height},pr{m.preferred.width,m.preferred.height};
            for(unsigned axis=0;axis<2;++axis){const auto& bound=layout[axis?"height":"width"];
                item.minimum[axis]=std::max(up(bound["min"]),mn[axis]);item.maximum[axis]=down(bound["max"]);
                if(item.maximum[axis]<item.minimum[axis]){diagnose(item.id,"layout.constraint");item.maximum[axis]=item.minimum[axis];}
                item.preferred[axis]=std::clamp(std::max(nearest(bound["preferred"]),pr[axis]),item.minimum[axis],item.maximum[axis]);}
            return;
        }
        auto children=flowing(item);const auto gap=up(layout["gap_dip"]);
        if(!children.empty()){
            if(item.kind=="stack"){
                const unsigned main=layout["axis"]=="horizontal"?0:1,cross=1-main;
                for(const auto* child:children){item.minimum[main]+=child->minimum[main];item.preferred[main]+=child->preferred[main];
                    item.minimum[cross]=std::max(item.minimum[cross],child->minimum[cross]);item.preferred[cross]=std::max(item.preferred[cross],child->preferred[cross]);}
                item.minimum[main]+=gap*static_cast<Unit>(children.size()-1);item.preferred[main]+=gap*static_cast<Unit>(children.size()-1);
            }else{
                const auto columns=layout["columns"].get<std::size_t>(),rows=(children.size()+columns-1)/columns;
                std::vector<Unit> col_min(columns),col_pref(columns),row_min(rows),row_pref(rows);
                for(std::size_t i=0;i<children.size();++i){const auto* c=children[i];col_min[i%columns]=std::max(col_min[i%columns],c->minimum[0]);col_pref[i%columns]=std::max(col_pref[i%columns],c->preferred[0]);
                    row_min[i/columns]=std::max(row_min[i/columns],c->minimum[1]);row_pref[i/columns]=std::max(row_pref[i/columns],c->preferred[1]);}
                item.minimum={std::accumulate(col_min.begin(),col_min.end(),gap*static_cast<Unit>(columns-1)),std::accumulate(row_min.begin(),row_min.end(),gap*static_cast<Unit>(rows-1))};
                item.preferred={std::accumulate(col_pref.begin(),col_pref.end(),gap*static_cast<Unit>(columns-1)),std::accumulate(row_pref.begin(),row_pref.end(),gap*static_cast<Unit>(rows-1))};
            }
        }
        for(const auto& id:item.children){const auto& c=items_.at(id);if(!c.fixed)continue;
            for(unsigned axis=0;axis<2;++axis){const auto extent=nearest((*c.layout)[axis?"y":"x"])+c.preferred[axis];item.minimum[axis]=std::max(item.minimum[axis],extent);item.preferred[axis]=std::max(item.preferred[axis],extent);}}
        item.maximum={origin_limit*256,origin_limit*256};
    }
    Unit fit_axis(const Item& item,unsigned axis,Unit available)const{
        if(item.kind=="fixed"||item.kind=="canvas")return item.preferred[axis];
        if(item.group)return std::max(item.minimum[axis],available);
        const auto wanted=(*item.layout)["anchor"]=="stretch"?available:std::min(item.preferred[axis],available);
        return std::clamp(wanted,item.minimum[axis],item.maximum[axis]);
    }
    Unit offset(const Item& item,Unit available,Unit size)const{
        if(item.group||available<=size)return 0;
        const auto& anchor=(*item.layout)["anchor"];return anchor=="end"?available-size:(anchor=="center"?(available-size)/2:0);
    }
    Rect box_in(const Item& item,const Rect& slot,bool root=false)const{
        if(item.fixed)return {slot.x+nearest((*item.layout)["x"]),slot.y+nearest((*item.layout)["y"]),item.preferred[0],item.preferred[1]};
        if(root&&item.group&&item.kind!="canvas")return slot;
        const auto width=fit_axis(item,0,slot.width),height=fit_axis(item,1,slot.height);
        return {slot.x+offset(item,slot.width,width),slot.y+offset(item,slot.height,height),width,height};
    }
    void stack_boxes(Item& item,const Rect& box,std::map<std::string,Rect>& boxes){
        auto children=flowing(item);if(children.empty())return;
        const bool horizontal=item.kind=="stack"&&(*item.layout)["axis"]=="horizontal";
        const unsigned main=horizontal?0:1,cross=1-main;const Unit gap=item.kind=="stack"?up((*item.layout)["gap_dip"]):0;
        std::vector<Unit> sizes,minima;std::vector<int> priorities;
        for(const auto* c:children){sizes.push_back(c->preferred[main]);minima.push_back(c->minimum[main]);priorities.push_back(priority(*c->widget));}
        sizes=fit(std::move(sizes),minima,priorities,(horizontal?box.width:box.height)-gap*static_cast<Unit>(children.size()-1));
        Unit cursor=horizontal?box.x:box.y;
        for(std::size_t i=0;i<children.size();++i){auto& c=*children[i];const auto available=horizontal?box.height:box.width,length=fit_axis(c,cross,available),shift=offset(c,available,length);
            boxes.emplace(c.id,horizontal?Rect{cursor,box.y+shift,sizes[i],length}:Rect{box.x+shift,cursor,length,sizes[i]});cursor+=sizes[i]+gap;}
    }
    void grid_boxes(Item& item,const Rect& box,std::map<std::string,Rect>& boxes){
        const auto children=flowing(item);if(children.empty())return;
        const auto columns=(*item.layout)["columns"].get<std::size_t>(),rows=(children.size()+columns-1)/columns;const auto gap=up((*item.layout)["gap_dip"]);
        const auto available=std::max(Unit{0},box.width-gap*static_cast<Unit>(columns-1)),count=static_cast<Unit>(columns);
        std::vector<Unit> widths(columns),heights(rows),minima(rows);std::vector<int> priorities(rows,2);
        for(std::size_t i=0;i<columns;++i)widths[i]=available/count+(static_cast<Unit>(i)<available%count?1:0);
        for(std::size_t i=0;i<children.size();++i){const auto* c=children[i];widths[i%columns]=std::max(widths[i%columns],c->minimum[0]);heights[i/columns]=std::max(heights[i/columns],c->preferred[1]);
            minima[i/columns]=std::max(minima[i/columns],c->minimum[1]);priorities[i/columns]=std::min(priorities[i/columns],priority(*c->widget));}
        heights=fit(std::move(heights),minima,priorities,box.height-gap*static_cast<Unit>(rows-1));Unit y=box.y;
        for(std::size_t row=0;row<rows;++row){Unit x=box.x;for(std::size_t col=0;col<columns;++col){const auto i=row*columns+col;
                if(i<children.size())boxes.emplace(children[i]->id,box_in(*children[i],{x,y,widths[col],heights[row]}));
                x+=widths[col]+gap;}
            y+=heights[row]+gap;}
    }
    void place(Item& item,const Rect& box,const Rect& clip){
        const auto index=plan_.nodes.size();Node node;node.id=item.id;node.parent=item.parent;node.display=item.display->id;node.kind=(*item.widget)["kind"];node.variant=item.variant;
        node.box=box;node.visible=intersection(box,clip);node.content=box;node.pixels=pixels(node.visible,*item.display);node.clipped=positive(box)&&!same(box,node.visible);
        plan_.nodes.push_back(node);
        if(item.group){std::map<std::string,Rect> boxes;
            if(item.kind=="grid")grid_boxes(item,box,boxes);else stack_boxes(item,box,boxes);
            for(const auto& id:item.children){auto& child=items_.at(id);place(child,child.fixed?box_in(child,box):boxes.at(id),node.visible);
                plan_.nodes[index].content=united(plan_.nodes[index].content,plan_.nodes[indices_.at(id)].content);}
        }
        auto& result=plan_.nodes[index];if(result.clipped||(positive(result.content)&&!contains(box,result.content))){
            result.overflow=item.group&&item.layout->value("overflow",std::string("diagnose"))=="scroll"?"scroll":"diagnose";diagnose(item.id,"layout.overflow");}
        if(!item.group&&result.clipped)plan_.state=State::alternative;
        indices_.emplace(item.id,index);
    }
    const Json& scene_;const Topology& topology_;const std::map<std::string,Metrics>& metrics_;
    std::map<std::string,const Display*> displays_;std::map<std::string,Rect> regions_;
    std::map<std::string,const Json*> widgets_;std::map<std::string,Item> items_;std::map<std::string,std::size_t> indices_;Plan plan_;
};
}
Plan resolve(const configuration::Json& scene,const Topology& topology,const std::map<std::string,Metrics>& metrics){return Engine(scene,topology,metrics).run();}
Plan resolve(const configuration::ValidatedAuthored& value,const Topology& topology,const std::map<std::string,Metrics>& metrics){return Engine(value,topology,metrics).run();}
}
