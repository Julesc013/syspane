---
type: "SysPane Work Record"
title: "Native GNOME application-list checkpoint"
description: "The passive bridge stays out of Alt+Tab and the overview dash, with actual normal-window and omitted-popup controls."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:00:03Z"}
sp_id: "SP-GNOME-SWITCHER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-SWITCHER", "SP-GNOME-WALLPAPER-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GNOME application-list checkpoint

From `b761ee6b7ba79642164f1d11972c6a7b24bb1a10`, the passive bridge stays out
of the owned GNOME/DING Alt+Tab application switcher and overview running-app dash.
Two identifiable normal applications remain visible and usable in both lists.
The known Show Desktop focus-restoration failure remains open; ordinary application
switching and overview dismissal do not waive that separate acceptance condition.

## Actual native results

The [package](packages/w-05-gnome-switcher.md) defines the native observations,
controls, ownership, resource bounds and completion conditions. The exact profile
has an overview dash rather than a permanently visible conventional taskbar. Its
private favorites are empty; the built-in Show Apps control is not an application.

| Control | Alt+Tab applications | Overview dash applications | Required absence | Focus and final desktop |
|---|---|---|---|---|
| Passive live bridge | Alpha, Beta | Alpha, Beta | Pass in both lists | Pass |
| Added normal-window fault | Alpha, Beta, SysPane Surface Fault | Alpha, Beta, SysPane Surface Fault | Fail in both lists as required | Pass |
| Omitted first Alt+Tab chord | Popup absent | Unexecuted | Fail; a missing list cannot pass | Alpha remains focused; final interval unexecuted |

All three final cases use identical source/runtime inputs and begin with the
unchanged live composition prerequisite. XRes binds each actual normal window to
its retained fixture process, exact script arguments, native geometry and lifetime.
Read-only AT-SPI observations bind the shell's unique private-bus peer to the held
shell PID. Native XTEST input opens and dismisses the UI; no accessibility action
or candidate-reported application list supplies the result.

The observer enumerates every native item in the identified list, without filtering
to expected names. Complete visible subtree traversal, native roles/ancestry and
child counts prevent an omitted or hidden item from becoming a successful absence
claim. Exact 8x8 pixel witnesses inside independently observed icon rectangles
confirm each fixture's rendered icon. The negative normal window is a real third
application with its own desktop identity and pixels, not a fabricated report entry.

After canceling the popup, Alpha remains active. Complete Alt+Tab chords select
Beta then Alpha, with independent active-client and client-pixel observations.
Opening and dismissing the overview restores Alpha. The subsequent 2,400 ms
three-generation marker interval preserves icon/rectangle pixels, background and
Alpha focus. Native popup/overview occlusion is outside that ordinary-desktop
interval and is not claimed as uninterrupted desktop visibility.

The largest final observed shell tree contains 173 nodes. The longest accepted UI
transition is 424,003 microseconds, below its three-second deadline. Final desktop
coverage gaps stay at or below 52,691 microseconds and paired observations at or
below 3,344 microseconds, within the unchanged 150 ms and 50 ms budgets.

## Preserved investigation and verification

The first native tree traversal hit its 512-node bound while visiting hidden shell
internals. That failed attempt and source archive remain unchanged. The observer
now records child counts and explicit pruning of non-showing subtrees, while
requiring every visible subtree to be complete. The next observation gathered real
shell names, roles, ancestry and icon rectangles and was explicitly inconclusive
pending calibration. It did not claim qualification.

An earlier complete matrix also remains separate from the final matrix. The final
contract records the pinned shell list structures and the omitted-popup control's
bounded observation of continued Alpha focus; later dependent steps stay unrun.
No native application-list implementation or bridge behavior was patched to pass.

Thirty-four new verifier checks pass, including semantic mutations with consistent
report/journal copies. They reject foreign peers or processes, missing/duplicate
tree nodes, pruning of visible children, false names or pixels, unlisted normal
clients, wrong focus, late transitions, stimuli outside their declared actions,
missing final composition and incorrect negative-control claims.

The input, wallpaper and default reveal/composition/marker paths retain separate
native regression evidence: 100 existing verifier checks pass, giving **134 checks
in this checkpoint**. The native live reveal case still fails foreground-focus
restoration. Validation confirms that failure; it does not turn it into a pass.

The final comparison is `out/evidence/w-05-gnome-switcher-calibration.json`.
Files with the same prefix preserve 20 native attempts and exact source archives,
37 raw journals, 12 PNG regression artifacts, execution records and two reviewer
images decoded from the live native captures. Completed workspace preflights precede every run;
owned process groups finish with no surviving members.

No C++ implementation, supported target profile, runtime package lock, workspace
allocation or shell-bridge implementation changed. Previous CTest/smoke evidence
retains its original identity. This closes only the named Alt+Tab and overview dash
experiment. Other taskbars/shells, Wayland/GPU presentation and complete product
qualification remain open.

## Remaining work

Continue shell/icon-manager recovery and post-recovery input under a bounded native
contract. Resolve the independently observed DING MRU-focus restoration failure
separately. Wallpaper policy, other image/display profiles and the other native
platform tracks still require evidence. W-02, W-05 and the full campaign remain open.
