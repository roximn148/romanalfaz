# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
import re

import pytest

from romanalfaz.algorithm import (
    MAX_CONSECUTIVE_VOWELS,
    concatenateCombos,
    findVowelCombos,
    permuteAllOccurrences,
    permuteConsecutiveVowels,
    tafseerUrduRm2Rm,
)
from romanalfaz.exceptions import MaxVowelRunExceededError

# ******************************************************************************
# Golden candidate sets for the example words documented in docs/tafseer.ipynb
# and in the tafseerUrduRm2Rm docstring.
NOTEBOOK_GOLDEN_SETS: list[tuple[str, set[str]]] = [
    ("khalq", {"KHALQ", "KHLQ"}),
    ("alag", {"AALAG", "AALG", "ALAG", "ALG"}),
    ("ullo", {"ALO", "AOLO"}),
    ("bukhar", {"BKHAR", "BKHR", "BOKHAR", "BOKHR"}),
    ("bhai", {"BHAAY", "BHAY", "BHAYY", "BHE", "BHYY"}),
    ("hai", {"HAAY", "HAY", "HAYY", "HE", "HYY"}),
    ("bhayi", {"BHAYY", "BHYY"}),
    ("shohrat", {"SHHRAT", "SHHRT", "SHOHRAT", "SHOHRT"}),
    ("kya", {"KYA", "KYH"}),
]


# ******************************************************************************
class TestTafseerUrduRm2Rm:
    @pytest.mark.parametrize(
        ("romanWord", "expected"), NOTEBOOK_GOLDEN_SETS, ids=[w for w, _ in NOTEBOOK_GOLDEN_SETS]
    )
    def testNotebookGoldenWords(self, romanWord, expected):
        """Produces exactly the documented candidate set for each notebook example word."""
        assert tafseerUrduRm2Rm(romanWord) == expected

    def testEmptyInputReturnsEmptySet(self):
        """Returns an empty set for an empty input word."""
        assert tafseerUrduRm2Rm("") == set()

    @pytest.mark.parametrize(
        ("romanWord", "expectedCount"),
        [
            ("baaaarish", 146),
            ("kaaaaal", 227),
            ("baaaaaad", 697),
        ],
    )
    def testCandidateCountsAreStable(self, romanWord, expectedCount):
        """The total number of unique candidates is frozen for words with long vowel runs."""
        assert len(tafseerUrduRm2Rm(romanWord)) == expectedCount

    def testVowelRunBeyondLimitIsTruncated(self):
        """An overflow run is truncated: candidates match the word with the tail removed."""
        overflowWord = "b" + "a" * (MAX_CONSECUTIVE_VOWELS + 1) + "d"
        truncatedWord = "b" + "a" * MAX_CONSECUTIVE_VOWELS + "d"
        # Overflow vowels are dropped, so the candidate set is exactly that of
        # the input with the run clipped to MAX_CONSECUTIVE_VOWELS
        assert tafseerUrduRm2Rm(overflowWord) == tafseerUrduRm2Rm(truncatedWord)

    def testVowelRunAtLimitIsAccepted(self):
        """Accepts a consecutive-vowel run exactly at the documented limit."""
        # 8 vowels partition into exactly Fibonacci(9) = 34 chunk breakdowns
        assert len(findVowelCombos("a" * MAX_CONSECUTIVE_VOWELS)) == 34

    def testWorstCaseProbeWordIsTruncated(self):
        """A 10-vowel worst-case probe yields the 8-run candidate set, not an error."""
        # 10 consecutive 'a's: vowels beyond the cap are dropped at step 09
        assert tafseerUrduRm2Rm("b" + "a" * 10 + "d") == tafseerUrduRm2Rm(
            "b" + "a" * MAX_CONSECUTIVE_VOWELS + "d"
        )

    def testNoTokenExceedsTheVowelCapAfterStep09(self):
        """After step 09, no lowercase vowel run exceeds the cap (anchors don't count)."""
        # lowercase runs are the pipeline's typed vowels; uppercase A/Y/E anchors
        # are the encoding alphabet, not intake vowels
        tokens = permuteConsecutiveVowels(["k" + "e" * (MAX_CONSECUTIVE_VOWELS + 4) + "p"])
        assert tokens
        for token in tokens:
            longestRun = max(len(m.group()) for m in re.finditer(r"[aeiou]+", token))
            assert longestRun <= MAX_CONSECUTIVE_VOWELS


