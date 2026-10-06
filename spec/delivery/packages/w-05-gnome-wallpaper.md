---
type: "SysPane Work Package"
title: "W-05 native GNOME image-wallpaper preservation"
description: "Separate original file identity, native settings and externally observed image pixels."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:25:54Z"}
sp_id: "SP-W05-GNOME-WALLPAPER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-ORACLE", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native GNOME image-wallpaper preservation

This independent experiment keeps the existing focus-restoration failure and input
evidence intact. Use the pinned owned GNOME/DING laboratory, its real background
loader and the unchanged initial solid-color composition/marker prerequisite.
`--wallpaper live|replace-file|redirect-setting|cover-wallpaper` owns that prerequisite
and excludes other optional experiment flags. Never read or configure a user desktop.

## Fixed image and independent baseline

`tests/desktop/fixtures/gnome-wallpaper.json` defines a lossless 800x600 RGB PNG,
four exact palette colors and tile index `(x // 40 + 3 * (y // 30)) % 4`.
The configured original and alternate PNG have identical pixels and bytes.
Each lives in the unique owned attempt directory, is a regular single-link file,
and is set to mode 0444 before observation. Retain an `O_NOFOLLOW` read-only
descriptor to the original. Bound encoded files to 2 MiB and exclude access time
from identity comparisons; do not change permissions to make a case pass.

After the initial composition interval, hide only the candidate's owned actors.
Set the private native background's light/dark image URIs to the original file
and `picture-options` to `centered`. On this exact single 800x600 display, require
1:1 image pixels without scaling, cropping or tolerance. Preserve the other native
background settings and then freeze the complete `gsettings list-recursively`
background record, not just the visible URI.

Within five seconds, require both unobstructed image witnesses to match the fixture:
(600,400,128,96) and (480,80,96,96). Also require every pre-calibrated opaque icon
anchor to retain its original RGB, and every clean overlap witness to match the
corresponding image pixel. Then record three identical native baseline frames
100 ms apart. No candidate pixels participate in choosing masks or image expectations.
A failed image load, nonmatching baseline or unstable fixture is a laboratory
failure, not a wallpaper-preservation result.

## Measured interval and controls

Enable the same passive live scene and run the unchanged 2,400 ms marker trace:
generations 1, 2 and 3, 800 ms apart, 50 ms capture cadence, 200 ms generation
deadline, 150 ms maximum coverage gap and 50 ms combined observation budget.
Each paired observation includes overlap pixels, both image witnesses, the complete
native background-settings output, and original-path/held-descriptor file snapshots.
Bound the native settings response to 8 KiB and one second; a response that breaks
the stricter combined observation budget cannot qualify the temporal interval.
Keep native DING ownership and its live process handle through the interval.

Require exact file bytes, size, device/inode, mode, UID, link count and modification/
change timestamps to match the baseline at both the configured path and held
descriptor. Require all native settings to match their frozen baseline. Require
both image witnesses to match the fixture in every measured sample. Independently
retain the original opaque-icon, transparent-rectangle and changing-marker tests.

For each negative control, issue exactly one bounded fault at 1,000 ms (within
50 ms), without repairing it during the interval:

- `replace-file`: atomically replace only the owned configured path with another
  mode-0444 PNG encoding the same pixels plus a PNG text annotation. Native image
  pixels and settings must remain correct, while path bytes/identity and the held
  original's link count expose replacement.
- `redirect-setting`: change only the native light-image URI to the owned alternate
  identical PNG. Image pixels and the original file must remain correct; the full
  settings record must expose the changed URI.
- `cover-wallpaper`: enable a separate nonreactive, nonfocusable test drawing over
  the first image witness, using RGB (1,2,3). It exists only under this explicit
  laboratory flag, starts hidden, and is destroyed on disable. Files/settings and
  the second witness stay correct; external pixels must expose the obstruction.

The cover method is available only on the private laboratory object for this
control; it is not a product transport or a wallpaper-writing mechanism. All
controls must preserve live marker/overlap composition. Before each fault, all
three wallpaper dimensions must pass. At least three samples after its completion
plus 200 ms must expose the intended failure, with unrelated dimensions passing.
A startup error, uncertain coverage or unrelated failure cannot calibrate a control.

## Evidence and limits

Preserve the exact fixture, original/alternate/replacement bytes, source/runtime
identities, flushed raw journal (8 MiB/180 records), settings stdout, file snapshots,
native pixels, faults, partial failures and confirmed cleanup. Recompute every
dimension and the control outcomes from those records; never substitute a successful
settings call or matching file hash for native pixels. Keep the 40-second overall
observer bound and existing owned process-group cleanup limits.

This establishes only the named single-display image-preservation experiment.
It does not qualify mandatory wallpaper policy, other image formats/scaling modes,
multiple monitors, color-managed/GPU presentation, native recovery or a complete
desktop profile. Continue those gates and the separate focus integration work
without weakening their existing acceptance criteria.
