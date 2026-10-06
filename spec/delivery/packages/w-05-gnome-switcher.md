---
type: "SysPane Work Package"
title: "W-05 native GNOME application-list absence"
description: "Observe actual Alt+Tab and overview dash entries independently of candidate-reported window hints."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:47:30Z"}
sp_id: "SP-W05-GNOME-SWITCHER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-DESKTOP", "SP-ORACLE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native GNOME application-list absence

Use only the pinned owned GNOME/DING X11 laboratory. This named shell has an
overview dash rather than a permanently visible conventional taskbar. Qualify its
native Alt+Tab application switcher and running-application dash separately; no
other shell/taskbar is implied. Preserve the existing Show Desktop focus failure.

## Fixture and ownership

The fixed fixture defines two normal GTK applications, Alpha and Beta, distinct
desktop-file/WM_CLASS identities, exact titles, colors, icons and nonoverlapping
geometry outside the original marker/icon/background witnesses. Clear only the
private shell favorites. Register the fixture desktop files and icons before shell
startup. Do not change native eligibility flags or patch native application lists.

Require the existing live solid-color composition prerequisite. Bind each fixture
window through XRes to its retained process, executable, script arguments, group,
session and start time; retain pidfds through observations. The passive candidate
must add no normal application window. The private AT-SPI registry is explicitly
launched, and shell tree observations must bind its unique bus peer to the held
shell PID. No accessibility action drives the UI. Native XTEST keys/clicks supply
all input. Do not read a user session, clipboard or application list.

## Native sequence and independent expectations

Click Beta then Alpha and establish Alpha's native focus and exact client pixels.
Press Alt+Tab, retaining Alt while observing the actual popup. Both fixture
application entries must be showing, and no other ordinary application entry may
be present. Their independently observed names and rendered fixture-icon colors
must agree. Cancel with Escape, release Alt, and require Alpha to remain active.
Perform complete Alt+Tab chords to select Beta and then Alpha, observing native
active-client identity and exact foreground pixels after each transition.

Open the overview through native Super. The running-application dash must contain
both fixture applications and no additional application entry. Favorites are empty;
the built-in Show Apps control is not an application. Observe shell accessibility
roles/ancestry/states, bounded screen rectangles and external root pixels. Close
with Escape and require Alpha focus to return. This is an overview-dismissal test,
not a substitute for the separately failed Show Desktop test.

Each UI transition has a three-second observation deadline. A tree is bounded to
512 nodes, depth 24, 64 children per node, 256 characters per name and three seconds;
each private-bus call has a 250 ms limit and forbids service auto-start. Preserve
full observed trees and pixels, including failed observations. Missing or ambiguous
native accessibility is a failed laboratory prerequisite, never evidence of absence.
The normal controls must appear; an empty list cannot pass.
Record each visited node's child count. Exclude descendants of non-showing native
subtrees from the visible-list traversal, recording that pruning explicitly; always
traverse the application root. Every showing subtree must be complete. Hidden
overview/application-grid internals do not consume an unbounded visible-tree budget.

On the pinned shell, locate Alt+Tab's list from Alpha's showing label and its unique
push-button ancestor, then enumerate every sibling button and its single showing
label. Locate the overview's running-app container beside its native Show Apps
toggle, beneath the showing Overview panel; enumerate every direct application item.
Do not filter these lists down to expected names. Require exactly Alpha and Beta
for a live pass. The extra normal-window control must produce exactly those two
plus SysPane Surface Fault. For every item, locate its smallest square descendant
icon (16–128 pixels) and require the centered 8x8 external pixels to equal the
fixture's exact icon color. No name-only, metadata-only or partial-tree pass is valid.
Record all child counts/paths and reject missing, duplicate, orphaned or reordered
visible children. Shell peer identity and observed roles are part of the evidence.

After dismissing shell UI, run the original 2,400 ms three-generation marker trace
with paired icon/rectangle pixels and active-client observations. Require live
composition, unchanged background and continued Alpha focus throughout that final
interval. Existing 50 ms observation, 150 ms coverage and 200 ms generation budgets
remain unchanged. Native popup/overview occlusion is not asserted to be ordinary
desktop visibility.

## Calibrated failures and completion

`--switcher live|ordinary-window|no-switcher` owns the composition prerequisite and
excludes the other optional experiment flags. The ordinary-window control adds a
third actual normal GTK application named SysPane Surface Fault with its own
fixture icon, visible window and desktop identity. Its entry must be detected in
both native application lists, while the live desktop composition still passes.
It is a deliberate unwanted-entry control, not an alternative desktop host.

The no-switcher control omits the first Alt+Tab chord only. Require observation to
reject the missing popup despite both normal controls being available and the
composition prerequisite passing. Later dependent steps remain explicitly unrun.
Observe the continued focused Alpha window and absence of the popup within the
same transition deadline; this is an expected failure of the required visible-list
condition, not a successful absence qualification.
Do not manufacture a passed absence verdict from a hidden or unavailable list.

Record exact source/runtime/fixture identities, native windows and held processes,
private launcher bytes, complete stimulus/observation journals, actual verdicts,
partial failures and cleanup. Bound the new journal to 8 MiB/180 records and the
whole attempt to the existing 40-second observer lifetime. Recompute outcomes from
native records; metadata flags or candidate assertions alone cannot qualify either
list. Preserve preliminary failures and original test expectations when correcting
laboratory defects. Full desktop, recovery, other shell profiles and GPU/Wayland
qualification remain separate gates.
