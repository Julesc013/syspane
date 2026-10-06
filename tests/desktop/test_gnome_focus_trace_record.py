"""Reject unbound native decisions and instrumentation-induced attribution."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_focus_trace import validate, interpret, compare, HANDLER, PREFIX

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(6)]
TRACED=next(r for r in REPORTS if r['focus_baseline_mode']=='ding' and r['focus_trace'])
OBSERVATION=TRACED['observation']['focus_baseline']
RAW=TRACED['logs']['shell.log']


def shifted(line, delta):
    match=PREFIX.fullmatch(line)
    hour,minute,second,millis=map(int,match.group(1,2,3,4))
    clock=(((hour*60+minute)*60+second)*1000+millis+delta)%86400000
    second,millis=divmod(clock,1000); minute,second=divmod(second,60); hour,minute=divmod(minute,60)
    return line[:match.start(1)]+f'{hour:02}:{minute:02}:{second:02}.{millis:03}'+line[match.end(4):]


class FocusTraceEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=[validate(r,BUILD) for r in REPORTS]
        cls.decision=interpret(RAW.encode(),OBSERVATION)

    def reject_log(self, text):
        with self.assertRaises(ValueError):interpret(text.encode(),OBSERVATION)

    def reject_record(self, mutate):
        value=copy.deepcopy(TRACED)
        mutate(value)
        with self.assertRaises(ValueError):validate(value,BUILD)

    def test_all_six_native_observations(self):
        result=compare(self.results)
        self.assertEqual(result['outcome'],'stable')
        self.assertTrue(all(p['selection_matches_restored_role'] for p in result['pairs'].values()))

    def test_missing_executed_handler(self):
        self.reject_log(RAW.replace(HANDLER,'Registering show-desktop',1))

    def test_extra_executed_handler(self):
        line=next(s for s in RAW.splitlines() if HANDLER in s)
        self.reject_log(RAW+'\n'+line)

    def test_unknown_native_xid(self):
        self.reject_log(RAW.replace('Focusing workspace MRU window '+hex(OBSERVATION['icon_manager']['window']),
                                    'Focusing workspace MRU window 0xdeadbeef'))

    def test_missing_selection_cannot_use_cleanup_selection(self):
        lines=RAW.splitlines()
        lines[self.decision['selection_line']-1]=''
        self.reject_log('\n'.join(lines))

    def test_ambiguous_selection(self):
        lines=RAW.splitlines()
        at=self.decision['selection_line']-1
        lines.insert(at,lines[at])
        self.reject_log('\n'.join(lines))

    def test_missing_focus_assignment(self):
        lines=RAW.splitlines(); lines[self.decision['focus_assignment_line']-1]=''
        self.reject_log('\n'.join(lines))

    def test_missing_foreground_show(self):
        lines=RAW.splitlines(); lines[self.decision['foreground_show_line']-1]=''
        self.reject_log('\n'.join(lines))

    def test_click_before_decision_is_not_restore(self):
        lines=RAW.splitlines(); at=self.decision['selection_line']-1
        prefix=lines[at].split('FOCUS:')[0]
        lines.insert(at,prefix+'FOCUS: Focusing 0x400003 due to button 1 press (display.c)')
        self.reject_log('\n'.join(lines))

    def test_keyboard_boundary_before_decision(self):
        lines=RAW.splitlines(); at=self.decision['selection_line']-1
        prefix=lines[at].split('FOCUS:')[0]
        lines.insert(at,prefix+'KEYBINDINGS: Handling key event')
        self.reject_log('\n'.join(lines))

    def test_late_decision(self):
        lines=RAW.splitlines(); at=self.decision['selection_line']-1
        lines[at]=shifted(lines[at],201)
        self.reject_log('\n'.join(lines))

    def test_backwards_decision_clock(self):
        lines=RAW.splitlines(); at=self.decision['selection_line']-1
        lines[at]=shifted(lines[at],-1)
        self.reject_log('\n'.join(lines))

    def test_action_separation_mismatch(self):
        value=copy.deepcopy(OBSERVATION)
        value['interval']['actions'][1]['start_us']+=100000
        with self.assertRaises(ValueError):interpret(RAW.encode(),value)

    def test_raw_log_hash(self):
        self.reject_record(lambda r:r['native_focus_log'].update(sha256='0'*64))

    def test_raw_log_path(self):
        self.reject_record(lambda r:r['native_focus_log'].update(path=r['foreground_events']['path']))

    def test_report_log_truncation(self):
        self.reject_record(lambda r:r['logs'].update({'shell.log':r['logs']['shell.log'][:-100]}))

    def test_trace_topics(self):
        self.reject_record(lambda r:r['environment']['explicit'].update(MUTTER_DEBUG='all'))

    def test_trace_flag(self):
        self.reject_record(lambda r:r.update(focus_trace=False))

    def test_unowned_logging(self):
        self.reject_record(lambda r:r['environment']['explicit'].update(MUTTER_USE_LOGFILE='1'))

    def test_missing_pair(self):
        with self.assertRaises(ValueError):compare(self.results[:-1])

    def test_duplicate_pair(self):
        with self.assertRaises(ValueError):compare(self.results[:-1]+[self.results[0]])

    def test_instrumentation_difference_inconclusive(self):
        rows=copy.deepcopy(self.results)
        rows[0]['f9_delivered']=not rows[0]['f9_delivered']
        self.assertEqual(compare(rows)['outcome'],'inconclusive')

    def test_selection_not_forced_to_match_external_focus(self):
        rows=copy.deepcopy(self.results)
        next(r for r in rows if r['mode']=='ding' and r['traced'])['native_decision']['selected_role']='foreground'
        self.assertFalse(compare(rows)['pairs']['ding']['selection_matches_restored_role'])


if __name__=='__main__':unittest.main()
