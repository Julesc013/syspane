---
type: "SysPane Work Package"
title: "Bounded editor recovery drafts"
description: "Generation-bound unsaved scene intent restored explicitly through the existing draft and transaction owner."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T13:08:27+00:00"}
sp_id: "SP-W10-RECOVERY-DRAFT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-EDITOR", "SP-PERSISTENCE", "SP-W10-EDITOR-DRAFT", "SP-W10-THEME-HISTORY", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded editor recovery drafts

Implement the recovery prerequisite in the existing EditorDraft. A recovery record
contains unsaved scene intent. Reading or restoring it never commits configuration,
increments its revision, starts a request, activates a desktop surface or imports a
package. Apply uses the ordinary transaction owner with a fresh request identity.
Keep the accepted generation intact. This package closes shared semantics and the
requirements for the following native storage/UI integration; W-10 remains open
until that integration and the complete editor requirements pass.

## Admission and ownership

The trusted resource context must explicitly include editor.recovery and the
existing large-command admission. Native Authority must be authenticated with its
desktop or console role granted. Current Policy must be available, must grant
history/sensitive disclosure, and must not deny editor.recovery. Existing inspector,
accessibility, preview, scene replacement, resource and version capabilities still
apply. Changed font intent requires current theme-edit authority. Stored policy
generation, role or other caller data is never a grant.

Capture, inspection and restoration require a quiescent editable draft: no active
request, unknown result, conflict, unavailable state or close. Capture returns no
record when clean. Inspection/restoration additionally require a clean draft with
empty undo/redo stacks, so a delayed offer cannot overwrite newer local work. A
selection on an otherwise pristine draft is allowed. No implicit discard or rebase.

The native owner supplies RecoveryIdentity: profile is a bounded protocol identifier;
generation is exactly 64 lowercase hexadecimal characters identifying the currently
accepted generation. It remains stable across a controller restart and must change
if any accepted documents, revision or resource identity changes. Native storage
must derive it from its verified selecting record/manifest, never from the recovery
file or an untrusted client. An example generation token is data, not provenance.
The private profile root and authenticated owner establish user/session scope.

RecoveryIdentity must match exactly on inspection and restoration. A restored
generation 41 rejects an old generation-40 draft even after a lost acknowledgement;
it must never silently reapply that change as revision 42. Stale/conflicting bytes
remain available to their authorized storage owner for diagnostics and an explicit
later decision. This operation does not invent merge semantics.

## Record shape and bounds

The new editor-recovery 0.1 JSON document has exactly format, schema_version,
identity and command. format is syspane.editor-recovery; identity has exactly profile
and generation. command is a UTF-8 string containing an existing complete command
document, rather than a nested command object. This keeps the command's established
depth/node accounting independent of its storage envelope. The accompanying schema
fixes the envelope; existing command and scene validators fix its contents.

The record is at most 786432 bytes before parsing, including whitespace. Its decoded
command is at most 327680 bytes and receives the existing version-specific command
limits, duplicate-key rejection, UTF-8, 40-level/18432-node large-command checks and
all semantic validation. The envelope uses the existing 32-level/16384-node parser.
Whitespace outside the envelope may be stripped only after the byte check. No BOM,
unknown field, invalid identifier, malformed generation, unsupported version or
oversized nested string is accepted. Capture uses compact sorted-key JSON, with
UTF-8 preserved; there is no base64, binary payload, absolute path or executable.

The stored command has intent preview, request_id editor:recovery, the capture-time
policy generation and expected accepted revision, exactly one scene.replace, and
the ordinary content selection. No settings operations, package import, arbitrary
request identity or commit intent is allowed. Existing command versions and their
limits do not change. Capture verifies that the complete command is representable;
it does not truncate a large scene or drop properties to make a snapshot fit.

