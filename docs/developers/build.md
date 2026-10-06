# Developer setup and checks

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
`python build-support/check_workspace_budget.py --action build` (select `test` or
`package` as appropriate); require exit zero. Run it afterward with `--action inspect`.
The combined checkout/native-Linux allocation is 2 GiB with growth reservations;
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
`build-support/record_protocol.py --preservation --profile <profile> --build-dir
<build> --output <record>`. Historical recording accepts `--preservation` for the
portable predicate only; its file/UI adapters stay disabled.

The repository builds the C++17 model, portable protocol/configuration libraries
and a deterministic development smoke program. A usable desktop application
remains pending. Use the pinned tools in
[the development profiles](../../build-support/targets/README.md). From the repository
root on Windows:

```powershell
cmake --preset windows-x64-gcc15
cmake --build --preset windows-x64-gcc15
ctest --preset windows-x64-gcc15 --output-on-failure
out/build/windows-x64-gcc15/SysPane.ModelSmoke.exe
```

The Linux preset uses an unprivileged account and a native cache directory for
build products. The same source checkout and expectations are used. From the
repository root in the admitted Ubuntu environment, `sh build-support/run_foundation.sh`
runs the documented configure/build/test/package commands. Individual `configure`,
`build`, `test` and `package` arguments are available. The wrapper sets the bounded
cache root; it does not install dependencies or require root.

Create a local Windows smoke archive and check relocation with:

```powershell
python build-support/package_smoke.py --profile windows-x64-gcc15 --build-dir out/build/windows-x64-gcc15
```

The W-24 checkpoint ran 37 CTest entries: the original 18 model/smoke/component checks,
17 portable protocol/policy checks and two native IPC families. Run portable cases with
`ctest --preset windows-x64-gcc15 -R '^protocol\.' --output-on-failure`.
The original W-01 results remain historical; W-24 case/artifact records are
`build-support/evidence/w-24-native-<profile>.json`. The two native families contain
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
[Dependency identities](../../build-support/dependencies.json) pin the header and
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
Portable checkpoint records are `build-support/evidence/w-25-portable-<profile>.json`.

The [W-25 package](../../spec/delivery/packages/w-25-recovery.md) defines the time,
ownership, expiry and restart boundaries. Guard objects are single-owner and cannot
be copied/moved. Their time inputs are local invocation times; views do not sample
a clock. The caller must advance time and apply current policy before presentation.
`build-support/record_protocol.py --recovery --profile <profile> --build-dir <build>
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

Supervision checkpoint records are `build-support/evidence/w-25-supervision-<profile>.json`.
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
in `build-support/check_diagnostic_dependencies.py`. It installs nothing. GTK is
dynamically linked; the report skips toolkit initialization but still needs its
installed loader dependencies. The measured native close test uses owned authenticated Xvfb/X11;
Wayland and full transitive packaging remain unqualified.

The policy reader has fixed protected system locations and no path/environment
override. Tests do not write HKLM or `/etc`. Positive protected-policy deployment
and native revocation qualification need an admitted administrative lab. Portable
fixtures test parsing/projection semantics, not policy provenance. Diagnostic
preservation, recent-failure metadata and recovery actions remain pending.

Diagnostic checkpoint records are `build-support/evidence/w-25-diagnostic-<profile>.json`.
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
`build-support/evidence/w-02-oracle-<profile>.json`; see the
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
python3 build-support/prepare_x11_lab.py <build> --refresh-metadata
python3 tests/desktop/native_x11_host.py <build>
python3 tests/desktop/native_x11_host.py <build> --wallpaper-mode color
python3 tests/desktop/native_x11_host.py <build> --delayed-wallpaper --icon-input
python3 tests/desktop/native_x11_host.py <build> --wallpaper-mode color --restart-window-manager
python3 tests/desktop/native_x11_host.py <build> --delayed-wallpaper --restart-window-manager
```

Preparation downloads only the exact archives in `build-support/x11-lab-packages.json`
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
runtime against `build-support/x11-input-runtime.json`, starts an owned accessibility
registry and observes native pointer/keyboard routing through exact private clipboard
URIs, AT-SPI, focus and root pixels. It never uses the user's clipboard or desktop.
Missing/mismatched optional runtime is a lab limitation, not an installation request.

Use `python3 build-support/record_x11_host.py --build-dir <build>
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
The optional runtime is pinned in `build-support/x11-recovery-runtime.json`.
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
python3 build-support/prepare_gnome_lab.py <owned-build-directory>
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory>
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker --marker-control hidden
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --marker --marker-control frozen
python3 build-support/record_gnome_host.py --build-dir <owned-build-directory> --reports <live-report> <hidden-report> <frozen-report> --output <new-owned-record>
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
python3 build-support/record_gnome_composition.py --build-dir <owned-build-directory> --reports <live-report> <above-report> <below-report> --output <new-owned-record>
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
python3 build-support/record_gnome_reveal.py --build-dir <owned-build-directory> --reports <live-report> <no-action-report> <blank-report> --output <new-owned-record>
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
python3 build-support/record_gnome_focus.py --build-dir <owned-build-directory> --reports <nine-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_focus_trace.py --build-dir <owned-build-directory> --reports <six-paired-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_input.py --build-dir <owned-build-directory> --reports <three-input-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_wallpaper.py --build-dir <owned-build-directory> --reports <four-wallpaper-reports> --output <new-owned-record>
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

For the historical shared-subset experiment, the existing Visual Studio 2017 XP
toolset has its own preset. It compiles the same model, protocol/policy, recovery
and diagnostic projection sources; modern native adapters require separate closure.

```powershell
cmake --preset windows-x86-v141-xp
cmake --build --preset windows-x86-v141-xp
ctest --preset windows-x86-v141-xp --output-on-failure
python build-support/package_smoke.py --profile windows-x86-v141-xp --build-dir out/build/windows-x86-v141-xp
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

Collect current full runs with `build-support/record_protocol.py --failure-metadata
--profile <profile> --build-dir <build> --output <record>`. That flag includes all
existing native/oracle regression families and requires the new concrete records.
For the historical build, use `record_legacy_build.py --failure-metadata` with its
existing build/smoke/output arguments. Records retain source/artifact identities,
raw failures and explicitly unexecuted Windows symlink qualification.

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
