---
type: "SysPane Specification"
title: "Network telemetry and diagnostic presentation"
description: "Join device, interface, protocol, connectivity and history without flattening their meanings."
tags: ["telemetry"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-NETWORK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-SCHEDULER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Network telemetry and diagnostic presentation

The [native acquisition prerequisite](../delivery/packages/w-25-network-acquisition.md)
now defines and implements the bounded raw table/counter boundary. Its
[handoff](../delivery/network-acquisition-handoff.md) separates actual native reads
from the notification, identity, measured-publication and complete network-view
requirements below. Raw interface keys must not become persistent selectors.

The [supervised publication experiment](../delivery/network-publication-handoff.md)
now sends real Linux counters and interval rates through measured telemetry, with
source lifetimes, retained failures and independent child recovery. This covers a
bounded part of the network view; the topology, address, routing, resolver, device
and connectivity requirements below remain open.

## Required view

Represent the complete dynamic adapter inventory, including disconnected/disabled physical and virtual adapters where the native source permits. Join device presence and problem state, interface administrative/media/operational state, IPv4/IPv6 addresses, routes/gateways, configured resolver information, network profile and source-specific connectivity assessment. Do not cap the inventory at sixteen entries or store only one address per family.

Sort by user-defined priority, physical/virtual category, operational class, interface type and name. Default sorting is stable; transient throughput does not continuously reorder the wall. Retain full data in the inspector even when a compact scene collapses columns.

## Windows provider plan

Candidate sources from the design discussion are SetupAPI/Configuration Manager for device identity, IP Helper for interfaces/addresses/routes, NLM per-network and per-connection assessments, PnP notifications and Native Wi-Fi when necessary. Each API must enter the implementation API inventory with exact minimum OS, required permissions, imports, lifecycle and test coverage before use. The specification does not claim that all those APIs exist on XP or old NT.

For XP/7 tracks, qualify an appropriate available API set and reduced capability declarations; missing NLM or modern interface structures must not be manufactured by guessing. Preserve device/interface joins and IPv4/IPv6 distinctions to the extent the target exposes them.

A callback is an indication, not a complete snapshot. Subscribe-before-enumerate and generation-safe reconciliation are required. Explicitly test DNS-only changes, disabled/unbound adapters, VPN split routing, interface-index reuse, multiple IPv6 addresses, temporary addresses, DHCP/APIPA transitions, sleep and device storms.

## Cross-platform meaning

Linux native netlink/network-manager sources and macOS SystemConfiguration/system APIs are implementation candidates. Keep their assessments source-specific. “Windows reports Internet access”, a network manager assessment and a successful destination probe are not the same fact. A probe must record target, method, family, selected source/interface context and observation time.

“Cable connected; configuring” is a valid useful intermediate state. Do not delay its display until address assignment or Internet assessment finishes. Configured DNS servers are not a complete description of effective DNS policy, VPN split DNS, DNS-over-HTTPS or application-specific resolvers.

## Sampling and correctness

Link and address topology are event-first, with bounded reconciliation for gaps. Throughput is a sampled counter delta divided by actual monotonic elapsed time. Detect counter reset, wrap and interface generation changes. A zero rate can mean no traffic only after a successful interval; it does not mean the interface is down.

IPv6 addresses include scope where required. Gateway and route presence do not prove reachability. Do not expose SSIDs, public IPs or device addresses against display/privacy policy. Copy actions use canonical values, never truncated visible strings.

## Acceptance

Use a controlled changing network fixture in deterministic tests, then real interface actions on leased lab hosts. Measure notification-to-publication and externally visible change, as well as physical stimulus-to-notification where available. A one-second fallback cannot be claimed if its actual configured interval is longer. Document each field's acquisition and latency coverage.
