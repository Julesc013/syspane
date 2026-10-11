---
type: "SysPane Work Package Boundary"
title: "GTK text-cell cache lifetime ownership"
description: "Clear cached disclosure before collapse/removal retires a cell; preserve standard lifecycle events."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T22:50:00+00:00"}
sp_id: "SP-W11-GTK-CELL-LIFETIME"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-GTK-HISTORY-LIMITS", "SP-ACCESSIBILITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# GTK text-cell cache lifetime ownership

Continue W-11 from 1e7f324f. The preceding standalone experiment leaves collapsed
and retired local text/name/layout readable under stock cells. Its expanded scrub
also fails timing; all strict external empty-response cases remain failed.
Preserve those checkpoints, collectors, errors and original performance oracles.

## Fixed boundary

Introduce an internal Linux text renderer and accessible subtype using public GTK
class-init and widget-unset hooks. GTK owns each cell's lifetime and calls its
unset hook when collapse, removal, model replacement or destruction retires it.
There is no application registry, copied row cache, global scene pointer or worker
access. Existing GTK/SceneInspector thread ownership and all resource limits apply.

Before forwarding the inherited widget-unset operation, acquire the cell's shared
renderer, save its text, temporarily set empty text, and invoke the inherited
public text-cache update slot with emit_signal false. Restore the shared renderer's
exact prior text, including null, and release temporary references/strings. This
erases the retired cell's text/count/name-derived value and cached word/layout
content while preserving other active cells. Forward the normal inherited unset
hook exactly once; retain native defunct/model/visible-data events. Do not block
signals, touch private toolkit fields, alter the accessibility tree, recreate the
root or detach as a performance substitute. Cells use derived names; product code
does not install explicit per-cell names. Verify that invariant and held names.

The helper owns no additional per-row storage. Place its internal declaration and
implementation in source/interfaces/scene_inspector_text_linux.hpp/.cpp, with one
declared scene-inspector component source and ordinary GTK dependency. First use
it only in a native lifetime probe; integrate both real inspector columns after
the semantic gate succeeds. The integration changes no row values, keys, policy,
source, history, selection, interface version or renderer cadence.

## Evidence and acceptance

Reuse the preceding exact 3172-row, 6344-cell canaries and fresh rows in a new
lifetime mode. Hold every original cell; compare the 66 retired-root cells after
retirement, all 6276 chart children after collapse, every cell after erase and
again after fresh regrant. All retired native text/name/count/word values must be
empty. The expanded live chart remains exact; the collapsed chart root remains
exact. This proves shared-renderer restoration instead of merely erasing all data.

Keep the original strict empty-response experiment unchanged and unqualified.
The separate lifecycle test recognizes two distinct wire outcomes: a successful
empty reply, or verified withdrawal of the exact previously supported object.
Withdrawal requires the precise UnknownObject error for the retained bus/path,
the same live application/root, exact fresh rows and normal exit. Timeout, service
loss, generic errors, missing initial support or rebound old paths fail. Never
map errors to empty text or use an SDK default as a successful reply. The literal
oracle is settled from lifecycle meaning, not regenerated from candidate output.

Run native.GTK-CELL-LIFETIME as two fresh expanded/collapsed children, each bounded
by the existing 120 seconds, family 250 seconds. Keep the same input/output/observer
caps and lossless wire journals. Record all callback/mutation times and failures.
This semantic gate does not qualify GUI performance; no 100-ms GUI/200-ms erasure
limit, timing sample or original case is changed or excluded. A collapsed/removed
cell is allowed to be withdrawn, not required to remain a live object forever.

Before product integration, pass the lifetime oracle and component graph checks.
After integration, run the same lifetime probe plus real SceneInspector/model,
renderer/background, receiver/frame-boundary and held-erasure regressions. Record
source-bound artifacts and declared installed smoke/harness identities if changed.
Preserve every preceding failure and blocked qualification. General GTK history
update/erase performance, maximum-policy cases, installed/human/desktop integration
and all five complete release editions remain required.

Add native.INSPECTOR-CELL-LIFETIME in the existing inspector test executable,
with a private Xvfb and 25-second bound. Feed three actual complete chart packets
at generations 1..3 and measurement 0/1/2 ms, values 10/11/12, through the public
receiver/delivery boundary. Inspect both real column renderers and all eight text
objects. Collapse the root: six held child objects become empty/defunct while
the root remains current. Deny inspector at revision 8: all eight old objects
become empty. Regrant 9 with scope (11,5), value 99/generation 4/3 ms: one fresh
start point, no old cache value. Close and destroy the real widget while holding
old/fresh text objects, then check every full/name/count/word getter. Each native
cell receives exactly one ordinary defunct transition; no signal is suppressed.
This small real-component test complements the complete standalone lifetime
cohorts; it does not replace maximum/history/policy/installed performance tests.

Preserve the first real-inspector fixture failure: it incorrectly required an
allocated empty value from the optional modern native word slot. The pinned GTK
text cell does not implement that slot; ATK documents null and offsets -1/-1 when
no implementation exists. Verify that absence before retirement, record it as
unsupported and require the same explicit result afterward. Do not count it as a
successful empty-data read. Full text/count/name and all three implemented legacy
word/layout slots remain mandatory empty after retirement. Wire GetStringAtOffset
is checked separately with its real reply/error; native absence is not a wire pass.
Primary definitions: GTK 3.24.41 gtktextcellaccessible.c and AT-SPI 2.52.0
atk/atktext.c, with the original failed fixture/source retained for review.

## Avoid redundant cache recreation

The integrated baseline passes both lifetime cohorts and real-widget erasure,
but the unchanged live-table POLICY case records 106937 us of GUI work against
100000 us; retain its source and complete report. Its erasure observation is
169.490 ms against 200 ms. This is a failure, not evidence of its cause.

Before acquiring/mutating the renderer, test whether the existing native cache is
already empty using public ATK reads: non-null empty derived name, zero character
count, allocated empty full text and allocated empty values from all three
implemented legacy word/layout getters at offset zero. Require every condition.
If the name is null, do not query potentially uninitialized layout getters;
perform the original refresh. A missing getter, null read or nonempty value also
requires refresh. Free every temporary string. No cache pointer, copied row state
or application registry is introduced. Always forward the inherited widget-unset
hook once, including when refresh is unnecessary.

The pinned public cache-update slot recreates a Pango layout even when cached
text is already empty. This guard avoids that redundant work after normal live
model blanking while still refreshing collapsed/retired values. Verify both
paths with the existing complete lifetime cohorts and actual widget test; rerun
the original table, erasure, history/renderer and installed suites. Preserve the
baseline failure even if the new candidate passes. Do not infer a general timing
qualification or proven causal attribution from a later passing run.
Primary source: https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtktextcellaccessible.c
