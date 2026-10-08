---
type: "SysPane Work Record"
title: "Native GNOME icon-manager recovery checkpoint"
description: "Owned DING replacement preserves live composition and replacement-bound input while independent fault controls remain failed."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:21:25Z"}
sp_id: "SP-GNOME-ICON-RECOVERY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-ICON-RECOVERY", "SP-GNOME-SWITCHER-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GNOME icon-manager recovery checkpoint

From `0b14bb0a0674ae05ed800c85c0bb794e14df04d3`, the owned GNOME/DING experiment
now confirms icon-manager exit, native replacement, continuing live drawing and
usable icons afterward. The original shell, bridge, Xvfb and private buses remain
alive. This closes the named DING recovery boundary; shell/compositor replacement,
product renderer/collector continuity and the Show Desktop focus failure remain open.

## Actual native results

The [package](packages/w-05-gnome-icon-recovery.md) fixes ownership, deadlines,
pixel witnesses, negative controls and dependent input before native execution.

| Control | Native replacement | Marker progress | Restored icons | Input afterward |
|---|---|---|---|---|
| Live | Pass | Generations 4/5/6 pass | Pass | Full sequence passes |
| Frozen surface | Pass | Generation 4 remains; deadline fails | Pass | Unexecuted |
| Omitted stop | Fails; original remains alive | Generations 4/5 pass | Original icons remain | Unexecuted |

All three final cases share identical sources/runtime and the unchanged live
composition prerequisite. XRes binds the original desktop to its owned process,
script, executable, group/session and start time. A held pidfd receives the exact
stop signal and independently proves exit. The pinned DING supervisor launches
its own replacement; neither DING nor Mutter is patched and the harness does not
launch a replacement itself.

Both actual replacement cases reuse the original window ID. The live run changes
from PID 524 to PID 605; the frozen control changes from PID 821 to PID 907.
Native process/resource binding and start time, backed by held handles, distinguish
these lifetimes. A window ID alone would have missed the replacement. Readiness is
observed 151,532 and 145,515 microseconds after the respective stop requests.

External frames preserve the icon outage rather than replacing it with a later
successful image. The first sampled absence occurs at 302,023 microseconds in the
live trace and 300,376 in the frozen trace. These are sampled observations, not
exact outage durations. After the declared recovery settling interval, every
required frame matches the original opaque-icon and transparent-overlap witnesses.
Background pixels and native settings remain unchanged throughout. Coverage gaps
stay at or below 52,739 microseconds and paired captures at or below 3,703,
within the unchanged 150 ms and 50 ms budgets.

Successful live recovery then executes the existing full input sequence against
the new DING identity: selection, clear, drag selection, menu/dismissal, actual
folder contents/open/close, restored clear selection and final live composition.
Fresh clipboard replies and private accessibility observations bind to the new
process. The original process cannot satisfy these observations.

## Preserved investigation and verification

The first no-stop fixture supplied only generation 4. The existing temporal oracle
rejected it because it requires at least two stimuli. That inconclusive attempt
and its exact sources remain preserved. The corrected control supplies a real
generation-5 liveness stimulus at 500 ms; the oracle is unchanged. An earlier live
attempt and preliminary matrix remain separate from the final three controls.

Thirty-six new verifier checks pass. They include consistent report/journal
mutations that reject false exit or readiness, old-process reuse, foreign native
ownership, shell/replacement death, missing paired samples, wrong timing, altered
pixels/settings, input from the original owner and falsely completed dependent
work. Ordinary composition still requires its icon manager to survive to cleanup;
only this recovery family accepts independently proven old-process exit.

Fresh native application-list, input, wallpaper and default reveal/composition/
marker regressions supply 134 existing verifier checks, for **170 checks** in this
checkpoint. The original live Show Desktop case still fails foreground-focus
restoration. Verification confirms that failure; it does not waive it.

The final comparison is `out/evidence/w-05-gnome-icon-recovery-calibration.json`.
Files with the same prefix preserve 22 native attempts and exact source archives,
raw journals, regression PNG artifacts and invocation/verification records.
Completed workspace preflights precede each run, and owned process groups finish
with no surviving members.

The bridge adds a private one-way freeze method only for the explicit recovery
fault control. Existing default paths retain regression evidence. No C++ component,
supported target profile, runtime package lock or workspace allocation changes;
previous CTest/smoke evidence retains its original identity.

## Remaining work

Close and execute the bounded shell/compositor replacement contract, including
bridge reattachment and independent post-recovery input. Resolve the native DING
MRU-focus restoration failure separately. Wallpaper policy, other image/display
profiles, Wayland/GPU presentation and other native platform tracks still require
evidence. W-02, W-05 and the full campaign remain open; no complete desktop profile
or release is qualified.
