---
type: "SysPane Work Record"
title: "Native Mutter focus-decision evidence"
description: "Built-in native diagnostics bind the reproduced focus failure to desktop MRU selection."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:54:00Z"}
sp_id: "SP-GNOME-FOCUS-TRACE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-FOCUS-TRACE", "SP-GNOME-FOCUS-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native Mutter focus-decision evidence

From `4ed0861528b80fb3965474b3450a9b0ec9835a8a`, built-in Mutter diagnostics identify
the native decision behind the reproduced DING/X11 focus failure. On the second
Show Desktop action, Mutter selects the DING desktop as its workspace MRU focus
target and shows the foreground window without focusing it. GNOME without DING
selects the foreground window. The same native decision occurs with and without
the SysPane bridge. This establishes the observed mechanism in the pinned runtime;
it does not implement a fix or change the failed foreground-focus acceptance.

## Native decisions and independent observations

The [package](packages/w-05-gnome-focus-trace.md) uses the existing runner and
fixed external pixel/native-state/keyboard observations. The optional
`--focus-trace` flag enables only Mutter's built-in focus, key-binding and window
state diagnostics in the private shell environment. There is no new observer
extension, upstream patch, key-handler replacement or focus manipulation. Logs
stay in the owned workspace under the existing 1 MiB bound.

Six source-identical cases provide one traced and one untraced run per mode.
Each pair agrees on visible transitions, active-client roles, focus result,
keyboard receipt and original candidate acceptance. The prior nine-run comparison
remains separate evidence; these six cases test instrumentation effects.

| Mode | Native MRU selection on restore | External active client | F9 receipt without refocus | Traced/untraced observations |
|---|---|---|---|---|
| GNOME alone | Foreground | Foreground | Yes | Equal |
| GNOME with DING | Icon desktop | Icon desktop | No | Equal |
| GNOME with DING and candidate | Icon desktop | Icon desktop | No | Equal |

All explicit-click F10 positive controls pass. That later click is diagnostic;
it neither repairs the earlier acceptance nor supplies the native decision being
attributed. Each fixed native interval retains 48 samples. The maximum observation
duration is 4,077 us and maximum coverage gap 53,999 us, within the unchanged
50 ms / 150 ms budgets. Both candidate cases also validate the full original
composition and three-generation reveal evidence, including failed focus.

The raw traced logs contain 96,791, 117,528 and 117,537 bytes respectively. Exactly
two executed Show Desktop handler entries appear in each. Their separation agrees
with the independent action separation within 50 ms. The recorder binds the
selected hexadecimal window ID to the retained XRes/process owner, requires its
subsequent focus assignment and foreground show event, and preserves the exact
decision excerpt with original line numbers. The full log remains available.

The decision search ends at the next keyboard-handling boundary, a mouse-focus
event or 200 ms after the handler, whichever occurs first. Unknown owners,
ambiguous/missing decisions, backwards time, changed bytes or missing controls
invalidate attribution. Native wall-clock text bounds log association only;
the original monotonic observer remains the acceptance authority. A later cleanup
MRU selection cannot substitute for the restore decision.

## Verification and evidence identity

`out/evidence/w-05-gnome-focus-trace-comparison.json` contains recomputed
native observations, pair comparisons, exact source/runtime identities and
decision excerpts. Twenty-three evidence checks pass, covering handler count,
window ownership, missing/ambiguous decisions, assignment/show events, late and
backwards timestamps, click/keyboard boundaries, action separation, raw log
identity/path/completeness, trace configuration, missing/duplicate pairs and
instrumentation differences. The comparison permits a native selection to
disagree with the external result; it does not force the hypothesis to pass.

Seven native attempts, seven source archives and 22 raw journals/event files/logs
are preserved under `out/evidence/w-05-gnome-focus-trace-*`. The first
DING-only trace predates the package's explicit mouse/time association bounds;
its source archive remains separate from the final six-case matrix. Successful
completed budget preflights precede the native executions and verifier checks.
Owned processes and their retained groups exit without surviving members.

The runner's default path remains untraced. No C++ implementation, target profile,
runtime package lock, workspace allocation, user desktop, shell, VM or public
release changed. Existing CTest/smoke results retain their original identities;
they were not rerun or claimed as new evidence in this checkpoint.

## Next boundary

The pinned native MRU-selection mechanism is now observed, so the next focus work
is an integration decision with a bounded contract and independent acceptance.
Determine whether a supported native integration can preserve normal foreground
focus without taking focus from user actions or replacing upstream semantics.
Keep the original failure while investigating; do not add a periodic focus repair
or silently redefine the expected result. Any proposed oracle correction must
remain a separately reviewed contract change with the original failure preserved.

Taskbar/task-switcher behavior, native icon input, image wallpaper, shell/icon-manager
recovery, real system services, GPU presentation, Wayland and the product vertical
remain unqualified. Continue independent native tracks and deterministic product
work under their existing gates. W-02, W-05 and the full campaign remain open.
