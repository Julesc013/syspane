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
- [ ] W-25 completion: add bounded recent-failure metadata, explicit configuration preservation, telemetry/renderer recovery, policy-driven payload erasure and native editor-exit/visible recovery. Qualify installed protected policy in an admitted lab.
- [x] W-02 initial boundary: decode external marker pixels and temporal coverage; calibrate against live, disappearing, frozen, obstructed and capture-gap cases on an owned X11 test server. See the [handoff](spec/delivery/oracle-handoff.md).
- [ ] W-02 completion: add named reveal-action, icon-input/focus and real wallpaper adapters, including Windows external capture in an admitted synthetic desktop.
- [ ] W-03–W-06: run changing-scene host probes for contemporary Windows, XP/7, Linux and macOS/older OS X.
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
