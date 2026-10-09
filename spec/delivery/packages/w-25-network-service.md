---
type: "SysPane Work Package Boundary"
title: "W-25 native network service for installed inspection"
description: "Move measured acquisition into an authenticated, independently supervised product child."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T00:00:00+11:00"}
sp_id: "SP-W25-NETWORK-SERVICE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-NETWORK-PUBLICATION", "SP-W11-INSTALLED-INSPECTOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native network service

This prerequisite connects the existing measured source, demand and native child
owners to a product service. The installed inspector still needs its own bounded
consumer and current-policy delivery integration before it can display these data.
Keep the four fields, clocks, rates, complete-table limits and failure semantics
of [network publication](w-25-network-publication.md) unchanged.

## Authority and ownership

The verified configuration helper also accepts the trusted invocation `--network`
followed by the decimal guardian PID. This selects a separate process and does not
give network work access to profile commands or paths. The existing supervisor
selects this entry through a typed service argument; its default configuration
entry remains unchanged. Sealed execution still uses the existing verified helper
identity. Its argv[0] is `syspane-network-host` and epochs start with `network:`;
the sealed executable retains its verified `syspane-configuration-host` memfd
label. Distinguish roles by held process identity and exact arguments, not that
shared executable label. This clarification preserves the observed initial
label assertion failure; it does not change executable identity or authorization.

The inherited authenticated guardian stream carries one length-framed bootstrap
of at most 32768 bytes within five seconds. Its exact members are `format`
(`SysPane.NetworkController`), `schema_version` (`0.1.0`), `producer_epoch`
(identifier), `client_pid` (nonzero canonical decimal string) and `endpoint`
(the private listener path). No client-supplied policy, profile or acquisition
instructions are admitted. Native same-user/session/PID checks remain mandatory.

The service reads the existing protected machine policy itself. A trusted compiled
test caller may inject a policy reader and an acquisition callback; the production
entry exposes neither through environment variables nor files. Policy must be
available at startup, checked at least every 100 ms while the loop runs, before
message admission and before publication/dequeue. Any changed or unavailable
snapshot ends the epoch. A blocked policy reader is contained by the guardian's
existing independent three-second producer lease.

The guardian channel uses recovery-health 0.1 with collector role and no transaction
feature. Its startup, lease, two-second close, exact child-reap, restart backoff,
circuit and identity-bound directory cleanup contracts stay unchanged. No sample
or successful socket write renews health. Parent death terminates the native child.

One exact console PID can open one data connection. It negotiates existing measured
telemetry/snapshot/observation 0.2 for `producer:network`, channel `inspector`,
classification `operational`. Both inspector and accessibility disclosure must be
permitted. Only hello, heartbeat, subscribe, unsubscribe and shutdown directions
are admitted; configuration commands and non-telemetry handshake features are
refused. The frame ceiling is 1 MiB,
with no more than 16 decoded input frames or 2 MiB of input in one loop pass.
Output uses the existing bounded session outbox and negotiated frame limit.

The source watch is created only after authorized demand for the existing four
fields. One acquisition slot has a 1000-ms cadence, two-second cooperative native
deadline and 2500-ms demand timeout. The task owns the read and original UTC/start/
end measurement; the service loop owns demand, source identities and publication.
The data stream outlives the task; measurement-clock calls have one serialized
task owner. The service loop does not also sample that mutable clock facility
while the task runs. Exceptions or expired deadlines exit the process without
waiting indefinitely in a task destructor; the guardian confirms native exit.

Disconnect, lost demand, unsubscribe or shutdown cancel the task, clear applicable
queues and drain for at most two seconds. This child never reuses a retired source
identity map for another subscription. Changed policy or acquisition continuity
ends the epoch immediately. Initial failed acquisition sends no invented table;
later failure retains the original values and timestamps with failed/stale status.

## Fixed acceptance and execution

The native service harness must observe actual Unix peers, held process lifetimes,
route-netlink ownership and independent kernel counter/time brackets. Cases cover
no demand, two live measured publications and independent rates, wrong role,
wrong PID, configuration-feature refusal, sealed launch and crash/restart,
unauthorized disclosure, unsubscribe, lost data lease, policy change during held
acquisition, hung acquisition, guardian loss and clean/held-task shutdown. A wrong counter
control must fail the independent value oracle. The unchanged collector/demand
and configuration-supervisor regressions are required after shared-owner changes.
Freeze the package and oracle before product edits; preserve baseline failure.

Use ordinary workspace preflight and the Linux development build, then:

```sh
ctest --preset linux-x64-gcc13 -R '^native[.](NETWORK-SERVICE|NETWORK-SUPERVISOR|PROFILE-SUPERVISOR|NATIVE-COLLECTOR|NATIVE-DEMAND-EXECUTOR)$' --output-on-failure
```

Record exact source and artifact hashes and raw results in ignored owned evidence.
This package does not qualify installed inspector pixels, other native editions,
protected policy deployment, or public release. Its successor connects this service
to the installed frontend with bounded queue, clock, lease and erasure ownership.
