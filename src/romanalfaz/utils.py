# -*- coding: utf-8 -*-
# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
This module contains the normalization functions for Urdu arabic-script
Unicode text.

Note:
    The module relies on the `unicodedataplus`_ for Unicode character properties.

..  _unicodedataplus: https://pypi.org/project/unicodedataplus/

"""
# ******************************************************************************
import unicodedataplus as ud

# ******************************************************************************
# URDU VARIANT MAP START
URDU_VARIANT_MAP: dict[str, list[str]] = {
    # ALIF (ا)
    '\u0627': [
        '\u0627',  # ARABIC LETTER ALIF
        '\uFE8D',  # ARABIC LETTER ALIF ISOLATED FORM
        '\uFE8E',  # ARABIC LETTER ALIF FINAL FORM
    ],
    # ALEF MADDA (آ)
    '\u0622': [
        '\u0622',  # ARABIC LETTER ALEF WITH MADDA ABOVE
        '\uFE81',  # ALEF WITH MADDA ABOVE ISOLATED FORM
        '\uFE82',  # ALEF WITH MADDA ABOVE FINAL FORM
    ],
    # BE (ب)
    '\u0628': [
        '\u0628',  # ARABIC LETTER BE
        '\uFE8F',  # ARABIC LETTER BE ISOLATED FORM
        '\uFE90',  # ARABIC LETTER BE FINAL FORM
        '\uFE91',  # ARABIC LETTER BE INITIAL FORM
        '\uFE92',  # ARABIC LETTER BE MEDIAL FORM
    ],
    # PE (پ)
    '\u067E': [
        '\u067E',  # ARABIC LETTER PE
        '\uFB56',  # ARABIC LETTER PE ISOLATED FORM
        '\uFB57',  # ARABIC LETTER PE FINAL FORM
        '\uFB58',  # ARABIC LETTER PE INITIAL FORM
        '\uFB59',  # ARABIC LETTER PE MEDIAL FORM
    ],
    # TE (ت)
    '\u062A': [
        '\u062A',  # ARABIC LETTER TE
        '\uFE95',  # ARABIC LETTER TE ISOLATED FORM
        '\uFE96',  # ARABIC LETTER TE FINAL FORM
        '\uFE97',  # ARABIC LETTER TE INITIAL FORM
        '\uFE98',  # ARABIC LETTER TE MEDIAL FORM
    ],
    # TTE (ٹ)
    '\u0679': [
        '\u0679',  # ARABIC LETTER TTE
        '\uFB66',  # ARABIC LETTER TTE ISOLATED FORM
        '\uFB67',  # ARABIC LETTER TTE FINAL FORM
        '\uFB68',  # ARABIC LETTER TTE INITIAL FORM
        '\uFB69',  # ARABIC LETTER TTE MEDIAL FORM
    ],
    # SE (ث)
    '\u062B': [
        '\u062B',  # ARABIC LETTER THE
        '\uFE99',  # ARABIC LETTER THE ISOLATED FORM
        '\uFE9A',  # ARABIC LETTER THE FINAL FORM
        '\uFE9B',  # ARABIC LETTER THE INITIAL FORM
        '\uFE9C',  # ARABIC LETTER THE MEDIAL FORM
    ],
    # JEEM (ج)
    '\u062C': [
        '\u062C',  # ARABIC LETTER JEEM
        '\uFE9D',  # ARABIC LETTER JEEM ISOLATED FORM
        '\uFE9E',  # ARABIC LETTER JEEM FINAL FORM
        '\uFE9F',  # ARABIC LETTER JEEM INITIAL FORM
        '\uFEA0',  # ARABIC LETTER JEEM MEDIAL FORM
    ],
    # CHE (چ)
    '\u0686': [
        '\u0686',  # ARABIC LETTER CHE
        '\uFB7A',  # ARABIC LETTER CHE ISOLATED FORM
        '\uFB7B',  # ARABIC LETTER CHE FINAL FORM
        '\uFB7C',  # ARABIC LETTER CHE INITIAL FORM
        '\uFB7D',  # ARABIC LETTER CHE MEDIAL FORM
    ],
    # BARI HE (ح)
    '\u062D': [
        '\u062D',  # ARABIC LETTER HAA
        '\uFEA1',  # ARABIC LETTER HAA ISOLATED FORM
        '\uFEA2',  # ARABIC LETTER HAA FINAL FORM
        '\uFEA3',  # ARABIC LETTER HAA INITIAL FORM
        '\uFEA4',  # ARABIC LETTER HAA MEDIAL FORM
    ],
    # KHE (خ)
    '\u062E': [
        '\u062E',  # ARABIC LETTER KHAA
        '\uFEA5',  # ARABIC LETTER KHAA ISOLATED FORM
        '\uFEA6',  # ARABIC LETTER KHAA FINAL FORM
        '\uFEA7',  # ARABIC LETTER KHAA INITIAL FORM
        '\uFEA8',  # ARABIC LETTER KHAA MEDIAL FORM
    ],
    # DAL (د)
    '\u062F': [
        '\u062F',  # ARABIC LETTER DAL
        '\uFEA9',  # ARABIC LETTER DAL ISOLATED FORM
        '\uFEAA',  # ARABIC LETTER DAL FINAL FORM
    ],
    # DDAL (ڈ)
    '\u0688': [
        '\u0688',  # ARABIC LETTER DDAL
        '\uFB88',  # ARABIC LETTER DDAL ISOLATED FORM
        '\uFB89',  # ARABIC LETTER DDAL FINAL FORM
    ],
    # ZAL (ذ)
    '\u0630': [
        '\u0630',  # ARABIC LETTER THAL
        '\uFEAB',  # ARABIC LETTER THAL ISOLATED FORM
        '\uFEAC',  # ARABIC LETTER THAL FINAL FORM
    ],
    # RE (ر)
    '\u0631': [
        '\u0631',  # ARABIC LETTER REH
        '\uFEAD',  # ARABIC LETTER REH ISOLATED FORM
        '\uFEAE',  # ARABIC LETTER REH FINAL FORM
    ],
    # RRE (ڑ)
    '\u0691': [
        '\u0691',  # ARABIC LETTER RREH
        '\uFB8C',  # ARABIC LETTER RREH ISOLATED FORM
        '\uFB8D',  # ARABIC LETTER RREH FINAL FORM
    ],
    # ZE (ز)
    '\u0632': [
        '\u0632',  # ARABIC LETTER ZAIN
        '\uFEAF',  # ARABIC LETTER ZAIN ISOLATED FORM
        '\uFEB0',  # ARABIC LETTER ZAIN FINAL FORM
    ],
    # ZHE (ژ)
    '\u0698': [
        '\u0698',  # ARABIC LETTER JEH
        '\uFB8A',  # ARABIC LETTER JEH ISOLATED FORM
        '\uFB8B',  # ARABIC LETTER JEH FINAL FORM
    ],
    # SEEN (س)
    '\u0633': [
        '\u0633',  # ARABIC LETTER SEEN
        '\uFEB1',  # ARABIC LETTER SEEN ISOLATED FORM
        '\uFEB2',  # ARABIC LETTER SEEN FINAL FORM
        '\uFEB3',  # ARABIC LETTER SEEN INITIAL FORM
        '\uFEB4',  # ARABIC LETTER SEEN MEDIAL FORM
    ],
    # SHEEN (ش)
    '\u0634': [
        '\u0634',  # ARABIC LETTER SHEEN
        '\uFEB5',  # ARABIC LETTER SHEEN ISOLATED FORM
        '\uFEB6',  # ARABIC LETTER SHEEN FINAL FORM
        '\uFEB7',  # ARABIC LETTER SHEEN INITIAL FORM
        '\uFEB8',  # ARABIC LETTER SHEEN MEDIAL FORM
    ],
    # SUAD (ص)
    '\u0635': [
        '\u0635',  # ARABIC LETTER SAD
        '\uFEB9',  # ARABIC LETTER SAD ISOLATED FORM
        '\uFEBA',  # ARABIC LETTER SAD FINAL FORM
        '\uFEBB',  # ARABIC LETTER SAD INITIAL FORM
        '\uFEBC',  # ARABIC LETTER SAD MEDIAL FORM
    ],
    # ZUAD (ض)
    '\u0636': [
        '\u0636',  # ARABIC LETTER DAD
        '\uFEBD',  # ARABIC LETTER DAD ISOLATED FORM
        '\uFEBE',  # ARABIC LETTER DAD FINAL FORM
        '\uFEBF',  # ARABIC LETTER DAD INITIAL FORM
        '\uFEC0',  # ARABIC LETTER DAD MEDIAL FORM
    ],
    # TO'E (ط)
    '\u0637': [
        '\u0637',  # ARABIC LETTER TAH
        '\uFEC1',  # ARABIC LETTER TAH ISOLATED FORM
        '\uFEC2',  # ARABIC LETTER TAH FINAL FORM
        '\uFEC3',  # ARABIC LETTER TAH INITIAL FORM
        '\uFEC4',  # ARABIC LETTER TAH MEDIAL FORM
    ],
    # ZO'E (ظ)
    '\u0638': [
        '\u0638',  # ARABIC LETTER ZAH
        '\uFEC5',  # ARABIC LETTER ZAH ISOLATED FORM
        '\uFEC6',  # ARABIC LETTER ZAH FINAL FORM
        '\uFEC7',  # ARABIC LETTER ZAH INITIAL FORM
        '\uFEC8',  # ARABIC LETTER ZAH MEDIAL FORM
    ],
    # AIN (ع)
    '\u0639': [
        '\u0639',  # ARABIC LETTER AIN
        '\uFEC9',  # ARABIC LETTER AIN ISOLATED FORM
        '\uFECA',  # ARABIC LETTER AIN FINAL FORM
        '\uFECB',  # ARABIC LETTER AIN INITIAL FORM
        '\uFECC',  # ARABIC LETTER AIN MEDIAL FORM
    ],
    # GHAIN (غ)
    '\u063A': [
        '\u063A',  # ARABIC LETTER GHAIN
        '\uFECD',  # ARABIC LETTER GHAIN ISOLATED FORM
        '\uFECE',  # ARABIC LETTER GHAIN FINAL FORM
        '\uFECF',  # ARABIC LETTER GHAIN INITIAL FORM
        '\uFED0',  # ARABIC LETTER GHAIN MEDIAL FORM
    ],
    # FE (ف)
    '\u0641': [
        '\u0641',  # ARABIC LETTER FE
        '\uFED1',  # ARABIC LETTER FE ISOLATED FORM
        '\uFED2',  # ARABIC LETTER FE FINAL FORM
        '\uFED3',  # ARABIC LETTER FE INITIAL FORM
        '\uFED4',  # ARABIC LETTER FE MEDIAL FORM
    ],
    # QAF (ق)
    '\u0642': [
        '\u0642',  # ARABIC LETTER QAF
        '\uFED5',  # ARABIC LETTER QAF ISOLATED FORM
        '\uFED6',  # ARABIC LETTER QAF FINAL FORM
        '\uFED7',  # ARABIC LETTER QAF INITIAL FORM
        '\uFED8',  # ARABIC LETTER QAF MEDIAL FORM
    ],
    # URDU KAF (ک)
    '\u06A9': [
        # Urdu/Persian Keheh (ک)
        '\u06A9',  # ARABIC LETTER KEHEH
        '\uFB8E',  # ARABIC LETTER KEHEH ISOLATED FORM
        '\uFB8F',  # ARABIC LETTER KEHEH FINAL FORM
        '\uFB90',  # ARABIC LETTER KEHEH INITIAL FORM
        '\uFB91',  # ARABIC LETTER KEHEH MEDIAL FORM
        # Arabic Kaf (ك)
        '\u0643',  # ARABIC LETTER KAF
        '\uFED9',  # ARABIC LETTER KAF ISOLATED FORM
        '\uFEDA',  # ARABIC LETTER KAF FINAL FORM
        '\uFEDB',  # ARABIC LETTER KAF INITIAL FORM
        '\uFEDC',  # ARABIC LETTER KAF MEDIAL FORM
        # Old Persian / Swash Kaf (ݢ)
        '\u06A8',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE
        '\uFB96',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE ISOLATED FORM
        '\uFB97',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE FINAL FORM
        '\uFB98',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE INITIAL FORM
        '\uFB99',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE MEDIAL FORM
    ],
    # GAF (گ)
    '\u06AF': [
        '\u06AF',  # ARABIC LETTER GAF
        '\uFB92',  # ARABIC LETTER GAF ISOLATED FORM
        '\uFB93',  # ARABIC LETTER GAF FINAL FORM
        '\uFB94',  # ARABIC LETTER GAF INITIAL FORM
        '\uFB95',  # ARABIC LETTER GAF MEDIAL FORM
    ],
    # LAM (ل)
    '\u0644': [
        '\u0644',  # ARABIC LETTER LAM
        '\uFEDD',  # ARABIC LETTER LAM ISOLATED FORM
        '\uFEDE',  # ARABIC LETTER LAM FINAL FORM
        '\uFEDF',  # ARABIC LETTER LAM INITIAL FORM
        '\uFEE0',  # ARABIC LETTER LAM MEDIAL FORM
    ],
    # MEEM (م)
    '\u0645': [
        '\u0645',  # ARABIC LETTER MEEM
        '\uFEE1',  # ARABIC LETTER MEEM ISOLATED FORM
        '\uFEE2',  # ARABIC LETTER MEEM FINAL FORM
        '\uFEE3',  # ARABIC LETTER MEEM INITIAL FORM
        '\uFEE4',  # ARABIC LETTER MEEM MEDIAL FORM
    ],
    # NOON (ن)
    '\u0646': [
        '\u0646',  # ARABIC LETTER NOON
        '\uFEE5',  # ARABIC LETTER NOON ISOLATED FORM
        '\uFEE6',  # ARABIC LETTER NOON FINAL FORM
        '\uFEE7',  # ARABIC LETTER NOON INITIAL FORM
        '\uFEE8',  # ARABIC LETTER NOON MEDIAL FORM
    ],
    # NOON GHUNNA (ں)
    '\u06BA': [
        '\u06BA',  # ARABIC LETTER NOON GHUNNA
        '\uFB9E',  # ARABIC LETTER NOON GHUNNA ISOLATED FORM
        '\uFB9F',  # ARABIC LETTER NOON GHUNNA FINAL FORM
    ],
    # WAO (و)
    '\u0648': [
        # Standard Wao
        '\u0648',  # ARABIC LETTER WAW
        '\uFEED',  # ARABIC LETTER WAW ISOLATED FORM
        '\uFEEE',  # ARABIC LETTER WAW FINAL FORM
        # Wao with Hamza (ؤ)
        '\u0624',  # ARABIC LETTER WAW WITH HAMZA ABOVE
        '\uFE85',  # ARABIC LETTER WAW WITH HAMZA ABOVE ISOLATED FORM
        '\uFE86',  # ARABIC LETTER WAW WITH HAMZA ABOVE FINAL FORM
    ],
    # HE GOAL (ہ)
    '\u06C1': [
        # Urdu Heh Goal (ہ)
        '\u06C1',  # ARABIC LETTER HEH GOAL
        '\uFBA6',  # ARABIC LETTER HEH GOAL ISOLATED FORM
        '\uFBA7',  # ARABIC LETTER HEH GOAL FINAL FORM
        '\uFBA8',  # ARABIC LETTER HEH GOAL INITIAL FORM
        '\uFBA9',  # ARABIC LETTER HEH GOAL MEDIAL FORM
        # Arabic Ha (ه)
        '\u0647',  # ARABIC LETTER HEH
        '\uFEE9',  # ARABIC LETTER HEH ISOLATED FORM
        '\uFEEA',  # ARABIC LETTER HEH FINAL FORM
        '\uFEEB',  # ARABIC LETTER HEH INITIAL FORM
        '\uFEEC',  # ARABIC LETTER HEH MEDIAL FORM
        # Heh with Hamza variants (ۂ)
        '\u06C2',  # ARABIC LETTER HEH GOAL WITH HAMZA ABOVE
        '\u06C0',  # ARABIC LETTER HEH WITH YEH ABOVE
        # Te Marbuta (ة)
        '\u0629',  # ARABIC LETTER TE MARBUTA
        '\uFE93',  # ARABIC LETTER TE MARBUTA ISOLATED FORM
        '\uFE94',  # ARABIC LETTER TE MARBUTA FINAL FORM
    ],
    # TEH MARBUTA GOAL (ۃ)
    '\u06C3': [
        # Base Character
        '\u06C3',  # ARABIC LETTER TEH MARBUTA GOAL (Urdu/Sindhi variant)
        # Standard Arabic Equivalents (For Cross-Dialect Search/Matching)
        '\u0629',  # ARABIC LETTER TEH MARBUTA (ة)
        '\uFE93',  # ARABIC LETTER TEH MARBUTA ISOLATED FORM (ﺓ)
        '\uFE94',  # ARABIC LETTER TEH MARBUTA FINAL FORM (ﺔ)
    ],
    # DO CHASHMI HE (ھ)
    '\u06BE': [
        '\u06BE',  # ARABIC LETTER HEH DOACHASHMEE
        '\uFBAC',  # ARABIC LETTER HEH DOACHASHMEE ISOLATED FORM
        '\uFBAD',  # ARABIC LETTER HEH DOACHASHMEE FINAL FORM
        '\uFBAE',  # ARABIC LETTER HEH DOACHASHMEE INITIAL FORM
        '\uFBAF',  # ARABIC LETTER HEH DOACHASHMEE MEDIAL FORM
    ],
    # CHOTI YE / FARSI YEH / ARABIC YEH (ی / ي)
    '\u06CC': [
        # Urdu/Farsi Standard (ی)
        '\u06CC',  # ARABIC LETTER FARSI YEH
        '\uFBFB',  # ARABIC LETTER FARSI YEH ISOLATED FORM
        '\uFBFC',  # ARABIC LETTER FARSI YEH FINAL FORM
        '\uFBFD',  # ARABIC LETTER FARSI YEH INITIAL FORM
        '\uFBFE',  # ARABIC LETTER FARSI YEH MEDIAL FORM
        # Arabic/Sindhi Standard (ي)
        '\u064A',  # ARABIC LETTER YEH
        '\uFEF1',  # ARABIC LETTER YEH ISOLATED FORM
        '\uFEF2',  # ARABIC LETTER YEH FINAL FORM
        '\uFEF3',  # ARABIC LETTER YEH INITIAL FORM
        '\uFEF4',  # ARABIC LETTER YEH MEDIAL FORM
        # Alef Maksura (ى)
        '\u0649',  # ARABIC LETTER ALEF MAKSURA
        '\uEEF1',  # ARABIC LETTER ALEF MAKSURA ISOLATED FORM
        '\uEEF2',  # ARABIC LETTER ALEF MAKSURA FINAL FORM
    ],
    '\u0626': [ # Yeh with Hamza (ئ) - Common compositional variant
        '\u0626',  # ARABIC LETTER YEH WITH HAMZA ABOVE
        '\uFE8B',  # ARABIC LETTER YEH WITH HAMZA ABOVE INITIAL FORM
        '\uFE8C',  # ARABIC LETTER YEH WITH HAMZA ABOVE MEDIAL FORM
        '\uFE89',  # ARABIC LETTER YEH WITH HAMZA ABOVE ISOLATED FORM
        '\uFE8A',  # ARABIC LETTER YEH WITH HAMZA ABOVE FINAL FORM
    ],
    # BARI YE (ے)
    '\u06D2': [
        '\u06D2',  # ARABIC LETTER YEH BARREE
        '\uFBAE',  # ARABIC LETTER YEH BARREE ISOLATED FORM
        '\uFBAF',  # ARABIC LETTER YEH BARREE FINAL FORM
        '\u06D3',  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    ],
    # KASHEEDA / TATWEEL (ـ)
    # Mapping to empty string is a common way to 'strip' it during normalization
    '': [
        '\u0640',  # ARABIC TATWEEL
    ],
}
# URDU VARIANT MAP END
"""
Urdu Unicode base characters map to their positional and combinational variants.

