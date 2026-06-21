# Changelog — Core

The **core** changelog: the cross-cutting pieces — the protocol (`PROTOCOL.md`), the
orchestrator (`harness.py`), the report (`report.py` + `report_template.html`), the
`examples/` consumer, and shared docs. Per-language template changes live in each
`templates/<lang>/CHANGELOG.md`; [`VERSIONS.md`](VERSIONS.md) is the master table of
every component and its current version.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); when a
release is cut, the `Unreleased` entries get a dated version heading below.

**Rule:** route each change by what it touches — a protocol/`harness.py`/`report.py`/
`report_template.html`/`examples/`/shared-doc change adds a bullet here; a change to a
single `templates/<lang>/` goes in that language's changelog; a change to the landing
page goes in [`web/CHANGELOG.md`](web/CHANGELOG.md); a protocol change that ripples into
the templates is recorded here once and pointed to from each language log. Add the bullet
under Added / Changed / Fixed / Removed **in the same commit or PR**.

## [Unreleased]

### Added

- **Protocol: `mbps_median`.** Each runner now records every measure-phase batch's MB/s
  and emits the median alongside the peak, so the JSON line is
  `{"impl","bench","mbps","mbps_median","iters"}`. The gap between peak and median is a
  stability signal (close = clean run; wide = noisy, peak less trusted). PROTOCOL.md and
  all seven `templates/<lang>/gota.*` are updated in lockstep; see each template's
  changelog for its sync.
- `harness.gather_metadata(toolchains=...)` records each compiler/runtime's version under
  a `toolchains` key in the results' provenance (absent tools skipped). A throughput
  number is only reproducible alongside the toolchain that produced it. The example
  `run.py` passes its toolchains.
- `harness.Metric` enum (`BYTE_THROUGHPUT` / `OP_THROUGHPUT` / `LATENCY`) and a `metric`
  field in `results.json`. It records *what kind* of quantity a run measures, distinct
  from the free-text `units` display label (many labels — "requests/sec", "rows/sec" —
  map to one metric). `build_results_doc`/`write_results` take an optional `metric=`
  (default `BYTE_THROUGHPUT`, so existing callers and copied harnesses are unaffected) and
  validate it (an unknown value raises). The example declares `BYTE_THROUGHPUT`.
- The example (`examples/`) now covers all seven languages: Zig, Java, and TypeScript
  runners are added (FNV-1a, matching the existing four), wired into `run.py`. The
  TypeScript runner uses BigInt for 64-bit math (slow but honest; JS has no native u64).
- `report_template.html` gains a **MB/s ⇄ ops/sec toggle** for throughput runs (single
  and comparison views). Both units derive from each row's `mbps` and the per-op payload
  size (`params.buffer_bytes`), so one report shows the same run in either unit — same
  ranking, same bars, same deltas (delta % is unit-invariant), only the numbers relabel.
  Hidden for `latency` runs and when the payload size is unknown. The committed example
  `report.html` (and its `web/public/` copy showcased by the site) carries the toggle.
- `tests/test_harness.py`: a stdlib-`unittest` suite for `harness.py` (no new
  dependency) — `Metric` validation, the results-doc shape, `render_markdown`,
  `compare_runs` (faster/slower/same/new/gone, the tolerance band, and the metric /
  machine / param guards), the `regressions` gate, the `_first_line` toolchain probe, and
  `run_all`'s skip-on-None/error/timeout and drop-malformed-JSON behavior. Wired into the
  `core` CI job.
- Continuous integration (`.github/workflows/ci.yml`): each language template builds and
  runs standalone and must emit one JSON line, plus a core job that syntax-checks the
  Python and confirms the report generates. It is path-filtered: a `changes` job
  (`dorny/paths-filter`) runs each template's job only when `templates/<lang>/` changed,
  and a change to `PROTOCOL.md` or the workflow re-runs every template (the protocol is
  the contract they all share). A pure docs/changelog change runs no build jobs.
