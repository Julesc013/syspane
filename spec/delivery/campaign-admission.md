---
type: "SysPane Work Record"
title: "Foundation and native-experiment campaign admission"
description: "Record the user-admitted implementation scope and the first package's closed boundaries."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:15:42+11:00"}
sp_id: "SP-CAMPAIGN-ADMISSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-WORK-PACKAGES", "SP-W01-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
updated: {"by": "codex", "at": "2026-10-06T08:15:42+11:00", "scope": "Record original workspace overrun and bounded 2 GiB development allocation with preflight reservations"}
---

# Foundation and native-experiment campaign admission

The user explicitly instructed completion of the foundation and native-experiment
campaign on 2026-10-05, starting from `229a49850a657a76b0201532b4ea61ddfd92a3aa`.
This supersedes the earlier absence of implementation authority. The scope covers
component targets, pinned development profiles, the model, transport/policy,
independent recovery and desktop oracle, early smoke packages and independent
initial native-host tracks. Existing requirements and contract identities remain.

Routine source changes, local builds/tests and task-local commits are admitted.
Privileged operations, weakened acceptance and public release are excluded. No
AIDE binding or descendant-agent authority is invented. Desktop experiments must
remain bounded and reversible, with recovery independent of the surface under test.
Unavailable target laboratories remain blocked qualification, not compatibility.

Use this checkout. Windows development build roots are `out/build/<preset>/`,
captures and packages use `out/campaign/`. Linux uses an explicitly declared
`SYSPANE_LINUX_BUILD_ROOT` task directory under the existing unprivileged account's
`~/.cache/syspane/`, with no second source checkout. An initial configure and chmod
probe demonstrated that this account cannot set permissions on the Windows mount;
the native cache avoids requiring privilege changes. Keep an ownership marker,
record artifact sizes and stop a task
before its owned outputs exceed the current bounded campaign allocation. Do not delete unrelated files or create a
second checkout. Run Linux tools through the existing unprivileged WSL account;
the distribution's default root identity is not needed for building.

The initial allocation was 1 GiB. The subscription checkpoint measured 1,108,437,093
bytes after expanding all three debug/toolset builds; that overrun is preserved,
not described as compliance with the old ceiling. That checkpoint raised the allocation to 2 GiB
combined, recorded in `build-support/campaign-workspace.json`. This is a reversible
development-workspace allocation within the admitted campaign, not a product memory
limit or relaxed acceptance condition. The checkout drive had 68,639,891,456 free
bytes at this decision. Retain the exact debug artifacts and original evidence.

Before each build, test or package launch, run the Windows coordinator
`python build-support/check_workspace_budget.py --action build|test|package` with
one action selected. It reserves respectively 256, 64 or 32 MiB of growth under
the combined ceiling; inspect again afterward. Stop on a failed check and preserve
it before archiving verified owned outputs or explicitly revising the allocation.
The GNOME investigation raises the owned development allocation to 3 GiB. Its
196-package runtime snapshot requires 123,909,062 archive bytes and 345,080,832
declared extracted bytes. Combined with 1,586,274,144 existing owned bytes, the old
2 GiB allocation would leave inadequate room for repeated preserved attempts and
the normal build reservation. The checkout drive has 63.54 GiB free and the native
Linux filesystem more than 1 TB free. This is a measured reversible workspace
decision; no product resource or acceptance budget changes.

This is a preflight reservation, not an OS quota; a new package whose predicted
growth exceeds the reservation needs a measured allocation decision before launch.

## W-01 closure before implementation

The in-process API uses typed publication candidates, each with producer/epoch,
record identity, optional expected base and complete proposed next snapshot. A
base mismatch requests resynchronization before any mutation. This is an internal
publication API, not the future wire delta format. One store is owned by one
writer and fixed producer/epoch; a restarted producer gets a new store and must
publish a full snapshot. Readers retain immutable shared snapshots.

Record replay compares the original typed candidate, including base/generation,
not its normalized result. Identical replay is a no-op; conflicting reuse fails.
Record IDs and retired lifetime IDs remain reserved for the store's epoch. No
silent eviction/reuse occurs when the bounded store fills. A fresh epoch requires
explicit consumer resynchronization and cannot be an automatic capacity workaround.

The initial limits are 8,192 entities, 16,384 relationships, 1,024 sources,
65,536 observations, 8,192 retired identities and 128 replay records. A candidate's
accounted storage is at most 8 MiB, and retained original replay candidates at most
64 MiB. Account fixed typed record storage plus string lengths; these are admission
budgets, not measured allocator/RSS guarantees. Account retired observations within
the same 64 MiB retained-data budget. Candidate construction by trusted callers
precedes admission; later decoders must enforce bounds before allocation.

Identifiers follow the existing ASCII ID grammar and length 256. Display labels
are bounded at 2,048 bytes, string values at 16,384 bytes, units at 64 bytes and safe
error messages at 2,048 bytes. Reject non-finite numbers, duplicate observation
keys, unknown sources/fields, wrong units/value kinds, dangling graph references,
retired identities and non-increasing generations. No partial publication or
uint64 wrapping is allowed. Allocation failure returns a capacity error and
preserves the last accepted state.

For a failed/denied/pending/disabled acquisition on the same entity/source/field,
retain the previous successful value/time, mark retained data stale and preserve
the current attempt/error. Unsupported fields remain null. Removal retains a
bounded diagnostic observation with absent presence, outside the active snapshot.
It cannot bind a replacement entity. A metric-specific expiry makes a sample stale
when monotonic age is at least its declared TTL; inventory without a TTL remains
valid until explicit invalidation. Epoch mismatch or backwards monotonic time
invalidates interval calculation. UTC does not determine elapsed intervals.

Target recipes select actual installed Windows GCC 15.2 and Linux GCC 13.3 tools.
No downloaded dependency or external native library is needed for this package.
Exact tool/runtime fingerprints and declared flags are in `build-support/targets/`.
The Windows profile targets this Windows 10 x64 host; the Linux profile targets
Ubuntu 24.04 x64 under WSL. Neither is a desktop-host or historical support claim.

Cases in SP-ACCEPTANCE-TRACES retain their original oracles. Additional boundary
checks cover capacity, malformed observations, replay exhaustion and epoch changes.
Evidence and the handoff will identify exact commands, source/artifact inputs and
remaining native work under the existing campaign IDs.
