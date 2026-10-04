---
type: "SysPane Specification"
title: "Native screensaver composition"
description: "Share scene meaning while separating saver hosting, lifecycle and disclosure."
tags: ["desktop"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-SCREENSAVER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMPOSITION", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-SAVER"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}, {"id": "SRC-SAVER", "resource": "https://learn.microsoft.com/en-us/windows/win32/lwef/screen-saver-library", "title": "Microsoft Windows saver lifecycle"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Native screensaver composition


The optional companion shares scene projection, themes, bounded widgets and native
configuration components. It does not rename the full desktop executable or reuse
desktop placement assumptions. Select saver, preview or configuration mode before
initializing role-specific services. All profiles remain planned and unqualified.

| Role | Required behaviour |
|---|---|
| Full-screen saver | Read-only filtered presentation under the actual native saver host. |
| Embedded preview | Constrain output to the supplied preview container; no surprise full-screen window. |
| Configuration | Unlocked native settings through common commands and preview/apply/cancel. |
| Scene editor | Interactive unlocked application; never collect credentials or edit through the lock boundary. |

Windows uses `SysPane.scr` with the native saver/configuration lifecycle and explicit
architecture/host matching. Microsoft documents distinct saver and configuration
entry points and host security contexts; these must be tested on each named profile.
[Windows saver reference](https://learn.microsoft.com/en-us/windows/win32/lwef/screen-saver-library).
macOS proposes a separately qualified `SysPane.saver`; select a supported native host
and configuration adapter before release. Linux has no universal saver/locker host
contract here: name and qualify the actual integration. The OS or approved locker
owns authentication and lock security; saver failure must not weaken that boundary.

When the controller is available, use an authenticated read-only subscription with
saver disclosure policy applied before delivery. Bounded standalone acquisition is
a separate qualified capability and cannot start privileged helpers, installers or
external probes. Desktop and saver have distinct instance identities and coexist
without singleton collisions. Multiple displays share acquisition demand.

Display-off/sleep reduces or suspends work under policy. Exit releases saver demand
without stopping independent recording. Lease expiry and stale data remain visible.
Preview and full-screen disclose only permitted fields, including accessibility and
cached text. Configuration may use a different explicitly authorized disclosure role.

Saver and desktop payloads have explicit shared-component/data ownership. Saver-only
uninstall preserves shared content. ScreenSave is a possible mechanics/test provider,
not an adopted dependency: pin/review public interfaces and license before reuse;
SysPane retains diagnostic semantics. Native acceptance covers preview/fullscreen/
configuration, lock ownership, multi-display, power, failure and coexistence.
