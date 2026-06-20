# Gota runner: TypeScript

Files:

- `gota.ts` — the harness. Copy as-is; do not edit.
- `runner.ts` — your code. Replace the `example` op.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
npx tsx runner.ts 65536 0.5 2.0
# or, with no extra tooling on Node >= 22.6:
node --experimental-strip-types runner.ts 65536 0.5 2.0
```

The seam: `run(IMPL, (b, data) => { ... })` parses args, allocates the buffer, and
hands your callback a `Bencher` and the buffer; you call `b.bench(name, op)` once per
operation.

Notes:

- `gota.ts` deliberately avoids TypeScript parameter properties so it runs under
  Node's strip-only type stripping, not just `tsx`. Imports use an explicit `.ts`
  extension for the same reason.
- Timing uses `performance.now()`. V8 is warmed up before measuring (the protocol's
  warmup phase), so the numbers reflect JIT steady state.
- This measures whatever your op does in JS/TS. If you call into WASM or a native
  addon, you are measuring that, benchmarked under the same protocol.
