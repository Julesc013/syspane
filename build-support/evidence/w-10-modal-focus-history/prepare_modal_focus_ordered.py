from pathlib import Path
r=Path.cwd();o=r/'out/campaign';s=(o/'modal_focus_probe_minimal.py').read_text().replace('modal-focus-plan-v2.json','modal-focus-plan-v3.json')
s=s.replace("directory,mode);original=h.focus;steps=[]", "directory,'canvas' if mode in ('batched','ordered') else mode);original=h.focus;steps=[]")
s=s.replace("    h.focus=focus\n    try:oracle.exercise(h);h.report['diagnostic']='unchanged_pass_inconclusive'", """    h.focus=focus
    original_value=h.value;original_press=h.input.press;trace=[];h.report['input_trace']=trace
    def value(id):
        text=original_value(id)
        if id=='title':trace.append(dict(at=time.monotonic(),title=text))
        return text
    def press(key,*a,**kw):
        trace.append(dict(at=time.monotonic(),key=key));return original_press(key,*a,**kw)
    h.value=value;h.input.press=press
    def ordered(index):
        h.focus('objects')
        for key,row in [(0xff57,3),(0xff50,0)]+[(0xff54,n) for n in range(1,index+1)]:
            h.input.press(key);title=oracle.CASES['authored']['scene']['widgets'][row]['title'];h.wait(lambda:h.value('title')==title)
    def selection(index):
        if mode=='ordered':ordered(index)
        else:oracle.select(h,index)
    def opened():return h.find('layout.set') is not None and h.state(h.find('layout.set'),h.Atspi.StateType.SHOWING) and not h.sensitive('layout')
    def trace_case():
        h.launch();h.check();selection(0);h.click('layout');h.wait(opened)
        h.click('layout.cancel');h.wait(lambda:h.sensitive('layout'));h.input.focus(h.pid)
        selection(3);h.report['selection_observed']=trace[-1];h.stage='GROUP-FOCUS';h.focus('layout');h.input.press(0x20);h.wait(opened)
        h.input.press(0xff1b);h.wait(lambda:h.sensitive('layout'));h.check();h.command('quit');assert h.proc.wait(timeout=5)==0
    try:
        if mode in ('batched','ordered'):trace_case()
        else:oracle.exercise(h)
        h.report['diagnostic']='ordered_pass' if mode=='ordered' else 'unchanged_pass_inconclusive'""")
s=s.replace("n//3+1", "n//len(PLAN['modes'])+1").replace("'MODAL-FOCUS-MINIMAL-DIAGNOSTIC'", "'MODAL-FOCUS-ORDERED-DIAGNOSTIC'").replace("'modal-focus-minimal-'", "'modal-focus-ordered-'")
(o/'modal_focus_probe_ordered.py').write_text(s,encoding='utf-8',newline='\n')
s=(o/'modal_focus_minimal_step.py').read_text().replace('modal_focus_probe_minimal.py','modal_focus_probe_ordered.py').replace('modal-focus-plan-v2.json','modal-focus-plan-v3.json');(o/'modal_focus_ordered_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(o/'modal_focus_minimal_flow.py').read_text().replace('modal_focus_minimal_step.py','modal_focus_ordered_step.py').replace('modal-focus-minimal-execution','modal-focus-ordered-execution');(o/'modal_focus_ordered_flow.py').write_text(s,encoding='utf-8',newline='\n')
