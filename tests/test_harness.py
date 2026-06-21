#!/usr/bin/env python3
"""Unit tests for harness.py — the generic orchestrator.

These cover the pure, deterministic logic that the example only smoke-tests: the
Metric enum and results-doc shape, the Markdown renderer, run-to-run comparison
(deltas, status thresholds, provenance guards), the regression gate, the toolchain
probe, and run_all's robustness (skip on None/error/timeout, drop malformed JSON).

Stdlib only (no pytest), matching gota's copy-don't-depend ethos. Run with:

    python3 -m unittest discover tests
    python3 tests/test_harness.py
"""

import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import harness
from harness import Metric, RunnerSpec


def _doc(results, *, metric="byte_throughput", machine="M1", params=None, units="MB/s"):
    """A minimal results doc for comparison tests."""
    return {
        "machine": machine,
        "os": "Test arm64",
        "date": "2026-06-21",
        "git_commit": "abc1234",
        "metric": metric,
        "units": units,
        "params": params or {"buffer_bytes": 65536},
        "results": results,
    }


class TestMetric(unittest.TestCase):
    def test_default_is_byte_throughput(self):
        doc = harness.build_results_doc([], params={}, meta={}, units="MB/s")
        self.assertEqual(doc["metric"], "byte_throughput")

    def test_enum_and_string_accepted(self):
        a = harness.build_results_doc([], params={}, meta={}, units="x", metric=Metric.OP_THROUGHPUT)
        b = harness.build_results_doc([], params={}, meta={}, units="x", metric="op_throughput")
        self.assertEqual(a["metric"], "op_throughput")
        self.assertEqual(b["metric"], "op_throughput")

    def test_unknown_metric_raises(self):
        with self.assertRaises(ValueError):
            harness.build_results_doc([], params={}, meta={}, units="x", metric="bogus")

    def test_doc_shape(self):
        doc = harness.build_results_doc(
            [{"impl": "rust", "bench": "b", "mbps": 1.0}],
            params={"buffer_bytes": 1024}, meta={"machine": "X"}, units="MB/s",
        )
        self.assertEqual(doc["machine"], "X")
        self.assertEqual(doc["params"], {"buffer_bytes": 1024})
        self.assertEqual(doc["units"], "MB/s")
        self.assertEqual(len(doc["results"]), 1)


class TestRenderMarkdown(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"impl": "rust", "bench": "fnv", "mbps": 100.0},
            {"impl": "go", "bench": "fnv", "mbps": 90.0},
        ]
        self.kw = dict(
            intro="hello intro",
            impl_order=["rust", "go", "c"], impl_labels={"rust": "Rust", "go": "Go", "c": "C"},
            bench_order=["fnv"], bench_labels={"fnv": "FNV"},
        )

    def test_table_and_intro(self):
        md = harness.render_markdown(self.rows, **self.kw)
        self.assertIn("hello intro", md)
        self.assertIn("| Rust |", md)
        self.assertIn("| Go |", md)
        self.assertIn("100.0", md)

    def test_absent_impl_omitted_and_missing_cell_dash(self):
        # C has no row -> not present; a bench with no value would render "-"
        md = harness.render_markdown(self.rows, **self.kw)
        self.assertNotIn("| C |", md)
        rows_missing = [{"impl": "rust", "bench": "other", "mbps": 5.0}]
        md2 = harness.render_markdown(
            rows_missing, intro="i",
            impl_order=["rust"], impl_labels={"rust": "Rust"},
            bench_order=["fnv"], bench_labels={"fnv": "FNV"},
        )
        self.assertIn("-", md2)


