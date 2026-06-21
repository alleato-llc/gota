// Gota harness (TypeScript). Copy this file into your project as-is and do not edit
// it. It owns the measurement: argument parsing, the buffer, the peak-of-batches
// timing loop, and the JSON output. Your code plugs in through run(impl, register):
// the harness hands your register a Bencher and the buffer, and you call
// b.bench(name, op) for each operation. See ../../PROTOCOL.md.

export class Bencher {
  readonly impl: string;
  readonly bufBytes: number;
  readonly warmup: number;
  readonly measure: number;

  constructor(impl: string, bufBytes: number, warmup: number, measure: number) {
    this.impl = impl;
    this.bufBytes = bufBytes;
    this.warmup = warmup;
    this.measure = measure;
  }

  // Report peak throughput across many batches (max MB/s is the reproducible rate;
  // jitter only ever slows a batch). The clock is read only at batch boundaries.
  bench(name: string, op: () => void): void {
    const wstart = performance.now();
    while ((performance.now() - wstart) / 1000 < this.warmup) op();

    let batch = 1;
    for (;;) {
      const start = performance.now();
      for (let i = 0; i < batch; i++) op();
      if ((performance.now() - start) / 1000 >= 0.1) break;
      batch *= 2;
    }

    let best = 0;
    let total = 0;
    const samples: number[] = []; // per-batch MB/s; median vs peak shows run stability
    const t0 = performance.now();
    while ((performance.now() - t0) / 1000 < this.measure) {
      const start = performance.now();
      for (let i = 0; i < batch; i++) op();
      const mbps = (this.bufBytes * batch) / 1e6 / ((performance.now() - start) / 1000);
      if (mbps > best) best = mbps;
      samples.push(mbps);
      total += batch;
    }
    samples.sort((a, b) => a - b);
    const n = samples.length;
    const median = n === 0 ? 0 : n % 2 === 1 ? samples[(n - 1) / 2] : (samples[n / 2 - 1] + samples[n / 2]) / 2;
    process.stdout.write(
      `{"impl":"${this.impl}","bench":"${name}","mbps":${best.toFixed(2)},"mbps_median":${median.toFixed(2)},"iters":${total}}\n`,
    );
  }
}

export function run(impl: string, register: (b: Bencher, data: Uint8Array) => void): void {
  const argv = process.argv.slice(2);
  const bufBytes = argv[0] ? parseInt(argv[0], 10) : 1048576;
  const warmup = argv[1] ? parseFloat(argv[1]) : 0.5;
  const measure = argv[2] ? parseFloat(argv[2]) : 2.0;
  register(new Bencher(impl, bufBytes, warmup, measure), new Uint8Array(bufBytes));
}
