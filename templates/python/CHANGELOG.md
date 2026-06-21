# Changelog — Python template

Changes to **this language template only** (`templates/python/gota.py`, `runner.py`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

## [0.1.0]

### Added

- Initial Python template: implements the Gota protocol (peak-of-batches `bench()`
  loop, three CLI args, one JSON line) split into a copy-as-is `gota.py` harness and a
  `runner.py` seam (`run(impl, register)` then `bench(name, op)`). Verified to run
  standalone.
