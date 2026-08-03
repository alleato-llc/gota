# Changelog — Java template

Changes to **this language template only** (`templates/java/Gota.java`, `Runner.java`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to protocol **1.2.0** (see the [core changelog](../../CHANGELOG.md)): the
  JSON line now carries a `protocol` field naming the version the runner implements.

- Synced to the protocol's `mbps_median` addition (see the [core changelog](../../CHANGELOG.md)): `Gota.java` now records each measure-phase
  batch's rate and emits the median beside the peak in its JSON line.

### Added

- `Runner.java`: a comment that a value-returning op must consume its result, or an
  optimizing build may delete the work and you measure nothing.

## [0.1.0]

### Added

- Initial Java template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `Gota.java` harness and a
  `Runner.java` seam. The op plugs in through a functional interface. Builds with
  `javac` and runs standalone.
