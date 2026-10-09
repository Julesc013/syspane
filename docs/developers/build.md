# Developer setup and checks

Shared build scripts, target profiles and dependency locks live in
[source/build](../../source/build/README.md). Generated artifacts and raw evidence
are local, ignored `out/` content. A fresh checkout does not include historical
recordings; deterministic build/tests do not require them. Native experiments that
validate a prerequisite build record must generate that record for their own source,
artifacts and environment before execution.

For the Windows/WSL campaign coordinator, create `out/campaign/`, copy
`source/build/workspace.example.json` to `out/campaign/workspace.json`, and explicitly
set the admitted distribution, non-root user and owned Linux campaign directory.
Keep that binding local. Run `python source/build/check_workspace_budget.py --action
build` before configuring or building; use `test` or `package` for those actions.
The common active-output budget is unchanged; retained `out/evidence/` archives
are measured separately. Never use the placeholder account from the example.

The [ordinary recovery package](../../spec/delivery/packages/w-11-production-recovery.md)
admits recovery/history through the common entry. After normal preflight/configure/
build, run `ctest --preset linux-x64-gcc13 -R
'^native[.](ADMITTED-RECOVERY|ADMITTED-SETTINGS)$' --output-on-failure`. Run/archive
each family separately within the active-output allowance. These use the unchanged
installed oracles with hostile diagnostic environment controls and a separately
compiled ordinary entry whose helper identity is supplied by the development fixture.
Production policy/helper refusal remains part of the original settings checks.

Run the original installed editor/recovery/settings, backend/GUI limits,
observer-failure, history/form/recovery and helper-supervision families. On all three
profiles run `ctest --preset <profile> -R
'^(editor[.](RECOVERY-|REQUEST-PREPARATION-|HISTORY-PREPARATION-|FRAGMENT-ADMISSION)|settings[.]|composition[.])'
--output-on-failure`; retain v141_xp artifact checks. The
[handoff](../../spec/delivery/ordinary-recovery-handoff.md) binds native evidence,
entry-code comparison and the still-unqualified protected deployment boundary.

The [native Apply package](../../spec/delivery/packages/w-11-request-form.md)
connects the existing request worker to the form. After ordinary preflight, configure
and build, run `ctest --preset linux-x64-gcc13 -R
'^native[.](EDITOR-REQUEST|EDITOR-REQUEST-EXIT)$' --output-on-failure`. The fixed real
GTK cases include held tasks, exact recovery digest, cancellation/late results,
unknown transport outcome and exit acknowledgement while image work is held.

Run the original history, reply, recovery-control, form and installed editor/recovery
families, then `ctest --preset linux-x64-gcc13 -R '^native[.]RECOVERY-GUI-LIMITS$'
--output-on-failure`. Preserve its original timing and erasure expectations. On all
three profiles run the request/history/component expression below and retain v141_xp
artifact checks. The [handoff](../../spec/delivery/request-form-handoff.md) records
123 final native cases and original failures. Ordinary-entry recovery/history
admission now passes separately above; these are development qualification commands.

The [native request package](../../spec/delivery/packages/w-11-request-worker.md)
adds one request slot to the existing Linux helper worker. After normal
preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]REQUEST-WORKER$' --output-on-failure`. Its fixed observer verifies
held/running cancellation, exact owner adoption and all three-kind admission orders.
Run the original history, helper-worker, recovery-preparation/admission and installed
editor/recovery consumers. Keep the unchanged 100-ms task-interface limits.

On all three development profiles, run `ctest --preset <profile> -R
'^(editor[.](REQUEST-PREPARATION-|HISTORY-PREPARATION-)|composition[.])'
--output-on-failure`, plus historical artifact checks on v141_xp. The
[handoff](../../spec/delivery/request-worker-handoff.md) preserves source-bound
results and the remaining form/recovery-digest integration boundary.

The [request preparation package](../../spec/delivery/packages/w-11-request-preparation.md)
adds portable detached command validation and current-owner adoption. After normal
preflight/configure/build on all three profiles, run `ctest --preset <profile> -R
'^editor[.]REQUEST-PREPARATION-' --output-on-failure -V`. The existing history test
target owns these cases; SYSPANE_TEST_REQUEST_PREPARATION is test-only. The COST case
reports capture, worker-plus-join and adoption separately for the fixed maximum scene.

Run the affected editor/settings/configuration/scene/protocol/component families
and legacy artifact checks, then native history, recovery preparation, helper and
installed editor/recovery consumers. The original synchronous begin entry remains.
The [handoff](../../spec/delivery/request-preparation-handoff.md) records portable
evidence; form integration and ordinary GUI qualification are pending.
Do not enable production recovery from these component measurements.

The [callback trace package](../../spec/delivery/packages/w-11-editor-callback-trace.md)
attributes GTK actions, drawing and application timers against the unchanged
installed GUI cases. Run `python3 tests/configuration/native_editor_callback_trace.py
--self-test` in the admitted non-root Linux laboratory. This compiles the test-only
preload probe and compares ordinary/instrumented GObject and timer behavior. Run
`python tests/configuration/editor_callback_trace_tests.py` for transcript checks.

After the ordinary workspace test preflight, run `python3
tests/configuration/native_editor_callback_trace.py <build>/syspane
<build>/syspane_frontend_fixture <build>/syspane_frontend_helper_fixture
<build>/native-evidence`. The driver repeats its probe preflight, records the
compiler and libraries, injects the probe only into the experiment and writes
callback-trace.json alongside the original result. It retains original GUI failure
exits. Complete frontend traces, callback symbols and per-process timer coverage
are required; overflow or missing records invalidate diagnosis. Inspect both
reports even when the command fails.

Wall spans and interval unions support attribution. The current WSL laboratory
reports substantial CPU-over-wall disagreement, so retain raw CPU values without
inferring utilization or blocked time. An instrumented pass cannot qualify latency.
The [handoff](../../spec/delivery/editor-callback-trace-handoff.md) identifies long
Apply/restore/form-timer work and preserves the earlier ordinary GUI failure.

The [immutable authored package](../../spec/delivery/packages/w-11-validated-authored.md)
adds a deep validated snapshot for surface layout. It carries no policy authority.
New topology and metrics are validated on every resolution; binding and current
authorization remain separate checks. Each live surface retains one extra bounded
authored pair, and each paint still measures current content and composes pixels.

After rebuilding all three development profiles, run `ctest --preset <profile> -R
'^(configuration|scene|editor|settings|protocol|composition)[.]' --output-on-failure`.
The new scene.AUTHORED-SNAPSHOT case uses the same 31 literal layout fixtures as its
pre-change reference adapter, plus ownership and invalid/current-input cases. Keep
SYSPANE_VALIDATED_AUTHORED_TEST confined to the scene test target. Run the v141_xp
legacy checks and the package's native rendering/editor/recovery regressions too.
Use the existing preview-cost diagnostic and unchanged ordinary GUI limits below;
diagnostic improvement alone does not enable production recovery. Preserve timeouts
and record concurrent workload when investigating timing-sensitive results.

The earlier [admission investigation](../../spec/delivery/recovery-admission-investigation-handoff.md)
preserves two failed ordinary GUI runs and the disabled production gate at that
checkpoint. The later Apply repair and ordinary-entry admission now pass current
qualification. The experimental recovery switch has been removed; only
syspane_frontend_fixture defines SYSPANE_FRONTEND_TEST_OBSERVERS=1.
syspane_frontend_entry_fixture has the ordinary main source and fixture helper
identity without observer support. It is not installed or represented as production.

For entry comparison, use `objdump -dr --disassemble=main` on
`<build>/CMakeFiles/syspane_frontend.dir/source/application/frontend_main_linux.cpp.o`
and `<build>/CMakeFiles/syspane_frontend_entry_fixture.dir/source/application/frontend_main_linux.cpp.o`.
The main code and relocations now match. Inspect `ninja -C <build> -t commands
syspane` and the corresponding entry-fixture command; record compiler/flags,
generated helper identities and common runtime library hashes. Only generated
identity include paths and object/executable destinations differ after normalization.
Production and the ordinary fixture contain no diagnostic environment handlers.

Keep the original failed GUI/diagnostic records and fixed expectations. The current
qualification follows a measured Apply repair; it is not inferred from byte equality
or a diagnostic pass. General authoring/preview responsiveness, protected deployment
and all complete release editions remain open.

The [recovery submission package](../../spec/delivery/packages/w-11-recovery-submission.md)
prepares structural eligibility while preserving current authorization and full Apply
validation. Run `ctest --preset <profile> -R
'^(editor[.](RECOVERY-|HISTORY-PREPARATION-|FRAGMENT-ADMISSION)|settings[.]|composition[.])'
--output-on-failure` after rebuilding all three profiles, then legacy artifact checks.
On Linux run the recovery limits/preparation, history worker/form, recovery controls,
frontend recovery and installed editor/recovery families. The unchanged ordinary
native.RECOVERY-GUI-LIMITS now passes for the source/artifacts in the
[handoff](../../spec/delivery/recovery-submission-handoff.md). Preserve earlier failures
and evaluate production admission separately from this development qualification.

The [history-form package](../../spec/delivery/packages/w-11-history-form.md) connects
the existing native worker to the experimental frontend's Undo/Redo. After ordinary
preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]EDITOR-HISTORY$' --output-on-failure`, then the worker, recovery, standalone
and installed editor, initial-input and reply lifecycle regressions. The component
mode uses real GTK and controlled tasks; the installed and worker cases exercise
actual native execution separately. Run portable history and component checks on
all three profiles. Finally run the unchanged native.RECOVERY-GUI-LIMITS command.
The [handoff](../../spec/delivery/history-form-handoff.md) records the failures; do not
substitute component success or diagnostic timings for ordinary GUI qualification.

The [history-worker package](../../spec/delivery/packages/w-11-history-worker.md)
adds bounded HistoryPreparationTask handles to the existing Linux helper worker.
After ordinary profile preflight/configure/build, run `ctest --preset linux-x64-gcc13
-R '^native[.]HISTORY-WORKER$' --output-on-failure`. Preserve the fixed literal scene
and cancellation expectations, including observed running tasks. Rerun the original
helper-worker, recovery-preparation/admission, installed editor/recovery, frontend
recovery and recovery-control cases. Run portable history and component checks on
all three profiles. Task-interface timing does not qualify complete GTK behavior.
The [handoff](../../spec/delivery/history-worker-handoff.md) records this boundary;
current-form integration and ordinary GUI qualification now pass in the experimental
frontend; ordinary-entry admission is now recorded above.

The [history-preparation package](../../spec/delivery/packages/w-11-history-preparation.md)
adds detached HistoryWork and opaque current-owner adoption. After ordinary profile
configure/build, run `ctest --preset <profile> -R '^editor[.]HISTORY-PREPARATION-'
--output-on-failure` on all three development profiles, then the affected portable
and existing native preparation/recovery/editor consumers. Keep the original trace
expectations; supplemental guards must not redefine their results.

The experimental installed GUI now consumes this API through the existing worker.
The ordinary entry now also admits the existing history worker;
current native preview validation/composition remains on the form owner.
The [handoff](../../spec/delivery/history-preparation-handoff.md) records the exact
implemented boundary, source-bound verification and remaining integration.

The [initial-preview package](../../spec/delivery/packages/w-11-initial-preview.md)
defers first composition to drawing or guarded earlier input. After ordinary
preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]EDITOR-INITIAL-INPUT$' --output-on-failure`. Its nine fixed cases use real
GTK controls without a first draw and compare exact submitted scenes. Preserve the
original pre-change expectations and all existing layout/refresh/installed/recovery
and image/erasure checks. Rerun the phase/paint diagnostics and ordinary GUI limits
separately. The [handoff](../../spec/delivery/initial-preview-handoff.md) preserves
the four delay failures at that checkpoint; the recovery submission checkpoint above
records the later passing ordinary qualification and remaining admission work.

The [native paint trace package](../../spec/delivery/packages/w-11-editor-paint-trace.md)
uses a test-only preload probe against the unchanged compiled frontend. After
ordinary preflight/configure/build, run `python3 tests/configuration/native_editor_paint_trace.py
<build>/syspane <build>/syspane_frontend_fixture
<build>/syspane_frontend_helper_fixture <build>/native-evidence` in the admitted
non-root Linux laboratory. The driver compiles the bounded probe under ignored
out/campaign/editor-paint-trace, supplies it only to this exercise and resolves
executable-relative stacks after process exit. It uses the profile compiler and
records compiler/library/symbolizer identities. The original failing GUI result
remains a nonzero exit even when paint-trace.json is complete. Inspect both.

Run `python tests/configuration/editor_paint_trace_tests.py` for transcript checks.
Capacity overflow or incomplete symbolization invalidates diagnosis. Never use
instrumented durations as qualification; retain the ordinary GUI command below.
The [handoff](../../spec/delivery/editor-paint-trace-handoff.md) records confirmed
call paths and the next initial-readiness/history-preparation boundaries.

The [prepared editor package](../../spec/delivery/packages/w-11-prepared-editor.md)
constructs an opaque PreparedEditor using ordinary full validation, without GTK.
Transfer its unique owner only after construction ends. EditorForm consumes it as
the sole initial semantic state; the traditional constructor remains synchronous.
The installed backend's take_editor requires the exact current shared profile and
returns empty for stale/loading/pending/closed/already-consumed state. Do not fall
back to GTK draft construction or infer current recovery authority from preparation.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13
-R '^native[.](PREPARED-EDITOR|FRONTEND-PREPARED-EDITOR)$' --output-on-failure`.
Run all selected portable families on the three profiles and legacy PE checks,
then native backend/maximum-input, installed recovery/editor/settings, standalone
editor/recovery, reply lifecycle, observer-failure and image/erasure regressions.
Use the existing phase command below and ordinary GUI qualification separately;
current prepared construction improves latency but does not pass all fixed limits.
The [handoff](../../spec/delivery/prepared-editor-handoff.md) records exact evidence.

The [frontend phase package](../../spec/delivery/packages/w-11-frontend-phases.md)
adds optional numeric attribution inside the existing GTK tick. After ordinary
preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.](EDITOR-REPLY-LIFECYCLE|FRONTEND-PHASE-FAILURE)$' --output-on-failure`.
Run the installed recovery/editor/settings, native recovery controls and original
editor/scene-image/erasure regressions when changing accepted-reply closure.
EditorForm's default reply behavior refreshes the form; close_on_accepted is for a
validated reply whose owner is replacing that form. Keep polling stopped() before
destruction and obtain fresh profile/recovery authority before constructing another.

For phase diagnosis run `python3 tests/configuration/native_frontend_phases.py
<build>/syspane <build>/syspane_frontend_fixture
<build>/syspane_frontend_helper_fixture <build>/native-evidence` in the admitted
non-root Linux laboratory. The wrapper enables the fixture-only phase/timing
observers and preserves the original GUI exercise and its failures. Inspect the
separate phases.json after all owned processes exit. Nested durations overlap.
The bounded decoder has a portable configuration.FRONTEND-PHASE-DECODER check.
Observer refusal/exception must fail the host while allowing normal child closure.
Production does not read any SYSPANE_TEST_PHASES or SYSPANE_TEST_PHASE_FAULT variables.

Always run ordinary native.RECOVERY-GUI-LIMITS without phase attribution as the
qualification check. Phase completion or reduced reply cost cannot qualify the
remaining construction/callback/painting work or enable production recovery.
The [handoff](../../spec/delivery/frontend-phases-handoff.md) records measured
differences, source-bound regressions and remaining failures.

The [draft admission package](../../spec/delivery/packages/w-11-draft-admission.md)
keeps submit eligibility structural results private to the current SettingsDraft;
every eligible call still authorizes current policy, and begin always revalidates.
Run `ctest --preset <profile> -R '^(editor[.](FRAGMENT|THEME-HISTORY)-|settings[.])'
after building. FRAGMENT-ADMISSION freezes observable outcomes from the original
implementation; THEME-HISTORY-SNAPSHOT verifies actual immutable owners and release.
Retain the broader portable suite and native clipboard, theme history, renderer,
erasure and recovery regressions when changing invalidation or preview ownership.
The existing preview-cost diagnostic records repeated/first submit costs and owning
snapshot transfer separately from its retained old catalog/resource measurements.

The [schema hot-path package](../../spec/delivery/packages/w-11-recovery-hotpaths.md)
compiles the finite trusted schema graph once, without retaining authored values or
validation results. Run `ctest --preset <profile> -R '^configuration[.]AUTH-SCHEMA-EQUIVALENCE$'
after building. Its 5823 fixed public-API cases compare against results captured on
all three toolchains before the evaluator change. The runner cannot regenerate its
expectations. Preserve a discrepancy and investigate it alongside the independent
schema fixtures and semantic tests. This check does not qualify GUI responsiveness.

The [native text session package](../../spec/delivery/packages/w-11-text-session.md)
reuses Linux font setup within one synchronous composition. Run `ctest --preset
linux-x64-gcc13 -R '^native[.](TEXT-RASTER|TEXT-SESSION|THEME-TYPOGRAPHY)$'
after building. TEXT-SESSION compares 30 frozen original requests in isolation and
three shared-session orders, including exact pixels/errors, rejection recovery and
wrong-thread refusal. Expected results are pinned to the recorded font runtime.
Retain the scene/role/visibility/table/chart/image and erasure checks when changing
composition. A TextSession must die before frame publication; requests and retained
objects must never store its borrowed pointer. The test-only probe joins its
wrong-thread witness before continuing; production gains no thread or scheduler.

The [recovery limits package](../../spec/delivery/packages/w-11-recovery-limits.md)
and [GTK observation contract](../../spec/delivery/packages/w-11-recovery-gui-limits.md)
freeze maximum valid inputs independently of product output. After ordinary preflight,
configure and build, run `ctest --preset linux-x64-gcc13 -R '^native[.]RECOVERY-LIMITS$'
--output-on-failure` and then `ctest --preset linux-x64-gcc13
-R '^native[.]RECOVERY-GUI-LIMITS$' --output-on-failure`. Run/archive families separately
under the unchanged workspace budget. The latter is currently a failing qualification
gate, not a passing product acceptance claim; its observer preserves all seven cases.

The GTK fixture enables the optional timing callback with SYSPANE_TEST_TIMING=1 and
passes a nonblocking stdout pipe. The production entry point never reads this variable.
No additional timer or worker is created. Individual work and excess-delay samples
must each stay within 100 ms, including failed semantic cases. The observer records
bounded numeric output and exact files; malformed/missing output cannot mean a pass.

For stage diagnostics, run `python3 tests/configuration/native_recovery_preview_cost.py
<build>/syspane_frontend_recovery_probe <build>/syspane_frontend_helper_fixture
<build>/native-evidence` in the admitted non-root environment. Diagnostic completion
only records stage costs. It does not satisfy any latency criterion. Existing schema
patterns are compiled once from the trusted finite schema set; no authored string
may create a cache entry. Original validation and matching rules remain required.

Run `ctest --preset <profile> -R '^(editor|settings|configuration|scene|protocol|composition)[.]'
--output-on-failure` on all three development profiles after changing shared validation.
Retain the installed recovery/settings/editor, backend, preparation and recovery-controls
native regressions. See the [measured results and next repair](../../spec/delivery/recovery-limits-handoff.md).

The [installed recovery package](../../spec/delivery/packages/w-11-installed-recovery.md)
connects the actual GTK editor to recovery()/preparations(), authenticated current
binding and accepted-draft metadata. EditorForm::Actions::submit_recovery receives
the capture digest before callback dispatch; do not reenter the form from callbacks.
Bind retirement metadata with fresh admission and acknowledge the current profile
serial only after retirement_decided(). Policy withdrawal erases cached results;
completion handlers use reply outcomes only after original-request validation.

The ordinary entry now admits the qualified recovery/history path. Both development
entries use that same admission; only the observer fixture defines
SYSPANE_FRONTEND_TEST_OBSERVERS=1. There is no runtime feature override. Current
policy and helper authority remain mandatory; protected deployment is unqualified.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13
-R '^native[.](INSTALLED-RECOVERY|INSTALLED-EDITOR|INSTALLED-SETTINGS|FRONTEND-RECOVERY|RECOVERY-PREPARATION|EDITOR-RECOVERY)$'
--output-on-failure`. Run/archive families separately within the existing quota and
run both composition checks on all three profiles. The new family stages one relocated
five-file fixture and verified ZIP. Original installed families also cover production
packaging and helper substitution. Native observations verify exact recovery bytes,
documents, selecting records and child exit. Preserve crash orphan roots explicitly;
clean-close assertions apply to each subsequent newly owned runtime allocation.
Raw archives and the original failures are indexed by the
[handoff](../../spec/delivery/installed-recovery-handoff.md).

