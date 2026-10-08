from pathlib import Path
from datetime import datetime, timezone
import json
import re
r = Path.cwd()
index = json.loads((r/'build-support/evidence/w-10-theme-controls-attempts.json').read_bytes())
now = datetime.now(timezone.utc).isoformat()

def write(name, text):
    (r/name).write_text(text, encoding='utf-8', newline='\n')

def replace(name, old, new):
    text = (r/name).read_text()
    assert old in text, (name, old)
    write(name, text.replace(old, new))

def append(name, text):
    with (r/name).open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(text)

intro = '''The [native font-controls checkpoint](LINKtheme-controls-handoff.md) connects
base and role fonts to the Linux editor's private controls, current draft preview,
undo/redo and durable save/reopen. Independent pixels, exact stored artifacts,
lost-result recovery and bounded erasure pass. Clipboard/recovery drafts, installed
ownership and all five complete editions remain open.

'''
for name, link in [('README.md', 'spec/delivery/'), ('spec/delivery/current-state.md', '')]:
    replace(name, 'The [theme-history checkpoint]', intro.replace('LINK', link)+'The [theme-history checkpoint]')
    replace(name, 'package allocations. Native font controls and their independent preview/save/reopen\nevidence remain next; all five complete editions remain open.', 'package allocations. Native font controls now have the checkpoint above; all five\ncomplete editions remain open.')
    replace(name, 'editor resource history now has the checkpoint above; native font controls and all\nfive complete editions remain open.', 'editor resource history and native font controls now have the checkpoints above;\nall five complete editions remain open.')
    replace(name, 'Native controls still require editor integration and independent preview/save/reopen\nevidence before enabling edited theme rendering.', 'The font-controls checkpoint above supplies explicitly admitted Linux editor\nintegration and independent preview/save/reopen evidence.')
    replace(name, 'trusted development admission; native theme-authoring controls and their editor\nintegration are next. Installed ownership and all five complete editions remain open.', 'trusted development admission; the native font-controls checkpoint above supplies\neditor integration. Installed ownership and all five complete editions remain open.')
