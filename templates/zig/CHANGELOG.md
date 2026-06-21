# Changelog — Zig template

Changes to **this language template only** (`templates/zig/gota.zig`, `runner.zig`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

## [0.1.0]

### Added

- Initial Zig template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `gota.zig` harness and a
  `runner.zig` seam. Targets **Zig 0.16** (args via `std.process.Init`, timing via
  `std.Io.Clock`, buffered writer flushed before exit). Builds with
  `zig build-exe -O ReleaseFast` and runs standalone.
