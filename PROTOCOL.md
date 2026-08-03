# The Gota protocol

**Protocol version 1.2.0.** This is the normative contract: what a runner must do to be
comparable with every other runner. It is deliberately short. The reasoning behind each
requirement — why batches, why the peak, why a warmup — is in
[`docs/DESIGN.md`](docs/DESIGN.md), which is the more interesting document and the one to
read if you want to understand the recipe rather than implement it.

A conforming runner is native to its language (you cannot time Zig code from Python), so
the protocol constrains behavior, not implementation.

## 1. Invocation

A runner is a standalone executable taking three positional arguments:

```
runner <buffer_bytes> <warmup_seconds> <measure_seconds>
```

1.1. All three are optional; a runner MUST default to `1048576 0.5 2.0` when they are
absent, so it is runnable with no arguments.

1.2. `buffer_bytes` is an integer; `warmup_seconds` and `measure_seconds` are decimal.

1.3. A runner MUST allocate one zeroed buffer of `buffer_bytes` and reuse it for every
benchmark in the run. It MUST NOT reallocate per iteration.

## 2. Output

2.1. A runner MUST print exactly one JSON object per benchmark, one per line, to stdout:

```json
{"impl":"<name>","bench":"<name>","mbps":<float>,"mbps_median":<float>,"iters":<int>,"protocol":"1.2.0"}
```

2.2. Field meanings:

| Field | Meaning |
| --- | --- |
| `impl` | the implementation being measured (e.g. `rust`) |
| `bench` | the operation (e.g. `blake3`) |
| `mbps` | the **peak** per-batch rate, decimal MB/s (1e6 bytes) |
| `mbps_median` | the **median** of the per-batch rates in the measure phase |
| `iters` | total iterations run in the measure phase |
| `protocol` | the protocol version this runner implements (added in 1.2.0) |

2.3. `mbps` and `mbps_median` MUST be computed as
`buffer_bytes * batch / 1e6 / batch_seconds` per batch. The gap between them is the
run's stability signal: close means clean, wide means the peak is noisy.

2.4. `protocol` states the version of this document that the runner implements. A
consumer whose copied runners report an older version than the orchestrator is behind,
which is the point of the field. Parsers MUST treat it as OPTIONAL: a runner copied
before 1.2.0 omits it entirely and remains valid, reported as "unspecified".

2.5. Nothing else may go to stdout. Diagnostics go to stderr. The orchestrator skips a
line it cannot parse rather than aborting, but a conforming runner emits none.

## 3. The measurement

For each benchmark, in order:

3.1. **Warm up.** Run the operation in a loop until `warmup_seconds` have elapsed.
Discard all timings. (Without this, JIT and VM runtimes are measured mid-compilation.)

3.2. **Size a batch.** Start at `batch = 1`. Time one batch; if it took less than 100ms,
double `batch` and repeat. Stop at the first batch that clears 100ms and keep that
`batch` fixed for the measure phase. Discard these calibration timings.

3.3. **Measure.** Until `measure_seconds` have elapsed, run `batch` iterations as one
timed unit and record that batch's rate. Report the peak of those rates as `mbps`, their
median as `mbps_median`, and the total iterations as `iters`.

3.4. The clock MUST be read only at batch boundaries — never around a single iteration.
A per-iteration clock read can cost as much as the operation itself.

3.5. The clock MUST be monotonic (`clock_gettime(CLOCK_MONOTONIC)`,
`std::chrono::steady_clock`, `System.nanoTime`, and equivalents).

## 4. The operation

4.1. The measured operation MUST consume its own result — write into the buffer, or fold
the result back into it. An unconsumed result may be optimized away entirely, and the
runner then measures nothing at full speed.

4.2. In a lazy language this is stronger: the result MUST be forced, and threaded so it
cannot be computed once and shared.

4.3. Setup that is not under test (key schedules, allocations) MUST happen outside the
timed operation.

## Conformance checklist

A new language template is conforming when all of these hold:

- [ ] Runs standalone with no arguments, and with all three.
- [ ] Prints one JSON line per benchmark, with all six fields (including `protocol`),
      and nothing else on stdout.
- [ ] Warms up, then grows a batch to ≥ 100ms, then measures for the requested duration.
- [ ] Reads a monotonic clock only at batch boundaries.
- [ ] Reports the peak rate and the median of per-batch rates.
- [ ] Its example operation consumes its result (and forces it, if the language is lazy).
- [ ] Its numbers land in the same range as the other templates for the same operation —
      the practical check that it is measuring the same work.

## Scope

**In scope:** the implementation's own code, isolated from process startup and I/O.

**Out of scope, deliberately:** anything delegated to a library (you would be measuring
the library), per-call latency and its distribution, and end-to-end CLI timing. See
[`docs/DESIGN.md`](docs/DESIGN.md#what-is-and-is-not-measured).

## Honesty requirements

These are as binding as the timing rules; a number that violates them is not comparable.

- State the machine, date, and commit alongside any published figure.
- Never publish numbers measured in CI: its hardware varies between runs.
- Peak throughput is the *unimpeded* rate. It is right for comparing implementations and
  optimistic for predicting real-world latency under load. Say so.
- Naive from-scratch code shows language and runtime overhead, not how fast tuned or SIMD
  code can go. Say that too.

## Versioning

The protocol carries its own semantic version, tracked in
[`VERSIONS.md`](VERSIONS.md). A consumer states which version its copied runners
implement, so a stale copy is a visible fact rather than a guess.

- **MAJOR** — a change that makes existing runners non-comparable or unparseable (new
  arguments, a changed timing loop, a removed or redefined JSON field).
- **MINOR** — a backward-compatible addition (a new JSON field, as `mbps_median` was in
  1.1.0 and `protocol` in 1.2.0).
- **PATCH** — clarification with no behavioral change.

A protocol change must land in all ten `templates/<lang>/gota.*` in the same PR, or they
stop being comparable.
