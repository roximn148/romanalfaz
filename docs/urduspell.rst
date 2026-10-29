.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Urdu-Spell Normalization
********************************************************************************

Purpose (Why)
===============
Normalization establishes one standard way to represent Unicode text for
processing. It reduces character variations from different sources to a single
canonical form.

- **Positional Variants:** Unicode assigns characters that appear in
  different positions (initial, medial, final, isolated) having distinct
  *visual positional shapes*, with its own codepoint. These variants
  look identical, but their differing encodings make naïve codepoint-based
  processing treat them differently. Normalization resolves this by
  standardizing character sequences, stripping only visual information while
  preserving semantic meaning.

  - **Example:** The letter BEH (``ب``), encoded at U+0628, renders
    differently depending on whether it starts a word, appears in the middle,
    or ends one. While the presentation layer built atop Unicode handles
    context-specific shaping, these positional variants can be hardcoded to
    represent a specific shape *in addition* to the base alphabet characters.

    - U+FE8F (``ﺏ``) - ARABIC LETTER BEH ISOLATED FORM
    - U+FE90 (``ﺐ``) - ARABIC LETTER BEH FINAL FORM
    - U+FE91 (``ﺑ``) - ARABIC LETTER BEH INITIAL FORM
    - U+FE92 (``ﺒ``) - ARABIC LETTER BEH MEDIAL FORM

    Normalization maps all these positional variants back to the same base
    codepoint (U+0628), keeping the encoding consistent for downstream
    processing.

- **Composition/Ligatures:** Unicode also encodes combinations of characters
  as a single codepoint, such as a base character with combining marks, or
  multiple characters forming one composed shape. The standard provides rules
  for the composition and decomposition of these codepoints.

  - **Example:** The U+0622 (``آ``) codepoint represents a precomposed
    combination of U+0627 ``Alef`` and U+0653 ``Madda``. The goal of
    normalization is to resolve all representations into *one* standard form
    and not to retain both possibilities. Similarly, presentation forms and
    ligature normalization belong in this subcategory.

- **Marks (Linguistic and Formatting):** Linguistic marks differ across authors
  and authoring tools. To parse consistently, the process must decide whether
  to strip or keep these marks, relative to the intended processing scope.
  Stripping formatting marks used only for presentation (such as Zero Width
  Joiners (ZWJ), Non-Joiners (ZWNJ) or soft hyphens) is necessary for semantic
  processing.

  - **Example:** ``مُحَمَّدٌ`` ↔ ``محمد``, and ``قُرْآن`` ↔ ``قرآن``. A ZWNJ
    might be inserted between characters in a compound word to stop them from
    joining visually, but semantically the parser should treat it as
    transparent noise and strip it out. In ``ذمہ‌داری``, the ZWNJ between ``ہ``
    and ``د`` is necessary for correct rendering (without it, the word would
    render as ``ذمہداری`` and use of a space would split the word), yet the
    mark must be stripped.

- **Cross-Lingual Substitutions:** Related scripts within the same character
  family (e.g., Arabic/Farsi/Urdu/Sindhi variants) need distinguishing and
  processing based on their intended language context. For instance, an Arabic
  word processed for an Urdu context must maintain the appropriate phonological
  structure and the correct language-specific codepoints. In contrast to the
  three categories above, which have Unicode-standardized definitions of
  composition and decomposition, cross-lingual variants need explicit processing
  on top of the standard Unicode normalization stack.

  - **Example:** Certain visually similar characters have unique
    language-specific codepoints. When normalization targets a specific output
    language (e.g., for spellchecking), the process must map them; it cannot
    strip or skip them. Urdu ``Choti Ye`` (U+06CC) is not the same as Arabic
    ``Yeh`` (U+064A), and Urdu words should not contain Arabic U+064A while
    Arabic words should not contain Urdu U+06CC. The difference between the
    Arabic and Urdu ``Kaf``, and the ``Teh Marbuta`` variants, are other
    examples. A normalization process must select the sequence mandated by the
    target language's ruleset.

Scope (What and for Whom)
=========================

The intended application and the target audience's expected input define the
scope. Normalization is a mapping from an **Input Set** to an **Output Set** of
Unicode characters; defining both sets is a prerequisite to any implementation.

- **Input Definition:** What constitutes the input? Is it a word, a full
  sentence, a paragraph, or entire books/web pages? What structural elements
  need cleaning, and are we targeting format-specific constructs (like HTML
  tags) or only raw text ("content" alone)?

  - **Example:** If the scope is "Search Indexing" and the input may include
    HTML tags (``<p>``) or Markdown syntax (``##``), this requires removing all
    such structural noise.

- **Output Constraint:** What must the resulting canonical form *guarantee*?
  Is it for word lookups (spell checking), creating a search index, or
  linguistic processing within NLP tasks?

  - **Example:** If the output constraint is "Word Lookup," the result **must
    not** contain punctuation or numerals attached to the root word (e.g.,
    ``word.`` must resolve to ``word``).

- **Audience Dependence:** The principle of "one size fits all" does not exist
  in linguistics. The correct character combination order depends on the
  audience, and the necessary level of normalization differs between
  applications.

  - **Example:** A system for *displaying* historical manuscripts might
    require retaining every subtle variation (high fidelity), whereas a modern
    spellchecker demands aggressive simplification toward canonical form
    (high standardization).

Limitations
===========

Normalization is bound by the standard and ruleset established by the Unicode
Consortium, so any limitation in the character encoding standard limits the
normalization process.

- **Linguistic Ambiguity:** The main limitation is linguistic ambiguity.
  Normalization only corrects or standardizes *codepoints*; it does not
  understand the meaning those codepoints convey together, and has no sense of
  word boundaries or higher syntactic constructs. These semantics must be
  layered on top of the normalization process. Standardization can correct
  **syntax**, not **semantics**. For domain-specific processing (like
  Urdu-specific morphology), Unicode standardization *must* be complemented by
  morphological analyzers tailored for Arabic-script languages.

  - **Example:** The alphabetic order does not match the codepoint order and
    must be encoded by hand and processed. Unlike English, where the
    alphabet's encoding is a continuous, monotonic sequence of codepoints,
    the Urdu alphabet has a non-contiguous, non-monotonic codepoint assignment,
    which requires extra processing.

- **Script Coverage:** If the system encounters characters outside the
  defined input sets (e.g., historical scripts or obscure ideograms), the
  normalization routine has no defined output behavior.

Implementation
==============

.. automodule:: romanalfaz.urduspell
   :members:
   :undoc-members:  # includes objects without docstrings
   :show-inheritance: # shows base classes
   :exclude-members: URDU_VARIANT_MAP, URDU_VARIANT_REVERSAL_MAP, LIGATURE_MAP

.. autodata:: romanalfaz.urduspell.URDU_VARIANT_MAP
   :no-value:

.. literalinclude:: ../src/romanalfaz/urduspell.py
   :language: python
   :start-after: # URDU VARIANT MAP START
   :end-before: # URDU VARIANT MAP END

.. autodata:: romanalfaz.urduspell.URDU_VARIANT_REVERSAL_MAP
   :no-value:

.. autodata:: romanalfaz.urduspell.LIGATURE_MAP
   :no-value:

.. literalinclude:: ../src/romanalfaz/urduspell.py
   :language: python
   :start-after: # LIGATURE MAP START
   :end-before: # LIGATURE MAP END
