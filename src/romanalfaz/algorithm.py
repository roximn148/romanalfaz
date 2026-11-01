# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
The :py:mod:`romanalfaz.algorithm` module contains the Urdu language roman-to-arabic script transliteration
algorithm and its helper functions.
"""

# ******************************************************************************
import itertools
import re
from collections import deque

from .exceptions import MaxVowelRunExceededError
from .urduspell import normalize, normalizeWhiteSpace

# ******************************************************************************
# URDU ARABIC2ROMAN ENCODING MAP START
URDU_ARABIC2ROMAN_ENCODING_MAP: dict[str, str] = {
    "\u0627": "A",  # ARABIC LETTER ALEF
    "\u0639": "A",  # ARABIC LETTER AIN
    "\u0622": "AA",  # ARABIC LETTER ALEF WITH MADDA ABOVE
    "\u0623": "A",  # ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\u0628": "B",  # ARABIC LETTER BEH
    "\u067e": "P",  # ARABIC LETTER PEH
    "\u062a": "T",  # ARABIC LETTER TEH
    "\u0637": "T",  # ARABIC LETTER TAH
    "\u0679": "T",  # ARABIC LETTER TTEH
    "\u06c3": "T",  # ARABIC LETTER TEH MARBUTA GOAL
    "\u062c": "J",  # ARABIC LETTER JEEM
    "\u062b": "S",  # ARABIC LETTER THEH
    "\u0633": "S",  # ARABIC LETTER SEEN
    "\u0635": "S",  # ARABIC LETTER SAD
    "\u0686": "CH",  # ARABIC LETTER TCHEH
    "\u062d": "H",  # ARABIC LETTER HAH
    "\u06c1": "H",  # ARABIC LETTER HEH GOAL
    "\u06c2": "H",  # ARABIC LETTER HEH GOAL WITH HAMZA ABOVE
    "\u06be": "H",  # ARABIC LETTER HEH DOACHASHMEE
    "\u0647": "H",  # ARABIC LETTER HEH
    "\u062e": "KH",  # ARABIC LETTER KHAH
    "\u062f": "D",  # ARABIC LETTER DAL
    "\u0688": "D",  # ARABIC LETTER DDAL
    "\u0630": "Z",  # ARABIC LETTER THAL
    "\u0632": "Z",  # ARABIC LETTER ZAIN
    "\u0636": "Z",  # ARABIC LETTER DAD
    "\u0638": "Z",  # ARABIC LETTER ZAH
    "\u0698": "Z",  # ARABIC LETTER JEH
    "\u0631": "R",  # ARABIC LETTER REH
    "\u0691": "R",  # ARABIC LETTER RREH
    "\u0634": "SH",  # ARABIC LETTER SHEEN
    "\u063a": "GH",  # ARABIC LETTER GHAIN
    "\u0641": "F",  # ARABIC LETTER FEH
    "\u06a9": "K",  # ARABIC LETTER KEHEH
    "\u0642": "Q",  # ARABIC LETTER QAF
    "\u06af": "G",  # ARABIC LETTER GAF
    "\u0644": "L",  # ARABIC LETTER LAM
    "\u0645": "M",  # ARABIC LETTER MEEM
    "\u0646": "N",  # ARABIC LETTER NOON
    "\u06ba": "N",  # ARABIC LETTER NOON GHUNNA
    "\u0648": "O",  # ARABIC LETTER WAW
    "\u0624": "O",  # ARABIC LETTER WAW WITH HAMZA ABOVE
    "\u06cc": "Y",  # ARABIC LETTER FARSI YEH
    "\u0621": "Y",  # ARABIC LETTER HAMZA
    "\u0626": "Y",  # ARABIC LETTER YEH WITH HAMZA ABOVE
    "\u064a": "Y",  # ARABIC LETTER YEH
    "\u06d2": "E",  # ARABIC LETTER YEH BARREE
}
# URDU ARABIC2ROMAN ENCODING MAP END
"""This is one-to-one transliteration convertion map for converting Urdu text
from arabic-script to roman-script for word list lookup.

