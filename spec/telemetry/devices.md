---
type: "SysPane Specification"
title: "Device, dock, serial and software inventory"
description: "Keep operational observation non-invasive and source-specific."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-DEVICES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Device, dock, serial and software inventory

## Device graph

Model device instances, containers, ports, buses, hubs and functions. A dock may expose network, USB, storage, audio and display functions; it is not always one reliable boolean. Report the associations supported by native identifiers and distinguish inferred relationships. Hotplug creates/removes generations; user aliases survive only with a defensible identity match.

List serial ports through inventory without opening them simply to identify or test availability. Active serial diagnostics require a separate capability and explicit equipment authorization. Apply the same restraint to camera, microphone, smart-card, tape and industrial devices: enumeration must not activate capture or alter control lines.

## Firmware and host identity

Read model, manufacturer, firmware, serial, UUID, architecture and boot identity when exposed. Parse binary firmware tables with strict length and offset checks; malformed manufacturer data is untrusted input. Do not use a fabricated placeholder as a hardware serial or upload identifiers by default. Validate duplicates and platform-specific redaction.

## Software and services

Collect selected software/package/service inventory at low frequency or on relevant changes. OS-native package databases differ in semantics; show provenance. Avoid queries known to trigger repair or reconciliation as a side effect. Service monitoring is observation, not authorization to start, stop or install services.

Inventory is not employee monitoring. Default fields exclude document names, browsing, keystrokes, credentials and arbitrary user-activity capture. Scope user-specific packages and process information to approved needs. Record permission denial instead of elevating the entire application.

## OS and boot state

Capture verified target identity, architecture, kernel/build and session mode. Do not rely on a potentially virtualized version API without qualification. Capability detection, not an OS string alone, selects a provider. Suspend/resume and boot boundaries change rate/history interpretation.

## Acceptance

Synthetic fixtures cover malformed long strings, bidirectional text controls, duplicate serials, dock replacement, device storms, enumeration failure and partial inventory. Lab tests verify that attaching/removing devices updates the wall without stealing focus or changing the device. A “read-only” provider must document its operational side effects before admission.
