---
type: "SysPane Work Package"
title: "Policy-owned collection tables"
description: "Render identity-aligned collection columns with bounded native grid geometry and explicit incomplete states."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T21:40:00Z"}
sp_id: "SP-W09-TABLE-SURFACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-SCENE-SURFACE", "SP-W09-BINDINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned collection tables

Extend W-09's existing scene surface to table widgets using scene 0.2 and binding
0.1. Ordered bindings are ordered columns. Each is a collection selector; all
descriptors must be equal after removing only `field`. Fields must be distinct.
The selector's scope/type/predicates/sort/limit determine the same row set for every
column. No new behavior is hidden in extensions, no schema is reinterpreted, and
unsupported combinations remain preserved with a whole-scene alternative.

The admitted capability has one to sixteen columns, an authored selector limit
of at most 64 rows and at most 256 projected cells. A scene may perform at most
256 binding projections per frame, counting scalar bindings and table columns.
These are capability budgets; larger valid documents produce surface.capacity.
Invalid table combinations produce surface.unsupported. They are not new authored
schema validation failures. Charts, images and richer column formatting remain
required separate capabilities.

## Rows, cells and incomplete input

The first column owns order and total/truncated facts. Match every following cell
by the exact `(producer, epoch, entity)` tuple, with the same snapshot generation.
Never zip by arrival position, display name or interface index. Any inconsistent
row set, total or truncation produces surface.table_identity and no partial frame.
Stable keys survive reorder; a new epoch gives new keys. Presentation retains these
keys for future native selection/editing without exporting a DataView pointer.

Resolve all columns on the surface's serialized loop with one supplied `now` and
the same qualified ticks. A binding denial restricts the whole scene and erases
payload. Any non-matched column suppresses all table rows: choose the outcome by
denied, invalid, capacity, ambiguous, unsupported, pending, empty precedence.
Show the scalar surface's existing outcome label, not data from other columns.
Missing cells within a matched row retain that identity and the existing cell
outcome label. Row presence is independent of the requested metric's availability.

Format each matched cell with the scalar contract's exact value/unit line and
mandatory status line, excluding the scalar title. Accessible cell content also
includes the existing support/acquisition/presence/freshness/origin/lease/age axes.
No private provider error message is copied. Metadata fields retain Configured
origin. There is no implicit unit conversion, name-based join or history store.

Column headers are their invariant field identifiers. Column renaming/localized
labels will require explicit versioned authoring; do not invent them from telemetry.
The title is the existing widget title. A matched table always shows
`Showing N of M rows`, including complete, truncated and empty outcomes; empty is
`Showing 0 of 0 rows`. Truncation never silently drops the fact that more rows exist.
For a non-matched, non-empty table, show its outcome label below the title and no
headers or cells. Accessible text is title, summary, then each row in display order:
`Row producer/epoch/entity` followed by each `field: cell-accessible-content`.
Identity is carried structurally too; the slash-delimited label is not a key parser.

## Native grid and ownership

Measure unwrapped title, summary, each header and every cell with the existing
native text adapter. Column width is the maximum native raster width of that
header and its cells. Header-row and each data-row height are their maximum raster
height. Horizontal gap is ceil(8 * scale) device pixels; vertical gap is
ceil(4 * scale). Place title at (0,0), summary below title plus vertical gap, headers
below summary plus vertical gap, then data rows separated by vertical gap. Every
cell is top-left aligned. Table width is the maximum of title, summary and the sum
of column widths plus inter-column gaps. Height ends at the final row, with no
trailing gap. These exact algorithms operate separately on each resolved display.

Fill the table background once, then draw transparent text rasters with the
effective foreground. High contrast overrides both colors as in the text adapter.
Do not repeatedly blend the authored translucent background under each cell.
No wrapping, clipping, ellipsis or optional removal substitutes for readable layout.
Supply the completed table extent to shared layout, keeping the whole-scene
alternative if it does not fit. Group ordering and scene OVER composition remain.

Retain typed table rows/cells, cell pixel rectangles relative to the table, one
accessible string and the final native raster only inside SceneSurface's frame.
The registered native clear callback covers copied table accessible content too.
All existing revocation/regrant/source/close/reentry rules apply. Cell strings,
identities, headers and duplicate accessible text count toward the existing
262144-byte frame payload budget. Display buffers, prior leaf rasters, current
table parts and its destination share the existing 8,388,608 construction-pixel
ceiling. Final table raster remains at most 2048 pixels per axis/4,194,304 pixels.

## Acceptance and execution

Archive original expected component cases before implementing: two columns/two
rows, exact zero/null/uint64, stable keys and reorder, missing cell, incomplete
column, explicit truncation, no-match, retained/stale source, resource/row/column
limits, inconsistent descriptors, high contrast/alpha, policy erasure and regrant.
Keep every original scalar test; direct-pinned tables stay unsupported.

Extend the independent owned-Xvfb/AT-SPI observer with a two-column/two-row table.
Build expected pixels from fixed values and independently composed native text
rasters using the specified grid algorithm. Compare the external root capture and
actual accessible names after initial data, replacement, revoke, stale delivery,
regrant, fresh attachment and source loss. Preserve both deliberate pixel/name
retention controls and the original 200 ms deadline. No user desktop is used.

Use ordinary configure/build/test commands and bounded owned outputs. Run Linux
surface/text/layout/binding regression checks plus the full Linux suite after
integration. Changes are Linux-only; preserve Windows baselines without claiming
new Windows table implementation. Update component inventory, work graph, handoff,
README/TODO and sealed specification. W-09 and all complete releases remain open.
