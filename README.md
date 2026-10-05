# SysPane — System Panel

A native operational desktop for seeing host identity, network connections,
resources and connected devices at a glance, without replacing your wallpaper.

SysPane is designed around a persistent passive desktop surface, a native
inspector and settings application, and direct desktop editing. GUI, editor,
CLI and local automation share the same validated operations. Portable scenes,
themes and presets describe user intent; native adapters supply each platform's
data, controls and desktop integration. A companion screensaver reuses the
presentation components under its own lifecycle and privacy policy.

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
recovery, product retention and desktop integration remain pending.
An external pixel/time oracle is calibrated against live, hidden, frozen and
obstructed synthetic X11 surfaces. A real Openbox/PCManFM Show Desktop experiment
now exposes the basic X11 candidate's placement failure: above the desktop it
covers icons and blocks the tested icon click; below it the marker is hidden.
The hidden variant passes the native input sequence. Delayed image setup passes
pixel checks; the original image-at-startup failure remains separate. See the
[X11 input checkpoint](spec/delivery/x11-input-handoff.md). No desktop profile is qualified.
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
