---
type: "SysPane Handoff"
title: "Supervised native profile controller process"
description: "Authenticated startup, current-policy result disclosure and interrupted command recovery."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:00:00+11:00"}
sp_id: "SP-PROFILE-CONTROLLER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-CONTROLLER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised native profile controller process

The private Linux syspane-configuration-host now runs the existing profile,
transaction, session and health components through a production entry point.
It authenticates its inherited parent channel, validates a bounded bootstrap,
opens the policy-bound profile and negotiates independent health/transaction
supervision before admitting the configured console peer. Production arguments
cannot inject policy, resources or fault behavior.

The session loop stays responsive while storage is blocked. Native policy sampling
runs on a joined worker before each bounded application dispatch/output batch and
periodically while idle. Policy-only and command work both require an independently
armed watch; policy refreshes during a command share its original absolute deadline.
Changed/unavailable policy drops queued disclosure and exits the process, including
same-revision semantic changes. A fresh sample after command completion gates its
result; a pre-completion sample cannot authorize that result.

The persistent storage thread retains native profile ownership. Per-watch command
and policy threads are joined before completion; AsyncCommands now exposes its
latched storage-fault state to trigger process replacement. Cooperative shutdown
closes the profile only after callers stop. Guardian loss and uncooperative shutdown
exit the whole process, without claiming cancellation or non-commit.

## Evidence and preserved failures

Seventeen fixed native cases pass in the admitted non-root Linux/ext4 environment.
An independent parent speaks the bootstrap/health protocol, holds a pidfd and
enforces startup/watch deadlines; an ordinary authenticated client speaks the
existing command protocol and validates result schemas. Independent file checks
compare exact defaults, commits and resource bytes against the earlier literal
fixtures. No successful child log is used as a storage oracle.

The cases cover cold startup, default native policy refusal despite environment
overrides, malformed authority input, wrong parent/client, actual absence of a
policy worker before arm, sequential commands/replay/reconnect, responsive heartbeat
and cancellation while storage waits, revoked/same-revision policy, held-policy
deadline, post-durable timeout and fresh-epoch reconciliation, guardian loss,
normal closure and blocked shutdown. The no-arm check holds the fixture policy
source: premature sampling would leave a marker and a visible extra native task.
A deliberately wrong stored-output expectation is rejected.

The first build failed the warning-as-error check on misleading indentation in the
test entry point; formatting was corrected. The first native run then refused
startup because the fixture advertised a Unix socket path longer than the existing
native limit. Its coherent initialized profile and fixed startup error were retained.
The runner now uses shorter private endpoint directories within the same owned
evidence root. Neither the native path contract nor test deadlines were weakened.

The [checkpoint](checkpoints/profile-controller.json) binds successful and failed
attempts, source captures, exact helper/probe hashes, existing regression results
and tooling checks. Raw recordings remain ignored local out/evidence/profile-controller*
content. Fresh checkouts regenerate evidence with the ordinary developer commands.
The production protected-policy source is unavailable in this lab and fails closed;
positive tests use a separate in-process fixture entry, not native policy provenance.

## Next admitted boundary

Integrate the private process with the real controller/inspector frontend and its
verified installation/helper lookup, exact Child ownership and bounded restart gate.
The native oracle supplies that parent here; this checkpoint does not ship an
installed supervisor or a desktop launcher. Add coherent policy-filtered profile
projection for native settings/editor startup, then connect telemetry, live scene
activation, recovery context, the import catalog and package/lifecycle commands.

Current native command IPC alone is not a desktop edition. Full layers/updates,
positive protected-policy deployment, other native storage/supervision adapters,
accessibility/performance, lifecycle and all five complete release editions remain
required. W-08 remains in progress. Earlier failures and blocked legacy/Mac
qualification remain preserved; no public release or privileged operation is granted.
