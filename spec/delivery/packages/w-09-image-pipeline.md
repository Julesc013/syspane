---
type: "SysPane Work Package"
title: "Bounded pinned image pipeline"
description: "Static image admission, isolated native decoding and exact premultiplied fit geometry before scene integration."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T00:00:00Z"}
sp_id: "SP-W09-IMAGE-PIPELINE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-SCENE-CONTENT", "SP-W09-NATIVE-CHART"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded pinned image pipeline

Implement the image decoder and fit boundary for the existing scene 0.3 content.
Keep PNG, JPEG and static SVG; do not reinterpret bytes according to a filename.
Only immutable bytes from the exact admitted manifest/path/SHA256 may enter an
operational image job. Document/resource admission alone never authorizes a codec.
Scene integration must additionally bind asynchronous results to current resource,
policy and scene identity and erase reachable decoded pixels on revocation.

## Decoder contract

Encoded input is nonempty and at most 8 MiB (SVG at most 1 MiB). Source dimensions
are positive, at most 4096 per axis and at most 4194304 pixels. Reject oversize
dimensions before a native raster allocation; resizing an oversize source is not
a substitute. Decoded output is tightly packed, premultiplied RGBA8. Convert each
RGB component by (component*alpha+127)/255. Alpha-zero pixels have zero RGB.
Native decoders are profile-specific and pinned; a decode error never returns a
partial raster or a successful blank placeholder. The original encoded digest is
part of the result identity even when harmless metadata is omitted for decoding.

PNG admission checks the signature, complete bounded chunk framing, CRCs, one first
IHDR, required IDAT and terminal IEND without trailing bytes. Unknown critical
chunks, APNG control/frame chunks and invalid dimensions reject. Preserve IHDR,
PLTE, tRNS, IDAT and IEND for decoding; omit other ancillary metadata, including
compressed text and profiles, so it cannot trigger unrelated decompression.
Interpret decoded channel values in the existing RGBA8 rendering space; do not
apply image ICC/gamma metadata in this profile. The native decoder still validates
bit depth, color type, palette, interlace and compressed sample validity.

JPEG admission checks complete marker/entropy framing, terminal EOI without
trailing bytes, one 8-bit sequential/progressive frame and bounded dimensions.
Preserve required coding markers, bounded JFIF/Adobe color metadata and entropy;
discard comments and other APP metadata after extracting EXIF orientation.
Accept one well-formed orientation value 1..8; duplicate/conflicting/malformed
orientation rejects. Missing orientation means 1. Apply its mirror/rotation before
fit. ICC thumbnails/profiles are not separately decoded. Native codec color
conversion is part of the pinned target result; exact PNG/SVG fixtures and fixed
JPEG interior/dimension expectations qualify it independently.

