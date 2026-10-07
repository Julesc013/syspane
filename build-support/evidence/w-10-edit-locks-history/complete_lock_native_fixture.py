from pathlib import Path
p=Path('tests/editor/editor_window.cpp');s=p.read_text();s=s.replace('if(locks_mode&&behavior=="nested")scene=read(root+"/tests/editor/edit-lock-cases.json")["grouped"];','')
s=s.replace('actions.widget_id=[&]{return "widget:new"+std::to_string(++serial);};','actions.widget_id=[&]{if(locks_mode&&behavior=="nested"&&!serial){++serial;return std::string("widget:group");}return "widget:new"+std::to_string(++serial);};')
p.write_text(s,encoding='utf-8',newline='\n')
