---
type: "SysPane Handoff"
title: "Inspector image launch follows current GUI adoption"
description: "Preserve literal loading before observable child creation and drain cancelled native work honestly."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T18:23:05.073338+00:00"}
sp_id: "SP-INSPECTOR-IMAGE-ADOPTION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-BACKGROUND-INSPECTOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector image launch follows current GUI adoption

The background inspector queues an image task before starting its native child.
GTK acknowledges the latest transferred ticket only after current-result guards
and native presentation succeed. The original worker-owned factory then launches
under that ticket. Visible image loading therefore precedes observable child
creation. Cancellation before adoption creates no child; cancellation during
launch or decoding retains the original real-child drainage requirement.

The [existing W-11 package](packages/w-11-background-inspector.md#bounded-image-loading-order-investigation)
owns the interface, failure and resource rules. This refines the current worker,
not the work graph or synchronous surface behavior. At most one existing bounded
image input/factory is queued. Installation verification, actual-launch decoder
deadline, pixels, current authority and the fixed native oracles remain.

## Reproduced boundary and controlled checks

The baseline native.BACKGROUND-INSPECTOR run fails its new controlled assertion:
`loading native row must precede observable image child`. Its factory creates a
real child and holds the worker before returning. The GTK tree is still empty.
The exact baseline source, CTest failure and child/native recording are preserved
locally; this reproduces the ordering defect independently of the preceding
installed failure, without claiming that failure's complete cause.

After the repair, native.INSPECTOR-RENDERER and all seven background native cases
pass. The controlled GTK probe checks the exact `Image title` /
`Public image\nImage loading` row while a real child exists and its factory is
held. Closing erases the row and acknowledges only actual child disappearance.
Renderer cases reject untransferred/superseded/foreign/closed adoption,
retain no-child cancellation and the exact post-adoption installation refusal.
Factory polling outside claimed composition now reports running honestly.

Review found that notification was inside the enclosing measured adoption action,
before its observer accepted completion. Notification now follows that acceptance.
Four controlled presentation/adoption refusal/throw cases hold the observer for
30 ms and verify zero native factory invocations, immediate erasure and drainage.
The first passing candidate and its recorder are preserved separately; reviewed
source qualification must use its own artifact identities.

## Native regression evidence

The first candidate passes all twelve installed image/topology cases with the unchanged Python oracle,
including HELD-NAVIGATION, HELD-CLOSE, real logical monitor restoration and the
deliberate wrong-value control. The original inspector, installed telemetry,
authored-limit family and all seven ordinary maximum-table cases also pass.
The complete phase diagnostic passes all seven cases with strict journals. Ordinary
GUI work/delay peak at 83.406/67.125 ms; phase work/delay peak at
77.107/69.288 ms. Policy erasure measures 102.071/86.666 ms respectively,
within the unchanged 100-ms GUI and 200-ms erasure limits. Those first-candidate runs do
not reproduce the preceding AT-SPI timeout or establish its cause.
Recovery GUI limits, phase-refusal handling, three native table-erasure cases and
all 146 selected Linux shared checks pass. The
[checkpoint](checkpoints/inspector-image-adoption.json) preserves the first candidate's
fifteen executions and eleven byte/type-verified native archives, alongside the
reviewed source's evidence: twenty-eight executions and twenty-one archives in
total, exact source/artifact/environment identities and all 27 unchanged oracle
hashes. Linux development profile 82 is
the scope of these results; no Windows, historical guest or Mac qualification is
inferred. Raw evidence remains local and ignored. Keep W-11 in progress.

The source refined after the phase-observer review passes controlled worker/GTK
checks, including all four refusal/throw cases. Its installed family passes eleven
cases, including HELD-NAVIGATION, and fails HELD-CLOSE at the unchanged 62-second
observation deadline. The observer records the verified image executable with
empty argv and then never finds an eligible held child. This is an identity
observation failure, not a successful stopped-child/shutdown proof. Preserve the
exact failed recording and first candidate's twelve-case pass; current installed
qualification remains open. The reviewed source passes both seven-case ordinary
and complete-phase table runs, original inspector, installed telemetry, eight
authored-limit cases, seven recovery GUI cases, two phase-refusal cases, three
table-erasure cases and all 146 selected Linux shared checks. Reviewed ordinary
work/delay peak at 73.724/66.807 ms; phase work/delay at 71.072/64.160 ms.
Policy erasure measures 87.891/77.498 ms respectively. Original timing limits and
strict complete-journal analysis remain. These passes do not establish the
preceding intermittent timeout's cause.
The [preceding checkpoint](checkpoints/background-inspector.json) retains the
installed HELD-NAVIGATION and TOPOLOGY failures, ordinary AT-SPI timeout and all
earlier timing/diagnostic failures. A controlled pass is not installed, human
accessibility, physical hotplug or desktop qualification.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.

## Next admitted work

The later [child identity follow-up](child-identity-handoff.md) records the
collection correction, twelve passing installed image/topology cases and a new
authored MAX-FRAME timing failure. This checkpoint and its original failed
HELD-CLOSE observation remain unchanged evidence of the preceding source/oracle.

Close the reviewed HELD-CLOSE identity observation failure and investigate the
preceding native AT-SPI timeout and child-observer exit race
without claiming their causes from these passing runs. Preserve failures and exact
sources before selecting another repair. Qualify maximum native GTK chart/mixed histories,
actual installed accumulation, human accessibility and desktop/lifecycle
composition. Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X still require
their complete editions and release evidence. Generated recordings stay in ignored
out/; shared build tooling stays in source/build/.
