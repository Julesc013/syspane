# Developer setup and checks

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

Both profiles now run 37 CTest entries: the original 18 model/smoke/component checks,
17 portable protocol/policy checks and two native IPC families. Run portable cases with
`ctest --preset windows-x64-gcc15 -R '^protocol\.' --output-on-failure`.
The original W-01 results remain historical; current case/artifact records are
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
