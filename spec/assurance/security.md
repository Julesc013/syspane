---
type: "SysPane Specification"
title: "Security, privacy and operational safety"
description: "Constrain collection and automation according to actual trust boundaries."
tags: ["assurance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-SECURITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AUTHORITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Security, privacy and operational safety

## Assets and boundaries

Protect host availability, desktop input/focus, hardware under test, identifiers, history, configuration, organization policy, build provenance and signing credentials. Boundaries include native source callbacks, device metadata, provider IPC, user imports, optional privileged helper, local automation, remote probes, update packages and development agents.

Normal operation is unelevated and local. No mandatory service, listening web server, cloud telemetry, crash upload, external exporter, subnet discovery or arbitrary script execution. Read-only collection must account for operational side effects such as wakeups, port-control signals, device stress and reparative inventory queries.

## Privileged helper

Before implementation, enumerate exact required operations and the least rights each needs. Do not default every hardware query to a system-wide privileged service. Use bounded typed requests, authenticated peers, explicit session/scope policy and allowlisted device operations. No arbitrary path opening, command execution, memory access or general IOCTL proxy.

The helper does not draw UI. The controller and surface do not inherit helper authority. IPC ACLs/permissions and peer checks are implemented and tested, not merely described. Handle service absence and denial as capability states.

## Untrusted input

Validate lengths, arithmetic, encoding, counts and references before allocation. Device names, firmware, log lines, imported themes, file paths and issue text are data, never instructions. Avoid DLL/library search through user-writable locations. Deny path traversal, symlink/reparse escape and unapproved network retrieval in packages. Bound queues, retry loops, parser depth, decoded asset memory and logs.

## Privacy

Default display fields avoid unnecessary personal identifiers. Administrators select allowed host/network/asset fields. Diagnostic exports are explicit, previewable, redacted and bounded. Screenshots and dumps may expose unrelated applications or credentials; they require separate consent and retention controls. Data stays local unless an explicitly configured exporter is admitted.

## Development security

AIDE worktrees isolate file organization, not privilege. Execute untrusted changes in an actual sandbox/account/VM boundary with restricted credentials. Do not run public pull-request code on a persistent privileged workshop runner. Signing identities and deployment authority stay outside worker processes.

## Acceptance

Threat-model each new trust boundary; map threats to negative tests and mitigations. Test oversized inputs, path escapes, forged peers, event storms, permission changes, provider crashes and denied operations. Document residual risks and update/vulnerability response policy. A syntax pass or a signature does not certify security.

## Contract additions and early gates

[Policy](../experience/policy.md) defines role/channel disclosure and live revocation;
[transport](../contracts/transport.md) requires native peer/session authentication,
bounded framing and control progress before cross-process use. [Recovery](../architecture/recovery.md)
cannot bypass mandatory policy. [Content admission](../experience/presets.md) separates
declarative imports from executable-provider admission and actual sandbox controls.
These are first-slice gates, not optional hardening after a public preview.
