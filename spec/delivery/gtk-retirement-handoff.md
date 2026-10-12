---
type: "SysPane Handoff"
title: "Measured GTK retirement and complete projection cleanup"
description: "Preserve native cache/lifecycle evidence and retire complete projections through the same owned model."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T00:42:57.936123+00:00"}
sp_id: "SP-GTK-RETIREMENT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-GTK-CELL-LIFETIME"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Measured GTK retirement and complete projection cleanup

The product retires complete native inspector projections by detaching the tree
model, clearing the owned store and reattaching that same empty store. The existing
text-cell unset hook physically clears held text/name/count/layout before normal
defunct events. Tree/root/columns/renderers/store ownership and partial updates
remain stable. A separate row-cleanup method preserves current adopted results,
status, tickets and renderer acknowledgement when a qualified projection is empty;
explicit clear/shutdown still resets admission and adopted input.

The [package](packages/w-11-gtk-cell-lifetime.md) closes the experiment and this
product boundary before implementation. Detachment was admitted only after complete
held-native/wire/lifecycle gates. It cannot replace actual cache erasure. No
production profiling, copied row registry, private toolkit access or notification
batching is introduced. This is measured progress toward the original performance
requirement; no limit, acceptance oracle or failure is discarded.

## Native experiment

All candidates use the same exact 3172 initial rows and 6344 held cells, expanded/
collapsed cohorts, retired root, fresh values and seven wire methods. A test-owned
public cache-update wrapper forwards the original slot once and records inclusive
counts/times, signal/quiet calls and nesting inside each original callback clock.
Active cache calls reach depth one, so these recorded slot durations have no
nested double count. Private class fields and foreign processes are untouched.
The original slot is restored after owned cell/widget teardown.

Every original cell has exactly one normal defunct transition at its retirement;
active chart cells remain live and exact. Held native data remain empty after
erase and fresh recovery. Each case records 88816 raw old-reference wire requests
with complete method/reference coverage, distinct verified withdrawal, exact fresh
rows, no old-path reuse and normal native exit. All eight semantic cases pass.
These are not GUI or full-product qualification passes.

| Expanded candidate | Complete erase callback | Public cache slot time | Signal / quiet calls | Renderer text notifications |
| --- | --- | --- | --- | --- |
| lifetime-detach | 308.786 ms | 34.495 ms | 0 / 6278 | not recorded |
| lifetime-profile | 828.374 ms | 283.529 ms | 6278 / 0 | not recorded |
| lifetime-remove | 526.127 ms | 38.852 ms | 0 / 6278 | not recorded |
| lifetime-bulk | 486.891 ms | 35.452 ms | 0 / 6278 | 2 |

The baseline blank/clear path has 6278 signaled cache calls; direct remove/detach
has 6278 quiet calls. Quiet slot durations explain only about 33–39 ms of callbacks
that remain hundreds of milliseconds long. Collapsed retirement also remains
slow. Do not label the rest as proven Pango, property notification or event cost.

The separate batching candidate freezes/thaws property notifications only on the
two owned shared renderers, retaining all native defunct/model/visible events and
full clocks. It coalesces text notifications while expanded removal still takes
486.891 ms and collapsed retirement 322.404 ms. This does not establish the earlier
notification hypothesis or enter the product. The private prototype process ends
with its normal events and no persistent machine change.

Pinned GTK distinguishes per-child removal events from model replacement/cache
retirement; the selected product path uses its public model operation and retains
the toolkit's normal lifecycle behavior. The source definitions are
[GTK tree accessibility](https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtktreeviewaccessible.c)
and [GTK text-cell cache](https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtktextcellaccessible.c).
These definitions support method/lifetime interpretation; measured source-bound
results, not source inspection alone, govern qualification.

## Actual product checks

Strict native builds pass. Preserve the first instrumentation compile failure,
which is a misleading-indentation warning promoted to an error, and its exact
source/log. Two graph checks, actual inspector cell lifetime, five model/renderer/
frame/background suites, table erasure, installed inspector and installed telemetry
pass on the final product source. All seven unchanged live-table cases pass.

The ordinary maximum family retains its original cases, sample clocks, content,
recovery, owner exit, 100-ms GUI/200-ms erasure limits and native deadlines:

| Case | Maximum GUI work | Original samples | Actual outcome |
| --- | --- | --- | --- |
| Chart | 296.85 ms | 15955 | fail |
| Mixed | 315.191 ms | 21256 | fail |

Inspect complete observations and original violations in the source-bound
[checkpoint](checkpoints/gtk-retirement.json). Preserve preceding 718.584/534.685-ms
history failures, slow lifetime callbacks, strict wire-empty failures, original
lost-history/background-barrier and policy/fixture failures. Raw archives remain
under ignored out/. Previous source statements remain historical facts.

## Next required boundary

Complete remaining native retirement/event attribution and qualification without
suppressing normal accessibility events or treating hidden data as erased caches.
Maximum-policy/history, installed accumulation, human accessibility and independent
desktop/lifecycle composition remain required. A one-point denial/regrant stage
does not qualify denial of a full history. Continue all five complete Windows 9x,
Windows NT, Linux X11, Wayland and Mac OS X editions and their release gates.
W-11 remains in progress. Public publication and privileged operations retain
their corresponding authority boundaries; AIDE stays optional and inactive.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
