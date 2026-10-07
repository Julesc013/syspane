from pathlib import Path
r=Path(__file__).resolve().parents[2]
for name,prefix in [('native_widget_creation.py','create'),('native_content_properties.py','content'),('native_binding_authoring.py','binding')]:
    p=r/'tests/editor'/name;s=p.read_text();start=s.index('def selected(h,id):');end=s.index('def choose(',start)
    s=s[:start]+f"def selected(h,id):return h.observer.selected_text(h.find('{prefix}.'+id))\n\n"+s[end:]
    p.write_text(s,encoding='utf-8',newline='\n')
