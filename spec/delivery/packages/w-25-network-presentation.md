---
type: "SysPane Work Package Boundary"
title: "W-25 measured network presentation"
description: "Define the shared renderer projection before operational telemetry enters a native surface."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:45:15Z"}
sp_id: "SP-W25-NETWORK-PRESENTATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-NETWORK-PUBLICATION", "SP-W25-DATA-VIEW", "SP-W25-MEASURED-TIME", "SP-W25-GNOME-SURFACE-LEASE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 measured network presentation

Add the shared, toolkit-independent projection in `source/rendering/`. Consume
the existing measured DataView borrow; do not decode another wire format, retain
model pointers, sample the network, or bypass current disclosure policy. The
output is a synchronous native-renderer input, not a new portable document or IPC
message. This closes presentation meaning before the native surface accepts
operational telemetry. Native surface transport/cache erasure remains a subsequent
gate; public-marker admission alone cannot authorize this payload.

## Selection and atomic output

An explicit selection is the exact `(producer, epoch, entity_id)` triple. Match
it to the currently retained snapshot and a `network.interface` entity. Never
infer a replacement from an index, display label, table order or reused ID in a
different epoch. A new attachment without a full may still render the old exact
selection as retained. Once the new full replaces it, that old selection is
missing until the caller explicitly supplies a selection in the new epoch.

The projection emits exactly one callback per invocation. A ready frame contains
the selected triple, exact snapshot generation, lease presentation/reason and four
fields in order: receive bytes, transmit bytes, receive bytes/second, transmit
bytes/second. Each must come from `provider:native-network`, source kind
`native.network.counters`, scope `host:local`. Duplicate, missing or foreign-source
matches, a wrong entity kind, wrong unit/type or negative/nonfinite rates produce
one invalid frame with no payload. Other unrelated entities/fields are ignored.

Each field carries its original support, acquisition, presence, origin, reported
freshness, original observation/attempt UTC, measured tick, interval and optional
error code; do not copy arbitrary display names, native indices, error messages or
unrelated identity metadata. Keep reported and effective freshness separate.
The four existing metrics have 3,000,000,000 ns TTL. Use the existing model clock
comparison/freshness function and actual qualified measurement tick. Age is null
when absent or incomparable, including a retained old epoch after reattachment.
Never rebase its measurement to the new epoch or reset age on replay/heartbeat.
Lease state and metric freshness are independent: an active producer may have old
samples, and a recently disconnected producer may have a still-current sample.

Null values stay null, including first-interval rates. Exact counters are unsigned
decimal integers without grouping, padding or conversion to floating point. Rates
use three fractional decimal digits, no exponent/grouping, and round the exact
nonnegative binary64 value to the nearest 0.001, with exact halfway cases upward.
Both signed zeros render `0.000`. Preserve the underlying measured interval; this
is formatting, not a new rate calculation. Output is invariant under process
locale. Decimal arithmetic on the binary significand avoids host CRT rounding
differences. This reference representation does not preclude separately specified
localized or scaled UI formatting later.

Public no-payload outcomes are restricted, waiting, unavailable, selection missing,
invalid and capacity. Denied policy takes precedence over selection or capacity
details. Waiting means no accepted payload yet; an unavailable measured borrow
(such as a latched clock fault) supplies no old payload. Every no-payload frame
has empty selected identity/generation and default empty fields. Never supply a
partial four-field prefix, old text from a previous callback, or a hidden copy.

Account the ready frame as 1,024 fixed bytes plus the UTF-8 byte lengths of its
three identities, generation, value/unit/error-code strings, UTC subnanosecond
strings and measured tick identity strings. Default capacity is 4,096 bytes; a
smaller caller limit rejects the whole frame when accounting exceeds it, equality
is admitted. This is a deterministic payload budget, not an allocator/RSS claim.
Source model limits bound input scanning. Formatting uses at most 313 characters
for any finite binary64 rate and bounded integer operations. Allocation failure
before delivery supplies capacity without operational payload.

The callback is a synchronous borrow: no retention, export or DataView reentry.
Construct the whole frame before invoking it; propagate callback exceptions without
a second invocation. The component owns no cache between calls. Consumers that
retain native text/pixels must separately implement current-policy clearing,
bounded delivery, independent lease timers and lifecycle acknowledgement before
this adapter can enable operational data on a surface.

