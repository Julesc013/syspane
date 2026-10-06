# SysPane implementation checklist

The October 2026 audit is incorporated into the specification and documentation.
The model/build foundation is implemented on Windows and Linux development
profiles; **the native desktop application and release qualification remain pending**.
This checklist routes work; the
[work-unit catalog](spec/delivery/work-units.json) owns dependencies and acceptance.

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
- [ ] W-05 GNOME continuation: qualify multiple windows, modal/workspace/session changes and alternate reveal triggers before enabling focus integration generally; qualify wallpaper policy, actual session-manager supervision and product renderer/collector continuity before qualifying a host. Other native taskbar/input/image profiles remain unqualified.
- [ ] W-02 completion: qualify usable desktop composition, shell recovery and wallpaper policy, additional platform reveal/input scenarios and Windows external capture in an admitted synthetic desktop.
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
