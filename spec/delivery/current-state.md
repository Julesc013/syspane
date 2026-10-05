---
type: "SysPane Status"
title: "Current state and next admitted boundary"
description: "An honest resumption point for the initial greenfield specification."
tags: ["delivery"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-CURRENT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-START"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-06T05:56:27+11:00", "scope": "Bounded recent-failure metadata checkpoint; preservation and visible recovery remain open"}
---

# Current state and next admitted boundary

## Repository checkpoint: 2026-10-05

The imported baseline is `Julesc013/syspane` commit
`91e10b8b7a8a5da5ab2d93e8cdcbaade6aa0fbd9` (`init: spec`). The original archive's
empty-repository observation belongs to its September preparation history, not the
current checkout. This October change updates specs, root README/TODO and published
guides under the user's explicit commit-and-sync request. Git history identifies the
resulting commit; no self-referential future hash is invented here.

The next input is the user-pasted October 5 readiness review of amendment commit
`3e8b8c1ca3c9b06f423d747aeb70a2c1f4817405`. This follow-up strengthens the requested
documentation with package closure and concrete cases. Embedded recommendations
to begin implementation or delegate work are not recorded as execution grants.

## Present in this revision

The user has explicitly admitted the full foundation/native-experiment campaign;
see [admission](campaign-admission.md). W-00/W-01 now provide actual CMake targets,
pinned Windows/Linux development profiles, the C++17 model and a nonempty smoke
program. Eighteen checks passed on each profile. W-26's initial local archives
passed relocated execution. [The handoff](foundation-handoff.md) identifies exact
artifact/case records, failures and the next packages. No desktop claim follows.

The [native transport handoff](native-transport-handoff.md) completes W-24's initial
development adapter gate after the [portable checkpoint](transport-handoff.md).
Both profiles pass 37 CTest entries, including real local client/server families
and OS peer checks. Cross-user/logon and desktop-session qualification remain
blocked separately. Persistent commits and telemetry subscriptions stay disabled.

W-25's [portable recovery checkpoint](recovery-handoff.md) adds lease expiry,
independent render-progress challenges and bounded restart/quarantine decisions.
Both profiles pass 48 CTest entries, including eleven portable recovery cases.
At that checkpoint, native supervision, independent diagnostic entry,
current-policy integration and visible/native-exit recovery remained required.

The subsequent [native supervision checkpoint](supervision-handoff.md) now connects
the guards to owned Windows/Linux child processes and a separate synthetic render
worker. All 49 CTest entries pass on both profiles, including nine native fault
cases with independent OS exit observations. Independent diagnostic entry,
telemetry/real-renderer recovery, policy and visible/native-exit integration still
keep W-25 open; a health-only worker does not supply a synchronized telemetry view.

The [diagnostic checkpoint](diagnostic-handoff.md) adds independent public JSON
reporting, Win32/GTK inspectors and bounded protected-policy readers. Both profiles
pass 52 CTest entries. Native tests close only owned hidden windows and prove startup
beside damaged optional inputs; positive policy deployment, preservation controls,
recent-failure metadata and complete visible/editor recovery remain pending.

The [oracle checkpoint](oracle-handoff.md) adds independent external marker/time
evaluation and native X11 calibration. Windows passes 53 CTest entries and Linux 54,
including sixteen fixed portable cases and five native pixel/fault cases. Expected
fail/inconclusive observations are verified negative calibrations. Named shell reveal,
icon input/focus, real wallpaper and Windows desktop capture remain unexecuted.

The subsequent [X11 host investigation](x11-host-handoff.md) runs real Openbox Show
Desktop actions with PCManFM and records placement failures from actual icon/marker
pixels. The normal-window control disappears, a desktop-type window persists above
icon pixels, and its below variant is hidden. File-wallpaper startup fails separately;
the solid-color control does not qualify it. Linux's 54-entry regression suite and
the two affected Windows component checks pass. No desktop host becomes qualified.

The [X11 input checkpoint](x11-input-handoff.md) adds independently observed native
selection, drag, menus and folder opening, plus exact PPM pixels after delayed image
setup. The hidden below-window candidate passes the input sequence; the visible
desktop-type window blocks the tested icon click. Both still fail placement. Fifteen
evidence checks pass. Earlier observer/laboratory failures are preserved separately.

