// Example Gota runner (TypeScript): FNV-1a over the buffer. See ../README.md.
//   node --experimental-strip-types runner.ts [buffer_bytes] [warmup_s] [measure_s]
//
// JS has no native u64, so the 64-bit FNV runs on BigInt. That is genuinely slow
// (the result is honest, not a bug): it shows the cost of naive 64-bit math in JS,
// which the example intro already flags as not a serious cross-language comparison.
import { run, type Bencher } from "./gota.ts";

const PRIME = 0x100000001b3n;
const MASK = 0xffffffffffffffffn;

run("ts", (b: Bencher, data: Uint8Array) => {
  b.bench("fnv1a-64", () => {
    let h = 0xcbf29ce484222325n;
    for (let i = 0; i < data.length; i++) {
      h = ((h ^ BigInt(data[i])) * PRIME) & MASK;
    }
    data[0] ^= Number(h & 0xffn); // sink: consume h
  });
});
