# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
import unicodedata

import pytest

from romanalfaz.urduspell import (
    LIGATURE_MAP,
    URDU_VARIANT_MAP,
    URDU_VARIANT_REVERSAL_MAP,
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
        """Test a highly mixed string with Latin, Urdu, symbols, numbers, and multiple diacritics."""
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
        """Test that standard Urdu/Latin diacritics are stripped, while structural marks (Madda) remain."""
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
        """Test that standard spaces are preserved while consecutive punctuation separation leaves clean spaces."""
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
        """Test that standard Urdu text without ligatures or positional variants remains untouched."""
        # This test verifies behavior against the existing map contents
        text = "یہ ایک سادہ جملہ ہے۔"
        # The output should equal input if input contains no elements present in the maps
        assert normalizeUrduChars(text) == text

    def testLatinAndSymbolsPreserved(self):
        """Test that Latin text, digits, and symbols are entirely preserved and untouched."""
        text = "Python 3.10! @#$ [Test] alphanumeric text"
        assert normalizeUrduChars(text) == text

    def testMultiCharacterLigaturesReplaced(self):
        """Test that keys present in LIGATURE_MAP are replaced by their mapped values if found in the input."""
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
        """Test that keys present in URDU_VARIANT_REVERSAL_MAP are mapped back to their base forms."""
        # We use a conditional check to find an available key from the pre-defined URDU_VARIANT_REVERSAL_MAP
        if URDU_VARIANT_REVERSAL_MAP:
            testVariant = next(iter(URDU_VARIANT_REVERSAL_MAP))
            expectedBase = URDU_VARIANT_REVERSAL_MAP[testVariant]

            inputText = f"ٹیکسٹ {testVariant} abc"
            expectedOutput = f"ٹیکسٹ {expectedBase} abc"
            assert normalizeUrduChars(inputText) == expectedOutput
        else:
            pytest.skip("URDU_VARIANT_REVERSAL_MAP is empty, skipping dynamic evaluation.")

    def testMixedChaosLigaturesVariantsAndLatin(self):
        """Test a chaotic string mixing Latin elements, digits, and elements from both maps if populated."""
        inputText = "Urdu ٹیکسٹ 123 !@#"
        expectedOutput = "Urdu ٹیکسٹ 123 !@#"

        # Dynamically inject one item from each dictionary into the text to run a combined simulation
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
        """Test that every form repaired by the variant map corrections normalizes to its base character."""
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
        """Test that every codepoint in both maps is an assigned character with an official name."""
        codepoints = set()
        for base, variants in URDU_VARIANT_MAP.items():
            if base:
                codepoints.add(base)
            codepoints.update(variants)
        for ligature, replacement in LIGATURE_MAP.items():
            codepoints.add(ligature)
            codepoints.update(replacement)
        unassigned = [
            f"U+{ord(codepoint):04X}"
            for codepoint in sorted(codepoints, key=ord)
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
        """Test that foreign codepoints listed under a base are exactly the intentional cross-map set."""
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

    def testValuesAreSequencesOfBaseCharacters(self):
        """Test that every character in every replacement is a base key of URDU_VARIANT_MAP."""
        for ligature, replacement in LIGATURE_MAP.items():
            assert replacement, (
                f"replacement for {ligature!r} (U+{ord(ligature):04X}) must not be empty"
            )
            for char in replacement:
                assert char in URDU_VARIANT_MAP, (
                    f"{char!r} (U+{ord(char):04X}) in the replacement for "
                    f"{ligature!r} (U+{ord(ligature):04X}) is not a URDU_VARIANT_MAP base key"
                )


# ******************************************************************************