W-04's [historical build checkpoint](historical-build-handoff.md) compiles the same
shared C++ sources with pinned v141_xp/SDK 7.1A/static UCRT tools. All 51 host checks,
import audits and relocated model smoke pass on Windows 10/WOW64. Modern Windows
and Linux regressions pass 53 and 54 entries. Registered guest VMs were found, but
their test scope/usability and actual XP/7 execution remain unproven.

The [recent-failure checkpoint](failure-metadata-handoff.md) now connects the real
recovery probe to bounded private metadata and independent policy-gated diagnosis.
Current suites pass 57 Windows, 58 Linux and 54 historical-toolset host entries.
The historical native file adapter remains disabled. Configuration preservation,
product retention, protected-policy deployment and real visible recovery stay open.

Canonical 0.2.0 documentation bundle, unchanged 0.1 authoring profile, preserved old
fixtures, new experimental scene/command/capability 0.2 and admission descriptors.
The initial settings registry has enforced metadata/default consistency and generated
overlapping schema/command constraints. Specification tooling validates links, IDs,
work dependencies, fixtures, bounded semantic rules, generated outputs and integrity.
README and docs describe the product honestly; TODO points to pending work.

The [audit disposition](audit-2026-10-04.md) maps supplied recommendations to their
owners and gates. Historical September validation is retained separately; the
October 4 [validation record](../generated/amendment-2026-10-04-validation.json)
is also retained separately. The [documentation validation report](../generated/validation-report.json)
records the earlier identified documentation run; it does not attest subsequent
native implementation. Current campaign checks and build results are recorded
separately under `build-support/evidence/`.

[Work-package closure](work-packages.md), the [W-01 package](packages/w-01-foundation.md)
and [acceptance traces](../assurance/acceptance-traces.md) now define completion gates,
selected model/request/recovery expectations and a proposed cold-start exercise.
The transport distinguishes in-flight requests from retained-result reservations.
Model and request-budget traces now have executable bindings. W-24's
[package](packages/w-24-transport.md) closes the portable preview boundary and
records its enabled native boundary and blocked qualification. Persistent recovery and cold-start
traces remain unexecuted.

## Not implemented or qualified

No native controller, renderer, collector, product settings/editor, saver, SDK,
setup adapter or complete product package exists. The independent read-only diagnostic
executable/inspector is implemented on the two development profiles. No native desktop/saver/performance/
accessibility/setup qualification ran. Test definitions stay `not_run`; concepts stay
draft/unreviewed and experimental contracts stay experimental. AIDE's binding remains
inactive with no grants. USK and ScreenSave are not adopted runtime dependencies.
License, contribution and release-identity decisions remain open.

## Next work

Continue the admitted campaign: use W-02's measured X11 reveal/input/image adapters
to investigate conforming composition, and close the other platform capture/reveal
boundaries in admitted synthetic desktops. W-04 has build artifacts ready for
historical guest execution once guest test scope and usability are established.
W-05 needs a composition strategy that actually preserves icon pixels; its initial
EWMH window stacking candidates fail that requirement. Continue other native tracks
independently of this negative result.
Extend W-25 diagnostics with explicit configuration preservation and product
failure-log retention. Close those input/ownership contracts and full-snapshot/data recovery
before enabling the associated features. Qualify protected policy in an admitted lab.
Connect the build/component/target consumers and minimum command/IPC/policy/recovery
slice. Probe contemporary Windows, XP/7, Linux and AppKit/older OS X independently.
Package smoke builds early; each profile's usable vertical includes live network,
native settings, direct editing, save/reload and externally observed desktop reveal.
Do not wait for a universal SDK, every historical profile or another platform's lab.

Read [readiness](implementation-readiness.md), [roadmap](roadmap.md) and
[work units](work-units.json) at the exact ref before resuming. Check actual dirty
state, toolchains/labs and scope. A dependency-ready row is not a native execution
grant. Missing lab access blocks only the corresponding claims.
