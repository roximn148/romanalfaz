# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
import time
import unicodedata
from importlib import resources as importlibResources
from typing import NamedTuple

import pytest

from romanalfaz.urduspell import (
    LIGATURE_DELETED,
    LIGATURE_EXCLUDED,
    LIGATURE_MAP,
    PRESERVED_MARKS,
    URDU_VARIANT_MAP,
    URDU_VARIANT_REVERSAL_MAP,
    normalize,
    normalizeUrduChars,
    removeMarks,
    removeNonLetterChars,
)


# ******************************************************************************
class TestRemoveMarks:
    def testEmptyString(self):
        """Test that an empty string input returns an empty string."""
        assert removeMarks("") == ""

    def testLatinTextNoDiacritics(self):
        """Test that standard Latin text with punctuation remains completely unchanged."""
        text = "Hello, World! 123 @#$"
        assert removeMarks(text) == text

    def testMixedLatinUrduNoDiacritics(self):
        """Test mixed Latin and Urdu text without any diacritical marks."""
        text = "Python (پائیتھن) is a language!"
        assert removeMarks(text) == text

    def testUrduStandardDiacriticsRemoved(self):
        """Test removal of standard Urdu diacritics like fatha, kasra, damma, and shadda."""
        # مُحَمَّدٌ with damma, fatha, shadda, dammatan
        inputText = "\u0645\u064f\u062d\u064e\u0645\u0651\u064e\u062f\u064c"
        # محمد (base characters remaining)
        expectedOutput = "\u0645\u062d\u0645\u062f"
        assert removeMarks(inputText) == expectedOutput

    def testPreserveMadda(self):
        """Test that Madda (U+0653) on Alif (آ) is strictly preserved."""
        text = "آفتاب"
        assert removeMarks(text) == text

    def testPreserveHamzaAbove(self):
        """Test that Hamza Above (U+0654) on Yeh (ئ) is strictly preserved."""
        text = "آئینہ"
        assert removeMarks(text) == text

    def testMixedDiacriticsRetentionAndRemoval(self):
        """Test a complex mix where some marks are removed and essential ones are kept."""
        # قُرْآن - contains damma (remove), sukun (remove), and madda (keep)
        inputText = "\u0642\u064f\u0631\u0652\u0622\u0646"
        expectedOutput = "قرآن"
        assert removeMarks(inputText) == expectedOutput

    def testLatinDiacriticsRemoved(self):
        """Test that Latin combining diacritics (like French é or Spanish ñ) are stripped."""
        # decomposed 'é' (e + combining acute accent) and 'ñ' (n + combining tilde)
        inputText = "café niñO"
        expectedOutput = "cafe ninO"
        assert removeMarks(inputText) == expectedOutput

    def testMixedScriptChaos(self):
        """Test a highly mixed string with Latin, Urdu, symbols, numbers,
        and multiple diacritics."""
        # 'بَ' (ba + fatha -> remove fatha), 'آ' (keep), Latin symbols, 'é' (remove accent)
        inputText = "بَ !@# 123 آ café"
        expectedOutput = "ب !@# 123 آ cafe"
        assert removeMarks(inputText) == expectedOutput

    def testInvalidInputTypeRaisesAssertionError(self):
        """Test that passing a non-string object correctly raises an AssertionError."""
        with pytest.raises(AssertionError) as excInfo:
            removeMarks(12345)
        assert "Input must be a string" in str(excInfo.value)

    def testNoneInputRaisesAssertionError(self):
        """Test that passing None correctly triggers the type guard clause."""
        with pytest.raises(AssertionError):
            removeMarks(None)


