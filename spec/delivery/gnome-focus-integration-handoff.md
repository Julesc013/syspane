---
type: "SysPane Work Record"
title: "Optional GNOME focus integration checkpoint"
description: "Native event-bound focus restoration passes the original oracle and declared interaction guards while default behavior remains unchanged."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:07:41Z"}
sp_id: "SP-GNOME-FOCUS-INTEGRATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-FOCUS-INTEGRATION", "SP-GNOME-SHELL-RECOVERY-HANDOFF", "SP-GNOME-FOCUS-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Optional GNOME focus integration checkpoint

From `3ebc3cc3735a56ddfe3152bdf8150627e2e314f6`, an optional trusted GNOME X11
bridge controller passes the original native Show Desktop focus deadline and
actual F9 receipt. It remains disabled by default. The original failed baseline,
native MRU trace and unchanged default failure remain preserved.

## Native behavior and evidence

The [package](packages/w-05-gnome-focus-integration.md) bounds the controller to
one retained eligible normal window and the actual native Super+D event. The
public workspace-manager signal observes desktop-mode transitions. On an eligible
restoration, the controller calls the public window focus method once, synchronously,
before Mutter's existing default-focus selection. It does not replace a key
handler, patch Mutter/DING, activate/unminimize a window or run periodic repair.

| Observation | Observe control | Restore candidate |
|---|---|---|
| Original composition, marker and visible hide/restore | Pass | Pass |
| Original foreground focus deadline | Fail | Pass |
| F9 receipt before any repair click | Absent | Received |
| Explicit-click F10 positive control | Received | Received |
| All 15 native guard steps | Pass | Pass |
| Full native folder-input sequence | Pass | Pass |
| After one-way disable | Original failure returns | Original failure returns |

The fixed 2,400 ms reveal interval, 200 ms transition deadline and external
pixel/native-client oracle are unchanged. Later setup clicks, Alt+Tab actions and
the F10 positive control cannot repair that interval or satisfy F9 acceptance.
Both completed experiments return exit 0 because their expected results differ;
the original acceptance verdict remains explicit in each record.

The guards retain actual icon focus outside Show Desktop, ignore unrelated F8,
allow icon interaction during desktop mode and restore only on the second native
chord. Running the existing selection/clear/drag/menu/open/contents/close sequence
while desktop mode is active observes native folder activation ending that mode
without a key event. The controller abstains, tracks the new normal folder and
clears its lifetime when the folder closes. Actual folder contents, focus and
native ownership are independently verified.

Ordinary Alt+Tab restores the original foreground before the minimization case.
Explicitly minimizing it during desktop mode clears the retained target; the
later native restore leaves it minimized and does not focus it. A final one-way
disable removes callbacks: the decision trace stops, and native Show Desktop
again restores visible foreground pixels while leaving DING focused.

Each guard records marker/background/foreground pixels and native state every
50 ms for 400 ms. The original capture/gap limits apply, with at least three
settled observations after the transition allowance. Native PID/type bindings,
the complete raw journals, unchanged final settings and retained process cleanup
are checked independently of the controller's explanatory decision trace.

## Preserved failures and verification

The first two probes demonstrated the original focus difference but left guards
unexecuted, so they remain inconclusive. The first guard harness selected the
input report family, causing the foreground helper's owned-path check to reject
startup. The corrected family remains the existing candidate focus family.

The next harness incorrectly expected NormalState while Show Desktop hid the
window. Native Mutter reports IconicState there even without explicit minimization.
That failed attempt remains preserved. The corrected observation distinguishes
actual minimization through continued IconicState and hidden pixels after desktop
mode ends. It does not change the original reveal/focus oracle. A subsequent
complete pair is preserved separately from the final source-identical pair that
also records final binding/background settings.

An initial verifier addressed a nonexistent `type` field on the icon-owner record.
Its failure remains preserved. The verifier now checks each guard's native type
against the original independently observed icon client, while retaining exact
PID/resource/lifetime validation. No native acceptance failure is waived.

Forty-four verifier tests pass, including synchronized report/journal mutations
for false/stale focus, later-click substitution, foreign targets/PIDs/types,
wrong event/modifier/workspace, missing/late captures, stale/hidden pixels,
minimized-target restoration, folder misidentification, callbacks after disable,
changed settings and missing cleanup. Original focus, reveal, composition and
full native input verification are reused without a weaker substitute oracle.

Fresh shell recovery, DING recovery, application-list, input, wallpaper and default
reveal/composition/marker regressions add 215 checks: **259 desktop verifier checks
pass** in total. Default focus restoration remains failed, as required by its
unchanged control. Specification tooling is verified separately.

The final comparison is
`build-support/evidence/w-05-gnome-focus-integration-calibration.json`. Files with
that prefix preserve native reports, exact source archives, raw journals,
regression artifacts and all invocation/verification failures. Every native/test
launch uses a completed workspace preflight. Owned process groups finish without
surviving members; only private synthetic displays/settings/processes are used.

The [previous shell checkpoint](gnome-shell-recovery-handoff.md) links the native
recovery, application-list, input and wallpaper investigations. Fresh regressions
verify those paths with the optional controller absent. No C++ component,
supported profile, pinned native package or workspace allocation changed; previous
CTest and smoke-package evidence retains its original identity.

## Next admitted boundary

Before general enablement, close and execute bounded multi-window/modal,
workspace-change, lock/session and alternate reveal-trigger cases. Preserve
explicit user choice and native window lifetimes under each transition. Extend
the independent oracle; do not turn the candidate's own decision trace into proof
of correct focus.

Continue wallpaper policy, actual session-manager supervision, product
controller/renderer/collector continuity and the other native tracks independently.
This optional X11 candidate does not qualify Wayland, physical GPU presentation,
other GNOME versions or a complete desktop product. W-02, W-05 and the campaign
remain open; there is no release or general-enable authority in this checkpoint.
