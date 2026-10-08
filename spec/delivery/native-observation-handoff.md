---
type: "SysPane Work Record"
title: "Native observation checkpoint"
description: "Explicit native evidence distinguishes unavailable observations from absent content or state."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T09:30:22.966768+00:00"}
sp_id: "SP-NATIVE-OBSERVATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-NATIVE-OBSERVATION", "SP-WIDGET-CREATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native observation checkpoint

Source baseline: `066657a89472b0476e3d30a1a1d51a944c88789b`. The
[package](packages/w-10-native-observation.md) investigates the preceding native
focus/interface failures. Production source, binary and existing expected scenes
are unchanged. W-10 and all five complete desktop editions remain in progress.

## Findings and correction

Two bounded diagnostic matrices compare convenience APIs, explicit D-Bus replies
and X11 input focus with ordinary/large editors, 50/350-ms stops and terminated
owned children. The first probe used an initially empty field and its cleanup
resumed a timed-out call early. The corrected probe reads `Editable pane` and
records the full stop interval. Both attempts and their exact scripts are preserved.

After child exit, the old text helper reports empty text for that nonempty field;
explicit queries report ServiceUnknown. During the 350-ms stop, explicit calls
time out at approximately 200 ms while X focus stays with the editor. Convenience
API calls return successfully after approximately 350–360 ms despite their nominal
200-ms setting. The reason for that duration is not established. Neither experiment
reproduces the earlier intermittent live focus/interface failure; its cause remains
unproven. An unchanged successful matrix does not explain a historical failure.

The installed 2.52.0 upstream [state API source](https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/atspi/atspi-accessible.c)
contains error-suppressing state/interface paths. This explains why those APIs alone
cannot distinguish unavailable observations from absent state; it does not prove
the historical failure's cause. Pinned runtime identities and source hashes accompany
the records. The [wire interfaces](https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/xml/Accessible.xml)
provide explicit replies/errors for the observer boundary.

The editor harness now reads text, state, interfaces, geometry and selection through
error-reporting native calls. Only addresses are cached. Successful negative checks
require explicit replies. Removed-object erasure requires UnknownObject plus a fresh
accessible live owner; ServiceUnknown, denial, timeout and local DEFUNCT fallbacks
cannot prove it. A selection replaced between count/child/text reads is unavailable,
not empty. This race was exposed by the first stricter binding matrix, whose failure
and source snapshot remain preserved.

Read-only retries stay within the existing overall deadline. Each explicit call is
capped at 200 ms and the remaining wait budget; late replies cannot satisfy a wait.
The 200-ms disclosure deadline, held-key focus assertion, mutation count, exact
scene/storage/pixel outcomes and original fault controls remain fixed. No mutation
is retried and no held-focus assertion reactivates the control. Focus failures record
X11 ownership, accessible identity and explicit query outcomes.

## Executed evidence

Seven native calibrations pass: live, genuinely unfocused, 50-ms stop, 350-ms frozen
owner, dead owner, explicitly removed object and a separate denied D-Bus service.
The denial service calibrates protocol error handling; it is not a product policy
qualification. Nonempty retained text cannot pass erasure, and a frozen/disconnected
owner cannot provide a focus or empty-text witness.

The unchanged native matrices pass: creation 17, binding 15, content 15, snap 13,
group 11, arrangement 14, editor 20 and large-command 24. Together with calibration,
this checkpoint has 136 native cases in nine CTest families. Product binaries are
identical to the previous checkpoint; no new Windows or historical execution claim
is made. Schema/fixture, specification-tool and integrity results are recorded
separately from native evidence.

Records: `out/evidence/w-10-native-observation-attempts.json`,
`out/evidence/w-10-native-observation-native-index.json`,
`out/evidence/w-10-native-observation-verification.json`,
`out/evidence/w-10-native-observation-staging.json` and
`out/evidence/native-observation-handoff.json`. Source archives retain
each original attempt and frozen product/calibration inputs. Twenty duplicate native
folders (246,621,430 bytes) were removed only after matching their already committed
creation-checkpoint archives. The existing 7 GiB output budget remains in force.

## Next boundary

Close responsive/flow transforms and remaining property controls, then installed
controller/catalog/policy ownership and scene-aligned entry/restoration with independent
escape. Preserve the new snapshots if focus failures recur; do not claim their cause
has been repaired. Complete accessibility, performance, other native adapters,
historical laboratories, packaging and release gates remain open. Owned ext4/Xvfb/
D-Bus tests do not qualify an installed desktop or physical power-loss durability.
Continue Windows 9x, Windows NT, X11, Wayland and Mac OS X independently.