This mapping defines which characters are retained during text normalization for processing, 
effectively filtering out visual representations.
"""

# LIGATURE MAP START
LIGATURE_MAP: dict[str, str] = {
    '\uFEFB': '\u0644\u0627',  # LAM WITH ALEF ISOLATED -> ل + ا
    '\uFEFC': '\u0644\u0627',  # LAM WITH ALEF FINAL -> ل + ا
    '\uFEF5': '\u0644\u0622',  # LAM WITH ALEF MADDA ISOLATED -> ل + آ
    '\uFEF6': '\u0644\u0622',  # LAM WITH ALEF MADDA FINAL -> ل + آ
}
# LIGATURE MAP END
"""Urdu ligature mapping to base characters."""

URDU_VARIANT_REVERSAL_MAP: dict[str, str] = {
    v: base for base, variants in URDU_VARIANT_MAP.items() for v in variants
}
"""
Urdu Unicode reverse lookup map from positional and combinational variants to base characters.

This is automatically generated from the `URDU_VARIANT_MAP`. It is used to
normalize the input text for subsequent processing.
"""

# ******************************************************************************
def normalize(text: str) -> str:
    """
    Performs a comprehensive normalization of the input string.

    This function applies a multistep pipeline to clean and standardize text data:

    1. Strips leading/trailing whitespace using :py:func:`strip`.
    2. Normalizes specific characters via :py:func:`romanalfaz.utils.normalizeUrduChars`.
    3. Removes non-alphanumeric marks, digits, and punctuation via :py:func:`romanalfaz.utils.normalizeNonChars`.
    4. Finally, normalizes all internal whitespace sequences to a single `space` using
       :py:func:`romanalfaz.utils.normalizeWhiteSpace`.

    The goal is to produce a clean string containing primarily letters and single spaces
    between words,  for further processing or comparison.

    Args:
        text (str): The input string to be normalized.

    Returns:
        str: A fully normalized string with standardized characters and spacing.

    Raises:
        AssertionError: If the input `text` is not a ``str`` instance.

    Example:
        >>> text = "  Café! 123   "
        >>> normalize(text)
        'Cafe'

        >>> text = "Hello World"
        >>> normalize(text)
        'Hello World'
    """
    # Guard Clause: Validate input type and content before processing.
    # Ensures the function only accepts non-empty strings to prevent errors downstream.
    assert isinstance(text, str), f"Input must be a string, got {type(text)}"

    if not text:
        # Return an empty string immediately if the input is None or empty.
        return ""

    # Pipeline execution: Apply normalization steps in sequence.
    # 1. strip(): Removes leading/trailing whitespace to avoid processing it as content.
    # 2. normalizeUrduChars(): Handles specific character encoding issues (e.g., Urdu).
    # 3. normalizeNonChars(): Cleans the text by removing marks, digits, and punctuation.
    # 4. normalizeWhiteSpace(): Collapses multiple spaces into single spaces for readability.
    return normalizeWhiteSpace(removeNonLetterChars(normalizeUrduChars(text.strip())))


# ******************************************************************************
def normalizeUrduChars(text: str) -> str:
    """
    Normalizes Urdu text by converting various character forms into their base representations.

    This function processes input text to handle:

      #. Multi-character ligatures (e.g., combining characters that look like single glyphs).
      #. Positional variants (initial, medial, final, isolated forms) mapped back to base characters.

    The output is a string containing only the standard base Urdu characters .

    Args:
        text (str): The input string potentially containing ligatures or positional variants.

    Returns:
        str: A normalized string with all Urdu-specific forms converted to base characters.

    Raises:
        AssertionError: If the input `text` is not a ``str`` instance.
    """
    # Guard Clause: Validate input type and content before processing.
    # Ensures the function only accepts non-empty strings to prevent errors downstream.
    assert isinstance(text, str), f"Input must be a string, got {type(text)}"

    if not text:
        # Return an empty string immediately if the input is None or empty.
        return ""

    # Step 1: Handle Multi-character Ligatures
    # LIGATURE_MAP is a dictionary where keys are multi-character sequences
    # (e.g., "شہ") and values are the single base character they represent (e.g., "ش").
    # We iterate through each pair and replace occurrences in the text.
    for ligature, replacement in LIGATURE_MAP.items():
        text = text.replace(ligature, replacement)

    # Step 2: Handle 1-to-1 Character Variants using map()
    # URDU_VARIANT_REVERSAL_MAP maps specific Unicode code points (like initial/medial forms)
    # to their base character. For example, it might map the 'initial' form of 'ا'
    # back to the standard 'ا'.
    #
    # The lambda function applies this lookup to every single character in the string:
    # - If a character exists in URDU_VARIANT_REVERSAL_MAP, replace it with its base form.
    # - If not (e.g., spaces, punctuation, or other scripts), keep the original character
    #   using .get(c, c). This ensures non-Urdu characters are preserved unchanged.
    text = "".join(map(lambda c: URDU_VARIANT_REVERSAL_MAP.get(c, c), text))

    return text


# ******************************************************************************
def normalizeWhiteSpace(text: str) -> str:
    """
    Normalizes whitespace in a string by removing all extra spaces and ensuring
    single spaces between words.

    This function collapses multiple consecutive spaces (including tabs, newlines,
    and other whitespace characters) into a single space. It also removes leading
    and trailing whitespace from the input string.

    Args:
        text (str): The input string containing irregular or excessive whitespace.

    Returns:
        str: A normalized string with consistent single spaces between words
        and no leading/trailing whitespace. If the input is ``None``, returns an empty string.

    Raises:
        AssertionError: If the input `text` is not a ``str`` instance.

    Examples:
        >>> normalizeWhiteSpace("  Hello   World  ")
        "Hello World"
        >>> normalizeWhiteSpace("Line1\\nLine2")
        "Line1 Line2"
        >>> normalizeWhiteSpace("")
        ""
    """
    # Guard Clause: Validate input type and content before processing.
    # Ensures the function only accepts non-empty strings to prevent errors downstream.
    assert isinstance(text, str), f"Input must be a string, got {type(text)}"

    if not text:
        # Return an empty string immediately if the input is None or empty.
        return ""

    # Split the string into tokens based on any whitespace character.
    # The .split() method (without arguments) automatically
    # handles all types of whitespace (spaces, tabs, newlines, etc.) and treats
    # consecutive whitespace as a single separator. It also strips leading/trailing
    # whitespace by default. Then join the tokens back together with a single space.
    # This reconstructs the string ensuring exactly one space between words.
    return " ".join(text.split())


# ******************************************************************************
def removeNonLetterChars(text: str) -> str:
    """
    Removes marks, digits, punctuation, symbols and control chars based on Unicode category.

    This function removes special marks (e.g., accents or diacritics),
    all numeric digits, all Punctuation, Symbols, and Control characters.
    The result is a string containing only alphanumeric letters and
    whitespace (if any).

    Args:
        text (str): The input string to be normalized.

    Returns:
        str: A new string with marks, digits, and punctuation removed.
        If the input is invalid or empty, returns an empty string.

    Raises:
        AssertionError: If the input `text` is not a ``str`` instance.

    Example:
        >>> removeNonLetterChars("سلام! (Hello, World?) [ایک] #Urdu @Script۔")
        'سلام Hello World ایک Urdu Script'
    """
    # Guard Clause: Validate input type and content before processing.
    assert isinstance(text, str), f"Input must be a string, got {type(text)}"

    if not text:
        return ""

    # Step 1: Remove diacritics/marks using the `removeMarks` helper function.
    # This cleans characters like accents (é -> e) or combining marks.
    cleanedText = removeMarks(text)

    # Step 2: Remove Digits, Punctuation (P), Symbols (S), and Control chars (C).
    return ''.join([c for c in cleanedText if not ud.category(c).startswith(('C', 'P', 'S', 'Nd'))])


# ******************************************************************************
def removeMarks(text: str) -> str:
    """
    Removes all diacritical marks (combining characters) from Urdu text while preserving
    specific essential marks.

    This function uses Unicode Normalization Form Decomposition (NFD) to separate base
    characters from their combining diacritics. It then filters out unwanted marks and
    recomposes the string using Normalization Form Composition (NFC).

    The function specifically preserves:

      - U+0653 (Madda): For the letter 'آ' (A with Madda).
      - U+0654 (Hamza Above): For the letter 'ئ' (Yeh with Hamza above).

    Other combining characters (like shadda, fatha, kasra, etc.) are removed.

    Args:
        text (str): The input string containing Urdu text with potential diacritics.

    Returns:
        str: A normalized string where unnecessary diacritical marks have been removed,
        but essential structural marks for specific letters remain intact.

    Raises:
        AssertionError: If the input `text` is not a ``str`` instance.

    Examples:
        >>> removeMarks("مُحَمَّدٌ")
        'محمد'
        >>> removeMarks("قُرْآن")
        'قرآن'
        >>> removeMarks("آئینہ")
        'آئینہ'
    """
    # Guard Clause: Validate input type and content before processing.
    # Ensures the function only accepts non-empty strings to prevent errors downstream.
    assert isinstance(text, str), f"Input must be a string, got {type(text)}"

    if not text:
        # Return an empty string immediately if the input is None or empty.
        return ""

    # Step 1: Define Preserved Marks
    # We explicitly list the Unicode characters that must remain even though they are
    # technically combining marks (or specific base forms in some contexts).
    # These are critical for displaying 'آ' and 'ئ' correctly without relying solely on
    # base character normalization.
    preservedMarks = {'\u0653', '\u0654'}

    # Step 2: Normalize to NFD (Normalization Form Decomposition)
    # NFD breaks down characters into their constituent parts: the base character + any
    # combining marks (diacritics). For example, 'آ' becomes [Base 'ا', Combining Madda].
    nfdForm = ud.normalize('NFD', text)

    # Step 3: Filter Characters
    # We iterate through each character in the decomposed string and apply two conditions:
    # 1. Keep if it is one of our explicitly preserved marks (Madda or Hamza Above).
    # 2. Keep if it is NOT a combining character (ud.combining(c) returns True for diacritics).
    # This effectively removes all other diacritical marks while keeping the base letters
    # and the essential structural marks.
    token = "".join([c for c in nfdForm if c in preservedMarks or not ud.combining(c)])

    # Step 4: Normalize to NFC (Normalization Form Composition)
    # The filtered string is now a mix of base characters and preserved marks.
    # We re-compose them into NFC form to ensure the output is a valid, standard Unicode
    # string where necessary ligatures are formed correctly for display purposes.
    return ud.normalize('NFC', token)


# ******************************************************************************
