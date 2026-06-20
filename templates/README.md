# Gota templates

A runnable starting point per language. Each is split in two so the thing you measure
plugs into the harness instead of being tangled up in it:

- **`gota.*`** — the harness. The peak-of-batches timing loop, argument parsing, the
  buffer, and the JSON output. Copy it in and **do not edit it**.
- **`runner.*`** (and `Runner.java`) — *your* code. It declares the operation(s) and
  plugs them in: the harness hands your `register` a bencher and the buffer, and you
  call `bench(name, op)` once per operation. No timing, batching, or JSON lives here.

The seam is the same idea in every language: `run(impl, register)`, then
`b.bench("name", op)`. Replace the `example` op (a trivial buffer XOR, here only so
the template runs out of the box) with the code you actually want to measure.

Every runner takes the same three arguments and prints the same JSON, so the Python
orchestrator (`../harness.py`) can build and run any of them interchangeably. See
[`../PROTOCOL.md`](../PROTOCOL.md) for the contract and the reasoning.

## Build and run

All accept `[buffer_bytes] [warmup_seconds] [measure_seconds]` (defaults: 1048576,
0.5, 2.0).

| Language | Files | Build and run |
| --- | --- | --- |
| Python | `python/{gota.py, runner.py}` | `python3 runner.py 65536 0.5 2.0` |
| Rust | `rust/{gota.rs, runner.rs}` | `rustc -O runner.rs -o runner && ./runner` |
| C | `c/{gota.h, gota.c, runner.c}` | `cc -std=c17 -O2 runner.c gota.c -o runner && ./runner` |
| Go | `go/{go.mod, gota/gota.go, runner.go}` | `go build -o runner . && ./runner` |
| Java | `java/{Gota.java, Runner.java}` | `javac Gota.java Runner.java && java Runner` |
| Zig | `zig/{gota.zig, runner.zig}` | `zig build-exe runner.zig -O ReleaseFast && ./runner` |
| TypeScript | `ts/{gota.ts, runner.ts}` | `npx tsx runner.ts` (or `node --experimental-strip-types runner.ts` on Node >= 22.6) |

Notes:

- **Rust** builds with plain `rustc`; `mod gota;` picks up `gota.rs` beside it. No
  Cargo project needed for the template (a real consumer would link its own crate).
- **Go** uses a tiny module (`go.mod`) so `runner.go` (package `main`) can import the
  separate `gota` package. Rename the module if you vendor it elsewhere.
- **Zig** targets 0.16: args arrive via `std.process.Init`, timing uses
  `std.Io.Clock`, and the buffered writer is flushed for you. See the dorado port's
  `DEVELOPMENT.md` for the 0.16 API background.
- **TypeScript** avoids parameter properties so it runs under Node's strip-only type
  stripping as well as `tsx`.
