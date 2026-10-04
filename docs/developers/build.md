# Developer setup and checks

The repository contains specification tooling; there is no native CMake target
or product build yet. Use Python 3.11+ in an isolated development environment.
From the repository root on Windows:

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

Future builds use one `source/` tree, explicit CMake targets and pinned target
profiles. Introduce directories only with real implementation. Keep outputs in
owned, bounded checkout/build/cache roots. Human, CI and AIDE workflows use the
same commands; AIDE is neither an endpoint dependency nor a build prerequisite.

Start with [TODO](../../TODO.md), [architecture](architecture.md) and
[target profiles](../../spec/delivery/target-profiles.md). License/contribution
terms remain an owner decision; this guide does not invent them.
