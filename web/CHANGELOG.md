# Changelog — Web

Changes to **the landing page only** (`web/`). This component is independent of
the protocol, harness, report, and language templates; protocol- or core-level
changes live in the [core CHANGELOG](../CHANGELOG.md). Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current version of
every component is in [VERSIONS.md](../VERSIONS.md).

## [Unreleased]

### Added

- **A deploy pipeline for the page.** `.github/workflows/deploy-site.yml` publishes `web/`
  to **gota.alleato.dev** on pushes to `main` that touch `web/` (plus `workflow_dispatch`),
  via `salpa deploy` (pinned from ghcr) configured by the new root `salpa.yaml`: npm build,
  sync `web/dist` to S3, invalidate CloudFront. Auth is short-lived OIDC — `AWS_SITE_ROLE_ARN`
  is a **secret** (a variable is not redacted in the step's own log preamble), `AWS_REGION`
  a variable; the bucket/CDN/DNS/role are provisioned separately as IaC.
  Mirrors the dorado and soroban site deploys, minus their release triggers — gota ships no
  binaries. The matching pre-merge build job is in the [core CHANGELOG](../CHANGELOG.md).
- `scripts/sync-report.mjs`, wired as npm's `prebuild`/`predev`, copies
  `examples/report.html` into `public/report.html` at build time (including the build
  `salpa deploy` runs). `public/report.html` is now gitignored rather than committed.
- A "What a micro-benchmark is" section (and a matching nav link) after the hero:
  a plain-language definition plus a comparison table placing gota among the
  traditional performance approaches (micro-benchmark vs macro/application
  benchmark vs profiling), and a note on the throughput-vs-latency distinction.
  Gives newcomers the context to read the rest of the page.
- In that section, a paragraph drawing the copy-don't-depend / cross-language
  distinction from criterion, JMH, and Google Benchmark (each a single-language
  dependency), so the section reinforces the hero's "the protocol is the product"
  framing rather than implying gota is a peer framework you install.

- A "See a live report" section (and a `Report` nav link) showcasing the generated
  example report, served from `public/` (soroban-style): one self-contained
  `report.html` with a MB/s ⇄ ops/sec toggle, so a single page shows the same FNV run in
  both units.
- Haskell added as the eighth language: a card in the languages grid, a row in the
  build-commands table, and the "seven languages" copy updated to eight throughout.
- A "The easiest way to measure nothing" section (and a `Pitfalls` nav link) on the
  dead-code-elimination / laziness hazard and gota's sink discipline — non-obvious, and
  the reason Haskell's seam threads-and-forces an accumulator.

### Changed

- Reflect the latest protocol/orchestrator changes: the JSON line now reads
  `{"impl","bench","mbps","mbps_median","iters"}` (Measure card + protocol
  checklist), the peak-of-batches item notes the peak-vs-median stability check,
  the orchestrator records toolchain-version provenance, and the report card
  mentions metric-aware units (MB/s or ops/sec). No latency/IO claims — those are
  design-only and unshipped.

### Fixed

- The page was **two languages behind the repo**: it advertised "Eight languages" with
  eight cards and eight table rows, missing both Swift (added to the repo in July but
  never to the page) and C++. Added a card and a build-row for each, in the README's
  order, and corrected every count in the copy — the hero, the meta description, the
  section heading, the badge line, the protocol/report/pitfall paragraphs — from eight to
  ten. The languages array and the build table are hand-maintained here and are not
  derived from `templates/`, so adding a language means editing this file too.
- The site deploy now also triggers on `examples/report.html`. The showcased report is
  copied into the page at build time but lives outside `web/`, so a regenerated example
  did not redeploy — the published report could silently lag the repo (it did: `main`
  carried the ten-language run while the site still served the nine-language one). The
  build-time copy guarantees the two match *when a deploy runs*; this makes one run.
- Every "view the source" link pointed at a repository that isn't this one: the page's
  single `REPO` constant read `github.com/nycjv321/gota` while the remote is
  `alleato-llc/gota`, so all of them 404'd. Corrected at the constant.
- The showcased report no longer drifts from the example it claims to be. The committed
  `public/report.html` had gone stale — it embedded a 2026-06-21 run while
  `examples/report.html` (same machine) carried 2026-07-06, so the published page
  advertised older numbers than the repo. It is now copied at build time from the single
  source under `examples/`, and a missing source fails the build instead of shipping a
  dead link. The copy step never *generates* numbers: CI hardware varies, so the figures
  can only come from a real run on a stated machine.

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
