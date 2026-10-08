from pathlib import Path
r=Path.cwd()
def edit(path,changes):
 p=r/path;s=p.read_text(encoding='utf-8')
 for old,new in changes:
  assert old in s,(path,old);s=s.replace(old,new)
 p.write_text(s,encoding='utf-8',newline='\n')
edit('source/rendering/scene_surface.hpp',[
 ('#include "native_text.hpp"','#include "scene_text.hpp"'),
 ('bool experimental_visibility=false;','bool experimental_typography=false; // Trusted development admission, not an authored capability.\n    bool experimental_visibility=false;'),
 ('struct SurfaceCell { std::string text,accessible;scene::Rect pixels; };','struct SurfaceCell { std::string text,accessible;scene::Rect pixels;std::vector<TextBlock> blocks; };'),
 ('std::string id,kind,title,text,accessible;std::vector<std::string> fonts;','std::string id,kind,title,text,accessible;std::vector<std::string> fonts;std::vector<TextBlock> blocks;')])
edit('source/rendering/scene_surface.cpp',[
 ('SurfaceText text(const Json& w,const s::BindingFrame* frame){','SurfaceText text(const Json& w,const s::BindingFrame* frame,bool typography){'),
 ('if(out.kind=="text"){out.text=out.accessible=w.contains("content")?w["content"]["body"].get<std::string>():title;return out;}','if(out.kind=="text"){out.text=out.accessible=w.contains("content")?w["content"]["body"].get<std::string>():title;if(typography)out.blocks.push_back({"body",out.text});return out;}'),
 ('out.text=title+"\\n";','out.text=title+"\\n";if(typography)out.blocks.push_back({"label",title});'),
 ('out.text+=out.notices.back();out.accessible=out.text;return out;','out.text+=out.notices.back();out.accessible=out.text;if(typography)out.blocks.push_back({"diagnostic",out.notices.back()});return out;'),
 ('std::vector<std::string> states;','if(typography)out.blocks.push_back({"value",out.text.substr(title.size()+1)});\n    std::vector<std::string> states;'),
 ("out.text+='\\n';for(std::size_t i=0;i<states.size();++i){if(i)out.text+=\" | \";out.text+=states[i];}","std::string state_text;for(std::size_t i=0;i<states.size();++i){if(i)state_text+=\" | \";state_text+=states[i];}out.text+='\\n'+state_text;\n    if(typography)out.blocks.push_back({\"diagnostic\",state_text});"),
 ('config.resources->theme().at("schema_version")!="0.2.0","surface.typography_unavailable"','config.resources->theme().at("schema_version")!="0.2.0"||config.experimental_typography,"surface.typography_unavailable"'),
 ('i.config.resources->theme().at("schema_version")!="0.2.0","surface.typography_unavailable"','i.config.resources->theme().at("schema_version")!="0.2.0"||i.config.experimental_typography,"surface.typography_unavailable"'),
 ('const auto catalog=inputs(ticks);std::map<std::string,TextRaster> rasters;','const bool typography=config.resources->theme().at("schema_version")=="0.2.0";\n        const auto catalog=inputs(ticks);std::map<std::string,TextRaster> rasters;'),
 ('const auto cell=text({{"id","cell"},{"kind","value"},{"title",""}},&frame);','auto cell=text({{"id","cell"},{"kind","value"},{"title",""}},&frame,typography);'),
 ('return SurfaceCell{cell.text.substr(1),cell.accessible.substr(1),{}};','if(typography)cell.blocks.erase(cell.blocks.begin());\n                    return SurfaceCell{cell.text.substr(1),cell.accessible.substr(1),{},std::move(cell.blocks)};'),
 ('out=text(w,&f);','out=text(w,&f,typography);'),('out=text(w,nullptr);','out=text(w,nullptr,typography);'),
 (':render_text(q);need(!raster.missing_glyphs',':typography?render_blocks(q,out.blocks,8388608-display_pixels-leaf_pixels):render_text(q);need(!raster.missing_glyphs')])
