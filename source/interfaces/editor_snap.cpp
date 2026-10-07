#include "editor_snap.hpp"
#include <algorithm>
#include <array>
#include <cstdlib>
#include <set>
#include <tuple>
namespace syspane::interfaces {
namespace {
using U=scene::Unit;constexpr U limit=134217728;
void need(bool value){if(!value)throw protocol::Error("editor.snap_input");}
void bounded(U n){need(n>=-limit&&n<=limit);}
void rectangle(const scene::Rect& r){bounded(r.x);bounded(r.y);bounded(r.width);bounded(r.height);need(r.width>0&&r.height>0);bounded(r.x+r.width);bounded(r.y+r.height);}
U nearest(U n,U spacing){const U q=n/spacing,r=n%spacing;return (q+(std::abs(r)*2>=spacing?(n<0?-1:1):0))*spacing;}
std::array<U,3> anchors(U start,U extent){return {{start,start+extent/2,start+extent}};}
std::pair<U,std::optional<SnapGuide>> axis(const SnapInput& in,bool vertical){
    const U delta=vertical?in.dy:in.dx,start=vertical?in.selection.y:in.selection.x,extent=vertical?in.selection.height:in.selection.width;
    if(!delta||in.bypass||(!in.grid&&!in.guides)||(in.resize&&extent+delta<=0))return {delta,{}};
    const auto moving=anchors(start+(in.resize?0:delta),extent+(in.resize?delta:0));
    std::optional<SnapGuide> best;U correction=0;
    auto score=[](U offset,const SnapGuide& g){return std::make_tuple(std::abs(offset),g.source,g.position,g.target,g.moving,g.anchor);};
    auto consider=[&](const SnapGuide& g){const U offset=g.position-moving[g.moving];
        if(std::abs(offset)>in.threshold)return;
        if(!best||score(offset,g)<score(correction,*best)){best=g;correction=offset;}};
    if(in.guides){
        auto target=[&](const scene::Rect& box,GuideSource source,const std::string& id){const auto points=anchors(vertical?box.y:box.x,vertical?box.height:box.width);
            for(unsigned m=in.resize?2:0;m<3;++m)for(unsigned t=0;t<3;++t)consider({points[t],source,id,m,t});};
        target(in.area,GuideSource::area,"");for(const auto& t:in.siblings)target(t.box,GuideSource::sibling,t.id);
    }
    if(in.grid){const U origin=vertical?in.origin_y:in.origin_x;const unsigned m=in.resize?2:0;
        consider({origin+nearest(moving[m]-origin,in.spacing),GuideSource::grid,"",m,0});}
    return {delta+correction,best};
}
}
SnapResult snap(const SnapInput& in){
    rectangle(in.selection);rectangle(in.area);bounded(in.origin_x);bounded(in.origin_y);bounded(in.dx);bounded(in.dy);
    need(in.spacing>=scene::dip&&in.spacing<=256*scene::dip&&in.threshold>=0&&in.threshold<=16*scene::dip&&in.siblings.size()<=256);
    std::set<std::string> ids;for(const auto& t:in.siblings){need(protocol::identifier(t.id)&&ids.insert(t.id).second);rectangle(t.box);}
    const auto x=axis(in,false),y=axis(in,true);return {x.first,y.first,x.second,y.second};
}
}