class TestComparison(unittest.TestCase):
    def test_faster_slower_same(self):
        base = _doc([{"impl": "rust", "bench": "b", "mbps": 100.0}])
        cand = _doc([{"impl": "rust", "bench": "b", "mbps": 110.0}])
        cell = harness.compare_runs(base, [cand], tolerance=0.02)["runs"][0]["cells"][0]
        self.assertEqual(cell["status"], "faster")
        self.assertAlmostEqual(cell["pct"], 10.0, places=5)

        slower = harness.compare_runs(base, [_doc([{"impl": "rust", "bench": "b", "mbps": 80.0}])])
        self.assertEqual(slower["runs"][0]["cells"][0]["status"], "slower")

        within = harness.compare_runs(base, [_doc([{"impl": "rust", "bench": "b", "mbps": 101.0}])], tolerance=0.02)
        self.assertEqual(within["runs"][0]["cells"][0]["status"], "same")

    def test_new_and_gone(self):
        base = _doc([{"impl": "rust", "bench": "b", "mbps": 100.0}])
        cand = _doc([{"impl": "go", "bench": "b", "mbps": 50.0}])
        cells = {(c["impl"], c["bench"]): c for c in harness.compare_runs(base, [cand])["runs"][0]["cells"]}
        self.assertEqual(cells[("go", "b")]["status"], "new")
        self.assertEqual(cells[("rust", "b")]["status"], "gone")

    def test_metric_mismatch_warns(self):
        base = _doc([{"impl": "rust", "bench": "b", "mbps": 100.0}], metric="byte_throughput")
        cand = _doc([{"impl": "rust", "bench": "b", "mbps": 100.0}], metric="op_throughput")
        warns = harness.compare_runs(base, [cand])["runs"][0]["warnings"]
        self.assertTrue(any("metric kind differs" in w for w in warns))

    def test_same_metric_different_label_no_metric_warning(self):
        base = _doc([{"impl": "r", "bench": "b", "mbps": 1.0}], metric="op_throughput", units="requests/sec")
        cand = _doc([{"impl": "r", "bench": "b", "mbps": 1.0}], metric="op_throughput", units="rows/sec")
        warns = harness.compare_runs(base, [cand])["runs"][0]["warnings"]
        self.assertFalse(any("metric kind differs" in w for w in warns))

    def test_machine_and_param_warnings(self):
        base = _doc([{"impl": "r", "bench": "b", "mbps": 1.0}], machine="M1", params={"buffer_bytes": 65536})
        cand = _doc([{"impl": "r", "bench": "b", "mbps": 1.0}], machine="M2", params={"buffer_bytes": 1024})
        warns = harness.compare_runs(base, [cand])["runs"][0]["warnings"]
        self.assertTrue(any("machine differs" in w for w in warns))
        self.assertTrue(any("param buffer_bytes differs" in w for w in warns))

    def test_regressions_gate(self):
        base = _doc([{"impl": "r", "bench": "b", "mbps": 100.0}])
        cand = _doc([{"impl": "r", "bench": "b", "mbps": 80.0}])  # -20%
        cmp = harness.compare_runs(base, [cand])
        self.assertEqual(len(harness.regressions(cmp, threshold_pct=5)), 1)
        self.assertEqual(harness.regressions(cmp, threshold_pct=50), [])


class TestWriteResults(unittest.TestCase):
    def test_streams(self):
        rows = [{"impl": "rust", "bench": "fnv", "mbps": 12.3, "mbps_median": 12.0, "iters": 100}]
        jbuf, mbuf = io.StringIO(), io.StringIO()
        harness.write_results(
            rows, jbuf, mbuf,
            params={"buffer_bytes": 65536}, meta={"machine": "X"},
            metric=Metric.BYTE_THROUGHPUT, units="MB/s",
            impl_order=["rust"], impl_labels={"rust": "Rust"},
            bench_order=["fnv"], bench_labels={"fnv": "FNV"}, intro="hi",
        )
        doc = json.loads(jbuf.getvalue())
        self.assertEqual(doc["metric"], "byte_throughput")
        self.assertEqual(doc["results"][0]["mbps_median"], 12.0)
        self.assertIn("| Rust |", mbuf.getvalue())


class TestToolchainProbe(unittest.TestCase):
    def test_first_line_present_and_absent(self):
        self.assertEqual(harness._first_line(["echo", "hello world"]), "hello world")
        self.assertIsNone(harness._first_line(["this-command-does-not-exist-xyz123"]))


class TestRunAll(unittest.TestCase):
    def _spec(self, name, script):
        return RunnerSpec(name, lambda: [sys.executable, "-c", script])

    def test_collects_valid_and_skips_malformed(self):
        # Print one valid JSON line and one malformed line that still starts with "{";
        # run_all should collect the first and skip the second without aborting.
        script = (
            "import json, sys;"
            "sys.stdout.write(json.dumps({'impl': 'x', 'bench': 'b', 'mbps': 1.5, 'iters': 10}) + '\\n');"
            "sys.stdout.write('{garbage\\n')"
        )
        rows = harness.run_all([self._spec("x", script)], buf=1, warmup=0.0, measure=0.0, timeout=10)
        self.assertEqual(rows, [{"impl": "x", "bench": "b", "mbps": 1.5, "iters": 10}])

    def test_skips_unavailable_and_failed(self):
        none_spec = RunnerSpec("none", lambda: None)
        fail_spec = self._spec("fail", "import sys; sys.exit(1)")
        rows = harness.run_all([none_spec, fail_spec], buf=1, warmup=0.0, measure=0.0, timeout=10)
        self.assertEqual(rows, [])

    def test_timeout_skips(self):
        slow = self._spec("slow", "import time; time.sleep(5)")
        rows = harness.run_all([slow], buf=1, warmup=0.0, measure=0.0, timeout=0.3)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
