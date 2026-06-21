# Gota example

A complete, runnable Gota consumer in miniature: eight runners (Rust, C, Go, Zig, Java,
Haskell, Python, TypeScript), one per language template, each plugged into its language's
`gota` harness, all driven by the Python orchestrator into one table. This is what using
Gota looks like end to end.

```
python3 run.py
```

builds every available runner, runs each with identical parameters, and writes
[`results.json`](results.json) and [`RESULTS.md`](RESULTS.md). Override the parameters
with environment variables:

```
GOTA_BUF=131072 GOTA_WARMUP=0.5 GOTA_MEASURE=1.0 python3 run.py
```

A runner whose toolchain is missing is skipped with a note, not an error.

For an HTML view of the same data, generate the report from the results.json:

```
python3 ../report.py results.json -o report.html --title "Gota example — FNV-1a throughput"
```

[`report.html`](report.html) (committed) is a standalone, sortable viewer with a file
picker. A **show: MB/s | ops/sec** toggle in the report flips the same measurement
between byte throughput and operations per second (one op = hashing the whole buffer, so
ops/sec = MB/s × 1e6 ÷ buffer bytes) — same numbers, same ranking, two units. This is what
the website showcases.

## What it measures

FNV-1a over the buffer, in each language, as a stand-in for "your operation." FNV-1a
is a deliberately dull choice: a serial byte reduction with a carried dependency, so
no compiler can vectorize it away, and the compiled languages (Rust, C, Go, Zig) plus
the warmed-up JVM land close together while Python pays the interpreter tax and the
TypeScript runner pays for BigInt 64-bit math (JS has no native u64). That is the
*point* of the example: it shows the harness producing an honest, comparable number,
not a language race. Each op ends with a one-byte sink (`data[0] ^= h`) so the loop
cannot be optimized out under `-O`. Each result also carries `mbps_median` (the median
of the per-batch rates) alongside the peak; the two being close means a clean run.

## Layout (mirrors a real consumer)

```
examples/
  harness.py        # copied from ../harness.py (the generic engine)
  run.py            # this project's config: which runners, labels, framing
  python/{gota.py, runner.py}
  c/{gota.h, gota.c, runner.c}
  go/{go.mod, gota/gota.go, runner.go}
  rust/{gota.rs, runner.rs}
  zig/{gota.zig, runner.zig}
  java/{Gota.java, Runner.java}
  ts/{gota.ts, runner.ts}
  haskell/{Gota.hs, runner.hs}
  results.json      # generated
  RESULTS.md        # generated
  report.html       # generated — MB/s/ops-sec toggle
```

The `gota.*` files are copies of the [templates](../templates); only the `runner.*`
files and `run.py` are project code. For the real thing, see `dorado/bench`.
