---
type: "SysPane Work Package Boundary"
title: "W-25 live measured collector session for GJS"
description: "Preserve original measured frames through a bounded supervised native session before visible desktop acceptance."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:32:16Z"}
sp_id: "SP-W25-LIVE-NETWORK-SESSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-GJS-NETWORK-VIEW", "SP-W25-NETWORK-PUBLICATION", "SP-W25-GNOME-CLOCK"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 live measured collector session for GJS

Extend the existing finite Linux CollectorProbe and native NetworkView. Add one
asynchronous GJS session owner reusable by the owned shell experiment. Preserve
all prior probe modes, telemetry 0.2 identities and the shared model/projection.
This development session is not installed policy, a complete controller or a
general routing service. Native pixels remain mandatory before visible freshness.

## Native owner and forwarding

`CollectorProbe stream <owned-root> <mode> <private-journal>` is launched directly
by its GJS owner in the same POSIX session. Modes are `hold`, `lease-loss`, `hang`.
The native parent-death guard binds the actual launching parent; only that held
parent PID may connect to `<root>/v/s`. Health/data listeners remain `<root>/h/s`
and `<root>/d/s`. Every directory is private and owned; each endpoint retains the
existing native UID/session/PID checks. One session launches at most one worker.

The worker acquires and publishes two actual network samples one second apart.
After the second it holds the original publication, demand and watch alive while
the sample ages. This deliberate measurement pause is disclosed in the fixture;
it is not a claim of continuous current sampling. `hang` stalls that worker after
the second publication. `lease-loss` keeps the worker/health path alive but drops
subsequent data-heartbeat responses at the forwarding boundary. Neither control
rewrites values, measured times or producer epoch.

Forward each admitted hello/subscribe/heartbeat and producer welcome/snapshot/
heartbeat as its exact original payload and four-byte framing. Shutdown is forwarded
before graceful worker exit. Only those directions/types are admitted. Bind all
post-welcome envelopes to D and the newly launched worker epoch. Before forwarding
a producer message, sample both authenticated connections and require equal native
clock ID and process-local scope. GJS independently maps that namespace to its own
native scope; no textual scope is forwarded or reused across processes.

Read chunks are at most 16 KiB and batches at most 16 messages, with the existing
1 MiB frame and five-second incomplete-frame limits. Both directions use the
negotiated frame ceiling. Welcome must finish within five seconds. There is no
unbounded forwarding queue: each write has a 100 ms limit and failure stops the
session. The native session is finite, at most 20 seconds after connection plus
bounded child cleanup. Existing worker health expires after three seconds; a
responsive supervisor requests shutdown, waits 250 ms on fault, then terminates
only its held child if necessary and requires native exit proof within two seconds.
Normal shutdown gets one second for graceful exit. No automatic restart is added.
Parent death uses the existing kernel guard for both native generations.

Public stdout contains only bounded lifecycle events, never network payloads.
The explicit journal is exclusive, no-follow, regular, mode 0600 below an owned
mode-0700 parent. Record exact producer payloads and native observation ticks there,
with a 4 MiB total limit; keep it private in owned evidence. Local filesystem calls
are not claimed interruptible. The GJS owner has its own finite deadline and can
terminate its held supervisor if native I/O ceases. No retained report is a live
source after native exit.

## GJS session and policy

Add native `subscribe()` and `heartbeat(sequence)` frame constructors; they require
a welcomed, permitted, non-obsolete owner and reuse existing bound 0.2 messages.
Heartbeat sequence is a canonical uint64 string. No JS telemetry encoder is added.
The session launches the native supervisor, drains its bounded public stdout, then
connects/reads/writes asynchronously with cancellation. It owns one native
NetworkView, one serialized write queue (at most 16 frames/64 KiB), one pending read
of at most 16 KiB, and timer callbacks. Startup must reach the first full within
two seconds; the complete session deadline is 18 seconds. A 50 ms timer projects
the shared model independently of observer calls. Send increasing heartbeats every
second while admitted. Queue overflow, native error or late callback after closure
cannot restore data.

The trusted owner supplies initial typed policy revision 7. Revocation applies
revision 8 and drops the native/JS projection before reporting completion, then
shuts down the source session. Regrant requires a new owner. On ordinary stop,
stop new work, send the native normal-shutdown frame asynchronously when bound,
close transport and wait for actual supervisor exit. If graceful completion fails,
terminate the owned supervisor after one second; wait/reap it explicitly. Public
state contains lifecycle facts only. Operational projections are passed synchronously
to the admitted renderer/private fixture sink, which must clear retained payload
on revocation/close. Pixel erasure cannot be inferred from callback completion.

## Fixed evidence and visible integration

First exercise the real asynchronous owner in standalone GJS, without a display:
`live`, `lease-loss`, `hang`, `revoke` and `parent-loss`. Independently hold supervisor
and worker pidfds. Bracket original counters with native before/after reads and
measurement times with BOOTTIME. Derive rates from the two original counter/time
pairs; verify native projected strings and exact original timestamps/metadata.
The journal's original payloads must agree with the consumer's observed generation
and values. Live heartbeats must allow the fixed second sample to become stale
without changing its age; dropped data heartbeats must expire its independent
lease. Worker hang must be detected by native supervision and stopped with native
exit proof. Revocation must synchronously drop the consumer/sink before source
shutdown. Actual GJS parent exit must stop both native descendants. Preserve raw
failures and source/artifact/environment identities; never commit private values.

Then use the same owner in the existing owned GNOME composition. Independently
decode actual counter/rate glyphs and age/expiry, with frozen-age, ignored-expiry
and wrong-value controls. Verify policy erasure, lease loss, native exit and
callback disposal. The prior public-clock and retained-cache oracles stay intact.
Until those pixels pass, describe the result as live native session qualification
only. Product demand/policy, general queues, render supervision, native suspend,
namespace changes and complete desktop/editor recovery remain separate work.