# ******************************************************************************
class TestNormalizeNonChars:
    def testEmptyString(self):
        """Test that an empty string input returns an empty string."""
        assert removeNonLetterChars("") == ""

    def testCleanAlphabeticTextPreserved(self):
        """Test that pure alphabetic Latin and Urdu text without non-characters remains intact."""
        text = "Hello ایک لفظ"
        assert removeNonLetterChars(text) == text

    def testPunctuationAndSymbolsRemoved(self):
        """Test that Latin, Urdu, and symbolic punctuation are completely removed."""
        inputText = "سلام! (Hello, World?) [ایک] #Urdu @Script۔"
        expectedOutput = "سلام Hello World ایک Urdu Script"
        assert removeNonLetterChars(inputText) == expectedOutput

    def testDigitsRemoved(self):
        """Test that both Latin and Urdu digits are successfully removed from the text."""
        inputText = "Page 123 صفحہ ۴۵۶"
        expectedOutput = "Page  صفحہ "
        assert removeNonLetterChars(inputText) == expectedOutput

    def testDiacriticsRemovedExceptPreserved(self):
        """Test that standard Urdu/Latin diacritics are stripped, while
        structural marks (Madda) remain."""
        # مُحَمَّدٌ (contains standard diacritics to remove) and قرآن (contains Madda to preserve)
        inputText = "\u0645\u064f\u062d\u064e\u0645\u0651\u064e\u062f\u064c قرآن café"
        expectedOutput = "محمد قرآن cafe"
        assert removeNonLetterChars(inputText) == expectedOutput

    def testControlCharactersRemoved(self):
        """Test that control characters (p{C}) like newlines, tabs, and null bytes are stripped."""
        inputText = "Urdu\nٹیکسٹ\tData\x00"
        expectedOutput = "UrduٹیکسٹData"
        assert removeNonLetterChars(inputText) == expectedOutput

    def testWhitespacePreservation(self):
        """Test that standard spaces are preserved while consecutive
        punctuation separation leaves clean spaces."""
        inputText = "Word1,,,   Word2!!!   لفظ۳"
        expectedOutput = "Word   Word   لفظ"
        assert removeNonLetterChars(inputText) == expectedOutput

    def testChaosMixedScriptBoundaryCase(self):
        """Test a chaotic boundary string mixing Latin, Urdu, math symbols, numbers, and accents."""
        # "ٹیکسٹ! 786 + café = Best??" -> "ٹیکسٹ  cafe  Best"
        inputText = "ٹیکسٹ! 786 + café = Best??"
        expectedOutput = "ٹیکسٹ   cafe  Best"
        assert removeNonLetterChars(inputText) == expectedOutput

    def testInvalidInputTypeRaisesAssertionError(self):
        """Test that passing a non-string object correctly triggers the type guard assertion."""
        with pytest.raises(AssertionError) as excInfo:
            removeNonLetterChars([1, 2, 3])
        assert "Input must be a string" in str(excInfo.value)

    def testNoneInputRaisesAssertionError(self):
        """Test that passing None causes the type check guard clause to fail."""
        with pytest.raises(AssertionError):
            removeNonLetterChars(None)