# ******************************************************************************
class TestPermuteAllOccurrences:
    def testStep04ShohRaTLineMatchesNotebook(self):
        """Reproduces the documented step-04 output list for the notebook word 'ShohRaT'."""
        hVowelCombos = {
            "ehe": ["eHe", "H"],
            "eh": ["eH", "H"],
            "oh": ["oH", "H"],
            "h": ["H"],
        }
        assert permuteAllOccurrences(["ShohRaT"], hVowelCombos) == ["SHoHRaT", "SHHRaT"]

    def testStep12ShohratLineMatchesNotebook(self):
        """Reproduces the documented step-12 output list for 'ShohRaT'/'SHHRaT' in order."""
        vowelReplacements = {
            "a": ["", "A"],
            "i": ["", "Y"],
            "u": ["", "O"],
            "e": ["E"],
            "o": ["O"],
        }
        assert permuteAllOccurrences(["SHoHRaT", "SHHRaT"], vowelReplacements) == [
            "SHOHRT", "SHOHRAT", "SHHRT", "SHHRAT",
        ]

    def testDuplicateListEntriesArePreserved(self):
        """Keeps duplicate output entries that the notebook documents for the 'BHYY/#HaYY' batch."""
        vowelReplacements = {
            "a": ["", "A"],
            "i": ["", "Y"],
            "u": ["", "O"],
            "e": ["E"],
            "o": ["O"],
        }
        assert permuteAllOccurrences(["BHYY", "BHaYY"], vowelReplacements) == [
            "BHYY", "BHYY", "BHAYY",
        ]

    def testDocstringExampleKhooshee(self):
        """Fully resolves the documented 'khooshee' example with the given rule map."""
        ruleMap = {"oo": ["u"], "ee": ["i"]}
        assert permuteAllOccurrences(["khooshee"], ruleMap) == ["khushi"]


# ******************************************************************************
class TestPermuteConsecutiveVowels:
    @pytest.mark.parametrize(
        ("token", "expected"),
        [
            # ['koo'] documents the true interleaving order (the original
            # docstring example listed ['koo', 'koAo', 'koYo'], which is stale)
            (["koo"], ["koAo", "koYo", "koo"]),
            (["sait"], ["saAit", "saYit", "sait"]),
            (["ua"], ["uAa", "uYa"]),
            (["aai"], ["aAaAi", "aAaYi", "aYaAi", "aYaYi", "aAai", "aYai", "aaAi", "aaYi"]),
        ],
    )
    def testNotebookStep09Samples(self, token, expected):
        """Reproduces the documented step-09 sample outputs in exact list order."""
        assert permuteConsecutiveVowels(token) == expected

    def testVowelRunBeyondLimitIsTruncated(self):
        """Truncates an overflow run to the capped prefix and drops the remainder."""
        overflowTokens = permuteConsecutiveVowels(["k" + "e" * (MAX_CONSECUTIVE_VOWELS + 1) + "p"])
        truncatedTokens = permuteConsecutiveVowels(["k" + "e" * MAX_CONSECUTIVE_VOWELS + "p"])
        # The 9th vowel is absent from every output, and the expanded prefix
        # is expanded exactly as a native capped run would be
        assert overflowTokens == truncatedTokens
        # no variation retains 9 consecutive 'e's: the overflow vowel is gone
        assert all("e" * (MAX_CONSECUTIVE_VOWELS + 1) not in t for t in overflowTokens)

    def testOverflowRunKeepsConsonantContext(self):
        """Truncation preserves the consonants flanking the overflow run."""
        variants = permuteConsecutiveVowels(["k" + "e" * (MAX_CONSECUTIVE_VOWELS + 4) + "p"])
        assert variants
        assert all(v.startswith("k") and v.endswith("p") for v in variants)


# ******************************************************************************
class TestFindVowelCombos:
    def testDefensiveRaiseOnDirectOversizeInput(self):
        """Segmentation itself still refuses a run longer than MAX_CONSECUTIVE_VOWELS."""
        with pytest.raises(MaxVowelRunExceededError) as excInfo:
            findVowelCombos("a" * (MAX_CONSECUTIVE_VOWELS + 1))
        assert str(MAX_CONSECUTIVE_VOWELS + 1) in str(excInfo.value)
    def testDocstringExampleAa(self):
        """Segments the documented 'aa' example into both partitions, in order."""
        assert findVowelCombos("aa") == [["a", "a"], ["aa"]]

    def testPartitionCountGrowsAsFibonacci(self):
        """Yields exactly Fibonacci(n+1) partitions for a run of n identical vowels."""
        # Fibonacci counts for the supported (guarded) run lengths 1..8
        fibonacci = [1, 2, 3, 5, 8, 13, 21, 34]
        for n, expected in enumerate(fibonacci, start=1):
            assert len(findVowelCombos("a" * n)) == expected


# ******************************************************************************
class TestConcatenateCombos:
    def testDocstringInterleavings(self):
        """Interleaves the documented separator variations in a deterministic order."""
        assert concatenateCombos(["b", "n", "n"], ["a", "o"]) == [
            "banan", "banon", "bonan", "bonon",
        ]
