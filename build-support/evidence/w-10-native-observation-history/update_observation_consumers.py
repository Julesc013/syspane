from pathlib import Path
import re
r=Path(__file__).resolve().parents[2]
for name in ('native_widget_creation.py','native_content_properties.py','native_binding_authoring.py','native_snap.py','native_arrange.py'):
    p=r/'tests/editor'/name;s=p.read_text()
    s=s.replace('obj.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN)','h.extents(obj)').replace('o.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN)','h.extents(o)').replace('matches[0].get_component_iface().get_extents(h.Atspi.CoordType.SCREEN)','h.extents(matches[0])')
    s=s.replace('obj.get_component_iface().get_extents(self.Atspi.CoordType.SCREEN)','self.extents(obj)')
    s=re.sub(r'(obj|o|matches\[0\])\.get_state_set\(\)\.contains\((h|self)\.Atspi.StateType\.(\w+)\)',r'\2.state(\1,\2.Atspi.StateType.\3)',s)
    s=s.replace("h.find('binding.'+('predicate-Add' if id=='filter' else 'sort-Add' if id=='order' else 'scope')).get_state_set().contains(h.Atspi.StateType.SHOWING)","h.state(h.find('binding.'+('predicate-Add' if id=='filter' else 'sort-Add' if id=='order' else 'scope')),h.Atspi.StateType.SHOWING)")
    if name=='native_content_properties.py':
        start=s.index('    def erased(self,obj):');end=s.index('    def check(',start);s=s[:start]+s[end:]
    if name=='native_arrange.py':
        start=s.index("                h.report['focus_failure']=");end=s.index('\n',start)
        s=s[:start]+"                h.report['focus_failure']=h.focus_snapshot(id)"+s[end:]
    p.write_text(s,encoding='utf-8',newline='\n')
