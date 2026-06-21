# Benchmark results

Example Gota run: FNV-1a over a 64 KiB buffer in four languages under one
protocol. Peak MB/s (decimal, 1e6 bytes), higher is better.

This demonstrates the harness; it is not a serious language comparison. FNV-1a is a
trivial serial byte reduction, so these numbers reflect each compiler's handling of a
tight scalar loop, nothing more.

Machine: Apple M4 Max | Darwin arm64 | 2026-06-20 | commit 0788b69.

| Implementation | FNV-1a 64 |
| --- | ---: |
| Rust | 1051.7 |
| C | 1060.4 |
| Go | 1053.5 |
| Python | 18.7 |
