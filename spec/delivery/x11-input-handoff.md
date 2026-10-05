---
type: "SysPane Work Record"
title: "X11 native input and image-wallpaper checkpoint"
description: "Bind native pointer routing and delayed image setup to independent clipboard, accessibility, focus and pixel evidence."
tags: ["delivery", "assurance", "desktop"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:53:25+11:00"}
sp_id: "SP-X11-INPUT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W05-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# X11 native input and image-wallpaper checkpoint

This extends the [initial X11 investigation](x11-host-handoff.md) from base
`ca05f1b989686dbe5af7652205a4770f347db416`. The containing commit and recorded source
digests identify the implementation. W-02/W-05 and the full campaign remain open.
No desktop host or product edition is qualified.

## Observed results

On the exact owned Xvfb/Openbox/PCManFM laboratory, starting PCManFM with a synthetic
color and then setting the fixture image through its ordinary command succeeds.
Independent root pixels match the corresponding PPM bytes exactly. The image,
configuration, fixture folders and unobstructed wallpaper remain unchanged during
the candidate interval. This distinct setup sequence does not qualify the original
image-at-startup profile, whose BadDrawable failures remain historical evidence.

| Candidate | Reveal observation | Placement | Native icon-input sequence |
|---|---|---|---|
| Ordinary window, negative control | Fail: disappears during reveal | Fail: covers icons | Fail: overlapping click does not select the icon |
| EWMH desktop window | Pass for the measured changing marker | Fail: covers icons | Fail: overlapping click does not select the icon despite its input-shape hint |
| EWMH below window | Fail: marker hidden | Fail: hidden beneath the opaque icon manager | Pass: selection, clear, drag-selection, context menu, double-click folder open, close and restore |

The input pass applies to the named hidden candidate on this profile. It cannot
compensate for its placement/reveal failures. After a failed selection prerequisite,
later input steps remain unexecuted. No cause is inferred solely from window flags.

## Independent observations and calibration corrections

XTEST supplies pointer/keyboard stimuli on the private display. Selected files are
observed through its private native clipboard, with exact fixture URIs, bounded
responses, a fresh owner for every copy request and explicit handling of one final
GTK buffer NUL. Native focus/client identity and captured pixels accompany each step.
The real context menu and opened folder title are read through AT-SPI on the owned
bus. The opened normal window must belong to PCManFM, receive focus, and yield
exactly Sentinel.txt after native select-all/copy. Accessibility actions never drive
the interaction. Fixture identities and the restored icon pixels are checked.

Earlier attempts are retained unchanged. Their draft input verdicts are not accepted
candidate findings: this PCManFM build exposes neither desktop icons nor the folder
item view as accessibility children. An empty tree was insufficient selection or
content evidence. Captured pixels also show that the folder menu hides Open and
shows Open in New Window. The package records these observer expectation corrections;
the product's input, visibility and wallpaper requirements remain unchanged.

Other retained laboratory failures include the private bus's missing receive rule,
an overlong accessibility socket path, unconfirmed registry startup and libatspi's
implicit peer-connection timeout. The final adapter confirms the registry PID,
uses a retained short alias to the same owned runtime directory, and reads AT-SPI
through explicit private-bus calls with deadlines and activation disabled.

## Evidence and validation

`build-support/evidence/w-05-x11-input.json` binds the final report and prepared lab.
Its raw report includes compressed independent frames, semantic/focus snapshots,
clipboard bytes, flushed stimulus/observation journals and confirmed process cleanup.
The recorder independently recomputes temporal/placement/input outcomes, exact image
pixels and fixture URI meaning, checking source/artifact/runtime identity.
Fifteen evidence tests pass, including rejection of wrong files, stale clipboard
owners, hidden menus, title-only folder claims, focus theft and corrupted journals.

`build-support/x11-input-runtime.json` pins the optional installed AT-SPI/GI runtime.
No system installation or privilege was used. All services, clipboard operations and
captures belong to the synthetic private display. The user's desktop and clipboard
were not accessed. Owned output remains below the admitted 1 GiB limit.

The attempt register preserves all eleven earlier raw reports from this checkpoint.
Intermediate edits were hashed by those reports but their complete source snapshots
were not archived; they are diagnostic history, not replayable final acceptance.
The final source-bound report is replayable with the recorded runtime and artifacts.

Changes here affect the optional Python experiment and documentation. C++ targets
and the ordinary regression suite are unchanged; the prior Linux 54-entry and Windows
composition runs remain historical, rather than being presented as fresh runs.
Specification generation, schema/fixture validation, tooling tests and integrity are
recorded separately in `build-support/evidence/w-05-x11-input-verification.json`.

## Next admitted boundary

Investigate a composition strategy that preserves a visible surface behind real
icons; the tested above/below stack fails that requirement. Keep shell recovery,
policy-controlled wallpaper behavior, GNOME/Plasma/Wayland and Windows/XP/7/macOS
qualification separate. Other profiles and W-25 can progress independently.
W-25 still requires bounded recent-failure metadata, explicit configuration
preservation and integration with real data, rendering and visible/editor recovery.
