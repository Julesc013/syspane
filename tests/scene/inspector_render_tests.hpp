#pragma once
#include "image_fixture.hpp"
#include "inspector_admission_owner.hpp"
#include "scene_inspector_render.hpp"
#include <atomic>
#include <chrono>
#include <csignal>
#include <future>
#include <glib.h>

namespace inspector_render_test {
using namespace fixture;
namespace ui=syspane::interfaces;
inline std::uint64_t now(){return static_cast<std::uint64_t>(g_get_monotonic_time()/1000);}
inline auto setup(const std::string& root,bool chart=false,bool image=false){
    auto value=std::make_shared<ui::InspectorRenderSetup>();value->authority={true,"console",{"console"}};value->policy=inspector_admission_owner_test::grant();
    value->config=std::make_shared<const v::SurfaceConfig>(image?image_config(root):chart?chart_config(root):config(root));value->providers={provider()};value->profile=11;return value;
}
inline ui::InspectorRenderInput input(r::TelemetryReceiver& receiver){ui::InspectorRenderInput value;value.delivery=receiver.view(now());value.scope={11,4};return value;}
inline auto ready(ui::InspectorRenderTask& task,std::uint64_t ticket){
    const auto end=now()+2500;
    while(now()<end){const auto state=task.status();need(state.error.empty(),"native renderer failure");
        auto value=task.take();if(value&&value->ticket>=ticket)return value;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    throw std::runtime_error("native renderer completion deadline");
}
inline void stop(ui::InspectorRenderTask& task){task.close();const auto end=now()+2500;while(!task.status().stopped){need(now()<end,"renderer drain deadline");std::this_thread::sleep_for(std::chrono::milliseconds(1));}need(task.status().error.empty(),"renderer drain failure");}
inline void loading_image(const std::vector<ui::InspectorRow>& rows){need(rows.size()==1&&rows[0].item=="Image title"&&rows[0].information=="Public image\nImage loading","literal renderer loading row");}
struct Gate {
    std::promise<void> entered,release;std::shared_future<void> released=release.get_future().share();std::future<void> arrived=entered.get_future();
    bool opened=false;
    void hold(){entered.set_value();released.wait();}
    void wait(){need(arrived.wait_for(std::chrono::seconds(2))==std::future_status::ready,"worker barrier entry");arrived.get();}
    void open(){if(!opened){opened=true;release.set_value();}}
};
struct ReleaseGate {std::shared_ptr<Gate> gate;~ReleaseGate(){gate->open();}};
inline void scalar(const std::string& root){
    const auto binding=inspector_admission_owner_test::binding();r::TelemetryReceiver receiver({11,4},inspector_admission_owner_test::grant(),n::network_metrics(),binding,now());
    need(receiver.receive(wire(document(),binding),now(),tick()).code==r::DataCode::accepted,"renderer scalar receipt");
    auto factory=ui::threaded_inspector_renderer();auto task=factory(setup(root));const auto original=input(receiver);
    auto value=ready(*task,task->submit(original));inspector_admission_owner_test::shows(value->rows,"123 byte","lease=active","age=0 ns");
    need(!value->time_dependent&&value->current(original,11,now())&&value->timeline.at("P1").maximum_ns==3000000099ULL,"exact freshness transition guard");
    auto current=original;current.delivery->clock=tick(3000000099ULL);need(value->current(current,11,now()),"freshness inclusive final current tick");
    current.delivery->clock=tick(3000000100ULL);need(!value->current(current,11,now()),"exact TTL expiry rejects prepared Current label");
    current=original;current.delivery->clock=tick(99);need(!value->current(current,11,now()),"clock regression rejects prepared result");
    current=original;current.delivery->clock=tick(100,"E2");need(!value->current(current,11,now()),"clock domain rejects prepared result");
    current=original;current.delivery->connected=false;need(!value->current(current,11,now()),"peer loss rejects active result");
    current=original;++current.scope.generation;need(!value->current(current,11,now()),"scope generation rejects prepared result");
    need(!value->current(original,12,now()),"profile rejects prepared result");
    need(!value->current(original,11,original.delivery->live_until_ms),"native absolute deadline rejects prepared result");
    need(!value->current(original,11,original.delivery->clock_ms+251),"original sampled clock expiry rejects prepared result");
    const auto later=original.delivery->clock_ms+251;current=original;current.delivery->clock_ms=later;
    need(value->current(current,11,later,false)&&!value->current(current,11,later),"fresh current native sample maintains already adopted data without admitting a delayed old result");
    current.delivery->clock_ms=later-251;need(!value->current(current,11,later,false),"display maintenance still requires a fresh independent native sample");
    auto disconnected=original;disconnected.delivery->connected=false;
    value=ready(*task,task->submit(disconnected));inspector_admission_owner_test::shows(value->rows,"123 byte","lease=retained","age=unknown");
    need(value->current(disconnected,11,now())&&!value->current(original,11,now()),"retained adoption requires current unavailable delivery");
    bool rejected=false;std::thread other([&]{try{(void)task->status();}catch(const p::Error& e){rejected=std::string(e.what())=="inspector.render_owner";}});other.join();need(rejected,"renderer task rejects foreign GUI owner");
    stop(*task);need(!task->take(),"closed renderer transfers no payload");
    std::cout<<"renderer scalar temporal/domain/scope/lease/retained/owner pass\n";
}
inline void charts(const std::string& root){
    const auto cases=read(root+"/../../../tests/scene","inspector-delivery-cases.json");
    for(const auto& scenario:cases["cases"]){
        const auto b=inspector_admission_owner_test::binding();r::TelemetryReceiver receiver({11,4},inspector_admission_owner_test::grant(),n::network_metrics(),b,now());auto task=ui::threaded_inspector_renderer()(setup(root,true));std::uint64_t clock=0;
        for(const auto& step:scenario["steps"]){
            clock=std::max(clock,step["time"].get<std::uint64_t>());auto doc=chart_document(step["value"],step["generation"],step["time"]);
            if(step.value("failed",false))for(auto& observation:doc["observations"])if(observation["field"]=="network.receive_bytes"){
                observation["acquisition"]="failed";observation["freshness"]="stale";observation["error"]={{"code","fixture.failed"},{"message","Controlled failure"},{"retryable",true}};
            }
            need(receiver.receive(wire(doc,b),now(),tick(clock)).code==(step.value("duplicate",false)?r::DataCode::duplicate:r::DataCode::accepted),"renderer chart receiver admission");
            if(!step.contains("points"))continue;
            auto value=ready(*task,task->submit(input(receiver)));need(value->time_dependent&&value->rows.size()==1&&value->rows[0].children.size()==step["points"].size(),"renderer literal point count");
            for(std::size_t i=0;i<step["points"].size();++i){const auto& point=step["points"][i];const auto& row=value->rows[0].children[i];
                need(row.item=="Point "+point[0].dump()+" ns"&&row.information==point[1].dump()+" byte; generation "+point[2].dump()+"; "+point[3].get<std::string>(),"renderer unchanged literal point oracle");}
            need((value->rows[0].information.find("Gap pending")!=std::string::npos)==step.value("gap_pending",false),"renderer exact pending chart gap");
        }
        stop(*task);std::cout<<"renderer chart "<<scenario["id"].get<std::string>()<<" pass\n";
    }
}
inline void table(const std::string& root){
    const auto b=inspector_admission_owner_test::binding();r::TelemetryReceiver receiver({11,4},inspector_admission_owner_test::grant(),n::network_metrics(),b,now());
    auto candidate=setup(root);candidate->config=std::make_shared<const v::SurfaceConfig>(table_config(root));
    auto task=ui::threaded_inspector_renderer()(candidate);
    need(receiver.receive(wire(table_document(123,1),b),now(),tick()).code==r::DataCode::accepted,"renderer table native receipt");
    auto value=ready(*task,task->submit(input(receiver)));const auto oracle=read(root+"/../../../tests/scene","inspector-cases.json")["table"];
    need(value->rows.size()==1&&value->rows[0].item==oracle["item"]&&value->rows[0].information.find(oracle["summary"].get<std::string>())!=std::string::npos,"renderer literal table summary");
    const auto& entities=value->rows[0].children;need(entities.size()==2,"renderer literal entity count");
    for(std::size_t i=0;i<2;++i){need(entities[i].item==oracle["entities"][i]&&entities[i].children.size()==2,"renderer literal table identity");
        for(std::size_t j=0;j<2;++j)need(entities[i].children[j].item==oracle["columns"][j]&&entities[i].children[j].information.find(oracle["values"][i*2+j].get<std::string>())!=std::string::npos,"renderer literal cell value");}
    stop(*task);std::cout<<"renderer literal table projection pass\n";
}
inline void coalescing(const std::string& root){
    auto gate=std::make_shared<Gate>();const auto b=inspector_admission_owner_test::binding();r::TelemetryReceiver receiver({11,4},inspector_admission_owner_test::grant(),n::network_metrics(),b,now());
    auto task=ui::threaded_inspector_renderer({},[gate](std::uint64_t ticket){if(ticket==2)gate->hold();})(setup(root,true));
    ReleaseGate release{gate};
    const auto send=[&](std::uint64_t generation){need(receiver.receive(wire(chart_document(generation*10,generation,generation*100),b),now(),tick(generation*100)).code==r::DataCode::accepted,"coalescing source receipt");auto value=input(receiver);return task->submit(std::move(value));};
    (void)ready(*task,send(1));(void)send(2);gate->wait();
    need(receiver.receive(wire(chart_document(30,3,300),b),now(),tick(300)).code==r::DataCode::accepted,"skipped source receipt");
    auto skipped=input(receiver);std::weak_ptr<const r::DeliveredFrame> released=skipped.delivery->frame;(void)task->submit(std::move(skipped));
    const auto last=send(4);need(released.expired()&&task->status().running&&task->status().replaced==1,"latest slot releases superseded complete frame while one job runs");
    gate->open();auto value=ready(*task,last);const auto& points=value->rows.at(0).children;need(points.size()==3,"only admitted history points survive queue coalescing");
    const std::vector<std::string> expected={"10 byte; generation 1; start","20 byte; generation 2; join","40 byte; generation 4; start"};
    for(std::size_t i=0;i<points.size();++i)need(points[i].information==expected[i],"exact queued gap oracle");
    need(task->status().accepted==4&&task->status().completed==3,"bounded queue exact work counts");
    auto current=input(receiver);current.delivery->clock=tick(1000000100ULL);need(value->current(current,11,now()),"chart keeps point at exact window boundary");
    current.delivery->clock=tick(1000000101ULL);need(!value->current(current,11,now()),"chart window expiry rejects old prepared point");
    stop(*task);std::cout<<"renderer claimed/latest-slot/chart-window pass\n";
}
inline void cancellation(const std::string& root){
    auto gate=std::make_shared<Gate>();const auto b=inspector_admission_owner_test::binding();r::TelemetryReceiver receiver({11,4},inspector_admission_owner_test::grant(),n::network_metrics(),b,now());
    need(receiver.receive(wire(document(),b),now(),tick()).code==r::DataCode::accepted,"cancellation source receipt");
    auto task=ui::threaded_inspector_renderer({},[gate](std::uint64_t){gate->hold();})(setup(root));ReleaseGate release{gate};auto value=input(receiver);std::weak_ptr<const r::DeliveredFrame> frame=value.delivery->frame;
    (void)task->submit(std::move(value));receiver.withdraw(now());gate->wait();task->close();
    need(task->status().closing&&task->status().running&&!task->status().stopped&&!frame.expired()&&!task->take(),"claimed work remains honestly stopping without stale publication");
    gate->open();stop(*task);need(frame.expired()&&!task->take(),"stop follows claimed input destruction");
    std::cout<<"renderer claimed cancellation/destruction acknowledgement pass\n";
}
inline void images(const std::string& root){
    auto gate=std::make_shared<Gate>();std::atomic<std::uint64_t> process{0};const auto path=image_worker_path();
    auto task=ui::threaded_inspector_renderer([gate,path,&process]{return [gate,path,&process](std::string media,std::string bytes){
        gate->hold();auto job=std::make_unique<v::ImageJob>(path,std::move(media),std::move(bytes));process=job->process_id();return job;
    };})(setup(root,false,true));
    ReleaseGate release{gate};
    ui::InspectorRenderInput value;value.scope={11,0};const auto ticket=task->submit(std::move(value));auto loading=ready(*task,ticket);
    loading_image(loading->rows);need(process==0,"transferred loading alone cannot launch image child");
    task->acknowledge(ticket);gate->wait();task->close();need(!task->status().stopped&&task->status().running,"native image creation remains running during cancellation");
    gate->open();stop(*task);need(process!=0&&::kill(static_cast<pid_t>(process.load()),0)==-1&&errno==ESRCH,"stop acknowledges real image child disappearance");
    std::cout<<"renderer native image child drain pass\n";
}
inline void image_adoption(const std::string& root){
    std::atomic<unsigned> starts{0};const auto path=image_worker_path();
    auto factory=ui::threaded_inspector_renderer([path,&starts]{return [path,&starts](std::string media,std::string bytes){++starts;return std::make_unique<v::ImageJob>(path,std::move(media),std::move(bytes));};});
    auto task=factory(setup(root,false,true));ui::InspectorRenderInput input;input.scope={11,0};const auto first=task->submit(input);
    // Completion without transfer, transfer without adoption and obsolete tickets
    // must all keep the real native factory untouched.
    const auto end=now()+2500;while(!task->status().ready){need(now()<end,"untransferred image completion deadline");g_usleep(1000);}
    bool refused=false;try{task->acknowledge(first);}catch(const syspane::protocol::Error& e){refused=std::string(e.what())=="inspector.render_ticket";}need(refused&&starts==0,"untransferred result cannot acknowledge image launch");
    auto initial=ready(*task,first);const auto next=task->submit(input);auto newer=ready(*task,next);
    loading_image(initial->rows);loading_image(newer->rows);
    refused=false;try{task->acknowledge(first);}catch(const syspane::protocol::Error& e){refused=std::string(e.what())=="inspector.render_ticket";}need(refused&&starts==0,"superseded transfer cannot start queued image");
    bool foreign=false;std::thread wrong([&]{try{task->acknowledge(next);}catch(const syspane::protocol::Error& e){foreign=std::string(e.what())=="inspector.render_owner";}});wrong.join();need(foreign&&starts==0,"foreign owner cannot acknowledge image adoption");
    stop(*task);need(starts==0,"cancellation before adopted loading creates no native child");
    refused=false;try{task->acknowledge(next);}catch(const syspane::protocol::Error& e){refused=std::string(e.what())=="inspector.render_closed";}need(refused,"closed owner cannot revive queued image");
    // Launch failures after acknowledgement retain the exact image refusal.
    auto failed=ui::threaded_inspector_renderer([]{return [](std::string,std::string)->std::unique_ptr<v::ImageTask>{throw syspane::protocol::Error("image.installation");};})(setup(root,false,true));
    const auto loading_ticket=failed->submit(input);auto loading=ready(*failed,loading_ticket);failed->acknowledge(loading_ticket);
    const auto failure_end=now()+2500;bool found=false;
    while(!found){need(now()<failure_end,"adopted image refusal deadline");auto result=ready(*failed,failed->submit(input));
        for(const auto& row:result->rows)if(row.information=="Public image\nImage failed (image.installation)")found=true;
        g_usleep(1000);
    }
    stop(*failed);std::cout<<"renderer transfer/adoption/cancellation/native refusal pass\n";
}
inline int run(const std::string& root){scalar(root);table(root);charts(root);coalescing(root);cancellation(root);image_adoption(root);images(root);return 0;}
}
