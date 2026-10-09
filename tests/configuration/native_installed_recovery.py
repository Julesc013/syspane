"""Observe recovery through the installed GTK editor and exact independent files."""
from pathlib import Path
import json,select,signal,time
import native_installed_editor as h

CASES_PATH='tests/configuration/installed-recovery-cases.json'
CASES=json.loads((h.ROOT/CASES_PATH).read_bytes())
EXISTING=json.loads((h.ROOT/'tests/configuration/installed-editor-cases.json').read_bytes())
COMMAND=json.loads((h.ROOT/CASES['expected_command']).read_bytes())
# The shared command fixes semantic values. GTK's property editor admits all
# four geometry entries through its real-number parser, including unchanged
# width/height/y fields. Derive those wire types from that input contract,
# never from the captured output. Keep exact byte comparison below.
for field in ('x','y','width','height'):
    COMMAND['operations'][0]['scene']['widgets'][0]['layout']['base'][field]=float(COMMAND['operations'][0]['scene']['widgets'][0]['layout']['base'][field])
h.CASES=CASES


def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value,sensitive=(e[k] for k in ('wait','click','find','value','sensitive'))
    launch,settings,documents,quit=(e[k] for k in ('launch','settings_ready','documents','quit'))
    (folder/'history').write_text('erase-denied\n' if mode=='ERASE-DENIED' else 'allow\n')
    state_root=folder/'state/syspane/state'/h.sha(CASES['profile'].encode())
    record=state_root/'recovery/draft.json'
    def bytes_at(expected):
        actual=record.read_bytes() if record.exists() else None
        assert actual==expected,('recovery bytes',actual,expected)
    def literal():
        generation=h.sha((e['generations']/'current.json').read_bytes())
        return h.encoded(dict(format='syspane.editor-recovery',schema_version='0.1.0',identity=dict(profile=CASES['profile'],generation=generation),command=h.encoded(COMMAND).decode()))
    def ready(title='Network',x=24):
        wait(lambda:value('editor.recovery-status')=='Recovery ready. No unsaved draft.' and sensitive(find('frontend.settings')),12)
        e['select_network'](title,x);e['child']()
    def open_ready():click('frontend.editor');ready()
    def offer(restorable=True):
        wait(lambda:find('editor.recovery-keep') and sensitive(find('editor.recovery-keep')),12)
        assert bool(sensitive(find('editor.recovery-restore')))==restorable
        assert not sensitive(find('frontend.settings')) and not sensitive(find('editor.apply'))
    def edit():
        e['properties']()
        wait(lambda:value('editor.recovery-status')=='Recovery draft retained. Configuration remains unsaved.' and sensitive(find('editor.apply')),12)
        bytes_at(literal());documents()
    def save(navigate=True):
        click('editor.apply')
        wait(lambda:'Configuration saved durably at revision 1.' in e['status']() and sensitive(find('frontend.settings' if navigate else 'editor.recovery-keep')),12)
        documents(True)
    def reopen(raw,restorable=True):
        quit();record.write_bytes(raw);record.chmod(0o600);launch();settings();click('frontend.editor');offer(restorable);bytes_at(raw)
    launch();settings();documents();open_ready();bytes_at(None)
    report['command_sha256']=h.sha((h.ROOT/CASES['expected_command']).read_bytes())
    if mode=='PRIVATE-FIELD':
        e['enter']('editor.value.title','Private draft field');e['enter']('editor.value.x','-')
        assert not sensitive(find('frontend.settings'));bytes_at(None);documents()
        click('editor.revert-fields');ready();bytes_at(None)
    elif mode=='INVALID-RECORD':
        reopen(b'{',False);assert sensitive(find('editor.recovery-discard'))
        click('editor.recovery-keep');wait(lambda:'kept for later' in value('editor.recovery-status'));bytes_at(b'{');documents()
    elif mode=='ORACLE':
        edit();detected=False
        try:bytes_at(literal()+b'\n')
        except AssertionError:detected=True
        assert detected;report['fault_detected']=True
    else:
        edit();raw=record.read_bytes()
        if mode=='CAPTURE-APPLY':save();ready(CASES['title'],CASES['x']);bytes_at(None)
        elif mode=='CRASH-RESTORE':
            e['crash']();bytes_at(raw);launch();settings();click('frontend.editor');offer()
            click('editor.recovery-restore');wait(lambda:sensitive(find('editor.apply')))
            e['select_network'](CASES['title'],CASES['x']);bytes_at(raw);documents()
            click('editor.undo');ready();bytes_at(None);documents()
            click('editor.redo');wait(lambda:sensitive(find('editor.apply')) and record.exists());bytes_at(raw)
            save();ready(CASES['title'],CASES['x']);bytes_at(None)
        elif mode=='KEEP-APPLY':
            reopen(raw);click('editor.recovery-keep');wait(lambda:'kept for later' in value('editor.recovery-status'))
            e['select_network']();e['properties']();wait(lambda:sensitive(find('editor.apply')));bytes_at(raw)
            save(False);offer(False);bytes_at(raw)
        elif mode=='DISCARD':
            reopen(raw);click('editor.recovery-discard');ready();bytes_at(None);documents()
        elif mode=='CANCEL':
            click('editor.cancel');settings();bytes_at(None);documents();open_ready()
        elif mode=='ERASE-DENIED':
            reopen(raw);assert not sensitive(find('editor.recovery-discard'));bytes_at(raw)
            click('editor.recovery-keep');wait(lambda:'kept for later' in value('editor.recovery-status'));documents()
        elif mode in ('REPLACEMENT-RECORD','LOST-RESULT','UNKNOWN-RESULT'):
            e['hold']('store.durable' if mode in ('LOST-RESULT','UNKNOWN-RESULT') else 'store.selector_ready')
            click('editor.apply');mark=wait(e['held']);pid,fd=e['child']();assert mark['pid']==pid
            bytes_at(raw);assert not sensitive(find('frontend.settings'))
            if mode=='REPLACEMENT-RECORD':
                replacement=raw+b'\n';record.write_bytes(replacement)
                (folder/'release').write_text('yes\n');offer(False);documents(True);bytes_at(replacement)
            else:
                documents(True);(folder/'phase').write_text('');(folder/'reconcile').write_text('deny\n')
                signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
                wait(lambda:'Outcome unknown' in e['status']() and e['erased'](),12);bytes_at(raw)
                assert not sensitive(find('editor.apply')) and not sensitive(find('frontend.settings'))
                if mode=='LOST-RESULT':
                    (folder/'reconcile').write_text('allow\n');ready(CASES['title'],CASES['x']);documents(True);bytes_at(None)
                assert not any(json.loads(p.read_bytes())['revision']=='2' for p in e['generations'].glob('*/scene.json'))
        elif mode=='POLICY':
            e['enter']('editor.value.title','Private field to erase');pid,fd=e['child']();(folder/'policy').write_text('deny\n')
            wait(lambda:bool(select.select([fd],[],[],0)[0]),4)
            limit=min(CASES['erasure_after_observed_loss_ms'],EXISTING['erasure_after_observed_loss_ms'])
            observed=time.monotonic();wait(e['erased'],limit/1000)
            report.update(erasure_limit_ms=limit,erasure_ms=(time.monotonic()-observed)*1000)
            bytes_at(raw);assert not sensitive(find('editor.apply'));documents()
        elif mode=='CLOSE':
            quit();bytes_at(raw);documents();return
        else:raise AssertionError(mode)
    quit()


if __name__=='__main__':h.main(exercise,__file__,CASES_PATH,'ir-')
