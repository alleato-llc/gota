# CLAUDE.md

This is the `web/` part of gota: the marketing landing page. The benchmark
harness it advertises lives in the repo root (`../harness.py`, `../report.py`,
`../PROTOCOL.md`, `../templates/`); see `../CLAUDE.md`.

## What this is

A static [Astro](https://astro.build/) 5 site with the `@astrojs/preact`
integration and TypeScript. The **structure** mirrors the sibling `dorado`
project's `web/` (same stack, same file layout, same theme-toggle pattern); the
**theming** mirrors the sibling `soroban` site (Solarized light / Dracula dark).
Keeping all three consistent is the point.

- `astro.config.mjs` sets `build: { format: "file" }` so routes emit flat
  `name.html` files for static hosts.
- `src/layouts/Layout.astro` is the shared shell. An inline script resolves the
  theme before first paint: a stored choice (`localStorage["gota-theme"]`) wins,
  otherwise it follows the system and keeps following it until the user picks.
- `src/components/ThemeToggle.tsx` is a Preact island (`client:load`) that flips
  and persists the theme.
- `src/styles/global.css` is the design system: two themes via the `data-theme`
  attribute on `:root`, with CSS custom properties. Light is Solarized, dark is
  Dracula, with a warm secondary accent (`--gold`) for badges, counters, the
  comparison table's Python row, and the honesty note.
- `src/pages/` holds one file per route. `public/` is served as-is, and includes
  `report.html`, linked from the "See a live report" section. The report has a MB/s ⇄
  ops/sec toggle, so one page shows the same example run in both units (demonstrating the
  metric-aware report).

  **`public/report.html` is generated, not committed.** `scripts/sync-report.mjs` copies
  `examples/report.html` into it on every `npm run build` / `npm run dev` (npm's
  `prebuild`/`predev` hooks), and it is gitignored. It used to be a checked-in copy, which
  drifted — the published page was a run three weeks older than the committed example. So:
  regenerate under `examples/` (`python3 examples/run.py`, then `report.py`) and the site
  picks it up; never hand-edit either copy, and never re-add the file to git. The script
  only copies — it must never *generate* numbers, since a CI machine's hardware varies
  (the no-fabricated-numbers rule in the root `CLAUDE.md`). A missing
  `examples/report.html` fails the build loudly rather than shipping a page with a dead
  link.

There is no in-browser demo (unlike dorado's `web/`): gota is a copy-it
reference for a measurement protocol, not a runnable artifact, so the page is
content only — no WASM, no extra dependencies.

## Conventions

- The copy is persuasive but truthful, matching the repo's honesty rule. gota
  reports peak (unimpeded) throughput, not lab-grade absolutes or latency, and
  shows no invented benchmarks. Do not add numbers to this page.
- Keep the stack minimal: Astro + Preact + TypeScript. Do not add a UI framework
  or dependencies without asking first.
- `REPO` in `src/pages/index.astro` is the single source for the repository URL;
  update it there.
- Keep the language list and build commands in step with the repo root
  `README.md` and each `../templates/<lang>/README.md`.

## Verify

```
npm install
npm run build
```

A successful `npm run build` (static output in `dist/`) is the check.

Preview over a server (`npm run dev`, or `npm run preview` after a build), **not**
by opening `dist/index.html` from `file://`. Astro emits a root-absolute stylesheet
link (`/_astro/*.css`); under `file://` that resolves to the filesystem root, 404s,
and the page renders unstyled. The same applies to any headless-screenshot check:
serve `dist/` over HTTP first, or the CSS will not load.

## Responsive

The page is mobile-first and single-column by nature. The one breakpoint is
`@media (max-width: 600px)` in `global.css`: below it the header wraps (wordmark and
toggle on the top row, the nav on its own centered row). The card grids are
`auto-fit, minmax(...)`, so they collapse from three or two columns to one on a phone
with no extra rules. The only element wider than a phone is the language comparison
table; it lives in `.cmp-scroll` (`overflow-x: auto`) so it scrolls **within its own
box** rather than widening the page. The document itself never overflows horizontally
(`scrollWidth == clientWidth` at 390px). Note headless Chrome clamps `--window-size`
to a 500px minimum, so a true sub-500px capture needs device emulation
(`Emulation.setDeviceMetricsOverride`), not just a narrow window.
