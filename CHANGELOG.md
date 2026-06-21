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
