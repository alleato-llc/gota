# Changelog — Rust template

Changes to **this language template only** (`templates/rust/gota.rs`, `runner.rs`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

## [0.1.0]

### Added

- Initial Rust template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `gota.rs` harness and a
  `runner.rs` seam (`run(impl, register)` then `bench(name, op)`). Builds with
  `rustc -O` and runs standalone.
