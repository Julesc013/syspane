from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();now=datetime.now(timezone.utc).isoformat();e=r/'build-support/evidence';prefix='w-10-visibility-controls-'
index=json.loads((e/(prefix+'attempts.json')).read_bytes());native=json.loads((e/(prefix+'native-index.json')).read_bytes())
assert all(json.loads((r/a['record']['path']).read_bytes())['exit']==0 for actions in index['final_runs'].values() for a in actions.values())
def write(path,text):(r/path).write_text(text,encoding='utf-8',newline='\n')
def replace(path,old,new):
 s=(r/path).read_text(encoding='utf-8');assert old in s,path;write(path,s.replace(old,new))
intro='''The [native visibility controls](LINKvisibility-controls-handoff.md) now edit
bounded conditions through the existing draft and persistence owners. Hidden objects
remain selectable in the authored list; current condition diagnostics continue during
held gestures. Nested private buffers erase on cancellation or loss of authority.
The trusted Linux editor component can enable scene 0.5 after capability admission.
Installed ownership, native platform qualification and all five complete editions
remain open.
'''
old='''The [native visibility experiment](LINKnative-visibility-handoff.md) now preserves layout while hiding
conditional content, keeps source/condition diagnostics visible and erases hidden
pixels and inspector payloads. All seven primitive kinds and independent X11/AT-SPI
fault controls pass. This requires an explicit development opt-in; native rule
controls and ordinary editor/installed enablement remain the next gate. No complete
edition or new target qualification is claimed.
'''
for path,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 replace(path,old.replace('LINK',link),intro.replace('LINK',link))
 replace(path,'''recovery. Ordinary conditional scenes still report an unavailable renderer until
native controls and their integration checks pass; only the experiment opts in. This is a component checkpoint; the
five complete editions and their release qualification remain open.''','''recovery. The native controls above now close the trusted EditorForm integration
gate. Direct SceneSurface consumers retain default refusal unless explicitly admitted;
installed ownership and release qualification remain open.''')
 replace(path,'''Native controls/rendering remain required after the authored admission above;
the evaluator alone does not enable conditional widgets.''','''The native controls above supply the admitted Linux component integration;
the evaluator alone does not enable conditional widgets.''')
replace('spec/delivery/current-state.md','"scope": "Native visibility experiment verified; private controls and complete editions remain open"','"scope": "Native visibility controls and trusted EditorForm integration verified; installed ownership and complete editions remain open"')
replace('spec/delivery/current-state.md','"at": "2026-10-08T00:34:15.101366+00:00"','"at": "'+now+'"')
todo='- [x] W-10 native visibility controls: private exact rule/source input, hidden-object selection, current held-gesture diagnostics and independent durable save/reopen/erasure checks. See the [handoff](spec/delivery/visibility-controls-handoff.md). Installed ownership and complete editions remain open.\n'
replace('TODO.md','## First native campaign\n','## First native campaign\n\n'+todo)
readiness='''The [visibility-controls checkpoint](visibility-controls-handoff.md) now adds
native rule input and trusted EditorForm integration to the earlier authored and
rendering contracts. Its executable cases preserve exact scenes, private erasure,
hidden selection, current held-gesture diagnostics and durable reconciliation.
The repository supports continued package-by-package implementation. It does not
establish complete editions or permission to publish. The source-bound handoff and
work-unit row identify the next boundary; historical counts below describe their
own checkpoints rather than current totals.

'''
replace('spec/delivery/implementation-readiness.md','# Implementation readiness and gates\n\n','# Implementation readiness and gates\n\n'+readiness)
replace('spec/delivery/implementation-readiness.md','The October revision closes bounded contract and documentation gaps. It does not\nimplement the native product.','The October revision closed bounded contract and documentation gaps. Subsequent\ncomponent checkpoints above add implementation; the complete native product remains\nunqualified.')
replace('spec/experience/editor.md','''persistence. Native private input, mandatory status preservation and independent
pixels/accessibility checks remain required.''','''persistence. The native rendering and control packages below supply private input,
mandatory status preservation and independent pixel/accessibility component checks.''')
replace('spec/experience/editor.md','''changes preserve the existing conditional scene and its resource closure. Native
condition dialogs and WYSIWYG composition remain open; retain unavailable-preview,
authored recovery and durable/activation distinctions in the meantime.''','''changes preserve the existing conditional scene and its resource closure. The
[native controls package](../delivery/packages/w-10-visibility-controls.md) defines
Always show, When condition matches and mixed Keep unchanged, with nested private
source input and one atomic draft edit. The [checkpoint](../delivery/visibility-controls-handoff.md)
records exact scene, pixel, accessibility and storage evidence.

Trusted EditorForm admission requires the negotiated large-command context and
scene.content/edit-locks/visibility plus configuration.edit-locks/visibility support.
Hidden content keeps its authored-list row and geometry; canvas hits skip it.
Current scene 0.5 content and mandatory diagnostics paint during a held gesture,
while captured geometry and snap targets remain fixed. Private outer and nested
buffers erase together on cancellation or authority/lifetime changes. Keep the
existing unavailable-preview, recovery and durable/activation distinctions.
Installed ownership, full accessibility and other native adapters remain open.''')
replace('spec/experience/scene-bindings.md','''Versioned authored admission is recorded below. Native status/group composition
and editor controls remain required before enablement.''','''Versioned authored admission, native status/group composition and trusted editor
integration are recorded below.''')
replace('spec/experience/scene-bindings.md','''Private native controls, selection/gesture behavior and durable recovery integration
remain required before ordinary editor or installed enablement.''','''The [native controls package](../delivery/packages/w-10-visibility-controls.md) now
admits the trusted EditorForm component after its capability gate. It preserves
authored-list selection, captured gesture geometry, current conditional diagnostics
and exact durable rules. Installed entry paths and other native adapters still need
their own ownership and qualification evidence; direct SceneSurface default refusal
remains unchanged.''')
build='''The [native visibility controls](../../spec/delivery/packages/w-10-visibility-controls.md)
add the shared `VisibilityInput` parser and lazy GTK `EditorVisibilityForm`. Set routes
through `SetWidgetVisibility`; nested binding input changes only the private buffer.
Trusted EditorForm explicitly enables conditional rendering after large-command and
scene/configuration capability admission. Direct SceneSurface defaults false.
Installed host entry has a separate ownership and qualification gate.

Run the ordinary preflight/configure/build commands, then `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])' --output-on-failure`.
The owned non-root Linux laboratory also runs `ctest --preset linux-x64-gcc13
-R '^native[.]EDITOR-VISIBILITY$' --output-on-failure`. Its sixteen cases exercise
real controls, exact scenes, held gestures, hidden pixels/names, nested erasure and
save/reopen/reconciliation, with deliberate wrong-rule/frozen/retained-input controls.
Frozen inputs are tests/editor/visibility-controls-cases.json. The
[handoff](../../spec/delivery/visibility-controls-handoff.md) distinguishes component
restart from a separate-process interruption and records the remaining release gates.

'''
replace('docs/developers/build.md','# Developer setup and checks\n\n','# Developer setup and checks\n\n'+build)
replace('docs/developers/build.md','''adds `SurfaceConfig.experimental_visibility`, default false. Only a trusted owned
laboratory sets it for scene 0.5. Resource capability declarations do not enable it;
ordinary editor and installed entry paths retain the refusal gate. SceneSurface owns''','''adds `SurfaceConfig.experimental_visibility`, default false. Trusted EditorForm now
sets it after the admission above; resource declarations alone cannot enable it.
Installed entry paths retain their separate integration gate. SceneSurface owns''')
replace('docs/developers/build.md','''continuing private rule controls, selection/gestures and native persistence/recovery.''','''continuing installed ownership and complete-edition integration.''')
user='''Select an object and choose Visibility to edit its own condition. Always show
removes that condition; a container's condition can still apply. When condition
matches lets you choose a data source, comparison, typed value and unit. New rules
start with this host's network receive bytes greater than 0 byte. Choose source
opens the existing binding controls. Set visibility creates one reversible draft
edit; Apply saves it. Cancel discards the private input.

For objects with different own conditions, Keep unchanged preserves each rule.
Choosing another mode replaces all selected own rules together. Hidden objects
remain in the object list: select them there to change or clear their condition.
Missing or failed source information remains visible as a diagnostic. During a drag,
conditions and diagnostics update while the captured geometry remains fixed.

'''
replace('docs/users/configuration.md','Use Snap to grid or Snap to guides while dragging or resizing fixed widgets.\n',user+'Use Snap to grid or Snap to guides while dragging or resizing fixed widgets.\n')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());w=next(x for x in v['work_units'] if x['id']=='W-10');w['specs'].append('SP-W10-VISIBILITY-CONTROLS');w['package']='delivery/packages/w-10-visibility-controls.md';w['evidence']='delivery/visibility-controls-handoff.md'
w['notes']='Shared typed drafts drive the Linux GTK editor: selection, pointer/keyboard geometry, arrangement, grouping, snapping, native content/binding/creation/layout/container/lock input, exact resource-aware persistence and independent recovery/erasure evidence. Native visibility controls now support bounded exact conditions, mixed bulk edits, nested private source input, hidden authored-list selection and current conditional diagnostics during held geometry. Trusted EditorForm admits scene 0.5 only after command/capability admission. Frozen examples, original failures and deliberate wrong-rule/frozen-preview/retained-input controls are preserved. Historical native accessibility timeout causes remain open; passing current regressions do not explain them. W-10 remains in progress: typography and remaining property contracts, clipboard authority, recovery drafts, installed scene-aligned entry/restoration, complete accessibility/performance and other native adapters remain required. Read the linked checkpoint and earlier handoffs for source-bound evidence; all five complete editions remain open.'
w=next(x for x in v['work_units'] if x['id']=='W-09');w['notes']=w['notes'].replace('Ordinary scene 0.5 rendering remains gated until W-10 private rule controls, selection/gestures and native durable recovery integration pass.','W-10 now supplies private rule controls, hidden selection, held-gesture diagnostics and durable integration for trusted EditorForm. Direct SceneSurface defaults to refusal; installed entry still needs its own admission.')
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
failed=[a for a in index['attempts'] if a['exit']]
text=f'''---
type: "SysPane Work Record"
title: "Native conditional editing checkpoint"
description: "Exact private visibility input, hidden selection and current held-gesture diagnostics through the existing durable editor."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-VISIBILITY-CONTROLS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-VISIBILITY-CONTROLS", "SP-NATIVE-VISIBILITY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native conditional editing checkpoint

Source baseline: {index['source_base']}. The
[package](packages/w-10-visibility-controls.md) and literal expected scenes were
frozen and independently schema-validated before production edits. Their bytes remain
unchanged. This checkpoint closes the Linux editor component integration boundary.

## Implemented behavior

VisibilityInput hydrates equal own rules exactly, preserves mixed selections through
Keep unchanged and provides explicit Always show/When condition matches choices.
Typed values retain signed/unsigned integer extremes and escaped control text.
Shared authored equality now compares mixed integer/real and signed/unsigned values
without rounding or wrapping, so mixed-rule detection, draft history, dirty state
and emitted scene replacements agree. Numerically equal forms such as 1 and 1.0
retain existing no-op behavior. Eleven additional literal numeric pairs were frozen
and checked independently with Decimal before this repair.
The private source dialog reuses existing binding controls and rejects non-singleton
or multi-result sources without mutating the outer buffer or draft. One Set routes
through the existing atomic SetWidgetVisibility operation, history and command 0.7.

The lazy GTK dialog bounds private inputs and erases fields, models, errors, selected
IDs and nested references on cancellation, successful Set or authority/lifetime changes.
Trusted EditorForm enables scene 0.5 only after large-command and scene/configuration
capability admission. Direct SceneSurface default refusal remains unchanged.
Hidden content keeps authored-list selection and geometry; canvas hit testing skips
it. During scene 0.5 gestures, content and mandatory diagnostics use current data,
while captured geometry, variants and snap targets remain fixed. Release commits
the captured delta once even if the selected payload became hidden.

## Executed evidence

All 159 affected checks pass on each development profile. Full non-native suites
pass 336 Linux GCC13, 333 Windows GCC15 and 330 v141_xp checks (999 total).
The historical toolset runs on contemporary Windows; this does not qualify XP.

The new native family passes sixteen frozen scenarios using real GTK controls,
independent owned-X11 pixels, explicit AT-SPI replies and exact stored documents.
It covers hidden-list selection, mixed/clear edits, direct source changes, exact
uint64 input, invalid values/sources, outer/nested cancellation and revocation,
held hide/diagnostic transitions, history, save/reopen and lost acknowledgement.
Wrong stored predicates, frozen preview pixels and retained private input each
have a positive observed fault witness; missing replies or timeouts cannot pass.

The restart scenario reconstructs the transaction/store owner with a new epoch in
the same laboratory editor process, reconciles the original request and preserves
the selecting record at revision 41. Reopen launches a fresh editor process.
Separate controller-process interruption remains covered by the earlier
[authored admission](visibility-admission-handoff.md); this fixture does not itself
claim a separate controller-process crash or installed product routing.

Twelve existing native editor matrices, fifteen rendering regressions and the
native all-kind SCENE-VISIBILITY checks pass. {len(index['attempts'])} source-bound
attempts and {len(native)} native archives preserve successes and original failures.
{len(failed)} build/test attempts failed. Initial builds caught misleading indentation
in reload cleanup and a comma declaration inside a G_CALLBACK lambda macro argument.
The numeric regressions then failed mixed-rule and atomic-edit assertions: the JSON
library equates distinct large integer/real values and signed -1 with UINT64_MAX.
Two builds of the repair caught an unintended std::equal overload selected by argument
lookup; a distinct helper name resolves it. All original failures and source bytes
remain available. The preliminary registration helper also selected a nonexistent
target before any build/test; its stop record and correction are preserved.

A native rerun then exposed blank geometry fields despite a valid held outline and
visible text. Telemetry erases cached nodes; selecting an authored row before repaint
hydrated empty geometry, and later frames did not refresh clean fields. A deterministic
sample-then-native-selection stimulus reproduced the same failure before production
changed. EditorForm now hydrates clean geometry when its resolved variant returns,
while preserving dirty private property input. Original and deterministic failures,
screenshots, explicit field values and the unchanged acceptance outcomes are retained.
This establishes that race separately from older unexplained accessibility timeouts.

Records: build-support/evidence/w-10-visibility-controls-attempts.json,
w-10-visibility-controls-native-index.json, w-10-visibility-controls-verification.json,
w-10-visibility-controls-staging.json and visibility-controls-handoff.json. They bind
source archives, commands, fixed inputs, native observations and artifact identities.
Existing 176 schema/fixture files remain byte-identical to the baseline.

Workspace preflight stopped two build admissions when the ordinary reservation did
not fit. Cleanup verifies exact committed bytes before removing output duplicates.
The receipts cover 36 native folders, 109 attempt folders, 25 historical profile
files and 764 copied GNOME source/archive files. Observations and journals remain
preserved. Three native-index searches found no remaining complete duplicates and
stopped before deletion; an attempt-cleanup parent check also stopped before its
first deletion and was corrected to retain each target's own parent.

Commit 86a730e preserves raw pre-repair evidence before its duplicate outputs were
reclaimed. The attempt register records both source bases and exact source archives;
that evidence-only commit does not claim a completed feature. The combined workspace
bound remains 7 GiB with ordinary per-action reservations. All receipt/helper bytes
are retained, including the failed cleanup/preflight records.

## Required continuation

Close typography and remaining property contracts, clipboard authority and recovery
drafts, then connect installed controller/catalog/policy ownership and scene-aligned
entry/restoration. Keep native acceptance independent of implementation expectations.
W-09/W-10, full accessibility/performance, other adapters and historical laboratories,
and all five complete editions remain open. Historical accessibility timeout causes
remain unresolved; passing these component regressions does not explain them.
'''
write('spec/delivery/visibility-controls-handoff.md',text)
with (r/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n# Preserve exact native visibility-control attempts, failures and executed helpers.\nbuild-support/evidence/w-10-visibility-controls-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-10-visibility-controls-history/support/*.ps1 -whitespace\n')
print('Documented actual component boundary and remaining release work.')
