# SysPane — System Panel

A native operational desktop for seeing host identity, network connections,
resources and connected devices at a glance, without replacing your wallpaper.

SysPane is designed around a persistent passive desktop surface, a native
inspector and settings application, and direct desktop editing. GUI, editor,
CLI and local automation share the same validated operations. Portable scenes,
themes and presets describe user intent; native adapters supply each platform's
data, controls and desktop integration. A companion screensaver reuses the
presentation components under its own lifecycle and privacy policy.

The [campaign coverage audit](spec/delivery/campaign-coverage.md) maps implemented
foundations and outstanding native gates. A [Windows observer](spec/delivery/windows-host-inventory-handoff.md)
now records Explorer ownership and icon hierarchy; actual Windows desktop tests
await a designated synthetic lab.

**Current stage: foundation implementation.** The C++17 model, explicit CMake
targets and development smoke program build on pinned Windows and Linux profiles.
Portable framing, request replay, settings-preview policy and connection handling
now run over tested Windows/Linux local IPC adapters. Portable producer-lease,
render-progress and restart-budget guards now supervise real isolated test workers
on both profiles. An independent diagnostic executable now provides a public JSON
report and conservative Win32/GTK inspector with mandatory-policy checks.
Explicit recent-failure reporting now uses bounded private files and current
operational disclosure policy; see the [checkpoint](spec/delivery/failure-metadata-handoff.md).
The diagnostic now offers explicit private file preservation through native controls
and CLI; see the [preservation checkpoint](spec/delivery/preservation-handoff.md).
A [synchronized data view](spec/delivery/data-view-handoff.md) now joins model
validation, producer leases and policy-bound presentation. Native telemetry/renderer
recovery, product retention and desktop integration remain pending. A
[bounded telemetry codec](spec/delivery/telemetry-wire-handoff.md) now preserves
versioned snapshot documents and exact replay bytes. The new
[complete-state import](spec/delivery/state-import-handoff.md) connects decoded
state to that owner while preserving remote retention and identity metadata.
A [native subscription probe](spec/delivery/subscriptions-handoff.md) now exchanges
synthetic inventory with demand expiry, policy revocation and reconnect recovery.
The [native clock investigation](spec/delivery/measurement-clock-handoff.md) verifies
comparable readings across live local processes and rejects sampling after peer exit.
The [GJS clock adapter](spec/delivery/gjs-clock-handoff.md) exposes that same Linux
clock as exact decimal strings, with tested native resource cleanup and peer-exit
rejection. The [owned GNOME clock experiment](spec/delivery/gnome-clock-handoff.md)
adds asynchronous attachment, visible public-sample age/expiry and native teardown.
Operational network freshness is covered by the later measured-tile experiment below.
The [native GJS network consumer](spec/delivery/gjs-network-view-handoff.md) now
reuses the shared C++ model, measured projection and revocable policy. Standalone
fixtures check its exact values, age, lease and failure behavior. The
[live native session](spec/delivery/live-network-session-handoff.md) now forwards
real measured collector messages to an asynchronous GJS owner and tests source
hang, policy erasure and parent loss. The [measured GNOME tile](spec/delivery/gnome-live-network-handoff.md)
now uses that owner to display actual counters/rates, advancing age and independent
freshness/lease states. External pixel checks detect frozen age, false freshness,
wrong values and failed clearing; native exits and typed policy erasure also pass.
An [independent render watcher](spec/delivery/gnome-render-watch-handoff.md) now
connects native challenges to operational drawing and paint instrumentation.
External pixels reject false progress; native deadlines survive a stopped shell
and queued late messages. Watcher loss clears the tile and retains actual child
exit failures. Later controller experiments below add bounded automatic replacement;
complete desktop recovery remains open.
The [consumer-continuity checkpoint](spec/delivery/consumer-continuity-handoff.md)
keeps one real collector alive across consumer crashes, lease expiry and bounded
replacement. Reattachment preserves original measurements; typed consumer-policy
revocation blocks another launch. The subsequent [persistent-controller experiment](spec/delivery/gnome-controller-recovery-handoff.md)
now replaces an owned GNOME shell automatically while preserving its collector,
then reattaches and displays current original measurements. Independent pixels
verify recovery after native dismissal of GNOME's startup overview. Disabled
reattachment and revoked permission controls preserve their distinct outcomes.
The [render-failure recovery checkpoint](spec/delivery/controller-render-recovery-handoff.md)
now connects independent render deadlines to that replacement owner. Stopped or
hidden drawing and a frozen owned shell recover current pixels; external observation
still rejects false progress acknowledgements. Editor recovery, installed ownership
and complete host qualification remain open.
The [independent editor-exit experiment](spec/delivery/editor-exit-handoff.md) now
removes an owned stopped editor candidate through a separate keyboard/GTK path.
Native exit, restored pixels and restored clicks are checked independently. This
closes a lifetime prerequisite. The subsequent [GNOME editor-exit checkpoint](spec/delivery/gnome-editor-exit-handoff.md)
connects it to the owned desktop and persistent collector/controller: native icon
input and original measured pixels recover without replacing those lifetimes.
Scene editing, transaction recovery, fullscreen discovery and installed ownership
remain required.
The [measured telemetry path](spec/delivery/measured-time-handoff.md) now preserves
sample age through delay, replay and reconnect, with explicit clock scope and TTL checks.
A [native network reader](spec/delivery/network-acquisition-handoff.md) now acquires
real interface counters on Windows/Linux. The [network reconciliation checkpoint](spec/delivery/network-reconciliation-handoff.md)
adds stable observation lifetimes, obsolete-result rejection and exact counter
intervals, plus a Linux link subscription held across repeated acquisition.
A [supervised Linux collector experiment](spec/delivery/network-publication-handoff.md)
now delivers real counters and interval rates through that measured path, preserving
failed samples and recovering a hung child after confirmed exit. Windows notification
coverage, product service/subscription integration and native suspend qualification
remain pending.
The [measured network presentation checkpoint](spec/delivery/network-presentation-handoff.md)
adds a shared renderer input with exact selection, counter/rate text, original
measurement age, independent freshness/lease state and policy-bound borrowing.
It passes portable checks on all three build profiles and comparisons against
the real Linux collector. A [native retained-cache experiment](spec/delivery/native-network-cache-handoff.md)
now displays its real values on the owned GNOME desktop and independently decodes
the digits. Revision-bound revocation and owner exit remove the cached actors and
pixels; negative controls expose wrong values and failed clearing. That retained
fixture keeps its original semantics. Installed policy and general product delivery
remain pending.
An external pixel/time oracle is calibrated against live, hidden, frozen and
obstructed synthetic X11 surfaces. A real Openbox/PCManFM Show Desktop experiment
now exposes the basic X11 candidate's placement failure: above the desktop it
covers icons and blocks the tested icon click; below it the marker is hidden.
The hidden variant passes the native input sequence. Delayed image setup passes
pixel checks; the original image-at-startup failure remains separate. See the
[X11 input checkpoint](spec/delivery/x11-input-handoff.md). An
[owned Openbox restart](spec/delivery/x11-recovery-handoff.md) now proves manager
recovery and continuing marker progress, while independently retaining the candidates'
visible-placement failures. A [GNOME 46/DING experiment](spec/delivery/gnome-composition-handoff.md)
now observes live drawings between a synthetic wallpaper and real desktop icons,
with independently calibrated pixels and wrong-layer controls. The subsequent
[native reveal experiment](spec/delivery/gnome-reveal-handoff.md) keeps those drawings
live while Show Desktop hides and restores a foreground window, but fails the
required foreground-focus restoration.
No desktop profile is qualified.
An [independent native comparison](spec/delivery/gnome-focus-handoff.md) reproduces
the focus and keyboard-delivery failure with DING while the SysPane extension is
absent; GNOME alone restores both. The original default acceptance failure remains open.
A [native decision trace](spec/delivery/gnome-focus-trace-handoff.md) now shows Mutter
selecting the DING desktop as its recent focus target on restoration. Traced and
untraced observations agree; the original default failure remains recorded.
A [native icon-input experiment](spec/delivery/gnome-input-handoff.md) now passes
real selection, drag selection, menus and folder opening with GNOME/DING and the
pinned PCManFM laboratory. Pointer-blocking and omitted-click controls fail as
required; this does not resolve the separate focus-restoration failure.
A [native image-wallpaper experiment](spec/delivery/gnome-wallpaper-handoff.md) now
preserves original file identity, native settings and exact PNG pixels beside the
live drawing. Separate replacement, setting-redirection and obstruction controls
expose each failure independently. A [native policy experiment](spec/delivery/gnome-wallpaper-policy-handoff.md)
now verifies locked wallpaper keys and unchanged policy identity. Protected policy
deployment, locked images and other display profiles still require qualification.
A [native application-list experiment](spec/delivery/gnome-switcher-handoff.md)
now keeps the passive bridge out of GNOME's Alt+Tab switcher and overview dash.
Actual normal-window and omitted-popup controls validate the observations; normal
application switching and overview dismissal preserve focus. The separate Show
Desktop focus failure remains open.
A [native icon-manager recovery experiment](spec/delivery/gnome-icon-recovery-handoff.md)
now confirms DING process replacement, continuing live drawing and usable icons
after the fault. Held process identities distinguish replacement even when the
window ID is reused. Frozen-drawing and omitted-stop controls fail independently.
A [native shell/compositor recovery experiment](spec/delivery/gnome-shell-recovery-handoff.md)
now replaces the owned GNOME process, reattaches the drawing and verifies input on
the new desktop. Omitting reattachment or replacement fails independently. User
session recovery and product continuity remain open.
A [native surface-lease experiment](spec/delivery/gnome-surface-lease-handoff.md)
now marks the last public marker retained after producer expiry or actual disconnect.
A replacement heartbeat preserves that old identity until a full snapshot arrives.
Independent pixels and held process identities verify the transition. Product
telemetry, policy integration and render-watchdog recovery remain open.
An [optional focus integration](spec/delivery/gnome-focus-integration-handoff.md)
now passes the original Show Desktop focus deadline and actual keyboard receipt.
Native icon/folder interactions, minimization and disabling the controller pass
the declared guards. A [further native experiment](spec/delivery/gnome-focus-scenarios-handoff.md)
now verifies selecting between two normal windows, modal focus, target closure and
workspace invalidation. The controller remains disabled by default pending broader
application/session cases and alternate triggers; the default failure is preserved.
There is no usable SysPane desktop application or downloadable release yet.
Desktop, screensaver and installer profiles remain unqualified.

