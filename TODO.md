# SysPane implementation checklist

The October 2026 audit is incorporated into the specification and documentation.
The model/build foundation is implemented on Windows and Linux development
profiles; **the native desktop application and release qualification remain pending**.
This checklist routes work; the
[work-unit catalog](spec/delivery/work-units.json) owns dependencies and acceptance.

The user-expanded [0.1.0 release scope](spec/delivery/release-0.1.0.md) now requires
Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X. Finish the full native desktop
editions and their release gates; foundation experiments alone cannot complete this goal.

## Completed specification work

- [x] Preserve the native architecture, one `source/` tree and Windows controller/surface isolation.
- [x] Add the product README and user, operator and developer documentation.
- [x] Define configuration precedence, policy, persistence and recovery contracts.
- [x] Expand and validate the initial setting descriptors and generated constraints.
- [x] Add experimental portable scene/binding/layout contracts and retain 0.1 fixtures.
- [x] Define saver roles, target identity, binary names, installation ownership and maintenance gates.
- [x] Separate native profile delivery and trace audit recommendations to contracts and work.
- [x] Define work-package gates, a detailed W-01 foundation package and concrete model/request/recovery acceptance traces.

These checks mean documentation/contract work is present, not that its runtime
behaviour has been implemented. See [audit disposition](spec/delivery/audit-2026-10-04.md).

## First native campaign

