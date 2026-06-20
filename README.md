# Gota

A small, copy-it reference for **cross-language throughput micro-benchmarks**.

When you have the same operation implemented in several languages and want an honest,
*comparable* picture of how fast each implementation's own code runs, Gota gives you:

- **A protocol** (see [`PROTOCOL.md`](PROTOCOL.md)) every runner follows, so the
  numbers compare even though each runner is native to its language.
- **A generic orchestrator** ([`harness.py`](harness.py)) that builds and runs your
  runners with identical parameters, collects their JSON, records provenance, and
  writes `results.json` + a Markdown table.
- **Per-language templates** ([`templates/`](templates/)) — a tiny `bench()` helper
  (the peak-of-batches timing loop) plus a runnable skeleton you fill in with your op.

The reusable thing here is the **protocol and the lessons**, not the code: a
peak-of-batches loop is ~20 lines you can re-type once you know the recipe. So Gota
is meant to be **copied, not depended on** — the helpers are small, stable, and
polyglot (no single package manager spans Rust, Go, Zig, C, Java, Python, and
TypeScript), so copying is the pragmatic, low-harm choice. Re-copy when the protocol
improves.

## How to use it

1. **Copy** `harness.py` into your project, and the `templates/<lang>` skeleton for
   each language you benchmark.
2. In each runner, replace the example operation with **your** operation (keep the
   `bench()` helper as-is).
3. Write a `run.py` that declares one `RunnerSpec` per runner (how to build it and
   how to invoke it) and the row/column labels, then calls `harness.run_all` and
   `harness.write_results`. The templates include a `run.py` example.
4. `python3 run.py` builds and runs everything and writes `results.json` +
   `RESULTS.md`.

## What it is not

- Not a nanosecond-latency tool (timing one tiny op with statistical outlier
  rejection) — for that use a per-language framework like criterion or JMH.
- Not lab-grade absolute numbers — it reports *peak* (unimpeded) throughput on a
  normal machine, which is right for *comparing* implementations. For reproducible
  absolutes you would pin cores, lock frequency, and use a dedicated box.

## Origin

Gota was extracted from the benchmark harness of the
[dorado](https://github.com/nycjv321/dorado) project (a from-scratch cipher
implemented in eight languages), which remains its first consumer and proving ground.
The name is *gota*, "drop" in Spanish/Portuguese — measuring throughput drop by drop.

Educational; MIT licensed.
