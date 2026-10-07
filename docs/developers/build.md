# Developer setup and checks

The [image pipeline package](../../spec/delivery/packages/w-09-image-pipeline.md)
adds shared premultiplied bilinear fit/orientation and the Linux
`SysPane.ImageWorker` / `rendering::ImageJob` boundary. The worker accepts PNG,
JPEG and the declared static SVG profile from bounded bytes. Its installed codec,
loader, relevant header and kernel identities are in `build-support/image-runtime.json`.
Linux requires Landlock ABI >= 3, seccomp and the pinned runtime; startup fails
when containment cannot be installed. No privileged installation is involved.

Supply ImageJob an admitted canonical worker ELF, declared media type and immutable
encoded bytes. Poll without waiting; cancellation suppresses take immediately but
the owner must retain the job until actual stop is observed. The worker receives
no image path or base URI. The job binds the original input SHA256, limits IPC
and accepts output only after successful exit and reaping. This low-level API
does not grant disclosure permission. SceneSurface still rejects image widgets
until an asynchronous scene/policy owner and external erasure oracle are integrated.

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
The renderer consumes text bodies, column labels and scene 0.3 chart content;
images and legacy charts still select the explicit unsupported whole-scene alternative.

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
AT-SPI/ATK/observer identities are checked against `build-support/surface-runtime.json`.
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
libraries, fonts and font configuration against `build-support/text-runtime.json`.
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
`python build-support/check_workspace_budget.py --action build` (select `test` or
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

The application-list experiment observes GNOME's actual Alt+Tab popup and overview
running-app dash, using two private normal applications and their native icons:

```text
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher live
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher ordinary-window
python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory> --switcher no-switcher
python3 build-support/record_gnome_switcher.py --build-dir <owned-build-directory> --reports <three-switcher-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_icon_recovery.py --build-dir <owned-build-directory> --reports <three-recovery-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_shell_recovery.py --build-dir <owned-build-directory> --reports <three-shell-recovery-reports> --output <new-owned-record>
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
python3 build-support/record_gnome_focus_integration.py --build-dir <owned-build-directory> --reports <observe-report> <restore-report> --output <new-owned-record>
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
python3 build-support/record_gnome_focus_scenarios.py --build-dir <owned-build-directory> --reports <restore-report> <observe-report> <helper-exit-report> --output <new-owned-record>
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

The [native wallpaper-policy checkpoint](../../spec/delivery/gnome-wallpaper-policy-handoff.md)
uses the private dconf backend only under `--wallpaper-policy`. Prepare its pinned
CLI with `python3 build-support/prepare_gnome_policy.py <owned-linux-build>` after
a successful Windows coordinator `--action package` preflight. No packages are
installed. After a `--action test` preflight before each invocation, run:

```sh
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy locked
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy unlocked
python3 tests/desktop/native_gnome_bootstrap.py <owned-linux-build> --wallpaper-policy replace-policy
```

The locked mode returns 0; the two completed negative controls return 1. Use the
three exact emitted report paths with `build-support/record_gnome_wallpaper_policy.py
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
python3 build-support/record_gnome_surface_lease.py --build-dir <owned-linux-build> --reports <live-report> <ignore-expiry-report> <disconnect-report> --output <new-owned-record>
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
python3 build-support/record_gnome_network_cache.py --build-dir <owned-linux-build> --reports <live> <ignore-clear> <wrong-value> <owner-loss> --output <new-owned-record>
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

`build-support/record_gnome_live_network.py --build-dir "$BUILD" --output
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

`build-support/record_gnome_render_watch.py --build-dir "$BUILD" --output
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

Run `build-support/record_gnome_controller_recovery.py --build-dir "$BUILD"
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

Revalidate an existing report with `python3 build-support/record_editor_exit.py
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
`build-support/evidence/`, in addition to the existing measured-controller build pin.

Use `build-support/record_gnome_editor_exit.py --build-dir "$BUILD" --output
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
