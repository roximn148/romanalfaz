# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
import pytest
from romanalfaz.utils import (
    removeMarks, removeNonLetterChars, normalizeUrduChars,
    LIGATURE_MAP, URDU_VARIANT_REVERSAL_MAP
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
            testLigature = list(LIGATURE_MAP.keys())[0]
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
            testVariant = list(URDU_VARIANT_REVERSAL_MAP.keys())[0]
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
            ligatureKey = list(LIGATURE_MAP.keys())[0]
            inputText += f" {ligatureKey}"
            expectedOutput += f" {LIGATURE_MAP[ligatureKey]}"

        if URDU_VARIANT_REVERSAL_MAP:
            variantKey = list(URDU_VARIANT_REVERSAL_MAP.keys())[0]
            inputText += f" {variantKey}"
            expectedOutput += f" {URDU_VARIANT_REVERSAL_MAP[variantKey]}"

        assert normalizeUrduChars(inputText) == expectedOutput

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
