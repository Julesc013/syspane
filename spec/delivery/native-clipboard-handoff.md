---
type: "SysPane Work Record"
title: "Bounded native clipboard checkpoint"
description: "Explicit Linux X11 object transfers with independent peers and exact draft/persistence results."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T13:00:00+00:00"}
sp_id: "SP-NATIVE-CLIPBOARD-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-NATIVE-CLIPBOARD", "SP-SCENE-FRAGMENTS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded native clipboard checkpoint

Baseline 3ccb8bbaf3816bb8401928015bb9be50a0de6ee8. The
[frozen package](packages/w-10-native-clipboard.md) connects the existing shared
fragment/draft owner to explicit Copy, Paste and Cancel paste in the admitted GTK3/X11
development editor. Ctrl+C/V act only in the canvas or object list. Paste appends
fresh-ID roots as one undo operation; Apply retains the existing durable transaction.
The destination theme and exact resource closure remain authoritative.

The adapter in `source/platform/linux/` owns a private X connection on the serialized
GLib owner. It exports only the custom scene-fragment target and protocol metadata.
It never claims PRIMARY, publishes generic text or requests clipboard-manager
persistence. Each outgoing chunk obtains a newly authorized borrowed snapshot.
Metadata requests cannot overwrite a property used by an active transfer. Ownership
loss erases the snapshot without clearing a foreign owner's selection.

One incoming and eight outgoing transfers use a 262144-byte payload ceiling,
16384-byte chunks, one-second idle and five-second absolute deadlines. Both direct
properties and INCR are bounded before payload allocation. A fresh receiving window
isolates every paste from old replies. Pending paste prevents draft edits/submission;
cancel, Escape, topology, reload, policy, disconnect and close end the pending receive.
Policy restoration never restores an erased offer. No new filesystem owner, runtime
scheduler, command version or persisted clipboard format is introduced.

## Executable verification

Six independent native cases cover exact Copy/Paste, TARGETS/TIMESTAMP and refused
text export, foreign PRIMARY, direct/INCR receive including the exact byte ceiling,
malformed bodies/headers/formats, incorrect notification fields, lying size hints,
cumulative overflow, missing pins, cancellation and late replies, policy/regrant,
topology, foreign ownership, closed editors, destroyed requestors, duplicate properties,
eight-slot capacity and recovery, per-chunk revocation and both deadline classes.
Real controls and keyboard input exercise one-step undo/redo and exact durable
save/reopen, including original resource bytes. A wrong-scene witness fails the fixed
comparison. The peer imports no product codec or fragment generator.

All 372 Linux GCC13, 369 Windows GCC15 and 366 v141_xp portable checks pass. The 195
affected editor/settings/configuration/composition/protocol checks are included in
each full suite. Native EDITOR-FORM, EDITOR-CONTENT-PROPERTIES, EDITOR-VISIBILITY,
EDITOR-FONTS and THEME-HISTORY regressions pass. The latest clipboard execution uses
the final runtime and harness sources. Existing portable expectations, schemas and
fixtures are unchanged; the new package and example fixture retain their hashes
recorded before production edits.

The [compact checkpoint](checkpoints/native-clipboard.json) records exact source
archives, executable identities, commands, outcomes and specification/tool checks.
Raw archives and native recordings are retained locally under ignored `out/evidence/`.
A fresh checkout runs the declared tests to create its own evidence. No raw recording,
binary or machine-specific workspace binding is added to Git.

## Preserved failures and limits

The first native attempt queried the selection before the native Copy event had been
handled. The observer now waits for the actual owner/conversion request. A later large
transfer delivered 196608 bytes before the observer's three-second window expired;
the package allowed five seconds. Observation now covers that unchanged deadline,
and redundant full draft validation between chunks was removed. Each borrow still
reauthorizes current policy. The observed 200418-byte transfer then completed in about
1.6 seconds; a deliberately slow peer still reached the absolute timeout.

Log review found an extra unref after closing a GDK-owned display in an early passing
attempt. That defect was corrected; unknown critical diagnostics now fail the native
clipboard oracle. Two earlier GTK warning families remain: private-text selection
clipboard cleanup and duplicate gtk_main_quit. Baseline recordings already contain
them; they are explicitly retained rather than treated as clipboard regressions or
clean shutdown evidence. They remain required cleanup before complete-edition claims.

The content-properties regression also exposed the observer's 64-reference cache
bound after three new toolbar controls appeared. Its allowance is now 67, with live
state/value reads preserved. Exact edit, persistence and failure expectations did not
change. The failed run and subsequent passing run are both retained. Earlier failed
native-host and accessibility evidence is unchanged. Windows tooling retains its two
existing symlink-privilege skips; historical compiler checks on contemporary Windows
do not qualify historical operating systems.

## Next boundary

Keep W-10 in progress. Continue the recovery-draft contract and its interrupted,
untrusted and rejected-restoration examples before implementing recovery storage.
Installed controller/catalog/policy ownership, scene-aligned desktop
entry/restoration, full accessibility/performance and the known shutdown warnings
remain open. Other clipboard backends need their own bounded native adapter and
independent evidence. All five complete desktop editions and release qualification
remain required; this checkpoint authorizes no public release or privileged operation.
