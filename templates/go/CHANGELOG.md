# Changelog — Go template

Changes to **this language template only** (`templates/go/gota.go`, `runner.go`,
`go.mod`, `README.md`). Protocol- or harness-level changes that touch every language
live in the [core CHANGELOG](../../CHANGELOG.md); this file notes when the template is
synced to them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The
current version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to protocol **1.2.0** (see the [core changelog](../../CHANGELOG.md)): the
  JSON line now carries a `protocol` field naming the version the runner implements.

- Synced to the protocol's `mbps_median` addition (see the [core changelog](../../CHANGELOG.md)): `gota/gota.go` now records each measure-phase
  batch's rate and emits the median beside the peak in its JSON line.

### Added

- `runner.go`: a comment that a value-returning op must consume its result, or an
  optimizing build may delete the work and you measure nothing.

## [0.1.0]

### Added

- Initial Go template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `gota` harness and a
  `runner.go` seam (`run(impl, register)` then `bench(name, op)`). Builds with
  `go build` and runs standalone.
