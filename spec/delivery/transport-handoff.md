---
type: "SysPane Work Record"
title: "Portable transport and policy checkpoint"
description: "Resume W-24 from executable portable contracts without claiming native authentication."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:26:58+11:00"}
sp_id: "SP-TRANSPORT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W24-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Portable transport and policy checkpoint

The campaign and W-24 remain active. The source base is
`a3597f9c165dc7691950faf90138c959296db367`; the containing commit and per-input
digests identify this integration. This checkpoint is deliberately narrower than
the [W-24 completion gate](packages/w-24-transport.md).

## Delivered boundary

The C++17 protocol library implements four-byte length framing, bounded strict JSON,
raw body byte identity, exact negotiation, request reservations and replay, monotonic
expiry and separately bounded data/control queues. The configuration library
implements eleven generated setting descriptors, current-policy preview checks,
disclosure decisions and a portable connection state machine. The model does not
depend on JSON or the configuration layer. The vendored nlohmann/json 3.12.0 header
and MIT license are pinned and verified offline by `source/build/dependencies.json`.
This third-party license does not choose the project's own licensing terms.

The initial controller has no durable mutator: settings preview is enabled only
after exact command/result document negotiation; commit and scene replacement
return unsupported. Stored/durable/visible stay false. A typed authentication
context is supplied by the caller, and all test contexts are fixtures. There is
no endpoint that trusts a caller-provided approval field. A native authenticated
context factory and stream adapters remain to be implemented.

Both development profiles pass 35 checks: 18 existing model/smoke/composition cases
and 17 protocol cases (16 named cases plus dependency verification). The new cases
include fragmented/coalesced framing, partial EOF, deadline boundaries, duplicate
decoded keys, invalid Unicode, parser limits, lower-version negotiation, all four
fixed request-budget traces, cancellation, controller capacity, settings bounds,
role/channel disclosure, queue exhaustion, policy revocation and reconnect.

Case commands, original log hashes, normalized logs, source inputs, generated
descriptor and executable/library hashes are recorded in
`out/evidence/w-24-portable-windows-x64-gcc15.json` and
`out/evidence/w-24-portable-linux-x64-gcc13.json`. W-01's historical
records remain unchanged. These are implementation checks with injected clocks
and authority contexts, not native IPC or desktop qualification.

## Choices and limits

Protocol JSON is isolated from the model. Diagnostic byte positions preserve
whitespace in request identity instead of using a reserialized canonical document.
Native descriptors are generated from the existing registry, with generation
failing on unsupported constraints. JSON integer-valued numeric forms such as
1000.0 follow the schema's integer semantics; uint64 revisions remain strings.

The ledger reserves each result's maximum bytes before admission, shares principal
reservations across reconnects, and preserves them for exactly 600 seconds after
completion. The preview slice also retains preview IDs under that conservative
budget. An unauthorized caller cannot retrieve a result through the cache after
policy revocation. No persistent journal or restart reconciliation is implemented.

Data queues and disclosure decisions are tested helpers; real telemetry
subscriptions and their serialization remain disabled. The native integration
must enforce the negotiated frame limit before allocation, stream/handshake/write
deadlines and connection ownership. It must never present these portable tests as
proof of a named-pipe ACL, Unix peer credential or actual cross-session denial.

## Next step

Close the Windows and Linux adapter details in the W-24 package, then implement
NATIVE-01/NATIVE-02 and their real client/server harness. Use private local endpoints
under the existing bounded workspaces. Reuse the portable code and fixed oracles;
do not create another protocol. Record actual OS identity and distinguish denied
fixture credentials from a real cross-user/logon laboratory experiment. Then finish
W-24's required native stream/state integration checks before admitting dependent
W-25 recovery and native-host work. W-02's independent desktop oracle can progress
from W-01 without waiting for missing historical/Mac laboratories.
