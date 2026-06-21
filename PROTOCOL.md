# The Gota protocol

A uniform, comparable way to micro-benchmark the *same* operation implemented in
*different* languages. The runners are necessarily native to each language (you
cannot time Zig code from Python), but every runner follows this one recipe, so the
numbers compare. The protocol is the reusable part; the code is almost incidental.

## Interface

Each runner is invoked with three arguments and prints one JSON line per benchmark:

```
runner <buffer_bytes> <warmup_seconds> <measure_seconds>

{"impl":"<name>","bench":"<name>","mbps":<float>,"mbps_median":<float>,"iters":<int>}
```

`impl` identifies the implementation (e.g. `rust`); `bench` the operation (e.g.
`blake3`); `mbps` is the peak (decimal MB/s, 1e6 bytes); `mbps_median` is the median
of the per-batch rates in the measure phase; `iters` the total iterations run. The
gap between `mbps` and `mbps_median` is a stability signal: close together means a
clean run, a wide gap means the measure phase was noisy and the peak is less trusted.

## The measurement (`bench()`)

For each benchmark the runner:

1. fills a `buffer_bytes` buffer once,
2. **warms up**: runs the operation in a loop until `warmup_seconds` elapse, so
   JIT/VM runtimes reach steady state (otherwise they are measured mid-compilation),
3. **sizes a batch**: grows an iteration count until one batch takes at least ~100ms,
4. **measures**: runs that batch repeatedly for `measure_seconds`, recording each
   batch's `MB/s = buffer_bytes * batch / 1e6 / batch_seconds`, and reports the
   **peak** of those rates (plus their **median** as a stability signal).

## The core idea: batch up an op too fast to time

The operation under test is almost always *much* faster than the clock can resolve —
hashing or encrypting a 64 KiB buffer takes nanoseconds to microseconds, while reading
the clock itself costs comparable time (a vDSO call, sometimes a syscall). You cannot
time a single such op directly: the measurement would be dominated by its own overhead.

So we don't. We run the op `batch` times back-to-back as one unit and time the *whole
batch*. A batch is sized so its combined time clears ~100ms — large enough that the two
clock reads bracketing it, and the clock's own resolution, are negligible. The 100ms is
a property of the **batch**, never of one op; the implicit expectation is *one op ≪
100ms*, so `batch` must be ≫ 1 to reach it.

This is sound because throughput is a *rate*, and batching does not distort a rate.
`buffer_bytes × batch` bytes in `T` seconds is the same MB/s as `buffer_bytes` bytes in
`T / batch` seconds — batching just shifts the measurement up to where the clock is
trustworthy, and dividing by `batch_seconds` divides the inflation back out. What
batching deliberately discards is per-call overhead (setup, call latency); that is out
of scope here on purpose — this measures steady-state throughput of the op over a
buffer, not the latency of a single call.

### Sizing the batch (exponential search)

Finding `batch` is **exponential (geometric) search**, the standard auto-calibration
trick for "the thing I want to measure is faster than my clock": start at 1, time it,
and keep doubling until one batch clears ~100ms.

```
batch = 1
loop:
    time the batch (run the op `batch` times)
    if elapsed >= 100ms: stop, lock in this batch
    batch *= 2
```

Doubling, rather than incrementing or estimating directly, buys three things:

- **O(log N) probes** to reach any batch size — the example's `batch ≈ 16384` is found
  in 15 doublings, not 16384 increments.
- **Bounded overshoot** — the final batch lands in `[100ms, 200ms)`, never more than 2×
  past target. The exact value does not matter (it cancels out of the rate); it only
  has to clear the floor, and doubling clears it fast without wild overshoot.
- **No prior knowledge of the op's speed** — the same template self-calibrates across a
  ~200× range of implementation speeds, which is exactly why the buffer size can stay
  fixed (see below). These calibration timings are thrown away; only the chosen `batch`
  survives into the measure phase, where it stays constant.

Go's `testing.B` (grow `b.N` until the run is long enough), JMH, and criterion all use
the same family of trick for the same reason.

The harness's sweet spot follows directly: ops in the **nanosecond-to-millisecond** per
call range batch up cleanly and yield many samples. An op that *already* takes >100ms
per call breaks the loop at `batch = 1` — it still runs, but you get few samples and
lose the benefit of peak-of-batches; that regime wants a different tool (a few timed
runs with explicit outlier handling), not this one.

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
