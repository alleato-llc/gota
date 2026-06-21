# Changelog — Zig template

Changes to **this language template only** (`templates/zig/gota.zig`, `runner.zig`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to the protocol's `mbps_median` addition (see the [core changelog](../../CHANGELOG.md)): `gota.zig` now records each measure-phase
  batch's rate and emits the median beside the peak in its JSON line.

### Added

- `runner.zig`: a comment that a value-returning op must consume its result, or an
  optimizing build may delete the work and you measure nothing.

## [0.1.0]

### Added

- Initial Zig template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `gota.zig` harness and a
  `runner.zig` seam. Targets **Zig 0.16** (args via `std.process.Init`, timing via
  `std.Io.Clock`, buffered writer flushed before exit). Builds with
  `zig build-exe -O ReleaseFast` and runs standalone.
