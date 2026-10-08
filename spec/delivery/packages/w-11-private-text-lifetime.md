---
type: "SysPane Work Package"
title: "Private native text lifetime"
description: "Balance GTK selection registration across realization and destruction without exporting authored text."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T22:05:00+00:00"}
sp_id: "SP-W11-PRIVATE-TEXT-LIFETIME"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-NATIVE-SETTINGS", "SP-W10-NATIVE-EDITOR", "SP-W11-INSTALLED-SETTINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Private native text lifetime

Repair the shared private_text GTK control used by settings and editor forms.
Preserve its bounded UTF-8 input, ordinary text selection/editing, native accessibility
and refusal of automatic PRIMARY/CLIPBOARD, copy/cut and drag export. Do not silence
GTK diagnostics, disable fatal-critical verification or grant clipboard authority.

The control owns one buffer throughout its lifetime. Trusted callers edit that
buffer's contents; they must not replace it, share it with another view or directly
change its clipboard registrations. Keep this ownership explicit in its public header.
Other buffers and another application's selections are outside this control's ownership.

On the pinned GTK 3.24.41 implementation, realization adds a PRIMARY registration;
unrealization removes it. Buffer replacement while realized also removes it. The
existing realization hook removes the registration to prevent export, leaving GTK's
later removal unbalanced. See the pinned [TextView implementation](https://github.com/GNOME/gtk/blob/3.24.41/gtk/gtktextview.c)
and [TextBuffer implementation](https://github.com/GNOME/gtk/blob/3.24.41/gtk/gtktextbuffer.c).
Restoring a registration alone does not publish selected text; buffer selection
updates perform publication. Any balanced handoff must therefore restore and consume
the registration synchronously, without yielding or allowing a buffer mutation in
between. Use public GTK lifecycle methods; do not access its private structures.

Repeated unrealize/realize must preserve text, selection and editability. Destroying
a selected realized control and destroying a never-realized control must both finish
without GTK criticals or warnings. Retained private text must not become a transient
selection owner during teardown. Do not clear, replace or otherwise claim a foreign
PRIMARY or CLIPBOARD selection to make the test pass.

## Fixed native verification

Freeze this package and private-text-lifetime-cases.json before changing production.
Add a small native consumer of the actual shared control and an independent observer
on an owned Xvfb/private D-Bus display. Run the consumer with fatal GTK criticals;
preserve the baseline failure before repairing it. Use actual native keyboard actions
and AT-SPI observations for selection, copy/cut, text and continued editing.

Exercise three realize/unrealize cycles with a selection, destruction while selected,
and destruction before realization. An independent Xlib owner must hold both PRIMARY
and CLIPBOARD throughout each live case. Check current owner identity and consume
SelectionClear events, which also reveal an ownership transfer reversed before a
later poll. Calibrate that observer with a deliberate foreign takeover; reject a
dead process, a lost selection, GTK warning/critical, wrong text/selection or timeout.
Bound each case to twenty seconds and every readiness/action observation to five.

Run native.SETTINGS-FORM, native.INSTALLED-SETTINGS and the existing native editor
regression against the rebuilt shared component; preserve all original oracles and
failed runs. Check every retained GTK stderr for the repaired diagnostic. Regenerate
component graphs on the three configured profiles. This qualifies only the pinned
native lab behavior, not all GTK releases, Wayland, screen-reader usability or full
accessibility. Continue installed editor/private-helper integration and all five
complete desktop editions after this shared control defect is closed.
