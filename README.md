# Gota

A small, copy-it reference for **cross-language throughput micro-benchmarks**.

When you have the same operation implemented in several languages and want an honest,
*comparable* picture of how fast each implementation's own code runs, Gota gives you:

- **A protocol** (see [`PROTOCOL.md`](PROTOCOL.md)) every runner follows, so the
  numbers compare even though each runner is native to its language.
- **A generic orchestrator** ([`harness.py`](harness.py)) that builds and runs your
  runners with identical parameters, collects their JSON, records provenance, and
  writes `results.json` + a Markdown table.
- **Per-language templates** ([`templates/`](templates/)) — two files per language:
  `gota.*` (the harness: the peak-of-batches timing loop, copy as-is) and `runner.*`
  (your code: the operation, plugged in through one seam). See the
  [languages](#languages) below.
- **A generic HTML report** ([`report.py`](report.py)) that turns any results.json
  into a standalone, sortable viewer with a file picker.

The reusable thing here is the **protocol and the lessons**, not the code: a
peak-of-batches loop is ~20 lines you can re-type once you know the recipe. So Gota
is meant to be **copied, not depended on** — the helpers are small, stable, and
polyglot (no single package manager spans Rust, Go, Zig, C, Java, Python, and
TypeScript), so copying is the pragmatic, low-harm choice. Re-copy when the protocol
improves.

## Design

Three layers, with one contract (the protocol) between the bottom two. The arrows are
data flow; what you copy versus what you write is marked.

```
   ┌─ PROTOCOL.md ─ the contract every runner and the orchestrator agree on ─┐
   │   in  (argv):   <buffer_bytes> <warmup_s> <measure_s>                    │
   │   out (stdout): {"impl","bench","mbps","iters"}   one line per benchmark │
   └─────────────────────────────────────────────────────────────────────────┘

   1. MEASURE — native code, one runner per language
      ┌───────────────────────────────────────────────┐
      │  gota.<lang>    the harness        (copy as-is) │
      │     bench(name, op): peak-of-batches timing     │
      │          ▲  your op plugs in here               │
      │  runner.<lang>  YOUR code                       │
      │     run(impl, register) → b.bench(name, op)     │
      └───────────────────────────────────────────────┘
                       │  prints JSON lines on stdout
                       ▼
   2. ORCHESTRATE — Python, once, across all languages
      ┌───────────────────────────────────────────────┐
      │  run.py      YOUR config (RunnerSpecs, labels)  │
      │  harness.py  the engine            (copy as-is) │
      │     run_all(): build + invoke each runner       │
      │     write_results(): collect JSON, tabulate     │
      └───────────────────────────────────────────────┘
                       │  writes
                       ▼
              results.json   +   RESULTS.md
                       │
   3. REPORT — optional, generic over the format
      ┌────────────────▼──────────────────────────────┐
      │  report.py  reads a results.json                │
      │     → report.html: file picker, sortable,       │
      │       formatted numbers (84.3 MB/s)             │
      └───────────────────────────────────────────────┘
```

A runner (layer 1) is usable on its own; the orchestrator (layer 2) is only the
conductor that runs them together and tabulates; the report (layer 3) is a pure
consumer of `results.json`. You can stop at any layer.

## How to use it

There are three pieces, and you only write part of one of them:

| Piece | Who writes it | What it does |
| --- | --- | --- |
| `gota.*` (per language) | **copied as-is** | the in-process timing loop; prints one JSON line per op |
| `runner.*` (per language) | **you edit the op** | plugs your operation into `gota.*` |
| `harness.py` + `run.py` | **copied + you write `run.py`** | the cross-language orchestrator that builds, runs, and tabulates the runners |

Steps:

1. **Copy** `harness.py` into your project, and the `templates/<lang>` files for each
   language you benchmark.
2. In each `runner.*`, replace the example operation with **your** operation. Leave
   `gota.*` untouched. Each runner is independently runnable at this point (see the
   per-language READMEs).
3. **Write a `run.py`** (next section) that tells the orchestrator how to build and
   invoke each runner.
4. Run `python3 run.py`. It builds every runner, runs each with identical parameters,
   collects their JSON, and **generates** `results.json` and `RESULTS.md`.

### What `run.py` is, and what you write in it

`harness.py` is the generic engine and never changes. `run.py` is the one
project-specific file you author: it is the *configuration* that points the engine at
your runners. After copying `harness.py`, a `run.py` needs four things:

```python
import subprocess
import harness
from harness import RunnerSpec

# 1. One RunnerSpec per runner. `prepare` builds it (compile, etc.) and returns the
#    argv to invoke it, or None to skip it when a toolchain is missing. The harness
#    appends the three protocol numbers (buffer, warmup, measure) when it runs it.
def prep_rust():
    if not harness.which("rustc"):
        return None
    subprocess.run(["rustc", "-O", "runner.rs", "-o", "runner"], cwd="rust", check=True)
    return ["rust/runner"]

SPECS = [RunnerSpec("rust", prep_rust), ...]

# 2. How to label and order the table's rows (implementations) and columns (benches).
IMPL_ORDER  = ["rust", ...]; IMPL_LABELS  = {"rust": "Rust", ...}
BENCH_ORDER = ["fnv1a-64"];  BENCH_LABELS = {"fnv1a-64": "FNV-1a 64"}

# 3. The framing text printed above the table (what was measured, on what machine).
def intro(meta): return f"... {meta['machine']} {meta['date']} ..."

# 4. Wire it together: run everything, then write the outputs.
def main():
    rows = harness.run_all(SPECS, buf=65536, warmup=0.5, measure=1.5)
    meta = harness.gather_metadata()
    harness.write_results(rows, "results.json", "RESULTS.md",
        params={...}, meta=meta, units="MB/s, peak of batches",
        impl_order=IMPL_ORDER, impl_labels=IMPL_LABELS,
        bench_order=BENCH_ORDER, bench_labels=BENCH_LABELS, intro=intro(meta))
```

[`examples/run.py`](examples/run.py) is a complete, working version of exactly this
(four languages). Copy it and adjust the four parts above.

### Where `RESULTS.md` comes from

`RESULTS.md` (and `results.json`) are **generated by `run.py`**, not written by hand —
`harness.write_results` formats the collected numbers into the Markdown table and the
JSON, stamping in the machine, date, and git commit. You commit the generated files as
a snapshot; re-running `run.py` overwrites them. The example's
[`RESULTS.md`](examples/RESULTS.md) was produced this way on the stated machine, never
edited afterward.

## Languages

Two files per language; the per-language README has the exact build/run command and
any language-specific notes.

| Language | Files | Doc |
| --- | --- | --- |
| Python | `templates/python/{gota.py, runner.py}` | [README](templates/python/README.md) |
| Rust | `templates/rust/{gota.rs, runner.rs}` | [README](templates/rust/README.md) |
| C | `templates/c/{gota.h, gota.c, runner.c}` | [README](templates/c/README.md) |
| Go | `templates/go/{go.mod, gota/gota.go, runner.go}` | [README](templates/go/README.md) |
| Java | `templates/java/{Gota.java, Runner.java}` | [README](templates/java/README.md) |
| Zig | `templates/zig/{gota.zig, runner.zig}` | [README](templates/zig/README.md) |
| TypeScript | `templates/ts/{gota.ts, runner.ts}` | [README](templates/ts/README.md) |

For a complete worked consumer that ties several of these together, see
[`examples/`](examples/).

## HTML report

`report.py` fills in [`report_template.html`](report_template.html) to produce a
single self-contained `report.html` — no build step, no network, no dependencies. The
presentation (HTML/CSS/JS) lives entirely in the template; the script only substitutes
the title, the embedded data, and the date. To restyle the report, **edit the
template, not the script** (or pass `--template your.html`). It is generic over the
*format*: it renders only what the JSON carries (the impl/bench/mbps rows plus the
machine/date/params provenance), so the same template works for any project.

```
python3 report.py results.json -o report.html --title "My project throughput"
python3 report.py                 # empty viewer; load a results.json from the page
```

The page has a **file picker**, so one generated `report.html` can open any
`results.json` you hand it later (drop the file in, it re-renders). Passing a
`results.json` on the command line just embeds it so the page is populated on open.
Numbers are formatted with units (`84.3 MB/s`, not `84.3`); each cell carries a
magnitude bar tinted with a per-language color; columns sort on click; and the best
value per column is starred. The example's report is committed at
[`examples/report.html`](examples/report.html).

## Using it in your own tooling

Nothing here is a closed pipeline; pick the layer that fits and route the rest into
your own systems (CI, a dashboard, a database, a PR comment):

- **Just the numbers.** `harness.run_all(specs, buf, warmup, measure)` returns a plain
  `list[dict]` (`{"impl","bench","mbps","iters"}`). Do whatever you want with it;
  ignore the rest of the harness.
- **The JSON document.** `harness.build_results_doc(rows, params=, meta=, units=)`
  returns the `results.json` dict (rows + provenance). Serialize it where you like.
- **The Markdown string.** `harness.render_markdown(rows, intro=, impl_order=, ...)`
  returns the table as a string, for a PR comment or a docs page.
- **Stream the outputs.** `harness.write_results(...)` accepts a path *or any open
  writable stream* for each output, so you can send the JSON or Markdown to
  `sys.stdout`, an `io.StringIO`, or an HTTP response body instead of a file:

  ```python
  import io, sys, harness
  buf = io.StringIO()
  harness.write_results(rows, buf, sys.stdout, params=..., meta=..., units=..., ...)
  post_to_dashboard(buf.getvalue())   # the results.json text
  ```

- **The HTML.** Feed your `results.json` to `report.py` (above), or call
  `report.build_html(doc, title)` to get the HTML string.

## What it is not

- Not a nanosecond-latency tool (timing one tiny op with statistical outlier
  rejection) — for that use a per-language framework like criterion or JMH.
- Not lab-grade absolute numbers — it reports *peak* (unimpeded) throughput on a
  normal machine, which is right for *comparing* implementations. For reproducible
  absolutes you would pin cores, lock frequency, and use a dedicated box.

## Origin

Gota was extracted from the benchmark harness of the
[dorado](https://github.com/nycjv321/dorado) project (a from-scratch cipher
implemented in eight languages), which remains its first consumer and proving ground.
The name is *gota*, "drop" in Spanish/Portuguese — measuring throughput drop by drop.

Educational; MIT licensed.
