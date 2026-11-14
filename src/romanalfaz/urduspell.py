# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
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
        # Exception enabling full lam-alef ligature coverage (U+FEF7-U+FEFA):
        # bare hamza'd alefs fold to ALEF, consistent with this map's other
        # cross-dialect folds (e.g. U+0624, WAW WITH HAMZA ABOVE -> U+0648).
        # The hamza (U+0655) is a fold input only and never survives, so the
        # PRESERVED_MARKS contract is untouched.
        "\u0623",  # ARABIC LETTER ALEF WITH HAMZA ABOVE
        "\u0625",  # ARABIC LETTER ALEF WITH HAMZA BELOW
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

This mapping defines which characters are retained during text normalization
for processing, effectively filtering out visual representations.
"""

# LIGATURE MAP START

# ******************************************************************************
# The Arabic presentation-form ranges (U+FB50-FDFF and U+FE70-FEFF) contain
# exactly 494 assigned codepoints whose official Unicode names contain
# LIGATURE (verified against unicodedataplus 16.0.0), plus 25 honorific
# ligatures added in Unicode 17.0 that are unassigned in unicodedataplus
# 16.0.0 (U+FBC3-FBD2, U+FD90-FD91, U+FDC8-FDCE; 519 codepoints in total).
# Every one of them falls into exactly one of three classes:
#
#   1. Paired/triplet ligatures: decomposed to their base-character sequence
#      (compatibility tags stripped). Mark-bearing ligatures among them
#      (U+FC5B-FC5D, U+FC5E-FC63, U+FC90, U+FCF2-FCF4, U+FCD9, U+FD3C-FD3D)
#      keep their combining marks, which pass through to be stripped
#      downstream by removeMarks; the U+0020 and U+0640 of their
#      decompositions (where present) are dropped -- a space or tatweel
#      inside a word would split it for lookup.
#   2. Honorifics, phrases, and standalone-word ligatures: mapped to "" and
#      stripped from the input. These are complete words (e.g. U+FDF2, ALLAH)
#      that require no decomposition and no dictionary lookup.
#   3. Excluded ligatures: no entry at all, so they pass through untouched
#      like any other non-Urdu character (see LIGATURE_EXCLUDED below).
#
# The two registries below define classes 2 and 3 explicitly; every other
# ligature codepoint is a literal entry of the table, authored from the
# Unicode decomposition data (one-off generator at authoring time, in the
# pattern of URDU_VARIANT_MAP). Nothing is left to a silent gap: the tests
# assert that all three classes together account for every ligature
# codepoint of the two ranges.

LIGATURE_EXCLUDED: frozenset[str] = frozenset(
    [
        # U+FBEC/U+FBED: LIGATURE YEH WITH HAMZA ABOVE WITH AE (partner
        # U+06D5, AE) -- U+06D5 is not an Urdu letter, so the ligature is
        # outside the target language.
        "\ufbec",
        "\ufbed",
        # U+FBF0-FBF8: LIGATURE YEH WITH HAMZA ABOVE WITH U/OE/YU/E -- the
        # Uyghur/Kazakh/Kirghiz vowel ligatures; not Urdu.
        "\ufbf0",
        "\ufbf1",
        "\ufbf2",
        "\ufbf3",
        "\ufbf4",
        "\ufbf5",
        "\ufbf6",
        "\ufbf7",
        "\ufbf8",
        # U+FBF9-FBFB: LIGATURE UIGHUR KIRGHIZ YEH WITH HAMZA ABOVE WITH
        # ALEF MAKSURA -- same Uyghur family (although the partner U+0649 is
        # itself in URDU_VARIANT_MAP, the ligature is not Urdu).
        "\ufbf9",
        "\ufbfa",
        "\ufbfb",
    ]
)
"""
Arabic presentation-form ligatures deliberately given no entry in
:data:`romanalfaz.urduspell.LIGATURE_MAP`.

These 14 codepoints are ligatures of the target script (U+0626) with letters
outside the Urdu charset (U+06D5) or of the Uyghur/Kazakh/Kirghiz vowel
series. They pass through :py:func:`romanalfaz.urduspell.normalizeUrduChars`
untouched, like any other non-Urdu base letter.
"""

LIGATURE_DELETED: frozenset[str] = frozenset(
    [
        # U+FBC3-FBD2, U+FD90-FD91, U+FDC8-FDCE: honorific/invocation
        # ligatures added in Unicode 17.0. They are unassigned in
        # unicodedataplus 16.0.0, so they are kept as literals here (and as
        # literal "" entries of LIGATURE_MAP) to make the deletion
        # version-independent.
        *("\ufbc3", "\ufbc4", "\ufbc5", "\ufbc6", "\ufbc7", "\ufbc8"),
        *("\ufbc9", "\ufbca", "\ufbcb", "\ufbcc", "\ufbcd", "\ufbce"),
        *("\ufbcf", "\ufbd0", "\ufbd1", "\ufbd2"),
        *("\ufd90", "\ufd91"),
        *("\ufdc8", "\ufdc9", "\ufdca", "\ufdcb", "\ufdcc", "\ufdcd"),
        "\ufdce",
        # U+FD40-FD4F: honorific/invocation ligatures (RAHIMAHU ALLAAH,
        # RADI ALLAAHU ANH, ALAYHI AS-SALAAM, QUDDISA SIRRAH, ...) with no
        # decomposition field in the Unicode data.
        *("\ufd40", "\ufd41", "\ufd42", "\ufd43", "\ufd44", "\ufd45"),
        *("\ufd46", "\ufd47", "\ufd48", "\ufd49", "\ufd4a", "\ufd4b"),
        *("\ufd4c", "\ufd4d", "\ufd4e", "\ufd4f"),
        # U+FDCF: SALAAMUHU ALAYNAA, no decomposition (U+FDC8-FDCE are
        # unassigned in Unicode 16.0).
        "\ufdcf",
        # U+FDF0-FDFB: standalone-word and phrase ligatures. Although most
        # of them (e.g. U+FDF2, ALLAH) do decompose to real words, they are
        # full-fledged complete words that require no decomposition and no
        # dictionary lookup, so they are deliberately stripped instead.
        *("\ufdf0", "\ufdf1", "\ufdf2", "\ufdf3", "\ufdf4", "\ufdf5"),
        *("\ufdf6", "\ufdf7", "\ufdf8", "\ufdf9", "\ufdfa", "\ufdfb"),
        # U+FDFD-FDFF: BISMILLAH AR-RAHMAN AR-RAHEEM, SUBHAANAHU WA TAAALAA,
        # AZZA WA JALL -- phrase ligatures with no decomposition field.
        "\ufdfd",
        "\ufdfe",
        "\ufdff",
    ]
)
"""
Arabic presentation-form ligatures mapped to ``""`` by
:data:`romanalfaz.urduspell.LIGATURE_MAP` and thereby stripped from the input.

