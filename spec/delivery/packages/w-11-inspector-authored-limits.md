---
type: "SysPane Work Package"
title: "Installed inspector authored-input responsiveness"
description: "Qualify complete visible maximum authored scenes and explicit frame refusal on the real GTK loop."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T04:26:50+00:00"}
sp_id: "SP-W11-INSPECTOR-AUTHORED-LIMITS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-SCENE-INSPECTOR", "SP-W11-INSPECTOR-ASSETS", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed inspector authored-input responsiveness

Continue W-11 using the actual installed frontend, saved-profile transfer,
SceneSurface, native SceneInspector and the existing fixture-only timing observer.
No product environment override or alternate renderer is admitted. Freeze the
input recipe, exact row expectations and case table before product changes.

## Boundary and independent inputs

The existing authored limits admit 256 widgets, 16 hierarchy levels and 262144
serialized scene bytes. The renderer separately admits 262144 bytes of frame
strings/identities/typed chart storage; the inspector then admits at most 65536
semantic rows, 2 MiB of semantic strings and 258 levels. Do not confuse the latter
ceilings with reachable authored hierarchy or invent a successful blank scene.

Install a coherent offline revision-zero generation after clean profile creation,
using the original default theme and independently pinned scene/preset packages.
Preserve the initial generation. Inspection must preserve the selecting record,
all selected files, their exact bytes and the generation set. This is fixture
input, not an acknowledged configuration mutation.

The case recipe defines these independent axes on the owned 800-by-600 display:

- MAX-WIDGETS has 256 essential text widgets in a 16-by-16 grid, each with body L.
  All 256 exact native rows must appear. Each rectangle is 50 by 32 DIP.
- MAX-FRAME has 256 essential empty groups with four-byte IDs. Their titles are
  507 bytes for the first half and 508 for the second half. Each group contributes
  its four-byte ID, five-byte kind, title and identical accessible title: exactly
  262144 frame bytes in total. Both columns must preserve the complete strings.
- MAX-SCENE retains that complete maximum frame and fills ignored namespaced
  extension chunks to exactly 262144 authored bytes. This exercises both boundaries
  together; extension padding alone is not rendering qualification.
- MAX-DEPTH has sixteen independent chains, each fifteen groups and one text leaf,
  reaching sixteen authored levels and 256 widgets. Shift-Left on the first root
  hides exactly its fifteen descendants (241 rows); Shift-Right restores all 256.
  The selected root identity remains unchanged through both native key actions.
- OVER-FRAME adds one character to the first MAX-FRAME title, yielding 262146
  frame bytes. The scene remains structurally valid but the inspector must erase
  its rows/summary and report the existing explicit scene/display unavailability.

Additional NAVIGATION, REOPEN and POLICY cases use those maximum inputs. Verify
native keyboard selection and explicit summary; observe stable exact rows for at
least two seconds and ten GUI samples. Navigate through the existing Settings and
Edit scene modes, reopen the saved profile and clear policy-withdrawn content.
After confirmed controller exit, rows and requested summary must clear within
200 ms. Preserve current native child ownership and normal shutdown.
An intentionally incorrect maximum-widget title must fail the same exact-row
observer. Preserve the original baseline and this added hierarchy/oracle coverage.

These cases qualify authored/static frame limits. Maximum admitted live table/chart
semantic trees and updates, real assistive-technology usability and the other
platform adapters remain required performance/accessibility work. Do not label this
package as complete inspector performance or full release qualification.

## Timing, ownership and repair authority

Use the existing timing observer without changing its definition: each 20-ms host
tick's elapsed work and excess delay must be at most 100 ms. Retain every sample
from initialization, population, presentation, navigation, withdrawal and close;
no warm-up exclusion, percentile or averaging may hide a failure. The 75-second
observer case limit and 4096-record limit bound the test itself. Production does
not read the fixture observer environment variables.

Ordinary presentation remains a complete synchronous native transaction with no
main-loop entry or callbacks partway through. Policy/scene/resource replacement
and close still erase strings, identities, selection and summary in the owning
call. Any optimization must preserve these contracts, current resource/topology/
policy checks, exact row identities and all existing bounds. A prepared structural
snapshot never proves authority or rendering success. Do not add an unbounded
cache, disable content, reduce limits or extend timing deadlines to pass.

Run the baseline first, preserve failures and diagnose expensive phases before a
repair. Routine reversible implementation choices within this boundary are
delegated. A change to asynchronous presentation semantics requires a separately
closed contract and acceptance evidence; it is not an implicit escape from a
failed timing case. Privileged deployment and release remain reserved.

## Execution and completion

The preserved strengthened baseline fails OVER-FRAME, REOPEN and POLICY at
100766, 122129 and 100103 microseconds of tick work; NAVIGATION also records an
AT-SPI timeout. A separate phase diagnostic attributes the largest initial load
cost to Settings construction (up to 87641 microseconds), before inspection.
Its passing outcome does not supersede the original qualification failures.

Prepare one opaque SettingsDraft on the existing client worker after complete
authenticated profile transfer, alongside the existing prepared editor. Use the
same full constructor, resource validation and policy rules. No GTK object may
be created there. The backend owns at most one pending settings draft per current
profile; the form takes exclusive ownership once, only for the exact current
shared profile identity. A copied, old, loading, pending, withdrawn or closing
profile cannot consume it. Settings and editor consumption are independent.
Reload, submit, withdrawal and close discard any unconsumed result. Do not add
a queue, worker, revision cache, trusted validation flag or GUI fallback.

SettingsForm gains an opaque prepared-input constructor; the raw-input constructor
continues to run the same complete validation through that owner. Native controls,
callbacks, edits, submission, current-policy checks and erasure remain on the
owning GTK thread. No mutable draft alias escapes preparation. One additional
pending draft has the existing bounded settings/scene/resource state; transfer
does not duplicate it. Preserve the exact initial profile and all result semantics.

Freeze the seven prepared-settings ownership cases before the repair: one-time
consumption and independent editor ownership, reload/repeated reload, pending
request, policy withdrawal/restoration, controller restart and close. Then run
them, the original prepared-editor and installed Settings/inspector/editor/
recovery/telemetry/image/topology and GUI-limit checks. Run affected shared
settings and component checks on all three development profiles. Repeat the
separate phase diagnostic to measure the repaired boundary, and qualify the
original eight authored-limit cases without changing their observer or bounds.

After ordinary workspace preflight/configure/build, run:

```sh
ctest --preset linux-x64-gcc13 -R '^native[.]INSPECTOR-AUTHORED-LIMITS$' --output-on-failure
```

Retain the original installed image/topology, inspector, telemetry, editor/recovery
and GUI timing oracles. Run affected portable checks on all development profiles
for any shared-code repair. Capture source/artifact/oracle/environment identity,
the exact failing samples and passing results; archive each native family before
the next reservation. Update the existing W-11 row and handoff with the qualified
axes, unresolved cases and next dependency-ready work. All five complete native
release editions remain required.
