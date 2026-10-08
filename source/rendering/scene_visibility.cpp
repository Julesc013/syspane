#include "scene_visibility.hpp"
#include "scene_table.hpp"
#include "visibility.hpp"
#include <algorithm>
namespace syspane::rendering {
namespace {
namespace s=scene;
void need(bool ok,const char* code){if(!ok)throw protocol::Error(code);}
const char* label(s::VisibilityCode code){switch(code){
    case s::VisibilityCode::pending:return "Waiting";case s::VisibilityCode::empty:return "No match";
    case s::VisibilityCode::unsupported:return "Unsupported";case s::VisibilityCode::ambiguous:return "Ambiguous";
    case s::VisibilityCode::capacity:return "Capacity";case s::VisibilityCode::lease_lost:return "Source lost";
    case s::VisibilityCode::unavailable:return "Unavailable";case s::VisibilityCode::stale:return "Stale";
    case s::VisibilityCode::unit_mismatch:return "Unit mismatch";case s::VisibilityCode::type_mismatch:return "Type mismatch";
    default:return "Invalid";
}}
bool intersects(const s::Rect& a,const s::Rect& b){return a.x<b.x+b.width&&b.x<a.x+a.width&&a.y<b.y+b.height&&b.y<a.y+a.height;}
}
void condition_surface(const SurfaceConfig& cfg,const std::vector<s::BindingInput>& inputs,std::uint64_t now,
    SurfaceFrame& frame,std::map<std::string,SurfaceText>& texts,std::map<std::string,TextRaster>& rasters,
    std::size_t display_pixels,std::size_t& leaf_pixels){
    if(cfg.authored.scene.at("schema_version")!="0.5.0")return;
    need(cfg.experimental_visibility,"surface.visibility_unavailable");
    s::project_scene_visibility(cfg.authored.scene,inputs,now,[&](const s::VisibilityScene& view){
        need(view.code!=s::VisibilitySceneCode::restricted,"policy.denied");need(view.code!=s::VisibilitySceneCode::capacity,"surface.capacity");
        std::map<std::string,const s::VisibilityNode*> decisions;
        std::map<std::string,std::vector<std::string>> inherited;std::map<std::string,std::string> own;
        std::map<std::string,bool> empty_groups;
        for(const auto& w:cfg.authored.scene.at("widgets"))if(w.at("kind")=="group")empty_groups.emplace(w.at("id"),w.at("children").empty());
        for(const auto& d:view.diagnostics)own.emplace(d.id,"Visibility ("+d.id+"): "+label(d.code));
        for(const auto& node:view.nodes){decisions.emplace(node.id,&node);auto& lines=inherited[node.id];if(!node.parent.empty())lines=inherited.at(node.parent);
            const auto found=own.find(node.id);if(found!=own.end())lines.push_back(found->second);}
        std::vector<std::pair<std::string,s::Rect>> warnings;
        for(const auto& node:frame.layout.nodes){const auto& decision=*decisions.at(node.id);if(decision.show_content)continue;
            auto& out=texts.at(node.id);auto lines=inherited.at(node.id);
            for(const auto& notice:out.notices)if(std::find(lines.begin(),lines.end(),notice)==lines.end())lines.push_back(notice);
            const auto old=rasters.find(node.id);if(old!=rasters.end()){leaf_pixels-=static_cast<std::size_t>(old->second.width)*old->second.height;rasters.erase(old);}
            const auto title=out.title;auto mandatory=std::move(out.notices);out={};out.id=node.id;out.kind=node.kind;
            out.presented=!lines.empty();if(!out.presented)continue;
            out.title=title;out.diagnostic=true;out.notices=std::move(mandatory);
            for(const auto& line:lines){if(!out.text.empty())out.text+='\n';out.text+=line;}
            out.accessible=title+"\n"+out.text;
            if(node.kind=="group"&&!empty_groups.at(node.id))continue;
            const auto display=std::find_if(cfg.topology.displays.begin(),cfg.topology.displays.end(),[&](const auto& d){return d.id==node.display;});
            need(display!=cfg.topology.displays.end(),"surface.display");
            need(node.pixels.width>2&&node.pixels.height>2,"surface.visibility_layout");
            TextRequest q;q.text=out.text;q.theme=cfg.resources->theme();q.language=cfg.language;q.contrast=cfg.contrast;
            q.numerator=display->scale_numerator;q.denominator=display->scale_denominator;
            q.wrap_units=(node.pixels.width-2)*64*q.denominator/q.numerator;need(*q.wrap_units>=64,"surface.visibility_layout");
            q.pixel_budget=std::min(std::size_t{4194304},8388608-display_pixels-leaf_pixels);need(q.pixel_budget>0,"surface.capacity");
            auto raster=render_text(q);need(!raster.missing_glyphs,"surface.glyphs");
            need(raster.width<=node.pixels.width&&raster.height<=node.pixels.height,"surface.visibility_layout");
            const s::Rect rect{node.pixels.x,node.pixels.y,raster.width,raster.height};
            for(const auto& existing:warnings)need(existing.first!=node.display||!intersects(existing.second,rect),"surface.visibility_layout");
            warnings.emplace_back(node.display,rect);leaf_pixels+=static_cast<std::size_t>(raster.width)*raster.height;
            out.fonts=raster.fonts;rasters.emplace(node.id,std::move(raster));
        }
        std::size_t bytes=0;for(const auto& pair:texts){bytes+=surface_text_bytes(pair.second);need(bytes<=262144,"surface.capacity");}
    });
}
}
