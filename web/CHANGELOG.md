# Changelog — Web

Changes to **the landing page only** (`web/`). This component is independent of
the protocol, harness, report, and language templates; protocol- or core-level
changes live in the [core CHANGELOG](../CHANGELOG.md). Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current version of
every component is in [VERSIONS.md](../VERSIONS.md).

## [Unreleased]

### Added

- A "What a micro-benchmark is" section (and a matching nav link) after the hero:
  a plain-language definition plus a comparison table placing gota among the
  traditional performance approaches (micro-benchmark vs macro/application
  benchmark vs profiling), and a note on the throughput-vs-latency distinction.
  Gives newcomers the context to read the rest of the page.
- In that section, a paragraph drawing the copy-don't-depend / cross-language
  distinction from criterion, JMH, and Google Benchmark (each a single-language
  dependency), so the section reinforces the hero's "the protocol is the product"
  framing rather than implying gota is a peer framework you install.

## [0.1.0]

### Added

- Initial landing page: a static Astro 5 + Preact site advertising Gota. The
  structure mirrors the sibling `dorado` project's `web/` (same stack, flat-file
  build, Layout / ThemeToggle / global.css split, section-and-card composition);
  the theming mirrors the sibling `soroban` site (Solarized light / Dracula dark
  via a `data-theme` attribute, with a warm secondary accent). One page covering
  the three layers, the seven language templates, the peak-of-batches protocol,
  and the honesty framing. No invented numbers; `npm run build` is the check.
- Responsive layout: a single 600px breakpoint wraps the header and the
  `auto-fit` card grids collapse to one column on a phone; the wide language
  comparison table scrolls inside its own box, so the document never overflows
  horizontally. Verified at a 390px viewport (`scrollWidth == clientWidth`).
