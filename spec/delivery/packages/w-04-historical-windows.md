---
type: "SysPane Work Package"
title: "W-04 historical Windows build and host experiments"
description: "Test the existing shared C++ subset with the installed XP toolset before claiming historical runtime or desktop support."
tags: ["delivery", "architecture", "desktop"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:15:00+11:00"}
sp_id: "SP-W04-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-WINDOWS", "SP-W02-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-READINESS-2026-10-05"]
---

# W-04 historical Windows build and host experiments

The campaign admits reversible source/build experiments now. Existing guest machines
are not implicitly disposable or synthetic desktops: establish their scope before
booting, changing disks or capturing their content. Read-only inventory identifies
available tools and registrations; it cannot establish a working guest laboratory.
Missing guest access does not block this build experiment or other native tracks.

## Shared-subset question and fixed outcome

Can the actual model, protocol/policy, portable recovery and diagnostic projection
sources compile and pass their existing behavioral tests using the installed XP
toolset, without duplicating implementations or changing their oracles? Use the
same root CMake project and existing source/test ownership. Keep native IPC, process
supervision, protected-policy readers and UI components out of this profile until
their historical OS contracts and imports are closed; their existing modern profiles
and requirements remain intact.

`windows-x86-v141-xp` is an experimental build profile, not a supported product.
It selects Visual Studio 2017, v141_xp/14.16.27023, Win32, Windows SDK 7.1A and UCRT
10.0.10240.0. Pin installed compiler/linker/build/SDK/runtime identities. Use C++17,
exceptions/RTTI, SSE2, Release and static `/MT` runtime, with warning errors and no
host tuning. The intended runtime experiment is XP SP3 x86 and Windows 7; running
the artifacts on this Windows 10 host does not establish either historical floor.

The configured component graph must exactly match the selected profile, including
all existing portable tests. No native test is relabeled as portable or silently
reported passed. Native product capabilities stay disabled in this experiment.
The configured PE executables must be x86, subsystem 5.01, and have no mandatory
CRT sidecar or unclosed static imports. Record the complete import table and linker
selection; a module-name check alone does not prove XP API availability. Dynamic
runtime fallbacks still require actual guest execution.

Use the checked-in configure/build/test preset and existing local smoke-package
command. A relocated smoke test must run the exact packaged bytes with an empty
PATH and match the existing literal expected output. Keep generated binaries,
logs and packages in owned `out/` roots below the campaign's 1 GiB ceiling. No
toolchain download, installation, license activation or public release is admitted.

## Evidence and decision authority

Compilation or test failures preserve their original command, source/tool identity
and output. Correct portable implementation defects when justified by the existing
contract; do not change expectations merely to obtain a pass. Record warnings and
runtime dependency limitations explicitly. Compiler-private implementation choices
are delegated; changing public behavior or accepting unsupported imports is not.

Ready-to-build means the profile/commands/inputs are fixed. A build pass requires
all selected targets and existing portable cases, the import audit and relocated
smoke. Historical runtime qualification additionally requires exact guest OS/CPU/
runtime identity and execution of those binaries/tests there. Host qualification
requires actual native candidates, externally captured changing pixels, desktop
reveal, icon input, wallpaper preservation and independent recovery on each OS.
The W-02 oracle and behind-icons acceptance criteria remain unchanged.

The initial profile revision ran 51 CTest entries. Revision 2 adds three shared
failure-metadata cases, for 54 entries on the modern CMake/Python build host. A historical
guest must execute the four C++ test binaries with their 47 current case IDs and
the model smoke binary with its literal output oracle. The six build/tooling CTest
entries stay on the build host; do not require Python 3.11 or current CMake inside
XP, or count host checks as guest execution. Close the transfer/launch/result
collection boundary after the guest is admitted, before declaring a guest run.

The completion record must distinguish registered VM, usable guest, build result,
host execution, historical execution and desktop qualification. A tiny or powered-off
disk is not proof of an installed OS. Windows XP and Windows 7 stay independent.

References: [Microsoft XP toolset guidance](https://learn.microsoft.com/en-us/cpp/build/configuring-programs-for-windows-xp?view=msvc-160),
[CMake Visual Studio 2017 generator](https://cmake.org/cmake/help/v3.31/generator/Visual%20Studio%2015%202017.html),
and [CMake MSVC runtime selection](https://cmake.org/cmake/help/latest/variable/CMAKE_MSVC_RUNTIME_LIBRARY.html).
