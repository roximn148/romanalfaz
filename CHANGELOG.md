# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Changed
- Bump development dependency floors: `pytest` 9.0.3 → 9.2.0, `ruff` 0.17.1 → 0.17.3, `sphinx` 8.1.3 → 9.2.0 (all three are bug-fix/minor releases with no breaking changes for this project)
- Relax the build backend pin from `uv_build>=0.11.14,<0.12.0` to `uv_build>=0.13.7,<0.14.0`
- Resolve all 61 pre-existing `ruff` findings (line-length wraps, explicit `strict=False` on `zip()` calls, exception chaining); no behavioral changes

## [0.1.0a11] - 2026-11-04

### Changed
- Bump development Python from 3.10 to 3.13 (`.python-version`, ruff `target-version`, pyrefly `python-version`); `requires-python` remains `>=3.10`
- Upgrade `symspellpy` from 6.9.0 to 6.10.1 and declare the `editdistpy` extra (`editdistpy` now resolves to 0.5.0), pinning `DistanceAlgorithm.DAMERAU_OSA_FAST` explicitly at both `SymSpell` construction sites (6.10.x switched the default to the pure-Python comparer)

## [0.1.0a10] - 2026-11-01

### Added
- `RomanAlfaz.minRomanWordLength` and `RomanAlfaz.maxRomanWordLength`: the
  minimum and maximum length (in characters) of the encoded roman words in
  the aggregate dictionary. Both are `None` while the dictionary is empty,
  and are recomputed from the aggregate vocabulary on every `recompileLookup`
  and committed atomically with the lookup index, so a failed recompile leaves
  the previously committed statistics intact.

## [0.1.0a9] - 2026-11-01

### Added
- `MAX_CONSECUTIVE_VOWELS` in `romanalfaz.algorithm` (default 8): the upper bound
  on a consecutive-vowel run that the Tafseer step-09 combinatorics will expand.
  The value is corpus-derived, not arbitrary — the longest vowel run in the
  bundled CLE 5000-word vocabulary is 5 characters (4 word-finally), so 8
  admits every legitimate romanization with margin while capping the
  worst-case expansion under 100 ms
- `MaxVowelRunExceededError` in `romanalfaz.exceptions`: defensive guard raised
  when `findVowelCombos` is called directly with a vowel segment longer than
  `MAX_CONSECUTIVE_VOWELS`; the pipeline never raises it
- Overflow runs are truncated at step 09: a consecutive-vowel run longer than
  `MAX_CONSECUTIVE_VOWELS` is treated as over-typing — only the first
  `MAX_CONSECUTIVE_VOWELS` vowels are segmented and expanded, and the
  remainder of the run is dropped from the tokens (so it contributes no
  candidates and never reaches the later pipeline steps). Candidates of an
  over-cap word are exactly those of the corresponding truncated word, and
  `RomanAlfaz.suggest` completes instead of raising on such input

### Fixed
- Long consecutive-vowel runs made `RomanAlfaz.suggest` unworkably slow
  (e.g. 3.6 s per word at 11 vowels, over a minute at 12) because the step-09
  expansion re-derived every chunk partition and re-expanded duplicate
  variation subtrees. All four step-09/step-10/step-12 helpers
  (`findVowelCombos`, `concatenateCombos`, `permuteAllOccurrences`,
  `permuteAllEndings`) were optimized in isolation with unchanged
  documented outputs: memoized suffix breakdowns (Fibonacci-partition growth
  is now output-bound), join-based separator assembly, and a queue worklist
  that skips re-deriving already-expanded subtrees while preserving
  duplicate list entries. Each step follows docs/tafseer.ipynb exactly;
  outputs verified byte-identical against the documented step examples
- Corrected stale doctest examples in `algorithm.py`:
  `permuteConsecutiveVowels(["koo"])` actually yields
  `['koAo', 'koYo', 'koo']` (docstring claimed a different order), and the
  `concatenateCombos` example now uses a list charset so its display order
  is deterministic

## [0.1.0a8] - 2026-10-31

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
- `RomanAlfaz(vocabularies=[])` no longer falls back to the bundled default
  wordlist; an explicit empty list now yields an engine with no vocabularies
  (only `None` triggers the default-dictionary fallback)
- The default wordlist construction no longer recompiles the lookup index
  twice: the redundant baseline `recompileLookup` call left over from the
  pre-observer `loadDictionary` design was removed, since `addVocabulary`
  already triggers the initial compilation
- `RomanAlfaz.removeVocabulary` now detaches every occurrence of its
  recompile callback, so a manually double-attached observer can no longer
  double-recompile per mutation; the observer contract on the
  `onChangeCallbacks` seam is documented on `Vocabulary`

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
