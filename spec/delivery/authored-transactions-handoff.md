---
type: "SysPane Work Record"
title: "Authored transactions and Linux generation recovery"
description: "Preserve coherent scene/settings changes and committed request identities through native process interruption."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T16:09:21Z"}
sp_id: "SP-AUTHORED-TRANSACTIONS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-AUTHORED", "SP-SESSION-DEMAND-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authored transactions and Linux generation recovery

Source baseline: `c2656732efb5f15f3b257e4508c7052154c503d7`. Git history identifies
the resulting commit. Build/test attempts retain source archives and exact input
hashes; native reports identify the tested binary and independent oracle.

The common validator embeds the existing settings 0.1, scene/command 0.2, layout
and binding schema closure. It checks complete candidates, coherent revisions,
single ownership, acyclic bounded hierarchy, layout compatibility and bounds, and
typed operations. No replacement schema is fetched at runtime. Optional annotations
remain authored content. Resource preparation is mandatory; the finite native
fixture admits its synthetic built-in theme, not arbitrary installed assets.

The serialized transaction owner prepares whole-scene and settings changes together.
Preview writes nothing. Publication rechecks current policy, cancellation and expected
revision; exactly one successful commit advances both document revisions. Byte-exact
request replay and retained committed identities prevent duplicate edits. Result
0.1 documents distinguish unsaved failure, uncertain publication and durable storage.
Activation remains pending and visibility false; no renderer acknowledgement is
invented. Cross-epoch reconciliation is currently a typed component API; existing
transport command sessions remain preview-only.

The native Linux adapter holds a private exclusive writer lock, uses held directory
handles and rejects symlinks, unsafe ownership/modes and multiply-linked documents.
Immutable generations bind settings, scene and original request identity through
SHA-256. File/generation/parent flush acknowledgements precede durable success.
The policy guard runs after the temporary selector is flushed and immediately before
replacement. Current and previous selecting records govern recovery; incomplete
directories cannot become current by timestamp. Corruption is retained, with a
verified fallback readable but further publication blocked until explicit repair.
Generation attempts are capped at 32; this first adapter does not implement pruning.

Eight portable families cover schemas/semantics, mixed edits, policy/revision
conflicts, replay/reconciliation, cancellation/storage uncertainty, revision/graph
bounds, retention capacity and known SHA-256 vectors. Twenty final native cases
cover ten stop-and-kill transitions, lost acknowledgement, independent document/hash
checks, last-moment policy replacement, pre/post-publication failures, corrupt
current/previous selectors, mixed documents, symlinks, writer exclusion and capacity.
The observer confirms actual stopped children and SIGKILL exit before reopening.
Recovered fixtures equal literal revision 40 or 41 bundles; no mixed state or
duplicate revision 42 is accepted.

Full suites passed **139 Linux, 127 contemporary Windows and 116 historical-toolset
entries**. After that full run, review moved the Linux policy guard behind temporary
selector flushing and added its native negative case. Import/component metadata
also changed. Final affected reruns pass 11 Linux, 10 Windows and 12 historical
entries; shared compiled sources and existing unrelated native oracles are unchanged.
The record does not claim a second complete full-suite run after those refinements.

The initial Linux focus run passed its eight portable families and native storage
family, but failed both component checks because the probe's thread dependency was
not declared. The manifest now declares it; the original failure remains archived.
The initial historical audit also failed on four new event imports. The amended
experimental closure admits only the documented XP/Kernel32 functions
[CreateEventW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventw),
[ResetEvent](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-resetevent),
[SetEvent](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-setevent)
and [WaitForSingleObjectEx](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobjectex).
All sixteen historical executables then pass PE/header/import and pinned actual
SDK/static-CRT input checks; rejection mutations remain passing. These checks and
host execution do not prove exports or behavior on an XP, 9x or older NT guest.

`out/evidence/w-08-authored-attempts.json` indexes archives, native reports,
artifact identities, original failures and the historical audit. Specification/tool
checks are in `out/evidence/w-08-authored-verification.json`; the machine
handoff is `out/evidence/authored-transactions-handoff.json`. All native
documents in this experiment are synthetic. No installed configuration, real-user
desktop, VM or protected policy was modified, and no release was published.

W-08 remains in progress. Next integrate asynchronous commit/cancel/reconciliation
with the existing authenticated IPC owner and bounded queues, close installed store
and resource/preset ownership, then connect native settings/editor and per-component
activation. Undo, external authoring conflicts, migration and other-platform storage
remain required. The complete PERSIST wire/activation trace is still open. Only the
owned ext4 process-interruption profile was exercised; power-cut, other-filesystem,
Windows/Mac storage and complete [five-family release](release-0.1.0.md) qualification
remain unproven. Existing historical floor/laboratory questions remain unresolved.