An experimental [XP-toolset build](spec/delivery/historical-build-handoff.md) now
compiles the same shared C++ components and passes 51 checks on Windows 10/WOW64.
XP/7 guest execution and desktop support remain unproven.

The first implementation campaign includes contemporary Windows, Windows XP/7
investigations, Linux and macOS/older OS X. Each profile must prove its own
capabilities. Ordinary operation is intended to be native, unelevated and usable
offline, with truthful unavailable/stale states and an independent diagnostic
path when optional components fail.

- [Specification](spec/README.md) and [navigation](spec/index.md)
- [Documentation](docs/README.md)
- [Implementation checklist](TODO.md) and [campaign](spec/delivery/roadmap.md)
- [Current state](spec/delivery/current-state.md)
- [Implementation readiness](spec/delivery/implementation-readiness.md) and [first foundation package](spec/delivery/packages/w-01-foundation.md)
- [October audit disposition](spec/delivery/audit-2026-10-04.md)

`spec/` owns design and contracts, `source/` owns implementation, and `docs/`
owns audience-oriented guides. Python is used only for development tooling.
See [developer checks](docs/developers/build.md) for validation commands.

The active campaign covers the foundation and native experiments. Each package
must connect specified behaviour to runnable checks and a source-bound handoff;
see [the developer workflow](docs/developers/agent-workflow.md). Specification
validation does not establish that an entire edition can be built or released
without further experiments and contract decisions.

Code, documentation and asset licensing and contribution policy still require
an owner decision. Public visibility does not grant a project license. No
Microsoft, Apple, Linux project or upstream endorsement is implied.
