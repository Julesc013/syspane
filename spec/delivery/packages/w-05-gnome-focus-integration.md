---
type: "SysPane Work Package"
title: "W-05 bounded native Show Desktop focus integration"
description: "Test event-bound restoration using public shell signals while preserving native key handling and icon focus."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:50:47Z"}
sp_id: "SP-W05-GNOME-FOCUS-INTEGRATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-FOCUS-TRACE", "SP-W05-GNOME-REVEAL", "SP-W05-GNOME-INPUT", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 bounded native Show Desktop focus integration

Investigate the pinned GNOME 46/DING X11 focus-restoration failure using an optional
trusted bridge controller. `--focus-integration observe|restore` requires the
existing `--focus-baseline candidate` experiment, its unchanged composition/reveal
oracle and real F9/F10 receipt probes. Default bridge behavior remains unchanged.
This is a named integration experiment, not permission to patch Mutter/DING,
replace a native key handler, disable icon focus or add periodic focus repair.

## Native basis and bounded decision

The public `showing-desktop-changed` workspace-manager signal runs after the native
desktop-mode change. It carries no new-state argument. The public window method
`showing_on_its_workspace()` includes desktop-mode visibility in its result.
The native key handler performs its usual default-focus selection after the
restoration signal. Inspect the pinned runtime and execute the hypothesis; upstream
source alone is insufficient evidence. References: [workspace manager](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/meta-workspace-manager.c),
[window visibility](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/window.c),
[native key handler](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/keybindings.c).

Track at most one last-focused normal, non-transient, non-minimized window on the
active workspace, retaining its native object lifetime rather than an XID. Clear
it on unmanaging, minimization or workspace movement/change. Unknown state or
missing native APIs must abstain and leave failed evidence; never guess a target.

At the desktop-mode signal, inspect the actual current Clutter event. Only a
KeyPress for the configured laboratory Super+D binding is eligible. Require the
exact binding, D/d keysym, Super/Mod4 state with no Shift/Control/Alt/other modifiers
(Caps Lock/Num Lock may be present), nonzero native event time and X11 mode.
Other events invalidate pending restoration. Do not install a key handler.

When the retained eligible normal window becomes non-showing, remember this exact
entry transition and workspace; do not change focus. A later eligible signal may
restore focus once only when that same window is showing again, is still eligible,
the workspace is unchanged and current focus is a native desktop window. Clear
pending state before calling the public `window.focus(event_time)` synchronously.
Do not activate, raise, unminimize or move a window; do not schedule a timer or
retry. User actions selecting another normal window supersede the saved target.

`observe` records the same decision but omits the focus call. `restore` permits
only that synchronous call. Native signal/decision diagnostics are explanatory
metadata; external pixels, native active-client state and actual key receipt are
the acceptance authority. Bound diagnostics to 256 records and 64 KiB; overflow
disables the controller and invalidates evidence. Keep the 40-second attempt,
existing owned resources and campaign workspace preflight.

## Required observations and guards

Both modes must pass initial composition, original visible reveal and original
pixel/timing coverage. The observation control retains the established focus/F9
failure. The restoration candidate must pass the unchanged focus deadline and
deliver F9 without the later explicit-click F10 positive control repairing it.
Keep all original failed baseline/trace evidence separately.

Then exercise bounded native guards with no private focus command:

- An explicit icon click outside Show Desktop keeps DING focused; unrelated keys
  cannot invoke restoration. Retain external active-client samples for 400 ms.
- Native entry, icon interaction and native restoration preserve icon usability
  and restore the original normal window only on the explicit second chord.
- Minimize the saved normal window while Show Desktop is active. A later native
  restore must leave it minimized and must not focus or unminimize it.
- A desktop-mode change without the eligible key event must not restore saved
  focus. Preserve its native result rather than imposing a guessed focus target.
- Disable the optional controller through its one-way laboratory method. Subsequent
  native Show Desktop must reproduce default behavior, proving callback removal.

Guard captures run every 50 ms for 400 ms, with the original 50 ms capture and
150 ms gap budgets; require at least three observations after the 200 ms native
transition allowance. Capture marker, background, foreground witness, client list,
active client, desktop mode and WM_STATE together. Native Show Desktop itself
sets WM_STATE to IconicState; actual minimization is distinguished by retaining
IconicState and hidden foreground pixels after desktop mode ends. The initial
incorrect NormalState assumption remains in the failed experiment record.

Use the existing complete native icon-input sequence while Show Desktop is active.
Opening the owned folder must end desktop mode without an eligible key event;
verify actual folder focus/contents and subsequent closure, then restore the
original foreground through ordinary Alt+Tab before the minimization guard. Final
binding and background settings must match the original fixture. These setup
steps do not repair or alter the earlier fixed acceptance interval.

Only passive diagnostic retrieval and one-way disable are exposed on the private
laboratory bus; no method accepts a focus target or invokes restoration. Original
binding/settings and fixture identities must remain exact. Broader multi-window,
modal, workspace, lock/session and alternate reveal-trigger behavior requires its
own evidence before general enablement; these limits do not remove those goals.

## Verification and continuation

Preserve complete native reports, event/decision journals, source archives, failed
attempts, exact runtime identities and cleanup. Recompute original reveal and
keyboard outcomes with existing verifiers. Add checks rejecting false focus/key
receipt, stale target identity, non-key restoration, missing guards, rewritten
journals and later-click substitution. Run relevant default-path regressions.

A missing event or failed native guard is a failed integration candidate, not a
reason to weaken acceptance or silently broaden the hook. Do not enable this
controller by default until its supported behavior has independent qualification.
W-02, W-05 and the campaign remain open after this finite experiment.
