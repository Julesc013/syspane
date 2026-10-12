---
type: "SysPane Work Package Boundary"
title: "Complete Linux processor accounting and reported topology"
description: "Bounded proc/sysfs acquisition, exact accounting semantics and independent live verification."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T05:00:00+00:00"}
sp_id: "SP-W14-LINUX-PROCESSOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RESOURCES", "SP-W14-PROCESSOR-STATE", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Complete Linux processor accounting and reported topology

Continue W-14 from ed79d5e7. This package admits unprivileged read-only Linux
acquisition in the existing WSL laboratory and portable decoder checks on all
three development profiles. It does not complete W-14, qualify physical hardware
or enable a resource metric in the product. Windows/macOS acquisition, descriptors,
publication, policy/demand integration, memory/GPU and all five complete editions
remain required. Platform acquisition must not depend on runtime state ownership.

## Observable accounting and identity

Read /sys/devices/system/cpu/online, kernel-reported per-CPU physical_package_id,
core_id and core_cpus_list, /proc/stat, the same topology again, and online again.
Compare parsed online sets and complete topology. A mismatch is interrupted, with
no partial result and no implicit retry. Equal brackets are evidence of consistency
at the reads, not an atomic snapshot or proof against hotplug ABA. Missing required
interfaces are unsupported; permission failure is denied; other system errors,
cancel and timeout retain their distinct status and errno. Never fabricate zero.

Include every online logical CPU, sorted numerically, with stable source IDs
linux:cpu:N in the source epoch. Do not use enumeration position, process affinity,
cgroup quota or the aggregate cpu line as a substitute. One linux:online domain
contains all included CPUs; package/core relationships are topology metadata,
not invented scheduler groups. Preserve reported IDs including -1 and core ID 0.
These values can be kernel defaults or virtual topology; physical inventory and
container/host scope require later descriptors and qualification.

The definition linux:execution-ticks-v1 uses USER_HZ from positive _SC_CLK_TCK.
Total is user + nice + system + idle + iowait + irq + softirq + steal. Nonexecution
is idle + iowait + steal. Busy is therefore user + nice + system + irq + softirq.
Guest and guest_nice, when provided, remain raw subcategories and are not added a
second time. Eight or ten counter columns are admitted; inconsistent row shapes,
nine columns or malformed unsigned numbers fail. Extra columns are unsupported
until a new definition is admitted. The aggregate line is parsed but not summed.

Retain all eight contributing categories as bounded accounting parts in the
shared counters. A decrease in any part rebases the entire interval, even when
total and nonexecution increased. Parts have a fixed order/count for a definition,
are at most sixteen, and all rows in a batch have the same count. A count change
for a surviving ID is invalid, including across demand/gap recovery; use a new
owner for a different definition. Existing callers may omit parts consistently.
All existing state/ticket/clock/gap rules remain. A reported topology change must
notify the existing state owner before committing a successor; there is no second
state scheduler or policy authority inside the native reader.

## Bounds, failure and ownership

CPU lists use canonical decimal indices up to INT32_MAX, comma-separated indices
and inclusive increasing ranges. Whitespace at the ends is accepted; empty lists,
duplicates, overlap, reversed ranges, signs or junk fail. Expand at most 8192 IDs,
or the requested smaller row limit. Oversize is capacity, never truncation. Admit
one topology record per online ID with its own ID in its core peer list. Offline
peer IDs may remain metadata. Missing/duplicate/unexpected CPU rows or topology
records fail. All arithmetic uses checked uint64 sums.

Bound each online/peer-list input to 64 KiB, each topology ID to 32 bytes and stat
to 2 MiB; all input text combined is at most 24 MiB. The native reader uses fixed
kernel paths derived only from validated numeric IDs. Before and after every
open/read and before successful return, check the caller's cancellation flag and
steady deadline. EINTR may retry only while these checks permit. Kernel read calls
are not preemptible by this helper; worker/process isolation remains the later
integration boundary. No GUI-thread or hard real-time guarantee is inferred.
Allocation exhaustion is capacity. All unsuccessful results have empty rows.

## Fixed oracles and live evidence

Portable cases independently specify sparse/shuffled IDs; all 128 CPUs; exact
weighted utilization; guest double-count rejection; valid zero/full execution;
hidden iowait decrease; topology interruption and explicit rebase; malformed,
duplicate, missing, oversized and overflowing inputs; unavailable/error mapping;
expired/cancelled requests; and accounting-part shape preservation across gaps.
Literal two-CPU deltas are busy/total 40/60 and 80/100, yielding 120/160 = 75%.

The Linux probe obtains two actual complete captures, emits every raw category,
topology and monotonic acquisition timestamp, and commits them through the shared
owner. An independent Python runner reads proc/sysfs immediately before and after
the probe, verifies complete CPU sets/topology and category bounds, and calculates
each and aggregate interval with Python integers. Preserve all observations and
source/artifact/environment hashes. Pending/reset is reported honestly rather
than invented as a utilization pass. Cancellation/timeout use actual reader calls.
No CPU hotplug, affinity, quota, privilege or machine topology is modified.

Run ordinary workspace preflight/configure/build, portable processor/model/network/
graph controls on all three profiles, Linux native acquisition and historical PE/
pinned-input audits including the new decoder executable. Preserve failures.
The checkpoint is implemented only after these runners execute; current-host WSL
evidence is not older Linux, large-server, low-end, XP guest, 9x or macOS evidence.
Next integrate Linux descriptors/publication/demand and implement remaining native
resource providers. Generated outputs stay under owned ignored out/ roots; shared
tools stay in source/build and the retired root stays absent.

Accounting and topology references: [proc documentation](https://docs.kernel.org/filesystems/proc.html),
[topology documentation](https://docs.kernel.org/admin-guide/cputopology.html), and
[kernel guest accounting](https://raw.githubusercontent.com/torvalds/linux/master/kernel/sched/cputime.c).
