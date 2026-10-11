---
type: "SysPane Handoff"
title: "GTK cell lifetime repair and preserved performance boundaries"
description: "Clear actual retained cell caches before normal retirement, with exact withdrawal and source-bound regressions."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T23:46:25.312722+00:00"}
sp_id: "SP-GTK-CELL-LIFETIME-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-GTK-CELL-LIFETIME"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# GTK cell lifetime repair and preserved performance boundaries

Both real Linux inspector columns now use a public GTK text renderer/accessibility
subtype. Before GTK retires a cell on collapse, removal or destruction, its unset
hook clears the inherited text/count/derived-name and word/layout cache using the
public cache-update slot. It restores the shared renderer's exact text and forwards
the standard unset hook once. There is no application registry, duplicated row
cache, private toolkit field access or suppressed defunct/model event.

The [package](packages/w-11-gtk-cell-lifetime.md) closes ownership, limits, lifecycle
and wire semantics before implementation. The product integration follows the
passing standalone semantic gate. A public-read guard avoids recreating an already
verified empty cache after normal live model blanking; nonempty or uninitialized
caches still refresh. Existing rows, policy/scope, selection and renderer cadence
are unchanged.

## Executed evidence

The full standalone expanded/collapsed cohorts retain all 6344 cells from 3172
exact initial rows. Every retired/collapsed/erased native text, name, count and
implemented word value is empty, while live chart rows and exact fresh recovery
remain correct. The final callbacks include local inspection and mutation:

| Cohort | Retirement callback | Erase callback | Held native cells with old values |
| --- | --- | --- | --- |
| Collapsed | 309.696 ms | 10.625 ms | 0 |
| Expanded | 3.673 ms | 896.274 ms | 0 |

These are lifetime passes, not timing passes. The expanded erase and collapsed
retirement still exceed the original 100-ms GUI limit. Every duration remains
recorded; the semantic gate explicitly records performance_qualified false.

Each cohort performs all seven wire methods against all original references after
erase and again after fresh recovery: 88816 requests. Exact UnknownObject withdrawal
is retained separately from successful empty replies. It is accepted only for a
previously supported bus/path while the same root/application remains live, fresh
rows are exact, paths are not reused and the native process exits normally.
Timeout, generic errors and SDK defaults cannot pass. The preceding strict wire
empty-response experiment remains failed and unchanged; its full record is linked
from the new [checkpoint](checkpoints/gtk-cell-lifetime.json).

The real SceneInspector fixture feeds three complete chart packets through the
public receiver/delivery boundary. It holds eight original cells across collapse,
denial and fresh-scope regrant, then four fresh cells across close/destruction.
Both renderer columns use the actual subtype. Every native cell has exactly one
ordinary defunct transition and remains empty after widget destruction.

Preserve its first failure: the fixture required allocated empty data from the
optional modern native word slot. Pinned GTK does not implement that slot; pinned
ATK returns null with offsets -1/-1. The corrected test verifies absence before
retirement and records unsupported explicitly. Full text/name/count and all three
implemented legacy word slots remain mandatory; wire behavior is independently
checked. Primary definitions are
[GTK 3.24.41](https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtktextcellaccessible.c)
and [ATK 2.52.0](https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/atk/atktext.c).

The first integrated table run fails POLICY at 106.937 ms of GUI work; its observed
erasure is 169.490 ms. Preserve that source, every sample and the failed case.
After the empty-cache guard, all seven unchanged table cases pass. POLICY peaks at
92.613 ms of work and observed erasure at
135.398 ms, against the unchanged 100/200-ms limits. A later passing
run does not establish the earlier failure's complete cause or general history
qualification. The guard's first compile failure (missing initializer_list) is
also preserved with its exact source and compiler output.

Two component graph checks, five inspector/model/renderer/frame/background suites,
native table erasure, installed inspector and installed telemetry pass on the
final product source. Earlier passing runs are recorded separately from the final
candidate; no failure is dropped. Raw/source/runtime/artifact identities and every
verified archive are in the checkpoint. Generated data remain under ignored out/;
shared tooling stays in source/build and the retired root remains absent.

## Remaining release work

Maximum GTK history/GUI/erasure qualification remains open. Both current ordinary
maximum-history cases complete full content, overflow/recovery, single-point
denial/regrant and actual producer/renderer shutdown. Both fail the unchanged
100-ms GUI limit:

| Case | Maximum GUI work | Original timing samples | Result |
| --- | --- | --- | --- |
| Chart | 718.584 ms | 15973 | Failed |
| Mixed | 534.685 ms | 21073 | Failed |

The single-point policy stage does not qualify denial of a maximum history.
Retain prior maximum-history, authored timing, lost-history and background-barrier
failures. Attribute remaining presentation/retirement costs before choosing a
repair, without hiding original callback work or retained accessibility values.
Separate normal model/notification work, cache-update calls and retirement-hook
refreshes in a bounded native diagnostic that keeps the original callback clock.

Continue maximum-policy and installed accumulation, human accessibility,
desktop/lifecycle composition and full Windows 9x, Windows NT, Linux X11, Wayland
and Mac OS X editions. W-11 remains in progress; this repair completes neither
an entire native interface nor the 0.1.0 release. Privileged operations and public
publication retain their corresponding authority boundaries.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
