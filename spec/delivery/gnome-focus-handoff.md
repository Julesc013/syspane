---
type: "SysPane Work Record"
title: "Independent GNOME and DING focus comparison"
description: "The native focus and keyboard-delivery failure repeats without the SysPane bridge."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:33:49Z"}
sp_id: "SP-GNOME-FOCUS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-FOCUS", "SP-GNOME-REVEAL-HANDOFF", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent GNOME and DING focus comparison

From `e7088c4ce4628848cff0b0ce51c96a52a55aa5e3`, a native comparison establishes
that the observed foreground-focus failure does not require the SysPane bridge.
The pinned DING/X11 integration reproduces it when the candidate extension is
absent. GNOME alone restores foreground focus and actual keyboard receipt. The
original reveal acceptance remains failed; this evidence identifies the next
integration boundary without waiving a requirement or qualifying a desktop host.

## Independent native evidence

The [package](packages/w-05-gnome-focus-baseline.md) defines three source-identical
repetitions of each mode on fresh owned desktops. All share the pinned GNOME 46
runtime, foreground window, synthetic background, explicit Super+D binding,
action schedule and observation budgets. DING modes retain the same folder/icon
fixture and exact upstream extension bytes. In both baselines the candidate
extension is neither copied nor enabled. The shell-only mode omits the native
icon manager as a diagnostic control; it is not an alternative product edition.

| Mode | Visible foreground hide/restore | Active client after restore | F9 delivered to foreground | F10 after explicit click |
|---|---|---|---|---|
| GNOME, no extensions | Pass in 3/3 | Foreground in 3/3 | Yes in 3/3 | Yes in 3/3 |
| GNOME with DING, no candidate | Pass in 3/3 | Icon desktop in 3/3 | No in 3/3 | Yes in 3/3 |
| GNOME with DING and candidate | Pass in 3/3 | Icon desktop in 3/3 | No in 3/3 | Yes in 3/3 |

Each fixed 2,400 ms native interval contains 48 samples. Across the nine cases,
the maximum combined observation duration is 3,374 us and maximum coverage gap
53,760 us, within the existing 50 ms / 150 ms bounds. Candidate mode first runs
the full composition prerequisite and unchanged three-generation reveal oracle.
Its marker, icon anchors, rectangle, background and visible transitions still
pass; required foreground-focus restoration still fails.

After the fixed acceptance interval, F9 tests actual delivery without refocusing.
An explicit native foreground click then precedes F10. The owned GTK process
records receipts independently in an exclusive 0600 event file, bounded to
16 KiB/16 events. Native resource/process ownership, file identity, event sequence,
hardware keycode, monotonic receipt time and positive-control focus are checked.
GNOME-only F9 receipts take 224–302 us from injection completion; every F10 receipt
takes 120–765 us. DING's F9 absence is bounded to the 200 ms observation window.
It does not prove that DING consumed the key. The explicit click is a diagnostic
positive control, not a proposed focus workaround or repair of earlier acceptance.

The recorder at repository path
`build-support/evidence/w-05-gnome-focus-comparison.json` recomputes the observations,
extension absence, exact native inputs, keyboard receipts and repeated comparison.
All three repetitions per mode agree. It rejects missing repetitions and reports
inconclusive attribution if their results differ. Its successful completion is
distinct from the recorded native focus/candidate acceptance result.

## Verification and retained failures

Twenty-four new evidence checks pass: candidate absence, native extension identity,
foreground/icon ownership, exact geometry, cleanup, post-interval key timing,
event-file lifetime, missing/foreign/late receipts, false delivery/focus claims,
raw journals, native captures/actions and inconsistent or incomplete repetitions.
The original reveal path is also rerun with live, omitted-action and temporary-blank
controls; its 22 checks pass with the same failed live acceptance. Separate
composition and marker regressions pass their 15 and nine evidence checks.

The first baseline attempt failed before observation because importing GDK chose
version 4 before GTK 3. Explicitly requiring GDK 3 fixed the owned helper without
changing the runtime package lock or test requirements. Its original report,
source archive, logs and failure journal are retained. An initial complete
three-mode comparison remains separate from the final nine-run matrix.

Eighteen native attempts, eighteen source archives and forty raw journals/event
files are preserved under `build-support/evidence/w-05-gnome-focus-*`. Completed
preflights precede all final native invocations. Final retained processes and their
groups exit with no surviving members. No C++ artifact, profile, workspace limit,
user desktop, wallpaper, shell, VM or public release changed. Earlier CTest/smoke
results retain their own source identities.

## Next boundary and limits

The results localize the observed difference to the tested DING/X11 integration;
they do not isolate an upstream function, establish behavior on other versions,
or prove an application-level fix. The candidate is unnecessary for the reproduced
failure, so changing its passive drawing actors would not address the demonstrated
baseline. Inspect/instrument the native focus transition before proposing an
integration fix or a separately reviewed contract correction. Preserve the original
failed oracle and do not add a focus-stealing timer.

The current laboratory omits real system/file-operation services and uses software
X11 rendering. Taskbar/task-switcher behavior, complete icon input, image wallpaper,
shell/icon-manager recovery, GPU presentation, Wayland and the product vertical
remain unqualified. Independent native tracks and deterministic implementation
work continue under their existing package/laboratory gates. W-02/W-05 and the
full campaign remain open.
