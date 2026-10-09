---
type: "SysPane Handoff"
title: "Recovery admission investigation handoff"
description: "Candidate entry checks pass, repeated ordinary timing failures keep production recovery disabled."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T10:07:13.837163+00:00"}
sp_id: "SP-RECOVERY-ADMISSION-INVESTIGATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-RECOVERY-ADMISSION-INVESTIGATION", "SP-RECOVERY-SUBMISSION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Recovery admission investigation handoff

Production recovery and prepared-history admission remain disabled. The
[admission package](packages/w-11-production-recovery.md) is unfinished: functional
candidate checks pass, but two unchanged ordinary GUI attempts fail qualification.
The [investigation package](packages/w-11-recovery-admission-investigation.md) keeps
that gate closed and separates fixture observer support from candidate admission.

Only the two development fixtures define SYSPANE_EXPERIMENTAL_RECOVERY=1. Only
syspane_frontend_fixture also defines SYSPANE_FRONTEND_TEST_OBSERVERS=1. The new
syspane_frontend_entry_fixture uses the same entry source and runtime with candidate
admission and the existing fixture helper identity, without observer support. It is
not the production binary and is never installed. Production ignores all three
SYSPANE_TEST_TIMING/PHASES/PHASE_FAULT variables and retains its disabled gate.

## Evidence and failed qualification

The [checkpoint](checkpoints/recovery-admission-investigation.json) binds complete
source archives, native recordings, exact artifacts and both failed ordinary runs.
The original package and test inputs were frozen before the candidate change. The
initial ordinary-entry baseline failed because the old production gate was disabled.
The enabled candidate then passed all fourteen original recovery and twelve settings
cases with hostile observer variables, including an invalid phase fault. Recovery
emitted no observer records. The settings oracle also exercised actual production
refusal of missing protected policy and substituted helper identity.

The candidate campaign passed 144 selected portable checks on three development
profiles and 141 distinct native functional cases across twelve families. That count
excludes ordinary GUI qualification and the seven-case paint diagnostic. The first
GUI attempt passed six cases and failed one; its single predeclared confirmation
passed five and failed two. Both work and excess-delay bounds remain 100000 us.

| Ordinary attempt | Failed case | Maximum work (us) | Maximum excess delay (us) |
|---|---|---:|---:|
| 1 | MAX-WIDGETS | 76999 | 108851 |
| 2 | MAX-RECORD | 112718 | 102714 |
| 2 | MAX-WIDGETS | 77169 | 102235 |

These are failures, not qualified passes or waived noise. Policy erasure passed both
attempts under its unchanged 200 ms bound. The preceding recovery-submission run's
seven passing cases remain valid historical observations and do not erase these.

The paint diagnostic completed its seven scenarios and identifies native composition
in restore/history callbacks and drawing. Its instrumented durations do not qualify
latency. Allocated observer code/data match the preceding passing artifact except
the ELF build ID; this does not establish the cause of delay. An isolated pointer
pixel-packing candidate preserved exact output and saved about 2 ms at 786432 pixels
in the pinned debug profile. It was not adopted as a product fix. Its initial
warnings-as-errors compile refusal and corrected probe are both preserved.

## Final closed gate

Linux entries were rebuilt at profile revision 70 after the failed confirmation.
Production and the candidate entry main differ only in the admission argument at
the call boundary; generated helper identities differ separately. Compile/link
commands and all 42 common library identities are recorded. Final production loaded
code/data match the preceding committed disabled production build, and both final
fixtures match their experimentally tested artifacts, apart from ELF build IDs.
This is explicit equivalence evidence, not a claim that every native suite reran.

After closure, all twelve settings cases, including actual production policy/helper
refusal, were rerun successfully, and all six component graph checks passed after
configuration on the three profiles. Windows GCC 39 and v141_xp 30 portable artifacts
remain identical to the preceding rebuilt checkpoint. These are development host
results, not historical Windows guest qualification or protected-policy deployment.

Local recorder errors are retained: a runner dictionary syntax error caught before
execution, and a Git mount-ownership refusal while recording initial parity. The
latter used a command-scoped safe.directory correction; global Git and credentials
were unchanged. Complete native attempts were archived and byte-verified before
reclaiming duplicate owned directories under the unchanged 8 GiB active allowance.
Archives and bindings stay ignored in out/; shared tooling remains in source/build/.

## Next boundary

Attribute MAX-WIDGETS between-callback delay and MAX-RECORD callback work using the
existing phase/paint tools and fixed maximum-input recipes. Select a measured repair
that preserves pixels, geometry, current authority, erasure and native lifetimes
before running ordinary qualification again. Do not repeat unchanged runs until a
pass appears. Resume production admission only after its unchanged gate is satisfied.

General authoring/preview responsiveness, native inspector, telemetry/desktop and
lifecycle integration, protected deployment, other adapters and all five complete
0.1.0 editions remain open. W-11 remains in progress.
