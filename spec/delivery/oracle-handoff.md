---
type: "SysPane Work Record"
title: "Independent temporal oracle implementation checkpoint"
description: "Bind external marker/time evaluation and native X11 fault calibration to source and raw capture evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:24:33+11:00"}
sp_id: "SP-ORACLE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W02-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent temporal oracle implementation checkpoint

W-02 now has an independent pixel/time evaluator and native X11 calibration, and
remains in progress. Base `1fe45133ada6bc092f00cf1fd2fe96afc3dfda6e`, the containing
commit and exact input digests identify this checkpoint. The
[diagnostic handoff](diagnostic-handoff.md) remains historical. No desktop host is
qualified and W-25's outstanding recovery/preservation requirements remain open.

## Implemented boundary

Marker 0.1 carries a spatial border, version, uint64 generation and CRC in a fixed
128x96 RGB grid. Literal golden cell matrices and a Python decoder are independent
of the native C++ painter. The evaluator uses actual captured RGB bytes and observer
monotonic times, rejects candidate-buffer/window-flag substitutes, detects a single
intervening disappearance and enforces update deadlines without mistaking a capture
gap for a pass. Invalid evidence, observed failure and incomplete observation remain
different outcomes. Fixed bounds cover frames, file/decoded bytes, stimuli and time.

`SysPane.OracleProbe` is a Linux-only diagnostic fixture. It paints its own window
through an owned backing pixmap, accepts bounded generation events and can actually
unmap or freeze painting while its native event loop continues. It supplies no
capture bytes to the oracle. A separate observer controls stimuli and captures the
owned Xvfb root. Candidate properties and acknowledgements are recorded separately;
they cannot turn absent/stale pixels into a pass. X11 PID properties are structural
checks inside this private trusted lab, not authentication against arbitrary clients.

The runner owns an authenticated abstract-socket Xvfb server and captures only its
synthetic content. Capture work runs in a bounded child. Every frame/stimulus is
flushed to a task-owned journal; complete reports embed lossless compressed frames.
The runner confirms candidate, observer and server exit and compares pre/post root
pixel hashes and six bounded wallpaper/desktop-related property snapshots. That
restoration check is distinct from real wallpaper-file/policy qualification.

## Executed checks and provenance

Revision 7 passes 53 CTest entries on Windows and 54 on Linux. Both execute sixteen
fixed portable marker/time cases. Linux additionally executes five native cases:

| Native calibration | Required observed result | Calibration check |
|---|---|---|
| Live | All three generations visible within declared coverage/deadline budgets | Pass |
| Disappear | Intervening missing marker, even though it returns later | Pass only when observation fails |
| Freeze | Native events acknowledged while pixels remain at generation 1 | Pass only when observation fails |
| Occlude | A second owned test window obstructs the live marker | Pass only when observation fails |
| Gap | Deliberately omitted capture exceeds the time-coverage budget | Pass only when observation is inconclusive |

`build-support/evidence/w-02-oracle-<profile>.json` binds full regression case sets,
source/dependency/profile hashes, artifacts/imports and the exact reports named by
CTest. Its `--oracle` recorder recomputes native observations from embedded frame
bytes, verifies capture-journal identity and checks cleanup/root restoration. Native
case results are calibration evidence; none is a product T-DESKTOP-REVEAL pass.
No oracle expectation or tolerance was changed to accommodate measured results.

The component manifest now has an explicit profile selector for the Linux-only
probe. The configured target graph is checked against the selected ownership profile;
negative checks reject both a forbidden model dependency and the wrong profile's
target set. Existing native IPC, supervision and diagnostic cases remain regressions.

## Remaining work

Complete native adapters for named desktop reveal actions, real icon input/focus
and wallpaper configuration/file evidence, then run the corresponding admitted
synthetic desktop scenarios. Windows has portable oracle tests but no external
desktop capture execution here. Xvfb has no shell/icon manager; it does not qualify
GNOME, Plasma, Wayland, macOS, historical Windows or the current Windows desktop.
The earlier WSLg connection-opening failure remains preserved and unqualified.

Use this calibrated observer in bounded host investigations once their relevant
native action/lab boundaries are closed. Keep missing laboratories and unexecuted
dimensions explicit. A successful ordinary window, static image or repaired
disappearance must not become a wall-conformant result. W-02 and the campaign remain
active; no user wallpaper/shell, privileged operation or public release was changed.