SVG is UTF-8 XML with the unprefixed SVG namespace on its single root. Reject compressed SVG, DTDs,
entity declarations, processing instructions other than the XML declaration,
foreign namespaces/elements, script, foreignObject, event handlers, XInclude,
animation/set elements, xml:base and external or embedded resource references.
Local fragment href and url(#id) references remain allowed; referenced IDs use
ASCII letters/digits/underscore/dot/colon/hyphen, start with a letter/underscore,
and contain at most 128 characters. IDs are unique and every reference must resolve.
CSS supports ordinary static selectors/properties with local fragment URLs;
reject at-rules and animation/transition declarations. Decode CSS escapes and
comments before checking URLs. Never let XML/CSS escaping bypass those checks.
Bound depth to 64, elements to 16384, attributes per element to 64 and combined
attribute/text bytes to 1 MiB. Require explicit positive integer width/height in
unitless CSS pixels or px, subject to the source raster limit; viewBox may control
the drawing within that extent. Reject unknown/active rendering features explicitly
rather than silently executing them. Richer safe SVG features remain an explicit
profile extension, not an implicit permission to fetch resources or animate.

## Execution and lifetime

Linux uses the installed pinned GdkPixbuf PNG/JPEG/SVG loaders in a dedicated native
worker. It receives bytes over inherited bounded IPC; it receives no resource path,
base URI, network address or mutable source directory. Before parsing, require
parent-lifetime death, no-new-privileges, no core dumps, a 256 MiB address-space
ceiling, 2 CPU seconds and a 3-second independent real-time worker limit. The owner
also enforces a 3-second deadline and caps result bytes at 16 MiB plus fixed header.
Cancellation discards output and requests stop; no successor may reuse that job's
identity until actual child termination is observed. Startup, timeout, signal,
malformed reply and input failure are distinct unsuccessful outcomes. Ordinary
scene painting must not synchronously wait for decoding or publish late results.

This boundary is complete only with actual subprocess results and kill/reap
evidence. OS limits are required because library parsing limits do not bound total
CPU or memory. Application-level reference rejection is required in addition to
the loader's restrictions. These controls are not a claim of a general-purpose
hostile-code sandbox or permission to load arbitrary plugins.

The worker requires Landlock ABI 3 or later: deny filesystem access except read-only
native libraries, font data/configuration/cache and the dynamic-loader cache.
Seccomp admits only the x86-64 syscall ABI, denies networking, exec, process forks,
signal sending, cross-process inspection/memory/descriptor access and namespace/mount changes. Native library threads
may be created; ordinary child processes may not. The profile locks installed codec,
plugin, relevant headers and native kernel identities. Other kernel/toolkit profiles
need their own admitted mechanism and evidence.

The native ImageJob owner launches the held canonical ELF through the existing
Child abstraction, with only supplied stdin/stdout/stderr, the temporary held ELF
descriptor (closed by the worker), and a clean environment. Its request is four
big-endian length bytes followed by exactly that many encoded bytes and EOF.
Success is `SPIM0001`, big-endian uint32 width and height, then exact RGBA bytes and
EOF. Only exit zero, complete reply, valid premultiplication and observed child
termination yield ready. Each poll sends at most 256 KiB and reads at most 256 KiB
of pixels plus 1025 error bytes; the total error stream is capped at 1024 bytes.
Replies cannot declare more than 4194304 pixels. No background thread or callback
owns output; take moves it once after reaping. The original input digest remains
bound to the job. Cancel makes take impossible, erases parent payload buffers and
requests exact-child stop; polling observes the termination before cancelled.
Destruction retains Child's stop/reap-or-fatal cleanup rule. Startup errors throw
before a usable job exists. Operational scene ownership must keep stopping jobs
until their proof arrives and must not block a rendering loop on destruction.

## Portable fit and orientation

An immutable raster has positive dimensions at most 4096, at most 4194304 pixels,
exactly width*height*4 bytes and RGB no greater than alpha. Reject malformed input.
Fit output is at most 2048 per axis and 4194304 pixels, within a caller-lowered
pixel budget. Contain/cover preserve aspect with k=min/max(W/sw,H/sh); stretch
uses the two independent ratios. Center both axes exactly; letterbox pixels are
transparent. For each destination pixel center, invert the transform to source
pixel-center coordinates. Bilinearly interpolate four edge-clamped premultiplied
samples using exact rational weights, rounding half up once per output channel.
Contain includes its left/top boundaries and excludes right/bottom boundaries.
Do not round the intermediate fitted rectangle or introduce hidden crop offsets.
EXIF orientations follow the standard eight mirror/rotation mappings; values
5..8 exchange dimensions. Source pixels and input ownership are never mutated.

## Verification and continuation

Freeze exact geometry expectations using independent Python Fraction calculations
before production code. Cover odd/fractional centering, contain letterboxes, cover
crop, stretch, translucent edges, all orientations and rejection budgets. Native
cases cover all three formats, mismatched media, truncation, malformed/oversize
data, animation, entity/external/CSS references, metadata bombs and controlled
worker timeout/cancellation. Preserve original fixtures and failed attempts.

Use ordinary profile configure/build/test commands with workspace preflight.
Record codec/header/plugin/runtime identities. Shared fit must pass all three
development toolchains; native decoding is initially a Linux experiment. Continue
with policy-owned asynchronous SceneSurface integration and external pixels/AT-SPI
erasure before enabling operational image widgets. Windows/Mac adapters, richer
format profiles and all complete desktop editions remain in the existing graph.

References: [GdkPixbuf incremental loading](https://docs.gtk.org/gdk-pixbuf/class.PixbufLoader.html),
[GLib markup callbacks](https://docs.gtk.org/glib/struct.MarkupParser.html),
[librsvg resource rules](https://gnome.pages.gitlab.gnome.org/librsvg/doc/src/rsvg/lib.rs.html)
and [librsvg application resource limits](https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/security.html).