# ******************************************************************************
class TestNormalizeUrduChars:
    def testEmptyString(self):
        """Test that an empty string input returns an empty string."""
        assert normalizeUrduChars("") == ""

    def testStandardTextRemainsUnchanged(self):
        """Test that standard Urdu text without ligatures or
        positional variants remains untouched."""
        # This test verifies behavior against the existing map contents
        text = "یہ ایک سادہ جملہ ہے۔"
        # The output should equal input if input contains no elements present in the maps
        assert normalizeUrduChars(text) == text

    def testLatinAndSymbolsPreserved(self):
        """Test that Latin text, digits, and symbols are entirely preserved and untouched."""
        text = "Python 3.10! @#$ [Test] alphanumeric text"
        assert normalizeUrduChars(text) == text

    def testMultiCharacterLigaturesReplaced(self):
        """Test that keys present in LIGATURE_MAP are replaced by
        their mapped values if found in the input."""
        # We use a conditional check to find an available key from the pre-defined LIGATURE_MAP
        if LIGATURE_MAP:
            testLigature = next(iter(LIGATURE_MAP))
            expectedReplacement = LIGATURE_MAP[testLigature]

            inputText = f"ٹیکسٹ {testLigature} 123"
            expectedOutput = f"ٹیکسٹ {expectedReplacement} 123"
            assert normalizeUrduChars(inputText) == expectedOutput
        else:
            pytest.skip("LIGATURE_MAP is empty, skipping dynamic evaluation.")

    def testPositionalVariantsReversed(self):
        """Test that keys present in URDU_VARIANT_REVERSAL_MAP are
        mapped back to their base forms."""
        # We use a conditional check to find an available key from
        # the pre-defined URDU_VARIANT_REVERSAL_MAP
        if URDU_VARIANT_REVERSAL_MAP:
            testVariant = next(iter(URDU_VARIANT_REVERSAL_MAP))
            expectedBase = URDU_VARIANT_REVERSAL_MAP[testVariant]

            inputText = f"ٹیکسٹ {testVariant} abc"
            expectedOutput = f"ٹیکسٹ {expectedBase} abc"
            assert normalizeUrduChars(inputText) == expectedOutput
        else:
            pytest.skip("URDU_VARIANT_REVERSAL_MAP is empty, skipping dynamic evaluation.")

    def testMixedChaosLigaturesVariantsAndLatin(self):
        """Test a chaotic string mixing Latin elements, digits, and
        elements from both maps if populated."""
        inputText = "Urdu ٹیکسٹ 123 !@#"
        expectedOutput = "Urdu ٹیکسٹ 123 !@#"

        # Dynamically inject one item from each dictionary into the
        # text to run a combined simulation
        if LIGATURE_MAP:
            ligatureKey = next(iter(LIGATURE_MAP))
            inputText += f" {ligatureKey}"
            expectedOutput += f" {LIGATURE_MAP[ligatureKey]}"

        if URDU_VARIANT_REVERSAL_MAP:
            variantKey = next(iter(URDU_VARIANT_REVERSAL_MAP))
            inputText += f" {variantKey}"
            expectedOutput += f" {URDU_VARIANT_REVERSAL_MAP[variantKey]}"

        assert normalizeUrduChars(inputText) == expectedOutput

    def testFixedCodepointsNormalizeToBase(self):
        """Test that every form repaired by the variant map
        corrections normalizes to its base character."""
        # The table pins the repaired forms: HEH DOACHASHMEE -> ھ, FARSI YEH -> ی
        # (including the ALEF MAKSURA cross-map, which resolves to ی by design),
        # HEH GOAL / HEH WITH YEH ABOVE -> ہ, YEH BARREE and YEH BARREE WITH
        # HAMZA ABOVE -> ے, and TEH MARBUTA -> TEH MARBUTA GOAL ۃ.
        fixedForms = {
            "\ufbaa": "\u06be",  # ARABIC LETTER HEH DOACHASHMEE ISOLATED FORM
            "\ufbab": "\u06be",  # ARABIC LETTER HEH DOACHASHMEE FINAL FORM
            "\ufbac": "\u06be",  # ARABIC LETTER HEH DOACHASHMEE INITIAL FORM
            "\ufbad": "\u06be",  # ARABIC LETTER HEH DOACHASHMEE MEDIAL FORM
            "\ufbfc": "\u06cc",  # ARABIC LETTER FARSI YEH ISOLATED FORM
            "\ufbfd": "\u06cc",  # ARABIC LETTER FARSI YEH FINAL FORM
            "\ufbfe": "\u06cc",  # ARABIC LETTER FARSI YEH INITIAL FORM
            "\ufbff": "\u06cc",  # ARABIC LETTER FARSI YEH MEDIAL FORM
            "\ufeef": "\u06cc",  # ARABIC LETTER ALEF MAKSURA ISOLATED FORM (cross-map)
            "\ufef0": "\u06cc",  # ARABIC LETTER ALEF MAKSURA FINAL FORM (cross-map)
            "\ufba4": "\u06c1",  # ARABIC LETTER HEH WITH YEH ABOVE ISOLATED FORM
            "\ufba5": "\u06c1",  # ARABIC LETTER HEH WITH YEH ABOVE FINAL FORM
            "\ufbae": "\u06d2",  # ARABIC LETTER YEH BARREE ISOLATED FORM
            "\ufbaf": "\u06d2",  # ARABIC LETTER YEH BARREE FINAL FORM
            "\ufbb0": "\u06d2",  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE ISOLATED FORM
            "\ufbb1": "\u06d2",  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE FINAL FORM
            "\u0629": "\u06c3",  # ARABIC LETTER TEH MARBUTA
            "\ufe93": "\u06c3",  # ARABIC LETTER TEH MARBUTA ISOLATED FORM
            "\ufe94": "\u06c3",  # ARABIC LETTER TEH MARBUTA FINAL FORM
        }
        for form, base in fixedForms.items():
            assert normalizeUrduChars(form) == base

    def testInvalidInputTypeRaisesAssertionError(self):
        """Test that passing a non-string object correctly triggers the type guard validation."""
        with pytest.raises(AssertionError) as excInfo:
            normalizeUrduChars(98765)
        assert "Input must be a string" in str(excInfo.value)

    def testNoneInputRaisesAssertionError(self):
        """Test that passing None explicitly triggers the type assertion failure."""
        with pytest.raises(AssertionError):
            normalizeUrduChars(None)


# ******************************************************************************
# Presentation-form helpers for the map structure tests below. Arabic
# presentation forms live in two Unicode blocks: U+FB50-U+FDFF (Presentation
# Forms-A) and U+FE70-U+FEFF (Presentation Forms-B).
PRESENTATION_FORM_KINDS = ("ISOLATED FORM", "FINAL FORM", "INITIAL FORM", "MEDIAL FORM")
PRESENTATION_BLOCKS = ((0xFB50, 0xFDFF), (0xFE70, 0xFEFF))


def officialName(codepoint):
    """Return the official Unicode name of a codepoint, or None if it is unassigned."""
    try:
        return unicodedata.name(codepoint)
    except ValueError:
        return None


