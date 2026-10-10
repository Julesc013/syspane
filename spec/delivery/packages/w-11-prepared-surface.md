---
type: "SysPane Work Package"
title: "Prepared authored state for native editor previews"
description: "Move repeated preview structure validation to existing preparation workers."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T14:10:00+11:00"}
sp_id: "SP-W11-PREPARED-SURFACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-VALIDATED-AUTHORED", "SP-W11-INSPECTOR-TELEMETRY", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared authored state for native editor previews

The installed telemetry checkpoint preserves ordinary GUI failures at 110421 us
delay and 116786 us work against 100000 us. Diagnostic attempts measured restore
and editor construction/population close to that limit without reproducing those
failures. The current fixed preview-cost diagnostic measures raw surface creation
at 42304/38565 us for MAX-WIDGETS/MAX-SCENE. The latter yields an alternative, not
a successful rendered scene. Source inspection shows preview construction repeats
structural validation after initial, history and recovery preparation.

## Ownership and behavior

Reuse the existing opaque `ValidatedAuthored` owner. Prepare its deep, const,
fully validated copy on the existing initial editor, history and recovery workers.
It proves only document structure and coherent revision. Transfer it with the
same exact candidate, after existing current-owner, policy and revision checks.
Do not introduce a trusted boolean, skip-validation constructor or new worker.

EditorDraft may retain one optional current authored snapshot. Selection alone
does not invalidate document structure. Mutation, request preparation, policy
change, disconnect, reload, discard and close release it through the existing
invalidation boundary. Detached copies start without that cache. Rejected/stale
results cannot install a snapshot. A consumer must release its copy on withdrawal;
structural ownership never confers permission to disclose retained documents.

SurfaceConfig accepts either its existing raw authored pair or an optional opaque
authored snapshot. A snapshot requires both raw documents to be null; mixed sources
fail with `surface.authored_source`, even if their bytes would match. A moved-from
snapshot fails with `authored.snapshot`. This explicit choice avoids approximate
JSON equality, numeric-type coercion and an ambiguous authoritative document.
The raw path retains its existing complete validation and error order.

The snapshot path still checks the current resource binding, topology, metrics,
text setup, capabilities and policy. All paint, pixel, source lease, visibility,
image lifetime and erasure checks remain. Replacement validates before adopting
configuration and proof together. Existing clear/history invalidation on failed
replacement remains unchanged. Editor previews without a prepared snapshot retain
the raw path. This repair does not cache frames or permission decisions.

## Limits and authority

Keep settings/scene/widget/history limits and the 100-ms GUI and 200-ms erasure
oracles unchanged. A detached candidate may add one bounded authored copy (up to
16384 + 262144 serialized bytes, plus JSON heap overhead). The adopted editor and
surface share that const allocation; no revision-indexed cache is permitted.
Existing bounded task slots, cancellation and actual-stop requirements still apply.
Routine helper organization is delegated; protocol changes, privileged deployment
and release qualification are outside this repair.

## Fixed verification

Freeze portable snapshot lifetime/adoption assertions and native surface tests
before product edits. Cover exact restored/history documents, selection, edits,
policy loss, close and stale results. Cover identical native output on both input
paths, retained mutable caller aliases, mixed sources, moved-from owners, changed
resource binding/topology and policy erasure. Keep all original expected outputs.

Run the existing maximum-input preview-cost diagnostic before and after, adding
separate prepared-validation and prepared-surface spans. Its expected states remain
degraded for MAX-WIDGETS and alternative for MAX-SCENE; timings do not qualify GUI
responsiveness. After a measured implementation repair, run the unchanged ordinary
RECOVERY-GUI-LIMITS suite once and preserve its outcome, including any failure.

Use ordinary workspace preflight/configure/build. Run affected portable editor,
settings, configuration, scene and component checks on all three development
profiles and retain historical artifact checks. Run native surface/render/erasure,
editor/history/recovery/preparation and installed consumer regressions, including
live inspection. Record actual source, artifacts, environment, commands and failed
attempts in a handoff. This package advances W-11; all five complete editions and
the separate installed inspector qualification remain required.
