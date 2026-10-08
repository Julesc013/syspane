---
type: "SysPane Work Record"
title: "GNOME native focus lifetimes and workspace checkpoint"
description: "Selected normal/modal focus, closed targets and workspace invalidation have independent native evidence."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:39:45Z"}
sp_id: "SP-GNOME-FOCUS-SCENARIOS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-FOCUS-SCENARIOS", "SP-GNOME-FOCUS-INTEGRATION-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# GNOME native focus lifetimes and workspace checkpoint

From `0caf49403b98728a3ad4b041430a45d3e64c781d`, the existing optional GNOME X11
controller passes 24 native steps covering two normal windows in one retained GTK
helper, its modal transient, a closed target and workspace changes. The original
separate foreground control remains present. The controller implementation and
original acceptance oracles did not change; general enablement remains pending.

## Actual native results

The [package](packages/w-05-gnome-focus-scenarios.md) closes stimuli, observable
outcomes, native ownership, timing, resource limits and interrupted evidence.

| Required result | Restore candidate | Observe control |
|---|---|---|
| Original focus deadline and F9 | Pass | Fail |
| Restore selected beta and receive F9 | Pass | Fail |
| Restore selected alpha and receive F9 | Pass | Fail |
| Restore modal dialog and receive F9 there | Pass | Fail |
| Close beta during desktop mode; discard its target | Pass | Pass |
| Switch workspaces; invalidate old pending restoration | Pass | Pass |
| Fresh alpha selection restores and receives F9 | Pass | Fail |
| Original changing-marker oracle afterward | Pass | Pass |

The candidate retains beta's normal-window lifetime and calls its existing public
focus method. Native Mutter redirection delivers focus and F9 to the actual modal
dialog. Native dialog type, modal state, transient parent, XRes ownership, root
pixels and role-specific key receipt establish the result; focusing the parent
behind its modal cannot pass. No broader eligibility rule or private focus command
was added.

Closing beta generates actual native unmanaging, removes its window and clears the
pending target. The subsequent native restore has no retained target to restore.
Two private static workspaces use configured Ctrl+Alt+1/2 chords. Leaving and
returning clear pending restoration; the other workspace cannot focus a normal
fixture still assigned to the original workspace. A declared single native chord
leaves desktop mode on return, then explicit alpha selection establishes a fresh
entry that restores correctly. No retry or repair loop supplies acceptance.

All steps keep independent marker/background pixels and native client observations
on the existing 50 ms cadence, 50 ms capture, 150 ms gap and 200 ms transition
budgets. Each 400 ms step has at least three settled samples. Final source-identical
runs preserve actual transient BadWindow errors when modal/beta close during a
property query. Those exact owned GetProperty errors have unavailable native state
only before the transition deadline; their pixels remain recorded. Foreign,
unexpected or settled errors cannot pass. No failed frame is retried away.

## Harness corrections and failure preservation

The first helper attempt loaded GDK 4 before GTK 3 and failed before creating its
windows. It also exposed an outer-report defect: an exception after a passed
substep could leave `outcome: pass` alongside an error. The original report remains
preserved and is not accepted as successful evidence. The helper now explicitly
pins GDK 3, and any outer exception sets the attempt to fail.

The next attempt passed selected normal/modal focus and actual F9 but hit an
unhandled native BadWindow race while the modal was being destroyed. Its complete
previous step prefix and helper receipts remain preserved. The bounded observer
now records this native race instead of allowing Xlib to terminate it. A subsequent
complete prototype remains separate from the final matrix, which flushes each
individual sample immediately to its journal.

The intentional `helper-exit` control completes the original baseline and then
exits the newly retained helper with code 7 before window creation. Its native
command returns 1, the outer attempt records fail, and scenario completion remains
unexecuted. This proves an earlier passed substep no longer masks startup failure.

Forty-five verifier tests pass. They reject wrong selected/modal targets, foreign
PID/resource/group/type bindings, false transient relationships, dead-target or
cross-workspace focus, changed stimuli/settings, missing/late captures, wrong
pixels, consistently rewritten key attribution, absent invalidation, unsolicited
restoration and incomplete cleanup. A positive bounded-race test also verifies
that preserving an early exact-owned BadWindow is allowed while foreign or late
errors are rejected.

The original optional integration and default reveal/composition/marker regressions
add 44 and 46 checks respectively, for **135 desktop verifier checks passed**.
Their original positive/negative outcomes
remain unchanged, including the failed default focus restoration. The final
comparison is `out/evidence/w-05-gnome-focus-scenarios-calibration.json`;
the same prefix preserves 13 current-base attempts, their exact source archives,
54 raw journals and invocation/verification records. Owned process groups have no surviving
members after cleanup.

No native package lock, C++ component, supported profile or workspace allocation
changed. Existing CTest/smoke evidence retains its own source identity. The developer
guide now correctly states the already-admitted 3 GiB output allocation. The Windows
track still has no admitted interactive synthetic desktop; a noninteractive window
station cannot supply its display/input evidence. No Windows desktop was captured
or changed.

## Next admitted boundary

Continue moved-window, broader application/modal, lock/session and alternate
reveal-trigger contracts and native evidence before general enablement. Keep the
controller disabled by default and preserve the original failed default result.
Wallpaper policy, actual session-manager supervision, product continuity and other
native tracks remain independent work. This named GNOME/DING X11 experiment does
not qualify other runtimes, Wayland, physical GPU presentation or a complete host.
W-02, W-05 and the full campaign remain open.
