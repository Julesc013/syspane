---
type: "SysPane Work Record"
title: "Owned GNOME native reveal and failed focus restoration"
description: "Live composition survives visible native hide/restore, while the required foreground focus remains failed."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:14:00Z"}
sp_id: "SP-GNOME-REVEAL-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-REVEAL", "SP-GNOME-COMPOSITION-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Owned GNOME native reveal and failed focus restoration

From `5923ca9d3f3d58d58b258d7a042632790eeb8b54`, the GNOME/DING bridge now has
source-bound native Show Desktop evidence. Its changing drawing survives while a
real normal foreground window disappears and returns. The live acceptance case
still fails: after visible restoration, the native active client remains DING
instead of the foreground window. No focus requirement or overall verdict is
relaxed. The campaign and W-02/W-05 remain open.

## Scenario and measured outcomes

The [package](packages/w-05-gnome-reveal.md) fixes the window, pixels, native action,
ownership, timing, controls and resource limits before execution. The pinned
GNOME 46/Mutter/DING runtime runs on the existing authenticated owned Xvfb display,
with private settings and buses. This scenario explicitly binds Super+D to Show
Desktop; it does not assert that binding is GNOME's default.

A separate retained GTK process supplies a normal 200x120 foreground window at
(500,60). X-Resource binds its actual client to the retained process, script,
group/session and start ticks; a pidfd remains held throughout the trace. Native
geometry, type, active window, client pixels, mapped runtime and process cleanup
are observed independently of the shell bridge. The foreground fixture never
covers the marker, icon overlap or background witness.

After the unchanged live composition prerequisite and native foreground activation,
each 2,400 ms trace captures generations 4–6, real icon pixels, the foreground
witness, background pixels and native state. Super+D occurs at 400 and 2,000 ms.
The ordinary window must disappear against the known background and return in
the recorded normal desktop state; successful key injection or state flags alone
cannot pass. Both visible transitions and foreground-focus restoration remain
required within 200 ms of the corresponding action.

| Control | Continuous marker / rectangle | Icons / background | Visible native transitions | Foreground focus | Overall acceptance |
|---|---|---|---|---|---|
| Live bridge | Pass / Pass | Pass / Pass | Pass | Fail | Fail |
| Native actions omitted | Pass / Pass | Pass / Pass | Fail | Pass | Fail |
| Candidate hidden briefly, then restored | Fail / Fail | Pass / Pass | Pass | Fail | Fail |

All final cases contain 48 samples. The live visible transitions are independently
observed 52,090 and 52,306 us after the respective native actions. Its maximum
combined capture/state duration is 3,110 us and maximum coverage gap 52,046 us,
inside the unchanged 50 ms / 150 ms limits. The original Marker 0.1 oracle remains
unchanged. Real opaque icon anchors and calibrated transparent witnesses are reused
from the existing composition fixture; background settings/pixels remain unchanged.

The temporary-blank control hides only the owned drawing actors at 1,000 ms and
restores them at 1,200 ms. The preserved trace contains both the absence and later
visible frames. It remains failed with `marker.absent_or_invalid`; the repaired
final appearance cannot erase earlier failure. The omitted-action control leaves
the normal window visible and correctly fails the transition requirement.

The recorder result at repository path
`out/evidence/w-05-gnome-reveal-calibration.json` recomputes the raw
observations, source identity, native ownership and journals.
Recorder success means the controls/evidence are valid, not that the live candidate
passed. Twenty-two adversarial reveal checks pass, including visible pixels without
native state, native state without disappearance, late focus, false focus claims,
ownership, missing actions, capture order, settings and journal changes. The separate
composition and marker paths are rerun; their 15 and nine evidence checks pass.
All owned groups exit with no surviving members in the final records.

## Preserved attempts and implementation corrections

The first foreground helper used a Python Cairo drawing callback unavailable in
the lab's GI environment. Its normal window opened and focused, but exact pixels
failed. GTK's native CSS background painting supplies the same fixed RGB without
adding a system package. The next attempt exposed GTK's empty-window 200x200
allocation; an explicitly sized native content box supplies the required 200x120.
Both original prerequisite failures remain failed with their source archives.

The first complete live run already showed successful visible transitions and failed
focus restoration. Diagnostic visibility/focus dimensions were added to explain
that failure, while preserving the original joint acceptance requirement. Review
then added an explicit first-observed focus/joint-transition deadline check and a
late-focus negative case. All final controls and native regressions were rerun with
identical current source inputs. Earlier passing calibration records remain separate
from the final record; their live candidate acceptance was also failed.

Thirteen native attempts, thirteen source ZIPs and twenty composition/reveal journal
files are retained under `out/evidence/w-05-gnome-reveal-*`, along with
invocation/preflight and verification records. The bootstrap runner now allows the
observer to exit naturally after sending its result before applying bounded cleanup,
avoiding a race that previously terminated an already-completed observer. It still
terminates only its retained owned processes.

No C++ artifact, target profile, runtime package lock or workspace allocation changed.
Earlier CTest and smoke-package results keep their previous checkpoint identities.
Specification validation is separate from the native experiment and cannot qualify
a desktop profile. No user desktop, wallpaper, shell, VM or public release was touched.

## Next boundary

Run an independently specified native baseline to determine whether the failed
foreground-focus restoration also occurs without the candidate bridge. Do not
attribute the failure to GNOME, DING or the bridge without that comparison, and do
not add a focus-stealing workaround. Keep the failure until an appropriate contract
or implementation change has independent evidence.

Taskbar/task-switcher absence, broader focus behavior, icon selection/drag/menu/opening,
image wallpaper/policy and bridge/shell/icon-manager recovery remain unexecuted on
this path. DING's missing file-operation services remain logged; visible icons are
not proof of working file operations. This synthetic software-rendered X11 lab does
not qualify GPU presentation, Wayland, other shell versions, scaling or a complete
product vertical. Independent Windows, historical Windows and macOS tracks retain
their existing admission and laboratory constraints.