The [frontend recovery backend](../../spec/delivery/packages/w-11-frontend-recovery.md)
now negotiates profile 0.2 and supplies current session authority to its existing
native helper worker. Use recovery()/preparations() from the GUI owner; their factory
parameters do not grant authority. Each reload creates a fresh session and withdraws
old tasks. Null context keeps ordinary settings and editing available.

Pass submit() an optional digest only for the editor's completed durable capture.
The client worker matches it to the actual scene commit before dispatch. After an
accepted result/reconciliation, reload for a current FrontendProfile. Its optional
recovery_retirement is metadata: load through fresh admission, compare the exact
digest and conditionally retire only a match. Preserve a replacement or denial.
After the decision, acknowledge_retirement(profile.serial); a stale or missing
receipt is refused. The installed EditorForm now consumes this in the experimental
fixture; complete scheduling/latency qualification still gates production enablement.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13
-R '^native[.](FRONTEND-RECOVERY|INSTALLED-SETTINGS|INSTALLED-EDITOR|RECOVERY-ADMISSION|EDITOR-HELPER-WORKER|RECOVERY-PREPARATION)$'
--output-on-failure`. Run/archive these families separately under the unchanged
quota. The new family stages one relocated five-file bundle plus ZIP; forecast twice
the combined artifact sizes and 16 MiB of fixtures. Use the existing marker-verified
short runtime root; profile state roots admit only their specified three entries.
Run both composition checks on all three profiles. Preserve original failed attempts.

The [recovery preparation package](../../spec/delivery/packages/w-11-recovery-preparation.md)
adds EditorDraft::recovery_capture_work/recovery_restore_work and opaque prepared
results. Run RecoveryWork::run off the GUI, then consume only through the original
draft's recovery_capture, inspect_recovery or restore_recovery overload. Every
authored/request/policy/connection/baseline attempt invalidates older proofs, even
when rejected or unchanged. Selection alone is permitted. No caller-built candidate
can replace the opaque proof, and current authority is rechecked at consumption.

Pass EditorHelperClient::preparations() alongside its recovery factory to
EditorRecoverySession or EditorForm::recovery for asynchronous consumption. The
existing native owner pumps both; factories/handles remain on the GUI. Keep one
active preparation and one latest pending input, and continue closure polling until
the worker acknowledges acquired computation. Apply waits for durable capture,
not just completed preparation. Do not enable installed recovery before live scope,
matching applied-draft retirement and complete native scheduling are qualified.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|protocol[.]|composition[.])'
--output-on-failure` on all three development profiles. On non-root Linux run
`ctest --preset linux-x64-gcc13 -R '^native[.](RECOVERY-PREPARATION|RECOVERY-ADMISSION|EDITOR-HELPER-WORKER|RECOVERY-QUEUE|RECOVERY-STORE|PROFILE-OWNER|RECOVERY-CONTEXT|RECOVERY-TRANSFER|EDITOR-RECOVERY|EDITOR-FORM|IMAGE-JOB|SCENE-IMAGE|IMAGE-ERASURE|INSTALLED-SETTINGS|INSTALLED-EDITOR)$'
--output-on-failure`, splitting families and archiving completed owned recordings
when the unchanged workspace budget requires it. Preserve failed runs; the
[handoff](../../spec/delivery/recovery-preparation-handoff.md) records the Windows
resource-limit timing failure separately from its isolated passing rerun.

The [native recovery admission](../../spec/delivery/packages/w-11-recovery-admission.md)
adds LinuxRecoveryAdmission on the existing helper worker. Supply the locally selected
ProfileLocation, the validated transferred view and a Current callback from the live
authenticated connection owner. That callback returns no authority on connection,
epoch, profile, session or policy loss. Return the exact current document/policy
revisions and current retention/erase permission; never construct authority from the
GUI task's parameters. The admission compares local path selection, holds native
directory nodes and permanently withdraws on a failed verification.

Pass a trusted RecoveryAdmissionFactory to LinuxEditorHelperOwner. It runs on that
worker outside shared locks, and its immutable context must match the requested task.
The parent checks current authority through each operation and result delivery; the
sealed child independently checks expected directory identities before creating its
writer file. Existing explicit path experiments keep their original constructor.
The backend now supplies that live callback. The ordinary installed form connects
capture, submission and post-commit retirement after worker/GUI and maximum-input
qualification. Protected deployment remains a separate authority boundary.

After the ordinary configure/build and budget checks, run
`ctest --preset linux-x64-gcc13 -R '^native[.](RECOVERY-ADMISSION|EDITOR-HELPER-WORKER|RECOVERY-QUEUE|RECOVERY-STORE|PROFILE-OWNER|RECOVERY-CONTEXT|RECOVERY-TRANSFER)$' --output-on-failure`.
The new family observes real sealed children in a relocated five-file bundle. Keep
its fixed cases and preserve actual files after withdrawal; a previously dispatched
publication guard can race withdrawal, which is not rollback. Archive and verify
completed recordings before reclaiming duplicates when workspace headroom is needed.

The [recovery transfer](../../spec/delivery/packages/w-08-recovery-transfer.md)
extends the existing authenticated profile session with configuration.recovery-context
and profile-request/profile-result 0.2. Negotiate both versions and configuration.profile
before constructing ProfileDownload with an explicit ProfileRecoveryScope containing
the expected profile and editor session. Include editor.recovery in the receiver's
locally admitted capabilities. The default mode remains the 0.1 reader.

After completion, ProfileView::recovery is optional. Its typed admission is bound
to the authenticated connection/epoch, requested scope, exact transfer, revision and
policy generation. Null means recovery is unavailable. Resource capability headers
retain their legacy contents; native recovery capability admission belongs to the
trusted recovery provider. Never convert the projected policy or directory pathname
into native authority. The installed owner must match its current session and verify
the directory nodes before helper work; invalidate every received view on authority loss.

Run `ctest --preset <profile> -R '^configuration[.](RECOVERY-TRANSFER-|PROFILE-|COMMAND-|RECON-)' --output-on-failure`
on all three development profiles after their ordinary budget/build checks. On Linux,
run `ctest --preset linux-x64-gcc13 -R '^native[.](RECOVERY-TRANSFER|RECOVERY-CONTEXT|PROFILE-PROJECTION|PROFILE-CONTROLLER|PROFILE-WORKER)$' --output-on-failure`.
Keep the original 0.1 byte oracle and raw failed attempts. The native test uses the
existing unprivileged controller harness and independent filesystem observations.

When specification-tool tests use an owned temporary root under out/, set TMP and
TEMP to that root and GIT_CEILING_DIRECTORIES to the same absolute root. This prevents
the no-repository fixture from discovering the enclosing checkout. Let temporary-file
cleanup finish before workspace accounting; a disappearing node makes that inspection
unavailable and must not be converted into an assumed capacity pass.

The [native recovery snapshot](../../spec/delivery/packages/w-08-recovery-context.md)
is available through LinuxProfileStore::recovery_snapshot(authority) and the blocking
LinuxProfileWorker facade. Call it from a trusted controller worker. Its committed
documents and optional admission describe one accepted generation; resources retain
their shared immutable allocations. Admission includes verified native directory
identities and current retention/erase permission. It is absent for recovery denial
or damaged-selector fallback. Policy/path changes invalidate the profile owner.

After the ordinary budget/configure/build checks, run
`ctest --preset linux-x64-gcc13 -R '^native[.](RECOVERY-CONTEXT|PROFILE-OWNER|PROFILE-STARTUP|PROFILE-WORKER|PROFILE-CONTROLLER)$' --output-on-failure`
and the component graph checks on all three development profiles. The new observer
requires a non-root native ext4 laboratory and independently checks selector bytes,
directory identities, shared resources and actual process exit.

The API returns trusted internal state, like load(). Do not disclose it directly,
infer a client session from it or enable installed recovery from its paths alone.
The transfer contract above now binds coherent state to authenticated peer/epoch/
profile/session. Independent native directory verification before helper operations,
existing editing checks, revocation guards and recovery validation latency remain
separate requirements.

The [installed scene editor](../../spec/delivery/packages/w-11-installed-editor.md)
uses the actual frontend entry point and the existing supervisor/client workers.
DevelopmentFrontend installs bin/syspane, libexec/syspane/syspane-configuration-host,
libexec/syspane/syspane-image-worker, libexec/syspane/syspane-recovery-worker and
share/syspane/helpers.json. Move the complete payload together; helper record 0.2
and the executable's compiled expectations cover all roles. Record 0.1 is retained
only for its other explicit consumers.

After ordinary budget/configure/build checks, run
`ctest --preset linux-x64-gcc13 -R '^native[.]INSTALLED-EDITOR$' --output-on-failure`.
Run INSTALLED-SETTINGS, EDITOR-FORM and EDITOR-HELPER-WORKER regressions and the
configuration/profile/command and composition checks. The editor family packages
both production and fixture payloads; forecast twice their combined five-file sizes
for extracted files and ZIPs, plus 16 MiB fixtures. Archive completed recordings
before launching another large family if the unchanged workspace limit requires it.

Settings and Edit scene navigation requires a current clean draft and no private
fields, modal editor, gesture or pending command. Navigation requests a new coherent
profile; Cancel session explicitly discards and returns to Settings. GDK topology
uses session monitor identities. The outer form scrolls within the initial work area,
leaving application navigation and Quit accessible. Production recovery remains visibly
unavailable pending full scheduling/latency qualification. The installed experimental
form now connects scoped 0.2 transfer, native admission and exact capture retirement.
Do not infer authority from a revision or XDG path. Missing telemetry is not synthetic data.

The [editor helper worker](../../spec/delivery/packages/w-11-editor-helper-worker.md)
provides EditorHelperClient on the GUI owner and LinuxEditorHelperOwner on the
existing serialized native worker. Attach the latter with the shared verified bundle
before admitting factory calls. Pass images() to SceneSurface/EditorForm and the
stable shared recovery() factory to EditorRecoverySession/EditorForm. Factories
have no helper pathname and confer no recovery retention or directory authority.

Pump the native owner at least every 10 ms in the development host. GUI task poll()
only reads state. Four retained image slots share two active native jobs; dropped
active tasks retain slots until actual closure. Recovery admits one immutable context,
requires GUI consumption of load, coalesces pending captures and fences retirement.
Close GUI consumers/client, continue native pumping until stopped, release GUI task
handles and destroy the native owner on its own worker. GUI destruction never joins it.

After budget/configure/build checks, run
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-HELPER-WORKER|IMAGE-JOB|RECOVERY-QUEUE|SCENE-IMAGE|IMAGE-ERASURE|EDITOR-RECOVERY|EDITOR-FORM|INSTALLED-SETTINGS)$' --output-on-failure`
and the composition checks on all three development profiles. Run/archive larger
native families separately under the quota. Forecast the worker family's five-file
extracted payload plus ZIP (twice their combined bytes) and 16 MiB fixture allowance.
Its test observer requires unprivileged ptrace and verifies held kernel exec stops.

The actual task interface has the fixed 100 ms development observation bound.
Consumer timings also include synchronous document validation/rasterization; record
those separately. Recovery-offer validation exceeded that bound in the initial
consumer run and remains an installed-editor performance issue. This worker does
not enable installed recovery, authenticate its directory, or qualify whole-UI latency.

The [editor helper bundle](../../spec/delivery/packages/w-26-editor-helper-bundle.md)
adds explicitly selected helper record 0.2 and built_helper_bundle_expectation().
Its fixed roles are configuration, image and recovery. Construct LinuxInstallation
with that expectation on a serialized native worker, then pass its shared owner to
ImageJob or LinuxRecoveryQueue. Verification covers the entire bundle on every launch;
failure has no pathname fallback. A failed image constructor creates no child. The
recovery queue reports its existing unavailable/failure outcome, with no storage
success claim. Keep filesystem verification off the GTK thread.

After the ordinary build/test preflights, run
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-HELPER-BUNDLE|HELPER-IDENTITY|IMAGE-JOB|RECOVERY-QUEUE|INSTALLED-SETTINGS)$' --output-on-failure`.
Account for each native family's extracted payload/archive growth before running;
under the campaign quota, run and archive the larger families separately. The bundle
family forecasts twice the combined five-file payload size plus 16 MiB. It uses one
reusable relocated payload and exact mutation snapshots. Its unprivileged tracer
observes helper exec before image containment disables inspection, detaches before
worker instructions run and holds independent pidfds through exit. Tests require
that native tracing capability; absence is a blocked check, never an inferred pass.

The installed-editor package above advances DevelopmentFrontend to five files.
Record 0.1 remains for its other explicit consumers. Verified helpers do not grant
recovery retention authority or qualify a desktop edition. Bind installed recovery
to the authenticated profile, session, generation and current policy next.

The shared private text control owns one GtkTextBuffer. Callers may edit its contents,
but must not replace/share the buffer or alter its clipboard registrations. Its native
lifecycle wrappers balance GTK's bookkeeping without enabling implicit PRIMARY or
CLIPBOARD publication. See the [lifetime package](../../spec/delivery/packages/w-11-private-text-lifetime.md).

After the ordinary budget/configure/build checks, run
`ctest --preset linux-x64-gcc13 -R '^native[.](PRIVATE-TEXT-LIFETIME|SETTINGS-FORM|EDITOR-FORM|INSTALLED-SETTINGS)$' --output-on-failure`.
The dedicated consumer runs with fatal criticals on an isolated display; its observer
holds both selections and detects transient ownership loss. Keep native stderr and
baseline failures. The installed family still requires its additional payload-space
forecast. Other native environments and complete accessibility remain unqualified.

The [installed settings package](../../spec/delivery/packages/w-11-installed-settings.md)
adds the real `syspane` frontend on the Linux development profile. After the ordinary
configure/build preflight and preset commands, stage its unmanaged development
payload into a fresh owned native prefix:

```sh
cmake --install "$SYSPANE_LINUX_BUILD_ROOT/linux-x64-gcc13" --prefix "<owned-native-prefix>" --component DevelopmentFrontend
<owned-native-prefix>/bin/syspane --help
<owned-native-prefix>/bin/syspane --profile profile:default
```

The payload now contains `bin/syspane`, all three private helpers and their exact
bundle record, as specified by the installed-editor package above. The main embeds
that record's expected identity; lookup does not depend on the working directory.
Native libraries remain the pinned development runtime; this is not a self-contained release.
Profile directories come from the existing XDG selector, and XDG_RUNTIME_DIR must
already name a private admitted native base. Production still requires protected
machine policy; absent authority produces an unavailable UI, not a policy bypass.

The GTK owner handles controls. Separate client and supervisor threads handle
authenticated framing/profile/command work and native process/runtime ownership.
Reconnect preserves unresolved request identities and retrieves/reconciles them
before reopening editing. Quit remains responsive while waiting for actual child
exit. A conventional settings window does not provide desktop-host qualification.

Run `ctest --preset linux-x64-gcc13 -R '^native[.]INSTALLED-SETTINGS$'
--output-on-failure`. This creates and relocates production and dedicated fixture
payloads in the owned laboratory, then observes native controls and actual stored
documents. The separate fixture consumer compiles its own exact helper expectation;
its policy/phase controls are absent from production. Preserve each native record,
package and node inventory before reclaiming duplicate output. The F runtime lab
base retains its marker and crash orphans. The ordinary 8 GiB allocation and fixed
preflight reservations remain unchanged; account separately for the two extracted
payloads and their ZIP archives before running the family.

The [runtime directory package](../../spec/delivery/packages/w-08-runtime-directory.md)
provides LinuxRuntimeDirectory for the frontend's independent native owner. Pass an
explicit native runtime base; ordinary frontend composition should select
XDG_RUNTIME_DIR and report unavailable when it is absent or inadmissible. There is
no implicit path fallback. The base must already be private, canonical and on the
admitted native filesystem, with at most 50 path bytes. The new empty root preserves
the supervisor's existing 70-byte limit.

Construct and use both owners on the supervisory worker. Pass runtime.path() to
LinuxProfileSupervisor. On close, keep polling and draining the supervisor until
it is closed, destroy it to release its flock, then call runtime.cleanup(). A busy
lock is retryable. Changed identity or unexpected contents permanently invalidate
the runtime owner and preserve the directory. Its destructor never deletes paths.

Run `ctest --preset linux-x64-gcc13 -R '^native[.]RUNTIME-DIRECTORY$'
--output-on-failure` after the ordinary build and test preflights. The independent
oracle uses the owned campaign's private R lab base, retaining its marker, orphan
directories and node snapshots. Its restrictive-umask case records the original
unreadable node before restoring lab access for storage accounting; the production
owner does not repair it. The composed cases use the existing dedicated supervisor
helper, not a production policy override. Continue with authenticated frontend
commands and reconciliation; this library is not an installed desktop application.

The [profile projection package](../../spec/delivery/packages/w-08-profile-projection.md)
adds configuration.profile with profile-request/profile-result 0.1 and a 12288-byte
negotiated frame floor. The existing native controller exposes it only to its exact
authenticated console peer with current operational and sensitive inspector and
accessibility disclosure. No new endpoint or policy override is introduced.

Use ProfileDownload on the independent native client worker after authenticating
the controller, fixing the connection/producer epoch and admitting local capabilities.
Send request(query_id) in profile.read and pass the decoded profile.chunk to receive.
Wait for complete() before obtaining view(); its documents, resources and effective
UI policy belong to one saved revision. Build SettingsResources from
ContentCatalog::retained(*view.resources), the exact selection and admitted
capabilities before handing it to SettingsDraft/EditorForm. Native IO, decoding and
catalog validation stay outside GUI callbacks. The view is not proof of activation.

Await each response, preserve the fixed transfer deadlines and call invalidate()
on transport/epoch/policy loss, including after completion. Clear every UI-owned copy
through existing erasure paths. Reconnect starts a new read; command reconciliation
continues separately with the original mutation identity. The projected policy
describes UI constraints and never supplies controller/native Authority.

After budget preflight/configure/build, run `ctest --preset <profile> -R
'^(configuration[.](PROFILE-|COMMAND-|RECON-|INITIAL-PROFILE|DIGEST)|protocol[.])'
--output-on-failure`. Linux also runs native.PROFILE-PROJECTION and the existing
controller/supervisor/command/reconciliation/supervision families. Run component
graphs on all profiles. Preserve exact source/artifact/native records; the
[handoff](../../spec/delivery/profile-projection-handoff.md) states remaining
frontend, protected-policy and complete-edition requirements.

The [helper identity package](../../spec/delivery/packages/w-26-helper-identity.md)
adds LinuxInstallation and Child::launch_sealed. Linux builds generate helpers.json
and helper_identity.hpp under the owned build's generated/ directory after producing
the configuration host. The generator checks ELF/interpreter/import closure and
pins the exact helper bytes. Depend on syspane_helper_identity_data before compiling
a consumer of helper_identity.hpp; it is a build-generation utility, not an installed
runtime component. Never obtain HelperExpectation from preferences or an adjacent file.

The consuming application must be bin/syspane under the admitted prefix, with the
helper at libexec/syspane/syspane-configuration-host and the record at
share/syspane/helpers.json. Construct LinuxInstallation(built_helper_expectation())
on the independent native owner, then pass its shared owner to LinuxProfileSupervisor.
Native verification and copying happen outside GUI callbacks. Retain the owner
through child launch and retire it after detected installation change. Original
application acquisition, deployment/data/runtime ownership and complete release
closure remain separate admission requirements.

After ordinary budget/configure/build checks, run `ctest --preset linux-x64-gcc13 -R
'^native[.](HELPER-IDENTITY|PROFILE-SUPERVISOR|PROFILE-CONTROLLER|RECOVERY-QUEUE)$'
--output-on-failure`, the affected configuration DIGEST/COMMAND-/RECON-/INITIAL-PROFILE
families and all three component graphs. The helper-identity oracle produces a local
four-file development ZIP; its bin/syspane is a test application. Preserve the ZIP,
per-step image inventories and compressed mutation blobs alongside its native result,
including failed runs and the separately recorded short runtime root. See the
[handoff](../../spec/delivery/helper-identity-handoff.md) for exact limits and remaining
frontend, protected-policy and release work.

The [supervisor package](../../spec/delivery/packages/w-08-profile-supervisor.md)
provides LinuxProfileSupervisor for the native configuration helper. Supply a
previously admitted canonical helper ELF, an empty canonical 0700 runtime directory
on ext4/tmpfs (at most 70 path bytes), ProfileLocation, creation intent and the exact
console PID. The helper path is a trusted native input, never a wire/environment
lookup or evidence of installation provenance. Run this owner independently of
storage and outside GUI callbacks, polling at least every 100 ms.

Drain take() regularly; its bounded native events support owner diagnostics. Use
status().endpoint only while ready. On loss of readiness invalidate the command
connection; after a new epoch reconnect and reconcile original requests without
repeating mutations. close() is terminal: continue polling until closed before
destruction, and inspect the actual last_exit and any cleanup fault. Never infer
non-commit from a stopped controller. The empty runtime root remains caller-owned.

