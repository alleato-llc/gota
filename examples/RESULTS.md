# Benchmark results

Example Gota run: FNV-1a over a 64 KiB buffer in seven languages under one
protocol. Peak MB/s (decimal, 1e6 bytes), higher is better; results.json also records
each run's median rate (mbps_median) as a stability signal.

This demonstrates the harness; it is not a serious language comparison. FNV-1a is a
trivial serial byte reduction, so these numbers reflect each runtime's handling of a
tight scalar loop, nothing more (the TypeScript runner uses BigInt for 64-bit math,
which is genuinely slow — an honest artifact, not a bug).

Machine: Apple M4 Max | Darwin arm64 | 2026-06-21 | commit 56d70dd.

| Implementation | FNV-1a 64 |
| --- | ---: |
| Rust | 1110.0 |
| C | 1112.4 |
| Go | 1109.9 |
| Zig | 1113.1 |
| Java | 1111.2 |
| Python | 19.5 |
| TypeScript | 84.5 |
