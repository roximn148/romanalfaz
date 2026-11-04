# AGENTS.md

Guidance for AI agents (and humans) working in this repository.

## Project Overview

RomanAlfaz is a dictionary-based predictive transliterator that converts
roman-script Urdu words into arabic-script equivalents. It is a Python
package (alpha stage, SemVer `0.1.0a*`) built around a two-layer pipeline:
a rule-based Roman→intermediate-Roman encoding step (`tafseerUrduRm2Rm`) and
a SymSpell fuzzy dictionary lookup against a precompiled frequency vocabulary.
The package exposes a single public entry point: the `RomanAlfaz` class.

## Repository Layout

- `src/romanalfaz/` — package source
  - `engine.py` — `RomanAlfaz`, `Vocabulary`, `Suggestion` (public API)
  - `algorithm.py` — Tafseer transliteration rules (`tafseerUrduRm2Rm`, `tafseerUrduAr2Rm`) and permutation helpers
  - `normalization.py` — registry of the normalization methods
  - `urduspell.py` — UrduSpell `normalize` pipeline (variant folding, ligatures, cross-lingual substitution)
  - `cli.py` — CLI for SymSpell vocabulary files (`python -m romanalfaz`)
  - `exceptions.py` — exception hierarchy
  - `UrduWords5k.sym` — data, not code: bundled baseline vocabulary (CLE 5000-word frequency list), SymSpell format `word$frequency`, one entry per line
- `tests/` — pytest suite, one file per source module
- `docs/` — Sphinx documentation (ReadTheDocs theme); `docs/tafseer.ipynb` is rendered into the docs via myst-nb
- `pyproject.toml` — metadata, dependencies, version; `uv.lock` — lockfile

## Environment & Commands

- Python 3.13+ (`.python-version` pins 3.13); the project uses **uv** as the package manager.
- `uv sync` — setup (runtime + dev dependencies).
- `uv run pytest` — run tests (quick: `uv run pytest -q`).
- `uv run ruff check .` — lint.
- `uv run pyrefly check` — typecheck.
- `cd docs && make html` — build docs (output in `docs/_build/`).
- No CI is configured. Definition of done: ruff, pyrefly, and pytest all clean before committing; do not introduce new tooling config without being asked.

## Code Conventions

Follow the existing in-file conventions exactly; they are deliberate:

- **License banner**: every source file starts with the MIT license comment banner. Keep it as the first lines of any new file.
- **Naming**: camelCase for functions and methods (e.g. `recompileLookup`, `getBestMatch`) — this is the project style, not PEP 8. PascalCase for classes, `SCREAMING_SNAKE_CASE` for module constants.
- **Docstrings**: Google style with `Args`, `Returns`, `Raises`, `Example` sections; user-facing functions include runnable `>>>` examples. New public functions follow the same shape.
- **Section separators**: source files use full-width `# ***...` comment lines as section dividers. Preserve the pattern in new files.
- **Assertions**: public/internal APIs use `assert isinstance(...)` / value-range asserts at entry, matching the existing style.
- **Text**: files are UTF-8 and contain literal arabic-script strings in tests, fixtures, and docstrings. Never strip or transliterate non-ASCII content.
- **Tests**: pytest classes mirroring the source module under test; fixtures live in the same class. Test names describe behavior.

## Changelog & Releases

- Commit titles: single line with a short conventional prefix (for example, `feat:`, `fix:`, `ref:`, `chore:`, `docs:`, `ver:`) and a concise summary.
- `CHANGELOG.md` follows Keep a Changelog + SemVer.
- For user-visible changes, add an entry under `## [Unreleased]` in the same commit that makes the change.
- Release flow: bump `version` in `pyproject.toml`, promote `[Unreleased]` into a dated release section in `CHANGELOG.md`, and tag `v<version>`.

## Notes

- `RomanAlfaz.suggest()` returns a 3-tuple of tiers (exact / 1-edit / 2-edit) of `Suggestion` NamedTuples; tier semantics are documented in `README.md` and `docs/`.
- `Vocabulary` instances are observed by `RomanAlfaz` (observer pattern); mutations trigger `recompileLookup`. When touching `Vocabulary` or `RomanAlfaz` internals, keep the observer contract intact.
- The docs are the public API reference; keep `docs/`, `README.md`, and this file in sync when behavior or signatures change.
