#pragma once
#include "native_text.hpp"
#include "bindings.hpp"
#include "content.hpp"

namespace syspane::rendering {
enum class SurfaceCode { ready,degraded,empty,restricted,alternative,closed };
struct SurfaceConfig {
    configuration::Authored authored;
    configuration::ResourceSnapshot resources;
    scene::Topology topology;
    std::string language="en",contrast="authored";
    std::set<std::string> capabilities;
};
struct SurfaceProvider {
    std::string producer;
    scene::BindingScope scope;
    std::set<std::string> types;
    std::vector<model::Metric> metrics;
    std::map<std::string,std::optional<std::uint64_t>> fields;
    std::vector<scene::PinMapping> pins;
};
struct SurfacePixels {
    std::string display;
    scene::Unit x=0,y=0;
    unsigned width=0,height=0;
    std::vector<unsigned char> rgba;
};
struct SurfaceCell { std::string text,accessible;scene::Rect pixels; };
struct SurfaceRow {
    std::string producer,epoch,entity;
    std::uint64_t generation=0;
    std::vector<SurfaceCell> cells;
};
struct SurfaceTable {
    std::vector<std::string> columns,labels;
    std::vector<SurfaceRow> rows;
    std::string summary;
    std::size_t total=0;
    bool truncated=false;
};
struct SurfaceText {
    std::string id,kind,text,accessible;std::vector<std::string> fonts;
    std::optional<SurfaceTable> table;
};
struct SurfaceFrame {
    scene::Plan layout;
    configuration::Json theme_pin;
    std::vector<SurfaceText> widgets;
    std::vector<SurfacePixels> displays;
};
struct SurfaceStatus { SurfaceCode code=SurfaceCode::empty;std::size_t widgets=0,pixels=0;std::string reason; };
class SceneSurface {
public:
    SceneSurface(configuration::Authority,configuration::Policy,SurfaceConfig,
                 std::vector<SurfaceProvider>,std::function<bool()> clear_native);
    ~SceneSurface();
    SceneSurface(const SceneSurface&)=delete;
    SceneSurface& operator=(const SceneSurface&)=delete;
    recovery::DataAttachment attach(const std::string&,const protocol::TelemetryBinding&,std::uint64_t now);
    recovery::DataResult receive(const std::string&,std::uint64_t token,std::uint64_t revision,
                                std::string_view bytes,std::uint64_t now,const model::Tick&);
    recovery::DataCode heartbeat(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now);
    recovery::DataCode gap(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    recovery::DataCode disconnect(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    void policy(configuration::Policy,std::uint64_t now);
    void replace(SurfaceConfig,std::uint64_t now);
    void close();
    void paint(std::uint64_t now,const std::map<std::string,model::Tick>& ticks,
               const std::function<void(SurfaceCode,const SurfaceFrame*)>& sink);
    SurfaceStatus status()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