After budget preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.](PROFILE-SUPERVISOR|PROFILE-CONTROLLER|COMMAND-IPC|RECONCILIATION|TRANSACTION-SUPERVISION)$'
--output-on-failure` and the component graph checks on all three profiles. The
independent supervisor test owns short runtime roots inside the existing Linux
campaign (alongside the profile build directory) and records them with its evidence.
Preserve those roots as well as native-evidence recordings, including failed runs.
See the [handoff](../../spec/delivery/profile-supervisor-handoff.md). Verified
installation lookup is supplied above; frontend/profile projection and complete
native editions remain pending.

The [native controller package](../../spec/delivery/packages/w-08-profile-controller.md)
builds the private Linux `syspane-configuration-host` helper. Its sole argument is
its actual parent PID; descriptors 0/1 carry the inherited nonblocking authenticated
Unix channel. A verified parent supplies the exact bounded bootstrap, then the
existing recovery.health/recovery.transaction handshake. The production entry uses
fixed native machine policy and offers no fixture or environment policy override.
The helper is not a standalone desktop or an installed supervisor.

Resolve profile locations in the trusted frontend and keep the advertised client
endpoint within the existing Unix path limit in a private 0700 runtime directory.
The independent parent owns startup/operation deadlines and actual child stop/reap.
Arm each watch before native execution; finish never extends its absolute deadline.
Policy-only refreshes also require watches. Reconnect under a new producer epoch
and reconcile original requests after replacement; do not resubmit mutations.
Shutdown returns zero only after normal worker/profile closure. The package defines
fixed startup, guardian-loss, active-fault and policy-invalidated exit codes.

After budget preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]PROFILE-CONTROLLER$' --output-on-failure`. The separate fixture entry
injects positive policy and held I/O; it does not qualify protected-policy deployment.
Run PROFILE-WORKER/STARTUP/OWNER, command IPC/reconciliation/supervision, storage
regressions, shared command cases and component graphs. See the
[handoff](../../spec/delivery/profile-controller-handoff.md) for preserved failures
and the remaining frontend, profile projection, native UI and package work.

The [profile worker package](../../spec/delivery/packages/w-08-profile-worker.md)
connects LinuxProfileStore to AsyncCommands without transferring a native owner
between threads. LinuxProfileWorker implements the same blocking GenerationStore
interface. Create it during supervised controller bootstrap; construct AsyncCommands
with make_resource_provider(worker, capabilities), then keep subsequent store calls
on the serialized command worker. Its dedicated storage thread retains all profile
leases. Session queries continue to use the existing immutable receipt snapshot.

Only one outer invocation is admitted; concurrent calls/close return
profile_worker.busy. Publication guards may read through the facade on the native
storage thread; recursive publication/lifecycle calls and other callback reentry
refuse. After invalidating command admission and joining transaction workers, close
the facade off the UI loop. close joins storage and releases leases; it does not
bound a hung I/O operation. Installed composition still needs the existing exact
process supervisor and transaction deadlines. Never detach or kill a C++ thread.

After budget preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]PROFILE-WORKER$' --output-on-failure` in the admitted non-root ext4 lab.
Run profile/startup/storage regressions and configuration.COMMAND-/RECON- checks,
plus component graphs. The [handoff](../../spec/delivery/profile-worker-handoff.md)
records thread observations, exact stored bytes, actual process cuts and remaining
installed lifecycle/policy requirements. Positive policy cases are in-process test
fixtures; no product policy override or installed policy is introduced.

The [initial profile package](../../spec/delivery/packages/w-08-profile-startup.md)
provides initial_profile and LinuxProfileStore. Shipped scene/theme bytes come from
configuration/defaults/profile.json; settings defaults come from the existing
registry. No runtime test fixture or build path is needed. The composed store uses
machine_policy by default, owns the three profile leases and seeds revision zero
only within a new configuration leaf's private stage. Existing roots never reseed.

Create and use it on one supervised worker, with the admitted capability set and
explicit ProfileLocation/creation intent. Bind the existing Transactions and resource
provider to this GenerationStore. A changed or unavailable policy permanently
invalidates the owner; construct a fresh owner after verified stop/reap. load is a
trusted authored-state read, not a policy-filtered UI projection. An accepted commit
still has separate activation/visibility facts. Test injection is only a native
in-process PolicySource; do not expose policy overrides in product arguments.

After normal preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]INITIAL-PROFILE$' --output-on-failure` on each development profile.
Linux additionally runs native.PROFILE-STARTUP, PROFILE-OWNER, CONFIG-STORE,
RESOURCE-GENERATIONS, CONTENT-COMMANDS and RECOVERY-STORE. Run component graphs on
all profiles. The [handoff](../../spec/delivery/profile-startup-handoff.md) records
exact artifacts, native cuts and policy provenance limits. Bootstrap manifest 0.5
has no client receipt; real later edits retain their existing command identities.

The [profile ownership package](../../spec/delivery/packages/w-08-profile-owner.md)
adds LinuxProfileOwner. Resolve ProfileLocation from explicit native environment or
an explicitly selected portable data root. Construct on a serialized worker with
an explicit creation flag and current native authority guard. Retain the owner for
the controller lifetime and call verified_paths before handing the generations,
packages or recovery children to their existing owners. A failed verification
invalidates the owner; regrant needs a fresh owner. Do not copy markers into stores,
adopt unmarked directories, infer policy from environment strings or run filesystem
work in GTK callbacks. Installed composition must use supervised workers.

After preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^(native[.]PROFILE-OWNER|composition[.])' --output-on-failure` in the admitted non-root
ext4 environment. The runner observes exact metadata/bytes, competing processes,
pre-publication substitutions and actual stopped-child termination. Run the existing
CONFIG-STORE and RECOVERY-STORE/QUEUE/APPLY/STORED-APPLY families for storage
regressions. See the [handoff](../../spec/delivery/profile-owner-handoff.md). No
installed controller or default policy is enabled by this component checkpoint.

The [recovery-draft package](../../spec/delivery/packages/w-10-recovery-draft.md)
adds EditorDraft::recovery_snapshot, inspect_recovery and restore_recovery. Admit
editor.recovery only from trusted native context, with large commands and current
history/sensitive disclosure. Supply a separately verified RecoveryIdentity; never
trust the identity in the record. LinuxGenerationStore::generation_token identifies
its loaded verified selection and refuses empty, damaged or indeterminate stores.
Restore creates one ordinary undo step. Apply uses the existing transaction owner.

After normal preflight/configure/build, run `ctest --preset <profile> -R
'^editor[.]RECOVERY-' --output-on-failure`. The declared non-root ext4 laboratory
also runs `ctest --preset linux-x64-gcc13 -R '^native[.]RECOVERY-APPLY$'
--output-on-failure`. The native runner owns private stores and cuts its own commit
process after durability; it checks exact bytes and stale-record refusal. This
experiment does not implement product recovery-file retention or native offers.
See the [shared handoff](../../spec/delivery/recovery-draft-handoff.md) for that scope.

The [native storage package](../../spec/delivery/packages/w-10-recovery-store.md)
adds LinuxRecoveryStore for one existing caller-selected private directory. Construct,
use and destroy it on its serialized worker thread. Supply a current guard for every
snapshot, replacement and retirement. Pass the exact returned RecoveryVersion when
mutating; obtain a fresh version after an admitted attempt. An unknown outcome poisons
the owner and requires verified reopen. The store accepts opaque bounded bytes; use
EditorDraft inspection with separately verified identity before offering restoration.
Keep file I/O off the GTK thread and keep development fault hooks out of product flows.

After the same preflight/configure/build, the admitted non-root ext4 environment runs
`ctest --preset linux-x64-gcc13 -R '^native[.]RECOVERY-(STORE|STORED-APPLY)$'
--output-on-failure`. The storage oracle kills only its held child, observes exact
reopen state and checks unsafe files. The composed Apply oracle persists and reopens
real editor records through separate native owners while retaining the fixed Apply
outcomes. Run the ten shared recovery cases above and `ctest --preset <profile> -R
'^composition[.]' --output-on-failure` on all three development profiles. See the
[storage handoff](../../spec/delivery/recovery-store-handoff.md).

The [queue package](../../spec/delivery/packages/w-10-recovery-queue.md) adds
LinuxRecoveryQueue and SysPane.RecoveryWorker. Supply an explicitly authorized
RecoveryContext with separately verified session/profile/generation, policy revision
and read/retain/erase grants. Poll and consume the initial load before enqueueing a
capture or retirement. Captures coalesce; retirement permanently seals that owner.
Every successful completion requires matching bytes/context and verified helper exit.
Close on any relevant authority or lifetime change, continue polling until reaped,
then destroy the owner. Regrant does not resume it. The helper performs recovery
filesystem operations; never move those calls into GTK callbacks.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]RECOVERY-(QUEUE|STORE|APPLY|STORED-APPLY)$' --output-on-failure` in the
admitted non-root ext4 environment. Queue tests include a separate development fault
worker, real held-child stop/exit, forged protocol replies and exact final files.
Run the component graph checks above on all three profiles. See the
[queue handoff](../../spec/delivery/recovery-queue-handoff.md).

The [recovery controls package](../../spec/delivery/packages/w-10-recovery-controls.md)
connects the queue to EditorForm under explicit trusted admission. After constructing
the form, call recovery with the immutable worker/private directory and a separate
EditorRecoveryBinding: session, profile, verified generation, current policy revision
and explicit erase authority. Bind only outside private modal/property input. Policy,
disconnect and reload invalidate the old owner. After accepted Apply/reconciliation,
supply the newly verified generation; never use the record's own identity. Changing
session/profile clears earlier cleanup intent. Regrant alone does not restart capture.

Call close without waiting; continue the serialized host loop and poll stopped until
true before destroying the form or quitting GTK. A failed capture leaves Apply usable
and the retained file potentially present. Keep prevents later captures for that
binding. Restore uses the existing draft/undo path, and Apply uses its existing owner.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'^native[.]EDITOR-RECOVERY$' --output-on-failure`. The native runner uses private
non-root ext4 directories, real GTK input, an independent observer and held fault
workers. Run the existing native editor/clipboard and recovery layers plus shared
recovery and component checks on their declared profiles. The
[handoff](../../spec/delivery/recovery-controls-handoff.md) describes failures and
scope. Installed profile-directory and mandatory-policy ownership remain pending.

The [typography package](../../spec/delivery/packages/w-09-typography.md) introduces
theme 0.2 and `configuration::theme_font(theme, role)`. It returns an owned family,
DIP size, weight and style; `TextRequest.role` defaults to body. ContentCatalog adds
the required `theme.typography` capability for a selected version 0.2 theme even
when its manifest omitted it. Existing theme 0.1 output remains equivalent.

After ordinary preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]TYPOGRAPHY-' --output-on-failure`. The owned Linux laboratory runs
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-TYPOGRAPHY|TEXT-RASTER|SCENE-SURFACE)$'
--output-on-failure`. The new native oracle preserves pixels and positive ignored-role
and ignored-weight fault witnesses. The [role-composition experiment](../../spec/delivery/role-composition-handoff.md)
now connects those roles to semantic scene blocks. Set SurfaceConfig.experimental_typography
only in a trusted development owner, alongside theme.typography capability/current policy.
It defaults false; native authoring and trusted editor integration remain pending.
Run `ctest --preset linux-x64-gcc13 -R '^native[.]ROLE-COMPOSITION$' --output-on-failure`
after ordinary workspace preflight/configure/build. The oracle uses literal base fonts
and independent raw-pixel composition, with exact table rectangles and diagnostic checks.

The [native visibility controls](../../spec/delivery/packages/w-10-visibility-controls.md)
add the shared `VisibilityInput` parser and lazy GTK `EditorVisibilityForm`. Set routes
through `SetWidgetVisibility`; nested binding input changes only the private buffer.
Trusted EditorForm explicitly enables conditional rendering after large-command and
scene/configuration capability admission. Direct SceneSurface defaults false.
Installed host entry has a separate ownership and qualification gate.

Run the ordinary preflight/configure/build commands, then `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])' --output-on-failure`.
The owned non-root Linux laboratory also runs `ctest --preset linux-x64-gcc13
-R '^native[.]EDITOR-VISIBILITY$' --output-on-failure`. Its sixteen cases exercise
real controls, exact scenes, held gestures, hidden pixels/names, nested erasure and
save/reopen/reconciliation, with deliberate wrong-rule/frozen/retained-input controls.
Frozen inputs are tests/editor/visibility-controls-cases.json. The
[handoff](../../spec/delivery/visibility-controls-handoff.md) distinguishes component
restart from a separate-process interruption and records the remaining release gates.

The [native visibility experiment](../../spec/delivery/packages/w-09-native-visibility.md)
adds `SurfaceConfig.experimental_visibility`, default false. Trusted EditorForm now
sets it after the admission above; resource declarations alone cannot enable it.
Installed entry paths retain their separate integration gate. SceneSurface owns
conditional frames, hidden payload erasure and bounded chart/image continuation.
Consume `SurfaceText.presented` and `diagnostic` through the registered native owner;
use `inspector_rows` to omit hidden rows and promote diagnostic descendants.

After ordinary preflight/configure/build, Linux runs `ctest --preset linux-x64-gcc13
-R '^native[.](SCENE-VISIBILITY|VISIBILITY-PIXELS)$' --output-on-failure` under the
existing non-root account. The first family covers all kinds, exact frozen examples,
groups, status, geometry, retained work and revocation. The second owns Xvfb/private
D-Bus, compares pixels and explicit AT-SPI names and detects inverted and retained
content controls. Losslessly compressed RGB observations retain raw and archive
hashes. Read the [handoff](../../spec/delivery/native-visibility-handoff.md) before
continuing installed ownership and complete-edition integration.

The [snapping package](../../spec/delivery/packages/w-10-snap.md) defines the
pure `snap(SnapInput)` projection in editor_snap.hpp. Provide validated captured
world geometry in 1/64-DIP units; consume deltas through existing typed draft edits.
Do not rebuild targets from live telemetry during a gesture. Native adapters own
temporary guides and must erase both accessible feedback and pixels on revocation.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. The declared non-root Linux laboratory additionally runs
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-SNAP|EDITOR-GROUP|EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen inputs are tests/editor/snap-cases.json. See the
[handoff](../../spec/delivery/snap-handoff.md) for executed evidence and limits.

The [grouping package](../../spec/delivery/packages/w-10-group.md) adds
GroupWidgets and UngroupWidget to EditorDraft::execute. Supply sibling IDs and
a fresh group ID/title. Group bounds cover every fixed variant; selection changes
atomically with the scene. Ungroup requires contained fixed variants and a fixed
container origin. Native hosts must check current resolved geometry and parent
eligibility before using these transformations as direct-edit operations.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. In the declared non-root Linux laboratory also run `ctest
--preset linux-x64-gcc13 -R '^native[.](EDITOR-GROUP|EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen scenes live in tests/editor/group-cases.json and
tests/editor/group-overlap-cases.json. See the [handoff](../../spec/delivery/group-handoff.md)
for executed evidence and remaining boundaries.

The [arrangement package](../../spec/delivery/packages/w-10-arrange.md) adds typed
AlignWidgets and DistributeWidgets through EditorDraft::execute. Provide stable IDs;
alignment needs two disjoint siblings and spacing needs three. Only fixed base
origins change. Ownership order breaks spacing ties; current policy and ordinary
atomic/history limits apply. Native hosts must check active resolved base geometry
and native metric expansion before offering a WYSIWYG arrange operation.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. In the declared non-root Linux workspace also run `ctest
--preset linux-x64-gcc13 -R '^native[.](EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen inputs are tests/editor/arrange-cases.json; native
reports preserve independently observed pixels and stored scenes, including fault
controls. See the [handoff](../../spec/delivery/arrange-handoff.md) for remaining gates.

The [complete-scene command package](../../spec/delivery/packages/w-08-large-commands.md)
adds command 0.5 and Linux generation manifest 0.3. Pass `large_commands=true` as the
last `SettingsDraft`, `EditorDraft` or `EditorForm` constructor argument only after
the host has negotiated the exact version, features and frame floor. Legacy default
behavior remains unchanged. Do not rewrite an unresolved request on reconnect.
ContentCatalog preview accepts the explicit `configuration.large-commands` capability.

After the ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(configuration[.]LARGE-|editor[.]|settings[.]|configuration[.]|protocol[.]|composition[.])'
--output-on-failure`. Linux additionally runs `ctest --preset linux-x64-gcc13 -R
'^native[.](LARGE-COMMANDS|CONFIG-STORE|COMMAND-IPC|CONTENT-COMMANDS|RESOURCE-GENERATIONS|SCENE-CONTENT|EDITOR-FORM|SETTINGS-FORM)$'
--output-on-failure` in the declared non-root campaign workspace. The new native
family uses private ext4, authenticated IPC and owned Xvfb/DBus. Its records bind
original request bytes, coherent documents, resource pins and actual process exit.

The [editor draft package](../../spec/delivery/packages/w-10-editor-draft.md) adds
`syspane_editor_draft` and `interfaces::EditorDraft`. Construct it on one serialized
owner with the same coherent Authored/Authority/Policy/epoch and optional immutable
SettingsResources context as settings. `execute(vector<SceneEdit>)` applies an atomic
local batch; `scene()` is a const borrow valid only until the next mutation/policy
call. Native preview caches need their own policy-owned erasure. This component
creates no native surface, filesystem path, clipboard owner or persistence worker.

Use stable IDs with `select`, typed property/content/theme/insert/remove/reparent/
duplicate/move/resize operations, `undo`, `redo` and `discard`. Reparent coordinates
stay parent-local; responsive layout variants need explicit layout edits. Call
`begin("commit", fresh_request_id)` for Apply and route its exact body through the
existing asynchronous command owner. Deliver results with `complete` or `reconciled`.
Disconnect/callback failure remains unresolved; never retry under a new identity.
Close erases local state and cannot reverse a submitted transaction.

History holds at most 64 entries and 8 MiB of canonical scene/selection JSON bytes.
Local scenes retain their 256 KiB contract. Legacy oversized commands reject
without discarding the draft; explicitly negotiated command 0.5 supports full scenes.
The initial native editing component is recorded in the native editor handoff. After normal workspace preflight/configure/build, run
`ctest --preset <profile> -R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.](POLICY-|DISCLOSURE-))' --output-on-failure`.
Linux also runs the existing `native.SETTINGS-FORM` regression for the shared owner.
The [handoff](../../spec/delivery/editor-draft-handoff.md) records exact evidence and
the native editor's remaining acceptance gates.

The [native settings package](../../spec/delivery/packages/w-11-native-settings.md)
adds shared `interfaces::SettingsDraft` and Linux `interfaces::SettingsForm`. Construct
the form on the GTK owner thread with a coherent Authored snapshot, authenticated
authority, current policy and producer epoch; embed `widget()` in the host's window.
The canonical registry generates defaults, constraints and presentation metadata.
The [coverage report](../../spec/experience/settings-native-coverage.json) separates
owned component checks from pending installed UI and CLI coverage.

Provide fresh request IDs and callbacks that enqueue submit/cancel/reload work and
return immediately. Do not reenter the form from a callback or perform filesystem
work on the UI thread. Pass later results to `complete(ticket, result)`; after a
restart, pass the independently scoped response to `reconciled(ticket, query_id,
current_epoch, response)`. Disconnect or callback failure leaves the original request
unresolved. The external command owner retains its ledger/reconciliation duties after
the form closes. Explicit Reload takes a fresh snapshot only after no request remains
unresolved. Current policy must grant operational inspector and accessibility disclosure.

For a resource-backed generation, prepare `SettingsResources` before entering the UI
owner: an immutable validated ContentCatalog from that generation, its exact selection
and the adapter capability set. Pass it after the optional Translator constructor
argument, and provide fresh context with explicit reloads. The
[resource settings package](../../spec/delivery/packages/w-11-settings-resources.md)
defines ownership. Settings-only edits emit command 0.3 with that exact selection,
including when the unchanged scene uses schema 0.3. Resource-free scene 0.2 keeps
command 0.2; bare scene 0.3 and dropping an already-required context are rejected.
Only the trusted host can replace catalog/selection via a fresh admitted snapshot.
Current-policy checks cover content.select and required resource capabilities.

Theme edits resolve from the admitted catalog, without filesystem access. Revert and
accepted results update document/resource snapshots together. Disclosure loss clears
all local references and needs a fresh complete reload after regrant. Installed
owner/transport routing and preset/import controls remain open. Use built-in default assigns an explicit
value; persistent-layer inheritance reset is separate pending work. Native selection
does not publish authored values to PRIMARY/CLIPBOARD; copy/cut/drag export awaits an
admitted clipboard owner. Full locale formatting and human accessibility review remain.

