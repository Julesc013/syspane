---
type: "SysPane Work Package"
title: "Bounded measured chart history"
description: "Exact sample admission, discontinuities and bounded retention before native chart drawing."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T22:54:40Z"}
sp_id: "SP-W09-CHART-HISTORY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-SCENE-CONTENT", "SP-W09-BINDINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded measured chart history

Continue W-09 with the shared sample owner used by the forthcoming native chart
adapter. Preserve scene 0.3's existing duration, point, interpolation and axis
fields. This package closes sample retention; it does not enable chart painting,
choose pixel geometry or claim native accessibility/erasure qualification. Existing
SceneSurface continues its explicit unsupported alternative until those gates pass.

## Admission and identity

One ChartHistory belongs to one unchanged widget/binding in one serialized owner.
Construct it with window_ms (1000..3600000) and max_points (2..4096) from validated
content. Invalid bounds throw chart.settings. Its input is a current-policy
singleton BindingFrame borrow plus an optional current producer-qualified Tick.
Call observe for every admitted publication affecting the selection, before a
later publication can replace it, and at presentation/expiry. Repainting alone is
not sample acquisition. There is no interpolation, counter differentiation, unit
conversion, sample synthesis or persistent recording in this component.

Stream identity is producer, epoch, entity, field, source, unit, numeric type,
origin, clock ID and clock scope. Snapshot generation is provenance, not identity.
Any identity change discards the old stream before accepting the new one; names
and interface indexes cannot transfer history. Identity strings total at most
8192 bytes. Bindings selecting metadata or nonnumeric values return unsupported
and erase history. Preserve uint64 as uint64 (including values above 2^53); finite
binary64 stays binary64. Null does not become zero or change the previous numeric
type. With no previous numeric stream, null leaves no identity or points.

Append only a matched nonmetadata numeric observation that is supported, present,
successfully acquired, effectively current, and on an active producer lease, with
a measured_at Tick in the same nonempty epoch/clock/scope as supplied now. A
configured or derived numeric observation follows the same admission rules and
retains its origin. Copy no error message, label or other observation payload.
The observation entity must equal the row entity; identities/field/source/unit
must be nonempty. A matched frame must contain exactly one row/total, no truncation.

Repeated measured timestamp and identical numeric value is duplicate, even in a
new snapshot generation. It never appends or changes original point provenance.
A different value at the same measured timestamp is conflict; a decreasing
measurement or current tick is clock_fault. Future measurements are clock_fault.
Decreasing snapshot generation is conflict. These faults erase payload and latch
until explicit clear; unrelated later samples cannot conceal them. Signed binary64
zero compares equal. Domain changes establish a new stream rather than subtracting
incomparable clocks. Arithmetic never adds a duration to a tick.

## Window, capacity and discontinuity

The inclusive window is [max(0, now_ns - window_ms * 1000000), now_ns]. Advance and
prune on each valid supplied clock, including duplicates, retained leases and
failed/null observations. Missing now freezes the last horizon, admits no sample
and marks clock_unknown; it never substitutes reception time. A mismatched now is
a clock fault. Keep the last admitted sample's timestamp/value/generation even
after all visible points expire, so replay cannot resurrect expired history.

Keep the newest max_points eligible samples in that window, in measurement order.
FIFO removal is explicit bounded retention, not a decimation algorithm. Report
capacity_truncated while the newest capacity-evicted timestamp remains within the
current inclusive window; clear that fact once it ages out. Window expiry alone
does not count as capacity truncation. No hidden look-behind sample is retained for
line clipping. Each retained point carries measured nanoseconds, exact number,
first-admitted snapshot generation and joins_previous. The first visible point
always has joins_previous=false.

Every noneligible matched observation (null, stale/unknown freshness, failed,
pending/disabled acquisition, absent/unknown presence, unsupported/unknown support,
retained/empty lease or missing measured clock) creates a pending break. Do not
append its possibly retained value. An explicit gap call also marks a break.
The next newly admitted point has joins_previous=false. A duplicate cannot heal
that break. No inferred sampling cadence can prove missing delivery; the owner
must forward transport gaps, disconnect, expiry and skipped admission context.
Retained points remain available only for the same resolved stream and a current
authorized borrow, together with the current binding's mandatory status axes.

Nonmatched selection (including ambiguous/pending/empty/capacity) erases history
and returns that selection with no payload. Row denial or acquisition denial also
erases. Structural invalidity erases and reports invalid. Thus disappearing and
later reappearing selection cannot silently bridge an unobserved interval.

## Lifetime and integration gate

observe delivers exactly one synchronous ChartView borrow; the sink cannot retain
references, export payload or reenter this history. All methods reject reentry.
Sink exceptions propagate once after the state transition, with the borrow released.
clear removes points, identity, replay high-water, truncation and faults. This is
logical application-state erasure, not forensic memory sanitization. The logical
payload ceiling is 8192 identity bytes plus 32 bytes per retained point and one
32-byte replay record; allocator/RSS overhead is outside that accounting.

The enclosing native owner must clear histories before every policy change,
resource denial, binding/scene replacement, close, native-clear failure or clock
fault. Retention requires explicit current history-channel disclosure permission
in addition to the existing desktop/accessibility permissions; synthetic tests
do not confer that authority on an installed component. A grant requires fresh
attachment and full state. It must limit aggregate
histories and account for them separately from temporary frames; ordinary repaint
frame erasure must not erase valid history. This component is not an authorization
engine and has no standalone operational export API.

Before enabling native charts, supply current clocks for every producer relevant
to selector resolution on each admitted publication; incomplete context must
produce an explicit break, never a false complete timeline. Close exact axis
normalization (including near-uint64-limit values), linear/step pixel geometry,
point reduction at device resolution, readable metrics, status/accessibility and
aggregate budgets in the next linked package. Verify native policy erasure with
the existing independent pixel/accessibility observer and deliberate faults.

## Fixed acceptance and execution

Archive this package, interface and tests before production implementation. Eleven
scene.CHART-* families cover bounds; inclusive nanosecond windows/uint64 clocks;
FIFO and expiring truncation; replay after expiry and conflicts; all gap axes;
identity/epoch changes; clock failures; selection erasure; exact numeric values;
borrow/reentry/clear; and actual telemetry admission plus shared singleton binding.
The wire case delivers several samples before any paint and must retain all three.
Run ordinary workspace preflight/configure/build and CTest on all three development
profiles, preserving exact inputs, failures and artifacts. Historical compiler
execution on the modern host is not historical OS qualification. W-09 stays open.
