# Architecture and ownership

SysPane shares semantic contracts and a native engine where toolchains permit.
Platform adapters own OS acquisition, controls, rendering and desktop hosting.
Constrained editions may substitute specific components while passing applicable
conformance fixtures; they do not create a second product specification.

Observation feeds a demand scheduler, typed state, history and presentation.
GUI/editor/CLI/import operations feed one policy-checked revision transaction.
Maintenance feeds a separate qualified setup provider. Ordinary presentation
has no installation authority.

The model knows no native handles or GUI types. Collectors publish typed data;
presentation never calls them directly. Native controls edit through commands.
Application composition roots connect selected adapters. Windows retains
`SysPane.exe` and `SysPane.Surface.exe`; extra workers exist only for a concrete
fault, privilege or lifecycle boundary.

The independent diagnostic path has fewer dependencies than the components it
helps recover. Process liveness, source freshness and visible rendering progress
are measured separately. Screensaver roles share scene semantics while preserving
their own host lifecycle, disclosure limits and demand leases.

See [composition](../../spec/architecture/composition.md),
[portability](../../spec/architecture/portability.md),
[recovery](../../spec/architecture/recovery.md) and
[repository ownership](../../spec/foundation/repository.md).

The measured network presentation component in `source/rendering/network_view.*`
consumes a synchronous DataView borrow. It selects an exact producer/epoch/entity,
keeps lease state separate from metric freshness, and formats counters/rates without
native toolkit dependencies. It owns no cache or IPC endpoint. A native backend must
close its own delivery, policy clearing and acknowledgement contract before retaining
operational text or pixels. The existing collector probe exercises the shared
projection over actual measured data through its private development pipe.

## Native retained network cache experiment

The optional GNOME `NetworkCache` adapter accepts one bounded selected frame from
a retained, native-PID-authenticated laboratory relay. A policy revision owns its
single cache; every new revision clears it before another full frame is admitted.
Revocation, owner loss and owner-lease expiry remove payload references and native
actors. A local clear acknowledgement and externally observed pixel disappearance
are separate facts. The public diagnostic reports counts/status only.

The finite relay uses the existing tested C++ CollectorProbe and independently
checked documents. Raw operational values and pixel crops remain in private owned
evidence. The tile explicitly shows retained samples with unknown age; its GLib
timer is not a qualified replacement for the C++ CLOCK_BOOTTIME measurement domain.
Live clock integration, general IPC, installed policy and a production controller
remain separate work. See the [package](../../spec/delivery/packages/w-25-native-network-cache.md).

## Live measured drawing and independent render supervision

The later `NetworkLive` experiment uses the shared C++ `NetworkView` directly
through `networkSession.js`. Its asynchronous native session owns one supervised
source, socket, revocable model, serialized write queue and cancellable read.
Drawing consumes the model's values, age and separate freshness/lease statuses.
It does not calculate a competing telemetry state in JavaScript.

`RenderSession` reuses that process/socket owner. Its native `HealthView` exposes
the same recovery-health parser used by native supervisors. The independent
RecoveryProbe child owns the render deadline; the shell owns the pending drawing
generation and stage callback. A completed operational draw stages that generation,
and subsequent after-paint instrumentation acknowledges it. Heartbeats do not
complete drawing. Independent pixel evidence is still required because this
callback alone cannot establish visibility or correct displayed content.

Both owners erase their retained state before asynchronous teardown. A nonzero
child exit remains failed even when a sibling already initiated closure. The
native health view expires a silent watcher, while the watcher can detect a
stopped shell independently. A stopped shell cannot repaint: the experiment
records its surviving pixels and verifies erasure after confirmed resume. The
existing consumer lease can expire concurrently; it is never extended to make
this test pass. See the [render-watch package](../../spec/delivery/packages/w-25-gnome-render-watch.md).
Automatic renderer replacement, product demand/policy and editor recovery remain
separate implementation boundaries.
