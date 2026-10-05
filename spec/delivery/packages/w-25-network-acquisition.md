---
type: "SysPane Work Package Boundary"
title: "W-25 native network acquisition prerequisite"
description: "Bound real interface-counter reads before admitting identity reconciliation and supervised measured publication."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:17:20+11:00"}
sp_id: "SP-W25-NETWORK-ACQUISITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-NETWORK", "SP-SCHEDULER", "SP-W25-MEASURED-TIME", "SP-W25-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 native network acquisition prerequisite

Implement the native **raw acquisition** boundary required by the real collector.
Read all interfaces returned by the native table, including loopback and inactive
interfaces. Keep native keys and raw type numbers private to the provider. They
are not model entity IDs or persistent selectors. No telemetry publication, rate,
topology continuity, device join, address, route, DNS or Internet claim follows
from this acquisition alone. The full network requirements remain unchanged.

## Result, ownership and limits

One serialized caller owns each acquisition. A request supplies an absolute
steady-clock deadline, a caller-owned atomic cancellation flag and a row ceiling
from 0 through 8,192 (default 8,192). Success returns a sorted unique vector of
native interface keys, interface indices, source-native type and optional paired
uint64 receive/transmit counters. Windows keys are LUIDs; Linux keys are ifindices
within the querying process's current network namespace. No name, MAC, GUID,
address, SSID or packet content is copied into the shared result. Counter absence
stays null; never manufacture zero or widen a 32-bit-only counter as 64-bit data.

The result is either all admitted rows or no rows. Codes distinguish success,
cancelled, timed out, capacity, denied, unsupported, interrupted, malformed and
native failure, with native error number where available. Allocation failure is
capacity. Invalid limits reject before querying. Cancellation/deadline checks run
before opening/querying, between native batches/rows and before returning success.
Cancellation takes precedence when both are already true. All handles/buffers are
released on every return. No timers, threads, retries or retained cache are added.

Linux uses one private nonblocking route-netlink socket, no multicast subscription
in this raw reader, an RTM_GETLINK dump and only IFLA_STATS64 for counters. Bound
datagrams to 64 KiB, total received bytes to 8 MiB, datagrams to 128 and rows to the
request ceiling. Poll at most 20 ms between cancellation/deadline checks. Require
kernel sender, matching sequence/port, bounded aligned records/attributes, unique
indices and a successful DONE. Truncation, overrun, interrupted dump, native error,
malformed lengths and duplicate stats reject the whole candidate. Do not retry a
possibly inconsistent dump inside this primitive; reconciliation owns retries.

Windows uses GetIfTable2 and FreeMibTable, typed MIB_IF_ROW2 access, LUID/index/type
and InOctets/OutOctets. The API allocates its table before the caller can inspect
its row count; this adapter cannot promise an allocation ceiling for that native
buffer or cancel an in-progress API call. The production caller must isolate it
in the existing independently supervised child boundary. A flag is cooperative
cancellation, never proof that a blocked native call stopped. No thread termination
or privileged API is admitted.

Both APIs report counters sampled over the call, not one atomic timestamp shared
by every row. The next reconciliation/publishing package must retain acquisition
start/end brackets, select a documented conservative measurement time, subscribe
before enumeration, reject dirty generations and reserve lifetimes across removal
and native-key reuse. It must also connect demand cancellation, failure retention,
producer lease expiry and OS-confirmed child exit before restart. This package is
a prerequisite, not a replacement for that integration or W-07's full planner.

## API inventory and target scope

| Profile | API / ownership | Documented and admitted floor |
| --- | --- | --- |
| Windows x64 development | GetIfTable2 allocates; FreeMibTable frees; no mutation | APIs documented since Vista; implementation admitted only on the pinned Windows 10 profile, never inferred XP support |
| Linux x64 development | socket/bind/sendto/poll/recvmsg/close, NETLINK_ROUTE RTM_GETLINK, IFLA_STATS64 | Existing pinned Ubuntu/WSL profile; current network namespace only; no namespace change or capability request |

Pin the Windows iphlpapi import archive in the development lock; keep native
network targets absent from the historical profile. Native errors use numeric
codes and fixed project text, not unsanitized OS messages. Operational counters
and native keys are permitted only inside the explicit local acquisition probe.

Sources: [Microsoft table API](https://learn.microsoft.com/en-us/windows/win32/api/netioapi/nf-netioapi-getiftable2),
[row and counter meanings](https://learn.microsoft.com/en-us/windows/win32/api/netioapi/ns-netioapi-mib_if_row2),
[Linux statistics](https://docs.kernel.org/networking/statistics.html),
[Netlink dump consistency](https://docs.kernel.org/userspace-api/netlink/intro.html).
These describe API semantics; native tests establish only observed profile behavior.

## Fixed acceptance before implementation

| Case | Stimulus | Required result |
| --- | --- | --- |
| `NETWORK-READ` | Independent OS reads before/after one raw acquisition | Same complete key set; each returned 64-bit counter inside its independently observed inclusive bracket; source type/index preserved |
| `NETWORK-CANCEL` | Cancellation already true, including an expired deadline | Cancelled; no rows |
| `NETWORK-DEADLINE` | Deadline already expired | Timed out; no rows |
| `NETWORK-CAPACITY` | Zero row ceiling on a host with an independently observed interface | Capacity; no rows; no partial prefix |
| `NETWORK-NETLINK` | Fixed native-layout datagrams with two rows, uint64 extremes, missing stats, unrelated attrs | Exact sorted rows; absent stats null; no counter truncation |
| `NETWORK-NETLINK-REJECT` | Truncated/malformed lengths, duplicate key/stats, wrong sequence/port, ERROR, OVERRUN, DUMP_INTR, missing DONE | Explicit failure with no admitted result, never a partial successful prefix |

The external oracle uses Windows GetIfTable2 through independently declared ctypes
ABI structures, and Linux sysfs counters/index/type. Same-API Windows evidence
checks adapter decoding against a separate implementation, not independent kernel
correctness. Key churn/reset during the bracket is a recorded failure, not a
silently widened oracle. No interface mutation or external traffic is required.

Probe stdout is a bounded private test exchange, not a product/export channel.
The harness holds rows in memory. Committed evidence contains source/artifact
identity, fixed case outcomes and comparison counts, but no native keys, labels
or counter values. On failure preserve raw exchanges only in owned ignored output
and reference their hashes without copying their contents into public records.
Keep the original failure and expectation; never modify the oracle just to pass.

Use ordinary CMake/CTest commands and workspace preflights. Bind native results to
the source, package, executable and exact environment. Full regression, local smoke
packages and schema/tooling checks remain required at the checkpoint. This does
not qualify event delivery, counter-reset recovery, suspend, replacement identity,
cancel-during-native-call, measured publication, complete collection or desktop use.