- [x] W-07 controller demand component: merge authorized field/entity/age/priority/recording leases, apply cadence/concurrency policy, age priorities and retain cancelled slots until confirmed stop. See the [handoff](spec/delivery/demand-owner-handoff.md).
- [x] W-07/W-25 Linux demand integration: real bounded acquisition outside the IPC loop, native join before slot release, rejected late results and policy revocation while a worker remains alive. See the [handoff](spec/delivery/demand-executor-handoff.md).
- [x] W-07/W-25 session demand adapter: bind controller-selected requests to authenticated roles, exact heartbeat/expiry rules and current policy; preserve independent leases and held native jobs. See the [handoff](spec/delivery/session-demand-handoff.md).
- [ ] W-07/W-25: finish general consumer wire selection, invalidation/coalescing and installed policy/controller ownership; connect common scene commands and persistence into the native vertical.
- [x] W-08 authored-state prerequisite: validate scene/settings contracts, prepare atomic mixed edits, enforce current policy/revision/replay and test Linux generation recovery at native interruption points. See the [handoff](spec/delivery/authored-transactions-handoff.md).
- [x] W-08 asynchronous command prerequisite: one bounded ledger, reserved replies, current-policy result retrieval, cancellation at the commit permit, worker-stop ownership and same-epoch reconnect; exercise real Linux IPC/storage. See the [handoff](spec/delivery/command-sessions-handoff.md).
- [x] W-08 reconciliation prerequisite: versioned read-only lookup of original-epoch committed identities, current-policy disclosure, bounded receipt ownership and six native crash/restart cases. See the [handoff](spec/delivery/reconciliation-handoff.md).
- [x] W-08 Linux supervision prerequisite: independent absolute transaction deadlines, confirmed controller exit before replacement, supervisor-loss handling and bounded restart circuit. See the [handoff](spec/delivery/transaction-supervision-handoff.md).
- [ ] W-08 product integration: installed store/controller ownership, activation, undo/external-edit handling and non-Linux storage/supervision qualification; connect native editor/settings controls.
- [x] W-08 content preview prerequisite: verify pinned manifests/documents/assets, resolve bounded preset inheritance, preserve provenance and enforce current policy; exercise the private Linux directory reader. See the [handoff](spec/delivery/content-resolution-handoff.md).
- [ ] W-08 resource integration: implement admitted media preparation and connect native settings and activation; retain archive import, layer resets, three-way updates and non-Linux resource storage as explicit gates.
- [x] W-08 supervised content prerequisite: authenticated command 0.3, private catalog discovery, retained edits after import loss/restart and independent interruption/cancellation/policy cases. See the [handoff](spec/delivery/native-content-handoff.md).
- [x] W-08 durable resource prerequisite: bind content selection to command identity, persist exact package bytes and verify complete Linux generation recovery through interrupted writes and corrupt resources. See the [handoff](spec/delivery/resource-generations-handoff.md).
- [x] W-25 consumer continuity: preserve real collection and original measurements across bounded native consumer replacement; verify typed consumer revocation and circuit opening. See the [handoff](spec/delivery/consumer-continuity-handoff.md).
- [x] W-25 owned GNOME controller: preserve collection during automatic shell replacement and full-state reattachment; verify current operational pixels after native overview dismissal, with disabled-attachment and revoked-permission controls. See the [handoff](spec/delivery/gnome-controller-recovery-handoff.md).
- [x] W-25 independent render recovery: connect render/health expiry to the persistent native replacement owner; recover drawing and frozen-shell cases, reject false progress and enforce current typed revocation. See the [handoff](spec/delivery/controller-render-recovery-handoff.md).
- [x] W-25 owned X11 editor lifetime: independent keyboard/GTK exit, held child termination, parent-loss cleanup and restored pixels/input; preserve failed attempts. See the [handoff](spec/delivery/editor-exit-handoff.md).
- [x] W-25 owned GNOME editor lifetime: recover actual icon input and original measured pixels through independent keyboard/button exit and owner loss, including a frozen controller; calibrate unavailable recovery. See the [handoff](spec/delivery/gnome-editor-exit-handoff.md).
- [ ] W-25 integration: close installed controller/session/policy/demand ownership and connect actual scene transactions. Fullscreen discovery and overview-free unattended recovery remain unqualified.
- [x] W-00/W-01: admit runtime scope; create real CMake targets, component ownership and pinned Windows/Linux development profiles.
- [x] W-01: bind mandatory model cases to runnable tests and deliver a nonempty fixture smoke program; see the [handoff](spec/delivery/foundation-handoff.md).
- [x] W-24 portable slice: close and test framing, negotiation, request reservations, settings preview, policy/disclosure, queues and connection states; see the [package](spec/delivery/packages/w-24-transport.md).
- [x] W-24 native slice: implement OS peer authentication and bounded stream I/O; 37 CTest entries pass per Windows/Linux profile, with cross-user/logon qualification still blocked. See the [native handoff](spec/delivery/native-transport-handoff.md).
- [x] W-25 portable boundary: implement producer leases, render-progress challenges and bounded restart/quarantine decisions; see the [package](spec/delivery/packages/w-25-recovery.md).
- [x] W-25 native supervision: confirm owned-child lifetime, health expiry, render-worker stalls, restart/circuit behavior and parent-loss cleanup on Windows/Linux; see the [handoff](spec/delivery/supervision-handoff.md).
- [x] W-25 diagnostic entry: build independent JSON reporting and Win32/GTK inspectors with bounded policy decoding, protected-source readers and native close checks; see the [handoff](spec/delivery/diagnostic-handoff.md).
- [x] W-25 recent-failure boundary: record bounded native fault metadata, reject unsafe/malformed file inputs and enforce current diagnostic disclosure; see the [checkpoint](spec/delivery/failure-metadata-handoff.md).
- [x] W-25 preservation boundary: implement private opaque copies, current-policy cancellation, exclusive publication and native controls; see the [checkpoint](spec/delivery/preservation-handoff.md).
- [x] W-25 data owner: join model validation, full resynchronization, producer leases and revocable presentation; see the [typed component checkpoint](spec/delivery/data-view-handoff.md).
- [x] W-25 telemetry documents: decode versioned messages with bound identity/revision, resource limits and exact replay bytes; see the [checkpoint](spec/delivery/telemetry-wire-handoff.md).
- [x] W-25 state import: publish complete wire-bound remote state with preserved metadata, retention, replay and revocable lifetime; see the [checkpoint](spec/delivery/state-import-handoff.md).
- [x] W-25 subscription experiment: connect bounded demand, policy-bound queues and state import across authenticated native processes; see the [checkpoint](spec/delivery/subscriptions-handoff.md).
- [x] W-25 native clock investigation: verify causal time brackets and held-peer exit rejection on Windows/Linux; see the [checkpoint](spec/delivery/measurement-clock-handoff.md). Suspend and namespace mismatch qualification remain open.
- [x] W-25 measured-time boundary: version measurement documents, preserve clock scope/age through replay and reconnect, and exercise native fresh/delayed/future delivery; see the [checkpoint](spec/delivery/measured-time-handoff.md).
- [x] W-25 native acquisition prerequisite: read real Windows/Linux interface counters with bounded results and independent OS brackets; see the [checkpoint](spec/delivery/network-acquisition-handoff.md).
- [x] W-25 reconciliation prerequisite: preserve interface lifetimes, reject obsolete/dirty results, retain failure timestamps and derive exact counter intervals; hold a Linux link subscription across acquisition. See the [checkpoint](spec/delivery/network-reconciliation-handoff.md).
- [x] W-25 Linux collector experiment: connect real counters/rates to measured publication, retained failure/replay and independent child recovery; prove demand/watch release and parent-loss exit. See the [checkpoint](spec/delivery/network-publication-handoff.md).
- [x] W-25 native surface lease: observe independent expiry and actual producer exit, retain public marker identity/pixels, require a replacement full snapshot and remove callbacks on disable; reject the ignored-expiry control. See the [checkpoint](spec/delivery/gnome-surface-lease-handoff.md).
- [x] W-25 shared network presentation: select an exact producer/epoch/entity, preserve four measured fields and status axes, format exact bounded text and reject revoked/invalid payloads atomically; compare real collector output and explicit stale retention after exit. See the [checkpoint](spec/delivery/network-presentation-handoff.md).
- [x] W-25 native retained-cache experiment: admit a held relay, display actual shared C++ network projections as retained samples, reject stale policy/replay and independently verify digits plus revocation/owner-loss clearing. Preserve wrong-value and ignored-clear controls; see the [checkpoint](spec/delivery/native-network-cache-handoff.md).
- [x] W-25 standalone native GJS clock: reuse authenticated Linux measurement-clock checks through a native object, preserve exact strings, reject invalid sockets and peer exit, and release owned resources. See the [checkpoint](spec/delivery/gjs-clock-handoff.md).
- [x] W-25 owned GNOME clock: asynchronously attach an authenticated same-session peer; independently verify public-sample age/expiry, wrong-peer rejection, native exit and disable during startup. See the [checkpoint](spec/delivery/gnome-clock-handoff.md).
- [x] W-25 native GJS network consumer: reuse measured DataView/projection, preserve exact values and status metadata, enforce deadlines and policy erasure, and test replay, lease and native resource lifetime with standalone synthetic inputs. See the [checkpoint](spec/delivery/gjs-network-view-handoff.md).
- [x] W-25 live native session: forward original real collector frames to the asynchronous GJS owner, preserve native clock provenance and metadata, and test independent data-lease loss, source hang, typed revocation and parent death. See the [checkpoint](spec/delivery/live-network-session-handoff.md).
- [x] W-25 measured GNOME tile: independently decode real counter/rate and age/status pixels; distinguish sample freshness from data-lease expiry; prove typed erasure and native exit, with four failing drawing controls. See the [checkpoint](spec/delivery/gnome-live-network-handoff.md).
- [x] W-25 finite real-rendering supervision: connect independent native challenges to measured GNOME drawing/paint, expose false progress through pixels, detect stopped drawing and watcher/shell faults, and retain queued-message deadline and native-exit failures. See the [checkpoint](spec/delivery/gnome-render-watch-handoff.md).
- [ ] W-25 renderer recovery: admit bounded automatic replacement only after confirmed old exit; restore a current-policy full snapshot and prove visible recovery independently. Complete editor-exit recovery and general product queues.
- [ ] W-25: integrate the tested source/data boundary into product demand/policy and renderer recovery; qualify Windows notification coverage and actual native topology/namespace faults.
- [ ] W-25 completion: close real native acquisition contracts and connect collectors/renderers; finish product demand/policy distribution; qualify native suspend/namespace and installed policy/foreign-owner/unsupported-filesystem cases; add product failure-log retention, telemetry/renderer recovery, policy-driven payload erasure and native editor-exit/visible recovery. Qualify installed protected policy in an admitted lab.
- [x] W-02 initial boundary: decode external marker pixels and temporal coverage; calibrate against live, disappearing, frozen, obstructed and capture-gap cases on an owned X11 test server. See the [handoff](spec/delivery/oracle-handoff.md).
- [x] W-02/W-05 initial X11 investigation: drive Openbox Show Desktop under real PCManFM, observe temporal pixels and icon concealment, preserve file-wallpaper startup failures. See the [handoff](spec/delivery/x11-host-handoff.md); no candidate qualifies as a wall.
- [x] W-02/W-05 scoped input/image adapter: observe native selection, drag, menu and folder opening on the hidden X11 candidate, verify delayed image setup against fixture pixels, and retain the visible candidate's input failure. See the [checkpoint](spec/delivery/x11-input-handoff.md).
- [x] W-02/W-05 owned Openbox restart: prove held-process exit, replacement ownership, continuing marker progress and unchanged wallpaper while preserving failed visible recovery. See the [checkpoint](spec/delivery/x11-recovery-handoff.md).
- [x] W-02/W-05 GNOME prerequisite: bootstrap pinned GNOME 46 on an owned display and observe live/hidden/frozen shell-bridge markers with the unchanged external oracle. Preserve failed attempts and source archives; see the [checkpoint](spec/delivery/gnome-marker-handoff.md).
- [x] W-05 GNOME solid-color composition: calibrate separate marker/opaque-icon/transparent-pixel witnesses, enable real DING, and reject above-icons/below-wallpaper controls; preserve original fixture/control defects. See the [checkpoint](spec/delivery/gnome-composition-handoff.md).
- [x] W-05 GNOME reveal experiment: observe configured native Super+D, live composition and visible foreground hide/restore; reject omitted actions and temporary disappearance. Preserve the failed foreground-focus restoration. See the [checkpoint](spec/delivery/gnome-reveal-handoff.md).
- [x] W-05 GNOME focus baseline: repeat shell-only, DING-only and candidate native reveal three times each, observe actual keyboard delivery, and preserve the focus failure without attributing it to the bridge. See the [checkpoint](spec/delivery/gnome-focus-handoff.md).
- [x] W-05 GNOME native decision: bind built-in Mutter MRU-selection logs to independent focus/keyboard observations and verify traced/untraced pairs. See the [checkpoint](spec/delivery/gnome-focus-trace-handoff.md).
- [x] W-05 GNOME icon input: observe real selection, clear, drag selection, menus, folder contents/open/close and restoration, with pointer-blocking and omitted-click controls. See the [named laboratory checkpoint](spec/delivery/gnome-input-handoff.md).
- [x] W-05 GNOME image wallpaper: preserve original file identity, complete native settings and exact image pixels; independently reject same-pixel file replacement, URI redirection and visual obstruction. See the [named PNG checkpoint](spec/delivery/gnome-wallpaper-handoff.md).
- [x] W-05 GNOME application lists: observe actual Alt+Tab and overview dash entries, rendered icons, native application switching and restored focus; reject an added normal window and omitted popup. See the [named shell checkpoint](spec/delivery/gnome-switcher-handoff.md).
- [x] W-05 GNOME icon-manager recovery: confirm exact owned DING exit and native replacement, continuing marker/icon composition and input bound to the replacement; reject frozen drawing and omitted stop. See the [checkpoint](spec/delivery/gnome-icon-recovery-handoff.md).
- [x] W-05 owned GNOME shell/compositor recovery: prove exact shell exit, native replacement, bridge reattachment and input on the new desktop, with omitted-reattachment and omitted-restart controls. See the [checkpoint](spec/delivery/gnome-shell-recovery-handoff.md).
- [x] W-05 optional GNOME focus integration: pass the original focus/keyboard oracle and native icon, folder, minimization and disable guards; preserve the observation control and default failure. See the [checkpoint](spec/delivery/gnome-focus-integration-handoff.md).
- [x] W-05 GNOME focus scenarios: verify two selected normal windows, modal redirection, closed targets and workspace invalidation with actual key receipt; calibrate helper-startup failure. See the [checkpoint](spec/delivery/gnome-focus-scenarios-handoff.md).
- [x] W-05 GNOME wallpaper policy: preserve native dconf locks and policy identity during live composition; reject unlocked settings and identical-byte policy replacement. See the [checkpoint](spec/delivery/gnome-wallpaper-policy-handoff.md).
- [ ] W-05 GNOME continuation: qualify moved windows, broader application/modal cases, lock/session changes and alternate reveal triggers before enabling focus integration generally; qualify protected deployment, locked-image wallpaper, live policy changes, actual session-manager supervision and product renderer/collector continuity before qualifying a host. Other native taskbar/input/image profiles remain unqualified.
- [ ] W-02 completion: qualify usable desktop composition, shell recovery and wallpaper policy, additional platform reveal/input scenarios and Windows external capture in an admitted synthetic desktop.
- [x] W-03 initial observation: bind native Explorer ownership and two bounded icon-hierarchy observations; pass 14 structural decision tests. See the [checkpoint](spec/delivery/windows-host-inventory-handoff.md). No native host is qualified.
- [ ] W-03 native experiment: designate and verify a synthetic Windows lab, then close and run attachment, external pixels, Win+D/reveal, icon input, wallpaper and controlled shell recovery.
- [ ] W-03–W-06: run changing-scene host probes for contemporary Windows, XP/7, Linux and macOS/older OS X.
- [x] W-04 build experiment: pin the installed v141_xp toolset, compile the existing shared subset, pass 51 host checks and relocate its smoke archive. See the [checkpoint](spec/delivery/historical-build-handoff.md).
- [ ] W-04 runtime/host gate: establish guest test scope and usability, run the exact binaries on XP/7, then qualify actual native host behavior independently.
- [ ] W-07–W-11: implement demand, commands, configuration recovery, portable scenes, editor and native settings facilities.
- [x] W-26 initial slice: produce local Windows/Linux model smoke archives and prove relocated execution; product package/lifecycle qualification remains pending.
- [ ] W-34–W-37: implement native network providers independently for each family.
- [ ] W-27–W-30: complete each profile's live editable persistent desktop, save/reload and failure journey.
- [ ] W-40–W-43: qualify each selected payload's accessibility, privacy, performance and recovery.
- [ ] W-48: verify document conformance across independent native implementations.
- [ ] Run the admitted [cold-start exercise](spec/assurance/acceptance-traces.md#cold-start-exercise) and classify consequential assumptions before claiming repository-only implementation closure.

One blocked native lab does not block another profile's honestly scoped preview.
W-12/W-13/W-20/W-21 are aggregate tracking milestones, not prerequisite joins for
the independent units. Scope every execution and support claim to an exact profile.

## Feature gates

- [ ] W-14–W-16: add resource, storage/device and bounded history/replay implementations with descriptor semantics.
- [ ] W-31: qualify saver preview, full-screen and configuration roles, disclosure, power and desktop coexistence.
- [ ] W-33: implement preset inheritance/updates, bounded package import, copy-on-migrate and downgrade reporting.
- [ ] W-09/W-33: version richer theme tokens and a bounded expression AST before enabling them.
- [ ] W-19: implement provider admission and the SDK; prove result-buffer retrieval and independent C/C++ consumers before ABI stability.
- [ ] W-18/W-23: admit optional workshop providers and additional native historical profiles individually.
- [ ] W-22: inspect and bind actual AIDE contracts, workspace/evidence ownership and explicit grants; binding remains inactive.

## Distribution and owner decisions

- [ ] Populate a finite release scope with exact profiles, capabilities, document versions, packages, mandatory tests and explicit deferrals.
- [ ] W-38: choose code/docs/assets licensing, contribution/IP terms, security intake and supported-release ownership.
- [ ] W-26/W-32: instantiate component, release and setup manifests from real build closure and inspected provider contracts.
- [ ] W-32: pin USK source/artifact/SDK and qualify each enabled operation/profile; keep normal startup independent.
- [ ] W-32: prove ownership, offline repair, interruption, upgrade/rollback and uninstall while preserving user/shared/foreign data.
- [ ] W-44–W-47: package each qualified payload; retain unsigned reproduction and signing transformation provenance separately.
- [ ] W-39: qualify metadata trust, key rotation/revocation, expiry and rollback/freeze handling before automatic updating.
- [ ] W-19/W-33: choose controlled public contract identifiers and migration aliases before a stable SDK.

[Readiness gates](spec/delivery/implementation-readiness.md),
[open questions](spec/delivery/open-questions.md) and
[current state](spec/delivery/current-state.md) distinguish pending implementation,
missing native evidence and decisions that cannot be inferred from the audits.