After ordinary preflight/configure/build, use `ctest --preset <profile> -R
'^(settings[.]|configuration[.]|composition[.]|protocol[.](POLICY-|DISCLOSURE-))'
--output-on-failure`. Linux adds `-R '^native[.]SETTINGS-FORM$'`. The latter creates
owned Xvfb/private-D-Bus windows, sends XTest keys, reads AT-SPI controls and independently
checks coherent ext4 generations. It preserves the 200 ms disclosure bound and requires
positive detection of retained-value, premature-saved and wrong-resource-selection
controls. Resource cases compare every manifest/asset byte and exact theme/selection
pin after save/reopen and restart, while the owner rejects import fallback. Check
the independent fixed resource fixture with `python tests/configuration/settings_content_fixture.py --check`.
These checks do
not qualify an installed settings application or a complete desktop edition.

The [scene inspector package](../../spec/delivery/packages/w-11-scene-inspector.md)
adds Linux `interfaces::SceneInspector`. Construct it on the GTK owner thread with
the same authority, immutable scene/resources, providers and trusted image worker
as SceneSurface, then embed `widget()` in an application-owned native window.
It uses the `inspector` telemetry/disclosure channel; accessibility, history and
resource permission checks still apply independently. Supply an inspector-bound
attachment and current qualified ticks. All public calls and GTK events share one
serialized loop; do not reenter the inspector during an operation.

Deliver telemetry and refresh normally. Close on host shutdown, then poll
`poll_image_jobs()` until actual worker termination before destroying the owner.
Policy and scene replacement clear native strings and require the existing fresh
attachment/full-state rules. Keys retain selected identities and native expansion;
Summary requests snapshot the selected row's last presented content. Native GTK
Shift-Left/Shift-Right collapses/expands; ordinary Left/Right changes columns.
The four `inspector.*` chrome translation IDs accept bounded plain UTF-8 labels.

After ordinary preflight/configure/build, run `ctest --preset linux-x64-gcc13 -R
'native[.]SCENE-INSPECTOR' --output-on-failure`. The model checks exact data/channel
semantics and bounds. The independent runner uses an owned Xvfb/private D-Bus,
native XTest keys and AT-SPI cell reads, including held references after revoke.
Its deliberate retained-content and wrong-selection controls must both be detected.
This is an embeddable component; installed settings/editor routing and representative
human accessibility review remain required.

The [scene images package](../../spec/delivery/packages/w-09-scene-images.md) connects
the worker to SceneSurface. Pass its canonical executable as the constructor's
optional worker argument from trusted application setup. Authored content cannot choose
an executable. With an admitted resource closure and current desktop/accessibility
policy, image widgets now render asynchronously. Repaint while pending; use
`poll_image_jobs()` during native ticks and after `close()` until it returns true
before destroying the owner. Pending work preserves chart history. Resource, scene
and policy replacement cancel old jobs and clear decoded caches.

Linux adds `native.SCENE-IMAGE` and `native.IMAGE-ERASURE`; the latter observes actual
owned X11 pixels and AT-SPI names with intentional erasure faults. Check the independent
geometry with `python tests/scene/image_surface_oracle.py --check`. The shared
`configuration.DIGEST-CONTENT` case checks the separate 16 MiB asset-hashing ceiling;
the ordinary document digest remains limited to 1 MiB. Native content-command tests
include large-asset persistence and recovery after the import is removed.

The [image pipeline package](../../spec/delivery/packages/w-09-image-pipeline.md)
adds shared premultiplied bilinear fit/orientation and the Linux
`SysPane.ImageWorker` / `rendering::ImageJob` boundary. The worker accepts PNG,
JPEG and the declared static SVG profile from bounded bytes. Its installed codec,
loader, relevant header and kernel identities are in `source/build/image-runtime.json`.
Linux requires Landlock ABI >= 3, seccomp and the pinned runtime; startup fails
when containment cannot be installed. No privileged installation is involved.

Supply ImageJob an admitted canonical worker ELF, declared media type and immutable
encoded bytes. Poll without waiting; cancellation suppresses take immediately but
the owner must retain the job until actual stop is observed. The worker receives
no image path or base URI. The job binds the original input SHA256, limits IPC
and accepts output only after successful exit and reaping. This low-level API
does not grant disclosure permission. SceneSurface supplies the scene/policy owner
described above; direct ImageJob callers must supply their own admitted owner.

After ordinary workspace preflight/configure/build, run
`ctest --preset <profile> -R '^scene[.]IMAGE-' --output-on-failure` on each toolchain.
Linux adds `-R '^native[.]IMAGE-(DECODE|JOB)$'`. The fixed portable oracle is checked
with `python tests/scene/image_fit_oracle.py --check`. Native tests use owned public
fixtures, verify actual worker pixels and rejection, and inspect OS limits and
termination; they do not test an installed desktop image widget.

The [native chart package](../../spec/delivery/packages/w-09-native-chart.md)
connects scene 0.3 charts to the Linux SceneSurface. Grant operational disclosure
on `history` as well as desktop/accessibility. `receive` takes an optional map of
current ticks for other providers; supply the complete context relevant to any
affected selector. Its mandatory receiving-provider tick takes precedence. Samples
are captured before receive returns, not merely when painting. Unrelated producers
do not clear a direct chart; incomplete relevant selector context clears history
and reports Waiting. Policy changes require fresh attachment/full state.

`scene::plot_chart` uses exact finite-number ratios and a bounded union of integer
line coverage; no uint64-to-double conversion or sample downsampling occurs. Axis,
window, clipping, gap and capacity facts are visible. Accessible content includes
every retained point and its original generation. Initial graph size is 320 by
120 DIP plus readable text; normal scene overflow and budget rules apply. Full
native accessibility navigation and installed producer/editor integration remain.

After workspace preflight/configure/build, run `ctest --preset <profile> -R
'^scene[.]PLOT-' --output-on-failure`. The fixed numeric cases can be independently
verified with `python tests/scene/chart_plot_oracle.py --check`. Linux adds
`native.SCENE-CHART` component families and `native.CHART-ERASURE` external pixels
and AT-SPI names. The latter uses the same owned Xvfb/private D-Bus runner and
deliberate erasure faults as the existing scalar/table/content experiments. Preserve
their original checks with `-R '^native[.](SCENE-ERASURE|TABLE-ERASURE|CONTENT-ERASURE|CHART-ERASURE)$'`.

The [chart history package](../../spec/delivery/packages/w-09-chart-history.md)
adds `scene::ChartHistory` to the existing portable scene component. Construct
one per unchanged chart binding, using validated window_ms/max_points. Feed each
admitted singleton BindingFrame and its qualified measurement clock before a later
publication replaces it; also observe at presentation/expiry. The synchronous
ChartView contains exact numeric points, continuity flags, window horizon and
capacity truncation. Null/failure/retained states create gaps; selection changes
erase, and chronology conflicts latch until clear. No raster or axis conversion
occurs in this component.

After ordinary preflight/configure/build, run `ctest --preset <profile> -R
'^scene[.]CHART-' --output-on-failure` for eleven families, including actual wire
admission and three samples delivered before painting. Regression selection is
`'^(scene[.]|composition[.]|legacy[.]|native[.]SCENE-(SURFACE|TABLE)$)'` on each
development profile. These are affected-component checks, not a full release suite.
The native chart owner now authorizes history-channel retention and clears on
policy/resource/binding/lifetime changes. The shared class itself grants no authority.

The [scene-content package](../../spec/delivery/packages/w-09-scene-content.md)
adds scene 0.3 and resource-bound command 0.4. Use `upgrade_scene_content` explicitly;
it returns a validated copy and refuses to guess legacy image/chart parameters.
Enable `scene.content` in the resource provider's capabilities and negotiate
`configuration.scene-content` alongside configuration.content/transactions and
command 0.4/result 0.1. ContentCatalog resolves every image reference within the
selected verified closure; no renderer reads an import directory by path.

After ordinary preflight/configure/build, `ctest --preset <profile> -R
configuration.SCENE-CONTENT --output-on-failure` runs six shared families. Linux
also runs `native.SCENE-CONTENT` (owned ext4 crash/recovery) and
`native.CONTENT-ERASURE` (owned Xvfb pixels and AT-SPI names with fault controls).
The former deliberately uses opaque media bytes and does not qualify a decoder.
The renderer consumes text bodies, column labels and scene 0.3 chart/image content.
Legacy charts/images without explicit content, or images without a trusted worker,
select the explicit unsupported whole-scene alternative.

The [table package](../../spec/delivery/packages/w-09-table-surface.md) extends
SceneSurface with table widgets. Supply ordered collection selectors that differ
only in field; the renderer joins cells by scoped identity and exposes typed rows
and relative cell pixel rectangles inside the same synchronous frame borrow.
`native.SCENE-TABLE` checks component semantics; `native.TABLE-ERASURE` checks an
owned two-column/two-row GTK window with independent grid pixels and AT-SPI names.
Use the existing Linux preflight/configure/build commands, then `ctest --preset
linux-x64-gcc13 -R '^native[.](SCENE-(SURFACE|ERASURE|TABLE)|TABLE-ERASURE)$'
--output-on-failure`. Every native mode keeps the 200 ms observation bound and
private Xvfb/D-Bus ownership. Tables are not yet an installed desktop feature.

The [scalar surface package](../../spec/delivery/packages/w-09-scene-surface.md)
adds Linux `SceneSurface`, owning immutable authored/resources input, its complete
fixed provider catalog and private DataViews. Supply a native clear callback that
removes copied accessibility text and requests blank painting. Deliver all events
on one serialized loop; all painting uses current qualified producer ticks and a
synchronous borrowed frame. No model/frame pointer may escape. Regrant requires
fresh attach/full state. Native clear failure closes permanently and requires host
teardown/recovery before any new activation.

After standard preflight/configure/build, run `ctest --preset linux-x64-gcc13
-R '^native[.]SCENE-(SURFACE|ERASURE)$' --output-on-failure`. The component test uses
actual wire admission. The independent native oracle opens only its owned Xvfb and
private D-Bus session, compares root pixels with fixed expected text, and reads
actual GTK names through AT-SPI. Intentional pixel/name retention controls must be
rejected. Synthetic captures are under `native-evidence/surface-*`; the temporary
X authorization file must never be copied into committed evidence. Installed
AT-SPI/ATK/observer identities are checked against `source/build/surface-runtime.json`.
This experiment does not install a renderer or qualify behind-icons placement.

The [native text package](../../spec/delivery/packages/w-09-native-text.md) adds
`syspane_native_text` and finite `SysPane.TextProbe` on the Linux development profile.
`rendering::render_text` accepts plain text, an immutable validated theme, language,
wrap width in 1/64 DIP, scale and contrast. It returns readable native metrics and
owned premultiplied RGBA8 pixels. This prerequisite accepts public/authored or
synthetic text; live DataView values require a separately admitted erasure owner.
It performs no scene activation or display access.

After normal workspace preflight/configure/build, run `ctest --preset
linux-x64-gcc13 -R '^native[.]TEXT-RASTER$' --output-on-failure` with the existing
Linux build-root environment. The independent Python oracle inspects raw pixels
and rejects malformed/bounded input. Reports and synthetic rasters are written
under `native-evidence/text-*`. Configure and native tests verify installed text
libraries, fonts and font configuration against `source/build/text-runtime.json`.
Dependency changes require an explicit identity revision; no package installation
is performed. The probe accepts one bounded JSON input on stdin and one owned raw
output path; its `text_hex` input is malformed-UTF-8 laboratory instrumentation.


The [authored binding package](../../spec/delivery/packages/w-09-bindings.md) adds
`scene::project_binding` to `syspane_scene`. Supply a complete trusted catalog of
scoped DataViews, supported types/fields/TTLs, explicit pin mappings and qualified
measurement ticks. The callback must consume results synchronously without
retaining payload or reentering a view. No implicit routing, acquisition, mapping
or unit conversion occurs. Inspect resolution and row status separately.

After workspace preflight/configure/build, run `ctest --preset <profile>
-R "^scene[.]BIND-" --output-on-failure` for the seventeen binding families.
The Linux development profile explicitly records the externally updated GLib
2.80.0-6ubuntu3.9 and glibc 2.39-0ubuntu8.9 environment; historical evidence retains
its original dependency identity.

The [scene layout package](../../spec/delivery/packages/w-09-layout.md) adds
`syspane_scene` and `syspane_scene_tests` on all three development profiles. Call
`scene::resolve(scene, topology, metrics)` with immutable authored data, explicit
display identities/role candidates/fallback and native readable minimum/preferred
sizes for every leaf. Typed geometry uses 1/64 DIP; returned `pixels` use device
pixels. Inspect plan state and diagnostics before using geometry. An alternative
plan requires an exposed fallback presentation and proves no visible activation.

After normal workspace preflight/configure/build, run `ctest --preset <profile>
-R '^scene[.]' --output-on-failure`. The 31 fixed JSON cases in `tests/scene/cases/`
contain independently specified exact rectangles. Additional limits and exhaustive
exclusion checks run in the same executable. This engine performs no font, hardware
or file I/O; native metric production and rendering are separate integration work.

The [native content package](../../spec/delivery/packages/w-08-native-content.md)
adds `make_resource_provider(store, capabilities, imports)` to the shared transaction
component. The store must outlive the provider, invoked on its serialized worker.
An exact current selection resolves solely from retained original packages; every
other selection uses the configured loader once. There is no cross-catalog merge
or fallback. Current policy and the commit permit still govern publication.

The Linux finite command fixture accepts `content <catalog-root-or-dash>` before
its existing direct or supervisor arguments. For example, use `SysPane.CommandProbe
content <private-root> supervisor <private-runtime> <store> normal <client-pid>
allow`. The root has a private `catalog.json` following content-catalog 0.1 and
explicit named package child directories. `-` permits retained-only editing.
Imports load on the transaction worker, never at startup or in the IPC loop.
The supervisor forwards this configuration to each owned replacement child.
The laboratory's explicit policy and scene.selector capability confer no installed
authority. Existing framing, child argument limits and 5000 ms deadline remain.

After the usual workspace preflight/configure/build, run `ctest --preset <profile>
-R '^configuration[.]RESOURCE-RETAINED$' --output-on-failure`. Linux also runs
`ctest --preset linux-x64-gcc13 -R '^native[.]CONTENT-COMMANDS$' --output-on-failure`.
Reports use `native-evidence/content-commands-*`. This independent client validates
wire results, held process exit, original-epoch reconciliation and exact persisted
resource bytes. The resource-write hang is an owned test phase, not product behavior.

The [resource generation package](../../spec/delivery/packages/w-08-resource-generations.md)
adds command 0.3 with an explicit content selection. A typed `ResourceProvider`
returns an immutable `ResourceSet` from the existing `ContentCatalog`; the common
coordinator verifies its selection, candidate theme, capability availability and
current policy. AsyncCommands advertises `configuration.content` only with this
provider. Ordinary command 0.2 ownership remains available for resource-free stores.

After workspace preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]RESOURCE-' --output-on-failure`. Linux also runs `ctest --preset
linux-x64-gcc13 -R '^native[.]RESOURCE-GENERATIONS$' --output-on-failure`. Native
reports use `native-evidence/resources-*`. The independent oracle covers exact
stored bytes, interrupted writes, missing import sources and complete-previous
fallback without repairing corrupt generations.

The existing finite ConfigProbe accepts `<store> content-commit <command-json>
<fault-or-dash> <package-dir>...`. It uses laboratory console authority, policy 7
and the scene.selector capability, and loads package directories only when actual
preparation is required. Replayed committed requests therefore need no import path.
`read` additionally reports recovered selection/theme/package pins for resource-bearing
generations. Native installed endpoint/policy ownership, media decoding and visible
activation are separate gates; do not infer them from a durable response.

The [content resolution package](../../spec/delivery/packages/w-08-content-resolution.md)
adds `ContentCatalog` to the authored configuration component. Supply exact package
and document pins, an immutable baseline, authenticated role, current policy and
trusted available capabilities. `preview` returns the command, candidate, original
package bytes, theme, provenance and missing optional capabilities. It performs no
publication or activation. Runtime schema validation reuses the compiled closure.

After normal workspace preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]CONTENT-' --output-on-failure`. Linux also runs `ctest --preset
linux-x64-gcc13 -R '^native[.]CONTENT-READER$' --output-on-failure` with the existing
native-cache environment. The oracle creates private package directories and checks
hashes and complete output independently. Reports use `native-evidence/content-*`.

The finite `SysPane.ContentProbe <preview|snapshot|denied> <package-dir>...` accepts
one JSON line with `settings`, `scene`, `package` pin and `preset` pin on stdin.
It uses explicit laboratory console authority, policy generation 7 and the
`scene.selector` capability. Snapshot mode emits `{"ready":true}` after reading,
before consuming stdin; tests change the files then prove copied bytes survive.
Denied mode blocks settings previews. These controls do not supply installed policy
or an import UI. The current generation store cannot publish external resource
closures in the original 0.2 path. The subsequent 0.3 resource path above binds
selection explicitly; changing only a preview's intent is insufficient.

The [transaction supervision checkpoint](../../spec/delivery/transaction-supervision-handoff.md)
adds `TransactionWatch` in the common recovery component and an opt-in controller
HealthLink profile. A started/armed handshake precedes worker dispatch; finished
follows native join. The independent 5000 ms operation deadline cannot be renewed
by health traffic. Whole-process termination isolates an uncooperative transaction.

After workspace preflight/configure/build, run the recovery and health families
with `ctest --preset <profile> -R '^(recovery[.]TRANSACTION-|health[.]HEALTH-TRANSACTION)'
--output-on-failure`. Linux additionally runs `ctest --preset linux-x64-gcc13 -R
'^native[.]TRANSACTION-SUPERVISION$' --output-on-failure`. This experiment launches
`SysPane.CommandProbe supervisor <private-runtime-root> <owned-store>
<normal|prepare|durable|repeat> <client-parent-pid> <allow|deny>`. The scenario and
policy flags are finite laboratory controls. The supervisor creates fresh private
endpoint directories for each child, uses the existing native Child owner, and
retains one restart budget across replacements. Its parent pipe accepts `stop`.

The independent client observes worker tasks and process exit through pidfds, then
reconnects to the reported fresh epoch. It checks exact stored documents and receipt
results without automatic command replay. Runtime reports are under
`native-evidence/supervision-*`. Installed endpoint discovery, policy distribution,
installation identity, assets and native UI activation remain separate gates.

The [reconciliation checkpoint](../../spec/delivery/reconciliation-handoff.md) adds
`result.reconcile` / `result.reconciled`, negotiated with reconciliation-request and
reconciliation-result 0.1 plus command-result 0.1. `consume_reconciliation` checks
the complete connection/current epoch/query/original epoch/request tuple. Read-only
lookup uses the owner-loop receipt snapshot; only the worker refreshes it, and
`finish(..., true)` publishes it after actual join. It performs no store I/O,
mutation admission or resource preparation on the connection loop.

After normal preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]RECON-' --output-on-failure`. On Linux, also run
`ctest --preset linux-x64-gcc13 -R '^native[.]RECONCILIATION$' --output-on-failure`
with the existing native-cache environment. The independent client kills only its
exact owned stopped probe, restarts with a distinct epoch, validates reply schemas
and hashes stored files before/after lookup. Six cases cover durable/before-publish
crashes, policy revocation, fallback, identity retention and responsive live-worker
lookup. Reports are under `native-evidence/reconciliation-*`. The probe accepts
optional epoch and allow/deny laboratory-policy arguments; these are test controls,
not an installed policy source. Full activation and installed ownership remain open.

The [command session checkpoint](../../spec/delivery/command-sessions-handoff.md)
adds `syspane_async_commands` and seven portable command families on all three
development profiles. The optional `configuration.transactions` feature uses existing
command/result versions and requires an 8192-byte frame floor. Construct Sessions
with its command owner; call its admission/delivery methods only on the serialized
session loop. Dispatch `take()` tickets to one native worker, call `run()` there,
join that worker, then call `finish(..., true)` on the owner loop. Keep the store and
owner alive until actual stop. Do not substitute a cancellation callback for a join.

After ordinary preflight and configure/build, run `ctest --preset <profile> -R
'^(configuration[.]|native[.]COMMAND-IPC$)' --output-on-failure`. Linux's
`SysPane.CommandProbe` uses the same private ext4 and native peer-authentication
adapters. Its independent Python socket client verifies responsive control traffic,
preparation/permit cancellation, policy revocation and same-epoch lost-response
retrieval, then checks stored documents. Parent-pipe controls and bounded worker
gates are test instrumentation. Reports remain under `native-evidence/commands-*`.
This finite composition does not install a controller or qualify arbitrary resource
preparers, a hard worker deadline or activation. Original-epoch lookup is covered
by the subsequent reconciliation checkpoint above.

