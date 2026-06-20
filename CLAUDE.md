# CLAUDE.md

Gota is a small, standalone reference for **cross-language throughput
micro-benchmarks**: a protocol, a generic Python orchestrator, per-language runner
templates, and an HTML report. It is meant to be **copied into other projects, not
depended on as a package** (the helpers are small, stable, and polyglot; no single
package manager spans all the languages). The first consumer is the `dorado` project's
`bench/`, which copies `harness.py`, `report.py`, and `report_template.html` from here.

Start with `README.md` (what it is, how to use it, the design diagram) and
`PROTOCOL.md` (the measurement recipe and the hard-won lessons). This file is for
working *on* Gota.

## Layout

- `PROTOCOL.md` — the contract every runner obeys and the reasoning behind it
  (peak-of-batches, read the clock at batch boundaries, warm up JITs, what is in and
  out of scope). This is the real product; the code is almost incidental.
- `harness.py` — the generic orchestrator. `RunnerSpec` + `run_all` (build and run each
  runner as a subprocess under identical params, collect their JSON), `gather_metadata`
  (machine/os/date/git provenance), and the output helpers `build_results_doc`,
  `render_markdown`, and `write_results` (which accepts a path or any writable stream).
  Nothing project-specific lives here.
- `templates/<lang>/` — two files per language plus a README:
  - `gota.*` is the **harness**: the peak-of-batches `bench()` loop, arg parsing,
    buffer allocation, and JSON output. A consumer copies this as-is and does not edit
    it.
  - `runner.*` (and `Runner.java`) is the **user's code**: it plugs an operation into
    the harness through one seam (`run(impl, register)` then `bench(name, op)`). The
    committed op is a trivial example to keep the template runnable.
  - Languages: `python`, `rust`, `c`, `go`, `java`, `zig`, `ts`.
- `report.py` + `report_template.html` — a generic HTML report. The script fills three
  tokens (`__TITLE__`, `__DATA__`, `__GENERATED__`) into the template and writes a
  self-contained, format-aware viewer (file picker, sortable table, per-language
  colors, magnitude bars, formatted units). Presentation lives in the template; the
  script does not change when you restyle.
- `examples/` — a complete miniature consumer (Rust, C, Go, Python) driven by a copy of
  `harness.py` and an `examples/run.py`, producing a generated `RESULTS.md`,
  `results.json`, and `report.html`. FNV-1a is the stand-in op.

## The core invariant: keep the languages equivalent

Every `templates/<lang>/gota.*` implements the **same** protocol: same three CLI args,
same peak-of-batches loop (warm up, grow a batch to >= 100ms, then report the fastest
batch's MB/s), same JSON line `{"impl","bench","mbps","iters"}`. If you change the
protocol or the timing loop, change it in **all seven** language templates and in
`PROTOCOL.md`, or they stop being comparable. This is the same discipline a multi-port
project uses to keep ports in sync; here the "ports" are the harness templates.

The seam is also uniform on purpose: `run(impl, register)` hands the user a bencher and
a buffer, and `bench(name, op)` is called once per operation. Keep that shape when
adding a language (C and Java vary only as far as the language forces: C uses a
function pointer + `void* ctx`, Java a functional interface, because neither has
closures).

## Verifying changes

Templates must actually build and run. After touching a `gota.*` or the protocol,
re-run each affected language standalone (commands are in each `templates/<lang>/
README.md`), for example:

```
python3 templates/python/runner.py 65536 0.2 0.4
( cd templates/rust && rustc -O runner.rs -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/c    && cc -std=c17 -O2 runner.c gota.c -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/go   && go build -o runner . && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/java && javac Gota.java Runner.java && java Runner 65536 0.2 0.4 && rm *.class )
( cd templates/zig  && zig build-exe runner.zig -O ReleaseFast && ./runner 65536 0.2 0.4 && rm runner runner.zig.o )
node --experimental-strip-types templates/ts/runner.ts 65536 0.2 0.4   # or: npx tsx
```

Each must print one JSON line. For the orchestrator and report, run the example
end-to-end and regenerate its artifacts:

```
python3 examples/run.py                 # writes examples/{results.json,RESULTS.md}
python3 report.py examples/results.json -o examples/report.html
```

When editing `report_template.html`, confirm the embedded JS still parses and renders
(extract the `<script>` and `node --check` it, or open the HTML).

Notes on toolchains: the Zig templates target **Zig 0.16** (args via
`std.process.Init`, timing via `std.Io.Clock`, buffered writer flushed before exit; see
the dorado port's `DEVELOPMENT.md` for the 0.16 API background). The TS template avoids
TypeScript parameter properties so it runs under Node's strip-only type stripping, not
just `tsx`.

## Consumers and syncing

`harness.py`, `report.py`, and `report_template.html` are copied verbatim into
consumers (the dorado `bench/` carries copies with a one-line provenance note in their
header). When you change any of these here, the consumer copies do not update
automatically; they must be re-copied. Treat a change to these three files as something
that ripples outward, and keep the change minimal and backward-compatible
(`write_results`'s positional `out_json, out_md` and its keyword args are part of that
contract).

## Conventions

- **No fabricated numbers.** Every benchmark figure must come from a real run on a
  stated machine; `RESULTS.md`/`results.json`/`report.html` are generated, never
  hand-edited. Do not commit numbers from CI (its hardware varies).
- **Honest framing.** Peak-of-batches is the *unimpeded* rate: right for comparing
  implementations, optimistic for real-world latency. Naive code shows
  language/runtime overhead, not how fast tuned/SIMD code can go. Say so.
- Keep `PROTOCOL.md`, `README.md`, and the per-language READMEs in step with the code.
- **Update the changelog as you go.** Any change worth noting adds a bullet to the
  `Unreleased` section of `CHANGELOG.md` (grouped under Added / Changed / Fixed /
  Removed) in the same commit or PR.
- Direct prose, minimal ceremony. Educational and unaudited; MIT licensed.
