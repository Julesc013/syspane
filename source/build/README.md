# Shared build tooling

This directory contains versioned build scripts, dependency and runtime locks,
target profiles, component metadata and evidence recorders. CMake and the tests
use these files on every checkout. Run commands from the repository root; see
[the build guide](../../docs/developers/build.md).

Generated artifacts and recordings belong in ignored `out/` directories. Preserved
historical evidence lives locally in `out/evidence/`; it is not a build dependency.
Native experiments requiring earlier build evidence must create their own declared
prerequisite records before qualification. A missing laboratory or record does not
mean a pass.

For the Windows/WSL campaign coordinator, copy `workspace.example.json` to
`out/campaign/workspace.json` and replace its placeholders with the explicitly
admitted distribution, non-root user and owned Linux campaign directory. That file
is machine-local. Common active-output budgets remain in `campaign-workspace.json`;
retained evidence storage is measured separately.

The former root `build-support/` path is retired. Keep new shared build utilities
here and keep generated evidence out of Git.
