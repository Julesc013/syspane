---
type: "SysPane Work Package"
title: "Recovery admission investigation and closed production gate"
description: "Preserve the ordinary-entry experiment and repeated timing failures while separating fixture observers from candidate admission."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T10:05:00+00:00"}
sp_id: "SP-W11-RECOVERY-ADMISSION-INVESTIGATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-PRODUCTION-RECOVERY", "SP-W11-RECOVERY-GUI-LIMITS", "SP-W11-EDITOR-PAINT-TRACE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Recovery admission investigation and closed production gate

SP-W11-PRODUCTION-RECOVERY remains unfinished. Its enabled ordinary-entry experiment
passed functional cases, but the unchanged ordinary GUI qualification failed. A
predeclared single confirmation also failed. Preserve both attempts; the earlier
recovery-submission pass and the passing paint diagnostic do not override them.

Keep the production entry's recovery/history admission disabled. Keep the existing
SYSPANE_EXPERIMENTAL_RECOVERY definition only on development fixtures. Independently
define SYSPANE_FRONTEND_TEST_OBSERVERS only on the observer fixture. The ordinary
entry fixture admits candidate recovery without observer support. It is not the
production binary: helper identity and the compile-time admission argument differ.
No environment variable supplies feature or policy authority. No fixture is installed.

Verify final main code/relocations: the disabled production and candidate main differ
only in the admission argument, in addition to their separate generated helper
identity. Record compiler/flags, exact artifacts and common runtime libraries.
Compare allocated code/data of the final fixtures with the already-executed candidate
artifacts, excluding only the recorded ELF build ID. Recheck actual production
policy/helper refusal through the unchanged settings oracle and current component
graphs on all three profiles. Do not claim another full native rerun from byte
equivalence or claim production admission complete.

## Preserved failure and next experiment

The first ordinary attempt exceeded the MAX-WIDGETS excess-delay limit at 108851 us.
The sole declared confirmation exceeded MAX-WIDGETS at 102235 us, and MAX-RECORD at
102714 us delay and 112718 us callback work. The limits remain 100000 us. Preserve
exact timing rows, native files, children and source/artifact/environment identities.

The observer fixture's allocated code/data match the preceding passing checkpoint
except its ELF build ID. This comparison does not establish the cause of a delay.
The paint trace identifies repeated native composition in restore/history callbacks
and drawing; its instrumented timings are not qualification. An isolated equivalent
pixel-packing loop saves about 2 ms for 786432 pixels in the current debug profile;
that result does not justify treating it as the cause or repair. Keep product pixel
code unchanged until a measured repair is selected.

Next use the existing phase/paint diagnostics and exact maximum-input recipes to
attribute callback work separately from between-callback drawing/delay. Bound each
experiment and preserve failed results before changing code. Select a repair with
fixed pixel, geometry, authority, erasure and lifetime expectations. Re-run unchanged
ordinary qualification after that repair; no repeated-until-pass admission rule.
Then resume SP-W11-PRODUCTION-RECOVERY. General authoring/preview responsiveness,
native inspector, telemetry/desktop, protected deployment and all editions remain open.
