#pragma once
#include "scene_table.hpp"
#include <fstream>
namespace table_raster_probe {
using namespace fixture;
inline Json rect(const s::Rect& r){return Json::array({r.x,r.y,r.width,r.height});}
inline Json draw(const Json& input,const std::string& output,bool shared,unsigned iteration){
    v::TextRequest q;q.theme={{"schema_version","0.1.0"},{"theme_id","test"},{"name","Table raster fixture"},
        {"tokens",{{"foreground","#ffffffff"},{"background",input.value("background","#00000000")},{"warning","#ff8000ff"},{"error","#ff0000ff"},{"muted","#808080ff"}}},
        {"font",{{"family","Noto Sans"},{"size_dip",9}}},{"motion","none"}};
    if(input.value("roles",false)){q.theme["schema_version"]="0.2.0";q.theme["font"]["weight"]=400;q.theme["font"]["style"]="normal";
        for(const auto& pair:std::vector<std::pair<std::string,int>>{{"label",9},{"value",14},{"diagnostic",18}})q.theme["font_roles"][pair.first]={{"family","Noto Sans"},{"size_dip",pair.second},{"weight",400},{"style","normal"}};}
    q.contrast=input.value("contrast","authored");q.numerator=input.value("numerator",1U);q.denominator=input.value("denominator",1U);
    v::SurfaceText widget;widget.id="table";widget.kind="table";widget.title=widget.text="same";widget.table.emplace();auto& table=*widget.table;table.summary="same";
    const auto columns=input["columns"].get<unsigned>(),rows=input["rows"].get<unsigned>();
    for(unsigned col=0;col<columns;++col){table.columns.push_back("field:"+std::to_string(col));table.labels.push_back("same");}
    for(unsigned row=0;row<rows;++row){table.rows.push_back({"P","E","entity:"+std::to_string(row),1,{}});
        for(unsigned col=0;col<columns;++col){std::string text="same";const auto pattern=input["pattern"].get<std::string>();
            if(pattern=="unique")text="cell "+std::to_string(row)+"/"+std::to_string(col);
            if(pattern=="mixed")text=col==3?"network.interface\nConfigured":std::to_string((col+1)*1000+row)+"\nCurrent";
            if(input.value("changed",false)&&iteration&&row==0&&col==0)text="changed composition";
            if(input.value("invalid",false)&&row==2&&col==0)text="bad\x01";
            table.rows.back().cells.push_back({text,text,{},{}});if(input.value("blocks",false))table.rows.back().cells.back().blocks={{"value",text},{"diagnostic","Configured"}};}}
    const auto capacity=input.value("capacity",std::size_t{16777216});v::TextSession session;
    try{auto raster=v::raster_table(q,widget,capacity,shared?&session:nullptr);
        std::ofstream pixels(output,std::ios::binary);pixels.write(reinterpret_cast<const char*>(raster.rgba.data()),static_cast<std::streamsize>(raster.rgba.size()));pixels.close();need(static_cast<bool>(pixels),"fixture output");
        Json cells=Json::array();for(const auto& row:table.rows)for(const auto& cell:row.cells)cells.push_back(rect(cell.pixels));
        return {{"width",raster.width},{"height",raster.height},{"fonts",raster.fonts},{"cells",cells},{"pixel_bytes",raster.rgba.size()}};
    }catch(const p::Error& e){return {{"error",e.what()}};}
}
inline int run(const std::string& root,const std::string& id,const std::string& output,bool shared){
    const auto cases=read(root+"/../../../tests/scene","table-raster-cases.json");for(const auto& input:cases["cases"])if(input["id"]==id){
        Json results=Json::array();for(unsigned i=0;i<(input.value("changed",false)?2U:1U);++i)results.push_back(draw(input,output+"."+std::to_string(i),shared,i));
        std::cout<<Json({{"results",results}}).dump()<<'\n';return 0;}
    throw std::runtime_error("unknown table raster case");
}
}
