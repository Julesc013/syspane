---
type: "SysPane Work Record"
title: "Measured network presentation checkpoint"
description: "Shared renderer inputs preserve exact selected values, measurement metadata, lease state and disclosure lifetime."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:02:33Z"}
sp_id: "SP-NETWORK-PRESENTATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-NETWORK-PRESENTATION", "SP-W25-PACKAGE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Measured network presentation checkpoint

From `8b34ac65dbdf9abbaba3ffa75d7ba10b204994b2`, the shared C++ renderer projection
consumes the existing measured data owner through a synchronous, current-policy
borrow. The [package](packages/w-25-network-presentation.md) fixes exact selection,
four-field order, status axes, TTL, text formatting, capacity and empty outcomes.
It introduces no transport format or persistent cache.

The selected `(producer, epoch, entity)` cannot silently follow a reused index or
new epoch. Counters retain all 64 bits. Rate text rounds the actual binary64 value
to three decimal places using bounded integer arithmetic; 46 independently prepared
rational expectations cover extremes, halfway cases and adjacent values. Lease
presentation does not overwrite field freshness or original measurement metadata.

Current disclosure denial yields an empty restricted frame. Invalid selection,
clock, shape or capacity cannot expose a partial field prefix. Callback exceptions
propagate once, and borrowing prevents data-owner reentry. The production component
is exercised by the existing finite Linux CollectorProbe through its private test
pipe. Public evidence contains comparison counts and outcomes, not operational
counter values or native interface identities.

## Executed verification

| Profile | Full suite | Scope |
|---|---:|---|
| Windows x64 / GCC 15 | 102 passed | Shared projection and existing native Windows regressions |
| Linux x64 / GCC 13 | 107 passed | Shared projection, real collector comparisons and existing native regressions |
| Windows x86 / v141_xp | 94 passed | Portable components and 13 PE/import audits on Windows 10/WOW64 |

All six new `presentation.NVIEW-*` families and both component-graph checks also
pass independently on every profile. Three fresh local model smoke packages pass
relocated execution. These archives contain the development model, not a desktop
edition. Profile revisions are 19, 20 and 11 respectively; pinned toolchains are
unchanged. The developer guide `docs/developers/build.md`, under Shared measured
network presentation, contains the runner and evidence commands.

Evidence is retained under `out/evidence/w-25-network-presentation-`:
profile records and logs, native public records, smoke records, the attempt manifest
and specification verification. The machine handoff is
`out/evidence/network-presentation-handoff.json`. Original attempt source
archives and private operational failure data remain in their owned ignored roots;
the public manifest identifies exact hashes and paths.

## Preserved failures and corrections

The initial combined-workspace preflight stopped within its declared reserve. A
measured allocation revision raises this campaign's combined output allowance from
3 GiB to 4 GiB; reserves remain unchanged and no files were removed. The initial
Linux configure also exposed an obsolete hard-coded 1 GiB subtree guard. It now
uses the declared allocation in addition to the mandatory combined preflight.

Two initial portable selection runs failed because the fixture changed the document
epoch without updating its observation epochs. The existing codec correctly rejected
that inconsistent document. The corrected fixture still requires explicit selection
after full replacement; the original failures and source archives remain.

The first Linux full suite failed its collector crash case with `clock.peer_exited`.
The stream correctly refused clock qualification after peer exit. An explicit retained
projection now uses the existing ordinary borrow only in retained state: age is
unknown, allowed non-null values are stale, and original metadata stays unchanged.
The measured API and native clock guard remain unchanged. This is the retained path
already allowed by the measured-time contract, now precisely bound and tested.

The first historical full suite rejected three previously undeclared static-CRT
imports introduced by the locale fixture. Their documented API floor and exact
allowlist amendment are recorded in the package. The original audit failure is
preserved; all other import restrictions still apply. Guest execution remains
unqualified. A final review also corrected indentation and added renderer test
inputs in the historical evidence recorder; final recording uses that corrected
tool and fresh smoke manifests. Product source and fixed test oracles did not
change after the final passing suites.

## Next boundary

Close operational delivery to the native surface: authenticated admission, selected
frame ownership, queue bounds, policy revision/invalidation, cache/text/pixel erasure,
independent expiry and lifecycle acknowledgement. Then verify real displayed values
and retained/revoked pixels with an external oracle. The public-marker experiment
does not authorize an operational cache. Keep the original default focus failure
and optional-integration limits intact.

Product controller/demand planning, render watchdogs, native editor exit, protected
policy, Windows full-table notification coverage, kernel topology/suspend faults,
historical guests and the Mac laboratory remain open. No allocation-fault injection,
native typography/accessibility or full desktop qualification is claimed here.
W-25, full scene/rendering work and the overall campaign remain incomplete.
