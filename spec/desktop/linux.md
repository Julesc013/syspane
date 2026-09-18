---
type: "SysPane Specification"
title: "Linux desktop and distribution profiles"
description: "Separate kernel collection, packaging, UI toolkit and compositor integration."
tags: ["desktop"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-LINUX"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Linux desktop and distribution profiles

## Four boundaries

Linux collection, distribution dependencies, native settings toolkit and desktop-shell hosting are independent. Debian and RHEL are distribution/build/package profiles, not copies of the semantic engine. X11, Wayland compositors, GNOME Shell and Plasma require separate host qualification.

Native collectors use appropriate kernel/system interfaces after checking permissions and API availability. Notifications and dumps can be incomplete, raced or overflowed; resynchronization is mandatory. Shared contracts do not expose Linux-only structs to other platforms. Container, namespace and host scope are explicit rather than inferred from a convenient process view.

## Host investigations

For X11, investigate desktop-type windows together with the actual window manager and icon manager. For Wayland, investigate a layer protocol only when advertised by the compositor and permitted by the session. Protocol availability is not proof of placement between the existing wallpaper and icon surfaces.

GNOME may require a small shell-specific bridge; Plasma may benefit from native containment/widget integration. These are implementation candidates from the design conversation, not qualified claims in this archive. The host experiment must identify the exact supported API/extension version and its packaging rules before release. Keep expensive collection and blocking I/O outside the shell.

A bridge without process isolation declares that reduced isolation explicitly. No imported plugin or device metadata may execute inside the compositor/shell. On shell restart, recreate only the native bridge resources while preserving controller state.

## Native configuration

GNOME uses a GTK/libadwaita-oriented interface and KDE a Qt/KDE-oriented one. Generated bindings may use their native settings facilities, but the typed transaction store remains canonical. Do not create two independently writable configuration databases. Shared editor operations and accessible property panels remain equivalent even when native widgets differ.

## Packaging and baseline

Record libc/libstdc++ baseline, architecture, toolkit versions, desktop protocols, sandbox/portal permissions and package dependencies. Distribution-provided libraries may be appropriate; do not promise one static executable across all Linux installations. Do not bundle an entire browser engine to avoid solving native integration.

## Acceptance

Run the same changing-scene, edit/apply/cancel, icon-input, display-change and desktop-reveal tests on each admitted environment. Cover shell/bridge reload, absent protocol, denied permissions, multi-monitor scaling and hot-plug. A headless collector can be admitted separately; a top-level preview window cannot stand in for a persistent wall qualification.
