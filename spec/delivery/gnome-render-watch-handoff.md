---
type: "SysPane Implementation Handoff"
title: "Independent supervision of operational GNOME drawing"
description: "Native render deadlines, independent pixels, actual exits and preserved boundary failures."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T10:26:00Z"}
sp_id: "SP-GNOME-RENDER-WATCH-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GNOME-RENDER-WATCH", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent supervision of operational GNOME drawing

From `6e687f1a09277213801071185d601c3461322af0`, the existing RecoveryProbe now
supervises actual measured drawing in the owned GNOME laboratory. The
[package](packages/w-25-gnome-render-watch.md) fixes the health protocol, mutable
owners, deadlines, resource limits and independent acceptance conditions.

The shared HealthLink exposes bounded asynchronous input/output without a second
protocol parser. A native `HealthView` supplies that parser and authenticated peer
lifetime to GJS. `RenderSession` shares the existing asynchronous source-session
owner. Drawing stages an exact native challenge; subsequent stage after-paint
instrumentation completes it. A separate process owns the render deadline and
public health journal. Independent glyph pixels remain the visibility/content
oracle. The native view also expires a silent watcher.

## Executed boundaries

| Case | Required and observed outcome |
|---|---|
| live | Original measured values, advancing age and native paint completions; graceful clearing and all native exits |
| render-stall | Frozen pixels with living source/health; independent three-second render fault, then clearing |
| false-progress | Injected acknowledgements continue while pixels freeze; candidate fails independent age acceptance |
| hidden | No visible tile and no eligible completion; unrelated stage paint cannot rescue its render deadline |
| revoke | Typed denial erases actors and removes callbacks before acknowledged teardown |
| watch-exit | Held watcher death clears the tile and releases the collector |
| watch-hang | Native client lease expires a stopped watcher; clearing precedes confirmed forced child exit |
| shell-freeze | Independent native fault while shell pixels survive; confirmed resume precedes clearing and actual descendant exits |

The standalone `RENDER-DEADLINE` experiment additionally queues late progress,
heartbeat and shutdown while only its owned watcher is stopped. Each must retain
the original deadline fault and failed exit after resume. The stopped interval is
not presented as runnable scheduling latency.

The complete native suites pass 113 Linux and 105 Windows CTest entries, including
three new shared-health families. Both local model smoke packages pass relocation.
Two affected historical-toolset component checks pass; the earlier full historical
suite and smoke keep their original identity. Thirty-five adversarial render
evidence checks reject missing drawing/paint, false completion, erased/rebased
faults, missing process exits, retained pixels and forged success.

Public evidence uses `build-support/evidence/w-25-gnome-render-watch-*`;
`render-calibration.json` verifies the eight current native reports, and
`compiled-attempts.json` preserves builds, full suites and smoke invocations.
The attempt index retains earlier sources and failed outcomes. Operational
source journals and glyph crops remain mode 0600 inside private native attempt
directories. Public records contain their paths, sizes and hashes, never their
contents. The separate watcher journal contains lifecycle facts only.

## Preserved findings

The first stopped-shell oracle assumed the collector would exit normally. The
existing consumer lease can expire while the shell stops renewing it; the worker
then exits normally and the supervisor records source loss. Health EOF, data EOF,
observed child exit and peer-clock loss have no guaranteed cross-channel delivery
order. The original normal-only and health-EOF-only failures remain preserved.
The amended case requires the actual worker exit, supervisor failure and original
channel reason. No lease is extended and no source failure is called success.

That experiment also exposed a lifecycle reporting bug: a sibling could initiate
closure before a nonzero child exit was delivered. The owner now retains that
failure after waiting, even when shutdown was already underway.

The first queued-message experiment failed all three cases. Late progress and
heartbeat exited without the required latched deadline journal; queued shutdown
could incorrectly finish normally. Native guards now advance before dispatching
each admitted event and on idle turns. The same three deadline expectations pass
against the corrected binary. Original reports, sources and artifact identities
remain available alongside the corrected evidence.

## Remaining work

W-25 and the campaign remain incomplete. Close bounded automatic renderer
replacement only after confirmed old exit, require a current-policy full snapshot
for reattachment, and independently prove visible recovery. Complete native editor
exit, product controller/demand/policy, general delivery queues and installed policy
qualification. Native settings, direct editing, persistence and real telemetry
remain required for the first complete desktop edition.

The named GNOME laboratory does not qualify other desktops, suspend/namespace
migration or an installed production service. The default Show Desktop focus
failure remains open and optional integration stays disabled by default. Windows
synthetic-lab designation is pending; historical guest scope and an admitted Mac
endpoint remain unresolved. No active user desktop, guest, privileged operation,
release publication or AIDE activation is authorized by this checkpoint.
