#include "chart_fixture.hpp"
#include <iostream>
using namespace fixture;
int chart_surface_tests(const std::string& root){unsigned count=0;const auto test=[&](const char* name,const std::function<void()>& run){run();++count;std::cout<<name<<" pass\n";};
    test("BURST",[&]{ChartOwner f(root);f.full(10,0);f.full(90,500000000);f.full(10,1000000000);auto frame=f.paint();const auto& w=frame.widgets[0];
        need(w.chart&&w.chart->samples==3&&w.chart->segments==1,"retain every prepaint delivery");
        need(w.text=="Receive\n10 byte\nCurrent\nSamples 3 | Segments 1\nRange 0.0 .. 100.0 byte\nWindow 1000 ms | linear","visible chart summary");
        need(w.accessible.find("Point 500000000: 90; generation 2; join")!=std::string::npos,"accessible exact point");need(w.chart->pixels.width==320&&w.chart->pixels.height==120,"graph dimensions");
        need(f.paint().widgets[0].chart->samples==3,"paint cannot duplicate");});
    test("GAP",[&]{ChartOwner f(root);f.full(10,0);f.surface->gap("P1",f.token,7,++f.now);f.full(90,500000000);auto w=f.paint().widgets[0];
        need(w.chart->samples==2&&w.chart->segments==2,"gap cannot join");need(w.accessible.find("Point 500000000: 90; generation 2; start")!=std::string::npos,"gap accessible");});
    test("REATTACH",[&]{ChartOwner f(root);f.full(10,0);const auto old=f.token;f.attach();f.full(90,500000000);
        need(f.surface->disconnect("P1",old,7,++f.now)==r::DataCode::stale_attachment,"old disconnect");f.full(80,1000000000);
        auto w=f.paint().widgets[0];need(w.chart->samples==2&&w.chart->segments==1,"old callback cannot break successor");});
    test("HISTORY-POLICY",[&]{ChartOwner f(root);f.full(10,0);f.paint();auto p=chart_policy(8);p.disclosure.erase({"desktop","history"});f.surface->policy(p,++f.now);f.empty(v::SurfaceCode::restricted);
        f.surface->policy(chart_policy(9),++f.now);f.revision=9;auto w=f.paint().widgets[0];need(w.chart->samples==0&&w.text.find("Waiting")!=std::string::npos,"history grant no old data");
        f.attach();f.full(90,500000000);need(f.paint().widgets[0].chart->samples==1,"history fresh attach");});
    test("RESOURCE",[&]{ChartOwner f(root);f.full(10,0);f.paint();auto p=chart_policy(8);p.denied_capabilities.insert("scene.content");f.surface->policy(p,++f.now);f.empty(v::SurfaceCode::restricted);
        f.surface->policy(chart_policy(9),++f.now);f.revision=9;need(f.paint().widgets[0].chart->samples==0,"resource regrant cleared");});
    test("EXPIRY",[&]{ChartOwner f(root);f.full(10,0);f.now+=10000;need(f.surface->heartbeat("P1",f.token,7,1,++f.now)==r::DataCode::closed,"expired attachment stays closed");
        auto w=f.paint().widgets[0];need(w.chart->samples==1&&w.text.find("Retained")!=std::string::npos&&w.text.find("Gap pending")!=std::string::npos,"expiry remains explicit");
        f.attach();f.full(90,500000000);need(f.paint().widgets[0].chart->samples==1,"fresh attachment resets expired history");});
    test("WINDOW",[&]{ChartOwner f(root);f.full(10,0);f.full(20,500000000);f.full(30,1500000001);need(f.paint().widgets[0].chart->samples==1,"window drops expired points");});
    test("REPLACE",[&]{ChartOwner f(root);f.full(10,0);f.full(20,500000000);auto cfg=f.cfg;cfg.authored.scene["widgets"][0]["content"]["interpolation"]="step";f.surface->replace(cfg,++f.now);
        auto w=f.paint().widgets[0];need(w.chart->samples==1&&w.text.find("| step")!=std::string::npos,"replacement resets history");});
    test("CLEAR-FAILURE",[&]{ChartOwner f(root);f.full(10,0);f.paint();f.clear_ok=false;f.surface->policy(chart_policy(8,false),++f.now);f.empty(v::SurfaceCode::closed);});
    test("BUDGET",[&]{ChartOwner f(root);auto cfg=f.cfg;auto prototype=cfg.authored.scene["widgets"][0];cfg.authored.scene["widgets"]=Json::array();cfg.authored.scene["roots"]=Json::array();
        for(unsigned i=0;i<5;++i){auto w=prototype;w["id"]="chart:"+std::to_string(i);w["content"]["max_points"]=4096;cfg.authored.scene["widgets"].push_back(w);cfg.authored.scene["roots"].push_back(w["id"]);}
        f.surface->replace(cfg,++f.now);f.empty(v::SurfaceCode::alternative);need(f.surface->status().reason=="surface.capacity","aggregate history reservation");});
    test("DISCONNECT",[&]{ChartOwner f(root);f.full(10,0);f.full(90,500000000);f.surface->disconnect("P1",f.token,7,++f.now);auto w=f.paint().widgets[0];
        need(w.chart->samples==2&&w.text.find("Retained")!=std::string::npos&&w.text.find("Gap pending")!=std::string::npos,"retained history explicit");});
    test("FAULTS",[&]{ChartOwner f(root);f.full(10,0);f.full(11,0);auto w=f.paint().widgets[0];need(w.chart->samples==0&&w.text.find("Chart conflict")!=std::string::npos,"conflict visible");
        f.full(12,100);need(f.paint().widgets[0].text.find("Chart conflict")!=std::string::npos,"conflict latched");
        ChartOwner broken(root);broken.full(10,100);auto d=chart_document(20,2,90);
        need(broken.surface->receive("P1",broken.token,7,wire(d,link()),++broken.now,tick(90)).code==r::DataCode::clock_fault,"native measurement regression");
        w=broken.paint().widgets[0];need(w.chart->samples==0&&w.text.find("Chart clock fault")!=std::string::npos,"native clock fault visible and erased");});
    test("ALPHA-CONTRAST",[&]{ChartOwner f(root);auto tokens=f.cfg.resources->theme()["tokens"];tokens["foreground"]="#ffffff80";tokens["background"]="#ff000080";tokens["muted"]="#0000ff80";
        auto cfg=chart_config(root,{{"tokens",tokens}});f.surface->replace(cfg,++f.now);f.full(10,0);f.full(90,500000000);f.full(10,1000000000);auto frame=f.paint();const auto y=frame.widgets[0].chart->pixels.y;
        const auto pixel=[&](unsigned x,s::Unit row){const auto at=static_cast<std::size_t>(row*800+x)*4;const auto& p=frame.displays[0].rgba;return std::vector<unsigned char>(p.begin()+at,p.begin()+at+4);};
        need(pixel(1,y+1)==std::vector<unsigned char>({128,0,0,128}),"graph background once");
        need(pixel(160,y+12)==std::vector<unsigned char>({192,128,128,192}),"curve vertex coverage once");
        need(pixel(0,y+107)==std::vector<unsigned char>({160,128,192,224}),"border and curve alpha");
        cfg.contrast="dark";f.surface->replace(cfg,++f.now);frame=f.paint();const auto dark_y=frame.widgets[0].chart->pixels.y;
        need(pixel(1,dark_y+1)==std::vector<unsigned char>({0,0,0,255})&&pixel(0,dark_y)==std::vector<unsigned char>({255,255,255,255}),"chart high contrast");});
    test("PRODUCER-CONTEXT",[&]{for(bool selector:{false,true}){auto cfg=chart_config(root);if(selector){auto b=collection();b["mode"]="singleton";b["limit"]=1;b["predicates"]=Json::array({{{"field","entity.id"},{"op","eq"},{"value","network:interface:1"}}});cfg.authored.scene["widgets"][0]["bindings"]=Json::array({b});}
        auto other=provider();other.producer="P2";v::SceneSurface owner({true,"desktop",{"desktop"}},chart_policy(),cfg,{provider(),other},[]{return true;});
        auto l1=link(),l2=link();l2.producer="P2";const auto t1=owner.attach("P1",l1,0).token,t2=owner.attach("P2",l2,0).token;need(t1&&t2,"two providers attached");
        const auto receive=[&](std::string producer,std::uint64_t generation,std::uint64_t ns,const std::map<std::string,m::Tick>& clocks){auto d=chart_document(10+generation,generation,ns);const auto l=producer=="P1"?l1:l2;
            if(producer=="P2"){d["entities"][0]["id"]="network:interface:2";for(auto& o:d["observations"])o["entity_id"]="network:interface:2";}
            Json body={{"schema_version","0.2.0"},{"subscription_id","S"},{"producer_id",producer},{"record_id","R"+std::to_string(generation)},
                {"policy_revision","7"},{"clock_id","clock:1"},{"snapshot",d}};const auto bytes=p::encode_telemetry({"snapshot","D","E1",body.dump(),body},l);
            need(owner.receive(producer,producer=="P1"?t1:t2,7,bytes,1+generation,tick(ns),clocks).code==r::DataCode::accepted,"two-provider delivery");};
        receive("P1",1,0,{});receive("P2",1,0,selector?std::map<std::string,m::Tick>{{"P1",tick(0)}}:std::map<std::string,m::Tick>{});
        receive("P1",2,500000000,selector?std::map<std::string,m::Tick>{{"P2",tick(500000000)}}:std::map<std::string,m::Tick>{});
        receive("P2",2,500000000,selector?std::map<std::string,m::Tick>{{"P1",tick(500000000)}}:std::map<std::string,m::Tick>{});
        owner.paint(4,{{"P1",tick(500000000)},{"P2",tick(500000000)}},[&](auto code,const auto* frame){need(code==v::SurfaceCode::ready&&frame&&frame->widgets[0].chart->samples==2,"complete relevant context and unrelated preservation");});
        if(selector){receive("P1",3,1000000000,{});owner.paint(5,{{"P1",tick(1000000000)}},[&](auto,const auto* frame){need(frame&&frame->widgets[0].chart->samples==0,"missing selector clock explicit");});}
    }});
    std::cout<<"CHART-SURFACE-FAMILIES "<<count<<'\n';return 0;
}
