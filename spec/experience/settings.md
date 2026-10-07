---
type: "SysPane Specification"
title: "Native settings and complete user operation coverage"
description: "Every supported user-configurable capability has a native discoverable operation."
tags: ["experience"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-SETTINGS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Native settings and complete user operation coverage

## Registry-driven completeness

Maintain one typed registry for settings: identifier, type, units, default, range, scope, dependencies, policy constraints, preview/activation rules, restart requirement, labels, help and localization IDs. Generate validator/control bindings and CLI help from it. Purpose-built native editors handle complex fields; a generic form is only the completeness floor.

All supported user settings SHALL be reachable without editing TOML, YAML, JSON or INI manually. Search finds both friendly labels and technical IDs. Source capabilities that are unavailable remain explainable; policy-disabled controls identify the enforcing scope without exposing secrets.

## Native applications

Use Win32 native controls/property interfaces, AppKit on macOS/OS X, and appropriate GTK/KDE interfaces. Do not make the settings application imitate a foreign OS theme. Shared operation semantics matter more than identical pixels. User themes apply primarily to the diagnostic scene; accessibility and native navigation remain trustworthy.

The inspector provides selectable/copyable values, full address and device details, source/timestamp/error context, recent transitions, collector health, host diagnostics, layout preview and explicit support-bundle creation. Normal operation is unelevated; clicking an advanced field is not implicit permission to install or launch a service.

## Persistence

The typed configuration store is canonical at runtime. TOML is a supported human-authoring/import format, not the only interface. Import normalizes to the same typed configuration and transaction validation. Comments are preserved when editing an authored text file or the application writes a clearly scoped generated override rather than destroying the user's organization.

Display changes, provider configuration and retention policy have distinct activation scopes. Prepare new resources before switching to a committed generation; a malformed layout cannot blank the existing wall. A newly restrictive policy must not be ignored merely because an old configuration worked.

## Defaults

First launch displays a useful conservative host/network scene, not an empty dashboard. Persistent recording, active remote probing, autostart, exporters, privileged collection and third-party providers require explicit enablement. The GUI offers first-use discovery and layout preview without a cloud account or network connection.

## Acceptance

A machine-readable settings coverage report maps every user setting to native UI, control API and CLI operations or an explicit non-user/internal classification. Missing native editing is a release defect for advertised user functionality. Test search, keyboard navigation, reset, policy locks, invalid input, effective-value explanation and persistence across all initial platforms.

## October contract ownership

The eleven initial descriptors now carry structural constraints, units, scope,
dependencies, activation, policy classification, localization/help IDs and native
coverage status. `specctl generate` projects their setting constraints into settings
and both command schemas; validation rejects bad defaults and projection drift.
The [native settings checkpoint](../delivery/native-settings-handoff.md) adds generated
descriptor metadata, portable drafts and an embeddable GTK form. Its
[resource-aware extension](../delivery/settings-resources-handoff.md) retains exact
package/preset selection through theme edits, saves and reconciliation. The
[coverage report](settings-native-coverage.json) maps all eleven controls to commands
and executable cases. Installed routing, preset/import controls, CLI/help generation,
inheritance reset and other native adapters remain implementation work; component
evidence does not mark full product coverage complete.

[Resolution](configuration-resolution.md) owns precedence, reset/delete/list semantics,
theme selection and provenance. [Presets](presets.md), [policy](policy.md) and
[generation persistence](../architecture/persistence.md) own import, restrictions and
crash behaviour. Portable paths follow [installation ownership](../setup/ownership.md).
