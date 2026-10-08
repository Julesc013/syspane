---
type: "SysPane Implementation Handoff"
title: "Live measured collector and asynchronous GJS session checkpoint"
description: "Original real telemetry, native clock provenance and independent lifecycle evidence before operational shell pixels."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:51:45Z"}
sp_id: "SP-LIVE-NETWORK-SESSION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-LIVE-NETWORK-SESSION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Live measured collector and asynchronous GJS session checkpoint

From `66e1d664488d4e31748cba826843604d1b3d4e26`, the existing CollectorProbe can
forward original measured telemetry to an asynchronous GJS owner while its native
worker remains alive. This closes the standalone delivery prerequisite to visible
operational age. No shell drawing or pixel qualification is included in this result.

The [package](packages/w-25-live-network-session.md) fixes native ownership,
forwarding, message/resource bounds, policy, shutdown and independent acceptance.
`networkSession.js` owns asynchronous startup, bounded reads/writes, native
NetworkView, heartbeat/projection timers and explicit teardown. The same owner is
intended for the next owned GNOME experiment; no second JavaScript freshness or
network model was introduced. Native subscribe/heartbeat constructors reuse the
bound telemetry 0.2 messages.

The GJS process directly launches the existing native supervisor in its session.
The supervisor admits only that native parent, launches one held worker and checks
both source/destination native clocks before forwarding original frames unchanged.
Each new experimental session uses a new owner and source lifetime; reconnect and
automatic restart are not added. The worker acquires two real network samples,
then deliberately pauses acquisition while retaining its demand/watch. This exposes
the difference between current producer health and an aging measurement.

## Executed results

The five cases run in standalone GJS without a display or user bus:

| Case | Independently checked result |
|---|---|
| `live` | Original counters/rates and metadata arrive; sample age advances to stale while producer/data heartbeats keep its lease active; shutdown is graceful |
| `lease-loss` | Dropped data-heartbeat responses expire the consumer lease while the native worker/health path remain active; shutdown is graceful |
| `hang` | The worker stalls after the second sample; the independent supervisor expires its health lease, terminates the held worker and confirms actual exit |
| `revoke` | Native policy revision 8 erases the model and JS sink before acknowledgement; no subsequent projection appears; source shutdown is graceful |
| `parent-loss` | Actual GJS termination causes both native descendants to exit under the existing parent-death guards; independent pidfds confirm all exits |

The observer brackets counters with independent native reads and times with
BOOTTIME, derives rates from the original counter/time pairs, and checks exact
projected text, original timestamps, intervals and status axes. It observes the
held network watch and the shared time namespace. Producer journals preserve exact
original payloads. All operational journals/transcripts remain private; public
records contain lifecycle facts, source identities and artifact hashes.

The complete **110-entry Linux CTest suite passes**, including both preceding GJS
families and all eight original native collector scenarios. The Linux model smoke
package passes relocated execution. Windows and historical-toolset native targets
did not change; their two component checks pass on each profile. Their prior full
102/94-entry suites and smoke archives retain the preceding checkpoint's identities
and were not rerun or represented as new full-suite evidence.

## Evidence and preserved failure

Evidence uses `out/evidence/w-25-live-network-session-`; the machine
handoff is `out/evidence/live-network-session-handoff.json`. Six original
configure/build/test attempts, three native session reports and eleven public case
records preserve the failed and passing runs with source archives. Raw operational
files remain in their owned mode-0700 directories, with mode-0600 files; committed
records identify them by path, size and hash without copying their contents.

The first live run failed. The new supervisor sampled `now` before polling health,
then advanced its lease with that older time after accepting a later heartbeat.
The lease correctly rejected the regression; the wrapper reported producer expiry
and shut down. Sampling the advance time after processing health fixes the ordering
without changing any acceptance rule. The original failing sources, native report
and private transcript remain preserved. That first harness did not retain GJS
stderr on its failing path; the corrected harness captures it on every exit path.
Two subsequent complete five-case native runs pass, with the final run adding
explicit watch, namespace and complete metadata assertions.

The ordinary recorder verifies all required cases, source/library/typelib/runtime
identities, held process exits and private artifact hashes. Workspace preflights,
Windows component results and the relocated Linux package are recorded separately.
This remains typed development policy, not protected policy deployment. Blocking
local filesystem calls, suspend/namespace changes and complete renderer recovery
are not qualified by these finite sessions.

## Next boundary

Use `networkSession.js` inside the existing owned GNOME composition. Refresh the
exact pinned collector/library evidence binding to this checkpoint before launch;
the old clock/cache records must keep their original artifact identities. Render
the actual measured values and age/status from NetworkView, then independently
decode the pixels. Preserve frozen-age, ignored-expiry and wrong-value controls,
policy erasure, data-lease loss, native exit and teardown acceptance. The previous
public-clock and retained-cache oracles remain intact.

Keep the [campaign coverage audit](campaign-coverage.md) visible. Windows synthetic
lab designation, XP/7 guest scope and a macOS endpoint remain unresolved. No guest,
active user desktop, installed service, privileged operation or release was changed.
W-25 and the full campaign remain incomplete; product demand/current policy,
general queues, renderer supervision and visible/editor recovery remain required.
