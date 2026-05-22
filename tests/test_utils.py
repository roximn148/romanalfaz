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
def test_removeMarks_empty_string():
    """Test that an empty string input returns an empty string."""
    assert removeMarks("") == ""

def test_removeMarks_latin_text_no_diacritics():
    """Test that standard Latin text with punctuation remains completely unchanged."""
    text = "Hello, World! 123 @#$"
    assert removeMarks(text) == text

def test_removeMarks_mixed_latin_urdu_no_diacritics():
    """Test mixed Latin and Urdu text without any diacritical marks."""
    text = "Python (پائتھون) is a language!"
    assert removeMarks(text) == text

def test_removeMarks_urdu_standard_diacritics_removed():
    """Test removal of standard Urdu diacritics like fatha, kasra, damma, and shadda."""
    # مُحَمَّدٌ with damma, fatha, shadda, dammatan
    input_text = "\u0645\u064f\u062d\u064e\u0645\u0651\u064e\u062f\u064c"
    # محمد (base characters remaining)
    expected_output = "\u0645\u062d\u0645\u062f"
    assert removeMarks(input_text) == expected_output

def test_removeMarks_preserve_madda():
    """Test that Madda (U+0653) on Alif (آ) is strictly preserved."""
    # Alif with Madda
    text = "آفتاب"
    assert removeMarks(text) == text

def test_removeMarks_preserve_hamza_above():
    """Test that Hamza Above (U+0654) on Yeh (ئ) is strictly preserved."""
    # Yeh with Hamza Above
    text = "آئینہ"
    assert removeMarks(text) == text

def test_removeMarks_mixed_diacritics_retention_and_removal():
    """Test a complex mix where some marks are removed and essential ones are kept."""
    # قُرْآن - contains damma (remove), sukun (remove), and madda (keep)
    input_text = "\u0642\u064f\u0631\u0652\u0622\u0646"
    expected_output = "قرآن"
    assert removeMarks(input_text) == expected_output

def test_removeMarks_latin_diacritics_removed():
    """Test that Latin combining diacritics (like French é or Spanish ñ) are stripped."""
    # decomposed 'é' (e + combining acute accent) and 'ñ' (n + combining tilde)
    input_text = "café niñO"
    expected_output = "cafe ninO"
    assert removeMarks(input_text) == expected_output

def test_removeMarks_mixed_script_chaos():
    """Test a highly mixed string with Latin, Urdu, symbols, numbers, and multiple diacritics."""
    # 'بَ' (ba + fatha -> remove fatha), 'آ' (keep), Latin symbols, 'é' (remove accent)
    input_text = "بَ !@# 123 آ café"
    expected_output = "ب !@# 123 آ cafe"
    assert removeMarks(input_text) == expected_output

def test_removeMarks_invalid_input_type_raises_assertion_error():
    """Test that passing a non-string object correctly raises an AssertionError."""
    with pytest.raises(AssertionError) as exc_info:
        removeMarks(12345)
    assert "Input must be a string" in str(exc_info.value)

def test_removeMarks_none_input_raises_assertion_error():
    """Test that passing None correctly triggers the type guard clause."""
    with pytest.raises(AssertionError):
        removeMarks(None)


# ******************************************************************************
def test_normalizeNonChars_empty_string():
    """Test that an empty string input returns an empty string."""
    assert removeNonLetterChars("") == ""

def test_normalizeNonChars_clean_alphabetic_text_preserved():
    """Test that pure alphabetic Latin and Urdu text without non-characters remains intact."""
    text = "Hello ایک لفظ"
    assert removeNonLetterChars(text) == text

def test_normalizeNonChars_punctuation_and_symbols_removed():
    """Test that Latin, Urdu, and symbolic punctuation are completely removed."""
    input_text = "سلام! (Hello, World?) [ایک] #Urdu @Script۔"
    expected_output = "سلام Hello World ایک Urdu Script"
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_digits_removed():
    """Test that both Latin and Urdu digits are successfully removed from the text."""
    input_text = "Page 123 صفحہ ۴۵۶"
    expected_output = "Page  صفحہ "
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_diacritics_removed_except_preserved():
    """Test that standard Urdu/Latin diacritics are stripped, while structural marks (Madda) remain."""
    # مُحَمَّدٌ (contains standard diacritics to remove) and قرآن (contains Madda to preserve)
    input_text = "\u0645\u064f\u062d\u064e\u0645\u0651\u064e\u062f\u064c قرآن café"
    expected_output = "محمد قرآن cafe"
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_control_characters_removed():
    """Test that control characters (\p{C}) like newlines, tabs, and null bytes are stripped."""
    input_text = "Urdu\nٹیکسٹ\tData\x00"
    expected_output = "UrduٹیکسٹData"
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_whitespace_preservation():
    """Test that standard spaces are preserved while consecutive punctuation separation leaves clean spaces."""
    input_text = "Word1,,,   Word2!!!   لفظ۳"
    expected_output = "Word   Word   لفظ"
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_chaos_mixed_script_boundary_case():
    """Test a chaotic boundary string mixing Latin, Urdu, math symbols, numbers, and accents."""
    # "ٹیکسٹ! 786 + café = Best??" -> "ٹیکسٹ  cafe  Best"
    input_text = "ٹیکسٹ! 786 + café = Best??"
    expected_output = "ٹیکسٹ   cafe  Best"
    assert removeNonLetterChars(input_text) == expected_output

