#!/usr/bin/env python3
"""Example Gota orchestrator. Builds the four example runners (Rust, C, Go, Python),
runs them under identical parameters, and writes results.json + RESULTS.md.

This is the project-specific config; the generic engine is in harness.py (copied from
Gota). A real consumer (see dorado/bench) looks just like this.

    python3 run.py
    GOTA_BUF=131072 GOTA_MEASURE=1.0 python3 run.py    # override params
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import harness
from harness import RunnerSpec

HERE = Path(__file__).resolve().parent
os.chdir(HERE)

BUF = int(os.environ.get("GOTA_BUF", 65536))
WARMUP = float(os.environ.get("GOTA_WARMUP", 0.5))
MEASURE = float(os.environ.get("GOTA_MEASURE", 1.5))


def _build(cmd: list[str], cwd: str) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def prep_python():
    return ["python3", "python/runner.py"]


def prep_c():
    if not harness.which("cc"):
        return None
    _build(["cc", "-std=c17", "-O2", "runner.c", "gota.c", "-o", "runner"], cwd="c")
    return ["c/runner"]


def prep_go():
    if not harness.which("go"):
        return None
    _build(["go", "build", "-o", "runner", "."], cwd="go")
    return ["go/runner"]


def prep_rust():
    if not harness.which("rustc"):
        return None
    _build(["rustc", "-O", "runner.rs", "-o", "runner"], cwd="rust")
    return ["rust/runner"]


SPECS = [
    RunnerSpec("python", prep_python),
    RunnerSpec("c", prep_c),
    RunnerSpec("go", prep_go),
    RunnerSpec("rust", prep_rust),
]

IMPL_ORDER = ["rust", "c", "go", "python"]
IMPL_LABELS = {"rust": "Rust", "c": "C", "go": "Go", "python": "Python"}
BENCH_ORDER = ["fnv1a-64"]
BENCH_LABELS = {"fnv1a-64": "FNV-1a 64"}


def intro(meta: dict) -> str:
    return f"""\
Example Gota run: FNV-1a over a {BUF // 1024} KiB buffer in four languages under one
protocol. Peak MB/s (decimal, 1e6 bytes), higher is better.

This demonstrates the harness; it is not a serious language comparison. FNV-1a is a
trivial serial byte reduction, so these numbers reflect each compiler's handling of a
tight scalar loop, nothing more.

Machine: {meta['machine']} | {meta['os']} | {meta['date']} | commit {meta['git_commit']}.
"""


def main() -> None:
    harness.log(f"params: buf={BUF} warmup={WARMUP} measure={MEASURE}")
    rows = harness.run_all(SPECS, BUF, WARMUP, MEASURE)
    meta = harness.gather_metadata()
    harness.write_results(
        rows,
        "results.json",
        "RESULTS.md",
        params={"buffer_bytes": BUF, "warmup_s": WARMUP, "measure_s": MEASURE},
        meta=meta,
        units="MB/s (decimal, 1e6 bytes), peak of batches",
        impl_order=IMPL_ORDER,
        impl_labels=IMPL_LABELS,
        bench_order=BENCH_ORDER,
        bench_labels=BENCH_LABELS,
        intro=intro(meta),
    )


if __name__ == "__main__":
    main()