- Baseline/multi-run comparison. `harness.py` gains `compare_runs`,
  `render_comparison_markdown`, and `regressions` (per-`(impl,bench)` deltas with a
  noise-band tolerance and provenance/param mismatch warnings). `report.py` accepts two
  or more results files with `--baseline`, embedding a comparison view in the HTML, and
  adds `--markdown` (delta table to stdout) and `--fail-on-regression PCT` (CI exit-code
  gate). `report_template.html` gains a comparison mode: multi-file load, a baseline
  picker, color-graded deltas, and loud machine/param mismatch warnings.
- Per-component versioning: a `VERSIONS.md` master table (full semver per component) and
  a per-language `templates/<lang>/CHANGELOG.md`, so a change to one template or to the
  example no longer implies the others moved. Each `templates/<lang>/README.md` now
  points to its changelog and to `VERSIONS.md`, and the `CLAUDE.md` template-dir
  inventory notes the added CHANGELOG.
- `PROTOCOL.md`: a "core idea" section explaining *why* the loop batches (timing an op
  faster than the clock, and why batching a rate is lossless) and naming the batch-
  sizing algorithm (exponential/geometric search), with its trade-offs and sweet spot.

### Changed

- `harness.run_all` is more robust: a per-runner `timeout=` (default 120s) kills and
  skips a hung runner instead of stalling the whole run, and a malformed JSON line is
  logged and skipped rather than raising and aborting the collection. Both are
  backward-compatible (new keyword-only arg; same return shape).
- The comparison guard (`compare_runs`) now keys comparability on the `metric` kind
  rather than the free-text `units` string. Two `OP_THROUGHPUT` runs labelled differently
  ("requests/sec" vs "rows/sec") are comparable; a TPS run and an MB/s run are flagged as
  not comparable. Results predating the `metric` field are treated as `BYTE_THROUGHPUT`.
- `report_template.html` is metric-aware. It reads `metric` to choose the headline:
  `byte_throughput` shows MB/s (unchanged), `op_throughput` derives and shows ops/sec
  (from `mbps` and the payload size) under the free-text `units` label, and `latency`
  reads per-call fields with smaller-is-better bars, best-marking, and delta coloring.
  The metric is shown in the meta, and the in-browser comparison guard mirrors the
  Python one (flags mismatched metric kinds).
- The changelog rule (in `CLAUDE.md` and `README.md`) now routes a change to the
  changelog of whatever it touches (core vs a specific language template), instead of a
  single global `CHANGELOG.md`. This file is now scoped to the core.
- `README.md`: the "Using it in your own tooling" stream-outputs example now shows both
  in-memory capture (two `io.StringIO` buffers) and true streaming to open sinks, side
  by side, instead of a single mixed snippet.

### Fixed

- `examples/harness.py` was a stale copy that predated the stream-output refactor (it
  lacked `build_results_doc`/`render_markdown`/stream support). Re-synced it to the root
  `harness.py` so the in-repo consumer reflects the current orchestrator (now including
  the comparison helpers); `examples/report.html` regenerated against the new template.
- `report_template.html`: the documentation comment listed the substitution tokens
  verbatim, so `report.py`'s `.replace()` dumped the title/data/date into the comment.
  Reworded the comment so it no longer contains the literal tokens.

### Added (initial)

- The protocol (`PROTOCOL.md`): the uniform recipe every runner follows and the
  reasoning (peak-of-batches, read the clock at batch boundaries, warm up JITs, scope).
- The generic orchestrator (`harness.py`): `RunnerSpec`, `run_all`, `gather_metadata`,
  and stream-friendly output (`build_results_doc`, `render_markdown`, and a
  `write_results` that accepts a path or any writable stream).
- Per-language templates (Python, Rust, C, Go, Java, Zig, TypeScript), each split into
  a copy-as-is `gota.*` harness and a `runner.*` you edit, plus a per-language README.
  All verified to build and run standalone. (Per-template history now lives in each
  `templates/<lang>/CHANGELOG.md`.)
- A complete `examples/` consumer (Rust, C, Go, Python) driven by `examples/run.py`,
  generating `RESULTS.md`, `results.json`, and `report.html`.
- A generic HTML report (`report.py` + `report_template.html`): a standalone,
  format-aware viewer with a file picker, sortable table, per-language colors,
  magnitude bars, and formatted units.
- `CLAUDE.md` with the project conventions and the keep-the-languages-equivalent
  invariant.