The latest [authored transaction checkpoint](../../spec/delivery/authored-transactions-handoff.md)
adds `syspane_authored` on all three development profiles and the Linux-only
`syspane_generation_store` / `SysPane.ConfigProbe`. After ordinary workspace
preflight and configure/build, run `ctest --preset <profile> -R
'^(configuration[.]|native[.]CONFIG-STORE$)' --output-on-failure`. Linux requires
the existing native cache build root, unprivileged runner, ext4, `findmnt` and the
recorded Python JSON Schema validator. The native test creates private synthetic
stores, observes stopped child processes, kills only those held children and records
recovery. It preserves all case directories under the build's `native-evidence/`.

The compiled validator embeds canonical settings/scene/layout/binding/command
schemas; runtime validation does not fetch schemas. Transactions require a resource
preparer and current-policy callback. The probe uses typed laboratory policy and
its synthetic built-in theme only. Publication and reconciliation return result
0.1 documents, with pending activation and no visibility claim. IPC compositions
without an asynchronous command owner remain preview-only. Do not point the probes
at installed user configuration.
The native store retains at most 32 generation attempts and does not prune them;
capacity or corruption requires an explicit maintenance/repair boundary still to
be implemented. Current/previous selectors, not directory timestamps, own recovery.

The latest [session demand checkpoint](../../spec/delivery/session-demand-handoff.md)
passes full suites of 130 Linux, 119 Windows and 108 historical-toolset entries.
`syspane_demand_sessions` privately owns Sessions and DemandOwner. The controller
supplies an immutable bounded request when opening a native-authenticated connection;
only an admitted subscription creates acquisition demand. Existing wire documents
do not accept arbitrary field/entity selections. Native loops remain responsible
for authentication, serialized calls, worker ownership and exact stop proof.

After the ordinary workspace preflight and configure/build, run the five portable
families with `ctest --preset <profile> -R '^demand-session[.]' --output-on-failure`.
They cover admission, heartbeat/expiry, resubscription/callback identity, policy and
clock faults. The Linux collector consumes the same adapter; its existing native
collector, demand and continuity oracles pass unchanged. Historical host execution
and a 15-executable PE/import/input audit do not establish guest OS compatibility.

The [Linux demand executor checkpoint](../../spec/delivery/demand-executor-handoff.md)
adds `native.NATIVE-DEMAND-EXECUTOR` with five cases. Run it using
`ctest --preset linux-x64-gcc13 -R '^native[.]NATIVE-DEMAND-EXECUTOR$' --output-on-failure`
with the ordinary Linux build-root environment. It observes actual native threads,
watched sockets and original measurements, including IPC policy revocation during
an outstanding acquisition. The Linux full run passed 124 of 125 entries; the new
family passes after correcting only its observer, against the same binary. The
failed attempt remains recorded. Windows's 11 demand/component checks also pass.
No installed policy, general multi-client selection or other-platform executor is
qualified. Probe stdout can contain operational counters; publish only the generated
public outcome report, keeping any `.private.json` failure capture in owned output.

The [supervised network publication checkpoint](../../spec/delivery/network-publication-handoff.md)
passes 96 Windows, 101 Linux and 88 historical-toolset host checks. All profiles run
three `network.PUBLICATION-*` families; Linux adds `native.NATIVE-COLLECTOR` with
eight real collection/lifecycle cases. Both recorders accept `--network-publication`,
which includes preceding regression scopes. The native collector target exists only
on Linux; typed development policy does not qualify installed policy or product
service wiring. Twelve historical executables receive the PE/import audit.

The earlier [network reconciliation checkpoint](../../spec/delivery/network-reconciliation-handoff.md)
passes 93 Windows, 97 Linux and 85 historical-toolset host checks. Four
`network.RECONCILE-*` families run on all profiles. Linux adds
`network.NETWORK-WATCH-DECODE` and a fifth native network case which independently
observes subscription registration before two real acquisitions. Both recorders now
accept `--network-reconciliation` with their existing arguments; it includes all
preceding regression scopes. Actual native topology faults, Windows notification
coverage and supervised publication remain separate gates. Historical native
readers remain disabled; eleven executables receive the PE/import audit.

The earlier [native network acquisition checkpoint](../../spec/delivery/network-acquisition-handoff.md)
passes 89 Windows, 92 Linux and 81 historical-toolset host checks. Modern profiles
add `native.NATIVE-NETWORK` (four fixed cases); Linux adds two `network.NETWORK-*`
native-layout decoder cases. Use `record_protocol.py --network` with the ordinary
profile/build/output arguments for the full modern suite. The historical recorder
continues to use `--measured-time`; native network targets are absent there.
`SysPane.NetworkProbe read` outputs operational native keys/counters for explicit
local tests. CTest records only comparison outcomes/counts; do not publish raw
probe stdout. Notification-backed identity and supervised publication are pending.

The preceding [measured telemetry checkpoint](../../spec/delivery/measured-time-handoff.md)
passes 88 Windows, 89 Linux and 81 historical-toolset host checks. Five
`measured.MEASURED-*` families run on each profile; `native.NATIVE-MEASURED` exercises
fresh, delayed and future synthetic measurements on modern Windows/Linux. Both
recorders accept `--measured-time` with their existing profile/build/smoke/output
arguments. The native probe explicitly negotiates 0.2; original inventory cases
continue to use 0.1. Real collectors, suspend and namespace migration are unqualified.

The preceding [native clock checkpoint](../../spec/delivery/measurement-clock-handoff.md)
passes 82 Windows, 83 Linux and 76 historical-toolset host checks. Modern suites
add `native.NATIVE-CLOCK`: two separate-process causal-bracket/peer-exit cases.
Record complete modern suites using `record_protocol.py --measurement-clock` with
the existing profile/build/output arguments; historical recording still uses
`record_legacy_build.py --subscriptions`. The Windows lock now also verifies the
installed `libmincore.a` archive. These checks enable no measured telemetry or
suspend/namespace-mismatch qualification.

The preceding [subscription checkpoint](../../spec/delivery/subscriptions-handoff.md)
passes 81 Windows, 82 Linux and 76 historical-toolset host checks. Three
`subscription.SUB-*` families run everywhere; `native.NATIVE-SUB` executes five
separate-process synthetic inventory scenarios on modern Windows/Linux. Record
complete suites using `--subscriptions`. Product demand, real collectors and
measured-field freshness remain unqualified.

Before a build, test or package launch, run the Windows coordinator
`python source/build/check_workspace_budget.py --action build` (select `test` or
`package` as appropriate); require exit zero. Run it afterward with `--action inspect`.
The combined checkout/native-Linux allocation is 5 GiB with growth reservations;
this is a preflight check, not an OS quota. The original 1 GiB overrun is preserved
in the subscription checkpoint. Do not remove or overwrite another task's files to gain space.

The earlier [complete-state import checkpoint](../../spec/delivery/state-import-handoff.md)
passes 77 Windows, 78 Linux and 73 historical-toolset host CTest entries. Run the six
import families with `ctest --preset windows-x64-gcc15 -R "^import\." --output-on-failure`;
Linux uses the ordinary wrapper. Both recorders accept `--state-import`, which also
requires the preceding telemetry/data-view and applicable native regression cases.
The receive boundary is in-process; native subscription/demand and producer-clock
mapping remain pending.

The earlier [telemetry document checkpoint](../../spec/delivery/telemetry-wire-handoff.md)
passes 71 Windows, 72 Linux and 67 historical-toolset host CTest entries. Run the
six codec families with `ctest --preset windows-x64-gcc15 -R "^telemetry\."
--output-on-failure` (one command); Linux uses the ordinary wrapper. Record the full
suite using `--telemetry`. The decoder does not enable native subscriptions.

The earlier [data-view checkpoint](../../spec/delivery/data-view-handoff.md) passes
65 Windows, 66 Linux and 61 historical-toolset host CTest entries. Six `data.VIEW-*`
cases exercise the typed model/lease/policy owner. Run them with
`ctest --preset windows-x64-gcc15 -R "^data\." --output-on-failure`; Linux uses the
ordinary wrapper. Record complete suites with the recorder's `--data-view` option.
Native subscriptions, real collectors and renderer integration remain pending.
Earlier counts below describe their named historical checkpoints.

The modern diagnostic's native source/destination fields and
`--preserve <absolute-source> <absolute-destination>` request an explicit private
opaque copy. Mandatory policy must be available and permit
`diagnostic.preserve_configuration`; CLI acknowledgement requires public/export,
and path controls require operational inspector/accessibility permission. No local
switch installs or overrides policy. An unavailable policy disables these controls.
The source is never parsed or activated. Existing destination/`.partial` names are
conflicts, failed partials are retained, and the acknowledgement always reports
`durable:false`. See the [contract](../../spec/delivery/packages/w-25-preservation.md)
for limits and exit codes. This is not a configuration restore or support export.

Run `ctest --preset windows-x64-gcc15 -R 'PRESERVE' --output-on-failure` for the
portable policy predicate and native file/UI family. Linux's ordinary `test` action
runs the same cases. Native UI tests use typed policy fixtures in a separate test
executable; they programmatically activate the same Win32/GTK controls without
changing machine policy. Linux uses an owned authenticated Xvfb server. Preserve
failures and unexecuted privilege/filesystem cases. Record a complete final run with
`source/build/record_protocol.py --preservation --profile <profile> --build-dir
<build> --output <record>`. Historical recording accepts `--preservation` for the
portable predicate only; its file/UI adapters stay disabled.

The repository builds the C++17 model, portable protocol/configuration libraries
and a deterministic development smoke program. A usable desktop application
remains pending. Use the pinned tools in
[the development profiles](../../source/build/targets/README.md). From the repository
root on Windows:

```powershell
cmake --preset windows-x64-gcc15
cmake --build --preset windows-x64-gcc15
ctest --preset windows-x64-gcc15 --output-on-failure
out/build/windows-x64-gcc15/SysPane.ModelSmoke.exe
```

The Linux preset uses an unprivileged account and a native cache directory for
build products. The same source checkout and expectations are used. From the
repository root in the admitted Ubuntu environment, `sh source/build/run_foundation.sh`
runs the documented configure/build/test/package commands. Set
`SYSPANE_LINUX_BUILD_ROOT` to the admitted owned campaign directory first;
the wrapper refuses an unset value. Individual `configure`, `build`, `test` and
`package` arguments are available. The wrapper does not install dependencies or
require root.

Create a local Windows smoke archive and check relocation with:

```powershell
python source/build/package_smoke.py --profile windows-x64-gcc15 --build-dir out/build/windows-x64-gcc15
```

The W-24 checkpoint ran 37 CTest entries: the original 18 model/smoke/component checks,
17 portable protocol/policy checks and two native IPC families. Run portable cases with
`ctest --preset windows-x64-gcc15 -R '^protocol\.' --output-on-failure`.
The original W-01 results remain historical; W-24 case/artifact records are
`out/evidence/w-24-native-<profile>.json`. The two native families contain
15 concrete Windows cases and 16 Linux cases, with raw process transcripts. Run
them alone with `ctest --preset windows-x64-gcc15 -R '^native\.' --output-on-failure`.
`SysPane.IpcProbe` is a finite development probe; it is not the SysPane product.
Native tests take about 30 seconds because they execute real five-second deadlines.
They open only private local endpoints, check unelevated execution, and use synthetic
commands. Cross-user/Windows cross-logon qualification, desktop hosting, persistent
commits and older OS qualification remain pending or blocked as recorded.

Linux IPC tests require the measured kernel's SO_PEERPIDFD support and procfs. They
create private directories below `~/.cache/syspane/ipc-w24/`, remove only their own
socket and empty directory, and preserve unexpected entries for investigation.
The real separate-POSIX-session denial case is not a desktop login-session claim.
Per-attempt native JSON reports remain in the owned build's `native-evidence/`.
The recorder's `--native` mode binds the exact reports named in the complete CTest
log; it does not choose an arbitrary latest passing file.

The protocol boundary vendors nlohmann/json 3.12.0 under its upstream MIT license.
[Dependency identities](../../source/build/dependencies.json) pin the header and
license digests; configure verifies them offline. The model has no JSON dependency.
`generate_settings.py` projects the canonical eleven-descriptor registry into the
build directory and rejects constraints it cannot implement. Never hand-edit that
generated table. Preview validation changes no stored configuration; commit and
scene replacement return an explicit unsupported result.

Profile revision 4 adds eleven portable recovery cases and the `syspane_recovery`
static library, for 48 total CTest entries. The library has no model, JSON, GUI or
native-handle dependency. Tests link the model separately to verify that producer
heartbeats leave observation freshness unchanged. Run just these cases with
`ctest --preset windows-x64-gcc15 -R '^recovery\.' --output-on-failure`.
The Linux wrapper's `test` action runs the full suite in its owned native build root.
Portable checkpoint records are `out/evidence/w-25-portable-<profile>.json`.

The [W-25 package](../../spec/delivery/packages/w-25-recovery.md) defines the time,
ownership, expiry and restart boundaries. Guard objects are single-owner and cannot
be copied/moved. Their time inputs are local invocation times; views do not sample
a clock. The caller must advance time and apply current policy before presentation.
`source/build/record_protocol.py --recovery --profile <profile> --build-dir <build>
--output <record>` records a completed full run, requiring all 48 cases and the
native IPC reports named in its log. It labels recovery evidence as portable only.
At that portable checkpoint, native supervision, diagnostic startup/inspector,
policy integration and visible/native-exit recovery were still pending.

Profile revision 5 adds native child supervision: both profiles run 49 CTest entries.
`SysPane.RecoveryProbe` launches only its own isolated synthetic worker and uses
authenticated health messages. It proves producer expiry, a stalled separate render
worker with responsive IPC, confirmed child exit, bounded replacement/circuit and
parent-loss cleanup. No pixels or user desktop are captured. Run the nine-case
family with `ctest --preset windows-x64-gcc15 -R '^native.RECOVERY-01$' --output-on-failure`.
It takes approximately 35 seconds; the full suite takes approximately 65 seconds.
The Linux wrapper uses the same test family in its owned build root.

Supervision checkpoint records are `out/evidence/w-25-supervision-<profile>.json`.
Use the recorder's `--supervision` option to require the complete 49-entry run and
its nine native recovery cases. Per-attempt reports remain in `native-evidence/`;
the recorder binds the exact files named by CTest, checks the probe/source digests
and requires independent child-alive/exit observations. Linux runtime sockets live
in private case directories below `~/.cache/syspane/recovery-w25/`; cleanup never
recursively deletes a tree. The parent-loss case removes only its owned socket.

See the [native supervision handoff](../../spec/delivery/supervision-handoff.md).
Telemetry and actual renderer recovery, current-policy data erasure and independent
desktop/native-editor-exit evidence remain required. The health feature does not
enable snapshot/delta or stored commands.

Profile revision 6 adds `SysPane.Diag.exe` / `syspane-diag`, a separate native
diagnostic composition, for 52 CTest entries. `--report` writes public JSON;
no arguments or `--inspect` opens standard Win32/GTK controls. The native harness
copies the executable to an owned unrelated directory, adds damaged optional files,
checks policy-override rejection and closes only its own hidden native window.
Linux also checks reporting without DISPLAY/WAYLAND_DISPLAY. Hidden-window tests
do not qualify visible desktop behavior or full accessibility. Run this boundary
with `ctest --preset windows-x64-gcc15 -R 'diagnostic|DIAG-01' --output-on-failure`.

Linux configure verifies GTK 3.24.41 and the installed package/runtime identities
in `source/build/check_diagnostic_dependencies.py`. It installs nothing. GTK is
dynamically linked; the report skips toolkit initialization but still needs its
installed loader dependencies. The measured native close test uses owned authenticated Xvfb/X11;
Wayland and full transitive packaging remain unqualified.

The policy reader has fixed protected system locations and no path/environment
override. Tests do not write HKLM or `/etc`. Positive protected-policy deployment
and native revocation qualification need an admitted administrative lab. Portable
fixtures test parsing/projection semantics, not policy provenance. Diagnostic
preservation, recent-failure metadata and recovery actions remain pending.

Diagnostic checkpoint records are `out/evidence/w-25-diagnostic-<profile>.json`.
`record_protocol.py --diagnostic --profile <profile> --build-dir <build> --output
<record>` requires the exact 52-entry suite and its IPC, supervision and diagnostic
reports, checking source and executable identity. See the
[diagnostic handoff](../../spec/delivery/diagnostic-handoff.md).

Profile revision 7 adds the independent temporal pixel oracle in `tests/desktop/`.
Windows runs 53 CTest entries, including 16 portable marker/time checks inside
`desktop.ORACLE-UNIT`; Linux runs 54, adding five native calibration cases in
`native.ORACLE-01`. Run the boundary with `ctest --preset windows-x64-gcc15 -R ORACLE
--output-on-failure`, or the same regex in the configured Linux build directory.
`SysPane.OracleProbe` exists only in the Linux profile; component metadata and the
graph checker enforce that selector instead of declaring an unavailable Win32 target.

The native observer drives generations independently and captures actual root pixels
from its owned authenticated Xvfb server. Disappearance, freeze and obstruction must
produce failed temporal observations; a deliberate capture gap must be inconclusive.
The suite passes when those fixed calibration outcomes match. Candidate visibility
flags or responsive event processing cannot replace changing pixels. No user's
desktop or unrelated application is captured, and no shell is restarted.

Raw RGB frames are bounded, losslessly compressed and embedded in each native report.
Task-owned `oracle-case-<id>/` journals also preserve each flushed frame/stimulus,
including an interrupted prefix. The recorder's `--oracle` mode recomputes every
temporal result from the captured bytes, verifies journal/source/artifact identity
and checks confirmed cleanup/root restoration. Current records are
`out/evidence/w-02-oracle-<profile>.json`; see the
[oracle handoff](../../spec/delivery/oracle-handoff.md) and
[package](../../spec/delivery/packages/w-02-desktop-oracle.md).

These checks establish observer calibration on the named development environment.
The optional lab below supplies scoped reveal, input and image-file observations;
wallpaper policy and Windows external desktop capture remain required. A synthetic Xvfb window is
never a behind-icons desktop qualification. The standalone `tests/desktop/oracle.py`
accepts one bounded trace JSON and exits 0/pass, 1/fail, 3/inconclusive or 2/invalid.

The optional W-05 X11 investigation uses an extracted Openbox/PCManFM lab. From
the admitted Linux checkout, with the owned build directory as `<build>`:

```sh
python3 source/build/prepare_x11_lab.py <build> --refresh-metadata
python3 tests/desktop/native_x11_host.py <build>
python3 tests/desktop/native_x11_host.py <build> --wallpaper-mode color
python3 tests/desktop/native_x11_host.py <build> --delayed-wallpaper --icon-input
python3 tests/desktop/native_x11_host.py <build> --wallpaper-mode color --restart-window-manager
python3 tests/desktop/native_x11_host.py <build> --delayed-wallpaper --restart-window-manager
```

Preparation downloads only the exact archives in `source/build/x11-lab-packages.json`
and verifies their sizes/digests before extraction. Metadata refresh uses a task-local
APT list directory. No system installation or maintainer script runs. The ordinary
configure/build/test commands neither prepare nor launch this optional desktop lab.
The ordinary Linux regression suite still runs without it. Revision 8 introduced
the separately owned `syspane_x11_candidate` library and pinned Xext dependency.

Default file-wallpaper startup currently fails in PCManFM with `BadDrawable`; that
failure must remain visible. `--gtk-rendering image` is a separately recorded GTK
software-backing experiment. The color control runs the same reveal/pixel criteria
without image initialization and does not qualify the failed image profile. The
runner exits zero for a completed investigation even when every host candidate fails
placement. Inspect `execution`, `observation`, `placement` and wallpaper scope in
the unique `X11-HOST-01-<id>.json` report instead of treating exit zero as a wall pass.

The observer uses only the owned Xvfb desktop with real icon-manager content and
native Super+D actions. It captures through reveal/restore, measures actual icon
concealment, preserves frame journals and checks owned-process cleanup.
`--delayed-wallpaper` configures the fixture after PCManFM initializes and requires
captured image pixels to match the PPM exactly. `--icon-input` checks the installed
runtime against `source/build/x11-input-runtime.json`, starts an owned accessibility
registry and observes native pointer/keyboard routing through exact private clipboard
URIs, AT-SPI, focus and root pixels. It never uses the user's clipboard or desktop.
Missing/mismatched optional runtime is a lab limitation, not an installation request.

