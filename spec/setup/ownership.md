---
type: "SysPane Specification"
title: "Installation paths and mutation ownership"
description: "Separate immutable payload, user state and maintenance receipts across deployment modes."
tags: ["setup"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-INSTALL-OWNERSHIP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SETUP"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-XDG"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}, {"id": "SRC-XDG", "resource": "https://specifications.freedesktop.org/basedir/latest/", "title": "XDG Base Directory Specification"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Installation paths and mutation ownership


## One mutation owner

Each installed component and OS resource has one recorded mutation authority:
unmanaged portable, USK-managed, or a native package manager. Plain extraction does
not enroll ownership, autostart or elevation. Adoption of an untracked directory
needs an explicit ownership plan. Native-manager-owned files are changed only through
that backend; USK may inspect/delegate but cannot maintain a competing ownership DB.

Payload, user-data and setup-state roots are logically disjoint and cannot contain
one another for managed portable mutation. Reject resolved overlap, aliases and
ambiguous ownership. An example is `SysPane/app/`, `SysPane/data/`,
`SysPane/setup-state/`. Unmanaged portable archives may keep binaries at their root
and use an explicitly selected adjacent data root; no payload repair owns that data.

## Installed paths

| Class | Windows | Linux/XDG | macOS |
|---|---|---|---|
| Payload | Admitted protected/per-user program root | Package-owned bin/lib/libexec/share | Application bundle |
| Authored settings | Resolved per-user application-data root | CONFIG_HOME | User Application Support |
| Presets/assets | Separate user-content subtree | DATA_HOME | User Application Support |
| Local history/bindings | Bounded local-state subtree | STATE_HOME | Separate local support/state subtree |
| Cache | Disposable local cache | CACHE_HOME | Library/Caches |
| Session IPC | Native user/session endpoint | RUNTIME_DIR and session scope | Native user/session endpoint |
| Machine policy | Protected administrative source | Protected system policy | Admitted managed/system policy |
| Setup receipts | Backend-owned protected state | Backend-owned state | Backend-owned state |

Resolve native directories with APIs qualified for the target; never assume modern
Windows paths on XP. Do not write mutable data inside signed payloads. XDG distinguishes
configuration, data, state, cache and session runtime; policy enforcement is separate
from preference search order. [XDG reference](https://specifications.freedesktop.org/basedir/latest/).

Portable mode uses an explicit marker/selection and data root, not current-directory
writability. Read-only or removed media reports failure or clearly selected session-only
changes; another persistent root must be chosen explicitly. Keep roaming authored content
apart from host identities, credentials and history. No ad-hoc drive-root directories.

Repair/uninstall preserve unowned or locally modified resources and report conflicts.
Saver-only removal preserves desktop/shared data; shared payload is removed only when
no installed component owns it. Purging user data is a separately authorized operation.
