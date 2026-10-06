---
type: "SysPane Implementation Handoff"
title: "Measured network pixels and lifecycle in the owned GNOME shell"
description: "Original counters/rates, native age and independent lease/erasure observations."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:25:00Z"}
sp_id: "SP-GNOME-LIVE-NETWORK-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GNOME-LIVE-NETWORK", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Measured network pixels and lifecycle in the owned GNOME shell

From `8da0d83487f8e70f8f2071b0471cefbcfa0ae7df`, the owned GNOME experiment now
draws real measured network values and advancing age through the same asynchronous
`networkSession.js` owner tested in standalone GJS. The small drawing adapter uses
the native C++ projection's values, freshness and data-lease state. No second
JavaScript telemetry model or TTL calculation was introduced.

The [package](packages/w-25-gnome-live-network.md) fixes the independent pixel,
original-source, resource and lifecycle acceptance. The collector takes two native
samples and pauses acquisition while retaining its watch. Original source JSON and
pixel crops remain private. Public evidence records only hashes, source/artifact
identities, lifecycle facts and outcomes.

## Executed result

Nine source-identical cases are independently verified:

| Case | Observed result |
|---|---|
| Live | Exact counter/rate pixels, advancing original age and stale freshness while the data lease remains active |
| Frozen age | Fails age acceptance; values, freshness, lease and erasure still pass |
| Ignored expiry | Fails freshness acceptance while age continues correctly |
| Wrong value | Fails value acceptance without disturbing age/status or clearing |
| Ignored clearing | Fails erasure after typed policy revocation; final explicit cleanup removes all pixels |
| Data lease loss | Values remain visible while the independently expired lease and stale measurement are reported separately |
| Revocation | Native policy revision 8 clears actors before acknowledgement, followed by confirmed graceful source exit |
| Supervisor exit | A signal through the independently held pidfd ends the owned supervisor; its worker exits and pixels disappear |
| Worker hang | Independent health expiry forces the held worker to exit; the supervisor reports failure and the shell clears its tile |

The observer brackets original counters with native reads, derives rates from
original counter/time pairs, and decodes calibrated glyphs without diagnostic calls
during timed observation. Normal cases have at least 55 captures and three seconds
of age progression. Pixels have the specified 200 ms presentation allowance;
portable exact-boundary semantics are unchanged. Both descendant exits are observed
through held pidfds. The original icon manager and live marker survive each case.
Eighteen adversarial evidence checks reject altered originals, frozen captures,
missing erasure, forged exits, retained resources and changed outcomes.

The initial live attempt failed in the observer: it converted the independent
inventory's canonical string keys to integers before comparing source identities.
Keeping the original string keys fixes the harness. The failed report, original
sources and private capture hashes remain preserved; acceptance was not weakened.

The six public-clock, four retained-cache, three reveal, three surface-lease and
two optional-focus cases reproduce their established outcomes. Their 150 evidence
checks pass, alongside the 18 new network checks: 168 in total. The focus verifier's
explicit extension inventory initially omitted the two added/copied JavaScript
modules. It now requires their exact byte identities, with two added mutation
checks. Its rejected transcript and original verifier are preserved. A separate
coordinator exit-code expectation for observation mode was corrected; the native
report and independent focus oracle were unchanged. Default focus still fails.

Public evidence uses `build-support/evidence/w-25-gnome-live-network-`; the machine
handoff is `build-support/evidence/gnome-live-network-handoff.json`. Twenty-eight
native attempts include the first failed live run, the final nine network cases
and eighteen regressions. Source archives, public journals, original verifier
history and private artifact hashes make each result independently traceable.

Native C++ artifacts and target profiles are unchanged. The desktop runner and
existing clock/cache verifiers explicitly bind the tested live-session library,
typelib and collector record. Earlier records retain their original identities;
their historical outcomes are not rewritten. The full compiled suites and model
smoke packages remain evidence of their preceding checkpoints.

## Remaining boundary

This proves one finite operational tile in the owned GNOME X11 laboratory. It does
not qualify a complete desktop, protected policy deployment, general selection or
demand planning, suspension or namespace changes. The default Show Desktop focus
failure remains open, and optional focus integration remains disabled by default.

Next connect the existing independent render-progress guard to actual operational
rendering, defining progress evidence that cannot be satisfied by producer health
or static surviving pixels. Preserve current-policy erasure and held native exits
through renderer recovery. Continue Windows, historical guest and macOS tracks
when their required laboratories are admitted. Native settings, direct editing,
persistence and full recovery remain required for the first complete edition.
