# The Gota protocol

A uniform, comparable way to micro-benchmark the *same* operation implemented in
*different* languages. The runners are necessarily native to each language (you
cannot time Zig code from Python), but every runner follows this one recipe, so the
numbers compare. The protocol is the reusable part; the code is almost incidental.

## Interface

Each runner is invoked with three arguments and prints one JSON line per benchmark:

```
runner <buffer_bytes> <warmup_seconds> <measure_seconds>

{"impl":"<name>","bench":"<name>","mbps":<float>,"iters":<int>}
```

`impl` identifies the implementation (e.g. `rust`); `bench` the operation (e.g.
`blake3`); `mbps` is decimal MB/s (1e6 bytes); `iters` the total iterations run.

## The measurement (`bench()`)

For each benchmark the runner:

1. fills a `buffer_bytes` buffer once,
2. **warms up**: runs the operation in a loop until `warmup_seconds` elapse, so
   JIT/VM runtimes reach steady state (otherwise they are measured mid-compilation),
3. **sizes a batch**: grows an iteration count until one batch takes at least ~100ms,
4. **measures**: runs that batch repeatedly for `measure_seconds`, and reports the
   **peak** `MB/s = buffer_bytes * batch / 1e6 / batch_seconds`.

## Why these choices (the lessons)

These are not arbitrary; each fixes a real failure observed in practice.

- **Read the clock only at batch boundaries, never per iteration.** Some clocks are
  cheap (a vDSO call) but others are expensive (a syscall, or a vtable indirection
  through a runtime's I/O layer). At a small buffer with a fast op, a per-iteration
  clock read can dominate and destabilize the measurement. Batching amortizes it.
- **Report the peak (fastest) batch, not the mean.** Scheduling jitter, CPU
  frequency scaling, thermal throttling, and (on hybrid CPUs like Apple Silicon)
  performance-vs-efficiency core placement can only ever make a batch *slower* —
  there is no mechanism that makes code run *faster* than its true rate. So the
  maximum throughput across batches is the reproducible estimate of the code running
  unimpeded. This is standard practice (criterion, JMH report on the minimum time).
  Without it, the same benchmark measured ~75 MB/s on an idle machine and ~17 MB/s
  under load; peak-of-batches removes that variance while *keeping* genuine
  differences (a real codegen slowdown stayed; the spurious load variance vanished).
- **Warm up before measuring.** JIT and VM runtimes (the JVM, V8) need the hot path
  compiled before the clock starts, or they are measured during interpretation and
  look slow for the wrong reason. Compiled languages are unaffected, so a uniform
  warmup costs them nothing.
- **Pick the buffer size for the speed range, and keep it compute-bound.** Small
  enough that the slowest implementation still completes several batches; large
  enough that per-call setup is negligible and the working set stays in cache, so the
  number reflects compute, not memory bandwidth. 64 KiB worked across a ~200x speed
  range in one project.

## What is and is not measured

- **In scope:** the implementation's own code — the operation you wrote, isolated
  from process startup and I/O.
- **Out of scope (by choice):** anything delegated to a library (you would be
  benchmarking the library, not your code), and end-to-end CLI timing (startup +
  I/O), which is a different question best answered separately.

## Honesty

Peak throughput is the *unimpeded* rate, which is right for comparing
implementations but optimistic for predicting real-world latency under load. State
the machine, date, and commit; never auto-publish numbers from CI (its hardware
varies). And be clear about *what* is being compared — naive from-scratch code shows
language/runtime overhead, not how fast a tuned, SIMD library can go.
