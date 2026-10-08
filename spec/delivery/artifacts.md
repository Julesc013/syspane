---
type: "SysPane Specification"
title: "Binaries, packages and release identity"
description: "Choose stable binary roles and exact offline payload closure."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-ARTIFACTS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMPOSITION", "SP-TARGETS"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-CONVERSATION"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-08T20:02:42+00:00", "scope": "Compiled Linux helper closure and immutable execution; complete installed integration remains unqualified"}
---

# Binaries, packages and release identity


## Planned binary names

These are selected design names, not existing downloads. Conflicting names in the
audit drafts are consolidated here before scripts depend on them.

| Role | Windows | Unix/macOS | Package membership |
|---|---|---|---|
| Controller/inspector | `SysPane.exe` | `syspane`; `SysPane.app` | Desktop |
| Isolated surface | `SysPane.Surface.exe` | Private libexec/bundle helper where needed | Host-dependent |
| CLI/TUI | `spctl.exe` | `spctl` | Desktop or console |
| Independent diagnostic | `SysPane.Diag.exe` | `syspane-diag` | Recovery capability |
| Configuration transaction host | Private helper where admitted | Private `syspane-configuration-host` on Linux | Controller runtime; installed integration pending |
| Provider worker | `SysPane.Provider.exe` | Private `syspane-provider-host` | On-demand admitted providers |
| Privileged broker | `SysPane.Service.exe` | Admitted native service/helper | Optional, explicit installation |
| Maintenance frontend | `SysPane.Setup.exe` | Qualified setup frontend/native package action | Separate maintenance |
| Screensaver | `SysPane.scr` | `SysPane.saver`; named Linux host adapter | Optional companion |

Helpers resolve relative to verified installation identity, never the current working
directory or an arbitrary search path. CPU variants retain the same runtime basenames.
Historical profiles can generate short-name aliases with collision checks. The
[helper identity package](packages/w-26-helper-identity.md) closes the initial Linux
compiled closure and immutable helper-launch boundary; it does not qualify a
complete installed desktop package. CLI stdout is machine-readable UTF-8,
diagnostics go to stderr, exit statuses and cancellation
are documented before implementation. Version/capability queries do not start a
permanent collector. Standalone means a complete deployment unit for its profile,
not one file or no OS dependencies.

## Artifact grammar and closure

Use `syspane-<version>-<target-profile>-<composition>-<distribution>.<extension>` for
project archives, for example `syspane-<version>-<target>-desktop-portable.zip`.
Target IDs resolve immutable exact descriptors; labels such as current/classic alone
are not release minima. Native package filenames follow their own ecosystem rules.
Source, SDK and symbols are separate artifacts. An offline workshop kit contains
distinct target packages, not one universal executable.

Build a target payload once, validate its dependencies and native behaviour, then
package those same bytes for applicable portable/managed forms. Record source tree,
toolchain and dependency locks, enabled components, hashes, SBOM/notices, schema/profile
versions, runtime floor and qualification evidence in the release manifest. Signing,
notarization and timestamping are separate recorded transformations of the unsigned
payload. Package-level native checks remain required after transformation.

Default downloads include normal workflow closure, not every optional role or debug
runtime. Offline packages include redistributable dependencies/assets and notices.
Test extraction, case collisions, relocation, helper lookup and wrong-target selection.
Only qualified profiles enter the public download list. Online update metadata and
provider lifecycle gates are in [setup lifecycle](../setup/lifecycle.md).
