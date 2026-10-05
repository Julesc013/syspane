# Implementation and resumption workflow

Start at the root README, [current state](../../spec/delivery/current-state.md)
and [work-unit catalog](../../spec/delivery/work-units.json). Check the actual Git
state and available environment. Use the existing user instruction to determine
authority; an assistant review or a dependency-ready row is not a new grant.
Ordinary reversible engineering choices within an admitted package do not need
repeated permission. AIDE is optional development infrastructure, currently inactive.

1. Select dependency-ready work and check evidence for its required outputs.
2. Read its linked package and contracts. Close ambiguities affecting its observable
   behaviour, interfaces, failures, resources and acceptance before implementation.
3. Record private engineering choices. Run bounded experiments for choices that
   need platform evidence; continue independent work when a lab is unavailable.
4. Implement and run the declared build, tests and smoke commands. Bind concrete
   cases to the existing parent test IDs. Keep expected outcomes independent of
   implementation output, and preserve failures before changing an oracle.
5. Leave a source-bound handoff with artifacts, commands, actual results, limitations,
   gate states and the next step. A later session must not need the chat history.

The [work-package contract](../../spec/delivery/work-packages.md) is canonical.
[W-01](../../spec/delivery/packages/w-01-foundation.md) defines the first useful
model program. Its [case traces](../../spec/assurance/acceptance-traces.md) are
expected behaviour. Model cases now have executed CTest bindings on Windows and
Linux; request/recovery and cold-start cases remain unexecuted. Read the current
handoff and exact artifact evidence before carrying a result forward.

An implemented package has passed its mandatory implementation checks. A missing
native lab blocks the named qualification, and mandatory release gates still apply.
Do not call a skipped or unavailable mandatory implementation check complete.
Use the proposed cold-start exercise only when admitted; it tests whether the
repository supplies enough context, rather than whether two implementations use
the same private classes.

For a bounded foundation context export, run this existing tooling command from
the repository root (use `.venv/bin/python` on POSIX):

```powershell
.venv/Scripts/python spec/tools/specctl.py context --topic foundation --max-chars 80000 --out out/foundation-context.md
```

The export records input hashes and omissions; it does not replace the canonical
contracts. Choose a new output filename for a later export or explicitly use
`--force` after deciding to replace the old projection.
