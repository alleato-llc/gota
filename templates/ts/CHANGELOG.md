# Changelog — TypeScript template

Changes to **this language template only** (`templates/ts/gota.ts`, `runner.ts`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to the protocol's `mbps_median` addition (see the [core changelog](../../CHANGELOG.md)): `gota.ts` now records each measure-phase
  batch's rate and emits the median beside the peak in its JSON line.

### Added

- `runner.ts`: a comment that a value-returning op must consume its result, or an
  optimizing build may delete the work and you measure nothing.

## [0.1.0]

### Added

- Initial TypeScript template: implements the Gota protocol (peak-of-batches `bench()`
  loop, three CLI args, one JSON line) split into a copy-as-is `gota.ts` harness and a
  `runner.ts` seam (`run(impl, register)` then `bench(name, op)`). Avoids TypeScript
  parameter properties so it runs under Node's strip-only type stripping
  (`node --experimental-strip-types`), not just `tsx`.
