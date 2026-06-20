#!/usr/bin/env python3
"""Gota runner (Python) - YOUR code. This is the file you edit.

It declares the operation(s) to measure and plugs them into the harness. There is no
timing, batching, or JSON here: `register` receives a Bencher `b` and the buffer
`data`, and calls `b.bench(name, op)` once per operation. `gota.run` does the rest.

    python3 runner.py [buffer_bytes] [warmup_seconds] [measure_seconds]
"""

from __future__ import annotations

import gota

IMPL = "example"  # your implementation's name


def register(b: gota.Bencher, data: bytearray) -> None:
    # Replace with your real operation(s). Each op closes over `data` and runs the
    # work to measure. Call b.bench once per operation you want in the table.
    def example():
        for i in range(len(data)):
            data[i] ^= 0x5A

    b.bench("example", example)


if __name__ == "__main__":
    gota.run(IMPL, register)