Selection, undo/redo history, private un-applied property buffers, clipboard content,
live observations, pending requests and authorization objects are excluded. The
scene retains all authored objects, hierarchy, coordinates, bindings, pins, locks,
visibility and opaque widget extensions. Scene identity, revision and other root
metadata stay equal to the accepted baseline; only schema_version, theme_id, roots
and widgets may differ. Scene 0.2 stays 0.2. Scene 0.3 may promote to 0.4/0.5, and
0.4 may promote to 0.5 with all current feature capabilities; no downgrade or implicit
legacy migration. These are the existing typed editor's version rules.

## Reconstruction, policy and history

Validate the stored command before replacing its old policy_generation with the
current policy generation for this local preview check. Preserve the stored bytes.
Compare expected revision to the current baseline; the native generation token
also protects same-revision identity/resource replacement. Reuse prepare_authored,
current resource authorization and the existing scene staging path.

The command's package/preset pins must equal the baseline selection. Resolve ordinary
scene changes only from the already verified baseline ResourceSet. Reconstruct command
0.8 font intent through prepare_theme_command using its committed source. No import
callback or filesystem lookup is permitted. Exact original packages and media share
their immutable allocations. Any canonical authored theme override must match its
declared content selection; missing pins, changed source or wrong font bytes reject
atomically. A command with no font intent cannot smuggle a new theme package.

Inspection returns only validated metadata (scene ID, accepted revision, widget count
and whether the theme pin changes), leaving all draft state unchanged. It grants no
future right: restoration repeats identity, state, policy, version and resource checks.
Restoration stages the complete candidate and matching resources as one ordinary undo
step, clearing current selection. Undo restores the exact accepted scene/resources and
prior selection; redo restores the recovered state. An exact no-op returns false and
leaves both stacks, selection and resources unchanged. Invalid/denied attempts change
nothing. Accepted commit, discard, close, policy erasure and reload retain their existing
history/result/resource rules. No second transaction ledger or live scheduler is added.

## Native storage and UI gate

Implement storage only after fixing its exact filesystem profile, private root,
bounded replacement sequence, queue ownership and interruption oracles. Keep recovery
records separate from committed generations. The host must serialize one current
record per profile, retain at most an old/new coherent pair during replacement and
bind asynchronous completions to the exact editor session and capture generation.
Coalesce pending captures; no unbounded history. Recheck current retention policy and
generation before publication. A failed write must expose recovery-unavailable state
without damaging either the accepted configuration or an earlier complete draft.

Offer Restore, Discard recovery draft and Keep for later explicitly. Never activate
recovered content at startup or change committed selection merely by opening the
offer. Unvalidated/off-screen/input-blocking content must not become a desktop host.
Restoration enters the existing editor preview and Apply path with independent exit.
Successful Apply/discard must retire only the matching captured record. Late writes
must not resurrect a record after retirement, policy change or session close.

Revocation immediately prevents new capture, disclosure and publication and erases
queued in-memory copies. Previously retained bytes follow the existing restrict or
purge-with-authority policy; denial alone is not authority to delete them. Regrant
does not automatically restore a draft or activate a desktop. No automatic export,
secure-erasure promise, hardware power-loss claim or cross-filesystem durability claim.

## Fixed acceptance

Freeze this package, envelope schema and independent literal recovery cases before
production edits. Verify exact capture bytes/expected scenes and commands, clean
no-record, metadata-only inspection, one-step restore/undo/redo, normal and canonical
font edits, current-policy reauthorization, version admission, unchanged metadata,
same-revision wrong generation/profile, stale revision, malformed/oversized/deep input,
duplicate keys, wrong intent/request, extra operations, missing pins, spoofed font
selection and source, newer local history, pending/unknown/conflict and erasure.
Prove a wrong expected scene differs; never derive expected output from the code.

Run affected and full portable suites on all three development profiles. Exercise
restored edits through the actual Linux generation store with independently checked
document/resource bytes and lost-result reconciliation before claiming that boundary.
The subsequent native storage/UI work additionally needs process cuts at every write,
replace and retirement transition, stale completion/revocation races, exact crash
reopen, refused malicious filesystem entries and real Restore/Discard/Keep controls.
Preserve all failures and source/artifact/environment identities. Shared semantic tests
alone do not claim that recovery survives a process crash or is enabled in any edition.
