# CLAUDE.md

Gota is a small, standalone reference for **cross-language throughput
micro-benchmarks**: a protocol, a generic Python orchestrator, per-language runner
templates, and an HTML report. It is meant to be **copied into other projects, not
depended on as a package** (the helpers are small, stable, and polyglot; no single
package manager spans all the languages). The first consumer is the `dorado` project's
`bench/`, which copies `harness.py`, `report.py`, and `report_template.html` from here.

Start with `README.md` (what it is, how to use it, the design diagram) and
`PROTOCOL.md` (the measurement recipe and the hard-won lessons). This file is for
working *on* Gota.

## Layout

- `PROTOCOL.md` — the **normative** contract every runner obeys: invocation, the JSON
  line, the four measurement steps, a conformance checklist, and the honesty rules. It
  carries its own semantic version (currently **1.1.0**, tracked in `VERSIONS.md`), so a
  consumer can state which protocol its copied runners implement and a stale copy is a
  checkable fact. This is the real product; the code is almost incidental.
- `docs/DESIGN.md` — the reasoning behind every requirement in `PROTOCOL.md`: why batches,
  why exponential search, why the peak rather than the mean, why the median alongside it,
  why a warmup, why the sink. The spec is short because this exists; when a requirement
  needs justifying, justify it here and keep the spec terse.
- `harness.py` — the generic orchestrator. `RunnerSpec` + `run_all` (build and run each
  runner as a subprocess under identical params with a per-runner `timeout`, collect their
  JSON, skipping a malformed line rather than aborting), `gather_metadata`
  (machine/os/date/git provenance, plus `toolchains=` compiler/runtime versions), the
  `Metric` enum (`BYTE_THROUGHPUT` / `OP_THROUGHPUT` / `LATENCY` — the kind measured, kept
  distinct from the free-text `units` label), and the output helpers `build_results_doc`,
  `render_markdown`, and `write_results` (which accepts a path or any writable stream).
  Also the comparison helpers `compare_runs` / `render_comparison_markdown` /
  `regressions` (a baseline vs one or more candidate runs, with a noise-band tolerance and
  provenance-mismatch warnings — comparability keys on the `metric` kind). Nothing
  project-specific lives here. Unit-tested in `tests/test_harness.py`.
- `templates/<lang>/` — two source files per language, plus a README and a CHANGELOG:
  - `gota.*` is the **harness**: the peak-of-batches `bench()` loop, arg parsing,
    buffer allocation, and JSON output. A consumer copies this as-is and does not edit
    it.
  - `runner.*` (and `Runner.java`) is the **user's code**: it plugs an operation into
    the harness through one seam (`run(impl, register)` then `bench(name, op)`). The
    committed op is a trivial example to keep the template runnable.
  - Languages: `python`, `rust`, `c`, `cpp`, `go`, `java`, `swift`, `zig`, `ts`,
    `haskell`.
- `report.py` + `report_template.html` — a generic HTML report. The script fills three
  tokens (`__TITLE__`, `__DATA__`, `__GENERATED__`) into the template and writes a
  self-contained, format-aware viewer (file picker, sortable table, per-language
  colors, magnitude bars, formatted units). Pass two or more results files (with
  `--baseline`) to get a comparison report; `--markdown` and `--fail-on-regression`
  turn the same comparison into a stdout delta table and a CI exit-code gate.
  Presentation lives in the template; the script does not change when you restyle.
- `examples/` — a complete miniature consumer (every language above) driven by a copy of
  `harness.py` and an `examples/run.py`, producing a generated `RESULTS.md`,
  `results.json`, and `report.html`. FNV-1a is the stand-in op.
- `web/` — the marketing landing page that advertises Gota: a static Astro 5 + Preact
  site, content only (no benchmark code, no invented numbers). Its structure mirrors the
  sibling `dorado` project's `web/`; its theming mirrors the sibling `soroban` site
  (Solarized light / Dracula dark). It is an independent component with its own
  `web/CLAUDE.md`, `web/README.md`, and `web/CHANGELOG.md`; it does not participate in the
  copy-it harness or the protocol.
- `CHANGELOG.md` + `templates/<lang>/CHANGELOG.md` + `web/CHANGELOG.md` + `VERSIONS.md` —
  versioning is per-component: a core changelog (protocol, harness, report, examples,
  docs), a changelog per language template, a web changelog, and a master table of every
  component's semver.

## The core invariant: keep the languages equivalent

