# Gota runner: Zig

Targets Zig 0.16.

Files:

- `gota.zig` — the harness. Copy as-is; do not edit.
- `runner.zig` — your code. Replace the `exampleOp` and its `bench` call.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
zig build-exe runner.zig -O ReleaseFast
./runner 65536 0.5 2.0
```

The seam: `gota.run(init, IMPL, register)` parses args, allocates the buffer, and
calls your `register(b: *gota.Bencher)`; you call `b.bench(name, op)` once per
operation, where `op` is `fn([]u8) void` over the shared buffer.

Notes (Zig 0.16, see the dorado port's `DEVELOPMENT.md`):

- `main` is `pub fn main(init: std.process.Init) !void`; args come from
  `init.minimal.args` (`std.process.argsAlloc` is gone), and the `Io` for the clock
  comes from `init.io`.
- Timing uses `std.Io.Clock` (`std.time.Timer` is gone). The buffered stdout writer is
  flushed by the harness before exit, so output is never truncated.
- Only the standard library is used.

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
