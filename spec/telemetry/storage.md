---
type: "SysPane Specification"
title: "Storage, volumes, partitions and filesystem identity"
description: "Model storage topology without opening or mutating devices unnecessarily."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-STORAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Storage, volumes, partitions and filesystem identity

## Topology

Represent physical/block devices, partitions, volume extents, logical volumes, filesystems and mount points as separate entities with edges. One drive letter is not one physical disk; one volume can span devices and one filesystem can have multiple mount points. Network shares have remote scope and different failure/latency behaviour.

Inventory includes source-supported model, serial, capacity, bus/transport, removable state and health provenance. Serial strings can be missing, duplicated, redacted or controller-translated. Preserve raw/source identity separately from friendly presentation, sanitize untrusted strings and do not key permanent identity on a drive letter.

## Safe acquisition

Prefer passive/native inventory and bounded filesystem queries. Separate volume free space, disk transfer rates, queue statistics and health/log-page queries. Do not repeatedly touch sleeping, failing or removable media to keep a cosmetic field fresh. A device capable of reporting health does not imply its bridge/controller forwards it or that the current user has permission.

Deeper SMART/NVMe/controller interrogations declare command, transport, permission, timeout and potential side effects. They are opt-in when they may perturb equipment. No formatting, partition changes, firmware writes, mount changes or repair actions belong in the normal observer.

## Failure behaviour

Removal invalidates the entity generation and cancels pending consumers. Late I/O results are discarded rather than applied to newly inserted media. A timeout can leave a system call blocked; isolate hazardous providers instead of terminating a thread inside shared runtime code. Network filesystem failures cannot freeze the UI.

Low free space and full history storage are separate diagnoses. SysPane must stop or rotate its own recording safely, expose the loss and preserve the wall, not recursively fill storage while reporting an error. Durability settings are explicit because excessive flushes themselves create storage work.

## Acceptance

Test unlettered volumes, multiple mount points, removable swaps, missing serials, multi-extent layouts, path encoding, permissions, unavailable network filesystems and delayed responses. Product tests use synthetic storage graphs before leased device tests. No disruptive raw-device action runs on a developer workstation merely because an agent owns a worktree.
