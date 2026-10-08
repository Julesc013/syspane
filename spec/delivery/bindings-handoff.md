---
type: "SysPane Work Record"
title: "Policy-bound scene binding checkpoint"
description: "Scoped authored selectors and pins consume accepted telemetry with explicit identity, freshness and permission."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T20:04:02Z"}
sp_id: "SP-BINDINGS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-BINDINGS", "SP-LAYOUT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-bound scene binding checkpoint

Source baseline: `743da6cd75a342e53ba76492b9c312c69ddffa10`. The resulting commit
is identified by Git history. The [package](packages/w-09-bindings.md) closes the
existing selector/direct/persistent/unresolved binding grammar without changing
its version or the authored scene. W-09 and all complete release tracks stay open.

The shared scene component routes through an explicit trusted producer catalog,
checks every relevant view's current disclosure permission and borrows all inputs
until one synchronous callback finishes. It performs no acquisition or caching.
Unknown predicates cannot become true through ne; incomplete inputs cannot become
a complete-looking partial collection. Exact uint64/binary64 comparison, stable
scoped identity, collection truncation and explicit pin mapping are executable.
Observation status, null versus zero, safe error code, TTL freshness and producer
lease state remain distinct. Sorting and temporary/output storage are bounded.

## Validation and preserved failures

Seventeen binding families exercise the production DataView admission and borrowed
projection, including two producers, scope isolation, missing/stale/retained values,
restarts, invalid clocks, policy erasure, maximum returned collection, budgets and
callback lifetime. Original expectations were archived before implementation.
The initial fixture needed its existing accessibility grant, removal of an invalid
snapshot member and one compiler-formatting correction. Review of the proposed
duplicate wire fixture identified the existing stricter entity/field uniqueness
rule. Retain the original proposed test and failed run, require wire rejection,
and separately exercise the original ambiguity expectation through an admitted
typed retained DataView.
No existing wire or model acceptance rule was weakened.

One full regression run timed out at the existing content-command oracle's
one-second receive check after confirmed worker replacement. The store still
selected revision 40; the complete synthetic failure tree and event trace are
preserved. The unchanged isolated oracle passed afterward. The cause remains
undetermined; no product deadline or acceptance assertion was relaxed. Subsequent
passes do not erase this timing failure or qualify reliability under arbitrary load.

The initial Linux configure failure detected an external installed-package update.
Record the package log, old/new pins and actual GLib/GObject/GI hashes. The revised
Linux profile uses GLib 2.80.0-6ubuntu3.9 and glibc 2.39-0ubuntu8.9; previous evidence
remains bound to its original runtime. No system package was installed or changed
by this work. A separate preserved workspace reservation stop led to the measured
6 GiB development allocation, retaining standard reservations and product limits.

Final suites and exact staged-source checks are recorded in
`out/evidence/w-09-bindings-attempts.json` and
`out/evidence/w-09-bindings-staging.json`. The machine handoff is
`out/evidence/bindings-handoff.json`. Historical-toolset checks run on the
modern Windows host; they are not historical OS qualification.

## Next integration

Bind the common authored scene/resource generation to this value projection and
the shared geometry engine, then supply real native text metrics and draw the
admitted primitives with native fallback and current-policy cache erasure. Route
all candidate producers and own persistent mappings explicitly. Complete native
settings/direct editing, independent visible activation/recovery and each platform's
package/lifecycle qualification. A synchronous shared projection is not evidence
of displayed values, accessibility, behind-icons placement or a complete release.
