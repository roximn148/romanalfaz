# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""
The :py:mod:`romanalfaz.urduspell` module is the ``urdu-spell`` normalization
method: the normalization functions for Urdu arabic-script Unicode text.

In the broad sense, normalization is a mapping from a defined *Input Set* of
Unicode characters to a canonical *Output Set*: it reduces the many valid but variant
spellings of a word (positional and presentation forms, composed ligatures,
linguistic and formatting marks, and cross-lingual character substitutions)
to a single standard form suited to a fixed processing task. This module is
one concrete realization of that idea, scoped to the *Word Lookup* constraint
of the general problem: the expected input is already tokenized words of any
Unicode text content, and the output is normalized to the target Urdu language
for dictionary lookup.

Each defining element of that general problem is delegated to a dedicated
stage of the :py:func:`romanalfaz.urduspell.normalize` pipeline, so that no stage
performs another's work:

- **Positional Variants** and **Composition/Ligatures** are resolved by
  :py:func:`romanalfaz.urduspell.normalizeUrduChars`, which folds every positional
  and presentation form, and every composed ligature, back to its base
  character through :data:`romanalfaz.urduspell.URDU_VARIANT_MAP` and
  :data:`romanalfaz.urduspell.LIGATURE_MAP`.
- **Cross-Lingual Substitutions** are resolved by the same stage, which also
  folds non-Urdu base characters (e.g. U+0624) to their Urdu counterparts.
- **Marks (Linguistic and Formatting)** are stripped by
  :py:func:`romanalfaz.urduspell.removeMarks`, which removes every combining mark
  except the structural marks in :data:`romanalfaz.urduspell.PRESERVED_MARKS`;
  :py:func:`romanalfaz.urduspell.removeNonLetterChars` then discards the remaining
  non-letter residue (digits, punctuation, symbols, control characters).
- **Whitespace** is collapsed to single spaces by
  :py:func:`romanalfaz.urduspell.normalizeWhiteSpace`.

Note:
    The module relies on the `unicodedataplus`_ for Unicode character properties.

..  _unicodedataplus: https://pypi.org/project/unicodedataplus/

"""

# ******************************************************************************
import unicodedataplus as ud

# ******************************************************************************
# PRESERVED MARKS
PRESERVED_MARKS: set[str] = {
    "\u0653",  # ARABIC MADDAH ABOVE
    "\u0654",  # ARABIC HAMZA ABOVE
}
"""
The combining marks preserved by :py:func:`romanalfaz.urduspell.removeMarks`.

