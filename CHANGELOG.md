# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- `Vocabulary.isModified()`: reports whether the word list has changed
  since construction or the last `save`/`load`
- `isCompleted` argument to `Vocabulary.add`: when True, the word is marked
  as completed in the same mutation, so a completed word needs only a
  single call and a single change notification

### Changed
- `Vocabulary` now tracks modification state with a private `_dirty` flag,
  committed in the new private `_notifyChanges` (renamed from the public
  `notifyChanges`), the single convergence point of all mutations, and
  cleared by `save` and `load` once the word list matches the file on disk.
  The privatization keeps a public caller from flipping the flag without
  an actual state change
- `Vocabulary.replace` now introduces the replacement word through a
  single `add(..., isCompleted=...)` mutation, firing exactly one change
  notification per replacement (previously two)
- `Vocabulary.setCompleted` no longer notifies on no-op toggles (the word
  already holding the requested status), so attached `RomanAlfaz`
  instances no longer recompile needlessly
- `Vocabulary.load` now introduces each saved word through a single
  `add(..., isCompleted=True)` mutation

### Fixed
- `RomanAlfaz.recompileLookup` now rebuilds the lookup index atomically: a
  build that fails mid-way (e.g., an unmapped character) no longer wipes the
  previously compiled engine, so `hasWord` and `suggest` stay consistent
  after the propagated assertion

## [0.1.0a7] - 2026-10-29

### Added
- Vocabulary file CLI: the `romanalfaz` command and `python -m romanalfaz`
  expose `validate`, `normalize`, `words`, `merge`, `subtract`, and `list`
  for SymSpell `word$frequency` files, built on the standard library only;
  blank lines are reported as issues rather than silently skipped
- Normalization method registry (`romanalfaz.normalization`): each method is
  a separate module registered with its label, scope, and pipeline stages;
  `--normalize` selects a method and `list` describes the available ones
  (`urdu-spell` is the only method registered for now)

### Changed
- The utils module is renamed to urduspell, establishing the per-method
  module convention: each normalization method lives in its own module, and
  the module is now identified as the urdu-spell normalization method
  implementation. No code changes.

## [0.1.0a6] - 2026-10-28

### Fixed
- URDU_VARIANT_MAP now lists the correct own presentation forms for HEH
  DOACHASHMEE (U+06BE) and FARSI YEH (U+06CC), and uses the real ALEF MAKSURA
  presentation forms (U+FEEF/U+FEF0) instead of unassigned code points
- Every presentation form is now listed exactly once, so
  URDU_VARIANT_REVERSAL_MAP has no code point owned by two base characters
- The Sphinx build no longer warns that the myst_nb intermediate
  processed.ipynb artifacts are not included in any toctree; docs/conf.py
  now excludes the myst_nb execution output directories (build,
  jupyter_execute)

### Changed
- utils.py, algorithm.py, and engine.py module docstrings now use the
  :py:mod: reference style; algorithm.py, engine.py, and docs/conf.py were
  reformatted with ruff
- Prose simplified in docs/utils.rst and src/romanalfaz/utils.py
- Vocabulary.add and the Vocabulary data dict now reject words whose
  normalized form is empty (e.g., tatweel-only or diacritic-only
  strings), which previously stored a phantom key that produced an
  empty-key entry in the lookup index
- The assertion raised when a stored word contains characters outside
  the Arabic->Roman map now names the offending word

### Added
- Purpose, Scope, and Limitations sections to the normalization
  documentation page (docs/utils.rst), plus the utils.py module docstring
  description of the disjoint pipeline stages
- PRESERVED_MARKS constant in utils.py, and the preserved-marks contract
  between normalizeUrduChars and removeMarks documented in their
  docstrings
- Test coverage for the URDU_VARIANT_MAP, URDU_VARIANT_REVERSAL_MAP, and
  LIGATURE_MAP data structures and for the normalization of the repaired
  code points

## [0.1.0a5] - 2026-10-19

### Added
- RomanAlfaz.hasWord() method to check the presence of arabic-script
  words in the dictionary (normalized exact match, no fuzzy matching)

## [0.1.0a4] - 2026-10-18

## Planned
- Direct Roman2Arabic algorithm

### Added
- Suggestion fields now carry defaults, so Suggestion() constructs the blank suggestion
- Suggestion.isUndefined() method to detect undefined suggestions
  (missing arabic word or zero frequency)

### Changed
- RomanAlfaz default dictionary loading now only wraps OSError and
  ValueError into DictionaryNotFoundError

## [0.1.0a3] - 2026-05-26
### Added
* RomanAlfaz suggestion improvements
  * getExactMatches and getBestMatch convenience methods

## [0.1.0a2] - 2026-05-26
### Added
* MultiVocabulary Management to RomanAlfaz
  * RomanAlfaz observes multiple Vocabulary instances 
    while internally maintains a singular source of wordlist
  * Added adding/removing Vocabulary instances
    and responding to dynamic change in each instance itself.

## [0.1.0a1] - 2026-05-25
### Added
- RomanAlfaz roman Urdu transliterator
  - Tafseer Roman2Roman and Arabic2Roman algorithms
- Initial 5000 Word-Frequency Vocabulary
- Initial documentation and ReadTheDocs config

## [Initial Commit] - 2026-05-20
### Added
- Initial project scaffolding and package setup.
- Standard MIT License header comments to all source files.
- Configuration files for Sphinx RTD docs.

Copyright (C) 2026 RoXimn <roximn148@gmail.com>. All rights reserved.
Licensed under the [MIT License](LICENSE.txt).