def test_normalizeNonChars_invalid_input_type_raises_assertion_error():
    """Test that passing a non-string object correctly triggers the type guard assertion."""
    with pytest.raises(AssertionError) as exc_info:
        removeNonLetterChars([1, 2, 3])
    assert "Input must be a string" in str(exc_info.value)

def test_normalizeNonChars_none_input_raises_assertion_error():
    """Test that passing None causes the type check guard clause to fail."""
    with pytest.raises(AssertionError):
        removeNonLetterChars(None)


# ******************************************************************************
def test_normalizeUrduChars_empty_string():
    """Test that an empty string input returns an empty string."""
    assert normalizeUrduChars("") == ""

def test_normalizeUrduChars_standard_text_remains_unchanged():
    """Test that standard Urdu text without ligatures or positional variants remains untouched."""
    # This test verifies behavior against the existing map contents
    text = "یہ ایک سادہ جملہ ہے۔"
    # The output should equal input if input contains no elements present in the maps
    assert normalizeUrduChars(text) == text

def test_normalizeUrduChars_latin_and_symbols_preserved():
    """Test that Latin text, digits, and symbols are entirely preserved and untouched."""
    text = "Python 3.10! @#$ [Test] alphanumeric text"
    assert normalizeUrduChars(text) == text

def test_normalizeUrduChars_multi_character_ligatures_replaced():
    """Test that keys present in LIGATURE_MAP are replaced by their mapped values if found in the input."""
    # We use a conditional check to find an available key from the pre-defined LIGATURE_MAP
    if LIGATURE_MAP:
        test_ligature = list(LIGATURE_MAP.keys())[0]
        expected_replacement = LIGATURE_MAP[test_ligature]

        input_text = f"ٹیکسٹ {test_ligature} 123"
        expected_output = f"ٹیکسٹ {expected_replacement} 123"
        assert normalizeUrduChars(input_text) == expected_output
    else:
        pytest.skip("LIGATURE_MAP is empty, skipping dynamic evaluation.")

def test_normalizeUrduChars_positional_variants_reversed():
    """Test that keys present in URDU_VARIANT_REVERSAL_MAP are mapped back to their base forms."""
    # We use a conditional check to find an available key from the pre-defined URDU_VARIANT_REVERSAL_MAP
    if URDU_VARIANT_REVERSAL_MAP:
        test_variant = list(URDU_VARIANT_REVERSAL_MAP.keys())[0]
        expected_base = URDU_VARIANT_REVERSAL_MAP[test_variant]

        input_text = f"ٹیکسٹ {test_variant} abc"
        expected_output = f"ٹیکسٹ {expected_base} abc"
        assert normalizeUrduChars(input_text) == expected_output
    else:
        pytest.skip("URDU_VARIANT_REVERSAL_MAP is empty, skipping dynamic evaluation.")

def test_mixed_chaos_ligatures_variants_and_latin():
    """Test a chaotic string mixing Latin elements, digits, and elements from both maps if populated."""
    input_text = "Urdu ٹیکسٹ 123 !@#"
    expected_output = "Urdu ٹیکسٹ 123 !@#"

    # Dynamically inject one item from each dictionary into the text to run a combined simulation
    if LIGATURE_MAP:
        ligature_key = list(LIGATURE_MAP.keys())[0]
        input_text += f" {ligature_key}"
        expected_output += f" {LIGATURE_MAP[ligature_key]}"

    if URDU_VARIANT_REVERSAL_MAP:
        variant_key = list(URDU_VARIANT_REVERSAL_MAP.keys())[0]
        input_text += f" {variant_key}"
        expected_output += f" {URDU_VARIANT_REVERSAL_MAP[variant_key]}"

    assert normalizeUrduChars(input_text) == expected_output

def test_normalizeUrduChars_invalid_input_type_raises_assertion_error():
    """Test that passing a non-string object correctly triggers the type guard validation."""
    with pytest.raises(AssertionError) as exc_info:
        normalizeUrduChars(98765)
    assert "Input must be a string" in str(exc_info.value)

def test_normalizeUrduChars_none_input_raises_assertion_error():
    """Test that passing None explicitly triggers the type assertion failure."""
    with pytest.raises(AssertionError):
        normalizeUrduChars(None)

# ******************************************************************************
