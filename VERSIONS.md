# Versions

Gota is versioned **per component**, not as one monolith, because a change to one
language template (or to the example) does not change the others. Each component carries
its own [semantic version](https://semver.org/) and its own changelog; this table is the
index. A change is recorded in the changelog of whatever it touches — see the routing
rule in [CLAUDE.md](CLAUDE.md) and the summary in [`README.md`](README.md#changelog).

The **Core** row covers the cross-cutting pieces — the protocol, the orchestrator
(`harness.py`), and the report (`report.py` + `report_template.html`) plus the
`examples/` consumer, the `tests/` suite, and shared docs. A protocol-level change bumps
Core and is then referenced from each language template's changelog as it syncs.

| Component | Version | Changelog | Covers |
| --- | --- | --- | --- |
| Core | 0.1.0 | [CHANGELOG.md](CHANGELOG.md) | `PROTOCOL.md`, `harness.py`, `report.py`, `report_template.html`, `examples/`, `tests/`, shared docs |
| Python template | 0.1.0 | [templates/python/CHANGELOG.md](templates/python/CHANGELOG.md) | `templates/python/` |
| Rust template | 0.1.0 | [templates/rust/CHANGELOG.md](templates/rust/CHANGELOG.md) | `templates/rust/` |
| C template | 0.1.0 | [templates/c/CHANGELOG.md](templates/c/CHANGELOG.md) | `templates/c/` |
| Go template | 0.1.0 | [templates/go/CHANGELOG.md](templates/go/CHANGELOG.md) | `templates/go/` |
| Java template | 0.1.0 | [templates/java/CHANGELOG.md](templates/java/CHANGELOG.md) | `templates/java/` |
| Swift template | 0.1.0 | [templates/swift/CHANGELOG.md](templates/swift/CHANGELOG.md) | `templates/swift/` |
| Zig template | 0.1.0 | [templates/zig/CHANGELOG.md](templates/zig/CHANGELOG.md) | `templates/zig/` |
| TypeScript template | 0.1.0 | [templates/ts/CHANGELOG.md](templates/ts/CHANGELOG.md) | `templates/ts/` |
| Haskell template | 0.1.0 | [templates/haskell/CHANGELOG.md](templates/haskell/CHANGELOG.md) | `templates/haskell/` |
| Web | 0.1.0 | [web/CHANGELOG.md](web/CHANGELOG.md) | `web/` (the landing page) |

All components are at `0.1.0` and unreleased (no dated release has been cut yet); their
current work sits in each changelog's `Unreleased` section. When the first release is
cut, the `Unreleased` entries get a dated `0.1.0` heading and this table tracks each
component independently from there.

## Versioning rules

- **MAJOR** — a breaking change. For Core, a protocol change that makes runners no
  longer comparable (new CLI args, a changed timing loop or JSON shape). For a template,
  a change to the copy-as-is `gota.*` contract that a consumer must adapt to.
- **MINOR** — backward-compatible additions (a new harness/report capability, a new
  language feature in a template).
- **PATCH** — fixes and doc-only changes that do not alter behavior or contract.