text = (r/'spec/delivery/current-state.md').read_text()
text = re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex', at=now, scope='Native base/role font controls and independent preview/save/reopen/erasure verified; installed ownership and complete editions remain open')), text, flags=re.M)
write('spec/delivery/current-state.md', text)
replace('spec/delivery/current-state.md', 'The immediate theme-editing boundary is native base/role font controls: use the\nshared atomic history and command owner, then prove preview pixels, accessibility,\nsave/reopen, lost results and private-input erasure before trusted editor admission.\nUse the [theme-history handoff](theme-history-handoff.md) and W-10 row; preserve', 'Native base/role fonts now have independent control, pixel, persistence and erasure\nevidence. Continue W-10 with bounded clipboard/recovery-draft contracts and installed\ncontroller/catalog/policy ownership, including scene-aligned entry and restoration.\nUse the [font-controls handoff](theme-controls-handoff.md) and W-10 row; preserve')
replace('TODO.md', '- [ ] W-10 native theme editing: base/role font controls, borrowed draft resource preview, independent pixels/accessibility/save/reopen/lost-result/erasure evidence and trusted editor admission. Preserve mandatory diagnostics and existing limits.', '- [x] W-10 native theme editing: base/role fonts, current draft resource preview, exact pixels/artifact save/reopen, lost-result recovery and private erasure under explicit trusted admission. See the [handoff](spec/delivery/theme-controls-handoff.md).\n- [ ] W-10 remaining delivery: close bounded clipboard/recovery-draft contracts and installed controller/catalog/policy ownership, then scene-aligned entry/restoration, full accessibility/performance and complete editions.')
replace('spec/delivery/implementation-readiness.md', 'now connects atomic editor resources, history and Apply/reload. Native font controls\nand their independent evidence remain next; complete editions remain unqualified.', 'now connects atomic editor resources, history and Apply/reload. The\n[font-controls checkpoint](theme-controls-handoff.md) adds explicitly admitted Linux\ncontrols and independent pixels, exact storage, restart and erasure checks. Installed\nownership and complete editions remain unqualified.')
replace('spec/delivery/implementation-readiness.md', 'roles with explicit development admission. Native theme authoring and trusted editor\nintegration remain the next gate.', 'roles with explicit development admission. The font-controls checkpoint now closes\nthat Linux editor integration gate; other adapters and full qualification remain open.')
replace('spec/experience/editor.md', 'the existing transaction owner. Native base/role font controls, borrowed-resource\npreview, independent pixels/accessibility and private-input erasure remain required\nbefore trusted EditorForm typography admission.', 'the existing transaction owner. The [native font-control contract](../delivery/packages/w-10-theme-controls.md)\nconnects a scene-wide Fonts modal to that draft and its matching resources. Unchanged\nSet preserves exact bytes; explicit empty and omitted role overrides remain distinct.\nPrivate input erases on every lifetime boundary. Trusted Linux EditorForm typography\nrequires all seven capabilities and large-command admission; direct renderer defaults\nremain unchanged. The [checkpoint](../delivery/theme-controls-handoff.md) supplies\nindependent pixels, exact durable artifacts, reopen, recovery and erasure evidence.')
replace('spec/experience/scene-theme.md', 'authoring and trusted editor integration remain the following boundary.', 'authoring and trusted Linux editor integration now have the\n[font-controls checkpoint](../delivery/theme-controls-handoff.md).')
replace('spec/experience/scene-theme.md', 'history and native controls remain required before native theme editing is enabled.', 'history and native controls now have their linked contracts and independent\nLinux evidence; other adapters and installed ownership remain required.')
replace('spec/experience/scene-theme.md', 'atomic editor resources and Apply/reload. Native authoring still requires font controls,\nindependent pixels/save/reopen and policy-loss erasure evidence.', 'atomic editor resources and Apply/reload. The [font-controls contract](../delivery/packages/w-10-theme-controls.md)\nadds exact base/role input, current resource preview and private erasure. Its native\nevidence permits explicitly admitted Linux component integration, not release qualification.')
append('docs/developers/build.md', '''

The [native font-controls package](../../spec/delivery/packages/w-10-theme-controls.md)
adds the scene-wide Fonts modal to the Linux EditorForm. `theme_control_input` and
`theme_control_edit` preserve exact no-ops and distinguish inherited roles from an
explicit empty map. Set authors one atomic draft edit; Apply publishes command 0.8.
Use settings theme restores scene inheritance and ignores uncommitted private input.
Each role retains its raw private values while switching targets; inactive roles do
not invalidate Set. Private buffers, models and snapshots erase on every close,
policy, disconnection, topology and reload boundary.

Preview, content choices and widget creation borrow the draft's matching resources.
SceneSurface owns a validated snapshot sharing immutable package allocations.
EditorForm retains capability admission, not a second original catalog. Font-only
changes resolve new intrinsic metrics in the queued native paint, avoiding a duplicate
immediate render before private-erasure observations. Existing geometry-edit paths
retain immediate resolution. Display permission remains distinct from theme.edit.

After workspace preflight/configure/build, run
`ctest --preset <profile> -R '^editor[.]THEME-CONTROLS-' --output-on-failure`, the
affected editor/settings/configuration/protocol/component families and full portable
suite. In the existing non-root Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-FONTS|EDITOR-VISIBILITY|EDITOR-CONTENT-PROPERTIES|EDITOR-WIDGET-CREATION|THEME-HISTORY|THEME-COMMANDS|ROLE-COMPOSITION|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM)$' --output-on-failure`.
The 19 font cases operate native controls, compare literal independent TextProbe
requests with observed canvas pixels, inspect every selected package byte and reopen
the committed store. Held text objects are positively identified before the stimulus;
independent explicit GetText replies are dispatched together within one 200-ms bound.
Timeouts and unavailable replies cannot count as erasure. The
[handoff](../../spec/delivery/theme-controls-handoff.md) records failures and corrections.
''')
units = json.loads((r/'spec/delivery/work-units.json').read_bytes())
row = next(v for v in units['work_units'] if v['id'] == 'W-10')
row['specs'].append('SP-W10-THEME-CONTROLS')
row['package'] = 'delivery/packages/w-10-theme-controls.md'
row['evidence'] = 'delivery/theme-controls-handoff.md'
row['notes'] = 'Native Linux base/role font controls now use shared atomic history, current borrowed resources and command 0.8. Independent literal-font pixels, exact package bytes, save/reopen, reset, policy denial, lost-result reconciliation and private erasure pass; all seven capabilities and large commands gate trusted typography. W-10 remains in progress: bounded clipboard/recovery drafts, installed controller/catalog/policy ownership and scene-aligned entry/restoration remain, followed by full accessibility/performance and other adapters. Preserve historical observation failures and all five complete-edition gates.'
write('spec/delivery/work-units.json', json.dumps(units, indent=2)+'\n')
write('spec/delivery/theme-controls-handoff.md', f'''---
type: "SysPane Work Record"
title: "Native font controls checkpoint"
description: "Exact private base/role input, current resource preview and independent durable native evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-THEME-CONTROLS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-CONTROLS", "SP-THEME-HISTORY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native font controls checkpoint

Baseline {index['source_base']}. The [package](packages/w-10-theme-controls.md)
connects exact base and body/label/value/diagnostic fonts to the Linux editor.
The scene-wide Fonts action opens private bounded fields and explicit inherited or
custom role choices. Empty custom maps remain distinct from omission. Switching
targets preserves raw input; inactive invalid values are ignored. An unchanged Set
preserves the exact theme. Changed Set uses one existing atomic draft operation;
Apply saves and Use settings theme restores scene inheritance. Undo/redo and all
resource, transport and history limits remain unchanged.

Preview, content choices and widget creation now use the current matching draft
resource borrow. SceneSurface owns its validated retained snapshot; EditorForm drops
the redundant original catalog. All seven existing capabilities and large-command
admission gate trusted typography. Losing edit permission does not itself revoke
display permission. Direct renderer consumers retain their default refusal.

## Verification and preserved failures

Four portable families cover exact hydration/no-ops, all role maps, inactive and
invalid values, atomic history, reset, pending state and capability loss. All 187
affected checks pass per profile. Full portable suites pass 364 Linux GCC13, 361
Windows GCC15 and 358 v141_xp checks (1083 total). Historical compiler execution on
contemporary Windows does not qualify a historical operating system.

Eleven native families pass: EDITOR-FONTS, EDITOR-VISIBILITY,
EDITOR-CONTENT-PROPERTIES, EDITOR-WIDGET-CREATION, THEME-HISTORY, THEME-COMMANDS,
ROLE-COMPOSITION, RESOURCE-GENERATIONS, CONTENT-COMMANDS, SETTINGS-FORM and EDITOR-FORM.
The 19 font cases verify base/all roles, empty/inherited maps, no-op/cancel,
invalid correction, undo/redo, reset, exact durable save/reopen, cancelled requests,
policy-hidden results and cross-epoch reconciliation without duplicate publication.
Private native references erase within 200 ms on successful modal completion,
cancel, policy, capability loss, disconnect, topology and close. Deliberate retained
text, frozen preview and wrong committed font witnesses are positively detected.
Literal fonts drive an independent TextProbe; complete selected package bytes are
compared against fixed examples rather than inferred from the editor's output.

The original frozen artifact generator accidentally inserted another expected
artifact object as the license. Existing committed source/authoring/command fixtures
specify MIT. A separate audited correction retains the original freeze and failing
history result, changes only license-derived artifact identities/bytes and their
scene/selection references, and preserves all font examples and contract behavior.
No schema or product acceptance criterion changed.

Other preserved failures include a compiler indentation warning; the first pixel
oracle's single-block alpha path; role-dialog erasure deadlines; a cached hidden
modal treated as open; a transient empty accessible canvas during repaint; and a
denial test that expected a disclosed result despite existing policy concealment.
The single-block oracle now requests its authored background directly from the
independent text probe; multi-block composition retains the fixed 4-DIP gaps.
The Fonts button is visible in the lower action row. Timing instrumentation showed
roughly 170 ms of synchronous role application/preview before another render.
Font-only edits now resolve metrics once in the queued paint. Text interfaces are
positively identified before input; their independent explicit reads run together
under the unchanged 200-ms deadline. Instrumentation is absent from final production.
Modal tests await actual showing state; positive canvas observations await repaint.
Denied results remain unknown with hidden facts, then retrieve the original conflict
after regrant. Original failures and diagnostic source snapshots remain intact.

Evidence uses build-support/evidence/w-10-theme-controls: attempts, native-index,
verification and staging, plus theme-controls-handoff.json. The attempt index preserves
{len(index['attempts'])} executions, source archives, fixed and corrected inputs, native
fault witnesses and final artifact identities. All 199 baseline schema/fixture files
retain their bytes. Specification/schema/fixture/tooling and sealed-integrity checks
accompany this record; two existing Windows symlink assertions remain skipped.
The staged-byte audit found CRLF in the new dialog source. Canonical LF normalization
changed no other bytes; rebuilding produced identical executables, preserving the
tested artifact identities. Its first build preflight refusal and successful rebuild
are recorded separately. Verified duplicate copies of the previous checkpoint and
current archived native outputs were reclaimed with hash/containment receipts inside
the unchanged 7-GiB allocation; all archived evidence remains retained.

## Next admitted work

Continue W-10 with bounded clipboard/recovery-draft contracts and installed
controller/catalog/policy ownership. Connect scene-aligned desktop entry/restoration
to the independent recovery owner. Preserve current resource and disclosure rules,
fixed examples, failed evidence and the work graph. Continue unrelated platform
tracks when their environments are available.

Full accessibility/performance, unresolved historical observation causes, other
native/storage adapters, all five complete editions and release qualification remain
open. This checkpoint qualifies the owned Linux component experiment only; W-10 and
the complete release objective remain in progress.
''')
append('.gitattributes', '\n# Preserve exact native font-control attempts and independently fixed examples.\nbuild-support/evidence/w-10-theme-controls-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-10-theme-controls-history/support/*.ps1 -whitespace\n')
