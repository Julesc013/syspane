---
type: "SysPane Work Record"
title: "Original-epoch request reconciliation checkpoint"
description: "Recover committed outcomes across controller restart without replaying mutations."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T17:11:17Z"}
sp_id: "SP-RECONCILIATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-RECONCILIATION", "SP-COMMAND-SESSIONS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Original-epoch request reconciliation checkpoint

Source baseline: `b3b9a5addf4483700fb13f330f9d2c4c5b3657b7`. Git history identifies
the resulting commit. The [package](packages/w-08-reconciliation.md) closes this
finite boundary after the [command-session checkpoint](command-sessions-handoff.md).

Authenticated clients can negotiate read-only `result.reconcile` independently of
mutation submission. The query names an original producer epoch and request ID;
the reply echoes its correlation fields and identifies the current producer epoch.
The client validator rejects crossed connections, epochs, queries and request IDs.
Two versioned schemas and valid/invalid fixtures define the bodies and facts.

The native store exposes at most two receipts from validated current/previous
selectors. The command owner validates their command bytes and revision relation,
collapses identical fallback receipts and rejects conflicting identities. The
worker refreshes receipts; the serialized owner publishes them only after actual
stop. Session lookup reads that snapshot without native-store access, preparation,
ledger admission, expiry renewal or writes. Storage faults clear availability.

Current policy authorizes receipt and pending-request disclosure. An accepted
receipt proves that its original revision committed; it does not mean that the
revision remains selected or visible. Missing/pruned receipts stay unknown, and
new E2/R cannot replace the meaning of E1/R. Clients obtain current authored state
before any subsequent edit; a missing acknowledgement never authorizes blind retry.

The independent Linux client submits scene x=20 from revision 40/x=10, observes
the exact controller stopped at its durable boundary before any acknowledgement,
kills it and restarts E2. Reconciliation recovers revision 41 without creating 42.
The oracle reads full settings/scene documents, verifies manifest hashes and checks
all store-file hashes before/after queries. Additional cases cover the before-
publication control, revoked policy at restart, corrupt-selector fallback, retained
and pruned epoch-scoped identities, and heartbeat/lookup while a real worker lives.

## Evidence

Full suites pass 152 Linux, 138 contemporary Windows and 127 historical-toolset
entries on the modern Windows host. All three runs use the final implementation,
package and fixed oracle inputs. The six new native cases pass alongside six
command-session and twenty generation-storage cases. Seventeen historical
executables pass the ordinary PE/header/import and pinned linker-input audit;
this establishes no historical runtime claim. Specification/schema/generation/
integrity checks pass, with 56 tooling tests passing and two existing Windows
symlink assertions skipped.

The initial archive audit rejected three generated navigation indexes changed
after the Linux full run. They contain only inserted reconciliation links;
the corrected evidence check verifies that exact difference byte-for-byte while
requiring identical implementation, schemas, fixtures, package and oracle inputs.
The original audit failure and helper are preserved. No product test failed or
acceptance expectation changed during this checkpoint.

Verification is recorded in `build-support/evidence/w-08-reconciliation-attempts.json`;
the machine handoff is `build-support/evidence/reconciliation-handoff.json`.
The attempt index binds source archives, native reports and compiled artifacts.
Specification/tool and staged-byte checks use the same evidence prefix.

## Remaining boundary

W-08 remains in progress. Next close installed controller/store/protected-policy
ownership, independently supervised native workers and complete resource/preset
preparation, then connect native settings, direct editing and real activation.
Undo, external authoring, migrations and non-Linux persistence remain required.

This is only the reconciliation portion of PERSIST-01 and related variants.
Pending presentation facts do not prove renderer activation or independent
diagnostic availability. A process crash does not simulate media removal or power
loss. Historical-toolset checks on the modern host do not qualify historical OS
execution. Version floors/labs and all five complete native release tracks remain
open. No installed user configuration, user desktop, unrelated VM, privilege or
public release is exercised by this checkpoint.
