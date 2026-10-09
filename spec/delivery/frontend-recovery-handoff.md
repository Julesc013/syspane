---
type: "SysPane Handoff"
title: "Frontend recovery authority and accepted-request identity"
description: "The actual frontend backend now supplies scoped native admission and exact accepted-draft metadata."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T02:55:28.137718+00:00"}
sp_id: "SP-FRONTEND-RECOVERY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-FRONTEND-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Frontend recovery authority and accepted-request identity

LinuxFrontendBackend now negotiates profile 0.2 and allocates a fresh editor session
for each authenticated download. The existing helper worker receives a native
admission factory whose callback reads the actual current connection, profile,
session, authored revision and policy. Submission, reload, disconnect, policy loss
and close withdraw that admission. No additional worker or scheduler was added.
The existing recovery and preparation factories are available to native consumers.
The installed EditorForm has not yet connected them and recovery remains disabled.

An optional captured digest accompanies the existing pending request. Before dispatch,
the client worker reconstructs its canonical recovery envelope from the actual scene
commit and original profile/generation; the digest and revisions must match. Unknown
outcomes preserve bounded original-request metadata. Only authenticated accepted
results, including reconciliation after controller replacement, create a retirement
receipt. No record bytes or second request ledger are retained for this purpose.

A fresh profile exposes that digest only at the accepted revision, under a changed
generation and the same original native directory identities, with current retention
and erase permission. The native consumer loads under fresh admission and compares
the file digest before conditional retirement. Replaced/kept records and denied
deletion remain intact. Acknowledgement requires the current profile serial and an
issued receipt; absent, stale and repeated acknowledgements fail. This metadata is
not authority to delete or proof that deletion completed.

The [frozen package](packages/w-11-frontend-recovery.md) and literal command precede
production edits. The [checkpoint](checkpoints/frontend-recovery.json) binds actual
commands, source archives, installed fixture artifacts and outcomes. Its 14 new native
cases run the real backend with its existing two workers in a relocated verified
bundle. Independent observations compare selecting-record hashes, native directory
identities, exact recovery bytes and saved scenes. They cover null admission, capture,
stale scope, invalid metadata, accepted/lost/unknown results, kept/replaced records,
erase denial, directory substitution, policy loss, closure and a wrong oracle.

The final new family completes 14 backend instances without
forced cleanup; observed children exit and each owned runtime allocation retires.
Its 5821 measured consumer calls take at most
8967 microseconds under the unchanged 100 ms fixture
bound. These measurements do not qualify full GTK or maximum-size scheduling.
Six native report families contain 82 named cases, including unchanged installed
settings/editor and helper/admission/preparation regressions. Both component-graph
checks pass on all three development profiles. Unchanged portable implementations
were not rebuilt or requalified by this Linux-only backend change.

Two failed fixture attempts remain preserved. The first used a runtime base longer
than the existing 50-byte limit and startup refused. The corrected fixture uses the
established owned runtime. The next placed its preserved substituted directory inside
the profile's strict three-entry state root, so restart correctly refused. That old
node now stays elsewhere in the same owned case directory; the identity and exact
non-deletion expectations are unchanged. No deadline, product limit, frozen input
or expected outcome was relaxed.

Completed recordings were archived and verified byte-for-byte and node-for-node
before duplicate removal, after checking for live owners. Four older owned recording/
runtime archives preserve 49708770 raw bytes.
Hardlinks mean that archived bytes are not a claim of equal reclaimed capacity.
The 8 GiB active-output budget and its ordinary reservations remain unchanged. Raw
evidence and machine settings remain ignored under out/.

Next connect EditorForm's durable captured digest to submission and consume accepted
receipts through fresh current admission. Close/reap the old task before rebinding,
preserve kept/replacement records and acknowledge only after the retirement decision.
Qualify the complete supervisor/helper loop and maximum-size GUI operations before
enabling installed recovery. Native inspector, telemetry/desktop/lifecycle and all
five complete release editions remain required. Earlier Windows resource-limit and
installed AT-SPI focus timeouts remain unexplained despite passing regressions.
