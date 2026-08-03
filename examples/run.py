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


def prep_cpp():
    if not harness.which("c++"):
        return None
    _build(["c++", "-std=c++20", "-O2", "runner.cpp", "-o", "runner"], cwd="cpp")
    return ["cpp/runner"]


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


def prep_zig():
    if not harness.which("zig"):
        return None
    _build(["zig", "build-exe", "runner.zig", "-O", "ReleaseFast"], cwd="zig")
    return ["zig/runner"]


def prep_java():
    if not (harness.which("javac") and harness.which("java")):
        return None
    _build(["javac", "Gota.java", "Runner.java"], cwd="java")
    return ["java", "-cp", "java", "Runner"]


def prep_ts():
    if not harness.which("node"):
        return None
    return ["node", "--experimental-strip-types", "ts/runner.ts"]


def prep_haskell():
    if not harness.which("ghc"):
        return None
    _build(["ghc", "-O2", "runner.hs", "-o", "runner"], cwd="haskell")
    return ["haskell/runner"]


def prep_swift():
    if not harness.which("swiftc"):
        return None
    _build(["swiftc", "-O", "Gota.swift", "runner.swift", "-o", "runner"], cwd="swift")
    return ["swift/runner"]


SPECS = [
    RunnerSpec("python", prep_python),
    RunnerSpec("c", prep_c),
    RunnerSpec("cpp", prep_cpp),
    RunnerSpec("go", prep_go),
    RunnerSpec("rust", prep_rust),
    RunnerSpec("zig", prep_zig),
    RunnerSpec("java", prep_java),
    RunnerSpec("swift", prep_swift),
    RunnerSpec("ts", prep_ts),
    RunnerSpec("haskell", prep_haskell),
]

# Version probes for the toolchains this run uses, recorded into the results'
# provenance (absent tools are skipped). A number is only reproducible with the
# compiler that produced it.
TOOLCHAINS = {
    "rust": ["rustc", "--version"],
    "c": ["cc", "--version"],
    "cpp": ["c++", "--version"],
    "go": ["go", "version"],
    "zig": ["zig", "version"],
    "java": ["java", "-version"],
    "swift": ["swift", "--version"],
    "python": ["python3", "--version"],
    "ts": ["node", "--version"],
    "haskell": ["ghc", "--numeric-version"],
}

IMPL_ORDER = ["rust", "c", "cpp", "go", "zig", "java", "swift", "haskell", "python", "ts"]
IMPL_LABELS = {
    "rust": "Rust", "c": "C", "cpp": "C++", "go": "Go", "zig": "Zig", "java": "Java",
    "swift": "Swift", "haskell": "Haskell", "python": "Python", "ts": "TypeScript",
}
BENCH_ORDER = ["fnv1a-64"]
BENCH_LABELS = {"fnv1a-64": "FNV-1a 64"}


def intro(meta: dict) -> str:
    return f"""\
Example Gota run: FNV-1a over a {BUF // 1024} KiB buffer in ten languages under one
protocol. Peak MB/s (decimal, 1e6 bytes), higher is better; results.json also records
each run's median rate (mbps_median) as a stability signal.

This demonstrates the harness; it is not a serious language comparison. FNV-1a is a
trivial serial byte reduction, so these numbers reflect each runtime's handling of a
tight scalar loop, nothing more (the TypeScript runner uses BigInt for 64-bit math,
which is genuinely slow — an honest artifact, not a bug; the Haskell runner threads and
forces an accumulator so laziness cannot defer or share the work).

Machine: {meta['machine']} | {meta['os']} | {meta['date']} | commit {meta['git_commit']}.
"""


def main() -> None:
    harness.log(f"params: buf={BUF} warmup={WARMUP} measure={MEASURE}")
    rows = harness.run_all(SPECS, BUF, WARMUP, MEASURE)
    meta = harness.gather_metadata(toolchains=TOOLCHAINS)
    params = {"buffer_bytes": BUF, "warmup_s": WARMUP, "measure_s": MEASURE}
    harness.write_results(
        rows,
        "results.json",
        "RESULTS.md",
        params=params,
        meta=meta,
        metric=harness.Metric.BYTE_THROUGHPUT,
        units="MB/s (decimal, 1e6 bytes), peak of batches",
        impl_order=IMPL_ORDER,
        impl_labels=IMPL_LABELS,
        bench_order=BENCH_ORDER,
        bench_labels=BENCH_LABELS,
        intro=intro(meta),
    )


if __name__ == "__main__":
    main()