def isOwnForm(base, variant):
    """Return True if the variant is the base itself or one of its own presentation forms."""
    baseName = officialName(base)
    variantName = officialName(variant)
    if baseName is None or variantName is None:
        return False
    return variant == base or any(
        variantName == f"{baseName} {kind}" for kind in PRESENTATION_FORM_KINDS
    )


def ownPresentationForms(base):
    """Return the set of presentation forms officially named after the base character."""
    forms = set()
    for low, high in PRESENTATION_BLOCKS:
        for codepoint in range(low, high + 1):
            char = chr(codepoint)
            if char != base and isOwnForm(base, char):
                forms.add(char)
    return forms


# ******************************************************************************
class TestUrduVariantMap:
    """Tests for the URDU_VARIANT_MAP data structure (base characters -> variant forms)."""

    def testKeysAreSingleCodepoints(self):
        """Test that every key is a single codepoint, except the TATWEEL strip entry ('')."""
        for base in URDU_VARIANT_MAP:
            assert isinstance(base, str)
            assert len(base) in (0, 1), f"key {base!r} must be '' or a single codepoint"

    def testVariantsAreSingleCodepoints(self):
        """Test that every variant in every list is exactly one codepoint."""
        for base, variants in URDU_VARIANT_MAP.items():
            for variant in variants:
                assert isinstance(variant, str)
                assert len(variant) == 1, (
                    f"variant {variant!r} under {base!r} must be a single codepoint"
                )

    def testFirstVariantEqualsBase(self):
        """Test that the first variant of every entry is the base character itself.

        The TATWEEL entry is the exception: it maps U+0640 to '' (strip) by design.
        """
        for base, variants in URDU_VARIANT_MAP.items():
            if base == "":
                assert variants == ["\u0640"], "the TATWEEL entry must strip U+0640 to ''"
                continue
            assert variants[0] == base, f"first variant of {base!r} must be the base itself"

    def testNoDuplicateCodepointsWithinOrAcrossLists(self):
        """Test that no codepoint appears twice in one list nor in two different lists."""
        seen = {}
        for base, variants in URDU_VARIANT_MAP.items():
            for variant in variants:
                assert variant not in seen, (
                    f"U+{ord(variant):04X} appears under both {seen[variant]!r} and {base!r}"
                )
                seen[variant] = base

    def testEveryCodepointHasOfficialUnicodeName(self):
        """Test that every codepoint in both maps is an assigned character with an official name.

        Exception: the Unicode 17.0 honorific ligatures are deliberately kept
        as deleted literals although unicodedata 16.0.0 leaves them
        unassigned (see TestLigatureCoverage).
        """
        codepoints = set()
        for base, variants in URDU_VARIANT_MAP.items():
            if base:
                codepoints.add(base)
            codepoints.update(variants)
        for ligature, replacement in LIGATURE_MAP.items():
            codepoints.add(ligature)
            codepoints.update(replacement)
        v17Deleted = {cp for cp in LIGATURE_DELETED if officialName(cp) is None}
        unassigned = [
            f"U+{ord(codepoint):04X}"
            for codepoint in sorted(codepoints - v17Deleted, key=ord)
            if officialName(codepoint) is None
        ]
        assert not unassigned, f"unassigned codepoints in maps: {unassigned}"

    def testKeyedBasesListTheirOwnPresentationForms(self):
        """Test that every keyed base lists all of its own presentation forms under its key."""
        for base, variants in URDU_VARIANT_MAP.items():
            if base == "":
                continue
            missing = ownPresentationForms(base) - set(variants)
            assert not missing, (
                f"base {base!r} (U+{ord(base):04X}) is missing its own forms "
                f"{[f'U+{ord(c):04X}' for c in sorted(missing)]}"
            )

    def testCrossMapsMatchIntentionalAllowlist(self):
        """Test that foreign codepoints listed under a base are
        exactly the intentional cross-map set."""
        expectedCrossMaps = {
            # URDU KAF (ک): Arabic KAF and forms, Old Persian GUEH and forms
            "\u06a9": {
                "\u0643", "\ufed9", "\ufeda", "\ufedb", "\ufedc",
                "\u06a8", "\ufb96", "\ufb97", "\ufb98", "\ufb99",
            },
            # WAO (و): WAW WITH HAMZA ABOVE and forms
            "\u0648": {"\u0624", "\ufe85", "\ufe86"},
            # HE GOAL (ہ): Arabic HEH and forms, HEH GOAL WITH HAMZA ABOVE,
            # HEH WITH YEH ABOVE and forms
            "\u06c1": {
                "\u0647", "\ufee9", "\ufeea", "\ufeeb", "\ufeec",
                "\u06c2",
                "\u06c0", "\ufba4", "\ufba5",
            },
            # TEH MARBUTA GOAL (ۃ): Arabic TEH MARBUTA and forms
            "\u06c3": {"\u0629", "\ufe93", "\ufe94"},
            # ALIF (ا): the sanctioned ALEF WITH HAMZA ABOVE/BELOW exception
            # enabling full lam-alef ligature coverage (U+FEF7-U+FEFA)
            "\u0627": {"\u0623", "\u0625"},
            # FARSI YEH (ی): Arabic YEH and forms, ALEF MAKSURA and forms
            "\u06cc": {
                "\u064a", "\ufef1", "\ufef2", "\ufef3", "\ufef4",
                "\u0649", "\ufeef", "\ufef0",
            },
            # BARI YE (ے): YEH BARREE WITH HAMZA ABOVE and forms
            "\u06d2": {"\u06d3", "\ufbb0", "\ufbb1"},
        }
        for base, variants in URDU_VARIANT_MAP.items():
            if base == "":
                continue
            foreign = {
                variant
                for variant in variants
                if not isOwnForm(base, variant)
            }
            expected = expectedCrossMaps.get(base, set())
            assert foreign == expected, (
                f"cross-map mismatch for base {base!r} (U+{ord(base):04X}): "
                f"extra={sorted(f'U+{ord(c):04X}' for c in foreign - expected)}, "
                f"missing={sorted(f'U+{ord(c):04X}' for c in expected - foreign)}"
            )