Use `python3 source/build/record_x11_host.py --build-dir <build>
--report <exact-report> --output <record>` to bind evidence and recompute outcomes.
The optional `--failed-image-report <exact-default-report>` accepts a failure from
the same source/runtime checkpoint. Historical reports retain their original source
identity and must not be silently rebound to current code.
See the [input/image checkpoint](../../spec/delivery/x11-input-handoff.md).
`python3 tests/desktop/test_x11_record.py <build> <exact-input-report> -v` runs fifteen
evidence checks, including wrong URI, stale clipboard, hidden menu, title-only folder,
focus, journal and fixture overclaims. The hidden candidate passes input here; the
visible desktop candidate blocks selection, and neither passes placement. Other
profiles, product shell recovery and wallpaper policy remain unqualified.

`--restart-window-manager` adds a separate recovery interval after the unchanged
reveal trace. It stops only the owned Openbox child, requires independent pidfd exit
proof, starts one replacement and binds its supporting window through X-Resource.
The optional runtime is pinned in `source/build/x11-recovery-runtime.json`.
It cannot be combined with `--icon-input` under the current lifetime contract.
Inspect `recovery_observation.outcomes`: manager recovery and continuing generations
can pass while visible recovery fails. Every captured frame/journal is preserved.
Use the same recorder, then run
`python3 tests/desktop/test_x11_recovery_record.py <build> <exact-restart-report> -v`
for nine independent evidence checks. See the [recovery checkpoint](../../spec/delivery/x11-recovery-handoff.md).

The optional GNOME laboratory extracts a pinned runtime into the owned Linux build;
it performs no package installation or service activation. Run the workspace budget
preflight before preparation and each test. The 3 GiB combined allocation includes
runtime archives, signed metadata and preserved attempts. Preparation is the explicit
network step; ordinary builds and the native experiment stay offline.

```sh
python3 source/build/prepare_gnome_lab.py <owned-build-directory>
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory>
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker --marker-control hidden
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker --marker-control frozen
python3 source/build/record_gnome_host.py --build-dir <owned-build-directory> --reports <live-report> <hidden-report> <frozen-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_record.py <owned-build-directory> <live-report> -v
```

Each attempt retains source bytes, root frames, process identity and cleanup. The
negative controls intentionally return exit 1 with completed traces; the recorder
requires their specific visibility/deadline failures and adequate capture coverage.
It also requires identical current source inputs for all three controls. A startup
error cannot substitute for a negative control. The default command tests bootstrap
only. No icon, reveal/input, wallpaper-policy, recovery or product-host claim follows
from the marker result. See the [GNOME checkpoint](../../spec/delivery/gnome-marker-handoff.md).

The same owned GNOME runner now has a separate DING composition fixture:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --composition live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --composition above-icons
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --composition below-wallpaper
python3 source/build/record_gnome_composition.py --build-dir <owned-build-directory> --reports <live-report> <above-report> <below-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_composition_record.py <owned-build-directory> <live-report> -v
```

Run and await a successful workspace preflight before each invocation. Wrong-layer
controls intentionally return 1, but must finish the exact native scenario and fail
the required pixel dimensions. A native error does not qualify as a control. The
recorder requires all three reports to share exact current source inputs. It checks
independent pre-candidate black/white calibration, fixed opaque/transparent witnesses,
paired captures, native DING ownership, unchanged settings and preserved journals.
No user icon/theme/wallpaper is used. See the [composition checkpoint](../../spec/delivery/gnome-composition-handoff.md)
for scope and the next reveal/input/recovery boundaries.

The configured GNOME reveal experiment adds a normal owned GTK foreground window:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --reveal live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --reveal no-action
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --reveal transient-blank
python3 source/build/record_gnome_reveal.py --build-dir <owned-build-directory> --reports <live-report> <no-action-report> <blank-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_reveal_record.py <owned-build-directory> <live-report> <no-action-report> <blank-report> -v
```

Await a successful workspace preflight before each invocation. The pinned lab's
live case currently returns 1: visible hide/restore succeeds, but foreground focus
does not return. Both negative controls also return 1. The recorder requires
completed source-identical cases with exact native/pixel control outcomes; startup
errors cannot calibrate it. Recorder success means the experiment is validated,
not that the live candidate passed. Its output keeps visual transitions, focus,
continuous marker/rectangle visibility and overall acceptance separate. Raw journals
and source archives preserve failed attempts. See the [reveal checkpoint](../../spec/delivery/gnome-reveal-handoff.md).

The independent focus comparison runs three modes, each in a fresh owned desktop:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline shell
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline ding
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline candidate
python3 source/build/record_gnome_focus.py --build-dir <owned-build-directory> --reports <nine-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_focus_record.py <owned-build-directory> <nine-reports> -v
```

Repeat each mode three times with identical sources and await a successful workspace
preflight before each command. These modes return zero for completed diagnostic
observation; their records separately retain failed native focus and candidate
acceptance. The shell and DING baselines never copy or enable the candidate extension.
F9 after restoration measures actual foreground key receipt; F10 after an explicit
foreground click proves the keyboard observer works. Neither key alters the fixed
earlier acceptance interval. Missing repetitions or inconsistent results cannot
establish attribution. See the [native comparison](../../spec/delivery/gnome-focus-handoff.md).

For the native decision trace, run each of the three modes once with and once
without `--focus-trace`, completing the normal workspace preflight before each run:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline ding --focus-trace
python3 source/build/record_gnome_focus_trace.py --build-dir <owned-build-directory> --reports <six-paired-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_focus_trace_record.py <owned-build-directory> <six-paired-reports> -v
```

The flag enables bounded built-in Mutter diagnostics only in the owned shell.
The recorder binds raw-log decisions to independently identified windows and
checks that tracing did not alter observed behaviour. A successful recorder does
not imply successful candidate acceptance. See the [decision evidence](../../spec/delivery/gnome-focus-trace-handoff.md)
for the observed DING MRU selection and remaining integration boundary.

Native icon input uses the same GNOME scene and the existing pinned X11 laboratory's
PCManFM through a private MIME association. Complete the normal workspace preflight
before each invocation; no packages or user settings are installed:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-input live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-input block-pointer
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-input no-selection
python3 source/build/record_gnome_input.py --build-dir <owned-build-directory> --reports <three-input-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_input_record.py <owned-build-directory> <three-input-reports> -v
```

Live input returns 0; both calibrated negative controls return 1 with an observed
selection failure. An inconclusive startup/observer error is not a valid negative
control. The recorder verifies initial composition, native input ownership and
observations, final live composition and exact control outcomes. See the
[input checkpoint](../../spec/delivery/gnome-input-handoff.md) for scope and retained failures.

The image-wallpaper experiment runs after its own live composition prerequisite:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --wallpaper live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --wallpaper replace-file
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --wallpaper redirect-setting
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --wallpaper cover-wallpaper
python3 source/build/record_gnome_wallpaper.py --build-dir <owned-build-directory> --reports <four-wallpaper-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_wallpaper_record.py <owned-build-directory> <four-wallpaper-reports> -v
```

Use the same Windows coordinator's completed workspace-budget preflight before each
native run or verifier. The four reports must share source/runtime identities.
The recorder requires a live pass and each negative control to fail only its
intended file, settings or pixel dimension. Preserve native reports, source archives,
raw journals and PNG artifacts; native exit 1 for these calibrated faults is expected.
This uses only a private fixed 800x600 PNG and settings backend. It does not qualify
wallpaper policy or other image/display profiles, and it leaves the separate Show
Desktop focus failure open. See the [wallpaper checkpoint](../../spec/delivery/gnome-wallpaper-handoff.md).

The application-list experiment observes GNOME's actual Alt+Tab popup and overview
running-app dash, using two private normal applications and their native icons:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher ordinary-window
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher no-switcher
python3 source/build/record_gnome_switcher.py --build-dir <owned-build-directory> --reports <three-switcher-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_switcher_record.py <owned-build-directory> <three-switcher-reports> -v
```

Complete the Windows coordinator's workspace-budget preflight before each run or
verifier. These modes own their composition prerequisite and cannot combine with
other optional experiment flags. The recorder requires identical source/runtime
inputs, both normal controls and full visible native trees with independently
matched icon pixels. The extra-window and omitted-popup cases must fail the
corresponding acceptance conditions; their native exit 1 is expected. Preserve
failed attempts and raw journals. GNOME's overview dash is the named running-app
surface here; other taskbars require their own evidence. See the
[application-list checkpoint](../../spec/delivery/gnome-switcher-handoff.md).

The icon-manager recovery experiment stops only the exact held owned DING process,
lets its unchanged native supervisor replace it, and observes live drawing and
full icon input on the replacement:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-recovery live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-recovery frozen-surface
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --icon-recovery no-stop
python3 source/build/record_gnome_icon_recovery.py --build-dir <owned-build-directory> --reports <three-recovery-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_icon_recovery_record.py <owned-build-directory> <three-recovery-reports> -v
```

Complete the Windows coordinator's workspace-budget preflight before each run or
verifier. These modes own their composition and private input prerequisites and
cannot combine with other optional flags. Each attempt retains the ordinary
40-second bound and owned cleanup. The recorder requires identical source/runtime
inputs, held-process exit, native replacement ownership, original pixel witnesses
and replacement-bound input. Frozen drawing must fail progress despite successful
native replacement; omitted stop must fail replacement despite live drawing.
Both controls return native exit 1 and leave dependent input unexecuted. Preserve
all attempts and journals. Shell/compositor replacement and Show Desktop focus
remain separate open gates; see the [checkpoint](../../spec/delivery/gnome-icon-recovery-handoff.md).

The shell/compositor experiment replaces only the exact owned GNOME process while
retaining Xvfb and private buses, then checks bridge reattachment and new-desktop input:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --shell-recovery live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --shell-recovery no-reattach
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --shell-recovery no-restart
python3 source/build/record_gnome_shell_recovery.py --build-dir <owned-build-directory> --reports <three-shell-recovery-reports> --output <new-owned-record>
python3 tests/desktop/test_gnome_shell_recovery_record.py <owned-build-directory> <three-shell-recovery-reports> -v
```

Complete the Windows coordinator's workspace-budget preflight before each run or
verifier. These modes own their live composition/private input setup and exclude
other optional flags. The observer holds original shell/DING process handles; the
parent retains one replacement launched only after confirmed original shell exit.
Keep the complete outage journal and original pixel calibration. Omitted reattachment
must fail drawing despite native recovery; omitted restart must fail recovery.
These controls return native exit 1 and leave dependent input unexecuted. The named
experiment does not qualify a real session manager or product continuity. See the
[shell recovery checkpoint](../../spec/delivery/gnome-shell-recovery-handoff.md).

The optional focus experiment reuses the original candidate baseline and adds
native interaction guards. It leaves the default bridge behavior unchanged:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline candidate --focus-integration observe
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-baseline candidate --focus-integration restore
python3 source/build/record_gnome_focus_integration.py --build-dir <owned-build-directory> --reports <observe-report> <restore-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_focus_integration_record.py <owned-build-directory> <observe-report> <restore-report> -v
```

Complete the Windows coordinator's workspace-budget preflight before each native
run or verification. This mode owns its private input/registry setup and cannot be
combined with the trace or other experiment flags. Both completed controls return
exit 0 because observation mode must retain failed focus/F9 while restoration must
pass them. The original acceptance verdicts remain separate from control completion.
Keep the original reveal interval, actual keyboard journal, all 15 guard steps,
full folder-input evidence, bounded native decisions and one-way disable result.
Do not enable the controller generally from this finite experiment; see the
[focus integration checkpoint](../../spec/delivery/gnome-focus-integration-handoff.md).

The next focus experiment tests selected normal windows, a modal transient,
closed targets and static-workspace changes using the same optional controller:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-scenarios restore
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-scenarios observe
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --focus-scenarios helper-exit
python3 source/build/record_gnome_focus_scenarios.py --build-dir <owned-build-directory> --reports <restore-report> <observe-report> <helper-exit-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_focus_scenarios_record.py <owned-build-directory> <restore-report> <observe-report> <helper-exit-report> -v
```

Complete the Windows coordinator's workspace preflight before each launch. These
modes own their original candidate baseline, helper and private workspace settings;
do not combine them with other flags. Completed restore/observe runs return 0 with
separate fixed per-scenario outcomes. The deliberate helper-exit control returns 1
and must record failed startup without a dependent completion claim. Preserve every
raw sample, including transient BadWindow records for the exact closing owned
window; foreign or settled query errors cannot pass. See the
[focus-scenario checkpoint](../../spec/delivery/gnome-focus-scenarios-handoff.md).

For the historical shared-subset experiment, the existing Visual Studio 2017 XP
toolset has its own preset. It compiles the same model, protocol/policy, recovery
and diagnostic projection sources; modern native adapters require separate closure.

```powershell
cmake --preset windows-x86-v141-xp
cmake --build --preset windows-x86-v141-xp
ctest --preset windows-x86-v141-xp --output-on-failure
python source/build/package_smoke.py --profile windows-x86-v141-xp --build-dir out/build/windows-x86-v141-xp
```

This is an x86 Release/static-runtime build. Its current 54 checks execute on the current
Windows host; historical guest execution and desktop qualification remain pending.
Guest execution will cover 47 C++ case invocations and the model smoke binary;
the six build/tooling entries run on the modern host, without installing Python
3.11 or current CMake in XP.
The PE audit checks all five executables and resolved MSBuild runtime inputs.
It does not infer XP compatibility from module names or subsystem version alone.
See the [historical checkpoint](../../spec/delivery/historical-build-handoff.md).
Existing guest machines need an established test scope before use or capture.

The recent-failure boundary brings current full CTest totals to 57 on Windows and
58 on Linux. `SysPane.Diag.exe --report --failures <absolute-path>` (or
`syspane-diag` on Linux) opts into bounded advisory metadata. `--inspect --failures
<absolute-path>` uses the same current policy checks for native/accessibility text.
Unavailable operational permission returns `restricted` without reading the file;
the filename never grants policy authority. Default startup opens no failure file.

The development recovery probe accepts `supervisor <endpoint> <scenario>
<new-absolute-failure-file>` to record its synthetic fault facts. It creates a
private file exclusively and never overwrites one. This is not a product retention
or configuration-preservation command. See the [closed boundary](../../spec/delivery/packages/w-25-failure-metadata.md).

Collect current full runs with `source/build/record_protocol.py --failure-metadata
--profile <profile> --build-dir <build> --output <record>`. That flag includes all
existing native/oracle regression families and requires the new concrete records.
For the historical build, use `record_legacy_build.py --failure-metadata` with its
existing build/smoke/output arguments. Records retain source/artifact identities,
raw failures and explicitly unexecuted Windows symlink qualification.

The [native wallpaper-policy checkpoint](../../spec/delivery/gnome-wallpaper-policy-handoff.md)
uses the private dconf backend only under `--wallpaper-policy`. Prepare its pinned
CLI with `python3 source/build/prepare_gnome_policy.py <owned-linux-build>` after
a successful Windows coordinator `--action package` preflight. No packages are
installed. After a `--action test` preflight before each invocation, run:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy locked
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy unlocked
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy replace-policy
```

The locked mode returns 0; the two completed negative controls return 1. Use the
three exact emitted report paths with `source/build/record_gnome_wallpaper_policy.py
--build-dir <build> --reports <locked> <unlocked> <replacement> --output
<build>/native-evidence/<unique-record>.json`, then run
`tests/desktop/test_gnome_wallpaper_policy_record.py <build> <locked> <unlocked>
<replacement> -v` (35 checks). The private writer has a retained process lifetime
and the original background/marker/icon oracle remains unchanged. The lab owns its
policy files, so this does not qualify protected organization-policy deployment.

Specification tooling separately uses Python 3.11+ in an isolated environment:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r spec/tools/requirements.txt
.venv/Scripts/python spec/tools/specctl.py validate --schemas
.venv/Scripts/python spec/tools/specctl.py generate --check
.venv/Scripts/python spec/tools/specctl.py verify-integrity
.venv/Scripts/python -m unittest discover -s spec/tools/tests -v
```

On POSIX systems use `.venv/bin/python` instead. Missing schema dependencies
must fail explicitly. Symlink tests require OS permission; any unavailable test
is reported as skipped, never passed. Specification checks do not run native
SysPane, desktop, screensaver or setup acceptance tests.

After editing canonical inputs, run `generate`, validate and test, inspect the
diff, then run `seal --apply` and `verify-integrity`. Generated files and hashes
are projections; never edit them as if they were authored contracts. The
validation report records an identified run, not automatic certification of
subsequent changes. Use [tool usage](../../spec/tools/usage.md) for context and
impact commands.

Builds use one `source/` tree, explicit CMake targets and pinned target
profiles. Introduce directories only with real implementation. Keep outputs in
owned, bounded checkout/build/cache roots. Human, CI and AIDE workflows use the
same commands; AIDE is neither an endpoint dependency nor a build prerequisite.

Start with [TODO](../../TODO.md), [architecture](architecture.md) and
[target profiles](../../spec/delivery/target-profiles.md). License/contribution
terms remain an owner decision; this guide does not invent them.

The [W-01 foundation package](../../spec/delivery/packages/w-01-foundation.md)
defines the first model program and required cases. Its concrete profiles and
commands are now present. Buildable, implemented, qualified and
releasable are separate claims. See [the workflow](agent-workflow.md) for case
bindings and evidence needed to resume from a fresh checkout.

## Native GNOME surface producer lease

The [surface-lease package](../../spec/delivery/packages/w-25-gnome-surface-lease.md)
uses the existing owned X11/GNOME/DING laboratory and two retained public-marker
fixture processes. Run the Windows workspace preflight before each invocation,
then use `wsl -d Ubuntu-24.04 -u ir4runner --` for these Linux commands:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --surface-lease live
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --surface-lease ignore-expiry
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --surface-lease disconnect
python3 source/build/record_gnome_surface_lease.py --build-dir <owned-linux-build> --reports <live-report> <ignore-expiry-report> <disconnect-report> --output <new-owned-record>
python3 tests/desktop/test_gnome_surface_lease_record.py <owned-linux-build> <live-report> <ignore-expiry-report> <disconnect-report> -v
```

The ignored-expiry native command intentionally exits 1 with failed lease acceptance;
the other two exit 0. The recorder must accept all three intended results. It checks
exact peer/process lifetimes, command/receipt times, last-accepted data identity,
raw journals, external marker/status pixels and a post-disable original marker trace.
The first child exits 73 deliberately; the second is prelaunched and stays alive
until cleanup. This is neither an automatic restart test nor real telemetry.

Capture samples alone establish timer expiry before any later diagnostic call.
The existing marker helper has a 250 ms preparation delay before its separate
2,400 ms post-disable interval. Failed verification attempts and their source
revisions are preserved in the [checkpoint](../../spec/delivery/gnome-surface-lease-handoff.md).
The bridge is active only under this explicit experiment flag. Native product
transport/policy, render-watchdog and editor-exit integration remain pending.

## Shared measured network presentation

`syspane_network_view` provides the policy-bound renderer projection described in
`spec/delivery/packages/w-25-network-presentation.md`. The six `presentation.NVIEW-*`
CTest families cover exact counter/rate text, TTL/status axes, exact entity selection,
whole-frame capacity and borrow/policy lifetime. Forty-six fixed binary64 vectors
have independently calculated rational expectations; they run under a changed locale.
Use the ordinary build commands and, for a focused Windows check:

```powershell
ctest --preset windows-x64-gcc15 -R '^presentation[.]' --output-on-failure
```

For Linux, set the existing `SYSPANE_LINUX_BUILD_ROOT` and use the corresponding
preset through the admitted `ir4runner` account. The historical preset runs the same
portable cases on this host; it does not qualify XP/7. The native Linux collector
family additionally checks real counters/rates, retained states and typed revocation
through this projection. Raw operational fields stay in its owned pipe or ignored
private failure records; public evidence contains only outcomes and counts.

Record a complete run with `record_protocol.py --network-presentation` or
`record_legacy_build.py --network-presentation` and their existing profile/build/
output arguments. The historical recorder also requires the exact relocated smoke
result. The configure-time subtree size guard reads the declared campaign allocation;
it supplements the mandatory combined Windows preflight and does not replace it.
The component enables no native operational surface, cached payload or release.

## Native retained network cache and erasure

