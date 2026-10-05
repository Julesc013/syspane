# Foundation development profiles

Current revisions are Windows x64 10, Linux x64 11 and historical x86 4. The
[data-view checkpoint](../../spec/delivery/data-view-handoff.md) passes 65/66 modern
and 61 historical host checks, including six typed synchronization/policy cases.
The previous revisions were Windows x64 9, Linux x64 10 and historical x86 3. The
[preservation checkpoint](../../spec/delivery/preservation-handoff.md) records
59/60 modern checks and 55 historical host checks. Native opaque copy/UI adapters
are enabled only in modern profiles; historical evidence covers the portable
policy predicate. Earlier revision/count statements below remain historical.

These profiles build the typed model and development smoke program. They do not
qualify a desktop host or release. Exact installed compiler, frontend, static
runtime archives, CMake and Ninja fingerprints are in the corresponding lock.
Configure refuses a mismatch. Changing a lock is an explicit profile revision,
followed by a fresh build and evidence; it is not an automatic configure action.

From the repository root on Windows, with the pinned WinLibs tools on PATH:

```powershell
cmake --preset windows-x64-gcc15
cmake --build --preset windows-x64-gcc15
ctest --preset windows-x64-gcc15 --output-on-failure
out/build/windows-x64-gcc15/SysPane.ModelSmoke.exe
```

In the existing Ubuntu 24.04 WSL environment, use an unprivileged account, change
to the mounted repository root and run:

```sh
export SYSPANE_LINUX_BUILD_ROOT="$HOME/.cache/syspane/campaign-229a498"
cmake --preset linux-x64-gcc13
cmake --build --preset linux-x64-gcc13
ctest --preset linux-x64-gcc13 --output-on-failure
"$SYSPANE_LINUX_BUILD_ROOT/linux-x64-gcc13/SysPane.ModelSmoke"
```

Python 3.11+ is a configure/test tool only; no endpoint Python dependency is
introduced. Both builds use C++17, exceptions and RTTI, x86-64/SSE2 baseline with
generic tuning, a single model writer and Debug assertions independent of NDEBUG.
Windows links GCC/libstdc++/winpthread statically; OS DLL imports must still be
audited. Linux uses the named host glibc/libstdc++ baseline. Header/vendor archive
provenance is incomplete, so these locks do not prove bit-for-bit reproducibility.

Expected outputs are the model static library, `SysPane.ModelSmoke` (plus `.exe`
on Windows), `syspane_model_tests`, CTest results and the generated component graph
inside `out/build/<preset>/`. The smoke program exits 0 only after its fixture
journey succeeds and prints one JSON object checked against
`tests/model/smoke.expected.json`. Failures return nonzero; zero discovered CTest
cases is an error. The test executable requires one known case ID and rejects
unknown IDs. All outputs remain local development artifacts.

Profile revision 2 adds the portable `syspane_protocol` and
`syspane_configuration` static libraries and `syspane_protocol_tests`, for 35 total
CTest checks. The protocol boundary uses the vendored nlohmann/json 3.12.0 header;
`build-support/dependencies.json` pins its header and MIT-license digests. No native
IPC or desktop capability follows from these added libraries. Existing W-01 and
model smoke-package evidence remains tied to the earlier recorded source/profile.

Linux build products use the explicitly set native cache root instead of the
mounted Windows drive: unprivileged `chmod` on that mount failed during the first
configure experiment. The cache holds build products only, never a second source
checkout. Configure checks containment under `~/.cache/syspane/`, writes an ownership
marker and enforces the 1 GiB output budget. Preserve failure logs before cleaning
an identified owned build root. The source and acceptance oracles are shared.

Profile revision 3 adds `syspane_local_ipc` and `SysPane.IpcProbe`, with real
Windows named-pipe and Linux Unix-socket tests. Windows adds ADVAPI32 imports for
token/ACL inspection. Linux requires SO_PEERPIDFD and procfs in the measured WSL2
environment; it does not infer an older kernel floor. Both profiles run 37 CTest
entries. The probe is single-connection, synthetic and unelevated; cross-user/logon
and desktop qualification are distinct blocked/pending claims. No product support
or isolation tier is promoted by this development profile revision.

Profile revision 4 adds the dependency-independent `syspane_recovery` library and
`syspane_recovery_tests`, for 48 CTest entries. Eleven portable cases use injected
monotonic time to prove lease/render/restart decisions. No native diagnostic entry,
independent process supervision or visible expiry is qualified by those cases.

Profile revision 5 adds `syspane_child`, `syspane_health` and
`SysPane.RecoveryProbe`, with nine native supervision cases in one additional CTest
family (49 entries total). Windows requires job assignment before resuming the
owned child; Linux requires pidfds, procfs and the measured libc spawn/closefrom
support. The launcher executes only itself and passes no unrelated handles or
standard streams. The inherited development environment is trusted input. This
is not hostile-code isolation or a product/historical-platform qualification.

