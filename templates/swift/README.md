# Gota runner: Swift

Files:

- `Gota.swift` — the harness. Copy as-is; do not edit.
- `runner.swift` — your code. Replace the `example` op.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
swiftc -O Gota.swift runner.swift -o runner
./runner 65536 0.5 2.0
```

The seam: `Gota.run(IMPL) { b, data in ... }` parses `CommandLine.arguments`, allocates
the buffer, and hands your closure a `Gota` bencher and the buffer (`inout [UInt8]`); you
call `b.bench(name, op)` once per operation.

Notes:

- The runner is an `@main` type, not top-level code — `swiftc` only allows top-level
  statements in a file literally named `main.swift`, and the harness builds two named
  files together, so `runner.swift` declares `@main struct Runner`.
- `data` is an `inout [UInt8]` handed to your closure; the `op` you pass to `bench` is
  non-escaping and may capture it (write in place, or consume a computed value into it as
  a sink so `-O` can't delete the work).
- Only the standard library + Foundation are used (`DispatchTime.now().uptimeNanoseconds`
  for a monotonic clock, `String(format:)` for the two-decimal rates). Compiled ahead of
  time, so the protocol's warmup phase costs nothing but keeps the loop uniform.

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
