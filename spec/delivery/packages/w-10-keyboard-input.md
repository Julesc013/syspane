---
type: "SysPane Work Package"
title: "Native keyboard input completion"
description: "Acknowledge navigation before requesting a different focus target."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T10:52:14.897725+00:00"}
sp_id: "SP-W10-KEYBOARD-INPUT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-NATIVE-OBSERVATION", "SP-W10-LAYOUT-AUTHORING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native keyboard input completion

Continue W-10 from the recorded layout-button focus failure. Keep production,
authored scenes, acceptance outcomes, request ownership and resource/erasure
limits unchanged. This package corrects the independent laboratory's input
completion observation; it does not weaken a required focused-state assertion.

## Evidence and decision

The bounded experiment compares the preserved keyboard oracle on the same binary.
Detailed snapshots on every focus call yield three inconclusive passes. Minimal
instrumentation reproduces the failure three times. A paired experiment repeats
the same End/Home/Down sequence with and without per-key selection observations.
All three batched runs fail; all three ordered runs focus and activate Layout.

End selects the group that is also the final target. Observing that title once
does not prove that the following queued Home/Down events have completed. The
failed runs retain X11 focus in the active editor, report actual focus on the
object list/Image row, and do not open Layout on Space. Preserve these traces;
do not attribute this failure to a missing accessibility reply or change GTK
production behavior without further evidence.

## Admitted correction

The layout oracle must observe the expected native selected row and title after
each navigation key before sending the next key or requesting another focus
target. Use a single three-second deadline for the complete selection operation,
including focus acquisition and all reads. Read-only retries remain subject to
the existing explicit-error rules. Never retry an input mutation or force focus
during a held-focus assertion. A transient intermediate match cannot complete
the full sequence.

Record bounded per-key expected and observed row/title evidence. The fixed fixture
owns its expected row order; this is not a product requirement that titles be
unique. Native dialog entry still requires showing controls and disabled parent
mutation paths; closing still requires editor re-enablement. Restore explicit
focus plus Space activation for layout-suite buttons. Keep native combo activation,
exact scene/pixel/storage comparisons, fault controls and the 200-ms erasure bound.

## Verification and handoff

Freeze this package, the unchanged layout/observation fixtures and shared observer
before correction. Run all 21 layout cases, seven observer calibrations and the
existing creation, binding, content, snap, group, arrangement, editor and large-
command matrices with normal workspace preflight and CTest commands. Preserve
source, script, executable and environment identities and every diagnostic result.
Verify production and existing contract/fixture bytes against the starting commit;
unchanged portable build/test evidence remains source-bound to that commit.

Record the specific input-ordering cause and remaining boundaries in the existing
work graph, current-state page, README, TODO and developer guidance. Earlier
unrelated component/interface/focus failures remain unresolved unless their own
evidence establishes the same cause. Complete accessibility, installed integration,
flow/container group transformations and all five native editions remain required.