edit('source/rendering/scene_chart.cpp',[
 ('chart.summary+=\'\\n\';chart.summary+=plot.minimum?', 'if(!text.blocks.empty())text.blocks.push_back({view.capacity_truncated||view.pending_break||*why?"diagnostic":"label",chart.summary});\n    const auto range_start=chart.summary.size()+1;\n    chart.summary+=\'\\n\';chart.summary+=plot.minimum?'),
 ('chart.summary+="\\nWindow "+','if(!text.blocks.empty())text.blocks.push_back({!plot.minimum||plot.clipped?"diagnostic":"value",chart.summary.substr(range_start)});\n    const auto window_start=chart.summary.size()+1;\n    chart.summary+="\\nWindow "+'),
 ("text.text+='\\n'+chart.summary;",'if(!text.blocks.empty())text.blocks.push_back({"label",chart.summary.substr(window_start)});\n    text.text+=\'\\n\'+chart.summary;'),
 ('auto text=render_text(q);','auto text=request.theme["schema_version"]=="0.2.0"?render_blocks(q,widget.blocks,capacity-mask_pixels):render_text(q);')])
edit('source/rendering/scene_table.cpp',[
 ('for(const auto& f:s.fonts)size+=f.size();','for(const auto& f:s.fonts)size+=f.size();\n    for(const auto& b:s.blocks)size+=b.role.size()+b.text.size();'),
 ('for(const auto& c:r.cells)size+=c.text.size()+c.accessible.size();','for(const auto& c:r.cells){size+=c.text.size()+c.accessible.size();for(const auto& b:c.blocks)size+=b.role.size()+b.text.size();}'),
 ('const auto add=[&](const std::string& text){','const bool typography=request.theme["schema_version"]=="0.2.0";\n    const auto add=[&](const std::string& text,const std::string& role,const std::vector<TextBlock>& blocks){'),
 ('auto raster=render_text(q);','q.role=typography?role:"body";auto raster=typography&&!blocks.empty()?render_blocks(q,blocks,capacity-retained):render_text(q);'),
 ('const auto title=add(widget.text),summary=add(table.summary);','const auto title=add(widget.text,"label",{}),summary=add(table.summary,"diagnostic",{});'),
 ('headers.push_back(add(name))','headers.push_back(add(name,"label",{}))'),
 ('cells.back().push_back(add(c.text))','cells.back().push_back(add(c.text,"value",c.blocks))')])
edit('source/rendering/scene_visibility.cpp',[
 ('TextRequest q;q.text=out.text;q.theme=cfg.resources->theme();','if(cfg.resources->theme()["schema_version"]=="0.2.0")out.blocks.push_back({"diagnostic",out.text});\n            TextRequest q;q.role="diagnostic";q.text=out.text;q.theme=cfg.resources->theme();')])
edit('source/interfaces/scene_inspector_model.cpp',[
 ('w.fonts.empty()&&!w.table','w.fonts.empty()&&w.blocks.empty()&&!w.table')])
edit('CMakeLists.txt',[
 ('STATIC source/rendering/scene_surface.cpp','STATIC source/rendering/scene_text.cpp source/rendering/scene_surface.cpp'),
 ('        add_test(NAME native.THEME-TYPOGRAPHY','        add_executable(syspane_role_composition_probe tests/scene/role_composition_probe.cpp)\n        target_link_libraries(syspane_role_composition_probe PRIVATE syspane_scene_surface syspane_scene_inspector syspane_network_publication)\n        add_test(NAME native.ROLE-COMPOSITION COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/scene/native_role_composition.py"\n            "$<TARGET_FILE:syspane_role_composition_probe>" "$<TARGET_FILE:syspane_text_probe>" "${CMAKE_BINARY_DIR}/native-evidence")\n        set_tests_properties(native.ROLE-COMPOSITION PROPERTIES TIMEOUT 180)\n        add_test(NAME native.THEME-TYPOGRAPHY'),
 ('list(APPEND component_targets syspane_scene_surface syspane_scene_surface_tests syspane_typography_tests)','list(APPEND component_targets syspane_scene_surface syspane_scene_surface_tests syspane_typography_tests syspane_role_composition_probe)')])
