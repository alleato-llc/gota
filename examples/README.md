# Gota example

A complete, runnable Gota consumer in miniature: four runners (Rust, C, Go, Python),
each plugged into its language's `gota` harness, all driven by the Python orchestrator
into one table. This is what using Gota looks like end to end.

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

## What it measures

FNV-1a over the buffer, in each language, as a stand-in for "your operation." FNV-1a
is a deliberately dull choice: a serial byte reduction with a carried dependency, so
no compiler can vectorize it away, and the three compiled languages land close
together while Python pays the interpreter tax. That is the *point* of the example: it
shows the harness producing an honest, comparable number, not a language race. Each
op ends with a one-byte sink (`data[0] ^= h`) so the loop cannot be optimized out
under `-O`.

## Layout (mirrors a real consumer)

```
examples/
  harness.py        # copied from ../harness.py (the generic engine)
  run.py            # this project's config: which runners, labels, framing
  python/{gota.py, runner.py}
  c/{gota.h, gota.c, runner.c}
  go/{go.mod, gota/gota.go, runner.go}
  rust/{gota.rs, runner.rs}
  results.json      # generated
  RESULTS.md        # generated
```

The `gota.*` files are copies of the [templates](../templates); only the `runner.*`
files and `run.py` are project code. For the real thing, see `dorado/bench`.
