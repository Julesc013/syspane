---
type: "SysPane Work Record"
title: "Independent editor lifetime checkpoint"
description: "An owned X11 candidate has independent keyboard and native exit with external process, pixel and input evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T13:00:00Z"}
sp_id: "SP-EDITOR-EXIT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-EDITOR-EXIT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent editor lifetime checkpoint

Source baseline: `be0caa3651d0bc9414d85371f99d57459e777bec`. Git history identifies
the resulting commit; preserved source archives identify each original attempt.

The [closed experiment](packages/w-25-editor-exit.md) adds an X11 keyboard guard
and native GTK recovery owner with an isolated ordinary interactive candidate.
The owner acquires Ctrl+Alt+Escape before child launch. It needs no application
controller, renderer, configuration, policy disclosure or child event loop.
The existing held-pidfd Child adapter scopes every signal; only native wait proves
termination. Exit requests cooperative shutdown, then kills the same child after
250 ms if necessary. Parent-death protection removes the child if its owner dies.

Nine cases pass: ordinary/shifted input followed by keyboard exit, frozen editor
keyboard and GTK-button exit, locked modifiers, held pointer, relevant mapping
loss, owner loss, child crash and shortcut conflict. Independent input first fails
to reach the underlying witness while red candidate pixels obscure it. After exit,
green witness pixels and delivered clicks return within the unchanged 1,500 ms
deadline. Every case also checks shortcut release. Four evidence tests include
17 corrupt-record rejection variations. The recorder verifies original observer
files, native journals and current source/executable identities.

The first attempt failed because unchanged XKB mapping notifications were treated
as binding loss, and the button observer assumed a coordinate. The guard now
revalidates relevant bindings. The second attempt passed every other case but
selected GTK's hidden leader during button discovery. The observer now requires
the exact recovery title, geometry and native owner PID before sending input.
Both failures and original sources remain preserved. A Windows focused invocation
also selected a Linux-only test and correctly failed with no tests found; the
corrected two Windows component-graph checks passed. No failure becomes a pass. The first specification validation also rejected four
evidence links leaving the portable bundle; repository-relative evidence paths
replace those links, with the original failed validation preserved.

The complete Linux regression passes 115 CTest entries. Subsequent harness-only
changes add runtime fingerprints and allow 300 seconds for nine bounded cases and
cleanup; the focused native family is rerun with those bytes. Native implementation
bytes remain those of the passing complete suite. Both affected Windows component
checks pass; no Windows native source changed and no Windows editor qualification
follows.

Evidence is indexed in
`out/evidence/w-25-editor-exit-attempts.json`.
Current independent checks are in
`out/evidence/w-25-editor-exit-evidence-check.json`;
the source-bound handoff is
`out/evidence/editor-exit-handoff.json`.
Specification generation, schemas/fixtures, tooling and integrity outcomes are in
`out/evidence/w-25-editor-exit-verification.json`.

W-25 remains in progress. This public-pixel candidate uses owned Xvfb and a reserved
recovery strip. It does not implement the scene editor, fullscreen escape discovery
or an installed recovery service. Emergency release writes no document and never
reports a successful Apply or Cancel. Active keyboard grabs, unavailable display
servers and Wayland require distinct platform contracts.

Next integrate independent exit with the actual owned desktop/editor role while
preserving collection and passive-wall input. Close installed session/controller/
policy/demand ownership independently. W-08/W-09/W-10 must supply real draft,
transaction and persistence boundaries before edit recovery is claimed. Windows
synthetic-lab designation, historical guest scope and an admitted Mac endpoint
remain unresolved; unrelated deterministic work can continue.
