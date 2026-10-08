---
type: "SysPane Work Record"
title: "Independent editor exit on the measured GNOME desktop"
description: "Native exit restores icon input and original measured pixels while desktop and collector lifetimes survive."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T13:56:23Z"}
sp_id: "SP-GNOME-EDITOR-EXIT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GNOME-EDITOR-EXIT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent editor exit on the measured GNOME desktop

Source baseline: `c6a600d97e04b7c0d93f4727d77bfe3d3f659b6b`. Git history identifies
the resulting commit. Original source archives identify every native attempt.

The [experiment](packages/w-25-gnome-editor-exit.md) connects the existing independent
keyboard/GTK exit owner to the owned GNOME/DING desktop, persistent controller,
real collector and live measured tile. The transient candidate contains only fixed
public pixels. Native resource/PID identity, geometry, actual icon obstruction and
blocked clipboard selection are observed before stopping its held process.

Four positive controls require confirmed child exit and removal of the obstruction
within 1,500 ms, then real icon selection within 2,500 ms: keyboard exit, native
button exit, recovery-owner death and keyboard exit while the controller is frozen.
The latter resumes the controller only after independently observed release. The
same source epoch, controller, shell and icon manager survive; original acquisition
continues during obstruction and current counter/rate/age pixels return afterward.
Stopping both editor and recovery owner leaves the obstruction and blocked input
in place. That negative control remains a failed candidate, never a cleanup-based
recovery. Thirty evidence tests challenge ownership, geometry, collection, deadlines,
escalation, input and operational pixels.

The first candidate exited before placement. Subsequent initial Xlib/GTK maximize
requests left it beside the icon, so those attempts failed before fault injection.
GTK maximization on the actual map event establishes observed obstruction on this
profile. No fixture position, recovery deadline or pixel oracle was weakened.
The initial corruption-test runner omitted `AssertionError` from its expected
rejections: the continuous-source oracle correctly rejected missing collection,
but the test reported that rejection as its own failure. The correction preserves
that assertion and the original failed test record.

Evidence is indexed in `out/evidence/w-25-gnome-editor-exit-attempts.json`.
The five-control matrix, independent revalidation, earlier eight controller controls
and their 33 evidence tests retain exact native artifacts and original private
journals. The Linux CTest regression covers 115 entries, including the original nine
owned-Xvfb exit cases. The complete-suite archive precedes only the corruption-test
runner's exception-handling correction; the final desktop matrix archives that
corrected runner separately. Native implementation bytes are identical.
Specification validation and integrity results are recorded in
`out/evidence/w-25-gnome-editor-exit-verification.json`; the source-bound
handoff is `out/evidence/gnome-editor-exit-handoff.json`.

Operational measurements, interface records and pixel crops remain mode 0600 in
the owned private laboratory directories. Public records retain their hashes and
scoped results. All owned groups exit; no real user desktop or VM is faulted.

W-25 and the campaign remain open. This closes one transient desktop lifetime/input
boundary, not actual scene drafts, Apply/Cancel, interrupted transactions, fullscreen
recovery discovery, Wayland or installed supervision. Next close controller/session/
policy/demand ownership and connect W-08/W-09/W-10's real transaction and persistence
contracts. Windows synthetic-lab designation, historical guest scope and an admitted
Mac endpoint remain unresolved; unrelated deterministic work can continue.
