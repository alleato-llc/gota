# Changelog — C++ template

Changes to **this language template only** (`templates/cpp/gota.hpp`, `runner.cpp`,
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

- Initial C++ template: implements the Gota protocol (peak-of-batches `bench()` loop,
  three CLI args, one JSON line with `mbps`/`mbps_median`) split into a copy-as-is
  `gota.hpp` harness and a `runner.cpp` seam. The op plugs in as a lambda over a
  `std::span<std::uint8_t>` buffer. Timing uses `std::chrono::steady_clock`
  (monotonic); builds with `c++ -std=c++20 -O2` and runs standalone.
- Header-only, unlike the sibling C template: because C++ has lambdas, `bench` is a
  template and the op inlines into the timing loop (the same seam Rust's `impl FnMut()`
  gives), so the function-pointer + `void* ctx` indirection C needs has no counterpart
  here and there is no `gota.cpp`.