## Fixed acceptance

| Case | Required results |
|---|---|
| `NVIEW-VALUES` | uint64 maximum remains `18446744073709551615`; zero remains `0`; first rates stay null; valid measured rates/intervals and status axes remain exact. |
| `NVIEW-FORMAT` | `0.0625` -> `0.063`, `1.0625` -> `1.063`, adjacent binary64 values lie on the correct side; signed zero/subnormal values -> `0.000`; maximum finite double formats to its exact integer plus `.000`; a changed global locale changes no result. |
| `NVIEW-STATES` | Current just before TTL and stale at equality; heartbeat does not refresh measurements; failed acquisition preserves values/original times; disconnect changes lease presentation without changing source metadata. |
| `NVIEW-SELECTION` | Wrong producer/epoch/entity cannot bind; removal gives missing; a reused entity ID in another epoch does not inherit selection; pending new attachment retains the old identity with incomparable age until a full replaces it. |
| `NVIEW-BOUNDS` | Exact byte-limit equality succeeds, one byte less yields empty capacity; missing/foreign-source/wrong-kind candidates produce one empty invalid result; no callback prefix. |
| `NVIEW-LIFETIME` | Denial erases accessible payload; a later permitted policy still needs a new full; invalid clock cannot project; reentry is rejected; callback exception propagates once and releases the original borrow. |

Build and run these fixed cases on Windows/Linux and the historical portable
profile. Include ordinary regression suites, component checks, historical imports,
relocated smoke packages and exact source/artifact records. These prove a reusable
projection boundary, not native text visibility, accessibility, renderer watchdogs,
installed policy, or a complete desktop edition. Integrate with a native surface
only through the separately closed admission and policy-erasure boundary.

## Existing native collector consumer

The finite CollectorProbe also calls this production projection component after
its existing imported/retained/revoked events. Its explicit development selection
is `producer:network`, the current connection epoch and `network:interface:1`;
this is not persisted selector inference or a product default. The sink consumes
its result synchronously into the already admitted private test pipe and retains
nothing after the borrow. This narrowly scoped test serialization does not grant
production export, native caches or arbitrary operational disclosure.

All eight existing native collector scenarios must independently compare projected
values, units, original measurement/interval, acquisition/freshness and retained
lease state to the already verified native document. Python rational arithmetic
computes rate-text expectations independently. Policy revocation must yield the
empty restricted frame. Preserve only aggregate outcomes/counts in public evidence;
raw operational values remain in memory or the existing ignored private failure
record. No new wire protocol or collector lifecycle is introduced.

## Explicit retained projection without clock qualification

The first native crash run showed `clock.peer_exited`: the native stream correctly
refused a fresh measurement-clock read after its held peer exited. Preserve that
failure. Do not reopen or relax the stream's clock qualification. The existing
measured-time contract already permits ordinary, explicitly retained presentation
when measured projection is unavailable.

Provide a separate `project_network_retained` call. It requires current policy and
an existing retained lease presentation; active state without a qualified clock
returns unavailable. It retains exact allowed values, original metadata and selected
identity, but age is null and every non-null value has effective stale freshness
(unsupported stays not-applicable). It never treats an old qualified tick as now.
The measured API still fails closed on an invalid clock, with no implicit fallback.
The collector's retained event uses this explicit path without querying the departed
peer. Native and portable checks require unknown age/stale values on this path;
restriction takes precedence and provides no payload through either API.

The historical locale fixture links three additional pinned static-CRT imports:
[GetDateFormatW](https://learn.microsoft.com/en-us/windows/win32/api/datetimeapi/nf-datetimeapi-getdateformatw),
[GetTimeFormatW](https://learn.microsoft.com/en-us/windows/win32/api/datetimeapi/nf-datetimeapi-gettimeformatw)
and [GetTimeZoneInformation](https://learn.microsoft.com/en-us/windows/win32/api/timezoneapi/nf-timezoneapi-gettimezoneinformation).
Microsoft documents Windows 2000 as their minimum client. Add these specific names
to the declared import closure while retaining the original failed audit; keep all
other DLL/ordinal/header/import restrictions. This is documentary API-floor evidence,
not guest execution or proof of CRT fallback behavior on XP/7.
