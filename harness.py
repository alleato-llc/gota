"""Gota: a generic cross-language micro-benchmark orchestrator.

This file is project-agnostic. It runs a list of `RunnerSpec`s (each builds itself
and emits JSON lines of {"impl","bench","mbps","iters"}), collects the rows, and
writes a results.json plus a Markdown table. The project-specific configuration
(which runners, the row/column labels, the framing text) lives in a `run.py` that
imports this and supplies those, so the engine here never changes.

Copy this file into your project as-is; write a `run.py` that declares your runners
and calls `run_all` + `write_results`. See README.md and PROTOCOL.md.
"""

from __future__ import annotations

import dataclasses
import json
import platform
import shutil
import subprocess
import sys
from typing import Callable, Optional


def which(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


@dataclasses.dataclass
class RunnerSpec:
    """One benchmark runner.

    `prepare` builds/sets up the runner and returns the argv to invoke it (the three
    protocol parameters are appended by the harness), or None if the runner is
    unavailable (a missing toolchain) and should be skipped. It may raise on a build
    failure; the harness logs and skips.
    """

    name: str
    prepare: Callable[[], Optional[list[str]]]


def run_all(specs: list[RunnerSpec], buf: int, warmup: float, measure: float) -> list[dict]:
    """Build and run each available runner with identical parameters; collect the
    JSON-line results. Each runner's stdout is captured separately, so there is no
    shared-output ordering or interleaving."""
    rows: list[dict] = []
    for spec in specs:
        try:
            argv = spec.prepare()
        except Exception as e:  # build failure, etc.
            log(f"  {spec.name}: prepare failed ({e}), skipping")
            continue
        if argv is None:
            log(f"  {spec.name}: unavailable, skipping")
            continue
        log(f"  {spec.name}: running")
        proc = subprocess.run(
            [*argv, str(buf), str(warmup), str(measure)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            log(f"  {spec.name}: runner exited {proc.returncode}; stderr:\n{proc.stderr.strip()}")
            continue
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                rows.append(json.loads(line))
    return rows


def gather_metadata() -> dict:
    """Machine, OS, date, and git commit, for provenance in the results."""
    machine = "unknown"
    try:
        if platform.system() == "Darwin":
            machine = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
        else:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        machine = line.split(":", 1)[1].strip()
                        break
    except Exception:
        pass
    commit = "unknown"
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        pass
    return {
        "machine": machine,
        "os": f"{platform.system()} {platform.machine()}",
        "date": subprocess.check_output(["date", "+%Y-%m-%d"], text=True).strip(),
        "git_commit": commit,
    }


def write_results(
    rows: list[dict],
    out_json: str,
    out_md: str,
    *,
    params: dict,
    meta: dict,
    units: str,
    impl_order: list[str],
    impl_labels: dict[str, str],
    bench_order: list[str],
    bench_labels: dict[str, str],
    intro: str,
) -> None:
    """Write results.json (raw + provenance) and a Markdown table. The orderings,
    labels, and intro text are supplied by the caller, so this stays generic."""
    doc = {**meta, "params": params, "units": units, "results": rows}
    with open(out_json, "w") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    by = {(r["impl"], r["bench"]): r["mbps"] for r in rows}
    present = [i for i in impl_order if any(r["impl"] == i for r in rows)]

    lines = ["# Benchmark results", "", intro.strip(), ""]
    lines.append("| Implementation | " + " | ".join(bench_labels[b] for b in bench_order) + " |")
    lines.append("| --- | " + " | ".join("---:" for _ in bench_order) + " |")
    for impl in present:
        cells = []
        for b in bench_order:
            v = by.get((impl, b))
            cells.append(f"{v:.1f}" if v is not None else "-")
        lines.append(f"| {impl_labels[impl]} | " + " | ".join(cells) + " |")
    lines.append("")
    with open(out_md, "w") as f:
        f.write("\n".join(lines))

    log(f"wrote {out_json} and {out_md} ({len(rows)} measurements, {len(present)} implementations)")
