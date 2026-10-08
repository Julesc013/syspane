---
type: "SysPane Handoff"
title: "Private native text lifetime repair"
description: "Balanced GTK teardown preserves selection and prevents implicit clipboard export."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T22:07:00+00:00"}
sp_id: "SP-PRIVATE-TEXT-LIFETIME-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-PRIVATE-TEXT-LIFETIME"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Private native text lifetime repair

The shared private_text control now balances GTK's PRIMARY registration across
realization, unrealization and destruction. The original implementation removed the
registration after realization, leaving GTK to remove it a second time during
teardown. The new lifecycle wrappers remove it before returning from realization,
restore only the bookkeeping reference immediately before GTK consumes it, and finish
unrealization before destruction replaces the buffer. No event loop or buffer mutation
runs in the handoff. The pinned GTK implementation is linked in the [package](packages/w-11-private-text-lifetime.md).

The control retains its single buffer, text, selection, accessibility and editing
behavior. Copy/cut and drag export remain unavailable. Callers may modify the owned
buffer's contents but must not replace/share it or alter its registrations. The fix
does not clear or claim another application's PRIMARY or CLIPBOARD selection.

## Native evidence

The unchanged production component first failed the new native lifetime test with
exit -5 under fatal criticals, reporting the duplicate selection-removal assertion.
That baseline, source snapshot and exact executable identity remain preserved.
After the repair, all four fixed cases pass: three repeated realization cycles,
destruction while selected, destruction before realization and independent observer
calibration. Text and selection survive the cycles and subsequent editing works.

An independent Xlib client owns both selections during each live case. It checks
current ownership and SelectionClear events; the latter detect even a transfer
reversed before polling. A deliberate takeover/restoration generates both expected
events and fails the ownership oracle. The production control generates none. The
dedicated consumer runs with fatal criticals and its observer rejects GTK warnings.
The test consumer's cycle now hides/unrealizes/shows the control so it remaps normally.
Later intentional-fatal test launches disable core dumps to bound laboratory output.
Neither adjustment changes the fixed expectations or suppresses a diagnostic.

The installed frontend's twelve cases, the editor's twenty cases and the settings
form's eighteen cases pass with the rebuilt shared component. Both component graph
checks pass on all three configured development profiles. These are 54 native cases
and six graph checks; no Windows UI implementation or historical guest result is
claimed by graph regeneration.
Specification validation passes for 48 schemas and 166 fixtures. Specification-tool
unit tests were not repeated because their implementation did not change.

The stderr audit found a second defect in the settings test window after its behavior
checks passed: the destructor's destroy callback called gtk_main_quit after the loop
had returned. The callback now checks for an active loop. The settings observer now
enables fatal criticals and rejects GTK warnings/criticals, and all eighteen cases pass
again. The original behavior-pass records and failed stderr audit remain diagnostic
evidence, not clean shutdown qualification. Current lifetime, installed frontend,
editor and corrected settings artifact records contain no GTK warnings or criticals.

The [checkpoint](checkpoints/private-text-lifetime.json) binds the fixed inputs,
commands, exact source/artifact identities, native recordings and diagnostic audit.
Nine archives preserve 121,534,944 raw bytes, including an earlier historical settings
record explicitly excluded from current qualification. Its inclusion came from the
archive helper's original prior-campaign cutoff; subsequent capture uses this campaign's
own executions. No earlier record was rewritten. A configure preflight stopped when
native package copies consumed the normal build reservation. The complete frontend
attempt was archived, rechecked byte-for-byte with its node inventory and checked for
live users before its duplicate directory was removed. The subsequent preflight passed.
The F runtime base and crash orphans remain, and the 8 GiB ceiling is unchanged.

## Remaining application work

W-11 remains in progress. This evidence qualifies the pinned Linux GTK/Xvfb/AT-SPI
laboratory behavior, not other GTK versions, Wayland, screen-reader usability or
complete accessibility. The historical diagnostic records remain unchanged.

Continue connecting the editor and inspector to the installed frontend. Image and
recovery helpers still use the earlier admitted native-path launch interfaces; extend
verified installation closure and keep verification on native workers before exposing
those paths in the application. Bind live telemetry, activation/visibility, independent
desktop escape/recovery and installed session/draft context to the same owners.
Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X remain required complete
editions. No protected deployment or public release was performed here.