# ******************************************************************************
class TestUrduVariantReversalMap:
    """Tests for the URDU_VARIANT_REVERSAL_MAP data structure (variants -> base characters)."""

    def testConsistentWithUrduVariantMap(self):
        """Test that the reversal map is exactly the flattening of URDU_VARIANT_MAP."""
        expected = {
            variant: base
            for base, variants in URDU_VARIANT_MAP.items()
            for variant in variants
        }
        assert URDU_VARIANT_REVERSAL_MAP == expected


# ******************************************************************************
class TestLigatureMap:
    """Tests for the LIGATURE_MAP data structure (ligature forms -> base character sequences)."""

    def testKeysAreSingleCodepoints(self):
        """Test that every ligature key is exactly one codepoint."""
        for ligature in LIGATURE_MAP:
            assert isinstance(ligature, str)
            assert len(ligature) == 1, f"ligature key {ligature!r} must be a single codepoint"

    def testValuesAreBaseCharsCombiningMarksOrEmpty(self):
        """Test that every replacement character folds to a base character
        (via URDU_VARIANT_REVERSAL_MAP) or is a combining mark that
        removeMarks strips downstream, and that deleted ligatures map to ''."""
        for ligature, replacement in LIGATURE_MAP.items():
            if ligature in LIGATURE_DELETED:
                assert replacement == "", (
                    f"deleted ligature {ligature!r} (U+{ord(ligature):04X}) must map to ''"
                )
                continue
            assert replacement, (
                f"replacement for {ligature!r} (U+{ord(ligature):04X}) must not be empty"
            )
            for char in replacement:
                assert char in URDU_VARIANT_REVERSAL_MAP or unicodedata.combining(char) > 0, (
                    f"{char!r} (U+{ord(char):04X}) in the replacement for "
                    f"{ligature!r} (U+{ord(ligature):04X}) is neither a variant-map "
                    f"codepoint nor a combining mark"
                )

    def testNoSpaceOrTatweelInAnyValue(self):
        """Test that no replacement emits U+0020 (SPACE) or U+0640 (TATWEEL):
        a space or tatweel inside a word would split it for lookup."""
        for ligature, replacement in LIGATURE_MAP.items():
            assert " " not in replacement, (
                f"replacement for {ligature!r} (U+{ord(ligature):04X}) contains U+0020"
            )
            assert "\u0640" not in replacement, (
                f"replacement for {ligature!r} (U+{ord(ligature):04X}) contains U+0640"
            )


# ******************************************************************************
# Presentation-form helpers for the ligature coverage tests below. The
# ligature codepoints are the assigned characters of the two presentation
# blocks whose official Unicode names contain LIGATURE.


def ligatureCodepoints():
    """Return the sorted codepoints of every assigned ligature character
    in the two Arabic presentation-form blocks."""
    codepoints = []
    for low, high in PRESENTATION_BLOCKS:
        for codepoint in range(low, high + 1):
            name = officialName(chr(codepoint))
            if name and "LIGATURE" in name:
                codepoints.append(codepoint)
    return codepoints


