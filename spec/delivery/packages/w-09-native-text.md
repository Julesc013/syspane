---
type: "SysPane Work Package"
title: "Native Linux text metrics and raster adapter"
description: "Bounded plain-text shaping and painting with explicit native metrics, fallback and pixel ownership."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T20:37:20Z"}
sp_id: "SP-W09-NATIVE-TEXT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-LAYOUT", "SP-W09-BINDINGS", "SP-RENDERING", "SP-SCENE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native Linux text metrics and raster adapter

Continue W-09 with a reusable Linux Pango/Cairo text backend. This prerequisite
measures and paints plain text supplied by its owner; it does not infer text/value,
table, chart or image content from scene extensions. Preserve scene 0.2 and theme
0.1. Windows and Mac text adapters, complete native scene composition, accessibility,
current-policy cache ownership and visible activation remain required.

## Input, ownership and bounds

One synchronous call consumes immutable text, a validated theme 0.1, one foreground
semantic token (foreground/warning/error/muted), an explicit language, optional wrap
width, rational scale and contrast mode. It returns owned raster bytes and metrics;
there is no background work or application-level layout/text cache. Pango objects
are destroyed before return. Font system caches are external native dependencies.
The caller owns returned bytes and must discard superseded results. This initial
adapter is admitted for authored/public text and synthetic laboratory values only.
It does not grant retention/export of policy-bound DataView payload: live binding
use awaits a separately admitted cache erasure/accessibility owner.

Text is valid UTF-8, at most 4096 bytes and 1024 Unicode scalars, with at most 64
explicit lines. Reject embedded NUL, CR, TAB and C0/C1 controls other than LF; never
silently truncate, replace malformed encoding or interpret markup. Unicode shaping,
combining marks and bidirectional controls remain text handled by Pango. Empty text
retains one line's readable logical height. The language is 1..35 ASCII letters,
digits or hyphens, beginning with a letter. Pass it explicitly; do not use the
process locale. Theme font families obey the schema's 128-scalar bound, reject
controls and are passed as family names, never parsed as font descriptions.

Size is theme size_dip, 9..72, set as an absolute native size in DIP. Use normal
weight/style, automatic paragraph direction, left alignment (native auto-direction
selects RTL alignment), word/character wrapping, no ellipsis, no markup and no
implicit line limit. Wrap width, if present, is 1..32768 DIP in 1/64-DIP units.
Maximum resulting line count is 1024. Scale numerator and denominator are 1..16,
ratio 1/4..8. Font metrics use 96 DPI, grayscale antialiasing, disabled hint metrics,
disabled hint style and unrounded glyph positions; raster scale does not change
the DIP measurement context. Native missing glyphs remain visible and are counted.
Report actual font families used, sorted uniquely, so fallback is inspectable.

## Measurement and painting

Return native ink and logical rectangles, their enclosing union, first baseline,
line count and missing-glyph count. Rectangles are signed 1/64 DIP, with leading
edges rounded down and trailing edges up from Pango units. Negative bearings and
nonzero RTL logical origins must survive measurement. The enclosing union's size
is the readable extent for this text block. Return separate unwrapped preferred
extent; do not mistake constrained wrapping for the preferred width. A future
widget composer owns label/status padding and its minimum-width policy.

Measure independently of output scale. Translate the union's origin to one pixel
of guard space, then scale and draw the same shaped layout. Raster width/height
are ceil(union size * scale / 64) + 2. No clipping/ellipsis may make an oversized
result pass. Reject extents beyond 32768 DIP, dimensions beyond 2048 pixels, or
more than 4,194,304 pixels before allocating the image. A caller may lower the
pixel budget to a positive value; it cannot raise it. Native allocation/render
failure returns text.native; invalid inputs text.input; raster/extent exhaustion
text.capacity. Existing theme schema errors retain their authored validator code.
No partial raster is returned on failure.

Use sRGB straight-alpha theme colors as Cairo source RGBA. Paint the entire raster
background with SOURCE, then glyphs with OVER. Output is tightly packed,
premultiplied RGBA8 in explicit byte order, independent of Cairo's native-endian
ARGB32 storage. Every RGB byte is at most alpha; transparent black is all zero.
Contrast mode authored uses the requested token and background. Explicit light
mode uses opaque black on white; dark uses opaque white on black for every token.
These are owner-selected accessibility overrides, not automatic OS detection.
Status meaning must also be conveyed by text by the later widget composer.
Rasterize glyphs into an alpha coverage mask, including color-font layers, then
apply the chosen foreground. Embedded glyph colors cannot override semantic or
contrast colors. The pixel ceiling bounds each native surface and returned buffer;
it is not an RSS bound for the native font/shaping libraries.

## Independent acceptance and continuation

Before implementation, preserve the package and independent Python oracle. Drive
the native adapter through a bounded one-shot probe and inspect raw raster bytes.
Cover empty/transparent text, exact opaque/half-alpha backgrounds, foreground
premultiplication, literal markup, combining normalization, Arabic/mixed direction,
wrapping/newlines, scale-invariant DIP metrics, fallback/missing glyph reporting,
all tokens and contrast overrides. Reject malformed UTF-8, controls, text/line/font/
language/scale limits and pixel exhaustion. Repeated calls must produce identical
bytes in the pinned environment and may not mutate the theme.

Record selected installed package/library and all installed font/configuration
identities for the native run. These pins identify the development experiment, not
a portable glyph golden or complete dependency/reproduction closure. Use ordinary
preflight, configure, build and test commands; test native.TEXT-RASTER on Linux and
composition checks on all three profiles. Preserve failures and exact source,
oracle, artifact and environment identities. An offscreen native raster pass is
not external desktop visibility, behind-icons placement, accessibility, policy
erasure or historical OS qualification. Continue to bounded widget composition,
native cache erasure and independent host activation; W-09 stays in progress.

API references: [Pango extents](https://docs.gtk.org/Pango/method.Layout.get_extents.html),
[plain text](https://docs.gtk.org/Pango/method.Layout.set_text.html), and
[Cairo image surfaces](https://www.cairographics.org/manual/cairo-Image-Surfaces.html).
Use the installed 1.52.1/1.18.0 headers; newer documentation does not change pins.
