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


class TestProtocolVersion(unittest.TestCase):
    """The protocol version is hardcoded in twenty harness copies (ten templates, ten
    example runners), which is a hand-maintained constant of exactly the kind that goes
    stale. It is worth it because a CONSUMER's copy reporting an old version is the
    signal the field exists for -- but inside this repo it must never drift, so it is
    checked here against VERSIONS.md and PROTOCOL.md."""

    @staticmethod
    def _declared_version():
        text = (ROOT / "VERSIONS.md").read_text()
        match = re.search(r"^\| Protocol \| ([0-9]+\.[0-9]+\.[0-9]+) \|", text, re.MULTILINE)
        assert match, "VERSIONS.md: no Protocol row"
        return match.group(1)

    def test_spec_states_the_same_version(self):
        version = self._declared_version()
        spec = (ROOT / "PROTOCOL.md").read_text()
        self.assertIn(
            f"**Protocol version {version}.**",
            spec,
            f"PROTOCOL.md does not announce {version} (VERSIONS.md says it should)",
        )

    def test_harness_implements_the_same_version(self):
        version = self._declared_version()
        harness = (ROOT / "harness.py").read_text()
        self.assertIn(
            f'PROTOCOL_VERSION = "{version}"',
            harness,
            f"harness.py PROTOCOL_VERSION is not {version}",
        )

    def test_every_harness_copy_emits_the_current_version(self):
        """Found by CONTENT, not filename: the harness is `gota.c`, `Gota.java`,
        `gota/gota.go`..., and the tree also holds `gota.h` (no emit) plus gitignored
        build artifacts. The emitting file is the one carrying the JSON line."""
        version = self._declared_version()
        # Compiled runners, .pyc caches, and .o/.hi artifacts sit beside the sources
        # (gitignored, but this walks the filesystem). Rather than maintain a blocklist,
        # skip anything that is not UTF-8 text: source is, build output is not.
        for base in ("templates", "examples"):
            for lang_id in IDS:
                emitters = []
                for path in (ROOT / base / lang_id).rglob("*"):
                    if not path.is_file() or path.suffix == ".md":
                        continue
                    try:
                        text = path.read_bytes().decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    if "mbps_median" in text and "iters" in text:
                        emitters.append((path, text))
                self.assertTrue(
                    emitters, f"{base}/{lang_id}: no file emits the protocol JSON line"
                )
                for path, text in emitters:
                    self.assertIn(
                        version,
                        text,
                        f"{path.relative_to(ROOT)}: does not emit protocol {version}",
                    )


class TestVendoredCopies(unittest.TestCase):
    """`examples/` is a self-contained consumer, so it carries its own copy of
    `harness.py` -- the same copy-don't-depend model gota advocates. That copy silently
    went stale the moment the root gained protocol-version handling, so pin it."""

    def test_example_harness_matches_the_root(self):
        root = (ROOT / "harness.py").read_bytes()
        vendored = (ROOT / "examples" / "harness.py").read_bytes()
        self.assertEqual(
            root,
            vendored,
            "examples/harness.py has drifted from harness.py -- re-copy it "
            "(`cp harness.py examples/harness.py`)",
        )


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
