# Changelog

All notable changes to Gota are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); when releases are cut they
get a dated version heading below `Unreleased`.

**Rule:** any change worth noting (a feature, a fix, a breaking or behavior change, a
notable doc change) adds a bullet to the `Unreleased` section **in the same commit or
PR**, grouped under Added / Changed / Fixed / Removed.

## [Unreleased]

### Changed

- `README.md`: the "Using it in your own tooling" stream-outputs example now shows both
  in-memory capture (two `io.StringIO` buffers) and true streaming to open sinks, side
  by side, instead of a single mixed snippet.

### Fixed

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
