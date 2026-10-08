---
type: "SysPane Work Package"
title: "W-26 early local smoke package"
description: "Bind foundation payload bytes to a local archive and independently check relocated execution."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:15:42+11:00"}
sp_id: "SP-W26-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-ARTIFACTS", "SP-TARGETS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-26 early local smoke package

Consume W-01's tested development binary, component manifest and identified target
profile. The first artifact is explicitly `model-development`, not a desktop
edition, installer or public release. The campaign admits local creation and
execution; publication, signing and privileged installation remain excluded.

The recipe is `source/build/package_smoke.py --profile <profile> --build-dir
<owned-build-root>`, run through an available Python 3.11+ interpreter from the
repository root. `source/build/targets/README.md` supplies exact profile commands.
The Linux shell wrapper avoids forwarding nested variable expansion through WSL.

The ZIP contains exactly one component-owned executable under `bin/`, plus
package-recipe-owned `manifest.json` and `README.txt`. It excludes tests, build
tools and source copies. The manifest identifies profile, source base plus exact
input hashes, component, payload hash, OS imports and qualification/publication
limits. Archive timestamps are fixed; no claim of compiler bit reproducibility is
made. Preserve the selected compiled payload bytes through packaging/relocation.

Outputs use a fresh marked attempt directory under `out/campaign/<profile>/`.
The recipe checks the 1 GiB campaign output budget before writing payload copies.
For Linux execution use the admitted native cache root; do not require chmod or
privilege changes on the Windows mount. No arbitrary archive import is implemented:
the extraction step accepts only the fixed generated member set.

| Case / parent | Stimulus | Required outcome |
|---|---|---|
| PKG-01 / T-ARTIFACTS | Package a tested matching-profile model binary. | Exact fixed file set, single owner per entry, source/profile/payload hashes recorded. |
| PKG-02 / T-ARTIFACTS | Relocate its archive bytes and execute from the new directory with empty PATH and no injected loader path. | Exit 0, empty stderr and JSON exactly matching the independent model smoke fixture. |
| PKG-03 / T-TARGETS | Inspect PE/ELF dependencies for the selected payload. | Only declared OS/runtime imports; unresolved/unexpected dependencies reject packaging. This is not an older-OS support test. |

Failures return nonzero and retain their attempt artifacts. A successful local
smoke result does not settle licenses/notices, final package lifecycle, wrong-ISA
installer selection, native desktop support or signed-release qualification.
Later payloads extend the same package work unit after their component closure
and mandatory profile tests exist. Those later capabilities remain pending.
