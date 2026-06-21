# Changelog — Java template

Changes to **this language template only** (`templates/java/Gota.java`, `Runner.java`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [Unreleased]

## [0.1.0]

### Added

- Initial Java template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line) split into a copy-as-is `Gota.java` harness and a
  `Runner.java` seam. The op plugs in through a functional interface. Builds with
  `javac` and runs standalone.
