---
type: "SysPane Work Record"
title: "Owned GNOME and DING composition checkpoint"
description: "Externally verify a live drawing between the synthetic wallpaper and real desktop icons, with two wrong-layer controls."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:47:00Z"}
sp_id: "SP-GNOME-COMPOSITION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-GNOME-MARKER-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Owned GNOME and DING composition checkpoint

From `0b24cf3d7af298a9320addd1bc2eb9bcbbd30745`, the shell bridge now passes the
selected solid-color composition experiment with real DING desktop icons. Its live
marker remains visible, a separate drawing appears through transparent desktop
pixels, and opaque icon pixels remain unchanged. Above-icons and below-wallpaper
controls fail the required independent dimensions. This is scoped native composition
evidence, not qualification of the entire desktop contract or product.

## Observed results

The [package](packages/w-05-gnome-composition.md) closes the fixture, ownership,
calibration, limits and control outcomes. The existing GNOME 46/Mutter/GJS lab now
enables the pinned DING `46+really47.0.9-1ubuntu5` extension from a unique private
copy whose identity matches the extracted package. DING's real GJS desktop window
is bound through X-Resource, exact script path and the retained shell process group.
Its pidfd remains held during observation; mapped runtime files and cleanup are
recorded independently of the marker bridge.

One synthetic folder uses a known opaque icon, drawn by DING through its ordinary
icon theme. The marker occupies a separate unoccluded region. Before enabling the
candidate, black and white background controls establish which native pixels are
opaque icon content and which are transparent. The original background is restored
before the candidate interval. No candidate output selects either witness mask.

| Candidate | Changing marker | Opaque icon anchors | Drawing through transparent pixels |
|---|---|---|---|
| Live background-layer bridge | Pass | Pass | Pass |
| Above-icons control | Pass | Fail | Pass |
| Below-wallpaper control | Fail | Pass | Fail |

Each final case preserves 48 paired samples. All use 4,096 opaque anchor pixels
and 33,695 independently calibrated transparent witnesses. The live case's maximum
combined capture duration is 2,195 us and maximum gap 52,470 us, within the unchanged
50 ms capture / 150 ms coverage budgets. Marker generations retain the original
200 ms presentation requirement. The separate synthetic background pixels and
background settings remain unchanged during every candidate interval.

The recorder recomputes masks, raw samples, timings, expected controls, native
ownership, source/runtime/fixture identity and preserved journals. Fifteen adversarial
checks pass, including an empty-icon-mask case with internally valid image hashes.
The ordinary marker-only path is rerun and its nine existing evidence checks pass.
Every owned process group exits; original failures and source archives are retained.

## What the failures changed

The first version 0.1 fixture incorrectly inferred transparency from one dark
baseline. Its marker and 4,096 icon anchors passed, but 189 faint label-shadow pixels
rounded to the baseline color and then produced (191,32,127) over the rectangle's
(192,32,128). The preserved verdict remains failed. Version 0.2 adds independent
black/white calibration before the candidate is enabled. Exact pixel equality,
opaque-icon preservation and the original temporal oracle remain unchanged.

An early below-wallpaper control unexpectedly passed all three dimensions: GNOME's
background replacements during calibration changed the relative actor order after
creation. The corrected control moves only its own actors to the bottom once at
activation. It never restacks during measurement. All three final cases use the
same corrected source inputs; the unexpected passing control is retained as an
experiment defect, not accepted negative-control evidence.

A preliminary live run also launched before the asynchronous budget-check exit
had been observed. The later poll confirmed adequate budget, but that run is
excluded from final calibration. Final execution records prove each successful
preflight completed before its corresponding native launch. No workspace allocation
or product resource limit changed in this checkpoint.

Nine native attempts, original source ZIPs and eight raw composition journals are
preserved under `build-support/evidence/w-05-gnome-composition-*`. The successful
marker regression has no composition journal. Existing C++ binaries, build profiles
and earlier CTest/smoke evidence retain their previous checkpoint identities; no
unrelated C++ rebuild or product package qualification is claimed here.

## Remaining boundary

W-02/W-05 remain open. The next native steps are real desktop reveal with foreground
windows, focus/taskbar checks, icon selection/drag/menu/opening, image-wallpaper
preservation and shell/icon-manager recovery. Keep their evidence separate from
this static composition result. DING's logs retain missing Nautilus/file-operation
services and a failed version-helper launch; file opening and metadata persistence
were not tested or inferred from displayed icons.

The laboratory still has private buses without real system services and software
rendering on Xvfb. Native login/device/policy integration, GPU presentation, Wayland,
multi-monitor scaling, other shell versions and other platforms remain unqualified.
No user desktop, wallpaper, shell or VM was controlled. The full campaign and native
application/controller/settings/editor/persistence verticals remain incomplete.
