---
type: "SysPane Handoff"
title: "Asynchronous editor recovery preparation"
description: "Validate detached recovery work on the existing native worker and consume only current opaque results."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T02:26:59.812423+00:00"}
sp_id: "SP-RECOVERY-PREPARATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-RECOVERY-PREPARATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Asynchronous editor recovery preparation

EditorDraft now creates detached capture/restore work with authored documents,
immutable shared resources, current policy and trusted profile/generation identity.
It excludes selection, undo/redo, clipboard, private input and request state. The
existing semantic/resource checks execute on that value. An opaque result carries
a weak validity token: every authored, policy, request, connection, baseline or
lifetime mutation invalidates it, including rejected/no-op attempts. A copy cannot
consume its origin's proof. Selection alone may change before one atomic Restore;
Undo restores the selection that was current at consumption.

The existing Linux editor helper owner has one preparation slot. It acquires work
and computes outside its shared mutex, then publishes only if cancellation has not
won. GUI handles erase queued inputs/results on cancel, while acquired computation
retains its slot until acknowledged. No additional native worker, thread pool,
history or request scheduler was introduced. Immutable package/media allocations
remain shared and all original record, command, scene and history bounds remain.

EditorRecoverySession optionally accepts the helper client's preparation factory.
Initial inspection keeps editing blocked until it can offer Restore or only
Discard/Keep. Capture coalesces into one active and one latest pending input; Apply
waits for preparation and durable storage. Prepared restoration rechecks current
permission, identity and token, then enters the existing history without semantic
reconstruction on GTK. Legacy explicit synchronous consumers retain their APIs.
Keep, discard, cancellation, invalidation and close remove proofs and suppress late
results. EditorForm forwards this factory without enabling installed recovery.
An explicit closed-owner witness first reproduced an offer surviving inspection
cancellation. Polling now withdraws offers when the queue becomes unavailable,
closing or closed. Restore checks that status itself before touching the draft,
so a click before the next poll cannot consume a withdrawn offer. Both initial
inspection and already prepared offers have native regression cases.

The [frozen package](packages/w-11-recovery-preparation.md), literal fixtures and
[checkpoint](checkpoints/recovery-preparation.json) bind commands, source archives,
artifacts and actual outcomes. The eight new portable families cover exact bytes,
scene/theme resources, no-op/history behavior, invalid input, policy, mutation
boundaries, cross-draft identity and origin lifetime. Eight native case groups exercise
held computation, exact offers/captures, acquired-work cancellation, erasure,
coalescing, malformed/stale offers and wrong-oracle calibration.

The final native preparation run observes 15 hosts and
21 sealed helper children, all exited without forced
fixture cleanup. Its 1635 measured GUI calls take at most
861 microseconds under the unchanged 100 ms
development bound. These fixed consumer fixtures do not qualify maximum-size
inputs or scheduling of the complete installed supervisor/client/helper loop.

The checkpoint records 239 selected portable checks per development profile,
including all eight new families and two component-graph checks on each profile
(six graph checks in total). Its
13 native report families contain 344
named cases; IMAGE-JOB and SCENE-IMAGE also pass their C++ CTest checks. This covers
the existing helper/admission, queue/storage, recovery controls, editor form and
installed settings/editor regressions. Windows host execution with v141_xp does
not qualify an XP guest, Windows 9x or another historical target.

The first Linux build exposed misleading test indentation; the first v141_xp build
exposed an implicit integer-to-character token initializer. Both failures remain
preserved; the final source fixes the warnings without lowering compiler checks.
Windows GCC15's existing THEME-HISTORY-RESOURCE-LIMIT check hit its unchanged
20-second deadline. An isolated unchanged rerun passed in 18.52 seconds, and prior
committed build-layout evidence passed in 19.82 seconds. The cause remains unproven;
the checkpoint distinguishes whole-suite results from isolated results. No timeout,
fixture, expected output or product capacity was relaxed.

The first installed-editor regression in this checkpoint passed thirteen cases before an
AT-SPI grab_focus timeout on frontend.editor in CLOSE-HELD setup. The editor had
not opened and the held-storage stimulus had not begun. Subsequent controls still
reported Settings connected, enabled Edit scene and revision 0; application stderr
was empty. Its screenshot, exact payloads, failed result and teardown are preserved.
The unchanged replay is a separate result, not a causal explanation or an erased
failure. Keep this focus reliability question open alongside earlier native failures.

Completed owned recordings were archived, byte/node verified and checked for live
owners before duplicate removal. This includes 293
older attempts (94440585 raw bytes),
including their original failures. The 8 GiB active-output allowance and ordinary
reservations remain unchanged; all raw archives and machine bindings stay ignored.

W-11 and all five complete release editions remain open. Next compose the actual
frontend's explicit 0.2 profile download and current-session callback with native
admission and this preparation factory. Preserve exact applied-draft retirement
through accepted/lost-result reconciliation, then qualify worker/supervisor scheduling
and maximum-size GUI operations before enabling installed recovery. A storage grant
can race authority withdrawal; closure is not rollback. Protected deployment, native
inspector, telemetry, desktop activation/visibility, lifecycle and other adapters
retain their existing release gates. Keep the Windows resource-limit timing failure
visible until its cause is established, along with the installed AT-SPI focus timeout.
