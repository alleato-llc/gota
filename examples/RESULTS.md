# Benchmark results

Example Gota run: FNV-1a over a 64 KiB buffer in ten languages under one
protocol. Peak MB/s (decimal, 1e6 bytes), higher is better; results.json also records
each run's median rate (mbps_median) as a stability signal.

This demonstrates the harness; it is not a serious language comparison. FNV-1a is a
trivial serial byte reduction, so these numbers reflect each runtime's handling of a
tight scalar loop, nothing more (the TypeScript runner uses BigInt for 64-bit math,
which is genuinely slow — an honest artifact, not a bug; the Haskell runner threads and
forces an accumulator so laziness cannot defer or share the work).

Machine: Apple M4 Max | Darwin arm64 | 2026-08-03 | commit 94665dc.

| Implementation | FNV-1a 64 |
| --- | ---: |
| Rust | 1089.0 |
| C | 1086.5 |
| C++ | 1087.2 |
| Go | 1083.2 |
| Zig | 1084.3 |
| Java | 1085.3 |
| Swift | 1085.6 |
| Haskell | 1068.7 |
| Python | 19.0 |
| TypeScript | 86.5 |