These 57 codepoints are honorific, invocation, and phrase ligatures, or
standalone-word ligatures (e.g. U+FDF2, ALLAH) that are complete words
requiring no dictionary lookup; 32 of them are present in unicodedataplus
16.0.0 and 25 are Unicode 17.0 additions kept as literals. See the section
comment above for the group-by-group rationale.
"""

LIGATURE_MAP: dict[str, str] = {
    # lam-alef family (U+FEF5-FEFC)
    "\ufef5": "\u0644\u0622",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH MADDA ABOVE
    "\ufef6": "\u0644\u0622",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH MADDA ABOVE
    "\ufef7": "\u0644\u0623",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\ufef8": "\u0644\u0623",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH HAMZA ABOVE
    "\ufef9": "\u0644\u0625",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH HAMZA BELOW
    "\ufefa": "\u0644\u0625",  # ARABIC LETTER LAM + ARABIC LETTER ALEF WITH HAMZA BELOW
    "\ufefb": "\u0644\u0627",  # ARABIC LETTER LAM + ARABIC LETTER ALEF
    "\ufefc": "\u0644\u0627",  # ARABIC LETTER LAM + ARABIC LETTER ALEF
    # YEH WITH HAMZA inclusions (U+FBEA-FBEB, U+FBEE-FBEF)
    "\ufbea": "\u0626\u0627",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER ALEF
    "\ufbeb": "\u0626\u0627",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER ALEF
    "\ufbee": "\u0626\u0648",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER WAW
    "\ufbef": "\u0626\u0648",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER WAW
    # two-letter contextual ligatures (U+FC00-FD3D)
    "\ufc00": "\u0626\u062c",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER JEEM
    "\ufc01": "\u0626\u062d",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER HAH
    "\ufc02": "\u0626\u0645",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER MEEM
    "\ufc03": "\u0626\u0649",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER ALEF MAKSURA
    "\ufc04": "\u0626\u064a",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER YEH
    "\ufc05": "\u0628\u062c",  # ARABIC LETTER BEH + ARABIC LETTER JEEM
    "\ufc06": "\u0628\u062d",  # ARABIC LETTER BEH + ARABIC LETTER HAH
    "\ufc07": "\u0628\u062e",  # ARABIC LETTER BEH + ARABIC LETTER KHAH
    "\ufc08": "\u0628\u0645",  # ARABIC LETTER BEH + ARABIC LETTER MEEM
    "\ufc09": "\u0628\u0649",  # ARABIC LETTER BEH + ARABIC LETTER ALEF MAKSURA
    "\ufc0a": "\u0628\u064a",  # ARABIC LETTER BEH + ARABIC LETTER YEH
    "\ufc0b": "\u062a\u062c",  # ARABIC LETTER TEH + ARABIC LETTER JEEM
    "\ufc0c": "\u062a\u062d",  # ARABIC LETTER TEH + ARABIC LETTER HAH
    "\ufc0d": "\u062a\u062e",  # ARABIC LETTER TEH + ARABIC LETTER KHAH
    "\ufc0e": "\u062a\u0645",  # ARABIC LETTER TEH + ARABIC LETTER MEEM
    "\ufc0f": "\u062a\u0649",  # ARABIC LETTER TEH + ARABIC LETTER ALEF MAKSURA
    "\ufc10": "\u062a\u064a",  # ARABIC LETTER TEH + ARABIC LETTER YEH
    "\ufc11": "\u062b\u062c",  # ARABIC LETTER THEH + ARABIC LETTER JEEM
    "\ufc12": "\u062b\u0645",  # ARABIC LETTER THEH + ARABIC LETTER MEEM
    "\ufc13": "\u062b\u0649",  # ARABIC LETTER THEH + ARABIC LETTER ALEF MAKSURA
    "\ufc14": "\u062b\u064a",  # ARABIC LETTER THEH + ARABIC LETTER YEH
    "\ufc15": "\u062c\u062d",  # ARABIC LETTER JEEM + ARABIC LETTER HAH
    "\ufc16": "\u062c\u0645",  # ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufc17": "\u062d\u062c",  # ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufc18": "\u062d\u0645",  # ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufc19": "\u062e\u062c",  # ARABIC LETTER KHAH + ARABIC LETTER JEEM
    "\ufc1a": "\u062e\u062d",  # ARABIC LETTER KHAH + ARABIC LETTER HAH
    "\ufc1b": "\u062e\u0645",  # ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufc1c": "\u0633\u062c",  # ARABIC LETTER SEEN + ARABIC LETTER JEEM
    "\ufc1d": "\u0633\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER HAH
    "\ufc1e": "\u0633\u062e",  # ARABIC LETTER SEEN + ARABIC LETTER KHAH
    "\ufc1f": "\u0633\u0645",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM
    "\ufc20": "\u0635\u062d",  # ARABIC LETTER SAD + ARABIC LETTER HAH
    "\ufc21": "\u0635\u0645",  # ARABIC LETTER SAD + ARABIC LETTER MEEM
    "\ufc22": "\u0636\u062c",  # ARABIC LETTER DAD + ARABIC LETTER JEEM
    "\ufc23": "\u0636\u062d",  # ARABIC LETTER DAD + ARABIC LETTER HAH
    "\ufc24": "\u0636\u062e",  # ARABIC LETTER DAD + ARABIC LETTER KHAH
    "\ufc25": "\u0636\u0645",  # ARABIC LETTER DAD + ARABIC LETTER MEEM
    "\ufc26": "\u0637\u062d",  # ARABIC LETTER TAH + ARABIC LETTER HAH
    "\ufc27": "\u0637\u0645",  # ARABIC LETTER TAH + ARABIC LETTER MEEM
    "\ufc28": "\u0638\u0645",  # ARABIC LETTER ZAH + ARABIC LETTER MEEM
    "\ufc29": "\u0639\u062c",  # ARABIC LETTER AIN + ARABIC LETTER JEEM
    "\ufc2a": "\u0639\u0645",  # ARABIC LETTER AIN + ARABIC LETTER MEEM
    "\ufc2b": "\u063a\u062c",  # ARABIC LETTER GHAIN + ARABIC LETTER JEEM
    "\ufc2c": "\u063a\u0645",  # ARABIC LETTER GHAIN + ARABIC LETTER MEEM
    "\ufc2d": "\u0641\u062c",  # ARABIC LETTER FEH + ARABIC LETTER JEEM
    "\ufc2e": "\u0641\u062d",  # ARABIC LETTER FEH + ARABIC LETTER HAH
    "\ufc2f": "\u0641\u062e",  # ARABIC LETTER FEH + ARABIC LETTER KHAH
    "\ufc30": "\u0641\u0645",  # ARABIC LETTER FEH + ARABIC LETTER MEEM
    "\ufc31": "\u0641\u0649",  # ARABIC LETTER FEH + ARABIC LETTER ALEF MAKSURA
    "\ufc32": "\u0641\u064a",  # ARABIC LETTER FEH + ARABIC LETTER YEH
    "\ufc33": "\u0642\u062d",  # ARABIC LETTER QAF + ARABIC LETTER HAH
    "\ufc34": "\u0642\u0645",  # ARABIC LETTER QAF + ARABIC LETTER MEEM
    "\ufc35": "\u0642\u0649",  # ARABIC LETTER QAF + ARABIC LETTER ALEF MAKSURA
    "\ufc36": "\u0642\u064a",  # ARABIC LETTER QAF + ARABIC LETTER YEH
    "\ufc37": "\u0643\u0627",  # ARABIC LETTER KAF + ARABIC LETTER ALEF
    "\ufc38": "\u0643\u062c",  # ARABIC LETTER KAF + ARABIC LETTER JEEM
    "\ufc39": "\u0643\u062d",  # ARABIC LETTER KAF + ARABIC LETTER HAH
    "\ufc3a": "\u0643\u062e",  # ARABIC LETTER KAF + ARABIC LETTER KHAH
    "\ufc3b": "\u0643\u0644",  # ARABIC LETTER KAF + ARABIC LETTER LAM
    "\ufc3c": "\u0643\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM
    "\ufc3d": "\u0643\u0649",  # ARABIC LETTER KAF + ARABIC LETTER ALEF MAKSURA
    "\ufc3e": "\u0643\u064a",  # ARABIC LETTER KAF + ARABIC LETTER YEH
    "\ufc3f": "\u0644\u062c",  # ARABIC LETTER LAM + ARABIC LETTER JEEM
    "\ufc40": "\u0644\u062d",  # ARABIC LETTER LAM + ARABIC LETTER HAH
    "\ufc41": "\u0644\u062e",  # ARABIC LETTER LAM + ARABIC LETTER KHAH
    "\ufc42": "\u0644\u0645",  # ARABIC LETTER LAM + ARABIC LETTER MEEM
    "\ufc43": "\u0644\u0649",  # ARABIC LETTER LAM + ARABIC LETTER ALEF MAKSURA
    "\ufc44": "\u0644\u064a",  # ARABIC LETTER LAM + ARABIC LETTER YEH
    "\ufc45": "\u0645\u062c",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM
    "\ufc46": "\u0645\u062d",  # ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufc47": "\u0645\u062e",  # ARABIC LETTER MEEM + ARABIC LETTER KHAH
    "\ufc48": "\u0645\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufc49": "\u0645\u0649",  # ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufc4a": "\u0645\u064a",  # ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufc4b": "\u0646\u062c",  # ARABIC LETTER NOON + ARABIC LETTER JEEM
    "\ufc4c": "\u0646\u062d",  # ARABIC LETTER NOON + ARABIC LETTER HAH
    "\ufc4d": "\u0646\u062e",  # ARABIC LETTER NOON + ARABIC LETTER KHAH
    "\ufc4e": "\u0646\u0645",  # ARABIC LETTER NOON + ARABIC LETTER MEEM
    "\ufc4f": "\u0646\u0649",  # ARABIC LETTER NOON + ARABIC LETTER ALEF MAKSURA
    "\ufc50": "\u0646\u064a",  # ARABIC LETTER NOON + ARABIC LETTER YEH
    "\ufc51": "\u0647\u062c",  # ARABIC LETTER HEH + ARABIC LETTER JEEM
    "\ufc52": "\u0647\u0645",  # ARABIC LETTER HEH + ARABIC LETTER MEEM
    "\ufc53": "\u0647\u0649",  # ARABIC LETTER HEH + ARABIC LETTER ALEF MAKSURA
    "\ufc54": "\u0647\u064a",  # ARABIC LETTER HEH + ARABIC LETTER YEH
    "\ufc55": "\u064a\u062c",  # ARABIC LETTER YEH + ARABIC LETTER JEEM
    "\ufc56": "\u064a\u062d",  # ARABIC LETTER YEH + ARABIC LETTER HAH
    "\ufc57": "\u064a\u062e",  # ARABIC LETTER YEH + ARABIC LETTER KHAH
    "\ufc58": "\u064a\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM
    "\ufc59": "\u064a\u0649",  # ARABIC LETTER YEH + ARABIC LETTER ALEF MAKSURA
    "\ufc5a": "\u064a\u064a",  # ARABIC LETTER YEH + ARABIC LETTER YEH
    "\ufc5b": "\u0630\u0670",  # ARABIC LETTER THAL + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufc5c": "\u0631\u0670",  # ARABIC LETTER REH + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufc5d": "\u0649\u0670",  # ARABIC LETTER ALEF MAKSURA + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufc5e": "\u064c\u0651",  # ARABIC DAMMATAN + ARABIC SHADDA
    "\ufc5f": "\u064d\u0651",  # ARABIC KASRATAN + ARABIC SHADDA
    "\ufc60": "\u064e\u0651",  # ARABIC FATHA + ARABIC SHADDA
    "\ufc61": "\u064f\u0651",  # ARABIC DAMMA + ARABIC SHADDA
    "\ufc62": "\u0650\u0651",  # ARABIC KASRA + ARABIC SHADDA
    "\ufc63": "\u0651\u0670",  # ARABIC SHADDA + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufc64": "\u0626\u0631",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER REH
    "\ufc65": "\u0626\u0632",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER ZAIN
    "\ufc66": "\u0626\u0645",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER MEEM
    "\ufc67": "\u0626\u0646",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER NOON
    "\ufc68": "\u0626\u0649",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER ALEF MAKSURA
    "\ufc69": "\u0626\u064a",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER YEH
    "\ufc6a": "\u0628\u0631",  # ARABIC LETTER BEH + ARABIC LETTER REH
    "\ufc6b": "\u0628\u0632",  # ARABIC LETTER BEH + ARABIC LETTER ZAIN
    "\ufc6c": "\u0628\u0645",  # ARABIC LETTER BEH + ARABIC LETTER MEEM
    "\ufc6d": "\u0628\u0646",  # ARABIC LETTER BEH + ARABIC LETTER NOON
    "\ufc6e": "\u0628\u0649",  # ARABIC LETTER BEH + ARABIC LETTER ALEF MAKSURA
    "\ufc6f": "\u0628\u064a",  # ARABIC LETTER BEH + ARABIC LETTER YEH
    "\ufc70": "\u062a\u0631",  # ARABIC LETTER TEH + ARABIC LETTER REH
    "\ufc71": "\u062a\u0632",  # ARABIC LETTER TEH + ARABIC LETTER ZAIN
    "\ufc72": "\u062a\u0645",  # ARABIC LETTER TEH + ARABIC LETTER MEEM
    "\ufc73": "\u062a\u0646",  # ARABIC LETTER TEH + ARABIC LETTER NOON
    "\ufc74": "\u062a\u0649",  # ARABIC LETTER TEH + ARABIC LETTER ALEF MAKSURA
    "\ufc75": "\u062a\u064a",  # ARABIC LETTER TEH + ARABIC LETTER YEH
    "\ufc76": "\u062b\u0631",  # ARABIC LETTER THEH + ARABIC LETTER REH
    "\ufc77": "\u062b\u0632",  # ARABIC LETTER THEH + ARABIC LETTER ZAIN
    "\ufc78": "\u062b\u0645",  # ARABIC LETTER THEH + ARABIC LETTER MEEM
    "\ufc79": "\u062b\u0646",  # ARABIC LETTER THEH + ARABIC LETTER NOON
    "\ufc7a": "\u062b\u0649",  # ARABIC LETTER THEH + ARABIC LETTER ALEF MAKSURA
    "\ufc7b": "\u062b\u064a",  # ARABIC LETTER THEH + ARABIC LETTER YEH
    "\ufc7c": "\u0641\u0649",  # ARABIC LETTER FEH + ARABIC LETTER ALEF MAKSURA
    "\ufc7d": "\u0641\u064a",  # ARABIC LETTER FEH + ARABIC LETTER YEH
    "\ufc7e": "\u0642\u0649",  # ARABIC LETTER QAF + ARABIC LETTER ALEF MAKSURA
    "\ufc7f": "\u0642\u064a",  # ARABIC LETTER QAF + ARABIC LETTER YEH
    "\ufc80": "\u0643\u0627",  # ARABIC LETTER KAF + ARABIC LETTER ALEF
    "\ufc81": "\u0643\u0644",  # ARABIC LETTER KAF + ARABIC LETTER LAM
    "\ufc82": "\u0643\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM
    "\ufc83": "\u0643\u0649",  # ARABIC LETTER KAF + ARABIC LETTER ALEF MAKSURA
    "\ufc84": "\u0643\u064a",  # ARABIC LETTER KAF + ARABIC LETTER YEH
    "\ufc85": "\u0644\u0645",  # ARABIC LETTER LAM + ARABIC LETTER MEEM
    "\ufc86": "\u0644\u0649",  # ARABIC LETTER LAM + ARABIC LETTER ALEF MAKSURA
    "\ufc87": "\u0644\u064a",  # ARABIC LETTER LAM + ARABIC LETTER YEH
    "\ufc88": "\u0645\u0627",  # ARABIC LETTER MEEM + ARABIC LETTER ALEF
    "\ufc89": "\u0645\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufc8a": "\u0646\u0631",  # ARABIC LETTER NOON + ARABIC LETTER REH
    "\ufc8b": "\u0646\u0632",  # ARABIC LETTER NOON + ARABIC LETTER ZAIN
    "\ufc8c": "\u0646\u0645",  # ARABIC LETTER NOON + ARABIC LETTER MEEM
    "\ufc8d": "\u0646\u0646",  # ARABIC LETTER NOON + ARABIC LETTER NOON
    "\ufc8e": "\u0646\u0649",  # ARABIC LETTER NOON + ARABIC LETTER ALEF MAKSURA
    "\ufc8f": "\u0646\u064a",  # ARABIC LETTER NOON + ARABIC LETTER YEH
    "\ufc90": "\u0649\u0670",  # ARABIC LETTER ALEF MAKSURA + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufc91": "\u064a\u0631",  # ARABIC LETTER YEH + ARABIC LETTER REH
    "\ufc92": "\u064a\u0632",  # ARABIC LETTER YEH + ARABIC LETTER ZAIN
    "\ufc93": "\u064a\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM
    "\ufc94": "\u064a\u0646",  # ARABIC LETTER YEH + ARABIC LETTER NOON
    "\ufc95": "\u064a\u0649",  # ARABIC LETTER YEH + ARABIC LETTER ALEF MAKSURA
    "\ufc96": "\u064a\u064a",  # ARABIC LETTER YEH + ARABIC LETTER YEH
    "\ufc97": "\u0626\u062c",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER JEEM
    "\ufc98": "\u0626\u062d",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER HAH
    "\ufc99": "\u0626\u062e",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER KHAH
    "\ufc9a": "\u0626\u0645",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER MEEM
    "\ufc9b": "\u0626\u0647",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER HEH
    "\ufc9c": "\u0628\u062c",  # ARABIC LETTER BEH + ARABIC LETTER JEEM
    "\ufc9d": "\u0628\u062d",  # ARABIC LETTER BEH + ARABIC LETTER HAH
    "\ufc9e": "\u0628\u062e",  # ARABIC LETTER BEH + ARABIC LETTER KHAH
    "\ufc9f": "\u0628\u0645",  # ARABIC LETTER BEH + ARABIC LETTER MEEM
    "\ufca0": "\u0628\u0647",  # ARABIC LETTER BEH + ARABIC LETTER HEH
    "\ufca1": "\u062a\u062c",  # ARABIC LETTER TEH + ARABIC LETTER JEEM
    "\ufca2": "\u062a\u062d",  # ARABIC LETTER TEH + ARABIC LETTER HAH
    "\ufca3": "\u062a\u062e",  # ARABIC LETTER TEH + ARABIC LETTER KHAH
    "\ufca4": "\u062a\u0645",  # ARABIC LETTER TEH + ARABIC LETTER MEEM
    "\ufca5": "\u062a\u0647",  # ARABIC LETTER TEH + ARABIC LETTER HEH
    "\ufca6": "\u062b\u0645",  # ARABIC LETTER THEH + ARABIC LETTER MEEM
    "\ufca7": "\u062c\u062d",  # ARABIC LETTER JEEM + ARABIC LETTER HAH
    "\ufca8": "\u062c\u0645",  # ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufca9": "\u062d\u062c",  # ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufcaa": "\u062d\u0645",  # ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufcab": "\u062e\u062c",  # ARABIC LETTER KHAH + ARABIC LETTER JEEM
    "\ufcac": "\u062e\u0645",  # ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufcad": "\u0633\u062c",  # ARABIC LETTER SEEN + ARABIC LETTER JEEM
    "\ufcae": "\u0633\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER HAH
    "\ufcaf": "\u0633\u062e",  # ARABIC LETTER SEEN + ARABIC LETTER KHAH
    "\ufcb0": "\u0633\u0645",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM
    "\ufcb1": "\u0635\u062d",  # ARABIC LETTER SAD + ARABIC LETTER HAH
    "\ufcb2": "\u0635\u062e",  # ARABIC LETTER SAD + ARABIC LETTER KHAH
    "\ufcb3": "\u0635\u0645",  # ARABIC LETTER SAD + ARABIC LETTER MEEM
    "\ufcb4": "\u0636\u062c",  # ARABIC LETTER DAD + ARABIC LETTER JEEM
    "\ufcb5": "\u0636\u062d",  # ARABIC LETTER DAD + ARABIC LETTER HAH
    "\ufcb6": "\u0636\u062e",  # ARABIC LETTER DAD + ARABIC LETTER KHAH
    "\ufcb7": "\u0636\u0645",  # ARABIC LETTER DAD + ARABIC LETTER MEEM
    "\ufcb8": "\u0637\u062d",  # ARABIC LETTER TAH + ARABIC LETTER HAH
    "\ufcb9": "\u0638\u0645",  # ARABIC LETTER ZAH + ARABIC LETTER MEEM
    "\ufcba": "\u0639\u062c",  # ARABIC LETTER AIN + ARABIC LETTER JEEM
    "\ufcbb": "\u0639\u0645",  # ARABIC LETTER AIN + ARABIC LETTER MEEM
    "\ufcbc": "\u063a\u062c",  # ARABIC LETTER GHAIN + ARABIC LETTER JEEM
    "\ufcbd": "\u063a\u0645",  # ARABIC LETTER GHAIN + ARABIC LETTER MEEM
    "\ufcbe": "\u0641\u062c",  # ARABIC LETTER FEH + ARABIC LETTER JEEM
    "\ufcbf": "\u0641\u062d",  # ARABIC LETTER FEH + ARABIC LETTER HAH
    "\ufcc0": "\u0641\u062e",  # ARABIC LETTER FEH + ARABIC LETTER KHAH
    "\ufcc1": "\u0641\u0645",  # ARABIC LETTER FEH + ARABIC LETTER MEEM
    "\ufcc2": "\u0642\u062d",  # ARABIC LETTER QAF + ARABIC LETTER HAH
    "\ufcc3": "\u0642\u0645",  # ARABIC LETTER QAF + ARABIC LETTER MEEM
    "\ufcc4": "\u0643\u062c",  # ARABIC LETTER KAF + ARABIC LETTER JEEM
    "\ufcc5": "\u0643\u062d",  # ARABIC LETTER KAF + ARABIC LETTER HAH
    "\ufcc6": "\u0643\u062e",  # ARABIC LETTER KAF + ARABIC LETTER KHAH
    "\ufcc7": "\u0643\u0644",  # ARABIC LETTER KAF + ARABIC LETTER LAM
    "\ufcc8": "\u0643\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM
    "\ufcc9": "\u0644\u062c",  # ARABIC LETTER LAM + ARABIC LETTER JEEM
    "\ufcca": "\u0644\u062d",  # ARABIC LETTER LAM + ARABIC LETTER HAH
    "\ufccb": "\u0644\u062e",  # ARABIC LETTER LAM + ARABIC LETTER KHAH
    "\ufccc": "\u0644\u0645",  # ARABIC LETTER LAM + ARABIC LETTER MEEM
    "\ufccd": "\u0644\u0647",  # ARABIC LETTER LAM + ARABIC LETTER HEH
    "\ufcce": "\u0645\u062c",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM
    "\ufccf": "\u0645\u062d",  # ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufcd0": "\u0645\u062e",  # ARABIC LETTER MEEM + ARABIC LETTER KHAH
    "\ufcd1": "\u0645\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufcd2": "\u0646\u062c",  # ARABIC LETTER NOON + ARABIC LETTER JEEM
    "\ufcd3": "\u0646\u062d",  # ARABIC LETTER NOON + ARABIC LETTER HAH
    "\ufcd4": "\u0646\u062e",  # ARABIC LETTER NOON + ARABIC LETTER KHAH
    "\ufcd5": "\u0646\u0645",  # ARABIC LETTER NOON + ARABIC LETTER MEEM
    "\ufcd6": "\u0646\u0647",  # ARABIC LETTER NOON + ARABIC LETTER HEH
    "\ufcd7": "\u0647\u062c",  # ARABIC LETTER HEH + ARABIC LETTER JEEM
    "\ufcd8": "\u0647\u0645",  # ARABIC LETTER HEH + ARABIC LETTER MEEM
    "\ufcd9": "\u0647\u0670",  # ARABIC LETTER HEH + ARABIC LETTER SUPERSCRIPT ALEF
    "\ufcda": "\u064a\u062c",  # ARABIC LETTER YEH + ARABIC LETTER JEEM
    "\ufcdb": "\u064a\u062d",  # ARABIC LETTER YEH + ARABIC LETTER HAH
    "\ufcdc": "\u064a\u062e",  # ARABIC LETTER YEH + ARABIC LETTER KHAH
    "\ufcdd": "\u064a\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM
    "\ufcde": "\u064a\u0647",  # ARABIC LETTER YEH + ARABIC LETTER HEH
    "\ufcdf": "\u0626\u0645",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER MEEM
    "\ufce0": "\u0626\u0647",  # ARABIC LETTER YEH WITH HAMZA ABOVE + ARABIC LETTER HEH
    "\ufce1": "\u0628\u0645",  # ARABIC LETTER BEH + ARABIC LETTER MEEM
    "\ufce2": "\u0628\u0647",  # ARABIC LETTER BEH + ARABIC LETTER HEH
    "\ufce3": "\u062a\u0645",  # ARABIC LETTER TEH + ARABIC LETTER MEEM
    "\ufce4": "\u062a\u0647",  # ARABIC LETTER TEH + ARABIC LETTER HEH
    "\ufce5": "\u062b\u0645",  # ARABIC LETTER THEH + ARABIC LETTER MEEM
    "\ufce6": "\u062b\u0647",  # ARABIC LETTER THEH + ARABIC LETTER HEH
    "\ufce7": "\u0633\u0645",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM
    "\ufce8": "\u0633\u0647",  # ARABIC LETTER SEEN + ARABIC LETTER HEH
    "\ufce9": "\u0634\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM
    "\ufcea": "\u0634\u0647",  # ARABIC LETTER SHEEN + ARABIC LETTER HEH
    "\ufceb": "\u0643\u0644",  # ARABIC LETTER KAF + ARABIC LETTER LAM
    "\ufcec": "\u0643\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM
    "\ufced": "\u0644\u0645",  # ARABIC LETTER LAM + ARABIC LETTER MEEM
    "\ufcee": "\u0646\u0645",  # ARABIC LETTER NOON + ARABIC LETTER MEEM
    "\ufcef": "\u0646\u0647",  # ARABIC LETTER NOON + ARABIC LETTER HEH
    "\ufcf0": "\u064a\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM
    "\ufcf1": "\u064a\u0647",  # ARABIC LETTER YEH + ARABIC LETTER HEH
    "\ufcf2": "\u064e\u0651",  # ARABIC FATHA + ARABIC SHADDA
    "\ufcf3": "\u064f\u0651",  # ARABIC DAMMA + ARABIC SHADDA
    "\ufcf4": "\u0650\u0651",  # ARABIC KASRA + ARABIC SHADDA
    "\ufcf5": "\u0637\u0649",  # ARABIC LETTER TAH + ARABIC LETTER ALEF MAKSURA
    "\ufcf6": "\u0637\u064a",  # ARABIC LETTER TAH + ARABIC LETTER YEH
    "\ufcf7": "\u0639\u0649",  # ARABIC LETTER AIN + ARABIC LETTER ALEF MAKSURA
    "\ufcf8": "\u0639\u064a",  # ARABIC LETTER AIN + ARABIC LETTER YEH
    "\ufcf9": "\u063a\u0649",  # ARABIC LETTER GHAIN + ARABIC LETTER ALEF MAKSURA
    "\ufcfa": "\u063a\u064a",  # ARABIC LETTER GHAIN + ARABIC LETTER YEH
    "\ufcfb": "\u0633\u0649",  # ARABIC LETTER SEEN + ARABIC LETTER ALEF MAKSURA
    "\ufcfc": "\u0633\u064a",  # ARABIC LETTER SEEN + ARABIC LETTER YEH
    "\ufcfd": "\u0634\u0649",  # ARABIC LETTER SHEEN + ARABIC LETTER ALEF MAKSURA
    "\ufcfe": "\u0634\u064a",  # ARABIC LETTER SHEEN + ARABIC LETTER YEH
    "\ufcff": "\u062d\u0649",  # ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufd00": "\u062d\u064a",  # ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufd01": "\u062c\u0649",  # ARABIC LETTER JEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd02": "\u062c\u064a",  # ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufd03": "\u062e\u0649",  # ARABIC LETTER KHAH + ARABIC LETTER ALEF MAKSURA
    "\ufd04": "\u062e\u064a",  # ARABIC LETTER KHAH + ARABIC LETTER YEH
    "\ufd05": "\u0635\u0649",  # ARABIC LETTER SAD + ARABIC LETTER ALEF MAKSURA
    "\ufd06": "\u0635\u064a",  # ARABIC LETTER SAD + ARABIC LETTER YEH
    "\ufd07": "\u0636\u0649",  # ARABIC LETTER DAD + ARABIC LETTER ALEF MAKSURA
    "\ufd08": "\u0636\u064a",  # ARABIC LETTER DAD + ARABIC LETTER YEH
    "\ufd09": "\u0634\u062c",  # ARABIC LETTER SHEEN + ARABIC LETTER JEEM
    "\ufd0a": "\u0634\u062d",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH
    "\ufd0b": "\u0634\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER KHAH
    "\ufd0c": "\u0634\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM
    "\ufd0d": "\u0634\u0631",  # ARABIC LETTER SHEEN + ARABIC LETTER REH
    "\ufd0e": "\u0633\u0631",  # ARABIC LETTER SEEN + ARABIC LETTER REH
    "\ufd0f": "\u0635\u0631",  # ARABIC LETTER SAD + ARABIC LETTER REH
    "\ufd10": "\u0636\u0631",  # ARABIC LETTER DAD + ARABIC LETTER REH
    "\ufd11": "\u0637\u0649",  # ARABIC LETTER TAH + ARABIC LETTER ALEF MAKSURA
    "\ufd12": "\u0637\u064a",  # ARABIC LETTER TAH + ARABIC LETTER YEH
    "\ufd13": "\u0639\u0649",  # ARABIC LETTER AIN + ARABIC LETTER ALEF MAKSURA
    "\ufd14": "\u0639\u064a",  # ARABIC LETTER AIN + ARABIC LETTER YEH
    "\ufd15": "\u063a\u0649",  # ARABIC LETTER GHAIN + ARABIC LETTER ALEF MAKSURA
    "\ufd16": "\u063a\u064a",  # ARABIC LETTER GHAIN + ARABIC LETTER YEH
    "\ufd17": "\u0633\u0649",  # ARABIC LETTER SEEN + ARABIC LETTER ALEF MAKSURA
    "\ufd18": "\u0633\u064a",  # ARABIC LETTER SEEN + ARABIC LETTER YEH
    "\ufd19": "\u0634\u0649",  # ARABIC LETTER SHEEN + ARABIC LETTER ALEF MAKSURA
    "\ufd1a": "\u0634\u064a",  # ARABIC LETTER SHEEN + ARABIC LETTER YEH
    "\ufd1b": "\u062d\u0649",  # ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufd1c": "\u062d\u064a",  # ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufd1d": "\u062c\u0649",  # ARABIC LETTER JEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd1e": "\u062c\u064a",  # ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufd1f": "\u062e\u0649",  # ARABIC LETTER KHAH + ARABIC LETTER ALEF MAKSURA
    "\ufd20": "\u062e\u064a",  # ARABIC LETTER KHAH + ARABIC LETTER YEH
    "\ufd21": "\u0635\u0649",  # ARABIC LETTER SAD + ARABIC LETTER ALEF MAKSURA
    "\ufd22": "\u0635\u064a",  # ARABIC LETTER SAD + ARABIC LETTER YEH
    "\ufd23": "\u0636\u0649",  # ARABIC LETTER DAD + ARABIC LETTER ALEF MAKSURA
    "\ufd24": "\u0636\u064a",  # ARABIC LETTER DAD + ARABIC LETTER YEH
    "\ufd25": "\u0634\u062c",  # ARABIC LETTER SHEEN + ARABIC LETTER JEEM
    "\ufd26": "\u0634\u062d",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH
    "\ufd27": "\u0634\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER KHAH
    "\ufd28": "\u0634\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM
    "\ufd29": "\u0634\u0631",  # ARABIC LETTER SHEEN + ARABIC LETTER REH
    "\ufd2a": "\u0633\u0631",  # ARABIC LETTER SEEN + ARABIC LETTER REH
    "\ufd2b": "\u0635\u0631",  # ARABIC LETTER SAD + ARABIC LETTER REH
    "\ufd2c": "\u0636\u0631",  # ARABIC LETTER DAD + ARABIC LETTER REH
    "\ufd2d": "\u0634\u062c",  # ARABIC LETTER SHEEN + ARABIC LETTER JEEM
    "\ufd2e": "\u0634\u062d",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH
    "\ufd2f": "\u0634\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER KHAH
    "\ufd30": "\u0634\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM
    "\ufd31": "\u0633\u0647",  # ARABIC LETTER SEEN + ARABIC LETTER HEH
    "\ufd32": "\u0634\u0647",  # ARABIC LETTER SHEEN + ARABIC LETTER HEH
    "\ufd33": "\u0637\u0645",  # ARABIC LETTER TAH + ARABIC LETTER MEEM
    "\ufd34": "\u0633\u062c",  # ARABIC LETTER SEEN + ARABIC LETTER JEEM
    "\ufd35": "\u0633\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER HAH
    "\ufd36": "\u0633\u062e",  # ARABIC LETTER SEEN + ARABIC LETTER KHAH
    "\ufd37": "\u0634\u062c",  # ARABIC LETTER SHEEN + ARABIC LETTER JEEM
    "\ufd38": "\u0634\u062d",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH
    "\ufd39": "\u0634\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER KHAH
    "\ufd3a": "\u0637\u0645",  # ARABIC LETTER TAH + ARABIC LETTER MEEM
    "\ufd3b": "\u0638\u0645",  # ARABIC LETTER ZAH + ARABIC LETTER MEEM
    "\ufd3c": "\u0627\u064b",  # ARABIC LETTER ALEF + ARABIC FATHATAN
    "\ufd3d": "\u0627\u064b",  # ARABIC LETTER ALEF + ARABIC FATHATAN
    # three-letter contextual ligatures (U+FD50-FD8F)
    "\ufd50": "\u062a\u062c\u0645",  # ARABIC LETTER TEH + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufd51": "\u062a\u062d\u062c",  # ARABIC LETTER TEH + ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufd52": "\u062a\u062d\u062c",  # ARABIC LETTER TEH + ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufd53": "\u062a\u062d\u0645",  # ARABIC LETTER TEH + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufd54": "\u062a\u062e\u0645",  # ARABIC LETTER TEH + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd55": "\u062a\u0645\u062c",  # ARABIC LETTER TEH + ARABIC LETTER MEEM + ARABIC LETTER JEEM
    "\ufd56": "\u062a\u0645\u062d",  # ARABIC LETTER TEH + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd57": "\u062a\u0645\u062e",  # ARABIC LETTER TEH + ARABIC LETTER MEEM + ARABIC LETTER KHAH
    "\ufd58": "\u062c\u0645\u062d",  # ARABIC LETTER JEEM + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd59": "\u062c\u0645\u062d",  # ARABIC LETTER JEEM + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd5a": "\u062d\u0645\u064a",  # ARABIC LETTER HAH + ARABIC LETTER MEEM + ARABIC LETTER YEH
    # ARABIC LETTER HAH + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd5b": "\u062d\u0645\u0649",
    "\ufd5c": "\u0633\u062d\u062c",  # ARABIC LETTER SEEN + ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufd5d": "\u0633\u062c\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER JEEM + ARABIC LETTER HAH
    # ARABIC LETTER SEEN + ARABIC LETTER JEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd5e": "\u0633\u062c\u0649",
    "\ufd5f": "\u0633\u0645\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd60": "\u0633\u0645\u062d",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd61": "\u0633\u0645\u062c",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM + ARABIC LETTER JEEM
    "\ufd62": "\u0633\u0645\u0645",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd63": "\u0633\u0645\u0645",  # ARABIC LETTER SEEN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd64": "\u0635\u062d\u062d",  # ARABIC LETTER SAD + ARABIC LETTER HAH + ARABIC LETTER HAH
    "\ufd65": "\u0635\u062d\u062d",  # ARABIC LETTER SAD + ARABIC LETTER HAH + ARABIC LETTER HAH
    "\ufd66": "\u0635\u0645\u0645",  # ARABIC LETTER SAD + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd67": "\u0634\u062d\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufd68": "\u0634\u062d\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufd69": "\u0634\u062c\u064a",  # ARABIC LETTER SHEEN + ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufd6a": "\u0634\u0645\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM + ARABIC LETTER KHAH
    "\ufd6b": "\u0634\u0645\u062e",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM + ARABIC LETTER KHAH
    "\ufd6c": "\u0634\u0645\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd6d": "\u0634\u0645\u0645",  # ARABIC LETTER SHEEN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    # ARABIC LETTER DAD + ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufd6e": "\u0636\u062d\u0649",
    "\ufd6f": "\u0636\u062e\u0645",  # ARABIC LETTER DAD + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd70": "\u0636\u062e\u0645",  # ARABIC LETTER DAD + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd71": "\u0637\u0645\u062d",  # ARABIC LETTER TAH + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd72": "\u0637\u0645\u062d",  # ARABIC LETTER TAH + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd73": "\u0637\u0645\u0645",  # ARABIC LETTER TAH + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd74": "\u0637\u0645\u064a",  # ARABIC LETTER TAH + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufd75": "\u0639\u062c\u0645",  # ARABIC LETTER AIN + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufd76": "\u0639\u0645\u0645",  # ARABIC LETTER AIN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd77": "\u0639\u0645\u0645",  # ARABIC LETTER AIN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    # ARABIC LETTER AIN + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd78": "\u0639\u0645\u0649",
    "\ufd79": "\u063a\u0645\u0645",  # ARABIC LETTER GHAIN + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd7a": "\u063a\u0645\u064a",  # ARABIC LETTER GHAIN + ARABIC LETTER MEEM + ARABIC LETTER YEH
    # ARABIC LETTER GHAIN + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd7b": "\u063a\u0645\u0649",
    "\ufd7c": "\u0641\u062e\u0645",  # ARABIC LETTER FEH + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd7d": "\u0641\u062e\u0645",  # ARABIC LETTER FEH + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd7e": "\u0642\u0645\u062d",  # ARABIC LETTER QAF + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd7f": "\u0642\u0645\u0645",  # ARABIC LETTER QAF + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd80": "\u0644\u062d\u0645",  # ARABIC LETTER LAM + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufd81": "\u0644\u062d\u064a",  # ARABIC LETTER LAM + ARABIC LETTER HAH + ARABIC LETTER YEH
    # ARABIC LETTER LAM + ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufd82": "\u0644\u062d\u0649",
    "\ufd83": "\u0644\u062c\u062c",  # ARABIC LETTER LAM + ARABIC LETTER JEEM + ARABIC LETTER JEEM
    "\ufd84": "\u0644\u062c\u062c",  # ARABIC LETTER LAM + ARABIC LETTER JEEM + ARABIC LETTER JEEM
    "\ufd85": "\u0644\u062e\u0645",  # ARABIC LETTER LAM + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd86": "\u0644\u062e\u0645",  # ARABIC LETTER LAM + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    "\ufd87": "\u0644\u0645\u062d",  # ARABIC LETTER LAM + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd88": "\u0644\u0645\u062d",  # ARABIC LETTER LAM + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufd89": "\u0645\u062d\u062c",  # ARABIC LETTER MEEM + ARABIC LETTER HAH + ARABIC LETTER JEEM
    "\ufd8a": "\u0645\u062d\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufd8b": "\u0645\u062d\u064a",  # ARABIC LETTER MEEM + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufd8c": "\u0645\u062c\u062d",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM + ARABIC LETTER HAH
    "\ufd8d": "\u0645\u062c\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufd8e": "\u0645\u062e\u062c",  # ARABIC LETTER MEEM + ARABIC LETTER KHAH + ARABIC LETTER JEEM
    "\ufd8f": "\u0645\u062e\u0645",  # ARABIC LETTER MEEM + ARABIC LETTER KHAH + ARABIC LETTER MEEM
    # three-letter contextual ligatures (U+FD92-FDC7)
    "\ufd92": "\u0645\u062c\u062e",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM + ARABIC LETTER KHAH
    "\ufd93": "\u0647\u0645\u062c",  # ARABIC LETTER HEH + ARABIC LETTER MEEM + ARABIC LETTER JEEM
    "\ufd94": "\u0647\u0645\u0645",  # ARABIC LETTER HEH + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd95": "\u0646\u062d\u0645",  # ARABIC LETTER NOON + ARABIC LETTER HAH + ARABIC LETTER MEEM
    # ARABIC LETTER NOON + ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufd96": "\u0646\u062d\u0649",
    "\ufd97": "\u0646\u062c\u0645",  # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufd98": "\u0646\u062c\u0645",  # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd99": "\u0646\u062c\u0649",
    "\ufd9a": "\u0646\u0645\u064a",  # ARABIC LETTER NOON + ARABIC LETTER MEEM + ARABIC LETTER YEH
    # ARABIC LETTER NOON + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufd9b": "\u0646\u0645\u0649",
    "\ufd9c": "\u064a\u0645\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd9d": "\u064a\u0645\u0645",  # ARABIC LETTER YEH + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufd9e": "\u0628\u062e\u064a",  # ARABIC LETTER BEH + ARABIC LETTER KHAH + ARABIC LETTER YEH
    "\ufd9f": "\u062a\u062c\u064a",  # ARABIC LETTER TEH + ARABIC LETTER JEEM + ARABIC LETTER YEH
    # ARABIC LETTER TEH + ARABIC LETTER JEEM + ARABIC LETTER ALEF MAKSURA
    "\ufda0": "\u062a\u062c\u0649",
    "\ufda1": "\u062a\u062e\u064a",  # ARABIC LETTER TEH + ARABIC LETTER KHAH + ARABIC LETTER YEH
    # ARABIC LETTER TEH + ARABIC LETTER KHAH + ARABIC LETTER ALEF MAKSURA
    "\ufda2": "\u062a\u062e\u0649",
    "\ufda3": "\u062a\u0645\u064a",  # ARABIC LETTER TEH + ARABIC LETTER MEEM + ARABIC LETTER YEH
    # ARABIC LETTER TEH + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufda4": "\u062a\u0645\u0649",
    "\ufda5": "\u062c\u0645\u064a",  # ARABIC LETTER JEEM + ARABIC LETTER MEEM + ARABIC LETTER YEH
    # ARABIC LETTER JEEM + ARABIC LETTER HAH + ARABIC LETTER ALEF MAKSURA
    "\ufda6": "\u062c\u062d\u0649",
    # ARABIC LETTER JEEM + ARABIC LETTER MEEM + ARABIC LETTER ALEF MAKSURA
    "\ufda7": "\u062c\u0645\u0649",
    # ARABIC LETTER SEEN + ARABIC LETTER KHAH + ARABIC LETTER ALEF MAKSURA
    "\ufda8": "\u0633\u062e\u0649",
    "\ufda9": "\u0635\u062d\u064a",  # ARABIC LETTER SAD + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdaa": "\u0634\u062d\u064a",  # ARABIC LETTER SHEEN + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdab": "\u0636\u062d\u064a",  # ARABIC LETTER DAD + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdac": "\u0644\u062c\u064a",  # ARABIC LETTER LAM + ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufdad": "\u0644\u0645\u064a",  # ARABIC LETTER LAM + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdae": "\u064a\u062d\u064a",  # ARABIC LETTER YEH + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdaf": "\u064a\u062c\u064a",  # ARABIC LETTER YEH + ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufdb0": "\u064a\u0645\u064a",  # ARABIC LETTER YEH + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdb1": "\u0645\u0645\u064a",  # ARABIC LETTER MEEM + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdb2": "\u0642\u0645\u064a",  # ARABIC LETTER QAF + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdb3": "\u0646\u062d\u064a",  # ARABIC LETTER NOON + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdb4": "\u0642\u0645\u062d",  # ARABIC LETTER QAF + ARABIC LETTER MEEM + ARABIC LETTER HAH
    "\ufdb5": "\u0644\u062d\u0645",  # ARABIC LETTER LAM + ARABIC LETTER HAH + ARABIC LETTER MEEM
    "\ufdb6": "\u0639\u0645\u064a",  # ARABIC LETTER AIN + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdb7": "\u0643\u0645\u064a",  # ARABIC LETTER KAF + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdb8": "\u0646\u062c\u062d",  # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER HAH
    "\ufdb9": "\u0645\u062e\u064a",  # ARABIC LETTER MEEM + ARABIC LETTER KHAH + ARABIC LETTER YEH
    "\ufdba": "\u0644\u062c\u0645",  # ARABIC LETTER LAM + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufdbb": "\u0643\u0645\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufdbc": "\u0644\u062c\u0645",  # ARABIC LETTER LAM + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufdbd": "\u0646\u062c\u062d",  # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER HAH
    "\ufdbe": "\u062c\u062d\u064a",  # ARABIC LETTER JEEM + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdbf": "\u062d\u062c\u064a",  # ARABIC LETTER HAH + ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufdc0": "\u0645\u062c\u064a",  # ARABIC LETTER MEEM + ARABIC LETTER JEEM + ARABIC LETTER YEH
    "\ufdc1": "\u0641\u0645\u064a",  # ARABIC LETTER FEH + ARABIC LETTER MEEM + ARABIC LETTER YEH
    "\ufdc2": "\u0628\u062d\u064a",  # ARABIC LETTER BEH + ARABIC LETTER HAH + ARABIC LETTER YEH
    "\ufdc3": "\u0643\u0645\u0645",  # ARABIC LETTER KAF + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufdc4": "\u0639\u062c\u0645",  # ARABIC LETTER AIN + ARABIC LETTER JEEM + ARABIC LETTER MEEM
    "\ufdc5": "\u0635\u0645\u0645",  # ARABIC LETTER SAD + ARABIC LETTER MEEM + ARABIC LETTER MEEM
    "\ufdc6": "\u0633\u062e\u064a",  # ARABIC LETTER SEEN + ARABIC LETTER KHAH + ARABIC LETTER YEH
    "\ufdc7": "\u0646\u062c\u064a",  # ARABIC LETTER NOON + ARABIC LETTER JEEM + ARABIC LETTER YEH
    # deleted: honorifics, invocations, phrases, standalone words
    # U+FBC3-FBD2, U+FD90-FD91, U+FDC8-FDCE (Unicode 17.0 additions):
    "\ufbc3": "",  # deleted: honorific (JALLA WA-ALAA)
    "\ufbc4": "",  # deleted: honorific (DAAMAT BARAKAATUHUM)
    "\ufbc5": "",  # deleted: honorific (RAHMATU ALLAAHI TAAALAA ALAYH)
    "\ufbc6": "",  # deleted: honorific (RAHMATU ALLAAHI ALAYHIM)
    "\ufbc7": "",  # deleted: honorific (RAHMATU ALLAAHI ALAYHIMAA)
    "\ufbc8": "",  # deleted: honorific (RAHIMAHUM ALLAAHU TAAALAA)
    "\ufbc9": "",  # deleted: honorific (RAHIMAHUMAA ALLAAH)
    "\ufbca": "",  # deleted: honorific (RAHIMAHUMAA ALLAAHU TAAALAA)
    "\ufbcb": "",  # deleted: honorific (RADI ALLAAHU TAAALAA ANHUM)
    "\ufbcc": "",  # deleted: honorific (HAFIZAHU ALLAAH)
    "\ufbcd": "",  # deleted: honorific (HAFIZAHU ALLAAHU TAAALAA)
    "\ufbce": "",  # deleted: honorific (HAFIZAHUM ALLAAHU TAAALAA)
    "\ufbcf": "",  # deleted: honorific (HAFIZAHUMAA ALLAAHU TAAALAA)
    "\ufbd0": "",  # deleted: honorific (SALLALLAAHU TAAALAA ALAYHI WA-SALLAM)
    "\ufbd1": "",  # deleted: honorific (AJJAL ALLAAHU FARAJAHU ASH-SHAREEF)
    "\ufbd2": "",  # deleted: honorific (ALAYHI AR-RAHMAH)
    "\ufd90": "",  # deleted: honorific (RAHMATU ALLAAHI ALAYH)
    "\ufd91": "",  # deleted: honorific (RAHMATU ALLAAHI ALAYHAA)
    "\ufdc8": "",  # deleted: honorific (RAHIMAHU ALLAAH TAAALAA)
    "\ufdc9": "",  # deleted: honorific (RADI ALLAAHU TAAALAA ANH)
    "\ufdca": "",  # deleted: honorific (RADI ALLAAHU TAAALAA ANHAA)
    "\ufdcb": "",  # deleted: honorific (RADI ALLAAHU TAAALAA ANHUMAA)
    "\ufdcc": "",  # deleted: honorific (SALLALLAHU ALAYHI WA-ALAA AALIHEE WA-SALLAM)
    "\ufdcd": "",  # deleted: honorific (AJJAL ALLAAHU TAAALAA FARAJAHU ASH-SHAREEF)
    "\ufdce": "",  # deleted: honorific (KARRAMA ALLAAHU WAJHAH)
    # U+FD40-FD4F:
    "\ufd40": "",  # deleted: honorific (RAHIMAHU ALLAAH)
    "\ufd41": "",  # deleted: honorific (RADI ALLAAHU ANH)
    "\ufd42": "",  # deleted: honorific (RADI ALLAAHU ANHAA)
    "\ufd43": "",  # deleted: honorific (RADI ALLAAHU ANHUM)
    "\ufd44": "",  # deleted: honorific (RADI ALLAAHU ANHUMAA)
    "\ufd45": "",  # deleted: honorific (RADI ALLAAHU ANHUNNA)
    "\ufd46": "",  # deleted: honorific (SALLALLAAHU ALAYHI WA-AALIH)
    "\ufd47": "",  # deleted: honorific (ALAYHI AS-SALAAM)
    "\ufd48": "",  # deleted: honorific (ALAYHIM AS-SALAAM)
    "\ufd49": "",  # deleted: honorific (ALAYHIMAA AS-SALAAM)
    "\ufd4a": "",  # deleted: honorific (ALAYHI AS-SALAATU WAS-SALAAM)
    "\ufd4b": "",  # deleted: honorific (QUDDISA SIRRAH)
    "\ufd4c": "",  # deleted: honorific (SALLALLAHU ALAYHI WAAALIHEE WA-SALLAM)
    "\ufd4d": "",  # deleted: honorific (ALAYHAA AS-SALAAM)
    "\ufd4e": "",  # deleted: honorific (TABAARAKA WA-TAAALAA)
    "\ufd4f": "",  # deleted: honorific (RAHIMAHUM ALLAAH)
    # U+FDCF:
    "\ufdcf": "",  # deleted: honorific (SALAAMUHU ALAYNAA)
    # U+FDF0-FDFB:
    "\ufdf0": "",  # deleted: Koranic stop sign (SALLA)
    "\ufdf1": "",  # deleted: Koranic stop sign (QALA)
    "\ufdf2": "",  # deleted: standalone word (ALLAH)
    "\ufdf3": "",  # deleted: standalone word (AKBAR)
    "\ufdf4": "",  # deleted: standalone word (MOHAMMAD)
    "\ufdf5": "",  # deleted: standalone word (SALAM)
    "\ufdf6": "",  # deleted: standalone word (RASOUL)
    "\ufdf7": "",  # deleted: standalone word (ALAYHE)
    "\ufdf8": "",  # deleted: standalone word (WASALLAM)
    "\ufdf9": "",  # deleted: standalone word (SALLA)
    "\ufdfa": "",  # deleted: phrase (SALLALLAHOU ALAYHE WASALLAM)
    "\ufdfb": "",  # deleted: phrase (JALLAJALALOUHOU)
    # U+FDFD-FDFF:
    "\ufdfd": "",  # deleted: phrase (BISMILLAH AR-RAHMAN AR-RAHEEM)
    "\ufdfe": "",  # deleted: phrase (SUBHAANAHU WA TAAALAA)
    "\ufdff": "",  # deleted: phrase (AZZA WA JALL)
}
# LIGATURE MAP END
"""
Static Arabic presentation-form ligature mapping, authored as literals from
the Unicode decomposition data (unicodedataplus 16.0.0, in the pattern of
:data:`romanalfaz.urduspell.URDU_VARIANT_MAP`), plus the Unicode 17.0
additions noted inline.

