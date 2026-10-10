#pragma once
#include "scene_text.hpp"
#include "bindings.hpp"
#include "content.hpp"
#include "chart_plot.hpp"
#include "image_job.hpp"

namespace syspane::rendering {
enum class SurfaceCode { ready,degraded,empty,restricted,alternative,closed };
enum class SurfaceAudience { desktop,inspector };
struct SurfaceConfig {
    configuration::Authored authored;
    configuration::ResourceSnapshot resources;
    scene::Topology topology;
    std::string language="en",contrast="authored";
    std::set<std::string> capabilities;
    bool experimental_typography=false; // Trusted development admission, not an authored capability.
    bool experimental_visibility=false; // Trusted development admission, not an authored capability.
    // Alternative to raw authored documents (which must both be null). This
    // opaque owner proves structure only; current admission is never cached.
    std::optional<configuration::ValidatedAuthored> authored_snapshot;
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
struct SurfaceCell { std::string text,accessible;scene::Rect pixels;std::vector<TextBlock> blocks; };
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
    std::string id,kind,title,text,accessible;std::vector<std::string> fonts;std::vector<TextBlock> blocks;
    std::optional<SurfaceTable> table;
    struct Chart {
        std::string summary,accessible_summary;std::size_t samples=0,segments=0;scene::Rect pixels;
        std::optional<scene::ChartIdentity> identity;std::vector<scene::ChartPoint> points;
    };
    std::optional<Chart> chart;
    struct Image {std::string state;configuration::Json asset;unsigned width=0,height=0;};
    std::optional<Image> image;
    std::vector<std::string> notices; // Status only: no values, identities, ranges or asset references.
    bool presented=true,diagnostic=false;
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
                 std::vector<SurfaceProvider>,std::function<bool()> clear_native,std::string image_worker={},
                 SurfaceAudience audience=SurfaceAudience::desktop,ImageFactory images={});
    ~SceneSurface();
    SceneSurface(const SceneSurface&)=delete;
    SceneSurface& operator=(const SceneSurface&)=delete;
    recovery::DataAttachment attach(const std::string&,const protocol::TelemetryBinding&,std::uint64_t now);
    recovery::DataResult receive(const std::string&,std::uint64_t token,std::uint64_t revision,
                                std::string_view bytes,std::uint64_t now,const model::Tick&,
                                const std::map<std::string,model::Tick>& other_ticks={});
    recovery::DataCode heartbeat(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t sequence,std::uint64_t now);
    recovery::DataCode gap(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    recovery::DataCode disconnect(const std::string&,std::uint64_t token,std::uint64_t revision,std::uint64_t now);
    void policy(configuration::Policy,std::uint64_t now);
    void replace(SurfaceConfig,std::uint64_t now);
    void close();
    bool poll_image_jobs(); // Nonblocking; true when no running/stopping job remains.
    void paint(std::uint64_t now,const std::map<std::string,model::Tick>& ticks,
               const std::function<void(SurfaceCode,const SurfaceFrame*)>& sink);
    SurfaceStatus status()const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