# ******************************************************************************
class TestLigatureCoverage:
    """Tests pinning the full ligature coverage of the two presentation blocks.

    The ligature set is 519 codepoints: 494 assigned ligature codepoints
    (U+FB50-FDFF and U+FE70-FEFF, unicodedataplus 16.0.0) plus 25 honorific
    ligatures added in Unicode 17.0 that are unassigned in unicodedataplus
    16.0.0 (U+FBC3-FBD2, U+FD90-FD91, U+FDC8-FDCE). Of the 519, 448 decompose
    to base-character sequences, 57 honorific/phrase ligatures are deleted to
    '', and 14 Uyghur/non-Urdu ligatures are excluded from the table entirely.
    """

    def testExcludedRegistryPinsExactlyTheFourteenNonUrduLigatures(self):
        """Test that LIGATURE_EXCLUDED is exactly the FBEC/FBED and
        FBF0-FBFB groups (partner letters outside the Urdu charset)."""
        expected = {
            0xFBEC, 0xFBED,  # YEH WITH HAMZA ABOVE WITH AE (partner U+06D5)
            *range(0xFBF0, 0xFBF9),  # YEH WITH HAMZA ABOVE WITH U/OE/YU/E
            *range(0xFBF9, 0xFBFC),  # UIGHUR KIRGHIZ YEH ... WITH ALEF MAKSURA
        }
        assert {ord(c) for c in LIGATURE_EXCLUDED} == expected

    def testDeletedRegistryPinsExactlyTheFiftySevenHonorificLigatures(self):
        """Test that LIGATURE_DELETED is exactly the honorific, invocation,
        and standalone-word ligature groups, including the Unicode 17.0
        additions."""
        expected = {
            *range(0xFBC3, 0xFBD3),  # honorifics (Unicode 17.0)
            0xFD90, 0xFD91,  # honorifics (Unicode 17.0)
            *range(0xFDC8, 0xFDCF),  # honorifics (Unicode 17.0)
            *range(0xFD40, 0xFD50),  # honorific/invocation ligatures
            0xFDCF,  # SALAAMUHU ALAYNAA
            *range(0xFDF0, 0xFDFC),  # standalone words and phrases (incl. ALLAH)
            *range(0xFDFD, 0xFE00),  # BISMILLAH..., SUBHAANAHU..., AZZA WA JALL
        }
        assert {ord(c) for c in LIGATURE_DELETED} == expected

    def testUnicodeSeventeenLigaturesAreUnassignedYetDeleted(self):
        """Test the version skew explicitly: the 25 Unicode 17.0 honorific
        ligatures are unassigned in the installed unicodedata (16.0.0), so
        their names cannot be looked up, yet they must be present in
        LIGATURE_MAP with '' values (version-independent deletion)."""
        v17 = {
            *range(0xFBC3, 0xFBD3),
            0xFD90, 0xFD91,
            *range(0xFDC8, 0xFDCF),
        }
        assert len(v17) == 25
        for codepoint in v17:
            assert officialName(chr(codepoint)) is None, f"U+{codepoint:04X}"
            assert LIGATURE_MAP.get(chr(codepoint)) == "", f"U+{codepoint:04X}"

    def testEveryLigatureCodepointIsAccountedFor(self):
        """Test that mapped, deleted, and excluded classes partition the
        519 ligature codepoints with no overlap and no silent gaps: the 494
        assigned codepoints of the two ranges plus the 25 Unicode 17.0
        additions, which are deleted literals despite being unassigned in
        unicodedata 16.0.0."""
        ligatures = set(ligatureCodepoints())
        v17 = {
            *range(0xFBC3, 0xFBD3),
            0xFD90, 0xFD91,
            *range(0xFDC8, 0xFDCF),
        }
        mapped = {ord(c) for c, replacement in LIGATURE_MAP.items() if replacement}
        deleted = {ord(c) for c, replacement in LIGATURE_MAP.items() if not replacement}
        excluded = {ord(c) for c in LIGATURE_EXCLUDED}
        assert len(ligatures) == 494
        assert len(v17) == 25
        assert len(mapped) + len(deleted) + len(excluded) == 519
        assert not mapped & deleted, "a codepoint cannot be both mapped and deleted"
        assert not mapped & excluded, "a codepoint cannot be both mapped and excluded"
        assert not deleted & excluded, "a codepoint cannot be both deleted and excluded"
        missing = sorted(f"U+{cp:04X}" for cp in (ligatures | v17) - (mapped | deleted | excluded))
        assert mapped | deleted | excluded == ligatures | v17, f"silent gaps: {missing}"

    def testDeletedEntriesMapToEmptyString(self):
        """Test that every registry entry of LIGATURE_DELETED maps to '' in the table."""
        for char in LIGATURE_DELETED:
            assert LIGATURE_MAP[char] == ""

    def testDeletedEntriesAreCompleteWordsAndVanishUnderNormalize(self):
        """Test that honorific and phrase ligatures are stripped outright
        by the full pipeline, including a Unicode 17.0 addition."""
        for codepoint in (0xFBC3, 0xFD40, 0xFDCF, 0xFDF2, 0xFDFD, 0xFDFA):
            assert normalize(chr(codepoint)) == "", f"U+{codepoint:04X}"

    def testMarkBearingLigaturesMapToMarksOnly(self):
        """Test that the mark-bearing ligatures whose decompositions hold
        U+0020/U+0640 (U+FC5E-FC63, U+FCF2-FCF4) map to combining marks
        only, and are then stripped by the full pipeline."""
        for codepoint in [*range(0xFC5E, 0xFC64), *range(0xFCF2, 0xFCF5)]:
            replacement = LIGATURE_MAP[chr(codepoint)]
            assert replacement, f"U+{codepoint:04X} must not map to ''"
            assert all(unicodedata.combining(c) > 0 for c in replacement), (
                f"U+{codepoint:04X} must map to combining marks only"
            )
            assert normalize(chr(codepoint)) == "", f"U+{codepoint:04X}"

    def testAllEightLamAlefLigaturesNormalize(self):
        """Test that all eight U+FEF5-FEFC ligatures normalize through the
        full pipeline to lam-alef or lam-alef-madda."""
        for codepoint in range(0xFEF7, 0xFEFD):
            assert normalize(chr(codepoint)) == "\u0644\u0627", f"U+{codepoint:04X}"
        for codepoint in (0xFEF5, 0xFEF6):
            assert normalize(chr(codepoint)) == "\u0644\u0622", f"U+{codepoint:04X}"

    def testYehHamzaLigaturesFoldToBaseSequences(self):
        """Test that the Urdu YEH WITH HAMZA ligatures (U+FBEA-FBEB,
        U+FBEE-FBEF) fold to their base character pairs."""
        for codepoint in (0xFBEA, 0xFBEB):
            assert normalizeUrduChars(chr(codepoint)) == "\u0626\u0627", f"U+{codepoint:04X}"
        for codepoint in (0xFBEE, 0xFBEF):
            assert normalizeUrduChars(chr(codepoint)) == "\u0626\u0648", f"U+{codepoint:04X}"

    def testExcludedLigaturesPassThroughUnchanged(self):
        """Test that the excluded Uyghur/non-Urdu ligatures have no entry
        and pass through normalizeUrduChars untouched."""
        for codepoint in (0xFBEC, 0xFBF0, 0xFBF9):
            char = chr(codepoint)
            assert char not in LIGATURE_MAP, f"U+{codepoint:04X} must have no entry"
            assert char in LIGATURE_EXCLUDED
            assert normalizeUrduChars(char) == char

    def testRialSignHasNoEntry(self):
        """Test that U+FDFC (ARABIC RIAL SIGN, not a ligature) is absent
        from the table and passes through."""
        assert "\ufdfc" not in LIGATURE_MAP
        assert normalizeUrduChars("\ufdfc") == "\ufdfc"

    def testBareHamzaAlefFoldsToAlef(self):
        """Test that the sanctioned U+0623/U+0625 exception folds bare
        hamza'd alefs to ALEF through both the char stage and the pipeline."""
        for codepoint in (0x0623, 0x0625):
            assert normalizeUrduChars(chr(codepoint)) == "\u0627", f"U+{codepoint:04X}"
            assert normalize(chr(codepoint)) == "\u0627", f"U+{codepoint:04X}"

    def testPreservedMarksUnmodified(self):
        """Test that the ligature work left PRESERVED_MARKS exactly the
        structural pair {U+0653, U+0654}."""
        assert PRESERVED_MARKS == {"\u0653", "\u0654"}

    def testOriginalLamAlefEntriesDoNotRegress(self):
        """Test the original four-entry behavior: isolated/final
        lam-alef to lam+alef and isolated/final lam-alef-madda to
        lam+alef-madda."""
        assert LIGATURE_MAP["\ufefb"] == "\u0644\u0627"
        assert LIGATURE_MAP["\ufefc"] == "\u0644\u0627"
        assert LIGATURE_MAP["\ufef5"] == "\u0644\u0622"
        assert LIGATURE_MAP["\ufef6"] == "\u0644\u0622"
        assert normalizeUrduChars("\ufefb\ufefc") == "\u0644\u0627" * 2
        assert normalizeUrduChars("\ufef5\ufef6") == "\u0644\u0622" * 2


