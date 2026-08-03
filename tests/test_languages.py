"""The language list is the same list in eight places. This asserts they agree.

`languages.json` at the repo root is canonical: the landing page imports it directly, so
that one can no longer drift. Everything else here (the template and example
directories, the README table, `VERSIONS.md`, `examples/run.py`, and the CI workflow's
filter/job/gate entries) is hand-maintained and CANNOT be derived — a GitHub Actions job
must be static YAML, and the README is prose. So they are checked instead.

This exists because the page silently lagged the repo twice: Swift was added in July and
C++ in August, and neither reached `web/` until someone looked at the rendered site. Any
failure here means "you added a language and missed a spot" — the message names which.

Stdlib only, like the rest of `tests/`.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "languages.json").read_text())
LANGS = MANIFEST["languages"]
IDS = [lang["id"] for lang in LANGS]
NAMES = [lang["name"] for lang in LANGS]


class TestManifestShape(unittest.TestCase):
    def test_ids_are_unique(self):
        self.assertEqual(len(IDS), len(set(IDS)), "duplicate id in languages.json")

    def test_every_entry_is_complete(self):
        required = {"id", "name", "files", "body", "harness", "seam", "build"}
        for lang in LANGS:
            missing = required - lang.keys()
            self.assertFalse(missing, f"{lang.get('id')}: missing {sorted(missing)}")

    def test_exactly_one_orchestrator_language(self):
        # The page tints this row; Python hosts harness.py + run.py.
        flagged = [lang["id"] for lang in LANGS if lang.get("orchestrator")]
        self.assertEqual(flagged, ["python"])


class TestDirectoriesMatch(unittest.TestCase):
    def test_template_dirs(self):
        on_disk = {d.name for d in (ROOT / "templates").iterdir() if d.is_dir()}
        self.assertEqual(on_disk, set(IDS), "templates/ and languages.json disagree")

    def test_example_dirs(self):
        on_disk = {
            d.name
            for d in (ROOT / "examples").iterdir()
            if d.is_dir() and not d.name.startswith("__")
        }
        self.assertEqual(on_disk, set(IDS), "examples/ and languages.json disagree")

    def test_each_template_has_a_readme_and_changelog(self):
        for lang_id in IDS:
            base = ROOT / "templates" / lang_id
            self.assertTrue((base / "README.md").is_file(), f"{lang_id}: no README.md")
            self.assertTrue((base / "CHANGELOG.md").is_file(), f"{lang_id}: no CHANGELOG.md")


class TestDocsMatch(unittest.TestCase):
    def test_readme_language_table(self):
        text = (ROOT / "README.md").read_text()
        for lang in LANGS:
            row = re.compile(
                r"^\|\s*%s\s*\|.*templates/%s/" % (re.escape(lang["name"]), lang["id"]),
                re.MULTILINE,
            )
            # assertTrue, not assertRegex/assertIn: those echo the entire file into the
            # failure, which buries the one line that matters.
            self.assertTrue(
                row.search(text), f"README.md: no language-table row for {lang['name']}"
            )

    def test_versions_table(self):
        text = (ROOT / "VERSIONS.md").read_text()
        for lang in LANGS:
            self.assertTrue(
                f"templates/{lang['id']}/CHANGELOG.md" in text,
                f"VERSIONS.md: no row for {lang['name']}",
            )


class TestExampleRunnerMatches(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "examples" / "run.py").read_text()

    def _list_literal(self, name):
        match = re.search(rf"^{name} = \[(.*?)\]", self.text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(match, f"examples/run.py: {name} not found")
        return re.findall(r'"([^"]+)"', match.group(1))

    def test_impl_order(self):
        self.assertEqual(
            set(self._list_literal("IMPL_ORDER")),
            set(IDS),
            "examples/run.py IMPL_ORDER and languages.json disagree",
        )

    def test_every_language_has_a_spec_and_toolchain_probe(self):
        for lang_id in IDS:
            self.assertTrue(
                f'RunnerSpec("{lang_id}"' in self.text,
                f"examples/run.py: no RunnerSpec for {lang_id}",
            )
            self.assertTrue(
                re.search(rf'"{re.escape(lang_id)}":\s*\[', self.text),
                f"examples/run.py: no TOOLCHAINS probe for {lang_id}",
            )


class TestWorkflowMatches(unittest.TestCase):
    """The CI workflow cannot be generated — Actions needs static YAML — so a new
    language must be added to three places in it by hand. Each has bitten before: a
    missing gate entry means the job's failures never block a merge."""

    def setUp(self):
        self.text = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        gate = re.search(r"needs: \[([^\]]+)\]", self.text)
        self.assertIsNotNone(gate, "ci.yml: ci-passed needs[] not found")
        self.gate = {n.strip() for n in gate.group(1).split(",")}

    def test_every_language_has_a_job(self):
        for lang_id in IDS:
            # MULTILINE, and assertTrue rather than assertRegex so a failure names the
            # language instead of dumping the whole workflow.
            pattern = re.compile(rf"^  {re.escape(lang_id)}:$", re.MULTILINE)
            self.assertTrue(pattern.search(self.text), f"ci.yml: no job for {lang_id}")

    def test_every_language_has_a_paths_filter(self):
        for lang_id in IDS:
            self.assertTrue(
                f"'templates/{lang_id}/**'" in self.text,
                f"ci.yml: no paths-filter entry for {lang_id}",
            )

    def test_every_language_is_in_the_gate(self):
        missing = set(IDS) - self.gate
        self.assertFalse(
            missing,
            f"ci.yml: {sorted(missing)} missing from ci-passed needs[] — "
            "their failures would not block a merge",
        )


if __name__ == "__main__":
    unittest.main()
