# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- Direct Roman2Arabic algorithm
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
