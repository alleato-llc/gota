#!/usr/bin/env python3
"""Example Gota runner (Python): FNV-1a over the buffer. See ../README.md."""

from __future__ import annotations

import gota

IMPL = "python"
MASK = 0xFFFFFFFFFFFFFFFF
PRIME = 0x100000001B3


def register(b: gota.Bencher, data: bytearray) -> None:
    def fnv1a():
        h = 0xCBF29CE484222325
        for x in data:
            h = ((h ^ x) * PRIME) & MASK
        data[0] ^= h & 0xFF  # sink: consume h so the loop can't be optimized away

    b.bench("fnv1a-64", fnv1a)


if __name__ == "__main__":
    gota.run(IMPL, register)
