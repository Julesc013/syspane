---
type: "SysPane Work Package"
title: "W-05 native GNOME wallpaper policy preservation"
description: "Verify native locked background keys and immutable private policy during live composition."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:05:00Z"}
sp_id: "SP-W05-GNOME-WALLPAPER-POLICY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-DESKTOP", "SP-POLICY", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native GNOME wallpaper policy preservation

Use the existing owned GNOME/DING X11 lab. This package investigates preservation
of native wallpaper policy. It does not equate a locked wallpaper preference with
authorization to disclose telemetry, or qualify protected machine-policy deployment.
The live scene must retain the original independent marker/composition oracle.

## Native laboratory boundary

For this mode only, replace the private keyfile backend with the installed pinned
dconf 0.40.0 backend. Extract the matching 28,022-byte CLI package into an owned
runtime directory after SHA-256 verification; never install it or execute package
scripts. Record backend, library, service and CLI byte identities. All databases,
profiles, HOME/XDG paths and buses remain in the unique private attempt. Launch
one retained dconf session writer explicitly on that private bus, with no service
activation directories, system service, privilege change or user configuration.

Compile the initial user database from the lab's existing keyfile preparation.
Use an absolute private profile containing `user-db:user` and an absolute
`file-db:` policy database. The policy sets and locks `picture-uri=''`,
`picture-uri-dark=''` and `picture-options='none'` under
`/org/gnome/desktop/background/`. Other background keys remain writable for the
unchanged two-color icon calibration. This finite policy permits the existing
solid-color fixture; it does not qualify a locked image or every native key.

The GNOME [lock documentation](https://help.gnome.org/system-admin-guide/dconf-lockdown.html)
and [dconf profile implementation](https://github.com/GNOME/dconf/blob/0.40.0/engine/dconf-engine-profile.c)
define the native mechanism; runtime observations decide the experiment.

## Inputs, outcomes and controls

`--wallpaper-policy locked|unlocked|replace-policy` owns the live composition
prerequisite and excludes every other optional experiment flag. After that
prerequisite, retain read-only no-follow descriptors to the private profile and
compiled policy. Bound each to 64 KiB. Record bytes, hash, device/inode, UID, mode,
link count and modification/change times at the path and retained descriptor.
Freeze the complete native background settings record and policy snapshots.

Record `gsettings writable` for each policy key and attempt exactly one change of
`picture-uri` to an owned sentinel file URI. With locks it must be nonwritable and
the native write must fail without changing any background setting. A separate
write to the private `clock-show-seconds` preference must succeed and read back;
this rejects an unavailable writer being mistaken for enforcement. No candidate
method supplies the write result or native policy state.

Run the unchanged 2,400 ms marker trace, generations 1/2/3, with paired overlap and
background captures. Preserve the original 50 ms cadence/capture, 150 ms coverage
gap and 200 ms generation deadline. Capture policy file snapshots in each paired
sample; settings and native writability are checked before and after the trace.
No retry can erase a failed measured frame. Existing icon ownership and process
cleanup rules apply. Flush a bounded raw journal (180 records/8 MiB).

- `locked`: all keys reject writes, the attempted URI change fails, complete
  background settings and policy identity remain unchanged, and live composition
  passes.
- `unlocked`: compile identical defaults without locks from the outset. All three
  keys must be writable and the attempted URI write must succeed. The complete
  settings record exposes only that URI change. `picture-options='none'` keeps
  pixels identical, so pixels cannot substitute for native enforcement evidence.
  The policy requirement fails while marker, icons and background pass.
- `replace-policy`: retain the locks and rejected write, then atomically replace
  only the owned policy database with identical bytes at 1,000 ms, within 50 ms.
  The held original and replacement path expose distinct lifetimes despite equal
  hashes. Native settings, writability and pixels stay correct. At least three
  samples after completion plus 200 ms must reject policy identity preservation.

Startup failures, unavailable writer, changed native settings outside the intended
control, foreign file ownership or incomplete capture cannot calibrate a pass.
The shell bridge remains unchanged. Preserve exact source archives, package/runtime
identities, settings stdout/stderr/exit codes, policy bytes, raw samples and failures.
Recompute acceptance independently and test consistent false records, not only
single-field mutations. Keep the 40-second observer and owned cleanup bounds.

## Completion and remaining gates

Implementation completion requires all three source-identical native modes with
the declared isolated outcomes, independent negative verifier checks, unchanged
default composition/marker behavior, specification checks and a source-bound
handoff. This is a native settings-policy experiment, not a security sandbox:
the lab user owns its simulated policy and can replace it deliberately. Protected
deployment, locked image wallpaper, live organization policy changes, disclosure
revocation, other sessions/displays and a complete product host remain unqualified.
