# Gota runner: C

Files:

- `gota.h` / `gota.c` — the harness. Copy as-is; do not edit.
- `runner.c` — your code. Replace the `example_op` and its registration.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
cc -std=c17 -O2 runner.c gota.c -o runner
./runner 65536 0.5 2.0
```

The seam: `gota_run(IMPL, argc, argv, reg)` parses args, allocates the buffer, and
calls your `reg(b, data, n)`; inside it you call `gota_bench(b, name, op, ctx)` once
per operation.

Notes:

- C has no closures, so the op is a `void (*)(void *)` plus a `ctx` pointer. The
  template passes a small struct (`{data, n}`) as the context; widen it to carry
  whatever your op needs.
- Only the C standard library is used (`clock_gettime(CLOCK_MONOTONIC)` for timing).

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
