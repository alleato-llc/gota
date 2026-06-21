# gota web

The landing page that advertises gota. A static [Astro](https://astro.build/)
site with a Preact theme toggle, mirroring the setup of the sibling `dorado`
project's `web/` (its structure) and `soroban` project's `site/` (its theming).

## Develop

```
npm install
npm run dev      # local dev server
npm run build    # static output to dist/
npm run preview  # serve the built dist/
```

Always view it through one of these servers, not by opening `dist/index.html`
directly: Astro links the stylesheet with a root-absolute path (`/_astro/*.css`),
which 404s under `file://` and renders the page unstyled.

The layout is responsive. It is single-column and centered on desktop, and below a
600px breakpoint the header wraps and the card grids collapse to one column; the wide
language comparison table scrolls within its own box rather than overflowing the page.

## Layout

- `src/pages/` — one `.astro` file per route (`index.astro` is the home page).
- `src/layouts/Layout.astro` — the shared shell (head, header, footer, theme
  bootstrap).
- `src/components/ThemeToggle.tsx` — the Preact theme toggle island.
- `src/styles/global.css` — the two-theme design system (light / dark via the
  `data-theme` attribute on `:root`).
- `public/` — static assets served as-is: the favicon, and the showcased example
  report (`report.html`) linked from the "See a live report" section. It is a copy
  of the generated `examples/report.html` (regenerate with `python3 examples/run.py`
  then `report.py`, and re-copy into `public/`); like the rest of the example
  artifacts it is generated, never hand-edited. The report carries a MB/s ⇄ ops/sec
  toggle, so one page shows both units.

## Theming

The palette is lifted from the sibling `soroban` site so the two read as a
family: light is Solarized, dark is Dracula, with a warm secondary accent
(Solarized yellow / Dracula orange). The structure (Astro 5 + `@astrojs/preact`,
`build: { format: "file" }`, the Layout / ThemeToggle / global.css split, the
section-and-card composition of `index.astro`) follows the `dorado` `web/`.

The copy is kept truthful, matching the repo's honesty rule: gota reports peak
(unimpeded) throughput, makes no lab-grade-absolute claims, and shows no
invented benchmarks. Update the `REPO` constant in `src/pages/index.astro` once
the repository URL is final.