These are exactly the marks carried by the precomposed base characters that
:py:func:`romanalfaz.urduspell.normalizeUrduChars` retains (U+0622, ALEF WITH MADDA
ABOVE, and U+0626, YEH WITH HAMZA ABOVE). This exact fit is the contract
between the two stages: because the preserved marks survive the mark-stripping
step, :py:func:`romanalfaz.urduspell.removeMarks` is a net no-op on every base
character the map can output. See the Notes of
:py:func:`romanalfaz.urduspell.removeMarks` and
:py:func:`romanalfaz.urduspell.normalize`.
"""

# ******************************************************************************
# URDU VARIANT MAP START
URDU_VARIANT_MAP: dict[str, list[str]] = {
    # ALIF (ا)
    "\u0627": [
        "\u0627",  # ARABIC LETTER ALEF
        "\ufe8d",  # ARABIC LETTER ALEF ISOLATED FORM
        "\ufe8e",  # ARABIC LETTER ALEF FINAL FORM
    ],
    # ALIF MADDA (آ)
    "\u0622": [
        "\u0622",  # ARABIC LETTER ALEF WITH MADDA ABOVE
        "\ufe81",  # ARABIC LETTER ALEF WITH MADDA ABOVE ISOLATED FORM
        "\ufe82",  # ARABIC LETTER ALEF WITH MADDA ABOVE FINAL FORM
    ],
    # BE (ب)
    "\u0628": [
        "\u0628",  # ARABIC LETTER BEH
        "\ufe8f",  # ARABIC LETTER BEH ISOLATED FORM
        "\ufe90",  # ARABIC LETTER BEH FINAL FORM
        "\ufe91",  # ARABIC LETTER BEH INITIAL FORM
        "\ufe92",  # ARABIC LETTER BEH MEDIAL FORM
    ],
    # PE (پ)
    "\u067e": [
        "\u067e",  # ARABIC LETTER PEH
        "\ufb56",  # ARABIC LETTER PEH ISOLATED FORM
        "\ufb57",  # ARABIC LETTER PEH FINAL FORM
        "\ufb58",  # ARABIC LETTER PEH INITIAL FORM
        "\ufb59",  # ARABIC LETTER PEH MEDIAL FORM
    ],
    # TE (ت)
    "\u062a": [
        "\u062a",  # ARABIC LETTER TEH
        "\ufe95",  # ARABIC LETTER TEH ISOLATED FORM
        "\ufe96",  # ARABIC LETTER TEH FINAL FORM
        "\ufe97",  # ARABIC LETTER TEH INITIAL FORM
        "\ufe98",  # ARABIC LETTER TEH MEDIAL FORM
    ],
    # TTE (ٹ)
    "\u0679": [
        "\u0679",  # ARABIC LETTER TTEH
        "\ufb66",  # ARABIC LETTER TTEH ISOLATED FORM
        "\ufb67",  # ARABIC LETTER TTEH FINAL FORM
        "\ufb68",  # ARABIC LETTER TTEH INITIAL FORM
        "\ufb69",  # ARABIC LETTER TTEH MEDIAL FORM
    ],
    # SE (ث)
    "\u062b": [
        "\u062b",  # ARABIC LETTER THEH
        "\ufe99",  # ARABIC LETTER THEH ISOLATED FORM
        "\ufe9a",  # ARABIC LETTER THEH FINAL FORM
        "\ufe9b",  # ARABIC LETTER THEH INITIAL FORM
        "\ufe9c",  # ARABIC LETTER THEH MEDIAL FORM
    ],
    # JEEM (ج)
    "\u062c": [
        "\u062c",  # ARABIC LETTER JEEM
        "\ufe9d",  # ARABIC LETTER JEEM ISOLATED FORM
        "\ufe9e",  # ARABIC LETTER JEEM FINAL FORM
        "\ufe9f",  # ARABIC LETTER JEEM INITIAL FORM
        "\ufea0",  # ARABIC LETTER JEEM MEDIAL FORM
    ],
    # CHE (چ)
    "\u0686": [
        "\u0686",  # ARABIC LETTER TCHEH
        "\ufb7a",  # ARABIC LETTER TCHEH ISOLATED FORM
        "\ufb7b",  # ARABIC LETTER TCHEH FINAL FORM
        "\ufb7c",  # ARABIC LETTER TCHEH INITIAL FORM
        "\ufb7d",  # ARABIC LETTER TCHEH MEDIAL FORM
    ],
    # HE (ح)
    "\u062d": [
        "\u062d",  # ARABIC LETTER HAH
        "\ufea1",  # ARABIC LETTER HAH ISOLATED FORM
        "\ufea2",  # ARABIC LETTER HAH FINAL FORM
        "\ufea3",  # ARABIC LETTER HAH INITIAL FORM
        "\ufea4",  # ARABIC LETTER HAH MEDIAL FORM
    ],
    # KHE (خ)
    "\u062e": [
        "\u062e",  # ARABIC LETTER KHAH
        "\ufea5",  # ARABIC LETTER KHAH ISOLATED FORM
        "\ufea6",  # ARABIC LETTER KHAH FINAL FORM
        "\ufea7",  # ARABIC LETTER KHAH INITIAL FORM
        "\ufea8",  # ARABIC LETTER KHAH MEDIAL FORM
    ],
    # DAL (د)
    "\u062f": [
        "\u062f",  # ARABIC LETTER DAL
        "\ufea9",  # ARABIC LETTER DAL ISOLATED FORM
        "\ufeaa",  # ARABIC LETTER DAL FINAL FORM
    ],
    # DDAL (ڈ)
    "\u0688": [
        "\u0688",  # ARABIC LETTER DDAL
        "\ufb88",  # ARABIC LETTER DDAL ISOLATED FORM
        "\ufb89",  # ARABIC LETTER DDAL FINAL FORM
    ],
    # ZAL (ذ)
    "\u0630": [
        "\u0630",  # ARABIC LETTER THAL
        "\ufeab",  # ARABIC LETTER THAL ISOLATED FORM
        "\ufeac",  # ARABIC LETTER THAL FINAL FORM
    ],
    # RE (ر)
    "\u0631": [
        "\u0631",  # ARABIC LETTER REH
        "\ufead",  # ARABIC LETTER REH ISOLATED FORM
        "\ufeae",  # ARABIC LETTER REH FINAL FORM
    ],
    # RRE (ڑ)
    "\u0691": [
        "\u0691",  # ARABIC LETTER RREH
        "\ufb8c",  # ARABIC LETTER RREH ISOLATED FORM
        "\ufb8d",  # ARABIC LETTER RREH FINAL FORM
    ],
    # ZE (ز)
    "\u0632": [
        "\u0632",  # ARABIC LETTER ZAIN
        "\ufeaf",  # ARABIC LETTER ZAIN ISOLATED FORM
        "\ufeb0",  # ARABIC LETTER ZAIN FINAL FORM
    ],
    # ZHE (ژ)
    "\u0698": [
        "\u0698",  # ARABIC LETTER JEH
        "\ufb8a",  # ARABIC LETTER JEH ISOLATED FORM
        "\ufb8b",  # ARABIC LETTER JEH FINAL FORM
    ],
    # SEEN (س)
    "\u0633": [
        "\u0633",  # ARABIC LETTER SEEN
        "\ufeb1",  # ARABIC LETTER SEEN ISOLATED FORM
        "\ufeb2",  # ARABIC LETTER SEEN FINAL FORM
        "\ufeb3",  # ARABIC LETTER SEEN INITIAL FORM
        "\ufeb4",  # ARABIC LETTER SEEN MEDIAL FORM
    ],
    # SHEEN (ش)
    "\u0634": [
        "\u0634",  # ARABIC LETTER SHEEN
        "\ufeb5",  # ARABIC LETTER SHEEN ISOLATED FORM
        "\ufeb6",  # ARABIC LETTER SHEEN FINAL FORM
        "\ufeb7",  # ARABIC LETTER SHEEN INITIAL FORM
        "\ufeb8",  # ARABIC LETTER SHEEN MEDIAL FORM
    ],
    # SUAD (ص)
    "\u0635": [
        "\u0635",  # ARABIC LETTER SAD
        "\ufeb9",  # ARABIC LETTER SAD ISOLATED FORM
        "\ufeba",  # ARABIC LETTER SAD FINAL FORM
        "\ufebb",  # ARABIC LETTER SAD INITIAL FORM
        "\ufebc",  # ARABIC LETTER SAD MEDIAL FORM
    ],
    # ZUAD (ض)
    "\u0636": [
        "\u0636",  # ARABIC LETTER DAD
        "\ufebd",  # ARABIC LETTER DAD ISOLATED FORM
        "\ufebe",  # ARABIC LETTER DAD FINAL FORM
        "\ufebf",  # ARABIC LETTER DAD INITIAL FORM
        "\ufec0",  # ARABIC LETTER DAD MEDIAL FORM
    ],
    # TO'E (ط)
    "\u0637": [
        "\u0637",  # ARABIC LETTER TAH
        "\ufec1",  # ARABIC LETTER TAH ISOLATED FORM
        "\ufec2",  # ARABIC LETTER TAH FINAL FORM
        "\ufec3",  # ARABIC LETTER TAH INITIAL FORM
        "\ufec4",  # ARABIC LETTER TAH MEDIAL FORM
    ],
    # ZO'E (ظ)
    "\u0638": [
        "\u0638",  # ARABIC LETTER ZAH
        "\ufec5",  # ARABIC LETTER ZAH ISOLATED FORM
        "\ufec6",  # ARABIC LETTER ZAH FINAL FORM
        "\ufec7",  # ARABIC LETTER ZAH INITIAL FORM
        "\ufec8",  # ARABIC LETTER ZAH MEDIAL FORM
    ],
    # AIN (ع)
    "\u0639": [
        "\u0639",  # ARABIC LETTER AIN
        "\ufec9",  # ARABIC LETTER AIN ISOLATED FORM
        "\ufeca",  # ARABIC LETTER AIN FINAL FORM
        "\ufecb",  # ARABIC LETTER AIN INITIAL FORM
        "\ufecc",  # ARABIC LETTER AIN MEDIAL FORM
    ],
    # GHAIN (غ)
    "\u063a": [
        "\u063a",  # ARABIC LETTER GHAIN
        "\ufecd",  # ARABIC LETTER GHAIN ISOLATED FORM
        "\ufece",  # ARABIC LETTER GHAIN FINAL FORM
        "\ufecf",  # ARABIC LETTER GHAIN INITIAL FORM
        "\ufed0",  # ARABIC LETTER GHAIN MEDIAL FORM
    ],
    # FE (ف)
    "\u0641": [
        "\u0641",  # ARABIC LETTER FEH
        "\ufed1",  # ARABIC LETTER FEH ISOLATED FORM
        "\ufed2",  # ARABIC LETTER FEH FINAL FORM
        "\ufed3",  # ARABIC LETTER FEH INITIAL FORM
        "\ufed4",  # ARABIC LETTER FEH MEDIAL FORM
    ],
    # QAF (ق)
    "\u0642": [
        "\u0642",  # ARABIC LETTER QAF
        "\ufed5",  # ARABIC LETTER QAF ISOLATED FORM
        "\ufed6",  # ARABIC LETTER QAF FINAL FORM
        "\ufed7",  # ARABIC LETTER QAF INITIAL FORM
        "\ufed8",  # ARABIC LETTER QAF MEDIAL FORM
    ],
    # KAF (ک)
    "\u06a9": [
        # Urdu/Persian Kaf (ک)
        "\u06a9",  # ARABIC LETTER KEHEH
        "\ufb8e",  # ARABIC LETTER KEHEH ISOLATED FORM
        "\ufb8f",  # ARABIC LETTER KEHEH FINAL FORM
        "\ufb90",  # ARABIC LETTER KEHEH INITIAL FORM
        "\ufb91",  # ARABIC LETTER KEHEH MEDIAL FORM
        # Arabic Kaf (ك)
        "\u0643",  # ARABIC LETTER KAF
        "\ufed9",  # ARABIC LETTER KAF ISOLATED FORM
        "\ufeda",  # ARABIC LETTER KAF FINAL FORM
        "\ufedb",  # ARABIC LETTER KAF INITIAL FORM
        "\ufedc",  # ARABIC LETTER KAF MEDIAL FORM
        # Old Persian / Swash Kaf (ݢ) ??? :TODO: Review
        "\u06a8",  # ARABIC LETTER QAF WITH THREE DOTS ABOVE
        "\ufb96",  # ARABIC LETTER GUEH ISOLATED FORM
        "\ufb97",  # ARABIC LETTER GUEH FINAL FORM
        "\ufb98",  # ARABIC LETTER GUEH INITIAL FORM
        "\ufb99",  # ARABIC LETTER GUEH MEDIAL FORM
    ],
    # GAF (گ)
    "\u06af": [
        "\u06af",  # ARABIC LETTER GAF
        "\ufb92",  # ARABIC LETTER GAF ISOLATED FORM
        "\ufb93",  # ARABIC LETTER GAF FINAL FORM
        "\ufb94",  # ARABIC LETTER GAF INITIAL FORM
        "\ufb95",  # ARABIC LETTER GAF MEDIAL FORM
    ],
    # LAM (ل)
    "\u0644": [
        "\u0644",  # ARABIC LETTER LAM
        "\ufedd",  # ARABIC LETTER LAM ISOLATED FORM
        "\ufede",  # ARABIC LETTER LAM FINAL FORM
        "\ufedf",  # ARABIC LETTER LAM INITIAL FORM
        "\ufee0",  # ARABIC LETTER LAM MEDIAL FORM
    ],
    # MEEM (م)
    "\u0645": [
        "\u0645",  # ARABIC LETTER MEEM
        "\ufee1",  # ARABIC LETTER MEEM ISOLATED FORM
        "\ufee2",  # ARABIC LETTER MEEM FINAL FORM
        "\ufee3",  # ARABIC LETTER MEEM INITIAL FORM
        "\ufee4",  # ARABIC LETTER MEEM MEDIAL FORM
    ],
    # NOON (ن)
    "\u0646": [
        "\u0646",  # ARABIC LETTER NOON
        "\ufee5",  # ARABIC LETTER NOON ISOLATED FORM
        "\ufee6",  # ARABIC LETTER NOON FINAL FORM
        "\ufee7",  # ARABIC LETTER NOON INITIAL FORM
        "\ufee8",  # ARABIC LETTER NOON MEDIAL FORM
    ],
    # NOON GHUNNA (ں)
    "\u06ba": [
        "\u06ba",  # ARABIC LETTER NOON GHUNNA
        "\ufb9e",  # ARABIC LETTER NOON GHUNNA ISOLATED FORM
        "\ufb9f",  # ARABIC LETTER NOON GHUNNA FINAL FORM
    ],
    # WAO (و)
    "\u0648": [
        # Standard Wao
        "\u0648",  # ARABIC LETTER WAW
        "\ufeed",  # ARABIC LETTER WAW ISOLATED FORM
        "\ufeee",  # ARABIC LETTER WAW FINAL FORM
        # Wao with Hamza (ؤ)
        "\u0624",  # ARABIC LETTER WAW WITH HAMZA ABOVE
        "\ufe85",  # ARABIC LETTER WAW WITH HAMZA ABOVE ISOLATED FORM
        "\ufe86",  # ARABIC LETTER WAW WITH HAMZA ABOVE FINAL FORM
    ],
    # HE GOAL (ہ)
    "\u06c1": [
        # Urdu Heh Goal (ہ)
        "\u06c1",  # ARABIC LETTER HEH GOAL
        "\ufba6",  # ARABIC LETTER HEH GOAL ISOLATED FORM
        "\ufba7",  # ARABIC LETTER HEH GOAL FINAL FORM
        "\ufba8",  # ARABIC LETTER HEH GOAL INITIAL FORM
        "\ufba9",  # ARABIC LETTER HEH GOAL MEDIAL FORM
        # Arabic Ha (ه)
        "\u0647",  # ARABIC LETTER HEH
        "\ufee9",  # ARABIC LETTER HEH ISOLATED FORM
        "\ufeea",  # ARABIC LETTER HEH FINAL FORM
        "\ufeeb",  # ARABIC LETTER HEH INITIAL FORM
        "\ufeec",  # ARABIC LETTER HEH MEDIAL FORM
        # Heh with Hamza variants (ۂ)
        "\u06c2",  # ARABIC LETTER HEH GOAL WITH HAMZA ABOVE
        "\u06c0",  # ARABIC LETTER HEH WITH YEH ABOVE
        "\ufba4",  # ARABIC LETTER HEH WITH YEH ABOVE ISOLATED FORM
        "\ufba5",  # ARABIC LETTER HEH WITH YEH ABOVE FINAL FORM
    ],
    # TA MARBUTA GOAL (ۃ)
    "\u06c3": [
        # Base Character
        "\u06c3",  # ARABIC LETTER TEH MARBUTA GOAL (Urdu/Sindhi variant)
        # Standard Arabic Equivalents (For Cross-Dialect Search/Matching)
        "\u0629",  # ARABIC LETTER TEH MARBUTA (ة)
        "\ufe93",  # ARABIC LETTER TEH MARBUTA ISOLATED FORM (ﺓ)
        "\ufe94",  # ARABIC LETTER TEH MARBUTA FINAL FORM (ﺔ)
    ],
    # HE DO CHASHMI (ھ)
    "\u06be": [
        "\u06be",  # ARABIC LETTER HEH DOACHASHMEE
        "\ufbaa",  # ARABIC LETTER HEH DOACHASHMEE ISOLATED FORM
        "\ufbab",  # ARABIC LETTER HEH DOACHASHMEE FINAL FORM
        "\ufbac",  # ARABIC LETTER HEH DOACHASHMEE INITIAL FORM
        "\ufbad",  # ARABIC LETTER HEH DOACHASHMEE MEDIAL FORM
    ],
    # CHOTI YE (ی)
    "\u06cc": [
        # Urdu/Farsi Standard (ی)
        "\u06cc",  # ARABIC LETTER FARSI YEH
        "\ufbfc",  # ARABIC LETTER FARSI YEH ISOLATED FORM
        "\ufbfd",  # ARABIC LETTER FARSI YEH FINAL FORM
        "\ufbfe",  # ARABIC LETTER FARSI YEH INITIAL FORM
        "\ufbff",  # ARABIC LETTER FARSI YEH MEDIAL FORM
        # Arabic/Sindhi Standard (ي)
        "\u064a",  # ARABIC LETTER YEH
        "\ufef1",  # ARABIC LETTER YEH ISOLATED FORM
        "\ufef2",  # ARABIC LETTER YEH FINAL FORM
        "\ufef3",  # ARABIC LETTER YEH INITIAL FORM
        "\ufef4",  # ARABIC LETTER YEH MEDIAL FORM
        # Alef Maksura (ى)
        "\u0649",  # ARABIC LETTER ALEF MAKSURA
        "\ufeef",  # ARABIC LETTER ALEF MAKSURA ISOLATED FORM
        "\ufef0",  # ARABIC LETTER ALEF MAKSURA FINAL FORM
    ],
    "\u0626": [  # Yeh with Hamza (ئ) - Common compositional variant (opinionated inclusion)
        "\u0626",  # ARABIC LETTER YEH WITH HAMZA ABOVE
        "\ufe89",  # ARABIC LETTER YEH WITH HAMZA ABOVE ISOLATED FORM
        "\ufe8a",  # ARABIC LETTER YEH WITH HAMZA ABOVE FINAL FORM
        "\ufe8b",  # ARABIC LETTER YEH WITH HAMZA ABOVE INITIAL FORM
        "\ufe8c",  # ARABIC LETTER YEH WITH HAMZA ABOVE MEDIAL FORM
    ],
    # BARI YE (ے)
    "\u06d2": [
        "\u06d2",  # ARABIC LETTER YEH BARREE
        "\u06d3",  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
        "\ufbae",  # ARABIC LETTER YEH BARREE ISOLATED FORM
        "\ufbaf",  # ARABIC LETTER YEH BARREE FINAL FORM
        "\ufbb0",  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE ISOLATED FORM
        "\ufbb1",  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE FINAL FORM
    ],
    # KASHEEDA / TATWEEL (ـ)
    # Mapping to empty string is a common way to 'strip' it during normalization
    "": [
        "\u0640",  # ARABIC TATWEEL
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
    "\ufefb": "\u0644\u0627",  # ARABIC LIGATURE LAM WITH ALEF ISOLATED FORM -> ل + ا
    "\ufefc": "\u0644\u0627",  # ARABIC LIGATURE LAM WITH ALEF FINAL FORM -> ل + ا
    "\ufef5": "\u0644\u0622",  # ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE ISOLATED FORM -> ل + آ
    "\ufef6": "\u0644\u0622",  # ARABIC LIGATURE LAM WITH ALEF WITH MADDA ABOVE FINAL FORM -> ل + آ
}
# LIGATURE MAP END
"""Urdu ligature mapping to sequences of base characters."""

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
    2. Normalizes specific characters via :py:func:`romanalfaz.urduspell.normalizeUrduChars`.
    3. Removes non-alphanumeric marks, digits, and punctuation via :py:func:`romanalfaz.urduspell.removeNonLetterChars`.
    4. Finally, normalizes all internal whitespace sequences to a single `space` using
       :py:func:`romanalfaz.urduspell.normalizeWhiteSpace`.

    The goal is to produce a clean string containing primarily letters and single spaces
    between words,  for further processing or comparison.

    Notes:
        Each character class of the input is handled by exactly one stage of the
        pipeline, so no transformation is applied twice:

        - Positional presentation forms (e.g., U+FE8F, the isolated form of U+0628),
          ligatures (e.g., U+FEFB), and U+0640 (TATWEEL) are folded back to their
          base characters by :py:func:`romanalfaz.urduspell.normalizeUrduChars` only.
        - Cross-dialect base character folds (e.g., U+0624, WAW WITH HAMZA ABOVE,
          to U+0648, WAW) are applied by the same maps.
        - Combining marks other than U+0653 (MADDAH ABOVE) and U+0654 (HAMZA ABOVE)
          are removed by :py:func:`romanalfaz.urduspell.removeNonLetterChars` (via
          :py:func:`romanalfaz.urduspell.removeMarks`).
        - Digits, punctuation, symbols, and control characters are filtered out by
          the same function; whitespace runs are collapsed by
          :py:func:`romanalfaz.urduspell.normalizeWhiteSpace`.

        The NFD normalization inside :py:func:`romanalfaz.urduspell.removeMarks`
        targets only precomposed characters and never touches positional forms,
        so the maps and NFD do not do the same work twice:

        - Positional presentation forms are compatibility characters, so NFD
          leaves them unchanged; the maps are their sole handler.
        - Precomposed characters such as U+0622 (ALEF WITH MADDA ABOVE) decompose
          under NFD into their base plus U+0653; because U+0653 and U+0654 are
          preserved by :py:func:`romanalfaz.urduspell.removeMarks` and the final NFC
          recomposes the character, the round trip is a net no-op. This is the
          mechanism by which U+0622 and U+0626 (YEH WITH HAMZA ABOVE) survive
          mark removal.

        Pipeline effect on different inputs:

        - U+FE8F (isolated form of U+0628): folded to U+0628 only by the maps.
        - U+FEFB (LAM-ALEF ligature): decomposed to U+0644 U+0627 only by the maps.
        - U+0628 U+064E (base plus FATHA): the mark is removed only by
          :py:func:`romanalfaz.urduspell.removeMarks`; the maps leave marks untouched.
        - U+0622 (precomposed): a no-op at every stage (NFD decomposes,
          U+0653 is preserved, NFC recomposes).
        - U+0624 (cross-dialect base): folded to U+0648 only by the maps;
          :py:func:`romanalfaz.urduspell.removeMarks` leaves it unchanged.

        +------------------------------+-----------------------+---------------------------+---------------+
        | Input                        | `removeMarks` only    | `normalizeUrduChars` only | `normalize`   |
        +==============================+=======================+===========================+===============+
        | U+FE8F (positional form)     | U+FE8F (unchanged)    | U+0628 (folded)           | U+0628        |
        +------------------------------+-----------------------+---------------------------+---------------+
        | U+FEFB (ligature)            | U+FEFB (unchanged)    | U+0644 U+0627 (folded)    | U+0644 U+0627 |
        +------------------------------+-----------------------+---------------------------+---------------+
        | U+0628 U+064E (base + fatha) | U+0628 (mark removed) | U+0628 U+064E (unchanged) | U+0628        |
        +------------------------------+-----------------------+---------------------------+---------------+
        | U+0622 (precomposed)         | U+0622 (no-op)        | U+0622 (no-op)            | U+0622        |
        +------------------------------+-----------------------+---------------------------+---------------+
        | U+0624 (cross-dialect)       | U+0624 (no-op)        | U+0648 (folded)           | U+0648        |
        +------------------------------+-----------------------+---------------------------+---------------+

        The division of labor above rests on an exact fit: the marks preserved by
        :py:func:`romanalfaz.urduspell.removeMarks` (U+0653 and U+0654) are exactly the
        marks that the precomposed characters of the variant map's charset (its
        keys and values) carry. This is what makes every stage a no-op on the
        other's work. See the Notes of
        :py:func:`romanalfaz.urduspell.normalizeUrduChars` and
        :py:func:`romanalfaz.urduspell.removeMarks` for the two sides of this contract.

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
    # 3. removeNonLetterChars(): Cleans the text by removing marks, digits, and punctuation.
    # 4. normalizeWhiteSpace(): Collapses multiple spaces into single spaces for readability.
    return normalizeWhiteSpace(removeNonLetterChars(normalizeUrduChars(text.strip())))


# ******************************************************************************
def normalizeUrduChars(text: str) -> str:
    """
    Normalizes Urdu text by converting various character forms into their base representations.

    This function processes input text to handle:

      #. Ligature presentation forms (single characters that render as a ligature, e.g., lam-alef).
      #. Positional variants (initial, medial, final, isolated forms) mapped back to base characters.
      #. Cross-dialect base characters, e.g., U+0624 (WAW WITH HAMZA ABOVE) folded to U+0648 (WAW).

    The output is a string containing only the standard base Urdu characters.

    Notes:
        The base charset this function retains -- the keys of
        :data:`romanalfaz.urduspell.URDU_VARIANT_MAP` -- is chosen by dialect: which
        letters are canonical Urdu. That choice is constrained by the downstream
        :py:func:`romanalfaz.urduspell.removeMarks` stage: every retained base
        character may only carry the marks that
        :py:func:`romanalfaz.urduspell.removeMarks` preserves (U+0653 and U+0654),
        otherwise the mark-stripping step would alter a letter this function just
        produced. This is this function's side of the contract described in
        :py:func:`romanalfaz.urduspell.normalize`.

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

    # Step 1: Handle Ligature Presentation Forms
    # LIGATURE_MAP is a dictionary where keys are single ligature presentation
    # form characters (e.g., lam-alef U+FEFB) and values are the two base
    # characters they decompose into (e.g., "لا").
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
    text = "".join(URDU_VARIANT_REVERSAL_MAP.get(c, c) for c in text)

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

    This function removes marks (e.g., accents or diacritics), all numeric
    digits, all Punctuation, Symbols, and Control characters.
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
    return "".join(
        [c for c in cleanedText if not ud.category(c).startswith(("C", "P", "S", "Nd"))]
    )


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

    Notes:
        The preserved set is this function's side of a contract with the upstream
        :py:func:`romanalfaz.urduspell.normalizeUrduChars` stage. U+0653 and U+0654 are
        the marks carried by the precomposed base characters that the variant
        map retains (U+0622, ALEF WITH MADDA ABOVE, and U+0626, YEH WITH HAMZA
        ABOVE). NFD decomposes such a letter into its base plus one of these
        preserved marks, the filter keeps both parts, and the final NFC recomposes
        the original character: this function is a net no-op on every base
        character the map can output. That keeps the two stages disjoint: the map
        folds letters, this function strips marks, and neither does the other's
        work. If the variant map's base charset ever carries marks other than
        U+0653 or U+0654, this preserved set must be extended in the same change.

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

    # Step 1: Normalize to NFD (Normalization Form Decomposition)
    # NFD breaks down characters into their constituent parts: the base character + any
    # combining marks (diacritics). For example, 'آ' becomes [Base 'ا', Combining Madda].
    nfdForm = ud.normalize("NFD", text)

    # Step 2: Filter Characters
    # We iterate through each character in the decomposed string and apply two conditions:
    # 1. Keep if it is one of the PRESERVED_MARKS (Madda or Hamza Above).
    # 2. Keep if it is NOT a combining character (ud.combining(c) returns True for diacritics).
    # This effectively removes all other diacritical marks while keeping the base letters
    # and the essential structural marks.
    token = "".join([c for c in nfdForm if c in PRESERVED_MARKS or not ud.combining(c)])

    # Step 3: Normalize to NFC (Normalization Form Composition)
    # The filtered string is now a mix of base characters and preserved marks.
    # We re-compose them into NFC form to ensure the output is a valid, standard Unicode
    # string where necessary ligatures are formed correctly for display purposes.
    return ud.normalize("NFC", token)


# ******************************************************************************