Profile revision 6 adds independent diagnostic reporting and Win32/GTK inspectors,
bounded policy decoding and read-only protected policy sources (52 CTest entries).
Windows adds USER32/GDI32 native controls. Linux pins GTK 3.24.41 with Ubuntu
`libgtk-3-dev`/`libgtk-3-0t64` 3.24.41-4ubuntu1.3, GLib development 2.80.0-6ubuntu3.8
and X11 development 2:1.8.7-1build1. Configure checks those package versions and the
GTK shared-library SHA-256 through `check_diagnostic_dependencies.py`; it does not
install packages. The installed GTK copyright file records LGPL-2+, LGPL-2.1+ and
Expat terms; no GTK redistribution package or full transitive closure is claimed.
The native close check uses hidden Win32 and owned Xvfb/X11 windows owned by the harness.
Report mode requires no display initialization, but the Linux ELF still requires
its installed GTK loader closure. Wayland, policy deployment, preservation controls
and complete diagnostic/desktop qualification remain separate pending gates.

The test-only Xvfb package is 2:21.1.12-1ubuntu1.6; configure verifies its executable
fingerprint. Tests enable only an authenticated abstract Unix socket with a random
high display, check its server PID and stop the owned server. The WSLg display and
its filesystem socket directory are not modified. Initial WSLg/Xvfb failures remain
in the diagnostic attempts record; Xvfb success is not desktop qualification.

Profile revision 7 adds portable external marker/time evaluation on both profiles
(53 CTest entries on Windows) and `SysPane.OracleProbe` plus independent root capture
on Linux (54 entries). The Linux X11 development/runtime package is
2:1.8.7-1build1; the runtime SHA-256 is checked alongside the existing native UI lab
dependencies. The manifest's optional `profiles` selector restricts a component to
named profiles; an absent selector means both current development profiles. The
graph checker uses the build ownership marker and rejects a target set from the
wrong profile. It does not invent a placeholder Windows capture executable.

The Linux oracle uses 128x96 RGB markers on an owned 800x600 Xvfb display, retains
compressed raw frames and preserves failed/inconclusive temporal observations as
calibration evidence. No input reaches the user's display. Named shell actions,
icons, Windows capture, real wallpaper policy/files and wall qualification remain
pending. These native captures establish pixels only for this synthetic laboratory.

Linux revision 8 adds the separate EWMH/XShape candidate library and Xext
2:1.3.4-1build2 runtime/development pin. Windows stays revision 7. The optional
Openbox/PCManFM investigation uses 35 explicitly pinned Ubuntu archives extracted
inside the owned build cache, isolated XDG paths and a private session bus. It is
separate from the offline 54-entry regression suite. Its real Show Desktop action
exposes placement failures; the color control does not qualify the separately
failing image-wallpaper lab. See `spec/delivery/x11-host-handoff.md` and the developer
commands. No product role or supported desktop profile is enabled by these probes.

The separate `windows-x86-v141-xp` experiment uses the installed Visual Studio 2017
XP toolset, compiler 19.16.27054.0, SDK 7.1A and static UCRT 10.0.10240.0. Its lock
pins 34 key installed files; the artifact audit also checks actual compiler flags
and resolved linker inputs. It builds eleven existing portable components in x86
Release/SSE2, without native modern adapters or a duplicated shared implementation.

```powershell
cmake --preset windows-x86-v141-xp
cmake --build --preset windows-x86-v141-xp
ctest --preset windows-x86-v141-xp --output-on-failure
python build-support/package_smoke.py --profile windows-x86-v141-xp --build-dir out/build/windows-x86-v141-xp
```

The initial revision had 51 host checks, including PE/header/import validation and nine
mutation cases. Binaries are under `out/build/windows-x86-v141-xp/Release/`.
The intended XP SP3/Windows 7 runtime experiment is still unqualified; running the
artifacts on this Windows 10 host is WOW64 evidence only. CMake's SDK-selection
banner is not the resolved library list: v141_xp selects SDK 7.1A and the explicitly
pinned UCRT, which the audit verifies from MSBuild's actual input logs.
MSB8051 is a preserved vendor deprecation warning; compiler warnings remain errors.
See `spec/delivery/historical-build-handoff.md` for guest and desktop gates.

The current recent-failure increment uses Windows revision 8 (57 CTest entries),
Linux revision 9 (58) and historical revision 2 (54). Three shared diagnostic cases
cover the bounded metadata codec, byte-by-byte interruption and policy read gating.
The modern profiles additionally own `syspane_failure_store` and its native tests;
Windows links system Advapi32/Shell32 for private ACLs and Unicode arguments.
The historical profile includes only the portable codec/projection. Its current
guest workload would be 47 C++ case invocations plus model smoke; six tooling
entries stay on the modern host. Guest execution remains unqualified.
