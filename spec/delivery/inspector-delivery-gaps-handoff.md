---
type: "SysPane Handoff"
title: "Inspector chart continuity after skipped delivery"
description: "Preserve a reproduced false chart join and verify explicit gaps across coalesced complete frames."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T05:33:19.872295+00:00"}
sp_id: "SP-INSPECTOR-DELIVERY-GAPS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-INSPECTOR-DELIVERY-GAPS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector chart continuity after skipped delivery

The native receiver's latest-complete-state slot can replace an undelivered
snapshot. The inspector now forwards that known loss to chart history before
admitting the next complete state. A receiver-local ordinal distinguishes loss
from an ordinary snapshot-generation jump. Duplicates do not advance it; zero
is invalid and overflow fails closed. Existing wire versions, policy checks,
lease deadlines, measurement clocks and bounded retention remain unchanged.

The [checkpoint](checkpoints/inspector-delivery-gaps.json) binds commands, source
snapshots, binaries, environments, raw archive identities and the preserved
failures. Raw recordings remain in ignored local `out/evidence/` archives.
The [package](packages/w-11-inspector-delivery-gaps.md) defines the admission and
gap rules; it supplements the existing receiver and chart contracts.

## Reproduced failure and fixture correction

The baseline displayed point 100, replaced undelivered point 200 with point 300,
then exposed `30 byte; generation 3; join`. The fixed oracle required `start`.
The native failure is preserved in the baseline archive, including the exact
chart stderr and the source/fixture bytes used for that run.

The first repair passed contiguous generation jumps, coalesced success, hidden
failure and duplicate wire cases. A later new stimulus attempted measurements
100, 200, then 100, which correctly failed the existing model's measurement
high-water check before chart admission. Preserve this separate fixture failure.
Only that skipped publication was corrected to a failed acquisition retaining
measurement/value 100/10. All expected point rows and pending-break assertions
remain byte-equivalent as parsed data. The final seven scenarios pass, including
a duplicate measurement that cannot heal a break and first-latest attachment
that invents no earlier history.

## Executed checks

- Seven controlled native GTK chart-delivery scenarios, plus the original seven
  SCENE-INSPECTOR modes and its model test. The original independent AT-SPI,
  keyboard, summary, retained-reference and deliberately incorrect observer
  controls pass.
- Seven installed real-telemetry cases, eleven native network-consumer cases,
  three chart-erasure cases and the native scene-chart component check pass.
- All 111 selected receiver, data, measured-time, telemetry, scene and component
  checks pass on each of Linux GCC 13, Windows GCC 15 and Windows v141_xp.
  Both historical PE import/rejection checks pass. This is development-profile
  evidence, not execution on an XP guest or qualification of a Windows edition.

The new chart scenarios use controlled synthetic publications through the real
receiver, SceneSurface and GTK model. They do not qualify maximum-size workloads,
native acquisition of those synthetic samples, human accessibility or desktop
visibility. The separate installed cases still use actual native counters.

## Specification checks and test-environment correction

All 51 schemas and 183 fixtures validate. The 62 tooling tests finish with 60
passes and the two existing Windows symlink-privilege skips. The initial tooling
attempt failed its no-Git fixture assertion because the owned temporary root was
inside this checkout and Git discovered the parent HEAD. Preserve that failure.
The rerun sets `GIT_CEILING_DIRECTORIES` to the same temporary root; it changes no
tool implementation or expectation. Temporary files remain inside ignored `out/`.
The checkpoint records the exact environment, commands and both attempts.

## Next admitted work

Continue W-11 with maximum live table/chart semantic trees and updates. Account
for per-table row/cell limits, chart history bounds, frame bytes, native rows,
construction pixels and GUI timing together. Preserve explicit refusal and
independent expected outputs. Human accessibility, long-text usability, physical
hotplug, other native adapters and desktop/lifecycle composition remain open.
All five complete 0.1.0 editions and release gates remain required and unfinished.
