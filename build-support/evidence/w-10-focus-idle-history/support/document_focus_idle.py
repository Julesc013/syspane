from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();now=datetime.now(timezone.utc).isoformat()
index=json.loads((r/'build-support/evidence/w-10-focus-idle-attempts.json').read_bytes())
assert sum(v['cases'] for v in index['final_native'].values())==168
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
write('spec/delivery/focus-idle-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native editor refresh fairness checkpoint"
description: "Observed GTK/ATK focus starvation, scoped style transitions and unchanged native acceptance."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-FOCUS-IDLE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-FOCUS-IDLE", "SP-EDIT-LOCKS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor refresh fairness checkpoint

Source baseline: `9c1757de6a8227b2a4235f8be7b727a9d3f55d7d`. The
[package](packages/w-10-focus-idle.md), original implementation/oracles and new
regression inputs were frozen before production edits. All original scene,
history, pixel, storage, recovery, focus and erasure expectations remain unchanged.

## Cause and implementation

Paired native diagnostics distinguish GTK keyboard focus from exported ATK focus.
With 60 ms of bounded drawing work, the old 40 ms default-priority refresh left
GTK focused while ATK stayed unfocused and normal-idle work waited 4.85/5.17 seconds.
Changing only refresh priority let both paired runs pass the original keyboard,
scene, pixel and persistence oracle. Unloaded controls passed. This establishes a
scheduling defect under load; it does not assign every older unexplained failure
to that cause. GTK documents [main-loop priorities](https://docs.gtk.org/glib/main-loop.html)
and [normal-idle callbacks](https://docs.gtk.org/gdk3/func.threads_add_idle.html).

The editor now uses G_PRIORITY_LOW for its optional periodic refresh. Input and
policy callbacks retain their existing priority/semantics. An unavailable draft
queues its clearing paint and no longer requests periodic empty redraws; image-job
reaping continues. Native widget style transitions apply immediately within this
editor using a scoped CSS provider. Theme values and global animation preferences
are unchanged. Provider references follow the widget style-context lifetime.

The latter change follows a separate preserved failure: after the focus fix,
loaded revocation cleared the fields but failed the original 200 ms complete
observation deadline. Suppressing empty timer redraws alone did not repair it.
Paired private-process diagnostics failed twice with animations enabled and passed
twice with animations disabled (138/121 ms). The scoped production change then
passed loaded revocation in 129 ms with the same paint load and original oracle.
No deadline, focus requirement, expected scene or required erased surface changed.

## Executed evidence

All 311 Linux non-native checks pass. Eleven existing native editor matrices pass
165 cases, including the previously failing 24-case large-command matrix and seven
lock cases. The binding-authoring matrix fails while querying a tab role through
libatspi (`timeout from dbind` in the selector case). Its cause remains unresolved;
the complete 180-case existing editor regression has not passed. No unchanged
rerun is substituted for explaining that failure. The new three-case refresh matrix passes loaded editing, loaded
revocation and an explicit old-priority fault control: actual GTK focus persists
while ATK focus starves, the original deadline fails, and no mutation is submitted.
The 168 cases in passing matrices retain keyboard activation, exact scenes and independent
pixel/storage/recovery checks. The probe is a Linux-only laboratory module with
no installed files; ordinary product execution has no injected delays.

Thirteen of fifteen additional native rendering checks pass, including text
rasterization, image decode/worker lifetime, disclosure erasure and settings.
The inspector's translated case fails a libatspi selected-row query with
`timeout from dbind`. The scene-image check fails its existing nonblocking-paint
timing assertion (`scene paint waited for decoder`). Both failures and full logs
are retained; their causes are unresolved. The Linux environment received external FreeType/librsvg package updates
during the campaign. Initial configure rejections are preserved. Read-only vendor
package verification supported recording the exact installed revisions and library
hashes in the existing text/image development profiles; this work installed no
packages. Fonts, other dependency pins and rendering expectations are unchanged.
The original/current manifests, package checks and vendor changelogs are retained.
These pins record the development environment, not completed rendering qualification.

Both Windows profiles configure and pass their two composition checks. The Linux
form and probe are absent from their graphs, and every recorded Windows executable
is byte-identical to the previous checkpoint. Windows product suites were not rerun
for this Linux-only production change; the previous results remain historical.

The new auxiliary 50 ms focus sampler initially missed a brief focused state that
the original native oracle successfully observed before Undo disabled itself.
Its recorded correction captures the actual ATK query with simultaneous GTK focus.
Original failure, original/corrected probe and oracle, unchanged fixture and
unchanged production identity for that correction are retained. This is distinct
from the genuine focus and erasure failures described above.

Records: `build-support/evidence/w-10-focus-idle-attempts.json`,
`w-10-focus-idle-native-index.json`, `w-10-focus-idle-verification.json`,
`w-10-focus-idle-staging.json` and `build-support/evidence/focus-idle-handoff.json`.
Source archives, CTest logs, diagnostic arms, failures, executable identities,
fixed inputs and support scripts remain independently inspectable. The workspace
bound is unchanged; cleanup removed only duplicates verified against committed
archives. Both the initial budget refusal and the later rendering overrun are
preserved. The rendering run's native output grew about 340 MB, exceeding the
ordinary 64 MiB reservation and combined allocation. Further build/test work
stopped for verified duplicate cleanup. Future admission of that matrix must reserve
its measured growth in addition to the normal check. One animation diagnostic
launch also preceded collection of its pending preflight result, which eventually
passed; that ordering mistake is recorded separately.

## Remaining boundary

This checkpoint is not fully qualified. Investigate the preserved binding tab-role
timeout with explicit native object/address/reply evidence, preserving the failed
record and all original acceptance conditions. Also investigate the inspector
selected-row timeout and scene-image nonblocking timing failure; no attribution to
the changed runtime or editor is established. W-10 and all five complete editions
remain in progress. Continue conditional
visibility/typography, clipboard authority, recovery drafts, installed controller/
catalog/policy ownership and scene-aligned entry/restoration with independent escape.
Earlier unrelated interface/focus causes, broad accessibility/performance,
historical laboratories, other adapters and all release gates remain open. Owned
Xvfb/D-Bus evidence does not qualify the installed desktop or a complete edition.
''')
p=r/'README.md';s=p.read_text();marker='The [edit-lock checkpoint]';pos=s.index(marker)
s=s[:pos]+'''The [refresh-fairness checkpoint](spec/delivery/focus-idle-handoff.md) fixes
GTK accessibility-focus starvation under sustained preview drawing. Scoped editor
style transitions also preserve prompt policy erasure. Passing matrices cover 165
existing cases and three new load/fault cases, including the prior large-scene
regression. A binding-tab accessibility timeout keeps the full regression open.
Installed integration and complete editions remain in progress.

'''+s[pos:]
s=s.replace('Intermittent Apply/Undo keyboard-focus failures remain under investigation. Installed\nintegration, remaining authoring and all complete editions remain open.','Its large-scene focus regression now has the refresh-fairness checkpoint above.\nInstalled integration, remaining authoring and all complete editions remain open.')
write('README.md',s)
p=r/'TODO.md';s=p.read_text();s=s.replace('- [ ] W-10 persistent edit locks: implementation and seven native lock cases pass; qualification remains open because the large-scene regression failed on Apply/Undo keyboard focus. See the [handoff](spec/delivery/edit-locks-handoff.md).','- [ ] W-10 persistent edit locks: seven native lock cases and the previously failing large-command matrix pass after the refresh fix; a binding-tab accessibility timeout keeps full regression qualification open. See the [lock record](spec/delivery/edit-locks-handoff.md) and [new evidence](spec/delivery/focus-idle-handoff.md).')
s=s.replace('- [ ] W-10 keyboard-focus regression: preserve and explain the repeated large-scene Apply/Undo focus failures before claiming reliable native interaction; successful diagnostic runs alone do not close them.','- [x] W-10 refresh-induced focus starvation: paired GTK/ATK/idle traces isolate the scheduling defect; loaded editing/erasure and the old-priority fault control pass unchanged acceptance. See the [handoff](spec/delivery/focus-idle-handoff.md). Earlier unrelated interface/focus causes remain open.')
write('TODO.md',s)
p=r/'spec/delivery/current-state.md';s=p.read_text();s=s.replace('updated: {"by": "codex", "at": "2026-10-07T12:48:21.342320+00:00", "scope": "Persistent editor lock checkpoint and remaining editor/release boundaries"}',f'updated: {{"by": "codex", "at": "{now}", "scope": "Refresh-fairness repair and preserved binding observation failure"}}');start=s.index('The latest [edit-lock checkpoint]');end=s.index('The earlier [container checkpoint]',start)
s=s[:start]+'''The latest [refresh-fairness checkpoint](focus-idle-handoff.md) identifies and
repairs GTK/ATK focus starvation caused by continuous higher-priority preview
refresh. Scoped editor style transitions preserve prompt erasure under the same
load. Passing matrices cover 165 existing editor cases and three load/fault cases;
311 non-native Linux checks and 13 of 15 rendering checks also pass. The large-command
matrix passes, but binding authoring fails at a libatspi tab-role query. Investigate
that preserved timeout, the inspector selected-row timeout and scene-image timing
failure next; this checkpoint is not fully qualified. Earlier
unrelated interface/focus causes remain open. Then continue conditional
visibility/typography, clipboard/recovery drafts and installed ownership, then
full accessibility/performance and all five complete-edition release tracks.

The earlier [edit-lock checkpoint](edit-locks-handoff.md) adds persistent locks
through scene 0.4, negotiated command 0.6 and the existing resource/transaction
owners. Its original failed focus regressions remain preserved; the new checkpoint
above records the repaired behavior without rewriting historical outcomes.

'''+s[end:];write('spec/delivery/current-state.md',s)
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());units=v['work_units'] if 'work_units' in v else v['units'];row=next(x for x in units if x['id']=='W-10')
row['package']='delivery/packages/w-10-focus-idle.md';row['evidence']='delivery/focus-idle-handoff.md';row['notes']+=' The refresh-fairness checkpoint isolates GTK/ATK focus starvation under bounded paint load. Low-priority optional refresh and scoped immediate style changes pass three loaded/fault cases, including 200 ms erasure, plus 165 existing cases across eleven matrices. The large-command matrix passes, but the binding-authoring matrix fails at a libatspi tab-role query. Thirteen of fifteen rendering checks pass against reviewed updated Linux dependency identities; inspector selected-row observation and scene-image nonblocking timing fail. Preserve all three failures and investigate before full qualification. Remaining authoring/installed boundaries and complete editions stay open.'
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
p=r/'docs/developers/build.md';write('docs/developers/build.md',p.read_text()+'''

### Native editor refresh fairness

The editor refresh timer runs below normal-idle GTK accessibility work. Immediate
widget style transitions are scoped to the editor; global animation settings are
unchanged. After the usual workspace preflight/configure/build, run
`ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-REFRESH$" --output-on-failure`.
The owned non-root Xvfb/D-Bus test injects 60 ms paint work, reuses the original
large-scene keyboard/pixel/storage/erasure oracle, and positively detects the old
timer priority as a fault. Do not preload its module into an ordinary session.

The [handoff](../../spec/delivery/focus-idle-handoff.md) retains the original failures,
the auxiliary observation correction, paired animation experiment and exact runtime
admissions. Changed text/image runtime identities require configure verification
and existing native rendering/decode checks with unchanged expected outputs.
''')
p=r/'.gitattributes';write('.gitattributes',p.read_text()+'\n# Preserve exact focus/refresh diagnostics, attempts and admission records.\nbuild-support/evidence/w-10-focus-idle-history/** -text whitespace=cr-at-eol\n')
print('Updated status, handoff, work-unit links and developer guidance.')