The explicitly enabled cache experiment uses the existing owned GNOME laboratory
and tested Linux CollectorProbe. Run the mandatory Windows workspace preflight
before each native command, then use the admitted `ir4runner` account:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --network-cache live
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --network-cache ignore-clear
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --network-cache wrong-value
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --network-cache owner-loss
python3 source/build/record_gnome_network_cache.py --build-dir <owned-linux-build> --reports <live> <ignore-clear> <wrong-value> <owner-loss> --output <new-owned-record>
python3 tests/desktop/test_gnome_network_cache_record.py <owned-linux-build> <live> <ignore-clear> <wrong-value> <owner-loss> -v
```

The two negative controls must fail candidate acceptance and pass independent
verification of that failure. A public native glyph calibration establishes the
digit/null templates before any operational values. The oracle compares complete
real counter/rate strings, then checks old-pixel removal after policy revocation,
permission restoration without a full, disable and independently observed owner exit.
The tile's retained/unknown-age caption is deliberate; live freshness is not enabled.

`network-*.private.*` files contain operational values and pixels. Keep them under
their mode-0700 attempt directory with mode-0600 files. Commit only public reports,
source archives and hashes/references to those private files. The relay uses the
existing short native IPC root because the isolated GNOME HOME exceeds Unix socket
path limits. Native owner/queue/clock and release limitations are in the
[checkpoint](../../spec/delivery/native-network-cache-handoff.md).


The [standalone GJS clock boundary](../../spec/delivery/packages/w-25-gjs-clock.md)
adds a Linux development shared library and `SysPaneClock-0.1.typelib`. Ordinary
configure/build verifies the installed GI compiler and GObject identities offline.
`native.GJS-CLOCK` requires the already prepared, pinned GNOME extraction; it runs
standalone GJS with no display or user bus. Run it after the Windows test preflight:

```sh
SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498 \
  ctest --preset linux-x64-gcc13 -R '^native.GJS-CLOCK$' --output-on-failure
```

The observer retains both child process handles and checks exact BOOTTIME causal
brackets, rejected descriptors, 64 close cycles and native peer-exit failure.
`record_protocol.py --gjs-clock --profile linux-x64-gcc13 --build-dir <owned-build>
--output <record>` recorded the 108-entry clock checkpoint and checked the bound native
clock observations, sources and artifacts. The module has no installed product
payload; importing it does not authorize a producer or establish remote freshness.
Shell code must connect asynchronously and bind current policy before future use.
Existing desktop evidence keeps its original collector/source identity. Rebuilds
require an explicitly refreshed evidence binding before the retained-cache laboratory
can admit a changed collector; never bypass its fingerprint check.


The [owned asynchronous shell clock](../../spec/delivery/packages/w-25-gnome-clock.md)
uses the existing GNOME laboratory and native `SysPaneClock-0.1` artifacts. After
the Windows workspace test preflight, run from the unprivileged Linux checkout:

```sh
python3 tests/desktop/native_gnome_bootstrap.py \
  /home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13 --clock-age live
```

Also run `freeze-age`, `ignore-expiry`, `peer-exit`, `pending-disable` and
`wrong-peer`. The first two are expected failed candidate outcomes. The clock peer
is a bounded child of the owned shell, inheriting its POSIX session; do not weaken
the native session check to attach the separately launched retained relay.
`record_gnome_clock.py --build-dir <owned-build> --output <record> <six-reports>`
recomputes the public glyph/clock oracle and verifies held-child exit and artifacts.
`tests/desktop/test_gnome_clock_record.py <six-clock-age.json-files> -v` checks
adversarial mutations of those original observations. No operational values enter
this clock fixture. The clock and retained-cache relay now use the existing
`w-25-live-network-session-linux-x64-gcc13.json` native evidence binding; the earlier
presentation and native-cache records remain historical and unchanged.


The [Windows host observation package](../../spec/delivery/packages/w-03-windows-investigation.md)
adds a read-only native prerequisite with no C++ target or profile change. Run the
workspace test preflight before each command:

```powershell
.venv/Scripts/python.exe -X utf8 tests/desktop/test_windows_host_inventory.py -v
.venv/Scripts/python.exe -X utf8 tests/desktop/windows_host_inventory.py
```

The observer owns an eight-second child and writes exact source/runtime identities,
two shell observations and cleanup to a fresh `out/campaign/WINDOWS-HOST-INVENTORY-01-*`
directory. It records no window titles or pixels and performs no shell/input mutation.
`observed` describes only a consistent native structure, not a qualified attachment
or visible host. The complete desktop experiment requires a designated synthetic
lab and the package's unchanged independent pixel/input/recovery acceptance.

The [native GJS network consumer](../../spec/delivery/packages/w-25-gjs-network-view.md)
adds `SysPaneClock.NetworkView` to the existing module. It owns the shared C++
DataView and network projection; callers supply typed development policy and feed
bounded original frames. Its synchronous fixture driver is for standalone testing;
product shell I/O must remain asynchronous. After the Windows test preflight:

```sh
SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498 \
  ctest --preset linux-x64-gcc13 -R '^native.GJS-NETWORK$' --output-on-failure
```

The 109-entry checkpoint used `record_protocol.py --gjs-network --profile
linux-x64-gcc13 --build-dir <owned-build> --output <new-record>`. This
scope includes the original clock and all preceding regression families. It verifies
the synthetic consumer's source/artifact identities, native age brackets, namespace,
cleanup and held-peer exit. The standalone peer supplies clock/socket identity;
fixture input injection is not evidence of operational delivery through that socket.
The Linux profile rebuilds the static dependency closure as position-independent
code for the shared module. Before another desktop experiment, explicitly update
the pinned collector/library evidence binding to this build and preserve its old
record. The previous GNOME matrices keep their original artifact identities.

The [live native session](../../spec/delivery/packages/w-25-live-network-session.md)
adds `native.GJS-LIVE` to the current Linux suite. After the Windows workspace
test preflight, run from the unprivileged Linux checkout:

```sh
SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498 \
  ctest --preset linux-x64-gcc13 -R '^native.GJS-LIVE$' --output-on-failure
```

The runner starts real supervised collection and the same asynchronous
`networkSession.js` owner intended for the shell. It tests `live`, `lease-loss`,
`hang`, `revoke` and `parent-loss`. Each worker takes two real samples and deliberately
holds the second while it ages. Private original-frame journals and consumer
transcripts stay under mode-0700 native evidence directories, with mode-0600 files;
public reports contain lifecycle facts and hashes, without raw interface counters.

Record the complete current Linux suite with `record_protocol.py --live-network
--profile linux-x64-gcc13 --build-dir <owned-build> --output <new-record>`. It includes
both preceding GJS families and all native collector regressions. This evidence is
standalone native delivery, not a visible desktop qualification. Before the next
GNOME run, explicitly rebind its pinned collector/library record to this build;
preserve the old public-clock and retained-cache records and acceptance criteria.

The [measured GNOME network package](../../spec/delivery/packages/w-25-gnome-live-network.md)
uses that same asynchronous session owner inside the owned shell. Run the Windows
workspace test preflight before each Linux command, under the admitted unprivileged
runner:

```sh
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --network-live live
```

Repeat with `freeze-age`, `ignore-expiry`, `wrong-value`, `ignore-clear`,
`lease-loss`, `revoke`, `peer-exit` and `hang`. The four drawing fault controls must
retain failed candidate outcomes. Each attempt owns its Xvfb, private buses,
shell, same-session collector and short IPC directory. The tile stays hidden until
the public composition prerequisite finishes. The observer then brackets original
native counters, derives rates, decodes values/age/status pixels without diagnostic
queries during capture, and confirms erasure and actual descendant exits.

`source/build/record_gnome_live_network.py --build-dir "$BUILD" --output
<new-record> <nine-native-reports>` verifies source-identical controls against their
original private journals. `tests/desktop/test_gnome_live_network_record.py
<nine-network-live.private.json-files> -v` challenges that verifier with altered
observations. Raw operational JSON and crops remain mode 0600 inside the attempt's
0700 directory; preserve only their hashes in public evidence. Do not copy them to
the repository. The existing public-clock and retained-cache matrices remain useful
regressions with their original meanings. Native build artifacts retain the pinned
live-session checkpoint at that historical checkpoint; that drawing-only experiment
changed no C++ target or profile.

The [independent render-watch package](../../spec/delivery/packages/w-25-gnome-render-watch.md)
adds three `health.HEALTH-ASYNC-*` cases and a native `HealthView` in the existing
GJS module. The complete suites contain 113 Linux and 105 contemporary Windows
entries. Record them with `record_protocol.py --async-health --live-network` on
Linux and `--async-health --network-presentation` on Windows, retaining the usual
profile/build/output arguments. The current desktop bootstrap pins the new
`w-25-gnome-render-watch-linux-x64-gcc13.json` build record; earlier evidence retains
its original identity. Historical-toolset native health remains disabled.

After each completed Windows workspace test preflight, run under `ir4runner`:

```sh
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --render-watch live
```

Repeat with `render-stall`, `false-progress`, `hidden`, `revoke`, `watch-exit`,
`watch-hang` and `shell-freeze`. These cases launch the existing RecoveryProbe in
`render-watch` mode as a separate owned child. The shell uses the shared native
health parser over asynchronous socket IO; an operational draw followed by stage
after-paint completes the exact pending challenge. The native watcher enforces its
own deadline outside the shell loop. Independent pixels remain required: the
`false-progress` control must retain a failed candidate outcome.

The observer signals only held pidfds from the owned laboratory process tree.
It resumes the same stopped shell in a finally path and measures erasure from
confirmed resume. The stopped shell's surviving pixels are recorded honestly.
The native shell-side view also expires a silent watcher, then the existing owner
enforces its bounded teardown. Neither experiment restarts an installed desktop.

`source/build/record_gnome_render_watch.py --build-dir "$BUILD" --output
<new-record> <eight-native-reports>` recomputes acceptance from original health
journals and private glyph crops. Run `tests/desktop/test_gnome_render_watch_record.py
<eight-network-render-watch.private.json-files> -v` for adversarial evidence checks.
`render-watch.jsonl` contains public lifecycle facts; the two `network-*.private.*`
files retain operational originals/pixels and must remain in their private native
attempt directory. Preserve all attempts and source archives, including failures.

After the same workspace preflight, `/usr/bin/python3 tests/fault/native_render_deadline.py
"$BUILD"` exercises native queued-message ordering without a desktop. It holds and
stops its own watcher, queues late progress, heartbeat and shutdown separately,
then requires a latched expiry and failed native exit after resume. The initial
three failing traces remain preserved; no queued message may override expiry.

## Independent collection during consumer recovery

The [consumer-continuity package](../../spec/delivery/packages/w-25-consumer-continuity.md)
adds `native.CONSUMER-CONTINUITY` to the Linux suite (114 entries). After the ordinary
Windows workspace preflight, build and run the existing Linux preset. Record the
complete suite using `record_protocol.py --consumer-continuity --profile
linux-x64-gcc13 --build-dir <owned-build> --output <new-record>`. The flag includes
the earlier live-network and asynchronous-health families. Windows retains 105
entries; its new run is a regression, not consumer-continuity qualification.

For a focused run, invoke `tests/protocol/native_consumer_continuity.py
<owned-build>/SysPane.CollectorProbe <owned-build>/native-evidence` as the admitted
Linux user. The observer owns all processes, holds pidfds, faults only those exact
consumer lifetimes and verifies real acquisition throughout recovery. Original
source/consumer JSONL remains 0600 in the recorded owned 0700 native IPC directory;
public results contain only lifecycle metadata and original-file hashes. Do not
commit or print the private originals. The runner preserves each attempt under a
unique evidence directory before updating its current family record.

This composition uses one POSIX session, one continuously demanded real worker,
and fresh native consumers admitted by the existing Sessions/RestartGate owners.
The typed revocation fixture removes the consumer's authority while retaining the
controller's independently authorized collection demand. It does not model global
policy revocation or authorize cross-session attachment. The existing GNOME command
now pins `w-25-controller-render-recovery-linux-x64-gcc13.json`; earlier records keep
their original artifact identities. The following experiment closes one persistent
session composition while retaining the earlier native cases.

## Persistent controller and automatic GNOME reattachment

Read the [bounded package](../../spec/delivery/packages/w-25-gnome-controller-recovery.md)
and [checkpoint](../../spec/delivery/gnome-controller-recovery-handoff.md). After a
completed Windows workspace preflight for each test, run as `ir4runner` in the
admitted WSL distribution, using the existing owned build root:

```sh
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery live
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery no-reattach
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery revoke
```

The middle command returns 1 for its required failed pixel outcome. It must still
complete its native observation and cleanup; an observer exception cannot pass
that negative control. The other commands return 0. Retain these original crash
controls and add the five controls in the following section before recording the
current complete matrix. Keep all inputs identical across the matrix and retain
every attempted source archive, including failures.

The native controller is the persistent session/group owner. Its source and shell
inherit that session; the replacement attaches automatically after confirmed old
exit and existing backoff. The observer issues no replacement Start command. Native
Escape dismisses the replacement startup overview before the recovered desktop
interval, so this case does not qualify unattended overview-free recovery. Global
policy, installed session management and native editor recovery remain separate.

The four `network-controller-*.private.*` files contain original counter brackets,
source/delivery documents and pixels. Keep them 0600 in their owned 0700 native
attempt directory; public evidence records their paths, bounds and digests only.
The native owner acknowledges shutdown and confirms held child exits; the outer
lab confirms its owned process group is empty. No command targets a user desktop.

## Automatic replacement after independent render failure

The [render-recovery package](../../spec/delivery/packages/w-25-controller-render-recovery.md)
adds an independently serviced render-health connection to that same native
controller; the [checkpoint](../../spec/delivery/controller-render-recovery-handoff.md)
records its exact scope. Use the same bootstrap command and workspace preflight with each of
`render-stall`, `hidden`, `false-progress`, `shell-freeze` and `render-revoke` as the
`--controller-recovery` value. No additional installed service or desktop is used.

The fixed render deadline remains three seconds even while ordinary health and
collection continue. Exact old-child exit and the existing restart gate precede
replacement. The replacement automatically reattaches both measured state and its
render-health lifetime. `false-progress` deliberately acknowledges from the wrong
path while pixels remain frozen; its expected exit is 1. The other four new controls
expect exit 0, including denied replacement in `render-revoke`.

Run `source/build/record_gnome_controller_recovery.py --build-dir "$BUILD"
--output <new-owned-record> <eight-reports>` and
`tests/desktop/test_gnome_controller_recovery_record.py <eight-reports>` to recompute
the original private evidence and challenge the acceptance checks. Complete native
observations, exact artifacts/source identities and cleanup are mandatory even for
expected failed candidates. The earlier three-case checkpoint retains its original
recorder in its archived source; it is not relabeled as this eight-case matrix.

The `shell-freeze` observer stops only its held owned shell. The native controller
kills that exact stopped lifetime and replaces it; the observer cannot resume the
old shell to claim recovery. All recovered desktop intervals still record native
overview dismissal explicitly. Installed session management and editor recovery
remain separate. Keep original operational crops/journals private.


## Independent owned X11 editor exit

The [package](../../spec/delivery/packages/w-25-editor-exit.md) builds
`syspane_editor_exit` and the development-only `SysPane.EditorExitProbe` on the
Linux profile. It acquires a native emergency shortcut before creating one owned
candidate and provides a separate GTK Close editor button. It reads no scene or
operational data. The [handoff](../../spec/delivery/editor-exit-handoff.md) distinguishes
this lifetime experiment from full scene editing and installed recovery.

Use the ordinary Linux configure/build commands and Windows workspace preflight
before each action. In the existing unprivileged Linux environment, run:

```sh
SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498 \
  ctest --preset linux-x64-gcc13 -R '^native[.]EDITOR-EXIT$' --output-on-failure
```

The runner creates authenticated owned Xvfb displays. Nine cases require confirmed
native exit and independent restored pixels/clicks within 1,500 ms; conflict denies
child admission. Caps/Num Lock, held pointer, real keymap changes, frozen children
and parent loss have separate cases. Native GTK discovery verifies owner PID,
title and geometry. Reports are `native-evidence/EDITOR-EXIT-01-<attempt>.json`;
original native/observer records remain alongside each report. No user desktop,
window manager or installed shortcut is modified.

Revalidate an existing report with `python3 source/build/record_editor_exit.py
<absolute-report> <absolute-EditorExitProbe>`. After a test preflight, the independent
evidence tests run with `python3 tests/desktop/test_editor_exit_record.py
<absolute-report> -v`. The profile remains experimental; scene transactions,
fullscreen recovery discovery and Wayland need their own contracts and evidence.

## Independent exit on the measured GNOME desktop

The [GNOME package](../../spec/delivery/packages/w-25-gnome-editor-exit.md) adds an
ordinary maximized public-pixel candidate to the existing owned desktop/controller
experiment. The independent owner retains the same keyboard shortcut, GTK button,
child lifetime and bounded escalation. No installed shortcut or user desktop is used.

After each Windows workspace test preflight, run the existing unprivileged bootstrap:

```sh
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery editor-key
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery editor-button
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery editor-owner-loss
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery editor-controller-freeze
/usr/bin/python3 tests/desktop/native_gnome_bootstrap.py "$BUILD" --controller-recovery editor-no-exit
```

The last command returns 1 for its required failed recovery, with complete healthy
collection and native observation. The others return 0. Original icon obstruction,
native exit, restored input and original measured pixels are separate requirements.
The editor artifact must match `w-25-gnome-editor-exit-native-build.json` under
`out/evidence/`, in addition to the existing measured-controller build pin.

Use `source/build/record_gnome_editor_exit.py --build-dir "$BUILD" --output
<new-owned-record> <five-reports>` and
`tests/desktop/test_gnome_editor_exit_record.py <five-reports>` to verify the exact
matrix and challenge its evidence. Keep sources identical across the native matrix.
Preserve the original private measurement/pixel journals and failed placement
attempts. The [handoff](../../spec/delivery/gnome-editor-exit-handoff.md) records the
remaining scene-transaction, fullscreen and installed-ownership boundaries.

## Shared controller demand owner

`syspane_demand` implements the typed [demand contract](../../spec/delivery/packages/w-07-demand-owner.md).
It depends on the existing configuration/policy component and creates no threads,
timers, sockets or native workers. Call it from the controller's serialized event
loop, pass locally authenticated authority, and treat cancellation separately from
the executor's exact native stop/completion proof.

After ordinary workspace preflight and configure/build, run `ctest --preset
<profile> -R '^(demand|composition)[.]' --output-on-failure`. This selects nine
behavior families and two dependency checks on each existing development profile.
Historical-toolset tests execute on the current Windows host; the
[handoff](../../spec/delivery/demand-owner-handoff.md) records their import audit
and explicitly leaves guest/runtime and native executor qualification open.

The [0.1.0 release scope](../../spec/delivery/release-0.1.0.md) requires all five
named platform tracks and full native editions. Passing these component checks does
not establish any new OS floor, desktop support or release readiness.

## Native scene editor component

After ordinary Linux workspace preflight and configure/build, run
`ctest --preset linux-x64-gcc13 -R '^native[.]EDITOR-FORM$' --output-on-failure`.
The runner owns a private Xvfb/DBus laboratory. It checks actual pointer/keyboard
input, rendered pixels, accessible fields, coherent stored resources and a separate
recovery owner. The fixture executable is `syspane_editor_window`; it is not an
installed application entry point. See the [package](../../spec/delivery/packages/w-10-native-editor.md)
for the exact admitted controls and [handoff](../../spec/delivery/native-editor-handoff.md)
for results and remaining gates.

Embed EditorForm on its GTK owner thread, supply coherent authored/resource state,
current policy and topology, and route callbacks through the existing command owner.
Deliver results by their original ticket/epoch and reload with fresh resources.
Install the separate escape owner before mapping an input-blocking editor. The
form does not create a store, authorize itself or qualify a desktop host.

### Native content properties

The shared content projection lives in `source/interfaces/editor_content.*` and
uses EditorDraft for atomic validation/history. The private GTK dialog owns only
bounded input and admitted resource-choice buffers. Frozen scenes, package bytes
and pins are in `tests/editor/content-properties-{cases,fixture}.json`.

After the ordinary profile build, run `ctest --preset <profile> -R "^editor[.]CONTENT-" --output-on-failure`.
In the unprivileged Linux laboratory, run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-CONTENT-PROPERTIES$" --output-on-failure`.
The native observer records a 640×560 DIP display at ¾ scale, live synthetic
telemetry, actual input, pixels, held accessible references and stored resource
bytes. Deliberate wrong-content, frozen-preview and retained-content faults must
be positively distinguished. Run the existing snap/group/arrange/editor/large-command
matrices after changes to the shared native owner. See the
[handoff](../../spec/delivery/content-properties-handoff.md) for source-bound evidence.

### Native binding authoring

`source/interfaces/editor_binding.*` projects bounded private fields into existing
binding descriptors and one WidgetContentEdit. The lazily created GTK dialog owns
no DataView, persistent mapping or transaction ledger. The shared validator and
EditorDraft remain authoritative. Private text allows a caller-supplied 4096-character
editing buffer for escaped strings; all existing controls retain their own limits.

