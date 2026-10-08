---
type: "SysPane Work Record"
title: "Independent diagnostic implementation checkpoint"
description: "Bind independent public reporting and native inspector startup to scoped Windows/Linux evidence."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:42:44+11:00"}
sp_id: "SP-DIAGNOSTIC-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W25-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent diagnostic implementation checkpoint

W-25 now includes `SysPane.Diag.exe` and `syspane-diag`, and remains in progress.
Base `29db23e23e5d40292e5dc7166c1ce4d45174bfc6`, containing commit and recorded input
digests identify this checkpoint. The [supervision handoff](supervision-handoff.md)
remains historical. The full campaign and external desktop oracle remain open.

## Implemented boundary

The standalone diagnostic composition provides a public JSON report and a native
Win32/GTK inspector. It opens no controller connection, optional scene/theme,
history, provider, custom renderer or user configuration. Its only mutable input
is protected machine policy. Built-in metadata is limited to product, component,
build version, compiled profile, policy availability and absent recovery controls.
There is no network, process-control, clipboard, repair or preservation interface.

The policy decoder enforces bounded policy 0.1 syntax and semantics without granting
provenance. Native sources read fixed protected HKLM or `/etc` locations, check
ownership and mutation permissions, reject links/unsupported forms and mark a
fully validated snapshot available. Missing/unusable policy allows only the existing
public diagnostic fallback. Available policy gates report/export and both inspector
and accessibility projections. The inspector reloads policy every second while
runnable and replaces metadata after observing denial; this is a polled guarantee.

The read-only inspector uses standard controls with Close/Escape and native close
handling. Its native toolkit is separate from the custom renderer. Linux report
mode skips display initialization; ELF loader dependencies still include GTK.
The development profile pins the installed GTK identity, without claiming a full
transitive redistribution closure or historical/Wayland compatibility.

## Checks and evidence

Both revision 6 profiles pass 52 CTest entries, including the previous IPC/recovery
regressions, two portable diagnostic families and native DIAG-01. The new native
family contains four Windows cases and five Linux cases: relocated report, damaged
optional inputs/forged environment, argument rejection, independent native close,
and Linux reporting/UI behavior without a display server. Linux native controls use
an owned, authenticated Xvfb server over an abstract Unix socket. Only the harness's
own hidden window is closed; no desktop pixels or unrelated user content is captured.
Policy fixtures test denial and replacement snapshots independently of the native
source. Native tests observe unavailable policy; no protected policy is installed.

Records are `out/evidence/w-25-diagnostic-<profile>.json`, corresponding
CTest logs and exact NATIVE-01/NATIVE-02/RECOVERY-01/DIAG-01 report copies. The recorder
checks the complete case set, source/executable hashes and native close identity.
The original Windows compile failure (narrow IDC_ARROW macro passed to a wide API)
is preserved in `w-25-diagnostic-attempts.json`; the resource now uses the explicit
wide form. The initial WSLg focused check passed, but a subsequent full run timed out
inside XOpenDisplay. Its CTest log is preserved. An initial Xvfb attempt also failed
to bind filesystem sockets in the WSLg-owned directory; its report is retained.
The final harness uses a private authenticated abstract-socket Xvfb display, verifies
the server PID and bounds the Xlib observer in a separate process. WSLg qualification
remains unproven; no desktop acceptance criterion or compiler warning policy changed.

The shared specification checker now accepts mathematical integer JSON values
consistently with schema/native command validation, rejects duplicate policy
role/channel rules, and has two corresponding regressions. Specification-tool
checks remain separate from native product qualification.

## Remaining gates and next step

Positive native policy provenance/deployment and native revocation qualification
need an admitted administrative lab; no privileged policy write was performed.
The Windows reader deliberately accepts only SYSTEM/Administrators ownership and
simple allow/deny ACL forms. Additional enterprise-owner/ACL profiles need closure
and qualification. A hidden close test is neither accessibility certification nor
independent visible/editor recovery evidence.

Close and implement bounded recent-failure metadata and explicit preservation of
damaged configuration. Connect actual telemetry/renderer recovery and current-policy
payload erasure, then prove native editor exit and externally visible recovery with
W-02. Execute available host tracks while retaining separate unavailable historical
Windows/Mac and full-desktop laboratory claims. W-25 remains open; no release exists.
