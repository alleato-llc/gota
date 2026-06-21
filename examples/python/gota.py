"""Gota harness (Python). Copy this file into your project as-is and do not edit it.

It owns the measurement: argument parsing, the buffer, the peak-of-batches timing
loop, and the JSON output. Your code plugs in through `run(impl, register)`: the
harness hands your `register(b, data)` a Bencher and a buffer, and you call
`b.bench(name, op)` for each operation. Your op closes over `data` and runs the work;
it never touches the clock or the output. See ../../PROTOCOL.md.
"""

from __future__ import annotations

import sys
import time
from typing import Callable


class Bencher:
    def __init__(self, impl: str, buf_bytes: int, warmup: float, measure: float) -> None:
        self.impl = impl
        self.buf_bytes = buf_bytes
        self.warmup = warmup
        self.measure = measure

    def bench(self, name: str, op: Callable[[], None]) -> None:
        # Report peak throughput across many batches (max MB/s is the reproducible
        # rate; jitter only ever slows a batch). Clock is read at batch boundaries.
        start = time.perf_counter()
        while time.perf_counter() - start < self.warmup:
            op()
        batch = 1
        while True:
            start = time.perf_counter()
            for _ in range(batch):
                op()
            if time.perf_counter() - start >= 0.1:
                break
            batch *= 2
        best = 0.0
        total = 0
        samples: list[float] = []  # per-batch MB/s; median vs peak shows run stability
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < self.measure:
            start = time.perf_counter()
            for _ in range(batch):
                op()
            mbps = self.buf_bytes * batch / 1e6 / (time.perf_counter() - start)
            if mbps > best:
                best = mbps
            samples.append(mbps)
            total += batch
        samples.sort()
        n = len(samples)
        median = 0.0 if n == 0 else samples[n // 2] if n % 2 else (samples[n // 2 - 1] + samples[n // 2]) / 2
        print(
            f'{{"impl":"{self.impl}","bench":"{name}","mbps":{best:.2f},"mbps_median":{median:.2f},"iters":{total}}}',
            flush=True,
        )


def run(impl: str, register: Callable[["Bencher", bytearray], None]) -> None:
    buf_bytes = int(sys.argv[1]) if len(sys.argv) > 1 else 1048576
    warmup = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    measure = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    data = bytearray(buf_bytes)
    register(Bencher(impl, buf_bytes, warmup, measure), data)
