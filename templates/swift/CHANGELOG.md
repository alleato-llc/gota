# Changelog — Swift template

Changes to **this language template only** (`templates/swift/Gota.swift`, `runner.swift`,
`README.md`). Protocol- or harness-level changes that touch every language live in the
[core CHANGELOG](../../CHANGELOG.md); this file notes when the template is synced to
them. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current
version of every component is in [VERSIONS.md](../../VERSIONS.md).

## [0.1.0]

### Added

- Initial Swift template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line with `mbps`/`mbps_median`) split into a copy-as-is
  `Gota.swift` harness and a `runner.swift` seam. The op plugs in through a
  non-escaping closure over the `inout [UInt8]` buffer. Timing uses
  `DispatchTime.now().uptimeNanoseconds` (monotonic); builds with `swiftc -O` and runs
  standalone. The runner is an `@main struct` because `swiftc` reserves top-level code
  for `main.swift`.