After ordinary preflight and profile build, run `ctest --preset <profile> -R "^editor[.]BINDING-" --output-on-failure`.
The seven families use fixed complete scenes and exact text/number values. In the
unprivileged Linux laboratory run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-BINDING-AUTHORING$" --output-on-failure`.
Fifteen cases operate actual controls, compare pixels/accessibility and coherent
stored resources, reopen and challenge deliberate storage/preview/retention faults.
The original binding cases and supplemental escaped-text cases remain separate
frozen inputs. Rerun existing content, snap, group, arrange, editor, settings and
large-command matrices when changing shared native ownership or private controls.
See the [handoff](../../spec/delivery/binding-authoring-handoff.md) for exact evidence.

### Native widget creation

`editor_create.*` projects bounded private input into InsertWidget. The optional
`select_inserted` flag makes object insertion and selection one EditorDraft history
entry; its default preserves existing callers. The GTK creation dialog uses the
existing immutable resource choices, validator, renderer and request owner.

After profile build and workspace preflight, run `ctest --preset <profile> -R "^editor[.]CREATE-" --output-on-failure`.
Six families compare fixed full objects/scenes, parent display intent, selection
history, exact command scenes, limits and atomic rejection. In the unprivileged
Linux laboratory run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-WIDGET-CREATION$" --output-on-failure`.
Seventeen cases operate actual controls and inspect pixels, accessibility, coherent
stored resources, reopen, cancellation, restart and erasure. Existing native
binding/content/snap/group/arrange/editor and large-command matrices cover shared
ownership regressions. See the [evidence handoff](../../spec/delivery/widget-creation-handoff.md).

### Native observation calibration

After Linux workspace preflight and ordinary configure, run `ctest --preset
linux-x64-gcc13 -R "^native[.]EDITOR-OBSERVATION$" --output-on-failure`. Seven owned
cases verify explicit live, unfocused, delayed, disconnected, missing-object and
denied replies. Existing `EDITOR-WIDGET-CREATION`, `EDITOR-BINDING-AUTHORING`,
`EDITOR-CONTENT-PROPERTIES`, `EDITOR-SNAP`, `EDITOR-GROUP`, `EDITOR-ARRANGE`,
`EDITOR-FORM` and `LARGE-COMMANDS` remain required consumers of the shared observer.

`tests/editor/native_observation.py` caches addresses only. Calls have a 200-ms
ceiling and inherit any smaller remaining wait budget. Read-only retries never
repeat user input or persistence commands. No unavailable read counts as empty,
unfocused, unsupported or erased; held-key checks require positive focus throughout.
UnknownObject erasure additionally checks a live accessible owner. Per child, the
observer bounds retained addresses at 4096 and error records at 128. Reopening clears
addresses. Error records include method, unique owner, object path, duration and
explicit error; focus failures additionally record X11 ownership.

See the [handoff](../../spec/delivery/native-observation-handoff.md) for preserved
diagnostics and unresolved historical focus failures. These are native laboratory
checks, not installed-desktop or historical-platform qualification.

### Layout and responsive authoring

`editor_layout.*` projects bounded private input into existing atomic draft edits.
`RootDisplayEdit` assigns a whole top-level subtree in one operation, retaining the
128-operation limit for 256-node scenes. Optional variant indices on move, resize,
align and distribute preserve existing base-only callers. GTK captures resolved
variants for direct operations and rejects stale buffered geometry after topology
changes. Native tree selection retains its model during selection callbacks.

After ordinary workspace preflight and profile build, run
`ctest --preset <profile> -R "^editor[.]LAYOUT-" --output-on-failure`.
Eight families cover exact scenes, kinds, breakpoints, display/order, atomic bounds,
policy and independent geometry. In the unprivileged Linux laboratory run
`ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-LAYOUT$" --output-on-failure`.
Twenty-one cases exercise actual controls, pixels, saved resources, reopen,
topology, cancellation, recovery and erasure, including positive fault controls.
The existing nine native matrices remain required regressions for shared-owner
changes. See the [handoff](../../spec/delivery/layout-authoring-handoff.md).

### Native keyboard input ordering

The layout oracle acknowledges each navigation key using explicit native selected
rows and the expected title. A single three-second deadline covers the whole
selection. End can select the same row as the eventual final Down; that intermediate
match cannot prove the later queued input completed. Do not substitute an arbitrary
sleep, retry a mutation or force focus inside a held-focus assertion.

Layout-suite buttons now use explicit focus plus Space again. The original scenes,
pixel/storage outcomes, fault controls and 200-ms erasure bound remain unchanged.
After workspace test preflight, run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-LAYOUT$" --output-on-failure`.
The [handoff](../../spec/delivery/keyboard-input-handoff.md) records the paired native
experiment, all ten regression matrices and the remaining qualification scope.

### Explicit container transformations

`WrapWidgets` takes disjoint sibling IDs, a fresh group ID/title, complete group
layout and priority. `UnwrapWidget` removes one group and promotes its children.
Both preserve surviving authored values exactly and intentionally resolve them in
the new parent. Selection/history change atomically through EditorDraft. Existing
GroupWidgets/UngroupWidget retain their fixed-geometry rules. The native Layout
modal reuses its parser/buffers for Wrap and an explicit Unwrap confirmation.

After workspace preflight/configure/build, use `ctest --preset <profile> -R
"^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])" --output-on-failure`.
The owned non-root Linux laboratory additionally runs `ctest --preset linux-x64-gcc13
-R "^native[.]EDITOR-CONTAINERS$" --output-on-failure` and existing editor matrices.
See the [package](../../spec/delivery/packages/w-10-containers.md) and
[handoff](../../spec/delivery/containers-handoff.md) for exact scope and evidence.

Persistent editor locks use SetWidgetLocks through EditorDraft. Scene 0.4 retains
content and adds edit_locked; command 0.6 requires the resource, scene-content,
large-command and edit-lock negotiation gates. Use `editor.LOCK-*` and native
`native.EDITOR-LOCKS` in the existing presets. The [package](../../spec/delivery/packages/w-10-edit-locks.md)
and [handoff](../../spec/delivery/edit-locks-handoff.md) record scope and evidence.


### Native editor refresh fairness

The editor refresh timer runs below normal-idle GTK accessibility work. Immediate
widget style transitions are scoped to the editor; global animation settings are
unchanged. After the usual workspace preflight/configure/build, run
`ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-REFRESH$" --output-on-failure`.
The owned non-root Xvfb/D-Bus test injects 60 ms paint work, reuses the original
large-scene keyboard/pixel/storage/erasure oracle, and positively detects the old
timer priority as a fault. Do not preload its module into an ordinary session.

The [handoff](../../spec/delivery/focus-idle-handoff.md) retains the original failures,
the auxiliary observation correction, paired animation experiment and exact runtime
admissions. Changed text/image runtime identities require configure verification
and existing native rendering/decode checks with unchanged expected outputs.


### Complete image validation and observation evidence

`scene.IMAGE-VALIDATION` checks invalid first/middle/last color channels at maximum
size through validation, fitting and orientation. Existing raw-image checks remain
mandatory; a faster loop is not a trusted-input bypass. Use the existing image
and native rendering tests with their unchanged timing and pixel expectations.

Before the full native rendering matrix, admit at least 400 MiB of output growth
within the combined workspace bound in addition to running the ordinary preflight.
The earlier run exceeded its 64 MiB reservation; its failure is preserved.
The [handoff](../../spec/delivery/runtime-observation-handoff.md) records measured
validation cost, exact artifacts, six native query trials and remaining unexplained
accessibility timeouts. Successful unchanged queries do not establish a repair.

The [visibility evaluator](../../spec/delivery/packages/w-09-visibility.md) provides
`scene::project_visibility(rule, inputs, now_ms, sink, limits)` through syspane_scene.
The visibility 0.1 rule uses the existing singleton binding grammar and one typed
comparison with an explicit unit. The callback receives only a VisibilityCode
inside the existing policy-bound borrow; retain no operational decision or payload
and do not reenter DataView. Only shown/hidden are successful evaluations. Every
other outcome requires explicit unresolved handling by the future native owner.
Scene 0.4 and older and command 0.6 and older do not admit this property.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(scene[.](VISIBILITY-|BIND-)|composition[.])' --output-on-failure`, then the
affected ordinary non-native suite. The fixed inputs are
`tests/scene/visibility-cases.json`; the [handoff](../../spec/delivery/visibility-handoff.md)
records actual runs and the remaining native admission gates.

The [visibility admission package](../../spec/delivery/packages/w-10-visibility-admission.md)
adds scene 0.5/command 0.7 to the existing validators, resource provider, transaction
ledger and editor. SetWidgetVisibility accepts distinct target IDs and an optional
visibility document; absence means Clear. Do not advertise renderer support from
authored resource capability. The current SceneSurface rejects this version with
surface.visibility_unavailable after the existing policy checks.

After the ordinary workspace preflight/configure/build, run `ctest --preset
<profile> -R '^(editor[.](VIS-|LOCK-)|configuration[.]|composition[.])'
--output-on-failure` and the full non-native suite. On the owned non-root ext4 Linux
profile, native.VISIBILITY-ADMISSION invokes the bounded ConfigProbe visibility-commit
laboratory mode. It installs nothing and does not enable a native visibility UI.
Regress native storage/IPC, SCENE-SURFACE, SCENE-INSPECTOR-MODEL, EDITOR-LOCKS and
EDITOR-CONTAINERS. Exact input examples live in tests/editor/visibility-admission-cases.json;
the [handoff](../../spec/delivery/visibility-admission-handoff.md) binds executed evidence.


The [borrowed composition package](../../spec/delivery/packages/w-09-visibility-composition.md)
adds `scene::project_bindings` for ordered queries sharing one union of protected
DataView borrows. Its work/output limits apply to the whole batch. Use
`scene::project_scene_visibility` for authored preorder, inherited content gates
and independent unresolved diagnostics. Neither callback may retain payload or
decisions or reenter contributing views; these helpers create no native cache.
A content composer must also preserve current content authorization and mandatory
status. SceneSurface's refusal gate remains in force until that owner is verified.

Run `ctest --preset <profile> -R '^(scene[.]|editor[.]VIS-|composition[.])'
--output-on-failure`, followed by the full non-native suite. The new families are
VISIBILITY-BATCH-ORDER/ISOLATION/BOUNDS/LIFETIME and VISIBILITY-TREE-CASES/LIFETIME.
The frozen hierarchy examples are tests/scene/visibility-composition-cases.json.
Existing native SCENE-SURFACE, SCENE-INSPECTOR-MODEL, SCENE-ERASURE, EDITOR-LOCKS
and EDITOR-CONTAINERS remain regression checks; they do not qualify conditional
native pixels. The [handoff](../../spec/delivery/visibility-composition-handoff.md)
preserves the original failed fixture and the exact schema-based correction.


The [theme-authoring package](../../spec/delivery/packages/w-10-theme-authoring.md)
adds `interfaces::theme_input/theme_edit` and `configuration::author_theme`.
Input hydration and editing return owned values; no-op returns the original theme.
Artifact construction needs current resource policy and `theme.typography`, preserves
the source license and emits exact theme/package pins. It performs no I/O, draft
mutation or durable publication. A changed artifact alone cannot be submitted through
old command schemas or enable EditorForm typography.

After ordinary configure/build and workspace preflight, run
`ctest --preset <profile> -R '^editor[.]THEME-' --output-on-failure` and the full
portable suite. The pinned Linux laboratory also runs `native.THEME-TYPOGRAPHY` and
`native.ROLE-COMPOSITION`. Read the [handoff](../../spec/delivery/theme-authoring-handoff.md)
before extending resource selection, commands, generations and native controls.


The [theme-override package](../../spec/delivery/packages/w-10-theme-overrides.md)
adds explicit `ContentCatalog::theme_resources` for resource selection 0.2 and
`replace_theme_resources` for one immutable authored override or reset. The latter
requires current source/result policy and `configuration.theme-overrides` admission.
It retains `ResourceSet::base_packages()` and validates canonical artifact bytes;
it never appends a preset layer. `ContentCatalog::resources` keeps the legacy shape.
Legacy command/store formats and unadmitted SettingsDraft contexts reject new
selections. Command 0.8 supplies durable storage; the theme-history integration below
now admits shared drafts explicitly. Native controls still require their own evidence.

After ordinary workspace preflight/configure/build, run
`ctest --preset <profile> -R '^configuration[.]THEME-OVERRIDE-' --output-on-failure`
and the affected/full portable suites. The non-root Linux laboratory runs
`ctest --preset linux-x64-gcc13 -R '^native[.](RESOURCE-GENERATIONS|CONTENT-COMMANDS)$'
--output-on-failure` for legacy consumer regressions. These native checks do not
qualify storage of new selections. See the [handoff](../../spec/delivery/theme-overrides-handoff.md).


The [durable theme-command package](../../spec/delivery/packages/w-08-theme-commands.md)
adds `prepare_theme_command` to the existing transaction worker. Command 0.8 carries
an exact current source pin, complete base/role fonts and resource selection 0.2.
The owner constructs and validates canonical bytes without importing packages.
The explicit `configuration.theme-overrides` feature requires the existing visibility,
edit-lock, full-scene, content and transaction features plus theme typography support.
Original body bytes remain request identity, including their existing 327680-byte limit.

Linux writes generation manifest 0.4 and resource index 0.2 only for command 0.8.
Recovery checks version pairing, exact files/hashes and fulfilled font intent.
The ConfigProbe `theme-commit <command-file> <fault>` mode uses current resources;
it accepts no import roots. Old generations retain their readers. This does not
enable native font controls or EditorForm typography.

After ordinary preflight/configure/build, run
`ctest --preset <profile> -R '^configuration[.]THEME-COMMAND-' --output-on-failure`,
the affected configuration/editor/protocol/component tests and full portable suite.
In the existing non-root ext4 Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC|VISIBILITY-ADMISSION)$' --output-on-failure`.
The independent oracle compares literal artifact bytes, confirms stopped/killed owners,
and preserves corruption and wrong-output witnesses. Read the
[handoff](../../spec/delivery/theme-commands-handoff.md) before editor integration.


The [theme-history package](../../spec/delivery/packages/w-10-theme-history.md)
adds `EditorDraft::set_theme_fonts`, `theme_fonts_available` and a const `resources`
borrow. Supply complete font and null/complete role-map values. Existing SceneThemeEdit
retains the override or selects a base theme, preserving null versus explicit ID.
History stores scene/selection/resource snapshots together. `history_bytes` includes
unique additional resource bytes; count and byte limits remain 64 and 8 MiB.
Borrowed resources expire on mutation, policy, reload or close, like the scene borrow.

`ContentCatalog::retained` shares internally owned immutable packages from a validated
ResourceSet. Its optional added package enters by value and receives ordinary checks.
Use the existing explicit context capabilities and large-command admission before
loading versioned selections or authoring fonts. Apply derives one final command 0.8
from the accepted theme, even after several local edits. Selecting another base theme
must be committed before changing its fonts when the final artifact cannot be derived
from the accepted source. Do not bypass this with rewritten request pins.

After ordinary preflight/configure/build run
`ctest --preset <profile> -R '^editor[.]THEME-HISTORY-' --output-on-failure`, affected
editor/settings/configuration/protocol/component tests and the full portable suite.
In the existing non-root Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-HISTORY|THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM)$' --output-on-failure`.
The new native test emits requests from the actual EditorDraft, publishes through
ConfigProbe, independently compares files/bytes, and verifies fresh reload and a
lost-result reconciliation. It does not instantiate font controls. The
[handoff](../../spec/delivery/theme-history-handoff.md) preserves failures and evidence.


The [native font-controls package](../../spec/delivery/packages/w-10-theme-controls.md)
adds the scene-wide Fonts modal to the Linux EditorForm. `theme_control_input` and
`theme_control_edit` preserve exact no-ops and distinguish inherited roles from an
explicit empty map. Set authors one atomic draft edit; Apply publishes command 0.8.
Use settings theme restores scene inheritance and ignores uncommitted private input.
Each role retains its raw private values while switching targets; inactive roles do
not invalidate Set. Private buffers, models and snapshots erase on every close,
policy, disconnection, topology and reload boundary.

Preview, content choices and widget creation borrow the draft's matching resources.
SceneSurface owns a validated snapshot sharing immutable package allocations.
EditorForm retains capability admission, not a second original catalog. Font-only
changes resolve new intrinsic metrics in the queued native paint, avoiding a duplicate
immediate render before private-erasure observations. Existing geometry-edit paths
retain immediate resolution. Display permission remains distinct from theme.edit.

After workspace preflight/configure/build, run
`ctest --preset <profile> -R '^editor[.]THEME-CONTROLS-' --output-on-failure`, the
affected editor/settings/configuration/protocol/component families and full portable
suite. In the existing non-root Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-FONTS|EDITOR-VISIBILITY|EDITOR-CONTENT-PROPERTIES|EDITOR-WIDGET-CREATION|THEME-HISTORY|THEME-COMMANDS|ROLE-COMPOSITION|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM)$' --output-on-failure`.
The 19 font cases operate native controls, compare literal independent TextProbe
requests with observed canvas pixels, inspect every selected package byte and reopen
the committed store. Held text objects are positively identified before the stimulus;
independent explicit GetText replies are dispatched together within one 200-ms bound.
Timeouts and unavailable replies cannot count as erasure. The
[handoff](../../spec/delivery/theme-controls-handoff.md) records failures and corrections.


The [scene-fragment package](../../spec/delivery/packages/w-10-scene-fragments.md)
adds `EditorDraft::copy_selection`, `clipboard_data`, `clear_clipboard` and typed
`PasteWidgets`. A trusted resource context must admit `editor.clipboard`, and
current authenticated desktop/console policy must explicitly permit sensitive
clipboard disclosure. Default editor construction remains disabled. Each byte
borrow rechecks permission and expires at the next operation. Clear native ownership
when the draft clears its snapshot; never clear a foreign application's selection.

Fragments include authored selected subtrees, with exact bindings, image pins and
opaque extensions. They exclude scene metadata, settings, packages and live values.
Paste supplies a complete fresh-ID map, destination group/root and index. Coordinates
stay parent-local; the destination theme and admitted resource closure remain in
force. Missing pins reject atomically. Scene 0.3..0.5 promotion requires the existing
capabilities; there is no implicit scene 0.2 migration. Apply uses existing commands.

After workspace preflight/configure/build, run `ctest --preset <profile> -R
'^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure` and the full portable suite. The Linux regression command is
`ctest --preset linux-x64-gcc13 -R '^native[.](EDITOR-FONTS|EDITOR-VISIBILITY|EDITOR-FORM|THEME-HISTORY)$'
--output-on-failure` in the owned non-root laboratory. Frozen complete examples are
`tests/editor/scene-fragment-cases.json`. Native clipboard transfer is a separate
required adapter boundary: byte limits must be enforced before unbounded allocation,
and outgoing chunks need fresh permission checks. These shared tests do not enable
OS clipboard controls or qualify a complete edition.


## Bounded native scene clipboard

The [package](../../spec/delivery/packages/w-10-native-clipboard.md) connects the
shared draft to `source/platform/linux/scene_clipboard_x11.*`. The GTK3/X11 adapter
owns a separate X connection integrated with GLib. Outgoing borrows reauthorize the
current draft for every chunk and must throw on denial; views never outlive their
callback. The adapter retains no second outgoing payload. Incoming direct and INCR
reads are bounded before allocation. One incoming/eight outgoing transfers use
262144-byte payload, 16384-byte chunk, one-second idle and five-second total limits.
Cancelling a paste destroys its unique receiver; old replies cannot reach a new draft.

EditorForm requires explicit trusted `editor.clipboard` capability, current sensitive
clipboard disclosure and an X11 display. Other backends remain unavailable. Copy/Paste
and Cancel paste use the existing draft/history and durable Apply pipeline. Pending
paste prevents draft edits and submission. Clipboard protocol metadata cannot overwrite
an active transfer property. No generic text, PRIMARY or clipboard-manager persistence
is exported. Existing private text handling is unchanged.

After the normal workspace preflight/configure/build, run `ctest --preset
linux-x64-gcc13 -R '^native[.]EDITOR-CLIPBOARD$' --output-on-failure`. The independent
Xlib peer runs alongside native input/accessibility in private Xvfb/D-Bus laboratories.
It compares exact frozen fragments/scenes and stored resources, including a deliberately
wrong scene witness, and exercises malformed/oversized payloads, cancellation, late
replies, ownership, per-chunk revocation, slot limits and deadlines. The observer must
allow the specified five-second deadline before judging a transfer incomplete.

Run all portable suites and native EDITOR-FORM, EDITOR-CONTENT-PROPERTIES,
EDITOR-VISIBILITY, EDITOR-FONTS and THEME-HISTORY regressions. Raw attempts, source
archives and native recordings stay in ignored `out/evidence/`; the compact
[checkpoint](../../spec/delivery/checkpoints/native-clipboard.json) preserves source
and artifact identities. Two pre-existing GTK shutdown warning families remain
explicitly recorded; unknown critical diagnostics fail the clipboard oracle. This
development checkpoint does not qualify an installed edition or another native backend.
