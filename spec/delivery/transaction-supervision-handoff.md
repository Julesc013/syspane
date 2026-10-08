---
type: "SysPane Work Record"
title: "Independent transaction supervision checkpoint"
description: "Preserve exact process-stop and recovery boundaries for uncooperative native transactions."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T17:23:18Z"}
sp_id: "SP-TRANSACTION-SUPERVISION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-SUPERVISION", "SP-RECONCILIATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent transaction supervision checkpoint

Source baseline: `0463b963d30d3c9f9c106841a45bcaa0df16bd89`. Git history identifies
the resulting commit. The [package](packages/w-08-supervised-transactions.md)
continues W-08 through the existing native child, health and recovery components.

Transaction work starts only after its independent supervisor arms a 5000 ms
absolute deadline. Health traffic cannot extend it. A completion observed at the
deadline is late. The opt-in HealthLink profile rejects invalid tickets, direction,
order and missing negotiation; ordinary renderer/client channels do not enable it.
Transaction start/finish messages convey no command or policy authority.

The Linux supervisor owns the exact controller process through Child. A timeout,
health failure or disconnect quarantines the restart gate before requesting stop.
Only native wait supplies proof for replacement. Each new controller opens storage
afresh with a new epoch and private endpoint lifetime. The existing restart budget
survives handshakes and transactions. No mutation is replayed during recovery.

The controller owns its transaction thread and store lock. It monitors supervisor
health outside that thread and exits the process on loss/expiry without joining
uncooperative work. Native parent-death handling independently covers abrupt
supervisor death. Such exit makes no assertion about whether publication happened;
clients reconnect and use original-epoch reconciliation under current policy.

The independent native client observes actual worker tasks and process exit through
pidfds. It checks responsive command heartbeats during a hung transaction, verifies
that the old process is reaped before replacement, reconnects and inspects complete
stored documents and manifests. Normal completion, preparation/durable hangs,
controller freeze, supervisor death/freeze and circuit exhaustion are separate cases.

## Evidence

Full suites pass 157 Linux, 142 contemporary Windows and 129 historical-toolset
checks on the modern Windows host. All three runs match the final source, package,
schema, fixture and oracle inputs. Seven native supervision cases pass alongside
the existing six command, six reconciliation and twenty storage cases. Seventeen
historical executables pass the PE/header/import and pinned linker-input audit.
Specification/schema/generation/integrity checks pass; 56 tooling tests pass and
two existing Windows symlink assertions are skipped. None of these host checks
qualifies historical native OS behavior.

`out/evidence/w-08-supervision-attempts.json` indexes source archives,
actual build/test results, native reports and artifact hashes. The machine handoff
is `out/evidence/transaction-supervision-handoff.json`. Specification
checks and staged-byte verification use the same evidence prefix.

The initial build caught an exhaustive GNOME health-event switch missing the new
events. Its source and failure are retained. The adapter explicitly rejects those
events: its renderer link does not negotiate transaction supervision.

## Remaining boundary

W-08 and all five complete release tracks remain open. Next bind installed
controller/store/protected-policy ownership and persistent installation/endpoint
discovery, complete resource/preset preparation, then connect native settings,
direct editing and actual activation. Undo, external authoring, migrations and
non-Linux storage/supervision are still required.

This is a bounded Linux IPC/ext4 composition using synthetic built-in resources
and explicit laboratory policy. Process exit is not power-loss durability proof.
Historical-toolset execution on the modern Windows host does not qualify an old
OS. No user desktop, unrelated VM, privileged operation or public release occurs.