Every `templates/<lang>/gota.*` implements the **same** protocol: same three CLI args,
same peak-of-batches loop (warm up, grow a batch to >= 100ms, then report the fastest
batch's MB/s), same JSON line `{"impl","bench","mbps","mbps_median","iters"}`. If you change the
protocol or the timing loop, change it in **all ten** language templates and in
`PROTOCOL.md`, or they stop being comparable. A protocol change also **bumps the Protocol
version** in `VERSIONS.md` (MAJOR if runners stop being comparable or parseable, MINOR for
a backward-compatible addition like `mbps_median`), and the rationale goes in
`docs/DESIGN.md`, not in the spec. This is the same discipline a multi-port
project uses to keep ports in sync; here the "ports" are the harness templates.

The seam is also uniform on purpose: `run(impl, register)` hands the user a bencher and
a buffer, and `bench(name, op)` is called once per operation. Keep that shape when
adding a language (C and Java vary only as far as the language forces: C uses a
function pointer + `void* ctx`, Java a functional interface, because neither has
closures — C++, which does have them, is header-only and takes a lambda like Rust).

## Adding a language

The language list lives in **eight** places. `languages.json` at the repo root is the
canonical one — the landing page imports it directly, so the page can no longer drift —
and `tests/test_languages.py` fails if any of the rest disagrees, naming the spot. Run
`python3 -m unittest discover tests` and let it drive you through:

1. **`languages.json`** — id, display name, the `files` line and card `body` for the
   page, plus `harness`/`seam`/`build` for its build-command row. Start here.
2. **`templates/<id>/`** — `gota.*` + `runner.*` + `README.md` + `CHANGELOG.md`.
3. **`examples/<id>/`** — the FNV-1a runner, so the example spans every language.
4. **`examples/run.py`** — a `prep_<id>` + `RunnerSpec`, a `TOOLCHAINS` probe, and
   entries in `IMPL_ORDER` / `IMPL_LABELS`.
5. **`.github/workflows/ci.yml`** — a paths-filter entry, a `changes` output, a job, and
   the language in `ci-passed`'s `needs:`. All four by hand; Actions needs static YAML.
   *Forgetting the gate entry is the dangerous one — that job's failures would no longer
   block a merge.*
6. **`README.md`** language table, **`VERSIONS.md`** row, and the core `CHANGELOG.md`.
7. **Regenerate the example artifacts** (`python3 examples/run.py`) on an idle machine so
   the new language appears in `RESULTS.md`/`results.json`/`report.html` — and remember
   that is a real benchmark run, so never do it on a loaded box or in CI.

The page needs no edit (step 1 covers it), but it is worth opening: `npm run build` in
`web/` and look at the rendered page. Swift and C++ each shipped with the repo complete
and the site silently a language behind, because every check was against the repo and
nobody looked at the site.

## Verifying changes

Templates must actually build and run. After touching a `gota.*` or the protocol,
re-run each affected language standalone (commands are in each `templates/<lang>/
README.md`), for example:

```
python3 templates/python/runner.py 65536 0.2 0.4
( cd templates/rust && rustc -O runner.rs -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/c    && cc -std=c17 -O2 runner.c gota.c -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/cpp  && c++ -std=c++20 -O2 runner.cpp -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/go   && go build -o runner . && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/java && javac Gota.java Runner.java && java Runner 65536 0.2 0.4 && rm *.class )
( cd templates/swift && swiftc -O Gota.swift runner.swift -o runner && ./runner 65536 0.2 0.4 && rm runner )
( cd templates/zig  && zig build-exe runner.zig -O ReleaseFast && ./runner 65536 0.2 0.4 && rm runner runner.zig.o )
node --experimental-strip-types templates/ts/runner.ts 65536 0.2 0.4   # or: npx tsx
( cd templates/haskell && ghc -O2 runner.hs -o runner && ./runner 65536 0.2 0.4 && rm -f runner *.hi *.o )
```

Each must print one JSON line (now `{"impl","bench","mbps","mbps_median","iters"}`). For
the orchestrator and report, run the unit tests, then the example end-to-end and
regenerate its artifacts:

```
python3 -m unittest discover tests      # harness.py unit tests (stdlib only)
python3 examples/run.py                 # writes examples/{results.json,RESULTS.md}
python3 report.py examples/results.json -o examples/report.html
```

When editing `report_template.html`, confirm the embedded JS still parses and renders
(extract the `<script>` and `node --check` it, or open the HTML).

The landing page builds standalone; after touching `web/`, confirm it still compiles:

```
( cd web && npm install && npm run build )   # static output in web/dist/
```

Preview it with `npm run dev` (or `npm run preview`), not by opening `web/dist/index.html`
from `file://` — Astro's root-absolute CSS path 404s there and renders the page unstyled.
The layout is responsive (one 600px breakpoint); see `web/CLAUDE.md`.

CI (`.github/workflows/ci.yml`) runs these same checks: one job per language template
(build and run it, assert a JSON line), a Python core job (py_compile, the
`tests/` unit suite, report generation, the example runner), and a `web` job that builds
the landing page. It is path-filtered, so a job runs only when its `templates/<lang>/`
changed; the core job also runs on a `tests/` change, the `web` job only on `web/**`, and
a change to `PROTOCOL.md` (the shared contract) or the workflow re-runs every template.
It runs on every PR and on pushes to `main`.

The one check to require in branch protection is **`ci-passed`**, the gate job at the
bottom: it always runs and fails only if some suite genuinely failed or was cancelled — a
*skipped* job (its paths didn't change) is a pass. Requiring the individual jobs instead
would leave them "Expected" forever on a partial-path PR. When you add a language
template, add its job to that gate's `needs:` list too, or its failures won't block a merge.

## Deploying the landing page

`.github/workflows/deploy-site.yml` publishes `web/` to **gota.alleato.dev** on every push
to `main` that touches `web/`, `examples/report.html` (the showcased report, copied into
the page at build time — regenerating it must redeploy), `salpa.yaml`, or the workflow;
nothing else triggers it, and it can be run by hand with `workflow_dispatch`. The deploy itself is `salpa deploy`
(the house release tool, pulled pinned from ghcr), configured by `salpa.yaml` at the repo
root: it builds `web/` with npm, syncs `web/dist` to S3, and invalidates the CloudFront
cache. Credentials are short-lived OIDC (`AWS_SITE_ROLE_ARN` as a **secret**, `AWS_REGION`
as a variable) — no stored keys, and no raw aws-cli in the workflow. The bucket, CDN, DNS,
and deploy role are provisioned separately as IaC, in a repo this one does not name (the
sibling projects deliberately dropped that reference from their public docs).

Gota publishes **no binaries** and cuts no releases, so unlike the sibling dorado/soroban
repos there is no release workflow and no `release:` trigger on the deploy. This mirrors
soroban's split otherwise: CI validates on PRs, the deploy ships from `main`.

Notes on toolchains: the Zig templates target **Zig 0.16** (args via
`std.process.Init`, timing via `std.Io.Clock`, buffered writer flushed before exit; see
the dorado port's `DEVELOPMENT.md` for the 0.16 API background). The TS template avoids
TypeScript parameter properties so it runs under Node's strip-only type stripping, not
just `tsx`.

## Consumers and syncing

`harness.py`, `report.py`, and `report_template.html` are copied verbatim into
consumers (the dorado `bench/` carries copies with a one-line provenance note in their
header). When you change any of these here, the consumer copies do not update
automatically; they must be re-copied. Treat a change to these three files as something
that ripples outward, and keep the change minimal and backward-compatible
(`write_results`'s positional `out_json, out_md` and its keyword args are part of that
contract).

## Conventions

- **No fabricated numbers.** Every benchmark figure must come from a real run on a
  stated machine; `RESULTS.md`/`results.json`/`report.html` are generated, never
  hand-edited. Do not commit numbers from CI (its hardware varies). There is exactly one
  copy of any given run: the landing page's showcased report is *copied* from
  `examples/report.html` at build time (`web/scripts/sync-report.mjs`), not duplicated
  into `web/public/`, because the duplicate drifted once already.
- **Honest framing.** Peak-of-batches is the *unimpeded* rate: right for comparing
  implementations, optimistic for real-world latency. Naive code shows
  language/runtime overhead, not how fast tuned/SIMD code can go. Say so.
- Keep `PROTOCOL.md`, `README.md`, and the per-language READMEs in step with the code.
- **Update the changelog as you go, routed by what you touched.** A change to the
  protocol, `harness.py`, `report.py`, `report_template.html`, `examples/`, or shared
  docs adds a bullet to the core `CHANGELOG.md`; a change to a single `templates/<lang>/`
  goes in that language's `templates/<lang>/CHANGELOG.md`; a change to the landing page
  goes in `web/CHANGELOG.md`. A protocol/core change that ripples into the templates is
  recorded once in the core log and pointed to from each affected language log (don't
  duplicate the rationale eight times). Add the bullet under Added / Changed / Fixed /
  Removed in the same commit or PR, and bump the component's version in `VERSIONS.md`
  when you cut a release. `VERSIONS.md` is the master table of every component and its
  current semver.
- Direct prose, minimal ceremony. Educational and unaudited; MIT licensed.
