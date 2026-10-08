---
type: "SysPane Work Package"
title: "W-01 portable build and model foundation"
description: "Define the first useful program, model cases and build evidence without claiming a desktop implementation."
tags: ["delivery", "foundation"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T19:48:29+11:00"}
sp_id: "SP-W01-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-COMPOSITION", "SP-PORTABILITY", "SP-STATE", "SP-TARGETS", "SP-ACCEPTANCE-TRACES"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-READINESS-2026-10-05", "resource": "User-supplied readiness review, 2026-10-05", "title": "Implementation closure review"}]
updated: {"by": "codex", "at": "2026-10-05T23:39:47+11:00", "scope": "Admitted model foundation; executed development checks, no desktop qualification or human review attested"}
---

# W-01 portable build and model foundation

This is the detailed contract for W-01 in [the campaign index](../work-units.json).
The [campaign admission](../campaign-admission.md) records the user's implementation
instruction and closes the internal publication/resource boundary. The
[foundation handoff](../foundation-handoff.md) records implemented outputs and
actual development checks. This package does not itself grant release authority.

## Outcome and boundaries

Produce a small C++17 executable that exercises the real typed model through a
deterministic fixture journey and exits successfully only when its declared model
checks pass. It is a development smoke program. An empty scaffold or program that
only prints a version is insufficient. Desktop hosting, IPC, collection, rendering,
native controls, persistence and distribution qualification belong to later units.

Own `source/model/`, the smoke composition root in `source/application/`,
`tests/model/`, `CMakeLists.txt`, `CMakePresets.json`,
`source/build/components.json` and `source/build/targets/`. Extend the work row
with real additional outputs if a delegated design requires them. Create
directories only with real content. Keep build products under ignored `out/`.

## Input and ownership contract

Use the state semantics and experimental observation/snapshot 0.1 vocabulary.
Typed in-process values are authoritative within the model; a JSON runtime parser
is not required for W-01. Test inputs may be typed literals transcribed from the
versioned cases. Tests must compare explicit expected values, not values generated
by the production algorithm. Retain the decimal uint64 wire rule when a wire
adapter is introduced; never narrow counters to an imprecise floating-point type.

The store owns the current coherent generation, entity lifetimes and tombstones.
Only its publication path mutates them. Readers hold immutable snapshots; replacing
the current snapshot cannot mutate an older reader's values. The composition root
owns the store and injected clock/source lifetimes. A deterministic single-writer
implementation is sufficient here; concurrent writers and callback registrations
are outside this package. Do not introduce model dependencies on OS handles,
native UI, renderers, providers or a JSON library merely for test convenience.

Validate a whole candidate before publication. Duplicate entity identities,
dangling relationships, a missing delta base, conflicting duplicate records or
late updates for a retired lifetime leave the last accepted snapshot unchanged.
Error results must identify the rejected condition and whether a new snapshot is
required. Public wire error names are owned by the protocol package; private C++
enum/class names are delegated. No malformed candidate may partially update readers.

Observation support, acquisition, freshness and presence remain independent.
Retain the successful value and observation time after a later acquisition failure;
report that failure and stale status. Explicit null and measured zero remain
distinct. Inject monotonic time and producer epochs. Wall-clock adjustments cannot
create negative intervals; crossing an epoch invalidates an interval.

## Admission and profile work

Before the first build, populate a development profile using installed, identified
tools. Record compiler/SDK/runtime/dependency versions and hashes, architecture,
ISA and API floors, C++ mode, exceptions/RTTI/atomic assumptions, flags, enabled
components and expected outputs. A host-only profile may target the tested host
version; it must not guess a historical OS floor or claim supported distribution.
Record tool acquisition inputs or an explicit reproduction limitation. Do not pin
only a compiler name or a moving package-manager label.

Create explicit CMake targets for the model, smoke program and tests, with public
and private dependencies matching the component manifest. Delegate their exact
names and the preset names to the implementer, then document the actual names in
the checked-in recipe. The required command interface from repository root is:

```text
cmake --preset windows-x64-gcc15
cmake --build --preset windows-x64-gcc15
ctest --preset windows-x64-gcc15 --output-on-failure
out/build/windows-x64-gcc15/SysPane.ModelSmoke.exe
```

These Windows commands exist. The Linux preset is `linux-x64-gcc13`, with its native
cache root set as documented in `source/build/targets/README.md`; the optional
`source/build/run_foundation.sh` wrapper runs the same commands. Tests return nonzero on any failed required
assertion; a runner with zero discovered cases is a failure. Expected smoke output
includes the accepted epoch/generation and explicit unavailable/stale observations.
Version the exact output fixture with the implementation before accepting it.

Investigate one second toolchain/OS family and a Windows XP/7 candidate early.
Record each candidate's actual compiler/runtime/import floor and build/launch
outcome. A missing lab blocks its qualification, while host development proceeds.
Do not wait for every historical profile. Do not infer OS support from C++17
compilation or a successful run on contemporary Windows.

## Acceptance and completion

| Parent family | Required W-01 evidence |
|---|---|
| T-STATE | STATE-01 through STATE-05 in the linked traces, immutable-reader preservation and graph-reference validation |
| T-VALIDITY | VALIDITY-01 and VALIDITY-02, retaining separate value/status/time dimensions |
| T-CLOCK | CLOCK-01 and CLOCK-02 with an injected clock; native clock-adapter qualification remains separately pending |
| T-COMPOSITION | Machine-readable CMake dependency graph and component manifest agree; deliberate forbidden model dependency fails the check |
| T-TARGETS | Concrete development profile, clean configure/build/test/smoke logs, input/artifact identity and import/dependency inventory on that profile |

The [case tables](../../assurance/acceptance-traces.md#model-foundation-cases) are
the initial oracle; add boundary cases as implementation decisions expose them.
Before accepting W-01, bind every mandatory case to a test name/source and runnable
command. Preserve a failing expectation as evidence if a contract change is needed.

Complete the host implementation gate only after the nonempty program and suite
build and pass from the documented inputs. Record historical/second-family probe
results and remaining qualification separately. W-01 does not satisfy the whole
native T-CLOCK or T-TARGETS family, a desktop capability, or a release gate.

Resource ceilings for this initial test model are not production capacity claims.
Before exposing it to untrusted input or a long-running collector, the consuming
package must specify bounded entity, edge, observation and queued-publication
admission. Allocation/container strategy is delegated here; silent integer wrap,
partial publication and data-status conflation are prohibited at any scale.

The handoff names the exact source/profile/artifacts, passing case bindings,
unexecuted native cases, delegated choices and required next gates. W-02, W-24 and
W-26 can then consume this foundation through their own admission and interface
closure. W-25 additionally depends on W-24. No unrelated platform lab is an
implicit global barrier.
