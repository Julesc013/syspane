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
