---
type: "SysPane Work Record"
title: "Native editor refresh fairness checkpoint"
description: "Observed GTK/ATK focus starvation, scoped style transitions and unchanged native acceptance."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T22:02:10.361592+00:00"}
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
