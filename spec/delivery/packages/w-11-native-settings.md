---
type: "SysPane Work Package"
title: "Native settings drafts and transaction results"
description: "Connect every initial settings descriptor to native controls and the common authored transaction boundary."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T02:05:00Z"}
sp_id: "SP-W11-NATIVE-SETTINGS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SETTINGS", "SP-COMMANDS", "SP-CONFIG-RESOLUTION", "SP-W11-SCENE-INSPECTOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native settings drafts and transaction results

Continue admitted W-11 with a portable settings draft and an embeddable Linux GTK
form. Use the eleven canonical descriptors, the shared authored validator and
command/result identities, and the existing asynchronous command owner/native
generation store. No parallel settings engine or synchronous filesystem work on the
UI loop. Windows/AppKit adapters, installed routing, persistent layer reset, full
editor operations and complete release qualification remain required work.

## Registry and native controls

Extend the existing generated descriptor table with default, page, units, activation,
label/help localization IDs and English fallback text from the canonical registry.
No second hand-written constraint table. Reject unsupported metadata during
generation. Keep existing descriptor IDs, types, ranges and defaults unchanged.
Use native labelled boolean and plain text controls, with canonical unsigned decimal integer
parsing and identifier validation through the shared command validator. Invalid
input remains visible with an inline error and cannot be committed; never clamp,
truncate a number to the allowed range, interpret an empty field as zero or use a
floating-point round trip for integer input. Reject signs, whitespace and leading
zeroes except the single digit zero. Limit each entry to 256 characters.

Every descriptor is discoverable by friendly label or invariant identifier. Search
filters rows without changing draft state. Native labels, descriptions and keyboard
focus expose setting identity, help, units, activation scope and policy lock. Show
requested and effective values distinctly when current policy forces a setting;
the control is insensitive with an explicit policy reason. Native theme/scaling
applies. Translation callbacks take stable message IDs and bounded plain UTF-8
strings; complete locale formatting and human accessibility review remain open.

Native text selection must not implicitly publish authored values to PRIMARY or
CLIPBOARD. Use GTK TextView buffers with automatic selection publication removed;
block copy/cut and drag export, including native accessibility copy/cut operations,
until a separately admitted clipboard owner is connected. Selection and editing
remain available. Bound incoming plain text before insertion; do not install rich
text handlers. Independently request both X selections after select/copy attempts.
This detail follows the pinned [GTK selection clipboard API](https://docs.gtk.org/gtk3/method.TextBuffer.remove_selection_clipboard.html).

Use built-in default writes that descriptor's explicit value into the draft. It is
not inheritance reset. Revert draft restores the accepted authored settings exactly
and writes nothing. Persistent layer deletion/reset remains owned by the existing
resolution contract and must not be represented by assigning a default.

## Draft and request state

One serialized owner constructs a draft from validated coherent Authored documents,
authenticated Authority, current Policy and producer epoch. Preserve document
extensions and the scene unchanged. Disclosure requires operational inspector and
accessibility grants. Editing additionally requires the existing writer/preview/
settings.set checks; Apply rechecks settings.commit through the shared authorizer.
Only changed settings become operations, in registry order. Preview and Apply use
command 0.2, the base revision and current policy generation; no content selection
or private native-store mutation. A clean draft emits no transaction.

The caller supplies globally fresh request IDs within its existing producer scope.
Each submission has a monotonically increasing local ticket and exact immutable
body. At most one request is active per draft, including unresolved results. During
submission, edits, defaults, Revert and further Preview/Apply are disabled. Native
callbacks enqueue work and return; the owner invokes completion later. A callback
exception is ambiguous delivery and requires result retrieval, never an automatic
new request. The shared command owner remains the sole ledger and storage authority.

Cancel request requests cancellation of that exact active identity and remains
pending until a result arrives. It does not restore storage or report success.
Closing the form erases local draft/control state and cannot undo a submitted
transaction. The external request owner retains cancellation/reconciliation duties.

Validate bounded result 0.1 structure and facts, then match local ticket, request and
producer epoch before accepting completion. Ignore stale tickets without changing
the current draft. A malformed or mismatched current result becomes unresolved;
it cannot unlock a new commit or claim success. `unknown`, disconnect and pending
results retain that exact active identity for retrieval/reconciliation. No blind retry.

Current-policy result concealment is also unknown: when settings.commit is revoked
while preparation is held, delivery returns unknown/policy.denied with null revision,
stored, durable and visible facts. The independent storage oracle still requires
revision 40 unchanged. Regrant does not resolve the request: retrieve its original
identity, observe the retained conflict/policy.changed result, then explicitly reload.
The initial native oracle incorrectly expected a disclosed terminal rejection here;
preserve its failed run and original bytes. This correction follows the existing
AsyncCommands query contract; it changes neither publication nor disclosure policy.

Preview writes nothing and retains the draft. Accepted commit requires the original
base revision plus one, stored/durable true, visible false and the existing pending
presentation activation record; advance both local documents to that exact revision.
Do not claim visibility or activation from durable storage. Other terminal outcomes
preserve the draft and their explicit reason. Conflict requires an explicit fresh
snapshot reload; never silently rebase or change expected_revision and retry.
Explicit Reload discards the draft only after no unresolved request remains.

Policy generation must increase; rollback/reuse makes policy unavailable. Re-evaluate
locks immediately. A policy change before publication remains subject to the existing
commit guard. Loss of inspector/accessibility disclosure clears all local authored
values, controls, errors and result text in the same call; keep only bounded request
identity needed by the external owner. Regrant alone cannot restore cached values;
require a fresh admitted snapshot. An accepted late result cannot repopulate revoked
controls. Invalid state and close fail closed.

## Executable acceptance

Preserve literal descriptor values, exact expected documents and transition outcomes
before implementation. Bind the settings family to portable DRAFT, VALUES, DEFAULT,
PREVIEW, COMMIT, CANCEL, CONFLICT, POLICY, RESULT-SCOPE, UNKNOWN and BOUNDS cases on
all three development profiles. Preserve uint64 revisions and the unchanged scene,
prove no-op suppression and exact request retention, and compare commands with the
ordinary transaction API. The native form is not its own storage oracle.

On the owned unprivileged Linux ext4/Xvfb/private-D-Bus lab, independently enumerate
all eleven actual native controls through AT-SPI, enter values, send native keys,
invoke Preview/Apply/Revert/default/cancel, and observe labels and sensitivity.
Use the actual AsyncCommands worker and LinuxGenerationStore. Hold preparation to
prove responsive pending/cancel/policy behavior. Read selected settings/scene bytes
independently after commit and reopen to prove persistence. Test a stale revision,
policy change, lost acknowledgement and explicit retrieval without a duplicate
commit. Retained-value and premature-saved deliberate controls must be detected.
Also throw from a submission callback after enqueueing its request: keep the form
unresolved while the worker is held, then retrieve the original committed result.
Keep the existing 200 ms revocation observation bound. Capture failures and native
artifact/runtime/source/oracle identities. Do not equate AT-SPI checks with human
screen-reader review or modern-host compiler checks with historical OS support.

Use ordinary preflight/configure/build/test presets. New `settings.*` portable and
`native.SETTINGS-FORM` cases accompany affected configuration/policy/dependency
checks. Preserve the concrete next work boundary and all unresolved edition gates.

Record descriptor-to-control/command/test coverage in the existing experience
specification area. Distinguish this owned Linux component from installed product,
CLI, Windows and AppKit coverage; keep full-release coverage pending.
