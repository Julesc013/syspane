---
type: "SysPane Handoff"
title: "Supervised native network service"
description: "Authenticated measured acquisition for the installed inspector's next integration."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T00:00:00+11:00"}
sp_id: "SP-NETWORK-SERVICE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-NETWORK-SERVICE", "SP-INSTALLED-INSPECTOR-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised native network service

The Linux helper now provides an independently supervised network service through
the existing verified installation and child owners. A typed supervisor selection
launches a separate network process, preserves exact child-reap/restart ordering
and assigns a fresh producer epoch. The ordinary configuration entry is unchanged.
No additional installed binary, manifest format or telemetry version is introduced.

The service owns native policy checks and admits only its declared console PID,
inspector channel and operational classification. Acquisition begins after an
authorized subscription. The original native task is shared with CollectorProbe;
demand, identity reconciliation, original measured clocks and complete publication
continue through the existing owners. Configuration features are refused on this
connection. Policy change, failed continuity and stalled acquisition end the epoch.

Eighteen native cases pass across NETWORK-SERVICE and NETWORK-SUPERVISOR. They
compare actual kernel counters and independently calculated rates, reject a
deliberately wrong counter, observe demand/watch ownership, enforce role/PID and
disclosure, exercise held acquisition and shutdown, and verify sealed launch,
native crash/restart, exact process exit, guardian death and runtime cleanup.
The [checkpoint](checkpoints/network-service.json) binds source archives, artifacts,
commands, raw results, regressions and limitations. Raw operational records remain
in ignored evidence; archives are byte-verified before duplicate outputs are removed.

The first hung-read attempt exposed a product defect: demand marked a task
cancelled at its deadline, while the service kept servicing health. The repair
consumes that cancellation and exits before a blocking task destructor can join.
The unchanged deadline then passes. Initial absent-entry and compiler failures
remain preserved. Observer repairs supply the required nonblocking inherited
socket and invalidate incomplete procfs FD enumerations within the original
observation deadline. The sealed-executable observation now records both the
shared verified memfd label and exact network invocation arguments after readiness;
its original incorrect label assertion remains recorded. These repairs do not
weaken counter, authorization, time or child-lifetime expectations.

The existing native regressions also pass: helper identity, configuration
supervision, runtime-directory ownership, asynchronous demand execution, original
measured collector, installed settings and installed inspector. Together with the
new cases, these comprise 109 named native cases across nine families. Portable
component/demand/session/network/telemetry checks pass 56 cases on Linux and 53
on each Windows development profile; two historical PE/import checks also pass.
These Windows host results do not qualify historical operating systems.

The actual CMake DevelopmentFrontend install produces the expected five-file
payload. Its archived bytes match the built artifacts and survive relocation.
The production network entry refuses startup despite the local fixture's allow
file; no protected policy was installed or changed. The package stays local and
unsigned. Its larger measured reservation fits the unchanged workspace cap; an
initial calculation that followed lab symlinks was corrected to the coordinator's
existing apparent-size method, with the original conservative stop preserved.

Specification validation passes 51 schemas and 183 fixtures. Tooling reports 62
tests, with 60 passing and two existing Windows symlink-privilege skips. Canonical
LF normalization was followed by a rebuild; the tested collector, helper and
supervisor binaries remain byte-identical. The checkpoint preserves both source
forms and exact artifact comparisons.

## Required continuation

The ordinary inspector still has no telemetry consumer. Connect the new service
to its existing frontend worker and native inspector with a bounded full-state
queue and explicit current-profile/session ownership. Preserve original receipt
and measurement times; queued heartbeats must not extend a dead producer's lease.
Keep current-policy erasure distinct from permitted stale retention. Start demand
only for an authorized active inspector and drain its task/service on navigation
or close. Identify network children by held process identity and exact invocation;
the shared configuration-helper memfd label alone does not distinguish roles.

Then qualify installed pixels, image/topology cases, maximum-input responsiveness,
human accessibility and desktop/lifecycle composition. Positive service tests use
a compiled, nonprivileged policy fixture; protected production-policy deployment
remains unqualified. W-11 and W-25 remain in progress. The complete Windows 9x,
Windows NT, Linux X11, Wayland and Mac OS X editions remain required and unfinished.
