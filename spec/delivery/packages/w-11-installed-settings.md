---
type: "SysPane Work Package"
title: "Installed native settings frontend"
description: "Compose the real application entry point, independently supervised controller and authenticated settings client."
tags: ["delivery", "experience", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T21:20:00+00:00"}
sp_id: "SP-W11-INSTALLED-SETTINGS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-SETTINGS-RESOURCES", "SP-W08-RUNTIME-DIRECTORY", "SP-W08-PROFILE-PROJECTION", "SP-W26-HELPER-IDENTITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed native settings frontend

Implement the actual Linux bin/syspane entry point and SettingsForm integration
in the existing application source tree. This is the first installed UI composition,
not the complete desktop edition. The same application must subsequently integrate
the editor, inspector, telemetry, behind-icons presentation and independent escape,
activation, recovery context and catalogs. Do not turn a conventional settings window
into evidence of a desktop host or reduce the five-edition release scope.

## Startup and ownership

The initial development installation is an unmanaged extracted payload containing
bin/syspane, libexec/syspane/syspane-configuration-host and share/syspane/helpers.json.
Compile the existing exact helper expectation into its consuming main. Verify the
actual running installation through LinuxInstallation before starting its helper.
No executable, expected digest or native policy override is accepted from the CLI,
environment or mutable documents. The production helper retains protected machine
policy and fails closed when that authority is absent. This does not enroll a setup
or package manager, grant privilege or qualify protected-policy deployment.

Support --help and --profile ID (default profile:default); reject unknown arguments.
Use profile_environment for explicit XDG configuration/data/state selection and
read XDG_RUNTIME_DIR for the runtime base. No current-directory or payload fallback.
LinuxProfileOwner remains the sole authority for creation and profile locks. Runtime
allocation uses LinuxRuntimeDirectory and its unchanged checks. Do not reject an
entire shared installation prefix merely because XDG paths also descend from it.
Existing native no-follow ownership and exact file identities still apply.

GTK owns the window, controls and one settings form. A separate serialized supervisor
thread owns installation, runtime, LinuxProfileSupervisor and exact child retirement,
polling at most 100 ms apart during ordinary scheduling. A separate client thread
owns native Stream, Framer, handshake, profile transfer and catalog preparation.
Blocking native calls, parsing and resource hashing must not run on GTK or prevent
supervisor polling. Native filesystem stalls remain subject to the existing helper
process boundary; no thread-completion flag substitutes for native child exit.

Cross-thread state has one current controller identity, one published immutable
profile/catalog, one pending request, one reply and coalesced reload/retrieve/cancel
intent. Use short mutex-protected transfers; no native I/O or GUI calls while holding
that mutex. UI callbacks enqueue and return. Reject a second unresolved mutation.
Private command bytes are at most the existing 327680-byte command limit and are
dropped once dispatched or withdrawn. Retain only original request ID, producer
epoch, local ticket, intent and expected revision for unresolved recovery.

## Authenticated connection and transfer

Connect only to the current supervisor-advertised endpoint and exact child PID.
Recheck its generation after blocking connection and before every publication.
Negotiate wire 0.1, the existing command 0.2 through 0.8, command-result, profile and
reconciliation documents. Require the existing implemented transaction/content/
large-command/edit-lock/visibility/theme/profile features, result.get, cancel and
result.reconcile. Reject a welcome outside the offered versions/features, wrong
role/epoch or undersized frame. Use the selected native connection ID; wire content
does not authenticate the peer. Initial frame ceiling is 328704 bytes.

Send one ordered heartbeat per second, require its matching echo within three
seconds, and reject unsolicited/regressed sequence values. Check elapsed deadlines
before admitting queued replies. Handshake and incomplete frames retain five-second
deadlines. Native writes use at most 100 ms each; native reads wait at most 10 ms.
Bound incoming delivery to sixteen queued messages and 65536 queued payload bytes;
one ProfileDownload request is outstanding at a time. Its existing part/total/idle/
absolute bounds remain. No partial profile reaches the GUI. Build the retained
ContentCatalog on the client owner from the complete admitted immutable resources.

One controller generation admits at most three connection attempts, spaced at least
one second apart after failure. An explicit Reconnect or Retrieve action may admit
a new bounded attempt batch; coalesce those actions and accept at most one per
second. This does not reset the supervisor's restart circuit. A new controller
generation has a fresh client attempt scope. No automatic mutation replay.

## Settings, erasure and recovery

Show startup/loading/unavailable states and retain a responsive Quit action. Once
native authentication, complete transfer and current disclosure checks succeed,
instantiate the existing SettingsForm from that coherent snapshot. Enable its
existing large-command support only with the negotiated capability set, preserving
the default refusal for older callers. Use the registry's unchanged eleven controls,
validation, policy locks, Preview, Apply, Revert, defaults and explicit Reload.
No setting operation writes storage in the frontend.

Request IDs combine a process-lifetime native random nonce and a strictly increasing
counter; local tickets and identities never wrap or silently reset. Preserve the
exact immutable command body for its one dispatch. Validate result structure,
native connection/epoch, request identity, intent and expected revision. Accepted
commit means exactly base+1, stored/durable true, visible false and pending activation.
Preview requires the original revision and writes nothing. Validate other terminal
facts through the existing draft contract. Unknown or malformed current results
remain unresolved. Cancel is for that original identity only and cannot undo a save.

Controller withdrawal or client loss drops shared profiles/results and invalidates
partial downloads. On the next GTK dispatch, within 200 ms under the admitted native
scheduler, erase the form's private documents, resources, text and errors. Retain its
bounded active identity until the external request owner resolves it. Gate all late
client publications by the current controller/connection generation; stale data
cannot repopulate controls. The helper's protected-policy sampling cadence remains
unchanged; the 200 ms bound starts at observed native loss, not an unobserved file edit.

After reconnect, use result.get in the same producer epoch or result.reconcile after
replacement before loading a new editable profile. Cross-epoch accepted reconciliation
must identify the original request and exact expected revision; unknown is not proof
of non-commit. Preserve it and expose Retrieve original request, with edits/reload
blocked. Once resolved, load a fresh coherent profile and create a fresh form so a
new producer's unchanged native policy revision is not treated as an in-epoch regrant.
Normal terminal results in an uninterrupted connection use existing form completion
without silently discarding an unsaved draft. Explicit Reload replaces the snapshot
only when no request is unresolved.

Quit first erases UI state and stops client admission, then asks the supervisory
owner to close. Continue GTK dispatch while awaiting actual child exit and owner
retirement. Destroy the supervisor before runtime.cleanup. Only then finish normal
application shutdown and join completed workers. Preserve cleanup failures and
unreaped children as closing/unavailable rather than claiming a clean stop. Closing
does not undo submitted commands. A later frontend process loads durable state and
never automatically retries a former mutation; durable frontend draft/session
restoration remains a subsequent integration requirement.

## Executable evidence

Freeze this package and installed-settings-cases.json before implementation. Build
both the production application and a dedicated test consumer from the same shared
frontend implementation. The test consumer has a separately compiled expectation
for a dedicated helper supplying fixture policy/phase holds. Never add such switches
to production. Package and relocate both three-file closures under the owned native
lab; launch from an unrelated directory. Preserve exact package/runtime/source IDs.

Use an independent Xvfb/private-D-Bus AT-SPI/XTest observer to inspect actual controls,
invoke native actions and read settings/scene/resources on disk against the existing
literal startup fixtures. Cover startup, validation/preview/revert, commit/reopen,
cancellation while storage is held, controller replacement, durable lost result and
original-request reconciliation with no revision 2, disclosure erasure, unavailable
runtime/policy/helper, cooperative close and close during held storage. Observe exact
child exit and runtime retirement independently. Include a deliberately wrong stored
document oracle. Keep original failures and do not change expected outputs to match
the implementation. Run affected settings/profile/reconciliation checks and the
existing native settings regression; verify component graphs on all three profiles.
