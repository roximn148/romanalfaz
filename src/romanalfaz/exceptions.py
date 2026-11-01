# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
class RomanAlfazError(Exception):
    """Base exception for the RomanAlfaz package."""

class DictionaryNotFoundError(RomanAlfazError):
    """Raised when the specified SymSpell dictionary file cannot be found."""


class MaxVowelRunExceededError(RomanAlfazError):
    """Raised when a vowel segment longer than the supported limit is segmented directly.

    The Tafseer step-09 combinatorics grow exponentially with the length of a
    consecutive-vowel run. The pipeline driver
    (:py:func:`romanalfaz.algorithm.permuteConsecutiveVowels`) treats
    over-cap runs as over-typing and truncates them before segmentation, so
    this error only surfaces on direct calls to
    :py:func:`romanalfaz.algorithm.findVowelCombos` with a token beyond
    :py:data:`romanalfaz.algorithm.MAX_CONSECUTIVE_VOWELS`.
    """


# ******************************************************************************
