---
type: "SysPane Work Package"
title: "W-05 native Mutter focus-decision trace"
description: "Bind built-in native focus decisions to the independent window/pixel/keyboard baseline."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:43:03Z"}
sp_id: "SP-W05-GNOME-FOCUS-TRACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-FOCUS", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native Mutter focus-decision trace

The independent baseline already reproduces the failure without the candidate.
Trace the pinned native runtime's decision, without changing focus, replacing a
key handler, modifying upstream code or adding a shell observer extension.

## Hypothesis and source limits

Upstream Mutter 46.2's [Show Desktop handler](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/keybindings.c)
restores the desktop and invokes workspace default-focus selection. Its
[workspace implementation](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/workspace.c)
can select a recent focusable desktop window. This suggests that the native
decision itself may select DING again, rather than first selecting the foreground
and then losing focus to a later candidate action. These upstream sources establish
a hypothesis; the Ubuntu-patched runtime must supply actual decision evidence.

The pinned native library contains built-in focus diagnostics. Its upstream
[debug configuration](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/util.c)
supports topic selection through `MUTTER_DEBUG`. Do not equate a present diagnostic
string or a source inspection with an executed native decision.

## Closed experiment

Add optional `--focus-trace` only beside an existing `--focus-baseline` mode. It
sets `MUTTER_DEBUG=focus,keybindings,window-state` in the cleared private laboratory
environment. Do not set global logging variables or `MUTTER_USE_LOGFILE`; the
retained shell's existing stdout/stderr pipe writes only its owned `shell.log`.
Keep the current 1 MiB log bound and 40-second observation/cleanup limits. Preserve
the complete log and its digest; overflow, truncation or missing native diagnostics
is an invalid trace, never an inferred decision. Default execution stays untraced.

Run one traced and one untraced case for each of `shell`, `ding`, `candidate`, using
identical current sources and the complete existing native baseline/keyboard
observer. The earlier nine-run untraced comparison remains separate evidence.
All six new cases must retain exact native ownership, visible transition, timing,
keyboard and cleanup checks. Compare focus/active-client roles and key receipt
between each traced/untraced pair; a difference is inconclusive instrumentation,
not evidence that a logging switch fixed the product.

The traced log must contain exactly two executed `show-desktop` handler entries,
in order, matching the two independently retained native action records. Distinguish
executed handler entries from startup key-binding registration. Within the second
handler's synchronous decision sequence, identify its first workspace MRU selection
and bind the hexadecimal XID to the already retained normal foreground or DING
window. Bound the search to the next keyboard-event handling boundary; do not use
a later explicit click's focus change as the restoration decision. Preserve line
numbers and the exact native decision excerpt. An unknown XID, ambiguous/missing
decision or incomplete log leaves attribution unproven.
Also end that sequence at a later mouse-focus event or 200 ms after the native
handler timestamp, whichever occurs first. Reject backwards/uncorrelated log time;
the handler separation must agree with the independent action separation within
50 ms. Native wall-clock text only bounds diagnostic association; the original
monotonic capture/action deadlines remain the acceptance authority.

The recorder must recompute the interpretation from the full raw log and reject
changed XIDs, handler counts/order, later-focus substitution, mismatched bytes,
missing controls or changed native observations. It must continue to validate the
original candidate reveal oracle. A native selection of DING that matches the
external focus and missing-key evidence supports the MRU-selection mechanism for
this pinned integration. A foreground selection followed by lost focus instead
requires a different investigation. Neither result changes acceptance.

## Completion and next decision

Preserve source/runtime identities, raw logs/journals, failed attempts, pair
comparisons and adversarial verifier checks. Ordinary build commands and unrelated
native work continue. The trace does not authorize a native-library patch, a global
focus workaround, an acceptance downgrade or a release. A proposed integration
change requires its own bounded contract and independent evidence. Icon input,
taskbar/task-switcher behavior, wallpaper and recovery remain separate gates.
