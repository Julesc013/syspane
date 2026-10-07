from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
 s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
def append(p,s):write(p,(r/p).read_text()+s)
change('README.md','The [native observation checkpoint]', '''The [layout-authoring checkpoint](spec/delivery/layout-authoring-handoff.md) adds
fixed, flow, canvas, stack and grid controls, responsive breakpoints, priority,
sibling order and whole-group display assignment. Direct fixed-layout edits target
the active variant. Independent native checks cover pixels, save/reopen, history,
policy erasure and restart. Installed integration and full editions remain open.

The [native observation checkpoint]''')
change('TODO.md','- [ ] W-10 complete editor:', '- [x] W-10 layout authoring: all existing layout kinds and breakpoints, atomic display/order/priority edits, active fixed-variant gestures and independent native persistence/erasure checks. See the [handoff](spec/delivery/layout-authoring-handoff.md).\n- [ ] W-10 complete editor:')
change('TODO.md','responsive/flow container transforms, responsive arrangement, remaining property/authoring contracts','responsive/flow container group transforms, remaining property/authoring contracts')
append('docs/users/configuration.md','''
## Layouts and responsive editing

Select one object and choose **Layout**. Leaves offer fixed or flow sizing; groups
offer fixed, canvas, stack or grid. The Geometry tab exposes each kind's dimensions,
constraints, anchor, axis, gap and overflow options. Changing kind keeps its private
input until the panel closes. Invalid numbers stay available for correction.

Choose Base or a breakpoint. **Add breakpoint** copies the selected variant and
requires a minimum display width. Up to eight thresholds must stay strictly
increasing; they are not automatically sorted. **Remove breakpoint** removes the
selected row. Threshold equality activates that variant using the display's safe
width. Direct drag, resize, keyboard and arrangement operations edit the currently
active fixed variant; the status text identifies it. Flow objects use constraints
and sibling order instead of direct movement.

Assignment changes priority and zero-based sibling position. Changing a local
display ID or portable role moves the object's entire top-level group, including
its descendants. Missing displays retain the assignment for later recovery.

**Set layout** makes one undoable draft change; **Apply** saves separately. Cancel
or Escape discards private input. Policy, owner and topology changes erase the
panel. If a topology change switches a variant while numeric geometry is buffered,
**Set properties** rejects it; **Revert fields** loads the active variant. These
controls are currently exercised in the owned Linux development editor, as scoped
in the [handoff](../../spec/delivery/layout-authoring-handoff.md).
''')
append('docs/developers/build.md','''
### Layout and responsive authoring

`editor_layout.*` projects bounded private input into existing atomic draft edits.
`RootDisplayEdit` assigns a whole top-level subtree in one operation, retaining the
128-operation limit for 256-node scenes. Optional variant indices on move, resize,
align and distribute preserve existing base-only callers. GTK captures resolved
variants for direct operations and rejects stale buffered geometry after topology
changes. Native tree selection retains its model during selection callbacks.

After ordinary workspace preflight and profile build, run
`ctest --preset <profile> -R "^editor[.]LAYOUT-" --output-on-failure`.
Eight families cover exact scenes, kinds, breakpoints, display/order, atomic bounds,
policy and independent geometry. In the unprivileged Linux laboratory run
`ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-LAYOUT$" --output-on-failure`.
Twenty-one cases exercise actual controls, pixels, saved resources, reopen,
topology, cancellation, recovery and erasure, including positive fault controls.
The existing nine native matrices remain required regressions for shared-owner
changes. See the [handoff](../../spec/delivery/layout-authoring-handoff.md).
''')
append('spec/experience/editor.md','''
## Layout authoring boundary

The [layout-authoring package](../delivery/packages/w-10-layout-authoring.md)
closes private input for every existing layout kind, ordered responsive variants,
priority, sibling position and whole-root display intent. Direct fixed operations
target explicit resolved variants; base-only callers remain compatible. The
[checkpoint](../delivery/layout-authoring-handoff.md) records component evidence.
Flow/container group transformations, remaining properties, installed ownership
and full native editions remain required.
''')
change('spec/delivery/current-state.md','The latest [native observation checkpoint]', '''The latest [layout-authoring checkpoint](layout-authoring-handoff.md) adds every
existing layout kind, responsive breakpoint input, priority, sibling order and
whole-root display intent. Native fixed gestures and arrangement edit the active
variant; topology invalidates stale buffered geometry. Portable and independent
native checks cover exact scenes, pixels, persistence, recovery and erasure.
Continue flow/container group transformations and remaining property contracts,
then installed ownership and scene-aligned entry/restoration. W-10 and every full
edition remain in progress.

The earlier [native observation checkpoint]''')
p='spec/delivery/current-state.md';s=(r/p).read_text();s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Native layout authoring and active fixed variants')),s,flags=re.M);write(p,s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());w=next(w for w in v['work_units'] if w['id']=='W-10');w['specs']+=['SP-W10-LAYOUT-AUTHORING'];w['package']='delivery/packages/w-10-layout-authoring.md';w['evidence']='delivery/layout-authoring-handoff.md';w['notes']+=' Native layout authoring covers existing kinds/breakpoints, priority/order/display and active fixed-variant direct operations. Flow/container group transformations, remaining properties and installed ownership remain open.';write(p,json.dumps(v,indent=2)+'\n')
write('spec/delivery/layout-authoring-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native layout-authoring checkpoint"
description: "Existing layout grammar and active fixed variants through the shared draft."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-LAYOUT-AUTHORING-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-LAYOUT-AUTHORING", "SP-NATIVE-OBSERVATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native layout-authoring checkpoint

Source baseline: `{base}`. The [package](packages/w-10-layout-authoring.md)
adds fixed/flow leaf and fixed/canvas/stack/grid group authoring, ordered responsive
breakpoints, priority, sibling order and whole-root display assignment. It preserves
scene/layout/wire versions and the existing renderer, resource and transaction owners.
W-10 remains in progress; complete editions remain required.

Each variant/kind retains private input. Set layout is one atomic undo step; Apply
persists separately. Direct move/resize/arrange operations capture active fixed
variants without changing inactive layouts. Topology cancels gestures and layout
input; buffered geometry rejects a changed variant. Root display assignment handles
256 nodes in one typed operation without expanding the batch-operation limit.

## Verification

Complete authored/expected scenes, exact resolved geometry, package and unchanged
resource/schema inputs were frozen before implementation. Eight portable families
cover kinds, thresholds, variant indices, order/display, bounds, atomic rejection,
history, current policy and exact submitted scenes. All 132 affected checks pass on
Linux GCC 13, Windows GCC 15 and v141_xp on contemporary Windows.

Twenty-one owned Linux layout cases cover actual controls, rendered geometry,
save/reopen, history, topology, cancellation, policy erasure and lost acknowledgement.
Wrong persisted layout, retained private input and frozen preview require positive
fault observations. Existing observation (7), creation (17), binding (15), content
(15), snap (13), group (11), arrangement (14), editor (20) and large-command (24)
matrices pass: 157 native cases across ten matrices.

Every failed and successful attempt retains source snapshots and binary identities.
The evidence is under `build-support/evidence/w-10-layout-authoring-attempts.json`,
`w-10-layout-authoring-native-index.json`, `w-10-layout-authoring-verification.json`
and `w-10-layout-authoring-staging.json`; the machine handoff is
`build-support/evidence/layout-authoring-handoff.json`.

The first strict build rejected misleading indentation; the initial portable test
incorrectly reloaded a pending request. Both failures are preserved. Native setup
also exposed an initially unselected GTK cursor for which Home did nothing and a
dialog-close/open timing race. The harness now makes an explicit keyboard selection,
awaits editor re-enablement and requires visible modal controls. An alignment sample
incorrectly included transparent pixels over another expected widget; it now checks
the unobscured caption without changing frozen scenes or geometry. List selection
no longer rebuilds its own model during the selection callback.

The topology case initially clipped a fixed child on a 399-DIP display, which
requires the existing surface alternative. Native controls now temporarily fit
the root and child for the visible variant-change exercise and restore all frozen
geometry before saving. Combo activation uses its native accessibility action so
dialog resizing cannot invalidate a pointer rectangle before allocation completes.

A separate button-focus failure after modal closure retains X11 ownership and
accessibility-state evidence. Layout buttons use native pointer activation; direct
keyboard editing and list selection remain exercised. This does not qualify all
keyboard/accessibility paths or explain the earlier intermittent focus failures.

## Remaining work

Close flow/container group transformations, lock/visibility/typography, clipboard
authority and recovery drafts. Connect installed controller/catalog/policy ownership
and scene-aligned entry/restoration with independent escape. Full accessibility,
performance, other adapters, historical laboratories and all five complete editions
remain open. Owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior,
historical Windows runtimes or physical power loss.
''')
