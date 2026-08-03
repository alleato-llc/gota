# Changelog — Haskell template

Changes to **this language template only** (`templates/haskell/Gota.hs`, `runner.hs`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

### Changed

- Synced to protocol **1.2.0** (see the [core changelog](../../CHANGELOG.md)): the
  JSON line now carries a `protocol` field naming the version the runner implements.

## [0.1.0]

### Added

- Initial Haskell template: implements the Gota protocol (peak-of-batches timing loop,
  three CLI args, one JSON line with `mbps`/`mbps_median`/`iters`) split into a
  copy-as-is `Gota.hs` harness and a `runner.hs` seam. Builds with plain
  `ghc -O2 runner.hs -o runner` using only libraries that ship with GHC (`base` for the
  monotonic clock `GHC.Clock.getMonotonicTimeNSec`, args, and `printf`; the `bytestring`
  boot library for the buffer) — no Cabal/Stack. The op is `Word64 -> Word64`: the
  harness threads each result into the next call and forces it, so laziness can neither
  defer the work (a thunk) nor share it (one computation reused) — the
  dead-code-elimination/sink hazard in lazy form. The example seeds an FNV-1a fold with
  the accumulator accordingly.
