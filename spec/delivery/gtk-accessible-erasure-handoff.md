---
type: "SysPane Handoff"
title: "Retained GTK caches and explicit remote withdrawal"
description: "Preserve failed toolkit erasure candidates, retired/collapsed data and real wire errors."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T22:44:46.703477+00:00"}
sp_id: "SP-GTK-ACCESSIBLE-ERASURE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-GTK-HISTORY-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Retained GTK caches and explicit remote withdrawal

The standalone toolkit experiment rejects every candidate under its strict
original gate. Public cache refresh clears all held local text/name/count/layout
in both cohorts, but the expanded callback takes 276.833 ms against the unchanged
100-ms GUI limit. External old-object requests return explicit UnknownObject
errors rather than successful empty data. No product change or qualification is
claimed; all 70 preceding compiled artifacts remain byte-identical.

The [package](packages/w-11-gtk-history-limits.md) closes exact canaries,
ownership, allowed public APIs, retired/collapsed cohorts, limits and oracles
before this implementation. One optional Linux test target owns a two-column
GTK tree, 3138 chart children and a separate 32-child retirement root. All 3172
initial rows and 6344 cells are compared independently. The retirement root is
collapsed, recursively blanked and removed while its old cells remain held.
The chart then stays expanded or is collapsed before erasure.

## Executed evidence

The first native build fails because the new standalone source omitted cstdint;
the exact source and compiler output are preserved. Corrected strict builds pass.
The new prototype uses public GTK/ATK APIs, with no private structure access or
toolkit patch. It does not exercise SceneInspector, wire admission, installed
privacy, a desktop host or an edition.

Three strategies run in independent expanded/collapsed children. Local held
objects are inspected after erasure and fresh recovery through full text, name,
character count, three legacy word/layout slots and modern word granularity.
Every native callback includes its local checks in the recorded work duration.
Local-check fields are explicitly marked when measured; retire/quit defaults
are not observations of cache emptiness.

| Strategy/cohort | Native erase callback | Mutation within callback | Held local cells with text after erase |
| --- | --- | --- | --- |
| Blank, expanded | 849.161 ms | 847.641 ms | 64 |
| Blank, collapsed | 11.800 ms | 9.060 ms | 6340 |
| Detach, expanded | 272.545 ms | 268.817 ms | 6342 |
| Detach, collapsed | 10.814 ms | 8.106 ms | 6342 |
| Public scrub, expanded | 276.833 ms | 275.181 ms | 0 |
| Public scrub, collapsed | 23.389 ms | 21.190 ms | 0 |

The blank control demonstrates that traversing/blanking the current store is
insufficient for held cells that were collapsed or retired earlier. This is a
toolkit prototype observation, not an executed product privacy test. Plain
detachment continues to retain local data. Public scrub includes model detach,
store blank/clear, empty shared renderers, each held cell's public cache-update
slot with emit_signal false, empty-model reattachment and local inspection.
Its explicit ownership of every held cell does not supply a bounded product
registry or establish later scope/lifetime behaviour.

The first external collector stops when fresh interface lookup disappears.
The second holds each original Text interface; a later name property request
reports that its old object path no longer exists. Both failed sources remain.
An SDK default empty text response is not accepted as a successful remote read.

The final collector uses published AT-SPI D-Bus signatures and public object
references. Every method is checked before mutation. After erase and again after
fresh recovery it issues all seven methods against every original reference:
44,408 requests per phase, 88,816 per case. All return
org.freedesktop.DBus.Error.UnknownObject. There are zero successful empty-data
responses. The fresh active tree still exposes the exact two new rows, and all
six native processes exit normally. The strict original empty-success gate
therefore remains failed; withdrawal is recorded separately, without being
mapped to empty strings or blamed on an unavailable laboratory.

The lossless dictionary journals preserve every reference/method/reply/error
within 12 MiB per child. Exact error names, codes and normalized messages are
retained and independently checked for complete method/reference coverage.
No failed request or native time is excluded. Two component-graph checks and the
existing SCENE-INSPECTOR-MODEL suite pass; unrelated native product suites are
not claimed to have rerun.

## Preservation and next boundary

The source-bound [checkpoint](checkpoints/gtk-accessible-erasure.json) preserves
nine executions, four verified archives, all eighteen failed collection cases,
compiler failure, source/artifact/runtime identities and complete wire journals.
Raw data remain under ignored out/evidence. The preceding GTK history, lost-history,
authored timing and background-barrier failures remain unchanged.

Measure accessible-object retirement separately from cache refresh while keeping
both inside the original callback total. Close bounded complete per-cell scope,
registry and destruction ownership before a product cache change; investigate
public widget-unset/cache hooks without dropping native events or timing samples.
Resolve the held-reference contract explicitly against actual withdrawal before
eligibility; preserve the original failed oracle and never turn transport errors
or SDK defaults into successful empty reads.

Then repair and qualify real GTK history updates/erasure, separate maximum-policy
erasure, installed cadence, human accessibility and desktop/lifecycle composition.
W-11 and Windows 9x, Windows NT, X11, Wayland and Mac OS X complete editions remain
open. No public release or privileged operation is performed.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
