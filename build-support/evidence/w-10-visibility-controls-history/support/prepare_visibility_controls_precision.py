from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import hashlib,json
r=Path.cwd();p=r/'tests/editor/visibility-number-cases.json'
text='''{
  "purpose": "Exact numeric identity for mixed rules, no-op detection and emitted scene changes",
  "pairs": [
    {"left": 18446744073709551615, "right": 18446744073709551616.0, "equal": false},
    {"left": 9007199254740993, "right": 9007199254740992.0, "equal": false},
    {"left": -1, "right": 18446744073709551615, "equal": false},
    {"left": -9223372036854775808, "right": -9223372036854775808.0, "equal": true},
    {"left": 9223372036854775807, "right": 9223372036854775808.0, "equal": false},
    {"left": -9223372036854775808, "right": -9223372036854777856.0, "equal": false},
    {"left": 1, "right": 1.0, "equal": true},
    {"left": 0, "right": -0.0, "equal": true},
    {"left": 1, "right": 1.25, "equal": false},
    {"left": 18446744073709549568, "right": 18446744073709549568.0, "equal": true},
    {"left": -9007199254740993, "right": -9007199254740992.0, "equal": false}
  ]
}
'''
assert not p.exists();p.write_text(text,encoding='utf-8',newline='\n')
v=json.loads(text,parse_float=Decimal)
for row in v['pairs']:assert (row['left']==row['right']) is row['equal']
frozen=dict(frozen_at=datetime.now(timezone.utc).isoformat(),inputs={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()},independent_check='Python Decimal equality over explicit decimal tokens; all real tokens are exactly representable binary64 values.',repair_started=False)
(r/'out/campaign/visibility-controls-number-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'tests/editor/visibility_controls_tests.cpp';s=p.read_text(encoding='utf-8')
old='    if(name=="INPUT"){\n';new='''    if(name=="INPUT"){
        const auto numbers=settings_fixture::read(root+"/tests/editor/visibility-number-cases.json");
        for(const auto& pair:numbers["pairs"]){auto scene=cases["multi"];scene["widgets"][0]["visibility"]["value"]=pair["left"];scene["widgets"][1]["visibility"]["value"]=pair["right"];CHECK(ui::visibility_input(scene,both).mode==(pair["equal"].get<bool>()?"conditional":"keep"));}
'''
assert old in s;s=s.replace(old,new)
old='    }else if(name=="ATOMIC"){\n';new='''    }else if(name=="ATOMIC"){
        const auto numbers=settings_fixture::read(root+"/tests/editor/visibility-number-cases.json");
        for(const auto& pair:numbers["pairs"]){
            auto initial=fixture.authored;initial.scene=cases["conditional"];initial.scene["widgets"][0]["visibility"]["value"]=pair["left"];
            ui::EditorDraft exact(authority,policy(),initial,"E1",resources,true);auto next=ui::visibility_input(*exact.scene(),ids);next.comparison.value=pair["right"].dump();const bool different=!pair["equal"].get<bool>();
            CHECK(exact.execute({*ui::visibility_edit(ids,next)})==different);CHECK(exact.dirty()==different);
            if(different){CHECK(exact.undo()&&!exact.dirty());CHECK(exact.redo()&&exact.dirty());const auto request=exact.begin("commit","numeric.change");CHECK(request);const auto command=c::parse_command(request->body);CHECK(command["operations"].size()==1&&command["operations"][0]["scene"]["widgets"][0]["visibility"]["value"].dump()==pair["right"].dump());}
            else CHECK(exact.undo_count()==0&&!exact.begin("commit","numeric.noop"));
        }
'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8',newline='\n')
print('Frozen eleven independent numeric examples and added regressions before the production repair.')