# ******************************************************************************
MAX_REPORTED_VIOLATIONS = 20
"""How many round-trip violations the failure message lists before capping."""


class VocabularySnapshot(NamedTuple):
    """The parsed bundled vocabulary plus the timings of the stability pass."""

    words: list[str]
    """(list[str]): The bundled words in file order."""
    frequencies: list[int]
    """(list[int]): The bundled frequencies, aligned with `words`."""
    loadDuration: float
    """(float): Seconds spent loading and parsing the vocabulary file."""
    normalizeDuration: float
    """(float): Seconds spent in the per-word normalize pass."""
    violations: list[tuple[int, str, str]]
    """(list): ``(lineno, word, normalized)`` for every word that does not round-trip."""


def formatViolations(violations: list[tuple[int, str, str]]) -> str:
    """
    Formats the round-trip violations into a single actionable message.

    Args:
        violations (list[tuple[int, str, str]]): The ``(lineno, word,
            normalized)`` triples of every word that does not round-trip.

    Returns:
        str: A message listing the first
        :data:`romanalfaz.tests.test_urduspell.MAX_REPORTED_VIOLATIONS`
        violations with their line numbers, plus the total count.
    """
    shown = violations[:MAX_REPORTED_VIOLATIONS]
    lines = [
        "the bundled vocabulary does not round-trip under "
        "romanalfaz.urduspell.normalize "
        f"({len(violations)} violation(s), first {len(shown)} shown):"
    ]
    lines.extend(
        f"  line {lineno}: word={word!r} normalized={normalized!r}"
        for lineno, word, normalized in shown
    )
    if len(violations) > len(shown):
        lines.append(f"  ... and {len(violations) - len(shown)} more")
    return "\n".join(lines)


