# Changelog — C template

Changes to **this language template only** (`templates/c/gota.c`, `gota.h`, `runner.c`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to the protocol's `mbps_median` addition (see the [core changelog](../../CHANGELOG.md)): `gota.c` now records each measure-phase
  batch's rate and emits the median beside the peak in its JSON line.

### Added

- `runner.c`: a comment that a value-returning op must consume its result, or an
  optimizing build may delete the work and you measure nothing.

## [0.1.0]

### Added

- Initial C template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `gota.c`/`gota.h` harness and a
  `runner.c` seam. The op plugs in as a function pointer plus a `void* ctx` (C has no
  closures). Builds with `cc -std=c17 -O2` and runs standalone.
