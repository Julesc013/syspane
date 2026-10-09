"""Observe the ordinary installed inspector through native controls and saved files."""
import json,select,signal,time
import native_installed_editor as h

CASES_PATH='tests/configuration/installed-inspector-cases.json'
CASES=json.loads((h.ROOT/CASES_PATH).read_bytes())
h.CASES=CASES

def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value,sensitive=(e[k] for k in ('wait','click','find','value','sensitive'))
    launch,settings,documents,quit=(e[k] for k in ('launch','settings_ready','documents','quit'))
    def rows():
        tree=find('syspane.scene.inspector')
        if not tree:return None
        table=tree.get_table_iface()
        assert table and table.get_n_columns()==2
        return [[e['text'](table.get_accessible_at(r,c)) for c in range(2)] for r in range(table.get_n_rows())]
    def exact(expected):
        actual=rows();assert actual==expected,(actual,expected)
    def ready(edited=False):
        expected=CASES['saved_rows' if edited else 'initial_rows']
        wait(lambda:rows()==expected and sensitive(find('frontend.settings')) and sensitive(find('frontend.editor')))
        assert not sensitive(find('frontend.inspector'))
        assert find('editor.canvas') is None and find('settings.value.sampling.resources_ms') is None
        exact(expected);report['observations'].append(dict(rows=rows()));documents(edited)
    def open_view(edited=False):
        wait(lambda:sensitive(find('frontend.inspector')));click('frontend.inspector');ready(edited)
    def erased():
        current=rows()
        return current in (None,[]) and value('syspane.scene.requested-summary')==''
    launch();settings();documents()
    summary_keys=h.Keys(e['process']().pid) if mode=='SUMMARY' else None
    if mode in ('PRIVATE-NAV','DRAFT-NAV','REQUEST-NAV','SAVE-REOPEN'):
        if mode=='PRIVATE-NAV':
            e['enter']('settings.value.sampling.resources_ms','-')
            wait(lambda:not sensitive(find('frontend.inspector')))
            click('settings.revert');settings()
        e['open_editor']()
        if mode=='PRIVATE-NAV':
            e['enter']('editor.value.title','Private uncommitted title')
            wait(lambda:not sensitive(find('frontend.inspector')))
            click('editor.revert-fields');e['editor_ready']()
            click('editor.fonts');wait(lambda:find('editor.theme.cancel'))
            assert not sensitive(find('frontend.inspector'))
            click('editor.theme.cancel');e['editor_ready']();open_view()
        else:
            e['properties']();assert not sensitive(find('frontend.inspector'));documents()
            if mode=='DRAFT-NAV':
                click('editor.undo');e['editor_ready']();open_view()
            else:
                if mode=='REQUEST-NAV':e['hold']('store.selector_ready')
                click('editor.apply')
                if mode=='REQUEST-NAV':
                    mark=wait(e['held']);pid,_=e['child']();assert mark['pid']==pid
                    assert not sensitive(find('frontend.inspector'));documents();(folder/'release').write_text('yes\n')
                e['saved']();open_view(True)
                if mode=='SAVE-REOPEN':
                    quit();launch();settings();open_view(True)
    else:
        open_view()
        if mode=='SUMMARY':
            tree=find('syspane.scene.inspector');e['focus'](tree)
            keys=summary_keys
            try:
                keys.press(0xff57)
                wait(lambda:list(tree.get_table_iface().get_selected_rows())==[1])
                summary=next(o for o in e['objects']() if o.get_role()==e['Atspi'].Role.PUSH_BUTTON and o.get_name()=='Summary')
                e['focus'](summary);keys.press(0x20)
                wait(lambda:value('syspane.scene.requested-summary')==CASES['summary'])
            finally:keys.close()
            report['observations'].append(dict(summary=value('syspane.scene.requested-summary')))
        elif mode=='NAVIGATION':
            for _ in range(2):
                click('frontend.editor');e['editor_ready']();open_view()
                click('frontend.settings');settings();open_view()
        elif mode=='RELOAD':
            pid,fd=e['child']();click('frontend.settings');settings();open_view()
            assert e['child']()[0]==pid and not select.select([fd],[],[],0)[0]
        elif mode in ('POLICY','REPLACEMENT'):
            pid,fd=e['child']()
            if mode=='POLICY':(folder/'policy').write_text('deny\n');wait(lambda:select.select([fd],[],[],0)[0],4)
            else:signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
            start=time.monotonic();wait(erased,CASES['erasure_after_observed_loss_ms']/1000)
            report['erasure_ms']=(time.monotonic()-start)*1000
            assert not sensitive(find('frontend.inspector'));documents()
            if mode=='REPLACEMENT':
                ready();new_pid,new_fd=e['child']();assert new_pid!=pid and not select.select([new_fd],[],[],0)[0]
        elif mode=='ORACLE':
            wrong=[list(v) for v in CASES['initial_rows']];wrong[0][0]='Incorrect saved title'
            try:exact(wrong)
            except AssertionError:report['wrong_row_rejected']=True
            else:raise AssertionError('row oracle accepted incorrect title')
            exact(CASES['initial_rows'])
        elif mode not in ('OPEN','CLOSE'):raise AssertionError(mode)
    e['screenshot']('inspector');quit()

if __name__=='__main__':h.main(exercise,__file__,CASES_PATH,'inspector-frontend-')