Keys are 505 of the 519 presentation-form ligature codepoints (494 assigned
in unicodedataplus 16.0.0 plus 25 Unicode 17.0 additions) minus the 14
excluded ones; values are base-character sequences (448 entries) or the
empty string (57 honorific/phrase entries). Mark-bearing decompositions keep
their combining marks and drop their U+0020/U+0640.
"""

LIGATURE_TRANSLATION_TABLE: dict[int, str] = {
    ord(ligature): replacement for ligature, replacement in LIGATURE_MAP.items()
}
"""
Integer-keyed view of :data:`romanalfaz.urduspell.LIGATURE_MAP` for ``str.translate``.

``str.translate`` indexes its mapping by Unicode ordinals, so the
character-keyed data structure above is flattened once, at import time, into
the table :py:func:`romanalfaz.urduspell.normalizeUrduChars` actually applies.
"""

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
    3. Removes non-alphanumeric marks, digits, and punctuation via
       :py:func:`romanalfaz.urduspell.removeNonLetterChars`.
    4. Finally, normalizes all internal whitespace sequences to a single `space` using
       :py:func:`romanalfaz.urduspell.normalizeWhiteSpace`.

    The goal is to produce a clean string containing primarily letters and single spaces
    between words,  for further processing or comparison.

    Notes:
        Each character class of the input is handled by exactly one stage of the
        pipeline, so no transformation is applied twice:

        - Positional presentation forms (e.g., U+FE8F, the isolated form of U+0628),
          ligatures (the full Arabic presentation-form ligature set, e.g., U+FEFB),
          and U+0640 (TATWEEL) are folded back to their
          base characters by :py:func:`romanalfaz.urduspell.normalizeUrduChars` only.
        - Cross-dialect base character folds (e.g., U+0624, WAW WITH HAMZA ABOVE,
          to U+0648, WAW; and U+0623/U+0625, ALEF WITH HAMZA ABOVE/BELOW, to
          U+0627, ALEF) are applied by the same maps.
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
        - U+FC5E (mark-bearing ligature): the maps drop the U+0020 of its
          compatibility decomposition and emit its combining marks (U+064C,
          U+0651); :py:func:`romanalfaz.urduspell.removeMarks` then removes them.
        - U+FDF2 (ALLAH ligature): mapped to the empty string only by the maps
          -- a complete honorific word that requires no decomposition and no
          dictionary lookup.
        - U+0628 U+064E (base plus FATHA): the mark is removed only by
          :py:func:`romanalfaz.urduspell.removeMarks`; the maps leave marks untouched.
        - U+0622 (precomposed): a no-op at every stage (NFD decomposes,
          U+0653 is preserved, NFC recomposes).
        - U+0624 (cross-dialect base): folded to U+0648 only by the maps;
          :py:func:`romanalfaz.urduspell.removeMarks` leaves it unchanged.

        +--------------------------+--------------------+---------------------------+-------------+
        | Input                    | `removeMarks` only | `normalizeUrduChars` only | `normalize` |
        +==========================+====================+===========================+=============+
        | U+FE8F (positional form) | U+FE8F (unchanged) | U+0628 (folded)           | U+0628      |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+FEFB (ligature)        | U+FEFB (unchanged) | U+0644 U+0627 (folded)    | U+0644      |
        |                          |                    |                           | U+0627      |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+FC5E (mark ligature)   | U+FC5E (unchanged) | U+064C U+0651 (marks)     | ''          |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+FDF2 (honorific)       | U+FDF2 (unchanged) | '' (stripped)             | ''          |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+0628 U+064E            | U+0628             | U+0628 U+064E (unchanged) | U+0628      |
        | (base + fatha)           | (mark removed)     |                           |             |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+0622 (precomposed)     | U+0622 (no-op)     | U+0622 (no-op)            | U+0622      |
        +--------------------------+--------------------+---------------------------+-------------+
        | U+0624 (cross-dialect)   | U+0624 (no-op)     | U+0648 (folded)           | U+0648      |
        +--------------------------+--------------------+---------------------------+-------------+

        The division of labor above rests on an exact fit: the marks preserved by
        :py:func:`romanalfaz.urduspell.removeMarks` (U+0653 and U+0654) are exactly the
        marks that the precomposed characters of the variant map's charset (its
        keys and values) carry. Mark-bearing ligatures do not disturb this fit:
        their combining marks are ordinary marks that
        :py:func:`romanalfaz.urduspell.removeMarks` strips, and the U+0623/U+0625
        fold happens before marks are ever considered, so
        :data:`romanalfaz.urduspell.PRESERVED_MARKS` remains exactly
        {U+0653, U+0654}. This is what makes every stage a no-op on the
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

      #. Ligature presentation forms (the full Arabic presentation-form
         ligature set, e.g., lam-alef U+FEFB; mark-bearing ligatures such as
         U+FC5E; honorific/phrase ligatures such as U+FDF2, which are
         stripped outright).
      #. Positional variants (initial, medial, final, isolated forms)
         mapped back to base characters.
      #. Cross-dialect base characters, e.g., U+0624 (WAW WITH HAMZA ABOVE) folded
         to U+0648 (WAW), and U+0623/U+0625 (ALEF WITH HAMZA ABOVE/BELOW) folded
         to U+0627 (ALEF).

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
        :py:func:`romanalfaz.urduspell.normalize`. Ligature
        decompositions are no exception: mark-bearing ligatures (e.g. U+FC5E)
        emit only ordinary combining marks, which
        :py:func:`romanalfaz.urduspell.removeMarks` strips, and the U+0623/U+0625
        fold happens before marks are ever considered (their hamza, U+0655, is a
        fold input only and never survives), so
        :data:`romanalfaz.urduspell.PRESERVED_MARKS` remains exactly
        {U+0653, U+0654}.

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
    # LIGATURE_MAP is a single-pass translation table authored as literals
    # from the Unicode decomposition data: keys are single ligature
    # presentation form characters (e.g., lam-alef U+FEFB) and values are the
    # base character sequences they decompose into (e.g., "لا"), with the
    # compatibility tags stripped. Honorific/phrase ligatures map to "" and
    # are deleted, and mark-bearing ligatures keep their combining marks
    # (their U+0020/U+0640 are dropped) so removeMarks strips them downstream.
    # str.translate indexes by ordinal, so the character-keyed structure is
    # applied through its integer-keyed view LIGATURE_TRANSLATION_TABLE.
    text = text.translate(LIGATURE_TRANSLATION_TABLE)

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
    return "".join([c for c in cleanedText if not ud.category(c).startswith(("C", "P", "S", "Nd"))])


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
