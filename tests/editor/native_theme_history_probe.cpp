#include "theme_history_fixture.hpp"
#include "generation_store_linux.hpp"
#include <iostream>
#include <unistd.h>
namespace {
using namespace theme_history_fixture;
void need(bool b){if(!b)throw std::runtime_error("native theme draft state");}
c::Committed read(const std::string& path){syspane::platform::LinuxGenerationStore store(path);return store.load();}
void output(const Json& value){std::cout<<value.dump()<<std::endl;}
}
int main(int argc,char** argv){try{
    need(argc==4&&::geteuid()!=0);const std::string root=argv[1],path=argv[2],mode=argv[3];auto current=read(path);const auto cases=settings_fixture::read(root+"/tests/editor/theme-history-cases.json");
    ui::EditorDraft d(authority(),policy(),current.documents,"E1",context(*current.resources),true);current={};
    for(const std::string& key:mode=="lost"?std::vector<std::string>{"first"}:std::vector<std::string>{"first","second","reset"}){
        if(key=="reset")d.execute({ui::SceneThemeEdit{std::nullopt}});else need(fonts(d,cases["artifacts"][key]));
        const auto q=*d.begin("commit","history:"+key);output({{"event","request"},{"step",key},{"body",q.body}});
        if(mode=="lost"){d.disconnected();need(d.state()==ui::DraftState::unknown&&d.active_request()->body==q.body);}
        std::string line;need(static_cast<bool>(std::getline(std::cin,line)));const auto result=Json::parse(line);
        if(mode=="lost")need(d.reconciled(q.ticket,"Q","E2",result));else need(d.complete(q.ticket,result));
        need(!d.dirty()&&!d.active_request()&&d.undo_count()==0);auto theme=d.resources()->theme();
        if(mode=="wrong-report"&&key=="first")theme["font"]["weight"]=900;
        output({{"event","accepted"},{"step",key},{"scene",*d.scene()},{"theme",theme},{"selection",d.resources()->selection()},{"revision",*d.revision()}});
    }
    d.close();need(!d.scene()&&!d.resources());current=read(path);ui::EditorDraft fresh(authority(),policy(),current.documents,"E2",context(*current.resources),true);
    output({{"event","reloaded"},{"scene",*fresh.scene()},{"theme",fresh.resources()->theme()},{"selection",fresh.resources()->selection()}});return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
