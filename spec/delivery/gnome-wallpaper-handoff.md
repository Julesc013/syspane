---
type: "SysPane Work Record"
title: "Native GNOME image-wallpaper checkpoint"
description: "Original image identity, native configuration and independent pixels pass with separately calibrated faults."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:40:44Z"}
sp_id: "SP-GNOME-WALLPAPER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-WALLPAPER", "SP-GNOME-INPUT-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GNOME image-wallpaper checkpoint

From `de1539ae8d75ab4d8fc076357f6b57c8fa605df2`, the passive drawing bridge
preserves the named image wallpaper on the owned GNOME/DING laboratory. Independent
observations agree on the original file identity, complete native background
configuration and exact image pixels. The existing Show Desktop foreground-focus
failure remains open. No complete desktop profile is qualified.

## Actual native results

The [package](packages/w-05-gnome-wallpaper.md) fixes the image, observations,
failure controls, deadlines and resource bounds. It first requires the unchanged
solid-color composition prerequisite. With candidate actors hidden, the actual
native loader then presents a fixed 800x600 PNG at 1:1 scale. Three stable baseline
frames preserve the calibrated icon anchors and expose the expected image through
the clean overlap pixels. Two unobstructed image regions match the fixture exactly.

The final four runs share identical source/runtime inputs. Each observes 48 paired
samples during the original 2,400 ms changing-marker interval. The maximum coverage
gap is 51,234 microseconds, below 150 ms; the maximum combined observation duration
is 11,978 microseconds, below 50 ms. Native fault calls complete within 7,897
microseconds, below their 50 ms budget.

| Control | Original file | Native settings | Image pixels | Marker and icon composition |
|---|---|---|---|---|
| Passive live bridge | Pass | Pass | Pass | Pass |
| Replace with same pixels, different encoding/inode | Fail as required | Pass | Pass | Pass |
| Redirect URI to an identical image | Pass | Fail as required | Pass | Pass |
| Cover first image witness | Pass | Pass | Fail as required | Pass |

The configured original is a single-link mode-0444 file. Each observation compares
its path and a retained read-only descriptor, including bytes, inode/device,
permissions, owner, link count and modification/change timestamps. Replacement
leaves the held original's bytes intact but removes its link; the path selects a
different inode and PNG encoding. Identical visible pixels cannot hide that change.

The native `gsettings` record includes every key in the pinned background schema,
including settings that do not affect the current pixels. URI redirection therefore
fails even though its alternate PNG is identical. The visual obstruction instead
leaves both file and configuration unchanged, while exact external captures detect
its RGB (1,2,3) cover. The second image witness remains correct. All controls retain
live marker progress and the original icon/transparent-rectangle observations.

Only owned private files, settings, display and process resources were used. The
cover actor and its private method exist only under the explicit negative-control
flag; it cannot receive input or focus. Original PNG bytes, alternate bytes and
the configured path's final bytes are preserved alongside the native observations.

## Verification and preserved evidence

Twenty-seven wallpaper verifier checks pass. They reject missing/unstable image
baselines, changed identities/bytes, incomplete settings, false pixels, incomplete
timing, missing or late faults, incorrect control isolation and false final
restoration. Semantic mutations keep report/journal copies consistent so the
verifier must inspect the actual content rather than rely on copy disagreement.

The existing native input matrix and five default reveal/composition/marker cases
were rerun against the final sources. All 27 input, 22 reveal, 15 composition and
nine marker verifier checks pass: **100 verifier checks in this checkpoint**.
The live reveal result still fails foreground-focus restoration. Passing evidence
validation means that failure was detected and preserved, not that acceptance passed.

The final comparison is `out/evidence/w-05-gnome-wallpaper-calibration.json`.
Files with the same prefix retain 13 native attempts, 13 exact source archives,
23 raw journals, 15 PNG artifacts and execution/verification records. The first
successful live image run remains separate from the final four-control matrix.
Completed workspace preflights precede every native/verifier run, and owned process
groups finish with no surviving members.

No C++ implementation, target profile, runtime package lock or workspace allocation
changed. Previous CTest and smoke evidence retains its original source identity.

## Remaining work

This closes only the owned GNOME/DING single-display PNG preservation experiment.
Wallpaper policy, other formats/scaling modes/topologies, GPU/color-managed
presentation, Wayland and native recovery require their own evidence. Resolve the
observed DING MRU-focus restoration boundary under a separate integration contract.
Continue taskbar/task-switcher and shell/icon-manager recovery observations
independently. Other native tracks and deterministic product boundaries remain
admitted; W-02, W-05 and the full campaign remain open.
