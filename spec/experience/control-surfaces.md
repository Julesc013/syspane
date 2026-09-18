---
type: "SysPane Specification"
title: "CLI, native launch and local automation"
description: "Present one user-facing application with explicit modes and shared commands."
tags: ["experience"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-CONTROL"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMMANDS", "SP-SECURITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# CLI, native launch and local automation

## Invocation

The native desktop package offers a normal application entry, inspector/settings and an explicit CLI path. Use `syspane --gui`, `--cli`, `--tui`, `--json` and `--help` as proposed mode selectors. Exact command grammar stabilizes after native entry-point experiments; no command in this design document is an already built executable.

Default invocation chooses a useful native GUI when launched from a desktop and avoids opening unsolicited windows for an explicitly headless/structured request. Platform-specific packaging may include helper executables or a console shim. One application identity does not require one process or one binary at the cost of OS console semantics.

## Control API

Every configuration/editor change uses the shared typed transaction contract. Local clients can inspect capabilities, read current state, request a bounded history range, validate a configuration, preview/apply a transaction and inspect activation results. Normal reads do not authorize probe execution or privileged collection.

JSON output writes only machine output to stdout; diagnostics go to stderr. Text output uses clear units and status. Exit codes distinguish success, validation/conflict, permission, unavailable capability and operation failure. Partial data is identified in the response, not hidden by a success exit code alone.

## Automation boundary

Use authenticated/authorized local IPC by default, not an always-on HTTP listener. Windows named pipes and Unix-domain equivalents are implementation choices with explicit peer identity, session/scope and ACL/permission checks. Request frames are versioned and bounded. The renderer cannot inherit broad controller privileges just because both are local.

A future remote control endpoint is a distinct feature with its own threat model. It must not be smuggled into the provider SDK or workshop probing. CLI mode cannot bypass organization policy. Destructive system actions are outside the normal operational-wall interface.

## Acceptance

Test GUI/CLI/API transaction equivalence, pipe disconnect, client/server version mismatch, oversized frames, duplicate requests, denied clients, invalid output modes, headless launch and Unicode paths. A diagnostic command can read host state without launching an interactive editor or altering desktop placement.
