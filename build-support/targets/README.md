# Foundation development profiles

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
