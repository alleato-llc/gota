# Changelog

All notable changes to Gota are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); when releases are cut they
get a dated version heading below `Unreleased`.

**Rule:** any change worth noting (a feature, a fix, a breaking or behavior change, a
notable doc change) adds a bullet to the `Unreleased` section **in the same commit or
PR**, grouped under Added / Changed / Fixed / Removed.

## [Unreleased]

### Added

- Baseline/multi-run comparison. `harness.py` gains `compare_runs`,
  `render_comparison_markdown`, and `regressions` (per-`(impl,bench)` deltas with a
  noise-band tolerance and provenance/param mismatch warnings). `report.py` accepts two
  or more results files with `--baseline`, embedding a comparison view in the HTML, and
  adds `--markdown` (delta table to stdout) and `--fail-on-regression PCT` (CI exit-code
  gate). `report_template.html` gains a comparison mode: multi-file load, a baseline
  picker, color-graded deltas, and loud machine/param mismatch warnings.
- `PROTOCOL.md`: a "core idea" section explaining *why* the loop batches (timing an op
  faster than the clock, and why batching a rate is lossless) and naming the batch-
  sizing algorithm (exponential/geometric search), with its trade-offs and sweet spot.

### Changed

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

### Added

- The protocol (`PROTOCOL.md`): the uniform recipe every runner follows and the
  reasoning (peak-of-batches, read the clock at batch boundaries, warm up JITs, scope).
- The generic orchestrator (`harness.py`): `RunnerSpec`, `run_all`, `gather_metadata`,
  and stream-friendly output (`build_results_doc`, `render_markdown`, and a
  `write_results` that accepts a path or any writable stream).
- Per-language templates (Python, Rust, C, Go, Java, Zig, TypeScript), each split into
  a copy-as-is `gota.*` harness and a `runner.*` you edit, plus a per-language README.
  All verified to build and run standalone.
- A complete `examples/` consumer (Rust, C, Go, Python) driven by `examples/run.py`,
  generating `RESULTS.md`, `results.json`, and `report.html`.
- A generic HTML report (`report.py` + `report_template.html`): a standalone,
  format-aware viewer with a file picker, sortable table, per-language colors,
  magnitude bars, and formatted units.
- `CLAUDE.md` with the project conventions and the keep-the-languages-equivalent
  invariant.
