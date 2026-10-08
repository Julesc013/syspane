---
type: "SysPane Implementation Handoff"
title: "Contemporary Windows host observation checkpoint"
description: "Read-only Explorer ownership and icon hierarchy, with native host execution still dependent on a designated laboratory."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:45:00Z"}
sp_id: "SP-WINDOWS-HOST-INVENTORY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W03-PACKAGE", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Contemporary Windows host observation checkpoint

W-03 now has a bounded read-only native observer and a
[closed observation package](packages/w-03-windows-investigation.md). This begins
the Windows investigation without making the active desktop a capture/recovery lab.
The observer cannot attach a surface, send input, change wallpaper or stop Explorer.

The final run from `a9015c02a60b89e77e24eb25a8e0d3f755e15c61` observed Windows
10 build 19045, WinSta0/Default and a held native Explorer process. The exact system
Explorer image digest and creation FILETIME are recorded. Two bounded observations
100 ms apart found the same 14 top-level shell roots: one Progman and 13 WorkerW
windows. One WorkerW owns the single SHELLDLL_DefView → SysListView32 icon chain.
Many windows share the WorkerW class; selecting the first class match would not
identify the required desktop host. No observed class or parent relationship proves
visible stacking, transparency, input pass-through or Show Desktop behavior.

**Fourteen decision tests passed.** Literal fixtures cover absent shell, inaccessible
owner, unexpected image, foreign session/child, exited owner, changed shell/parent,
duplicate hierarchy/handle, missing icons and disconnected parent chain. The native
child exited normally, and the parent independently recomputed its decision. Output
contains no window titles, icon labels, user files or pixel capture.

Evidence uses `out/evidence/w-03-windows-inventory-`. Both native attempts,
execution/preflight records and source snapshots remain. The first run also passed;
the final source avoids resolving an arbitrary custom shell image path and corrects
the package authoring timestamp. Neither attempt is desktop-host acceptance. The
machine handoff is `out/evidence/windows-host-inventory-handoff.json`.

## Required continuation

The registered Hyper-V Windows 10 VM was still powered off on the read-only check.
Its designation as a disposable/synthetic test laboratory is pending clarification;
registration alone does not authorize capturing its contents or prove usability.
XP/7 guest scope remains unresolved, and no macOS endpoint has been admitted.

After the Windows lab is designated, establish exact guest identity and independent
recovery, then close transfer/launch/capture/cleanup before the bounded WorkerW
candidate. Its attachment must validate HWND lifetimes with native events; two equal
polls do not rule out handle reuse. Reuse the existing fixed marker/time oracle for
actual composition, Win+D/reveal, icon input, wallpaper and shell replacement.
Preserve failed candidates and do not substitute structural observations for pixels.

The [campaign coverage audit](campaign-coverage.md) records the remaining boundaries.
W-03 and the campaign remain incomplete. Existing compiled suites and smoke packages
retain their earlier identities because this change adds no product target or C++
code. All existing requirements, including a complete editable desktop edition,
remain in the work graph.
