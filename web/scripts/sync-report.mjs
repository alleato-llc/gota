// Copy the generated example report into public/ so the site publishes the SAME
// artifact the repo commits, rather than a checked-in duplicate that silently
// drifts (it had: the committed copy was an older run than examples/report.html).
//
// Wired as npm's `prebuild`/`predev` hook, so every `npm run build` refreshes it —
// including the one `salpa deploy` runs (`npm ci && npm run build` in web/).
// public/report.html is gitignored; this script is the only thing that writes it.
//
// It COPIES, never generates. The numbers come from a real run on a stated machine
// (`python3 examples/run.py`, then `report.py`), committed under examples/. CI
// hardware varies, so CI must never produce them — see the no-fabricated-numbers
// rule in CLAUDE.md.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "examples", "report.html");
const dest = join(here, "..", "public", "report.html");

if (!existsSync(src)) {
  console.error(
    "sync-report: missing examples/report.html — regenerate it with:\n" +
      "  python3 examples/run.py && python3 report.py examples/results.json -o examples/report.html",
  );
  process.exit(1);
}

mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log("sync-report: public/report.html <- examples/report.html");
