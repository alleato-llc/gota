// Gota runner (TypeScript) - YOUR code. This is the file you edit.
//
// It declares the operation(s) to measure and plugs them into the harness. There is
// no timing, batching, or JSON here: run hands your callback a Bencher and the
// buffer, and you call b.bench(name, op) once per operation.
//
//   npx tsx runner.ts [buffer_bytes] [warmup_seconds] [measure_seconds]
//   # or, with no extra tooling on Node >= 22.6:
//   node --experimental-strip-types runner.ts [buffer_bytes] [warmup_seconds] [measure_seconds]

import { run, type Bencher } from "./gota.ts";

const IMPL = "example"; // your implementation's name

run(IMPL, (b: Bencher, data: Uint8Array) => {
  // Replace with your real operation(s). Each op closes over `data` and runs the
  // work to measure. Call b.bench once per operation you want in the table.
  //
  // This example writes `data` in place, which is always observed. If your op instead
  // computes a value, consume it (write a byte back into `data`) so the JIT can't elide
  // the work and you measure nothing.
  b.bench("example", () => {
    for (let i = 0; i < data.length; i++) data[i] ^= 0x5a;
  });
});
