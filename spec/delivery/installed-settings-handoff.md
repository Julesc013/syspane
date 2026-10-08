---
type: "SysPane Handoff"
title: "Installed native settings frontend"
description: "The development application composes native settings, authenticated profile reads and independent configuration supervision."
tags: ["delivery", "experience", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T21:51:11.915443+00:00"}
sp_id: "SP-INSTALLED-SETTINGS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-INSTALLED-SETTINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed native settings frontend

The Linux development application now installs as bin/syspane with its private
configuration helper and compiled helper identity. It locates that closure through
the running executable, creates a private runtime root and delegates durable profile
ownership to the helper. GTK, native supervision and authenticated client work have
separate owners. The frontend never writes a settings generation itself.

The existing eleven settings controls receive one complete coherent profile and
its exact resources. Preview, Apply, Cancel, Revert and Reload use the existing
command contracts. A lost connection erases private UI state; unresolved commands
retain their original identity and block further editing. Reconnection retrieves or
reconciles that original request before loading a fresh profile. Closing remains
responsive while the supervisor confirms child exit and retires its runtime root.

The ordinary DevelopmentFrontend install component packages three files. It still
requires the pinned native libraries and protected production policy. A separately
compiled test consumer/helper supplies positive fixture authority and storage holds;
production accepts no policy or helper override. This is an unmanaged development
payload, not a complete edition or managed release installer.

## Evidence and preserved failures

All twelve fixed installed-frontend cases pass against relocated payloads, launched
from unrelated working directories. Independent AT-SPI/XTest observations and exact
stored documents/resources verify startup values, validation, preview/revert,
save/reopen, cancellation, replacement, durable lost-result reconciliation without a
duplicate revision, policy erasure, runtime/policy/helper refusal and close during
held storage. Independent pidfds establish actual child death, and native directory
observations establish runtime retirement. An intentionally wrong stored-document
oracle fails as required. CLI help/profile selection and invalid arguments are checked.

The existing native suites also pass: eighteen settings-form, nineteen supervisor
and seven profile-projection cases. Each of the three development profiles passes
64 portable settings/configuration/protocol checks and both component graph checks.
The Linux frontend and dedicated fixtures were built; Windows reused their unaffected
portable artifacts after reconfiguration. No Windows frontend or historical guest
qualification follows from those host checks.
Specification validation passes for 48 schemas and 166 fixtures. Specification-tool
unit tests were not repeated because their implementation did not change.

The first native attempt released held storage immediately after queuing Cancel.
The command legitimately committed before cancellation reached it. The corrected
observer waits for the controller's unknown response while storage remains held,
then releases the hold and still requires cancellation with unchanged revision 0.
The second attempt encountered an AT-SPI object destroyed between enumeration and
property access during replacement. Only that explicit missing-object reply now
invalidates the observation and retries within its original deadline, at most 128
times; other errors still fail. The original failures remain preserved. Production
frontend and helper bytes match across all four native attempts; expectations did
not change. The final attempt additionally checks every initial value and resource pin.

The [checkpoint](checkpoints/installed-settings.json) binds exact source snapshots,
artifacts, commands, package identities and outcomes. Nine native archives preserve
488,552,491 raw bytes. Four duplicate attempt directories were removed only after
complete archive/node/byte verification and live-process checks. The F runtime lab
and original crash orphans remain. Two initial archive index rows incorrectly retained
their pre-pruning status; original metadata and independent pruning receipts are
preserved alongside the corrected classification. The 8 GiB active workspace ceiling
and standard reservations are unchanged. Archived evidence remains local and ignored.

GTK selection-clipboard shutdown critical diagnostics remain in native stderr.
They require investigation before complete accessibility/shutdown qualification.
These checks also do not qualify protected-policy deployment, client queue exhaustion,
maximum native profile throughput, representative performance or all scheduling faults.

## Continue with the complete application

W-11 remains in progress. Connect the existing editor and inspector to this frontend,
extending verified installation closure to image and recovery helpers before launch.
Bind real telemetry, activation/visibility and the independent desktop escape/recovery
owners. Add installed session/draft context, import catalogs and persistence layers.
Preserve command reconciliation, current-policy erasure and independent expected
results. A settings window does not satisfy behind-icons desktop acceptance.

Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X remain required complete
editions. Their native hosts, historical laboratories, lifecycle, accessibility,
performance and release gates remain open. No privileged deployment or public
release was performed by this checkpoint.
