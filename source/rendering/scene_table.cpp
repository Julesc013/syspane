#include "scene_table.hpp"
#include <algorithm>
#include <array>
#include <tuple>
namespace syspane::rendering {
namespace {
using configuration::Json;using Code=scene::BindingCode;using Key=std::tuple<std::string,std::string,std::string>;
void need(bool ok,const char* why){if(!ok)throw protocol::Error(why);}
int rank(Code c){switch(c){case Code::matched:return 0;case Code::empty:return 1;case Code::pending:return 2;case Code::unsupported:return 3;case Code::ambiguous:return 4;case Code::capacity:return 5;case Code::invalid:return 6;default:return 7;}}
const char* label(Code c){switch(c){case Code::pending:return "Waiting";case Code::unsupported:return "Unsupported field";case Code::ambiguous:return "Ambiguous selection";case Code::capacity:return "Capacity exceeded";default:return "Invalid source";}}
Key key(const scene::BindingRow& r){return {r.producer,r.epoch,r.entity};}
}
std::size_t surface_text_bytes(const SurfaceText& s){
    std::size_t size=s.id.size()+s.kind.size()+s.text.size()+s.accessible.size();
    for(const auto& f:s.fonts)size+=f.size();
    if(s.chart)size+=s.chart->summary.size();
    if(s.table){const auto& t=*s.table;size+=t.summary.size();for(const auto& c:t.columns)size+=c.size();for(const auto& c:t.labels)size+=c.size();
        for(const auto& r:t.rows){size+=r.producer.size()+r.epoch.size()+r.entity.size();for(const auto& c:r.cells)size+=c.text.size()+c.accessible.size();}}
    return size;
}
SurfaceText compose_table(const Json& w,const std::vector<scene::BindingInput>& inputs,std::uint64_t now,
                         const std::function<SurfaceCell(const scene::BindingRow&)>& format){
    const auto& bindings=w["bindings"];need(!bindings.empty(),"surface.unsupported");need(bindings.size()<=16,"surface.capacity");
    Json shape;std::set<std::string> fields;
    for(const auto& b:bindings){need(b["kind"]=="selector"&&b["mode"]=="collection","surface.unsupported");
        need(b["limit"].get<unsigned>()<=64,"surface.capacity");auto query=b;query.erase("field");
        if(shape.is_null())shape=query;else need(query==shape,"surface.unsupported");
        need(fields.insert(b["field"].get<std::string>()).second,"surface.unsupported");}
    SurfaceText out;out.id=w["id"];out.kind="table";out.text=w["title"];out.table.emplace();auto& t=*out.table;
    Code state=Code::matched;bool first=true;std::map<Key,std::size_t> indexes;
    for(const auto& b:bindings){t.labels.push_back(w.contains("content")?w["content"]["columns"][t.columns.size()]["label"]:b["field"]);t.columns.push_back(b["field"]);
        scene::project_binding(b,inputs,now,[&](const auto& frame){
            if(frame.code==Code::denied)throw protocol::Error("policy.denied");
            if(rank(frame.code)>rank(state))state=frame.code;
            if(frame.code!=Code::matched||state!=Code::matched)return;
            need(frame.rows.size()*bindings.size()<=256,"surface.capacity");
            if(first){t.total=frame.total;t.truncated=frame.truncated;
                for(const auto& row:frame.rows){need(indexes.emplace(key(row),t.rows.size()).second,"surface.table_identity");
                    t.rows.push_back({row.producer,row.epoch,row.entity,row.generation,{}});}}
            else need(frame.total==t.total&&frame.truncated==t.truncated&&frame.rows.size()==t.rows.size(),"surface.table_identity");
            std::set<Key> seen;
            for(const auto& row:frame.rows){auto found=indexes.find(key(row));need(found!=indexes.end()&&seen.insert(key(row)).second,"surface.table_identity");
                auto& target=t.rows[found->second];need(target.generation==row.generation,"surface.table_identity");target.cells.push_back(format(row));
                need(surface_text_bytes(out)<=262144,"surface.capacity");}
        });first=false;
    }
    if(state!=Code::matched){t.rows.clear();t.columns.clear();t.labels.clear();t.total=0;t.truncated=false;}
    t.summary=state==Code::matched||state==Code::empty?"Showing "+std::to_string(t.rows.size())+" of "+std::to_string(t.total)+" rows":label(state);
    out.accessible=out.text+"\n"+t.summary;
    for(const auto& row:t.rows){need(row.cells.size()==t.columns.size(),"surface.table_identity");
        out.accessible+="\nRow "+row.producer+"/"+row.epoch+"/"+row.entity;
        for(std::size_t i=0;i<row.cells.size();++i){out.accessible+="\n"+(t.labels[i]==t.columns[i]?t.columns[i]:t.labels[i]+" ["+t.columns[i]+"]")+": "+row.cells[i].accessible;need(surface_text_bytes(out)<=262144,"surface.capacity");}}
    return out;
}
TextRaster raster_table(const TextRequest& request,SurfaceText& widget,std::size_t capacity){
    need(widget.table.has_value(),"surface.table_identity");auto& table=*widget.table;
    TextRequest q=request;q.wrap_units.reset();
    const auto bg=request.contrast=="light"?"#ffffffff":request.contrast=="dark"?"#000000ff":request.theme["tokens"]["background"].get<std::string>();
    if(request.contrast!="authored")q.theme["tokens"]["foreground"]=request.contrast=="light"?"#000000ff":"#ffffffff";
    q.contrast="authored";q.theme["tokens"]["background"]="#00000000";
    std::vector<TextRaster> parts;std::size_t retained=0;std::set<std::string> fonts;
    const auto add=[&](const std::string& text){need(retained<capacity,"surface.capacity");q.text=text;q.pixel_budget=std::min(std::size_t{4194304},capacity-retained);
        auto raster=render_text(q);need(!raster.missing_glyphs,"surface.glyphs");retained+=static_cast<std::size_t>(raster.width)*raster.height;
        fonts.insert(raster.fonts.begin(),raster.fonts.end());parts.push_back(std::move(raster));return parts.size()-1;};
    const auto title=add(widget.text),summary=add(table.summary);std::vector<std::size_t> headers;std::vector<std::vector<std::size_t>> cells;
    for(const auto& name:table.labels)headers.push_back(add(name));
    for(const auto& row:table.rows){cells.emplace_back();for(const auto& c:row.cells)cells.back().push_back(add(c.text));}
    const unsigned horizontal=(8*q.numerator+q.denominator-1)/q.denominator,vertical=(4*q.numerator+q.denominator-1)/q.denominator;
    struct Placement {unsigned x,y;std::size_t part;};std::vector<Placement> placements{{0,0,title},{0,parts[title].height+vertical,summary}};
    unsigned width=std::max(parts[title].width,parts[summary].width),height=parts[title].height+vertical+parts[summary].height;
    if(!headers.empty()){
        std::vector<unsigned> widths;unsigned header_height=0;
        for(std::size_t c=0;c<headers.size();++c){unsigned w=parts[headers[c]].width;header_height=std::max(header_height,parts[headers[c]].height);
            for(const auto& row:cells)w=std::max(w,parts[row[c]].width);
            widths.push_back(w);}
        unsigned x=0;const auto header_y=height+vertical;
        for(std::size_t c=0;c<headers.size();++c){placements.push_back({x,header_y,headers[c]});x+=widths[c]+(c+1<headers.size()?horizontal:0);}
        width=std::max(width,x);height=header_y+header_height;
        for(std::size_t r=0;r<cells.size();++r){x=0;unsigned row_height=0;const auto y=height+vertical;
            for(std::size_t c=0;c<cells[r].size();++c){const auto part=cells[r][c];placements.push_back({x,y,part});row_height=std::max(row_height,parts[part].height);
                table.rows[r].cells[c].pixels={x,y,parts[part].width,parts[part].height};x+=widths[c]+horizontal;}
            height=y+row_height;}
    }
    const auto pixels=static_cast<std::size_t>(width)*height;
    need(width<=2048&&height<=2048&&pixels<=4194304&&retained<=capacity&&pixels<=capacity-retained,"surface.capacity");
    TextRaster result;result.width=width;result.height=height;result.fonts.assign(fonts.begin(),fonts.end());result.rgba.resize(pixels*4);
    std::array<unsigned,4> background{};for(unsigned c=0;c<4;++c)background[c]=static_cast<unsigned>(std::stoul(bg.substr(1+c*2,2),nullptr,16));
    for(unsigned c=0;c<3;++c)background[c]=(background[c]*background[3]+127)/255;
    for(std::size_t p=0;p<pixels;++p)for(unsigned c=0;c<4;++c)result.rgba[p*4+c]=static_cast<unsigned char>(background[c]);
    for(const auto& place:placements){const auto& src=parts[place.part];
        for(unsigned y=0;y<src.height;++y)for(unsigned x=0;x<src.width;++x){const auto a=(static_cast<std::size_t>(y)*src.width+x)*4;
            const auto b=(static_cast<std::size_t>(place.y+y)*width+place.x+x)*4;const auto inverse=255-src.rgba[a+3];
            for(unsigned c=0;c<4;++c)result.rgba[b+c]=static_cast<unsigned char>(src.rgba[a+c]+(result.rgba[b+c]*inverse+127)/255);}}
    return result;
}
}
