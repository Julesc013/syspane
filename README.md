# SysPane — System Panel

A native operational desktop for seeing host identity, network connections,
resources and connected devices at a glance, without replacing your wallpaper.

SysPane is designed around a persistent passive desktop surface, a native
inspector and settings application, and direct desktop editing. GUI, editor,
CLI and local automation share the same validated operations. Portable scenes,
themes and presets describe user intent; native adapters supply each platform's
data, controls and desktop integration. A companion screensaver reuses the
presentation components under its own lifecycle and privacy policy.

**Current stage: specification and implementation planning.** This repository
contains experimental contracts, synthetic fixtures and working specification
tools. It does not yet contain a native SysPane application or downloadable
release. No operating-system, desktop, screensaver or installer profile is
qualified.

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

`spec/` owns design and contracts, `source/` will own implementation, and `docs/`
owns audience-oriented guides. Python is used only for development tooling.
See [developer checks](docs/developers/build.md) for validation commands.

The next step is a bounded build foundation and native experiments. Each package
must connect specified behaviour to runnable checks and a source-bound handoff;
see [the developer workflow](docs/developers/agent-workflow.md). Specification
validation does not establish that an entire edition can be built or released
without further experiments and contract decisions.

Code, documentation and asset licensing and contribution policy still require
an owner decision. Public visibility does not grant a project license. No
Microsoft, Apple, Linux project or upstream endorsement is implied.
