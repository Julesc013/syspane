from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
 s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
change('README.md','The [layout-authoring checkpoint]', '''The [keyboard-input checkpoint](spec/delivery/keyboard-input-handoff.md) resolves
the recorded layout-button focus failure in the laboratory: navigation now awaits
each selected row before requesting another control's focus. Layout buttons again
use explicit focus and keyboard activation. Production bytes and fixed acceptance
outcomes are unchanged; earlier unrelated failures and full editions remain open.

The [layout-authoring checkpoint]''')
change('TODO.md','- [ ] W-10 recurring focus failures:', '- [x] W-10 layout-button focus investigation: paired input traces identify a transient selection match before queued navigation completed; per-key row/title acknowledgements restore keyboard button coverage. See the [handoff](spec/delivery/keyboard-input-handoff.md).\n- [ ] W-10 recurring focus failures:')
change('TODO.md','earlier intermittent failures do not yet have a proven cause.', 'the layout-navigation cause is established separately, while earlier unrelated intermittent failures remain unproven.')
change('spec/delivery/current-state.md','The latest [layout-authoring checkpoint]', '''The latest [keyboard-input checkpoint](keyboard-input-handoff.md) identifies the
layout-button focus failure as an input-ordering error in the laboratory. End
temporarily selected the expected final row before later queued navigation ran.
The oracle now awaits each selected row/title within one deadline and restores
keyboard button activation. Production bytes and all fixed outcomes remain unchanged.
Earlier unrelated interface/focus failures remain open. Continue flow/container
group transformations and remaining properties, then installed ownership and all
five complete editions; W-10 remains in progress.

The earlier [layout-authoring checkpoint]''')
p='spec/delivery/current-state.md';write(p,re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Proven layout keyboard input ordering cause and remaining native boundaries')),(r/p).read_text(),count=1,flags=re.M))
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());w=next(w for w in v['work_units'] if w['id']=='W-10');assert w['status']=='in_progress';w['specs'].append('SP-W10-KEYBOARD-INPUT');w['package']='delivery/packages/w-10-keyboard-input.md';w['evidence']='delivery/keyboard-input-handoff.md';w['notes']+=' The recorded layout-button focus failure is now traced to a transient expected selection before queued navigation finished. Per-key native row/title acknowledgement within one shared deadline restores keyboard button coverage without changing production or acceptance outcomes. Earlier unrelated focus/interface causes remain unproven. Continue flow/container group transformations, remaining properties and installed ownership.';write(p,json.dumps(v,indent=2)+'\n')
p='docs/developers/build.md';write(p,(r/p).read_text()+'''
### Native keyboard input ordering

The layout oracle acknowledges each navigation key using explicit native selected
rows and the expected title. A single three-second deadline covers the whole
selection. End can select the same row as the eventual final Down; that intermediate
match cannot prove the later queued input completed. Do not substitute an arbitrary
sleep, retry a mutation or force focus inside a held-focus assertion.

Layout-suite buttons now use explicit focus plus Space again. The original scenes,
pixel/storage outcomes, fault controls and 200-ms erasure bound remain unchanged.
After workspace test preflight, run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-LAYOUT$" --output-on-failure`.
The [handoff](../../spec/delivery/keyboard-input-handoff.md) records the paired native
experiment, all ten regression matrices and the remaining qualification scope.
''')
write('spec/delivery/keyboard-input-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native keyboard-input checkpoint"
description: "Queued navigation completion explains the recorded layout-button focus failure."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-KEYBOARD-INPUT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-KEYBOARD-INPUT", "SP-LAYOUT-AUTHORING-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native keyboard-input checkpoint

Source baseline: `{base}`. The [package](packages/w-10-keyboard-input.md)
closes the specific layout-button focus failure recorded by the preceding checkpoint.
Production source/binaries and all frozen product expectations remain unchanged.
W-10 and every complete desktop edition remain in progress.

## Causal evidence

The preserved keyboard oracle is replayed with the same native binary in the owned
unprivileged ext4/Xvfb/D-Bus laboratory. Three detailed-snapshot runs pass but are
inconclusive. Removing successful-path snapshots and replaying the original fixed/
flow prelude reproduces the canvas focus failure in all three repetitions. Explicit
queries show the editor remains the active X11 window, while its object list/Image
row retains focus. One diagnostic Space does not open Layout.

A paired experiment uses the same keys and dialog-boundary observations, retaining
the original three-second bound for each wait. The final corrected oracle instead
bounds the entire navigation sequence to three seconds.
All three batched runs fail and all three ordered runs focus and activate Layout.
The input trace shows End/Home/Down/Down/Down queued together, followed by an early
`Layout group` title read. End selected that same group before the following keys
completed. The later navigation reclaimed focus after the accessibility focus
request. Per-key row/title acknowledgement removes that ambiguity without changing
the producer or weakening the required focused state.

GTK's [3.24.41 focus-request implementation](https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtkwidgetaccessible.c)
requests widget/window focus before returning success. That return alone is not the
oracle's completion condition: the explicit focused-state check remains required.
Upstream source hashes explain the API boundary; the paired native observations
establish this failure's cause. They do not establish causes for earlier unrelated
interface lookup or focus failures.

## Correction and verification

The layout oracle reads explicit selected rows and the expected title after each
navigation key, within one three-second deadline for the entire operation. It logs
bounded expected/observed transitions. It performs no mutation retries, focus forcing
inside held checks or arbitrary settling sleep. Layout buttons again use explicit
focus plus Space. Existing showing/modal-state checks, exact scenes/pixels/storage,
negative fault controls and the 200-ms erasure bound remain fixed.

The first restored-keyboard regression run also exposed an alignment completion
race: the oracle changed selection immediately after queuing Space, before the
expected alignment appeared. Its screenshot preserves the unaligned second pane.
The correction observes the same frozen aligned caption pixels before moving focus,
then checks the original exact geometry and stored scene. This adds an observable
completion condition; it does not change the expected scene or retry the action.

All 157 native cases pass across ten matrices: layout 21, observer calibration 7,
creation 17, binding 15, content 15, snap 13, group 11, arrangement 14, editor 20 and
large-command 24. The three diagnostic matrices contain 24 separate investigative
cases, including intended failures and inconclusive passes; they are not added to
the product-pass count. Production bytes match the baseline, whose 132 affected
checks per development toolchain remain the portable evidence. No new Windows
runtime or historical qualification is claimed.

Records: `build-support/evidence/w-10-modal-focus-attempts.json`,
`w-10-modal-focus-native-index.json`, `w-10-modal-focus-verification.json`,
`w-10-modal-focus-staging.json` and `build-support/evidence/keyboard-input-handoff.json`.
They preserve every attempt, frozen package/inputs, exact diagnostic scripts,
native traces, source snapshots, executable identities and specification checks.
Twenty-one duplicate native folders were reclaimed only after verifying their
already committed layout archives. The existing output budget remains unchanged.

## Next boundary

Continue flow/container group transformations and remaining property contracts,
then installed controller/catalog/policy ownership and scene-aligned entry/restoration
with independent escape. Earlier unrelated focus/interface failures, complete
accessibility/performance, historical laboratories, other adapters and all five
complete-edition release gates remain open.
''')
