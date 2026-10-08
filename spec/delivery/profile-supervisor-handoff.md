---
type: "SysPane Handoff"
title: "Native configuration process supervisor"
description: "Independent deadlines, exact child exit proof and bounded profile-controller replacement."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T19:11:12+00:00"}
sp_id: "SP-PROFILE-SUPERVISOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-SUPERVISOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native configuration process supervisor

LinuxProfileSupervisor now owns the native configuration child through startup,
health/transaction watches, quarantine, actual exit and bounded replacement. It
uses the existing Child pidfd, health protocol and restart decisions. The caller
supplies an admitted helper and profile selection through a native API; the
supervisor sends the existing bootstrap on an exclusive inherited channel.

The connectable endpoint is available only after a matching-epoch handshake and
native socket verification. An operation that keeps sending heartbeats still
expires at its independent five-second deadline. Readiness never resets the
three-replacement circuit. Signals and EOF never count as stop proof: replacement
waits for native wait, and each generation receives a fresh producer epoch.

Close withdraws readiness, prevents further launches and allows two seconds for
cooperative shutdown before requesting an exact stop. Polling continues until
actual exit. Runtime cleanup verifies held directory/socket identities and removes
only owned entries; substitutions and unexpected files remain intact and prevent
automatic replacement. Health buffers, stderr and undrained native events have
explicit bounds. Native setup/launch/cleanup belong on an independent supervisory
owner outside GUI callbacks; command and storage workers cannot run this owner.

## Evidence

Nineteen fixed native cases pass in the admitted non-root Linux/ext4 laboratory.
A separate Python observer checks real child pidfds, elapsed deadlines, peer PIDs,
restart ordering, exact committed settings/scene/resource bytes and original-epoch
reconciliation. A post-durable timeout recovers revision 1 without producing
revision 2. The test-only helper can omit health, hold storage, change policy,
forge health, flood diagnostics/events or ignore shutdown. Production binaries
have no such controls. A deliberately wrong stored-output expectation is rejected.

The first native run failed in the observer after the real commit and normal child
closure. It checked the supervisor's exit before draining its last pipe messages.
The observer now reads through actual pipe EOF before treating a missing required
event as failure. Product code, deadlines, fixed case definitions and storage
expectations were unchanged. The failed execution, exact inputs, successful rerun
and both native/runtime directories remain preserved.

The existing PROFILE-CONTROLLER, COMMAND-IPC, RECONCILIATION and
TRANSACTION-SUPERVISION families also pass: five native families and 55 distinct
cases in this checkpoint. Component graphs and forbidden-edge controls pass on all
three development profiles. Windows checks verify component isolation; they do not
provide a Windows implementation of this Linux supervisor or qualify legacy OSes.

The [checkpoint](checkpoints/profile-supervisor.json) binds source captures,
artifact hashes, all executions, native archives, fixed inputs and specification
checks. Raw archives remain ignored local out/evidence/profile-supervisor* content.
Short runtime roots are explicitly inside the existing owned Linux campaign and
are archived separately with node identities. No evidence was pruned.

## Continuation

W-08 remains in progress. The next integration boundary is verified installed
helper lookup and a controller/inspector owner that schedules this supervisor
independently of UI and storage, connects authenticated command sessions and
reconciles outstanding requests on epoch change. Add coherent policy-filtered
profile/resource projection for settings/editor startup, then connect live telemetry,
scene activation, recovery context, imports and package/lifecycle operations.

The component accepts a trusted native helper path; held-ELF validation does not
attest to installation provenance. Production protected-policy deployment remains
unqualified in this laboratory. Complete native lifecycle, platform adapters,
accessibility/performance, all five desktop editions and the original release gates
remain required. No public release or privileged operation was performed.
