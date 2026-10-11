#pragma once
#include "surface_fixture.hpp"
#include "scene_inspector.hpp"
#include <gtk/gtk.h>
#include <array>
#include <cstdlib>
#include <fcntl.h>
#include <iostream>
#include <unistd.h>

namespace gtk_history_limits {
class Phases {
public:
    enum Part {receiver,delivery,lookup,publication};
private:
    static void need(bool okay,const char* reason){fixture::need(okay,reason);}
    struct Row {unsigned stage=0,before=0,after=0,points=0,mask=0;std::array<std::uint64_t,4> parts{};std::array<std::uint64_t,3> nested{};std::uint64_t work=0,delay=0;};
    std::string path_;std::vector<Row> rows_;Row current_;
public:
    Phases(){if(const auto* p=std::getenv("SYSPANE_GTK_HISTORY_PHASE_FILE")){path_=p;need(!path_.empty()&&path_.size()<=4096,"history phase path");rows_.reserve(32768);}}
    bool enabled()const{return !path_.empty();}
    void begin(unsigned stage,unsigned generation){if(enabled()){current_={};current_.stage=stage;current_.before=generation;}}
    template<class Operation> void measure(Part part,const Operation& operation){if(!enabled()){operation();return;}
        const auto begin=g_get_monotonic_time();operation();current_.parts[part]=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);}
    syspane::interfaces::SceneInspector::PhaseObserver observer(){if(!enabled())return {};
        return [this](auto phase,std::uint64_t us,bool completed){unsigned index;
            using P=syspane::interfaces::SceneInspector::Phase;
            switch(phase){case P::admission:index=0;break;case P::adoption:index=1;break;case P::presentation:index=2;break;default:return false;}
            if(!completed||(current_.mask&(1U<<index)))return false;
            current_.mask|=1U<<index;current_.nested[index]=us;return true;
        };}
    void finish(unsigned generation,unsigned count,std::uint64_t work,std::uint64_t delay){if(!enabled())return;
        need(rows_.size()<32768,"history phase capacity");current_.after=generation;current_.points=count;current_.work=work;current_.delay=delay;rows_.push_back(current_);}
    void emit()const{if(!enabled())return;
        std::string raw="history-phases-begin 1 "+std::to_string(rows_.size())+"\n";
        for(std::size_t i=0;i<rows_.size();++i){const auto& row=rows_[i];raw+="history-phase "+std::to_string(i);
            for(auto value:{static_cast<std::uint64_t>(row.stage),static_cast<std::uint64_t>(row.before),static_cast<std::uint64_t>(row.after),static_cast<std::uint64_t>(row.points),row.work,row.delay,row.parts[0],row.parts[1],row.parts[2],row.parts[3],row.nested[0],row.nested[1],row.nested[2],static_cast<std::uint64_t>(row.mask)})raw+=' '+std::to_string(value);
            raw+='\n';need(raw.size()<=6U*1024U*1024U,"history phase byte capacity");}
        raw+="history-phases-end "+std::to_string(rows_.size())+"\n";need(raw.size()<=6U*1024U*1024U,"history phase byte capacity");
        const auto fd=::open(path_.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);need(fd>=0,"history phase exclusive output");
        const auto written=::write(fd,raw.data(),raw.size());const auto closed=::close(fd);
        need(closed==0&&written>=0&&static_cast<std::size_t>(written)==raw.size(),"history phase complete output");
    }
};
inline int phases_probe(){
    using P=syspane::interfaces::SceneInspector::Phase;
    Phases phases;fixture::need(phases.enabled(),"phase probe output");const auto begin=g_get_monotonic_time();phases.begin(1,1);
    phases.measure(Phases::receiver,[]{});
    phases.measure(Phases::delivery,[&]{auto observer=phases.observer();fixture::need(observer(P::admission,0,true)&&observer(P::presentation,0,true)&&observer(P::adoption,0,true),"phase probe observer");});
    phases.measure(Phases::lookup,[]{});phases.measure(Phases::publication,[]{});
    const auto work=static_cast<std::uint64_t>(g_get_monotonic_time()-begin);phases.finish(2,1,work,34);phases.emit();
    bool exclusive=false;try{phases.emit();}catch(const std::exception&){exclusive=true;}fixture::need(exclusive,"phase overwrite refused");
    Phases guard;guard.begin(0,1);auto observer=guard.observer();fixture::need(observer(P::admission,0,true)&&!observer(P::admission,0,true),"duplicate phase refused");
    guard.begin(0,1);fixture::need(!observer(P::admission,0,false)&&!observer(P::paint,0,true),"incomplete/unknown phase refused");
    for(unsigned i=0;i<32768;++i){guard.begin(0,1);guard.finish(1,0,0,0);}
    bool capacity=false;try{guard.finish(1,0,0,0);}catch(const std::exception&){capacity=true;}fixture::need(capacity,"phase record overflow refused");
    std::cout<<fixture::Json({{"work_us",work},{"delay_us",34},{"exclusive_output",exclusive},{"record_capacity",capacity},{"observer_controls",3}}).dump()<<std::endl;return 0;
}
}
