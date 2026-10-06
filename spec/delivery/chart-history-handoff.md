---
type: "SysPane Work Record"
title: "Measured chart history checkpoint"
description: "Portable bounded sample retention with exact values, explicit discontinuities and fixed executable traces."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T23:04:14Z"}
sp_id: "SP-CHART-HISTORY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-CHART-HISTORY", "SP-SCENE-CONTENT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Measured chart history checkpoint

Source baseline: `b3d7bf22f696cc00e615a7686298ea63f952b29e`. Git history identifies
the resulting commit. The [package](packages/w-09-chart-history.md) closes the
sample-retention boundary of scene 0.3 charts. The shared scene library now owns
bounded measured windows, exact uint64/binary64 values, FIFO truncation, original
generation provenance and continuity flags. Null, failed, stale and retained
states cannot become fresh samples. New stream identities reset history; duplicate
measurements cannot resurrect expired points or heal a gap. Conflicting/reversed
measurements erase payload and latch until explicit clear.

The original interface, package and eleven test families were archived before
production implementation. The first real-wire case exposed an incomplete test
policy: DataView correctly refused attachment without accessibility permission.
The fixture now grants the required synthetic-test channels. Expectations of three
samples admitted before painting are unchanged. Subsequent review added cases
showing that an intervening pending selection cleared a conflict, and that stale,
retained or missing-current-clock input could conceal invalid chronology. Those
failures remain archived; fixes preserve the original acceptance conditions.

Final affected-component runs pass 65 Linux, 63 Windows GCC and 65 historical-toolset
host CTest entries. Each runs eleven chart families, all existing scene layout and
binding cases, and component dependency controls. Linux additionally runs the
existing scalar/table native component families. The historical profile runs its
PE/import and rejection controls on the modern Windows host. These are selected
regressions, not reruns of the entire product suite or historical OS qualification.

`build-support/evidence/w-09-chart-history-attempts.json` binds archived inputs,
actual commands, failures, final executable hashes and CTest logs. The separate
verification/staging records cover specification integrity, unchanged older
contracts and the exact committed source inputs. No older scene schema, fixture,
wire contract or native erasure oracle is weakened.

## Next boundary

Connect histories to SceneSurface with explicit history-channel authority,
aggregate budgets and erasure on every policy/resource/binding/lifetime change.
Resolve every admitted publication using complete relevant producer clock context;
ordinary repaint frequency must not define which samples survive. Close axis
normalization, device-resolution reduction, linear/step pixels, readable dimensions
and accessible status with independently fixed traces. Then verify actual native
chart pixels and erasure, including deliberate retained-pixel/name faults.

Chart drawing remains disabled until that integration passes. Image decoding,
complete accessibility, native settings/editing, installed ownership, desktop
recovery and all five release editions remain required. W-09 stays in progress;
unanswered historical/Mac lab and platform-floor questions remain recorded.
