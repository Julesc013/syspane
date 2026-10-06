---
type: "SysPane Work Package Boundary"
title: "W-25 collection continuity across consumer replacement"
description: "Keep real collection independently owned while admitting bounded replacement consumers."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T11:00:00Z"}
sp_id: "SP-W25-CONSUMER-CONTINUITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-W25-NETWORK-PUBLICATION", "SP-W25-SUBSCRIPTIONS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 collection continuity across consumer replacement

Surface failure must not restart otherwise independent collection. Close this
native ownership prerequisite before integrating automatic desktop replacement.
The application composition owns one continuous real network worker and one
replaceable native model consumer. Existing platform adapters own authenticated
streams and exact child lifetimes; Sessions, DataView and RestartGate retain their
existing protocol, policy, import and retry ownership. No new wire protocol,
collector, persistence model or scheduler is introduced.

## Finite development composition

Add `CollectorProbe continuity ROOT MODE` and a private child consumer mode.
Use the existing Linux development profile, same UID and POSIX session, exact
expected peer PID, owned 0700 endpoint directories and 0600 sockets/journals.
The root supervisor arms its actual parent lifetime. It owns continuous collector
demand independently of consumer demand. Worker producer identity/epoch and
original full-snapshot generation, measurement, interval and record identity
survive every consumer replacement. This finite authority is typed development
input; it does not establish deployed machine policy or an installed service.

The consumer has a fresh connection and subscription for each held child lifetime.
It imports through DataView before exposing a private synchronous projection.
Reconnect receives a complete original snapshot; transport envelope rebinding must
not alter that snapshot or manufacture a fresh measurement. The supervisor validates
source documents through its own DataView and retains at most one full wire body
for fanout. It remains independently authorized to collect when the desktop grant
is revoked. The revocation fixture changes only that consumer authority; revision
8 denial must prevent all subsequent consumer launch/delivery. A global collection
revocation is outside this case and must also stop its separately owned demand.

Consumer EOF, native exit, protocol failure, three-second subscription expiry or
two-second connection startup expiry quarantines that lifetime. Drop its queue
and subscription before requesting stop. Only an OS-confirmed exit releases the
quarantine. During exit waiting and 1/2/4-second retry backoff the source continues
heartbeats and real acquisitions. Reuse RestartGate with zero test jitter, maximum
three replacements per rolling minute, retained last failure and no automatic
circuit reset. No blocking accept or child wait may pause the source event loop.
The Linux listener gains one nonblocking authenticated accept attempt; EAGAIN or
EINTR yields no stream, never relaxed identity checks. Existing blocking accept
semantics remain unchanged.

Use a fourteen-second experiment bound, existing twenty-five-second worker bound,
one-second heartbeat/acquisition cadence, three-second native leases and existing
frame/queue/model budgets. Each data poll reads at most 16 KiB and 16 frames;
writes remain bounded to 100 ms and peer failure closes that consumer. Shutdown
has a two-second exact-child exit bound. Private journals retain original payloads
and receipt clocks within the existing 4 MiB/file ceiling; public records contain
lifecycle, generation and result metadata only. Preserve failures and all owned
descendant exit observations. No detached/unbounded process or inherited IPC FD.

## Fixed acceptance cases

Run `tests/protocol/native_consumer_continuity.py` against the actual Linux probe.
The independent observer holds pidfds before sending any fault to an owned child.
Check original source/consumer journals privately; publish only hashes and checks.

| Case | Required result |
|---|---|
| LIVE | One worker and consumer; advancing original source measurements and imported full snapshots; graceful held exits |
| CRASH | Kill first consumer after import; confirmed exit precedes replacement and the one-second backoff; same held source publishes new measurements during the outage; replacement imports matching original snapshots |
| HANG | Stop first consumer after import; independent subscription expires before stop request; no replacement until held exit; source keeps acquiring through the three-second failure and backoff |
| REVOKE | Kill first consumer; apply typed consumer revision 8 before retry admission; continued independent collection, no replacement or later consumer payload |
| CIRCUIT | Kill each of four consumers after import; delays are 1/2/4 seconds, no fifth child, circuit remains open while the same collector continues |

Every sample received by a consumer must match a previously observed original
source snapshot exactly, including measurement timestamps. Source generations and
successful acquisition timestamps must advance across the consumer outage; source
PID/held lifetime/epoch must remain identical. A held old sample or a newly
restarted collector cannot pass. Recompute real counter brackets and rates from
independent native reads and original source records. Preserve failed attempts
before rerunning. Run affected native IPC and collector regressions and the full
Linux CTest suite, then regenerate/validate the specification bundle.

This prerequisite does not qualify visible recovery, editing, shell replacement,
cross-session attachment, installed policy, Windows/macOS hosts or product release.
The GNOME shell currently owns its POSIX session; a persistent external controller
must acquire an explicitly specified same-session composition before using this
transport. Do not weaken native session authentication to bypass that boundary.