# ******************************************************************************
class TestVocabularyStability:
    """Tests that the bundled vocabulary round-trips under normalization.

    The bundled ``UrduWords5k.sym`` is canonical by construction: every word
    is stored in its base-letter Urdu form. This class guarantees that the
    shipped dictionary round-trips under
    :py:func:`romanalfaz.urduspell.normalize`, so any normalization change
    that would rewrite the shipped vocabulary fails loudly and names the
    broken words instead of silently changing the dictionary. Changing the
    vocabulary therefore requires a deliberate, reviewed decision.

    Note:
        The class-scoped `snapshot` fixture loads and parses the vocabulary
        and runs the per-word normalize pass exactly once per class, timing
        both steps separately with ``time.perf_counter``. The timings are
        recorded (and printed) for placement optimization only; they are
        deliberately not asserted against a threshold.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def snapshot(cls) -> VocabularySnapshot:
        """Loads, parses, and normalizes the bundled vocabulary once, timed.

        Returns:
            VocabularySnapshot: The parsed words and frequencies, both
            step durations, and the collected round-trip violations.
        """
        startedAt = time.perf_counter()
        symPath = importlibResources.files("romanalfaz") / "UrduWords5k.sym"
        symText = symPath.read_text(encoding="utf-8")
        words: list[str] = []
        frequencies: list[int] = []
        for lineno, line in enumerate(symText.splitlines(), start=1):
            assert line.strip(), f"line {lineno}: blank line in bundled vocabulary"
            word, separator, frequencyText = line.rpartition("$")
            assert separator and word and frequencyText.isdigit(), (
                f"line {lineno}: malformed vocabulary line {line!r}"
            )
            words.append(word)
            frequencies.append(int(frequencyText))
        loadDuration = time.perf_counter() - startedAt

        normalizeStartedAt = time.perf_counter()
        violations = [
            (lineno, word, normalized)
            for lineno, word, normalized in (
                (lineno, word, normalize(word))
                for lineno, word in enumerate(words, start=1)
            )
            if normalized != word
        ]
        normalizeDuration = time.perf_counter() - normalizeStartedAt
        return VocabularySnapshot(
            words, frequencies, loadDuration, normalizeDuration, violations
        )

    def testBundledWordCountIsPinned(self, snapshot):
        """Test that the bundled vocabulary has exactly 4994 entries."""
        assert len(snapshot.words) == 4994

    def testEveryWordRoundTripsUnderNormalize(self, snapshot):
        """Test that every bundled word is already canonical: normalize(word) == word.

        Fails with a single message naming every broken line (capped at the
        first 20) instead of stopping at the first mismatch.
        """
        assert not snapshot.violations, formatViolations(snapshot.violations)

    def testStabilityPassTimingsAreRecorded(self, snapshot, capsys):
        """Test that both step durations were measured and are non-negative.

        This is a recording check, not a performance threshold: the timings
        exist so the assertion's placement can be optimized if the pass
        becomes slow.
        """
        assert snapshot.loadDuration >= 0.0
        assert snapshot.normalizeDuration >= 0.0
        print(
            f"\nvocabulary load/parse: {snapshot.loadDuration:.4f} s; "
            f"normalize pass: {snapshot.normalizeDuration:.4f} s "
            f"({len(snapshot.words)} words)"
        )


# ******************************************************************************