.. todo:: Clean up the input characters to map only the normalized characters.
"""

# ******************************************************************************
MAX_CONSECUTIVE_VOWELS: int = 8
"""Upper bound on the length of a consecutive-vowel run that step 09 will expand.

Cost justification (measured on the optimized pipeline, probe word
``b + 'a' * n + 'd'``). The step-09 expansion of a vowel run grows
exponentially with the run length — the number of chunk partitions is
Fibonacci(n+1), and each partition of ``k`` chunks yields ``2 ** (k - 1)``
anchor interleavings — and every later pipeline step multiplies that base
expansion, so each extra vowel in a run multiplies the total cost roughly
3x::

    run n   candidates   time (ms)
    ------  -----------  ---------
         1            2        0.2
         2            7        0.1
         3           23        0.2
         4           73        0.6
         5          227        1.9
         6          697        6.3
         7        2 123       20.6
         8        6 433       67.8
         9       19 427      214.0
        10       58 537      719.5
        12      705 516    ~10 000

Why 8: the value is corpus-derived, not arbitrary. Across the bundled CLE
5000-word frequency vocabulary the longest consecutive-vowel run in any
genuine romanization is 5 characters (word-finally at most 4 — e.g. the
کارروائی family's ائیو/ائیا cluster). Vowel runs past that length cannot map
to a distinct Urdu vowel sound: they are redundant length-marking or typos.
Setting the cap at 8 therefore admits every legitimate romanization with
margin for casual over-typing while keeping the worst-case expansion well
under 100 ms; runs of 9–12 would spend 0.2–10 s per word for candidates that
are, by the corpus data's own definition, guaranteed-wrong.

Why the overflow is dropped (truncation policy). Two policies were evaluated
for a run longer than this cap:

- Keeping the overflow characters in the token (skipping only step 09's
  segmentation of them) does NOT bound the cost: steps 10–12 still fork on
  every remaining lowercase vowel — step 12 expands each into ``""`` and its
  uppercase substitute — so a tail of ``t`` vowels re-opens an exponential
  channel right past the cap. The tail would also yield candidates that
  contain guaranteed-wrong vowel characters, polluting dictionary lookups and
  occupying fuzzy suggestion slots.
- Dropping the overflow (the adopted policy) bounds each run's contribution
  to the capped expansion (~6 433 candidates, < 100 ms worst case), because
  steps 10–12 only ever see the capped prefix. It is mechanically safe: the
  removed fragment is strictly a contiguous ``[aeiou]`` sub-run, so no
  consonant digraph anchor can be created or broken (``h``/``y`` were already
  consumed in steps 04–08 before step 09 runs).

For every legitimate input (runs of at most 5) truncation never triggers and
outputs are identical to the untruncated algorithm; the deviation is an
acceptable approximation for over-typed noise.

Error policy: :py:class:`romanalfaz.exceptions.MaxVowelRunExceededError`
remains a defensive precondition on direct :py:func:`findVowelCombos` misuse;
the pipeline itself truncates and never raises. Tunable: each additional
vowel multiplies the expansion cost roughly 3x (see the cost table above).
"""


# ******************************************************************************
def tafseerUrduAr2Rm(word: str, keep: bool = True) -> tuple[str, int]:
    """
    Converts a string containing Urdu text in arabic-script to intermediate roman-script.

    The input word is normalized to base characters using :py:func:`romanalfaz.urduspell.normalize`
    before processing it for romanization.

    This function also handles specific orthographic rule of the Urdu language, treating
    the initial 'Waw' (و) as a consonant sound ('W') rather than a vowel marker, and maps
    it specifically separate from the predefined encoding map.

    Args:
        word (str): The input string containing Urdu text in arabic-script.
        keep (bool): To keep the undefined characters in the output text, or skip them.
            Default is ``True``.

    Returns:
        tuple[str, int]: A tuple containing two elements:

        - str: The fully romanized string with tokens separated by spaces.
        - int: The count of undefined characters encountered during conversion.
          Characters not found in the encoding map can be optionally kept as-is
          in the output, however, this counter reflects how many were in the input
          after normalization, irrespective of the output.

    Raises:
        AssertionError: If the input `word` is not a ``str`` instance.

    Example:
        >>> tafseerUrduAr2Rm("السلام")
        ('ALSLAM', 0)
        >>> tafseerUrduAr2Rm("والسلام")
        ('WALSLAM', 0)
        >>> tafseerUrduAr2Rm('الگ')
        ('ALG', 0)
        >>> tafseerUrduAr2Rm('الو')
        ('ALO', 0)
        >>> tafseerUrduAr2Rm('بخار')
        ('BKHAR', 0)
        >>> tafseerUrduAr2Rm('بهائ')
        ('BHAY', 0)
        >>> tafseerUrduAr2Rm('ہے')
        ('HE', 0)
        >>> tafseerUrduAr2Rm('شہرت')
        ('SHHRT', 0)
    """
    assert isinstance(word, str), f"Expected string type, got {type(word)}"

    # Normalize the input and split the input into individual tokens
    tokens = normalize(word).split(" ")

    # If no tokens exist after normalization, return empty strings/counts
    if not tokens:
        return "", 0

    romanizedTokens: list[str] = []
    undefCount: int = 0

    for token in tokens:
        romanizedToken: str = ""

        # Handle the specific Urdu rule where initial 'Waw' (و) is treated as a consonant 'W'.
        # We strip it from the token and prepend 'W' to the result.
        if token.startswith("\u0648"):
            token = token[1:]
            romanizedToken = "W"

        for char in token:
            # Check if the character exists in our predefined mapping
            if char in URDU_ARABIC2ROMAN_ENCODING_MAP:
                romanizedToken += URDU_ARABIC2ROMAN_ENCODING_MAP[char]
            else:
                if (
                    keep
                ):  # If a character is not in the map, keep it as-is (pass-through)
                    romanizedToken += char
                undefCount += 1

        romanizedTokens.append(romanizedToken)

    return " ".join(romanizedTokens), undefCount


# ******************************************************************************
def tafseerUrduRm2Rm(word: str) -> set[str]:
    """
    Transforms a roman-script Urdu input into an intermediate normalized representation.

    This function addresses common transliteration inconsistencies caused by:

    #. The absence of vowels in standard arabic-script writing (leading to ambiguous consonant clusters).
    #. Multiple distinct Arabic consonants that map to the same Roman letter (e.g., 'kaf' vs 'qaf').

    It executes a 12-step sequential algorithm designed to resolve these ambiguities,
    producing one or more candidate words in an intermediate Roman encoding format.
    These candidates can then be matched against a pre-defined dictionary of known words
    to predict the intended Arabic word.

    Args:
        word (str): The input string containing Roman-script Urdu text.

    Returns:
        set[str]: A set of candidate words in the intermediate Roman encoding.
        For empty string, returns an empty set.

    Raises:
        AssertionError: If the input `word` is not a ``str`` instance.

    Notes:
        Consecutive-vowel runs longer than :py:data:`MAX_CONSECUTIVE_VOWELS`
        are truncated to their first MAX_CONSECUTIVE_VOWELS vowels during
        step 09; the overflow is treated as over-typing and does not generate
        candidates.

    Example:
        >>> tafseerUrduRm2Rm('khalq') # Ambiguous, can be خالق or خلق
        {'KHALQ', 'KHLQ'}  # Generated possible candidates
        >>> tafseerUrduRm2Rm('alag')  # الگ
        {'AALAG', 'AALG', 'ALAG', 'ALG'}
        >>> tafseerUrduRm2Rm('ullo')  # الو
        {'ALO', 'AOLO'}
        >>> tafseerUrduRm2Rm('bukhar')  # بخار
        {'BKHAR', 'BKHR', 'BOKHAR', 'BOKHR'}
        >>> tafseerUrduRm2Rm('bhai')  # بهائ
        {'BHAAY', 'BHAY', 'BHAYY', 'BHE', 'BHYY'}
        >>> tafseerUrduRm2Rm('hai')   # ہے
        {'HAAY', 'HAY', 'HAYY', 'HE', 'HYY'}
        >>> tafseerUrduRm2Rm('bhayi')  # بهائ
        {'BHAYY', 'BHYY'}
        >>> tafseerUrduRm2Rm('shohrat')  # شہرت
        {'SHHRAT', 'SHHRT', 'SHOHRAT', 'SHOHRT'}
    """
    assert isinstance(word, str), f"Expected string type, got {type(word)}"

    if not word:
        return set()

    # Step 00 ------------------------------------------------------------------
    word = normalizeWhiteSpace(word).lower()

    # Step 01 ------------------------------------------------------------------
    # print(f' 1. "{word}" -> ', end='')
    token = "".join(char if char in "aeiouyh" else char.upper() for char in word)
    # print(f'"{token}"')

    # Step 02 ------------------------------------------------------------------
    # print(f' 2. "{token}" -> ', end='')
    token = re.sub(r"([A-Z])\1+", r"\1", token)
    # print(f'"{token}"')

    # Step 03 ------------------------------------------------------------------
    # print(f' 3. "{token}" -> ', end='')
    token = ("A" if token[0] in "aeiou" else "") + token
    # print(f'"{token}"')

    # Step 04 ------------------------------------------------------------------
    hVowelCombos = {
        "ehe": ["eHe", "H"],
        "eh": ["eH", "H"],
        "oh": ["oH", "H"],
        "h": ["H"],
    }
    # print(f' 4. "{token}" -> ', end='')
    tokenList = permuteAllOccurrences([token], hVowelCombos)
    # print(f'{tokenList}')

    # Step 05 ------------------------------------------------------------------
    yehEndings = {
        "ey": "Y",
        "ay": "E",
    }
    # print(f' 5. {tokenList} -> ', end='')
    tokenList = [replaceEnding(token, yehEndings, 2) for token in tokenList]
    # print(f'{tokenList}')

    # Step 06 ------------------------------------------------------------------
    yVowelCombos = {
        "ey": ["Y", "eY"],
        "ay": ["Y", "aY"],
    }
    # print(f' 6. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, yVowelCombos)
    # print(f'{tokenList}')

    # Step 07 ------------------------------------------------------------------
    # print(f' 7. {tokenList} -> ', end='')
    tokenList = [w.replace("y", "Y") for w in tokenList]
    # print(f'{tokenList}')

    # Step 08 ------------------------------------------------------------------
    iEndings = {
        "ai": ["E", "aYi", "aAi"],
        "ei": ["E", "eYi", "eAi"],
    }
    # print(f' 8. {tokenList} -> ', end='')
    tokenList = permuteAllEndings(tokenList, iEndings)
    # print(f'{tokenList}')

    # Step 09 ------------------------------------------------------------------
    # print(f' 9. {tokenList} -> ', end='')
    tokenList = permuteConsecutiveVowels(tokenList)
    # print(f'{tokenList}')

    # Step 10 ------------------------------------------------------------------
    DoubleVowels = {
        "aa": ["A"],
        "ai": ["Y"],
        "ei": ["Y"],
        "ee": ["Y"],
        "ie": ["Y"],
        "oo": ["O"],
        "au": ["O"],
        "ou": ["O"],
    }
    # print(f'10. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, DoubleVowels)
    # print(f'{tokenList}')

    # Step 11 ------------------------------------------------------------------
    VowelEndings = {"e": ["E"], "a": ["A", "H"], "i": ["Y"], "u": ["O"]}
    # print(f'11. {tokenList} -> ', end='')
    tokenList = permuteAllEndings(tokenList, VowelEndings)
    # print(f'{tokenList}')

    # Step 12 ------------------------------------------------------------------
    VowelReplacements = {
        "a": ["", "A"],
        "i": ["", "Y"],
        "u": ["", "O"],
        "e": ["E"],
        "o": ["O"],
    }
    # print(f'12. {tokenList} -> ', end='')
    tokenList = permuteAllOccurrences(tokenList, VowelReplacements)
    # print(f'{tokenList}')

    # remove duplicates
    return {w for w in tokenList}


# ******************************************************************************
def permuteFirstOccurrence(token: str, mapping: dict[str, list[str]]) -> list[str]:
    """Generates variations of a token by replacing its leftmost matching substring.

    This function scans the input token from left to right to find the earliest
    occurrence of any key defined in the mapping dictionary. Once found, it
    creates a list of new strings where only that first occurrence is replaced
    by each of its corresponding mapped values.

    Args:
        token: The input roman Urdu token to process.
        mapping: A dictionary where keys are target character patterns and
            values are lists of allowed replacement variations.

    Returns:
        A list of modified strings containing the variations. Returns an empty
        list if none of the mapping keys are found within the token.

    Example:
        >>> rule_map = {"aa": ["a", "e"], "kh": ["x"]}
        >>> permuteFirstOccurrence("baakh", rule_map)
        ['bakh', 'bekh']
    """
    # Initialize with a value larger than any possible index position
    minIndex: int = len(token)
    leftMostKey: str = ""

    # Scan the token to find the earliest (leftmost) mapping key
    for substr in mapping:
        index = token.find(substr)

        # If the substring is found and occurs earlier than the current minimum
        if index != -1 and index < minIndex:
            minIndex = index
            leftMostKey = substr

    # If a valid pattern was discovered, generate the single-replacement permutations
    if leftMostKey:
        substitutions = mapping[leftMostKey]

        # The '1' argument ensures only the first occurrence is swapped
        return [
            token.replace(leftMostKey, replacement, 1) for replacement in substitutions
        ]

    # Return an empty list if no operational keys were matched
    return []


# ******************************************************************************
def permuteAllOccurrences(
    tokenList: list[str], mapping: dict[str, list[str]]
) -> list[str]:
    """Exhaustively generates all phonetic permutations for a list of tokens.

    This function processes each string in the input list, running an iterative
    queue-based cascade. It repeatedly targets and replaces the leftmost matching
    character patterns using `permuteFirstOccurrence` until a string contains
    absolutely no keys from the mapping dictionary.

    Args:
        tokenList: A list of roman Urdu tokens to be fully permuted.
        mapping: A dictionary where keys are target character patterns and
            values are lists of allowed replacement variations.

    Returns:
        A list containing all fully transformed variations of the input tokens.
        If a token has no matches, it is returned as-is.

    Example:
        >>> rule_map = {"oo": ["u"], "ee": ["i"]}
        >>> permuteAllOccurrences(["khooshee"], rule_map)
        ['khushi']
    """
    outList: list[str] = []

    # Words whose expansion tree has already been queued anywhere in this call.
    # Re-deriving an identical subtree yields identical outputs, so its first
    # derivation is reused; leaf variations are still re-emitted so duplicate
    # list entries are preserved exactly as produced by the full enumeration.
    processedVariations: set[str] = set()

    for token in tokenList:
        # Initialize the processing queue with the current base token
        pendingWords: deque[str] = deque([token])

        # Process the queue until all strings are fully resolved
        while pendingWords:
            # Pop the first element from the queue (FIFO tracking)
            word = pendingWords.popleft()

            # Generate the next layer of single-replacement variations
            replacedVariations = permuteFirstOccurrence(word, mapping)

            if replacedVariations:
                # If changes occurred, queue them up for deeper scanning
                for variation in replacedVariations:
                    if variation in processedVariations:
                        # Skip re-deriving an already expanded subtree, but keep
                        # leaf variations so duplicate entries stay reproducible
                        if not permuteFirstOccurrence(variation, mapping):
                            pendingWords.append(variation)
                        continue
                    processedVariations.add(variation)
                    pendingWords.append(variation)
            else:
                # If no changes occurred, the token is fully processed
                outList.append(word)

    return outList


# ******************************************************************************
def permuteEnding(token: str, mapping: dict[str, list[str]]) -> list[str]:
    """Replaces the trailing suffix of a string with mapped variations.

    This function evaluates the end of the input string against keys in the
    mapping dictionary. When a trailing match is detected, it strips that
    specific suffix and returns a list of new strings combining the unchanged
    prefix with every allowed substitution tail.

    Args:
        token: The input Roman Urdu string to inspect for trailing patterns.
        mapping: A dictionary where keys are target trailing character
            sequences (suffixes) and values are lists of substitution variants.

    Returns:
        A list of strings containing the modified suffix variations. Returns
        an empty list if the text does not end with any of the mapping keys.

    Example:
        >>> suffix_rules = {"ein": ["ain", "en"], "iy": ["i"]}
        >>> permuteEnding("jaalein", suffix_rules)
        ['jaalain', 'jaalen']
    """
    for key, substitutions in mapping.items():
        if token.endswith(key):
            # Isolate the front part of the string by slicing off the suffix length
            prefix = token[: -len(key)]

            # Reconstruct the token variations by attaching the new suffix options
            return [prefix + sub for sub in substitutions]

    # Return an empty list if no suffix keys matched the trailing string boundary
    return []


# ******************************************************************************
def permuteAllEndings(tokenList: list[str], mapping: dict[str, list[str]]) -> list[str]:
    """Exhaustively generates all suffix variations for a list of tokens.

    This function steps through each string in the input token list, executing
    a queue-driven transformation loop. It continuously strips and replaces
    trailing character suffixes using `permuteEnding` until the strings
    contain absolutely no matching suffix keys left in the mapping dataset.

    Args:
        tokenList: A list of raw Roman Urdu tokens to evaluate for suffix changes.
        mapping: A dictionary where keys are target suffix patterns and
            values are lists of allowed trailing replacement variations.

    Returns:
        A list of all fully processed suffix variations across the input tokens.
        Tokens with no suffix matches are preserved in the list exactly as-is.

    Example:
        >>> suffixRules = {"ein": ["ain"], "ain": ["en"]}
        >>> permuteAllEndings(["karein"], suffixRules)
        ['karen']
    """
    outList: list[str] = []

    # Suffix variations whose expansion tree has already been queued anywhere in
    # this call. Re-deriving an identical subtree yields identical outputs, so
    # its first derivation is reused; leaf variations are still re-emitted so
    # duplicate list entries are preserved exactly as produced by the full
    # exhaustive enumeration.
    processedVariations: set[str] = set()

    for activeToken in tokenList:
        # Instantiate the processing queue with the current base string token
        pendingWords: deque[str] = deque([activeToken])

        # Drain the local variation queue completely
        while pendingWords:
            # Shift the front item out of the tracking array
            currentWord = pendingWords.popleft()

            # Identify and execute the next applicable single suffix shift
            replacedVariations = permuteEnding(currentWord, mapping)

            if replacedVariations:
                # Re-queue new variations to test for sequential cascading rules
                for variation in replacedVariations:
                    if variation in processedVariations:
                        # Skip re-deriving an already expanded subtree, but keep
                        # leaf variations so duplicate entries stay reproducible
                        if not permuteEnding(variation, mapping):
                            pendingWords.append(variation)
                        continue
                    processedVariations.add(variation)
                    pendingWords.append(variation)
            else:
                # No more rules apply to this token variant; save as finished product
                outList.append(currentWord)

    return outList


# ******************************************************************************
def replaceEnding(token: str, mapping: dict[str, str], n: int) -> str:
    """Replaces a suffix of length n with its mapped string substitution.

    This function extracts the final n characters of a token and checks if
    that suffix exists within the provided mapping dictionary. If a match
    is found, the old suffix is stripped and swapped for the replacement
    value. If no match is found, or if the string is shorter than n, the
    original token is returned unmodified.

    Args:
        token: The input Roman Urdu string to evaluate and modify.
        mapping: A dictionary where keys are target suffixes of length n and
            values are their single string replacements.
        n: The exact character length of the suffix to isolate and check.

    Returns:
        The modified string with the new ending applied, or the original
        unaltered token if no mapping constraints were met.

    Example:
        >>> suffixRules = {"ah": "a", "iy": "i"}
        >>> replaceEnding("vaalah", suffixRules, 2)
        'vaala'
    """
    # Verify token is long enough and its slice matches a rule key
    if len(token) >= n and token[-n:] in mapping:
        # Slice off the final n characters and append the replacement value
        return token[:-n] + mapping[token[-n:]]
    else:
        # Fall back to returning the original text string unmodified
        return token


# ******************************************************************************
def findVowelCombos(token: str) -> list[list[str]]:
    """Segments a string of vowels into all possible valid sub-pattern breakdowns.

    This function uses a recursive backtracking depth-first search to find every
    combination of 1-character and 2-character vowel tokens that can perfectly
    reconstruct the input string based on a predefined set of roman Urdu
    vowel patterns. Suffix-level memoization keeps the overall work linear in
    the size of the output instead of re-deriving each suffix breakdown on
    every path through the search tree.

    Args:
        token: A string consisting of vowel characters to partition.

    Returns:
        A list of lists, where each sub-list represents a valid sequence
        of parsed vowel patterns that exactly make up the input word.

    Raises:
        MaxVowelRunExceededError: If the input token is longer than
            :py:data:`MAX_CONSECUTIVE_VOWELS` characters. This is a defensive
            precondition for direct callers: the pipeline driver
            (`permuteConsecutiveVowels`) truncates overflow runs to the cap
            before handing them over, so this error never fires mid-pipeline.

    Example:
        >>> findVowelCombos("aa")
        [['a', 'a'], ['aa']]
    """
    vowelsSet = frozenset(
        [
            "a",
            "aa",
            "ai",
            "au",
            "ay",
            "e",
            "ee",
            "ei",
            "ey",
            "i",
            "ie",
            "o",
            "oo",
            "ou",
            "u",
        ]
    )

    if len(token) > MAX_CONSECUTIVE_VOWELS:
        raise MaxVowelRunExceededError(
            f"Consecutive-vowel run of length {len(token)} exceeds the supported"
            f" limit of {MAX_CONSECUTIVE_VOWELS} (in token {token!r})"
        )

    # Memo of suffix -> list of the exact breakdown tuples for that suffix.
    # Entries preserve depth-first enumeration order: single-character chunks
    # before two-character chunks, mirroring the sequential backtracking order.
    memo: dict[str, list[tuple[str, ...]]] = {}

    def findCombinations(remainingText: str) -> list[tuple[str, ...]]:
        """Helper that recursively branches and backtracks through text."""
        cachedBreakdowns = memo.get(remainingText)
        if cachedBreakdowns is not None:
            return cachedBreakdowns

        # Base case: if no characters are left, we found a valid breakdown
        if not remainingText:
            breakdowns = [()]
        else:
            breakdowns = []

            # Lookahead Check 1: Extract and evaluate a 1-character substring
            chunkOne = remainingText[:1]
            if chunkOne in vowelsSet:
                breakdowns.extend((chunkOne, *path) for path in findCombinations(remainingText[1:]))

            # Lookahead Check 2: Extract and evaluate a 2-character substring
            if len(remainingText) >= 2:
                chunkTwo = remainingText[:2]
                if chunkTwo in vowelsSet:
                    breakdowns.extend((chunkTwo, *path) for path in findCombinations(remainingText[2:]))

        memo[remainingText] = breakdowns
        return breakdowns

    return [list(breakdown) for breakdown in findCombinations(token)]


# ******************************************************************************
def concatenateCombos(
    subStrings: list[str], charset: set[str] | list[str]
) -> list[str]:
    """Concatenates strings using all combinations of characters from a charset.

    This function pieces together an array of fragmented sub-strings by interleaving
    every possible permutation sequence of characters from the given charset into
    the interstitial gaps between elements.

    Args:
        subStrings: A list of string segments to stitch together.
        charset: A collection (set or list) of single-character strings to
            act as variation separators between the text segments.

    Returns:
        A list of all possible interleaved concatenated string variants.

    Example:
        >>> concatenateCombos(["b", "n", "n"], ["a", "o"])
        ['banan', 'banon', 'bonan', 'bonon']
    """
    if not subStrings:
        return []
    if len(subStrings) == 1:
        return subStrings

    separatorCount = len(subStrings) - 1

    # Generate all Cartesian product combinations of separators with replacement
    return [
        subStrings[0] + "".join(
            separator + segment for separator, segment in zip(currentCombo, subStrings[1:])
        )
        for currentCombo in itertools.product(charset, repeat=separatorCount)
    ]


# ******************************************************************************
def permuteConsecutiveVowels(inList: list[str]) -> list[str]:
    """Processes tokens containing two or more consecutive vowels into variations.

    This function scans a list of string tokens to find consecutive vowel sequences.
    It isolates each vowel cluster, segments it into valid sub-patterns, and
    interleaves structural placeholders ("A" and "Y") between multi-token vowel
    combinations before reconstructing the final permuted words.

    Args:
        inList: A list of Roman Urdu string tokens to inspect and permute.

    Returns:
        A list of all newly generated word variations. If a word contains no
        consecutive vowels, it is returned in the output list unmodified.
        Consecutive-vowel runs longer than :py:data:`MAX_CONSECUTIVE_VOWELS`
        are treated as over-typing: only their first MAX_CONSECUTIVE_VOWELS
        characters are segmented and expanded, and the remaining vowels of the
        run are dropped from the output tokens entirely (they never reach the
        later pipeline steps).

    Example:
        >>> permuteConsecutiveVowels(["koo"])
        ['koAo', 'koYo', 'koo']
    """
    vowelRegexPattern = r"[aeiou]{2,}"
    outList: list[str] = []

    for activeToken in inList:
        hasPatternMatched = False
        wordLevelOutput: list[str] = []
        regexMatches = re.finditer(vowelRegexPattern, activeToken)

        for activeMatch in regexMatches:
            hasPatternMatched = True
            vowelComboOutput: list[str] = []

            # Overflow runs beyond the cap are over-typing noise: only the
            # first MAX_CONSECUTIVE_VOWELS vowels are retained for
            # segmentation; the remainder of the run is dropped, so neither
            # step 09 nor the later steps ever expand those characters
            cappedRun = activeMatch.group()[:MAX_CONSECUTIVE_VOWELS]
            parsedVowelCombos = findVowelCombos(cappedRun)

            for currentCombo in parsedVowelCombos:
                # If the segmented sequence is a single vowel pattern, preserve it
                if len(currentCombo) == 1:
                    vowelComboOutput.extend(currentCombo)
                # Interleave uppercase anchors between multi-token vowel clusters
                else:
                    vowelComboOutput.extend(concatenateCombos(currentCombo, ["A", "Y"]))

            # Reconstruct the token by replacing the match span with each variation
            for uniqueVowelVariation in vowelComboOutput:
                spanStart, spanEnd = activeMatch.span()
                reconstructedWord = f"{activeToken[:spanStart]}{uniqueVowelVariation}{activeToken[spanEnd:]}"
                wordLevelOutput.append(reconstructedWord)

        # Append generated variants, or fallback to the original token if no match occurred
        outList.extend(wordLevelOutput if hasPatternMatched else [activeToken])

    return outList


# ******************************************************************************
