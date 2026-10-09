---
type: "SysPane Handoff"
title: "Inspector telemetry receiver and bounded delivery"
description: "Native consumer evidence and the remaining ordinary-inspector integration."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T02:00:00+11:00"}
sp_id: "SP-INSPECTOR-TELEMETRY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-INSPECTOR-TELEMETRY", "SP-NETWORK-SERVICE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector telemetry receiver and bounded delivery

The production Linux network consumer now authenticates the exact supervised
process, negotiates the existing measured telemetry 0.2 contract and validates
complete snapshots through DataView at their native receipt clock. It subscribes
only after current-policy admission. Every I/O boundary checks the caller's live
profile/supervisor guard. The native service gives policy withdrawal the specified
exit code 126, independently observed through its held child.

The shared receiver exposes one immutable latest accepted full frame, original
bytes and receipt identity, an independently sampled clock and the absolute
heartbeat expiry. Data and duplicate heartbeats never renew the lease. A late
heartbeat cannot reopen it. Duplicate old publications cannot replace the queued
newest state. Delivery checks both profile and supervisor generation; a clock
older than 250 ms cannot authorize a new display update. Disconnect drops queued
payload and clock; policy withdrawal also erases the underlying model. The GUI
must separately own any previously displayed, still-permitted retained state.

Eleven portable cases cover coalescing, byte/time preservation, future and oversized
frames, lease boundaries, heartbeat replay, clock freshness/scope/regression,
obsolete profile/generation, epoch mismatch and policy erasure. Eleven native cases
exercise the production consumer against the real service and an independently
implemented peer. They compare kernel counters and rational rates, reject an
intentionally wrong expected counter, observe receipt/current clock ordering,
preserve exact wire bytes, reject future measurements and invalid role/epoch/PID
or heartbeat claims, and prove policy withdrawal and exact shutdown/reap.

The [checkpoint](checkpoints/inspector-telemetry.json) binds actual commands,
source archives, artifacts, fixed oracles, failures and regression results.
Generated evidence remains ignored under `out/`; shared build tooling remains
under `source/build/`. Completed native recordings are byte-verified before their
duplicate active-output files are removed. No workspace quota is enlarged.

The original portable fixture accidentally added a channel to the snapshot body.
The existing protocol permits that field only in subscription/binding context;
the correction removes the invented member without changing expected outcomes.
The initial independent peer also used an arbitrary socket basename, which the
existing native IPC owner rejects before connecting. Its corrected private parent
and `s` endpoint satisfy the existing contract. Both original failed attempts,
original oracle bytes and explicit corrections are preserved.

The regression selection passes 120 named native cases across ten families,
including the unchanged installed settings and saved-scene inspector. Thirty
portable delivery/model/clock/telemetry/component cases pass on each of Linux,
Windows GCC and the historical v141_xp host profile; the two historical PE/import
checks also pass. The v141_xp vendor deprecation warning remains visible and does
not qualify execution on historical Windows. Specification checks pass 51 schemas
and 183 fixtures; tooling passes 60 cases with two existing Windows symlink skips.

The handshake deadline starts at native connection establishment, including the
hello write. The unchanged native consumer oracle passes again after that review
correction. Source archives retain both implementations and their actual results.

The actual CMake DevelopmentFrontend install again produces exactly five files,
with byte-matched built/archived/relocated payloads. Its production network entry
still refuses the fixture's local allow file with exit 2; no protected policy is
installed. The local unsigned smoke package passes within the unchanged workspace
cap using an explicit reservation for three payload copies and observer overhead.

## Required continuation

W-11 is still in progress. The ordinary frontend and SceneInspector do not yet
consume this delivery object. Continue the same [work package](packages/w-11-inspector-telemetry.md):
add the independent client worker and second supervisor/runtime owner to the
existing backend, enforce exact active-profile intent, and batch UI attach/full/
heartbeat/render work at the existing cadence. Inspect held-child exit 126 to
withdraw the profile and reload through its configuration owner. Clear intent and
queued bytes on navigation, edits, reload, policy loss and shutdown. Do not use
GUI delivery time to renew the native lease or fabricate a measurement clock.

Before enabling that UI path, freeze and execute the installed live-inspector
oracle, keep the older absent-producer inspector fixture's exact expectations,
and run the original settings/editor/recovery/inspector and GUI limit suites.
Native rows, navigation without background demand, source failure/retention,
replacement, policy erasure and shutdown still require end-to-end evidence.
Installed image/topology/performance, human accessibility, desktop/lifecycle,
protected production-policy deployment and all five complete release editions
remain required. This checkpoint is a tested receiver prerequisite, not completed
inspector integration or a release qualification.
