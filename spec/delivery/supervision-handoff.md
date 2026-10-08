---
type: "SysPane Work Record"
title: "Native child supervision implementation checkpoint"
description: "Bind owned-child lifetime and independent health decisions to Windows/Linux fault evidence."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:09:36+11:00"}
sp_id: "SP-SUPERVISION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W25-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native child supervision implementation checkpoint

W-25 now has native owned-child supervision on both development profiles and remains
in progress. Base `8292b1cf7f0f5dcb96c75c0d3e6104134d36f94e`, containing commit and
recorded input digests identify this checkpoint. The earlier
[portable recovery handoff](recovery-handoff.md) remains historical. The full
campaign, independent diagnostic entry and external desktop oracle remain open.

## Implemented boundary

`source/platform/child.hpp` launches only a worker instance of its own executable;
there is no arbitrary-program, shell or attach-to-PID interface. Windows assigns a
suspended child to a private one-process, kill-on-close job before resuming it and
retains its process handle. Linux uses explicit self-exec spawn, closes inherited
descriptors, retains a pidfd and reaps only its owned child. Stop request and
confirmed termination are separate. The gate cannot start/reset a quarantined
slot; cleanup cannot silently declare an outstanding child stopped.

`source/diagnostics/health_link.hpp` negotiates `recovery-health` 0.1.0 and role-bound
health/render-progress features over W-24's native authenticated stream. Frame and
operation budgets are tightened for the health channel. A poisoned link closes;
old epochs, ungranted roles and wrong render generations never renew progress.
The existing preview session rejects the two new optional render message types.

`SysPane.RecoveryProbe` combines these adapters with the portable lease, render-watch
and restart guards. A synthetic desktop worker has an independent thread that can
stall while its IPC heartbeats continue. The producer-hang case blocks its actual
health loop; the crash case abruptly exits the actual child with code 73. The
supervisor confirms child exit before replacement and applies the previously fixed
backoff/circuit limits. No test terminates an unrelated process or uses elevation.

Both profile revision 5 builds pass 49 CTest entries: 18 foundation checks, 17
protocol/policy checks, eleven portable recovery cases and three native families.
The new RECOVERY-01 family has nine concrete cases: graceful shutdown, producer
hang, render-worker stall, crash circuit, live-child quarantine, parent loss,
role denial, wrong epoch and wrong render generation. Each profile's run observes
15 launched children, all through independent OS handles/pidfds before confirming
their exit. The parent-loss case kills only the harness's own supervisor.

## Evidence and failure preservation

Current records are `out/evidence/w-25-supervision-<profile>.json`, matching
CTest logs and NATIVE-01/NATIVE-02/RECOVERY-01 report copies. The recorder requires
the exact complete case set and reports named in that CTest log. It checks recovery
probe/source digests against the run and requires every child to have independent
alive and exited observations. Artifact/import, build/profile/dependency and source
identities remain bound to the actual development environment.

The first Windows build failed on dependent template parsing in a generic callback.
The callback now declares its actual `string_view` parameter. The original diagnostic
and source digest are preserved in `out/evidence/w-25-supervision-attempts.json`.
Warnings remain errors. No native case failed and no timing criterion was relaxed.
The initial eight-case runs preceded the added wrong-generation regression; the
final evidence requires all nine. Per-attempt reports remain in owned build output.

## Scope and remaining work

These workers do not render pixels or carry telemetry snapshots. The health-only
lease remains waiting for data, rather than inventing a synchronized presentation.
No independent diagnostic executable/inspector, current-policy payload erasure,
native editor-exit path or externally observed stale/visible state is delivered
here. W-02 and the native desktop-host experiments remain mandatory. Persistent
commands and telemetry subscriptions remain disabled.

Linux's parent-death bound follows the spawning thread's lifetime; the probe uses
one long-lived supervisor owner. Future compositions must preserve that lifetime
and sole-reaper rule. The inherited environment is trusted development input, and
the Linux worker creates no descendants. This is not hostile-code containment.
The native profiles remain the observed Windows 10 and Ubuntu WSL2 environments;
cross-user/logon, historical Windows, Mac and real desktop qualification do not
follow from these cases. Kernel/compositor failure remains outside the guarantee.

Next, implement independent diagnostics with bounded safe metadata and a conservative
native inspector, preserving mandatory policy when optional content is damaged.
Close full snapshot/data-recovery semantics before connecting a real surface.
Build W-02's external pixel/native-exit oracle independently, then execute host
tracks in available admitted labs while recording unavailable labs honestly.
W-25 and the campaign remain active and incomplete; no release was published.
