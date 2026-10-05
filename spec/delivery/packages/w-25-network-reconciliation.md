---
type: "SysPane Work Package Boundary"
title: "W-25 network lifetimes and watched acquisition"
description: "Reject obsolete acquisitions and native-key reuse before real network values enter measured publication."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T22:37:18Z"}
sp_id: "SP-W25-NETWORK-RECONCILIATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-NETWORK-ACQUISITION", "SP-W25-MEASURED-TIME", "SP-SCHEDULER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 network lifetimes and watched acquisition

Close the shared identity/reconciliation boundary and connect Linux acquisition
to a held route-netlink subscription. Keep Windows raw acquisition unchanged.
Windows IP-interface callbacks do not by themselves establish coverage of every
raw table interface; qualify that adapter separately. No platform waits for another.

## Shared serialized owner

One owner has a fixed producer epoch, qualified clock domain/local scope and a
monotonic indication revision starting at zero. Each valid change/removal indication
increments that revision. Removal immediately retires the native-key mapping.
Loss of indication continuity, invalid indications or revision exhaustion latches
a source fault; an ordinary full table cannot repair unknown lifetime history.
The owner must be replaced under a new producer epoch after independently confirmed
source/worker cleanup. Do not reset an epoch merely to evade resource exhaustion.

A locally supplied nonzero demand ticket admits work; zero admits no acquisition.
Nonzero tickets increase monotonically; setting the already-active ticket is an
idempotent renewal, and a released/replaced ticket cannot be reused.
Changing the ticket invalidates older results without changing identity history.
An obsolete callback is rejected before reading its result, bracket or clock.
This ticket is not authentication or policy authority. Policy revocation must
destroy the data owner, while a still-running watch may remain only under allowed
source-demand/retention policy. General W-07 demand aggregation remains required.

Commit receives the captured demand ticket, the indication revision at acquisition
start, a complete raw result and start/end qualified ticks. All indications delivered
through the end of acquisition must be applied first. A changed revision discards
the entire candidate and retains the previous sample. Failed/cancelled/capacity
acquisition never replaces prior values or measurement times. Such failure, dirty
state, absent demand or a latched fault makes the retained sample non-current.

On an accepted table, preserve each surviving key's assigned lifetime. First
appearance, reappearance after removal/absence, or changed native index/type gets
a new monotonically assigned lifetime. Sort by native key; reject duplicates,
zero keys/indices and more than 8,192 rows. Reserve at most 8,192 lifetime numbers
per owner (a smaller injected ceiling is permitted for tests); never recycle them.
Build the candidate/mapping first and publish atomically, including on allocation
failure. Capacity failure preserves the old state and reserved IDs. The lifetime
number plus producer epoch is an observation identity, not a persistent hardware
selector or proof of a device/interface join.

Ticks must match the fixed epoch/domain/scope, end >= start, and the next start
must be >= the previous accepted end. A local mismatch/regression latches a clock
fault. Use acquisition **start** as the conservative measurement time; retain end
separately. It is an acquisition bracket, not proof that the OS physically measured
every counter at that instant. Do not substitute completion/receipt/heartbeat time.

For two successful accepted samples of the same lifetime with paired counters and
strictly increasing start times, expose an exact integer delta pair and actual
start-to-start interval. A lower counter invalidates both deltas for that interval;
the new sample becomes the baseline. No wrap is inferred. First/missing/replaced
samples have no interval. Equal counters with positive time produce valid zero
deltas. A failed attempt may lie between successful samples; the next delta covers
the full elapsed interval and makes no claim about traffic distribution in the gap.
No floating-point rate, persistent state, timer or thread is introduced here.

## Linux watch ownership and acquisition

Open one private nonblocking CLOEXEC NETLINK_ROUTE socket, bind RTMGRP_LINK before
the first dump, and retain an open current-network-namespace handle. Verify the
same namespace device/inode before and after each operation. No namespace mutation,
network configuration action or extra privilege is admitted.

Use that socket for both monotonically sequenced dumps and sequence-zero link
indications. Separate notifications from dump replies without counting each
message as a new datagram. Validate kernel sender and notification headers/lengths.
Copy only change/remove kind and positive native key. Bound each drain/acquisition
to 128 datagrams, 8 MiB and 1,024 copied indications, with 64 KiB per datagram and
the existing 8,192-row ceiling. Poll at most 20 ms between stop checks.

Drain pending indications before capturing the dump's starting revision. Consume
indications interleaved with the dump and drain again after DONE. A changed revision
returns interrupted/no rows, with the observed indications and revisions intact.
The caller applies those indications before retrying. No retry occurs in this
primitive. Unknown loss, malformed data, overflow, wrong sequence/namespace, or an
in-flight cancellation/timeout permanently faults and closes the watch: unread
replies must not contaminate a successor query. A pre-call stop does not query or
invalidate a previously healthy watch. Native errors retain numeric codes.

The live test may observe real indications, but does not mutate an interface to
force them. Kernel delivery under removal, overflow, namespace migration and
suspend remains separately unqualified. Native-layout fixtures establish decoding,
not that a live kernel event was induced. The Windows notification track remains
open rather than treating IP-only indications as complete link coverage.
The probe reserves 750 ms before its first dump for an independent observer to
match its owned socket inode to the route-netlink link multicast group in procfs.
This fixed observation window is test infrastructure, not a product latency claim.

References: [Linux Netlink sequencing, multicast and dump consistency](https://docs.kernel.org/userspace-api/netlink/intro.html),
[Microsoft IP-interface notification scope](https://learn.microsoft.com/en-us/windows/win32/api/netioapi/nf-netioapi-notifyipinterfacechange).
Pinned profiles and raw-reader API semantics retain the preceding package.

## Fixed acceptance before implementation

| Case | Fixed stimulus | Required result |
| --- | --- | --- |
| `RECONCILE-IDENTITY` | Keys 1/2; unchanged table; remove/re-add 1; absent/reappearing 2; changed native index/type | Survivors keep lifetime; every replacement gets a different reserved lifetime; old result after indication is discarded |
| `RECONCILE-CLOCK-RATE` | Counters 100/200 at start 100, 130/260 at 110; equality, reset, missing stats, wrong scope, backwards bracket | Deltas 30/60 over 10; valid zero delta only with positive time; reset/missing/first invalid; local clock fault latches |
| `RECONCILE-CANCEL-FAILURE` | Ticket replacement, bad clock on obsolete completion, failed acquisition, dirty completion, continuity gap | Obsolete result harmless; old values/time retained and non-current; gap cannot be repaired by an ordinary full |
| `RECONCILE-CAPACITY` | Lifetime ceiling 2; replacement needs a third ID; duplicate/zero/native malformed rows | No partial publication or ID reuse; previous sample preserved |
| `NETWORK-WATCH-DECODE` | Interleaved change/delete notifications and matching dump/DONE, unknown attributes | Ordered minimal indications; exact dump bytes preserved; wrong/truncated notification rejects |
| `NETWORK-WATCH` | Real subscribed socket, repeated table reads, pre-call cancellation/deadline, independent sysfs brackets | Registration precedes dumps; revisions match observed indications; accepted rows meet fixed native brackets; cancelled/expired calls return empty and keep healthy registration |

Bind all checks to source/package/artifact identity and preserve failures. Keep raw
native keys/counters local under the acquisition package's disclosure rules; commit
case outcomes/counts only. Run full profile suites, import audits, ordinary smoke
packages and specification/tooling checks. Supervised collector publication is the
next integration gate, not a claim supplied by this package alone.
